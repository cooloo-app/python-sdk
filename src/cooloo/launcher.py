"""Transparent command forwarding; never resolves the bundled executable via PATH."""
import os
import subprocess
import sys
from .client import binary_path, CoolooError, _stop


def _run(binary: str) -> int:
    try:
        args = [str(binary_path(product=binary)), *sys.argv[1:]]
        if os.name != "nt":
            os.execv(args[0], args)
        # Explicit handles preserve redirected streams through the Python launcher.
        proc = subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        try:
            return proc.wait()
        except KeyboardInterrupt:
            _stop(proc)
            return 130
    except (CoolooError, OSError) as exc:
        print(f"cooloo: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    return _run("cooloo")


def text_main() -> int:
    return _run("cooloo-text")


if __name__ == "__main__":
    raise SystemExit(main())
