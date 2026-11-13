# XCMate 0.1.29.93 – Testbericht

13.11.2026 · Master #454 · [Draft-PR #455](https://github.com/artattakk-creator/kodi-noodleprivate/pull/455).
Basis: main .92 `3e1d6f87787baa95d24cc4e7c83c24914db31364`.
Geprüfter Quell-/Paketstand: `0b842c16edf12647a3d012b06c478b4929ca99a3`.
**Kein Merge, keine Veröffentlichung, keine Änderung an Android-Boxen. Der Master ist wegen offener Geräte-P0s nicht vollständig abgenommen.**

## Paket und Bestandsschutz

`plugin.video.xtreammate-0.1.29.93.zip`: **4.711.998 Bytes, 876 Mitglieder**.
SHA256: `48e0822827c2a8e8a854a812cbac0d0fb3407f6f6b9a5c3c2c2213f20fe77a95`.
Alle Mitglieder entsprechen bytegenau der aktuellen Quelle; CRC, Manifest, Pfade und Prüfsummendatei geprüft. Alle früheren .93-Entwicklungsprüfsummen sind überholt.

Die Pilot-Dateien liegen ausschließlich als nicht veröffentlichter Vorschlag unter `test-builds/02993/pilot-proposal`. Regulärer Katalog, Pilot-Katalog, NeoDark3, Installer .5.26 und .90-Fallback sind unverändert. .90-SHA256: `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`.

## Automatisierte Nachweise

| Prüfung | Ergebnis / Geltungsbereich |
|---|---|
| Neue P0-/Paketprüfungen | 24 PASS in 4,164 s; davon 20 P0- und vier Release93-Fälle. |
| Lokaler Gesamtlauf | 3.938 PASS in 781,900 s auf dem Stand vor der abschließenden opaken UI-Textur und deren zusätzlichem Test. Kein Nachweis für den exakten letzten Paketstand. |
| Unveränderliche vollständige GitHub-CI | [Lauf 43504728614](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504728614), **PASS: 3.939 Tests in 908,270 s**, 11 Branding-Tests, 17 PO-Kataloge, ZIP bytegleich reproduziert, alle eingefrorenen Kanäle unverändert. [Beleg](reports02993/host-ci93.json). |
| Exakte ZIP, natives Kodi 720p/1080p | [Lauf 43504728596](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504728596), **PASS in 720p und 1080p**, exakt SHA48e…77a95, 875 unveränderte Nichtmanifest-Dateien; Original-SkinShortcuts, sechs Reihen, drei kalte Neustarts, 20 × 137 Sender ohne EPG, nativer Speicher-Dialog mit echten Pixeln. Belege unter reports02993. |
| Bestehender Home-/Medien-Dauerlauf | [Lauf 43504729339](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504729339), einschließlich 30-minütiger DB-Pause bei 720p. 1080p und separater 60-Zyklen-Medienlauf PASS; 720p-Dauerlauf mit 30-minütiger DB-Pause noch IN_PROGRESS. Kein Dauerlauf-PASS vor dessen Abschluss. |
| Physische Android-Tests | **Alle 16 ANDROID_NOT_TESTED**. Linux-Kodi **21.2 Debian 2:21.2+dfsg-4**, synthetische Streams und Fehler-Injektion ersetzen keine RK3528-Abnahme. |

Die Tests decken reale SQLite-Backups, Hash-/Recovery-/Journal-/Abbruch-/Readback-Verhalten, offene Dateien, defekte Receipts, lokale XMLTV-Benutzerdateien, fortsetzbare Inventur, Rechte/Symlinks, Eventbindung und Quellendeaktivierung ab. Zusätzlich: einmalige nachgewiesene spätere FIFO-Quittung ohne zweiten Stop, 120 simulierte Zyklen, temporär unvollständiger Startsender sowie gezielte Gruppenlesung mit 137 Sendern ohne EPG. Kein vorhandener Test entfernt oder zusätzlicher Skip eingeführt. Historische exakte .92-Quell-/Paketverträge bleiben mit ihrer damaligen Basis reproduzierbar; die neue .93-Differenz wird separat exakt begrenzt.

Der separate native Linux-Medienlauf besteht **60 reale Dekodier-/Stop-/ACK-Zyklen**, je 20 Live, Film und Episode, mit genau einem Stop und Fortschrittssicherung. [Beleg](reports02993/native-media77.json). Android-Vollbild-/Ursprungsrückkehr und Rockchip-MediaCodec sind damit ausdrücklich nicht geprüft.

## Ursachen und verbleibende Grenzen

| Bereich | Bestätigte Korrektur | Offen |
|---|---|---|
| Player | Session-Diagnose vereinheitlicht. Verlorene erste Stop-Quittung darf nur durch einen tatsächlich ausgeführten späteren FIFO-Probe ersetzt werden. Kein zweiter Stop, keine zusätzliche Player-Abfrage oder Timeout-Verlängerung. | **Echte Rockchip-Decoder-/Mainqueue-Blockade nicht als behoben erklärt.** Ohne Queue-Fortschritt weiterhin kontrolliert blockiert. Eigenständiger Prozessabbruch benötigt getrennte Android-Belege. |
| EPG-Speicher | Eng nachgewiesene alte Guide-Recovery-Sätze journalisiert entfernen; letzten gültigen Satz und aktive DB schützen. Raw-Feeds im aktuellen Pfad RAM-only, Raw-Delete korrekt 0 Bytes. | Unbewiesene alte XMLTV-Dateien werden nicht gelöscht. Große Legacy-Quell-/DB-Konsolidierung und gesamter Orphan-GC offen. |
| Speicherdiagnose | Eigenes Fenster statt Plot/rohem JSON, lesbare Größen/Volumes/Reserve, Teilmessung/Rechtefehler und fortsetzbare Inventur. | Tatsächliche Android-Volumes, Quota und interner/USB-Platzgewinn fehlen. Bestehende verifizierte USB-Migration nicht umgeschrieben. |
| Galileo/XMLTV | Die installierte BINGIE-Skin machte versehentlich auch kleine Detailbilder von Hero-Mindestgrößen abhängig. Explizite Detailanfrage getrennt; exakter Event-/Quell-/Revisionscache, einmaliger Detail-Retry, bewusste Deaktivierung erhalten. | Sichtbare Android-Textur und persistente TMDB-/TVMaze-Auswahl nach Reboot getrennt prüfen. |
| Startsender/Mini-EPG | Vorübergehend fehlender Index löscht keine Startsender-Konfiguration. Aktivierte Gruppen gezielt lokal/asynchron lesen; Pending und wirklich leere Gruppe unterscheiden. | Echter Android-IR-/Busy-/Neustarttest offen. |

Der vom Nutzer korrigierte 20:14-Vorfall war ein Freeze nach Back/Stop mit anschließend **vom Nutzer gedrücktem Android-HOME**. Er ist kein Nachweis eines selbstständigen Kodi-Absturzes. Der frühere ungeordnete Neustart bleibt als separater Fall offen.

## Physisch gemessene Speicherfreigabe

[Maschinenlesbarer Hostbeleg](reports02993/storage-before-after.json): reale synthetische Linux-Dateien/SQLite, gleiches Device 34, **4.292.644.864 → 4.301.070.336 verfügbare Bytes**, netto **+8.425.472 Bytes**. Ein alter Satz mit 8.425.687 logischen Bytes entfernt; Keeper mit 2.049 Events und quick_check erhalten; Benutzerquelle unverändert. Intent und Result tatsächlich persistent/fsync gespeichert und kalt nachgelesen. Differenz durch Dateisystemblöcke und eigenes Journal. Dauer 33,082 ms. **Keine Android-Zahl und kein Raw-XML-Platzgewinn.**

## Visuelle Gegenprüfung statt bloßer Control-Meldung

Der erste native 720p-Lauf auf `1d3df02b` bestand Titel/Text/Back, aber seine betrachtete Originalaufnahme zeigte einen transparenten Hintergrund: skinrelatives `white.png` fehlte. Deshalb war das **kein visueller Speicher-PASS**. [Fehlerbeleg](reports02993/native-storage-before.json), [Originalaufnahme](reports02993/storage93-before-720.png).

Der aktuelle Stand bündelt drei eigene vollständig opake PNG-Texturen und verwendet absolute Add-on-Pfade. Der native Test verlangt tatsächliche Panel-/Fokus-/Button-Pixel zusätzlich zu Titel/Text/Back. Das Debugoverlay wird ausschließlich im Wegwerf-Testprofil für die Aufnahme abgeschaltet und danach wiederhergestellt. Keine Skin- oder Box-Einstellung geändert. Beide aktuellen Originalaufnahmen wurden betrachtet: [720p](reports02993/storage93-after-720.png), [1080p](reports02993/storage93-after-1080.png). Die opaken Panel-, Fokus- und Button-Pixel sowie Back wurden in beiden Auflösungen verifiziert. Englisches synthetisches Wegwerfprofil, keine Android-Aufnahme. [720p-Paketbeleg](reports02993/native720-package-proof91.json), [1080p-Paketbeleg](reports02993/native1080-package-proof91.json).

## Zusätzlicher historischer CI-Fehler

[Publish-Workflow 43504728829](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504728829): aktueller vollständiger Hostjob und nativer Live-Transport bestanden, Veröffentlichung SKIPPED. Der getrennte Job `kodi-helper57-transport` scheiterte im ausdrücklich archivierten .74-Home64-Harness: Docker-Container bereits beendet, Probe Exit137, Diagnose im gestoppten Container ebenfalls nicht möglich. **Keine bewiesene OOM-Ursache und kein pauschaler .93-Codefehlernachweis.** Ausschließlich diesen fehlgeschlagenen Job einmal erneut gestartet; Ergebnis noch offen, gesamter Workflow deshalb nicht als grün erklärt. Keine Tests oder Schwellen abgeschwächt.

## Frühere Fehlversuche

Zwei lokale breite Läufe liefen noch während der Fertigstellung von Quelle, exakter Delta-Fixture und PO-Dateien: 3.933 Fälle mit 89 FAIL/3 ERROR sowie 3.935 Fälle mit 38 FAIL/1 ERROR. Diese sind keine gültigen finalen PASS-Belege. Ursachen: ältere importierte Test-Caches, parallele Fixture-/PO-Fertigstellung, tatsächlicher Opt-out-/Dummy-Gruppenfehler sowie Workspace-ENOSPC im großen HTTP-Test. Die echten Fehler wurden korrigiert. Nur vier eigene saubere abgeschlossene lokale Worktrees wurden entfernt; Branches, Historie, Pakete und sämtliche Android-Daten blieben erhalten. Danach war der lokale 3.938-Testlauf grün; die finale CI nutzt einen unveränderlichen Checkout.

## Freigabe

[Issue-Matrix](ISSUE_MATRIX_02993_DE.md), [Android-Plan mit 16 offenen Gates](ANDROID_ABNAHME_02993_DE.md), [manuelles Testupdate](INSTALLATION_RC_02993_DE.md), [technische Übergabe](CODEX_UEBERGABE_02993_ANDROID_PLAYER_EPG_CLEANUP_2026-11-13_DE.md).

**Draft zur Prüfung, keine vollständige P0-Abnahme und keine Merge-/Release-Empfehlung.** P1 #435/#450/#427 bleibt getrennt. Keine privaten Rohlogs oder echten Zugangsdaten im Bericht.
