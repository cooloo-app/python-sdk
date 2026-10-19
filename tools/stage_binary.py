"""Stage the verified cooloo and cooloo-text artifacts into an isolated wheel source."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

p = argparse.ArgumentParser()
p.add_argument("cooloo", type=Path)
p.add_argument("cooloo_text", type=Path)
p.add_argument("--platform-tag", required=True)
p.add_argument("--source-commit", required=True)
p.add_argument("--version", required=True)
p.add_argument("--cooloo-sha256", required=True)
p.add_argument("--cooloo-text-sha256", required=True)
p.add_argument("--client-source", type=Path, required=True, help="matching client checkout with vendored license notices")
p.add_argument("--client-license", type=Path, help="owner-approved client license for older source snapshots")
a = p.parse_args()

if a.platform_tag == "win_amd64":
    if a.cooloo.read_bytes()[:2] != b"MZ" or a.cooloo_text.read_bytes()[:2] != b"MZ":
        p.error("not a PE binary")
    names = {"cooloo": "cooloo.exe", "cooloo-text": "cooloo-text.exe"}
elif a.platform_tag.startswith("macosx_") and a.platform_tag.endswith("_arm64"):
    if a.cooloo.read_bytes()[:4] != b"\xcf\xfa\xed\xfe" or a.cooloo_text.read_bytes()[:4] != b"\xcf\xfa\xed\xfe":
        p.error("not a 64-bit Mach-O binary")
    names = {"cooloo": "cooloo", "cooloo-text": "cooloo-text"}
else:
    p.error("unsupported platform tag")

artifacts = {"cooloo": (a.cooloo, a.cooloo_sha256), "cooloo-text": (a.cooloo_text, a.cooloo_text_sha256)}
for product, (source, expected) in artifacts.items():
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        p.error(f"{product} binary checksum mismatch")

target = Path(__file__).resolve().parents[1] / "src/cooloo/_bin"
target.mkdir(exist_ok=True)
if any((target / name).exists() for name in names.values()):
    p.error("use a clean staging directory per platform")
for product, (source, _) in artifacts.items():
    destination = target / names[product]
    shutil.copyfile(source, destination)
    destination.chmod(0o755)

notices = target.parent / "_licenses"
notices.mkdir(exist_ok=True)
shutil.copyfile(a.client_license or a.client_source / "LICENSE", notices / "cooloo-client-MIT.txt")
vendor = a.client_source / "vendor"
shutil.copyfile(vendor / "sdl3/LICENSE.txt", notices / "SDL.txt")
shutil.copyfile(a.client_source / "assets/fonts/OFL.txt", notices / "JetBrainsMono.txt")
lua = (vendor / "lua/lua.h").read_text()
(notices / "Lua.txt").write_text(lua[lua.index("/******************************************************************************"):] if "/******************************************************************************" in lua else lua)
stb = (vendor / "stb_truetype.h").read_text()
(notices / "stb_truetype.txt").write_text(stb[stb.index("ALTERNATIVE A - MIT License"):])
mono = (vendor / "monocypher.c").read_text()
(notices / "Monocypher.txt").write_text(mono[:mono.index("#include")])

manifest = {"version": a.version, "source_commit": a.source_commit, "platform_tag": a.platform_tag,
            "binaries": {product: {"filename": names[product], "sha256": expected}
                         for product, (_, expected) in artifacts.items()}}
(target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
