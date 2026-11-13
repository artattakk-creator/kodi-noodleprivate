# XCMate .92 – EPG-Retention und temporärer XMLTV-Import: Designvertrag (13.11.2026)

## Nutzervorgabe
XMLTV herunterladen, validieren/parsen, quellenbewusst in die EPG-Datenbank übernehmen, temporäre XMLTV-Rohdaten **nach bestätigter erfolgreicher Veröffentlichung verwerfen**. Kein Langzeitarchiv mit alten XML/GZ oder mehrfach angelegten vollen EPG-Dumps. Regelmäßig alte Programmdaten außerhalb des benötigten Zeitfensters bereinigen. **Datenbank benötigt dennoch dauerhaft Platz** für Sendungstitel, Beschreibungen, Zeitfenster, Quellen, IDs und Indizes.

## Verifizierter Codebefund in .91
- resources/lib/epg.py Zeilen ~558-563: http_get in raw Bytes im RAM; parse_xmltv(raw). Um ~619-621: guide_store.import_cache, daneben _save_disk als normalisierter EPG-Cache und _mem_set; also zusätzliche Disk-Kopie trotz ggf. fehlender Roh-XML-Datei.
- resources/lib/epg_sources.py ~277-300: jede aktivierte externe XMLTV-Quelle _read_source → raw → parse_xmltv → merged. Kein Beleg, dass das eigentliche HTTP-XMLTV in der heutigen Implementierung als dauerhafte Datei gespeichert wird.
- resources/lib/guide_store.py ~34-42: SQLite WAL mit Tabellen programmes/guide_alias/guide_meta und Indizes. ~69-72: neu importierte bereits abgelaufene Ereignisse außerhalb 7-Tage-Historie werden gefiltert; das löscht historisch vorhandene Daten NICHT.
- resources/lib/guide_publish44.py ~60-67: zusätzlicher guide44_inputs-Speicher je Quelle plus publizierte programmes, ausdrücklich KEINE ältere Source-/History-Retention implementiert. Außerdem programme_store46-Metadaten-Staging und expliziter guide_backup44-Ordner. Nicht nur Dateinamen scannen, sondern Tabellen/Cachekopien.
- Nutzerfrage „eine Datenbank“ ist ein vernünftiges Architekturziel, aber **keine zutreffende Beschreibung aller aktuellen persistierenden .91-Datenklassen**.

## Ziel und nicht verhandelbare Regeln
1. Download je Anbieter/Quelle in begrenzten Batches/Stream-Parser, möglichst RAM-limitiert, ggf. temporäres geprüftes USB-Staging für große gzip/XMLTV; URL/Token nie loggen. Keine unkontrollierten mehrfachen Vollkopien von XMLTV in /tmp, global cache, Backups.
2. Temp-Daten löschen sobald die vollständige, geprüfte Quellen-/Merge-Revision atomar in aktiver EPG-DB veröffentlicht UND readback bestätigt wurde. Bei Fehler nur kurzlebiges Resume-Staging mit TTL; niemals auf Fehler hin LastGood-EPG löschen.
3. Nur eine **logisch aktive** zentrale SQLite-EPG-Datenbank intern. Quellenkennzeichnung, manuelle Senderbindung, Konfliktauflösung, Fallback und Sendungsbilder-Verweise müssen nach Source-Reordering/Reboot erhalten bleiben. Nicht unüberlegt guide44_inputs streichen, wenn Quellprovenienz sonst verloren geht; stattdessen konsolidieren und zeitlich beschränken.
4. XMLTV-Picture/icon-Verweise für jeweilige Sendung persistent als geprüfte Metadaten-URL/Asset-Referenz verfügbar halten, bevor Rohfeed verworfen wird. Live-Titel, Start/Stop/ID bilden identischen Event-Key in Mini-EPG und Details.
5. Aufbewahrung: gültiges Fenster **7 Tage Vergangenheit / bis 20 Tage Zukunft**, nach Zeitende, sofern Quelle so weit liefert; abgeschnittene neue Quellen dürfen die gültigen LastGood-Events nicht entfernen. DB-Quellkopien außerhalb Fenster prunen, unnötige Aliase nach verifiziertem Referenzbeweis, keine Löschung von Nutzer-EPG-Mappings, Favoriten, Remindern, Catch-up.
6. Sichere physische Freigabe: Bounded DELETE + sicherer WAL-Checkpoint, SQLite-Compaction nur unter nachgewiesener Quell-/Zielreserve, Locks und Backups; bloße DELETE-Rowcounts sind kein physischer Platzgewinn. Kein VACUUM auf praktisch vollem Volume ohne gesicherte Ausweichkapazität.
7. Installer und Einstellungen: Bild-EPG opt-in, USB für temporäre Rohdownloads und Artwork, aktive DB samt WAL zunächst intern. Separat nachweislich entbehrliche Altlasten bereits bei Neuinstallation/Upgrade bereinigen, danach leichte periodische Pflege. Benutzer kann unter XCMate → Einstellungen → Speicher die Bereiche und Messwerte sehen.
8. Testmatrix: 3 konkurrierende Quellen inklusive EPGShare01/Provider; 100k+ Sendungen; ZIP/Gzip beschädigt; Netz/offline/Timeout; DST; 7d-20d Grenzen; SQLite Busy/Disk Full; Update/Crash/Retry/Reboot; manuelle Kanal-IDs und Bildlinks; Speicherbytes/Bytes-frei auf realer Android-Box vor/nach.
9. Fehlende echte Freisetzung oder nicht sichere Bereinigung = BLOCKED/OPEN, nicht als erledigt deklarieren.

**Einordnung:** Die großen Artwork-Daten und der separate Kodi-Thumbnail-Cache können weiterhin größere Speicherfresser als das Text-EPG sein. Erst die pro-Volume-Inventur entscheidet die Priorität der Auslagerung.
