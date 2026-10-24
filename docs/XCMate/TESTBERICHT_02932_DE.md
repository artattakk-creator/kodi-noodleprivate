# XCMate 0.1.29.32 – Suchfenster-Testkandidat

Stand: 24.10.2026. Draft-PR [#155](https://github.com/artattakk-creator/kodi-noodleprivate/pull/155). **CI_ONLY / Android NOT_TESTED / Issue #140 weiterhin offen.**

## Änderung und Nachweis

Die interaktive Suche aus dem EPG lief über einen Containerwechsel und konnte abhängig vom Kodi-Handle in der alten Directory-Suche landen. Der große Guide hielt beim Containerwechsel noch die äußere Navigation-Lease. Root-SearchWindow initialisierte zusätzlich zunächst die Filmstartseite. Der neue Stand führt diese Aufrufe direkt in die vorhandene native Suche und wartet bei Guide-Wechseln auf das Ende des Callbacks, Owner-Pumps und die tatsächliche native Fensterfreigabe. Back stellt den gespeicherten Guide-Ausschnitt wieder her.

Die vier vorab geschriebenen Reproduktionstests scheiterten auf .31; im Fix bestehen sie. Insgesamt **21 neue Navigationstests** decken beide Handles, echte Owner-Pump-Sequenz, nativen Close-Lag/Timeout, Guide-Back-Snapshot, verspätete Ergebnisse, Keyboard-Abbruch, Detailrückkehr, explizite Auswahl, 20 IR-Modellzyklen und redigierte Diagnose ab. [Fehlernachweis/Vertrag](SUCHFENSTER_FEHLERNACHWEIS_02932_DE.md) trennt belegten Codepfad von noch unbewiesener nativer Android-Race-Kausalität.

Zusätzliche bestehende Tests prüfen Programmtitel-/Sendernamen-Matching, Alias/manuelle Zuordnung, Short-Now und langsame vollständige Scans. Matching und EPG-Datenquellen wurden nicht verändert. Ein früherer 11er-Sendernamen-Treffer wird ausdrücklich nicht als Programmtitel-PASS gewertet.

## Automatisierte Prüfung und Paket

- **1.068 Tests PASS**, 119,468 s lokal, 0 Fehler/Fehlschläge/Skips oder Thread-Ausnahmen. Vollständiger Lauf und ZIP-Prüfung: verbindliche Zahlen/Prüfsumme in [TESTERGEBNISSE_02932.json](TESTERGEBNISSE_02932.json), Ausgabe in [TESTLOG_02932.txt](TESTLOG_02932.txt).
- Quell-/Teststand: `fcc27c4ca8d4da68eb42a98bae5a1bc661007bdc`; Add-on-Code seit `f388fbb8539cac5c4bb5fa622a2e679373fa1e5d` unverändert. Spätere Delivery-Commits fügen nur Paket und Nachweise hinzu.
- Build in isolierter Scratch-Kopie, kein geänderter Produktionsindex. ZIP wird aus genau diesem Quellstand erneut aufgebaut; CRC, eindeutige/sichere Pfade, Manifest/ID/Version, enthaltene Originalassets, Python-AST, vollständige Quellbyte-Identität und deterministischer Neuaufbau geprüft.
- Sprachdateien unverändert: DE/EN je **783 gültige PO-Kontexte**, Python-Syntaxprüfung PASS.
- Angepasste alte Tests: Directory-Suche ausdrücklich über `search_section`; Versionsverträge auf .32. WindowStart-Mocks akzeptieren den zusätzlichen vorhandenen After-Close-Vertrag. Navigation-Freeze normalisiert **nur zwei** neue optionale Anchor-Hooks; übriger alter Vollmodulhash bleibt. Guide-Freeze erhält historische Datei, pinnt den bewusst geänderten vollständigen Suchguide und prüft alle unveränderten Klassenmethoden gegen .31. Keine entfernten/übersprungenen Tests und keine abgeschwächten Player-/SSRF-/Integritätsprüfungen.
- **GitHub-CI: 1.068 Tests PASS in 192,306 s**, Run [40110190083](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40110190083). Der GitHub-PR-Workflow liefert ein Review-Artefakt mit derselben ZIP-SHA256 wie der lokale Neuaufbau; ein erneuter Raw-Download von GitHub wurde ebenfalls bytegleich geprüft. Der nach `main` schreibende Publish-Schritt ist für PRs gesperrt. Finale CI-URL/Job/ZIP-Vergleich stehen in [CI_NACHWEIS_02932.json](CI_NACHWEIS_02932.json).

ZIP im PR-Branch: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.32.zip`; daneben `.zip.sha256`. SHA256: `5490a3c9d0e0cc6aa593b9f03b8718157fcbcdcfe13564db178d644dea6a362e` (2.364.040 Bytes, 252 Dateien). Prüfsumme auch in TESTERGEBNISSE. **Nur Testpaket**, keine Änderung am normalen Kodi-Updatekanal und kein Release/Tag.

## Bestandsschutz

[SCHUTZPRUEFUNG_02932.json](SCHUTZPRUEFUNG_02932.json) vergleicht direkt mit main `59085e94f78d0bc9d66e3f6561a6fecf100abdf5`:

- **243 bestehende Add-on-Dateien bytegleich**, darunter Player, Owner-Pump, Fernbedienung, Autoplay/Resume, Portale/Profil, EPG-Matcher/Datenbank, Artwork sowie alle Downloads/Recorder/Dienste.
- **98 Original-Themebilder** separat bytegleich; Originalicon und Lightweight-Splash mit geprüften Originalhashes erhalten.
- `addons.xml`, `.md5`, Publish-Workflow und bisherige .31-ZIP unverändert. Andere lokale Entwicklungsarbeiten (62 geschützte Dateien) erhalten.
- Keine Profil-/Schemaänderung, Cache-/Joblöschung, Keymapänderung oder Änderung einer Benutzer-/Provideradresse.

## Android und Grenzen

[Ausführbare Checkliste NAVSEARCH-01–08 / REG-01–03](ANDROID_ABNAHME_02932_DE.md): **sämtlich NOT_TESTED**. Über .31 installieren, keine Neuinstallation. Einmal kurzer S1–S5-Smoke, betroffene Such-/Back-/Fokusabläufe und BINGIE/Estuary prüfen. Kein pauschaler neuer Vierstundenlauf; historische MEM1/MEM2 bleiben PASS. .31-Ergebnisse bleiben unverändert **9 PASS / 8 FAIL / 3 NOT_TESTED**, Q1–Q3 FAIL.

Hosttests beweisen keine Android-Skin-/IR-Abnahme. Besonders relevant: Freigabe der nativen Fenster-ID und positiver Directory-Handle im tatsächlich sichtbaren Kodi-Container. Timeout beendet kontrolliert, ohne fremdes Fenster zu schließen oder Rekursion zu starten. Ein fremder vorhandener Player wird nur durch die unveränderten Besitzer-/Sessionprüfungen der bereits bewährten Übergabe behandelt.

Die Playerstatus-Ausnahme nach Serienende sowie Service-Stop-Warnung beim Update sind **separate, hier nicht reparierte Auditbefunde**. Kein Zusammenhang mit der Suchursache behauptet. Downloads/Aufnahmen, Cover/OSD/Wizard und übrige Roadmap weiter getrennt. Beide privaten Rohlogs wurden nicht veröffentlicht; neue öffentliche Diagnosen enthalten nur feste Phasen/Counts und zufällige Sessions.

**Kein Merge, Release, OTA-Publish und keine Schließung von #140. Erst tatsächliche Android-Abnahme und ausdrückliche Freigabe des Nutzers.**
