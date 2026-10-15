# cooloo Python API and GUI launcher — 0.1.0

Thin wrapper around the bundled C GUI+CLI client (0.2.3, JSONL schema 1).
No Python Native/Noise implementation, SSH backend, daemon, or CLI-only distribution.
Initial wheels target Windows x86_64 and macOS arm64. Python >=3.10.
Licensed under MIT; bundled third-party components retain their own licenses.

## Installation / launch (after publication)

```sh
pip install cooloo
pipx install cooloo
cooloo --gui
# Or without a persistent pipx installation:
pipx run --spec cooloo cooloo --gui
```

`cooloo` with no arguments also opens the GUI. Other commands are forwarded unchanged.
Unsigned/not notarized native artifacts retain their platform trust limitations.
No runtime downloads, PATH lookup, implicit identity creation or registration.
Unsupported platforms have no matching wheel; source users may explicitly supply a
compatible local C executable. No source distribution is published in this first release.

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
`effective_identity=owner_id` to select an explicitly delegated identity; failed AS
never falls back to login identity. Administrative operations require actual owner
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
This CLI-only build is a local test fixture, not the distributed product.

Build each platform from a separate package source copy: stage its verified GUI+CLI
artifact with tools/stage_binary.py, then `python -m build --wheel`. The builder refuses
missing artifacts, changed hashes, and source distributions. macOS wheel tag must match
the actual deployment target; do not infer it from the build host version. Keep the
manifest's source commit/version/hash with the binary. The bundle must include third-party
license notices and the C client's MIT license before public distribution.
See [LICENSE](LICENSE) for the Python SDK's MIT license.

Source repository: https://github.com/cooloo-app/python-sdk . The planner includes it as
`python-sdk/` submodule; package name and Python import remain `cooloo`.
