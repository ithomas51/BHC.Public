"""lockups/banner and lockups/stacked: banner and stacked lockups (navy mark, black wordmark), transparent and
white-filled, plus an all-white set for dark backgrounds; and the stacked Google Workspace logo in
google-workspace/admin-logo."""
import numpy as np
from PIL import Image
import lockup as L
from paths import LOCKUP_BANNER, LOCKUP_STACKED, ADMIN_LOGO, out

BANNER_W = [256, 512, 600, 800, 1200, 1600, 2400, 3600]
STACKED_W = [256, 384, 512, 768, 1024, 1280, 1536, 1920, 2048, 2560, 3840, 4096]
BANNER_H = {256: 42, 512: 84}  # legacy sizes kept from the originals (the viewBox aspect gives 41 / 83)
# for dark backgrounds: mark and wordmark white, cutouts transparent (the background shows through them)
ON_DARK = dict(mark_colour=L.WHITE, text_colour=L.WHITE)
# google_workspace_logo: 320x132 canvas, stacked content 121 px wide centred on the original's box (102,8)-(223,125)
GWS_SIZE = (320, 132); GWS_BOX = (102, 8, 223, 125)


def bbox(im):
    a = np.array(im)[..., 3]; ys, xs = np.where(a > 0)
    return (int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1))


def build(root):
    vb_b = L.load_svg(L.BANNER)[0]; vb_s = L.load_svg(L.STACKED)[0]
    bh = lambda w: BANNER_H.get(w, int(round(w * vb_b[3] / vb_b[2])))
    sh = lambda w: int(round(w * vb_s[3] / vb_s[2]))
    for w in BANNER_W:
        h = bh(w)
        L.render(L.BANNER, w, h).save(out(root, LOCKUP_BANNER, 'BH_reversed_%dx%d.png' % (w, h)))
        L.render(L.BANNER, w, h, filled=True).save(out(root, LOCKUP_BANNER, 'BH_reversed_filled_%dx%d.png' % (w, h)))
        L.render(L.BANNER, w, h, **ON_DARK).save(out(root, LOCKUP_BANNER, 'BH_white_%dx%d.png' % (w, h)))
    for w in STACKED_W:
        h = sh(w)
        L.render(L.STACKED, w, h).save(out(root, LOCKUP_STACKED, 'BH_stacked_reversed_%dw.png' % w))
        L.render(L.STACKED, w, h, filled=True).save(out(root, LOCKUP_STACKED, 'BH_stacked_reversed_filled_%dw.png' % w))
        L.render(L.STACKED, w, h, **ON_DARK).save(out(root, LOCKUP_STACKED, 'BH_stacked_white_%dw.png' % w))
    # content width at stacked width W is W * 800/1024 (measured): render at that W, crop to the content, centre on the box
    cw = GWS_BOX[2] - GWS_BOX[0]
    W = int(round(cw * 1024 / 800)); H = sh(W)
    for filled, name in ((False, 'google_workspace_logo.png'), (True, 'google_workspace_logo_filled.png')):
        r = L.render(L.STACKED, W, H, filled=filled)
        content = r.crop(bbox(r))
        canvas = Image.new('RGBA', GWS_SIZE, (0, 0, 0, 0))
        cx = (GWS_BOX[0] + GWS_BOX[2]) / 2 - content.size[0] / 2; cy = (GWS_BOX[1] + GWS_BOX[3]) / 2 - content.size[1] / 2
        canvas.alpha_composite(content, (int(round(cx)), int(round(cy))))
        canvas.save(out(root, ADMIN_LOGO, name))
