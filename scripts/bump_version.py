#!/usr/bin/env python3
"""Verhoogt de datapack-versie met 1 stap en zet een changelog-entry klaar.

Telling: v0.0.1 -> v0.0.2 -> ... -> v0.0.99 -> v0.1.0 -> ... -> v0.99.99 -> v1.0.0
Elk deel loopt van 0 t/m 99; het maximum is v99.99.99.

Gebruik:
  python3 scripts/bump_version.py "Wat er veranderd is" "Nog iets"
  python3 scripts/bump_version.py --check   # alleen controleren, niets aanpassen
"""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACK = ROOT / "hawaii_beach" / "pack.mcmeta"
CHANGELOG = ROOT / "docs" / "CHANGELOG.md"
VERSION_RE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
MAX = 99


def current_version():
    desc = json.loads(PACK.read_text())["pack"]["description"]
    m = VERSION_RE.search(desc)
    if not m:
        sys.exit(f"Geen versie (vX.Y.Z) gevonden in {PACK}")
    return tuple(int(p) for p in m.groups())


def next_version(major, minor, patch):
    patch += 1
    if patch > MAX:
        patch, minor = 0, minor + 1
    if minor > MAX:
        minor, major = 0, major + 1
    if major > MAX:
        sys.exit("Maximale versie v99.99.99 bereikt")
    return major, minor, patch


def fmt(v):
    return "{}.{}.{}".format(*v)


def check():
    v = current_version()
    if any(p > MAX for p in v):
        sys.exit(f"Versie {fmt(v)} heeft een deel boven de {MAX}")
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", CHANGELOG.read_text(), re.M)
    if not m or m.group(1) != fmt(v):
        sys.exit(f"Bovenste changelog-versie ({m and m.group(1)}) is niet gelijk aan pack.mcmeta ({fmt(v)})")
    print(f"OK: v{fmt(v)}")


def bump(notes):
    old = current_version()
    new = next_version(*old)
    PACK.write_text(PACK.read_text().replace(f"v{fmt(old)}", f"v{fmt(new)}", 1))

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"## [{fmt(new)}] - {now}\n\n" + "".join(f"- {n}\n" for n in notes) + "\n"
    text = CHANGELOG.read_text()
    i = text.find("\n## [")
    text = text + "\n" + entry if i == -1 else text[: i + 1] + entry + text[i + 1 :]
    CHANGELOG.write_text(text)
    print(f"v{fmt(old)} -> v{fmt(new)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--check"]:
        check()
    elif args:
        bump(args)
    else:
        sys.exit(__doc__)
