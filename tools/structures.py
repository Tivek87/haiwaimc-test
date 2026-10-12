"""Gebouwen en objecten: tiki bar, steiger, hutten, vuurplaats, strandspullen, paden."""
import math

from world import SEA, st

CARPETS = ["red", "orange", "yellow", "lime", "cyan", "magenta", "light_blue", "pink"]
UMBRELLA_COLORS = [("red", "white"), ("yellow", "white"), ("cyan", "white"), ("lime", "white"),
                   ("orange", "white"), ("magenta", "white"), ("light_blue", "white"), ("pink", "white")]

LEAF = st("jungle_leaves", persistent="true")


def drink(name, color, rgb, effect, duration, amp=0):
    return (f'{{id:"minecraft:potion",count:1,components:{{"minecraft:custom_name":\'{{"text":"{name}",'
            f'"color":"{color}","italic":false}}\',"minecraft:potion_contents":{{custom_color:{rgb},'
            f'custom_effects:[{{id:"minecraft:{effect}",amplifier:{amp},duration:{duration}}}]}}}}}}')


DRINKS = [
    drink("Pina Colada", "yellow", 16768256, "regeneration", 200),
    drink("Blue Hawaii", "aqua", 2003199, "water_breathing", 3600),
    drink("Mai Tai", "gold", 16747520, "speed", 2400),
    drink("Lava Flow", "red", 15079755, "fire_resistance", 3600),
    drink("Coconut Kiss", "white", 15790320, "jump_boost", 2400),
    drink("Lagoon Punch", "light_purple", 14315734, "night_vision", 3600),
]


def trade(buy, sell, buy_count=1, sell_count=1):
    b = buy if buy.startswith("{") else f'{{id:"minecraft:{buy}",count:{buy_count}}}'
    s = sell if sell.startswith("{") else f'{{id:"minecraft:{sell}",count:{sell_count}}}'
    return f"{{buy:{b},sell:{s},maxUses:9999,rewardExp:0b}}"


def villager(w, x, y, z, name, color, yaw, profession, vtype="jungle", trades=(), extra=""):
    offers = f",Offers:{{Recipes:[{','.join(trades)}]}}" if trades else ""
    w.summon("villager", x, y, z,
             f"CustomName:'{{\"text\":\"{name}\",\"color\":\"{color}\"}}',CustomNameVisible:1b,NoAI:1b,"
             f"Invulnerable:1b,PersistenceRequired:1b,Silent:1b,Rotation:[{yaw}f,0f],"
             f'VillagerData:{{type:"minecraft:{vtype}",profession:"minecraft:{profession}",level:5}},Xp:250'
             f"{offers}{extra}")


def item_display(w, x, y, z, item, scale=0.45, yaw=0):
    q = yaw_quat(yaw)
    w.summon("item_display", x, y, z,
             f"item:{item},item_display:\"fixed\",transformation:{{left_rotation:{q},"
             f"right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}}")


def yaw_quat(deg):
    r = math.radians(deg) / 2
    return f"[0f,{math.sin(r):.4f}f,0f,{math.cos(r):.4f}f]"


def tilt_quat(axis, deg):
    r = math.radians(deg) / 2
    s = f"{math.sin(r):.4f}f"
    c = f"{math.cos(r):.4f}f"
    return {"x": f"[{s},0f,0f,{c}]", "z": f"[0f,0f,{s},{c}]"}[axis]


def surfboard(w, x, y, z, color, stripe, tilt):
    for blk, sx, sz, ty in ((f"{color}_concrete", 0.7, 0.1, 0.0), (f"{stripe}_concrete", 0.16, 0.12, 0.0)):
        off = (0.7 - sx) / 2
        w.summon("block_display", x + off, y, z,
                 f'block_state:{{Name:"minecraft:{blk}"}},transformation:{{left_rotation:{tilt_quat("x", tilt)},'
                 f"right_rotation:[0f,0f,0f,1f],translation:[0f,{ty}f,0f],scale:[{sx}f,2.4f,{sz}f]}}")


def hip_roof(w, x0, x1, z0, z1, y, stair="bamboo_mosaic_stairs", fill="hay_block"):
    """Schuin rieten dak: ring van trappen per laag, hooi als plafond en nok."""
    k = 0
    while x0 + k <= x1 - k and z0 + k <= z1 - k:
        a0, a1, b0, b1 = x0 + k, x1 - k, z0 + k, z1 - k
        yy = y + k
        if a1 - a0 < 2 or b1 - b0 < 2:
            for x in range(a0, a1 + 1):
                for z in range(b0, b1 + 1):
                    w.set(x, yy, z, fill)
            if a1 - a0 >= b1 - b0:
                for x in range(a0, a1 + 1):
                    w.set(x, yy + 1, (b0 + b1) // 2, st("bamboo_block", axis="x"))
            else:
                for z in range(b0, b1 + 1):
                    w.set((a0 + a1) // 2, yy + 1, z, st("bamboo_block", axis="z"))
            return yy + 1
        for x in range(a0, a1 + 1):
            for z in range(b0, b1 + 1):
                if x in (a0, a1) or z in (b0, b1):
                    f = "east" if x == a0 else "west" if x == a1 else "south" if z == b0 else "north"
                    w.set(x, yy, z, st(stair, facing=f, half="bottom"))
                elif k == 0:
                    w.set(x, yy, z, fill)
        k += 1
    return y + k


def glow_fringe(w, x0, x1, z0, z1, y, rng):
    """Hangende glow berries onder de dakrand."""
    i = 0
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z in (z0, z1):
                i += 1
                if i % 2:
                    continue
                if rng.random() < 0.5:
                    w.set(x, y, z, st("cave_vines_plant", berries="true"))
                    w.set(x, y - 1, z, st("cave_vines", age=25, berries="true"))
                else:
                    w.set(x, y, z, st("cave_vines", age=25, berries="true"))


def tiki_torch(w, x, g, z):
    """Bamboe fakkel op grondhoogte g (bovenkant grond)."""
    w.set(x, g + 1, z, "bamboo_fence")
    w.set(x, g + 2, z, "bamboo_fence")
    w.set(x, g + 3, z, "torch")


def totem(w, x, g, z, facing="west"):
    w.set(x, g + 1, z, st("stripped_jungle_log", axis="y"))
    w.set(x, g + 2, z, st("carved_pumpkin", facing=facing))
    w.set(x, g + 3, z, st("jungle_wood", axis="y"))
    w.set(x, g + 4, z, st("jack_o_lantern", facing=facing))
    w.set(x, g + 5, z, "bamboo_fence")
    w.set(x, g + 6, z, "torch")


def sign_text(lines, colors=None):
    colors = colors or ["gold"] * 4
    msgs = ",".join(f"'{{\"text\":\"{t}\",\"color\":\"{c}\",\"bold\":true}}'" if t else "'\"\"'"
                    for t, c in zip(lines, colors))
    side = f"{{messages:[{msgs}],has_glowing_text:1b}}"
    return f"{{front_text:{side},back_text:{side}}}"


def text_display(w, x, y, z, text, color, scale=2.0):
    w.summon("text_display", x, y, z,
             f"text:'{{\"text\":\"{text}\",\"color\":\"{color}\",\"bold\":true}}',billboard:\"center\","
             f"background:1275068416,shadow:1b,transformation:{{left_rotation:[0f,0f,0f,1f],"
             f"right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}}")


BAR_TRADES = [trade("emerald", d) for d in DRINKS[:4]] + [
    trade("emerald", "melon_slice", 1, 6),
    trade("emerald", "cookie", 1, 6),
    trade("cocoa_beans", "emerald", 8, 1),
]
FOOD_TRADES = [
    trade("emerald", "cooked_cod", 1, 4),
    trade("emerald", "cooked_salmon", 1, 3),
    trade("emerald", "baked_potato", 1, 4),
    trade("emerald", "pumpkin_pie", 1, 2),
    trade("emerald", "cake", 3, 1),
    trade("emerald", "golden_carrot", 2, 3),
]
DRINK2_TRADES = [trade("emerald", d) for d in DRINKS[3:]] + [trade("emerald", "honey_bottle", 1, 2)]
FISH_TRADES = [
    trade("emerald", "tropical_fish_bucket", 2, 1),
    trade("emerald", "fishing_rod", 2, 1),
    trade("cod", "emerald", 6, 1),
    trade("salmon", "emerald", 5, 1),
    trade("emerald", "nautilus_shell", 6, 1),
]


class Planner:
    def __init__(self, w, t):
        self.w, self.t, self.rng = w, t, w.rng
        self.builds = []
        self.tp = None
        self.paths = []
        self.bar = None
        self.huts = []
        self.palm_spots = []  # (x, z, lean) palmen die altijd geplant worden

    # ------------------------------------------------------------- hulpjes
    def land_x(self, z):
        w, t = self.w, self.t
        for x in range(t.shore_x[z], w.x1 + 1):
            if t.kind[(x, z)] != "beach":
                return x
        return w.x1

    def ground(self, x, z):
        return self.t.h(x, z)

    def plan(self):
        n = self.w.n
        if n >= 4:
            self.plan_big_bar()
        else:
            self.plan_small_bar()
        if n >= 3:
            self.plan_dock()
        if n >= 2:
            self.plan_firepit()
        if n >= 4:
            self.plan_huts()
        if n >= 5:
            self.plan_lifeguard()
            self.plan_volleyball()
        if n >= 2:
            self.plan_sandcastles()
        self.plan_umbrellas()
        if n >= 3:
            self.plan_paths()
        if n >= 5:
            self.plan_treasure()
        if self.t.volcano:
            self.plan_volcano_smoke()
        if self.t.lagoon:
            self.plan_waterfall()

    def build(self):
        for fn in self.builds:
            fn()

    # ---------------------------------------------------------- grote bar
    def plan_big_bar(self):
        w, t = self.w, self.t
        bz = 0
        bx = max(t.shore_x[z] for z in range(bz - 12, bz + 13)) + 7
        bx = min(bx, w.x1 - 17)
        self.bar = (bx, bz)
        t.flatten(bx - 6, bz - 13, bx + 17, bz + 13, -1, "beach")
        for x in range(bx + 15, bx + 19):
            for z in range(bz - 13, bz + 14):
                if (x, z) in t.H and t.kind[(x, z)] == "land":
                    t.H[(x, z)] = min(t.H[(x, z)], 0)
        w.reserve(bx - 6, bz - 13, bx + 17, bz + 13)
        self.tp = (bx - 7.5, 0, bz + 0.5, -90)
        self.palm_spots += [(bx - 8, bz - 15, (-1, -1)), (bx - 9, bz + 14, (-1, 1)), (bx + 3, bz - 15, (0, -1)),
                            (bx + 6, bz + 15, (0, 1))]
        self.exits = [(bx + 4, bz - 11), (bx + 4, bz + 11)]
        self.builds.append(lambda: self.build_big_bar(bx, bz))

    def build_big_bar(self, bx, bz):
        w, rng = self.w, self.rng

        def P(a, y, b, s):
            w.set(bx + a, y, bz + b, s)

        # vlonder
        for a in range(0, 15):
            for b in range(-10, 11):
                if a in (0, 14) or b in (-10, 10):
                    s = st("stripped_jungle_wood", axis="y")
                elif 10 <= a <= 13 and -5 <= b <= 5:
                    s = "bamboo_mosaic"
                else:
                    s = "bamboo_planks"
                P(a, 0, b, s)
        # trap aan de voorkant
        for b in range(-2, 3):
            P(-1, 0, b, st("bamboo_stairs", facing="east", half="bottom"))
        # reling
        for b in range(-10, 11):
            if abs(b) > 2:
                P(0, 1, b, "bamboo_fence")
        for a in range(0, 14):
            if a not in (4, 5):
                P(a, 1, -10, "bamboo_fence")
                P(a, 1, 10, "bamboo_fence")
        # palen
        for a, b in ((1, -9), (1, -3), (1, 3), (1, 9), (7, -9), (7, 9)):
            for y in range(1, 5):
                P(a, y, b, st("bamboo_block", axis="y"))
        # achterwand
        for b in range(-9, 10):
            for y in range(1, 5):
                col = b % 3 == 0
                P(14, y, b, st("stripped_bamboo_block", axis="y") if col else
                  ("bamboo_mosaic" if y == 4 else "bamboo_planks"))
        # dak
        hip_roof(w, bx - 1, bx + 16, bz - 12, bz + 12, 5)
        glow_fringe(w, bx - 1, bx + 16, bz - 12, bz + 12, 4, rng)
        for a, b in ((-1, -12), (-1, 12), (16, -12), (16, 12)):
            P(a, 4, b, st("lantern", hanging="true"))
        # toonbank (U-vorm)
        cells = [(9, b) for b in range(-6, 7)] + [(a, -6) for a in range(10, 14)] + [(a, 6) for a in range(10, 14)]
        for i, (a, b) in enumerate(cells):
            if (a, b) == (12, -6):
                P(a, 1, b, st("bamboo_fence_gate", facing="north"))
                continue
            P(a, 1, b, st("bamboo_block" if i % 2 else "stripped_bamboo_block", axis="y"))
            P(a, 2, b, st("bamboo_mosaic_slab", type="bottom"))
        # krukken
        for i, b in enumerate((-5, -3, -1, 1, 3, 5)):
            P(8, 1, b, "bamboo_fence")
            P(8, 2, b, f"{CARPETS[i % len(CARPETS)]}_carpet")
        # achterbar
        low = {-5: st("barrel", facing="west"), -4: st("barrel", facing="west"), -3: "bamboo_planks",
               -2: st("water_cauldron", level=3), -1: "bamboo_planks", 0: st("barrel", facing="west"),
               1: "bamboo_planks", 2: st("water_cauldron", level=3), 3: "bamboo_planks",
               4: st("barrel", facing="west"), 5: st("barrel", facing="west")}
        high = {-5: "brewing_stand", -4: "potted_fern", -3: st("decorated_pot", facing="west"),
                -1: st("orange_candle", candles=4, lit="true"), 0: "lantern",
                1: st("yellow_candle", candles=3, lit="true"), 3: st("decorated_pot", facing="west"),
                4: "potted_flowering_azalea_bush", 5: "brewing_stand"}
        for b, s in low.items():
            P(13, 1, b, s)
        for b, s in high.items():
            P(13, 2, b, s)
        # keuken
        P(10, 1, -9, st("barrel", facing="up"))
        P(11, 1, -9, st("campfire", lit="true", facing="south"))
        P(12, 1, -9, st("smoker", facing="south", lit="true"))
        P(13, 1, -9, "crafting_table")
        P(13, 1, -8, st("barrel", facing="west"))
        P(13, 1, -7, st("water_cauldron", level=3))
        P(10, 1, -7, "potted_bamboo")
        # podium
        for a in range(2, 7):
            for b in range(6, 10):
                P(a, 1, b, st("bamboo_mosaic_slab", type="bottom"))
        P(2, 2, 9, "note_block")
        P(6, 2, 9, "note_block")
        P(6, 3, 9, "jukebox")
        P(2, 3, 9, "jukebox")
        P(2, 1, 5, "potted_red_tulip")
        P(6, 1, 5, "potted_orange_tulip")
        # tafels met stoelen
        for a, b in ((3, -7), (6, -7), (3, -4), (6, -4), (3, 3), (6, 3)):
            P(a, 1, b, "bamboo_fence")
            P(a, 2, b, "bamboo_pressure_plate")
            P(a - 1, 1, b, st("bamboo_stairs", facing="west", half="bottom"))
            P(a + 1, 1, b, st("bamboo_stairs", facing="east", half="bottom"))
        # kroonluchters en bloemen aan het plafond
        for a, b in ((4, -6), (4, 4), (5, 0), (11, -3), (11, 3), (11, -8)):
            P(a, 4, b, st("chain", axis="y"))
            P(a, 3, b, st("lantern", hanging="true"))
        for a, b in ((3, -2), (6, 6), (2, -8), (9, 8), (12, 8), (7, 0)):
            P(a, 4, b, "spore_blossom")
        # plantenbakken in de hoeken
        for a, b, s in ((1, -1, "potted_bamboo"), (1, 1, "potted_bamboo"), (13, 8, "potted_jungle_sapling"),
                        (10, 9, "potted_flowering_azalea_bush"), (13, 9, "potted_fern")):
            P(a, 1, b, s)
        # naamborden onder de dakrand
        for b, lines, cols in ((-1, ["", "~ KAI'S ~", "", ""], ["gold"] * 4),
                               (0, ["", "TIKI BAR", "", ""], ["gold"] * 4),
                               (1, ["", "~ ALOHA ~", "", ""], ["green"] * 4)):
            w.setblock_late(bx, 4, bz + b, st("bamboo_hanging_sign", rotation=4, attached="false"),
                            sign_text(lines, cols))
        # totems en fakkels voor de ingang
        for b in (-5, 5):
            totem(w, bx - 4, -1, bz + b)
        for b in (-3, 3, -9, 9):
            tiki_torch(w, bx - 2, -1, bz + b)
        text_display(w, bx - 2.5, 6.6, bz + 0.5, "~ TIKI BAR ~", "gold", 2.4)
        text_display(w, bx - 2.5, 5.9, bz + 0.5, "Aloha & welkom!", "aqua", 1.2)
        # mensen en dieren
        villager(w, bx + 11.5, 1, bz + 0.5, "Kai de Tiki Barman", "gold", 90, "farmer", trades=BAR_TRADES)
        villager(w, bx + 11.5, 1, bz - 3.5, "Leilani (cocktails)", "light_purple", 90, "cleric", trades=DRINK2_TRADES)
        villager(w, bx + 11.5, 1, bz + 3.5, "Makoa de Kok", "yellow", 90, "butcher", trades=FOOD_TRADES)
        villager(w, bx + 3.5, 1.5, bz + 7.5, "Hula Danser Malia", "light_purple", 180, "nitwit", "savanna")
        villager(w, bx + 5.5, 1.5, bz + 7.5, "Hula Danser Nalu", "aqua", 180, "nitwit", "savanna")
        villager(w, bx + 4.5, 1.5, bz + 8.7, "Ukulele Keoni", "yellow", 180, "librarian", "jungle")
        for b, v in ((-6, 0), (6, 3)):
            w.summon("parrot", bx + 9.5, 2.5, bz + b + 0.5, f"Variant:{v},NoAI:1b,PersistenceRequired:1b,Rotation:[90f,0f]")
        for i, b in enumerate((-5, -1, 3)):
            item_display(w, bx + 9.5, 2.72, bz + b + 0.5, DRINKS[i], 0.45, 90)
        for i, (a, b) in enumerate(((3, -7), (6, -7), (3, -4), (6, -4), (3, 3), (6, 3))):
            item_display(w, bx + a + 0.5, 2.27, bz + b + 0.5, DRINKS[(i + 2) % len(DRINKS)], 0.4, i * 40)
        for i, b in enumerate((-4, -2, 0, 2, 4)):
            w.summon("glow_item_frame", bx + 13.5, 3.5, bz + b + 0.5,
                     f"Facing:4b,Fixed:1b,Invulnerable:1b,Item:{DRINKS[i % len(DRINKS)]}")
        w.summon("glow_item_frame", bx + 13.5, 3.5, bz - 8.5, 'Facing:4b,Fixed:1b,Invulnerable:1b,Item:{id:"minecraft:cooked_cod",count:1}')
        w.summon("item_display", bx + 11.5, 1.6, bz - 8.5,
                 'item:{id:"minecraft:cooked_salmon",count:1},item_display:"ground",transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.6f,0.6f,0.6f]}')

    # ---------------------------------------------------------- kleine bar
    def plan_small_bar(self):
        w, t = self.w, self.t
        bz = 0
        bx = max(t.shore_x[z] for z in range(bz - 5, bz + 6)) + 3
        bx = min(bx, w.x1 - 7)
        self.bar = (bx, bz)
        t.flatten(bx - 3, bz - 6, bx + 7, bz + 6, -1, "beach")
        w.reserve(bx - 4, bz - 6, bx + 8, bz + 6)
        self.tp = (bx - 2.5, 0, bz + 0.5, -90)
        self.palm_spots += [(bx - 3, bz - 7, (-1, -1)), (bx - 3, bz + 7, (-1, 1)), (bx + 6, bz - 7, (0, -1))]
        self.exits = [(bx + 3, bz - 6), (bx + 3, bz + 6)]
        self.builds.append(lambda: self.build_small_bar(bx, bz))

    def build_small_bar(self, bx, bz):
        w, rng = self.w, self.rng

        def P(a, y, b, s):
            w.set(bx + a, y, bz + b, s)

        for a in range(0, 7):
            for b in range(-4, 5):
                edge = a in (0, 6) or b in (-4, 4)
                P(a, 0, b, st("stripped_jungle_wood", axis="y") if edge else "bamboo_planks")
        for b in range(-1, 2):
            P(-1, 0, b, st("bamboo_stairs", facing="east", half="bottom"))
        for a, b in ((0, -4), (0, 4), (6, -4), (6, 4)):
            for y in range(1, 4):
                P(a, y, b, st("bamboo_block", axis="y"))
        for b in range(-3, 4):
            P(6, 1, b, st("barrel", facing="west") if b % 2 else "bamboo_planks")
            P(6, 2, b, "bamboo_planks")
            P(6, 3, b, "bamboo_mosaic")
        hip_roof(w, bx - 1, bx + 7, bz - 5, bz + 5, 4)
        glow_fringe(w, bx - 1, bx + 7, bz - 5, bz + 5, 3, rng)
        for b in range(-3, 4):
            P(3, 1, b, st("bamboo_block" if b % 2 else "stripped_bamboo_block", axis="y"))
            P(3, 2, b, st("bamboo_mosaic_slab", type="bottom"))
        P(4, 1, -3, st("bamboo_block", axis="y"))
        P(4, 2, -3, st("bamboo_mosaic_slab", type="bottom"))
        P(4, 1, 3, st("bamboo_fence_gate", facing="north"))
        for i, b in enumerate((-3, -1, 1, 3)):
            P(2, 1, b, "bamboo_fence")
            P(2, 2, b, f"{CARPETS[i]}_carpet")
        P(5, 1, -3, st("water_cauldron", level=3))
        P(5, 1, 3, "potted_flowering_azalea_bush")
        P(4, 3, 0, st("lantern", hanging="true"))
        P(1, 3, -2, "spore_blossom")
        P(1, 3, 2, "spore_blossom")
        for b in (-2, 2):
            tiki_torch(w, bx - 2, -1, bz + b)
        if w.n >= 2:
            for b in (-5, 5):
                totem(w, bx - 3, -1, bz + b)
        w.setblock_late(bx, 3, bz, st("bamboo_hanging_sign", rotation=4, attached="false"),
                        sign_text(["", "TIKI BAR", "~ Aloha ~", ""], ["gold", "gold", "green", "gold"]))
        text_display(w, bx - 1.5, 5.6, bz + 0.5, "~ TIKI BAR ~", "gold", 1.6)
        villager(w, bx + 4.5, 1, bz + 0.5, "Kai de Tiki Barman", "gold", 90, "farmer", trades=BAR_TRADES + FOOD_TRADES[:2])
        w.summon("parrot", bx + 3.5, 2.5, bz - 2.5, "Variant:0,NoAI:1b,PersistenceRequired:1b,Rotation:[90f,0f]")
        for i, b in enumerate((-3, 1)):
            item_display(w, bx + 3.5, 2.72, bz + b + 0.5, DRINKS[i], 0.45, 90)

    # ------------------------------------------------------------- steiger
    def plan_dock(self):
        w, t = self.w, self.t
        bx, bz = self.bar
        dz = bz + (15 if w.n >= 4 else 9)
        if dz + 3 > w.x1 - 2:
            return
        sx = t.shore_x[dz]
        length = max(8, min(24, round(0.2 * w.S)))
        ex = max(w.x0 + 4, sx - length)
        if sx - ex < 6:
            return
        w.reserve(ex - 4, dz - 3, sx + 2, dz + 3)
        self.builds.append(lambda: self.build_dock(ex, sx, dz))

    def build_dock(self, ex, sx, dz):
        w, t = self.w, self.t
        deck = SEA + 1
        for x in range(ex, sx + 2):
            for z in range(dz - 1, dz + 2):
                w.set(x, deck, z, "spruce_planks")
            for z in (dz - 1, dz + 1):
                if (x - ex) % 3 == 0:
                    for y in range(t.h(x, z) + 1, deck):
                        w.set(x, y, z, st("stripped_spruce_log", axis="y"))
                if x > ex + 4 and x < sx:
                    w.set(x, deck + 1, z, "spruce_fence")
            if x > ex + 4 and x < sx and (x - ex) % 6 == 0:
                for z in (dz - 1, dz + 1):
                    w.set(x, deck + 2, z, "spruce_fence")
                    w.set(x, deck + 3, z, "lantern")
        # platform aan het eind
        for x in range(ex - 4, ex + 1):
            for z in range(dz - 2, dz + 3):
                w.set(x, deck, z, "spruce_planks")
        for x in range(ex - 4, ex + 1):
            for z in (dz - 2, dz + 2):
                if x in (ex - 4, ex):
                    for y in range(t.h(x, z) + 1, deck):
                        w.set(x, y, z, st("stripped_spruce_log", axis="y"))
        for z in range(dz - 2, dz + 3):
            w.set(ex - 4, deck + 1, z, "spruce_fence")
        for x in range(ex - 4, ex + 1):
            w.set(x, deck + 1, dz - 2, "spruce_fence")
        for x, z in ((ex - 4, dz - 2), (ex - 4, dz + 2)):
            w.set(x, deck + 2, z, "spruce_fence")
            w.set(x, deck + 3, z, "lantern")
        w.set(ex - 3, deck + 1, dz - 1, st("spruce_stairs", facing="west"))
        w.set(ex - 3, deck + 1, dz, st("spruce_stairs", facing="west"))
        w.set(ex - 1, deck + 1, dz - 1, st("barrel", facing="up"))
        w.set(ex - 1, deck + 2, dz - 1, "potted_fern")
        villager(w, ex - 1.5, deck + 1, dz + 1.5, "Kimo de Visser", "aqua", 90, "fisherman", "jungle", FISH_TRADES)
        w.summon("boat", ex - 2.5, SEA + 0.6, dz + 4.0, 'Type:"jungle",Rotation:[90f,0f]')
        w.summon("boat", ex + 2.5, SEA + 0.6, dz + 3.2, 'Type:"bamboo",Rotation:[80f,0f]')

    # --------------------------------------------------------- vuurplaats
    def plan_firepit(self):
        w, t = self.w, self.t
        bx, bz = self.bar
        fz = bz - (19 if w.n >= 4 else 10)
        if fz - 5 < w.x0 + 1:
            return
        fx = (t.shore_x[fz] + self.land_x(fz)) // 2 + 1
        if w.is_reserved_area(fx - 5, fz - 5, fx + 5, fz + 5):
            return
        g = max(t.h(fx, fz), SEA + 1)
        t.flatten(fx - 5, fz - 5, fx + 5, fz + 5, g, "beach")
        w.reserve(fx - 6, fz - 6, fx + 6, fz + 6)
        self.firepit = (fx, fz)
        self.builds.append(lambda: self.build_firepit(fx, fz, g))

    def build_firepit(self, fx, fz, g):
        w = self.w
        w.set(fx, g + 1, fz, st("campfire", lit="true"))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                d = math.hypot(dx, dz)
                if 1.4 < d < 2.5:
                    w.set(fx + dx, g + 1, fz + dz, st("mossy_cobblestone_slab" if (dx + dz) % 2 else "cobblestone_slab", type="bottom"))
        for dz in (-1, 0, 1):
            w.set(fx - 4, g + 1, fz + dz, st("stripped_jungle_log", axis="z"))
            w.set(fx + 4, g + 1, fz + dz, st("stripped_jungle_log", axis="z"))
        for dx in (-1, 0, 1):
            w.set(fx + dx, g + 1, fz - 4, st("stripped_jungle_log", axis="x"))
        for dx in (-4, 4):
            tiki_torch(w, fx + dx, g, fz - 4)
        w.set(fx + 3, g + 1, fz + 3, st("barrel", facing="up"))
        w.set(fx + 3, g + 2, fz + 3, "lantern")
        villager(w, fx - 3.5, g + 1, fz + 0.5, "Pua (verhalenverteller)", "green", -90, "nitwit", "jungle")

    # ------------------------------------------------------------- hutten
    def plan_huts(self):
        w, t = self.w, self.t
        S = w.S
        want = min(4, w.n - 2)
        cands = [(zf, off) for zf in (-0.40, -0.30, 0.40, -0.20, 0.30, 0.45, -0.45) for off in (3, 6, 9, 12)]
        for zf, off in cands:
            if want <= 0:
                break
            hz = round(zf * S)
            if hz - 6 < w.x0 + 1 or hz + 6 > w.x1 - 1:
                continue
            hx = self.land_x(hz) + off
            if hx + 8 > w.x1 - 4:
                continue
            if w.is_reserved_area(hx - 3, hz - 5, hx + 8, hz + 5):
                continue
            cols = [(x, z) for x in range(hx - 2, hx + 8) for z in range(hz - 4, hz + 5)]
            if any(t.kind[c] not in ("land", "beach") for c in cols):
                continue
            hs = [t.h(*c) for c in cols]
            if max(hs) - min(hs) > 4:
                continue
            g = max(hs)
            t.flatten(hx - 2, hz - 4, hx + 7, hz + 4, g, "land")
            w.reserve(hx - 3, hz - 5, hx + 8, hz + 5)
            self.builds.append(lambda hx=hx, hz=hz, g=g: self.build_hut(hx, hz, g))
            self.huts.append((hx - 1, hz))
            want -= 1

    def build_hut(self, hx, hz, g):
        w, rng = self.w, self.rng
        F = g + 1

        def P(a, y, b, s):
            w.set(hx + a, y, hz + b, s)

        for a in range(0, 7):
            for b in range(-3, 4):
                P(a, F, b, "bamboo_planks" if 0 < a < 6 and abs(b) < 3 else st("stripped_bamboo_block", axis="y"))
        for b in range(-1, 2):
            P(-1, F, b, st("bamboo_stairs", facing="east", half="bottom"))
        for a in range(1, 6):
            for b in range(-2, 3):
                if a in (1, 5) or b in (-2, 2):
                    for y in range(F + 1, F + 4):
                        corner = a in (1, 5) and b in (-2, 2)
                        P(a, y, b, st("bamboo_block", axis="y") if corner else "bamboo_planks")
        # ramen en deur
        for b in (-2, 2):
            w.clear(hx + 3, F + 2, hz + b)
        w.clear(hx + 5, F + 2, hz)
        w.clear(hx + 1, F + 1, hz)
        w.clear(hx + 1, F + 2, hz)
        P(1, F + 1, 0, st("bamboo_door", facing="east", half="lower", hinge="left"))
        P(1, F + 2, 0, st("bamboo_door", facing="east", half="upper", hinge="left"))
        # puntdak
        for k in range(0, 5):
            y = F + 4 + k
            b = 4 - k
            for a in range(-1, 8):
                if b > 0:
                    P(a, y, -b, st("bamboo_mosaic_stairs", facing="south", half="bottom"))
                    P(a, y, b, st("bamboo_mosaic_stairs", facing="north", half="bottom"))
                else:
                    P(a, y, 0, "hay_block")
            for a in (1, 5):
                for bb in range(-(3 - k), 4 - k):
                    if k < 4 and abs(bb) < 4 - k:
                        P(a, y, bb, "bamboo_planks")
        # inrichting
        bed = rng.choice(["red_bed", "yellow_bed", "lime_bed", "light_blue_bed"])
        w.set(hx + 3, F + 1, hz - 1, st(bed, facing="east", part="foot"))
        w.set(hx + 4, F + 1, hz - 1, st(bed, facing="east", part="head"))
        P(4, F + 1, 1, st("barrel", facing="up"))
        P(4, F + 2, 1, "lantern")
        P(2, F + 1, 1, f"{rng.choice(CARPETS)}_carpet")
        P(2, F + 1, -1, "potted_fern")
        P(3, F + 1, 1, "crafting_table")
        for b in (-3, 3):
            P(0, F + 1, b, "bamboo_fence")
            P(0, F + 2, b, "bamboo_fence")
            P(0, F + 3, b, "lantern")

    # -------------------------------------------------------- strandwacht
    def plan_lifeguard(self):
        w, t = self.w, self.t
        bx, bz = self.bar
        tz = bz + round(0.38 * w.S)
        if tz + 4 > w.x1 - 1:
            return
        tx = t.shore_x[tz] + 2
        if w.is_reserved_area(tx - 2, tz - 2, tx + 4, tz + 4):
            return
        g = max(t.h(x, z) for x in range(tx, tx + 3) for z in range(tz, tz + 3))
        t.flatten(tx - 1, tz - 1, tx + 3, tz + 3, g, "beach")
        w.reserve(tx - 2, tz - 2, tx + 4, tz + 5)
        self.builds.append(lambda: self.build_lifeguard(tx, tz, g))

    def build_lifeguard(self, tx, tz, g):
        w = self.w
        for a in (0, 2):
            for b in (0, 2):
                for y in range(g + 1, g + 5):
                    w.set(tx + a, y, tz + b, st("stripped_birch_log", axis="y"))
                for y in range(g + 6, g + 8):
                    w.set(tx + a, y, tz + b, "birch_fence")
        for a in range(0, 3):
            for b in range(0, 3):
                w.set(tx + a, g + 5, tz + b, "birch_planks")
        for y in range(g + 1, g + 5):
            w.set(tx + 1, y, tz + 2, "birch_planks")
            w.set(tx + 1, y, tz + 3, st("ladder", facing="south"))
        w.set(tx + 1, g + 5, tz + 3, st("ladder", facing="south"))
        for a in range(0, 3):
            w.set(tx + a, g + 6, tz, "red_concrete")
        w.set(tx + 2, g + 6, tz + 1, "red_concrete")
        for a in range(-1, 4):
            for b in range(-1, 4):
                w.set(tx + a, g + 8, tz + b, "red_wool" if (a + b) % 2 else "white_wool")
        w.set(tx + 1, g + 9, tz + 1, "red_wool")
        villager(w, tx + 1.5, g + 6, tz + 1.5, "Strandwacht Noa", "red", 90, "nitwit", "jungle")
        surfboard(w, tx + 3.2, g + 1, tz - 1.2, "yellow", "red", -8)
        surfboard(w, tx + 4.1, g + 1, tz - 1.2, "light_blue", "white", -6)

    # -------------------------------------------------------- volleybal
    def plan_volleyball(self):
        w, t = self.w, self.t
        bx, bz = self.bar
        vz = bz - round(0.36 * w.S)
        if vz - 7 < w.x0 + 1:
            return
        vx = (t.shore_x[vz] + self.land_x(vz)) // 2 + 1
        if w.is_reserved_area(vx - 5, vz - 7, vx + 5, vz + 7):
            return
        g = max(t.h(vx, vz), SEA + 1)
        t.flatten(vx - 4, vz - 7, vx + 4, vz + 7, g, "beach")
        w.reserve(vx - 5, vz - 8, vx + 5, vz + 8)
        self.builds.append(lambda: self.build_volleyball(vx, vz, g))

    def build_volleyball(self, vx, vz, g):
        w = self.w
        for x in range(vx - 3, vx + 4):
            for z in range(vz - 6, vz + 7):
                if x in (vx - 3, vx + 3) or z in (vz - 6, vz + 6):
                    w.set(x, g + 1, z, "white_carpet")
        for x in (vx - 4, vx + 4):
            for y in range(g + 1, g + 4):
                w.set(x, y, vz, "bamboo_fence")
        for x in range(vx - 3, vx + 4):
            w.set(x, g + 3, vz, "cobweb")
        w.summon("block_display", vx - 1.2, g + 1, vz + 3.3,
                 'block_state:{Name:"minecraft:white_concrete"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.4f,0.4f,0.4f]}')
        w.summon("villager", vx + 1.5, g + 1, vz - 3.5,
                 'CustomName:\'{"text":"Speler Ikaika","color":"yellow"}\',NoAI:1b,PersistenceRequired:1b,Invulnerable:1b,Silent:1b,Rotation:[0f,0f],VillagerData:{type:"minecraft:jungle",profession:"minecraft:nitwit",level:1}')
        w.summon("villager", vx - 0.5, g + 1, vz + 4.5,
                 'CustomName:\'{"text":"Speler Lani","color":"aqua"}\',NoAI:1b,PersistenceRequired:1b,Invulnerable:1b,Silent:1b,Rotation:[180f,0f],VillagerData:{type:"minecraft:savanna",profession:"minecraft:nitwit",level:1}')

    # ------------------------------------------------------- zandkastelen
    def plan_sandcastles(self):
        w, t = self.w, self.t
        count = 1 if w.n < 5 else 2
        tries = 0
        while count > 0 and tries < 200:
            tries += 1
            z = self.rng.randint(w.x0 + 4, w.x1 - 4)
            x = t.shore_x[z] + self.rng.randint(2, 4)
            if w.is_reserved_area(x - 3, z - 3, x + 3, z + 3):
                continue
            cols = [(a, b) for a in range(x - 2, x + 3) for b in range(z - 2, z + 3)]
            if any(t.kind[c] != "beach" for c in cols):
                continue
            g = max(t.h(*c) for c in cols)
            t.flatten(x - 2, z - 2, x + 2, z + 2, g, "beach")
            w.reserve(x - 3, z - 3, x + 3, z + 3)
            self.builds.append(lambda x=x, z=z, g=g: self.build_sandcastle(x, z, g))
            count -= 1

    def build_sandcastle(self, x, z, g):
        w = self.w
        for a in range(-2, 3):
            for b in range(-2, 3):
                corner = abs(a) == 2 and abs(b) == 2
                edge = abs(a) == 2 or abs(b) == 2
                if corner:
                    w.set(x + a, g + 1, z + b, "smooth_sandstone")
                    w.set(x + a, g + 2, z + b, "chiseled_sandstone")
                elif edge:
                    w.set(x + a, g + 1, z + b, st("sandstone_slab", type="bottom"))
        w.set(x, g + 1, z, "cut_sandstone")
        w.set(x, g + 2, z, "cut_sandstone")
        w.set(x, g + 3, z, "chiseled_sandstone")
        w.set(x, g + 4, z, st(self.rng.choice(["red_banner", "light_blue_banner", "yellow_banner"]), rotation=4))

    # ----------------------------------------------------------- parasols
    def plan_umbrellas(self):
        w, t = self.w, self.t
        want = max(1, round(w.n * 1.5)) if w.n > 1 else 0
        tries = 0
        while want > 0 and tries < 400:
            tries += 1
            z = self.rng.randint(w.x0 + 3, w.x1 - 3)
            x = t.shore_x[z] + self.rng.randint(3, max(3, self.land_x(z) - t.shore_x[z] - 3))
            if w.is_reserved_area(x - 2, z - 2, x + 2, z + 2):
                continue
            cols = [(a, b) for a in range(x - 2, x + 3) for b in range(z - 2, z + 3)]
            if any(t.kind[c] != "beach" for c in cols):
                continue
            g = t.h(x, z)
            for c in cols:
                t.H[c] = g
            w.reserve(x - 2, z - 2, x + 2, z + 2)
            colors = self.rng.choice(UMBRELLA_COLORS)
            self.builds.append(lambda x=x, z=z, g=g, c=colors: self.build_umbrella(x, z, g, c))
            want -= 1

    def build_umbrella(self, x, z, g, colors):
        w, rng = self.w, self.rng
        c1, c2 = colors
        for y in range(g + 1, g + 4):
            w.set(x, y, z, "bamboo_fence")
        for a in range(-2, 3):
            for b in range(-2, 3):
                if abs(a) == 2 and abs(b) == 2:
                    continue
                ang = math.atan2(b, a)
                col = c1 if int((ang + math.pi) / (math.pi / 4)) % 2 else c2
                y = g + 4 if max(abs(a), abs(b)) < 2 else g + 3
                if (a, b) == (0, 0):
                    col = c1
                w.set(x + a, y, z + b, f"{col}_wool")
        wood = rng.choice(["birch", "bamboo", "jungle"])
        for b in (-1, 1):
            w.set(x + 1, g + 1, z + b, st(f"{wood}_stairs", facing="east", half="bottom"))
            w.set(x, g + 1, z + b, st(f"{wood}_slab", type="bottom"))
        if rng.random() < 0.6:
            towel = rng.choice(CARPETS)
            w.set(x - 2, g + 1, z, f"{towel}_carpet")
            w.set(x - 2, g + 1, z + 1, f"{towel}_carpet")
        if rng.random() < 0.4:
            w.set(x + 1, g + 1, z + 2 if rng.random() < 0.5 else z - 2,
                  st(rng.choice(["light_blue_shulker_box", "white_shulker_box", "red_shulker_box"]), facing="up"))
        if rng.random() < 0.5:
            item_display(w, x + 0.5, g + 1.3, z + 0.5, rng.choice(DRINKS), 0.35, rng.randint(0, 359))
        if rng.random() < 0.45:
            surfboard(w, x - 1.6, g + 1, z - 2.4, rng.choice(["yellow", "lime", "orange", "cyan", "magenta"]),
                      "white", -10)

    # ------------------------------------------------------------- paden
    def plan_paths(self):
        t, w = self.t, self.w
        targets = []
        if t.lagoon:
            lg = t.lagoon
            targets.append((self.exits[1], (lg["cx"] - lg["rx"] - 2, lg["cz"])))
        for hut in self.huts:
            ex = min(self.exits, key=lambda e: abs(e[1] - hut[1]))
            targets.append((ex, (hut[0] - 1, hut[1])))
        for (ax, az), (cx, cz) in targets:
            pts = [(ax, az), (ax, (az + cz) // 2), (cx, (az + cz) // 2), (cx, cz)]
            cells = []
            for (x1, z1), (x2, z2) in zip(pts, pts[1:]):
                steps = max(abs(x2 - x1), abs(z2 - z1), 1)
                for i in range(steps + 1):
                    x = round(x1 + (x2 - x1) * i / steps)
                    z = round(z1 + (z2 - z1) * i / steps)
                    cells.append((x, z))
            self.paths.append(cells)
        self.builds.append(self.build_paths)

    def build_paths(self):
        w, t = self.w, self.t
        done = set()
        for cells in self.paths:
            for i, (x, z) in enumerate(cells):
                for dx, dz in ((0, 0), (1, 0), (0, 1)):
                    c = (x + dx, z + dz)
                    if c in done or c not in t.H or c in w.reserved:
                        continue
                    k = t.kind[c]
                    h = t.h(*c)
                    if k == "land" and w.get(c[0], h, c[1]) == "minecraft:grass_block" and w.is_air(c[0], h + 1, c[1]):
                        w.set(c[0], h, c[1], "dirt_path")
                    elif k == "beach" and w.is_air(c[0], h + 1, c[1]):
                        w.set(c[0], h + 1, c[1], st("bamboo_mosaic_slab", type="bottom"))
                    else:
                        continue
                    done.add(c)
                if i % 7 == 3:
                    tx, tz = x + 2, z - 1
                    if (tx, tz) in t.H and (tx, tz) not in w.reserved and t.kind[(tx, tz)] in ("land", "beach"):
                        if w.is_air(tx, t.h(tx, tz) + 1, tz):
                            tiki_torch(w, tx, t.h(tx, tz), tz)
                            w.reserved.add((tx, tz))
        for c in done:
            w.reserved.add(c)

    # --------------------------------------------------------------- schat
    def plan_treasure(self):
        w, t = self.w, self.t
        for _ in range(200):
            x = self.rng.randint(w.x0 + 3, w.x0 + w.S // 5)
            z = self.rng.randint(w.x0 + 3, w.x1 - 3)
            if t.kind[(x, z)] == "sea" and SEA - t.h(x, z) >= 5:
                h = t.h(x, z)
                w.setblock_late(x, h + 1, z, st("chest", facing="east", waterlogged="true"),
                                '{LootTable:"minecraft:chests/buried_treasure"}')
                w.reserved.add((x, z))
                return

    # -------------------------------------------------------------- vulkaan
    def plan_volcano_smoke(self):
        t, w = self.t, self.w
        v = t.volcano
        cx, cz = int(v["cx"]), int(v["cz"])
        L = v["lava"]
        if not w.inb(cx, cz) or t.kind.get((cx, cz)) != "crater":
            return
        for dx in range(-1, 3):
            for dz in range(-1, 2):
                c = (cx + dx, cz + dz)
                if c in t.H:
                    t.H[c] = L
                    t.kind[c] = "volcano_island"
                    t.liquid.pop(c, None)

        def build():
            for dx in (0, 1):
                w.set(cx + dx, L, cz, "hay_block")
                w.set(cx + dx, L + 1, cz, st("campfire", lit="true", signal_fire="true"))
        self.builds.append(build)

    # ------------------------------------------------------------- waterval
    def plan_waterfall(self):
        t, w = self.t, self.w
        lg = t.lagoon
        cliff, top, cz = lg["cliff"], lg["top"], lg["cz"]

        def build():
            for z in range(cz - 1, cz + 2):
                if w.inb(cliff + 4, z):
                    w.cmds_end.append(f"setblock ~{cliff + 4} ~{top} ~{z} minecraft:water")
            # klimop op de klifwand
            for z in range(cz - 8, cz + 9):
                if abs(z - cz) <= 2 or not w.inb(cliff - 1, z):
                    continue
                if t.h(cliff, z) - t.h(cliff - 1, z) < 3 or self.rng.random() < 0.35:
                    continue
                y = t.h(cliff, z)
                length = self.rng.randint(2, max(2, t.h(cliff, z) - t.h(cliff - 1, z) - 1))
                for i in range(length):
                    if w.is_air(cliff - 1, y - i, z):
                        w.set(cliff - 1, y - i, z, st("vine", east="true"))
                    else:
                        break
        self.builds.append(build)
