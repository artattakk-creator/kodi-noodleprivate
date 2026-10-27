# XCMate .46 – vollständige Master-/Issue-Abnahmematrix

**Neueste direkte Nutzerfreigabe im Chat vom27.10.2026:** Den bereits implementierten und gezielt getesteten Datenbankumbau nach vollständiger Regression in .46 mit aufnehmen. Diese spätere direkte Weisung ersetzt für diesen Kandidaten die zwischenzeitliche Verschiebung aus #241/#242. Grafische EPG-/Widgetteile und alle P0-Fixes bleiben enthalten. #242 wird nicht eigenmächtig geschlossen; weitere Konsolidierung/Abnahme bleibt separat nachvollziehbar.


Basis main/.45 a2f83c49; Arbeitsbranch unverändert. IMPLEMENTED und HOST_PASS bezeichnen Code/Modelle, keinen Geräte-PASS. Alle neuen Box-B-Gates ANDROID_NOT_TESTED. Keine Issues geschlossen. Historische .45-Befunde bleiben erhalten.

| Auftrag / Referenz | Umsetzung / Hostbeleg | Android / verbleibende Grenze |
|---|---|---|
| #241 P0 Live-Timeout, #194/#216/.42 | IMPLEMENTED: historischer Timeout bleibt erhalten; idempotente einmalige Rückkehr nach passender später FIFO-ACK/Session/Lease; Hosttests Fremdplayer/Modal/Shutdown/Stale/kein Doppelstop | ANDROID_NOT_TESTED; dauerhaft ausbleibende native ACK bleibt BLOCKED_NATIVE_QUEUE_STALLED, keine Decoderreparatur behauptet |
| #240/#241 Filmwidget, #229/#230 | IMPLEMENTED: v2-Heads/Legacy-Existenz-Seeks, kein unnötiger Archivscan; LastGood/Busy/Budget/Empty/Revisionsprüfung und sichere Stufencodes | .45 Filmwidget FAIL historisch; .46 ANDROID_NOT_TESTED, reale DB-Ursache nicht allein aus synthetischer Repro endgültig bewiesen |
| #240/#241 vollständige Startgruppe | IMPLEMENTED: keine12er-Abschneidung,64er-Keysets/16er-EPG und atomare Dateiseiten;137 und1001 Sender hostgeprüft, Ende/Pin/Klickziele | ANDROID_NOT_TESTED; tatsächliches BINGIE-Scrolling/RAM und sehr große Gruppen offen |
| #241 Architekturkommentar SQLite/7+20 | IMPLEMENTED: programme_artwork.sqlite mit WAL/App-ID/Schema1, echte Quellfakten/DTO/TTL/Artrefs,32er-Backfill und128MiB Datenbudget;16:9-SHA-Blobs, Crash-/Quell-/Inkrementaltests | ANDROID_NOT_TESTED; reale20-Tage-Daten fehlen ggf. BLOCKED_DATA_NOT_AVAILABLE; kein neuer Refresh ohne Backupfreigabe |
| #239 grafisches EPG + Live-Widget gemeinsam | IMPLEMENTED: geteilter readonly Eventvertrag, Bild-/Folgenprovenienz, Details, separates Logo links oben, Fokusplot, Now→Next | ANDROID_NOT_TESTED; kein Gesamt-DoD vor beiden Gerätepfaden |
| #206/#207/#182/#229/#230 native BINGIE-Reihen | Bestehende URLs/Shortcuts/DirectoryProvider erhalten; native Reload-Properties, optionaler hashgeschützter2.2.3-Renderer und separater Reloadadapter | BLOCKED_NO_RELOAD_HOOK/BLOCKED_NO_OVERLAY_FOCUS_BINDING falls lokal nicht vorhanden; Anpassung nur nach separater bewusster Freigabe, keine automatische Skinänderung |
| #240/#241 schnelle Start-/Medienbedienung | IMPLEMENTED: Widget-Fastentry, frühe lokale Startgruppe, optionale Importvorbereitung im Worker, RAM-Reloadbridge, stabile Profilreads, FLOW46-Marker und Aggregatanalyse | ANDROID_NOT_TESTED; Cold/Warm Box-B-p50/p95 fehlen, Schätzung30s nicht als Messwert übernommen |
| #240/#241/#228/#151/#111 Cover-/Metadatenmanager | IMPLEMENTED: echtes Thumbnailraster/Rolefilter/Preview/Use/Save, sichere Worker/Cancel/Null-/Netzfehler und bestehende persistente Auswahl | .45 UX FAIL historisch; .46 ANDROID_NOT_TESTED mit echten Providerbildern/Neustart/optionalem Token |
| #231 EPG-Sicherung | IMPLEMENTED: befüllter Guide verlangt echten Backupnachweis statt nur Schemamarker, manual/service/Xtream-/M3U-/STB-Gates; keine Schema-/Datenresetaktion | Auf Box B BACKUP_VERIFIED unbestätigt; Import-/Refreshabnahme BLOCKED bis echte Sicherung + gesonderte Freigabe; read-only erlaubt |
| #161/#98 Mehrquellen/Chooser | PARTIAL: bestehende manuelle Zuordnung zuerst, stabile Eventherkunft, Kollisionen konservativ; keine globale Mappingmigration | Vollständiger Quellchooser mit Livepreview/Save/Cancel DEFERRED, separat nach stabiler Kernabnahme |
| #232 Vortage | Bestand −1/−2/−7 read-only, reale historische Ereignisse im neuen Detailpanel | ANDROID_NOT_TESTED groß−1/−2/−7; frühere positive Mini-Beobachtung historisch |
| #195/#200/#236 sieben Settings/PIN/Icons | Bestand erhalten; PIN exakt6666, direkte Experimentalrouten geschützt; neue Pickerfilter/Details/Adapter mit lokalen Icons | ANDROID_NOT_TESTED; keine Kodi-Keymapänderung |
| #100/#236 Referenzinfobar | .45-Referenzlayout/echter Kodi-Sampler bytegleich,1×/2×OK erhalten | ANDROID_NOT_TESTED, kein erfundener Codec/Atmos/UT |
| #227 Suche→Film/Serie | Vorhandene Suche und Returnverträge erhalten, lediglich sichere Latenzmarker ergänzt | ANDROID_NOT_TESTED Film und Episode getrennt; .44 positiver Einzelstart historisch |
| #223–#226 Mini/Rail/Kategorien | Bestehende Layout-/Fokus-/Backlogik erhalten, neue grafische Programmeinträge ownergeführt | ANDROID_NOT_TESTED, alte .43-Fehler nicht pauschal als .45-Fehler ausgegeben |
| #238/#235/#236/PR#237 | Kumulativ ab veröffentlichter .45, gleicher Entwicklungsbranch, vollständiger Test-/Dateikatalog und Schutzprüfung | Box A keine Aktionen; Draft, kein Merge/Release, kein reguläres Repo-Update der .46 |
| #194 übrige Roadmap | Kein stilles Einbauen zurückgestellter Downloads/Aufnahmen/Storage/PVR/Wizard-/Premiummigrationen | DEFERRED, bisheriger Code/Benutzerdaten erhalten |

Hostbelege: TESTERGEBNISSE_02946.json, TESTLOG_02946.txt, NEUE_TESTS_02946.json, PERFORMANCE_02946.json und SCHUTZPRUEFUNG_02946.json. Die veröffentlichte .45 bleibt unangetastet. Keine echte Hardware-/Speicher-/Netz-/Decoderblockade wird als Erfolg etikettiert.
