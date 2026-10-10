"""SVG path parsing into cubic segments, cubic evaluation, least-squares circle fit."""
import re
import numpy as np
from paths import MARK_SVG


def parse_d(d):
    """Cubic segments [(p0, p1, p2, p3), ...] of a path made of an absolute M and relative c commands."""
    toks = re.findall(r'[MmCcLlZzHhVvSs]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cur = None; segs = []; cmd = None
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t): cmd = t; i += 1; continue
        if cmd == 'M':
            cur = (float(toks[i]), float(toks[i + 1])); i += 2; cmd = 'L'
        elif cmd == 'c':
            v = [float(x) for x in toks[i:i + 6]]; i += 6
            p1 = (cur[0] + v[0], cur[1] + v[1]); p2 = (cur[0] + v[2], cur[1] + v[3]); p3 = (cur[0] + v[4], cur[1] + v[5])
            segs.append((cur, p1, p2, p3)); cur = p3
        else:
            raise ValueError('unsupported command %r in mark path' % cmd)
    return segs


def load(fn=MARK_SVG):
    return parse_d(re.search(r' d="([^"]+)"', open(fn).read()).group(1))


def bez(s, t):
    P = np.array(s); t = np.asarray(t)[:, None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


def fit(P):
    A = np.c_[2 * P, np.ones(len(P))]; b = (P ** 2).sum(1)
    c = np.linalg.lstsq(A, b, rcond=None)[0]; r = np.sqrt(c[2] + c[0] ** 2 + c[1] ** 2); return c[0], c[1], r
