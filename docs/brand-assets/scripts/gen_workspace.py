"""google-workspace/admin-logo: Admin console logo (Google displays it at exactly 320x132) from the BANNER lockup,
white-filled, 304 px wide (8 px side clear space), centred; plus the same layout at 3x."""
import numpy as np
import lockup as L
from paths import ADMIN_LOGO, out

CANVAS = (320, 132); CONTENT_W = 304
SCALES = {'BH_google_workspace_logo_320x132.png': 1, 'BH_google_workspace_logo_960x396_3x.png': 3}


def content_box():
    """Exact union bbox of mark + wordmark in SVG units, measured at high resolution."""
    vb, mark_d, text_ds = L.load_svg(L.BANNER)
    HW = 16000; HH = int(round(HW * vb[3] / vb[2]))
    a = L.cov(vb, '<path d="%s"/>' % mark_d + ''.join('<path d="%s"/>' % d for d in text_ds), HW, HH)
    ys, xs = np.nonzero(a > 0)
    u = vb[2] / HW
    bx0, bx1 = vb[0] + xs.min() * u, vb[0] + (xs.max() + 1) * u
    by0, by1 = vb[1] + ys.min() * u, vb[1] + (ys.max() + 1) * u
    return bx0, by0, bx1 - bx0, by1 - by0


def build(root):
    bx0, by0, cw, ch = content_box()
    for fn, sc in SCALES.items():
        W, H = CANVAS[0] * sc, CANVAS[1] * sc
        s = CONTENT_W * sc / cw                    # px per unit, uniform
        vw, vh = W / s, H / s                      # viewBox with the canvas aspect: no padding, no stretch
        vb = (bx0 + cw / 2 - vw / 2, by0 + ch / 2 - vh / 2, vw, vh)
        L.render(L.BANNER, W, H, filled=True, vb=vb).save(out(root, ADMIN_LOGO, fn), optimize=True)
