"""The mark in a square 512 viewBox: its path, its closed silhouette, and the master / mono / maskable SVG strings."""
import numpy as np
from parse import load, bez, fit

NAVY = '#2E3591'
segs = load()
allp = np.vstack([bez(s, np.linspace(0, 1, 200)) for s in segs])
mn = allp.min(0); mx = allp.max(0); ext = (mx - mn); S = 512 / ext.max()
off = (512 - ext * S) / 2


def T(p):
    return ((p[0] - mn[0]) * S + off[0], (p[1] - mn[1]) * S + off[1])


def f(v):
    return ('%.3f' % v).rstrip('0').rstrip('.')


def seg_str(s):
    return 'C' + ' '.join(f(c) for p in s[1:] for c in T(p))


def path_d(idx, close=True):
    d = 'M' + ' '.join(f(c) for c in T(segs[idx[0]][0]))
    d += ''.join(seg_str(segs[k]) for k in idx)
    return d + ('Z' if close else '')


OUTER = [24, 25, 26, 0, 1, 2, 3]
INNER = list(range(4, 24))
cx, cy, r = fit(np.vstack([bez(segs[k], np.linspace(0, 1, 50)) for k in OUTER]))
R = r * S
navy_d = path_d([24, 25, 26] + list(range(0, 24)))
gap_end = T(segs[24][0])
# closed silhouette: the outer arc segments, closed across the left gap with an arc of the fitted circle
outline_d = path_d(OUTER, close=False) + 'A%s %s 0 0 1 %s %sZ' % (f(R), f(R), f(gap_end[0]), f(gap_end[1]))
inner_d = path_d(INNER, close=False)


def sub(s, t0, t1):
    """Sub-curve of cubic s on [t0,t1] (de Casteljau)."""
    P = np.array(s, dtype=float)
    def split(P, t):
        a = P[0] + (P[1] - P[0]) * t; b = P[1] + (P[2] - P[1]) * t; c = P[2] + (P[3] - P[2]) * t
        d = a + (b - a) * t; e = b + (c - b) * t; m = d + (e - d) * t
        return np.array([P[0], a, d, m]), np.array([m, e, c, P[3]])
    _, R = split(P, t0)
    L, _ = split(R, (t1 - t0) / (1 - t0) if t0 < 1 else 0)
    return [tuple(p) for p in L]


# inner contour trimmed short of the two junctions with the outer edge (for the SVG under-stroke)
_trim = [sub(segs[4], 0.02, 1.0)] + [segs[k] for k in range(5, 23)] + [sub(segs[23], 0.0, 0.98)]
inner_trim_d = 'M' + ' '.join(f(c) for c in T(_trim[0][0])) + ''.join(seg_str(s) for s in _trim)
# white cutouts = silhouette minus navy, as one even-odd compound path (edges coincide exactly: no halo)
cut_d = outline_d + navy_d

HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">\n'
# 3-unit white under-stroke along the inner contour, drawn BELOW the colour: removes the translucent AA seam where the
# white cutout and the colour abut. Trimmed short of the outer edge, so it can never halo.
UNDER = '<path fill="none" stroke="#FFFFFF" stroke-width="%s" stroke-linejoin="round" stroke-linecap="butt" d="%s"/>'


def master(color=NAVY):
    """White-filled master, transparent outside."""
    return (HEAD + '  <path fill="#FFFFFF" fill-rule="evenodd" d="%s"/>\n' % cut_d + '  ' + UNDER % ('3', inner_trim_d) + '\n'
            + '  <path fill="%s" d="%s"/>\n' % (color, navy_d) + '</svg>\n')


def mono(color=NAVY):
    return HEAD + '  <path fill="%s" d="%s"/>\n</svg>\n' % (color, navy_d)


def maskable(bg='#FFFFFF', frac=0.80):
    """Master at `frac` on a full-bleed `bg` square (Android maskable safe zone)."""
    t = (1 - frac) / 2 * 512
    return (HEAD + '  <rect width="512" height="512" fill="%s"/>\n  <g transform="translate(%s %s) scale(%s)">\n'
            '    <path fill="#FFFFFF" fill-rule="evenodd" d="%s"/>\n    %s\n    <path fill="%s" d="%s"/>\n  </g>\n</svg>\n'
            ) % (bg, f(t), f(t), f(frac), cut_d, UNDER % (f(3.0 / frac), inner_trim_d), NAVY, navy_d)


def outline():
    return HEAD + '  <path fill="#000" d="%s"/>\n</svg>\n' % outline_d
