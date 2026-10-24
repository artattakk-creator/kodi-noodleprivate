# .30-D – Originaler Space-Splash im Lightweight-Skin (#122)

Die Originaldatei aus themes/xcmate/space-premium/assets/branding/splash-1920.jpg
liegt bytegleich im Addon unter resources/media/lightweight_splash.jpg.
SHA256: 2553464f81de674f3de8726ba1ec81dcf57d7c0232d39aa3322af10ee0435fcc
Kein Nachbau, keine Neugenerierung, kein Netzwerk- oder Premium-Paket-Download.

Core/Lightweight-Home und Einstellungsmenüs verwenden dieses lokale Hintergrund-
Fallback. Film-/Serienstart und Suche behalten den Splash auch beim Fokuswechsel
und Artwork-Refresh. Echte Detail-Fanarts dürfen weiter angezeigt werden; bei
fehlendem Fanart bleibt der Splash. Lesbarkeits-Shade liegt wie bisher darüber.
Keine Layout-, Fokus-, Navigations-, Player- oder Premium-Aktivierungsänderung.
Premium-XML erkennt den neuen Core-Texturpfad und ersetzt ihn wie zuvor mit seinem
eigenen Hintergrund. Neuer Renderer-Cache-Namespace verhindert alte XML-Kopien.

Das Original-XCMate-Icon bleibt unverändert:
81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135
Auch die Original-Theme-Assets werden nicht geändert.

19 gezielte Hosttests PASS: bytegenaue Asset-/Icon-Prüfung, Core-Home/Settings,
Film-/Serienlanding, Suche und asynchroner Cover-Refresh, Detail-Fanart,
Premium-Verhalten, Fokus-/Frame-/Kontrast- und Theme-Port-Regressionen.

```sh
PYTHONPATH=tests:src/plugin.video.xtreammate/resources/lib python -m unittest -v \
  test_xcmate_splash_02930 test_xcmate_focus_02925 test_xcmate_theme_port_02924
```

Android-Abnahme NOT_TESTED: Core wählen, Home/Filme/Serien/Suche und Menüs öffnen;
Originalmotiv, Textlesbarkeit, unverändertes Icon, stabile Hintergründe bei
Cover-Nachladung und IR-Fokus prüfen. Eigene bestehende Anzeigepräferenzen bleiben
erhalten; kein Reset zur Abnahme erforderlich. Premium separat optional prüfen.
Kein main-Merge, Release oder OTA.
