"""Verlaten, overwoekerde tiki/azteken-ruines als structure templates (voor worldgen)."""
import math
import random

from nbt import COMPOUND, INT, STRING, TagList, write_gzip
from world import ns, parse_state, st

DATA_VERSION = 3955
LEAF = st("jungle_leaves", persistent="true")
AZ = st("azalea_leaves", persistent="true")
FAZ = st("flowering_azalea_leaves", persistent="true")
STONE = ["mossy_stone_bricks", "mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks", "tuff_bricks",
         "mossy_cobblestone", "stone_bricks"]
FACES = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}


class Tpl:
    def __init__(self, seed):
        self.blk = {}
        self.nbt = {}
        self.rng = random.Random(seed)

    def set(self, x, y, z, s):
        self.blk[(x, y, z)] = ns(s)

    def setk(self, x, y, z, s):
        if (x, y, z) not in self.blk:
            self.blk[(x, y, z)] = ns(s)

    def get(self, x, y, z):
        return self.blk.get((x, y, z))

    def clear(self, x, y, z):
        self.blk.pop((x, y, z), None)

    def fill(self, x1, y1, z1, x2, y2, z2, s):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, s() if callable(s) else s)

    def stone(self):
        return self.rng.choice(STONE)

    def chest(self, x, y, z, facing, loot, waterlogged=False):
        props = {"facing": facing}
        if waterlogged:
            props["waterlogged"] = "true"
        self.set(x, y, z, st("chest", **props))
        self.nbt[(x, y, z)] = {"id": "minecraft:chest", "LootTable": f"minecraft:chests/{loot}"}

    def sign(self, x, y, z, state, lines, color="gray"):
        self.set(x, y, z, state)
        msgs = TagList(STRING, [f'{{"text":"{t}","color":"{color}"}}' if t else '""' for t in lines])
        side = {"messages": msgs, "has_glowing_text": 0, "color": "black"}
        self.nbt[(x, y, z)] = {"id": "minecraft:hanging_sign", "front_text": side,
                               "back_text": {"messages": TagList(STRING, list(msgs)), "has_glowing_text": 0, "color": "black"}}

    def vines_on(self, frac=0.12, maxlen=6):
        """Hang klimop aan zijkanten van stenen blokken."""
        rng = self.rng
        cells = [p for p, s in self.blk.items() if "brick" in s or "cobble" in s or "tuff" in s]
        for x, y, z in cells:
            if rng.random() > frac:
                continue
            face, (dx, dz) = rng.choice(list(FACES.items()))
            vx, vz = x + dx, z + dz
            opp = {"east": "west", "west": "east", "north": "south", "south": "north"}[face]
            for i in range(rng.randint(1, maxlen)):
                if (vx, y - i, vz) in self.blk or y - i < 0:
                    break
                self.set(vx, y - i, vz, st("vine", **{opp: "true"}))

    def overgrow(self, frac=0.25):
        """Mos, struikjes en bladeren bovenop vrije stenen oppervlakken."""
        rng = self.rng
        tops = [(x, y, z) for (x, y, z), s in list(self.blk.items())
                if (x, y + 1, z) not in self.blk and ("brick" in s or "cobble" in s or "tuff" in s or "stone" in s)
                and "slab" not in s and "stairs" not in s and "wall" not in s]
        for x, y, z in tops:
            r = rng.random()
            if r < frac * 0.5:
                self.set(x, y + 1, z, "moss_carpet")
            elif r < frac * 0.75:
                self.set(x, y + 1, z, rng.choice([LEAF, AZ, FAZ]))
            elif r < frac * 0.8:
                self.set(x, y + 1, z, LEAF)
                self.setk(x, y + 2, z, LEAF)

    def write(self, path):
        xs = [p[0] for p in self.blk]
        ys = [p[1] for p in self.blk]
        zs = [p[2] for p in self.blk]
        mx, my, mz = min(xs), min(ys), min(zs)
        size = [max(xs) - mx + 1, max(ys) - my + 1, max(zs) - mz + 1]
        palette = {}
        blocks = TagList(COMPOUND)
        for (x, y, z), s in sorted(self.blk.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            idx = palette.setdefault(s, len(palette))
            entry = {"pos": TagList(INT, [x - mx, y - my, z - mz]), "state": idx}
            if (x, y, z) in self.nbt:
                entry["nbt"] = self.nbt[(x, y, z)]
            blocks.append(entry)
        pal = TagList(COMPOUND)
        for s in palette:
            name, props = parse_state(s)
            c = {"Name": name}
            if props:
                c["Properties"] = props
            pal.append(c)
        write_gzip(path, {"DataVersion": DATA_VERSION, "size": TagList(INT, size), "palette": pal,
                          "blocks": blocks, "entities": TagList(COMPOUND)})
        return size, set(palette)


# ============================================================ onderdelen
def tiki(t, x, y, z, facing="south"):
    dx, dz = FACES[facing]
    px, pz = -dz, dx
    wood = st("stripped_jungle_wood", axis="y")
    for yy in range(0, 5):
        for s in (-1, 0, 1):
            t.set(x + px * s, y + yy, z + pz * s, wood)
    fx, fz = x + dx, z + dz
    for s in (-1, 1):
        t.set(fx + px * s, y + 3, fz + pz * s, "black_terracotta")
    t.set(fx, y + 2, fz, st("jungle_trapdoor", facing=facing, half="top", open="false"))
    t.set(fx, y + 1, fz, "red_terracotta")
    for s in (-1, 1):
        t.set(fx + px * s, y + 1, fz + pz * s, wood)
    for s in (-1, 0, 1):
        t.set(fx + px * s, y + 4, fz + pz * s, st("jungle_slab", type="bottom"))
    t.set(x, y + 5, z, "bamboo_fence")
    t.set(x, y + 6, z, "bamboo_fence")


def column(t, x, y0, z, h, broken=False):
    for y in range(y0, y0 + h):
        t.set(x, y, z, "chiseled_tuff_bricks" if (y - y0) % 4 == 0 else "tuff_bricks")
    if not broken:
        t.set(x, y0 + h, z, "chiseled_tuff")
        for dx, dz in FACES.values():
            t.set(x + dx, y0 + h, z + dz, st("tuff_brick_slab", type="top"))


def jungle_tree_in(t, x, y, z, h):
    for i in range(h):
        t.set(x, y + i, z, st("jungle_log", axis="y"))
    for a in range(-3, 4):
        for c in range(-3, 4):
            for b in range(-1, 3):
                if a * a + c * c + (b * 1.6) ** 2 <= 10 + t.rng.random() * 3:
                    t.setk(x + a, y + h - 1 + b, z + c, LEAF)
    for _ in range(10):
        a, c = t.rng.randint(-3, 3), t.rng.randint(-3, 3)
        face = "north" if c > 0 else "south"
        for i in range(t.rng.randint(1, 5)):
            if (x + a, y + h - 2 - i, z + c) in t.blk:
                break
            t.set(x + a, y + h - 2 - i, z + c, st("vine", **{face: "true"}))


# ============================================================ ruines
def lost_temple(seed):
    """Overwoekerde azteken trappenpiramide met tempel bovenop en een verborgen kamer."""
    t = Tpl(seed)
    rng = t.rng
    C = 16
    tiers = [16, 14, 12, 10, 8, 6]
    for x in range(0, 33):
        for z in range(0, 33):
            t.set(x, 0, z, rng.choice(["stone_bricks", "mossy_stone_bricks", "cobblestone", "mossy_cobblestone"]))
    for i, w in enumerate(tiers):
        for y in range(3 * i + 1, 3 * i + 4):
            for x in range(C - w, C + w + 1):
                for z in range(C - w, C + w + 1):
                    edge = max(abs(x - C), abs(z - C)) == w
                    if edge and y == 3 * i + 2 and (x + z) % 4 == 0:
                        t.set(x, y, z, rng.choice(["chiseled_stone_bricks", "chiseled_tuff_bricks"]))
                    elif edge or y == 3 * i + 3 or rng.random() < 0.3:
                        t.set(x, y, z, t.stone())
                    else:
                        t.set(x, y, z, "stone")
    top = 3 * len(tiers) + 1
    # trap aan de zuidkant
    for y in range(1, top):
        z = C + 17 - y
        for x in range(C - 2, C + 3):
            t.set(x, y, z, st("stone_brick_stairs", facing="north", half="bottom"))
            for yy in range(1, y):
                t.set(x, yy, z, t.stone())
            t.blk.pop((x, y + 1, z), None)
            t.blk.pop((x, y + 2, z), None)
        for x in (C - 3, C + 3):
            t.set(x, y, z, t.stone())
            t.set(x, y + 1, z, "mossy_stone_brick_wall")
    # slangenkoppen onderaan de trap
    for x in (C - 3, C + 3):
        t.set(x, 1, C + 17, "chiseled_stone_bricks")
        t.set(x, 2, C + 17, "chiseled_stone_bricks")
        t.set(x, 2, C + 18, st("mossy_stone_brick_stairs", facing="north", half="top"))
        t.set(x, 1, C + 18, "green_terracotta")
    # tempel bovenop
    for x in range(C - 4, C + 5):
        for z in range(C - 4, C + 5):
            edge = max(abs(x - C), abs(z - C)) == 4
            for y in range(top, top + 4):
                if edge:
                    t.set(x, y, z, "tuff_bricks" if y < top + 3 else "chiseled_tuff_bricks")
            t.set(x, top + 4, z, st("tuff_brick_slab", type="bottom") if not edge else "polished_tuff")
    for x in range(C - 1, C + 2):
        for y in range(top, top + 3):
            t.blk.pop((x, y, C + 4), None)
    t.set(C, top, C - 2, "chiseled_tuff")
    t.set(C, top + 1, C - 2, "gilded_blackstone")
    t.set(C - 2, top, C - 3, st("decorated_pot", facing="south"))
    t.set(C + 2, top, C - 3, st("decorated_pot", facing="south"))
    t.chest(C, top, C - 3, "south", "jungle_temple")
    for x, z in ((C - 4, C + 6), (C + 4, C + 6)):
        t.set(x, top, z, "chiseled_stone_bricks")
        t.set(x, top + 1, z, st("campfire", lit="false"))
    # verborgen kamer onderin met gang vanaf het oosten
    for x in range(C - 3, C + 4):
        for z in range(C - 3, C + 4):
            for y in range(2, 6):
                t.blk.pop((x, y, z), None)
            t.set(x, 1, z, "polished_tuff")
    for x in range(C + 4, C + 17):
        for y in (2, 3):
            t.blk.pop((x, y, C), None)
    t.chest(C, 2, C - 3, "south", "buried_treasure")
    t.set(C - 3, 2, C, st("skeleton_skull", rotation=4))
    t.set(C + 3, 5, C + 3, "cobweb")
    t.set(C - 3, 5, C - 3, "cobweb")
    for x, z in ((C - 2, C + 2), (C + 2, C - 2)):
        t.set(x, 2, z, st("decorated_pot", facing="north"))
    # overwoekering
    t.overgrow(0.35)
    t.vines_on(0.18, 7)
    jungle_tree_in(t, C - 11, 9, C - 11, 6)
    jungle_tree_in(t, C + 12, 4, C + 9, 7)
    return t


def plaza(seed):
    """Verzonken plein met (gebroken) zuilen, altaar en een boom die door de ruine groeit."""
    t = Tpl(seed)
    rng = t.rng
    C = 12
    for x in range(0, 25):
        for z in range(0, 25):
            d = max(abs(x - C), abs(z - C))
            r = rng.random()
            t.set(x, 0, z, "grass_block" if r < 0.12 else "moss_block" if r < 0.2 else
                  rng.choice(["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "tuff_bricks", "polished_tuff"]))
            if d == 12:
                t.set(x, 1, z, t.stone())
    for i in range(10):
        a = i * math.tau / 10
        x, z = C + round(9 * math.cos(a)), C + round(9 * math.sin(a))
        broken = rng.random() < 0.55
        h = rng.randint(2, 4) if broken else 6
        column(t, x, 1, z, h, broken)
    # omgevallen zuil
    fx, fz = C - 6, C + 2
    for i in range(5):
        t.set(fx + i, 1, fz, st("tuff_bricks"))
    # altaar
    for x in range(C - 2, C + 3):
        for z in range(C - 2, C + 3):
            t.set(x, 1, z, "polished_tuff")
            if max(abs(x - C), abs(z - C)) <= 1:
                t.set(x, 2, z, "chiseled_tuff_bricks")
    t.set(C, 3, C, "chiseled_tuff")
    t.set(C, 4, C, st("candle", candles=3, lit="false"))
    t.set(C + 1, 3, C, st("decorated_pot", facing="south"))
    for dx, dz, f in ((0, -3, "south"), (0, 3, "north"), (-3, 0, "east"), (3, 0, "west")):
        t.set(C + dx, 1, C + dz, st("tuff_brick_stairs", facing=f, half="bottom"))
    # stele met beeld
    tiki(t, C, 1, C - 6, "south")
    jungle_tree_in(t, C + 5, 1, C + 5, rng.randint(7, 10))
    t.overgrow(0.3)
    t.vines_on(0.2, 5)
    return t


def idol_head(seed):
    """Reusachtig half begraven stenen hoofd (olmeken/tiki)."""
    t = Tpl(seed)
    rng = t.rng
    W, H, D = 11, 12, 9
    cx, cz = 5, 4
    for x in range(W):
        for z in range(D):
            for y in range(H):
                ex = ((x - cx) / 5.5) ** 2 + ((y - 6) / 6.2) ** 2 + ((z - cz) / 4.6) ** 2
                if ex <= 1:
                    t.set(x, y, z, rng.choice(["tuff", "polished_tuff", "tuff", "mossy_cobblestone", "andesite"]))
    front = 0
    # gezicht aan de voorkant (z klein)
    for x in (3, 4, 6, 7):
        t.set(x, 7, front, "black_terracotta" if x in (3, 7) else "polished_tuff")
    for x in (3, 7):
        t.set(x, 7, front, "black_terracotta")
        t.set(x, 8, front, st("tuff_brick_stairs", facing="north", half="top"))
    t.set(5, 6, front, "chiseled_tuff")
    t.set(5, 5, front - 1, st("tuff_brick_stairs", facing="south", half="bottom"))
    for x in range(3, 8):
        t.set(x, 3, front, "red_terracotta" if 4 <= x <= 6 else "polished_tuff")
    for x in range(1, 10):
        t.set(x, 10, front + 1, "chiseled_tuff_bricks")
    t.overgrow(0.45)
    t.vines_on(0.25, 5)
    return t


def shrine(seed):
    t = Tpl(seed)
    rng = t.rng
    for x in range(0, 9):
        for z in range(0, 9):
            t.set(x, 0, z, t.stone())
            if 1 <= x <= 7 and 1 <= z <= 7:
                t.set(x, 1, z, t.stone())
    for x in range(3, 6):
        t.set(x, 1, 8, st("stone_brick_stairs", facing="north", half="bottom"))
    tiki(t, 4, 2, 2, "south")
    if rng.random() < 0.7:
        tiki(t, 1, 2, 2, "south")
    if rng.random() < 0.7:
        tiki(t, 7, 2, 2, "south")
    t.set(4, 2, 5, st("campfire", lit="false"))
    t.set(2, 2, 6, st("decorated_pot", facing="south"))
    t.set(6, 2, 6, st("skeleton_skull", rotation=rng.choice([0, 2, 14])))
    t.set(6, 2, 4, st("candle", candles=2, lit="false"))
    t.overgrow(0.4)
    t.vines_on(0.15, 3)
    return t


def abandoned_tiki_bar(seed):
    t = Tpl(seed)
    rng = t.rng
    for x in range(0, 13):
        for z in range(0, 11):
            if rng.random() < 0.85:
                t.set(x, 0, z, "bamboo_planks" if 0 < x < 12 and 0 < z < 10 else st("stripped_jungle_wood", axis="y"))
    for x, z in ((0, 0), (12, 0), (0, 10), (12, 10), (6, 0), (6, 10)):
        h = rng.randint(2, 4)
        for y in range(1, h + 1):
            t.set(x, y, z, st("bamboo_block", axis="y"))
    # half ingestort rieten dak
    for k in range(0, 5):
        for x in range(-1 + k, 14 - k):
            for z in range(-1 + k, 12 - k):
                ring = x in (-1 + k, 13 - k) or z in (-1 + k, 11 - k)
                if ring and rng.random() < 0.6 and not (x > 6 and z < 5):
                    t.set(x, 5 + k, z, st("bamboo_mosaic_stairs", facing="east" if x == -1 + k else "west" if x == 13 - k
                                          else "south" if z == -1 + k else "north", half="bottom"))
                elif k == 0 and not ring and rng.random() < 0.5 and not (x > 6 and z < 5):
                    t.set(x, 5, z, "hay_block")
    # ingestort stuk op de vloer
    for x in range(7, 12):
        for z in range(1, 5):
            if rng.random() < 0.6:
                t.set(x, 1, z, rng.choice(["hay_block", st("bamboo_mosaic_slab", type="bottom")]))
    for z in range(2, 9):
        if rng.random() < 0.8:
            t.set(8, 1, z, st("stripped_bamboo_block", axis="y"))
            if rng.random() < 0.6:
                t.set(8, 2, z, st("bamboo_mosaic_slab", type="bottom"))
    for z in (3, 5, 7):
        if rng.random() < 0.7:
            t.set(6, 1, z, "bamboo_fence")
    t.set(11, 1, 8, st("barrel", facing="up"))
    t.set(11, 1, 6, st("barrel", facing="west"))
    t.chest(11, 1, 7, "west", "shipwreck_supply")
    t.set(10, 1, 9, st("decorated_pot", facing="north"))
    for x, z in ((2, 2), (4, 8), (10, 3), (3, 6)):
        t.set(x, 4, z, "cobweb")
    t.sign(6, 4, 1, st("bamboo_hanging_sign", rotation=8, attached="false"), ["", "TIKI BAR", "~ gesloten ~", ""])
    for x in (-2, 14):
        tiki(t, x, 0, 5, "west" if x > 0 else "east")
    t.vines_on(0.25, 3)
    return t


def collapsed_fales(seed):
    t = Tpl(seed)
    rng = t.rng
    spots = [(5, 5), (19, 6), (11, 19)]
    for fx, fz in spots:
        for x in range(fx - 4, fx + 5):
            for z in range(fz - 3, fz + 4):
                edge = x in (fx - 4, fx + 4) or z in (fz - 3, fz + 3)
                t.set(x, 0, z, rng.choice(["cobblestone", "mossy_cobblestone"]) if edge else
                      rng.choice(["packed_mud", "coarse_dirt", "moss_block"]))
        for x, z in ((fx - 3, fz - 2), (fx + 3, fz - 2), (fx - 3, fz + 2), (fx + 3, fz + 2), (fx, fz - 2), (fx, fz + 2)):
            for y in range(1, rng.randint(1, 4) + 1):
                t.set(x, y, z, st("stripped_jungle_log", axis="y"))
        for x in range(fx - 4, fx + 5):
            for z in range(fz - 3, fz + 4):
                if rng.random() < 0.35:
                    t.set(x, rng.randint(1, 2), z, rng.choice(["hay_block", st("bamboo_mosaic_slab", type="bottom")]))
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if 1.4 < math.hypot(dx, dz) < 2.6:
                t.set(12 + dx, 1, 12 + dz, st("mossy_cobblestone_slab", type="bottom"))
    t.set(12, 1, 12, st("campfire", lit="false"))
    for i in range(6):
        t.set(16 + i, 1, 16, st("stripped_jungle_log", axis="x"))
    tiki(t, 3, 0, 14, "east")
    t.chest(5, 1, 6, "south", "village/village_fisher")
    t.overgrow(0.3)
    return t


def aqueduct(seed):
    t = Tpl(seed)
    rng = t.rng
    L = 29
    for x in range(L):
        broken = 17 <= x <= 22
        pier = x % 7 in (0, 1)
        for z in (0, 1, 2):
            if pier:
                for y in range(0, 10):
                    t.set(x, y, z, t.stone())
            elif not broken:
                k = x % 7
                arch_y = 6 + (1 if k in (2, 6) else 2 if k in (3, 5) else 3) - 1
                for y in range(arch_y, 10):
                    t.set(x, y, z, t.stone())
                t.set(x, arch_y - 1, z, st("stone_brick_stairs", facing="west" if k < 4 else "east", half="top"))
            if not broken:
                t.set(x, 10, z, "mossy_stone_brick_wall" if z != 1 else t.stone())
        if broken and rng.random() < 0.5:
            t.set(x, rng.randint(0, 1), rng.randint(0, 2), t.stone())
    t.overgrow(0.4)
    t.vines_on(0.25, 7)
    return t


def sunken_ruins(seed):
    t = Tpl(seed)
    rng = t.rng
    corals = ["tube", "brain", "bubble", "fire", "horn"]
    for x in range(0, 17):
        for z in range(0, 17):
            if rng.random() < 0.55:
                t.set(x, 0, z, rng.choice(["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "sand", "gravel"]))
    for x in range(1, 16):
        for z in (1, 15):
            for y in range(1, rng.randint(1, 5)):
                t.set(x, y, z, t.stone())
    for z in range(1, 16):
        for x in (1, 15):
            for y in range(1, rng.randint(1, 5)):
                t.set(x, y, z, t.stone())
    for x, z in ((5, 5), (11, 5), (5, 11), (11, 11)):
        column(t, x, 1, z, rng.randint(2, 6), rng.random() < 0.6)
    t.chest(8, 1, 8, "south", "underwater_ruin_big", waterlogged=True)
    tops = [(x, y, z) for (x, y, z) in list(t.blk) if (x, y + 1, z) not in t.blk and "chest" not in t.blk[(x, y, z)]]
    for x, y, z in tops:
        r = rng.random()
        if r < 0.25:
            t.set(x, y + 1, z, st(f"{rng.choice(corals)}_coral", waterlogged="true"))
        elif r < 0.4:
            t.set(x, y + 1, z, st(f"{rng.choice(corals)}_coral_fan", waterlogged="true"))
        elif r < 0.5:
            t.set(x, y + 1, z, st("sea_pickle", pickles=rng.randint(1, 4), waterlogged="true"))
        elif r < 0.6:
            t.set(x, y, z, f"{rng.choice(corals)}_coral_block")
    return t


RUINS = {
    # naam: (bouwfunctie, aantal varianten)
    "lost_temple": (lost_temple, 2),
    "plaza": (plaza, 3),
    "idol_head": (idol_head, 2),
    "shrine": (shrine, 3),
    "abandoned_tiki_bar": (abandoned_tiki_bar, 2),
    "collapsed_fales": (collapsed_fales, 2),
    "aqueduct": (aqueduct, 2),
    "sunken_ruins": (sunken_ruins, 3),
}
