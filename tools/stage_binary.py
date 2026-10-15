"""Stage a release artifact into an isolated package source copy before wheel build."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

p = argparse.ArgumentParser()
p.add_argument("binary", type=Path)
p.add_argument("--platform-tag", required=True)
p.add_argument("--source-commit", required=True)
p.add_argument("--version", default="0.2.3")
p.add_argument("--sha256", required=True)
a = p.parse_args()
blob = a.binary.read_bytes()
if hashlib.sha256(blob).hexdigest() != a.sha256:
    p.error("binary checksum mismatch")
if a.platform_tag == "win_amd64":
    if blob[:2] != b"MZ":
        p.error("not a PE binary")
    name = "cooloo.exe"
elif a.platform_tag.startswith("macosx_") and a.platform_tag.endswith("_arm64"):
    if blob[:4] != b"\xcf\xfa\xed\xfe":
        p.error("not a 64-bit Mach-O binary")
    name = "cooloo"
else:
    p.error("unsupported platform tag")
target = Path(__file__).resolve().parents[1] / "src/cooloo/_bin"
target.mkdir(exist_ok=True)
other = target / ("cooloo" if name.endswith(".exe") else "cooloo.exe")
if other.exists():
    p.error("use a clean staging directory per platform")
shutil.copyfile(a.binary, target / name)
(target / name).chmod(0o755)
(target / "manifest.json").write_text(json.dumps({"filename": name, "version": a.version,
    "source_commit": a.source_commit, "sha256": a.sha256, "platform_tag": a.platform_tag}, indent=2) + "\n")
