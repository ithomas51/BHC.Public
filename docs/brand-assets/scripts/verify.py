"""Verify the landing (docs\\brand-assets, or the root given as argv[1]). Ends with ALL OK or PROBLEMS.
1. Vector check: regenerate everything from vector into a temp folder; every landing file must be pixel-identical (PNG)
   or byte-identical (ICO; SVG up to line endings) to its fresh render, with nothing missing and nothing unexpected.
2. Property checks per folder: sizes, modes, fills, halo / seam, fringe, palette, circular crop, file-size limits."""
import sys
sys.dont_write_bytecode = True
import io, json, os, re, shutil, struct, tempfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import resvg_py
import build_all
import build_svg as B
import gen_3a4d5c as G3
import gen_icons as GI
import gen_lockups as GL
import gen_mobile as GM
import lockup as L
import render as R
from paths import (ROOT, WIN_APP, WIN_TILES, WIN_FOLDER, WEB, PLAY, ANDROID_RES, IOS_ICONSET, VECTOR, PROFILE, ADMIN_LOGO,
                   LOCKUP_BANNER, LOCKUP_STACKED)

root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT
ok = True


def at(folder, name):
    return os.path.join(root, *folder.split('/'), name)


def fail(msg):
    global ok; ok = False; print('FAIL', msg)


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok &= bool(cond)


def rgba(path):
    return np.array(Image.open(path).convert('RGBA')).astype(int)


def on_segment(rgb, a, b, tol=0.02):
    """True per pixel when rgb lies on the straight line between colours a and b (a blend of the two, nothing else)."""
    a = np.array(a, float); b = np.array(b, float); t = (rgb - a) / (b - a)
    return np.abs(t - t.mean(1, keepdims=True)).max(1) < tol


def files_under(d):
    return {os.path.relpath(os.path.join(p, f), d).replace('\\', '/') for p, _, fs in os.walk(d) for f in fs}


def mark_cov(n, scale):
    """Coverage of the mark's silhouette at `scale` of an n x n canvas, centred."""
    t = (1 - scale) / 2 * 512
    g = '<g transform="translate(%s %s) scale(%s)"><path fill="#000" d="%s"/></g>' % (B.f(t), B.f(t), B.f(scale), B.outline_d)
    return R.cov(B.HEAD + g + '</svg>', n)


# ---------------------------------------------------------------- 1. vector check
print('== 1. vector check: fresh render from vector vs landing', root)
tmp = tempfile.mkdtemp(prefix='bhc-vector-')
try:
    build_all.build(tmp)
    fresh, land = files_under(tmp), files_under(root)
    extra_ok = lambda p: p.endswith('.md') or p.startswith('scripts/')  # docs and the pipeline itself
    missing = sorted(fresh - land); unexpected = sorted(p for p in land - fresh if not extra_ok(p))
    check(not missing, 'no generated file missing from the landing %s' % (missing or ''))
    check(not unexpected, 'no unexpected file in the landing %s' % (unexpected or ''))
    same = 0
    for p in sorted(fresh & land):
        a, b = os.path.join(tmp, p), os.path.join(root, p)
        if p.endswith('.png'):
            ia, ib = Image.open(a), Image.open(b)
            eq = ia.size == ib.size and ia.mode == ib.mode and np.array_equal(np.array(ia), np.array(ib))
        elif p.endswith(('.svg', '.xml', '.json', '.webmanifest', '.ini')):  # text in git: ignore checkout line endings
            eq = open(a, 'rb').read().replace(b'\r\n', b'\n') == open(b, 'rb').read().replace(b'\r\n', b'\n')
        else:
            eq = open(a, 'rb').read() == open(b, 'rb').read()
        if eq: same += 1
        else: fail('%s differs from its fresh vector render' % p)
    check(same == len(fresh), '%d of %d generated files identical to a fresh vector render' % (same, len(fresh)))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------------------------------------------------------------- 2a. bhc-wb icon set (windows, web, mobile, vector)
print('\n== 2a. bhc-wb icon set: windows / web / mobile / vector')


def P(n):
    """Folder of an icon-set file by name."""
    if n.endswith('.svg'): return at(VECTOR, n)
    if n.startswith('bhc-wb-tile'): return at(WIN_TILES, n)
    if n == 'bhc-wb-folder.ico': return at(WIN_FOLDER, n)
    if n.startswith('bhc-wb-'): return at(WIN_APP, n)
    if n.startswith('play-store'): return at(PLAY, n)
    return at(WEB, n)  # favicon*, apple-touch, android-chrome, maskable, manifest

for name in ('bhc-wb-gui.ico', 'bhc-wb-folder.ico', 'favicon.ico'):
    b = open(P(name), 'rb').read()
    _, typ, n = struct.unpack('<HHH', b[:6]); ents = []
    for i in range(n):
        w, h, cc, r, planes, bpp, size, off = struct.unpack('<BBBBHHII', b[6 + 16 * i:22 + 16 * i])
        w = w or 256; h = h or 256
        data = b[off:off + size]
        kind = 'PNG' if data[:8] == b'\x89PNG\r\n\x1a\n' else 'BMP'
        if kind == 'BMP':
            bpp = struct.unpack('<IiiHHI', data[:20])[4]
        ents.append('%dx%d %d-bit %s' % (w, h, bpp, kind))
    print(name, ':', ', '.join(ents))
    ico = Image.open(P(name)); diff = []
    for s in sorted(ico.info['sizes']):
        ico.size = s; ico.load()
        if not np.array_equal(np.array(ico.convert('RGBA')), np.array(Image.open(P('bhc-wb-%d.png' % s[0])).convert('RGBA'))):
            diff.append(s)
    check(not diff, '%s: every entry identical to its bhc-wb-N.png %s' % (name, diff or ''))
    if name != 'favicon.ico':
        got = sorted(s[0] for s in ico.info['sizes'])
        check(got == GI.ICO_SIZES, '%s: sizes %s (Microsoft 16-256 set incl. 30 / 36 / 60 / 72 / 80)' % (name, got))
ini = open(at(WIN_FOLDER, 'desktop.ini'), 'rb').read()
check(ini.startswith(b'[.ShellClassInfo]') and b'IconResource=' in ini and b'bhc-wb-folder.ico,0' in ini,
      'windows/folder/desktop.ini: [.ShellClassInfo] IconResource template for bhc-wb-folder.ico')

expect = {}
for s in GI.ICO_SIZES: expect['bhc-wb-%d.png' % s] = (s, s, False)
for s in (44, 71, 150, 310): expect['bhc-wb-tile-%dx%d.png' % (s, s)] = (s, s, False)
expect['bhc-wb-tile-310x150.png'] = (310, 150, False)
for s in (16, 32, 48): expect['favicon-%d.png' % s] = (s, s, False)
expect['apple-touch-icon-180.png'] = (180, 180, True); expect['apple-touch-icon.png'] = (180, 180, True)
expect['android-chrome-192.png'] = (192, 192, False); expect['android-chrome-512.png'] = (512, 512, False)
expect['maskable-512.png'] = (512, 512, True); expect['play-store-512.png'] = (512, 512, True)
bad = []
for fn, (w, h, opaque) in expect.items():
    im = Image.open(P(fn)); a = np.array(im.convert('RGBA'))[..., 3]
    if im.size != (w, h) or im.mode != 'RGBA': bad.append('%s %s %s' % (fn, im.size, im.mode))
    if opaque and a.min() != 255: bad.append(fn + ' not opaque')
    if not opaque and (a[0, 0] != 0 or a.min() != 0): bad.append(fn + ' corners not transparent')
check(not bad, '%d PNGs: size, RGBA, opaque / transparent background as specified %s' % (len(expect), bad or ''))

svg = lambda **kw: np.array(Image.open(io.BytesIO(resvg_py.svg_to_bytes(**kw))).convert('RGBA'))
m = svg(svg_path=P('bhc-wb-master.svg'), width=512, height=512)
sil = svg(svg_string=B.outline(), width=512, height=512)[..., 3]
nav = svg(svg_path=P('bhc-wb-mono.svg'), width=512, height=512)[..., 3]
cut = (sil == 255) & (nav == 0)
check(np.all(m[cut] == 255), 'master.svg: all %d cutout-interior pixels are #FFFFFF alpha 255' % cut.sum())
check(np.all(m[..., 3][sil == 0] == 0), 'master.svg: transparent wherever the silhouette is')
d = m[..., 3].astype(int) - sil.astype(int)
check(d.max() <= 0, 'master.svg: alpha never exceeds silhouette alpha (no halo)')
check((d < -8).sum() <= 20, 'master.svg: seam residue %d px more than 8/255 under the silhouette (two contour junctions)' % (d < -8).sum())
for fn in ('bhc-wb-16.png', 'bhc-wb-32.png', 'bhc-wb-256.png', 'android-chrome-512.png', 'bhc-wb-tile-310x310.png'):
    # keyline: the mark shrinks by k px a side; outside its silhouette only white (alpha varies), a ring ~k px wide
    q = rgba(P(fn)); n = q.shape[0]; k = R.keyline(n); o = mark_cov(n, (n - 2 * k) / n)
    ring = (o == 0) & (q[..., 3] > 0)
    # ring area = total coverage minus the mark's (the ring also fills the mark's anti-aliased edge pixels)
    area = q[..., 3].sum() / 255 - o.sum(); expect_area = 2 * np.pi * (n / 2 - k) * k  # perimeter x width
    check((q[ring][:, :3] == 255).all() and 0.9 < area / expect_area < 1.15 and not q[0, 0, 3],
          '%s: white keyline %.2f px outside the mark (ring area %.0f px^2, expected ~%.0f), corners transparent'
          % (fn, k, area, expect_area))
q = rgba(P('bhc-wb-32.png')); vis = q[..., 3] / 255
white_share = (vis * (q[..., :3] == 255).all(-1)).sum() / vis.sum()
print('INFO bhc-wb-32.png: %.0f %% of the visible area is white (passes 3:1 on #202020); navy is ~1.6:1' % (100 * white_share))
mk = np.array(Image.open(P('maskable-512.png')).convert('RGBA'))
yy, xx = np.mgrid[:512, :512]; rr = np.hypot(xx - 256, yy - 256); ang = np.degrees(np.arctan2(yy - 256, xx - 256))
zone = (rr > 209) & ~(np.abs(np.abs(ang) - 180) < 15)  # beyond the 80 % circle, excluding the open gap on the left
check(not (mk[zone] != 255).any(), 'maskable-512.png: everything outside the mark is pure white')
for fn, n, sc in (('apple-touch-icon-180.png', 180, 0.80), ('play-store-512.png', 512, 0.75)):
    a = rgba(P(fn)); o = mark_cov(n, sc)
    check((a[o == 0][:, :3] == 255).all() and o[0, :].max() == 0 and o[:, 0].max() == 0,
          '%s: mark at %d %% with a white margin, nothing touches the edge' % (fn, round(sc * 100)))
check(open(P('apple-touch-icon.png'), 'rb').read() == open(P('apple-touch-icon-180.png'), 'rb').read(),
      'apple-touch-icon.png: same file as apple-touch-icon-180.png (root fallback name)')
mf = json.load(open(P('site.webmanifest')))
icons_ok = all(os.path.exists(P(i['src'].lstrip('/'))) and Image.open(P(i['src'].lstrip('/'))).size == tuple(map(int, i['sizes'].split('x')))
               for i in mf['icons'])
check(icons_ok and {'name', 'short_name', 'start_url', 'display'} <= set(mf) and any(i.get('purpose') == 'maskable' for i in mf['icons']),
      'site.webmanifest: name, short_name, start_url, display; every icon exists at its stated size; a maskable icon')
for fn in ('bhc-wb-master.svg', 'bhc-wb-mono.svg', 'bhc-wb-mono-white.svg', 'bhc-wb-maskable.svg'):
    t = open(P(fn), encoding='utf-8').read()
    check(not ('href' in t or 'image' in t or 'url(' in t.replace('url(#', '')), '%s: no raster or external refs' % fn)

# ---------------------------------------------------------------- 2b. lockups (+ the stacked Workspace logo pair)
print('\n== 2b. lockups, and the stacked google_workspace_logo pair in admin-logo')
NAVY, BLACK, WHITE = (0x2E, 0x35, 0x91), (0, 0, 0), (255, 255, 255)
vb_b = L.load_svg(L.BANNER)[0]; vb_s = L.load_svg(L.STACKED)[0]
lockup_files = ([at(LOCKUP_BANNER, f) for f in sorted(os.listdir(at(LOCKUP_BANNER, '')))]
                + [at(LOCKUP_STACKED, f) for f in sorted(os.listdir(at(LOCKUP_STACKED, '')))]
                + [at(ADMIN_LOGO, f) for f in ('google_workspace_logo.png', 'google_workspace_logo_filled.png')])
count = 0; bad = []
for p in lockup_files:
    if p.endswith('.md'): continue
    fn = os.path.basename(p); a = rgba(p); h, w = a.shape[:2]; al = a[..., 3]
    mb = re.match(r'BH_(reversed|reversed_filled|white)_(\d+)x(\d+)\.png$', fn)
    ms = re.match(r'BH_stacked_(reversed|reversed_filled|white)_(\d+)w\.png$', fn)
    if mb: size_ok = (w, h) == (int(mb[2]), int(mb[3])) and abs(h - w * vb_b[3] / vb_b[2]) < 1.5; kind = mb[1]
    elif ms: size_ok = w == int(ms[2]) and h == int(round(w * vb_s[3] / vb_s[2])); kind = ms[1]
    elif fn.startswith('google_workspace_logo'):
        size_ok = (w, h) == GL.GWS_SIZE; kind = 'reversed_filled' if 'filled' in fn else 'reversed'
        ys, xs = np.nonzero(al)
        if max(abs(xs.min() - GL.GWS_BOX[0]), abs(ys.min() - GL.GWS_BOX[1]), abs(xs.max() + 1 - GL.GWS_BOX[2]), abs(ys.max() + 1 - GL.GWS_BOX[3])) > 1:
            bad.append(fn + ' content outside its box')
    else:
        bad.append('unknown file ' + p); continue
    count += 1
    if not size_ok: bad.append('%s size %dx%d' % (fn, w, h))
    if ((al > 0) & (al < 8)).any(): bad.append(fn + ' fringe')
    if al[0, 0] or al[0, -1] or al[-1, 0] or al[-1, -1]: bad.append(fn + ' corners')
    if kind == 'white':  # every visible pixel pure white (only alpha varies)
        okc = (a[al > 0][:, :3] == WHITE).all(1)
    else:
        rgb = a[al == 255][:, :3].astype(float)
        exact = (rgb == NAVY).all(1) | (rgb == BLACK).all(1)
        okc = exact | on_segment(rgb, NAVY, WHITE) if kind == 'reversed_filled' else exact
    if not okc.all(): bad.append('%s %d off-palette px' % (fn, (~okc).sum()))
check(count == 3 * len(GL.BANNER_W) + 3 * len(GL.STACKED_W) + 2, '%d lockup PNGs present' % count)
check(not bad, 'every lockup: size = name and SVG aspect, RGBA, no fringe, transparent corners, opaque pixels navy / black '
               '(filled: + white and navy/white blends; white set: white only) %s' % (bad or ''))

# ---------------------------------------------------------------- 2c. #3A4D5C profile photos (+ its SVG in vector)
print('\n== 2c. google-workspace/profile-photo (#3A4D5C)')
SL = G3.SLATE
o98 = R.cov(R.shape_svg(B.outline_d), 98); nv98 = np.minimum(R.cov(R.shape_svg(B.navy_d), 98), o98)
for fn, ref in (('BH_icon_3a4d5c_98x98.png', o98), ('BH_icon_3a4d5c_98x98_mono.png', nv98)):
    a = rgba(at(PROFILE, fn))
    check(a.shape == (98, 98, 4) and not (a[0, 0, 3] or a[-1, -1, 3]), '%s: 98x98 RGBA, corners transparent' % fn)
    check(np.abs(a[..., 3] - np.round(ref * 255)).max() <= 1, '%s: alpha == coverage (no halo)' % fn)
a = rgba(at(PROFILE, 'BH_icon_3a4d5c_98x98.png')); rgb = a[a[..., 3] == 255][:, :3].astype(float)
check(on_segment(rgb, SL, WHITE).all(), 'BH_icon_3a4d5c_98x98.png: every opaque pixel is a #3A4D5C/#FFFFFF mix')
a = rgba(at(PROFILE, 'BH_icon_3a4d5c_98x98_mono.png'))
check((a[a[..., 3] > 0][:, :3] == SL).all(), 'BH_icon_3a4d5c_98x98_mono.png: every visible pixel is exactly #3A4D5C')
check('#3A4D5C' in open(at(VECTOR, 'BH_icon_3a4d5c.svg')).read(), 'BH_icon_3a4d5c.svg: fill #3A4D5C')

for n in G3.PROFILE_SIZES:
    D = G3.disk(n)
    for kind in ('transparent', 'white', 'slate'):
        fn = 'BH_icon_3a4d5c_%d_%s.png' % (n, kind); path = at(PROFILE, fn)
        a = rgba(path); al = a[..., 3]; o = mark_cov(n, 1.0 if kind == 'slate' else G3.PAD)
        msgs = []
        if a.shape != (n, n, 4): msgs.append('size')
        if os.path.getsize(path) >= 5 * 1024 * 1024: msgs.append('over 5 MB')
        if kind == 'transparent':
            if np.abs(al - np.round(o * 255)).max() > 1: msgs.append('alpha != silhouette')
        else:
            if not (al == 255).all(): msgs.append('not opaque')
            if not (a[o == 0][:, :3] == (WHITE if kind == 'white' else SL)).all(): msgs.append('background')
        if kind != 'slate' and (o * (1 - D)).sum() >= 0.5: msgs.append('mark clipped by the circular crop')
        rgb = a[(al == 255) & (o > 0)][:, :3].astype(float)
        if not on_segment(rgb, SL, WHITE).all(): msgs.append('off-palette')
        if kind == 'slate' and not on_segment(a[D > 0][:, :3].astype(float), SL, WHITE).all(): msgs.append('crop disc not slate/white')
        check(not msgs, '%s %s' % (fn, ', '.join(msgs) or 'ok: size, < 5 MB, background, no clip, palette'))

# ---------------------------------------------------------------- 2d. Google Workspace logo
print('\n== 2d. google-workspace/admin-logo')
for fn, sc in (('BH_google_workspace_logo_320x132.png', 1), ('BH_google_workspace_logo_960x396_3x.png', 3)):
    path = at(ADMIN_LOGO, fn); a = rgba(path); al = a[..., 3]
    msgs = []
    if a.shape != (132 * sc, 320 * sc, 4): msgs.append('size')
    if os.path.getsize(path) > 30 * 1024: msgs.append('over 30 KB')
    if ((al > 0) & (al < 8)).any(): msgs.append('fringe')
    if al[0, 0] or al[-1, -1]: msgs.append('corners')
    rgb = a[al == 255][:, :3].astype(float)
    if not ((rgb == BLACK).all(1) | (rgb == WHITE).all(1) | on_segment(rgb, NAVY, WHITE)).all(): msgs.append('off-palette')
    ys, xs = np.nonzero(al); W, H = 320 * sc, 132 * sc
    if abs(xs.min() - (W - 1 - xs.max())) > 1 or abs(ys.min() - (H - 1 - ys.max())) > 1: msgs.append('not centred')
    check(not msgs, '%s %s (%d bytes)' % (fn, ', '.join(msgs) or 'ok: size, <= 30 KB, no fringe, palette, centred', os.path.getsize(path)))

# ---------------------------------------------------------------- 2e. mobile: Android launcher, iOS app icon
print('\n== 2e. mobile/android, mobile/ios')
NS = '{http://schemas.android.com/apk/res/android}'
res = lambda sub, fn: at(ANDROID_RES + '/' + sub, fn)

for dens, n in GM.DENSITIES.items():
    for fn in ('ic_launcher.png', 'ic_launcher_round.png'):
        a = rgba(res('mipmap-' + dens, fn)); o = mark_cov(n, GM.LEGACY_SCALE)
        check(a.shape == (n, n, 4) and not a[0, 0, 3] and np.abs(a[..., 3] - np.round(o * 255)).max() <= 1,
              'mipmap-%s/%s: %dx%d RGBA, transparent corners, alpha == mark on the 44/48 keyline' % (dens, fn, n, n))

for fn in ('ic_launcher.xml', 'ic_launcher_round.xml'):
    ai = ET.parse(res('mipmap-anydpi-v26', fn)).getroot()
    refs = {c.tag: c.get(NS + 'drawable') for c in ai}
    found = all(os.path.exists(res('drawable', r.split('/')[1] + '.xml')) for k, r in refs.items() if r.startswith('@drawable/'))
    colors = {c.get('name') for c in ET.parse(res('values', 'ic_launcher_background.xml')).getroot()}
    check(ai.tag == 'adaptive-icon' and set(refs) == {'background', 'foreground', 'monochrome'} and found
          and refs['background'].split('/')[1] in colors, 'mipmap-anydpi-v26/%s: background / foreground / monochrome all resolve' % fn)


def vd_svg(path, bg=None):
    """A VectorDrawable as an equivalent SVG (viewport, group translate + scale, fill / even-odd / stroke paths)."""
    v = ET.parse(path).getroot(); g = v.find('group'); G = lambda k: g.get(NS + k)
    body = ''
    for p in g.findall('path'):
        d = p.get(NS + 'pathData')
        if p.get(NS + 'fillColor'):
            body += '<path fill="%s" fill-rule="%s" d="%s"/>' % (p.get(NS + 'fillColor'), 'evenodd' if p.get(NS + 'fillType') == 'evenOdd' else 'nonzero', d)
        else:
            body += '<path fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="%s" stroke-linecap="%s" d="%s"/>' % (
                p.get(NS + 'strokeColor'), p.get(NS + 'strokeWidth'), p.get(NS + 'strokeLineJoin'), p.get(NS + 'strokeLineCap'), d)
    vw, vh = v.get(NS + 'viewportWidth'), v.get(NS + 'viewportHeight')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s">%s<g transform="translate(%s %s) scale(%s %s)">%s</g></svg>'
            % (vw, vh, '<rect width="%s" height="%s" fill="%s"/>' % (vw, vh, bg) if bg else '', G('translateX'), G('translateY'), G('scaleX'), G('scaleY'), body))


fg_path = res('drawable', 'ic_launcher_foreground.xml'); v = ET.parse(fg_path).getroot()
check(v.get(NS + 'viewportWidth') == v.get(NS + 'viewportHeight') == '108' and v.get(NS + 'width') == '108dp',
      'ic_launcher_foreground.xml: 108 dp layer, 108 x 108 viewport')
# safe zone: every point of the mark, mapped through the group transform, within 33 dp of the centre
g = v.find('group'); sx, tx = float(g.get(NS + 'scaleX')), float(g.get(NS + 'translateX'))
pts = np.array([B.T(p) for p in B.allp]) * sx + tx
rmax = np.hypot(pts[:, 0] - 54, pts[:, 1] - 54).max()
check(rmax <= 33, 'ic_launcher_foreground.xml: mark reaches %.2f dp from the centre (66 dp safe zone: <= 33)' % rmax)
paths_ = [p.get(NS + 'pathData') for p in g.findall('path')]
check(paths_ == [B.cut_d, B.inner_trim_d, B.navy_d], 'ic_launcher_foreground.xml: path data is the SVG master\'s, verbatim')
# the VectorDrawable, rendered as SVG on its white background, against the exact composite of the same layer
N4 = 432
vd = np.array(Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=vd_svg(fg_path, '#FFFFFF'), width=N4, height=N4))).convert('RGB')).astype(int)
ex = np.array(GM.adaptive_layer(N4).convert('RGB')).astype(int)
diff = np.abs(vd - ex).max(-1)
check(diff.mean() < 0.5 and (diff > 64).sum() < 50,
      'ic_launcher_foreground.xml rendered at 432 px vs exact composite: mean diff %.3f, %d px over 64/255 (AA edges only)'
      % (diff.mean(), (diff > 64).sum()))
mv = ET.parse(res('drawable', 'ic_launcher_monochrome.xml')).getroot().find('group').findall('path')
check(len(mv) == 1 and mv[0].get(NS + 'pathData') == B.navy_d and mv[0].get(NS + 'fillType') is None,
      'ic_launcher_monochrome.xml: the mark shape only (cutouts transparent), same transform')

cj = json.load(open(at(IOS_ICONSET, 'Contents.json')))
looks = {(i.get('appearances') or [{}])[0].get('value', 'any'): i for i in cj['images']}
check(set(looks) == {'any', 'dark', 'tinted'} and all(
      i['idiom'] == 'universal' and i['platform'] == 'ios' and i['size'] == '1024x1024' and os.path.exists(at(IOS_ICONSET, i['filename']))
      and (i is looks['any'] or i['appearances'][0]['appearance'] == 'luminosity') for i in cj['images']),
      'Contents.json: universal iOS 1024x1024 any / dark / tinted (luminosity appearances), files present')
ip = at(IOS_ICONSET, looks['any']['filename'])
im = Image.open(ip); a = np.array(im).astype(int); o = mark_cov(1024, GM.IOS_SCALE)
check(im.size == (1024, 1024) and im.mode == 'RGB', 'AppIcon-1024.png: 1024x1024, RGB (no alpha channel)')
check((a[o == 0] == 255).all() and on_segment(a[o > 0].astype(float), NAVY, WHITE).all(),
      'AppIcon-1024.png: white outside the mark, mark pixels navy / white / blends only')
dk = Image.open(at(IOS_ICONSET, looks['dark']['filename'])); d_ = np.array(dk).astype(int)
contrast = (GM.luminance(GM.IOS_DARK) + 0.05) / 0.05
check(dk.mode == 'RGBA' and not d_[0, 0, 3] and (d_[d_[..., 3] > 0][:, :3] == GM.IOS_DARK).all() and d_[..., 3][o == 0].max() == 0
      and contrast >= 4.5, 'AppIcon-1024-dark.png: transparent background and cutouts, disc #%02X%02X%02X (%.2f:1 on black)'
      % (*GM.IOS_DARK, contrast))
tn = Image.open(at(IOS_ICONSET, looks['tinted']['filename'])); t_ = np.array(tn).astype(int)
check(tn.mode == 'RGB' and (t_[..., 0] == t_[..., 1]).all() and (t_[..., 1] == t_[..., 2]).all() and t_[0, 0, 0] == 0 and t_.max() == 255,
      'AppIcon-1024-tinted.png: grayscale (R = G = B), black background, white disc')

print('\nALL OK' if ok else '\nPROBLEMS')
sys.exit(0 if ok else 1)
