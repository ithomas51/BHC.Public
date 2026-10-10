# Regenerate and verify docs\brand-assets

Every deliverable in `brand-assets` is rendered from the vector sources by these scripts. Nothing is hand-edited.

## 1. Scratch environment

Nothing is installed into a project venv. CPython 3.12 via uv:

```powershell
uv venv $env:TEMP\iconenv --python 3.12
uv pip install --python $env:TEMP\iconenv\Scripts\python.exe -r requirements.txt
$py = "$env:TEMP\iconenv\Scripts\python.exe"
cd <repo>\docs\brand-assets\scripts
```

## 2. Build and verify

```powershell
& $py build_all.py    # rewrites every deliverable in brand-assets (deterministic; optional argument: another root)
& $py verify.py       # must end with ALL OK (exit code 0)
```

`verify.py` renders everything afresh from vector into a temp folder and requires every landing file to be identical to
it (PNG pixel for pixel, ICO byte for byte, SVG byte for byte up to line endings), with no generated file missing and
no unexpected file (only `*.md` and `scripts\` are allowed besides the generated files). It then runs the property
checks per platform: sizes, modes, fills, halo / seam, fringe, palette, circular crop, file-size limits.

To regenerate a single generator's output: `& $py -c "import gen_lockups, paths; gen_lockups.build(paths.ROOT)"`.

## 3. Scripts

| Script | Role |
|---|---|
| [paths.py](paths.py) | Every path read (landing root, vector sources, label font) and the landing layout (folder per platform). |
| [parse.py](parse.py) | SVG path to cubic segments, cubic evaluation, least-squares circle fit. |
| [build_svg.py](build_svg.py) | The mark in a square 512 viewBox: path, silhouette (outer arcs + arc across the left gap), master / mono / maskable SVG. |
| [render.py](render.py) | Exact coverage-mask compositing of the mark at any size and colour (white cutouts, small-size widening, scale, background). |
| [lockup.py](lockup.py) | Banner / stacked lockups from their SVGs with the same compositing (navy mark, black wordmark, optional white cutouts). |
| [gen_icons.py](gen_icons.py) | Navy icon set: `windows\app`, `windows\folder`, `windows\tiles`, `web` (incl. `site.webmanifest`), `mobile\play-store`, `vector` SVGs, two previews. |
| [gen_lockups.py](gen_lockups.py) | `lockups\banner`, `lockups\stacked` (filled, transparent, white), and the stacked logo pair in `google-workspace\admin-logo`. |
| [gen_mobile.py](gen_mobile.py) | `mobile\android\res` (adaptive VectorDrawable launcher icon, legacy PNGs), `mobile\ios\AppIcon.appiconset`, the adaptive-mask preview. |
| [gen_3a4d5c.py](gen_3a4d5c.py) | `google-workspace\profile-photo` (#3A4D5C), its SVG in `vector`, two previews. |
| [gen_workspace.py](gen_workspace.py) | The banner Admin console logo in `google-workspace\admin-logo` (320 x 132 and 3x). |
| [build_all.py](build_all.py) | Runs every generator. |
| [verify.py](verify.py) | The vector check and property checks above. |

## 4. Inputs

- Mark: `docs\BellevueHealth Care\bellevuehealthcare\assets\SVG\logo\svg\2e3591\BH_icon_2e3591_512x512.svg`
- Lockups: `BH_reversed.svg` and `BH stacked_reversed.svg` in `docs\BellevueHealth Care\bellevuehealthcare\assets\SVG\`
- Font for preview labels: `C:\Windows\Fonts\segoeui.ttf`
