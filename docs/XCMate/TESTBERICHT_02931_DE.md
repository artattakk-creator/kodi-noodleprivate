# XCMate 0.1.29.31 – kumulativer Android-Teststand

Review: [Draft #154](https://github.com/artattakk-creator/kodi-noodleprivate/pull/154).
Basis main **6d3555a / .30**, geprüfter Quellstand
**0763cbd2b1d126e084c8e1eeeaafcbedb099e676**. Nachfolgende Commits ergänzen nur
Paket/Nachweise. Kein main-Merge, Release oder produktiver Index-/OTA-Publish.

## Installation

[**.31-ZIP**](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/test/xcmate-02931-android-cumulative/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.31.zip)
· [**SHA256**](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/test/xcmate-02931-android-cumulative/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.31.zip.sha256)
· [**kurze Android-Anleitung**](ANDROID_ABNAHME_02931_DE.md).

**2.360.279 Bytes / 251 Dateien**, Addon-ID plugin.video.xtreammate, Version .31.

```text
b94eff9a615f891bfb8517486cca6c02063e7bd1b95220e26414cec0d266723f
```

Nur dieses kumulative .31-ZIP installieren. Die Teil-PR-Artefakte prüfen jeweils
unabhängigen Quellcode auf .30-Basis und sind keine zusätzlichen .31-Versionen.
Manuell über das bestehende Profil installieren; keine Deinstallation/Resets.
Produktive .30 und ihr ZIP bleiben unverändert als Rückfallbasis.

## Was sich ändert

**[#152](https://github.com/artattakk-creator/kodi-noodleprivate/pull/152) / #140:**
Der alte Short-EPG-Scan ließ nach zwei Sekunden alle übrigen Sender aus. Ein
Worker-eigener Cursor scannt jetzt alle zulässigen Sender in endlichen Scheiben;
Teilzählungen mit + bis zum tatsächlichen Abschluss. Cache-only, keine HTTP-
Aufrufe oder EPG-Schreiboperation. Manuelle Mappings bleiben maßgeblich.
Nach Keyboard-OK bleibt Suchnavigation fokussiert. Alte Klicks/Keyboard-Reinit
lösen keinen unbeabsichtigten Player-/Landing-Wechsel aus; erst bewusste Navigation
zum Treffer wählt ab. Native Sichtbarkeitsverzögerung hält den gewünschten Fokus.
Privater, begrenzter Cursor endet mit der Suche, keine globale Credential-Historie.
Das repariert belegte Codelücken, beweist allein keine komplette Android-Ursache.

**[#153](https://github.com/artattakk-creator/kodi-noodleprivate/pull/153) / #135/#63:**
Untrusted-Job erklärt fehlende Freigabe und bietet Prüfung vor blindem Retry.
Standard bleibt gesperrt. Nur ein unabhängig anhand eigener Anbieterinformationen
bestätigtes Ziel bewusst portal-/source-/target-gebunden freigeben. Atomare Prüfung
verhindert Grant einer währenddessen geänderten Pending-Anfrage. Zweiter Dialog
kann nur diesen weiterhin fehlgeschlagenen Redirect-Job einreihen; andere,
abgebrochene oder noch gesperrte Jobs unverändert. Bestehender Widerruf bleibt.
Kein Auto-Allow, keine Aufweichung der unveränderten Redirect-/TLS-/SSRF-/DNS-/
Header-/Content-/Hash-/NoReplace-Schutzregeln.

**#136:** Expliziter kleiner Zieltest schreibt/liest/prüft SHA256 direkt am
konfigurierten lokalen/USB-/SMB2-Ziel und entfernt nur die bestätigte eigene neue
Nonce-Datei. Kein Providerabruf, Medienjob oder interner Ersatz. Bei unsicherem
Inode/Inhalt bleibt die Probe ggf. erhalten; keine Fremddateilöschung. Eigene
SMB-Stagingdatei wird nach Inodeprüfung entfernt. Anonyme DOWNLOAD_PHASE-Zähler
trennen Source-Redirect-Deny von Probe-/Stage-/Zielkopiefehlern. Kleine Probe ist
kein Ersatz für vollständigen Film/Folge oder native Direct-TS-Aufnahme.

## Tatsächliche Hostprüfung

**1046 automatisierte Tests PASS**, 0 Fehler/Failures/Skips, **121,657 s** auf
Linux x86_64/Python 3.12, keine Thread-Ausnahme. [Vollständiges Testprotokoll](TESTLOG_02931.txt)
(nur Zeilenend-Leerzeichen normalisiert), [maschineller Bericht](TESTERGEBNISSE_02931.json).

17 neue Tests: sechs Suche, elf Downloadablauf. Gezielte Suiten 36 bzw. 57 PASS.
Darunter späte Short-only-Treffer nach >2 s auf mehreren Sendern, Keyboard-/
langsamer Worker-Reinit, Focus-Lag, kein Auto-Player, bewusste Live-Auswahl,
Default-Deny, genauer Grant/Retry, Pending-Wechsel, Loopback weiter abgelehnt,
Widerruf, Source-/Target-Diagnose und tatsächliche lokale/signierte SMB2-Zielprobe
mit Fremddatei-/Inodeschutz. Bestehende Daten-/Player-/Guide-/Resume-/Staffelautoplay-,
Capture-/Poster-/Volume-/Pause-/Hash-/NoReplace-Regressionen bestehen.

Zusätzlich **acht echte Host-Transfers** über zwei HTTP-Server mit Redirect und
intern/native-USB-/staged-USB-Simulation bzw. echtem signierten SMB2-Server. Je Film
und Folge, vollständiger Hash und strenge FFmpeg-Dekodierung PASS; keine sensiblen
Header weitergegeben. [Transferbericht](DOWNLOAD_HOSTTRANSFER_02931.json).
Loopback-Ausnahme nur im kontrollierten Fixture-Patch, nicht im Addon.
Hostabhängigkeit impacket==0.13.0 ist nicht Teil des Kodi-ZIP.

PO-Validator: DE/EN jeweils **783** gültige, gleiche Kontexte. CRC, sichere und
eindeutige ZIP-Pfade, keine Symlinks/Profil-/DB-/Log-/Testdateien, Python-AST,
bytegleiche Addon-Quellen und deterministischer Neuaufbau PASS. Unveränderter
vendor-SMB-Docstring hat unter Python 3.12 weiterhin eine SyntaxWarning; kein
neuer PO-/Runtimefehler. SHA256 oben bezeichnet das Addon-ZIP selbst.

## Diff-/Daten- und Freigabegrenzen

- Suche: search_data/media_search und gezielte Re-Init-/Focus-Hooks in media_window,
  numerische Diagnose-Allowlist. Delta Q1–Q3, alte Player-/Guide-Handoffs erhalten.
- Download: Trust-UI/atomarer Pending-Grant, Manager, Worker-Phasen, neues kleines
  Zieltestmodul und Menüroute, 350xx-PO. Delta Z1/Z2 und D1–D5; echter vollständiger
  Film/Folge nach Source-Freigabe nötig. Bestehende Grants/Settings/DB-Schemata bleiben.
- Paket: .31-Manifest/Versionsasserts, Service-Build nur numerisch 31, Changelog.
  CI vergleicht bereitgestelltes Paket bei kumulativen Testbranches versionsbezogen.

**30 geschützte Quellmodule**, Originalicon/Splash und **98 Original-Themebilder**,
Produktivindex und .30-ZIP bytegleich. 62 fremde lokale WIP-Dateien unverändert.
[Schutzprüfung](SCHUTZPRUEFUNG_02931.json). Keine Portal-/Gruppen-/EPG-/Favoriten-/
Resume-/Gesehen-/Bild-/Joblöschung, keine globale Keymap, Profil-/Medien-DB-Migration.
Service-/Portal-/Cache-/Thread-Lifecycle nicht geändert; kein erneuter pauschaler
Vierstundentest. Alte .30-PASS, besonders MEM1/MEM2, bleiben bestätigte Baseline.

**Neue .31-Android-Gates NOT_TESTED**, bis der Nutzer wirklich ausführt. Historische
.30-Werte bleiben **12 PASS /15 FAIL /1 BLOCKED /1 NOT_TESTED**. Kein behaupteter
physischer USB-/Android-SMB-/Providerfilm-/Offline-/Sendungssuch-PASS durch Host-CI.
Recorder #126 und Poster #111 bleiben bekannte offene Reparaturen. #151/Bildsuche,
Icon-Rail, Magazin-EPG, Catch-up und Wizard werden nicht als umgesetzt behauptet.
Nur einmal kurzer Smoke und die verlinkten Delta-Prüfungen, keine alte Vollmatrix.
Keine privaten Rohlogs hochgeladen; Merge/Release erst nach ausdrücklicher Freigabe.
