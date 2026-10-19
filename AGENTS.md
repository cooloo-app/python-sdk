# Python SDK

- Thin wrapper around the C GUI+CLI and cooloo-text binaries. Do not implement Noise/Native or SSH here.
- Source: cooloo-app/python-sdk; planner mounts this repository as python-sdk/.
- Runtime dependencies: Python standard library only. Build metadata lives in pyproject.toml.
- Package/import/entry point: cooloo. SDK version is independent from client binary version.
- Run `PYTHONPATH=src python -m unittest discover -s tests -v`; integration tests require
  sibling client/cooloo-cli and server/coolood or explicit COOLOO_TEST_CLI/COOLOO_TEST_SERVER.
  All test networking must use isolated servers, never production.
- Distribute platform wheels bundling both cooloo and cooloo-text; expose the `cooloo` and
  `cooloo-text` commands. Do not publish a universal wheel or silently download binaries.
  Stage verified release artifacts with tools/stage_binary.py --client-source <client checkout>.
- A stream must be explicitly closed on early exit; no implicit business ACK or SEND retries.
- No automatic publish/push without explicit authorization. Project-owned SDK and C client code
  are MIT licensed; retain bundled third-party notices.
