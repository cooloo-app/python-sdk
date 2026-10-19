"""Release checks shared by CI and local validation (Python 3.12 build tooling)."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import tomllib
import urllib.request
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def load():
    data = json.loads((ROOT / "release-inputs.json").read_text())
    for key in ("client_commit", "client_source_commit", "server_commit"):
        if not re.fullmatch(r"[0-9a-f]{40}", data[key]):
            raise ValueError(f"{key} must be a full commit SHA")
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    init = (ROOT / "src/cooloo/__init__.py").read_text()
    if f'__version__ = "{version}"' not in init:
        raise ValueError("SDK source and packaging versions differ")
    return data, version


def load_client_manifest(client):
    path = client / "release" / "manifest.json"
    manifest = json.loads(path.read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported client release manifest schema")
    return {entry["filename"]: entry for entry in manifest["artifacts"]}


def bundled_filename(product, platform_tag):
    if platform_tag not in {"macosx_11_0_arm64", "win_amd64"}:
        raise ValueError(f"unsupported platform tag: {platform_tag}")
    return product + (".exe" if platform_tag == "win_amd64" else "")


def check_wheels(directory):
    data, version = load()
    files = sorted(directory.glob("*"))
    expected = {f"cooloo-{version}-py3-none-{tag}.whl": tag for tag in data["artifacts"]}
    if {p.name for p in files} != set(expected):
        raise ValueError("Expected exactly the two platform wheels, no extra files")
    for path in files:
        tag = expected[path.name]
        with ZipFile(path) as z:
            manifest_path = next(n for n in z.namelist() if n.endswith("cooloo/_bin/manifest.json"))
            package = manifest_path.removesuffix("_bin/manifest.json")
            manifest = json.loads(z.read(manifest_path))
            assert manifest["platform_tag"] == tag
            assert manifest["version"] == data["client_version"]
            assert manifest["source_commit"] == data["client_source_commit"]
            for product in ("cooloo", "cooloo-text"):
                artifact = manifest["binaries"][product]
                digest = hashlib.sha256(z.read(package + "_bin/" + artifact["filename"])).hexdigest()
                assert digest == artifact["sha256"]
                assert artifact["filename"] == bundled_filename(product, tag)
            metadata = z.read(f"cooloo-{version}.dist-info/METADATA").decode()
            assert "License-Expression: MIT" in metadata.splitlines()
            license_text = z.read(f"cooloo-{version}.dist-info/licenses/LICENSE").decode()
            assert license_text.splitlines() == (ROOT / "LICENSE").read_text().splitlines()
            for name in ("cooloo-client-MIT.txt", "SDL.txt", "JetBrainsMono.txt", "Lua.txt", "stb_truetype.txt", "Monocypher.txt"):
                assert z.read(package + "_licenses/" + name)
        print(path.name, hashlib.sha256(path.read_bytes()).hexdigest())
    return files, version


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("prepare")
    q.add_argument("--tag")
    q.add_argument("--github-output", type=Path)
    q = sub.add_parser("stage")
    q.add_argument("--client", type=Path, required=True)
    q.add_argument("--platform", required=True)
    q = sub.add_parser("check")
    q.add_argument("--dist", type=Path, default=ROOT / "dist")
    q = sub.add_parser("verify-pypi")
    q.add_argument("--dist", type=Path, default=ROOT / "dist")
    a = p.parse_args()
    data, version = load()
    if a.command == "prepare":
        if a.tag and a.tag != f"v{version}":
            p.error(f"tag must be v{version}")
        if a.github_output:
            with a.github_output.open("a") as f:
                for key in ("client_repository", "client_commit", "server_repository", "server_commit"):
                    if "\n" in data[key] or "\r" in data[key]:
                        raise ValueError("Invalid output value")
                    f.write(f"{key}={data[key]}\n")
        print(f"SDK {version}; release inputs valid")
    elif a.command == "stage":
        inputs = data["artifacts"][a.platform]
        manifest = load_client_manifest(a.client)
        entries = [manifest.get(inputs["filename"]), manifest.get(inputs["text_filename"])]
        if any(entry is None for entry in entries):
            raise ValueError("cooloo and cooloo-text are both required in the client release manifest")
        if any(entry["source_commit"] != data["client_source_commit"] for entry in entries):
            raise ValueError("client source commit does not match release manifest")
        subprocess.run([sys.executable, str(ROOT / "tools/stage_binary.py"),
                        str(a.client / "release" / entries[0]["filename"]),
                        str(a.client / "release" / entries[1]["filename"]),
                        "--platform-tag", a.platform, "--source-commit", data["client_source_commit"],
                        "--version", data["client_version"], "--cooloo-sha256", entries[0]["sha256"],
                        "--cooloo-text-sha256", entries[1]["sha256"], "--client-source", str(a.client),
                        "--client-license", str(ROOT / "licenses/cooloo-client-MIT.txt")], check=True)
    else:
        files, version = check_wheels(a.dist)
        if a.command == "verify-pypi":
            for attempt in range(12):
                try:
                    with urllib.request.urlopen(f"https://pypi.org/pypi/cooloo/{version}/json", timeout=30) as r:
                        remote = json.load(r)
                    for path in files:
                        entry = next(x for x in remote["urls"] if x["filename"] == path.name)
                        digest = hashlib.sha256(path.read_bytes()).hexdigest()
                        assert entry["digests"]["sha256"] == digest
                        with urllib.request.urlopen(entry["url"], timeout=30) as r:
                            assert hashlib.sha256(r.read()).hexdigest() == digest
                    print("PyPI metadata and downloaded files verified")
                    break
                except (OSError, StopIteration):
                    if attempt == 11:
                        raise
                    time.sleep(10)


if __name__ == "__main__":
    main()
