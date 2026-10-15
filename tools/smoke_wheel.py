"""Check the installed distribution/launcher without contacting any server."""
import importlib.metadata
import json
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
import os

import cooloo

ROOT = Path(__file__).resolve().parents[1]
inputs = json.loads((ROOT / "release-inputs.json").read_text())
assert importlib.metadata.version("cooloo") == cooloo.__version__
assert ROOT / "src" not in Path(cooloo.__file__).resolve().parents, "must test installed wheel"
if platform.system() == "Darwin":
    assert platform.machine() == "arm64", "macOS wheel requires an arm64 runner"
launcher = shutil.which("cooloo")
assert launcher, "installed console entry point missing"
with tempfile.TemporaryDirectory() as config:
    result = subprocess.run([launcher, "--json", "version"],
                            env=dict(os.environ, COOLOO_CONFIG=config),
                            capture_output=True, text=True, check=True, timeout=30)
    event = json.loads(result.stdout)
    assert event["schema"] == 1
    assert event["binary_version"] == inputs["client_version"]
    assert "json-output" in event["capabilities"]
print("Installed wheel import and launcher version check passed")
