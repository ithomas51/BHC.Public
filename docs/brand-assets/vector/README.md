# vector — SVG masters of the BH mark

| File | What |
|---|---|
| [bhc-wb-master.svg](bhc-wb-master.svg) | Navy `#2E3591` mark, white-filled cutouts, transparent outside. 512 viewBox. No raster, no external refs. |
| [bhc-wb-mono.svg](bhc-wb-mono.svg) | Single colour `#2E3591`, transparent cutouts. Light backgrounds only (on dark the disc nearly disappears). |
| [bhc-wb-mono-white.svg](bhc-wb-mono-white.svg) | Single colour `#FFFFFF`, transparent cutouts, for dark backgrounds (including the brand navy). |
| [bhc-wb-maskable.svg](bhc-wb-maskable.svg) | Master at 80 % on a full-bleed **white** square (Android maskable safe zone). |
| [BH_icon_3a4d5c.svg](BH_icon_3a4d5c.svg) | Master in slate `#3A4D5C` (profile-photo colour). |

Every raster in `brand-assets` is rendered from these shapes (and the two lockup SVGs in the assets tree) by `..\scripts\`.

## Source

- Mark: `docs\BellevueHealth Care\bellevuehealthcare\assets\SVG\logo\svg\2e3591\BH_icon_2e3591_512x512.svg`
  (repo-relative). One compound path, fill `#2e3591`, viewBox `67.74 7.451 62.795 66.095`.
- No shape was redrawn; the path's bezier segments are copied verbatim, only translated and scaled into a square 512
  viewBox so the mark's bounding box (62.11 x 62.11 units, a near-circle) fills it.

## Fill method (white-filled cutouts)

The brand path is a single closed contour. Its outer boundary is a circle to within 0.5 % of the radius, broken only by
a 9-unit gap on the left where the lower wing of the cutout runs out to the edge. "Inside the mark's outline" is defined
as the outer-arc segments of the path, closed across that gap with an arc of the fitted circle.

- **SVG:** the white layer is one even-odd compound path (silhouette + mark path), exactly "silhouette minus mark". The
  outer edge of the white and of the colour are the same curve, so no white can appear outside it (no halo). A 3-unit
  white stroke along the inner contour is drawn *under* the colour to remove the faint anti-aliasing seam two abutting
  shapes leave; it stops 2 % short of the two points where the inner contour meets the outer edge, so it cannot poke out.
- **Rasters:** composited numerically from coverage masks rendered with resvg: `alpha = silhouette`,
  `colour = mark*cov_mark + white*(silhouette - cov_mark)`. The alpha of every transparent PNG equals the silhouette's
  coverage pixel for pixel, cutout interiors are pure `#FFFFFF`, and there are no seams or halos at any size.
- **Small sizes:** each size is rendered from the vector at that size. At 16 / 20 / 24 / 30 / 32 / 36 px the white
  cutouts are widened by 0.5 / 0.3 / 0.3 / 0.2 / 0.2 / 0.1 px (eroding the colour along the inner contour) so the thin
  lower tail and the left wing stay open; 40 px and above are the unmodified mark.

- **Keyline (transparent raster icons only):** the Windows ICO / PNGs / tiles, favicons and manifest "any" icons add a
  white keyline outside the disc (a round-joined stroke of the silhouette: max(1 px, 1.5 % of the size)) so
  the disc stays visible on dark themes. The SVG masters here are the mark itself, without it.

## Judgement calls

- **Maskable background: white, not navy.** On navy the circle disappears and only the white cutouts remain, which reads
  as a different mark. On white the full navy circle survives the mask.
- **Silhouette at the left gap** is closed with a circular arc, so the lower-left wing's white runs to the edge of the
  circle. Nothing is drawn outside the fitted circle.
- **SVG vs raster at small sizes.** The SVG seam fix is a fixed 3-unit stroke, which shrinks when a generic renderer draws
  the SVG below about 128 px; for small rasters use the supplied PNG / ICO files, which are exact. The only residue in the
  SVG at 512 px is 9 edge pixels at the two contour junctions, up to 25 % translucent.

Checked by `..\scripts\verify.py`: at 512 all 45 696 cutout-interior pixels are `#FFFFFF` alpha 255, alpha never exceeds
the silhouette (no halo), no raster or external references.
