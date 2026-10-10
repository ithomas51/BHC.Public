"""Render the BH lockups (banner + stacked) from their SVG sources with exact coverage-mask compositing."""
import io, os, re
import numpy as np
import resvg_py
from PIL import Image
from parse import parse_d, bez, fit
from paths import LOCKUP_DIR

NAVY = np.array([0x2E, 0x35, 0x91], float); BLACK = np.zeros(3); WHITE = np.full(3, 255.0)
# the original PNGs were rendered from the *_reversed.svg geometry (the *_black.svg files are offset ~1.6 units)
BANNER = os.path.join(LOCKUP_DIR, 'BH_reversed.svg')
STACKED = os.path.join(LOCKUP_DIR, 'BH stacked_reversed.svg')


def f(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')


def seg_str(s):
    return 'C' + ' '.join(f(c) for p in s[1:] for c in p)


OUTER = [24, 25, 26, 0, 1, 2, 3]


def silhouette_d(segs):
    """Closed outline of the mark: outer-arc segments + arc of the fitted circle across the left gap."""
    assert len(segs) == 27, len(segs)
    pts = np.vstack([bez(segs[k], np.linspace(0, 1, 50)) for k in OUTER])
    cx, cy, r = fit(pts)
    dev = np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r).max()
    assert dev < 0.01 * r, dev
    d = 'M' + ' '.join(f(c) for c in segs[OUTER[0]][0]) + ''.join(seg_str(segs[k]) for k in OUTER)
    e = segs[24][0]
    return d + 'A%s %s 0 0 1 %s %sZ' % (f(r), f(r), f(e[0]), f(e[1]))


def load_svg(path):
    """(viewBox, mark path d, [wordmark path d, ...])"""
    t = open(path, encoding='utf-8').read()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', t).group(1).split()]
    paths = re.findall(r'<path[^>]*\sd="([^"]+)"', t)
    mark = [d for d in paths if ('c1.044,6.88' in d.replace(' ', '') or 'c.63,4.152' in d.replace(' ', ''))]
    assert len(mark) == 1, 'mark path not identified'
    text = [d for d in paths if d is not mark[0]]
    return vb, mark[0], text


def svg_of(vb, body, w, h):
    # uniform scale: the viewBox is padded symmetrically to the canvas aspect, so the content is centred and never stretched
    x, y, W, H = vb
    if W / H > w / h:
        H2 = W * h / w; y -= (H2 - H) / 2; H = H2
    else:
        W2 = H * w / h; x -= (W2 - W) / 2; W = W2
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%s %s %s %s">%s</svg>' % (
        w, h, f(x), f(y), f(W), f(H), body)


def cov(vb, body, w, h):
    im = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg_of(vb, body, w, h)))).convert('RGBA')
    assert im.size == (w, h), im.size
    return np.array(im)[..., 3].astype(float) / 255.0


def render(src, w, h, filled=False, vb=None, mark_colour=NAVY, text_colour=BLACK):
    """RGBA (w x h): mark and wordmark (default navy / black). filled: mark cutouts filled white.
    vb: viewBox override (default: the file's)."""
    vb0, mark_d, text_ds = load_svg(src)
    vb = vb or vb0
    m = cov(vb, '<path d="%s"/>' % mark_d, w, h)
    t = cov(vb, ''.join('<path d="%s"/>' % d for d in text_ds), w, h)
    layers = [(m, mark_colour), (t, text_colour)]
    if filled:
        s = cov(vb, '<path d="%s"/>' % silhouette_d(parse_d(mark_d)), w, h)
        s = np.maximum(s, m)
        layers = [(np.clip(s - m, 0, 1), WHITE)] + layers
    # premultiplied accumulation; layers do not overlap (white only where navy is absent), so straight sum is exact
    pre = np.zeros((h, w, 3)); a = np.zeros((h, w))
    for c, colour in layers:
        pre += c[..., None] * colour; a += c
    a = np.clip(a, 0, 1)
    rgb = np.where(a[..., None] > 0, pre / np.maximum(a[..., None], 1e-9), 0)
    out = np.dstack([rgb, a * 255])
    out = np.round(np.clip(out, 0, 255)).astype(np.uint8)
    out[out[..., 3] < 8] = 0  # no stray fringe pixels (0 < alpha < 8)
    return Image.fromarray(out, 'RGBA')
