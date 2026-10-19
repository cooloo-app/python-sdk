# PyPI publishing

## Authentication (one-time)

On the existing PyPI `cooloo` project, configure a GitHub Trusted Publisher:

- Owner: `cooloo-app`
- Repository: `python-sdk`
- Workflow: `publish.yml`
- Environment: **empty**

No API token, GitHub secret or GitHub Environment is used. Restrict repository write
access and protect release tags: permission to push a version tag permits publication.
The workflow grants `id-token: write` only to the upload job.

## Release inputs

`release-inputs.json` pins client/server repositories and full commit SHAs, the native
client version/build-source commit, and the cooloo/cooloo-text artifact filenames for both platforms. The
client repository's Git LFS `release/manifest.json` is the source of truth for the
selected binaries and SHA256 values; the release tooling verifies it before staging.
Never substitute `latest` or a branch name. Publish client commits **and LFS objects**
before enabling a release using them. The SDK does not rebuild native binaries in CI.

The client v0.3.0 artifact commit `41101e8fa289a77f826c714434a20ccfb98947b0` and its
LFS objects are the pinned input for this release. Server commit availability was also confirmed.
For the historical client snapshot,
`licenses/cooloo-client-MIT.txt` records the owner's MIT grant and is bundled alongside
vendor notices; this does not change the recorded binary build-source commit.

## Validate without publishing

After explicitly authorized commits/pushes, use Actions → publish → Run workflow on
`main`. A `workflow_dispatch` run tests, packages and validates both wheels but **never
uploads to PyPI**, even when manually selected on a tag. Check the `pypi-dist` artifact.
Main-branch pushes and pull requests run the reusable C/Python test suite.

Local checks (from the SDK checkout, with Python 3.12 build tools installed):

```sh
python tools/release.py prepare
python tools/release.py check --dist /path/to/dist
```

CI builds isolated loopback test fixtures from pinned client/server commits. The wheel
jobs install and check the both bundled `cooloo` and `cooloo-text` launchers on macOS arm64 and Windows x64. CLI smoke checks
are offline; no production server, identity or message is used. This is not a full GUI
acceptance test or an oldest-supported-OS/Python compatibility matrix.

## Publish a new SDK version

1. Update `pyproject.toml` and `src/cooloo/__init__.py` to the same new version.
2. Update README/release notes. Change `release-inputs.json` only when changing native
   artifact selection/test sources, after validation and publication of the pinned
   client input. Artifact filenames and hashes come from the client manifest.
3. Commit and push with explicit owner authorization. Run the build-only workflow first.
4. Push a matching SDK tag, e.g. `v0.1.2`, with explicit release authorization.
5. The tag workflow checks version equality, runs CI, builds both platform wheels,
   checks bundled binary hashes/licenses, then uploads via OIDC. There is no TestPyPI step.
6. Check the final verification job: it downloads PyPI artifacts and compares SHA256.
   Perform supported-platform installation/GUI acceptance as appropriate.

SDK tags are independent of client tags. `0.1.0` is already on PyPI: do not retag/rebuild
it as a new release. No generic wheel or sdist is uploaded. Build jobs have no OIDC grant;
the upload job only downloads validated artifacts and invokes the PyPI publishing action.

## Partial failure

PyPI cannot atomically publish both wheels or overwrite existing files. The uploader uses
`skip-existing` to allow a partial upload to resume; final hash verification rejects any
existing file whose bytes differ. If upload fails after one file succeeded, rerun failed
jobs using the same workflow artifacts, not a new build (ZIP timestamps can change hashes).
A hash mismatch needs investigation; never delete/recreate tags or treat skipped files as
proof of a successful matching release. Use a new version when replacement is necessary.
