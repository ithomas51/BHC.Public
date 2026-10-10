"""The mark in slate #3A4D5C for Google profile photos: google-workspace/profile-photo (98x98 filled and mono, and
192 / 512 / 1024 transparent and white at 96 %, slate full-bleed), vector (SVG master), previews (two sheets)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import build_svg as B
from paths import FONT, PROFILE, VECTOR, PREVIEWS, out
from render import mark, mono

SLATE = (0x3A, 0x4D, 0x5C); WHITE = (255, 255, 255)
N = 98
PROFILE_SIZES = [192, 512, 1024]
# at 0.98 and below nothing of the mark falls outside the inscribed circle (at full size the mark overhangs it by up to
# 3.7 px at 1024: 0.36 % of the width, 0.72 % of the radius); 0.96 leaves a margin of ~1.6 % of the width
PAD = 0.96


def disk(n, ss=4):
    """Coverage of the circle inscribed in an n x n square (what a circular crop keeps), supersampled ss x ss."""
    g = (np.arange(n * ss) + 0.5) / ss
    X, Y = np.meshgrid(g, g)
    return ((X - n / 2) ** 2 + (Y - n / 2) ** 2 <= (n / 2) ** 2).astype(float).reshape(n, ss, n, ss).mean((1, 3))


def profile_variants(n):
    return {'transparent': mark(n, scale=PAD, color=SLATE),
            'white': mark(n, scale=PAD, bg=WHITE, color=SLATE),
            'slate': mark(n, bg=SLATE, color=SLATE)}


def client(upload, d, ui_bg, flatten=None):
    """What a client shows: upload resized to d device px (Lanczos), optional transparency flatten, then circular crop."""
    im = upload.convert('RGBA')
    if flatten is not None:
        base = Image.new('RGBA', im.size, flatten + (255,)); base.alpha_composite(im); im = base
    im = im.resize((d, d), Image.LANCZOS)
    mask = Image.fromarray(np.round(disk(d) * 255).astype(np.uint8), 'L')
    tile = Image.new('RGBA', (d, d), ui_bg + (255,))
    tile.paste(im, (0, 0), Image.fromarray(np.minimum(np.array(im)[..., 3], np.array(mask)).astype(np.uint8), 'L'))
    return tile


def build(root):
    font = ImageFont.truetype(FONT, 14)

    # --- 98x98 + vector ---
    filled = mark(N, color=SLATE); flat = mono(N, color=SLATE)
    filled.save(out(root, PROFILE, 'BH_icon_3a4d5c_98x98.png'), optimize=True)
    flat.save(out(root, PROFILE, 'BH_icon_3a4d5c_98x98_mono.png'), optimize=True)
    open(out(root, VECTOR, 'BH_icon_3a4d5c.svg'), 'w', encoding='utf-8').write(B.master(color='#3A4D5C'))

    # preview: 1x and 6x on white / grey / dark
    Z = 6; pad = 20
    cell = N * Z + 2 * pad
    sheet = Image.new('RGBA', (pad + 3 * (N + pad) + 2 * cell, 3 * (cell + 26)), (0, 0, 0, 255))
    d = ImageDraw.Draw(sheet)
    for i, (lab, bg, fg) in enumerate([('#FFFFFF', (255, 255, 255), (40, 40, 40)), ('#808080', (128, 128, 128), (255, 255, 255)), ('#1F1F1F', (31, 31, 31), (230, 230, 230))]):
        y0 = i * (cell + 26)
        d.rectangle([0, y0, sheet.width, y0 + cell + 26], fill=bg + (255,))
        d.text((pad, y0 + 4), f'{lab}   98x98 at 1x  |  filled 6x  |  mono 6x', fill=fg, font=font)
        sheet.alpha_composite(filled, (pad, y0 + 30)); sheet.alpha_composite(flat, (pad + N + pad, y0 + 30))
        x = pad + 3 * (N + pad)
        sheet.alpha_composite(filled.resize((N * Z, N * Z), Image.NEAREST), (x, y0 + 30))
        sheet.alpha_composite(flat.resize((N * Z, N * Z), Image.NEAREST), (x + cell, y0 + 30))
    sheet.convert('RGB').save(out(root, PREVIEWS, 'preview-98.png'))

    # --- profile-photo set ---
    big = {}
    for n in PROFILE_SIZES:
        for kind, im in profile_variants(n).items():
            im.save(out(root, PROFILE, 'BH_icon_3a4d5c_%d_%s.png' % (n, kind)), optimize=True)
            if n == 1024: big[kind] = im

    # client simulation: each upload downscaled to device px and circle-cropped, dark and light UI
    DEV = [32, 48, 64, 96, 192, 384]
    rows = [('98x98 upload (first version)', filled, None),
            ('1024 transparent', big['transparent'], None),
            ('1024 transparent, client flattens to black', big['transparent'], (0, 0, 0)),
            ('1024 white', big['white'], None),
            ('1024 slate', big['slate'], None)]
    UIS = [('dark UI #1B1B1B', (0x1B, 0x1B, 0x1B), (230, 230, 230)), ('light UI #FFFFFF', (255, 255, 255), (30, 30, 30))]
    pad = 16; rowh = max(DEV) + 30; colw = sum(DEV) + pad * (len(DEV) + 1)
    Z = 4  # zoom strip of the two smallest sizes
    zw = (32 + 48) * Z + 3 * pad
    sheet = Image.new('RGBA', (len(UIS) * (colw + zw), len(rows) * rowh + 30), (0, 0, 0, 255)); dr = ImageDraw.Draw(sheet)
    for ui, (uname, ubg, ufg) in enumerate(UIS):
        x0 = ui * (colw + zw)
        dr.rectangle([x0, 0, x0 + colw + zw - 1, sheet.height], fill=ubg + (255,))
        dr.text((x0 + pad, 4), uname + '   device px ' + ' / '.join(map(str, DEV)) + '   |   32 and 48 at 4x', fill=ufg, font=font)
        for ri, (lab, up, flat_bg) in enumerate(rows):
            y = 30 + ri * rowh
            dr.text((x0 + pad, y), lab, fill=ufg, font=font)
            x = x0 + pad
            for dv in DEV:
                sheet.alpha_composite(client(up, dv, ubg, flat_bg), (x, y + 22)); x += dv + pad
            for dv in (32, 48):
                sheet.alpha_composite(client(up, dv, ubg, flat_bg).resize((dv * Z, dv * Z), Image.NEAREST), (x, y + 22)); x += dv * Z + pad
    sheet.convert('RGB').save(out(root, PREVIEWS, 'preview-profile-client-sim.png'))
