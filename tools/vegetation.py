"""Natuur: palmen, junglebomen, bamboe, bloemen, koraalrif, lagune-planten, dieren en licht."""
import math

from world import SEA, TOP, st

LEAF = st("jungle_leaves", persistent="true")
CORALS = ["tube", "brain", "bubble", "fire", "horn"]
FLOWERS = ["red_tulip", "orange_tulip", "pink_tulip", "allium", "blue_orchid", "torchflower",
           "poppy", "dandelion", "oxeye_daisy", "cornflower"]
TALL_FLOWERS = ["rose_bush", "peony", "lilac", "pitcher_plant", "sunflower"]


def fish_variant(rng):
    size = rng.randint(0, 1)
    pattern = rng.randint(0, 5)
    base = rng.randint(0, 15)
    pat_col = rng.randint(0, 15)
    v = size | (pattern << 8) | (base << 16) | (pat_col << 24)
    return v - (1 << 32) if v >= 1 << 31 else v


class Nature:
    def __init__(self, w, t, palm_spots=()):
        self.w, self.t, self.rng = w, t, w.rng
        self.trunks = []
        self.palm_spots = palm_spots

    # ----------------------------------------------------------- hulpjes
    def free_trunk(self, x, z, dist):
        return all((x - a) ** 2 + (z - b) ** 2 >= dist * dist for a, b in self.trunks)

    def near_reserved(self, x, z, r):
        w = self.w
        for a in range(x - r, x + r + 1):
            for b in range(z - r, z + r + 1):
                if (a, b) in w.reserved:
                    return True
        return False

    def ok_ground(self, x, z, kinds):
        t, w = self.t, self.w
        if (x, z) not in t.H or t.kind[(x, z)] not in kinds or (x, z) in w.reserved:
            return False
        h = t.h(x, z)
        return w.is_air(x, h + 1, z)

    def leaf(self, x, y, z):
        if self.w.is_air(x, y, z):
            self.w.set(x, y, z, LEAF)

    def log(self, x, y, z, s=None):
        w = self.w
        cur = w.get(x, y, z)
        if cur is None or cur == LEAF:
            w.set(x, y, z, s or st("jungle_log", axis="y"))

    # ------------------------------------------------------------- palmen
    def palm(self, x, z, lean=None):
        w, rng, t = self.w, self.rng, self.t
        y0 = t.h(x, z) + 1
        height = rng.randint(6, 10) if w.n > 1 else rng.randint(5, 7)
        dx, dz = lean or rng.choice([(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0)])
        amount = rng.uniform(1.0, 3.2)
        px, pz = x, z
        for i in range(height):
            f = (i / (height - 1)) ** 2
            px, pz = x + round(dx * amount * f), z + round(dz * amount * f)
            if not w.inb(px, pz) or not (w.is_air(px, y0 + i, pz) or w.get(px, y0 + i, pz) == LEAF):
                return False
            self.log(px, y0 + i, pz, st("jungle_log", axis="y") if i % 3 else st("stripped_jungle_log", axis="y"))
        ty = y0 + height - 1
        self.leaf(px, ty + 1, pz)
        self.leaf(px, ty + 2, pz)
        fronds = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for fx, fz in fronds:
            diag = fx and fz
            length = rng.randint(3, 4) if diag else rng.randint(4, 6)
            prof = [1, 1, 1, 0, 0, -1, -1]
            for j in range(1, length + 1):
                yy = ty + prof[j]
                self.leaf(px + fx * j, yy, pz + fz * j)
                if j == length and rng.random() < 0.7:
                    self.leaf(px + fx * j, yy - 1, pz + fz * j)
                if not diag and j <= 2:
                    self.leaf(px + fx * j + fz, yy, pz + fz * j + fx)
                    self.leaf(px + fx * j - fz, yy, pz + fz * j - fx)
        for face, (cx, cz) in (("west", (1, 0)), ("east", (-1, 0)), ("north", (0, 1)), ("south", (0, -1))):
            if rng.random() < 0.55 and w.is_air(px + cx, ty, pz + cz):
                w.set(px + cx, ty, pz + cz, st("cocoa", facing=face, age=2))
        self.trunks.append((x, z))
        return True

    # ------------------------------------------------------- junglebomen
    def jungle_tree(self, x, z, big=False):
        w, rng, t = self.w, self.rng, self.t
        y0 = t.h(x, z) + 1
        h = rng.randint(14, 22) if big else rng.randint(7, 12)
        size = 2 if big else 1
        for a in range(size):
            for b in range(size):
                if t.h(x + a, z + b) + 1 < y0 - 1 or not w.inb(x + a, z + b):
                    return False
        if y0 + h + 4 > TOP:
            return False
        for i in range(h):
            for a in range(size):
                for b in range(size):
                    self.log(x + a, y0 + i, z + b)
        # wortels bij grote bomen
        if big:
            for a, b in ((-1, 0), (2, 1), (0, -1), (1, 2)):
                for i in range(rng.randint(1, 3)):
                    self.log(x + a, y0 + i, z + b, "jungle_wood")
        # cacao
        for _ in range(rng.randint(1, 4)):
            i = rng.randint(2, max(2, h - 4))
            face, (cx, cz), (ox, oz) = rng.choice([("east", (-1, 0), (0, 0)), ("west", (size, 0), (size - 1, 0)),
                                                   ("south", (0, -1), (0, 0)), ("north", (0, size), (0, size - 1))])
            if w.is_air(x + cx, y0 + i, z + cz):
                w.set(x + cx, y0 + i, z + cz, st("cocoa", facing=face, age=rng.randint(0, 2)))
        # takken + bladeren
        r = 4.5 if big else 2.8
        cxm, czm = x + (size - 1) / 2, z + (size - 1) / 2
        top = y0 + h
        blobs = [(cxm, top - 1, czm, r)]
        if big:
            for _ in range(rng.randint(2, 4)):
                ang = rng.uniform(0, math.tau)
                by = y0 + rng.randint(h // 2, h - 4)
                L = rng.randint(3, 5)
                ex, ez = cxm, czm
                for j in range(1, L + 1):
                    ex = cxm + math.cos(ang) * j
                    ez = czm + math.sin(ang) * j
                    axis = "x" if abs(math.cos(ang)) > abs(math.sin(ang)) else "z"
                    self.log(round(ex), by + j // 2, round(ez), st("jungle_log", axis=axis))
                blobs.append((ex, by + L // 2 + 1, ez, 2.6))
        else:
            blobs.append((cxm + rng.uniform(-1, 1), top - 3, czm + rng.uniform(-1, 1), 2.2))
        leaves = []
        for bx, by, bz, br in blobs:
            ri = int(br + 1)
            for a in range(-ri, ri + 1):
                for b in range(-2, 3):
                    for c in range(-ri, ri + 1):
                        d = (a / br) ** 2 + (b / (br * 0.55)) ** 2 + (c / br) ** 2
                        if d <= 1 + rng.uniform(-0.15, 0.1):
                            p = (round(bx + a), round(by + b), round(bz + c))
                            self.leaf(*p)
                            leaves.append(p)
        # klimop
        for _ in range(int(len(leaves) * 0.08)):
            lx, ly, lz = rng.choice(leaves)
            face, (ox, oz) = rng.choice([("east", (-1, 0)), ("west", (1, 0)), ("south", (0, -1)), ("north", (0, 1))])
            vx, vz = lx + ox, lz + oz
            if not w.is_air(vx, ly, vz):
                continue
            for i in range(rng.randint(2, 7)):
                if w.is_air(vx, ly - i, vz):
                    w.set(vx, ly - i, vz, st("vine", **{face: "true"}))
                else:
                    break
        self.trunks.append((x, z))
        return True

    def bush(self, x, z):
        w, t, rng = self.w, self.t, self.rng
        y0 = t.h(x, z) + 1
        self.log(x, y0, z)
        for a in range(-2, 3):
            for b in range(0, 3):
                for c in range(-2, 3):
                    if (a * a + c * c) / 4.5 + b * b / 3.0 <= 1 + rng.uniform(-0.2, 0.1):
                        self.leaf(x + a, y0 + b, z + c)

    def bamboo(self, x, z):
        w, t, rng = self.w, self.t, self.rng
        y0 = t.h(x, z) + 1
        h = rng.randint(5, 13)
        for i in range(h):
            if not w.is_air(x, y0 + i, z):
                return
        for i in range(h):
            leaves = "large" if i >= h - 2 else "small" if i >= h - 4 else "none"
            w.set(x, y0 + i, z, st("bamboo", age=1, leaves=leaves, stage=0))

    # ------------------------------------------------------------- planten
    def ground_cover(self, x, z):
        w, t, rng = self.w, self.t, self.rng
        h = t.h(x, z)
        top = w.get(x, h, z)
        if top not in ("minecraft:grass_block", "minecraft:podzol", "minecraft:moss_block", "minecraft:coarse_dirt"):
            return
        if not w.is_air(x, h + 1, z):
            return
        r = rng.random()
        if r < 0.26:
            w.set(x, h + 1, z, "short_grass")
        elif r < 0.36:
            w.set(x, h + 1, z, "fern")
        elif r < 0.42 and w.is_air(x, h + 2, z):
            kind = rng.choice(["tall_grass", "large_fern"])
            w.set(x, h + 1, z, st(kind, half="lower"))
            w.set(x, h + 2, z, st(kind, half="upper"))
        elif r < 0.50:
            w.set(x, h + 1, z, rng.choice(FLOWERS))
        elif r < 0.53 and w.is_air(x, h + 2, z):
            kind = rng.choice(TALL_FLOWERS)
            w.set(x, h + 1, z, st(kind, half="lower"))
            w.set(x, h + 2, z, st(kind, half="upper"))
        elif r < 0.56:
            w.set(x, h + 1, z, st("pink_petals", facing=rng.choice(["north", "south", "east", "west"]),
                                  flower_amount=rng.randint(1, 4)))
        elif r < 0.565:
            w.set(x, h + 1, z, "melon")
        elif r < 0.57 and top == "minecraft:moss_block":
            w.set(x, h + 1, z, "moss_carpet")

    # ------------------------------------------------------------ hoofdloop
    def grow(self):
        w, t, rng = self.w, self.t, self.rng
        cols = list(t.H.keys())
        rng.shuffle(cols)
        S = w.S
        # vaste palmen naast de bar
        for x, z, lean in self.palm_spots:
            if self.ok_ground(x, z, ("beach", "land")):
                self.palm(x, z, lean)
        # palmen op het strand
        beach = [c for c in cols if t.kind[c] == "beach" and c[0] >= t.shore_x[c[1]] + 2]
        target = max(2, len(beach) // 34)
        for x, z in beach:
            if target <= 0:
                break
            if not self.ok_ground(x, z, ("beach",)) or not self.free_trunk(x, z, 5) or self.near_reserved(x, z, 1):
                continue
            lean = (-1, rng.choice([-1, 0, 1])) if x - t.shore_x[z] < 6 else None
            if self.palm(x, z, lean):
                target -= 1
        # jungle
        land = [c for c in cols if t.kind[c] == "land"]
        bigs = len(land) // 420 if w.n >= 3 else 0
        trees = len(land) // 70
        palms_land = len(land) // 160
        bushes = len(land) // 40
        for x, z in land:
            if not self.ok_ground(x, z, ("land",)):
                continue
            edge = x - t.shore_x[z]
            if bigs > 0 and self.free_trunk(x, z, 9) and not self.near_reserved(x, z, 6) and self.ok_ground(x + 1, z + 1, ("land",)):
                if self.jungle_tree(x, z, big=True):
                    bigs -= 1
                    continue
            if trees > 0 and self.free_trunk(x, z, 5) and not self.near_reserved(x, z, 4):
                if self.jungle_tree(x, z):
                    trees -= 1
                    continue
            if palms_land > 0 and self.free_trunk(x, z, 5) and not self.near_reserved(x, z, 4) and edge < S * 0.45:
                if self.palm(x, z):
                    palms_land -= 1
                    continue
            if bushes > 0 and self.free_trunk(x, z, 3) and not self.near_reserved(x, z, 2):
                self.bush(x, z)
                self.trunks.append((x, z))
                bushes -= 1
        # bamboebossen (ruis-vlekken)
        for x, z in land:
            if self.t.n3.fbm(x * 0.09 + 100, z * 0.09) > 0.42 and rng.random() < 0.35:
                if self.ok_ground(x, z, ("land",)) and not self.near_reserved(x, z, 1) and self.free_trunk(x, z, 1):
                    self.bamboo(x, z)
        for x, z in land:
            if (x, z) not in w.reserved:
                self.ground_cover(x, z)
        self.beach_details(cols)
        self.underwater(cols)
        self.lagoon_details()
        self.rocks(cols)
        self.animals(cols)
        self.lights(cols)

    # ---------------------------------------------------------- strand
    def beach_details(self, cols):
        w, t, rng = self.w, self.t, self.rng
        for x, z in cols:
            if t.kind[(x, z)] != "beach" or (x, z) in w.reserved:
                continue
            h = t.h(x, z)
            if not w.is_air(x, h + 1, z):
                continue
            r = rng.random()
            if r < 0.012:
                w.set(x, h + 1, z, st(f"dead_{rng.choice(CORALS)}_coral_fan", waterlogged="false"))
            elif r < 0.017:
                w.set(x, h + 1, z, st(f"dead_{rng.choice(CORALS)}_coral", waterlogged="false"))
            elif r < 0.021:
                w.set(x, h + 1, z, "dead_bush")
            elif r < 0.023 and x - t.shore_x[z] < 5:
                axis = rng.choice(["x", "z"])
                dx, dz = (1, 0) if axis == "x" else (0, 1)
                for i in range(rng.randint(2, 3)):
                    if w.is_air(x + dx * i, h + 1, z + dz * i) and t.kind.get((x + dx * i, z + dz * i)) == "beach":
                        w.set(x + dx * i, h + 1, z + dz * i, st("stripped_oak_log", axis=axis))
            elif r < 0.0245:
                w.set(x, h + 1, z, st("turtle_egg", eggs=rng.randint(1, 4), hatch=0))

    # ---------------------------------------------------------- onder water
    def underwater(self, cols):
        w, t, rng = self.w, self.t, self.rng
        for x, z in cols:
            if t.kind[(x, z)] != "sea" or (x, z) in w.reserved:
                continue
            h = t.h(x, z)
            depth = SEA - h
            if not w.get(x, h + 1, z) == "minecraft:water":
                continue
            reef = t.n2.fbm(x * 0.12 + 200, z * 0.12) > 0.12 and depth >= 3
            r = rng.random()
            if reef and r < 0.22:
                self.coral_mound(x, h, z, depth)
            elif depth >= 6 and r < 0.18:
                kh = rng.randint(2, depth - 1)
                for i in range(kh):
                    w.set(x, h + 1 + i, z, "kelp_plant" if i < kh - 1 else st("kelp", age=25))
            elif r < 0.30:
                if depth >= 3 and rng.random() < 0.4:
                    w.set(x, h + 1, z, st("tall_seagrass", half="lower"))
                    w.set(x, h + 2, z, st("tall_seagrass", half="upper"))
                else:
                    w.set(x, h + 1, z, "seagrass")
            elif r < 0.33 and depth >= 2:
                w.set(x, h + 1, z, st("sea_pickle", pickles=rng.randint(1, 4), waterlogged="true"))

    def coral_mound(self, x, h, z, depth):
        w, rng = self.w, self.rng
        kind = rng.choice(CORALS)
        tall = rng.randint(1, max(1, min(3, depth - 2)))
        blocks = []
        for a in range(-1, 2):
            for b in range(-1, 2):
                if (a and b) and rng.random() < 0.5:
                    continue
                hh = tall if (a, b) == (0, 0) else rng.randint(0, tall - 1) if tall > 1 else rng.randint(0, 1)
                for i in range(hh):
                    p = (x + a, h + 1 + i, z + b)
                    if self.w.get(*p) == "minecraft:water":
                        w.set(*p, f"{rng.choice([kind, kind, rng.choice(CORALS)])}_coral_block")
                        blocks.append(p)
        for bx, by, bz in blocks:
            if w.get(bx, by + 1, bz) == "minecraft:water" and rng.random() < 0.7:
                r = rng.random()
                if r < 0.45:
                    w.set(bx, by + 1, bz, st(f"{rng.choice(CORALS)}_coral", waterlogged="true"))
                elif r < 0.8:
                    w.set(bx, by + 1, bz, st(f"{rng.choice(CORALS)}_coral_fan", waterlogged="true"))
                else:
                    w.set(bx, by + 1, bz, st("sea_pickle", pickles=rng.randint(2, 4), waterlogged="true"))
            for face, (ox, oz) in (("east", (1, 0)), ("west", (-1, 0)), ("south", (0, 1)), ("north", (0, -1))):
                if rng.random() < 0.25 and w.get(bx + ox, by, bz + oz) == "minecraft:water":
                    w.set(bx + ox, by, bz + oz, st(f"{rng.choice(CORALS)}_coral_wall_fan", facing=face, waterlogged="true"))

    # ---------------------------------------------------------- lagune
    def lagoon_details(self):
        w, t, rng = self.w, self.t, self.rng
        lg = t.lagoon
        if not lg:
            return
        lv = lg["level"]
        for (x, z), k in list(t.kind.items()):
            if k == "lagoon":
                h = t.h(x, z)
                if rng.random() < 0.13 and w.is_air(x, lv + 1, z):
                    w.set(x, lv + 1, z, "lily_pad")
                elif lv - h == 1 and rng.random() < 0.08 and w.get(x, h, z) in ("minecraft:clay",):
                    w.set(x, lv, z, st("big_dripleaf", facing=rng.choice(["north", "south", "east", "west"]),
                                       waterlogged="true"))
                elif rng.random() < 0.2 and w.get(x, h + 1, z) == "minecraft:water":
                    w.set(x, h + 1, z, "seagrass")
            elif k == "land" and (x, z) not in w.reserved and t.h(x, z) == lv:
                wet = any(t.kind.get((x + a, z + b)) == "lagoon" for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if wet and w.is_air(x, lv + 1, z) and rng.random() < 0.45:
                    for i in range(rng.randint(2, 3)):
                        w.set(x, lv + 1 + i, z, "sugar_cane")

    def rocks(self, cols):
        w, t, rng = self.w, self.t, self.rng
        for x, z in cols:
            k = t.kind[(x, z)]
            if (x, z) in w.reserved:
                continue
            h = t.h(x, z)
            if k == "rim" and rng.random() < 0.18:
                w.set(x, h + 1, z, rng.choice(["stone", "andesite", "mossy_cobblestone", "tuff"]))
            elif k == "beach" and x - t.shore_x[z] < 3 and rng.random() < 0.012:
                for a, b, c in ((0, 1, 0), (1, 1, 0), (0, 1, 1), (0, 2, 0)):
                    if rng.random() < 0.8 and w.is_air(x + a, h + b, z + c):
                        w.set(x + a, h + b, z + c, rng.choice(["stone", "andesite", "mossy_cobblestone", "cobblestone"]))

    # ---------------------------------------------------------- dieren
    def animals(self, cols):
        w, t, rng = self.w, self.t, self.rng
        S = w.S
        sea = [c for c in cols if t.kind[c] == "sea" and SEA - t.h(*c) >= 3 and c not in w.reserved]
        for _ in range(min(12, max(2, len(sea) // 120))):
            if not sea:
                break
            x, z = rng.choice(sea)
            var = fish_variant(rng)
            for i in range(rng.randint(3, 5)):
                y = rng.randint(t.h(x, z) + 1, SEA)
                w.summon("tropical_fish", x + rng.random(), y + 0.3, z + rng.random(),
                         f"Variant:{var},PersistenceRequired:1b")
        deep = [c for c in sea if SEA - t.h(*c) >= 5]
        for _ in range(min(3, len(deep) // 300)):
            x, z = rng.choice(deep)
            w.summon("dolphin", x + 0.5, SEA - 1, z + 0.5, "PersistenceRequired:1b")
        beach = [c for c in cols if t.kind[c] == "beach" and c not in w.reserved]
        for _ in range(min(5, max(1, len(beach) // 250))):
            if beach:
                x, z = rng.choice(beach)
                w.summon("turtle", x + 0.5, t.h(x, z) + 1, z + 0.5, "PersistenceRequired:1b")
        land = [c for c in cols if t.kind[c] == "land" and c not in w.reserved]
        for _ in range(min(10, max(1, len(land) // 200))):
            if land:
                x, z = rng.choice(land)
                w.summon("parrot", x + 0.5, t.h(x, z) + 2, z + 0.5,
                         f"Variant:{rng.randint(0, 4)},PersistenceRequired:1b")
        for _ in range(min(3, len(land) // 500)):
            x, z = rng.choice(land)
            w.summon("ocelot", x + 0.5, t.h(x, z) + 1, z + 0.5, "PersistenceRequired:1b")
        for _ in range(min(3, len(land) // 400)):
            x, z = rng.choice(land)
            w.summon("panda", x + 0.5, t.h(x, z) + 1, z + 0.5,
                     f'PersistenceRequired:1b,MainGene:"{rng.choice(["normal", "lazy", "playful"])}",HiddenGene:"normal"')
        lagoon = [c for c, k in t.kind.items() if k == "lagoon"]
        for _ in range(min(4, len(lagoon) // 10)):
            x, z = rng.choice(lagoon)
            w.summon("axolotl", x + 0.5, t.h(x, z) + 1, z + 0.5, f"Variant:{rng.randint(0, 4)},PersistenceRequired:1b")
        for _ in range(min(3, len(lagoon) // 12)):
            x, z = rng.choice(lagoon)
            w.summon("frog", x + 0.5, t.lagoon["level"] + 1.2, z + 0.5, 'variant:"minecraft:warm",PersistenceRequired:1b')
        for _ in range(min(3, len(lagoon) // 10)):
            x, z = rng.choice(lagoon)
            w.summon("tropical_fish", x + 0.5, t.h(x, z) + 1.2, z + 0.5,
                     f"Variant:{fish_variant(rng)},PersistenceRequired:1b")

    # ---------------------------------------------------------- licht
    def lights(self, cols):
        """Onzichtbare lichtblokken zodat er geen monsters spawnen."""
        w, t = self.w, self.t
        for x, z in cols:
            if (x - w.x0) % 9 != 4 or (z - w.x0) % 9 != 4:
                continue
            h = t.h(x, z)
            k = t.kind[(x, z)]
            if k in ("sea", "lagoon"):
                if w.get(x, h + 1, z) == "minecraft:water":
                    w.set(x, h + 1, z, st("light", level=10, waterlogged="true"))
            else:
                for y in range(h + 2, h + 5):
                    if w.is_air(x, y, z) and w.is_air(x, y - 1, z):
                        w.set(x, y, z, st("light", level=11))
                        break
