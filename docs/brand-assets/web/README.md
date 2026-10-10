# web — favicons, Apple touch icon, web app manifest

| File | What |
|---|---|
| [favicon.ico](favicon.ico) | 16, 32, 48 (32-bit BMP), transparent, with the white keyline that outlines the disc on dark tabs (as in `..\windows\`). |
| [favicon-16](favicon-16.png) / [32](favicon-32.png) / [48](favicon-48.png).png | The same pixels as PNGs (identical to `..\windows\app\bhc-wb-16/32/48.png`, kept here so this folder deploys on its own). |
| [apple-touch-icon-180.png](apple-touch-icon-180.png) | 180 x 180, opaque white, mark at 80 % (iOS ignores alpha and rounds the corners). |
| [apple-touch-icon.png](apple-touch-icon.png) | The same file under the name Safari requests from the site root when a page has no `<link>`. |
| [android-chrome-192.png](android-chrome-192.png), [android-chrome-512.png](android-chrome-512.png) | Transparent "any" icons for the manifest, with the white keyline. |
| [maskable-512.png](maskable-512.png) | Opaque white, mark at 80 % (exactly the maskable safe-zone circle), `purpose: maskable`. |
| [site.webmanifest](site.webmanifest) | name, short_name, start_url, display, theme `#2E3591`, background `#FFFFFF`, the three icons above. Edit `name` / `start_url` per site. |

`<head>`:

```html
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" type="image/png" sizes="192x192" href="/android-chrome-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180.png">
<link rel="manifest" href="/site.webmanifest">
```

The 192 px PNG link gives Google Search a favicon larger than 48 px
(https://developers.google.com/search/docs/appearance/favicon-in-search). The manifest makes the site installable
(https://web.dev/articles/add-manifest).

No SVG favicon on purpose: browsers that support one use it instead of the ICO and would draw the master SVG at 16-32 px
without the small-size widening.

Generator: `..\scripts\gen_icons.py`.
