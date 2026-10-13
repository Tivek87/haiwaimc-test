"""Buffers voor objecten (gebouwen, bomen) met optionele rotatie, compatibel met de oude bouwfuncties."""
import re

from world import ns, parse_state

from .terrain import S, TOP, X0, YMIN

AIR = "minecraft:air"
FACINGS = ["north", "east", "south", "west"]


def rot_dir(d, k):
    """Draai een richting k keer 90 graden: west -> zuid -> oost -> noord."""
    order = ["west", "south", "east", "north"]
    if d not in order:
        return d
    return order[(order.index(d) + k) % 4]


def rot_state(state, k):
    if k % 4 == 0:
        return state
    name, props = parse_state(state)
    if not props:
        return name
    out = {}
    for key, v in props.items():
        if key == "facing":
            out[key] = rot_dir(v, k)
        elif key == "axis" and v in ("x", "z") and k % 2:
            out[key] = "z" if v == "x" else "x"
        elif key == "rotation":
            out[key] = str((int(v) - 4 * k) % 16)
        elif key in ("north", "east", "south", "west"):
            out[rot_dir(key, k)] = v
        else:
            out[key] = v
    return name + "[" + ",".join(f"{a}={b}" for a, b in sorted(out.items())) + "]"


FACE_BYTE = {"north": 2, "south": 3, "west": 4, "east": 5}
BYTE_FACE = {v: k for k, v in FACE_BYTE.items()}


def rot_nbt(nbt, k):
    if k % 4 == 0:
        return nbt
    nbt = re.sub(r"Rotation:\[(-?[\d.]+)f", lambda m: f"Rotation:[{(float(m.group(1)) - 90 * k) % 360:g}f", nbt)
    nbt = re.sub(r"Facing:(\d)b", lambda m: f"Facing:{FACE_BYTE[rot_dir(BYTE_FACE[int(m.group(1))], k)]}b"
                 if int(m.group(1)) in BYTE_FACE else m.group(0), nbt)
    return nbt


class ObjBuf:
    """Verzamelt blokken/entities van 1 object in wereldcoordinaten (t.o.v. de speler)."""

    def __init__(self, isl, rng, mode="force"):
        self.isl = isl
        self.rng = rng
        self.mode = mode
        self.blk = {}
        self.ents = []  # (x, z, commando)
        self.late = []  # (x, z, commando)
        self.cmds_end = []
        self.n = 36
        self.S = S
        self.x0 = X0
        self.x1 = X0 + S - 1

    # ---- wereld-API (zelfde als World uit de kleine generator) ----
    def inb(self, x, z):
        return self.x0 <= x <= self.x1 and self.x0 <= z <= self.x1

    def set(self, x, y, z, state, force=True):
        if not self.inb(x, z) or y < YMIN or y > TOP:
            return
        key = (x, y, z)
        if not force and key in self.blk and self.blk[key] != AIR:
            return
        self.blk[key] = ns(state)

    def setk(self, x, y, z, state):
        if self.is_air(x, y, z):
            self.set(x, y, z, state)

    def clear(self, x, y, z):
        if self.inb(x, z):
            self.blk[(x, y, z)] = AIR

    def terrain_block(self, x, y, z):
        isl = self.isl
        ix, iz = x - X0, z - X0
        h = int(isl.H[ix, iz])
        if y <= h:
            return "minecraft:stone"
        lt = int(isl.liq_top[ix, iz])
        if lt > -999 and y <= lt:
            return "minecraft:lava" if isl.liq_lava[ix, iz] else "minecraft:water"
        if y <= -2 and h < -2:
            return "minecraft:water"
        return None

    def get(self, x, y, z):
        if not self.inb(x, z):
            return None
        s = self.blk.get((x, y, z))
        if s is not None:
            return None if s == AIR else s
        return self.terrain_block(x, y, z)

    def is_air(self, x, y, z):
        return self.inb(x, z) and YMIN <= y <= TOP and self.get(x, y, z) is None

    def fill(self, x1, y1, z1, x2, y2, z2, state):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, state)

    def reserve(self, x1, z1, x2, z2):
        self.isl.reserve(x1, z1, x2, z2)

    def is_reserved_area(self, x1, z1, x2, z2):
        return self.isl.is_reserved(x1, z1, x2, z2)

    def summon(self, etype, x, y, z, nbt=""):
        from world import fmt
        tag = 'Tags:["hawaii_ent","hawaii_isl"]'
        nbt = "{" + (tag + "," + nbt if nbt else tag) + "}"
        self.ents.append((x, z, f"summon minecraft:{etype} ~{fmt(x)} ~{fmt(y)} ~{fmt(z)} {nbt}"))

    def setblock_late(self, x, y, z, state, nbt=""):
        if self.inb(x, z):
            self.late.append((x, z, f"setblock ~{x} ~{y} ~{z} {ns(state)}{nbt}"))


class RotBuf:
    """Bouw in lokale coordinaten (voorkant naar het westen) en zet het gedraaid in de wereld."""

    def __init__(self, base, ox, oz, k):
        self.base, self.ox, self.oz, self.k = base, ox, oz, k % 4
        self.rng = base.rng
        self.n, self.S, self.x0, self.x1 = base.n, base.S, base.x0, base.x1
        self.isl = base.isl

    def tf(self, x, z):
        for _ in range(self.k):
            x, z = z, -x
        return self.ox + x, self.oz + z

    def tff(self, x, z):
        """Zelfde voor kommagetallen (entities)."""
        for _ in range(self.k):
            x, z = z, -x
        return self.ox + x, self.oz + z

    def inb(self, x, z):
        return self.base.inb(*self.tf(x, z))

    def set(self, x, y, z, state, force=True):
        wx, wz = self.tf(x, z)
        self.base.set(wx, y, wz, rot_state(ns(state), self.k), force)

    def setk(self, x, y, z, state):
        wx, wz = self.tf(x, z)
        self.base.setk(wx, y, wz, rot_state(ns(state), self.k))

    def clear(self, x, y, z):
        self.base.clear(*self._xyz(x, y, z))

    def _xyz(self, x, y, z):
        wx, wz = self.tf(x, z)
        return wx, y, wz

    def get(self, x, y, z):
        return self.base.get(*self._xyz(x, y, z))

    def is_air(self, x, y, z):
        return self.base.is_air(*self._xyz(x, y, z))

    def fill(self, x1, y1, z1, x2, y2, z2, state):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, state)

    def reserve(self, x1, z1, x2, z2):
        a, b = self.tf(x1, z1)
        c, d = self.tf(x2, z2)
        self.base.reserve(a, b, c, d)

    def is_reserved_area(self, x1, z1, x2, z2):
        a, b = self.tf(x1, z1)
        c, d = self.tf(x2, z2)
        return self.base.is_reserved_area(a, b, c, d)

    def summon(self, etype, x, y, z, nbt=""):
        # blok-midden (x.5) blijft blok-midden na draaien: draai rond het midden van het blok
        cx, cz = x - 0.5, z - 0.5
        wx, wz = self.tff(cx, cz)
        self.base.summon(etype, wx + 0.5, y, wz + 0.5, rot_nbt(nbt, self.k))

    def setblock_late(self, x, y, z, state, nbt=""):
        wx, wz = self.tf(x, z)
        self.base.setblock_late(wx, y, wz, rot_state(ns(state), self.k), nbt)


class RotTerrain:
    """h(x, z) in lokale coordinaten van een RotBuf."""

    def __init__(self, rb):
        self.rb = rb

    def h(self, x, z):
        wx, wz = self.rb.tf(x, z)
        return self.rb.isl.h(wx, wz)


class Shim:
    """Doet zich voor als Planner zodat de bouwfuncties uit structures.py herbruikt kunnen worden."""

    def __init__(self, buf):
        self.w = buf
        self.rng = buf.rng
        self.t = RotTerrain(buf) if isinstance(buf, RotBuf) else buf.isl
