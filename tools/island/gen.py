#!/usr/bin/env python3
"""Genereert het complete Hawaii/Polynesie-eiland (36x36 chunks) als structuren + functies.

Gebruik: python3 tools/island_generate.py [--preview]
"""
import json
import math
import random
import re
import struct
import sys
import time
import zlib
from collections import defaultdict

import numpy as np

from generate import MCDATA, depends_on
from world import parse_state, st

from . import flora
from .buffer import AIR, ObjBuf
from .builds import IslandPlanner
from .noise import fbm
from .terrain import (BAMBOO, BEACH, BIOMES, BLACKBEACH, CANYON, CLIFF, CRATER, DEEP, HIGHLAND, LAGOON, MEADOW, MOTU,
                      PEAK, PLANTATION, RAINFOREST, REEF, RIVERBANK, S, SEA, TOP, TOWN, VILLAGE, VOLCANIC, X0, YMIN,
                      N, Island)

DATA_VERSION = 3955
WINDOW = 10  # aantal chunks dat vooruit geladen wordt
CORALS = ["tube", "brain", "bubble", "fire", "horn"]
FLOWERS = ["red_tulip", "orange_tulip", "pink_tulip", "allium", "blue_orchid", "torchflower", "poppy", "oxeye_daisy",
           "cornflower", "dandelion"]
TALL = ["rose_bush", "peony", "lilac", "pitcher_plant", "sunflower"]


def crand(x, z, salt=0):
    """Deterministisch 'random' getal 0..1 per kolom."""
    h = (x * 73856093) ^ (z * 19349663) ^ (salt * 83492791)
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


# ===================================================================== bomen plannen
TREES = [
    # naam, rastergrootte, zones+kans, functie, straal (voor afstand), max helling
    ("giant", 12, {RAINFOREST: 0.6, RIVERBANK: 0.15, HIGHLAND: 0.12}, flora.giant_tree, 13, 2),
    ("banyan", 30, {VILLAGE: 0.5, RAINFOREST: 0.15, TOWN: 0.25, MEADOW: 0.1}, flora.banyan, 16, 1),
    ("jungle", 5, {RAINFOREST: 0.7, RIVERBANK: 0.4, BAMBOO: 0.2, HIGHLAND: 0.35, CLIFF: 0.12, PEAK: 0.05}, flora.jungle_tree, 6, 2),
    ("palm", 6, {BEACH: 0.75, VILLAGE: 0.3, RIVERBANK: 0.12, RAINFOREST: 0.04, TOWN: 0.12,
                 BLACKBEACH: 0.3, PLANTATION: 0.04, MEADOW: 0.03}, flora.palm, 7, 2),
    ("koa", 11, {MEADOW: 0.25, HIGHLAND: 0.3, PEAK: 0.08}, flora.koa, 6, 2),
    ("treefern", 5, {HIGHLAND: 0.45, PEAK: 0.18, CLIFF: 0.18, RAINFOREST: 0.12}, flora.tree_fern, 4, 4),
    ("plumeria", 9, {VILLAGE: 0.5, TOWN: 0.4, MEADOW: 0.08, BEACH: 0.06, RAINFOREST: 0.03, PLANTATION: 0.05},
     lambda b, x, z, r: flora.flowering_tree(b, x, z, r, "plumeria"), 5, 2),
    ("monkeypod", 22, {MEADOW: 0.4, PLANTATION: 0.15, TOWN: 0.2, RIVERBANK: 0.06, RAINFOREST: 0.03},
     lambda b, x, z, r: flora.flowering_tree(b, x, z, r, "monkeypod"), 8, 2),
    ("bush", 3, {RAINFOREST: 0.35, RIVERBANK: 0.25, HIGHLAND: 0.25, BAMBOO: 0.12, MEADOW: 0.04, BEACH: 0.05,
                 VILLAGE: 0.05, CLIFF: 0.1}, flora.bush, 3, 3),
    ("bamboo", 5, {BAMBOO: 0.8, RIVERBANK: 0.12, RAINFOREST: 0.06}, flora.bamboo_clump, 3, 3),
    ("dead", 12, {VOLCANIC: 0.25}, flora.dead_tree, 4, 4),
    ("boulder", 9, {PEAK: 0.3, CLIFF: 0.15, HIGHLAND: 0.08, CANYON: 0.12, RIVERBANK: 0.05, BLACKBEACH: 0.15,
                    MEADOW: 0.03, RAINFOREST: 0.02, BEACH: 0.015}, flora.boulder, 4, 6),
]


def plan_trees(isl, rng):
    plans = []
    occ = defaultdict(list)

    def free(x, z, r):
        cx, cz = x // 16, z // 16
        for a in (cx - 1, cx, cx + 1):
            for c in (cz - 1, cz, cz + 1):
                for (px, pz, pr) in occ[(a, c)]:
                    if (px - x) ** 2 + (pz - z) ** 2 < (min(r, pr) * 0.7) ** 2:
                        return False
        return True

    for name, cell, zones, fn, r, maxslope in TREES:
        for gx in range(X0, X0 + S, cell):
            for gz in range(X0, X0 + S, cell):
                x = gx + rng.randrange(cell)
                z = gz + rng.randrange(cell)
                if not (X0 + 3 <= x < X0 + S - 4 and X0 + 3 <= z < X0 + S - 4):
                    continue
                ix, iz = x - X0, z - X0
                zone = int(isl.zone[ix, iz])
                p = zones.get(zone, 0)
                if name == "palm" and zone == MOTU:
                    continue
                if name == "palm" and isl.dc[ix, iz] < 26 and zone in (RAINFOREST, RIVERBANK, MEADOW, VILLAGE, TOWN, BAMBOO):
                    p = max(p, 0.4)
                if p <= 0 or rng.random() > p:
                    continue
                if isl.slope[ix, iz] > maxslope or isl.H[ix, iz] < SEA or isl.liq_top[ix, iz] > -999:
                    continue
                rr = max(2, r - 3)
                sl = (slice(max(0, ix - rr), ix + rr + 1), slice(max(0, iz - rr), iz + rr + 1))
                if isl.res[sl].any() or isl.road[max(0, ix - 1):ix + 2, max(0, iz - 1):iz + 2].any():
                    continue
                if isl.river_wet[max(0, ix - 1):ix + 2, max(0, iz - 1):iz + 2].any():
                    continue
                if name in ("giant", "banyan") and isl.H[min(S - 1, ix + 1), min(S - 1, iz + 1)] < isl.H[ix, iz] - 1:
                    continue
                if not free(x, z, r):
                    continue
                occ[(x // 16, z // 16)].append((x, z, r))
                seed = rng.randrange(1 << 30)
                R = r + 6
                plans.append((name, (x - R, z - R, x + R, z + R), fn, x, z, seed))
    # mangroven bij de monding van rivier A
    mx, mz = isl.sites["mouthA"]
    for _ in range(60):
        x, z = mx + rng.randint(-26, 26), mz + rng.randint(-26, 26)
        ix, iz = x - X0, z - X0
        if 0 <= ix < S and 0 <= iz < S and SEA <= isl.H[ix, iz] <= SEA + 1 and not isl.res[ix, iz] \
                and not isl.river_wet[ix, iz] and free(x, z, 4):
            occ[(x // 16, z // 16)].append((x, z, 4))
            plans.append(("mangrove", (x - 8, z - 8, x + 8, z + 8), flora.mangrove, x, z, rng.randrange(1 << 30)))
    return plans


# ===================================================================== dieren
def fish_variant(rng):
    v = rng.randint(0, 1) | (rng.randint(0, 5) << 8) | (rng.randint(0, 15) << 16) | (rng.randint(0, 15) << 24)
    return v - (1 << 32) if v >= 1 << 31 else v


def plan_fauna(isl, rng):
    """Dieren verspreid over het eiland (als summon-commando's per chunk)."""
    out = []
    tag = 'Tags:["hawaii_ent","hawaii_isl"],PersistenceRequired:1b'
    zone, H = isl.zone, isl.H

    def pick(zones, n, cond=None):
        idx = np.argwhere(np.isin(zone, list(zones)) & ~isl.res)
        res = []
        for _ in range(n * 4):
            if len(res) >= n or len(idx) == 0:
                break
            ix, iz = idx[rng.randrange(len(idx))]
            if cond and not cond(ix, iz):
                continue
            res.append((int(ix) + X0, int(iz) + X0, int(H[ix, iz])))
        return res

    def add(et, x, y, z, nbt=""):
        out.append((x, z, f"summon minecraft:{et} ~{x}.5 ~{y} ~{z}.5 {{{tag}{',' + nbt if nbt else ''}}}"))

    for x, z, h in pick([RAINFOREST, RIVERBANK, BAMBOO, VILLAGE], 45):
        add("parrot", x, h + 2, z, f"Variant:{rng.randint(0, 4)}")
    for x, z, h in pick([RAINFOREST, VILLAGE, PLANTATION, MEADOW, BEACH], 30):
        add("chicken", x, h + 1, z)
    for x, z, h in pick([RAINFOREST], 8):
        add("ocelot", x, h + 1, z)
    for x, z, h in pick([BAMBOO], 8):
        add("panda", x, h + 1, z, f'MainGene:"{rng.choice(["normal", "lazy", "playful", "aggressive"])}",HiddenGene:"normal"')
    for x, z, h in pick([PEAK, HIGHLAND, CLIFF], 10):
        add("goat", x, h + 1, z)
    for x, z, h in pick([BEACH, BLACKBEACH, MOTU], 14):
        add("turtle", x, h + 1, z)
    for x, z, h in pick([RIVERBANK], 12):
        add("frog", x, h + 1, z, 'variant:"minecraft:warm"')
    for x, z, h in pick([MEADOW], 8):
        add("rabbit", x, h + 1, z, f"RabbitType:{rng.choice([0, 1, 3, 5])}")
    sea = lambda ix, iz: SEA - H[ix, iz] >= 3
    for x, z, h in pick([LAGOON, REEF], 45, sea):
        var = fish_variant(rng)
        for _ in range(rng.randint(3, 6)):
            out.append((x, z, f"summon minecraft:tropical_fish ~{x + rng.random():.2f} ~{rng.randint(h + 1, SEA)} "
                               f"~{z + rng.random():.2f} {{{tag},Variant:{var}}}"))
    for x, z, h in pick([LAGOON, REEF], 8, sea):
        add("pufferfish", x, h + 1, z)
    for x, z, h in pick([DEEP], 10, lambda ix, iz: SEA - H[ix, iz] >= 6):
        add("dolphin", x, SEA - 1, z)
    wet = np.argwhere(isl.river_wet & (isl.liq_top - isl.H >= 2))
    for _ in range(10):
        if len(wet):
            ix, iz = wet[rng.randrange(len(wet))]
            add("axolotl", int(ix) + X0, int(isl.H[ix, iz]) + 1, int(iz) + X0, f"Variant:{rng.randint(0, 3)}")
    return out


# ===================================================================== materialen
class Materials:
    def __init__(self, isl):
        self.isl = isl
        X, Z = isl.X, isl.Z
        self.n1 = fbm(X / 9, Z / 9, 501, 3)
        self.n2 = fbm(X / 5 + 40, Z / 5, 502, 2)
        self.n3 = fbm(X / 22, Z / 22, 503, 2)

    def column(self, x, z):
        """Lijst van (y, blok) van het oppervlak naar beneden (diepte 0..)."""
        isl = self.isl
        ix, iz = x - X0, z - X0
        zone = int(isl.zone[ix, iz])
        h = int(isl.H[ix, iz])
        n1, n2, n3 = self.n1[ix, iz], self.n2[ix, iz], self.n3[ix, iz]
        slope = int(isl.slope[ix, iz])
        road = bool(isl.road[ix, iz])
        wet = bool(isl.river_wet[ix, iz])
        steep = slope >= 3

        def rock(y):
            v = math.sin(y * 0.55 + n3 * 3)
            if zone == CANYON:
                bands = ["orange_terracotta", "terracotta", "red_terracotta", "white_terracotta", "yellow_terracotta",
                         "brown_terracotta", "orange_terracotta", "light_gray_terracotta"]
                return bands[int((y + n3 * 3) // 2) % len(bands)]
            if zone in (VOLCANIC, CRATER, BLACKBEACH):
                return "basalt[axis=y]" if v > 0 else "blackstone"
            if v > 0.6:
                return "andesite"
            if v < -0.7:
                return "tuff"
            if n2 > 0.45:
                return "mossy_cobblestone"
            return "stone"

        if zone in (DEEP, LAGOON, REEF) or (h < SEA and not wet):
            if zone == REEF and h >= SEA - 2:
                top = f"{CORALS[int(abs(n2) * 50) % 5]}_coral_block" if n1 > -0.3 else rock(h)
            elif zone == DEEP and h < SEA - 7:
                top = "gravel" if n1 > 0.35 else "clay" if n2 > 0.55 else "sand"
            else:
                top = "sand" if n2 > -0.55 else "gravel"
            return top, lambda d, y: "sand" if d < 3 else "sandstone" if d < 5 else "stone"
        if wet:
            top = "gravel" if n2 > 0.2 else "clay" if n1 > 0.3 else "sand"
            if zone == CANYON:
                top = "gravel" if n2 > -0.2 else "red_sand"
            return top, lambda d, y: "gravel" if d < 2 else rock(y)
        if zone in (BEACH, MOTU):
            top = "sand"
            if road:
                top = "sand"
            return top, lambda d, y: "sand" if d < 3 else "sandstone" if d < 5 else "stone"
        if zone == BLACKBEACH:
            top = "black_concrete_powder" if h > SEA else "blackstone"
            return top, lambda d, y: "black_concrete_powder" if d < 2 and h > SEA else "basalt[axis=y]"
        if zone in (VOLCANIC, CRATER):
            v = isl.volcano
            r = math.hypot(x - v["x"], z - v["z"]) / v["r"]
            ang = math.atan2(z - v["z"], x - v["x"])
            streak = abs(math.sin(ang * 4 + 2 * n3))
            if zone == CRATER:
                top = "magma_block"
            elif 0.15 < r < 0.85 and streak < 0.07:
                top = "magma_block"
            elif r < 0.2:
                top = "obsidian" if n2 > 0.2 else "blackstone"
            elif r > 0.85:
                top = "coarse_dirt" if n1 > 0.1 else "tuff"
            else:
                c = n1 + 0.6 * n2
                top = "smooth_basalt" if c > 0.35 else "tuff" if c < -0.35 else "basalt[axis=y]" if n2 > 0 else "blackstone"
            return top, lambda d, y: ("magma_block" if top == "magma_block" and d < 2 else "basalt[axis=y]" if d < 5 else "stone")
        if zone == CANYON:
            top = "coarse_dirt" if n2 > 0.3 else "red_sand" if n1 > 0.2 else "grass_block"
            return top, lambda d, y: rock(y)
        if zone == PEAK or (zone == CLIFF and steep):
            if slope <= 2 and n1 > -0.2:
                top = "grass_block" if n2 < 0.3 else "moss_block"
            else:
                top = rock(h) if n2 < 0.5 else "moss_block"
            return top, lambda d, y: rock(y)
        if road:
            top = "dirt_path"
        elif zone == HIGHLAND:
            top = "moss_block" if n2 > 0.5 else "grass_block" if n1 > -0.6 else "podzol"
        elif zone in (RAINFOREST, BAMBOO):
            top = "podzol" if n1 > 0.5 or (zone == BAMBOO and n1 > 0.1) else "moss_block" if n2 > 0.6 else \
                "rooted_dirt" if n2 < -0.7 else "coarse_dirt" if n1 < -0.65 else "grass_block"
        elif zone == RIVERBANK:
            top = "mud" if n2 > 0.55 else "grass_block" if n1 > -0.4 else "sand"
        elif zone == MEADOW:
            top = "grass_block" if n1 > -0.7 else "coarse_dirt"
        else:
            top = "grass_block"
        return top, lambda d, y: (rock(y) if steep and d > 0 else "dirt" if d < 4 else rock(y))


def ground_cover(isl, blocks, x, z, h, top, rng_v):
    """Planten op 1 kolom (alleen als de plek leeg is)."""
    zone = int(isl.zone[x - X0, z - X0])
    above = (x, h + 1, z)
    if above in blocks:
        return
    r = rng_v
    if top in ("minecraft:grass_block", "minecraft:podzol", "minecraft:moss_block", "minecraft:rooted_dirt",
               "minecraft:coarse_dirt", "minecraft:mud"):
        if isl.road[x - X0, z - X0]:
            return
        two = (x, h + 2, z) not in blocks
        if zone in (RAINFOREST, BAMBOO, RIVERBANK):
            if r < 0.22:
                blocks[above] = "minecraft:fern"
            elif r < 0.30 and two:
                blocks[above] = "minecraft:large_fern[half=lower]"
                blocks[(x, h + 2, z)] = "minecraft:large_fern[half=upper]"
            elif r < 0.40:
                blocks[above] = "minecraft:short_grass"
            elif r < 0.43:
                blocks[above] = "minecraft:" + FLOWERS[int(r * 1000) % len(FLOWERS)]
            elif r < 0.46 and top == "minecraft:moss_block":
                blocks[above] = "minecraft:moss_carpet"
            elif r < 0.475:
                blocks[above] = "minecraft:" + ("flowering_azalea" if r < 0.468 else "azalea")
            elif zone == BAMBOO and r < 0.55:
                blocks[above] = "minecraft:bamboo_sapling"
        elif zone in (MEADOW, PLANTATION, TOWN, VILLAGE):
            if r < 0.34:
                blocks[above] = "minecraft:short_grass"
            elif r < 0.40 and two:
                blocks[above] = "minecraft:tall_grass[half=lower]"
                blocks[(x, h + 2, z)] = "minecraft:tall_grass[half=upper]"
            elif r < 0.50:
                blocks[above] = "minecraft:" + FLOWERS[int(r * 1000) % len(FLOWERS)]
            elif r < 0.52 and two:
                k = TALL[int(r * 997) % len(TALL)]
                blocks[above] = f"minecraft:{k}[half=lower]"
                blocks[(x, h + 2, z)] = f"minecraft:{k}[half=upper]"
            elif r < 0.56 and zone == MEADOW:
                blocks[above] = f"minecraft:pink_petals[facing=north,flower_amount={1 + int(r * 400) % 4}]"
        elif zone in (HIGHLAND, PEAK, CLIFF):
            if r < 0.2:
                blocks[above] = "minecraft:short_grass"
            elif r < 0.3:
                blocks[above] = "minecraft:fern"
            elif r < 0.36:
                blocks[above] = "minecraft:moss_carpet"
            elif r < 0.38:
                blocks[above] = "minecraft:azalea"
        elif zone == CANYON:
            if r < 0.05:
                blocks[above] = "minecraft:dead_bush"
            elif r < 0.12:
                blocks[above] = "minecraft:short_grass"
    elif top == "minecraft:sand" and zone in (BEACH, MOTU):
        if r < 0.01:
            blocks[above] = f"minecraft:dead_{CORALS[int(r * 5000) % 5]}_coral_fan[waterlogged=false]"
        elif r < 0.013:
            blocks[above] = "minecraft:dead_bush"
        elif r < 0.0145:
            blocks[above] = "minecraft:turtle_egg[eggs=2,hatch=0]"
    elif top in ("minecraft:basalt[axis=y]", "minecraft:blackstone", "minecraft:tuff") and zone == VOLCANIC:
        if r < 0.01:
            blocks[above] = "minecraft:dead_bush"


def underwater(isl, blocks, x, z, h, r):
    """Zeegras, koraal, kelp in zee en lagune (water komt later via fill)."""
    zone = int(isl.zone[x - X0, z - X0])
    depth = SEA - h
    if depth < 1 or (x, h + 1, z) in blocks:
        return
    if zone == REEF or (zone == LAGOON and r < 0.08 and depth >= 2):
        if r < 0.5:
            blocks[(x, h + 1, z)] = f"minecraft:{CORALS[int(r * 977) % 5]}_coral_block"
            if depth >= 2:
                blocks[(x, h + 2, z)] = f"minecraft:{CORALS[int(r * 613) % 5]}_coral{'_fan' if r < 0.25 else ''}[waterlogged=true]"
        elif r < 0.62:
            blocks[(x, h + 1, z)] = f"minecraft:sea_pickle[pickles={1 + int(r * 400) % 4},waterlogged=true]"
        elif r < 0.8:
            blocks[(x, h + 1, z)] = f"minecraft:{CORALS[int(r * 313) % 5]}_coral[waterlogged=true]"
    elif zone == LAGOON:
        if r < 0.28:
            blocks[(x, h + 1, z)] = "minecraft:seagrass"
        elif r < 0.36 and depth >= 2:
            blocks[(x, h + 1, z)] = "minecraft:tall_seagrass[half=lower]"
            blocks[(x, h + 2, z)] = "minecraft:tall_seagrass[half=upper]"
        elif r < 0.38:
            blocks[(x, h + 1, z)] = f"minecraft:sea_pickle[pickles={1 + int(r * 400) % 4},waterlogged=true]"
    elif zone == DEEP:
        if depth >= 6 and r < 0.2:
            kh = 2 + int(r * 997) % max(1, depth - 3)
            for i in range(kh):
                blocks[(x, h + 1 + i, z)] = "minecraft:kelp_plant" if i < kh - 1 else "minecraft:kelp[age=25]"
        elif r < 0.35:
            blocks[(x, h + 1, z)] = "minecraft:seagrass"


# ===================================================================== NBT snel schrijven
def template_bytes(size, palette, blocks):
    out = bytearray()

    def tag(t, name):
        nb = name.encode()
        out.extend(struct.pack(">bH", t, len(nb)))
        out.extend(nb)

    def string(s):
        b = s.encode()
        out.extend(struct.pack(">H", len(b)))
        out.extend(b)

    tag(10, "")
    tag(3, "DataVersion")
    out.extend(struct.pack(">i", DATA_VERSION))
    tag(9, "size")
    out.extend(struct.pack(">bi", 3, 3))
    out.extend(struct.pack(">iii", *size))
    tag(9, "palette")
    out.extend(struct.pack(">bi", 10, len(palette)))
    for s in palette:
        name, props = parse_state(s)
        tag(8, "Name")
        string(name)
        if props:
            tag(10, "Properties")
            for k, v in props.items():
                tag(8, k)
                string(v)
            out.append(0)
        out.append(0)
    tag(9, "blocks")
    out.extend(struct.pack(">bi", 10, len(blocks)))
    pos_hdr = struct.pack(">bH", 9, 3) + b"pos" + struct.pack(">bi", 3, 3)
    st_hdr = struct.pack(">bH", 3, 5) + b"state"
    for x, y, z, i in blocks:
        out.extend(pos_hdr)
        out.extend(struct.pack(">iii", x, y, z))
        out.extend(st_hdr)
        out.extend(struct.pack(">i", i))
        out.append(0)
    tag(9, "entities")
    out.extend(struct.pack(">bi", 0, 0))
    out.append(0)
    return bytes(out)


def gzip_bytes(data):
    co = zlib.compressobj(6, zlib.DEFLATED, 31)
    raw = co.compress(data) + co.flush()
    # vaste header-tijd zodat de output deterministisch is
    return raw[:4] + b"\x00\x00\x00\x00" + raw[8:]


# ===================================================================== hoofdprogramma
def run(root, preview=False):
    t0 = time.time()
    rng = random.Random(1234)
    isl = Island(7)
    isl.build()
    planner = IslandPlanner(isl, rng)
    planner.plan_all()
    isl.after_planning()
    trees = plan_trees(isl, rng)
    fauna = plan_fauna(isl, rng)
    mats = Materials(isl)
    print(f"  plan klaar: {len(planner.plans)} gebouwen, {len(trees)} bomen/rotsen ({time.time() - t0:.0f}s)")

    # objecten (gebouwen eerst, dan natuur) gesorteerd op de eerste chunk-rij die ze raken
    objs = []
    for p in planner.plans:
        objs.append((p.bbox, "force", p.fn, None))
    for name, bbox, fn, x, z, seed in trees:
        objs.append((bbox, "keep", fn, (x, z, seed)))
    objs.sort(key=lambda o: (max(0, (o[0][1] - X0) // 16), 0 if o[1] == "force" else 1))
    data = root / "hawaii_beach" / "data" / "hawaii"
    sdir = data / "structure" / "island"
    gdir = data / "function" / "gen" / "island"
    for d in (sdir, gdir):
        d.mkdir(parents=True, exist_ok=True)
        for f in d.iterdir():
            f.unlink()
    buckets = defaultdict(list)  # (cx, cz) -> [(mode, x, y, z, state)]
    ents = defaultdict(list)
    for x, z, c in fauna:
        ents[((x - X0) // 16, (z - X0) // 16)].append(c)
    late_extra = defaultdict(list)
    cmds_end = []
    oi = 0
    total_blocks = 0
    states = set()
    all_cmds = []
    late_by_chunk = {}
    chunk_info = {}
    top_img = np.zeros((S, S, 3), dtype=np.uint8) if preview else None
    keep_blocks = {} if preview else None

    def chunk_of(x, z):
        return (x - X0) // 16, (z - X0) // 16

    for cz in range(N):
        # bouw alle objecten die in deze rij beginnen
        while oi < len(objs) and max(0, (objs[oi][0][1] - X0) // 16) <= cz:
            bbox, mode, fn, extra = objs[oi]
            oi += 1
            if extra is None:
                buf = ObjBuf(isl, rng, mode)
                fn(buf)
            else:
                x, z, seed = extra
                buf = ObjBuf(isl, random.Random(seed), mode)
                fn(buf, x, z, buf.rng)
            for (x, y, z), s in buf.blk.items():
                buckets[chunk_of(x, z)].append((mode, x, y, z, s))
            for x, z, c in buf.ents:
                ents[chunk_of(int(math.floor(x)), int(math.floor(z)))].append(c)
            for x, z, c in buf.late:
                late_extra[chunk_of(x, z)].append(c)
            cmds_end.extend(buf.cmds_end)
        for cx in range(N):
            px, pz = X0 + 16 * cx, X0 + 16 * cz
            blocks = {}
            Hs = isl.H[px - X0:px - X0 + 16, pz - X0:pz - X0 + 16]
            base = max(YMIN, int(Hs.min()) - 3)
            tops = {}
            for x in range(px, px + 16):
                for z in range(pz, pz + 16):
                    ix, iz = x - X0, z - X0
                    h = int(isl.H[ix, iz])
                    top, below = mats.column(x, z)
                    blocks[(x, h, z)] = "minecraft:" + top
                    for y in range(base, h):
                        blocks[(x, y, z)] = "minecraft:" + below(h - y, y)
                    tops[(x, z)] = (h, "minecraft:" + top)
                    lt = int(isl.liq_top[ix, iz])
                    if lt > -999:
                        liq = "minecraft:lava" if isl.liq_lava[ix, iz] else "minecraft:water"
                        for y in range(max(h + 1, SEA + 1), lt + 1):
                            blocks[(x, y, z)] = liq
            # objecten
            for mode, x, y, z, s in buckets.pop((cx, cz), []):
                if y < base:
                    continue
                key = (x, y, z)
                if mode == "force":
                    if s == AIR:
                        blocks.pop(key, None)
                    else:
                        blocks[key] = s
                else:
                    cur = blocks.get(key)
                    if cur is None or (cur == "minecraft:water" and ("waterlogged=true" in s or "seagrass" in s)):
                        blocks[key] = s
            # planten, koraal en licht per kolom
            for (x, z), (h, top) in tops.items():
                r = crand(x, z, 7)
                cur_top = blocks.get((x, h, z), top)
                if h < SEA or (int(isl.liq_top[x - X0, z - X0]) > h and not isl.liq_lava[x - X0, z - X0]):
                    if h < SEA and not isl.river_wet[x - X0, z - X0]:
                        underwater(isl, blocks, x, z, h, r)
                    elif isl.river_wet[x - X0, z - X0] and r < 0.25 and (x, h + 1, z) not in blocks:
                        blocks[(x, h + 1, z)] = "minecraft:seagrass"
                else:
                    if not isl.res[x - X0, z - X0] or (isl.zone[x - X0, z - X0] in (VILLAGE, TOWN, PLANTATION, MEADOW)
                                                        and r < 0.6):
                        ground_cover(isl, blocks, x, z, h, cur_top, r)
                    if isl.zone[x - X0, z - X0] == RIVERBANK and r < 0.3 and (x, h + 1, z) not in blocks \
                            and cur_top in ("minecraft:grass_block", "minecraft:sand", "minecraft:mud"):
                        wet = any(isl.river_wet[x + a - X0, z + c - X0] and isl.liq_top[x + a - X0, z + c - X0] == h
                                  for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                  if 0 <= x + a - X0 < S and 0 <= z + c - X0 < S)
                        if wet:
                            for i in range(1, 2 + int(r * 10) % 3):
                                blocks[(x, h + i, z)] = "minecraft:sugar_cane"
                if (x - X0) % 10 == 5 and (z - X0) % 10 == 5:
                    if h < SEA:
                        if (x, h + 1, z) not in blocks:
                            blocks[(x, h + 1, z)] = "minecraft:light[level=10,waterlogged=true]"
                    else:
                        for y in range(h + 2, h + 5):
                            if (x, y, z) not in blocks and (x, y - 1, z) not in blocks:
                                blocks[(x, y, z)] = "minecraft:light[level=9]"
                                break
            # late blokken (vast aan een buur in een andere chunk)
            late = []
            for (x, y, z), s in list(blocks.items()):
                name, props = parse_state(s)
                for dx, dy, dz in depends_on(name, props):
                    nx, nz = x + dx, z + dz
                    if X0 <= nx < X0 + S and X0 <= nz < X0 + S and chunk_of(nx, nz) != (cx, cz):
                        late.append((y, x, z, s))
                        del blocks[(x, y, z)]
                        break
            late.sort()
            late_cmds = [f"setblock ~{x} ~{y} ~{z} {s}" for y, x, z, s in late] + late_extra.pop((cx, cz), [])
            late_by_chunk[(cx, cz)] = late_cmds
            # template schrijven
            palette = {}
            items = []
            maxy = base
            for (x, y, z), s in sorted(blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
                if s == "minecraft:water" and y <= SEA:
                    continue
                idx = palette.setdefault(s, len(palette))
                items.append((x - px, y - base, z - pz, idx))
                maxy = max(maxy, y)
            states.update(palette)
            raw = template_bytes([16, maxy - base + 1, 16], list(palette), items)
            (sdir / f"c_{cx}_{cz}.nbt").write_bytes(gzip_bytes(raw))
            total_blocks += len(items)
            chunk_info[(cx, cz)] = base
            if preview:
                for (x, z), (h, _) in tops.items():
                    for y in range(TOP, base - 1, -1):
                        s = blocks.get((x, y, z))
                        if s and "light" not in s:
                            top_img[x - X0, z - X0] = preview_color(s, y)
                            break
                    else:
                        top_img[x - X0, z - X0] = (40, 120, 200)
                keep_blocks[(cx, cz)] = blocks
        print(f"  rij {cz + 1}/{N} klaar ({time.time() - t0:.0f}s)", end="\r", flush=True)
    print()

    # ------------------------------------------------------------- functies
    def chunk_pos(i):
        return X0 + 16 * (i % N), X0 + 16 * (i // N)

    total = N * N
    trigger = defaultdict(list)
    for cz in range(N):
        for cx in range(N):
            t = min(cz + 1, N - 1) * N + min(cx + 1, N - 1)
            trigger[t].append((cx, cz))
    for i in range(total):
        cx, cz = i % N, i // N
        px, pz = chunk_pos(i)
        base = chunk_info[(cx, cz)]
        lines = [f"# Chunk {cx},{cz} (gegenereerd door tools/island_generate.py)"]
        if i + WINDOW < total:
            ax, az = chunk_pos(i + WINDOW)
            lines.append(f"forceload add ~{ax} ~{az}")
        lines.append(f"fill ~{px} ~{YMIN} ~{pz} ~{px + 15} ~{TOP} ~{pz + 15} minecraft:air")
        if base > YMIN:
            lines.append(f"fill ~{px} ~{YMIN} ~{pz} ~{px + 15} ~{base - 1} ~{pz + 15} minecraft:stone")
        lines.append(f"place template hawaii:island/c_{cx}_{cz} ~{px} ~{base} ~{pz}")
        lines.append(f"fill ~{px} ~{YMIN} ~{pz} ~{px + 15} ~{SEA} ~{pz + 15} minecraft:water replace minecraft:air")
        lines += biome_cmds(isl, px, pz)
        lines += ents.pop((cx, cz), [])
        for ccx, ccz in trigger[i]:
            lines += late_by_chunk.pop((ccx, ccz), [])
        if i - (N + 2) >= 0:
            rx, rz = chunk_pos(i - (N + 2))
            lines.append(f"forceload remove ~{rx} ~{rz}")
        if i == total - 1:
            lines += cmds_end
        (gdir / f"k_{i}.mcfunction").write_text("\n".join(lines) + "\n")
        all_cmds += lines
    start = [f"forceload add ~{chunk_pos(i)[0]} ~{chunk_pos(i)[1]}" for i in range(min(WINDOW, total))]
    (gdir / "start.mcfunction").write_text("# Eerste chunks alvast laden\n" + "\n".join(start) + "\n")
    tx, ty, tz, yaw = planner.tp
    end = ["# Overgebleven chunks vrijgeven en speler naar de tiki bar"]
    end += [f"forceload remove ~{chunk_pos(i)[0]} ~{chunk_pos(i)[1]}" for i in range(max(0, total - (N + 2)), total)]
    end.append(f"tp @a[tag=hawaii_builder] ~{tx} ~{ty} ~{tz} {yaw} 5")
    (gdir / "end.mcfunction").write_text("\n".join(end) + "\n")
    write_biomes(data)
    print(f"  {total_blocks} blokken in {total} structuren, {sum(1 for c in all_cmds if c.startswith('summon'))} entities "
          f"({time.time() - t0:.0f}s)")
    errors = validate(states, all_cmds)
    if preview:
        from PIL import Image
        pdir = root / "tools" / "preview"
        pdir.mkdir(exist_ok=True)
        Image.fromarray(top_img.transpose(1, 0, 2)).resize((S * 2, S * 2), 0).save(pdir / "island_top.png")
        render_regions(isl, planner, keep_blocks, pdir)
    return errors


def biome_cmds(isl, px, pz):
    cmds = []
    for qz in range(4):
        row = []
        for qx in range(4):
            zs = isl.zone[px - X0 + 4 * qx:px - X0 + 4 * qx + 4, pz - X0 + 4 * qz:pz - X0 + 4 * qz + 4].ravel().tolist()
            row.append(max(sorted(set(zs)), key=zs.count))
        start = 0
        for qx in range(1, 5):
            if qx == 4 or BIOMES[row[qx]] != BIOMES[row[start]]:
                custom, vanilla = BIOMES[row[start]]
                x1, x2 = px + 4 * start, px + 4 * qx - 1
                z1, z2 = pz + 4 * qz, pz + 4 * qz + 3
                cmds.append(f"fillbiome ~{x1} ~{YMIN} ~{z1} ~{x2} ~{TOP} ~{z2} minecraft:{vanilla}")
                cmds.append(f"fillbiome ~{x1} ~{YMIN} ~{z1} ~{x2} ~{TOP} ~{z2} hawaii:{custom}")
                start = qx
    return cmds


# ===================================================================== biomen
def rgb(h):
    return int(h.lstrip("#"), 16)


BIOME_DEFS = {
    # naam: (gras, bladeren, water, waterfog, lucht, mist, temperatuur, neerslag, deeltje, kans, muziek)
    "tropical_ocean": ("#5fd13e", "#3fb43a", "#1fa4e0", "#0e5f9e", "#6db7ff", "#c7e4ff", 0.95, True, None, 0, "minecraft:music.overworld.jungle"),
    "coral_lagoon": ("#5fd13e", "#3fb43a", "#2fe3d4", "#21b8bf", "#6db7ff", "#c7e4ff", 0.95, True, None, 0, "minecraft:music.overworld.cherry_grove"),
    "white_sand_beach": ("#7fdc54", "#5ccc48", "#2fe3d4", "#21b8bf", "#6db7ff", "#d2ecff", 0.95, True, None, 0, "minecraft:music.overworld.cherry_grove"),
    "black_sand_beach": ("#6fb44a", "#4f9e3c", "#22b4c8", "#167d8f", "#7fb0f0", "#c4d6e8", 0.9, True, "minecraft:white_ash", 0.002, "minecraft:music.overworld.sparse_jungle"),
    "rainforest": ("#3fc32a", "#2fa82a", "#3fd1e8", "#2a9fb5", "#79b4ff", "#bfe0ee", 0.95, True, "minecraft:spore_blossom_air", 0.0025, "minecraft:music.overworld.jungle"),
    "bamboo_forest": ("#6ad63a", "#58c83a", "#3fd1e8", "#2a9fb5", "#79b4ff", "#c7e6d8", 0.95, True, "minecraft:spore_blossom_air", 0.0015, "minecraft:music.overworld.bamboo_jungle"),
    "cloud_forest": ("#4fb06a", "#3a9e5a", "#3fc8e0", "#2a8fa5", "#8cb8e8", "#e2ecf2", 0.8, True, "minecraft:white_ash", 0.004, "minecraft:music.overworld.sparse_jungle"),
    "volcanic_slopes": ("#8a8f5a", "#6e7a45", "#2f7f8a", "#1d5560", "#9aa6b8", "#a8a8a8", 1.0, False, "minecraft:ash", 0.02, "minecraft:music.overworld.badlands"),
    "upland_meadow": ("#8fd14f", "#6cb846", "#3fd1e8", "#2a9fb5", "#6db7ff", "#d2ecff", 0.85, True, None, 0, "minecraft:music.overworld.meadow"),
    "sugar_plantation": ("#a8c95a", "#7db44a", "#3fd1e8", "#2a9fb5", "#73b8ff", "#e4eecc", 0.95, True, None, 0, "minecraft:music.overworld.meadow"),
    "polynesian_village": ("#59d13e", "#3bbf35", "#2fe3d4", "#21b8bf", "#6db7ff", "#ffe6c7", 0.95, True, "minecraft:cherry_leaves", 0.0035, "minecraft:music.overworld.cherry_grove"),
    "colonial_town": ("#9ccf5a", "#7cbf4a", "#2fd8d0", "#21b0b8", "#74b6ff", "#ffe9cf", 0.95, True, None, 0, "minecraft:music.overworld.desert"),
    "red_canyon": ("#b9a65b", "#9e8f4a", "#47c3d6", "#2c8fa0", "#8fb4ff", "#f0c9a0", 1.0, False, None, 0, "minecraft:music.overworld.badlands"),
    "jungle_river": ("#47c936", "#36b034", "#42d9ee", "#2ab0c4", "#79b4ff", "#c7e6f0", 0.95, True, None, 0, "minecraft:music.overworld.jungle"),
}

CREATURES = {
    "rainforest": [("parrot", 40, 1, 2), ("ocelot", 4, 1, 1), ("panda", 2, 1, 2), ("chicken", 8, 2, 3)],
    "bamboo_forest": [("panda", 30, 1, 2), ("parrot", 20, 1, 2)],
    "cloud_forest": [("parrot", 20, 1, 2), ("rabbit", 6, 1, 2)],
    "upland_meadow": [("horse", 10, 2, 4), ("cow", 8, 2, 4), ("rabbit", 6, 2, 3)],
    "sugar_plantation": [("chicken", 10, 2, 4), ("pig", 6, 1, 3)],
    "polynesian_village": [("chicken", 20, 2, 4), ("pig", 8, 1, 2), ("parrot", 10, 1, 2)],
    "colonial_town": [("cat", 10, 1, 2), ("chicken", 6, 1, 2)],
    "white_sand_beach": [("turtle", 10, 2, 4)],
    "black_sand_beach": [("turtle", 20, 2, 5)],
    "jungle_river": [("frog", 10, 2, 4), ("parrot", 10, 1, 2)],
}
WATER = {
    "tropical_ocean": [("dolphin", 2, 1, 2), ("squid", 2, 1, 2)],
    "coral_lagoon": [],
    "jungle_river": [],
}
WATER_AMBIENT = {
    "tropical_ocean": [("tropical_fish", 25, 8, 8), ("pufferfish", 15, 1, 3)],
    "coral_lagoon": [("tropical_fish", 30, 8, 8), ("pufferfish", 10, 1, 3)],
    "jungle_river": [("tropical_fish", 10, 4, 6)],
}


def write_biomes(data):
    bdir = data / "worldgen" / "biome"
    bdir.mkdir(parents=True, exist_ok=True)
    for name, (grass, foliage, water, wfog, sky, fog, temp, rain, particle, prob, music) in BIOME_DEFS.items():
        effects = {
            "sky_color": rgb(sky), "fog_color": rgb(fog), "water_color": rgb(water), "water_fog_color": rgb(wfog),
            "grass_color": rgb(grass), "foliage_color": rgb(foliage),
            "mood_sound": {"sound": "minecraft:ambient.cave", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0},
            "music": {"sound": music, "min_delay": 12000, "max_delay": 24000, "replace_current_music": False},
        }
        if particle:
            effects["particle"] = {"options": {"type": particle}, "probability": prob}

        def spawns(table):
            return [{"type": f"minecraft:{t}", "weight": w, "minCount": a, "maxCount": b} for t, w, a, b in table.get(name, [])]
        biome = {
            "has_precipitation": rain,
            "temperature": temp,
            "downfall": 0.9 if rain else 0.0,
            "effects": effects,
            "spawners": {"monster": [], "creature": spawns(CREATURES), "ambient": [], "axolotls": [],
                         "underground_water_creature": [], "water_creature": spawns(WATER),
                         "water_ambient": spawns(WATER_AMBIENT), "misc": []},
            "spawn_costs": {},
            "carvers": {"air": [], "liquid": []},
            "features": [[] for _ in range(11)],
        }
        (bdir / f"{name}.json").write_text(json.dumps(biome, indent=2) + "\n")


# ===================================================================== controle
def validate(states, cmds):
    errors = []
    blocks = MCDATA["blocks"]
    cmd_states = [re.match(r"setblock \S+ \S+ \S+ ([^{\s]+)", c).group(1) for c in cmds if c.startswith("setblock")]
    for s in set(states) | set(cmd_states):
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
    text = "\n".join(cmds)
    for e in set(re.findall(r"summon minecraft:(\w+)", text)):
        if e not in MCDATA["entities"]:
            errors.append(f"onbekende entity {e}")
    for i in set(re.findall(r'id:"minecraft:(\w+)"', text)):
        if i not in MCDATA["items"] and i not in ("regeneration", "water_breathing", "speed", "fire_resistance",
                                                  "jump_boost", "night_vision"):
            errors.append(f"onbekend item {i}")
    for b in set(re.findall(r'Name:"minecraft:(\w+)"', text)):
        if b not in blocks:
            errors.append(f"onbekend blok in display {b}")
    for b in set(re.findall(r"fillbiome .* minecraft:(\w+)$", text, re.M)):
        if b not in MCDATA["biomes"]:
            errors.append(f"onbekend biome {b}")
    for c in cmds:
        if c.count("{") != c.count("}") or c.count("[") != c.count("]"):
            errors.append(f"haakjes kloppen niet: {c[:90]}")
    return errors


# ===================================================================== voorbeeld
def preview_color(s, y):
    import preview as pv
    c = pv.color(s) or (200, 200, 200)
    f = 0.8 + 0.2 * max(0.0, min(1.0, (y + 10) / 90))
    return tuple(min(255, int(v * f)) for v in c)


def render_regions(isl, planner, keep, pdir):
    import preview as pv

    class W:
        pass
    for name, (x, z) in (("resort", isl.sites["resort"]), ("village", isl.sites["village"]),
                         ("town", isl.sites["town"]), ("plantation", isl.sites["plantation"]),
                         ("temple", isl.sites["temple"]), ("lighthouse", isl.sites["lighthouse"]),
                         ("fort", isl.sites["fort"]), ("treehouse", isl.sites["treehouse"])):
        r = 40
        w = W()
        w.blk = {}
        for cx in range((x - r - X0) // 16, (x + r - X0) // 16 + 1):
            for cz in range((z - r - X0) // 16, (z + r - X0) // 16 + 1):
                for (bx, by, bz), s in keep.get((cx, cz), {}).items():
                    if abs(bx - x) <= r and abs(bz - z) <= r:
                        w.blk[(bx - x, by, bz - z)] = s
        # zee-water erbij voor de render
        for bx in range(x - r, x + r + 1):
            for bz in range(z - r, z + r + 1):
                if isl.inb(bx, bz) and isl.H[bx - X0, bz - X0] < SEA and (bx - x, SEA, bz - z) not in w.blk:
                    w.blk[(bx - x, SEA, bz - z)] = "minecraft:water"
        w.S = 2 * r + 2
        pv.render(w, None, pdir / f"island_{name}.png", 6)
