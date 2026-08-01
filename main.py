#!/usr/bin/env python3
"""Convenience entry point for running kde-ai-launcher directly via python3 main.py."""

import sys
from pathlib import Path

# Add src/ directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from kde_ai_launcher.cli import main

if __name__ == "__main__":
    sys.exit(main())
