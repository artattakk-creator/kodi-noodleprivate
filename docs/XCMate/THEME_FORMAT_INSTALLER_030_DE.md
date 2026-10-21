# XCMate Themes – Paketformat 1 und Installer 0.1.30

Stand **21.10.2026**, bestehender Draft-PR #50. Originale **98/98 vorhanden**, ein freigegebener Katalogeintrag im Entwicklungsbranch, **main-Katalog und Theme-ZIP derzeit HTTP 404**. GitHub ist die einzige offizielle Online-Quelle; Drive ist Quellarchiv. Kein Merge/Release/Index-Update. [Aktueller vollständiger Prüfbericht](PR50_PRUEFBERICHT_030_20261021_DE.md), [Pakete/Backup](INSTALLATION_0292_UND_THEME_030_DE.md).

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
| id/name/version/author | Eigene stabile ID, Anzeigename, semantische Version, Autor; Beispiel Space Premium 1.0.0 |
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
und `focus.default` Pflichtschlüssel. Weitere Aliasse sind erlaubt. Der Nutzer bestätigt den früheren Tracker-Abgleich; alle 98 Originale sind nun vorhanden und in dieser Runde gegen Manifest/ZIP/GitHub-Bytes geprüft.

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

## Aktuelle Renderer-Anbindung und Grenzen

[98-Dateien-/106-Key-Matrix](SPACE_PREMIUM_RENDERER_MATRIX_030.json): 86 Originaldateien an echte Verbraucher oder bedingte Fallbacks angebunden, 12 ohne Verbraucher. Unter anderem Livegruppen/-sender, Infobar/Controls/Extras, EPG, Mediaaktionen und Widgets mit Originaltexturen. Stock-Eingaben, Control-IDs, fokussierbare Geometrie und Navigationsziele bleiben gleich; nur lokale Themeauflösung/Texturepfade und nicht fokussierbare Dekorationen ergänzt. Keine Netzwerkzugriffe beim Navigieren. Freeze-Referenzdateien unverändert; enge AST-Normalisierung der Texturehooks und nativer Stock-/Theme-Vergleich bestanden.

Zwölf Reservebilder und deren fehlende Verbraucher stehen im Prüfbericht; weder Aufnahme/Skip noch neue Startup-/Ladescreens werden erfunden. Reale Kodi-Previews, IR, BINGIE, RAM/Skalierung und Android-Renderer **NOT_RUN**. Paketvollständigkeit bedeutet keine vollständige visuelle Abnahme.

## Erweiterbarer GitHub-Katalog und künftiger Updateweg

1. Neue Themes erhalten eine eigene `id`, `name`, `version`, `supported_xcmate`; keine Core-Auswahländerung für weitere IDs nötig. Der generische Hostbuilder akzeptiert weitere Themes; zwei unterschiedliche temporäre Fixtures belegen den kompletten Import-/Aktivierungs-/Updateweg. Keine öffentlich freigegebenen Testthemes oder neue Originalkunst erzeugt.
2. Autorisierte Originale inklusive Herkunft/Lizenz unverändert archivieren. Eigenes Staging mit `theme.json`, `SHA256SUMS.txt`, `README.md`, `LICENSE.txt` und manifestierten Bildern vorbereiten. Allgemeine Pflichtkeys erfüllen; nur `space-premium` verlangt genau 98 verschiedene Bilder. Keine ausführbaren Themes.
3. `python -B tools/build_xcmate_theme.py --source <staging> --output <neuer-Pfad>/<Theme>-<Version>.zip` decodiert vollständig und erzeugt reproduzierbares ZIP, SHA-Datei und Validierungsbericht; bestehendes Ausgabeziel wird nicht überschrieben. Weitere Versionen vorzugsweise unter `themes/xcmate/<id>/<version>/` ablegen; vorhandenes Space-Premium-1.0.0-Layout bleibt gültig.
4. ZIP + `.zip.sha256` + Manifest + Nachweise und **generischen Katalogeintrag** als PR vorlegen: `id/name/version/supported_xcmate/url/sha256/bytes/approved`. Nur allowlisted HTTPS-URL unter diesem GitHub-Repository/main, kein Drive/Redirect/Fremdhost. `approved=true` im Reviewbranch macht nichts vorzeitig auf main verfügbar.
5. `python -B tools/validate_xcmate_catalog.py` prüft alle freigegebenen Pakete offline einschließlich vollständigem Decoding. Draft-Builder erzeugt Artefakte read-only, ohne automatischen Commit. Eine existierende Themeversion muss beim Neubau bytegleich bleiben. **Niemals andere Bytes unter 1.0.0 ersetzen**; Änderungen brauchen neue Version und Review.
6. Nach Review und **ausdrücklicher Benutzerfreigabe**, nicht durch diesen Auftrag, folgt Merge. Erst dann müssen main-Katalog **und exakt referenziertes ZIP** am Android-Gerät HTTP 200 liefern. Bytes/SHA/Kompatibilität unabhängig vergleichen, Katalogauswahl/Download/Import/Aktivierung/Offline-Restart real abnehmen. Bis dahin zeigt 0.1.30 unter „Online-Katalog“ einen verständlichen 404-Hinweis. Lokaler ZIP-Import ist jetzt testbar.
7. Theme-Onlineverfügbarkeit und reguläre Core-Repositoryveröffentlichung sind getrennt. Ein späterer Core-Publish benötigt zusätzlich expliziten Owner-`workflow_dispatch` auf main mit `publish_repository=true` (Default false); kein Publish durch PR oder Main-Push. **Hier nicht ausgelöst.** Vorher Kodi-Profil konsistent sichern, Android-Gates und #40 prüfen. Benutzer entscheidet weiterhin über Merge und Release.

Space Premium 1.0.0 ist unveränderlich: **19.772.084 Bytes**, SHA-256 `8fc7f312a65fa5ecdbe68d3487939a25d685de29717896a0a1113c8d41176ae2`, Core **>=0.1.30,<0.2.0**. Core 0.1.29.2 hat keinen Themeinstaller und wird nicht unter gleicher Version ersetzt. Der freigegebene Core-Icon bleibt unabhängig vom Theme permanent enthalten.
