# XCMate 0.1.29.72 — sicherer Film-/Serien-Nachscan (#355)

**Review-Kandidat, kein Release.** Kumulative Basis: `main`
`f6ce8b135191c223d9cee7c0201f630acd196b75` (einschließlich PR #353 und Pilot-Veröffentlichung #354).
Der reguläre Pilot-Kanal bleibt auf XCMate **0.1.29.71** / Setup **0.5.20**.
Kein Merge, keine Kanalveröffentlichung, kein Installer-/Skin-/Keymap-Eingriff.

## Befund und nachweisbare Ursache

Der Android-Befund 53 Live-Gruppen, 0 Filmgruppen, 0 Seriengruppen und 3.357
gespeicherte Live-Sender ist ein erfolgreicher Live-Commit. Er beweist keine
leere Remote-VOD-API. Es liegen hier keine authentifizierten API-Antworten des
betroffenen Geräts vor; dessen genaue Remote-Ursache bleibt **NOT_TESTED**.

Im .71-Code sind drei konkrete Fehlerpfade reproduzierbar:

1. `Adapter.categories(..., remote=True)` ruft reguläre Xtream-Methoden ohne
   erzwungenen Remoteabruf auf. `_get_json` kann dadurch sogar eine bis zu
   30 Tage alte leere Liste wiederverwenden. „Remote“ war kein Beweis für HTTP.
2. Bei einem Wrapper-Objekt iteriert der Adapter dessen Schlüssel und verwirft
   sie als Nicht-Dictionaries. Das Ergebnis wird ohne Formatfehler zu `[]`.
   Der reguläre Client kann außerhalb der Wizard-Deadline zudem Transportfehler
   in `None` und anschließend `[]` verwandeln.
3. Der Wizard akzeptiert den Gesamtabruf, sobald irgendein Bereich Gruppen
   enthält. Damit wurde 53/0/0 ohne bewusste Teilabnahme fortgeführt.

Die tatsächlichen Xtream-Aktionen wurden geprüft: `get_vod_categories`,
`get_vod_streams` mit `category_id`, `get_series_categories`, `get_series` mit
`category_id`; Authentifizierung über denselben gespeicherten `player_api.php`-
Zugang. Username/Passwort werden durch die bestehende HTTP-Schicht URL-kodiert;
der Integrationstest verwendet Sonderzeichen. Keine anderen Zugangsdaten und
keine geratenen Endpunkte werden ausprobiert.

## Änderung und Bedienung

**XCMate → Einstellungen → Portale/Provider verwalten → vorhandener Provider →
Katalog aktualisieren (Filme / Serien).**

1. Filme und/oder Serien mit den unabhängigen Checkboxen wählen (beide voreingestellt).
2. Anmeldung und getrennte Remote-Kategorieabfragen laufen im Datenworker.
3. Gefundene Gruppen je Bereich bestätigen. Vorhandene Auswahlen bleiben
   vorbelegt; beim erstmaligen Fund nach 0 Gruppen sind alle vorgeschlagen.
   Eine bewusst früher abgewählte, bekannte Gruppe bleibt abgewählt.
4. **Starten** bestätigen. **Abbrechen/Zurück** beendet das Fenster; ein noch
   auslaufender Worker behält den bestehenden Writer-Lock bis zu seinem Ende.
5. **Ergebnis** zeigt gefundene/ausgewählte/veröffentlichte Gruppen, gelesene,
   neue, geänderte, unveränderte und übersprungene Titel, Fehler und echte
   DB-Readback-Zahlen. **Erneut prüfen/wiederholen** ist eine bewusste Aktion.

Der neue Nachscan unterstützt **Xtream**. M3U/STB werden eindeutig als anderer
Quellentyp gemeldet und bleiben unverändert. Unbekannte Providerformate werden
diagnostiziert, nicht als leerer oder erfolgreicher Import behandelt.

## Speicherung und Wiederanlauf

- `vodsync_api72.py`: ungecachte Requests, Streaming-Arrays und bekannte
  `data/items/results/categories/streams/series`-Wrapper (maximal zwei Ebenen),
  komplette Header-/Trailerprüfung, numerische Seitenfolge mit Total-Abgleich.
  Unbekanntes Offset-/Pagingformat wird abgelehnt. Wiederholte Seiten/IDs und
  abgeschnittene Antworten veröffentlichen keine Gruppe.
- Socket-Timeout 12 s und bestehender Streaming-Leerlaufschutz; kein pauschales
  Gesamtlimit für aktiv fortschreitende große Kategorien auf ARM32. Authentifizierung
  bleibt zeit-/größenbegrenzt. Keine automatische Retry-Schleife. Ein Rate-Limit oder grundlegender Verbindungsfehler beendet den
  Durchlauf. Netzwerkfehler, HTTP-Status, Authentifizierung, deaktivierte
  Kontobereiche, echte Leere, Schema, SQLite, Reserve und Berechtigung haben
  unterschiedliche sichere Diagnosecodes.
- `vodsync72.py`: dieselbe Portal-ID und bestehende Verbindung; derselbe
  `.catalog-delta52.lock` wie beim Service plus scoped SQLite-Leases. Kein
  paralleler Doppelscan. Nur erfolgreiche Film-/Seriengruppen werden zusätzlich
  aktiviert; bestehende Gruppen und Live-Startparameter werden nicht abgewählt.
- `vodsync_store72.py`: vor jedem Import eine private SQLite-Sicherung unter
  `addon_data/plugin.video.xtreammate/vodsync72/before-*.sqlite` mit geschütztem
  Manifest, SHA256 und `integrity_check`. Gesichert werden ausschließlich die
  betroffenen aktiven Film-/Serienkataloge, Gruppen und Selektions-/Bereichsflags.
  Keine Portalpasswort-, TMDB-Token-, EPG- oder Kodi-Konfigurationsdatei wird kopiert.
  Die .71-POSIX-/Android-App-Storage-Prüfung und Speicherreserve bleiben aktiv.
- Stabile Identität `(portal_id, kind, category_id, stream/series_id)`. Eine neue
  private Generation beginnt mit den bestehenden Titeln; valide Providerdaten
  werden ergänzt/aktualisiert. Fehlende Titel werden nie gelöscht. Fehlende
  neue Bildreferenzen überschreiben keine bestehende Coverreferenz.
- Erst nach EOF, Zähl-/Digestprüfung, Kontrolle auf konkurrierende Änderungen
  und vollständiger Transaktion wechselt der Gruppen-Head. Ein unabhängiger
  SQLite-Readback prüft die publizierte Generation. Das Journal und der Head
  werden atomar gemeinsam geschrieben.
- Nach einem Hard-Kill wird eine unvollständige eigene Staging-Generation beim
  bewussten Wiederholen ersetzt. Ein vollständig committed Import mit noch
  ausstehender Konfigurationsaktivierung wird verifiziert und ohne erneuten
  Titeldownload aktiviert. Bereits abgeschlossene Gruppen bleiben bei einem
  späteren Gruppenfehler erhalten; das Ergebnis lautet dann **PARTIAL**, nicht PASS.
- Aufgeräumt werden nur eigene, inzwischen unsichtbare Staging-Kopien, niemals
  ein aktiver Head oder ein bestehender Titel. Sicherungen bleiben privat erhalten.
- Nach Commit verwendet die Medienansicht ihre bestehende Katalogrevision.
  Nur Film-/Serien-Widgetframes werden gezielt veröffentlicht. Keine Änderungen
  an Widget-Routen, BINGIE-Bindings, Live-TV, EPG oder Texturecache.

## Testnachweise

- **41 gezielte Hosttests bestanden**: tatsächlicher synthetischer HTTP-Server,
  reale Xtream-Parameterkodierung, SQLite-Writer und Reader, Cold-Readback im
  neuen Prozess, Film-only/Serien-only, Fehlerformate/HTTP 401/403/404/429/500,
  Wrapper/Paging, doppelte IDs, Teilantworten, Cancel, SQLite-Sperre, readonly,
  ENOSPC/Reserve, Hard-Kill nach 256 Staging-Zeilen, Wiederholung/Idempotenz,
  Backup/Integrität/Restore auf isolierter Kopie und GUI-Owner-/Lock-Lifecycle.
- **Native Kodi 21.2 Linux PASS**: echtes neues WindowXML, Start per nativer
  OK-Eingabe, Worker-Fortschritt/Owner-Completion, Ergebnis, native Zurück-Taste
  und je ein Film-/Serienitem über echte `Files.GetDirectory`-Widget-Aufrufe.
  Die Checkbox- und Bestätigungsantworten sind synthetische Fixtures. Die
  vorhandenen Kodi-/BINGIE-Regressionsgates bleiben zusätzlich bestehen.
- Der Testbestand hat **exakt 3.357 Live-Sender in 53 Gruppen**. Vorher-/Nachher-
  Digest identisch. Die aufgezeichneten HTTP-Aktionen sind ausschließlich AUTH,
  Film-/Serienkategorien und deren Titel. Live-/EPG-Requests: **0**.
- Alle 685 bisherigen Add-on-Dateien bleiben erhalten; sechs vorhandene Dateien
  haben exakt dokumentierte Deltas. Alte Scope-Verträge normalisieren nur diese
  bytegenauen freigegebenen Änderungen; keine Testmethode/Skip-Bedingung entfällt.
  Vier bestehende Versionsasserts werden regulär auf .72 angehoben.
- **Gesamte Host-Suite auf Quellstand 804aa79: 2.943 Tests PASS in 460,867 s,
  0 Fehler, 0 Skips.** Die abschließende Streaming-/SQLite-Diagnosekorrektur
  ergänzt zwei Tests; alle 41 gezielten Tests des endgültigen Pakets bestehen.
  Ausgeführt mit den bestehenden CI-Abhängigkeiten Pillow, impacket 0.13.0 und
  simpleeval 0.9.13. Keine historischen Tests ausgelassen.
- [.72-CI 41791895817: SUCCESS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41791895817):
  Voriger Paketstand: 39 gezielte Tests, unveränderter Pilot-Index, ZIP-Neubau und native Kodi-Prüfung.
  Das endgültige Paket wurde danach wegen des ARM32-Streaming-Limits erneuert;
  maßgeblich sind die abschließenden CI-Nachweise in PR #356 und der unten genannte SHA256.
  [Historisches Review-Artefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41791895817/artifacts/13303801914).
- Die vollständigen zusätzlichen Kodi-/BINGIE-/TS-/HLS-Gates und der komplette
  CI-Hostlauf sind im [Draft-PR #356](https://github.com/artattakk-creator/kodi-noodleprivate/pull/356)
  mit ihren abschließenden Action-Links dokumentiert; offene Läufe werden nicht als PASS gezählt.
- Alle echten Android-Prüfungen und der reale Anbieterbefund: **NOT_TESTED**.

## Test-ZIP

`test-builds/02972/plugin.video.xtreammate-0.1.29.72.zip`, **689 Dateien**, 3.326.918 Bytes.
SHA256: `aebd3b268b67e8f2407f6643d4f6c51eb8a39591908534d40e23910e40abd4c6`.
Daneben liegt die `.zip.sha256`-Datei. Reproduzierbar mit
`python tools/package_xcmate71.py /tmp/xcmate72-review` (Builder ist versionsunabhängig).
ZIP-CRC, bytegleicher Quellinhalt und Ausschluss privater DB-/Log-/Profildaten
werden geprüft. CI baut das ZIP erneut und vergleicht es mit diesem Testpaket.

Installation erst als bewusstes **Update aus ZIP**, keine Deinstallation und
keine neue Einrichtung. Der reguläre Kodi-Kanal wird in diesem PR nicht geändert.
Android-Abnahme: `ANDROID_ABNAHME_02972_ISSUE355_DE.md`.
