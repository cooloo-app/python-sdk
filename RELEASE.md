# 0.1.0 local release candidate

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
Publication checklist: owner license decision, repository/organization PyPI ownership,
protected OIDC publishing environment, TestPyPI installation and explicit production
upload authorization. Do not upload merely because a tag exists. No automatic publishing
workflow is enabled while these prerequisites remain unresolved.
