#!/usr/bin/env python3
"""Build and run the local mystery-roster regression suite."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ISO = ROOT / "build" / "GALE01" / "melee-mystery-roster.iso"


def find_ninja() -> str:
    candidates = [
        shutil.which("ninja"),
        ROOT / ".venv" / "Scripts" / "ninja.exe",
        ROOT / ".venv" / "bin" / "ninja",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise FileNotFoundError(
        "ninja was not found on PATH or in the project's .venv"
    )


def build_dol() -> None:
    subprocess.run(
        [find_ninja(), "build/GALE01/main.dol"],
        cwd=ROOT,
        check=True,
    )


def run_tests(iso_path: Path) -> bool:
    os.environ["MELEE_TEST_ISO"] = str(iso_path.resolve())
    suite = unittest.defaultTestLoader.discover(
        str(ROOT / "tests" / "mods"), pattern="test_*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iso",
        type=Path,
        default=DEFAULT_ISO,
        help="modded ISO to verify (default: %(default)s)",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="test existing artifacts without rebuilding main.dol",
    )
    parser.add_argument(
        "--checklist",
        action="store_true",
        help="print the manual Dolphin checklist after automated tests",
    )
    args = parser.parse_args()

    try:
        if not args.skip_build:
            build_dol()
        success = run_tests(args.iso)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"mod test setup failed: {error}", file=sys.stderr)
        return 2

    if args.checklist:
        print("\n" + (ROOT / "MOD_TESTS.md").read_text(encoding="utf-8"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
