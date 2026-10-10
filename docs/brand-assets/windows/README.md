# windows — native .ico icons and tiles

Navy `#2E3591` mark with white-filled cutouts and a white keyline (see below), transparent outside. Each size is rendered
from vector at that size; at 16-36 px the white cutouts are widened by 0.1-0.5 px so the thin tail stays open (see
`..\vector\README.md`).

## [app\\](app/) — application icon

| File | What |
|---|---|
| [bhc-wb-gui.ico](app/bhc-wb-gui.ico) | 16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128 (32-bit BMP) + 256 (PNG). The bhc-wb-gui app window / taskbar icon. |
| [bhc-wb-16](app/bhc-wb-16.png) … [bhc-wb-256.png](app/bhc-wb-256.png) | Each ICO entry as its own RGBA PNG (identical pixels). |

The sizes are Microsoft's Win32 set: the shell picks the exact size for each surface and scale (taskbar 24 / 30 / 36 /
48 px at 100 / 125 / 150 / 200 %, Start and search, Explorer views up to 256). Without 30 and 36 Windows would downscale
32 and 40 for the taskbar at 125 % and 150 %. Source:
https://learn.microsoft.com/en-us/windows/apps/design/iconography/app-icon-construction

## [folder\\](folder/) — folder and shortcut icon

| File | What |
|---|---|
| [bhc-wb-folder.ico](folder/bhc-wb-folder.ico) | Same 15 entries as the app icon, as its own file so a folder or shortcut can point at it without depending on the app. |
| [desktop.ini](folder/desktop.ini) | Template: `[.ShellClassInfo]` / `IconResource=C:\path\to\bhc-wb-folder.ico,0`. |

To give a folder the icon: copy `desktop.ini` into the folder, set `IconResource` to the absolute path of
`bhc-wb-folder.ico`, then

```powershell
attrib +s "C:\path\to\Folder"
attrib +h +s "C:\path\to\Folder\desktop.ini"
```

For a shortcut: Properties > Change Icon > browse to `bhc-wb-folder.ico`.

## [tiles\\](tiles/) — reference only (unpackaged)

| File | What |
|---|---|
| [bhc-wb-tile-44x44](tiles/bhc-wb-tile-44x44.png) / [71x71](tiles/bhc-wb-tile-71x71.png) / [150x150](tiles/bhc-wb-tile-150x150.png) / [310x310](tiles/bhc-wb-tile-310x310.png).png | Tile / Store sizes at 100 % scale, transparent. |
| [bhc-wb-tile-310x150.png](tiles/bhc-wb-tile-310x150.png) | Wide tile, 150 px mark centred, transparent. |

These only matter if bhc-wb-gui is ever packaged as MSIX, and Windows 11 does not show tiles. A packaged app needs the
MSIX asset names, scale-100…400 and targetsize variants instead (see the Microsoft page above).

## Dark themes: white keyline

Every icon here (ICO entries, PNGs, tiles) has a white keyline just outside the disc, max(1 px, 1.5 % of
the size); the mark shrinks by that much a side so the keyline fits. On white it is invisible; on the Windows 11 dark
taskbar (`#202020`, where the navy is only about 1.6:1) it outlines the disc, so one ICO serves both themes. The keyline
is a round-joined stroke of the mark's own silhouette. Source for the contrast guidance:
https://learn.microsoft.com/en-us/windows/apps/design/iconography/app-icon-design

Previews: `..\previews\contact-sheet.png`, `..\previews\taskbar-preview.png`. Generator: `..\scripts\gen_icons.py`.
