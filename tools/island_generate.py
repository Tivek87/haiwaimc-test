#!/usr/bin/env python3
"""Genereert het grote eiland (36x36 chunks).

Gebruik:  python3 tools/island_generate.py            (genereren + controleren)
          python3 tools/island_generate.py --preview  (ook voorbeeldplaatjes in tools/preview/)
"""
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from island.gen import run  # noqa: E402

if __name__ == "__main__":
    errors = run(TOOLS.parent, preview="--preview" in sys.argv)
    for e in errors[:40]:
        print("   FOUT:", e)
    if errors:
        sys.exit(f"{len(errors)} fouten gevonden")
    print("Eiland klaar, geen fouten.")
