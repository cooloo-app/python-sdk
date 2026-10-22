"""Thin subprocess adapter for cooloo's JSONL CLI schema 1. No wire protocol."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import uuid
from typing import Iterator


class CoolooError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class SendOutcomeUnknown(CoolooError):
    pass


def _error(code: str, message: str) -> CoolooError:
    return (SendOutcomeUnknown if code == "send-outcome-unknown" else CoolooError)(code, message)


def binary_path(explicit: str | Path | None = None, product: str = "cooloo") -> Path:
    if product not in {"cooloo", "cooloo-text"}:
        raise CoolooError("binary-invalid", f"unsupported bundled product: {product}")
    filename = product + (".exe" if os.name == "nt" else "")
    path = Path(explicit).expanduser().resolve() if explicit else Path(__file__).parent / "_bin" / filename
    if not path.is_file():
        raise CoolooError("binary-missing", "install the matching platform wheel or specify binary= explicitly")
    return path


@dataclass(frozen=True)
class Message:
    ts: int
    sender: str
    destination: str
    content: str
    end_offset: int
    message_id: str = ""

    @classmethod
    def from_event(cls, event: dict) -> Message:
        try:
            m = event["message"]
            if not isinstance(m["ts"], int) or not all(isinstance(m[k], str) for k in ("from", "to", "content")):
                raise ValueError()
            offset = event["end_offset"]
            if type(offset) is not int or offset < 0:
                raise ValueError()
            return cls(m["ts"], m["from"], m["to"], m["content"], offset, m.get("id", ""))
        except (KeyError, TypeError, ValueError) as exc:
            raise CoolooError("protocol-error", "invalid message event") from exc


@dataclass(frozen=True)
class SentResult:
    messages: list[Message]
    scan_offset: int


def _stop(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    proc.wait()


class EventStream:
    """Context-managed stream. Always close early-abandoned streams."""
    def __init__(self, args: list[str], env: dict, payload: bytes | None, timeout: float | None, idle_timeout: float | None, sending: bool):
        self._deadline = None if timeout is None else time.monotonic() + timeout
        self._idle_timeout = idle_timeout
        self._sending = sending
        self._closed = False
        self._terminal = False
        self._events: queue.Queue = queue.Queue(maxsize=64)
        self._stop_event = threading.Event()
        self._diagnostics: deque[bytes] = deque(maxlen=16)
        try:
            self._proc = subprocess.Popen(args, stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        except OSError as exc:
            raise CoolooError("process-start-failed", str(exc)) from exc
        self._threads = [threading.Thread(target=self._read_stdout, daemon=True), threading.Thread(target=self._read_stderr, daemon=True)]
        for thread in self._threads:
            thread.start()
        if payload is not None:
            try:
                self._proc.stdin.write(payload)  # bounded by SEND's 4096-byte limit
                self._proc.stdin.close()
            except (BrokenPipeError, OSError):
                pass  # consume the structured error or process status

    def _put(self, event) -> None:
        while not self._stop_event.is_set():
            try:
                self._events.put(event, timeout=.1)
                return
            except queue.Full:
                pass

    def _read_stdout(self) -> None:
        try:
            while True:
                line = self._proc.stdout.readline(131073)
                if not line:
                    break
                if len(line) > 131072 or not line.endswith(b"\n"):
                    raise CoolooError("protocol-error", "oversized or incomplete JSONL event")
                try:
                    event = json.loads(line.decode("utf-8"))
                except (UnicodeError, ValueError) as exc:
                    raise CoolooError("protocol-error", "invalid JSONL") from exc
                if not isinstance(event, dict) or event.get("schema") != 1 or event.get("type") not in {"message", "room", "result", "end", "error", "sending"}:
                    raise CoolooError("protocol-error", "unsupported event schema/type")
                self._put(event)
        except Exception as exc:
            self._put(exc)
        finally:
            self._put(None)

    def _read_stderr(self) -> None:
        while True:
            data = self._proc.stderr.read(4096)
            if not data:
                return
            self._diagnostics.append(data)

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        if self._closed:
            raise StopIteration
        wait = self._idle_timeout
        if self._deadline is not None:
            remaining = max(0, self._deadline - time.monotonic())
            wait = remaining if wait is None else min(wait, remaining)
        try:
            event = self._events.get(timeout=wait)
            if isinstance(event, Exception):
                raise event
            if event is None:
                self._proc.wait(timeout=max(.001, self._deadline-time.monotonic()) if self._deadline else 2)
                if self._proc.returncode != 0 or not self._terminal:
                    raise _error("send-outcome-unknown" if self._sending and not self._terminal else "process-failed", "CLI exited without successful completion")
                self.close()
                raise StopIteration
            if self._terminal:
                raise CoolooError("protocol-error", "event after terminal result")
            if event["type"] == "error":
                raise _error(event.get("code", "protocol-error"), event.get("message", "CLI failed"))
            if event["type"] in {"result", "end"}:
                self._terminal = True
            return event
        except (queue.Empty, subprocess.TimeoutExpired) as exc:
            self.close()
            raise _error("send-outcome-unknown" if self._sending and not self._terminal else "timeout", "CLI deadline exceeded") from exc
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._stop_event.set()
        _stop(self._proc)
        for thread in self._threads:
            thread.join(timeout=3)
        for pipe in (self._proc.stdin, self._proc.stdout, self._proc.stderr):
            if pipe is not None:
                pipe.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class MessageStream:
    def __init__(self, events: EventStream, offset: int, follow: bool):
        self._events = events
        self._offset = offset
        self._follow = follow
        self.next_offset: int | None = None

    def __iter__(self) -> Iterator[Message]:
        return self

    def __next__(self) -> Message:
        try:
            event = next(self._events)
            if event["type"] == "end" and not self._follow:
                cursor = event.get("next_offset")
                if type(cursor) is not int or cursor != self._offset:
                    raise CoolooError("protocol-error", "invalid read cursor")
                self.next_offset = cursor
                try:
                    next(self._events)
                except StopIteration:
                    raise
                raise CoolooError("protocol-error", "event after end")
            if event["type"] != "message":
                raise CoolooError("protocol-error", "expected message")
            message = Message.from_event(event)
            if message.end_offset <= self._offset:
                raise CoolooError("protocol-error", "non-increasing cursor")
            self._offset = message.end_offset
            return message
        except Exception:
            self.close()
            raise

    def close(self):
        self._events.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class Client:
    """One CLI process per call. No retries, implicit registration or shared cache."""
    def __init__(self, *, binary: str | Path | None = None, host: str | None = None,
                 config_dir: str | Path | None = None, tofu: bool = False,
                 effective_identity: str | None = None, timeout: float = 30):
        self.binary = binary_path(binary)
        self._env = dict(os.environ)
        if host is not None:
            self._env["COOLOO_HOST"] = host
        if config_dir is not None:
            self._env["COOLOO_CONFIG"] = str(Path(config_dir).expanduser().resolve())
        self._prefix = [str(self.binary), "--json"]
        if tofu:
            self._prefix.append("--tofu")
        if effective_identity:
            self._prefix += ["--as", effective_identity]
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = timeout
        with EventStream([str(self.binary), "--json", "version"], self._env, None, timeout, None, False) as stream:
            events = list(stream)
        if len(events) != 1 or events[0].get("type") != "result" or 1 not in events[0].get("schema_versions", []) or not {"json-output", "follow-offset", "no-cache"} <= set(events[0].get("capabilities", [])):
            raise CoolooError("incompatible-binary", "CLI schema 1 with explicit offsets is required")
        self.binary_version = events[0]["binary_version"]

    @staticmethod
    def _offset(offset: int) -> str:
        if type(offset) is not int or not 0 <= offset <= 2**63-1:
            raise ValueError("offset must be a nonnegative signed 64-bit integer")
        return str(offset)

    def _stream(self, *args: str, payload: bytes | None = None, follow: bool = False, idle_timeout: float | None = None):
        return EventStream(self._prefix + list(args), self._env, payload,
                           None if follow else self.timeout, idle_timeout, args[0] in {"send", "join"})

    def _result(self, *args: str, payload: bytes | None = None) -> dict:
        with self._stream(*args, payload=payload) as stream:
            events = [event for event in stream if event["type"] != "sending"]
        if len(events) != 1 or events[0]["type"] != "result":
            raise CoolooError("protocol-error", "expected one result")
        return {k: v for k, v in events[0].items() if k not in {"schema", "type"}}

    def keygen(self) -> str:
        return self._result("keygen")["id"]

    def register(self, nickname: str) -> dict:
        return self._result("whoami", "--register", nickname)

    def whoami(self) -> dict:
        return self._result("whoami")

    def send(self, destination: str, content: str, *, message_id: str | None = None) -> int:
        payload = content.encode("utf-8")
        if not 1 <= len(payload) <= 4096 or b"\0" in payload:
            raise ValueError("content must be 1–4096 UTF-8 bytes without NUL")
        mid = message_id or uuid.uuid4().hex
        if len(mid) != 32 or uuid.UUID(hex=mid).version != 4 or uuid.UUID(hex=mid).hex != mid:
            raise ValueError("message_id must be lowercase UUIDv4 hex")
        try:
            return self._result("send", destination, "--message-id", mid, payload=payload)["end_offset"]
        except CoolooError as exc:
            exc.message_id = mid
            raise

    def read(self, destination: str, *, offset: int) -> MessageStream:
        return MessageStream(self._stream("read", destination, self._offset(offset)), offset, False)

    def follow(self, destination: str, *, offset: int, idle_timeout: float | None = None) -> MessageStream:
        if idle_timeout is not None and idle_timeout <= 0:
            raise ValueError("idle_timeout must be positive")
        return MessageStream(self._stream("follow", destination, self._offset(offset), follow=True, idle_timeout=idle_timeout), offset, True)

    def sent(self, peer: str, *, offset: int) -> SentResult:
        with self._stream("sent", peer, self._offset(offset)) as stream:
            events = list(stream)
        if not events or events[-1]["type"] != "end" or any(e["type"] != "message" for e in events[:-1]):
            raise CoolooError("protocol-error", "invalid sent result")
        messages = [Message.from_event(e) for e in events[:-1]]
        cursor = events[-1].get("scan_offset")
        if type(cursor) is not int or cursor < offset or (messages and cursor < messages[-1].end_offset):
            raise CoolooError("protocol-error", "invalid scan cursor")
        return SentResult(messages, cursor)

    def rooms(self) -> list[dict]:
        with self._stream("rooms") as stream:
            events = list(stream)
        if not events or events[-1]["type"] != "end" or any(e["type"] != "room" for e in events[:-1]):
            raise CoolooError("protocol-error", "invalid rooms result")
        return [{"id": e["id"], "nickname": e["nickname"]} for e in events[:-1]]

    def create_room(self, nickname: str) -> dict:
        return self._result("create", nickname)

    def meta(self, identity: str) -> dict:
        return self._result("meta", identity)

    def rename(self, identity: str, nickname: str) -> None:
        self._result("rename", identity, nickname)

    def avatar(self, slot: int, child_id: str, nickname: str) -> dict:
        return self._result("avatar", f"{slot:03d}", child_id, nickname)

    def join(self, room: str) -> int:
        return self._result("join", room)["end_offset"]

    def approve_join(self, room: str, applicant: str) -> int:
        return self.send(room, f"@{room} join-approve {applicant}")

    def set_room_mode(self, room: str, mode: str) -> None:
        self._result("room-mode", room, mode)

    def delegate(self, child_id: str, permissions: str) -> None:
        self._result("delegate", child_id, permissions)
