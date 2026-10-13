#!/usr/bin/env python3
"""Genereert het Tropical Paradise worldgen-pakket (biomen, bomen, watervallen, ruines, dimensie)."""
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from paradise.gen import run  # noqa: E402

if __name__ == "__main__":
    files, errors = run(TOOLS.parent)
    print(f"  {len(files)} worldgen-bestanden geschreven")
    for e in errors[:40]:
        print("   FOUT:", e)
    if errors:
        sys.exit(f"{len(errors)} fouten gevonden")
    print("Paradise klaar, geen fouten.")
