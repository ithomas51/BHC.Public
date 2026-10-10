# mobile — Android, iOS and Google Play icons

## [android\res\\](android/res/) — launcher icon (copy into `app/src/main/res`)

| Path | What |
|---|---|
| [mipmap-anydpi-v26\ic_launcher.xml](android/res/mipmap-anydpi-v26/ic_launcher.xml), [ic_launcher_round.xml](android/res/mipmap-anydpi-v26/ic_launcher_round.xml) | Adaptive icon (API 26+): background `@color/ic_launcher_background`, foreground and monochrome drawables. |
| [drawable\ic_launcher_foreground.xml](android/res/drawable/ic_launcher_foreground.xml) | **VectorDrawable** built from the mark's own path data (white even-odd cutouts, the 3-unit seam under-stroke, navy mark). 108 dp layer; mark 64 dp, centred, inside the 66 dp safe zone. |
| [drawable\ic_launcher_monochrome.xml](android/res/drawable/ic_launcher_monochrome.xml) | Android 13 themed icon: the mark's shape only, same placement; the system tints it and the cutouts show the background. |
| [values\ic_launcher_background.xml](android/res/values/ic_launcher_background.xml) | `#FFFFFF`. |
| mipmap-{[mdpi](android/res/mipmap-mdpi/),[hdpi](android/res/mipmap-hdpi/),[xhdpi](android/res/mipmap-xhdpi/),[xxhdpi](android/res/mipmap-xxhdpi/),[xxxhdpi](android/res/mipmap-xxxhdpi/)}\ic_launcher.png, ic_launcher_round.png | Legacy icons (API 25 and below): 48 / 72 / 96 / 144 / 192 px, mark on the 44 / 48 keyline, transparent. Unused if minSdk >= 26. |

Manifest: `android:icon="@mipmap/ic_launcher"` and `android:roundIcon="@mipmap/ic_launcher_round"`.
Source: https://developer.android.com/develop/ui/views/launch/icon_design_adaptive

## [ios\AppIcon.appiconset\\](ios/AppIcon.appiconset/) — Xcode app icon

| File | What |
|---|---|
| [AppIcon-1024.png](ios/AppIcon.appiconset/AppIcon-1024.png) | Any (light): 1024 x 1024, opaque RGB (no alpha), white, mark at 80 %. No rounded corners (iOS applies the mask). |
| [AppIcon-1024-dark.png](ios/AppIcon.appiconset/AppIcon-1024-dark.png) | Dark (iOS 18+): transparent background and cutouts, disc `#636BCE` (the navy's own hue and saturation, lightened to 4.5:1 on black). |
| [AppIcon-1024-tinted.png](ios/AppIcon.appiconset/AppIcon-1024-tinted.png) | Tinted (iOS 18+): grayscale, white disc on black, cutouts black; the system tints the light areas. |
| [Contents.json](ios/AppIcon.appiconset/Contents.json) | Single-size universal iOS entries: any, and `luminosity` `dark` / `tinted` appearances. |

Drop the folder into the app's `Assets.xcassets`. Apple: "Provide your tinted app icon as a grayscale image. Provide your
dark app icon with a transparent background so the system-provided background can show through."
(https://developer.apple.com/documentation/xcode/configuring-your-app-icon). The appearance keys in `Contents.json`
follow the format Xcode writes; that page does not list them, so open the set in Xcode once to confirm.

## [play-store\\](play-store/)

| File | What |
|---|---|
| [play-store-512.png](play-store/play-store-512.png) | 512 x 512, 32-bit PNG, opaque white, square corners, no shadow (Play applies both). Mark 384 px: a shape logo sits on the keyline grid, not full bleed. |

Source: https://developer.android.com/google-play/resources/icon-design-specifications

Preview: `..\previews\android-adaptive-masks.png` (circle, squircle, rounded square, teardrop masks; themed icon).
Generators: `..\scripts\gen_mobile.py` (android, ios), `..\scripts\gen_icons.py` (play-store).
