import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from cooloo import launcher


class LauncherTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows GUI-subsystem child")
    def test_gui_child_wait_input_output_and_status(self):
        # pythonw is a real GUI-subsystem executable, like the bundled client.
        # The child cannot finish until the launcher forwards stdin and waits.
        gui = Path(sys.executable).with_name("pythonw.exe")
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "child.py"
            script.write_text(
                'import os, sys\n'
                'assert os.environ["COOLOO_LAUNCHER_WAIT"] == "1"\n'
                'print("Trust fixture?", file=sys.stderr, flush=True)\n'
                'answer = sys.stdin.readline()\n'
                'print(repr(answer), flush=True)\n'
                'raise SystemExit(7)\n')
            code = (
                "from unittest.mock import patch; from cooloo import launcher; "
                f"patch('cooloo.launcher.binary_path', return_value={str(gui)!r}).start(); "
                "raise SystemExit(launcher.main())")
            proc = subprocess.Popen([sys.executable, "-c", code, str(script)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            try:
                out, err = proc.communicate("Y\n", timeout=10)
                self.assertEqual(err.strip(), "Trust fixture?")
                self.assertEqual(proc.returncode, 7, err)
                self.assertEqual(out.strip(), "'Y\\n'")
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()

    def test_windows_launcher_wait_contract(self):
        with patch.object(launcher, "binary_path", return_value="bundled.exe"), \
             patch.object(launcher.os, "name", "nt"), \
             patch.object(launcher.subprocess, "Popen") as popen, \
             patch.object(sys, "argv", ["cooloo", "whoami"]):
            popen.return_value.wait.return_value = 7
            self.assertEqual(launcher.main(), 7)
            args, kwargs = popen.call_args
            self.assertEqual(args[0], ["bundled.exe", "whoami"])
            self.assertEqual(kwargs["env"]["COOLOO_LAUNCHER_WAIT"], "1")
            self.assertIs(kwargs["stdin"], sys.stdin)
            popen.return_value.wait.assert_called_once()


if __name__ == "__main__":
    unittest.main()
