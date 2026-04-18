"""Allow running envdiff as a module: python -m envdiff."""
import sys

from envdiff.cli import main

sys.exit(main())
