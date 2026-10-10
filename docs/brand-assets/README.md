# brand-assets — Bellevue Healthcare logo assets

Production Bellevue Healthcare logo assets, organised by platform. Every image is rendered from the vector sources by
the pipeline in `scripts\`, and `scripts\verify.py` proves it: a fresh render from vector must match every file exactly,
with nothing missing and nothing extra.

Vector sources: `docs\BellevueHealth Care\bellevuehealthcare\assets\SVG\` (the mark and the two lockups).

## Where to find what

| Folder | Contents | Use |
|---|---|---|
| [`google-workspace\admin-logo\`](google-workspace/admin-logo/) | Stacked and banner logos for the 320 x 132 Admin console slot, Google's logo policy | Admin console > Account settings > Personalization: upload `google_workspace_logo_filled.png` |
| [`google-workspace\profile-photo\`](google-workspace/profile-photo/) | The mark in slate `#3A4D5C` (the colour for profile photos): 98 px, and 192 / 512 / 1024 in slate, white and transparent variants | Profile pictures: upload `BH_icon_3a4d5c_1024_slate.png` |
| [`windows\app\`](windows/app/) | `bhc-wb-gui.ico` (15 sizes, 16-256, white keyline for dark themes) and each entry as PNG | Desktop app window / taskbar icon |
| [`windows\folder\`](windows/folder/) | `bhc-wb-folder.ico` and a `desktop.ini` template | Folder and shortcut icons |
| [`windows\tiles\`](windows/tiles/) | Tile sizes 44, 71, 150, 310, 310x150 (reference; only for MSIX packaging) | Windows 10 tiles |
| [`web\`](web/) | `favicon.ico`, favicon PNGs, Apple touch icon, `site.webmanifest` and its icons (192, 512, maskable 512) | Websites and web apps |
| [`mobile\android\res\`](mobile/android/res/) | Adaptive launcher icon (VectorDrawable foreground + monochrome, white background) and legacy PNGs | Android apps |
| [`mobile\ios\AppIcon.appiconset\`](mobile/ios/AppIcon.appiconset/) | 1024 app icon in any / dark / tinted appearances + `Contents.json` | iOS apps (Xcode) |
| [`mobile\play-store\`](mobile/play-store/) | 512 Play listing icon | Google Play |
| [`lockups\banner\`](lockups/banner/), [`lockups\stacked\`](lockups/stacked/) | Mark + wordmark, 8 banner and 12 stacked widths: `_filled`, transparent, and all-white for dark backgrounds | Site headers, documents, email, slides |
| [`vector\`](vector/) | SVG masters: navy master / mono / mono-white / maskable, slate master | Any size; source for designers |
| [`previews\`](previews/) | Contact sheets and simulations | Review only, not for deployment |
| [`scripts\`](scripts/) | The pipeline (`RUN.md`) | Regenerate and verify |

Each folder has a README with sizes, decisions and the checks that apply.

## How the images are made

- Shapes come only from the SVG paths. Nothing is redrawn, traced or upscaled from an older raster.
- Each colour layer is rendered as a coverage mask with resvg and composited numerically (premultiplied), so edges are
  exact: no halos outside the shape, no seams where white cutouts meet the colour, no off-palette anti-aliasing colours,
  no stray pixels with alpha below 8.
- "Filled" means the mark's cutouts are white inside the mark's circular silhouette; outside it stays transparent.

## Verify or regenerate

See `scripts\RUN.md`. In short, from `scripts\` in the scratch venv:

```powershell
& $py verify.py       # ALL OK = every file identical to a fresh vector render, all property checks pass
& $py build_all.py    # regenerate everything (only needed after changing a source SVG or a script)
```
