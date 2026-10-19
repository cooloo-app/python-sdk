"""Real C Native protocol behind the Python subprocess API; loopback only."""
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import unittest
from cooloo import Client, CoolooError

ROOT = Path(__file__).resolve().parents[2]
CLI = Path(os.environ.get("COOLOO_TEST_CLI", ROOT / "client/cooloo-cli"))
SERVER = Path(os.environ.get("COOLOO_TEST_SERVER", ROOT / "server/coolood"))


@unittest.skipUnless(CLI.is_file() and SERVER.is_file(), "build sibling C client/server first")
class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="cooloo-python-")
        cls.root = Path(cls.tmp.name)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            cls.port = sock.getsockname()[1]
        cls.host = f"127.0.0.1:{cls.port}"
        cls.log = open(cls.root / "daemon.log", "wb")
        cls.daemon = subprocess.Popen([str(SERVER), "-b", "127.0.0.1", "-p", str(cls.port)],
            env=dict(os.environ, COOLOO_HOME=str(cls.root / "server")), stdout=cls.log, stderr=cls.log)
        for _ in range(100):
            if cls.daemon.poll() is not None:
                raise RuntimeError("test daemon failed")
            try:
                with socket.create_connection(("127.0.0.1", cls.port), timeout=.1):
                    break
            except OSError:
                time.sleep(.03)
        else:
            raise RuntimeError("daemon not ready")

    @classmethod
    def tearDownClass(cls):
        cls.daemon.terminate()
        cls.daemon.wait(timeout=5)
        cls.log.close()
        cls.tmp.cleanup()

    def client(self, name, *, register=True, tofu=True, effective=None):
        client = Client(binary=CLI, host=self.host, config_dir=self.root / name,
                        tofu=tofu, effective_identity=effective, timeout=10)
        if register:
            client.keygen()
            client.register(name)
        return client

    def test_roundtrip_streams_and_management(self):
        a = self.client("alice")
        b = self.client("bob")
        room = a.create_room('测试 "room"')['id']
        self.assertEqual(a.meta(room)["nickname"], '测试 "room"')
        a.rename(room, "renamed")
        self.assertTrue(any(r["id"] == room for r in b.rooms()))
        text = 'hello\n世界 " \\ --json --debug'
        end = a.send(room, text)
        with b.read(room, offset=0) as stream:
            messages = list(stream)
            self.assertEqual(stream.next_offset, end)
        self.assertEqual(messages[0].content, text)
        self.assertEqual(messages[0].end_offset, end)
        with b.read(room, offset=end) as stream:
            self.assertEqual(list(stream), [])
            self.assertEqual(stream.next_offset, end)
        with b.follow(room, offset=end, idle_timeout=3) as stream:
            next_end = a.send(room, "live")
            self.assertEqual(next(stream).end_offset, next_end)
            proc = stream._events._proc
        self.assertIsNotNone(proc.poll())
        self.assertFalse((self.root / "alice/cache").exists())
        self.assertFalse((self.root / "bob/cache").exists())
        with b.follow(room, offset=next_end, idle_timeout=.2) as stream:
            with self.assertRaises(CoolooError) as error:
                next(stream)
            self.assertEqual(error.exception.code, "timeout")
        # C -> Python and Python -> legacy C raw output.
        env = dict(os.environ, COOLOO_CONFIG=str(self.root / "alice"), COOLOO_HOST=self.host)
        subprocess.run([str(CLI), "send", room], input=b"legacy", env=env, check=True, capture_output=True)
        with b.read(room, offset=next_end) as stream:
            self.assertEqual(next(stream).content, "legacy")
        raw = subprocess.check_output([str(CLI), "read", "--raw", room, "0"], env=env)
        self.assertEqual(json.loads(raw.splitlines()[0])["content"], text)

    def test_trust_errors_and_argument_contract(self):
        a = self.client("strict", register=False, tofu=False)
        with self.assertRaises(CoolooError) as error:
            a.whoami()
        self.assertEqual(error.exception.code, "identity-missing")
        a.keygen()
        with self.assertRaises(CoolooError) as error:
            a.whoami()
        self.assertEqual(error.exception.code, "server-untrusted")
        trusted = self.client("strict", register=False)
        trusted.register("strict")
        (self.root / "strict/known_servers").write_text(f"{self.host} {'0'*64}\n")
        with self.assertRaises(CoolooError) as error:
            trusted.whoami()
        self.assertEqual(error.exception.code, "server-key-changed")
        for content in ("", "\0", "a"*4097, "世"*1366):
            with self.assertRaises(ValueError):
                trusted.send("0"*64, content)
        for args in (["--json"], ["--json", "wat"], ["--json", "send"], ["--json", "follow", "0"*64], ["--json", "--as", "bad", "whoami"]):
            run = subprocess.run([str(CLI), *args], capture_output=True, timeout=5)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)["code"], "invalid-argument")

    def test_private_delegation_sent(self):
        owner = self.client("owner")
        peer = self.client("peer")
        outsider = self.client("outsider")
        child = self.client("child", register=False)
        child_id = child.keygen()
        owner_id = owner.whoami()["id"]
        peer_id = peer.whoami()["id"]
        owner.avatar(1, child_id, "child")
        # DELEGATE controls the parent's access to its ordinary child, not
        # the child's access to the parent (server/DELEGATION.md).
        child_as_owner = self.client("child", register=False, effective=owner_id)
        with self.assertRaises(CoolooError):
            child_as_owner.send(peer_id, "denied")
        acting = self.client("owner", register=False, effective=child_id)
        owner.delegate(child_id, "read")
        with self.assertRaises(CoolooError):
            acting.send(peer_id, "denied")
        owner.delegate(child_id, "write")
        end = acting.send(peer_id, "delegated")
        with peer.read(peer_id, offset=0) as stream:
            self.assertEqual(next(stream).sender, child_id)
        owner.delegate(child_id, "read")
        self.assertEqual(acting.sent(peer_id, offset=0).messages[0].end_offset, end)
        with self.assertRaises(CoolooError) as error:
            acting.send(peer_id, "denied")
        self.assertEqual(error.exception.code, "forbidden")
        outsider.send(peer_id, "unrelated")
        result = acting.sent(peer_id, offset=end)
        self.assertEqual(result.messages, [])
        self.assertGreater(result.scan_offset, end)
        room = owner.create_room("private")["id"]
        owner.set_room_mode(room, "private")
        with self.assertRaises(CoolooError) as error:
            outsider.meta(room)
        self.assertEqual(error.exception.code, "forbidden")
        outsider.join(room)
        owner.approve_join(room, outsider.whoami()["id"])
        outsider.send(room, "joined")
        owner.delegate(child_id, "none")
        with self.assertRaises(CoolooError):
            acting.sent(peer_id, offset=0)


if __name__ == "__main__":
    unittest.main()
