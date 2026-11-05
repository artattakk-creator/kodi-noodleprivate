# XCMate .74 – Ursachen und technische Grenzen (#361)

Kumulative Basis: `2e9e81c696c65b6dfdf0293efca9ed5b51c7bab8`, XCMate .73 plus bereits separat freigegebene Installer-0.5.21-Veröffentlichung. Keine Änderung an regulären/Pilot-Katalogen oder Boxen durch diesen Branch.

## Bestätigte Codeursachen

- **Titel verschwinden ohne Datenbanklöschung:** `widget_render47` und `widget_refresh45.read` filterten ganze Film-/Serienzeilen, wenn ein Poster augenblicklich nicht renderbar war. Volatile Bildfreigaben liefen nach maximal 30 Sekunden ab. .74 erhält die Datenzeile und trennt Bildstatus von Kataloginhalt.
- **Zu breite Cacheinvalidierung:** Live-Policy enthielt DB-/WAL-Dateizeitstempel. Auch fremde Katalogschreibvorgänge invalidierten den vorherigen Live-Snapshot. .74 bindet die Policy an Profil/Account/Auswahl; die überprüfte Katalogrevision ist ein separates Merkmal. Ein während des Reads wechselnder Katalog wird nicht als kohärente neue Generation gespeichert.
- **Mehrere Writer/Reader:** Zwei wiederverwendete Seitenslots konnten einen noch laufenden alten Reader nach zwei Publikationen überholen. .74 schreibt unveränderliche, hashadressierte Metadatenseiten und wechselt erst dann das Manifest. Eine nicht blockierende Publikationssperre koordiniert Interpreter. Nur eigene obsolete Publikationsmetadaten nach zwei Stunden werden bereinigt; keine Bilder, Nutzerdaten oder Datenbanken.
- **EPG-Handoff:** Die fixe 300-Sekunden-Frischefrist konnte noch laufende lokale Sendungen aus der Anzeige entfernen. .74 prüft Profil, Sender, Mapping, Guide-/Konfigurationsrevision und reale Start-/Endzeit. Ab 300 Sekunden wird ein begrenzter, deduplizierter lokaler Hintergrundrefresh angefordert. Der endliche Metadatenhorizont beträgt sechs Stunden; abgelaufene Sendungen werden nicht als JETZT konserviert. Warme Display-Lookups verwenden den identischen Handoff ohne erneute SQL-Abfrage. Worker stoppen kontrolliert beim Service-Shutdown.
- **Sendungsbilder:** Ein vorhandener Token aktiviert keine Suche. Beide bestehenden TMDB-Opt-ins bleiben notwendig; der direkte TMDB-Fallback prüfte vorher nur eines davon. TVmaze bleibt optional und strikt identitätsgeprüft, nun auch anhand expliziter Staffel-/Episodendaten ohne Genre. Unsichere Live-/Sport-/Nachrichten-/Talk-Titel werden vor externer Filmsuche ausgesondert. Helperfehler erhalten exponentiellen Backoff; ein identitätsgleicher gültiger Bildnachweis geht bei temporärem negativem Auftrag nicht verloren. Fokusidentität umfasst Quelle/Revision/Profil. Der neue explizite Diagnosedialog prüft Verbindung und aktiven Eventbildabruf.
- **Guide-Layout:** Die 96×54-Vorschau wurde durch 320×180 unterhalb des achtzeiligen Rasters ersetzt. Rasterzeilen sind dafür 42 statt 56 Kodi-Logikpixel hoch. Remote-Reihenanzahl bleibt acht; Status/Fußzeile haben eine eigene Breite.
- **Standardpicker:** Die drei bestehenden nativen Quellen waren vorhanden, der normale Menüweg und der `handle<0`-Fallback führten jedoch in den separaten Slotmanager. .74 führt normale Auswahl und alte `widget_setup`-Bookmarks zu den drei unveränderten Quellen. Der alte technische Dialog bleibt separat unter Experimentell erreichbar. Keine automatische Skinshortcuts-Neuanlage oder Bindingänderung.

## Fokusadapter und Bestandsschutz

Der .66-Adapter ersetzte native vertikale Navigationsregeln durch einen Containerindex und kombinierte lokale mit globalen Rahmen. .74 stellt die nativen Regeln wieder her, bindet Rahmen an Ursprung/Größe des tatsächlich fokussierten Itemlayouts und unterdrückt konkurrierende globale Home-Rahmen für diese Layouts. Native Highlight-/Hub-Pfade bleiben erhalten.

Das ist **kein Beweis des exakten installierten Android-Skinstands**. Es gibt keinen direkten Zugriff auf dessen XML/Pixel. Der optionale Adapter akzeptiert nur die geprüften SHA-Stände des offiziellen BINGIE 2.2.3 beziehungsweise des exakten .66-Kandidaten, läuft über den vorhandenen Vorschau-/Backup-/Bestätigungs-/Restore-Mechanismus und lehnt unbekannte Anpassungen ab. Die Installation selbst schreibt keine Skin-XML und keine BINGIE-Bindings.

Bilder: Nur exakt dieselbe zuvor DNS-geprüfte öffentliche Providerreferenz erhält eine begrenzte 300-Sekunden-Überbrückung nach der kurzen positiven Lease. Bestätigt unsicheres DNS widerruft sofort. Account/Profil/SID/Rolle/Quelle müssen stimmen. Eine lokale Vorgängergrafik wird nur bei gleicher Quellenidentität übernommen. Echte Katalogrevisionen können Titel entfernen, einschließlich eines nachgewiesenen leeren Ergebnisses; unbekannt leer/Timeout ist kein Löschbeweis.

## Messung und Grenzen

Kontrollierter Linux-Hostvergleich mit identischen synthetischen lokalen Daten, 88 Sendern und 30 warmen 16-Sender-Abfragen:

| Messung | .73 | .74 |
|---|---:|---:|
| Erster lokaler Lookup, ms | 13,103 | 8,281 |
| Warm p50, ms | 6,576 | 0,985 |
| Warm p95, ms | 41,541 | 10,369 |
| SQLite-Verbindungen je warmem Aufruf | 2 | 0 |
| Atomare Metadatenwrites bei 30 identischen Publikationsaufrufen | 211 | 8 |

Kein kontrolliert kalter OS-Cache, keine ARM32-/Android-Latenzbehauptung. Rohwerte und reproduzierbarer Treiber liegen beim Testpaket.

Hosttests prüfen auch echte SQLite-Sperren, unveränderte Profil-/Kanaldaten, alte kumulative Verträge und sichere URLs. Native Tests verwenden echte Kodi-/BINGIE-Controls und Bilddecoder mit synthetischen Daten. Die isolierte HTTPS-Origin nutzt eine eigene Test-CA, SNI und GET/HEAD; ausschließlich ihr lokal aufgelöster Host wird im Test vom verwalteten Proxy ausgenommen. Keine öffentliche API wird dadurch umgangen. Der echte private TMDB-Zugang ist in dieser Arbeitsumgebung nicht verfügbar/extern zugelassen: **NOT_TESTED**.

Keine Reparatur/Löschung von Kodi `MyVideos131.db`. Keine zurückgestellten Download-, Aufnahme-, Wizard- oder Internationalisierungsumbauten. Issues #357–#359 behalten ihre früheren offenen Geräte-/Quellen-/Übersetzungsprüfungen. Alle Android-Gates bleiben **ANDROID_NOT_TESTED**.
