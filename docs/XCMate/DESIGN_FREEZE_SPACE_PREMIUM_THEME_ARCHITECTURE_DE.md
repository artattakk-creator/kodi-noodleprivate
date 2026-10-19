
# XCMate – Design-Freeze: Variante 1 „Space Premium“ und spätere installierbare Themes

**Freigabe:** 19.10.2026 durch Nutzer. **Status:** Verbindliche Designentscheidung und technische Planungsanweisung, keine bereits erstellten/hochgeladenen Einzelassets, keine implementierte Theme-Downloadfunktion.
**Basis:** XCMate 0.1.26 (produktiv) / Zielentwicklung 0.1.27, Repo artattakk-creator/kodi-noodleprivate.
**Referenz:** Die im Chat erzeugte Dreifach-Designmuster-Tafel, **linke Spalte „VARIANTE 1 – SPACE PREMIUM“**. Das konkrete Referenzbild befindet sich im Chat, **nicht als Binärdatei auf GitHub**.

## A. Ab jetzt ausschließlich Design 1 produzieren

- **Design 1 „Space Premium“ ist der einzig ausgewählte Standard.** Design 2 „Cinematic“ und Design 3 „Neon Future“ bleiben unverbindliche Ideen für später herunterladbare Add-on-Theme-Pakete; keine Design-2-/Design-3-Dateien in der aktuellen Produktionsphase.
- Motivwelt: tiefblauer Weltraum, blau leuchtende Erdkrümmung bzw. Planetenhorizont, Sterne, orbitales Licht, optional elegante Space-Station im oberen Hintergrund. Markantes dreidimensionales verchromtes X mit blauen Lichtkanten und lesbarer Wortmarke XCMate. Tiefenwirkung, Hochglanz, Cinematic, **keine schlichte graue Standardoberfläche**.
- Designpalette **vorläufige Codex-Tokens**: Hintergrund #061322, Navy #0A2947, Elektrischblau #159FEA, Cyan-Fokus #42D9FF, Ice-Text #E6F5FF, Sekundärtext #88A6BE. Visuelle Abnahme ist wichtiger als eine pixelgenaue Tokenvorgabe.
- Die sechs Home-Icons und sechs Hintergründe, zehn Settings-Kategorie-Icons/Hintergründe, EPG, Filme, Serien, Player, Suche und Widget-Fallbacks sollen die **gleichen Markenwerte** tragen. Breite ruhige, teilweise transparente blaue Panels, gut lesbare Texte, sichtbarer Fokus.
- Echte Film- und Serien-Backdrops beim fokussierten Titel weiterhin dynamisch aus Provider-Metadaten laden. Space-Premium-Grafiken dort nur als Rahmen/Fallback; keine Fake-Filmplakate erstellen.
- Das älter freigegebene Logo und das Space-Original sind in ARTWORK_ASSET_MANIFEST_DE.md mit Referenz-Hashes dokumentiert, aber das Manifest meldet, dass Originaldateien noch nicht als GitHub-Binärdateien vorliegen. **Neue Designwahl supersediert das alte generische Anthrazit-/Metallgrau-Muster**, nicht den Datenschutz oder die Quell-/Lizenzdokumentation. Tatsächlich eingesetzte Wortmarke und Icon erst nach Einzelbild-Abnahme ersetzen.
- **0.1.26-Live-TV-Funktion, Fernbedienung und OSD sind auf Funktions-FREEZE.** Keine Kodi-Action-/Fokus-/Playback-Umbauten zur Anpassung von Grafiken; bestehende Texturen nur nach gesondertem Gerätetest.

## B. Technische Architektur: XCMate Themes, nicht Kodi-Skins

- Ein **XCMate-Theme** verändert XCMate-interne Hintergründe, Icons, Farben, Fokus- und Paneltexturen. Es ist **kein Wechsel des globalen Kodi-Skins**. Titan BINGIE MOD und dessen vorhandene Nutzer-Widgets bleiben installiert und unberührt. Separates XCMate-Kodi-Skin-Issue #14 ist unabhängig.
- Ein semantischer Theme-Asset-Resolver mit Stable Keys (z. B. background.home, background.movies, icon.settings, icon.epg, panel.sidebar, focus.default), zentralem Palette-Objekt und konfigurierbaren Fallbacks. Kodi-Control-IDs und die D-Pad-Navigation ändern sich bei Themewechsel **nicht**.
- **Für den nächsten Entwicklungsschritt nur das gebündelte Space-Premium-Theme integrieren**; vorerst keine fertige Benutzerdownload-/Marketplace-Funktion vortäuschen.
- Vorgeschlagenes rein deklaratives theme.json: schema_version 1, id space-premium, name Space Premium, author GS Media, version, supported_xcmate, palette (background/accent/focus/text) und assets (Key-zu-relativem-Bildpfad-Mapping). Alle erforderlichen Keys, Versionsprüfung und Fallbacks im Test kontraktieren.
- Einstellung zukünftig über **Einstellungen → Darstellung & Sprache → XCMate-Design**, vorerst nur „Space Premium“ auswählbar. Bei defektem/verlorenem Theme immer sicher auf das Standarddesign zurückgehen.
- Weitere Designs 2 und 3 könnten **später** als separat installierbare ZIPs mit Bildern plus theme.json geliefert werden. Keine importierten ausführbaren Python-, Javascript- oder XML-UI-Dateien durch Themewechsel ausführen, keine ungeprüften Pfade akzeptieren.
- Für späteren lokalen ZIP-Import/Katalog-Download: sichere relative Pfade, keine Symlinks/Zip-Slip/ZIP-Bomb, Datei-/Pixel-/Speicherlimits, bevorzugt verifizierbare SHA-256-/Signaturprüfung, HTTPS, mit Nutzerfreigabe. **Diese Funktion ist Zukunftsoption, noch nicht implementiert oder zum aktuellen Release verpflichtet.**
- Shared Texturen und Kodi-Farb-/Alpha-Parameter statt aller Icons je Farbvariante zu duplizieren. Vorheriges Gesamtmanifest **98 logische Grafik-Slots** und Android-Performancebudget beachten.

## C. Konkrete Lieferung und Abnahme

**Erstphase Design-1-Preview:** individuelles App-Icon **512×512 PNG** und eine separate vollständige XCMate-Hauptmenü-Musteransicht **1920×1080, 16:9**. Beide exakt in Variante-1-Motivwelt aufbauen und visuell freigeben lassen; ein zusammengesetztes Mockup ersetzt keine einzeln nutzbaren Assets.

**Grafikproduktion danach:** 35–45 priorisierte Laufzeitdateien und später das vollständige 98-Slot-Mapping aus GRAPHICS_V2_ASSET_PLAN_027_DE.md. Die freigegebenen Quelldateien für späteren Austausch separat in artwork/xcmate/ halten, nicht unnötig in Kodi-ZIP ausliefern.

**Implementierung:** Themepfade testen, addon.xml-Fanart-Pfad-Mismatch (fanart.png eingetragen, fanart.jpg vorhanden) in kontrolliertem PR korrigieren, Kodi-21-/Android-TV-Safe-Area und Fokus prüfen; Bilder asynchron cachen. Die drei BINGIE-MOD-Widgets weiterhin in der bestehenden Skin-Konfiguration per Kodi-Widgetrouten nutzen.

**Releasekontrolle:** Neuer Branch + CI + Pull Request + echter TV-Gerätetest. **Kein eigenmächtiger Merge nach main, keine automatische Veröffentlichung.** XCMate 0.1.26 bleibt bis zur separaten Freigabe installiert.

## D. Direktverweis für Codex

Lies dieses Design-Freeze-Dokument und GRAPHICS_V2_ASSET_PLAN_027_DE.md vor dem Grafik-Sprint. Erzeuge und integriere **nur Design 1 „Space Premium“**. Bereite die Asset-Resolver-Schnittstelle so vor, dass weitere rein grafische Designpakete *später* ergänzbar wären, ohne Kodi/BINGIE MOD oder die gefreezte Live-TV-Bedienung zu verändern. Designs 2/3 noch nicht bauen.
