# GS Media 1.8.0 – zentraler Add-on-Katalog und Kodi-Startrettung

Stand: 01.11.2026. **DRAFT / NICHT MERGEN / NICHT AUF EINEM GESTÖRTEN KODI TESTEN**.

## 1. Gerätebefund (Nutzer)
Nach dem .66-Merge auf GitHub meldet der Nutzer, dass Kodi auf einer Android-TV-Box nicht mehr startet. Vorher erschienen Fehler u. a. von **SlyGuy Common** und weiteren Helpern. Es liegt noch kein vollständiger neuer Kodi-Log bzw. Android-Crashtrace für die tatsächliche Ursache vor. **Ein Repository-Git-Merge ist nicht gleich eine Android-Installation**: installierte Version, Repo-Publish und Boot-Ursache getrennt nachweisen; zeitlichen Zusammenhang nicht als Kausalbeweis behandeln.

**Datenschutz/Bestandsschutz:** Keine Deinstallation von Kodi, kein "Daten löschen", keine automatische Reinstallation, kein Überschreiben des Titan-BINGIE-MOD-Profils, der XCMate-Portal-/EPG-Daten oder Tokens. Zuerst externes Backup des gesamten Kodi-Profils (einschließlich addon_data, Datenbanken, Einstellungen) anfertigen. Wenn Kodi nicht startet, außerhalb von Kodi nach Berechtigung und zugänglichem Backupweg suchen; keine pauschalen ADB-/Filesystem-Befehle ohne Gerätetest. Erst Log/Trace sichern, dann nach konkreter Ursache gezielt reparieren.

## 2. Ziel: ein Installationskatalog, eindeutige Bezugsquellen
- **XCMate** `plugin.video.xtreammate`: eigener GS-Media-Quellcode bleibt auf `main` .66. Keine Änderungen am Plugin durch diese Repo-PR.
- **xVAULT**: bereits als unveränderter Upstream über `mojomedia1812/xVAULT` in GS Media 1.7.0. Kein Doppel-Fork; Lizenz, Anbieter, eigene Konfiguration und Spielermapping unangetastet.
- **Cumination**: bereits via Dobbelina + SMR im zentralen Repository. Keine kopierten Scraper oder Dependency-Rewrites.
- **TMDb Helper**: Kodi-21/Omega-Upstream `jurialmunkey/repository.jurialmunkey/master/omega/zips` mit passendem `script.module.jurialmunkey`, `script.module.infotagger` und weiteren im Manifest deklarierten Modulabhängigkeiten (kein blindes Pinnen einzelner Module). Kodi 20/21-Schutz über `minversion=20.9.1`; im Build `repository.gsmedia` 1.8.0.
- **MP3 Streams Echoed**: ID `plugin.audio.m3sr2019`, Version 2026.1.0, Buildhost-Paketimport aus Echo-Storm/MP3-Streams-2026-Kodi. Fixierter Git-Blob `ebc7f51129fb24f7db0c9d85c8c5c03ec3f97929`; ZIP-Pfade, CRC, Größe, Python 3 und Metadaten strikt prüfen. Quell-/Lizenzprüfung vor Freigabe.
- **SHOUTcast**: `plugin.audio.shoutcast` 2.5.2+matrix.1 als unverändertes, explizit erlaubtes offizielles Kodi-Omega-Archiv, Quelle `mirrors.kodi.tv`, verifizierte ZIP-Pfade/Manifest/Abhängigkeiten. 
- **Pluto.TV**: vorhandener, getrennter Kandidat aus PR #51 `plugin.video.plutotv` 1.6.2, optional mit in diesem Draft; nicht im neuen Nutzerauftrag zwingend.
- **SlyGuy Common**: `script.module.slyguy` und dazugehörige `slyguy.dependencies`/upstream Repo. **Noch NICHT integriert**: zunächst die tatsächlichen `repository.slyguy/addon.xml`-URLs, verifizierte Checksummen/Dateipfade, Lizenz und Abhängigkeitsauflösung anhand offizieller Upstream-Quellen prüfen. Keine erfundene `<dir>`-URL, keine eigene Fake-Version. Existierende User-Installation bis zur Diagnose in Ruhe lassen. Die SlyGuy-Fehlerursache ist damit noch nicht behoben.

**Technisches Modell:** Zentraler GS-Media-Repository-Installer bündelt nicht automatisch alle fremden Source-Repos in eigene Forks. Upstream-Kataloge sind transparent verlinkt, für ausgewählte Pakete wird der Original-ZIP-Build mit Herkunft/Hashes unverändert bzw. bei MP3 layout-normalisiert ausgeliefert. Rechte und Lizenzen müssen für Verteilung eingehalten werden. Keine unnötigen Duplikate oder globale Library-Umbauten.

## 3. Umgesetzter Draft-Stand
Frischer Branch vom .66-`main` Merge `00e930f2d1417582eba36ab797279eb8243f9cdf`, nicht vom 663 Commits veralteten PR #51. Basisänderungen:
- `src/repository.gsmedia/addon.xml` auf 1.8.0 + jurialmunkey Omega Index.
- Übernahme der isolierten, gepinnten Importer und Offline-Sicherheitstests aus PR #51 in den neuen aktuellen Branch.
- `tools/build_repository.py` erweitert um MP3 + zwei Kodi-Omega-Pakete.
- `.github/workflows/publish.yml`: explizite Whitelist für ZIPs/Prüfsummen bei finalem produktiven Main-Publish.
- `tests/test_repository_layout.py` prüft die neue Quelle/Version und erhält XCMate .66.

## 4. Pflichtgates vor Merge
1. Kodi-Startfehler durch bereinigtes Kodi-Log (`kodi.log`/`kodi.old.log`), Android-Starttrace und installierte Paket-Versionen differenzieren; `script.module.slyguy` **nicht ohne Evidenz als Ursache behaupten**.
2. SlyGuy-Originalindex/Checksum/ZIP-Dateipfad direkt vom Upstream lesen und alle zwingenden SlyGuy-Abhängigkeiten absichern; verifizierte Einbindung erst nach eigener Prüfung auf separatem Commit.
3. Vor jeder Redistribution Python-Source/License/NOTICE und Archive der Upstream-Pakete samt legitimer Nutzungsrechte verifizieren.
4. Echte Upstream-HTTP-Downloads, TLS, Hashes und Add-on-IDs prüfen; auf Fehlern fail-closed (keine veralteten oder gemischten ZIPs veröffentlichen).
5. Auf Kodi 21.3/Android ARM32: frisches Testprofil mit Repository-Update 1.7.0 -> 1.8.0, alle Apps und Dependencies installieren, Kodi kalt neu starten, Dienste (TMDb/SlyGuy) beobachten; keine produktiven Box-Profile verändern.
6. Kodi-Repo `addons.xml`, `addons.xml.md5`, `repository.gsmedia-1.8.0.zip`, selektierte Add-on-ZIPs und Checksums auf identische Versionen prüfen. Keinen automatischen Repo-Updateerfolg ohne nachgewiesenen Publish behaupten.
7. Unverändertes XCMate .66 (Startsender, Portal-/Gruppenspeicher, Widgets, EPG, TMDB-Token, Resume/Autoplay) sowie bestehende Cumination- und xVAULT-Quellen in Smoke-Tests schützen.
8. Vollständige CI und Repo-Unit-Tests grün, keine Skips oder Tests löschen; Android-Tests ausdrücklich als NOT_TESTED markieren, solange keine echte Abnahme vorliegt.

**Merge-Status: BLOCKED, bis Upstream, CI und Boot-/Android-Gates nachweislich erledigt sind.**

## 5. Codex-Folgeauftrag ohne Nachfragen
Öffne den aktuellen Draft-PR im Repository `artattakk-creator/kodi-noodleprivate`, lies dieses Dokument und den alten PR #51 nur als geprüfte Referenz. Prüfe SlyGuy-Upstream/Abhängigkeiten und korrigiere einen roten neuen Build zielgerichtet. Dokumentiere reale Nutzer-Startfehler ohne Ursachenbehauptung. Gib schließlich ZIP/SHA, GitHub-Run, Pr-Head, Testzahlen und Freigabestatus an. **Keine produktiven Merges, keine Kodi-Geräteaktionen und keine Profilresets.**
