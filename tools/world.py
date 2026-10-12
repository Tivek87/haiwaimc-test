"""Basis: wereld-buffer, ruis en hulpfuncties voor de Hawaii generator."""
import math
import random

YMIN = -12  # laagste laag van de structuren (t.o.v. de voeten van de speler)
TOP = 56  # hoogste laag die wordt leeggemaakt
SEA = -2  # bovenste waterlaag van de zee

DIRS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def ns(state):
    return state if state.startswith("minecraft:") else "minecraft:" + state


def st(name, **props):
    """st('oak_stairs', facing='east') -> 'minecraft:oak_stairs[facing=east]'"""
    if not props:
        return ns(name)
    inner = ",".join(f"{k}={str(v).lower()}" for k, v in sorted(props.items()))
    return f"{ns(name)}[{inner}]"


def parse_state(state):
    state = ns(state)
    if "[" not in state:
        return state, {}
    name, rest = state.split("[", 1)
    props = dict(p.split("=") for p in rest.rstrip("]").split(",") if p)
    return name, props


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Noise:
    """Eenvoudige value-noise met fbm, deterministisch per seed."""

    def __init__(self, seed):
        self.seed = seed

    def _h(self, ix, iy):
        h = (ix * 374761393 + iy * 668265263 + self.seed * 982451653) & 0xFFFFFFFF
        h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
        h ^= h >> 16
        return (h & 0xFFFF) / 32767.5 - 1.0

    def v(self, x, y):
        ix, iy = math.floor(x), math.floor(y)
        fx, fy = x - ix, y - iy
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a, b = self._h(ix, iy), self._h(ix + 1, iy)
        c, d = self._h(ix, iy + 1), self._h(ix + 1, iy + 1)
        top = a + (b - a) * sx
        bot = c + (d - c) * sx
        return top + (bot - top) * sy

    def fbm(self, x, y, octaves=3):
        total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            total += amp * self.v(x * freq, y * freq)
            norm += amp
            amp *= 0.5
            freq *= 2.0
        return total / norm


class World:
    """Alle blokken van 1 grootte, in coordinaten t.o.v. de speler (midden van het gebied)."""

    def __init__(self, n):
        self.n = n
        self.S = 16 * n
        self.x0 = -self.S // 2
        self.x1 = self.x0 + self.S - 1
        self.blk = {}
        self.late = []  # setblock-commando's die na het plaatsen van alle chunks moeten
        self.ents = []  # summon-commando's
        self.cmds_end = []  # overige commando's aan het eind
        self.rng = random.Random(4242 + n)
        self.reserved = set()  # kolommen (x, z) waar geen planten/bomen mogen komen

    def inb(self, x, z):
        return self.x0 <= x <= self.x1 and self.x0 <= z <= self.x1

    def set(self, x, y, z, state, force=True):
        if not self.inb(x, z) or y < YMIN or y > TOP:
            return
        key = (x, y, z)
        if not force and key in self.blk:
            return
        self.blk[key] = ns(state)

    def setk(self, x, y, z, state):
        """Alleen zetten als de plek nog leeg is."""
        self.set(x, y, z, state, force=False)

    def get(self, x, y, z):
        return self.blk.get((x, y, z))

    def clear(self, x, y, z):
        self.blk.pop((x, y, z), None)

    def is_air(self, x, y, z):
        return self.inb(x, z) and YMIN <= y <= TOP and (x, y, z) not in self.blk

    def fill(self, x1, y1, z1, x2, y2, z2, state):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, state)

    def reserve(self, x1, z1, x2, z2):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                self.reserved.add((x, z))

    def is_reserved_area(self, x1, z1, x2, z2):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                if (x, z) in self.reserved or not self.inb(x, z):
                    return True
        return False

    # ---- entiteiten -------------------------------------------------------
    def summon(self, etype, x, y, z, nbt=""):
        tag = 'Tags:["hawaii_ent"]'
        nbt = "{" + (tag + "," + nbt if nbt else tag) + "}"
        self.ents.append(f"summon minecraft:{etype} ~{fmt(x)} ~{fmt(y)} ~{fmt(z)} {nbt}")

    def setblock_late(self, x, y, z, state, nbt=""):
        if not self.inb(x, z):
            return
        self.late.append(f"setblock ~{x} ~{y} ~{z} {ns(state)}{nbt}")


def fmt(v):
    if isinstance(v, int) or float(v).is_integer():
        return str(int(v))
    return f"{v:.2f}".rstrip("0")
