# CODEX – XCMate: Installation 0.1.29.2 und Space Premium Theme 1.0

## Vollständiger Entwicklungs-, Integrations- und Installationsauftrag

**Projekt:** GS Media – XCMate  
**GitHub:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Google Drive:** https://drive.google.com/drive/folders/1f_CvKdgXGdTw1FFQ2vaCUjFFlG6Pp4db  
**Add-on-ID:** `plugin.video.xtreammate`  
**Aktueller Core:** XCMate 0.1.29.2  
**Zielsystem:** Kodi 21.3 Omega, Android TV, ARM 32-bit  
**Aktueller Kodi-Skin:** Titan BINGIE MOD  
**Theme:** XCMate Space Premium – Design 1  
**Geplante Theme-Version:** 1.0.0

---

## 1. Ausgangssituation

Die vollständige XCMate-Version 0.1.29.2 wurde über Pull Request #49 bereits in den Hauptbranch `main` integriert.

https://github.com/artattakk-creator/kodi-noodleprivate/pull/49

Der GitHub-Veröffentlichungsworkflow wurde erfolgreich abgeschlossen.

**Die Version 0.1.29.2 ist damit bereits im Repository vorhanden. Nicht erneut mergen oder unnötig neu veröffentlichen.**

Die vorhandenen Integrationstests sind dokumentiert:

- 462 bestandene Haupttests
- 26 ergänzende HTTP-/EPG-Tests
- Installierbares XCMate-ZIP im Repository
- Android-TV-Geräteabnahme steht noch aus

Die nächste Aufgabe besteht aus zwei miteinander verbundenen Arbeitspaketen:

**Arbeitspaket A:** Sichere Installation und Gerätetest von XCMate 0.1.29.2 vorbereiten.

**Arbeitspaket B:** Die 98 fertigen Space-Premium-Grafiken zu einem vollständigen, separat installierbaren XCMate-Theme zusammenführen und einen sicheren Theme-Installer entwickeln.

## 2. Arbeitspaket A – XCMate 0.1.29.2

Die vorhandene Datei prüfen:

`plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip`

Prüfungen:

1. ZIP-Datei ist vollständig und gültig.
2. `addon.xml` enthält die Version `0.1.29.2`.
3. Kodi-Repository-Index führt dieselbe Version.
4. SHA-256-Prüfsumme stimmt mit der tatsächlichen veröffentlichten Datei überein.
5. Keine Benutzerprofile oder persönlichen Zugangsdaten im Paket.
6. Update von 0.1.28 auf 0.1.29.2 ohne Neuinstallation des Add-ons möglich.

### Verbindliche Datensicherung

Vor der Installation eine Anleitung zur vollständigen Sicherung des XCMate-Profils erstellen.

Insbesondere sichern:

- Portal- und Accountdaten
- Aktivierte Sendergruppen
- EPG-Quellen und Zuordnungen
- Favoriten
- Wiedergabefortschritt
- Lokale Datenbanken
- Cover- und Metadatenbestände
- Fernbedienungsbelegung
- Startsender und Startgruppe

Vor dem Kopieren Kodi vollständig beenden und SQLite-Datenbanken einschließlich gegebenenfalls vorhandener WAL-/SHM-Dateien konsistent sichern.

**Keine App-Daten löschen, keine Konten zurücksetzen und keinen globalen Kodi-Reset durchführen.**

### Gerätetest

Eine schrittweise Testanleitung erstellen für:

- Kalt- und Warmstart
- Hauptmenü
- Startsender
- Fernbedienung und Overlays
- Schnellen EPG-Zugriff
- Kontinuierliche Senderliste
- Aktivierte Sendergruppen
- Film- und Serienstart
- Zuverlässigen Wiedergabestopp beim Verlassen
- Favoriten und Folgenstatus
- Persistente Cover und Hintergrundbilder
- Universellen Einrichtungsassistenten
- M3U-Import und Playlist-Editor
- Stalker-Unterstützung, soweit eine geeignete Testquelle verfügbar ist

Erst nach bestandenen realen Gerätetests die installierte Version als erfolgreich abgenommen dokumentieren.

---

# ARBEITSPAKET B – SPACE PREMIUM THEME 1.0

## 3. Grundlegende Vorgabe

Das Space-Premium-Design wurde grafisch bereits vollständig produziert und freigegeben.

**98 von 98 Grafikpositionen sind auf Google Drive vorhanden.**

Die Dateien wurden am 20.10.2026 erneut überprüft. Alle 98 erwarteten Dateinamen konnten in den Google-Drive-Kategorieordnern nachgewiesen werden.

Es ist deshalb keine neue Grafikproduktion erforderlich.

### Verbindlicher Masterordner

https://drive.google.com/drive/folders/1UPA7fLKIq21GkA4NzAPEVfLp2BvSpm3y

### Masterliste

https://drive.google.com/file/d/14NY62as0U-UWkTp_Rp3AiS0NreifxYOZ/view

Der Mastertracker definiert die 98 Positionen, Dateinamen und Verwendungszwecke.

**Die Originalgrafiken dürfen nicht ungefragt verändert, ersetzt oder neu generiert werden.**

## 4. Google-Drive-Quellverzeichnisse

Die Grafiken sind nach Funktionsbereichen gespeichert.

| Bereich | Anzahl | Google-Drive-Ordner |
|---|---:|---|
| Branding | 4 | https://drive.google.com/drive/folders/1E1Ob14vAyuM7NlLACNWEKWvzhsiNtcJL |
| Hauptmenü | 12 | https://drive.google.com/drive/folders/1IYCFPr6jTwxNI7elF42uOW98LYLEby19 |
| Einstellungen | 20 | https://drive.google.com/drive/folders/1hAVCr4SllD6E4saLCbXuF707cvBUSJOy |
| Filme und Serien | 14 | https://drive.google.com/drive/folders/1FnYj4u1E0fTA1GYwGkRoKwTLwAwH0VrO |
| EPG | 12 | https://drive.google.com/drive/folders/1Cg1x9AyT985hQ3tVgGkiU1iOSHQGWHsA |
| Player und Fernbedienung | 16 | https://drive.google.com/drive/folders/1rJzEAc48cQoSkKjeHLqVjld7_pPahmW4 |
| Navigation / Shared | 16 | https://drive.google.com/drive/folders/1xjo9dYcbpaYuidtm8YjUOX6-qkEHHI3o |
| Widgets | 4 | https://drive.google.com/drive/folders/1_nsaYc2bCXKOU4U8APCO94tREErWf1HJ |

Unveränderte Quellbilder liegen zusätzlich unter:

https://drive.google.com/drive/folders/1HDl6ANSi6giLqBl_IfTZ4VT5QkiD21Sv

Außerdem sind mehrere freigegebene Teil-ZIP-Dateien, JSON-Manifeste, Kontaktblätter und SHA-256-Dateien archiviert.

**Wichtig für Codex:** Google-Drive-Links sind keine Garantie für unmittelbaren binären Zugriff aus der Codex-Laufzeit.

Prüfe zuerst, ob die 98 Originaldateien tatsächlich heruntergeladen werden können. Falls nicht, dokumentiere exakt, welche Dateien übergeben werden müssen. Keine leeren Platzhalter als vollständiges Theme ausgeben.

## 5. Alle 98 Assets validieren

Vor dem Zusammenbau:

- Alle Dateinamen gegen die Masterliste abgleichen.
- Bilddateien öffnen und auf Fehler überprüfen.
- PNG-Transparenz prüfen.
- Bildauflösungen prüfen.
- Vorhandene SHA-256-Prüfsummen überprüfen.
- Doppelte Dateinamen und fehlende Assets erkennen.
- Originale nicht überschreiben.
- Dateien in die vorgesehene Theme-Verzeichnisstruktur überführen.

Erstelle einen maschinenlesbaren Prüfbericht.

Ein Theme darf erst als vollständig gelten, wenn **98 von 98 erforderlichen Assets tatsächlich vorhanden und lesbar** sind.

## 6. Unterschied zwischen XCMate-Theme und Kodi-Skin

Das Space-Premium-Paket ist ein eigenständiges **XCMate-Theme**.

Es soll ausschließlich XCMate-interne Gestaltungselemente ändern:

- Hauptmenü
- Navigationsleisten
- Kategorieansichten
- Einstellungen
- Live-TV-Bedienelemente
- EPG-Oberfläche
- Film- und Serienansichten
- Player-Overlays
- Icons und Hintergründe
- Fokusrahmen
- Widget-Fallbackgrafiken

**Titan BINGIE MOD bleibt installiert und unverändert.**

Keine Änderungen an globalen Kodi-Skin-Einstellungen.

Keine Modifikation globaler Kodi-Keymaps.

Keine automatische Änderung anderer Add-ons.

Kodi soll weiterhin beliebige kompatible globale Skins verwenden können, während XCMate sein eigenes Design darstellt.

## 7. Theme-Architektur

Entwickle eine zentrale Theme-Verwaltung.

Vorgeschlagene Struktur:

```text
xcmate-space-premium/
├── theme.json
├── assets/
│   ├── branding/
│   ├── home/
│   ├── settings/
│   ├── media/
│   ├── epg/
│   ├── player/
│   ├── shared/
│   └── widgets/
└── SHA256SUMS.txt
```

Das endgültige Paketformat wird versioniert und dokumentiert.

### Theme-Manifest

`theme.json` soll mindestens enthalten:

- Schema-Version
- Theme-ID `space-premium`
- Name `Space Premium`
- Theme-Version `1.0.0`
- Hersteller `GS Media`
- Unterstützte XCMate-Versionen
- Farbpalette
- Grafikzuordnungen
- Prüfsummen
- Erforderliche Dateien
- Optional unterstützte Funktionen

Farben und UI-Tokens aus der bereits freigegebenen Space-Premium-Designvorgabe übernehmen.

Keine grafische Neugestaltung ohne Freigabe.

### Asset-Resolver

Verwende stabile logische Schlüssel wie:

`background.home`

`background.movies`

`icon.settings`

`icon.epg`

`panel.sidebar`

`focus.default`

So können Themes später ausgetauscht werden, ohne XML-Layouts und Bedienungslogik für jede Grafik neu programmieren zu müssen.

## 8. Ein vollständiges Theme-ZIP bauen

Erzeuge das installierbare Paket:

**`XCMate-Space-Premium-1.0.0.zip`**

Das Archiv soll alle 98 freigegebenen Grafikdateien, das Theme-Manifest und die Prüfsummen enthalten.

Zusätzlich:

- README
- Versionsangabe
- Installationshinweise
- Lizenz-/Herkunftshinweise für die Grafiken

Keine persönlichen Daten.

Keine Zugangsdaten.

Keine ausführbaren Python-Skripte innerhalb eines Themes.

Keine unkontrollierten externen Abhängigkeiten.

ZIP-Inhalt automatisch validieren.

## 9. Theme-Installer direkt in XCMate

Entwickle in XCMate einen neuen Einstellungsbereich:

**Einstellungen → Darstellung & Sprache → XCMate-Designs**

Dort sollen folgende Funktionen verfügbar sein:

**Installierte Designs**

Zeigt vorhandene Themes einschließlich Version.

**Design aus GitHub installieren**

Öffnet einen Katalog verfügbarer Themes aus dem GS-Media-Repository.

**Design aus ZIP installieren**

Erlaubt die Auswahl einer lokal zugänglichen ZIP-Datei über den Kodi-Dateibrowser.

**Design aktivieren**

Aktiviert ein installiertes Theme.

**Standarddesign wiederherstellen**

Setzt XCMate auf das bisherige funktionierende Design zurück.

**Design entfernen**

Entfernt ein optionales Theme nach Bestätigung, ohne XCMate-Benutzerdaten zu verändern.

### Technische Sicherheitsvorgaben

Vor jeder Installation:

- ZIP-Datei prüfen.
- Manifest lesen.
- Theme-Version überprüfen.
- Dateipfade validieren.
- Path Traversal und ZIP-Slip verhindern.
- ZIP-Bomben und übergroße Bilder abweisen.
- Nur zugelassene Bild- und Metadatendateien installieren.
- Vorhandenes Theme erst nach erfolgreicher Validierung ersetzen.
- Fehler mit verständlicher Meldung anzeigen.

Bei beschädigtem Theme automatisch auf das funktionierende Standarddesign zurückfallen.

Ein Themewechsel darf **keinen laufenden Sender oder Film unterbrechen**, wenn dies nicht technisch unvermeidbar ist; nötigenfalls die Änderung erst nach Schließen der Medienansicht aktivieren.

## 10. Bereitstellung über GitHub

Das vollständige Theme soll nach erfolgreicher Prüfung im GS-Media-GitHub-Repository verfügbar werden.

Vorgeschlagene Ablage:

```text
themes/
└── xcmate/
    └── space-premium/
        ├── XCMate-Space-Premium-1.0.0.zip
        ├── XCMate-Space-Premium-1.0.0.zip.sha256
        └── theme.json
```

Der Theme-Katalog muss von XCMate über HTTPS gelesen werden können.

Nur ausdrücklich freigegebene Themes als installierbar anbieten.

Die vorhandenen Quellgrafiken und Freigabedokumente auf Google Drive unverändert erhalten.

Falls weitere Designs später folgen, sollen sie ohne Änderung des Installationsverfahrens ergänzt werden können.

## 11. Versionsstrategie für den Theme-Installer

XCMate 0.1.29.2 ist bereits auf `main` veröffentlicht.

Der Theme-Installer ist eine neue Core-Funktion, die in dieser Version noch nicht vorhanden ist.

Deshalb:

1. XCMate 0.1.29.2 nicht unter derselben Versionsnummer stillschweigend verändern.
2. Theme-Installer in einem separaten Feature-Branch entwickeln.
3. Nach der technischen Prüfung eine passende neue XCMate-Version vorschlagen, beispielsweise 0.1.30.
4. Das reine Theme-Paket unabhängig als `Space Premium 1.0.0` versionieren.
5. Beide Versionen und ihre Kompatibilität eindeutig dokumentieren.

Ein reines Theme-Update soll künftig ohne kompletten Austausch des XCMate-Cores möglich sein.

## 12. Designvorschau und Abnahme

Vor endgültiger Integration die tatsächlichen Grafiken in XCMate-Layouts darstellen.

Erstelle möglichst reale Kodi-XML-/Theme-Previews für:

- Hauptmenü
- Live-TV
- Gruppenliste
- Senderliste
- EPG
- Filme
- Serien
- Einstellungen
- Player-Infobar
- Untere Player-Bedienleiste

Keine reinen Werbemockups als Nachweis einer funktionierenden Oberfläche verwenden.

Fokus, Kontrast und Fernbedienungsnavigation unter Kodi 21.3 prüfen.

Die bereits vorhandenen XCMate-Funktionen dürfen nicht durch Theme-Änderungen beeinträchtigt werden.

## 13. Qualitätssicherung

Automatisierte Tests für:

- Vollständigkeit aller 98 Assets
- Theme-Manifest
- ZIP-Integrität
- SHA-256
- Theme-Installation
- Theme-Aktivierung
- Wechsel zwischen Standarddesign und Space Premium
- Wiederherstellung nach beschädigtem Theme
- Kodi-Neustart mit aktiviertem Theme
- Update eines bereits installierten Themes
- Fehlenden Speicherplatz
- Beschädigte ZIP-Datei
- Fehlerhafte Pfade
- Android-TV-Kompatibilität
- Persistenz der bestehenden XCMate-Einstellungen

Danach ist ein realer Android-TV-Test notwendig.

### Verbindlicher Funktions-Freeze

Die vorhandene Live-TV-Fernbedienung funktioniert bereits:

- OK → Infoleiste
- OK erneut → Untere Bedienleiste
- Links → Senderliste
- Links erneut → Gruppenliste
- Hoch/Runter → Senderwechsel
- Zurück → Schließt die vorgesehene Overlay-Ebene

Keine Änderung an dieser Bedienungslogik ohne gesonderten Auftrag.

## 14. Erwartete Lieferung

Am Ende bitte bereitstellen:

**Paket A – XCMate-Installationsprüfung**

- Bestätigung der aktuell veröffentlichten Version 0.1.29.2
- ZIP-Prüfung
- SHA-256
- Sicherungsanleitung
- Android-Gerätetestplan

**Paket B – Space Premium Theme**

- Vollständiges Theme-ZIP mit 98 Grafikdateien
- `theme.json`
- Prüfsummendatei
- Installationsdokumentation
- Theme-Abbildungen/Previews
- Automatisierter Testbericht

**Paket C – XCMate Theme-Installer**

- Separater Entwicklungsbranch
- Änderungen in den XCMate-Einstellungen
- GitHub-Theme-Katalog
- Lokaler ZIP-Import
- Designaktivierung
- Standarddesign-Fallback
- Tests
- Pull Request mit geplanter neuer Core-Version

## 15. GitHub-Arbeitsweise

Codex darf:

- Drive-Quellen analysieren, soweit zugänglich.
- Grafikdateien gegen den Mastertracker prüfen.
- Ein vollständiges Theme-ZIP erstellen.
- Den Theme-Installer implementieren.
- Tests ausführen.
- Neue Entwicklungsbranches und Pull Requests erstellen.
- Installations- und Testdokumentation erstellen.

Codex darf ohne gesonderte Freigabe NICHT:

- Bestehende Originalgrafiken ersetzen.
- Den globalen Kodi-Skin verändern.
- XCMate-Accountdaten löschen.
- `main` eigenmächtig ändern.
- Den Theme-Installer vorzeitig veröffentlichen.
- Eine neue produktive XCMate-Version freigeben.

## 16. Abschließende Arbeitsanweisung

**Beginne mit der Wiederherstellung und Validierung aller 98 Space-Premium-Grafiken aus Google Drive.**

Erstelle daraus ein vollständiges, geprüftes Theme-Archiv.

Implementiere anschließend den sicheren XCMate-Theme-Installer.

Bereite den GitHub-Theme-Katalog und einen separaten Pull Request vor.

Stelle alle Installationsdateien, Prüfsummen und Testberichte zur Kontrolle bereit.

**Ziel: Space Premium soll künftig direkt innerhalb von XCMate heruntergeladen, installiert, aktiviert und wieder deaktiviert werden können, ohne Titan BINGIE MOD oder bestehende Benutzerdaten zu verändern.**

Keine weiteren Grafik-Neuentwicklungen. Die 98 bereits freigegebenen Originale sind verbindlich.

**Keine eigenmächtigen Merges oder Releases. Abschlussbericht zur Freigabe vorlegen.**