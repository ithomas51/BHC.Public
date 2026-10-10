# admin-logo — Google Workspace Admin console logo (320 x 132)

Google displays the organization logo at exactly 320 x 132 (see `google-workspace-logo-policy.md`).

| File | Use |
|---|---|
| [google_workspace_logo_filled.png](google_workspace_logo_filled.png) | **Upload this one.** Stacked lockup in the 320 x 132 box, white-filled cutouts (the swoosh stays white on Gmail themes). Fills 89 % of the height: mark about 50 px, "Bellevue" about 30 px, "Healthcare" about 22 px tall. |
| [google_workspace_logo.png](google_workspace_logo.png) | The same with transparent cutouts. |
| [BH_google_workspace_logo_320x132.png](BH_google_workspace_logo_320x132.png) | Alternative: banner lockup 304 px wide, centred, white-filled. Fills only 29 % of the height (mark 37 px, wordmark 26 px), so it becomes a thin strip when Google scales the logo into the toolbar. |
| [BH_google_workspace_logo_960x396_3x.png](BH_google_workspace_logo_960x396_3x.png) | The banner at 3x for other uses. Google does not document using a larger upload. |
| [google-workspace-logo-policy.md](google-workspace-logo-policy.md) | Google's "Add your logo to Google Workspace" article (requirements, upload steps, logo policies), transcribed 2026-10-10. |

The stacked upload follows the 2026-10-10 design review. After uploading (it can take up to 4 days), check Gmail in light
and dark themes.

Upload: Admin console > Menu > Account > Account settings > Personalization (needs the Domain settings privilege; Chrome,
not Safari; can take up to 4 days to appear).

Checked by `..\..\scripts\verify.py`:
- the stacked pair (`google_workspace_logo*.png`): 320 x 132 RGBA, no 0<alpha<8 fringe, corners transparent, content
  within its box, every opaque pixel navy / black (filled: plus white and navy/white blends). 4.2 KB, well under the
  legacy 30 KB limit (not a check);
- the banner pair (`BH_google_workspace_logo_*.png`): exact size, RGBA, under the legacy 30 KB limit, no fringe, corners
  transparent, centred within 1 px, every opaque pixel black, white or a navy/white blend.

Known limit: the wordmark is black on transparent, so it disappears on a dark header (dark theme).

Generators: `..\..\scripts\gen_lockups.py` (stacked pair), `..\..\scripts\gen_workspace.py` (banner pair).
