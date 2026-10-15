# 0.1.0 — published to PyPI

Published directly to https://pypi.org/project/cooloo/0.1.0/ with owner authorization;
TestPyPI was explicitly skipped. Both uploaded files were downloaded from PyPI and
verified against local SHA256 values:

- macOS wheel: `130bc1e229d709b4d02a0b4dba6af71eb00a20b95dd629fa1de400faaa9799b7`
- Windows wheel: `24aecda8a3344460ab3029f2e3cde9564540ebdde9c2449048001c00a413e322`

Final MIT packaging passed twine checks, bundled license/metadata/binary-hash checks,
and Linux Python tests (7/7). Post-publication supported-platform pip installation
has not yet been repeated. The local temporary upload credential file was removed;
the owner must revoke the temporary token on PyPI.

Bundles C client 0.2.3 from source `2ac3f027aca3b5f6a746e490bf5dd3384fc0b746`.
GUI and CLI are the same executable; Python does not implement Native/Noise.

Artifact SHA256:
- macOS arm64 binary: `701cdeab865967ec15a41a5d1d44ed607ceca2329d04a775f421e693d1fe84f8`
- Windows x86_64 binary: `19079ec6c559eb58c5ddac6807669ba51b34fa830103246cdae003b7613fc28a`

Validated: Linux Python 3.12 integration/process tests 7/7; macOS Python 3.14 installed
wheel tests 7/7; macOS/Windows pip and pipx install/run, GUI first-frame probes, Windows
Python 3.12 Unicode send/read, FOLLOW cancellation, delegation and filtered SENT against
an isolated real C server. Windows launcher now explicitly inherits standard streams;
regression was found and fixed during platform validation. Native code handles machine
stdin/stdout in binary mode to avoid Windows newline translation.

Not validated: oldest supported Python/OS versions, full manual desktop GUI, Windows
non-ASCII identity/config paths (non-ASCII package path was checked), all failure paths
under real network loss. Unit tests exercise subprocess timeout, abrupt EOF, malformed
JSON, bounded stderr and cancellation. No exactly-once or complete history guarantee.

Build with tools/stage_binary.py (requires --client-source for vendor notices), then
python -m build --wheel. Distribution is platform-wheel-only; no generic sdist.
The owner approved MIT licensing for project-owned SDK and C client code and authorized
manual production PyPI upload, explicitly skipping TestPyPI. Rebuilt wheels must contain
the SDK/client MIT licenses and existing third-party notices. Verify metadata and binary
hashes before upload, then verify PyPI artifacts and supported-platform installation.
Tag-triggered OIDC publishing and a build-only manual workflow are now prepared in
`.github/workflows/`; see [PUBLISHING.md](PUBLISHING.md). Workflow and pinned client/LFS
inputs have been pushed. Manual build-only run 38753907756 passed on GitHub:
https://github.com/cooloo-app/python-sdk/actions/runs/38753907756
Linux C/Python tests, macOS/Windows installed-wheel checks and combined artifact validation
passed. PyPI upload and post-upload jobs were intentionally skipped; OIDC authentication
will first be exercised by a separately authorized new-version tag release.
Never store upload tokens in source, scripts, release notes or command-line arguments.
