"""Gevectoriseerde value-noise (numpy) voor het eiland."""
import numpy as np

M32 = np.uint64(0xFFFFFFFF)


def _hash(ix, iz, seed):
    ix = ix.astype(np.int64).astype(np.uint64)
    iz = iz.astype(np.int64).astype(np.uint64)
    h = (ix * np.uint64(374761393) + iz * np.uint64(668265263) + np.uint64(seed * 982451653 & 0xFFFFFFFF)) & M32
    h = ((h ^ (h >> np.uint64(13))) * np.uint64(1274126177)) & M32
    h ^= h >> np.uint64(16)
    return (h & np.uint64(0xFFFF)).astype(np.float64) / 32767.5 - 1.0


def vnoise(x, z, seed):
    x = np.asarray(x, dtype=np.float64)
    z = np.asarray(z, dtype=np.float64)
    ix, iz = np.floor(x), np.floor(z)
    fx, fz = x - ix, z - iz
    sx, sz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a = _hash(ix, iz, seed)
    b = _hash(ix + 1, iz, seed)
    c = _hash(ix, iz + 1, seed)
    d = _hash(ix + 1, iz + 1, seed)
    top = a + (b - a) * sx
    bot = c + (d - c) * sx
    return top + (bot - top) * sz


def fbm(x, z, seed, octaves=4, lac=2.0, gain=0.5):
    total = np.zeros(np.broadcast(np.asarray(x), np.asarray(z)).shape)
    amp, freq, norm = 1.0, 1.0, 0.0
    for o in range(octaves):
        total += amp * vnoise(np.asarray(x) * freq, np.asarray(z) * freq, seed + 101 * o)
        norm += amp
        amp *= gain
        freq *= lac
    return total / norm


def ridged(x, z, seed, octaves=5):
    """Scherpe bergkammen: 1 - |noise|, gestapeld."""
    total = np.zeros(np.broadcast(np.asarray(x), np.asarray(z)).shape)
    amp, freq, norm = 1.0, 1.0, 0.0
    for o in range(octaves):
        n = 1.0 - np.abs(vnoise(np.asarray(x) * freq, np.asarray(z) * freq, seed + 37 * o))
        total += amp * n * n
        norm += amp
        amp *= 0.5
        freq *= 2.1
    return total / norm


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)
