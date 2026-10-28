# cooloo Python API and GUI launcher — 0.1.12

Thin wrapper around the bundled C GUI+CLI client and `cooloo-text` editor (0.3.11, JSONL schema 1).
No Python Native/Noise implementation, SSH backend, daemon, or CLI-only distribution.
Wheels target Windows x86_64 and macOS arm64. Python >=3.10.
Licensed under MIT; bundled third-party components retain their own licenses.

Version 0.1.12 refreshes the bundled client 0.3.11 binaries with the latest editor fixes.

## Installation / launch

```sh
pip install cooloo
pipx install cooloo
cooloo --gui
cooloo-text
# Or without a persistent pipx installation:
pipx run --spec cooloo cooloo --gui
pipx run --spec cooloo cooloo-text
```

`cooloo` with no arguments prints terminal help; use `cooloo --gui` for the GUI.
`cooloo-text` launches the standalone text editor. Other commands are forwarded unchanged.

On Windows, the installed `cooloo` console entry point waits for the bundled GUI
executable and preserves stdin/stdout/stderr. No separate native CLI artifact is
required. Desktop shortcuts may continue to target the native executable with `--gui`.
If a standalone GUI `cooloo.exe` earlier on PATH shadows this entry point,
PowerShell/CMD can return to their prompt while that process is still running.
Check `Get-Command cooloo -All` (PowerShell) or `where cooloo` (CMD). Use
`python -m cooloo whoami` with the Python environment where cooloo is installed
to bypass PATH ambiguity; remove the obsolete PATH entry when appropriate.
Do not copy the bundled `_bin/cooloo.exe` into a command directory as a replacement
for the installed console entry point.

With current client source, terminal trust confirmation requires this waiting
launcher. Redirected input never confirms trust: verify the displayed fingerprint
and explicitly use `-y/--tofu` for first-use automation. Changed pins still fail.
Version 0.1.12 includes these native protections and the latest editor fixes in the
bundled binaries pinned in `release-inputs.json`, together with the waiting launcher
and module entry point.

### Upgrade to the Shanghai server

```sh
python -m pip install --upgrade cooloo
# pipx users: pipx upgrade cooloo
```

The bundled client 0.3.11 artifacts use `123.206.215.121:4222` as their default server.
Persisted old official `43.133.202.144:4222` config is resolved to Shanghai; identity
and history caches are not deleted or rewritten. An existing old-server pin is reused
only when it equals the verified unchanged official fingerprint
`e6da669a4763acc8e790c6c757f698eed8eeab2c56007a62d28fd48f421c06bf`.
An explicit pin for Shanghai takes precedence; fresh installs still require first-use
trust. Restart running GUI/Python processes after upgrading.

**Explicit overrides are preserved:** if your environment sets `COOLOO_HOST` or your
code passes `Client(host="43.133.202.144:4222")`, remove/update that override. Custom
servers and nonstandard ports are not migrated. `Client()` uses the native default;
no separate Python protocol or endpoint fallback is introduced.
Unsigned/not notarized native artifacts retain their platform trust limitations.
No runtime downloads, PATH lookup, implicit identity creation or registration.
Unsupported platforms have no matching wheel; source users may explicitly supply a
compatible local C executable. No source distribution is published.

## Protocol 3 message IDs

The SDK supports `send(destination, content, message_id=uuid_hex)` and
`Message.message_id`. Use a matching Protocol 3 server; older Protocol 2 servers
are not supported. Persist `uuid.uuid4().hex` before sending when retries must
survive process loss. On `CoolooError`, `exception.message_id` identifies the
attempted send. Explicitly retry with the same effective identity, destination,
exact content and UUID; no automatic retry occurs. Different content requires a
new UUID. The server returns the original offset for the same-ID retry;
`duplicate-content` and `id-conflict` reject sends.

## Python usage

```python
from cooloo import Client

client = Client(host="your-server:4222", config_dir="./bot-identity")
# client.keygen()                       # once, explicitly
# Client(..., tofu=True).register("bot") # explicitly trust first server connection
end = client.send("<destination-id>", "hello\n世界")
with client.read("<destination-id>", offset=0) as messages:
    for message in messages:
        print(message.sender, message.content, message.end_offset)

with client.follow("<destination-id>", offset=saved_offset) as messages:
    for message in messages:
        process(message)
        save_checkpoint(message.end_offset)  # only AFTER business processing
```

Replace example IDs, server, and application functions. Obtain/trust the server pin through
an appropriate trusted channel; `tofu=True` is an explicit first-use trust decision, not
protection from a first-connection MITM. Changed stored pins always fail. Config defaults
match native CLI (`~/.cooloo`); use a separate directory per service/credential. Parent
of a new config directory must exist. Private identity files must not be shared/logged.

Methods: keygen, register, whoami, rooms, create_room, meta, rename, avatar, send,
read, follow, sent, join, approve_join, set_room_mode, delegate. Pass
`effective_identity=child_id` with the parent's credentials to select an ordinary
child's message identity. `delegate(child_id, ...)` controls the parent's access to
that child, not the child's access to its parent; failed AS never falls back to login identity. Administrative operations require actual owner
credentials. `sent(peer, offset=...)` returns SentResult(messages, scan_offset), including
an advanced cursor on empty filtered results. SENT never populates normal message caches.
Private rooms currently permit any registered user to make them public: **not a
confidentiality guarantee**. No aggregate history or complete multi-device recovery.

Each call starts a process and authenticates a connection. `timeout=30` bounds finite
commands. FOLLOW has no overall timeout; optional idle_timeout bounds silence. It may
end when the server closes an idle connection; no automatic reconnect, keepalive or retry.
Context managers close streams and reap subprocesses; **always close streams on early
exit**, including breaks. GUI caches are untouched by machine READ/FOLLOW. No exactly-once
claim: replay can occur; deduplicate by destination/end_offset and persist business cursors.

CoolooError exposes code/message. SendOutcomeUnknown means delivery may have happened;
never blindly retry. A valid server acknowledgement returns end_offset. No guarantees of
thread-safe shared Client usage. No shell execution; SEND uses UTF-8 stdin, max 4096 bytes.

## Automatic releases

SDK version tags trigger tests, platform wheel builds and PyPI Trusted Publishing (OIDC,
no API token). Manual workflow runs build and validate only. See
[PUBLISHING.md](PUBLISHING.md) for setup, pinned native artifacts and release steps.

## Development and packaging

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```

Integration tests need sibling `client/cooloo-cli` and `server/coolood`, or explicit test
binary overrides; all connections use temporary identities and loopback servers.
This CLI-only build is a local test fixture, not the distributed product. The distributed
platform wheels bundle both the `cooloo` and `cooloo-text` native products.

Build each platform from a separate package source copy: stage its verified `cooloo` and
`cooloo-text` artifacts with tools/stage_binary.py, then `python -m build --wheel`. The builder refuses
missing artifacts, changed hashes, and source distributions. macOS wheel tag must match
the actual deployment target; do not infer it from the build host version. Keep the
manifest's source commit/version/hash with the binary. The bundle must include third-party
license notices and the C client's MIT license before public distribution.
See [LICENSE](LICENSE) for the Python SDK's MIT license.

Source repository: https://github.com/cooloo-app/python-sdk . The planner includes it as
`python-sdk/` submodule; package name and Python import remain `cooloo`.
