# CODEX-KORREKTURAUFTRAG
## XCMate 0.1.29.98 – vollständige CI reparieren und Pilot-Release vorbereiten

**Priorität:** P0  
**Repository:** `artattakk-creator/kodi-noodleprivate`  
**Ausgangsbranch:** `fix/xcmate-02997-artwork-epg482`  
**Bestehender Pull Request:** #484  
**Zielversion:** `0.1.29.98`

### 1. Ausgangslage

Die Fehlerkorrekturen für die Artwork-Darstellung und die manuelle EPG-Zuweisung wurden in PR #484 umgesetzt und durch unabhängige QA-Agenten überprüft.

Geprüfter Produktstand:

`38dbe103416c0040be0285be55f657c0dbe8dbd7`

Aktueller dokumentierter PR-HEAD:

`eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a`

Reviewpaket 0.1.29.97:

SHA256: `16c81e587cfe1739ae463ec69ba6d142ab75146e47c8273ae6a779ec750a1042`

Ergebnisse:

- 159 gezielte Regressionstests bestanden.
- 4/4 native Linux-Kodi-Tests bestanden.
- Unabhängige Artwork- und EPG-QA im ausgewiesenen Testumfang bestanden.
- Vollständige Pytestsuite: **4.206 PASS / 6 FAIL**.
- Vollständige Unittestsuite: **4.195 PASS / 4 FAIL / 2 ERROR**.
- Physische Android-Abnahme noch offen.

Die sechs verbleibenden Fehler betreffen historische Versions- und Paketverträge aus der Entwicklung von 0.1.29.96.

Die bisherige Pilotversion **0.1.29.97** bleibt unverändert.

### 2. Auftrag: Fehlerursachen gezielt korrigieren

Analysiere und korrigiere die sechs verbliebenen Testfehler:

1. `test_gsmedia_repo_180.GsMediaRepo180Tests.test_xcmate_release_unchanged`
2. `test_repository_layout.RepositoryLayoutTests.test_xtreammate_manifest_and_remote_service`
3. `test_xcmate_branding.XCMateBrandingTests.test_display_name_and_version`
4. `test_xcmate_cumulative_02922.IconContractTests.test_original_icon_bytes_dimensions_and_kodi_asset_reference`
5. `test_release_candidate96.Release96.test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes`
6. `test_release_candidate96.Release96.test_review_package_never_stages_or_authorizes_any_channel`

**Wichtig:** Die bestehenden Tests dürfen nicht einfach deaktiviert, übersprungen, pauschal als erwartete Fehler markiert oder ihrer eigentlichen Schutzfunktion beraubt werden.

Historische `.96`-Pakete und deren Prüfsummen müssen unverändert überprüfbar bleiben.

Trenne historische Paketprüfungen sauber von den aktuellen Releaseverträgen für `.98`.

### 3. Neue Version 0.1.29.98 erstellen

Erstelle einen neuen Release-Entwicklungsbranch auf Basis des aktuellen PR #484.

Übernimm alle bereits geprüften Fehlerkorrekturen vollständig.

Ändere die XCMate-Version auf:

`0.1.29.98`

Erzeuge ein reproduzierbares Installationspaket:

`plugin.video.xtreammate-0.1.29.98.zip`

Anforderungen:

- Vollständige ZIP-Integritätsprüfung
- SHA256-Prüfsumme
- Korrekte `addon.xml`
- Korrekte Version im Add-on und Release-Metadaten
- Keine fehlenden Dateien oder Abhängigkeiten
- Keine versehentlich enthaltenen Altdateien
- Keine Zugangsdaten, Tokens oder Benutzerprofile
- Keine Veränderung der bereits veröffentlichten .97- oder .96-Pakete

Die Produktänderungen gegenüber dem geprüften PR #484 sollen sich auf notwendige Versions- und Paketierungsanpassungen beschränken.

### 4. Vollständige Tests wiederholen

Führe sämtliche relevanten Tests erneut aus.

**A. Python und Regressionen**

- Vollständige Pytestsuite
- Vollständige Unittestsuite
- Artwork-Regressionen
- EPG-Zuweisung und Quellenwechsel
- Vorschau und Abbrechen
- Verifizierter EPG-Speichervorgang
- Cold-Readback und Persistenz
- Kodi-Einstellungs- und Speicherfreigaben
- Sendergruppen und Mini-EPG

**B. Native Kodi-Tests**

- Kodi Linux 21.2
- Auflösung 1280 × 720
- Auflösung 1920 × 1080
- Sichtbare Hero- und Detailbilder
- Sichtbare Bildabruf- und Fehlerstatusmeldungen
- Quellenwahl und automatische Sendersuche
- Reversible EPG-Vorschau
- Speicherbutton und bestätigter Save
- Lesbarkeit sämtlicher Dialoge
- Keine abgeschnittenen Statusmeldungen
- BINGIE-Widget-Bestandsschutz

**C. Paket- und Repositoryprüfung**

- ZIP/CRC
- SHA256
- 17 Sprachkataloge
- Versionskonsistenz
- Keine Regression gegenüber .97
- Upgradepfad von .97 auf .98
- Schutz vorhandener EPG-Zuordnungen und Kodi-Einstellungen

### 5. Unabhängige QA-Agenten erneut einsetzen

Nutze die bereits eingerichteten projektlokalen Prüfagenten:

**`artwork_qa`**

Prüft die vollständige Bildpipeline vom Bildabruf bis zur tatsächlichen Kodi-Textur und die Statusanzeigen.

**`epg_mapping_qa`**

Prüft Quellenauswahl, Sendersuche, Vorschau, Abbrechen, Speichern, Persistenz und Dialogbedienbarkeit.

Beide Agenten sollen unabhängig voneinander denselben finalen Produktstand beurteilen.

Ihre Berichte und festgestellten Einschränkungen sind zu dokumentieren.

### 6. Freigabebedingungen

Eine Pilotfreigabe darf nur vorbereitet werden, wenn:

- Die vollständigen Unit- und Pytestsuiten erfolgreich sind.
- Alle relevanten nativen Tests erfolgreich sind.
- Das Installationspaket vollständig validiert wurde.
- Die unabhängigen QA-Agenten keine offenen Releaseblocker feststellen.
- Historische Versions- und Paketverträge weiterhin korrekt geprüft werden.
- Bestehende Kodi- und Nutzerdaten geschützt bleiben.

Sollten neue Fehler auftreten, diese gezielt beheben und die betroffenen Prüfungen wiederholen.

**Nicht das Testergebnis kosmetisch verbessern, sondern die tatsächlichen Fehlerursachen beseitigen.**

### 7. Pilot-Repository

Die neue Version soll später ausschließlich im **GS Media Pilot-Repository** erscheinen.

Vorgesehener Veröffentlichungsbereich:

`main/online-test/`

Folgende Bereiche dürfen nicht verändert werden:

- Reguläres XCMate-Repository
- NeoDark3-Repository
- GS Media Installer
- Andere Kodi-Add-ons
- Bestehende .96- und .97-Installationspakete
- Produktquellstand von `main`, außer den ausdrücklich vorgesehenen Pilot-Metadaten bei einer späteren separaten Veröffentlichung

**In diesem Auftrag zunächst keinen Merge und keine Veröffentlichung durchführen.**

Erst wenn die vollständige CI grün ist, das neue Paket reproduzierbar geprüft wurde und keine Releaseblocker mehr vorhanden sind, den Releasekandidaten als **PILOT_READY** melden.

Wenn eine Bedingung nicht erfüllt ist, den Status **RELEASE_BLOCKED** setzen und den konkreten Grund angeben.

### 8. Abschluss und Übergabe

Erstelle einen neuen Draft-Pull-Request mit:

- Version 0.1.29.98
- Exaktem Commit-SHA
- Vollständigen Testresultaten
- Ergebnissen beider QA-Agenten
- Downloadpfad des unveröffentlichten Review-ZIP
- SHA256-Prüfsumme
- Liste der behobenen Testfehler
- Verbleibenden Einschränkungen
- Klarem Status `PILOT_READY` oder `RELEASE_BLOCKED`

Dokumentiere die Ergebnisse im bestehenden GitHub-Projekt und verlinke PR #484.

**Keine automatische Veröffentlichung, keine Änderungen an produktiven Repositories und keine Android-Erfolgsmeldung ohne echten Gerätetest.**

Nach erfolgreichem Abschluss erfolgt die Pilot-Veröffentlichung in einem ausdrücklich getrennten Freigabeschritt.