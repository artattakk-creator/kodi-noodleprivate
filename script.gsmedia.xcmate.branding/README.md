# XCMate BINGIE Space Blue Manager 0.2.0

Optionales Kodi-Programm-Add-on für **Titan BINGIE MOD 2.2.3** und Kodi 21 Omega.

## Inhalt

- Das vom Nutzer bereitgestellte **XCMate-intro.mp4** unverändert (H.264 1920×1080, 7,04 Sekunden, AAC-Sound).
- Splash aus dem Videointro und metallisches XCMate-Logo aus unserem Designmuster.
- **Space Blue** für die BINGIE-Menüs: rund 90 Skin-Farbwerte plus Anzeige-Namen für Colorpicker, benannte globale Farben, OSD, Buttons, Header, Panel, Scrollbars, Fortschritt, Fokus-**farben** und ausgewählte fest eingetragene rote Texturen.
- Vorherige Werte und sämtliche überschriebene Skin-Dateien gesichert; vollständiges Wiederherstellen per Add-on-Menü.

## Verwendung

Kodi → Add-ons → Aus ZIP-Datei installieren → script.gsmedia.xcmate.branding-0.2.0.zip.
Danach unter **Programm-Add-ons** den **XCMate BINGIE Space Blue Manager** starten.

1. **Status / Vorschau** zuerst lesen.
2. **Space Blue und Branding installieren**: Änderungen nur nach expliziter Bestätigung.
3. Kodi vollständig neu starten.
4. Für den Rückbau **Original-BINGIE wiederherstellen** auswählen und Kodi neu starten.

Das Add-on führt bei bloßer Installation **keine Skin-Änderung** aus. Es verändert
keine Widget-Routen, SkinShortcuts-Quellen, Kodi-Kataloge, Provider, EPG, Fokus-Positionen
oder Videobibliotheken. Der bereits bekannte Fokus-Geometriefehler aus XCMate 0.1.29.74
ist **nicht** Bestandteil des Branding-Pakets.

Originale liegen unter Kodi `userdata/addon_data/script.gsmedia.xcmate.branding/backups/<Zeitstempel>/`.
Das Add-on und dessen Daten nicht löschen, solange das Branding installiert ist.

## Einschränkungen

- **Entwicklungskandidat:** automatische Funktion und Rückbau auf einem echten
  Android-TV/BINGIE-Gerät noch **nicht** abgenommen. Erst auf Testbox verwenden.
- Unterstützt genau die bestätigte Skin-Version **2.2.3**. Unbekannte Skin-Dateien,
  externe Änderungen oder geänderte ZIP-Assets lösen sichere Abbrüche aus.
- Farbmodus verändert die von BINGIE verwendeten dynamischen Farbstrings und globale
  benannte Farben; **in Texturen.xbt eingebrannte Pixel** bleiben unberührt.
  Manche Fremd-Add-on-Ansichten nutzen eigene Farben. Das ist keine vollständige
  Neugestaltung jeder Grafik.
- Die Kodi-Skin-Intro-Einstellung muss aktiviert sein. Bestehende Player-Wiedergabe
  vor der Anwendung beenden.
- Bei späteren BINGIE-Updates kann ein Abgleich/Rebuild notwendig werden. Der
  Wiederherstellungsmodus verhindert das Überschreiben zwischenzeitlich geänderter
  Dateien und individuell veränderter Farben.
- Kein Update des GS-Media-Repository-Katalogs und keine Auto-Installation.

## Integrität

Siehe `resources/media/asset_sha256.json`, sowie die ZIP-Prüfsumme in der
beigefügten SHA256-Datei.
