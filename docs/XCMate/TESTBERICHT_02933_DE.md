# XCMate 0.1.29.33 – Suchreparatur und bebilderte Ergebnisse

24.10.2026 · [Draft-PR #156](https://github.com/artattakk-creator/kodi-noodleprivate/pull/156) · **Android NOT_TESTED / kein Release**.

## Umfang

Kumulativ auf `main` `6c1b9c34b547764523fba295e449821513c8f647` (.32), Quell-/Teststand `16276391abd1dfa1007e270042b05950dc13c509`. Spätere Paket-/Berichtscommits ändern keine Runtime-Dateien.

- #140: Im belegten Kodi-Busy-Fall 10138 kehrt der bisherige Aufruf nach Freigabe des eigenen Guide-Owners zurück. Eine einmalige asynchrone Plugin-Fortsetzung erhält den Add-on-Kontext und erwirbt eine eigene Lease; echte Modal-/Owner-/Portal-/Player-/Ordnerprüfung bleibt aktiv. Kein höherer Timeout, Modal-Bypass oder fremdes Dialogschließen.
- Medien-/Guide-XML: sichere dauerhaft sichtbare Standardziele, keine alten 400→120-Edges beim Fokus-Lag, redigierte Fokuszustände, unveränderte Trefferframes nicht wiederholt zurücksetzen.
- Ergänzender Nutzerauftrag: typisierte Zeilen mit Senderlogo bzw. Film-/Serienposter, eigenständigem Titel und Typ-/Jetzt-/Jahr-/Genrezeile. Nur lokale Bilder/Cachemetadaten bzw. saubere lokale Ersatzbilder; Updates auf bestehenden ListItems erhalten Fokus und Position. Keine neuen Grafikdateien oder Änderungen am Originalicon.
- EPG-Matching/Counts unverändert: Nur die Darstellung darf den schon ermittelten Jetzt-Titel auch beim Namenstreffer zeigen. Kein Sendernamen-Match als Programmtitel-PASS ausgegeben.
- #98 bleibt separater Folgeauftrag nach erfolgreicher Suchabnahme und Main-Freigabe. Keine EPG-Zuweisungs-/Preview-/Mappingmigration in .33. Downloads/Recorder weiterhin zurückgestellt.

[Architektur, API-Nachweis und Grenzen](SUCHE_BUSY_UI_02933_DE.md) · [Zusatzauftrag Suchdarstellung](SEARCHUI_ZUSATZAUFTRAG_02933_DE.md) · [vorher scheiternde Reproduktion](FEHLERNACHWEIS_02933.json).

## Validierung

**25 neue Tests: 19 Busy-/Fokus- und 6 Suchdarstellungsprüfungen.** Darunter echte Owner-/Search-/Guide-Restore-Sequenz im Modell, drei Timeout-Repros, Action-/Directory-Handle, fremde Modals/Owner, Player-/Portal-/Ordnerwechsel, TTL/Replay/abgelehnte neuere Anfrage, native Keyboard-Reinit, lokale Logos/Cover/Fallbacks und Bildnachladung ohne Fokusverlust. Drei vorab geschriebene Tests scheiterten auf unveränderter .32 und bestehen im neuen Stand.

**Lokal 1093 Tests PASS in 125.872 s**, 0 Fehler/Fehlschläge/Skips/Thread-Ausnahmen. ZIP-SHA256: `3a647b5f9428b08843ce76479d67bb3f05b2ec555982947eeb4883948fcd1df9`; 2369065 Bytes / 254 Dateien. Vollständige Laufzahlen, ZIP-Größe und SHA256 stehen in [TESTERGEBNISSE_02933.json](TESTERGEBNISSE_02933.json), vollständige Ausgabe in [TESTLOG_02933.txt](TESTLOG_02933.txt), **GitHub-CI ebenfalls 1.093 Tests PASS in 197,786 s**, Publish-Schritt SKIPPED. CI-Artefakt und lokaler ZIP-Neuaufbau haben denselben SHA256-Digest. GitHub-CI und Artefaktabgleich in [CI_NACHWEIS_02933.json](CI_NACHWEIS_02933.json). DE/EN je **788 PO-Kontexte gültig**, Python-Syntaxprüfung PASS. Keine historischen Tests gelöscht/übersprungen; nur explizite aktuelle Versions- und sichere XML-Standardziele als beabsichtigte neue Verträge aktualisiert.

Paket: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.33.zip`, daneben `.zip.sha256`. In isolierter Scratch-Kopie gebaut; eindeutige sichere Pfade, CRC, Manifest/ID/Version, Python-AST, vollständige Quellbyte-Identität und deterministischer Neuaufbau geprüft. GitHub-CI liefert unabhängig denselben Paketdigest. Kein Produktionsindex geändert oder veröffentlicht.

## Bestandsschutz

[SCHUTZPRUEFUNG_02933.json](SCHUTZPRUEFUNG_02933.json): **239 bestehende Add-on-Dateien bytegleich**, darunter Dienste, Player/Owner-Pump, Fernbedienung, Resume/Autoplay, Profile/Portale, EPG-Quellen/Mappings/Store, Artwork, sämtliche Download-/Recorder-Module. Alle **98 Original-Themebilder** unverändert, Originalicon-/Splashhashes erhalten. Matcherdatei entspricht dem Ausgangscode vollständig bis auf die klar geprüfte reine Ausgabe des bekannten Jetzt-Titels; Matchingberechnung und -zählung identisch.

`addons.xml`, `.md5`, Workflow und bisherige .32-ZIP unverändert; 62 geschützte Dateien anderer lokaler Entwicklungen erhalten. Keine Profil-/DB-Schemaänderung oder Daten-/Cache-/Joblöschung; nur bestehende abgeleitete XML-Varianten bekommen eine neue Renderer-Revision, alte Dateien bleiben bestehen.

## Gerätetest und Freigabe

[Android-Anleitung](ANDROID_ABNAHME_02933_DE.md): Zunächst ausschließlich **A1–A3**, dann bei PASS **SEARCHUI-01–06** und gegebenenfalls erweiterte Navigation. Sämtlich **NOT_TESTED**. Über .32 installieren, keine Deinstallation, kein Downgrade, kein Profilreset. Einmal kurzer Bestandssmoke; kein pauschaler Vierstundentest.

Hostmodelle belegen nicht die tatsächlich auf Android gerenderte/betätigbare Oberfläche oder den genauen Busy-Erzeuger. Kodi-21.2-API wurde geprüft, die tatsächliche Entkopplung des beobachteten Busy-/Skinzustands benötigt Nutzerabnahme. Echte fremde Dialoge und geänderter Player-/Portal-/Ordnerkontext bleiben absichtlich geschützt; abgewiesene Übergaben öffnen kein fremdes Fenster.

Historische .32-Abnahme **7 PASS / 10 FAIL**, .31-/ .30-Werte und frühere MEM1/MEM2-PASS unverändert. Keine privaten Rohlogs, Suchbegriffe oder Provider-/SMB-Adressen veröffentlicht. **Kein Merge, Release, OTA-Publish, Tag oder Schließen von #140/#98 ohne ausdrückliche Nutzerfreigabe.**
