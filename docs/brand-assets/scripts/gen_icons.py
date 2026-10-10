"""The bhc-wb icon set in navy: windows/app (ICO + PNG entries), windows/folder (ICO + desktop.ini), windows/tiles,
web (favicons, apple-touch, manifest + its icons), mobile/play-store, vector (master / mono / mono-white / maskable SVG),
previews (contact sheet, taskbar preview)."""
import io, json, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import build_svg as B
from paths import FONT, WIN_APP, WIN_FOLDER, WIN_TILES, WEB, PLAY, VECTOR, PREVIEWS, out
from render import keyline, mark

WIDEN = {16: 0.5, 20: 0.3, 24: 0.3, 30: 0.2, 32: 0.2, 36: 0.1}  # px the white cutouts are widened by (thin tail stays open)
# Microsoft's Win32 icon sizes (16-256 for 100-400 % scaling: taskbar, Start, Explorer views) plus 128
ICO_SIZES = [16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128, 256]
WHITE = (255, 255, 255)
DESKTOP_INI = '[.ShellClassInfo]\r\nIconResource=C:\\path\\to\\bhc-wb-folder.ico,0\r\n'
MANIFEST = {'name': 'Bellevue Healthcare', 'short_name': 'Bellevue', 'start_url': '/', 'display': 'standalone',
            'theme_color': '#2E3591', 'background_color': '#FFFFFF',
            'icons': [{'src': '/android-chrome-192.png', 'sizes': '192x192', 'type': 'image/png'},
                      {'src': '/android-chrome-512.png', 'sizes': '512x512', 'type': 'image/png'},
                      {'src': '/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]}


def bmp_entry(im):
    w, h = im.size
    a = np.array(im.convert('RGBA'))
    bgra = a[::-1, :, [2, 1, 0, 3]].tobytes()  # bottom-up
    and_row = ((w + 31) // 32) * 4
    and_mask = b'\x00' * (and_row * h)
    hdr = struct.pack('<IiiHHIIiiII', 40, w, h * 2, 1, 32, 0, len(bgra) + len(and_mask), 0, 0, 0, 0)
    return hdr + bgra + and_mask


def write_ico(path, images):
    """Hand-built ICO: 32-bit BMP entries below 256 px, a PNG entry at 256."""
    entries = []
    for im in images:
        w, h = im.size
        if w >= 256:
            buf = io.BytesIO(); im.save(buf, 'PNG'); data = buf.getvalue()
        else:
            data = bmp_entry(im)
        entries.append((w, h, data))
    n = len(entries)
    off = 6 + 16 * n
    hdr = struct.pack('<HHH', 0, 1, n); dirs = b''; blob = b''
    for w, h, data in entries:
        dirs += struct.pack('<BBBBHHII', w % 256, h % 256, 0, 0, 1, 32, len(data), off + len(blob))
        blob += data
    open(path, 'wb').write(hdr + dirs + blob)


def build(root):
    P = lambda folder, n: out(root, folder, n)
    # transparent icons (ICO entries, tiles, favicons, manifest "any" icons) carry the white keyline for dark themes
    imgs = {s: mark(s, widen_px=WIDEN.get(s, 0.0), keyline_px=keyline(s)) for s in ICO_SIZES + [44, 71, 150, 192, 310, 512]}

    # --- SVG ---
    open(P(VECTOR, 'bhc-wb-master.svg'), 'w', encoding='utf-8').write(B.master())
    open(P(VECTOR, 'bhc-wb-mono.svg'), 'w', encoding='utf-8').write(B.mono())
    open(P(VECTOR, 'bhc-wb-mono-white.svg'), 'w', encoding='utf-8').write(B.mono('#FFFFFF'))  # for dark backgrounds
    open(P(VECTOR, 'bhc-wb-maskable.svg'), 'w', encoding='utf-8').write(B.maskable())

    # --- ICO ---
    write_ico(P(WIN_APP, 'bhc-wb-gui.ico'), [imgs[s] for s in ICO_SIZES])
    write_ico(P(WIN_FOLDER, 'bhc-wb-folder.ico'), [imgs[s] for s in ICO_SIZES])  # same entries, deployable on its own
    open(P(WIN_FOLDER, 'desktop.ini'), 'w', encoding='ascii', newline='').write(DESKTOP_INI)
    write_ico(P(WEB, 'favicon.ico'), [imgs[s] for s in (16, 32, 48)])

    # --- PNG (Windows) ---
    for s in ICO_SIZES:
        imgs[s].save(P(WIN_APP, 'bhc-wb-%d.png' % s))
    for s in (44, 71, 150, 310):
        imgs[s].save(P(WIN_TILES, 'bhc-wb-tile-%dx%d.png' % (s, s)))
    wide = Image.new('RGBA', (310, 150), (0, 0, 0, 0)); wide.alpha_composite(imgs[150], (80, 0)); wide.save(P(WIN_TILES, 'bhc-wb-tile-310x150.png'))

    # --- PNG (web, mobile) ---
    for s in (16, 32, 48):
        imgs[s].save(P(WEB, 'favicon-%d.png' % s))
    # Apple touch icon: opaque, mark at 80 % so iOS's rounded-square mask leaves a margin (same layout as maskable / iOS)
    apple = mark(180, scale=0.80, bg=WHITE); apple.save(P(WEB, 'apple-touch-icon-180.png'))
    apple.save(P(WEB, 'apple-touch-icon.png'))  # the name Safari requests from the site root without a <link>
    imgs[192].save(P(WEB, 'android-chrome-192.png'))
    imgs[512].save(P(WEB, 'android-chrome-512.png'))
    maskable = mark(512, scale=0.80, bg=WHITE); maskable.save(P(WEB, 'maskable-512.png'))
    open(P(WEB, 'site.webmanifest'), 'w', encoding='utf-8').write(json.dumps(MANIFEST, indent=2) + '\n')
    # Google Play: full square, opaque, no corners / shadow (Play applies them); a shape logo sits on the 384 px keyline
    play = mark(512, scale=0.75, bg=WHITE); play.save(P(PLAY, 'play-store-512.png'))

    # --- contact sheet: every size at 1x on white, grey, dark ---
    font = ImageFont.truetype(FONT, 13)
    BGS = [('#FFFFFF', (255, 255, 255), (40, 40, 40)), ('#808080', (128, 128, 128), (255, 255, 255)), ('#1F1F1F', (31, 31, 31), (230, 230, 230))]
    rows = [('ICO / PNG sizes', [('%d' % s, imgs[s]) for s in ICO_SIZES]),
            ('Windows tiles', [('44', imgs[44]), ('71', imgs[71]), ('150', imgs[150]), ('310x150', wide), ('310', imgs[310])]),
            ('Google / web', [('fav16', imgs[16]), ('fav32', imgs[32]), ('fav48', imgs[48]), ('apple180', apple),
                              ('android192', imgs[192]), ('maskable512', maskable), ('android512', imgs[512]), ('play512', play)])]
    PAD = 14
    colw = max(sum(im.size[0] + PAD for _, im in r) + PAD for _, r in rows)
    rowh = [max(im.size[1] for _, im in r) + 34 for _, r in rows]
    H = sum(rowh) + 2 * PAD
    sheet = Image.new('RGBA', (colw, H * 3), (0, 0, 0, 255))
    d = ImageDraw.Draw(sheet)
    for bi, (name, bg, fg) in enumerate(BGS):
        y0 = bi * H
        d.rectangle([0, y0, colw - 1, y0 + H], fill=bg + (255,))
        d.text((PAD, y0 + 4), name, fill=fg, font=font)
        y = y0 + PAD + 10
        for (title, items), rh in zip(rows, rowh):
            x = PAD
            for lbl, im in items:
                sheet.alpha_composite(im, (x, y + 16))
                d.text((x, y), lbl, fill=fg, font=font)
                x += im.size[0] + PAD
            y += rh
    sheet.save(P(PREVIEWS, 'contact-sheet.png'))

    # --- taskbar preview: Win11 dark taskbar #202020; 24 / 30 / 36 are the taskbar icon at 100 / 125 / 150 % scaling ---
    TB = (0x20, 0x20, 0x20); TBS = (16, 24, 30, 36)
    tb = Image.new('RGBA', (16 + sum(s * 4 + 24 for s in TBS), 230), TB + (255,)); d = ImageDraw.Draw(tb)
    d.text((10, 6), 'Windows 11 dark taskbar  (#202020) - 16 / 24 / 30 / 36 px at 1x, then 4x', fill=(220, 220, 220), font=font)
    x = 16
    for s in TBS:
        tb.alpha_composite(imgs[s], (x, 48 - s // 2)); x += s + 24
    x = 16
    for s in TBS:
        tb.alpha_composite(imgs[s].resize((s * 4, s * 4), Image.NEAREST), (x, 150 - s * 2)); x += s * 4 + 24
    tb.save(P(PREVIEWS, 'taskbar-preview.png'))
