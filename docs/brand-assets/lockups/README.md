# lockups — mark + "BellevueHealthcare" wordmark

Rendered from `BH_reversed.svg` (banner) and `BH stacked_reversed.svg` (stacked) in
`docs\BellevueHealth Care\bellevuehealthcare\assets\SVG\`. Transparent background, zero fringe pixels, no off-palette
anti-aliasing colours.

| Variant | Banner (`banner\`) | Stacked (`stacked\`) | Colours | Use |
|---|---|---|---|---|
| filled | [`BH_reversed_filled_{W}x{H}.png`](banner/) | [`BH_stacked_reversed_filled_{W}w.png`](stacked/) | navy mark, white cutouts, black wordmark | **Default** on light backgrounds, tints and photos (the swoosh stays white) |
| transparent | [`BH_reversed_{W}x{H}.png`](banner/) | [`BH_stacked_reversed_{W}w.png`](stacked/) | navy mark, black wordmark, cutouts see-through | Plain white or light solid backgrounds where the background should show through |
| white | [`BH_white_{W}x{H}.png`](banner/) | [`BH_stacked_white_{W}w.png`](stacked/) | all white, cutouts see-through | Dark backgrounds, including the brand navy |

Sizes: banner 256x42, 512x84, 600x97, 800x129, 1200x194, 1600x258, 2400x388, 3600x581; stacked 256, 384, 512, 768,
1024, 1280, 1536, 1920, 2048, 2560, 3840, 4096 wide. 256x42 and 512x84 keep their legacy heights (the SVG aspect gives
41 / 83).

- "reversed" is the source SVGs' name; these are the dark-on-light versions. The light-on-dark set is `white`.
- Minimum sizes: banner 256x42 and stacked 256 wide. Below them use the mark alone (`..\vector\`).
- The artwork sits where the source artboards put it (slightly off-centre in the canvas, as in the originals).

Generator: `..\scripts\gen_lockups.py`.
