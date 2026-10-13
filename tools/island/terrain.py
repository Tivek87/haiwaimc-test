"""Het eiland: hoogtekaart, zones, rivieren met watervallen, kloof, lagune, rif, motu's en kliffen."""
import heapq
import math

import numpy as np

from .noise import fbm, ridged, smoothstep

N = 36  # chunks per zijde
S = N * 16  # 576 blokken
X0 = -S // 2  # -288
YMIN = -24
TOP = 103
SEA = -2

# zones
DEEP, LAGOON, REEF, BEACH, BLACKBEACH, RAINFOREST, HIGHLAND, PEAK, VOLCANIC, CRATER, MEADOW, PLANTATION, \
    VILLAGE, TOWN, CANYON, RIVERBANK, CLIFF, BAMBOO, MOTU = range(19)
ZONE_NAMES = ["deep", "lagoon", "reef", "beach", "blackbeach", "rainforest", "highland", "peak", "volcanic", "crater",
              "meadow", "plantation", "village", "town", "canyon", "riverbank", "cliff", "bamboo", "motu"]

# eigen biomen (hawaii:...) met een vanilla terugval als de eigen biomen niet geladen zijn
BIOMES = {
    DEEP: ("tropical_ocean", "warm_ocean"), LAGOON: ("coral_lagoon", "warm_ocean"), REEF: ("coral_lagoon", "warm_ocean"),
    BEACH: ("white_sand_beach", "beach"), BLACKBEACH: ("black_sand_beach", "stony_shore"),
    RAINFOREST: ("rainforest", "jungle"), HIGHLAND: ("cloud_forest", "sparse_jungle"), PEAK: ("cloud_forest", "sparse_jungle"),
    VOLCANIC: ("volcanic_slopes", "savanna"), CRATER: ("volcanic_slopes", "savanna"), MEADOW: ("upland_meadow", "plains"),
    PLANTATION: ("sugar_plantation", "savanna"), VILLAGE: ("polynesian_village", "jungle"), TOWN: ("colonial_town", "savanna"),
    CANYON: ("red_canyon", "badlands"), RIVERBANK: ("jungle_river", "jungle"), CLIFF: ("cloud_forest", "sparse_jungle"),
    BAMBOO: ("bamboo_forest", "bamboo_jungle"), MOTU: ("white_sand_beach", "beach"),
}

# vaste plekken (relatieve coordinaten) - het eiland is altijd hetzelfde
SITES = {
    "resort": (8, 0),  # wordt aan de zuidkust gezet (zie plan)
    "village": (-196, 30),
    "town": (190, 58),
    "plantation": (-105, 118),
    "ranch": (42, 70),
    "temple": (-112, -10),
    "treehouse": (-48, 52),
    "volcano": (132, -104),
}


def seg_dist(px, pz, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    t = np.clip(((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz), 0, 1)
    return np.hypot(px - (ax + t * dx), pz - (az + t * dz))


class Island:
    def __init__(self, seed=7):
        self.seed = seed
        xs = np.arange(X0, X0 + S, dtype=np.float64)
        self.X, self.Z = np.meshgrid(xs, xs, indexing="ij")
        self.rivers = []
        self.sites = dict(SITES)
        self.flat_sites = []

    # ---------------------------------------------------------------- reserveren
    def reserve(self, x1, z1, x2, z2):
        a, b = sorted((x1, x2))
        c, d = sorted((z1, z2))
        self.res[max(0, a - X0):max(0, b - X0 + 1), max(0, c - X0):max(0, d - X0 + 1)] = True

    def is_reserved(self, x1, z1, x2, z2):
        a, b = sorted((x1, x2))
        c, d = sorted((z1, z2))
        if a < X0 or c < X0 or b >= X0 + S or d >= X0 + S:
            return True
        return bool(self.res[a - X0:b - X0 + 1, c - X0:d - X0 + 1].any())

    # ---------------------------------------------------------------- indices
    @staticmethod
    def idx(x, z):
        return x - X0, z - X0

    def inb(self, x, z):
        return X0 <= x < X0 + S and X0 <= z < X0 + S

    def h(self, x, z):
        return int(self.H[x - X0, z - X0])

    def zone_at(self, x, z):
        return int(self.zone[x - X0, z - X0])

    # ------------------------------------------------------------------ vorm
    def build(self):
        X, Z, sd = self.X, self.Z, self.seed
        dist = np.hypot(X, Z)
        ang = np.arctan2(Z, X)
        rr = 212 * (1 + 0.16 * fbm(np.cos(ang) * 1.6 + 5, np.sin(ang) * 1.6 + 5, sd, 3)) \
            + 14 * fbm(X / 38, Z / 38, sd + 1, 3)
        # baaien
        for bang, bdepth, bw in ((math.radians(150), 34, 0.18), (math.radians(60), 26, 0.14), (math.radians(-60), 18, 0.12)):
            da = np.angle(np.exp(1j * (ang - bang)))
            rr -= bdepth * np.exp(-(da / bw) ** 2)
        self.dc = rr - dist  # afstand tot de kust (positief = land)
        self.ang = ang
        dc = self.dc
        # noordkust met kliffen
        north = smoothstep(-0.25, 0.15, -np.sin(ang)) * smoothstep(-0.9, -0.55, np.cos(ang + 0.0)) \
            * (1 - smoothstep(0.55, 0.8, np.cos(ang)))
        north = np.clip(north + 0.25 * fbm(X / 40, Z / 40, sd + 13, 2) * (north > 0.05), 0, 1)
        self.cliffw = north
        base = SEA + 1 + 24 * smoothstep(0, 105, dc) ** 1.3
        hills = 9 * fbm(X / 55, Z / 55, sd + 2, 4) * smoothstep(5, 50, dc)
        spine = [(-165, -30), (-95, -92), (-10, -112), (70, -88), (118, -58)]
        dsp = np.full(X.shape, 1e9)
        for (ax, az), (bx, bz) in zip(spine, spine[1:]):
            dsp = np.minimum(dsp, seg_dist(X, Z, ax, az, bx, bz))
        m = np.exp(-(dsp / 62) ** 2) * smoothstep(-5, 25, dc)
        mount = m * (18 + 62 * ridged(X / 52, Z / 52, sd + 3) ** 1.5)
        e = base + hills + mount
        # kliffen langs de noordkust (Na Pali / Maui)
        cliff_top = SEA + 6 + 34 * smoothstep(0, 16, dc) + 10 * fbm(X / 30, Z / 30, sd + 4, 3)
        e = np.where(dc > 0, np.maximum(e, cliff_top * north + e * (1 - north)), e)
        # vulkaan
        vx, vz = self.sites["volcano"]
        dv = np.hypot(X - vx, Z - vz)
        vr, vh, rc = 82.0, 86.0, 0.13
        rn = dv / vr
        cone = np.where(rn < 1, vh * (np.clip(1 - rn, 0, None) / (1 - rc)) ** 1.35 + 3 * fbm(X / 12, Z / 12, sd + 5, 2) * (1 - rn), -99)
        rim = vh
        crater = rn < rc
        cone = np.where(crater, rim - 2 - 9 * (1 - (rn / rc) ** 2), cone)
        self.volcano = dict(x=vx, z=vz, rim=int(rim), lava=int(rim) - 7, r=vr)
        self.vmask = (cone > e) | crater
        e = np.maximum(e, cone)
        e = np.where(crater, cone, e)
        # oceaan
        do = -dc
        lagoon_depth = np.clip(1.2 + do * 0.075 + 1.3 * fbm(X / 20, Z / 20, sd + 6, 2), 1, 5)
        reef_pass = fbm(X / 25, Z / 25, sd + 7, 2) > 0.42
        reef_depth = np.where(reef_pass, 3.5, 1.0)
        outer = np.clip(5 + (do - 50) * 0.32, 5, 20)
        depth = np.where(do < 42, lagoon_depth, np.where(do < 50, reef_depth, outer))
        cliff_depth = np.clip(3 + do * 0.35, 3, 20)
        depth = depth * (1 - north) + cliff_depth * north
        sea_floor = SEA - depth
        e = np.where(dc > 0, e, sea_floor)
        self.lagoon_mask = (dc <= 0) & (do < 42) & (north < 0.5)
        self.reef_mask = (dc <= 0) & (do >= 42) & (do < 50) & (north < 0.5) & ~reef_pass
        # motu's (eilandjes op het rif)
        self.motus = []
        for a in (118, 140, 66, 38, 200):
            ar = math.radians(a)
            # zoek de rifring langs deze straal
            for r in range(150, 290):
                px, pz = r * math.cos(ar), r * math.sin(ar)
                ix, iz = int(px) - X0, int(pz) - X0
                if not (0 <= ix < S and 0 <= iz < S):
                    break
                if 44 <= do[ix, iz] <= 48:
                    self.motus.append((int(px), int(pz), 7 + (a % 4)))
                    break
        for mx, mz, mr in self.motus:
            dm = np.hypot(X - mx, Z - mz) / mr
            isl = SEA + 1 + 2.2 * (1 - dm) + 0.6 * fbm(X / 6, Z / 6, sd + 8, 2)
            e = np.where(dm < 1, np.maximum(e, isl), e)
        # zeepilaren bij de kliffen
        self.stacks = []
        rng = np.random.default_rng(sd)
        for a in (-118, -96, -70, -52, -140):
            ar = math.radians(a)
            for r in range(120, 290):
                ix, iz = int(r * math.cos(ar)) - X0, int(r * math.sin(ar)) - X0
                if 0 <= ix < S and 0 <= iz < S and do[ix, iz] > 10 + rng.integers(0, 12):
                    self.stacks.append((ix + X0, iz + X0, int(rng.integers(3, 6)), int(rng.integers(10, 24))))
                    break
        for sx, sz, sr, shh in self.stacks:
            ds = np.hypot(X - sx, Z - sz) / sr
            pill = SEA + shh * (1 - ds ** 6) + 2 * fbm(X / 4, Z / 4, sd + 9, 2)
            e = np.where(ds < 1, np.maximum(e, pill), e)
        self.e = e
        self.place_sites()
        self.flatten_sites()
        self.carve_rivers()
        self.finalize()

    # ---------------------------------------------------------------- plekken
    def coast_point(self, deg, inland=0):
        ar = math.radians(deg)
        last = None
        for r in range(0, 300):
            x, z = int(r * math.cos(ar)), int(r * math.sin(ar))
            if not self.inb(x, z):
                break
            if self.dc[x - X0, z - X0] > inland:
                last = (x, z)
            elif last is not None and self.dc[x - X0, z - X0] <= 0:
                break
        return last

    def place_sites(self):
        # resort aan de zuidkust, net op het strand
        self.sites["resort"] = self.coast_point(92, inland=20)
        self.sites["village"] = self.coast_point(170, inland=26)
        self.sites["town"] = self.coast_point(18, inland=30)
        self.sites["lighthouse"] = self.coast_point(-108, inland=6)
        self.sites["fort"] = self.coast_point(-8, inland=8)
        self.sites["blackbeach"] = self.coast_point(-34, inland=2)
        self.sites["mouthA"] = self.coast_point(186, inland=-4)
        self.sites["mouthB"] = self.coast_point(34, inland=-4)
        self.sites["mouthC"] = self.coast_point(104, inland=-4)

    def flatten_sites(self):
        e = self.e
        X, Z = self.X, self.Z
        flats = [
            ("resort", 46, SEA + 1),
            ("village", 44, SEA + 2),
            ("town", 50, SEA + 3),
            ("plantation", 56, None),
            ("ranch", 38, None),
            ("temple", 24, None),
            ("lighthouse", 12, None),
            ("fort", 16, None),
        ]
        for name, r, g in flats:
            cx, cz = self.sites[name]
            ix, iz = cx - X0, cz - X0
            if g is None:
                g = float(np.median(e[max(0, ix - 6):ix + 7, max(0, iz - 6):iz + 7]))
                if name == "plantation":
                    g = max(g, SEA + 4)
                    g = min(g, SEA + 9)
            d = np.hypot(X - cx, Z - cz)
            mask = smoothstep(r, r * 0.55, d)
            if name in ("resort", "village", "town"):
                # alleen het land vlak maken, zee blijft zee
                mask = mask * smoothstep(-2, 6, self.dc)
            e[:] = e * (1 - mask) + g * mask
            self.flat_sites.append((name, cx, cz, r, int(round(g))))
        self.site_level = {n: g for n, _, _, _, g in self.flat_sites}

    # ---------------------------------------------------------------- rivieren
    def least_cost_path(self, src, dst, step=4):
        e = self.e
        nx = S // step
        sub = e[::step, ::step]
        land = self.dc[::step, ::step] > -6
        avoid = np.zeros(sub.shape)
        for name, cx, cz, r, g in self.flat_sites:
            if name in ("resort", "village", "town", "plantation", "ranch", "temple"):
                d = np.hypot(self.X[::step, ::step] - cx, self.Z[::step, ::step] - cz)
                avoid += d < r * 1.05
        if hasattr(self, "river_d"):
            avoid += 1.5 * (self.river_d[::step, ::step] < 16)
        sx, sz = (src[0] - X0) // step, (src[1] - X0) // step
        tx, tz = (dst[0] - X0) // step, (dst[1] - X0) // step
        dist = np.full((nx, nx), np.inf)
        prev = {}
        dist[sx, sz] = 0
        pq = [(0.0, sx, sz)]
        nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        while pq:
            d, x, z = heapq.heappop(pq)
            if (x, z) == (tx, tz):
                break
            if d > dist[x, z]:
                continue
            for dx, dz in nbrs:
                a, b = x + dx, z + dz
                if not (0 <= a < nx and 0 <= b < nx) or not land[a, b]:
                    continue
                rise = max(0.0, sub[a, b] - sub[x, z])
                c = math.hypot(dx, dz) * (1 + 40 * rise + 0.015 * max(0.0, sub[a, b] - SEA) + 60 * avoid[a, b])
                nd = d + c
                if nd < dist[a, b]:
                    dist[a, b] = nd
                    prev[(a, b)] = (x, z)
                    heapq.heappush(pq, (nd, a, b))
        path = [(tx, tz)]
        while path[-1] != (sx, sz):
            path.append(prev[path[-1]])
        path.reverse()
        pts = [(p[0] * step + step / 2 + X0, p[1] * step + step / 2 + X0) for p in path]
        # glad maken (Chaikin) en kronkelen
        for _ in range(3):
            new = [pts[0]]
            for (ax, az), (bx, bz) in zip(pts, pts[1:]):
                new += [(0.75 * ax + 0.25 * bx, 0.75 * az + 0.25 * bz), (0.25 * ax + 0.75 * bx, 0.25 * az + 0.75 * bz)]
            new.append(pts[-1])
            pts = new
        out = []
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(bx - ax, bz - az)))
            for i in range(n):
                out.append((ax + (bx - ax) * i / n, az + (bz - az) * i / n))
        out.append(pts[-1])
        return out

    def carve_rivers(self):
        specs = [
            # naam, bron, monding, breedte begin/eind, max insnijding, kloof
            ("A", (-92, -78), self.sites["mouthA"], 1.6, 4.5, 7, False, []),
            ("B", (6, -96), self.sites["mouthB"], 1.4, 3.5, 99, True, []),
            ("C", (-70, -34), self.sites["mouthC"], 1.2, 3.0, 5, False, [(-66, 40), (-50, 130)]),
        ]
        e = self.e
        self.river_d = np.full(e.shape, np.inf)
        self.river_L = np.full(e.shape, -999, dtype=np.int32)
        self.river_w = np.zeros(e.shape)
        self.canyon = np.zeros(e.shape, dtype=bool)
        for name, src, mouth, w0, w1, maxinc, canyon, via in specs:
            stops = [src] + via + [mouth]
            pts = []
            for a, b in zip(stops, stops[1:]):
                part = self.least_cost_path(a, b)
                pts += part if not pts else part[1:]
            n = len(pts)
            # kronkels
            mx = []
            for i, (x, z) in enumerate(pts):
                off = 3.0 * math.sin(i / 23.0 + len(name)) * min(1.0, i / 30) * min(1.0, (n - i) / 30)
                if i + 1 < n:
                    tx, tz = pts[i + 1][0] - x, pts[i + 1][1] - z
                    ln = math.hypot(tx, tz) or 1
                    x, z = x - tz / ln * off, z + tx / ln * off
                mx.append((x, z))
            pts = mx
            ev = [float(e[int(round(x)) - X0, int(round(z)) - X0]) for x, z in pts]
            L = []
            cur = math.floor(ev[0]) - 2
            for i, v in enumerate(ev):
                frac = i / max(1, n - 1)
                if canyon:
                    # bron, dan een grote waterval de kloof in, daarna rustig naar zee
                    target = SEA + max(0, int(12 * (1 - frac)))
                    if i < 18:
                        cur = min(cur, math.floor(v) - 2)
                    else:
                        cur = min(cur, max(target, SEA))
                else:
                    want = math.floor(v) - 2
                    if want < cur - maxinc or (want < cur and cur - want >= 1 and v < SEA + 4):
                        cur = want
                    cur = max(cur, SEA)
                if i > n - 6:
                    cur = SEA
                L.append(max(cur, SEA))
            widths = [w0 + (w1 - w0) * (i / max(1, n - 1)) for i in range(n)]
            for i in range(1, n):
                if L[i - 1] - L[i] >= 4:
                    for j in range(i, min(n, i + 6)):
                        widths[j] += 2.0
            self.rivers.append(dict(name=name, pts=pts, L=L, w=widths, canyon=canyon))
            for i, (x, z) in enumerate(pts):
                w = widths[i]
                lb = max(L[max(0, i - 6):i + 7])
                R = int(w + (5 if canyon else 14))
                cx, cz = int(round(x)), int(round(z))
                for a in range(cx - R, cx + R + 1):
                    for b in range(cz - R, cz + R + 1):
                        if not self.inb(a, b):
                            continue
                        ia, ib = a - X0, b - X0
                        d = math.hypot(a - x, b - z)
                        if d > R:
                            continue
                        if d < self.river_d[ia, ib]:
                            self.river_d[ia, ib] = d
                            self.river_L[ia, ib] = L[i]
                            self.river_w[ia, ib] = w
                        if self.dc[ia, ib] <= 0:
                            continue
                        if d <= w:
                            continue
                        if canyon and e[ia, ib] > L[i] + 8:
                            if d <= w + 2.5:
                                e[ia, ib] = lb
                                self.canyon[ia, ib] = True
                            elif d <= w + 5:
                                self.canyon[ia, ib] = True
                        else:
                            vmax = lb + (d - w) * 1.25
                            e[ia, ib] = min(max(e[ia, ib], lb), vmax) if e[ia, ib] > lb else lb
        # water in de bedding
        wet = self.river_d <= self.river_w
        depth = 1 + np.round(2 * np.clip(1 - self.river_d / np.maximum(self.river_w, 0.1), 0, 1))
        self.river_wet = wet & (self.dc > -2)
        e[self.river_wet] = self.river_L[self.river_wet] - depth[self.river_wet]

    # ---------------------------------------------------------------- zones
    def finalize(self):
        e, X, Z, sd = self.e, self.X, self.Z, self.seed
        H = np.floor(e).astype(np.int32)
        land = self.dc > 0
        motu = np.zeros(H.shape, dtype=bool)
        for mx, mz, mr in self.motus:
            motu |= np.hypot(X - mx, Z - mz) < mr
        land |= motu & (H >= SEA)
        H = np.where(land & ~self.river_wet, np.maximum(H, SEA), H)
        H = np.clip(H, YMIN + 2, TOP - 8)
        self.H = H
        self.res = np.zeros(H.shape, dtype=bool)
        self.road = np.zeros(H.shape, dtype=bool)
        # helling
        pad = np.pad(H, 1, mode="edge")
        lo = np.minimum.reduce([pad[2:, 1:-1], pad[:-2, 1:-1], pad[1:-1, 2:], pad[1:-1, :-2]])
        self.slope = H - lo
        z = np.full(H.shape, RAINFOREST, dtype=np.uint8)
        hh = H - SEA
        bw = 11 + 6 * fbm(X / 30, Z / 30, sd + 10, 2)
        vx, vz = self.volcano["x"], self.volcano["z"]
        near_volcano = np.hypot(X - vx, Z - vz) < 150
        z[(hh > 34)] = HIGHLAND
        z[(hh > 62)] = PEAK
        bamboo = (fbm(X / 34, Z / 34, sd + 11, 3) > 0.33) & (hh < 30)
        z[bamboo] = BAMBOO
        meadow = (fbm(X / 45, Z / 45, sd + 12, 3) > 0.38) & (hh > 8) & (hh < 34)
        z[meadow] = MEADOW
        beach = land & (self.dc < bw) & (hh <= 4) & (self.cliffw < 0.5)
        z[beach] = BEACH
        z[beach & near_volcano] = BLACKBEACH
        z[self.vmask & land] = VOLCANIC
        dv = np.hypot(X - vx, Z - vz)
        z[dv < 82 * 0.13] = CRATER
        z[(self.slope >= 4) & land & (z != CRATER)] = CLIFF
        for name, cx, cz, r, g in self.flat_sites:
            d = np.hypot(X - cx, Z - cz) + 7 * fbm(X / 14, Z / 14, sd + 14, 2)
            m = (d < r * 0.75) & land
            if name == "plantation":
                z[m] = PLANTATION
            elif name == "ranch":
                z[m] = MEADOW
            elif name == "village":
                z[m & (z != BEACH)] = VILLAGE
            elif name == "town":
                z[m & (z != BEACH)] = TOWN
        bank = (self.river_d <= self.river_w + 3) & land & ~self.river_wet
        z[bank & (z != CLIFF)] = RIVERBANK
        z[self.canyon] = CANYON
        z[motu & (H >= SEA)] = MOTU
        z[~land & self.lagoon_mask] = LAGOON
        z[~land & self.reef_mask] = REEF
        z[~land & ~self.lagoon_mask & ~self.reef_mask] = DEEP
        z[self.river_wet & land] = RIVERBANK
        self.zone = z
        # vloeistoffen: rivier/kratermeer boven zeeniveau zit in de structuur, zee eronder via fill
        self.liq_top = np.full(H.shape, -999, dtype=np.int32)
        self.liq_lava = np.zeros(H.shape, dtype=bool)
        rw = self.river_wet & land
        self.liq_top[rw] = self.river_L[rw]
        crater = z == CRATER
        lava = crater & (H < self.volcano["lava"])
        self.liq_top[lava] = self.volcano["lava"]
        self.liq_lava[lava] = True

    def after_planning(self):
        """Na het plannen van gebouwen: oevers weer minstens op waterhoogte en de helling opnieuw berekenen."""
        bank = (self.river_d <= self.river_w + 2.5) & ~self.river_wet & (self.dc > 0)
        self.H = np.where(bank, np.maximum(self.H, self.river_L), self.H)
        pad = np.pad(self.H, 1, mode="edge")
        lo = np.minimum.reduce([pad[2:, 1:-1], pad[:-2, 1:-1], pad[1:-1, 2:], pad[1:-1, :-2]])
        self.slope = self.H - lo

    def water_top(self, x, z):
        """Hoogste waterblok op deze kolom (of None)."""
        ix, iz = x - X0, z - X0
        if self.liq_top[ix, iz] > -999 and not self.liq_lava[ix, iz]:
            return int(self.liq_top[ix, iz])
        if self.H[ix, iz] < SEA:
            return SEA
        return None
