# XCMate 0.1.29.69 – Ursachen und Implementierung

Basis: main cf62f5d554634acca5c2676c6af3d524747f8f40 (.68, PR #314). Master #315, Befunde #313 und #307. Draft #316; kein Merge, kein produktives Release. PR #312 bleibt unabhängig.

## Gesicherter Android-Befund und Grenzen

Die in #315 dokumentierte Hauptdatei enthält 14.599 Zeilen, 15:15:13–15:40:46. Ihr früher 2.565-Zeilen-Ausschnitt und das doppelte 169-Zeilen-Altstartprotokoll zählen nicht zusätzlich. Die privaten Dateien wurden für diesen PR weder heruntergeladen noch veröffentlicht. Zählwerte sind Logzeilen, keine unabhängigen Fehler: 1.547 QUEUED, 1.519 RUNNING, 1.515 PROGRAMME_DB_UNAVAILABLE; 667 Ereigniskennungen, 662 betroffen, 283 mehrfach, eines 18-mal. Es gibt damit keinen belegten Bild-Render-PASS der .68.

Der eigene TMDB-Zugang war auf Box B bereits TMDB_OK. Kein erneuter Tokenimport verlangt. Tatsächliche freie Bytes, WAL/SHM und Seitenbelegung auf Box B sind hier nicht messbar und bleiben NOT_TESTED. Speicherknappheit wird weder behauptet noch durch Abschalten der Reserve umgangen.

## A: Metadaten-Schreibfehler lösten Bildsuche erneut aus

import_budget erzeugte errno=28 bereits unter 32 MiB Reserve plus 65.536 Byte geplantem Bedarf. Die alte Zuordnung DISK_FULL unterschied diesen Schutz nicht von echtem ENOSPC. Der .68-Worker erzwang lokale Materialisierung; bei fehlgeschlagener Persistenz wurde ein gefundenes Bild als PROGRAMME_DB_UNAVAILABLE/Platzhalter zurückgegeben. Die Queue gab dieselbe Identität nach Jobende erneut frei.

Neu: ReserveBlocked trägt SAFE_RESERVE_BLOCKED und die numerischen Messwerte. programme_writes69 unterscheidet REAL_ENOSPC, SQLITE_FULL_POLICY, SQLITE_FULL_STORAGE/UNKNOWN, SQLITE_BUSY_LOCKED, SQLITE_IO und Leseunterbrechung EPG_READ_TIMEOUT. SQLite-FULL ohne ausreichende Belege bleibt UNKNOWN. Read-only Diagnose zeigt DB/WAL/SHM, Seiten, Freelist, Reserve, Bilderbudget und Circuit-Zustand. Die Grenze 32768 Seiten und Sicherheitsreserven bleiben bestehen.

Ein nach Datei/Profil isolierter Circuit begrenzt Schreibversuche (Kapazität: 30/120/300/900 Sekunden, maximal 900); zurückgestellte Versuche verlängern die Sperre nicht. Eine gemessene Kapazitätsverbesserung kann die Sperre kontrolliert öffnen. Keine Datenbankmigration oder Bereinigung.

programme_session69 trennt validiertes Bild/negatives Suchergebnis von dessen Persistenz. Maximal 128 nachpersistierbare Ereignisse und 1024/4 MiB kompakte Ergebnisse im RAM, exakt nach Profil, Portal, Ereignis und vollständiger Richtlinienrevision. 667 Ereignisse verdrängen nicht bereits das erste Ergebnis. Flüchtige Resultate heißen RAM_ONLY und tragen den tatsächlichen Speicherfehler. Bei Recovery höchstens vier Metadatenresultate je Durchlauf in einer Transaktion nachpersistieren; kein erneuter API-Aufruf dafür. Negative Suchresultate und transiente Fehler haben unterschiedliche, begrenzte Wiederholungsfristen. Ein Prozessneustart verliert den ausdrücklich flüchtigen RAM; vorhandene persistente Daten bleiben erhalten.

## B: URL-only statt zwingendem Bildarchiv

Produktions-Queue und Prefetch benutzen standardmäßig den geprüften HTTPS-Modus. Die optionale Einstellung für zusätzliches lokales Sendungsbildarchiv bleibt verfügbar. Vorhandene lokale Dateien werden weiter verwendet und niemals gelöscht.

Nur der bestehende Resolver liefert Bildquellen: konkrete XMLTV/Provider-Ereignisse, eigener TMDB-Zugang, lokale passende Katalogdaten, TVmaze (sofern eingeschaltet), Helper-Fallback. Nachrichten/Sport/Sendepause lösen keine ungeeignete TMDB-/Helper-Suche aus. Konservatives Titel/Jahr/Staffel/Folgen-Matching bleibt erhalten.

URL-Ausgabe verlangt erlaubten Host, credentialloses HTTPS, keine Query-/Pipe-Injektion, geprüfte Bildheader und Dimensionen, Ablaufzeit, Profil und exakte Ereignis-/Quellenrevision. Redirects im Kodi-Texturabruf bleiben ausgeschaltet. GUI-Code liest nur RAM/Properties, führt weder Netzwerk noch SQLite aus. Gemeinsame Bildprüfung für Guide-/Mini-Vorschau, beide Detailpfade und BINGIE-Hero; fehlende Bilder werden ausgeblendet. Private Provider-Zugangslinks gelangen nicht als ungeprüfte Referenzen in Properties.

Der Native-Test verwendet eine ausschließlich im wegwerfbaren Linux-Container erzeugte CA und synthetische image.tmdb.org-Zuordnung. TLS/SNI/Zertifikatsprüfung, Bild-Preflight und Kodi-Curl bleiben aktiv. Synthetische eigene-Token-API-Antworten sind kein Test des privaten echten Tokens. Echte Live-API-Suche sowie Android-Pixel und Fernbedienung: NOT_TESTED.

## C: Home früher nutzbar

Ein kleiner separater Worker veröffentlicht lokale Film-/Serienkataloge und bereits öffentliche Provider-Bildreferenzen vor dem schweren Warmup. Provider-Referenzen hängen dabei nicht mehr an einer schreibbaren programme_v1.sqlite. Bestehender interner/externer Artwork-Modus und gespeicherte Bilder bleiben unverändert.

Provider-HTTPS-Referenzen werden im Hintergrund auf öffentliche Adressen geprüft, kurz nach Profil/Portal/Zugang/Quelle freigegeben und anschließend von Kodi geladen. Generische Poster werden auf BINGIE Home nicht gerendert; Einträge ohne renderbare Posterreferenz werden dort vorübergehend zurückgehalten statt als leere Kachel ausgegeben. Ihre Titel bleiben im lokalen Katalog und den normalen Medienansichten verfügbar. Das ist keine Zusage sofort sichtbarer Poster auf einer unerreichbaren Quelle.

Erneute schwere Warmups frühestens 30 Sekunden nach Abschluss statt fünf Sekunden ab Start. Bereits laufende lange Warmups lösen daher nicht sofort den nächsten Vollzyklus aus. Widgetveröffentlichung nur bei geänderten Daten/Richtlinien/Referenzen; keine Verzeichnisneuladung pro IR-Fokus. Startgruppe und vorhandene Widget-Routen bleiben unverändert; Tests decken 0/1/5/17/88/120/256 und aktivierte Gruppen ab.

## D: Stop war fertig, Rückkehr blieb geschützt hängen

Das Android-Log erreicht PLAYER_STOP_DONE und STOP_DONE. Der Fehler liegt anschließend bei DIRECTORY/MODAL-Guards; dies beweist keinen Decoder-Deadlock. Native Stop-/Decoder-/Autoplay-Implementierung bleibt erhalten.

live_return69 beobachtet nach positiv bestätigtem nativen Stop die echte Sichtbarkeit/Nutzbarkeit des Ziel-Home. Maximal zwei eigene Rückkehranfragen und acht Sekunden Beobachtungsfrist; Ergebnis HOME_REQUESTED → HOME_VISIBLE → COMPLETE oder FAILED mit festem Grund. Aktive/fremde Wiedergabe und neue Sitzung brechen den alten Rückkehrversuch ab. Eine fremde Modalebene wird weder geschlossen noch übergangen.

Eigene Guide-/Detailfenster registrieren Profil, Portal, native ID und Owner. Nur bei genau passender aktueller Identität wird ein kooperatives Schließsignal an die Owner-Pumpe geschickt. Kein globales Dialog.Close, kein Keymap-/Skin-Patch. Detail-Initialisierungsfehler und fünf Sekunden überschreitende Datenlesejobs werden abgefangen; Back bleibt bedienbar. Ein acht Sekunden bestehender fremder Dialog wird als FAILED/FOREIGN_MODAL_RETAINED dokumentiert, nicht als erfolgreicher Home-Return.

## Bestandsschutz und offene Geräteprüfung

Alle 670 bisherigen Quelldateien bleiben erhalten; Änderungen werden als exakte .69-Deltas auditiert. Alle 2805 bisherigen Testmethoden und vorhandenen Skip-Bedingungen werden geschützt. Ein alter Test erwartet jetzt ausdrücklich eine leere Hero-Texturreferenz statt neutral.png, entsprechend dem neuen Platzhalterverbot; die Assertions für EPG-Text, unveränderte öffentliche ProgrammeImage-API und Netzwerkfreiheit bleiben.

Keine Datenlöschung, kein Reindex, kein Profilreset, keine Passwort-/Tokenänderung. AAC-/Add-on-Manager-Startfehler und Drittanbieter-Repository-/Helper-404 sind separate Befunde, keine ungeprüften Fremdpatches. Box A und installierte BINGIE-Dateien werden nicht verändert.
