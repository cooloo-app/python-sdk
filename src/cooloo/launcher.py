"""Transparent command forwarding; never resolves the bundled executable via PATH."""
import os
import subprocess
import sys
from .client import binary_path, CoolooError, _stop


def main() -> int:
    try:
        args = [str(binary_path()), *sys.argv[1:]]
        if os.name != "nt":
            os.execv(args[0], args)
        proc = subprocess.Popen(args)
        try:
            return proc.wait()
        except KeyboardInterrupt:
            _stop(proc)
            return 130
    except (CoolooError, OSError) as exc:
        print(f"cooloo: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
