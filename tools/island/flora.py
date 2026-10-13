"""Bomen en planten voor het eiland. Elke functie bouwt 1 object in een ObjBuf (alleen in lege ruimte)."""
import math

from world import st

LEAF = st("jungle_leaves", persistent="true")
AZALEA = st("azalea_leaves", persistent="true")
FAZALEA = st("flowering_azalea_leaves", persistent="true")
CHERRY = st("cherry_leaves", persistent="true")
ACACIA = st("acacia_leaves", persistent="true")
MANGROVE = st("mangrove_leaves", persistent="true")


def ground(b, x, z):
    return b.isl.h(x, z) + 1


def blob(b, cx, cy, cz, rx, ry, rz, leaf, rng, jitter=0.15, out=None):
    for a in range(-int(rx) - 1, int(rx) + 2):
        for c in range(-int(rz) - 1, int(rz) + 2):
            for y in range(-int(ry) - 1, int(ry) + 2):
                d = (a / rx) ** 2 + (y / ry) ** 2 + (c / rz) ** 2
                if d <= 1 + rng.uniform(-jitter, jitter * 0.6):
                    p = (round(cx + a), round(cy + y), round(cz + c))
                    if b.is_air(*p):
                        b.set(*p, leaf)
                        if out is not None:
                            out.append(p)


def vines(b, leaves, rng, frac=0.08, maxlen=8):
    for _ in range(int(len(leaves) * frac)):
        lx, ly, lz = rng.choice(leaves)
        face, (ox, oz) = rng.choice([("east", (-1, 0)), ("west", (1, 0)), ("south", (0, -1)), ("north", (0, 1))])
        vx, vz = lx + ox, lz + oz
        for i in range(rng.randint(2, maxlen)):
            if b.is_air(vx, ly - i, vz):
                b.set(vx, ly - i, vz, st("vine", **{face: "true"}))
            else:
                break


def log(b, x, y, z, s=None):
    cur = b.get(x, y, z)
    if cur is None or "leaves" in cur or "vine" in cur:
        b.set(x, y, z, s or st("jungle_log", axis="y"))
        return True
    return False


def palm(b, x, z, rng, lean=None, height=None):
    y0 = ground(b, x, z)
    h = height or rng.randint(7, 12)
    dx, dz = lean or rng.choice([(-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)])
    amount = rng.uniform(1.0, 3.6)
    px, pz = x, z
    for i in range(h):
        f = (i / (h - 1)) ** 2
        px, pz = x + round(dx * amount * f), z + round(dz * amount * f)
        if not log(b, px, y0 + i, pz, st("jungle_log", axis="y") if i % 3 else st("stripped_jungle_log", axis="y")):
            return
    ty = y0 + h - 1
    for yy in (ty + 1, ty + 2):
        if b.is_air(px, yy, pz):
            b.set(px, yy, pz, LEAF)
    for fx, fz in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        diag = fx and fz
        length = rng.randint(3, 4) if diag else rng.randint(4, 6)
        prof = [1, 1, 1, 0, 0, -1, -1]
        for j in range(1, length + 1):
            yy = ty + prof[j]
            b.setk(px + fx * j, yy, pz + fz * j, LEAF)
            if j == length and rng.random() < 0.7:
                b.setk(px + fx * j, yy - 1, pz + fz * j, LEAF)
            if not diag and j <= 2:
                b.setk(px + fx * j + fz, yy, pz + fz * j + fx, LEAF)
                b.setk(px + fx * j - fz, yy, pz + fz * j - fx, LEAF)
    for face, (cx, cz) in (("west", (1, 0)), ("east", (-1, 0)), ("north", (0, 1)), ("south", (0, -1))):
        if rng.random() < 0.55:
            b.setk(px + cx, ty, pz + cz, st("cocoa", facing=face, age=2))


def jungle_tree(b, x, z, rng, hmin=8, hmax=14):
    y0 = ground(b, x, z)
    h = rng.randint(hmin, hmax)
    for i in range(h):
        log(b, x, y0 + i, z)
    for _ in range(rng.randint(0, 3)):
        i = rng.randint(2, max(2, h - 4))
        face, (cx, cz) = rng.choice([("east", (-1, 0)), ("west", (1, 0)), ("south", (0, -1)), ("north", (0, 1))])
        b.setk(x + cx, y0 + i, z + cz, st("cocoa", facing=face, age=rng.randint(0, 2)))
    leaves = []
    blob(b, x, y0 + h - 1, z, 3.0, 1.8, 3.0, LEAF, rng, out=leaves)
    blob(b, x + rng.uniform(-1.5, 1.5), y0 + h - 4, z + rng.uniform(-1.5, 1.5), 2.2, 1.3, 2.2, LEAF, rng, out=leaves)
    vines(b, leaves, rng, 0.07, 7)


def giant_tree(b, x, z, rng):
    """Reuzenboom van het regenwoud: 2x2 stam, plankwortels, meerdere kroonlagen, lianen."""
    y0 = ground(b, x, z)
    h = rng.randint(22, 32)
    for i in range(h):
        for a in (0, 1):
            for c in (0, 1):
                log(b, x + a, y0 + i, z + c)
    # plankwortels
    for (ax, az), (dx, dz) in (((-1, 0), (-1, 0)), ((2, 1), (1, 0)), ((0, -1), (0, -1)), ((1, 2), (0, 1)),
                               ((-1, 1), (-1, 0)), ((2, 0), (1, 0))):
        hh = rng.randint(2, 5)
        for i in range(hh):
            log(b, x + ax, y0 + i - 1, z + az, "jungle_wood")
        if rng.random() < 0.6:
            log(b, x + ax + dx, y0 - 1, z + az + dz, "jungle_wood")
            log(b, x + ax + dx, y0, z + az + dz, "jungle_wood")
    cxm, czm = x + 0.5, z + 0.5
    leaves = []
    # takken met kronen
    for k in range(rng.randint(3, 5)):
        ang = rng.uniform(0, math.tau)
        by = y0 + rng.randint(int(h * 0.55), h - 3)
        L = rng.randint(4, 7)
        ex, ez = cxm, czm
        for j in range(1, L + 1):
            ex = cxm + math.cos(ang) * j
            ez = czm + math.sin(ang) * j
            axis = "x" if abs(math.cos(ang)) > abs(math.sin(ang)) else "z"
            log(b, round(ex), by + j // 2, round(ez), st("jungle_log", axis=axis))
        blob(b, ex, by + L // 2 + 1, ez, rng.uniform(3, 4.5), 1.8, rng.uniform(3, 4.5), LEAF, rng, out=leaves)
    blob(b, cxm, y0 + h, czm, 6.0, 2.6, 6.0, LEAF, rng, out=leaves)
    blob(b, cxm, y0 + h + 2, czm, 3.5, 1.6, 3.5, LEAF, rng, out=leaves)
    # cacao en epifyten (kleine azalea-bosjes op takken)
    for _ in range(rng.randint(2, 6)):
        i = rng.randint(3, h - 5)
        face, (cx, cz) = rng.choice([("east", (-1, 0)), ("west", (2, 0)), ("south", (0, -1)), ("north", (0, 2))])
        b.setk(x + cx, y0 + i, z + cz, st("cocoa", facing=face, age=rng.randint(1, 2)))
    vines(b, leaves, rng, 0.1, 12)


def banyan(b, x, z, rng):
    """Brede banyanboom met luchtwortels."""
    y0 = ground(b, x, z)
    h = rng.randint(9, 13)
    for i in range(h):
        for a in (0, 1):
            for c in (0, 1):
                log(b, x + a, y0 + i, z + c, "jungle_wood" if i < 3 else None)
    leaves = []
    for k in range(6):
        ang = k * math.tau / 6 + rng.uniform(-0.3, 0.3)
        L = rng.randint(6, 10)
        by = y0 + h - 2
        ex = ez = 0
        for j in range(1, L + 1):
            ex = x + 0.5 + math.cos(ang) * j
            ez = z + 0.5 + math.sin(ang) * j
            axis = "x" if abs(math.cos(ang)) > abs(math.sin(ang)) else "z"
            log(b, round(ex), by + (1 if j > L // 2 else 0), round(ez), st("jungle_log", axis=axis))
            if j > 3 and j % 3 == 0:
                # luchtwortel naar beneden
                rx, rz = round(ex), round(ez)
                top = by - 1
                gy = b.isl.h(rx, rz) + 1 if b.inb(rx, rz) else y0
                for yy in range(top, gy - 1, -1):
                    if not log(b, rx, yy, rz, st("mangrove_roots") if yy == gy else st("jungle_log", axis="y")):
                        break
        blob(b, ex, by + 2, ez, 3.2, 1.6, 3.2, LEAF, rng, out=leaves)
    blob(b, x + 0.5, y0 + h + 1, z + 0.5, 6.5, 2.2, 6.5, LEAF, rng, out=leaves)
    vines(b, leaves, rng, 0.05, 5)


def flowering_tree(b, x, z, rng, kind="plumeria"):
    """Plumeria (wit/roze bloemen) of flamboyant/monkeypod (roze kersbloesem)."""
    y0 = ground(b, x, z)
    h = rng.randint(4, 6)
    trunk = st("stripped_birch_log", axis="y") if kind == "plumeria" else st("dark_oak_log", axis="y")
    for i in range(h):
        log(b, x, y0 + i, z, trunk)
    for k in range(rng.randint(2, 4)):
        dx, dz = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        L = rng.randint(2, 3)
        for j in range(1, L + 1):
            log(b, x + dx * j, y0 + h - 2 + j // 2, z + dz * j, trunk.replace("axis=y", "axis=" + ("x" if dx else "z")))
        if kind == "plumeria":
            blob(b, x + dx * L, y0 + h, z + dz * L, 2.4, 1.3, 2.4, FAZALEA if rng.random() < 0.6 else AZALEA, rng)
        else:
            blob(b, x + dx * L, y0 + h, z + dz * L, 3.0, 1.4, 3.0, CHERRY, rng)
    if kind == "plumeria":
        blob(b, x, y0 + h + 1, z, 2.6, 1.4, 2.6, FAZALEA, rng)
    else:
        blob(b, x, y0 + h + 1, z, 4.2, 1.7, 4.2, CHERRY, rng)


def koa(b, x, z, rng):
    """Koa / acacia met platte kroon (hooglanden en weides)."""
    y0 = ground(b, x, z)
    h = rng.randint(5, 8)
    px, pz = x, z
    for i in range(h):
        if i > 2 and rng.random() < 0.35:
            px += rng.choice([-1, 0, 1])
            pz += rng.choice([-1, 0, 1])
        log(b, px, y0 + i, pz, st("acacia_log", axis="y"))
    for _ in range(2):
        dx, dz = rng.choice([(2, 1), (-2, 1), (1, -2), (-1, 2), (2, -1)])
        log(b, px + dx // 2, y0 + h, pz + dz // 2, st("acacia_log", axis="y"))
        blob(b, px + dx, y0 + h + 1, pz + dz, 3.2, 0.9, 3.2, ACACIA, rng)
    blob(b, px, y0 + h + 1, pz, 3.6, 1.0, 3.6, ACACIA, rng)


def tree_fern(b, x, z, rng):
    """Boomvaren (hapu'u) van het nevelwoud."""
    y0 = ground(b, x, z)
    h = rng.randint(3, 5)
    for i in range(h):
        log(b, x, y0 + i, z, st("stripped_spruce_log", axis="y") if i % 2 else st("spruce_log", axis="y"))
    ty = y0 + h
    b.setk(x, ty, z, AZALEA)
    for fx, fz in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        L = 2 if (fx and fz) else 3
        for j in range(1, L + 1):
            b.setk(x + fx * j, ty - (1 if j == L else 0), z + fz * j, AZALEA)


def bush(b, x, z, rng, leaf=None):
    y0 = ground(b, x, z)
    leaf = leaf or rng.choice([LEAF, LEAF, AZALEA, FAZALEA])
    b.setk(x, y0, z, st("jungle_log", axis="y"))
    blob(b, x, y0 + 1, z, rng.uniform(1.6, 2.6), 1.2, rng.uniform(1.6, 2.6), leaf, rng)


def bamboo_clump(b, x, z, rng):
    for _ in range(rng.randint(5, 12)):
        bx, bz = x + rng.randint(-2, 2), z + rng.randint(-2, 2)
        if not b.inb(bx, bz):
            continue
        y0 = ground(b, bx, bz)
        h = rng.randint(7, 16)
        if not all(b.is_air(bx, y0 + i, bz) for i in range(h)):
            continue
        for i in range(h):
            leaves = "large" if i >= h - 2 else "small" if i >= h - 4 else "none"
            b.set(bx, y0 + i, bz, st("bamboo", age=1, leaves=leaves, stage=0))


def mangrove(b, x, z, rng):
    y0 = ground(b, x, z)
    top = y0 + rng.randint(3, 4)
    for a, c in ((-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)):
        for yy in range(y0 - 1, top):
            b.setk(x + a, yy, z + c, st("mangrove_roots", waterlogged="false"))
    h = rng.randint(4, 7)
    for i in range(h):
        log(b, x, top + i, z, st("mangrove_log", axis="y"))
    leaves = []
    blob(b, x, top + h, z, 3.0, 1.6, 3.0, MANGROVE, rng, out=leaves)
    for _ in range(4):
        lx, ly, lz = rng.choice(leaves)
        if b.is_air(lx, ly - 1, lz):
            b.set(lx, ly - 1, lz, st("mangrove_propagule", hanging="true", age=4))


def dead_tree(b, x, z, rng):
    y0 = ground(b, x, z)
    h = rng.randint(3, 6)
    for i in range(h):
        log(b, x, y0 + i, z, st("dark_oak_log", axis="y") if i < h - 1 else st("stripped_dark_oak_log", axis="y"))
    for _ in range(rng.randint(1, 2)):
        dx, dz = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        log(b, x + dx, y0 + h - 1 - rng.randint(0, 1), z + dz, st("dark_oak_log", axis="x" if dx else "z"))


def boulder(b, x, z, rng, mats=("stone", "andesite", "mossy_cobblestone", "cobblestone", "tuff")):
    y0 = ground(b, x, z) - 1
    r = rng.uniform(1.2, 2.6)
    for a in range(-3, 4):
        for c in range(-3, 4):
            for y in range(0, 4):
                if (a / r) ** 2 + (c / r) ** 2 + (y / (r * 0.8)) ** 2 <= 1 + rng.uniform(-0.2, 0.1):
                    b.set(x + a, y0 + y, z + c, rng.choice(mats))
    if rng.random() < 0.5:
        b.setk(x, y0 + round(r * 0.8) + 1, z, "moss_carpet")
