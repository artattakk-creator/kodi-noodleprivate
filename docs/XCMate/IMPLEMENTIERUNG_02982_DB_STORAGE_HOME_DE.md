# XCMate 0.1.29.82 – Ursachen, Umsetzung und Prüfgrenzen

Basis: `7e5a1cf588b7c1043a1849e5c48e77358812b1ef` (veröffentlichte .81).
Auftrag: #395; historische Befunde #392/#389. Keine Änderung der veröffentlichten
.81-Pakete, Repository-Indizes, Installer 0.5.26 oder Benutzerkonfigurationen.
Das .82-ZIP liegt ausschließlich als Review-Build vor. Kein Merge/Release.

## P0-A: Datenbankpause ist ein Jobzustand

Bestätigte Ursache im .81-Code: `widget_assets69._run → render_cache81.prepare →
store → programme_art46.space → art_store.used → artwork_db.connect`.
`ArtworkDBUnavailable` erbt von `sqlite3.OperationalError`, wurde vom Renderpfad
nicht behandelt und beendete den Daemon. Der nächste Poll startete ihn erneut.
Die dokumentierten 443 Ausnahmen gehören zu einer überlappungsbereinigten
.81-Sitzung; die sechs Logdateien werden nicht addiert.

`artwork_health82.py` liest DB-Identität, bestehende Pause und `retry_after`.
Der vorhandene Worker in `widget_assets69.py` hält maximal 16 wartende Jobs,
dedupliziert unverändert und respektiert die Pause. SQLite-/Storagefehler
erhalten begrenzten Backoff. Vorhandene Kodi-Texturen und zulässige Referenzen
werden vor optionalen neuen Bilddateien bereitgestellt. Es entsteht kein zweiter
Worker. Nach Ablauf/Freigabe wird derselbe Job kontrolliert fortgesetzt.
Unerwartete Programmfehler und MemoryError verriegeln den Worker mit FATAL;
sie werden weder als Erfolg noch als Anlass für ständiges Respawning behandelt.
Status enthält ausschließlich Codes, anonyme DB-Korrelation, Pausezeit und Zähler.

Ein Budget von `0` bedeutet **kein zusätzliches Archivlimit**. In diesem Fall
fragt `programme_art46.space` nicht mehr unnötig den gesamten Artworkbestand
über SQLite ab. Eine ausdrücklich konfigurierte Begrenzung bleibt wirksam.
`render_cache81` behandelt SQLitefehler kontrolliert und prüft Schreibfreigaben.
Automatische Service-Wartung verwendet eine nachgelagerte read-only Schema-
prüfung statt ungefragter Reindexierung/Sicherung/Reparatur. Der manuelle
Wartungsweg wird nicht ersetzt.

## P0-B: dieselbe Speicherklasse messen, Reserven beibehalten

Dokumentierter Androidbefund: 147 Reserveblocks, 53.825.536–58.871.808 freie
Bytes gegenüber 1.073.741.824 Bytes Reserve. Das beweist eine Schutzblockade,
aber nicht den physischen Android-Mount oder einen defekten TMDB-Aufruf.

`art_storage82.py` löst das tatsächlich ausgewählte lokale Ziel und den nächsten
existierenden Elternpfad auf. `shutil.disk_usage` und `statvfs.f_bavail` werden
am selben Ort mit Geräteidentität und Mountklasse verglichen. Bei Abweichung
gilt der kleinere verfügbare Wert; unbekannte/offline Ziele werden nicht
freigegeben. Die bestehende adaptive Policy wird nur bei SAME_VOLUME_VERIFIED
verwendet. Die feste Reserve bestehender Profile bleibt erhalten.

Die bestehende Artwork-Statusansicht enthält PROFILE_PROGRAMME,
PROFILE_METADATA, KODI_TEXTURES und gegebenenfalls SELECTED_ARCHIVE mit
Free/Total, anonymem Volume, Backend, Reservepolicy und Diagnosecode.
Ein zusätzlich ausdrücklich bestätigter Schreibtest darf ausschließlich eine
neue 4-KiB-Datei in einem der drei eigenen Cacheordner anlegen, rücklesen und
diese eigene Datei entfernen. Unbekannte oder widersprüchliche Kapazität
verweigert auch diese optionale Probe. Er respektiert die bestehende 32-MiB-Reserve für
Import-/Diagnosemetadaten; dies ist keine Freigabe neuer Bildarchive unterhalb
deren Bildreserve. Kein Benutzerfile wird gelöscht, kein Ziel automatisch
verschoben und kein größeres, unbewiesenes emuliertes Volume angenommen.

**Offen / ANDROID_NOT_TESTED:** Der tatsächliche Mount auf der Box und die
Ursache seiner Abweichung zu anderen Android-Speicheranzeigen müssen anhand
dieser neuen Receipts geprüft werden. Eine reale Hardware-Speicherblockade
wird nicht als behoben ausgegeben. Ein optionaler Speicherumzug gehört nicht
zu diesem Patch.

## P0-C: vorhandene Pixel unabhängig von einer neuen Archivkopie

`widget_cache82.py` gewinnt bereits bestehende Kodi-Texturen in 16er-Batches
über Textures.GetTextures zurück: exakte öffentliche Quellreferenz, erlaubter
Thumbnailpfad, vollständiges Bilddecode, SHA256 und unveränderter Dateistempel.
Keine Kodi-Datenbank wird beschrieben und kein Bild kopiert oder gelöscht.
Kleine Receipts verwenden den vorhandenen .79-Metadatenjournalpfad. Bei dessen
Speicherblock bleibt die geprüfte RAM-Referenz nutzbar, ohne DISK_PERSISTED zu
behaupten. Ein unverändertes geprüftes lokales Bild verfällt nicht nach einer
willkürlichen 30-Tage-Frist. Window-Properties verwenden den vollständigen
Content-Key; der frühere Modulo-512-Slot konnte bei großen Reihen kollidieren.

`home_lkg82.py` ergänzt die vorhandene atomare Frame-Publikation: Bei identischer
Quellrevision darf eine fehlende optionale Provider-Artantwort eine bestätigte
lokale Referenz derselben Rolle, Edition und Scope weiterverwenden. Ein echter
Provider-, Gruppen-, Account-, Titel-/Jahr- oder Revisionswechsel berechtigt
keine Übernahme eines fremden Bildes. Remote-DNS-Leases werden nicht verlängert.
Reine interne Proof-Metadaten lösen keine visuelle Vollaktualisierung aus.

## P0-D: Cache-Publikation vor Hintergrund-Warmup

`widget_fast69.prepare` veröffentlicht vorhandene Film-/Seriendatensätze auch,
wenn neue Netzwerkjobs für diese Phase noch nicht zugelassen sind. Die
Ladepriorität lokales EPG/Logos/Live-Hero vor neuen Film- und Serienjobs bleibt
erhalten; vorhandene Cover warten nicht auf den Vollscan.
`home_metrics82.py` trennt CACHED_ITEMS_READY, LISTITEM_PUBLISHED,
SKIN_CONTROL_ACTIVE, IMAGE_DECODE_REQUESTED und IMAGE_PENDING.
`android_render_verified` bleibt ausdrücklich false.

Die .81-Zeiten 114.611 / 1.230.977 / 1.523.127 ms bezeichnen interne Ready-
Stages, keine gemessenen Androidpixel. Ein belastbarer Vorher-/Nachhervergleich
erfordert die Geräteabnahme und wird nicht aus Host-Laufzeiten abgeleitet.

## Erhaltene P1- und Regressionsbereiche

Eigene TMDB-Implementierung und Token-/Optoutschutz bleiben erhalten. Die
historisch dokumentierten 126 HTTP-200 und 19 Exact-Matches widerlegen eine
generell deaktivierte TMDB-Anbindung. Kein externer Helper wird Voraussetzung.
Providerposter, TMDB-Backdrops, XMLTV- und TVMaze-Quellen bleiben getrennt.
Die bestehenden positiven/negativen Titel-, Alias- und Jahresprüfungen bleiben.

Full-bleed-Hero, proportionaler Posterfallback, transparentes Informations-
overlay, kompakte Film-/Serienreihen und stiller Katalogimport aus .81 werden
kumulativ übernommen. Player-/Exit-/Autoplaycode, Keymaps, SkinShortcuts,
Space Blue, Portale, EPG-Mappings und Installer sind nicht Gegenstand einer
Migration. Kodi-native fehlende Videoviews werden nicht neu aufgebaut.

## Prüfnachweise

Siehe `TESTBERICHT_02982_DE.md` für tatsächliche Resultate und CI-Links sowie
`ANDROID_ABNAHME_02982_DE.md` für die getrennte Geräteprüfung.
Host-, Linux-Kodi- und virtuelle Zeitprüfungen sind keine Androidabnahme.
