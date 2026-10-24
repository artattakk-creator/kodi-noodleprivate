# XCMate 0.1.29.30 – fertiger kumulativer Android-Testkandidat

**Review-Draft:** [#149](https://github.com/artattakk-creator/kodi-noodleprivate/pull/149).
**Quellbasis:** main b7ff441 (Produktivversion .29; neue Delta-Testpolitik enthalten).
**Geprüfter Addon-Code:** 942fef59cae8d2e3721343396706c8cf812c39c1.
**Finaler Test-/Workflow-Quellstand:** 0b12bc33ec8d7f28c666e52a26622715aa82c224.
Nachfolgende Commits ergänzen Testpaket/Nachweise/Dokumentation und einen reinen
CI-Vergleich des mitgelieferten ZIP mit dem Neuaufbau; kein weiterer Addon-Diff.
Kein main-Merge, Release oder Updatekanal-Publish. Der produktive Index und das
bestehende .29-ZIP bleiben bytegleich. Kein vollständiger RC: #43/#127 bleiben offen.

## Installierbare Datei

[Test-ZIP herunterladen](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/test/xcmate-02930-android-cumulative/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.30.zip)
· [SHA256-Datei](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/test/xcmate-02930-android-cumulative/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.30.zip.sha256).

Dateiname: `plugin.video.xtreammate-0.1.29.30.zip` · **2.355.571 Bytes**, 250 Dateien.

```text
0ab5331d2ea84abb587fd59d5ff719b5602fdc2927ffe9dc478d763921153b81
```

Nur dieses kumulative .30-ZIP für Android installieren. Automatische Artefakte
der einzelnen Quell-Drafts enthalten deren unabhängige .29-Basis und sind keine
weiteren .30-Testversionen. Normales manuelles Update über bestehendes Profil;
keine Deinstallation/Resets. [Ausführbare Android-Anleitung und Ergebnisblock](ANDROID_ABNAHME_02930_DE.md).

## Implementierung und getrennte Reviews

| Draft / Issue | Änderung | Vollständige Quell-PR-CI |
|---|---|---|
| [#144](https://github.com/artattakk-creator/kodi-noodleprivate/pull/144) / #141 | Versionsgeprüfte Portal-Snapshots, defensive Kopien, OOM-Backoff; optionale Vorbereitung entprellt; kontrollierte Service-/IO-Abbrüche; opt-in 4-/8-h ARM32-Messung | [1009 PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40080332199) |
| [#145](https://github.com/artattakk-creator/kodi-noodleprivate/pull/145) / #136 | Getrennte Quellenpicker/Backend-Marker, Kodi-SMB-Liste, USB-Mounts, exklusive private .part-Zwischenablage ohne Hardlinkpflicht | [1008 PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40082012443) |
| [#146](https://github.com/artattakk-creator/kodi-noodleprivate/pull/146) / #140 | Gültiges cache-only Jetzt-Short-EPG, begrenzte relevante Alias-/DB-Abfragen, anonyme Abdeckungs-/Trefferdiagnose | [1005 PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40080760988) |
| [#148](https://github.com/artattakk-creator/kodi-noodleprivate/pull/148) / #122 | Bytegleiches originales Space-Motiv lokal im Lightweight-Skin; stabile Landing-/Suchhintergründe | [1003 PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40081044333) |
| [#147](https://github.com/artattakk-creator/kodi-noodleprivate/pull/147) / #142 | Ungültiges PO-Unicode-Escape durch UTF-8 ersetzt, Gettext-Validator und CI-Schritt | [1004 PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40080768386) |

Alle fünf Drafts offen, kein Merge. Supersedierte rote Läufe betrafen die alte
Picker-Testbedienung bzw. alte Neutral-Hintergrund-Erwartungen; deren beabsichtigte
Verhaltensprüfungen wurden an die neue Quellenwahl/den Original-Splash angepasst.
Keine Schutz-Hashes oder Player-Regressionen aufgeweicht. Ein späterer
Kollisions-Stresslauf deckte zusätzlich eine Host-Server-Race auf; siehe unten.
Quell-CI und Fixture-Nachtest siehe
[CI-Provenienz](CI_02930_QUELLPRs.json).

## Vollständige kumulative Hostprüfung

**1029 Tests PASS, 0 Fehler/Failures/Skips, 115,845 s** unter Python 3.12/Linux x86_64.
Keine Thread-Ausnahme. Hostabhängigkeit impacket==0.13.0 für reale SMB2-Wire-Tests;
nicht Teil des Addons. [Vollständiges Testprotokoll (nur Zeilenend-Leerzeichen normalisiert)](TESTLOG_02930.txt) und
[maschineller Paket-/Testbericht](TESTERGEBNISSE_02930.json).

- 20.000 unveränderte Portalaufrufe → exakt ein JSON-Read. Versionsänderung,
  gleichgroße atomare Ersetzung, Writer-/Parallelleser, entkoppelte Daten und
  OOM-Backoff/Recovery geprüft. Prep-Arbeit wiederholt sich nicht je schnellem Job.
- Stop weckt registrierte Socket-Reads; IO-Eigentümer schließen eigene Deskriptoren.
  Autoplay-/Vordergrund-Deadlines unverändert. Betriebssystem-DNS/FS-IO kann trotzdem
  länger blockieren; kein versprochener harter Fünf-Sekunden-Stop auf jeder Box.
- Quellenwahl/Abbruch und getrennte Ziele, reale signierte SMB2-Verbindung mit
  erzwungenem Native-LINK:38 nur in der Stage; Datei-fsync bleibt Pflicht.
  Vorhandene Resume-/Disconnect-/Hash-/No-Replace-/Volume-Identitätsfälle bestehen.
- Short-only/future-only/manuelles Mapping und >50.000 irrelevante Jetzt-Sendungen
  reproduziert. Keine HTTP-Abfrage in der Suche; keine privaten Diagnosetexte.
- Original-Splash/Originalicon, Core-/Premium-/Fokus-/Fanart-Regressionen bestehen.
  DE/EN jeweils **773** gültige identische PO-Kontexte im kumulativen Paket.
- Bestehende Such-/Live-Handoff-/IR-/EPG-/Autoplay-/Resume-/Profil- und
  Aufnahme-/Poster-Retry-Regressionstests bestehen. CI ist kein Android-PASS.

Getrennt vom Unittest-Lauf: **8 echte Host-Transfers** über zwei HTTP-Server mit
Cross-Origin-Redirect, internen/native- und staged-USB-Simulationen und echtem
signiertem SMB2-Server. Je Film/Folge, 404.305 Bytes, identischer SHA256 und strenge
FFmpeg-Dekodierung PASS; keine Authorization/Cookie/Provider-Key-Weitergabe.
[Transferbericht](DOWNLOAD_HOSTTRANSFER_02930.json). Die Loopback-DNS-Ausnahme ist
nur Fixture-Patch; produktive SSRF-/TLS-/Redirect-Schutzregeln bleiben bestehen.
Keine echten Providerstreams/Privatserver benutzt. USB hier simuliert.

Ein weiterer GitHub-Lauf fand eine **Race im Host-Testserver impacket 0.13.0**:
SMB2Create verwendete exists() + O_CREAT ohne O_EXCL. Die Fixture serialisiert
nun ausschließlich CREATE-Handler, um die vorgeschriebene atomare FILE_CREATE-
Semantik abzubilden. Der signierte Client und seine FILE_CREATE-Anforderung bleiben
unverändert; keine Produktiv-/os.open-Patches, keine abgeschwächte Assertion.
Zwölf synchronisierte Runden mit je fünf Clients verlangen genau einen Erfolg
und vier TARGET_EXISTS bei korrektem Dateiinhalt. Gezielter Stresslauf, kompletter
1029-Test-Hostlauf und acht Transfers wurden damit erneut erfolgreich ausgeführt.
Das Addon-ZIP bleibt in jedem Byte gleich. Finale kumulative [GitHub-CI: 1029 PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40082027484)
in 190.384 s, keine Thread-Ausnahme. Neuaufbau und committed Review-ZIP
bytegleich geprüft; Publish-Schritt SKIPPED. [CI-Nachweis](CI_02930_KUMULATIV.json).

Paketprüfung: CRC, eindeutige/sichere ZIP-Pfade, keine Symlinks/Profile/DBs/Logs,
250 source-bytegleiche Dateien, Python-AST, Manifest, deterministischer Neuaufbau
und SHA256 PASS. Ein unveränderter vendorter SMB-Docstring erzeugt unter Python
3.12 eine SyntaxWarning zu einem Backslash; das betrifft keine PO-Datei und ist
kein neuer Laufzeitfehler. Vendorkopie unverändert.

Reproduktion aus einem frischen separaten Checkout des Quellstands:

```sh
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0'
python tools/build_repository.py
python tools/validate_kodi_po.py
python -m compileall -q src
for f in tests/test_addon.py tests/test_site.py tests/test_providers.py; do
  sed -i "s@'..', 'plugin.video.noodleprivate'@'..', 'src', 'plugin.video.noodleprivate'@g" "$f"
done
python -m unittest discover -s tests -v
```

Der Build erzeugt in diesem Checkout auch Indizes; diese nur im Scratch-Checkout
prüfen, niemals ungefragt in main oder den produktiven Updatekanal übernehmen.

## Diff-basierte Risiken und gezielte Android-Gates

| Bereich | Tatsächlich betroffene Pfade / gemeinsame Abhängigkeiten | Zusätzlich zu S1–S5 |
|---|---|---|
| A | portals/portal_snapshot/profile_transaction, app_services/service_runtime/stability_monitor, media_art, network_io/utils, download_redirect/download_smb/download_worker, Wartungsroute/348xx-PO | D-MEM1/2; gemeinsame IO zusätzlich bei Download, Aufnahme und Poster-Retry beobachten |
| B | storage_sources/storage_diagnostics, download_target_ui/download_targets, Aufnahmeordner-Aktion home_menu, 349xx-/Ordner-PO | D-ST1–5, D-DL1–4, D-REC1–4 |
| C | search_data, Diagnose-Allowlist live_diagnostics, Statusanzeige media_search | D-EPG1–3 (A03), keine pauschale tiefe Wiederholung aller neun alten PASS |
| D | home_menu, Hintergrund-Hooks media_window/theme_render, appearance-Cachekennung, Media-XML und eine lokale JPG | D-UI1–4, Lesbarkeit/Fokus; kein ganzer neuer Autoplay-Lauf allein für den Splash |
| E | DE/EN-PO, Hostvalidator/CI | D-I18N1; kein zusätzlicher SMB-Transfer nur für Sprache |
| Paket | addon.xml .30, Service-Build 30, Changelog/Versionsasserts, neuer ZIP-Name | Installiertes .30-Manifest, S1–S5 |

Keine Portal-/EPG-/Medien-DB-Migration, keine Keymapänderung. Nur neue private
Messdateien, kein Lösch-/Resetpfad. Gemeinsame Speicher-/IO-Risiken sind in obigen
Delta-Gates enthalten; keine automatische breit angelegte Regression allein
wegen eines neuen Versionsnamens.

## Grenzen / offene Abnahme

**Alle echten .30-Android-Gates zunächst NOT_TESTED.** Insbesondere mehrstündiger
ARM32-RSS/PSS-Verlauf, Service-Upgrade, physisches USB, reale Android-SMB-Quelle,
vollständiger echter Providerfilm/Folge, Kodi-Wiedergabe/Offline, Direct-TS und
Poster-Retry sind ohne Gerät nicht als PASS behauptet. .28-MemoryErrors und .29-
LINK:38-Befunde sind gesichert, die alleinige Leakursache und ein Download-SMB-
Fehler daraus nicht bewiesen. Native Aufnahmeziele müssen weiterhin ihre sichere
Publish-Probe bestehen; Download-Staging ist keine pauschale Capture-Freigabe.

Historische .29-Ergebnisse unverändert **12 PASS / 16 FAIL / 0 NOT_TESTED**.
Originalicon und alle 98 Originalbilder bytegleich; geschützte Player-/Autoplay-/
Guide-Übergaben und Produktivindex unverändert. Lokale fremde WIP-Dateien 35+27
unverändert. [Schutzprüfung](SCHUTZPRUEFUNG_02930.json). Keine privaten Rohlogs
hochgeladen. Offene #43/#127 und weitere Backlog-Funktionen gelten nicht als erledigt.

Erst echte Android-Abnahme und ausdrückliche Freigabe erlauben eine spätere
Veröffentlichung. Dieser Draft führt sie nicht aus.
