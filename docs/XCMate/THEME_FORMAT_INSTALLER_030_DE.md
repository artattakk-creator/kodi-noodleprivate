# XCMate Themes – Paketformat 1 und Installer 0.1.30

> **AKTUALISIERUNG 20.10.2026:** Die früher fehlenden 98 Originale wurden aus dem freigegebenen Nutzer-ZIP übernommen und das Theme-Paket erfolgreich und reproduzierbar erstellt. Die weiter unten stehenden Netzwerk-/Quellblocker und „kein Bau“-Passagen dokumentieren einen **historischen** Zwischenstand. Der Theme-GitHub-Katalog enthält jetzt den geprüften 1.0.0-Eintrag im Draft-Branch; Main enthält ihn **bis zu einer ausdrücklichen Freigabe/Merge nicht**. **Aktueller Nachweis: [98er Build-/Abnahmebericht](SPACE_PREMIUM_98_BUILD_ABNAHME_20261020_DE.md).** Die vollständige grafische Runtime-Abnahme bleibt offen.

Entwicklungsstand; kein produktiver Theme-Download verfügbar. Der
[Originale-/Übergabeblocker](INSTALLATION_0292_UND_THEME_030_DE.md) bleibt offen.

## Format und Kompatibilität

Ein Theme-ZIP enthält direkt `theme.json`, `SHA256SUMS.txt`, `README.md`,
`LICENSE.txt` und Grafikdateien unter `assets/<Bereich>/`. Kein zusätzlicher
Wurzelordner, keine Verzeichniseinträge, Python-/JS-/XML-Dateien, Fonts oder Skripte.
Die ausführbaren Layouts stammen immer aus dem Core. ZIP64 und mehrteilige Archive
werden nicht unterstützt. Das Format ist unabhängig von Kodi-Add-on-ZIPs;
Theme-ZIPs werden **innerhalb XCMates**, nicht im Kodi-Add-on-ZIP-Installer geöffnet.

`theme.json` enthält:

| Feld | Vertrag |
|---|---|
| schema_version | Ganzzahl 1 |
| id/name/version/author | `space-premium` / `Space Premium` / `1.0.0` / `GS Media` |
| supported_xcmate | `{"min":"0.1.30","max_exclusive":"0.2.0"}`; obere Grenze exklusiv |
| palette | background/accent/focus/text/secondary, je sechs Hex-Zeichen ohne `#` |
| assets | Stabile logische Schlüssel → sichere relative Bildpfade |
| required_files | Genau die unterschiedlichen Bilder aus assets, keine Duplikate |
| sha256 | Jeder required_files-Pfad → tatsächlicher SHA-256 der Originalbytes |
| asset_properties (optional) | Pro Datei autoritative width/height/alpha für den Bauabgleich |
| capabilities (optional) | Rein deklarative Angaben; keine ausgeführten Features |

Space Premium verlangt **98 verschiedene vorhandene Bilddateien**, nicht 98 Aliasse
derselben Datei. Zusätzlich sind `background.home`, `background.movies`,
`background.series`, `background.epg`, `icon.settings`, `icon.epg`, `panel.sidebar`
und `focus.default` Pflichtschlüssel. Weitere Aliasse sind erlaubt. Der tatsächliche
98er-Abgleich mit dem verbindlichen Mastertracker kann erst nach dessen Übergabe erfolgen.

Die bisher freigegebenen vorläufigen Farbtokens sind `061322`, `159FEA`, `42D9FF`,
`E6F5FF`, `88A6BE`; Navy `0A2947` bleibt eine dokumentierte Materialreferenz.
Kein neues Design wurde daraus produziert. Das endgültige Manifest übernimmt die
Originalfreigabe, falls der aktuelle Mastertracker davon abweicht.

`SHA256SUMS.txt`: UTF-8/ASCII, nach Pfad sortiert, pro Zeile
`<64 lowercase hex><zwei Leerzeichen><relativer Pfad>\n`.
README/Lizenzhinweise erklären Herkunft/Freigabe/Nutzungsrechte, ohne Providerdaten.

## Sichere Verarbeitung und Speichergrenzen

- ZIP höchstens 160 MiB, höchstens 128 Dateien, entpackt insgesamt 256 MiB.
- Vor `ZipFile`-Initialisierung EOCD prüfen: zentrale Verzeichnisdaten höchstens
  64 KiB; damit erzeugt ein manipuliertes Archiv nicht Millionen ZipInfo-Objekte.
- Pro Bild höchstens 16 MiB komprimierte Bilddatei, höchstens 4096 pro Achse und
  8.388.608 Pixel; Metadatendatei höchstens 256 KiB. Nur PNG und JPEG.
- ZIP-Verhältnis höchstens 500:1. Keine verschlüsselten Einträge, Symlinks,
  Spezialdateien, absoluten/Windows-Pfade, `..`, Backslash, NUL oder Case-Aliasse.
- ZIP und Dateiprüfsummen, erforderliche/unerwartete Dateien und Bildstruktur prüfen.
  PNG-CRC sowie IDAT-Inflate in 64-KiB-Ausgaben begrenzen; JPEG-Marker/Dimensionen
  prüfen. Der Android-Core braucht kein Pillow/natives Zusatzmodul. **Vollständiges
  JPEG-/PNG-Decoding erfolgt zusätzlich mit Pillow beim Paketbau/Katalogcheck.**
  Strukturelle Runtime-Prüfung ersetzt weder diesen Decodercheck noch Kodi-Rendering.
- PNG-Nebenmetadaten insgesamt höchstens 1 MiB, einschließlich begrenzt entpackter
  iCCP-/zTXt-/iTXt-Inhalte. Ein kleiner ZIP-/PNG-Input darf auch über Farbprofile
  oder komprimierten Text keinen unbeschränkten Decoder-Speicher anfordern.
- Mindestens 32 MiB freien Speicher für übrige Profilschreibvorgänge lassen;
  512 MiB Gesamtbudget für gültige Theme-Bilder und maximal 32 Revisionen.
  Keine automatische Löschung vorhandener Cover oder Metadaten zur Platzgewinnung.

Lokale/USB-/SMB-Dateien werden per Kodi-VFS in begrenzten 64-KiB-Stücken privat
kopiert. GitHub-Downloads: HTTPS, nur der festgelegte GS-Media-Repositorypfad auf
raw.githubusercontent.com, keine Redirects oder transparente GZIP-Dekompression,
Größenlimit, SHA-256 und Katalogidentität vor Installation. Netzwerk-Reads nutzen
`read1` und 10-s-Timeout; Gesamtbudget 120 s, Abbruch/Deadline zwischen Reads.
Der native Fortschrittsdialog bleibt bedienbar; Abbruch wartet nicht auf Netzwerk-I/O.
Der Worker beendet Rest-I/O spätestens mit dessen Timeout und prüft vor Commit erneut.

Die Katalog-Prüfsumme schützt Integrität und Zuordnung. Sie ist keine unabhängige
digitale Signatur gegen ein kompromittiertes GitHub-Repository; Vertrauen gilt den
Reviewern des freigegebenen Main-Katalogs. Lokaler Import erfordert eine bewusste
Dateiauswahl, führt aber ebenso keine Theme-Skripte aus.

## Transaktion, Aktivierung und Fallback

Speicherung ausschließlich unter dem privaten XCMate-Profil `themes_v1/`:
`packages/<id>/<version>-<ZIP-SHA256>/` und atomare `selection.json`.
Temporär `.import-`, `.download-` oder `.install-`; nach Fehler/Abbruch bereinigt.
Vor Veröffentlichung einer Revision müssen alle Dateien stimmen. Ein bestehendes
Theme wird niemals vor der Prüfung überschrieben; alte Revisionen bleiben bestehen,
damit laufende native Controls weiterhin gültige Bildpfade halten.

Profile-Schreiblock für Commit/Aktivierung; atomarer Rename im selben Dateisystem.
Android/Linux-flock ist unterstützt, Windows ist nicht als Geräteplattform geprüft.
Gleiche ZIP erneut ist idempotent, andere Bytes bei gleicher Version werden abgewiesen;
Downgrades ersetzen neuere installierte Versionen nicht. Erfolgreiches Update der
aktiven Theme-ID wechselt atomar oder wird bei Wiedergabe vorgemerkt.

Bei laufendem Video **oder Audio** wird Aktivieren/Standarddesign nur vorgemerkt.
Die nächste nach Wiedergabeende geöffnete XCMate-Ansicht übernimmt die Auswahl.
Bereits offene Controls werden nicht umgebaut. Entfernen benötigt Bestätigung und
wird während Wiedergabe mit verständlichem Hinweis abgewiesen. Keine Play-/Stop-
Aufrufe, globalen Kodi-Einstellungen oder globalen Keymaps. Bestehende Datenbanken,
Accounts, Favoriten, Resume, EPG-Quellen/-Zuordnungen werden nicht geschrieben.

Fehlende/ungültige Auswahl, inkompatibles oder beschädigtes Theme: neue Ansicht nutzt
das funktionierende Core-Design. Beim Wiederöffnen Hashprüfung geänderter Dateien;
unveränderte lokale Revisionen nutzen einen Stat-/Hashcache. Mediensichten halten
einen lokalen Snapshot, damit Navigation nicht 98 Dateien pro Kachel erneut prüft.
Öffnen ohne optionales Theme ist read-only und erzeugt keinen Theme-Ordner.
Eine bereits sichtbare Ansicht wird bei externer Beschädigung nicht live neu aufgebaut.

## Aktuelle Layoutanbindung und ehrliche Grenzen

| Bereich | Stand |
|---|---|
| Einstellungen → Darstellung & Sprache → XCMate-Designs | Installer/Import/Katalog/Aktivierung/Standard/Entfernen implementiert |
| Hauptmenü | Logische Iconpfade und Home-Fanart; vorhandene Kodi-Verzeichnisansicht bleibt |
| Film-/Serienfenster | Palette, Fokus, Hintergründe, Posterfallback; Provider-Art bleibt dynamisch |
| EPG-Fenster | Palette, Fokus, Hintergrund; Control-IDs/Geometrie/Pfeilnavigation gleich |
| Live-TV/Gruppe/Sender/Infobar/untere Bedienleiste | **Unverändert**, komplette grafische Anbindung bis Originale/Abnahme offen |
| Spezifische Settings-Hintergründe/alle 98 Nutzungspositionen | Mapping anhand des unzugänglichen Mastertrackers noch offen |
| Reale Kodi-Previews aller zehn Ansichten | **Nicht erstellt**, Originale und Kodi-Renderer hier fehlen |
| Android 21.3 / ARM32 | API-Argumenttests vorhanden; tatsächliches Rendering/Fokus/Leistung **NOT_RUN** |

Die gefreezten Dateien einschließlich `live_overlay.py`, Keymap-/Remote-/Playerpfaden
bleiben unverändert. Kein grafischer Komplettumbau als angeblich funktionierendes
Theme ausgegeben. Die vorhandenen Freeze-Fixtures werden nicht neu festgeschrieben.

## Bau und Katalogpflege nach Übergabe der Originale

1. Originale schreibgeschützt archivieren; Mastertracker, Herkunft und vorhandene
   SHA-256 abgleichen. Im Staging nur **bytegleich kopieren**, nichts skalieren.
2. Finale `theme.json` mit allen 98 Pfaden/Schlüsseln/Hashes und freigegebenen Tokens
   erstellen; README/Lizenz und SHA256SUMS beilegen. Maße/Alpha aus Master übernehmen.
3. `python -B tools/build_xcmate_theme.py --source <staging> --output <neuer-Pfad>/XCMate-Space-Premium-1.0.0.zip`
   decodiert jedes Bild vollständig, vergleicht alle deklarierte Hashes/Properties,
   baut reproduzierbar und schreibt ZIP-SHA256 plus `.validation.json`. Vorhandene
   Ausgabe wird nicht überschrieben. Aktuell fehlt das echte Staging, daher kein Bau.
4. Nach erfolgreicher visueller/technischer Prüfung ZIP, `.zip.sha256` und bytegleiches
   Manifest unter `themes/xcmate/space-premium/` zur PR-Prüfung ablegen. Im
   `catalog-v1.json` explizit approved=true, id/name/version, supported_xcmate,
   HTTPS-URL, ZIP-SHA256 und tatsächliche Bytes eintragen. Keine Platzhalter-URL.
5. `python -B tools/validate_xcmate_catalog.py` prüft offline alle freigegebenen
   Einträge einschließlich vollständigem Decoding. Eigener PR-Workflow ist read-only
   und veröffentlicht nichts. **0 freigegebene Pakete ist nicht 98/98 Assets.**
6. Erst nach Freigabe zusammenführen. Runtime-Katalog zeigt auf den produktiven
   Main-Pfad; solange er dort noch fehlt, zeigt die Entwicklungs-ZIP beim Abruf
   einen Downloadhinweis. Der leere Katalog in diesem Branch ist kein Live-Angebot.

Theme 1.0.0 benötigt Core ≥0.1.30 und <0.2.0. Core 0.1.29.2 besitzt den Installer
noch nicht und wird nicht nachträglich unter gleicher Versionsnummer verändert.
