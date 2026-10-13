"""Gebouwen en nederzettingen op het eiland."""
import heapq
import math

import numpy as np

import structures as old
from structures import (CARPETS, DRINKS, FISH_TRADES, FOOD_TRADES, UMBRELLA_COLORS, glow_fringe, hip_roof, item_display,
                        sign_text, surfboard, text_display, tiki_torch, totem, trade, villager)
from world import st

from .buffer import RotBuf, Shim
from .terrain import (BEACH, CANYON, MEADOW, MOTU, PLANTATION, RAINFOREST, SEA, TOWN, VILLAGE, X0, S)

PASTELS = ["pink_concrete", "yellow_concrete", "light_blue_concrete", "lime_concrete", "orange_terracotta",
           "white_concrete", "cyan_terracotta", "magenta_terracotta", "light_blue_terracotta", "yellow_terracotta"]


class Plan:
    """Een object dat later in een buffer gebouwd wordt."""

    def __init__(self, name, bbox, fn, mode="force"):
        self.name, self.bbox, self.fn, self.mode = name, bbox, fn, mode


# ============================================================ kleine onderdelen
def tiki_statue(b, x, g, z, facing="west", rng=None):
    """Groot tiki-beeld, 3 breed en 6 hoog, gezicht naar 'facing'."""
    dx, dz = {"west": (-1, 0), "east": (1, 0), "north": (0, -1), "south": (0, 1)}[facing]
    px, pz = -dz, dx  # zijwaarts
    wood = st("stripped_jungle_wood", axis="y")
    for y in range(1, 7):
        for s in (-1, 0, 1):
            b.set(x + px * s, g + y, z + pz * s, wood)
    fx, fz = x + dx, z + dz
    b.set(fx + px * -1, g + 4, fz + pz * -1, "black_terracotta")
    b.set(fx + px * 1, g + 4, fz + pz * 1, "black_terracotta")
    b.set(fx, g + 3, fz, st("jungle_trapdoor", facing=facing, half="top", open="false"))
    for s in (-1, 0, 1):
        b.set(fx + px * s, g + 2, fz + pz * s, "red_terracotta" if s == 0 else wood)
        b.set(fx + px * s, g + 5, fz + pz * s, st("jungle_slab", type="bottom"))
    for s in (-2, 2):
        b.set(x + px * s, g + 6, z + pz * s, st("bamboo_fence"))
    b.set(x, g + 7, z, st("bamboo_fence"))
    b.set(x, g + 8, z, "torch")


def lamp(b, x, g, z, h=3, post="dark_oak_fence"):
    for y in range(1, h + 1):
        b.set(x, g + y, z, post)
    b.set(x, g + h + 1, z, "lantern")


def gable_roof(b, x0, x1, z0, z1, y, stair, fill, along="x", ridge=None):
    """Zadeldak; 'along' is de richting van de nok."""
    if along == "x":
        k = 0
        while z0 + k <= z1 - k:
            for x in range(x0, x1 + 1):
                if z0 + k == z1 - k:
                    b.set(x, y + k, z0 + k, ridge or fill)
                else:
                    b.set(x, y + k, z0 + k, st(stair, facing="south", half="bottom"))
                    b.set(x, y + k, z1 - k, st(stair, facing="north", half="bottom"))
            k += 1
    else:
        k = 0
        while x0 + k <= x1 - k:
            for z in range(z0, z1 + 1):
                if x0 + k == x1 - k:
                    b.set(x0 + k, y + k, z, ridge or fill)
                else:
                    b.set(x0 + k, y + k, z, st(stair, facing="east", half="bottom"))
                    b.set(x1 - k, y + k, z, st(stair, facing="west", half="bottom"))
            k += 1


def chest_late(b, x, y, z, facing, table, waterlogged=False):
    props = {"facing": facing}
    if waterlogged:
        props["waterlogged"] = "true"
    b.setblock_late(x, y, z, st("chest", **props), f'{{LootTable:"minecraft:chests/{table}"}}')


def canoe(b, x, g, z, rng, along="x"):
    """Polynesische uitleggerkano."""
    L = 7
    for i in range(L):
        a, c = (x + i, z) if along == "x" else (x, z + i)
        end = i in (0, L - 1)
        b.set(a, g + 1, c, st("jungle_slab", type="bottom") if end else st("stripped_jungle_log", axis=along))
    for i in range(1, L - 1):
        a, c = (x + i, z + 3) if along == "x" else (x + 3, z + i)
        b.set(a, g + 1, c, st("stripped_bamboo_block", axis=along))
    for i in (2, 4):
        for s in (1, 2):
            a, c = (x + i, z + s) if along == "x" else (x + s, z + i)
            b.set(a, g + 2, c, st("bamboo_mosaic_slab", type="bottom"))
        a, c = (x + i, z) if along == "x" else (x, z + i)
        b.set(a, g + 2, c, st("bamboo_mosaic_slab", type="bottom"))


def fale(b, cx, g, cz, w, d, rng, big=False):
    """Polynesische fale: stenen platform, palen, open zijkanten, hoog rieten dak."""
    x0, x1, z0, z1 = cx - w // 2, cx + w // 2, cz - d // 2, cz + d // 2
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            edge = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
            b.set(x, g, z, rng.choice(["cobblestone", "mossy_cobblestone", "stone"]) if edge else "packed_mud")
            b.set(x, g + 1, z, st("cobblestone_slab", type="bottom") if edge else rng.choice(
                ["brown_carpet", "yellow_carpet", "white_carpet", "orange_carpet"] if big else ["air"] * 3 + ["brown_carpet"]))
            if b.get(x, g + 1, z) == "minecraft:air":
                b.clear(x, g + 1, z)
    posts = []
    for x in range(x0, x1 + 1, 2):
        posts += [(x, z0), (x, z1)]
    for z in range(z0, z1 + 1, 2):
        posts += [(x0, z), (x1, z)]
    ph = 4 if big else 3
    for (x, z) in set(posts):
        for y in range(1, ph + 1):
            b.set(x, g + y, z, st("stripped_jungle_log", axis="y"))
    hip_roof(b, x0 - 1, x1 + 1, z0 - 1, z1 + 1, g + ph + 1, stair="bamboo_mosaic_stairs", fill="hay_block")
    glow_fringe(b, x0 - 1, x1 + 1, z0 - 1, z1 + 1, g + ph, rng) if big else None
    b.set(cx, g + ph, cz, st("lantern", hanging="true"))
    if big:
        b.set(cx, g + 1, cz, st("water_cauldron", level=3))
        for x, z in ((x0 + 1, z0 + 1), (x1 - 1, z1 - 1)):
            b.set(x, g + 1, z, st("barrel", facing="up"))
        for x, z in ((x0, cz), (x1, cz)):
            for y in range(1, ph + 1):
                b.set(x, g + y, z, st("stripped_jungle_log", axis="y"))
            b.set(x, g + ph - 1, z, st("carved_pumpkin", facing="west" if x == x0 else "east"))


# ============================================================ planner
class IslandPlanner:
    def __init__(self, isl, rng):
        self.isl, self.rng = isl, rng
        self.plans = []
        self.tp = None
        self.road_targets = []

    def add(self, name, x1, z1, x2, z2, fn, mode="force"):
        self.plans.append(Plan(name, (min(x1, x2), min(z1, z2), max(x1, x2), max(z1, z2)), fn, mode))

    def flatten(self, x1, z1, x2, z2, g, zone=None, margin=None):
        """Maak een rechthoek vlak op hoogte g, met een zachte overgang (margin) naar het terrein eromheen."""
        isl = self.isl
        a, b = sorted((x1, x2))
        c, d = sorted((z1, z2))
        if margin is None:
            margin = 3 if max(b - a, d - c) < 12 else 14 if max(b - a, d - c) < 40 else 22
        A, B = max(0, a - margin - X0), min(S, b + margin - X0 + 1)
        C, D = max(0, c - margin - X0), min(S, d + margin - X0 + 1)
        X, Z = isl.X[A:B, C:D], isl.Z[A:B, C:D]
        dx = np.maximum(np.maximum(a - X, X - b), 0)
        dz = np.maximum(np.maximum(c - Z, Z - d), 0)
        dist = np.hypot(dx, dz)
        t = np.clip(1 - dist / max(1, margin), 0, 1)
        t = t * t * (3 - 2 * t)
        core = dist == 0
        land = isl.dc[A:B, C:D] > 0
        old = isl.H[A:B, C:D].astype(float)
        new = np.where(core, g, np.round(old * (1 - t) + g * t))
        # zee blijft zee: alleen land aanpassen (behalve in de kern)
        new = np.where(land | core, new, old)
        isl.H[A:B, C:D] = new.astype(isl.H.dtype)
        isl.liq_top[A:B, C:D][core] = -999
        isl.river_wet[A:B, C:D][core] = False
        if zone is not None:
            isl.zone[A:B, C:D][core] = zone

    def plan_all(self):
        self.resort()
        self.village()
        self.town()
        self.plantation()
        self.ranch()
        self.temple()
        self.lighthouse()
        self.fort()
        self.treehouse()
        self.canyon_bridge()
        self.shipwreck()
        self.motus()
        self.volcano()
        self.lookouts()
        self.roads()

    # -------------------------------------------------------------- resort
    def shore_south(self, x):
        isl = self.isl
        for z in range(X0 + S - 1, X0, -1):
            if isl.dc[x - X0, z - X0] > 0:
                return z
        return 0

    def resort(self):
        isl, rng = self.isl, self.rng
        rx, rz = isl.sites["resort"]
        sz = self.shore_south(rx)
        ox, oz = rx, sz - 9
        self.flatten(ox - 14, oz - 18, ox + 14, oz + 7, -1, BEACH)
        isl.reserve(ox - 14, oz - 18, ox + 14, oz + 7)

        def bar(b):
            rb = RotBuf(b, ox, oz, 1)
            old.Planner.build_big_bar(Shim(rb), 0, 0)
        self.add("tiki_bar", ox - 14, oz - 18, ox + 14, oz + 8, bar)
        # bar-coordinaat (-8, 0) draait (k=1) naar (0, 8): voor de bar, kijkend naar het noorden
        self.tp = (ox + 0.5, 0, oz + 8.5, 180)
        self.road_targets.append(("resort", ox, oz - 20))
        # strand: parasols, strandwacht, volleybal, zandkastelen, vuurplaats
        spots = []
        for x in list(range(rx - 70, rx - 18, 9)) + list(range(rx + 18, rx + 40, 9)):
            if not isl.inb(x, 0):
                continue
            zs = self.shore_south(x)
            z = zs - rng.randint(3, 5)
            if isl.zone_at(x, z) in (BEACH,) and not isl.is_reserved(x - 2, z - 2, x + 2, z + 2):
                spots.append((x, z))
        for x, z in spots:
            g = isl.h(x, z)
            self.flatten(x - 2, z - 2, x + 2, z + 2, g)
            isl.reserve(x - 2, z - 2, x + 2, z + 2)
            col = rng.choice(UMBRELLA_COLORS)
            self.add("umbrella", x - 3, z - 3, x + 3, z + 3,
                     lambda b, x=x, z=z, g=g, col=col: old.Planner.build_umbrella(Shim(RotBuf(b, x, z, 1)), 0, 0, g, col))
        lx = rx + 48
        lz = self.shore_south(lx) - 4
        if isl.zone_at(lx, lz) == BEACH:
            g = isl.h(lx, lz)
            self.flatten(lx - 3, lz - 4, lx + 3, lz + 2, g)
            isl.reserve(lx - 3, lz - 5, lx + 4, lz + 2)
            self.add("lifeguard", lx - 5, lz - 6, lx + 5, lz + 4,
                     lambda b: old.Planner.build_lifeguard(Shim(RotBuf(b, lx, lz, 1)), 0, 0, g))
        vx = rx - 82
        vz = self.shore_south(vx) - 8
        if isl.inb(vx, vz) and isl.zone_at(vx, vz) == BEACH and not isl.is_reserved(vx - 8, vz - 5, vx + 8, vz + 5):
            g = isl.h(vx, vz)
            self.flatten(vx - 8, vz - 5, vx + 8, vz + 5, g)
            isl.reserve(vx - 8, vz - 5, vx + 8, vz + 5)
            self.add("volleyball", vx - 9, vz - 6, vx + 9, vz + 6,
                     lambda b: old.Planner.build_volleyball(Shim(RotBuf(b, vx, vz, 1)), 0, 0, g))
        for sx in (rx - 30, rx + 60):
            szz = self.shore_south(sx) - 2
            if isl.zone_at(sx, szz) == BEACH and not isl.is_reserved(sx - 3, szz - 3, sx + 3, szz + 3):
                g = isl.h(sx, szz)
                self.flatten(sx - 2, szz - 2, sx + 2, szz + 2, g)
                isl.reserve(sx - 3, szz - 3, sx + 3, szz + 3)
                self.add("sandcastle", sx - 3, szz - 3, sx + 3, szz + 3,
                         lambda b, sx=sx, szz=szz, g=g: old.Planner.build_sandcastle(Shim(b), sx, szz, g))
        fx = rx + 28
        fz = self.shore_south(fx) - 12
        if not isl.is_reserved(fx - 6, fz - 6, fx + 6, fz + 6):
            g = max(isl.h(fx, fz), SEA + 1)
            self.flatten(fx - 5, fz - 5, fx + 5, fz + 5, g, BEACH)
            isl.reserve(fx - 6, fz - 6, fx + 6, fz + 6)
            self.add("firepit", fx - 6, fz - 6, fx + 6, fz + 6,
                     lambda b: old.Planner.build_firepit(Shim(RotBuf(b, fx, fz, 1)), 0, 0, g))
        self.bungalows(rx + 22, sz)

    def bungalows(self, wx, sz):
        """Boardwalk de lagune in met overwater bungalows (Tahiti)."""
        isl = self.isl
        deck = SEA + 1
        z_end = sz + 26
        branches = [(sz + 11, -1), (sz + 11, 1), (sz + 23, -1), (sz + 23, 1)]
        isl.reserve(wx - 22, sz - 4, wx + 22, z_end + 6)
        centers = [(wx + side * 15, bz) for bz, side in branches]

        def build(b):
            def posts(x, z):
                for y in range(isl.h(x, z) + 1, deck):
                    b.set(x, y, z, st("stripped_jungle_log", axis="y"))
            for z in range(sz - 3, z_end + 1):
                for x in range(wx - 1, wx + 2):
                    b.set(x, deck, z, "bamboo_planks" if x == wx else st("stripped_bamboo_block", axis="z"))
                if (z - sz) % 4 == 0 and z > sz:
                    posts(wx - 1, z)
                    posts(wx + 1, z)
                    if (z - sz) % 8 == 0:
                        lamp(b, wx + 1, deck, z, 1, "bamboo_fence")
            for bz, side in branches:
                for i in range(2, 12):
                    x = wx + side * i
                    for z in (bz - 1, bz, bz + 1):
                        b.set(x, deck, z, "bamboo_planks" if z == bz else st("stripped_bamboo_block", axis="x"))
                    if i % 4 == 0:
                        posts(x, bz - 1)
                        posts(x, bz + 1)
            for cx, cz in centers:
                bungalow(b, cx, deck, cz, self.rng, isl)
        self.add("bungalows", wx - 22, sz - 4, wx + 22, z_end + 6, build)


    # ------------------------------------------------------------- dorp
    def village(self):
        isl, rng = self.isl, self.rng
        vx, vz = isl.sites["village"]
        g = isl.site_level["village"]
        self.flatten(vx - 30, vz - 30, vx + 30, vz + 30, g, VILLAGE)
        # zeekant terug naar strand
        for x in range(vx - 30, vx + 31):
            for z in range(vz - 30, vz + 31):
                if isl.inb(x, z) and isl.dc[x - X0, z - X0] < 9:
                    isl.zone[x - X0, z - X0] = BEACH
                    isl.H[x - X0, z - X0] = SEA + (1 if isl.dc[x - X0, z - X0] > 3 else 0)
                if isl.inb(x, z) and isl.dc[x - X0, z - X0] <= 0:
                    isl.H[x - X0, z - X0] = min(isl.H[x - X0, z - X0], SEA - 1)
        isl.reserve(vx - 30, vz - 30, vx + 30, vz + 30)
        cx = vx + 6
        self.road_targets.append(("village", vx + 32, vz))

        def build(b):
            # plein met vuurplaats
            old.Planner.build_firepit(Shim(b), cx, vz, g)
            # grote fale van het opperhoofd
            fale(b, cx + 14, g, vz - 2, 11, 17, rng, big=True)
            villager(b, cx + 14.5, g + 1, vz - 1.5, "Opperhoofd Kahiko", "gold", 90, "nitwit", "jungle")
            villager(b, cx + 12.5, g + 1, vz + 3.5, "Tante Leilani", "light_purple", 90, "cleric", "jungle",
                     [trade("emerald", DRINKS[5]), trade("emerald", "cooked_porkchop", 1, 4), trade("emerald", "baked_potato", 1, 6)])
            # kleine fales in een kring
            for i in range(8):
                ang = math.pi * (0.25 + 1.5 * i / 7)
                fx = cx + int(round(math.cos(ang) * 20))
                fz = vz + int(round(math.sin(ang) * 22))
                if isl.dc[fx - X0, fz - X0] < 12:
                    continue
                fale(b, fx, g, fz, 7, 9, rng)
                if rng.random() < 0.6:
                    villager(b, fx + 0.5, g + 1, fz + 0.5, rng.choice(["Keanu", "Malia", "Kai", "Noelani", "Makana", "Ikaika", "Lani"]),
                             "green", rng.randint(0, 359), "nitwit", "jungle")
            # marae met tiki's
            mx, mz = cx + 4, vz + 20
            for x in range(mx - 6, mx + 7):
                for z in range(mz - 4, mz + 5):
                    b.set(x, g + 1, z, rng.choice(["cobblestone", "mossy_cobblestone", "stone_bricks", "mossy_stone_bricks"]))
                    if abs(x - mx) <= 4 and abs(z - mz) <= 2:
                        b.set(x, g + 2, z, rng.choice(["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks"]))
            for x in range(mx - 4, mx + 5, 2):
                b.set(x, g + 3, mz + 2, "andesite_wall")
                b.set(x, g + 4, mz + 2, "andesite_wall")
            for x in (mx - 3, mx, mx + 3):
                tiki_statue(b, x, g + 2, mz + 1, "north", rng)
            # kano's op het strand
            for i, dz in enumerate((-18, -10, 12, 18)):
                z = vz + dz
                sx = vx - 30
                for x in range(vx - 30, vx + 10):
                    if isl.inb(x, z) and isl.dc[x - X0, z - X0] > 1:
                        sx = x
                        break
                canoe(b, sx - 2, isl.h(sx, z), z, rng, "x")
            # taro velden (lo'i) met grote druppelbladeren
            tx, tz = cx + 6, vz - 24
            for k in range(3):
                x0 = tx + k * 8
                for x in range(x0, x0 + 7):
                    for z in range(tz, tz + 6):
                        edge = x in (x0, x0 + 6) or z in (tz, tz + 5)
                        if edge:
                            b.set(x, g, z, "packed_mud")
                        else:
                            b.set(x, g - 1, z, "clay")
                            b.set(x, g, z, st("big_dripleaf", facing=rng.choice(["north", "south", "east", "west"]),
                                              waterlogged="true") if rng.random() < 0.55 else "water")
            # varkens in een kraal en kippen
            px, pz = cx + 24, vz + 14
            for x in range(px - 3, px + 4):
                for z in range(pz - 3, pz + 4):
                    if x in (px - 3, px + 3) or z in (pz - 3, pz + 3):
                        b.set(x, g + 1, z, "bamboo_fence")
            for _ in range(3):
                b.summon("pig", px + rng.uniform(-1.5, 1.5) + 0.5, g + 1, pz + rng.uniform(-1.5, 1.5) + 0.5, "PersistenceRequired:1b")
            for _ in range(6):
                b.summon("chicken", cx + rng.uniform(-12, 12), g + 1, vz + rng.uniform(-12, 12), "PersistenceRequired:1b")
            # tiki's en fakkels bij de ingang (oostkant)
            for dz in (-4, 4):
                totem(b, vx + 29, g, vz + dz, "east")
            for dz in (-10, 10):
                tiki_torch(b, vx + 28, g, vz + dz)
            text_display(b, vx + 31.5, g + 8.5, vz + 0.5, "Kauhale o Moana", "gold", 2.2)
            from . import flora
            for i in range(10):
                ang = rng.uniform(0, math.tau)
                rr = rng.uniform(9, 13)
                fx, fz = cx + int(math.cos(ang) * rr), vz + int(math.sin(ang) * rr)
                if b.is_air(fx, g + 1, fz) and b.is_air(fx, g + 3, fz):
                    (flora.palm if i % 3 else lambda bb, x, z, r: flora.flowering_tree(bb, x, z, r, "plumeria"))(b, fx, fz, rng)
            for i in range(4):
                villager(b, cx + 2.5 + i, g + 1, vz + 4.5, "Hula Danser", rng.choice(["light_purple", "aqua", "yellow"]),
                         180, "nitwit", "savanna")
        self.add("village", vx - 30, vz - 30, vx + 31, vz + 31, build)

    # ------------------------------------------------------------- stad
    def town(self):
        isl, rng = self.isl, self.rng
        tx, tz = isl.sites["town"]
        g = isl.site_level["town"]
        px, pz = tx - 24, tz  # plein
        W0, W1, Z0, Z1 = px - 46, tx + 6, pz - 34, pz + 34
        self.flatten(W0, Z0, W1, Z1, g, TOWN)
        isl.reserve(W0, Z0, W1, Z1)
        self.road_targets.append(("town", W0 - 2, pz))
        # kavels langs drie oost-west straten (z = pz-14, pz, pz+14)
        lots = []
        for sz in (pz - 14, pz, pz + 14):
            for x0 in range(W0 + 2, W1 - 7, 9):
                for side, z0, face in ((-1, sz - 10, "south"), (1, sz + 3, "north")):
                    box = (x0, z0, x0 + 6, z0 + 6)
                    if box[2] >= px - 12 and box[0] <= px + 12 and box[3] >= pz - 12 and box[1] <= pz + 12:
                        continue  # plein
                    if box[2] >= px - 11 and box[0] <= px + 11 and box[1] <= pz - 13 and box[3] >= pz - 36:
                        continue  # kerk
                    if z0 < Z0 or z0 + 6 > Z1:
                        continue
                    lots.append((x0, z0, face))

        def build(b):
            from . import flora
            # plein
            for x in range(px - 11, px + 12):
                for z in range(pz - 11, pz + 12):
                    edge = max(abs(x - px), abs(z - pz)) == 11
                    b.set(x, g, z, "stone_bricks" if edge else ("polished_andesite" if (x + z) % 2 else "smooth_stone"))
            for x in range(px - 3, px + 4):
                for z in range(pz - 3, pz + 4):
                    d = max(abs(x - px), abs(z - pz))
                    if d == 3:
                        b.set(x, g + 1, z, st("stone_brick_slab", type="top") if (x + z) % 2 else "stone_bricks")
                    else:
                        b.set(x, g, z, "prismarine_bricks")
                        b.set(x, g + 1, z, "water")
            for y in range(1, 4):
                b.set(px, g + y, pz, "chiseled_stone_bricks")
            b.cmds_end.append(f"setblock ~{px} ~{g + 4} ~{pz} minecraft:water")
            # straten
            def street(x1, z1, x2, z2):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    for z in range(min(z1, z2), max(z1, z2) + 1):
                        if max(abs(x - px), abs(z - pz)) <= 11:
                            continue
                        b.set(x, g, z, rng.choice(["cobblestone", "andesite", "stone", "cobblestone", "gravel", "tuff"]))
            for sz in (pz - 14, pz, pz + 14):
                street(W0, sz - 1, W1 + 4, sz + 1)
                for x in range(W0, W1 + 1):
                    for z in (sz - 2, sz + 2):
                        if max(abs(x - px), abs(z - pz)) > 11:
                            b.set(x, g, z, "smooth_stone")
            for sx in (px, W0 + 1):
                street(sx - 1, Z0, sx + 1, Z1)
            # kerk aan de noordkant van het plein, voorkant naar het plein
            church(RotBuf(b, px, pz - 24, 3), 0, g, 0, rng)
            for x0, z0, face in lots:
                house(b, x0, g, z0, face, rng)
            for i, (mx, mz) in enumerate(((px - 7, pz - 7), (px + 7, pz - 7), (px - 7, pz + 7), (px + 7, pz + 7))):
                market_stall(b, mx, g, mz, rng, i)
            for x in range(W0 + 4, W1, 8):
                for sz in (pz - 14, pz, pz + 14):
                    if max(abs(x - px), abs(sz - pz)) > 13:
                        lamp(b, x, g, sz - 2, 3)
            for x in range(px + 14, W1, 7):
                for z in (pz - 3, pz + 3):
                    b.set(x, g, z, "grass_block")
                    flora.palm(b, x, z, rng, lean=(0, 1 if z > pz else -1), height=rng.randint(8, 11))
            for x, z in ((px - 10, pz - 10), (px + 10, pz - 10), (px - 10, pz + 10), (px + 10, pz + 10)):
                flora.flowering_tree(b, x, z, rng, "plumeria")
            for i in range(14):
                villager(b, px + rng.uniform(-9, 9), g + 1, pz + rng.uniform(-9, 9),
                         rng.choice(["Don Ernesto", "Maria", "Carlos", "Lucía", "Pedro", "Rosa", "Alejandro", "Isabel",
                                     "Camila", "Diego"]),
                         rng.choice(["yellow", "aqua", "gold", "light_purple"]), rng.randint(0, 359),
                         rng.choice(["nitwit", "farmer", "librarian", "cartographer"]), "savanna")
            villager(b, px + 7.5, g + 1, pz - 5.5, "Don Ramón (tabaco)", "gold", 0, "cartographer", "savanna",
                     [trade("emerald", "map", 2, 1), trade("emerald", "cocoa_beans", 1, 8), trade("gold_ingot", "emerald", 2, 3)])
            villager(b, px - 6.5, g + 1, pz + 5.5, "Señora Rosa (frutas)", "light_purple", 180, "farmer", "savanna",
                     [trade("emerald", "melon_slice", 1, 8), trade("emerald", "sweet_berries", 1, 10), trade("emerald", "golden_apple", 8, 1)])
            villager(b, px + 6.5, g + 1, pz + 5.5, "Cantina El Sol", "red", 180, "butcher", "savanna",
                     [trade("emerald", DRINKS[2]), trade("emerald", DRINKS[0]), trade("emerald", "cooked_porkchop", 1, 4)])
            for _ in range(6):
                b.summon("cat", px + rng.uniform(-9, 9), g + 1, pz + rng.uniform(-9, 9),
                         f'variant:"minecraft:{rng.choice(["tabby", "calico", "black", "red", "siamese", "white"])}",PersistenceRequired:1b')
            text_display(b, px + 0.5, g + 7, pz + 0.5, "Santa Lucía", "gold", 2.4)
            # haven
            sx = W1
            for x in range(px, px + 80):
                if isl.inb(x, pz) and isl.dc[x - X0, pz - X0] <= 0:
                    sx = x
                    break
            old.Planner.build_dock(Shim(RotBuf(b, sx - 1, pz, 2)), -18, 0, 0)
        self.add("town", W0 - 4, Z0 - 4, W1 + 34, Z1 + 4, build)

    # ------------------------------------------------------------ plantage
    def plantation(self):
        isl, rng = self.isl, self.rng
        cx, cz = isl.sites["plantation"]
        g = isl.site_level["plantation"]
        self.flatten(cx - 40, cz - 32, cx + 40, cz + 32, g, PLANTATION)
        isl.reserve(cx - 40, cz - 32, cx + 40, cz + 32)
        self.road_targets.append(("plantation", cx, cz - 34))

        def build(b):
            plots = [(cx - 38, cz - 30, "cane"), (cx - 14, cz - 30, "cane"), (cx - 38, cz + 4, "coffee"),
                     (cx - 14, cz + 4, "pine"), (cx + 12, cz + 8, "cane")]
            for x0, z0, kind in plots:
                field(b, x0, g, z0, 20, 22, kind, rng)
            hacienda(b, cx + 22, g, cz - 18, rng)
            from . import flora
            for x in range(cx + 10, cx + 36, 6):
                flora.palm(b, x, cz - 28, rng, lean=(0, -1), height=9)
            for x in (cx + 12, cx + 32):
                flora.flowering_tree(b, x, cz - 2, rng, "monkeypod")
            sugar_mill(b, cx + 30, g, cz + 12, rng)
            villager(b, cx + 22.5, g + 1, cz - 9.5, "Don Alonso (hacienda)", "gold", 180, "farmer", "savanna",
                     [trade("emerald", "sugar", 1, 12), trade("emerald", "sugar_cane", 1, 16), trade("emerald", "cookie", 1, 8)])
            for i in range(6):
                villager(b, cx - 30 + i * 8.5, g + 1, cz - 8.5, "Plantagewerker", "green", rng.randint(0, 359), "farmer", "savanna")
            text_display(b, cx + 22.5, g + 12, cz - 17.5, "Hacienda La Dulce", "gold", 2.0)
        self.add("plantation", cx - 41, cz - 33, cx + 41, cz + 33, build)

    # --------------------------------------------------------------- ranch
    def ranch(self):
        isl, rng = self.isl, self.rng
        cx, cz = isl.sites["ranch"]
        g = isl.site_level["ranch"]
        self.flatten(cx - 22, cz - 16, cx + 22, cz + 16, g, MEADOW)
        isl.reserve(cx - 22, cz - 16, cx + 22, cz + 16)
        self.road_targets.append(("ranch", cx - 24, cz))

        def build(b):
            for x in range(cx - 20, cx + 8):
                for z in range(cz - 12, cz + 13):
                    if x in (cx - 20, cx + 7) or z in (cz - 12, cz + 12):
                        if not (x == cx + 7 and abs(z - cz) <= 1):
                            b.set(x, g + 1, z, "oak_fence")
            b.set(cx + 7, g + 1, cz, st("oak_fence_gate", facing="east"))
            # schuur
            bx, bz = cx + 10, cz - 6
            for x in range(bx, bx + 10):
                for z in range(bz, bz + 12):
                    edge = x in (bx, bx + 9) or z in (bz, bz + 11)
                    b.set(x, g, z, "spruce_planks")
                    if edge:
                        for y in range(1, 6):
                            corner = x in (bx, bx + 9) and z in (bz, bz + 11)
                            b.set(x, g + y, z, st("stripped_spruce_log", axis="y") if corner else
                                  ("red_terracotta" if y < 5 else "white_terracotta"))
            for z in range(bz + 4, bz + 8):
                for y in range(1, 4):
                    b.clear(bx, g + y, z)
            gable_roof(b, bx - 1, bx + 10, bz - 1, bz + 12, g + 6, "dark_oak_stairs", "dark_oak_planks", along="z",
                       ridge="dark_oak_planks")
            for x in range(bx + 2, bx + 8, 2):
                b.set(x, g + 1, bz + 2, "hay_block")
                b.set(x, g + 2, bz + 2, "hay_block")
            b.set(cx - 8, g + 1, cz, st("water_cauldron", level=3))
            b.set(cx - 7, g + 1, cz, st("water_cauldron", level=3))
            for _ in range(6):
                b.summon("horse", cx - 6 + rng.uniform(-10, 10), g + 1, cz + rng.uniform(-9, 9),
                         f"Variant:{rng.choice([0, 1, 2, 3, 4, 5, 6, 256, 513, 770, 1024])},PersistenceRequired:1b")
            for _ in range(4):
                b.summon("cow", cx - 6 + rng.uniform(-10, 10), g + 1, cz + rng.uniform(-9, 9), "PersistenceRequired:1b")
            villager(b, cx + 9.5, g + 1, cz + 0.5, "Paniolo Makoa", "gold", 90, "leatherworker", "plains",
                     [trade("emerald", "saddle", 3, 1), trade("emerald", "lead", 1, 2), trade("emerald", "leather_horse_armor", 2, 1)])
            text_display(b, cx + 7.5, g + 4, cz + 0.5, "Paniolo Ranch", "gold", 1.6)
        self.add("ranch", cx - 23, cz - 17, cx + 23, cz + 17, build)

    # -------------------------------------------------------------- tempel
    def temple(self):
        isl, rng = self.isl, self.rng
        cx, cz = isl.sites["temple"]
        g = isl.site_level["temple"]
        self.flatten(cx - 14, cz - 14, cx + 14, cz + 14, g, RAINFOREST)
        isl.reserve(cx - 21, cz - 21, cx + 21, cz + 21)
        self.road_targets.append(("temple", cx, cz + 16))

        def build(b):
            mats = ["mossy_stone_bricks", "mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks", "mossy_cobblestone"]
            for t in range(5):
                r = 9 - 2 * t
                for x in range(cx - r, cx + r + 1):
                    for z in range(cz - r, cz + r + 1):
                        for y in (1, 2):
                            if rng.random() < 0.96:
                                b.set(x, g + 2 * t + y, z, rng.choice(mats))
                        if max(abs(x - cx), abs(z - cz)) == r and rng.random() < 0.25:
                            b.setk(x, g + 2 * t + 3, z, rng.choice(["moss_carpet", st("jungle_leaves", persistent="true")]))
            for y in range(1, 11):
                z = cz + 9 - (y - 1) // 2
                for x in (cx - 1, cx, cx + 1):
                    b.set(x, g + y, z + 1, st("stone_brick_stairs", facing="north", half="bottom"))
            tiki_statue(b, cx, g + 10, cz - 1, "south", rng)
            for x in (cx - 1, cx + 1):
                b.set(x, g + 11, cz + 1, st("campfire", lit="true"))
            for _ in range(40):
                x = cx + rng.randint(-9, 9)
                z = cz + rng.randint(-9, 9)
                face, (ox, oz) = rng.choice([("east", (-1, 0)), ("west", (1, 0)), ("south", (0, -1)), ("north", (0, 1))])
                top = g + 10
                for y in range(top, g, -1):
                    if b.get(x, y, z) and "stone" in b.get(x, y, z) and b.is_air(x + ox, y, z + oz):
                        for i in range(rng.randint(2, 6)):
                            if b.is_air(x + ox, y - i, z + oz):
                                b.set(x + ox, y - i, z + oz, st("vine", **{face: "true"}))
                        break
            for k in range(4):
                ang = rng.uniform(0, math.tau)
                px, pz = cx + int(13 * math.cos(ang)), cz + int(13 * math.sin(ang))
                for y in range(1, rng.randint(2, 5)):
                    b.set(px, isl.h(px, pz) + y, pz, rng.choice(["mossy_stone_bricks", "cracked_stone_bricks"]))
            chest_late(b, cx, g + 11, cz - 3, "south", "jungle_temple")
            text_display(b, cx + 0.5, g + 19, cz + 0.5, "Heiau o Lono", "green", 1.8)
        self.add("temple", cx - 15, cz - 15, cx + 15, cz + 15, build)

    # ---------------------------------------------------------- vuurtoren
    def lighthouse(self):
        isl, rng = self.isl, self.rng
        cx, cz = isl.sites["lighthouse"]
        g = isl.h(cx, cz)
        self.flatten(cx - 8, cz - 6, cx + 8, cz + 8, g)
        isl.reserve(cx - 8, cz - 6, cx + 8, cz + 8)
        self.road_targets.append(("lighthouse", cx, cz + 10))

        def build(b):
            H = 26
            for y in range(1, H + 1):
                band = "red_concrete" if (y // 4) % 2 else "white_concrete"
                for x in range(cx - 4, cx + 5):
                    for z in range(cz - 4, cz + 5):
                        d = math.hypot(x - cx, z - cz)
                        if 2.6 <= d < 3.8:
                            b.set(x, g + y, z, band)
                        elif d < 2.6:
                            b.clear(x, g + y, z)
                b.set(cx, g + y, cz + 1, st("ladder", facing="south"))
                b.set(cx, g + y, cz, "white_concrete")
            for y in (1, 2):
                b.clear(cx, g + y, cz + 3)
            b.set(cx, g + 1, cz + 3, st("oak_door", facing="south", half="lower", hinge="left"))
            b.set(cx, g + 2, cz + 3, st("oak_door", facing="south", half="upper", hinge="left"))
            for x in range(cx - 5, cx + 6):
                for z in range(cz - 5, cz + 6):
                    d = math.hypot(x - cx, z - cz)
                    if d < 5:
                        b.set(x, g + H + 1, z, "smooth_stone")
                    if 4 <= d < 5:
                        b.set(x, g + H + 2, z, "iron_bars")
            for x in range(cx - 2, cx + 3):
                for z in range(cz - 2, cz + 3):
                    edge = abs(x - cx) == 2 or abs(z - cz) == 2
                    for y in (2, 3, 4):
                        b.set(x, g + H + y, z, "glass" if edge else ("sea_lantern" if y < 4 else "glowstone"))
                    b.set(x, g + H + 5, z, "red_concrete")
            b.set(cx, g + H + 6, cz, "red_concrete")
            b.set(cx, g + H + 7, cz, "lightning_rod")
            # huisje van de vuurtorenwachter
            hx, hz = cx + 3, cz + 5
            for x in range(hx, hx + 6):
                for z in range(hz, hz + 5):
                    edge = x in (hx, hx + 5) or z in (hz, hz + 4)
                    b.set(x, g, z, "spruce_planks")
                    if edge:
                        for y in range(1, 4):
                            b.set(x, g + y, z, "white_concrete" if y < 3 else "stone_bricks")
            b.clear(hx + 2, g + 1, hz + 4)
            b.clear(hx + 2, g + 2, hz + 4)
            b.set(hx + 4, g + 2, hz + 4, "glass_pane")
            gable_roof(b, hx - 1, hx + 6, hz - 1, hz + 5, g + 4, "red_nether_brick_stairs", "red_nether_bricks", along="x")
            villager(b, hx + 2.5, g + 1, hz + 6.5, "Vuurtorenwachter Ikaika", "aqua", 0, "cartographer", "plains")
            b.set(hx + 1, g + 1, hz + 2, st("red_bed", facing="east", part="foot"))
            b.set(hx + 2, g + 1, hz + 2, st("red_bed", facing="east", part="head"))
            b.set(hx + 4, g + 1, hz + 1, "barrel")
            b.set(hx + 4, g + 2, hz + 1, "lantern")
        self.add("lighthouse", cx - 9, cz - 7, cx + 10, cz + 12, build)

    # --------------------------------------------------------------- fort
    def fort(self):
        isl, rng = self.isl, self.rng
        cx, cz = isl.sites["fort"]
        g = max(isl.h(cx, cz), SEA + 2)
        R = 11
        self.flatten(cx - R - 3, cz - R - 3, cx + R + 3, cz + R + 3, g)
        isl.reserve(cx - R - 3, cz - R - 3, cx + R + 3, cz + R + 3)
        self.road_targets.append(("fort", cx - R - 5, cz))

        def build(b):
            mats = ["stone_bricks", "stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks", "cobblestone"]
            for x in range(cx - R, cx + R + 1):
                for z in range(cz - R, cz + R + 1):
                    b.set(x, g, z, rng.choice(["gravel", "cobblestone", "coarse_dirt", "stone"]))
                    wall = max(abs(x - cx), abs(z - cz)) >= R - 1
                    if wall:
                        top = 7 if rng.random() > 0.12 else rng.randint(2, 6)
                        for y in range(1, top + 1):
                            b.set(x, g + y, z, rng.choice(mats))
                        if max(abs(x - cx), abs(z - cz)) == R and (x + z) % 2 == 0 and top == 7:
                            b.set(x, g + 8, z, "stone_brick_wall")
            # torens op de hoeken
            for sx in (-1, 1):
                for sz in (-1, 1):
                    tx, tz = cx + sx * R, cz + sz * R
                    for x in range(tx - 3, tx + 4):
                        for z in range(tz - 3, tz + 4):
                            for y in range(1, 10):
                                b.set(x, g + y, z, rng.choice(mats))
                            if max(abs(x - tx), abs(z - tz)) == 3 and (x + z) % 2 == 0:
                                b.set(x, g + 10, z, "stone_brick_wall")
            # poort aan de westkant
            for z in range(cz - 1, cz + 2):
                for y in range(1, 5):
                    for x in (cx - R, cx - R + 1):
                        b.clear(x, g + y, z)
            b.set(cx - R, g + 5, cz, "chiseled_stone_bricks")
            # kanonnen op de oostmuur (naar zee)
            for z in range(cz - 6, cz + 7, 4):
                x = cx + R - 2
                b.set(x - 1, g + 8, z, st("stripped_dark_oak_log", axis="x"))
                b.set(x, g + 8, z, st("polished_basalt", axis="x"))
                b.set(x + 1, g + 8, z, st("polished_basalt", axis="x"))
            # loopbrug binnen langs de muur
            for x in range(cx - R + 2, cx + R - 1):
                for z in range(cz - R + 2, cz + R - 1):
                    if max(abs(x - cx), abs(z - cz)) == R - 2:
                        b.set(x, g + 7, z, st("spruce_slab", type="top"))
            b.set(cx, g + 1, cz, "spruce_fence")
            for y in range(2, 10):
                b.set(cx, g + y, cz, "spruce_fence")
            b.set(cx, g + 10, cz, st("red_banner", rotation=4))
            for x, z in ((cx - 5, cz - 5), (cx + 4, cz + 5), (cx - 6, cz + 6)):
                b.set(x, g + 1, z, st("barrel", facing="up"))
                b.set(x + 1, g + 1, z, st("barrel", facing="up"))
            chest_late(b, cx + 5, g + 1, cz - 6, "west", "village/village_weaponsmith")
            text_display(b, cx - R - 1.5, g + 9, cz + 0.5, "Castillo San Felipe", "gold", 1.8)
        self.add("fort", cx - R - 4, cz - R - 4, cx + R + 4, cz + R + 4, build)

    # ----------------------------------------------------------- boomhut
    def treehouse(self):
        isl, rng = self.isl, self.rng
        cx, cz = isl.sites["treehouse"]
        g = isl.h(cx, cz)
        self.flatten(cx - 3, cz - 3, cx + 3, cz + 3, g)
        isl.reserve(cx - 9, cz - 9, cx + 24, cz + 9)
        cx2 = cx + 16
        g2 = isl.h(cx2, cz)
        self.road_targets.append(("treehouse", cx, cz + 10))

        def build(b):
            from . import flora
            P = g + 13
            for x, gg in ((cx, g), (cx2, g2)):
                for y in range(gg + 1, P + 8):
                    for a in (0, 1):
                        for c in (0, 1):
                            b.set(x + a, y, cz + c, st("jungle_log", axis="y"))
                flora.blob(b, x + 0.5, P + 9, cz + 0.5, 6, 2.5, 6, flora.LEAF, rng)
            for x in range(cx - 4, cx + 6):
                for z in range(cz - 4, cz + 6):
                    if b.is_air(x, P, z):
                        b.set(x, P, z, "jungle_planks")
                    if (x in (cx - 4, cx + 5) or z in (cz - 4, cz + 5)) and not (x == cx + 5 and z in (cz, cz + 1)):
                        b.set(x, P + 1, z, "jungle_fence")
            for x in range(cx2 - 3, cx2 + 5):
                for z in range(cz - 3, cz + 5):
                    if b.is_air(x, P, z):
                        b.set(x, P, z, "jungle_planks")
                    if (x in (cx2 - 3, cx2 + 4) or z in (cz - 3, cz + 4)) and not (x == cx2 - 3 and z in (cz, cz + 1)):
                        b.set(x, P + 1, z, "jungle_fence")
            # touwbrug
            for x in range(cx + 6, cx2 - 3):
                sag = -1 if cx + 8 < x < cx2 - 5 else 0
                for z in (cz, cz + 1):
                    b.set(x, P + sag, z, st("spruce_slab", type="top"))
                for z in (cz - 1, cz + 2):
                    b.set(x, P + 1 + sag, z, "chain" if (x % 2) else "spruce_fence")
            # hutje
            hx, hz = cx - 3, cz - 3
            for x in range(hx, hx + 4):
                for z in range(hz, hz + 3):
                    for y in (1, 2):
                        if x in (hx, hx + 3) or z in (hz,):
                            b.set(x, P + y, z, "bamboo_planks")
            hip_roof(b, hx - 1, hx + 4, hz - 1, hz + 3, P + 3, fill="hay_block")
            b.set(hx + 1, P + 1, hz + 1, st("lime_bed", facing="east", part="foot"))
            b.set(hx + 2, P + 1, hz + 1, st("lime_bed", facing="east", part="head"))
            b.set(cx + 4, P + 1, cz + 4, "lantern")
            b.set(cx2 + 3, P + 1, cz + 3, "lantern")
            for y in range(g + 1, P + 1):
                b.set(cx - 1, y, cz, st("ladder", facing="west"))
            for x in (cx2 + 1, cx2 + 2):
                b.set(x, P + 1, cz - 2, "yellow_wool")
            villager(b, cx + 3.5, P + 1, cz + 3.5, "Boswachter Kekoa", "green", 45, "cartographer", "jungle")
            b.summon("parrot", cx2 + 1.5, P + 1, cz + 1.5, "Variant:2,PersistenceRequired:1b")
        self.add("treehouse", cx - 12, cz - 12, cx2 + 12, cz + 12, build)

    # ---------------------------------------------------------- kloofbrug
    def canyon_bridge(self):
        isl = self.isl
        rv = [r for r in isl.rivers if r["canyon"]]
        if not rv:
            return
        r = rv[0]
        best = None
        for i in range(30, len(r["pts"]) - 30, 5):
            x, z = r["pts"][i]
            nx, nz = r["pts"][i + 3]
            tx, tz = nx - x, nz - z
            ln = math.hypot(tx, tz) or 1
            ux, uz = -tz / ln, tx / ln
            ends = []
            for sgn in (-1, 1):
                for d in range(3, 14):
                    px, pz = int(round(x + ux * d * sgn)), int(round(z + uz * d * sgn))
                    if not isl.inb(px, pz):
                        break
                    if not isl.canyon[px - X0, pz - X0] and isl.H[px - X0, pz - X0] > r["L"][i] + 10:
                        ends.append((px, pz, d))
                        break
            if len(ends) == 2:
                (ax, az, _), (bx, bz, _) = ends
                ha, hb = isl.h(ax, az), isl.h(bx, bz)
                if abs(ha - hb) <= 3 and min(ha, hb) - r["L"][i] > 14:
                    best = (ax, az, bx, bz, max(ha, hb))
                    break
        if not best:
            return
        ax, az, bx, bz, hh = best
        isl.reserve(min(ax, bx) - 2, min(az, bz) - 2, max(ax, bx) + 2, max(az, bz) + 2)
        self.road_targets.append(("canyon_bridge", ax, az))

        def build(b):
            n = int(max(abs(bx - ax), abs(bz - az))) + 1
            for i in range(n + 1):
                t = i / n
                x = round(ax + (bx - ax) * t)
                z = round(az + (bz - az) * t)
                sag = -round(2 * math.sin(math.pi * t))
                y = hh + sag
                horiz = abs(bx - ax) >= abs(bz - az)
                for s in (-1, 0, 1):
                    px, pz = (x, z + s) if horiz else (x + s, z)
                    b.set(px, y, pz, st("spruce_slab", type="top"))
                for s in (-2, 2):
                    px, pz = (x, z + s) if horiz else (x + s, z)
                    b.set(px, y + 1, pz, "spruce_fence" if i % 3 == 0 else "chain")
            for x, z in ((ax, az), (bx, bz)):
                for s in (-2, 2):
                    for y in range(1, 4):
                        b.set(x + s, hh + y, z, st("stripped_spruce_log", axis="y"))
                    b.set(x + s, hh + 4, z, "lantern")
            text_display(b, ax + 0.5, hh + 5, az + 0.5, "Kloof van Waimea", "gold", 1.4)
        self.add("canyon_bridge", min(ax, bx) - 3, min(az, bz) - 3, max(ax, bx) + 3, max(az, bz) + 3, build)

    # ----------------------------------------------------------- scheepswrak
    def shipwreck(self):
        isl, rng = self.isl, self.rng
        for deg in (128, 132, 124, 136, 60):
            ar = math.radians(deg)
            for r in range(220, 285):
                x, z = int(r * math.cos(ar)), int(r * math.sin(ar))
                if not isl.inb(x + 12, z + 6) or not isl.inb(x - 12, z - 6):
                    break
                if isl.dc[x - X0, z - X0] < -54 and SEA - isl.h(x, z) >= 6:
                    self._wreck(x, z)
                    return

    def _wreck(self, x, z):
        isl, rng = self.isl, self.rng
        floor = isl.h(x, z)
        isl.reserve(x - 14, z - 6, x + 14, z + 6)

        def build(b):
            L = 22
            for i in range(-L // 2, L // 2 + 1):
                half = 3 if abs(i) < L // 2 - 3 else (2 if abs(i) < L // 2 - 1 else 1)
                tilt = 1 if i > 3 else 0
                for s in range(-half, half + 1):
                    for y in range(0, 4):
                        side = abs(s) == half
                        if y == 0 or side:
                            if rng.random() < 0.88:
                                b.set(x + i, floor + 1 + y + tilt, z + s, rng.choice(["dark_oak_planks", "spruce_planks", "stripped_dark_oak_log[axis=x]"]))
                    if rng.random() < 0.5 and abs(i) < L // 2 - 2:
                        b.set(x + i, floor + 4 + tilt, z + s, st("spruce_slab", type="top"))
            for i in range(0, 13):
                mx = x + 2 + i // 3
                b.set(mx, floor + 2 + i, z, st("spruce_log", axis="y"))
            for i in range(-4, 5):
                b.set(x + 4 + 1, floor + 10, z + i, st("spruce_log", axis="z"))
            chest_late(b, x - 5, floor + 2, z, "east", "shipwreck_treasure", True)
            chest_late(b, x + 3, floor + 2, z + 1, "west", "shipwreck_supply", True)
            for _ in range(6):
                b.setk(x + rng.randint(-10, 10), floor + 2, z + rng.randint(-3, 3),
                       st(f"{rng.choice(['tube', 'brain', 'bubble', 'fire', 'horn'])}_coral_fan", waterlogged="true"))
        self.add("shipwreck", x - 15, z - 7, x + 15, z + 7, build)

    # ----------------------------------------------------------------- motu
    def motus(self):
        isl, rng = self.isl, self.rng
        for i, (mx, mz, mr) in enumerate(isl.motus):
            if not isl.inb(mx + 6, mz + 6) or not isl.inb(mx - 6, mz - 6):
                continue
            g = isl.h(mx, mz)

            def build(b, mx=mx, mz=mz, g=g, i=i):
                from . import flora
                flora.palm(b, mx - 2, mz - 1, rng, lean=(-1, 0), height=8)
                flora.palm(b, mx + 3, mz + 1, rng, lean=(1, 0), height=8)
                y = g + 3
                for x in range(mx - 1, mx + 3):
                    b.set(x, y - (1 if x in (mx, mx + 1) else 0), mz, "white_wool" if x % 2 else "light_blue_wool")
                if i == 0:
                    fale(b, mx, g, mz + 4, 5, 5, rng)
                else:
                    old.Planner.build_umbrella(Shim(RotBuf(b, mx, mz + 3, 1)), 0, 0, isl.h(mx, mz + 3), rng.choice(UMBRELLA_COLORS))
            isl.reserve(mx - 4, mz - 4, mx + 4, mz + 4)
            self.add("motu", mx - 8, mz - 8, mx + 8, mz + 8, build)

    # --------------------------------------------------------------- vulkaan
    def volcano(self):
        isl = self.isl
        v = isl.volcano
        cx, cz, L = v["x"], v["z"], v["lava"]
        for dx in range(-1, 3):
            for dz in range(-1, 2):
                isl.H[cx + dx - X0, cz + dz - X0] = L
                isl.liq_top[cx + dx - X0, cz + dz - X0] = -999

        def build(b):
            for dx in (0, 1):
                b.set(cx + dx, L, cz, "hay_block")
                b.set(cx + dx, L + 1, cz, st("campfire", lit="true", signal_fire="true"))
                for dz in (-1, 1):
                    b.set(cx + dx, L, cz + dz, "basalt[axis=y]")
            text_display(b, cx + 0.5, v["rim"] + 8, cz + 0.5, "Mauna Ahi", "red", 3.0)
        self.add("volcano", cx - 3, cz - 3, cx + 4, cz + 4, build)

    # -------------------------------------------------------- uitzichtpunten
    def lookouts(self):
        """Uitzichtplatform bij de grootste waterval van elke rivier."""
        isl = self.isl
        for r in isl.rivers:
            L = r["L"]
            best = max(range(1, len(L)), key=lambda i: L[i - 1] - L[i])
            drop = L[best - 1] - L[best]
            if drop < 4:
                continue
            x, z = r["pts"][best]
            nx, nz = r["pts"][min(len(L) - 1, best + 2)]
            tx, tz = nx - x, nz - z
            ln = math.hypot(tx, tz) or 1
            ux, uz = -tz / ln, tx / ln
            px, pz = int(round(x + ux * (r["w"][best] + 6))), int(round(z + uz * (r["w"][best] + 6)))
            if not isl.inb(px, pz) or isl.is_reserved(px - 3, pz - 3, px + 3, pz + 3):
                continue
            g = isl.h(px, pz)
            isl.reserve(px - 3, pz - 3, px + 3, pz + 3)
            name = {"A": "Wailua Falls", "B": "Akaka Falls", "C": "Manoa Falls"}[r["name"]]

            def build(b, px=px, pz=pz, g=g, name=name):
                for x in range(px - 2, px + 3):
                    for z in range(pz - 2, pz + 3):
                        b.set(x, g + 1, z, "spruce_planks")
                        if max(abs(x - px), abs(z - pz)) == 2:
                            b.set(x, g + 2, z, "spruce_fence")
                b.set(px, g + 2, pz, st("spruce_stairs", facing="north"))
                lamp(b, px + 2, g + 1, pz + 2, 2, "spruce_fence")
                text_display(b, px + 0.5, g + 5, pz + 0.5, name, "aqua", 1.4)
            self.add("lookout", px - 4, pz - 4, px + 4, pz + 4, build)

    # ---------------------------------------------------------------- wegen
    def roads(self):
        isl = self.isl
        t = {n: (x, z) for n, x, z in self.road_targets}
        links = [("resort", "plantation"), ("plantation", "village"), ("resort", "ranch"), ("ranch", "town"),
                 ("town", "fort"), ("village", "temple"), ("resort", "treehouse"), ("ranch", "canyon_bridge"),
                 ("temple", "lighthouse")]
        self.bridges = []
        for a, b in links:
            if a not in t or b not in t:
                continue
            path = self.road_path(t[a], t[b])
            wide = 2 if "lighthouse" in (a, b) or "temple" in (a, b) else 3
            span = []
            for x, z in path:
                for dx in range(-(wide // 2), wide - wide // 2):
                    for dz in range(-(wide // 2), wide - wide // 2):
                        px, pz = x + dx, z + dz
                        if isl.inb(px, pz) and not isl.res[px - X0, pz - X0]:
                            if isl.river_wet[px - X0, pz - X0]:
                                span.append((px, pz))
                            else:
                                isl.road[px - X0, pz - X0] = True
            # elke kruising met een rivier wordt een eigen brug
            left = set(span)
            while left:
                start = left.pop()
                comp, todo = [start], [start]
                while todo:
                    x, z = todo.pop()
                    for dx in (-1, 0, 1):
                        for dz in (-1, 0, 1):
                            q = (x + dx, z + dz)
                            if q in left:
                                left.remove(q)
                                comp.append(q)
                                todo.append(q)
                self.bridge(comp)

    def road_path(self, src, dst, step=2):
        isl = self.isl
        nx = S // step
        sub = isl.H[::step, ::step].astype(float)
        wet = isl.river_wet[::step, ::step]
        land = isl.dc[::step, ::step] > 1
        res = isl.res[::step, ::step]
        sx, sz = (src[0] - X0) // step, (src[1] - X0) // step
        tx, tz = (dst[0] - X0) // step, (dst[1] - X0) // step
        dist = {(sx, sz): 0.0}
        prev = {}
        pq = [(0.0, sx, sz)]
        while pq:
            d, x, z = heapq.heappop(pq)
            if (x, z) == (tx, tz):
                break
            if d > dist.get((x, z), 1e18):
                continue
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                a, b = x + dx, z + dz
                if not (0 <= a < nx and 0 <= b < nx) or not land[a, b]:
                    continue
                dh = abs(sub[a, b] - sub[x, z])
                c = math.hypot(dx, dz) * (1 + 3 * dh * dh + 25 * wet[a, b] + 6 * res[a, b])
                nd = d + c
                if nd < dist.get((a, b), 1e18):
                    dist[(a, b)] = nd
                    prev[(a, b)] = (x, z)
                    heapq.heappush(pq, (nd, a, b))
        if (tx, tz) not in prev:
            return []
        cells = [(tx, tz)]
        while cells[-1] != (sx, sz):
            cells.append(prev[cells[-1]])
        out = []
        for (ax, az), (bx, bz) in zip(cells, cells[1:]):
            for i in range(step):
                out.append((int(ax * step + X0 + (bx - ax) * i), int(az * step + X0 + (bz - az) * i)))
        return out

    def bridge(self, span):
        isl = self.isl
        xs = [p[0] for p in span]
        zs = [p[1] for p in span]
        x1, x2, z1, z2 = min(xs), max(xs), min(zs), max(zs)
        lv = max(int(isl.liq_top[p[0] - X0, p[1] - X0]) for p in span)
        banks = [isl.h(x, z) for x in range(x1 - 2, x2 + 3) for z in range(z1 - 2, z2 + 3)
                 if isl.inb(x, z) and not isl.river_wet[x - X0, z - X0]]
        deck = max(lv + 2, min(banks) if banks else lv + 2)
        cells = set(span)
        isl.reserve(x1 - 1, z1 - 1, x2 + 1, z2 + 1)

        def build(b):
            for x, z in cells:
                b.set(x, deck, z, "spruce_planks")
                for y in range(isl.h(x, z) + 1, deck):
                    if (x + z) % 4 == 0:
                        b.set(x, y, z, st("stripped_spruce_log", axis="y"))
            for x, z in cells:
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, z + dz) not in cells and isl.inb(x + dx, z + dz) and isl.river_wet[x + dx - X0, z + dz - X0]:
                        b.set(x + dx, deck, z + dz, "spruce_planks")
                        b.set(x + dx, deck + 1, z + dz, "spruce_fence")
        self.add("bridge", x1 - 2, z1 - 2, x2 + 2, z2 + 2, build)


# ============================================================ gebouwen
def bungalow(b, cx, deck, cz, rng, isl):
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            glassy = abs(x - cx) <= 0 and abs(z - cz) <= 0
            b.set(x, deck, z, "glass" if glassy else "bamboo_planks")
            if x in (cx - 3, cx + 3) and z in (cz - 3, cz + 3):
                for y in range(isl.h(x, z) + 1, deck):
                    b.set(x, y, z, st("stripped_jungle_log", axis="y"))
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 2, cz + 2):
            edge = x in (cx - 2, cx + 2) or z in (cz - 2, cz + 1)
            if edge:
                for y in range(1, 4):
                    corner = x in (cx - 2, cx + 2) and z in (cz - 2, cz + 1)
                    b.set(x, deck + y, z, st("bamboo_block", axis="y") if corner else "bamboo_planks")
    for x in (cx - 1, cx + 1):
        b.set(x, deck + 2, cz + 1, "glass_pane")
    b.clear(cx, deck + 1, cz - 2)
    b.clear(cx, deck + 2, cz - 2)
    b.set(cx, deck + 1, cz - 2, st("bamboo_door", facing="north", half="lower", hinge="left"))
    b.set(cx, deck + 2, cz - 2, st("bamboo_door", facing="north", half="upper", hinge="left"))
    bed = rng.choice(["white_bed", "light_blue_bed", "pink_bed"])
    b.set(cx - 1, deck + 1, cz - 1, st(bed, facing="south", part="foot"))
    b.set(cx - 1, deck + 1, cz, st(bed, facing="south", part="head"))
    b.set(cx + 1, deck + 1, cz - 1, st("barrel", facing="up"))
    b.set(cx + 1, deck + 2, cz - 1, "lantern")
    for x in (cx - 1, cx + 1):
        b.set(x, deck + 1, cz + 2, st("bamboo_stairs", facing="north", half="bottom"))
    b.set(cx + 3, deck, cz + 3, "bamboo_planks")
    for y in range(isl.h(cx + 3, cz + 4) + 1, deck + 1):
        b.set(cx + 3, y, cz + 4, st("ladder", facing="south"))
    hip_roof(b, cx - 4, cx + 4, cz - 4, cz + 4, deck + 4, fill="hay_block")
    glow_fringe(b, cx - 4, cx + 4, cz - 4, cz + 4, deck + 3, rng)


def church(b, x, g, z, rng):
    """Koloniale kerk met klokkentoren; voorkant naar het oosten (het plein)."""
    W, D = 11, 19
    x0, x1 = x - D // 2, x + D // 2
    z0, z1 = z - W // 2, z + W // 2
    for xx in range(x0, x1 + 1):
        for zz in range(z0, z1 + 1):
            b.set(xx, g, zz, "polished_andesite")
            edge = xx in (x0, x1) or zz in (z0, z1)
            if edge:
                for y in range(1, 9):
                    b.set(xx, g + y, zz, "smooth_quartz" if xx == x1 or y == 8 else "white_concrete")
    for xx in range(x0 + 2, x1 - 1, 3):
        for zz in (z0, z1):
            for y in (3, 4, 5):
                b.set(xx, g + y, zz, "yellow_stained_glass_pane" if y != 4 else "orange_stained_glass_pane")
    for zz in (z - 1, z, z + 1):
        for y in (1, 2, 3):
            b.clear(x1, g + y, zz)
    b.set(x1, g + 1, z, st("dark_oak_door", facing="east", half="lower", hinge="left"))
    b.set(x1, g + 2, z, st("dark_oak_door", facing="east", half="upper", hinge="left"))
    b.set(x1, g + 1, z + 1, st("dark_oak_door", facing="east", half="lower", hinge="right"))
    b.set(x1, g + 2, z + 1, st("dark_oak_door", facing="east", half="upper", hinge="right"))
    gable_roof(b, x0 - 1, x1 + 1, z0 - 1, z1 + 1, g + 9, "brick_stairs", "bricks", along="x")
    for xx in range(x0 + 3, x1 - 2, 2):
        for zz in (z - 3, z - 2, z + 2, z + 3):
            b.set(xx, g + 1, zz, st("dark_oak_stairs", facing="west"))
    b.set(x0 + 1, g + 1, z, "smooth_quartz")
    b.set(x0 + 1, g + 2, z, st("candle", candles=4, lit="true"))
    for zz in (z - 2, z + 2):
        b.set(x0 + 1, g + 1, zz, st("lantern"))
    # klokkentoren
    tx0, tz0 = x1 - 4, z0 - 5
    for xx in range(tx0, tx0 + 5):
        for zz in range(tz0, tz0 + 5):
            edge = xx in (tx0, tx0 + 4) or zz in (tz0, tz0 + 4)
            for y in range(1, 22):
                if edge:
                    b.set(xx, g + y, zz, "smooth_quartz" if y % 6 == 0 else "white_concrete")
    for xx, zz in ((tx0 + 2, tz0), (tx0 + 2, tz0 + 4), (tx0, tz0 + 2), (tx0 + 4, tz0 + 2)):
        for y in (17, 18, 19):
            b.clear(xx, g + y, zz)
    b.set(tx0 + 2, g + 20, tz0 + 2, "smooth_quartz")
    b.set(tx0 + 2, g + 19, tz0 + 2, st("bell", attachment="ceiling", facing="east"))
    hip_roof(b, tx0 - 1, tx0 + 5, tz0 - 1, tz0 + 5, g + 22, stair="brick_stairs", fill="bricks")
    b.set(tx0 + 2, g + 26, tz0 + 2, "iron_bars")
    b.set(tx0 + 2, g + 27, tz0 + 2, "iron_bars")


def house(b, x0, g, z0, face, rng):
    """Twee verdiepingen, pastelkleuren, luiken, balkon, pannendak. Voorkant naar 'face'."""
    W, D = 7, 7
    wall = rng.choice(PASTELS)
    trim = "smooth_quartz" if wall != "white_concrete" else "smooth_sandstone"
    shutter = rng.choice(["dark_oak_trapdoor", "spruce_trapdoor", "warped_trapdoor", "mangrove_trapdoor"])
    x1, z1 = x0 + W - 1, z0 + D - 1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            b.set(x, g, z, "spruce_planks")
            b.set(x, g + 4, z, "spruce_planks")
            edge = x in (x0, x1) or z in (z0, z1)
            if edge:
                for y in range(1, 9):
                    corner = x in (x0, x1) and z in (z0, z1)
                    b.set(x, g + y, z, trim if corner or y == 8 else wall)
            else:
                for y in (1, 2, 3, 5, 6, 7):
                    b.clear(x, g + y, z)
    # voorgevel
    if face in ("south", "north"):
        fz = z1 if face == "south" else z0
        out = 1 if face == "south" else -1
        cells = [(x, fz) for x in range(x0 + 1, x1)]
        ofs = (0, out)
        tface = face
    else:
        fx = x1 if face == "east" else x0
        out = 1 if face == "east" else -1
        cells = [(fx, z) for z in range(z0 + 1, z1)]
        ofs = (out, 0)
        tface = face
    mid = cells[len(cells) // 2]
    b.clear(mid[0], g + 1, mid[1])
    b.clear(mid[0], g + 2, mid[1])
    b.set(mid[0], g + 1, mid[1], st("dark_oak_door", facing=tface, half="lower", hinge="left"))
    b.set(mid[0], g + 2, mid[1], st("dark_oak_door", facing=tface, half="upper", hinge="left"))
    for (cx, cz) in (cells[0], cells[-1]):
        b.set(cx, g + 2, cz, "glass_pane")
        b.set(cx + ofs[0], g + 2, cz + ofs[1], st(shutter, facing=tface, half="top", open="true"))
    for (cx, cz) in cells[1:-1]:
        b.set(cx, g + 6, cz, "glass_pane")
        b.set(cx, g + 5, cz, "glass_pane") if (cx, cz) != mid else None
        b.set(cx + ofs[0], g + 4, cz + ofs[1], st("dark_oak_slab", type="top"))
        b.set(cx + ofs[0], g + 5, cz + ofs[1], "iron_bars")
    b.clear(mid[0], g + 5, mid[1])
    b.clear(mid[0], g + 6, mid[1])
    b.set(mid[0], g + 5, mid[1], st("dark_oak_door", facing=tface, half="lower", hinge="left"))
    b.set(mid[0], g + 6, mid[1], st("dark_oak_door", facing=tface, half="upper", hinge="left"))
    # dak
    hip_roof(b, x0 - 1, x1 + 1, z0 - 1, z1 + 1, g + 9, stair="brick_stairs", fill="bricks")
    # binnen
    b.set(x0 + 1, g + 1, z0 + 1, st("barrel", facing="up"))
    b.set(x0 + 1, g + 2, z0 + 1, "potted_red_tulip")
    b.set(x1 - 1, g + 1, z0 + 1, "crafting_table")
    b.set(x0 + 2, g + 3, z0 + 2, st("lantern", hanging="true"))
    bed = rng.choice(["red_bed", "blue_bed", "yellow_bed", "white_bed"])
    b.set(x0 + 1, g + 5, z0 + 1, st(bed, facing="south", part="foot"))
    b.set(x0 + 1, g + 5, z0 + 2, st(bed, facing="south", part="head"))
    b.set(x1 - 1, g + 5, z1 - 1, "lantern")
    # trap naar boven
    for i in range(3):
        b.set(x1 - 1, g + 1 + i, z0 + 2 + i, st("spruce_stairs", facing="south"))
        b.clear(x1 - 1, g + 4, z0 + 2 + i)


def market_stall(b, x, g, z, rng, i):
    colors = ["red", "yellow", "lime", "light_blue", "orange", "magenta"]
    c = colors[i % len(colors)]
    for dx in (-1, 1):
        for dz in (-1, 1):
            for y in (1, 2):
                b.set(x + dx, g + y, z + dz, "spruce_fence")
    for dx in (-2, -1, 0, 1, 2):
        for dz in (-1, 0, 1):
            b.set(x + dx, g + 3, z + dz, f"{c}_wool" if dx % 2 else "white_wool")
    for dx in (-1, 0, 1):
        b.set(x + dx, g + 1, z, rng.choice(["melon", "pumpkin", st("barrel", facing="up"), "hay_block"]))


def field(b, x0, g, z0, w, d, kind, rng):
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + d):
            edge = x in (x0, x0 + w - 1) or z in (z0, z0 + d - 1)
            if kind == "cane":
                row = (x - x0) % 3
                if edge:
                    b.set(x, g, z, "coarse_dirt")
                elif row == 0:
                    b.set(x, g, z, "water")
                else:
                    b.set(x, g, z, "grass_block")
                    for y in range(1, rng.randint(2, 4)):
                        b.set(x, g + y, z, "sugar_cane")
            elif kind == "coffee":
                b.set(x, g, z, "coarse_dirt" if edge or (x - x0) % 3 == 0 else "grass_block")
                if not edge and (x - x0) % 3 != 0 and (z - z0) % 2 == 0:
                    b.set(x, g + 1, z, st("sweet_berry_bush", age=3))
            else:  # ananas
                b.set(x, g, z, "coarse_dirt" if edge or (x - x0) % 2 == 0 else "rooted_dirt")
                if not edge and (x - x0) % 2 == 1 and (z - z0) % 2 == 0:
                    b.set(x, g + 1, z, "melon")
    for x, z in ((x0, z0), (x0 + w - 1, z0), (x0, z0 + d - 1), (x0 + w - 1, z0 + d - 1)):
        lamp(b, x, g, z, 2, "oak_fence")


def hacienda(b, x, g, z, rng):
    W, D = 15, 11
    x0, x1, z0, z1 = x - W // 2, x + W // 2, z - D // 2, z + D // 2
    for xx in range(x0, x1 + 1):
        for zz in range(z0, z1 + 1):
            b.set(xx, g, zz, "terracotta")
            edge = xx in (x0, x1) or zz in (z0, z1)
            if edge:
                for y in range(1, 6):
                    b.set(xx, g + y, zz, "white_terracotta" if y < 5 else "smooth_sandstone")
            else:
                for y in range(1, 6):
                    b.clear(xx, g + y, zz)
    for xx in range(x0 + 2, x1 - 1, 3):
        for y in (2, 3):
            b.set(xx, g + y, z1, "glass_pane")
            b.set(xx, g + y, z0, "glass_pane")
    b.clear(x, g + 1, z1)
    b.clear(x, g + 2, z1)
    b.set(x, g + 1, z1, st("dark_oak_door", facing="south", half="lower", hinge="left"))
    b.set(x, g + 2, z1, st("dark_oak_door", facing="south", half="upper", hinge="left"))
    # veranda met zuilen
    for xx in range(x0, x1 + 1):
        for zz in (z1 + 1, z1 + 2, z1 + 3):
            b.set(xx, g, zz, "smooth_stone")
        if (xx - x0) % 3 == 0:
            for y in range(1, 5):
                b.set(xx, g + y, z1 + 3, st("quartz_pillar", axis="y"))
    for xx in range(x0, x1 + 1):
        for zz in (z1 + 1, z1 + 2, z1 + 3):
            b.set(xx, g + 5, zz, st("smooth_sandstone_slab", type="bottom"))
    for xx in (x0 + 2, x1 - 2):
        b.set(xx, g + 1, z1 + 2, st("dark_oak_stairs", facing="north"))
    for xx in (x0 + 1, x1 - 1):
        b.set(xx, g + 4, z1 + 2, st("lantern", hanging="true"))
    hip_roof(b, x0 - 1, x1 + 1, z0 - 1, z1 + 1, g + 6, stair="brick_stairs", fill="bricks")
    b.set(x0 + 2, g + 1, z0 + 2, "bookshelf")
    b.set(x0 + 3, g + 1, z0 + 2, "bookshelf")
    b.set(x1 - 2, g + 1, z0 + 2, "lectern")
    b.set(x, g + 4, z, st("lantern", hanging="true"))


def sugar_mill(b, x, g, z, rng):
    for xx in range(x - 4, x + 5):
        for zz in range(z - 4, z + 5):
            b.set(xx, g, zz, "stone_bricks")
            if max(abs(xx - x), abs(zz - z)) == 4:
                for y in range(1, 6):
                    b.set(xx, g + y, zz, "bricks" if y < 5 else "mud_bricks")
            else:
                for y in range(1, 6):
                    b.clear(xx, g + y, zz)
    for y in (1, 2, 3):
        b.clear(x - 4, g + y, z)
    gable_roof(b, x - 5, x + 5, z - 5, z + 5, g + 6, "mud_brick_stairs", "mud_bricks", along="x")
    cx, cz = x + 6, z + 2
    for y in range(0, 24):
        for xx in range(cx - 1, cx + 2):
            for zz in range(cz - 1, cz + 2):
                if (xx, zz) != (cx, cz) or y == 0:
                    b.set(xx, g + y, zz, "bricks" if y < 22 else "mud_bricks")
                else:
                    b.clear(xx, g + y, zz)
    b.set(cx, g + 1, cz, "hay_block")
    b.set(cx, g + 2, cz, st("campfire", lit="true", signal_fire="true"))
    b.set(x, g + 1, z, "grindstone")
    b.set(x + 2, g + 1, z + 2, st("barrel", facing="up"))
    b.set(x - 2, g + 1, z + 2, st("barrel", facing="up"))
    b.set(x + 2, g + 1, z - 2, "cauldron")
