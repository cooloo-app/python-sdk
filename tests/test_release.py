"""Exercise release validation with synthetic wheels, without native execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location("sdk_release", Path(__file__).resolve().parents[1] / "tools/release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.inputs, self.version = release.load()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def wheels(self, fault=None):
        for tag in self.inputs["artifacts"]:
            binaries = {}
            path = self.directory / f"cooloo-{self.version}-py3-none-{tag}.whl"
            with ZipFile(path, "w") as z:
                for product in ("cooloo", "cooloo-text"):
                    name = release.bundled_filename(product, tag)
                    blob = f"{tag}:{product}".encode()
                    binaries[product] = {"filename": name, "sha256": hashlib.sha256(blob).hexdigest()}
                    if fault == "hash" and product == "cooloo-text":
                        blob += b"corrupted"
                    if fault != "missing" or product != "cooloo-text":
                        z.writestr("cooloo/_bin/" + name, blob)
                if fault == "swapped":
                    binaries["cooloo"], binaries["cooloo-text"] = binaries["cooloo-text"], binaries["cooloo"]
                z.writestr("cooloo/_bin/manifest.json", json.dumps({
                    "platform_tag": tag, "version": self.inputs["client_version"],
                    "source_commit": self.inputs["client_source_commit"], "binaries": binaries}))
                prefix = f"cooloo-{self.version}.dist-info/"
                z.writestr(prefix + "METADATA", "License-Expression: MIT\n")
                z.writestr(prefix + "licenses/LICENSE", (release.ROOT / "LICENSE").read_text())
                for name in ("cooloo-client-MIT.txt", "SDL.txt", "JetBrainsMono.txt", "Lua.txt", "stb_truetype.txt", "Monocypher.txt"):
                    z.writestr("cooloo/_licenses/" + name, "notice")

    def test_both_products_on_both_platforms(self):
        self.wheels()
        with patch("builtins.print"):
            files, version = release.check_wheels(self.directory)
        self.assertEqual(len(files), 2)
        self.assertEqual(version, self.version)

    def test_missing_text_binary_rejected(self):
        self.wheels("missing")
        with self.assertRaises(KeyError):
            release.check_wheels(self.directory)

    def test_corrupted_text_binary_rejected(self):
        self.wheels("hash")
        with self.assertRaises(AssertionError):
            release.check_wheels(self.directory)

    def test_product_filename_swap_rejected(self):
        self.wheels("swapped")
        with self.assertRaises(AssertionError):
            release.check_wheels(self.directory)


if __name__ == "__main__":
    unittest.main()
