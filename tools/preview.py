"""Maakt een isometrisch voorbeeldplaatje van een gegenereerde wereld (alleen voor controle)."""
import pathlib

from PIL import Image, ImageDraw

COLORS = [
    ("water", (40, 170, 200)), ("lava", (255, 110, 20)), ("magma", (200, 70, 20)),
    ("light", None), ("cave_vines", (240, 170, 60)), ("glass", (200, 230, 240)),
    ("grass_block", (95, 175, 60)), ("short_grass", (90, 170, 55)), ("fern", (70, 150, 50)),
    ("tall_grass", (90, 170, 55)), ("leaves", (40, 125, 35)), ("vine", (50, 120, 40)),
    ("bamboo_block", (150, 170, 60)), ("bamboo_planks", (215, 195, 95)), ("bamboo_mosaic", (205, 185, 85)),
    ("bamboo", (120, 170, 50)), ("hay", (210, 175, 60)), ("jungle_log", (110, 85, 45)),
    ("jungle_wood", (110, 85, 45)), ("stripped_jungle", (175, 125, 85)), ("cocoa", (150, 90, 40)),
    ("sand", (225, 210, 150)), ("sandstone", (215, 200, 140)), ("gravel", (140, 135, 130)),
    ("clay", (160, 165, 180)), ("dirt_path", (150, 120, 70)), ("coarse_dirt", (120, 85, 60)),
    ("podzol", (95, 65, 30)), ("moss", (90, 130, 50)), ("dirt", (130, 95, 65)),
    ("basalt", (75, 75, 80)), ("blackstone", (45, 40, 45)), ("tuff", (110, 110, 100)),
    ("obsidian", (25, 15, 40)), ("mossy", (100, 120, 90)), ("andesite", (135, 135, 135)),
    ("cobblestone", (120, 120, 120)), ("stone", (125, 125, 125)), ("coral", (230, 90, 160)),
    ("sea_pickle", (120, 160, 60)), ("kelp", (60, 120, 40)), ("seagrass", (60, 140, 60)),
    ("spruce", (110, 80, 50)), ("birch", (215, 205, 160)), ("oak", (160, 130, 80)),
    ("wool", None), ("carpet", None), ("concrete", None), ("terracotta", (180, 90, 60)),
    ("lily_pad", (40, 140, 40)), ("sugar_cane", (140, 190, 90)), ("melon", (110, 160, 40)),
    ("torch", (255, 220, 120)), ("lantern", (255, 200, 100)), ("campfire", (255, 150, 60)),
    ("barrel", (140, 100, 60)), ("fence", (190, 170, 90)),
]
DYES = {"white": (235, 235, 235), "red": (200, 50, 45), "yellow": (240, 210, 60), "cyan": (40, 150, 160),
        "lime": (120, 200, 40), "orange": (240, 130, 30), "magenta": (190, 70, 180), "light_blue": (90, 170, 220),
        "pink": (240, 150, 170), "blue": (50, 70, 170)}


def color(state):
    name = state.split(":")[1].split("[")[0]
    for key, col in COLORS:
        if key in name:
            if col is None:
                if key == "light":
                    return None
                for dye, c in DYES.items():
                    if name.startswith(dye):
                        return c
                return (200, 200, 200)
            return col
    for dye, c in DYES.items():
        if name.startswith(dye):
            return c
    return (200, 150, 200)


def render(w, planner, path, scale=4, region=None, ymax=999):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    blk = {k: v for k, v in w.blk.items() if k[1] <= ymax}
    s = scale
    S = w.S
    width = (2 * S + 4) * s * 2
    height = (S + 80) * s * 4
    img = Image.new("RGB", (width, height), (150, 200, 235))
    d = ImageDraw.Draw(img)
    ox, oy = S * s * 2 + 2 * s, (S + 70) * s * 2

    def visible(x, y, z):
        return any((x + a, y + b, z + c) not in blk or "water" in blk[(x + a, y + b, z + c)] and "water" not in blk[(x, y, z)]
                   for a, b, c in ((0, 1, 0), (-1, 0, 0), (0, 0, 1)))

    items = [(x, y, z, st) for (x, y, z), st in blk.items() if visible(x, y, z)
             and (region is None or (region[0] <= x <= region[2] and region[1] <= z <= region[3]))]
    # camera in het zuidwesten: eerst ver weg (noordoost), dan dichtbij; per kolom van onder naar boven
    items.sort(key=lambda i: (i[2] - i[0], i[1]))
    for x, y, z, stt in items:
        c = color(stt)
        if c is None:
            continue
        # isometrisch: kijk vanuit het zuidwesten
        px = ox + (x + z) * s * 2
        py = oy + (z - x) * s - y * s * 2
        top = [(px, py), (px + 2 * s, py - s), (px + 4 * s, py), (px + 2 * s, py + s)]
        left = [(px, py), (px + 2 * s, py + s), (px + 2 * s, py + 3 * s), (px, py + 2 * s)]
        right = [(px + 2 * s, py + s), (px + 4 * s, py), (px + 4 * s, py + 2 * s), (px + 2 * s, py + 3 * s)]
        d.polygon(top, fill=c)
        d.polygon(left, fill=tuple(int(v * 0.75) for v in c))
        d.polygon(right, fill=tuple(int(v * 0.6) for v in c))
    xs = [ox + (i[0] + i[2]) * s * 2 for i in items]
    img = img.crop((max(0, min(xs) - 10), max(0, min(oy + ((i[2] - i[0]) * s) - i[1] * s * 2 for i in items) - 10), width,
                    min(height, max(oy + ((i[2] - i[0]) * s) - i[1] * s * 2 for i in items) + 6 * s)))
    img = img.crop((0, 0, min(img.width, max(xs) - max(0, min(xs) - 10) + 4 * s + 10), img.height))
    img.save(path)
