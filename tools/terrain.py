"""Terrein: zee, strand, jungle, heuvels, vulkaan, lagune met waterval."""
import math

from world import SEA, YMIN, Noise, smooth, st


class Terrain:
    def __init__(self, w):
        self.w = w
        self.H = {}  # (x, z) -> hoogste vaste blok
        self.kind = {}  # (x, z) -> soort ondergrond
        self.liquid = {}  # (x, z) -> (blok, bovenste y)
        self.n1 = Noise(11 + w.n)
        self.n2 = Noise(23 + w.n)
        self.n3 = Noise(37 + w.n)
        self.volcano = None
        self.lagoon = None
        self.shore_x = {}  # z -> eerste strand-x

    # ------------------------------------------------------------------ vorm
    def uv(self, x, z):
        S = self.w.S
        return (x - self.w.x0 + 0.5) / S, (z - self.w.x0 + 0.5) / S

    def shore_frac(self, v):
        return 0.33 + 0.045 * self.n1.fbm(v * 3.0, 7.3)

    def compute(self):
        w, S = self.w, self.w.S
        bw = 0.19
        for x in range(w.x0, w.x1 + 1):
            for z in range(w.x0, w.x1 + 1):
                u, v = self.uv(x, z)
                d = u - self.shore_frac(v)
                if d < 0:
                    depth = 1 + (-d) * S * 0.32 + 1.3 * self.n2.fbm(u * 5 + 11, v * 5)
                    h, k = SEA - int(round(max(1, min(9, depth)))), "sea"
                    edge = min(x - w.x0, z - w.x0, w.x1 - z)
                    if edge < 2:
                        h, k = SEA, "rim"
                elif d < bw:
                    t = d / bw
                    h = SEA + int(round(2.3 * smooth(t) + 0.4 * self.n2.fbm(u * 7, v * 7 + 3, 2)))
                    if d * S < 1.3:
                        h = SEA
                    h, k = min(h, 0), "beach"
                else:
                    t = (d - bw) * S
                    base = 0.5 + 1.3 * smooth(t / 5) + 1.4 * self.n2.fbm(u * 4 + 5, v * 4 + 5)
                    hill = max(0.0, u - 0.70) * S * 0.55 * (0.8 + 0.4 * self.n3.fbm(u * 3 + 9, v * 3 + 9, 2))
                    h, k = max(0, int(round(base + hill))), "land"
                self.H[(x, z)] = h
                self.kind[(x, z)] = k
        for z in range(w.x0, w.x1 + 1):
            for x in range(w.x0, w.x1 + 1):
                if self.kind[(x, z)] == "beach":
                    self.shore_x[z] = x
                    break
            else:
                self.shore_x[z] = w.x0
        if w.n >= 4:
            self._volcano()
        if w.n >= 3:
            self._lagoon()
        self._edge_falloff()

    def _edge_falloff(self):
        """Laat heuvels/vulkaan aflopen naar de rand, zodat het aansluit op de omgeving."""
        w = self.w
        for (x, z), h in self.H.items():
            if self.kind[(x, z)] not in ("land", "volcano"):
                continue
            edge = min(w.x1 - x, z - w.x0, w.x1 - z)
            cap = 1 + int(edge * 1.6)
            if h > cap:
                self.H[(x, z)] = cap

    def _volcano(self):
        w, S = self.w, self.w.S
        cx, cz = w.x0 + 0.79 * S, w.x0 + 0.27 * S
        R = 0.19 * S
        Hv = min(44, round(0.34 * S))
        rc = 0.2
        lava = Hv - 4
        self.volcano = dict(cx=cx, cz=cz, R=R, H=Hv, rc=rc, lava=lava)
        for x in range(w.x0, w.x1 + 1):
            for z in range(w.x0, w.x1 + 1):
                r = math.hypot(x + 0.5 - cx, z + 0.5 - cz) / R
                if r >= 1:
                    continue
                if r >= rc:
                    hv = Hv * ((1 - r) / (1 - rc)) ** 1.4 + 1.2 * self.n1.fbm(x * 0.15, z * 0.15) * (1 - r)
                    k = "volcano"
                else:
                    hv = Hv - 1 - round(6 * (1 - (r / rc) ** 2))
                    k = "crater"
                if k == "crater" or hv > self.H[(x, z)] + 0.5:
                    self.H[(x, z)] = int(round(hv))
                    self.kind[(x, z)] = k
                    if k == "crater" and self.H[(x, z)] < lava:
                        self.liquid[(x, z)] = ("lava", lava)

    def _lagoon(self):
        w, S = self.w, self.w.S
        lcx, lcz = w.x0 + round(0.66 * S), w.x0 + round(0.75 * S)
        rx = max(3, round(0.07 * S))
        rz = round(rx * 1.35)
        lv = 1
        cliff = lcx + rx
        top = lv + max(6, min(14, round(0.12 * S)))
        band = rz + 2
        self.lagoon = dict(cx=lcx, cz=lcz, rx=rx, rz=rz, level=lv, cliff=cliff, top=top)
        for x in range(cliff, w.x1 + 1):
            for z in range(w.x0, w.x1 + 1):
                dz = abs(z - lcz)
                ridge = top if dz <= band else top - (dz - band) * 1.1
                ridge += 0.8 * self.n3.fbm(x * 0.2, z * 0.2)
                if self.kind[(x, z)] in ("land",) and ridge > self.H[(x, z)]:
                    self.H[(x, z)] = int(round(ridge)) if dz > band else top
        for x in range(w.x0, cliff):
            for z in range(w.x0, w.x1 + 1):
                e = ((x + 0.5 - lcx) / rx) ** 2 + ((z + 0.5 - lcz) / rz) ** 2
                if e < 1:
                    self.H[(x, z)] = lv - 1 - int(round(2.5 * (1 - e)))
                    self.kind[(x, z)] = "lagoon"
                    self.liquid[(x, z)] = ("water", lv)
                elif e < 2.2 and self.kind[(x, z)] in ("land", "beach"):
                    # oever minstens op waterhoogte zodat de lagune niet leegloopt
                    self.H[(x, z)] = max(self.H[(x, z)], lv)
                    self.kind[(x, z)] = "land"
        # goot bovenop de klif waar het water uit komt
        for x in range(cliff, cliff + 5):
            for z in range(lcz - 1, lcz + 2):
                if w.inb(x, z):
                    self.H[(x, z)] = top - 1
                    self.kind[(x, z)] = "channel"
        for x in range(cliff, cliff + 6):
            for z in (lcz - 2, lcz + 2):
                if w.inb(x, z):
                    self.H[(x, z)] = max(self.H[(x, z)], top)
        for z in range(lcz - 2, lcz + 3):
            if w.inb(cliff + 5, z):
                self.H[(cliff + 5, z)] = max(self.H[(cliff + 5, z)], top)

    # ---------------------------------------------------------- hulpfuncties
    def h(self, x, z):
        return self.H.get((x, z), YMIN)

    def flatten(self, x1, z1, x2, z2, height, kind=None):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                if (x, z) in self.H:
                    self.H[(x, z)] = height
                    if kind:
                        self.kind[(x, z)] = kind
                    self.liquid.pop((x, z), None)

    def is_water(self, x, z):
        k = self.kind.get((x, z))
        return k in ("sea", "lagoon")

    def water_top(self, x, z):
        k = self.kind.get((x, z))
        if k == "sea":
            return SEA
        if (x, z) in self.liquid:
            return self.liquid[(x, z)][1]
        return None

    def steep(self, x, z):
        h = self.h(x, z)
        low = min(self.H.get((x + dx, z + dz), h) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        return h - low >= 3

    # -------------------------------------------------------------- blokken
    def material(self, x, y, z, k, depth, steep):
        n1 = self.n1.fbm(x * 0.13, z * 0.13 + 50)
        n2 = self.n2.fbm(x * 0.21 + 30, z * 0.21)
        if k in ("sea", "rim"):
            if depth == 0:
                if k == "sea" and SEA - y >= 4 and n1 > 0.42:
                    return "gravel"
                if k == "sea" and n2 < -0.5:
                    return "clay"
                return "sand"
            return "sand" if depth < 4 else "sandstone" if depth < 6 else "stone"
        if k == "beach":
            return "sand" if depth < 4 else "sandstone" if depth < 6 else "stone"
        if k == "lagoon":
            if depth == 0:
                return "clay" if n1 > 0.3 else "gravel" if n2 > 0.45 else "sand"
            return "dirt" if depth < 3 else "stone"
        if k == "volcano_island":
            return "basalt[axis=y]"
        if k == "channel":
            return "mossy_cobblestone" if depth == 0 else "stone"
        if k in ("volcano", "crater"):
            v = self.volcano
            r = math.hypot(x + 0.5 - v["cx"], z + 0.5 - v["cz"]) / v["R"]
            if k == "crater":
                return "magma_block" if depth == 0 else "basalt[axis=y]"
            if depth <= 1:
                ang = math.atan2(z + 0.5 - v["cz"], x + 0.5 - v["cx"])
                streak = abs(math.sin(ang * 3 + 1.7 * self.n3.fbm(r * 3, ang)))
                if 0.25 < r < 0.85 and streak < 0.06:
                    return "magma_block"
                if r < v["rc"] + 0.06:
                    return "obsidian" if n2 > 0.2 else "blackstone"
                if r > 0.82:
                    return "coarse_dirt" if n1 > 0.1 else "gravel" if n2 > 0.3 else "tuff"
                c = n1 + 0.6 * n2
                if c > 0.35:
                    return "smooth_basalt"
                if c < -0.35:
                    return "tuff"
                return "basalt[axis=y]" if n2 > 0 else "blackstone"
            return "basalt[axis=y]" if depth < 4 else "stone"
        # land
        if depth == 0:
            if steep and n2 > 0.55:
                return "moss_block"
            if not steep:
                if n1 > 0.62:
                    return "podzol"
                if n1 < -0.66:
                    return "coarse_dirt"
                if n2 > 0.72:
                    return "moss_block"
            return "grass_block"
        if steep or depth >= 4:
            c = self.n3.fbm(x * 0.3, y * 0.3 + z * 0.3)
            if c > 0.3:
                return "mossy_cobblestone"
            if c < -0.3:
                return "andesite"
            if n2 > 0.4:
                return "cobblestone"
            return "stone"
        return "dirt"

    def write(self):
        w = self.w
        for (x, z), h in self.H.items():
            k = self.kind[(x, z)]
            steep = k == "land" and self.steep(x, z)
            for y in range(YMIN, h + 1):
                w.set(x, y, z, self.material(x, y, z, k, h - y, steep))
            if k == "sea":
                for y in range(h + 1, SEA + 1):
                    w.set(x, y, z, "water")
            if (x, z) in self.liquid:
                block, top = self.liquid[(x, z)]
                for y in range(h + 1, top + 1):
                    w.set(x, y, z, block)

    def biome(self, x, z):
        k = self.kind.get((x, z))
        if k in ("sea", "rim", "lagoon"):
            return "warm_ocean"
        if k == "beach":
            return "beach"
        return "jungle"
