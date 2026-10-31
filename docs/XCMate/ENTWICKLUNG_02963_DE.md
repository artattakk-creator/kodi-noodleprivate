# XCMate 0.1.29.63 – kumulative P0-Entwicklung

Basis: main 7b76bd0fdfe7dcbfdac1d936490d409d719b630c (.62). Master #293, Referenzen #291, #292, #284, #286 und #288 vollständig berücksichtigt. Nutzer-Mockup vom 31.10.2026 ist die Designreferenz. Kein Merge und kein Produktionspublish.

## Nachweisbare Codeursachen

- Die .62-Integration zeigt ein 1008×567-Bild mit keep und separate Textcontrols ab x=1314. Das ist der bestätigten Vollflächenansicht nicht entsprechend. .63 ersetzt ausschließlich das eigene Hero-Include; die akzeptierte LiveRow bleibt byteidentisch. Hintergrund 1920×540 mit scale, oberem/rechtem Bildanker, weichen eigenen RGBA-Verläufen, Textoverlay links und echten EPG-Properties. Keine Demo-Sendetitel im Produkt.
- Live-Home hatte Senderidentität gegen optionale Metadatenfehler abgesichert, aber bei Fehlern des gesamten optionalen Renderers auch seine EPG-Texte verloren. .63 lädt EPG-Texte unabhängig davon und hält Now/Next, Zeiten, Beschreibung und Bildidentität getrennt.
- GuideSnapshot begann pro Overlay leer und benötigte erneut Katalog-/Workerfreigabe. .63 übernimmt validierte lokale Now/Next-Daten schon mit der angekündigten SID. Der GUI-Lesepfad benutzt ausschließlich Kodi-RAM-Properties, keine SQL-/Provider-/TMDB-Abfrage. Der Worker validiert die vorhandene guide_v1.sqlite-Publikation über einen begrenzten Metadaten-Punktlesezugriff. Quellenbindung, Revision, Profil und Ereignisidentität gehören zur Prüfung. Keine zweite EPG-Datei/DB.
- Der .62-Import ließ nur lokale POSIX-Pfade zu; SMB wurde vor dem Formatvalidator abgewiesen. Android-Quell-Mounts und möglicherweise auch der private Profilanker können Symlink-Komponenten enthalten. .63 trennt explizit gewählte VFS-Quellen von der privaten Zieldatei. Nur der autoritative Kodi-Profilanker darf als Android-Mount aufgelöst werden; die privaten Kinder und Datei behalten O_NOFOLLOW. Ausgewählte Quellen werden nie pauschal realpath-resolviert.
- Die eigentliche Tokenvalidierung und bestehende atomare Schreib-/Vergleichslogik bleiben erhalten. Neue private Unterordner werden ausschließlich nach ausdrücklichem Import unter einem bestehenden Profilanker mit Deskriptoren angelegt. Ein Profilwechsel zwischen Bestätigung und Schreiben wird abgewiesen.

## Verhalten und Bestandsschutz

Token-Datei von Kodi-SMB oder Android-USB/Downloads: eng begrenzte Scheme-Auswahl, begrenztes Read/EOF-Budget, Schutz gegen wiederholte blockierte Aufrufe, einmaliges Einlesen, private lokale Kopie. Die native SMB/VFS-Operation kann durch Python nicht zuverlässig abgebrochen werden; die Oberfläche hat ein Zeitbudget, der höchstens eine noch laufende Aufruf bleibt begrenzt. Dies ist getrennt auf Android zu prüfen. Keine globale Änderung von Kodi-SMB-/Netzwerkeinstellungen.

TMDB-Menü: bisherige Position 4 bleibt Zurück, Position 5 separates bestätigtes Deaktivieren. Zusätzliche explizite Aktionen für Import mit Bildaktivierung und maskierte Eingabe. Bloßer Import aktiviert keine Bilder. Eine ungültige vorhandene Privatdatei blockiert weiterhin den stillen Legacy-Fallback und lässt sich geführt ersetzen. Echte HTTPS-Authentifizierung bleibt der vorhandene Verbindungstest; keine synthetische Antwort wird als echte Nutzer-Authentifizierung bezeichnet.

Der Hero veröffentlicht seine Felder in zwei RAM-Bänken und schaltet erst die vollständig vorbereitete Bank um; Sender-/Profilidentität verhindern fremden oder gemischten Text. Bildquelle und Ereignisschlüssel müssen zusammenpassen. Der bestehende lokale Artwork-/Programmcache liefert Bilder, die rotierende bestehende Queue bleibt der einzige Hintergrund-Lookup-Pfad. XMLTV/Provider und verifizierte lokale Bilder vor optionalem Helper/eigenem TMDB. Keine Netzabfrage beim Fokus.

Ein vorhandener, ausdrücklich genehmigter, hashgenau bekannter BINGIE-Adapter erhält eine sichtbare .63-Upgradevorschau und ausdrückliche Bestätigung. Keine automatische Skinmodifikation. Plan, Hashes, Backup, Restore und nativer Rebuild bleiben verbindlich. Unbekannte Skin-Dateien werden abgewiesen. Gespeicherte Widgetquellen, LiveRow, passive Quellenrouten und Film-/Seriencode werden nicht umgeschrieben.

## Prüfstand

Der erste isolierte VFS-Commit 24de09e796b17c72edad4ca2e5b35c8a69a2a357 hatte 2.559 Tests PASS / 526.737 s sowie alle fünf bestehenden nativen Kodi-Prüfungen PASS in CI 41227503154. Das ist KEINE Abnahme des danach entwickelten kumulativen .63-Stands.

Für den vollständigen Stand ist der im PR verlinkte abschließende grüne CI-Lauf am exakten HEAD verbindlich. Neue Tests: sichere VFS-/Datei-/Format-/Abbruchfälle, privater Android-Zielanker, bestehendes Tokenmenü, warme lokale Datenübergabe ohne GUI-IO, Revision und Quellen-/Profilkollisionen, EPG-Text bei optionalem Artworkfehler, vollständige 88-Sender-Snapshots, vollständige Bankpublikation, native Hero-Pixel und reversible Adaptermigration. Alle 2.553 bisherigen Testmethoden/Skip-Bedingungen und alle 624 bisherigen Quelldateien sind gegen den tatsächlichen .62-Baselinebestand geschützt; nur exakt dokumentierte .63-Deltas werden normalisiert.

Die verwaltete Entwicklungsumgebung fiel vor nutzbarem Start mit ERS-Readiness-Timeout aus. Ausführbare Verifikation erfolgt über GitHub Actions. Alle realen Android-/Box-B- sowie privaten TMDB-Verbindungsprüfungen bleiben ANDROID_NOT_TESTED. Keine privaten Dateien oder Kodi-Rohlogs verwendet, kein Gerät verändert, Box A unangetastet.

Paket-SHA256 und genaue Abschlusswerte werden im Abschlusskommentar desselben Draft-PR #294 aus dem erfolgreichen aktuellen CI-Artefakt angegeben. [Testbericht](TESTBERICHT_02963_DE.md) und [Android-Abnahmeplan](ANDROID_ABNAHME_02963_DE.md) trennen Hostbelege und echte Gerätegates.
