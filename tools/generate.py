#!/usr/bin/env python3
"""Genereert alle Hawaii-strand structuren en functies voor grootte 1 t/m 8 chunks.

Gebruik:  python3 tools/generate.py            (alles opnieuw genereren + controleren)
          python3 tools/generate.py --preview  (ook PNG-voorbeelden in tools/preview/)
          python3 tools/generate.py --check    (niets schrijven; faalt als de bestanden niet actueel zijn)
"""
import gzip
import json
import pathlib
import re
import shutil
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from nbt import COMPOUND, INT, TagList, to_bytes  # noqa: E402
from structures import Planner  # noqa: E402
from terrain import Terrain  # noqa: E402
from vegetation import Nature  # noqa: E402
from world import DIRS, TOP, YMIN, World, parse_state  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "hawaii_beach" / "data" / "hawaii"
STRUCT = DATA / "structure"
GEN = DATA / "function" / "gen"
MCDATA = json.loads((ROOT / "tools" / "mcdata_1.21.1.json").read_text())
DATA_VERSION = 3955  # Minecraft 1.21.1
CHECK = "--check" in sys.argv
STALE = []


def emit(path, data, nbt=False):
    """Schrijft een bestand, of vergelijkt het in --check modus (nbt: op ongecomprimeerde inhoud)."""
    if CHECK:
        try:
            old = path.read_bytes()
            old = gzip.decompress(old) if nbt else old
        except FileNotFoundError:
            old = None
        if old != data:
            STALE.append(str(path.relative_to(ROOT)))
        return
    path.write_bytes(gzip.compress(data, mtime=0) if nbt else data)


# ------------------------------------------------------------------ late blokken
def depends_on(name, props):
    """Buren (dx, dy, dz) waar dit blok aan vast zit of mee verbindt."""
    base = name.split(":")[1]
    horiz = [(dx, 0, dz) for dx, dz in DIRS.values()]
    out = []
    if base in ("wall_torch", "ladder") or base.endswith("_wall_fan"):
        dx, dz = DIRS[props["facing"]]
        out.append((-dx, 0, -dz))
    elif base == "cocoa":
        dx, dz = DIRS[props["facing"]]
        out.append((dx, 0, dz))
    elif base == "vine":
        for face, (dx, dz) in DIRS.items():
            if props.get(face) == "true":
                out.append((dx, 0, dz))
    elif base.endswith("_bed"):
        dx, dz = DIRS[props["facing"]]
        out.append((dx, 0, dz) if props.get("part") == "foot" else (-dx, 0, -dz))
    elif base.endswith(("_fence", "_fence_gate", "_pane", "_stairs", "_wall")) or base in ("iron_bars",):
        out += horiz
    elif base == "sugar_cane":
        out += [(dx, -1, dz) for dx, _, dz in horiz]
    return out


def split_late(w):
    """Blokken die aan een buur in een andere chunk vastzitten pas na alle chunks plaatsen."""
    def chunk(x, z):
        return ((x - w.x0) // 16, (z - w.x0) // 16)

    late = []
    for (x, y, z), s in list(w.blk.items()):
        name, props = parse_state(s)
        for dx, dy, dz in depends_on(name, props):
            nx, nz = x + dx, z + dz
            if w.inb(nx, nz) and chunk(nx, nz) != chunk(x, z):
                late.append((y, x, z, s))
                del w.blk[(x, y, z)]
                break
    late.sort()
    w.late = [f"setblock ~{x} ~{y} ~{z} {s}" for y, x, z, s in late] + w.late


# ------------------------------------------------------------------ uitvoer
def state_compound(s):
    name, props = parse_state(s)
    c = {"Name": name}
    if props:
        c["Properties"] = props
    return c


def write_size(w, planner):
    n = w.n
    sdir = STRUCT / f"s{n}"
    gdir = GEN / f"s{n}"
    if not CHECK:
        for d in (sdir, gdir):
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
    chunks = defaultdict(list)
    for (x, y, z), s in w.blk.items():
        cx, cz = (x - w.x0) // 16, (z - w.x0) // 16
        chunks[(cx, cz)].append((x - (w.x0 + 16 * cx), y - YMIN, z - (w.x0 + 16 * cz), s))
    total = 0
    for cx in range(n):
        for cz in range(n):
            items = sorted(chunks.get((cx, cz), []), key=lambda i: (i[1], i[2], i[0]))
            palette = {}
            blocks = TagList(COMPOUND)
            for lx, ly, lz, s in items:
                idx = palette.setdefault(s, len(palette))
                blocks.append({"pos": TagList(INT, [lx, ly, lz]), "state": idx})
            height = max((i[1] for i in items), default=0) + 1
            root = {
                "DataVersion": DATA_VERSION,
                "size": TagList(INT, [16, height, 16]),
                "palette": TagList(COMPOUND, [state_compound(s) for s in palette]),
                "blocks": blocks,
                "entities": TagList(COMPOUND),
            }
            emit(sdir / f"c_{cx}_{cz}.nbt", to_bytes(root), nbt=True)
            total += len(items)
            # biomen per 4x4 kolommen
            lines = [f"# Biomen voor chunk {cx},{cz} (gegenereerd)"]
            px, pz = w.x0 + 16 * cx, w.x0 + 16 * cz
            for qz in range(4):
                row = []
                for qx in range(4):
                    kinds = [planner.t.biome(px + 4 * qx + a, pz + 4 * qz + b) for a in range(4) for b in range(4)]
                    row.append("warm_ocean" if "warm_ocean" in kinds else max(sorted(set(kinds)), key=kinds.count))
                start = 0
                for qx in range(1, 5):
                    if qx == 4 or row[qx] != row[start]:
                        x1, x2 = px + 4 * start, px + 4 * qx - 1
                        z1, z2 = pz + 4 * qz, pz + 4 * qz + 3
                        lines.append(f"fillbiome ~{x1} ~{YMIN} ~{z1} ~{x2} ~{TOP} ~{z2} minecraft:{row[start]}")
                        custom = {"warm_ocean": "coral_lagoon", "beach": "white_sand_beach", "jungle": "rainforest"}[row[start]]
                        lines.append(f"fillbiome ~{x1} ~{YMIN} ~{z1} ~{x2} ~{TOP} ~{z2} hawaii:{custom}")
                        start = qx
            emit(gdir / f"b_{cx}_{cz}.mcfunction", ("\n".join(lines) + "\n").encode())
    tx, ty, tz, yaw = planner.tp
    post = [f"# Details, dieren en water voor {n}x{n} chunks (gegenereerd door tools/generate.py)"]
    post += w.late + w.cmds_end + w.ents
    post.append(f"tp @a[tag=hawaii_builder] ~{tx} ~{ty} ~{tz} {yaw} 5")
    emit(gdir / "post.mcfunction", ("\n".join(post) + "\n").encode())
    return total


# ------------------------------------------------------------------ controle
def validate(w):
    errors = []
    blocks = MCDATA["blocks"]
    states = set(w.blk.values())
    late_states = [re.match(r"setblock \S+ \S+ \S+ ([^{\s]+)", c).group(1) for c in w.late + w.cmds_end]
    for s in states | set(late_states):
        name, props = parse_state(s)
        base = name.split(":")[1]
        if base not in blocks:
            errors.append(f"onbekend blok {s}")
            continue
        for k, v in props.items():
            if k not in blocks[base]:
                errors.append(f"onbekende eigenschap {k} in {s}")
            elif v not in blocks[base][k]:
                errors.append(f"ongeldige waarde {k}={v} in {s}")
    text = "\n".join(w.ents + w.late)
    for e in set(re.findall(r"summon minecraft:(\w+)", text)):
        if e not in MCDATA["entities"]:
            errors.append(f"onbekende entity {e}")
    for i in set(re.findall(r'id:"minecraft:(\w+)"', text)):
        if i not in MCDATA["items"] and not i.startswith(("regeneration", "water_breathing", "speed", "fire_resistance",
                                                          "jump_boost", "night_vision")):
            errors.append(f"onbekend item {i}")
    for b in set(re.findall(r'Name:"minecraft:(\w+)"', text)):
        if b not in blocks:
            errors.append(f"onbekend blok in display {b}")
    for cmd in w.ents + w.late:
        if cmd.count("{") != cmd.count("}") or cmd.count("[") != cmd.count("]"):
            errors.append(f"haakjes kloppen niet: {cmd[:80]}")
    return errors


def build(n):
    w = World(n)
    t = Terrain(w)
    t.compute()
    planner = Planner(w, t)
    planner.plan()
    t.write()
    planner.build()
    Nature(w, t, planner.palm_spots).grow()
    split_late(w)
    return w, planner


def main():
    preview = "--preview" in sys.argv
    ok = True
    for n in range(1, 9):
        w, planner = build(n)
        errs = validate(w)
        count = write_size(w, planner)
        size_kb = sum(f.stat().st_size for f in (STRUCT / f"s{n}").iterdir()) // 1024
        print(f"{n}x{n} chunks: {count:7d} blokken, {len(w.late):4d} late, {len(w.ents):3d} entities, {size_kb:5d} KB")
        for e in errs[:20]:
            print("   FOUT:", e)
        ok &= not errs
        if preview:
            import preview as pv
            pv.render(w, planner, ROOT / "tools" / "preview" / f"s{n}.png")
            bx, bz = planner.bar
            pv.render(w, planner, ROOT / "tools" / "preview" / f"s{n}_bar.png", 10,
                      (bx - 10, bz - 16, bx + 20, bz + 16))
            pv.render(w, planner, ROOT / "tools" / "preview" / f"s{n}_bar_inside.png", 12,
                      (bx - 8, bz - 13, bx + 17, bz + 13), ymax=4)
    if STALE:
        print(f"{len(STALE)} bestanden zijn niet actueel, bv. {STALE[0]}. Run: python3 tools/generate.py")
        ok = False
    if not ok:
        sys.exit("Er zijn fouten gevonden")


if __name__ == "__main__":
    main()
