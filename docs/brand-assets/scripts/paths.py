"""Every path the pipeline reads, and the landing layout it writes. Outputs go under a root passed to each build(root);
ROOT is the default."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))  # docs\brand-assets
ASSETS = os.path.abspath(os.path.join(ROOT, '..', 'BellevueHealth Care', 'bellevuehealthcare', 'assets'))
LOCKUP_DIR = os.path.join(ASSETS, 'SVG')  # BH_reversed.svg, 'BH stacked_reversed.svg'
MARK_SVG = os.path.join(LOCKUP_DIR, 'logo', 'svg', '2e3591', 'BH_icon_2e3591_512x512.svg')  # the mark: one compound path
FONT = r'C:\Windows\Fonts\segoeui.ttf'  # labels on preview sheets

# landing layout, by platform (folders relative to the root)
WIN_APP = 'windows/app'                     # bhc-wb-gui.ico and its entries as PNGs
WIN_TILES = 'windows/tiles'                 # Windows tile / Store sizes
WIN_FOLDER = 'windows/folder'               # folder / shortcut icon (.ico) and a desktop.ini template
WEB = 'web'                                 # favicons, apple-touch, web-manifest icons
PLAY = 'mobile/play-store'                  # Play Store listing icon
ANDROID_RES = 'mobile/android/res'          # Android launcher icon resources (drop into app/src/main/res)
IOS_ICONSET = 'mobile/ios/AppIcon.appiconset'  # Xcode asset catalog app icon
VECTOR = 'vector'                           # SVG masters
PREVIEWS = 'previews'                       # contact sheets and simulations (not for deployment)
PROFILE = 'google-workspace/profile-photo'  # #3A4D5C profile pictures
ADMIN_LOGO = 'google-workspace/admin-logo'  # Admin console logo (320 x 132)
LOCKUP_BANNER = 'lockups/banner'
LOCKUP_STACKED = 'lockups/stacked'


def out(root, folder, name):
    """Path of `name` in root/folder, creating the folder."""
    d = os.path.join(root, *folder.split('/'))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)
