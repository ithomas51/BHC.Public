# profile-photo — #3A4D5C BH mark for Google profile pictures

Same mark and white-filled cutouts as the navy set; only the fill colour is slate `#3A4D5C`.

**Upload: `BH_icon_3a4d5c_1024_slate.png`.**

| File | Mark size | Outside the mark | Notes |
|---|---|---|---|
| BH_icon_3a4d5c_{[192](BH_icon_3a4d5c_192_slate.png),[512](BH_icon_3a4d5c_512_slate.png),[1024](BH_icon_3a4d5c_1024_slate.png)}_slate.png | full | opaque `#3A4D5C` | Any circular crop lands on slate: no clip, no sliver, nothing to flatten. **Recommended.** |
| BH_icon_3a4d5c_{[192](BH_icon_3a4d5c_192_white.png),[512](BH_icon_3a4d5c_512_white.png),[1024](BH_icon_3a4d5c_1024_white.png)}_white.png | 96 % | opaque `#FFFFFF` | Do not upload; only for a client that flattens transparency. Shows an uneven white ring on dark UIs. |
| BH_icon_3a4d5c_{[192](BH_icon_3a4d5c_192_transparent.png),[512](BH_icon_3a4d5c_512_transparent.png),[1024](BH_icon_3a4d5c_1024_transparent.png)}_transparent.png | 96 % | alpha 0 | Fine if the client keeps alpha; a black ring if it flattens to black. |
| [BH_icon_3a4d5c_98x98.png](BH_icon_3a4d5c_98x98.png) | full | alpha 0 | The first 98 px version (white-filled). Too small for clients that show the photo larger; it gets upscaled and soft. |
| [BH_icon_3a4d5c_98x98_mono.png](BH_icon_3a4d5c_98x98_mono.png) | full | alpha 0 | Single colour, transparent cutouts. Light backgrounds only. |

Why 96 %: the mark's fitted circle (R 256.82 on a 512 canvas) is slightly larger and off-centre relative to the
inscribed crop, so at full size it overhangs the crop by up to 3.7 px at 1024 (0.36 % of the width, 0.72 % of the radius) and leaves thin
uncovered crescents. At 98 % and below nothing falls outside the crop; 96 % leaves a margin of about 1.6 % of the width.

Google (checked 2026-10-10): Admin help "Add or change a user's profile photo": JPEG or PNG, max 5 MB, max 20 million
pixels, need not be square (scaled automatically); no minimum stated. Directory API `UserPhoto`: uploads through the API
are downsized to 96x96 whatever their size.

Previews: `..\..\previews\preview-98.png`, `..\..\previews\preview-profile-client-sim.png` (each upload downscaled to
32-384 device px and circle-cropped on dark and light UI, plus a flatten-to-black case). SVG: `..\..\vector\BH_icon_3a4d5c.svg`.

Checked by `..\..\scripts\verify.py`: sizes, < 5 MB, alpha == silhouette coverage, backgrounds exact, nothing of the mark
outside the crop (96 % variants), slate crop disc slate/white only, no off-palette colours.
Generator: `..\..\scripts\gen_3a4d5c.py`.
