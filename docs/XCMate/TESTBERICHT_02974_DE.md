# XCMate .74 – Testbericht (Arbeitsstand)

Dieser Bericht wird vor dem Draft-PR mit den endgültigen Laufresultaten und CI-Links ergänzt. Noch keine Gerätefreigabe, kein Merge und kein Release.

| Bereich | Nachweis / Status |
|---|---|
| Basis | aktuelles main `2e9e81c`, XCMate .73; bestehende .21-Installer-Veröffentlichung erhalten |
| Neue P0-Hosttests | LKG 24→7, echte Löschung/autorisiert leer, Quelle/Konto/Profil, 30s-Lease/Grace/unsicheres DNS, immutable Seiten/Parallelreader, Publikationssperre, 300s/Sendungsende/Rollover, Opt-outs, optionale Skinprüfung/Backup/Restore |
| Kumulative Tests | 3.051/3.051 PASS in 540,630 Sekunden auf dem .74-Kern; zusätzlich zwei Journal-/Quellen-Fehlerfälle PASS. Vollständiger Abschlusslauf für das finale Paket folgt. Keine entfernten Testmethoden/Skip-Verträge |
| PO | alle vorhandenen Kodi-PO-Kataloge validiert; neue Diagnosetexte DE/EN, bestehender Englisch-Fallback |
| Native Kodi/BINGIE | echte Controls/Pixel: 88 Live-Sender, 24 Film-/24 Serienquellen, Fremdwidgets, Fokus, echtes Mini-EPG und Guide, Details/Hero, PNG/JPEG über verifiziertes synthetisches HTTPS |
| Echter 60-Minuten-Lauf | 15 Minuten PASS (88/24/24 Items, 45 Workerzyklen, keine Workerfehler); 30/60 Minuten noch IN_PROGRESS. Reale monotone Zeit, kein Fast-forward; 15/30/60-Minuten-Screenshots, laufende Produktionsworker und injizierte Lesebudget-/Netzfehler. PR erst nach Abschluss |
| 720p | PASS lokal und in GitHub Actions; Originalauflösung bleibt im Screenshot erhalten; Koordinatenanalyse wird normalisiert |
| Messwerte | siehe Ursachenanalyse und `test-builds/02974/evidence/benchmark-*.json` |
| GitHub Actions | [.74-Lauf 41999154168](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41999154168): native 1080p/720p PASS; finale Paketprüfung wird nach letztem Guard-Commit erneut ausgeführt |
| Android/Kodi 21.2/21.3 ARM32 | ANDROID_NOT_TESTED |
| Privater TMDB-/TVmaze-Echtzugang | NOT_TESTED; in dieser Umgebung nur synthetische API-Antworten und echter isolierter HTTPS-Bildtransport |

## Reproduktion

```sh
python -m unittest discover -s tests -v
python tools/validate_kodi_po.py
python tools/package_xcmate71.py docs/XCMate/test-builds/02974
python tools/run_kodi_home74_contract.py --report-dir /tmp/native74 --idle-seconds 3600
python tools/run_kodi_home74_contract.py --report-dir /tmp/native74-720 --resolution 1280x720
python tools/benchmark_xcmate74.py --output /tmp/benchmark74.json
```

Hostabhängigkeiten wie CI: Python 3.12, Pillow, impacket 0.13.0, simpleeval 0.9.13; native Treiber zusätzlich Docker. Pinned BINGIE 2.2.3 wird gegen SHA256 geprüft. Nur wegwerfbare synthetische Kodi-Profile, keine Benutzer-/Box-Daten. Externe Helper und voller Add-on-Service sind im Renderingcontainer deaktiviert; die relevanten Produktionsworker für Snapshot, Artwork, EPG und Publikation werden im Dauerlauf ausdrücklich aufgerufen. Die bewusst gewählte Testprofil-Reserve beträgt 128 MiB; die Produktionsvoreinstellung 1 GiB bleibt unverändert. Ein eigener RAM-only-Test injiziert Reserveblockade und kontrolliert, dass Kodi dennoch die überprüfte URL direkt darstellt.

## Issue-Matrix

| Issue / Teil | Umsetzung | Geräteabnahme |
|---|---|---|
| #361 Home-Snapshot/Bild-Lease/EPG-Stabilität | implementiert; vollständige Gate-Ergebnisse vor PR ergänzen | ANDROID_NOT_TESTED |
| #361 Standardwidget-Auswahl | direkte drei Quellen, keine Pflicht-Slotverwaltung, alte URLs kompatibel | ANDROID_NOT_TESTED |
| #361 Fokus | optionaler SHA-geprüfter .74-Adapter, native Navigationsregeln, lokal gebundene Rahmen | ANDROID_NOT_TESTED, installierter privater Skin-SHA nicht verfügbar |
| #361 Eventbilder/Diagnose | bestehende gemeinsame Pipeline, Opt-ins, Helperbackoff, größere Guidevorschau | ANDROID_NOT_TESTED |
| #357–#359 | .73-Funktionen erhalten; keine themenfremde Erweiterung; frühere offene Quellen-/Übersetzungs-/Gerätetests bleiben offen | ANDROID_NOT_TESTED |

Die ersten Entwicklungsdurchläufe deckten alte Menü-/TTL-Testannahmen, einen unvollständigen synthetischen HEAD-Server und Pixelklassifikationsprobleme durch 720p-Resampling auf. Fehler wurden nicht als PASS gezählt. Finalbericht nennt die anschließend abgeschlossenen Läufe gesondert.

Der reale Dauerlauf verwendet den .74-Kern `68d7b71`. Eine spätere, separat geprüfte Ergänzung fängt ausschließlich `AttributeError` bei beschädigtem optionalen Referenzjournal ab; das ist kein verändertes Cache-/Renderingverfahren. Diese Korruptionspfade werden zusätzlich in Hosttests und das finale Paket erneut in CI geprüft.
