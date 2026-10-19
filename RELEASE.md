# 0.1.3 — published: waiting Windows launcher and refreshed native artifacts (2026-10-19)

Published SDK tag `v0.1.3` at source commit
`0c0db39f26b225116dcf5a71605f9ca7e5abeb89` after build-only validation:
https://github.com/cooloo-app/python-sdk/actions/runs/39281039182

The tag workflow passed isolated C/Python CI, both installed-wheel smoke checks,
package validation, OIDC upload and final PyPI verification:
https://github.com/cooloo-app/python-sdk/actions/runs/39284719327

The original tag-run artifacts were also checked locally against PyPI metadata
and downloaded wheel bytes. SHA256:
- macOS arm64: `f9bc1145ac2d4cd204650de46bae1fafed6aec4cc40451372c604f3f77ae05ad`
- Windows x86_64: `307af72a102e24793b87f72b4aac32952833200c1d332242141fe08ec0daff45`

CI installed local wheels; fresh supported-platform installs from official PyPI
and full manual GUI acceptance have not been repeated for 0.1.3.

Includes the waiting Windows console launcher and `python -m cooloo` entry point.
Refreshed client 0.3.0 binaries include terminal-only, complete-line trust confirmation
and Windows terminal-input guards, plus the current workspace/read-state changes.
Both `cooloo` and `cooloo-text` remain bundled on macOS arm64 and Windows x64.
Integration coverage and API guidance now match the current parent-to-child
DELEGATE direction; child credentials cannot act as the parent.

Client artifact commit: `9448aaf6cade687c52422a1fad1517022b5c34d0`.
Client build source: `cb21e62baac66cf965f2e2f751377ce49d392661`.
Isolated test server: `028913043b1774d84073fbd2caaf6cc618492168`.

Native release build, isolated protocol/headless/provider tests and static checks
passed. Local Windows startup, GUI first-frame, window/icon and console probes
passed. These checks do not constitute full manual GUI acceptance; macOS GUI,
SDL dummy and oldest-supported-OS/Python matrix remain unverified.

# 0.1.2 — published: client v0.3.0 and cooloo-text (2026-10-19)

Published via recovery workflow after the initial tag run stopped before upload on a
wheel-validator filename comparison bug. Final workflow
https://github.com/cooloo-app/python-sdk/actions/runs/39255874265 passed both platform
builds, pinned client/server CI, package validation, OIDC upload, and PyPI verification.
Bundles both `cooloo` and `cooloo-text` from client tag `v0.3.0`, client commit
`41101e8fa289a77f826c714434a20ccfb98947b0`, built from source
`017638f5e202c5035ebaf8dec4625fb71640dda8`. `pipx install cooloo` exposes both
`cooloo` and `cooloo-text` commands.

PyPI wheel SHA256:
- macOS arm64: `94266e6792ab0f20bc4fdb08cfd78bbc827217d0883dcd9811d3ae87031dbc4b`
- Windows x86_64: `87b0fac32db410556fbd957ba9457c41cfcb0ff0cf4c8d7d69a03651b2f0491d`

Client release verification passed its isolated builds and protocol tests; desktop GUI
acceptance remains pending.

# 0.1.1 — published: Shanghai endpoint (2026-10-16)

Published via GitHub OIDC Trusted Publishing; build-only run
https://github.com/cooloo-app/python-sdk/actions/runs/38867104384 and tag run
https://github.com/cooloo-app/python-sdk/actions/runs/38867325148 both passed.
PyPI metadata and downloaded wheel bytes match the original workflow artifacts:
- macOS wheel SHA256: `25b3113a6583d4d4891e81cdf57c8ddc165641e4f655b633cc1fb0871fb28c7c`
- Windows wheel SHA256: `155787f0abb6468f1ab334176d024e7d0d59767c5d09462ff42783a89552a32b`

Post-publication fresh Python 3.12 venv installs from official PyPI passed on m106
(macOS arm64) and m101 (Windows x64): SDK/client versions, bundled binary hashes,
JSON version output and GUI first-frame probes (30 ms / 1 ms). These do not claim
full manual GUI validation. No production data was modified by release tests.

Bundles client v0.2.4, build source `953f38f892a5ae1ff56f3ead51eaaba2ea92fd42`,
artifact commit `3d4758440aa0c4bf1a69e7d7c54248ddfd62a5f3` (client/LFS published).
Default and persisted old official endpoint relocate to Shanghai; exact verified
legacy trust pins remain usable without resetting identity/history. Explicit host
arguments/environment, custom servers/ports and explicit new-host pins win.
Fresh installations still require first-use trust. See README upgrade instructions.

The wheel includes the current explicit-GUI native startup behavior; the Python
launcher continues opening GUI with no arguments. No Python API/protocol change.

Native validation: Linux/macOS isolated configuration, protocol/cache/Lua/startup
regressions passed; macOS GUI-linked protocol integration and GUI first-frame passed.
Windows real startup/redirection/keygen and explicit/debug GUI first-frame passed;
desktop window/icon/console probe could not find a window in the SSH session.
Full manual GUI, oldest supported OS/Python and full compatibility matrix remain
unverified. Build-only and tag OIDC workflow results are recorded in planner release
handoff after completion; pushing a tag alone is not publication evidence.

Native SHA256:
- macOS: `656f55bcaa8a5760468b8397e8628b5b04176a70e0487699f167f13ecfcd8e9e`
- Windows: `c45904326045ee5fff57dac5261759970406ddfa59f866a7ab175c80179e83d4`

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
