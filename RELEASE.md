# 0.1.8 — published: client 0.3.6 editor integration fixes (2026-10-22)

Published SDK tag `v0.1.8` at source commit `9f9037101517d82dfc176dee5b7f3705c83596f7`.
Build-only validation: https://github.com/cooloo-app/python-sdk/actions/runs/39734784039
Tag publication and PyPI verification: https://github.com/cooloo-app/python-sdk/actions/runs/39735079743

PyPI wheel SHA256:
- macOS arm64: `8168359bc12b0460e4d2fcdc79154e53981e4d790c32096c220b9f44d0c7338c`
- Windows x86_64: `40749473641222eb5f66f549921abfbbb5be4989ad3c11f70d54e32ee84403e9`

CI passed pinned C/Python tests, macOS arm64 and Windows x86_64 wheel builds,
installed-wheel checks for `cooloo` and `cooloo-text`, package validation, OIDC upload,
and final PyPI metadata/download hash verification. The wheels bundle client v0.3.6
artifacts from client commit `9f0e6275677cd2c6257b58cf785cb3d0472a76e2`, built from
`3e7fc44010b56a63e9815a7406856454658f6501`; CI used server v0.3.6 commit
`0a7d77e18efe9d44dc787cc27f7baf9e5e61d299`. Fresh supported-platform installs and full
manual GUI acceptance were not performed.

# 0.1.7 — published: client 0.3.5 message threads (2026-10-22)

Published SDK tag `v0.1.7` at source commit `829910422f4e72d6eab9066c18245accd5b8b8ba`.
Build-only validation: https://github.com/cooloo-app/python-sdk/actions/runs/39728073169
Tag publication and PyPI verification: https://github.com/cooloo-app/python-sdk/actions/runs/39728369221

PyPI wheel SHA256:
- macOS arm64: `856edb681e437e7e1ae3b6e3f29991f817e10c27b5b7ea2052e8c34d90f1a29e`
- Windows x86_64: `aa4da949695d554451e3c498ee6734c382c76d523b5cd8bcd8f94100bd0198f7`

CI passed pinned C/Python tests, macOS arm64 and Windows x86_64 wheel builds,
installed-wheel checks for both `cooloo` and `cooloo-text`, package validation,
OIDC upload and final PyPI metadata/download hash verification. Fresh supported-platform
installs from PyPI and full manual GUI acceptance were not performed. Wheels bundle
client v0.3.5 artifacts from client commit `688b865853e61111e24a807fba8e4ae1769d94ea`,
built from `0168ae3ed715f26069df174716cca50b0086df2d`; tests pinned server commit
`0a7d77e18efe9d44dc787cc27f7baf9e5e61d299`. Client-side threads do not change the server
protocol or Python API.

# 0.1.6 — published: client 0.3.4 workspace synchronization (2026-10-21)

Published SDK tag `v0.1.6` at source commit `bd2b56118f9a6ad04bf4b9fd74a11a04655132cd`.
Build-only validation: https://github.com/cooloo-app/python-sdk/actions/runs/39554978684
Tag publication and PyPI verification: https://github.com/cooloo-app/python-sdk/actions/runs/39555716936

PyPI wheel SHA256:
- macOS arm64: `00ecdd45449b7368bd8e8fd47d500fcefa1dddfaa4684ae7af177499c3ae9044`
- Windows x86_64: `35608edde55f0c77d9b40e54fc938b4ff7b31f51e41297c27785710f3ef9885b`

CI passed pinned C/Python tests, installed-wheel CLI smoke checks, package validation, OIDC upload,
and PyPI metadata/download hash verification. Fresh supported-platform installs from PyPI and
full manual GUI acceptance were not performed. The wheels bundle client 0.3.4 artifacts from
client commit `ea448099c030ed730d5ae5d1b045bff2ece47156`, built from
`ed1f67cafe810d9ee79ec8d204875b59ce3e070a`; isolated test server
`c3b411b976467169f46b1924bb98e793a02f363a`.

# 0.1.5 — published: client 0.3.2 editor fixes (2026-10-20)

Published SDK tag `v0.1.5` at source commit `ad9488172eb1cbb4d25a1f434dcf838728718cc1`.
Build-only validation: https://github.com/cooloo-app/python-sdk/actions/runs/39391871296
Tag publication and PyPI verification: https://github.com/cooloo-app/python-sdk/actions/runs/39392360170

PyPI wheel SHA256:
- macOS arm64: `52dae7626abb294bfd03f43c9d222fe32e686d7c6d3aa6d1cb7d8d2b41c3dd78`
- Windows x86_64: `b79d46a8033d4da1a6b403139e6aa76c85824cd0d857b2f686aafd083bfdf08f`

The CI runners installed each wheel and checked both `cooloo` and `cooloo-text` launchers.
Fresh supported-platform installs from PyPI and full manual GUI acceptance were not performed.
The wheels bundle client 0.3.2 artifacts from client commit `af30a69ce3b0b4a87bc63837ca33c60ae46c68b2`,
built from `0149d964c09708dfaa17cf5a2328990db3f19024`.

# 0.1.4 — published: refreshed native binaries with Windows long-path fix (2026-10-20)

Published SDK tag `v0.1.4` at source commit
`e76f1603564a8c34bdcc4fc9b88dfbda5fdb9567` after successful build-only validation:
https://github.com/cooloo-app/python-sdk/actions/runs/39298209588

The tag workflow passed isolated C/Python CI, both installed-wheel smoke checks,
package validation, OIDC upload and final PyPI verification:
https://github.com/cooloo-app/python-sdk/actions/runs/39298614408

The original tag-run wheels were checked against PyPI metadata and downloaded bytes.
SHA256:
- macOS arm64: `bbec4e36efb42bd1707b8738d635351fd5fb35035dacc7b64b63622e0b053585`
- Windows x86_64: `c34de9c991551fe48ea0ee3fb381924e4342fc9390c30c842effee5afbd64aac`

Both CI runners installed the local wheels and checked the `cooloo` and `cooloo-text`
commands/processes. Fresh supported-platform installs from official PyPI and full manual
GUI acceptance have not been repeated for 0.1.4.

Refreshes the macOS arm64 and Windows x86_64 wheels with client 0.3.0 artifacts from
client commit `4d05ea07f7e46c23746fa4dff3d039f1844fa0b4`, built from source
`ad67e65351a47d632d1fe4d7f20d22b4830adc6b`. The refreshed Windows client includes
long-workspace-path support. Python API and launcher behavior are otherwise unchanged.
The isolated test server remains `028913043b1774d84073fbd2caaf6cc618492168`.

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
SDK/client MIT licenses and existing third-party notices. Verify metadata and binary
hashes before upload, then verify PyPI artifacts and supported-platform installation.
Tag-triggered OIDC publishing and a build-only manual workflow are now prepared in
`.github/workflows/`; see [PUBLISHING.md](PUBLISHING.md). Workflow and pinned client/LFS
inputs have been pushed. Manual build-only run 38753907756 passed on GitHub:
https://github.com/cooloo-app/python-sdk/actions/runs/38753907756
Linux C/Python tests, macOS/Windows installed-wheel checks and combined artifact validation
passed. PyPI upload and post-upload jobs were intentionally skipped; OIDC authentication
will first be exercised by a separately authorized new-version tag release.
Never store upload tokens in source, scripts, release notes or command-line arguments.
