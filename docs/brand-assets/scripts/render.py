"""Exact raster compositing of the mark from coverage masks (no AA conflation seams or halos)."""
import io
import numpy as np
import resvg_py
from PIL import Image
import build_svg as B

NAVY = (0x2E, 0x35, 0x91)
WHITE = np.array([255, 255, 255], dtype=np.float64)


def cov(svg, n):
    """Render an SVG string at n x n and return its alpha coverage in 0..1."""
    a = np.array(Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg, width=n, height=n))).convert('RGBA'))[..., 3]
    return a.astype(np.float64) / 255.0


def shape_svg(d):
    return B.HEAD + '  <path fill="#000" d="%s"/>\n</svg>\n' % d


def stroke_svg(w):
    """Inner contour stroked (width w in 512-units), clipped to the silhouette."""
    return B.HEAD + ('  <clipPath id="c"><path d="%s"/></clipPath>\n'
                     '  <path clip-path="url(#c)" fill="none" stroke="#000" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round" d="%s"/>\n</svg>\n'
                     ) % (B.outline_d, B.f(w), B.inner_d)


def keyline(n):
    """White keyline width (px) round the transparent icons: max(1 px, 1.5 % of the size)."""
    return max(1.0, 0.015 * n)


def scaled(t, s, body):
    return B.HEAD + '<g transform="translate(%s %s) scale(%s)">%s</g></svg>' % (B.f(t), B.f(t), B.f(s), body)


def mark_keyline(n, widen_px, k, col):
    """Transparent mark with a white keyline k px wide just outside the silhouette (a round-joined stroke of the
    silhouette); the mark shrinks so the keyline fits the canvas. Makes the disc's edge visible on dark backgrounds."""
    s = (n - 2 * k) / n; t = (1 - s) / 2 * 512
    fill = lambda d: '<path fill="#000" d="%s"/>' % d
    o = cov(scaled(t, s, fill(B.outline_d)), n)
    nv = cov(scaled(t, s, fill(B.navy_d)), n)
    if widen_px > 0:  # same erosion as stroke_svg, in the scaled group (stroke widths in 512-units shrink with s)
        nv = np.clip(nv - cov(scaled(t, s, '<clipPath id="c"><path d="%s"/></clipPath><path clip-path="url(#c)" fill="none" '
                                              'stroke="#000" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round" d="%s"/>'
                                              % (B.outline_d, B.f(2 * widen_px * 512 / (n * s)), B.inner_d)), n), 0, 1)
    dil = cov(scaled(t, s, '<path fill="#000" stroke="#000" stroke-width="%s" stroke-linejoin="round" d="%s"/>'
                     % (B.f(2 * k * 512 / (n * s)), B.outline_d)), n)
    nv = np.minimum(nv, o); w = np.clip(o - nv, 0, 1); a = np.maximum(dil, o)
    pre = nv[..., None] * col + (w + (a - o))[..., None] * WHITE  # cutouts and keyline white
    rgb = np.where(a[..., None] > 0, pre / np.maximum(a[..., None], 1e-9), 0)
    return Image.fromarray(np.round(np.clip(np.dstack([rgb, a * 255]), 0, 255)).astype(np.uint8), 'RGBA')


def mark(n, widen_px=0.0, scale=1.0, bg=None, color=NAVY, keyline_px=0.0):
    """RGBA uint8 n x n image of the white-filled mark in `color`.
    widen_px: widen the white cutouts by this many px (at size n) by eroding the colour along the inner contour.
    scale: mark size as a fraction of n (centred). bg: None (transparent) or (r,g,b) opaque background.
    keyline_px: white keyline outside the silhouette (transparent icons only; see mark_keyline)."""
    col = np.array(color, dtype=np.float64)
    if keyline_px > 0:
        assert scale == 1.0 and bg is None
        return mark_keyline(n, widen_px, keyline_px, col)
    if scale != 1.0:
        t = (1 - scale) / 2 * 512
        g = lambda d: '<g transform="translate(%s %s) scale(%s)"><path fill="#000" d="%s"/></g>' % (B.f(t), B.f(t), B.f(scale), d)
        o = cov(B.HEAD + g(B.outline_d) + '</svg>', n)
        nv = cov(B.HEAD + g(B.navy_d) + '</svg>', n)
        assert widen_px == 0
    else:
        o = cov(shape_svg(B.outline_d), n)
        nv = cov(shape_svg(B.navy_d), n)
        if widen_px > 0:
            s = cov(stroke_svg(2 * widen_px * 512 / n), n)  # stroke straddles the contour: width = 2*widen
            nv = np.clip(nv - s, 0, 1)
    nv = np.minimum(nv, o)
    w = np.clip(o - nv, 0, 1)
    pre = nv[..., None] * col + w[..., None] * WHITE  # premultiplied by alpha = o
    if bg is None:
        a = o
        rgb = np.where(a[..., None] > 0, pre / np.maximum(a[..., None], 1e-9), 0)
        out = np.dstack([rgb, a * 255])
    else:
        rgb = pre + (1 - o)[..., None] * np.array(bg, dtype=np.float64)
        out = np.dstack([rgb, np.full_like(o, 255)])
    return Image.fromarray(np.round(np.clip(out, 0, 255)).astype(np.uint8), 'RGBA')


def mono(n, color=NAVY, scale=1.0):
    """Single colour, transparent cutouts. scale: mark size as a fraction of n (centred)."""
    t = (1 - scale) / 2 * 512
    nv = cov(shape_svg(B.navy_d) if scale == 1.0 else scaled(t, scale, '<path fill="#000" d="%s"/>' % B.navy_d), n)
    out = np.dstack([np.broadcast_to(np.array(color, dtype=np.float64), nv.shape + (3,)), nv[..., None] * 255])
    return Image.fromarray(np.round(out).astype(np.uint8), 'RGBA')
