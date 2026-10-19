"""Launch the bundled product without relying on PATH command resolution."""
from .launcher import main

raise SystemExit(main())
