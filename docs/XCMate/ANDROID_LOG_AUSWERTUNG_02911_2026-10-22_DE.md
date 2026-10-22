# XCMate 0.1.29.11 – Bereinigte Android-Logauswertung

**Stand:** 22.10.2026. Basis: vom Nutzer privat übergebenes `kodi(5).log`, 57.982 Zeilen, Zeitraum **02:10:17 bis 08:11:09** (Gerätezeit). **Niemals Original-Log öffentlich ablegen:** Die Datei enthält u. a. Trakt-Bearer-Authentifizierungsheader und weitere sensible URLs/Metadaten. Dieses Dokument enthält bewusst **keine Zugangsdaten oder Original-Streamadressen**. Betroffene Trakt-Session/Tokens vom Nutzer widerrufen/erneuern lassen.

## Versionsgrenze im Log

- `02:10:18` Kodi-Add-on-Inventar: **XCMate 0.1.29.8**
- `03:11:32` Kodi-Add-on-Manager: **XCMate 0.1.29.11**; Dienst um `03:11:33` gestartet.
- **Alle Vorher-/Nachher-Angaben beziehen sich auf diese sichtbare Versionsgrenze.** Der frühere Abschnitt darf nicht als 0.1.29.11-Befund ausgegeben werden.

## Verifizierte Fehlerzahlen

| Signal | Vor Versionsgrenze (.8) | Nach Versionsgrenze (.11) | Bewertung |
|---|---:|---:|---|
| `XCMate artwork db: code=BUSY phase=QUERY sqlite=5` | 67 | 31 | Verbesserung plausibel, aber nicht beseitigt; Zeiträume/Belastung nicht vergleichbar |
| `[XCMate][BOOT] START_FAILED` | 0 | 0 | Kein derartiger Eintrag |
| `DISPATCH_FAILED` | 0 | 0 | Kein derartiger Eintrag |
| `MODAL_TIMEOUT` | 0 | 0 | Kein derartiger Eintrag |
| `MIGRATION_FAILED` | 0 | 0 | Kein derartiger Eintrag |
| `ART_STATUS_COUNTS_FAILED error=OperationalError` | 0 | 1 | 07:22:53, zeitweise fehlgeschlagene lesende Statistik |
| `GetDirectory - Error getting plugin://plugin.video.xtreammate/` | 0 | 1 | 07:55:00, bei Root-Verzeichnisaufruf (trotz `DIRECTORY_DONE`) |
| `CDVDVideoCodecAndroidMediaCodec::* dequeue*Buffer failed` | 0 | **33.930** | Massiver Hardwaredecoder-Logburst; gesondert untersuchen |
| `PORTALS_LOAD_BEGIN` | 2.315 | 8.173 | Häufigkeit und Logging-Budget überprüfen; Laufzeit ca. 5 h nach Update |

**Wichtig:** `BUSY` beweist **keine** Datenbankkorruption, und `letzter DB-Prüfstand OK` in der Oberfläche ist **kein neuer SQL-Integritätscheck**.

## Details

1. **Bildspeicherstatus:** `art_status` im Log 5-mal ausdrücklich geroutet; Nutzer bestätigt 10/10 sichtbare Statusdialoge als PASS. Eine `OperationalError`-Klasse beim Statistik-Snapshot (`07:22:53`), ohne `START_FAILED`/`DISPATCH_FAILED`. Das entspricht der vorgesehenen fehlertoleranten UI eher als einem vollständigen Datenbankfix.
2. **Root-Verzeichnis:** `07:55:00` meldet Kodi einmal `GetDirectory` und `CGUIMediaWindow::GetDirectory` fehlgeschlagen für die Root-Plugin-URI. Unmittelbar davor `DIRECTORY_DONE` und `DISPATCH_DONE` für `action=root`. Es ist **kein** `action=settings`-Fehler; den Einzelfall bei weiteren Regressionstests beobachten.
3. **Hardwaredecoder:** `08:01:20.923–08:02:45.250`: **33.930** der zwei benannten Decoderfehler, davon 19.829 um 08:01 und 14.101 um 08:02. XCMate-Playeraufrufe zu `08:01:19`, `08:01:54`, `08:02:20` liegen in diesem Fenster. Keine Kausalität zwischen Add-on-Logik, Rockchip-Decoder, Stream und Playback-Übergang nachgewiesen. [Issue #87](https://github.com/artattakk-creator/kodi-noodleprivate/issues/87).
4. **Filmkatalog:** Nutzer sieht Banner `Import/Abfrage fehlgeschlagen. Vorhandene Daten bleiben erhalten. Erneut versuchen.` **nur bei Filmen**, nicht bei Serien. Der Log enthält keine eindeutig zuordenbare, bereinigte Katalog-Sync-Ausnahme. Ursächlichen Eintrag im lokalen `library_v1.sqlite`/Syncstatus und einem kontrollierten weiteren Log prüfen, nicht aus der Warnung allein auf Netzproblem oder DB-Schaden schließen. [Issue #86](https://github.com/artattakk-creator/kodi-noodleprivate/issues/86).
5. **Andere Add-ons:** Weitere Kodi-Repository-Fehler (veraltetes Schema/404), Trakt-HTTP-401 des TMDb-Helpers und HTTP-Downloadwarnungen eines Fremd-Repositories sind **nicht** als XCMate-Codedefekte zuzuordnen. Diese Originalzeilen enthalten sensible Header, daher keine Ausschnitte übernehmen.
6. **Threading-Traceback um 03:11:31:** `SystemExit` beim Python-Threading-Shutdown im zeitlichen Zusammenhang mit Dienstwechsel/Update, **vor bestätigtem Start der neuen Version**. Nicht als neuer 0.1.29.11-Playbackfehler interpretieren.

## Manueller Android-Teststatus (Nutzerbestätigungen)

- Bildspeicherstatus 10/10 **PASS**, read-only Stats sichtbar, letzter in UI angezeigter Prüfstand OK; Budget 514/512 MB, physischer Speicher 47.677/53.004 MB, Ready 3.767 und Space Full ungefähr 17.676.
- Darstellungseinstellungen öffnen/schließen **PASS**.
- Filmnavigation und Serien-/Staffel-/Episodennavigation **PASS**.
- Serienwiedergabe, Stop, **Resume**, Filmwiedergabe/Stop **PASS**.
- Vorhandener EPG **PASS**, Live-TV samt Senderwechsel/Overlays/Back **PASS**.
- Banner beim Filmkatalog **offen** (Issue #86).
- **Fazit:** Funktionale Android-Smoke-Abnahme **PASS mit offenen technischen Befunden**; Datenbankkonkurrenz **nicht vollständig behoben** und Android-MediaCodec-Fehlerflut **nicht geklärt**. Issues [#69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69) und [#75](https://github.com/artattakk-creator/kodi-noodleprivate/issues/75) nicht pauschal schließen. Version `0.1.29.11` bleibt in `main`; öffentliches `addons.xml` war beim letzten Abgleich weiterhin `0.1.29.8`.

## Weiteres Vorgehen

- **Nichts löschen/reparieren**: keine DB-Resets, keine Zwangs-Reimports, keine automatische Artwork-Budgetveränderung.
- Sensible Trakt-Autorisierung erneuern/widerrufen und zukünftige Logexports vor Veröffentlichung automatisch von Auth-Headern/Tokens/URLs bereinigen.
- Separat priorisieren: [#87 Decoderfehler](https://github.com/artattakk-creator/kodi-noodleprivate/issues/87); [#86 Film-Import](https://github.com/artattakk-creator/kodi-noodleprivate/issues/86); [#69 SQLite](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69); [#75 Directory/Settings](https://github.com/artattakk-creator/kodi-noodleprivate/issues/75).
- Neue PRs/Versionen weiterhin separat auf Android testen; kein Merge/Release ohne ausdrücklichen Nutzerauftrag. Nächster separater Kandidat: 0.1.29.13 / PR #82 horizontaler EPG.
