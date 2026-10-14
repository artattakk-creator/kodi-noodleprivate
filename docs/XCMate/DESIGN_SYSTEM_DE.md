# XCMate – freigegebenes Space-Design und geplantes Themesystem

**Freigabe durch Nutzer:** 14.10.2026. Das metallisch-silberne „XCMate“-Logo vor einem dunklen Planeten und die monochrome, atmosphärische Weltraum-Grafik mit Horizont/Milchstraße wurden ausdrücklich als Designbasis bestätigt. Bildsprache bei jeder Erweiterung beibehalten.

## Originalquellen

- `grafik.png`: vom Nutzer ausdrücklich akzeptiertes XCMate-Logo, 573 × 358 px.
- `imagegen.png`: akzeptiertes Space-Hintergrundmotiv, 1672 × 941 px.
- Lokales Übergabepaket kann zusätzlich aus den Quellen `XCMate_icon_preview_512.png`, `XCMate_fanart_preview_1920x1080.jpg` und `XCMate_UI_panel_slate_1280x720.png` enthalten.
- **Nicht behaupten, die Originalgrafiken seien im GitHub-Repo**, solange die Binärdateien nicht tatsächlich vorhanden und verifiziert sind. Branding-Docs sind im Repo; der komplette Raster-Asset-Upload ist gesondert zu prüfen.

## Visuelle Festlegungen

- Standard: **edles, neutrales Dunkelgrau („Slate“) mit leichten silbernen Akzenten**. Stil hochwertig, kontrastreich, ruhig, futuristisch; kein Neon-Übermaß.
- Basis `#1B1D21`; obere Fläche `#292D33`; Panels `#32363D`; Rand `#59616A`; Text `#F0F2F5`; Sekundärtext `#B6BCC6`; Fokus/Silber `#D2D8E0`.
- Verlauf optional von `#30343A` nach `#191B20`; Android-TV muss ohne Shader oder GPU-Sondereffekte flüssig bleiben.
- Wählbare alternative Akzente (spätere UI-Einstellung): Ice Blue `#6EBDD9`, Violet `#9A85CE`, Steel `#95A7B8`, warme Amber `#D3AD79`.
- Statusfarben funktional: Aktiviert `#70B98B`, deaktiviert `#B97A7A`; zusätzlich Häkchen/Kreuz statt allein Farbe (Barrierefreiheit).
- Gut sichtbarer Fokusrahmen für Fernbedienung (kein reines Hover-Konzept); ausreichend große Schrift und Safe Area für TV-Overscan.

## Vorgesehenes vollständiges Grafikset

- Kodi `icon.png` (quadratisch, mindestens 512×512), `fanart.jpg`/Kodi-konforme Fanart.
- XCMate-Logo als breite Wortmarke und optional getrenntes `XC`-Signet.
- Kategorien-/Navigations-Icons für Live-TV, Sendergruppen, EPG, Filme, Serien, Neueste Inhalte, Weiterschauen, Favoriten, Aufnahmen, Suche, Einstellungen und Fernbedienung.
- TV-Sidebar/Player-OSD als dezentes Slate-Panel; Fokus-/Auswahlrahmen und Status-Häkchen.
- 16:9-Landschafts-Widget-Bild für Titan BINGIE MOD; Poster und Senderlogos vorrangig aus Anbieter-Caches.
- Quellgrafiken und exportierte PNGs verlustfrei im späteren Assets-Ordner dokumentieren; kein Nutzerlogo durch provisorische Schriftgrafik ersetzen.

## Theme-Einstellungen – geplanter Entwicklungsstand

`Einstellungen → Erscheinungsbild → Farbschema`: **Slate Grau** (Default), Ice Blue, Violet, Steel, Amber; `Akzentfarbe`, `Kontrastmodus`, später `Verlauf an/aus`. Theme-Daten persistent je Kodi-Profil ohne Rückwirkung auf fremde Kodi-Skins. Das Theme beeinflusst XCMate-eigene Dialoge/OSD/Artworks; Kodi-native Dialoge richten sich weiterhin nach Kodi/Titan BINGIE MOD. **Die freie Farbauswahl ist spezifiziert, im Release 0.1.9 nicht nachgewiesen.**

## Akzeptanz

Originalbildsprache, Grauton als Standard, vollständig via Android-Fernbedienung nutzbar, keine unlesbaren Transparenzen, stabil bei 1080p und 4K, kein Erzwingen anderer Kodi-Skins.
