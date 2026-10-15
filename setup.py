"""Build only explicitly staged platform wheels; never publish a universal wheel."""
import json
from pathlib import Path
from setuptools import setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.sdist import sdist

ROOT = Path(__file__).parent


class PlatformWheel(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        manifest = ROOT / "src/cooloo/_bin/manifest.json"
        if not manifest.exists():
            raise RuntimeError("Stage a verified GUI+CLI artifact with tools/stage_binary.py first")
        data = json.loads(manifest.read_text())
        import hashlib
        binary = manifest.parent / data["filename"]
        if hashlib.sha256(binary.read_bytes()).hexdigest() != data["sha256"]:
            raise RuntimeError("Staged executable checksum mismatch")
        self.root_is_pure = False
        self.plat_name = data["platform_tag"]

    def get_tag(self):
        return "py3", "none", self.plat_name


class NoSdist(sdist):
    def run(self):
        raise RuntimeError("Initial release is platform-wheel-only; build from the source repository")


setup(cmdclass={"bdist_wheel": PlatformWheel, "sdist": NoSdist})
