"""Native app icons. mobile/android/res: adaptive launcher icon whose foreground and monochrome layers are VectorDrawables
built from the mark's own path strings, a white background layer, and legacy launcher PNGs per density.
mobile/ios/AppIcon.appiconset: the Xcode single-size 1024 icon (opaque, no alpha) with its dark and tinted appearances,
and Contents.json. Plus a preview of the adaptive icon under launcher masks."""
import colorsys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import build_svg as B
from paths import ANDROID_RES, IOS_ICONSET, PREVIEWS, FONT, out
from render import NAVY, mark, mono, cov

WHITE = (255, 255, 255)


def luminance(c):
    lin = [(v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def lighten_for_dark(c, contrast=4.5):
    """The brand colour's own hue and saturation, lightened just until it reaches `contrast` against black."""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    while (luminance(c) + 0.05) / 0.05 < contrast:
        l += 0.001; c = tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))
    return c


# iOS 18+ appearances (Apple: "Provide your dark app icon with a transparent background so the system-provided background
# can show through"; "Provide your tinted app icon as a grayscale image")
IOS_DARK = lighten_for_dark(NAVY)
# adaptive icon: 108 dp layers; launchers show the inner 72 dp through a mask, and only a 66 dp circle is guaranteed.
# The mark is 64 dp (its fitted circle reaches ~32.2 dp from the centre, inside the 33 dp safe radius).
LAYER_DP = 108; MARK_DP = 64
VD_SCALE = MARK_DP / 512; VD_OFF = (LAYER_DP - MARK_DP) / 2
# legacy launcher icons (before API 26): 48 dp, circle icons on the 44 dp keyline
DENSITIES = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
LEGACY_SCALE = 44 / 48
IOS_SIZE = 1024; IOS_SCALE = 0.80  # mark inside the rounded-square mask with the same margin as the maskable icons

VD_HEAD = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
           '    android:width="%ddp" android:height="%ddp" android:viewportWidth="%d" android:viewportHeight="%d">\n'
           '    <group android:translateX="%s" android:translateY="%s" android:scaleX="%s" android:scaleY="%s">\n'
           ) % (LAYER_DP, LAYER_DP, LAYER_DP, LAYER_DP, B.f(VD_OFF), B.f(VD_OFF), B.f(VD_SCALE), B.f(VD_SCALE))
VD_TAIL = '    </group>\n</vector>\n'


def foreground_xml():
    """White cutouts (even-odd silhouette minus mark), the 3-unit white seam under-stroke, then the navy mark."""
    return (VD_HEAD
            + '        <path android:fillColor="#FFFFFF" android:fillType="evenOdd" android:pathData="%s"/>\n' % B.cut_d
            + '        <path android:strokeColor="#FFFFFF" android:strokeWidth="3" android:strokeLineJoin="round"'
              ' android:strokeLineCap="butt" android:pathData="%s"/>\n' % B.inner_trim_d
            + '        <path android:fillColor="%s" android:pathData="%s"/>\n' % (B.NAVY, B.navy_d)
            + VD_TAIL)


def monochrome_xml():
    """Android 13 themed icon: the mark's shape only (the system tints it); cutouts stay transparent."""
    return VD_HEAD + '        <path android:fillColor="#FFFFFF" android:pathData="%s"/>\n' % B.navy_d + VD_TAIL


ADAPTIVE_XML = ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
                '    <background android:drawable="@color/ic_launcher_background"/>\n'
                '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n'
                '    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>\n'
                '</adaptive-icon>\n')
BACKGROUND_XML = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                  '    <color name="ic_launcher_background">#FFFFFF</color>\n</resources>\n')
CONTENTS = {'images': [{'filename': 'AppIcon-1024.png', 'idiom': 'universal', 'platform': 'ios', 'size': '1024x1024'},
                       {'appearances': [{'appearance': 'luminosity', 'value': 'dark'}],
                        'filename': 'AppIcon-1024-dark.png', 'idiom': 'universal', 'platform': 'ios', 'size': '1024x1024'},
                       {'appearances': [{'appearance': 'luminosity', 'value': 'tinted'}],
                        'filename': 'AppIcon-1024-tinted.png', 'idiom': 'universal', 'platform': 'ios', 'size': '1024x1024'}],
            'info': {'author': 'xcode', 'version': 1}}


def adaptive_layer(n):
    """The adaptive icon's full 108 dp layer stack (white background + foreground) at n px."""
    return mark(n, scale=MARK_DP / LAYER_DP, bg=WHITE)


def write(path, text):
    open(path, 'w', encoding='utf-8').write(text)


def masks(n):
    """Launcher mask shapes over the visible n x n area (anti-aliased, 4x supersampled)."""
    ss = 4; g = (np.arange(n * ss) + 0.5) / ss / n * 2 - 1  # -1..1
    X, Y = np.meshgrid(g, g)
    r = 0.30  # rounded square corner radius (fraction of half-size)
    dx = np.maximum(np.abs(X) - (1 - r), 0); dy = np.maximum(np.abs(Y) - (1 - r), 0)
    shapes = {'circle': X ** 2 + Y ** 2 <= 1,
              'squircle': np.abs(X) ** 4 + np.abs(Y) ** 4 <= 1,
              'rounded square': dx ** 2 + dy ** 2 <= r ** 2,
              'teardrop': np.where((X > 0) & (Y > 0), np.maximum(X, Y) <= 1, X ** 2 + Y ** 2 <= 1)}
    return {k: v.astype(float).reshape(n, ss, n, ss).mean((1, 3)) for k, v in shapes.items()}


def build(root):
    # --- Android ---
    for dens, n in DENSITIES.items():
        im = mark(n, scale=LEGACY_SCALE)
        im.save(out(root, ANDROID_RES + '/mipmap-' + dens, 'ic_launcher.png'))
        im.save(out(root, ANDROID_RES + '/mipmap-' + dens, 'ic_launcher_round.png'))
    write(out(root, ANDROID_RES + '/mipmap-anydpi-v26', 'ic_launcher.xml'), ADAPTIVE_XML)
    write(out(root, ANDROID_RES + '/mipmap-anydpi-v26', 'ic_launcher_round.xml'), ADAPTIVE_XML)
    write(out(root, ANDROID_RES + '/drawable', 'ic_launcher_foreground.xml'), foreground_xml())
    write(out(root, ANDROID_RES + '/drawable', 'ic_launcher_monochrome.xml'), monochrome_xml())
    write(out(root, ANDROID_RES + '/values', 'ic_launcher_background.xml'), BACKGROUND_XML)

    # --- iOS ---
    mark(IOS_SIZE, scale=IOS_SCALE, bg=WHITE).convert('RGB').save(out(root, IOS_ICONSET, 'AppIcon-1024.png'))
    # dark: the disc in the lightened brand blue, cutouts and background transparent (the system background shows)
    mono(IOS_SIZE, color=IOS_DARK, scale=IOS_SCALE).save(out(root, IOS_ICONSET, 'AppIcon-1024-dark.png'))
    # tinted: grayscale luminance on black, the disc white (the system tints the light areas), cutouts black
    tint = np.array(mono(IOS_SIZE, color=WHITE, scale=IOS_SCALE))[..., 3]
    Image.fromarray(np.dstack([tint] * 3), 'RGB').save(out(root, IOS_ICONSET, 'AppIcon-1024-tinted.png'))
    write(out(root, IOS_ICONSET, 'Contents.json'), json.dumps(CONTENTS, indent=2) + '\n')

    # --- preview: adaptive icon (xxxhdpi, 432 px layer, 288 px visible) under launcher masks, themed, legacy ---
    font = ImageFont.truetype(FONT, 14)
    V = 288; layer = adaptive_layer(432); vis = np.array(layer.crop((72, 72, 72 + V, 72 + V))).astype(float)
    t = (1 - MARK_DP / LAYER_DP) / 2 * 512  # monochrome layer = the mark's shape at the foreground's scale
    mono_a = cov(B.HEAD + '<g transform="translate(%s %s) scale(%s)"><path fill="#000" d="%s"/></g></svg>'
                 % (B.f(t), B.f(t), B.f(MARK_DP / LAYER_DP), B.navy_d), 432)[72:72 + V, 72:72 + V]
    THEME_BG, THEME_FG = np.array([0xD3, 0xE3, 0xFD], float), np.array([0x04, 0x1E, 0x49], float)  # Material You light pair
    themed = mono_a[..., None] * THEME_FG + (1 - mono_a[..., None]) * THEME_BG
    pad = 24; cols = 5
    sheet = Image.new('RGB', (pad + cols * (V + pad), 2 * (V + 60) + 40), (0, 0, 0)); d = ImageDraw.Draw(sheet)
    for row, (wall, fg) in enumerate((((0x1F, 0x1F, 0x1F), (230, 230, 230)), ((0xEE, 0xF0, 0xF4), (30, 30, 30)))):
        y0 = row * (V + 60)
        d.rectangle([0, y0, sheet.width, y0 + V + 60], fill=wall)
        x = pad
        items = [(k, vis[..., :3], m) for k, m in masks(V).items()] + [('themed (Android 13)', themed, masks(V)['circle'])]
        for lab, rgb, m in items:
            px = np.round(rgb * m[..., None] + np.array(wall, float) * (1 - m[..., None])).astype(np.uint8)
            sheet.paste(Image.fromarray(px, 'RGB'), (x, y0 + 30))
            d.text((x, y0 + 6), lab, fill=fg, font=font)
            x += V + pad
    d.text((pad, sheet.height - 30), 'Adaptive icon at xxxhdpi (visible 72 dp = 288 px): white background layer + vector foreground, '
           'mark 64 dp in the 66 dp safe zone', fill=(200, 200, 200), font=font)
    sheet.save(out(root, PREVIEWS, 'android-adaptive-masks.png'))
