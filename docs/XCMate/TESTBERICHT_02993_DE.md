# XCMate 0.1.29.93 – Testbericht

13.11.2026 · Master #454 · [Draft-PR #455](https://github.com/artattakk-creator/kodi-noodleprivate/pull/455).
Basis: main .92 `3e1d6f87787baa95d24cc4e7c83c24914db31364`.
Add-on-/ZIP-Stand: `0b842c16edf12647a3d012b06c478b4929ca99a3`.
Aktueller geprüfter Test-Harness: `86462cb1f4845bf4d80fcd1c111f478a59079be7`; Add-on-Dateien und ZIP dazwischen unverändert.
**Kein Merge, keine Veröffentlichung, keine Änderung an Android-Boxen. Master wegen offener Geräte-P0s nicht vollständig abgenommen.**

## Aktueller Teststand

| Prüfung | Ergebnis und Grenze |
|---|---|
| Vollständige aktuelle [CI 43511300880](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43511300880) | **3.940 PASS in 936,787 s**, zusätzlich 11 Branding-Tests und 17 PO-Kataloge gültig. ZIP kanonisch bytegleich reproduziert, eingefrorene Veröffentlichungskanäle unverändert. [Maschinenbeleg](reports02993/host-ci93-final.json). |
| Neue P0-/Paket-/Harness-Prüfungen | 31 PASS in 4,487 s; Teilmenge der Gesamtsuite, nicht zusätzlich zu 3.940 zählen. Davon 20 P0-Tests. |
| Exaktes ZIP, natives Kodi 21.2/Linux, [720p und 1080p](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504728596) | **PASS**. 875 installierte Nichtmanifest-Dateien bytegleich, Fixture-Manifest/Service/Plugin-Einstieg ausdrücklich für den synthetischen Test angepasst. Original-SkinShortcuts, sechs Reihen, echte Spinner-/Coverpixel, IR/Klickziele und drei kalte Neustarts. |
| Gruppen im Teilkatalog | **PASS in beiden Auflösungen**: GUI beginnt mit 137 Sendern, SQLite enthält 20 × 137. Alle Gruppen ohne EPG erreichbar, bis Index 136 blättern, 20 echte native Senderstarts unter gehaltenem WAL-Writer. [720p](reports02993/native720-groups90.json), [1080p](reports02993/native1080-groups90.json). |
| Speicherfenster | **PASS in beiden Auflösungen**: eigener Titel, Teilmessung gekennzeichnet, kein rohes JSON als Standard, tatsächliche Panel-/Button-/Fokus-Pixel, Back. Originalaufnahmen unten. |
| Kumulative [Home-/Medienprüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504729339) | **PASS in 720p/1080p**. Vollständige 1.800,89-s-DB-Pause bei 720p: ein Worker, keine ungefangenen Fehler, Wiederaufnahme desselben Workers. [720p](reports02993/home720-home75.json), [1080p](reports02993/home1080-result.json). |
| Reale Linux-Dekodier-/Stop-/ACK-Zyklen | **60 PASS**, je 20 Live/Film/Episode, genau ein Stop und Fortschrittssicherung. [Beleg](reports02993/native-media77.json). Android-Vollbild-/Ursprungsrückkehr und Rockchip-MediaCodec damit nicht geprüft. |
| Film-Detailstart und Rückkehr | **PASS**: echte Video-/Audiospuren, native Stop-ACK und Rückkehr. Synthetischer 1080p-Fall 3.544 ms. [Beleg](reports02993/home1080-vod80.json). |
| Vollständiger Bild-/Cold-Gegenlauf [43511295707](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43511295707) | **PASS in beiden Auflösungen**: volle 900 s, 20 Fokuswechsel, 88 persistente Logos, fünf Jetzt/Danach-Einträge, keine erneuten geprüften Logo-HTTPs/Manifestcommits, drei kalte Neustarts; Zuordnung 9003 bleibt erhalten. [720p](reports02993/retention90-final720.json), [1080p](reports02993/retention90-final1080.json). |
| Physische Android-Tests | **Alle 16 ANDROID_NOT_TESTED**. Native Tests: Kodi 21.2 Debian `2:21.2+dfsg-4`, Linux x86-64, synthetische Daten/Streams. Keine RK3528- oder Kodi-21.3-Abnahme. |

Die Tests decken echte SQLite-Backups, Hash-/Recovery-/Journal-/Abbruch-/Readback-Verhalten, offene Dateien, defekte Receipts, lokale XMLTV-Benutzerdateien, fortsetzbare Inventur, Rechte/Symlinks, Eventbindung und Quellendeaktivierung ab. Zusätzlich: verlorene/späte Stop-ACK ohne zweiten Stop, 120 simulierte Zyklen und temporär fehlender Startsender. Kein alter Test entfernt oder zusätzlicher Skip eingeführt. Historische exakte .92-Verträge werden auf ihrer damaligen Basis reproduziert; die .93-Differenz wird separat exakt begrenzt.

## Paket und Bestandsschutz

[Installierbares ZIP](test-builds/02993/plugin.video.xtreammate-0.1.29.93.zip): **4.711.998 Bytes, 876 Mitglieder**.
SHA256: `48e0822827c2a8e8a854a812cbac0d0fb3407f6f6b9a5c3c2c2213f20fe77a95`.
CRC, Manifest, sichere Pfade, Prüfsummendatei und alle Quellbytes geprüft. [720p-Paketbeleg](reports02993/native720-package-proof91.json), [1080p-Paketbeleg](reports02993/native1080-package-proof91.json). Frühere .93-Prüfsummen überholt.

Pilot-Dateien nur als nicht veröffentlichter Vorschlag unter `test-builds/02993/pilot-proposal`. Regulärer Katalog, Pilot, NeoDark3, Installer .5.26 und .90-Fallback unverändert. .90-SHA256: `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`. Keine Profile, Quellen, Token, Favoriten oder Widgetpfade zurückgesetzt.

## Ursachen und verbleibende Grenzen

| Bereich | Korrektur | Offen |
|---|---|---|
| Player | Session-Korrelation vereinheitlicht. Verlorene erste Stop-Quittung nur durch tatsächlich ausgeführten späteren FIFO-Probe ersetzen. Kein zweiter Stop, zusätzliche Player-Abfrage, Stop-Thread oder verlängerter Player-Timeout. | **Echte Rockchip-Decoder-/Mainqueue-Blockade nicht als behoben erklärt.** Ohne Queue-Fortschritt kein erfundener Erfolg. Eigenständiger Prozessabbruch benötigt getrennte Android-Belege. |
| EPG-Speicher | Eng verifizierte alte Recovery-Sätze journalisiert entfernen; letzten gültigen Satz, aktive DB und Quellen schützen. Raw-Feeds RAM-only, Raw-Delete korrekt 0 Bytes. | Unbewiesene alte XMLTV-Dateien werden nicht gelöscht. Große Legacy-Quell-/DB-Konsolidierung und vollständiger Orphan-GC offen. |
| Speicherdiagnose | Eigenes lesbares Fenster, Größen/Volumes/Reserve, Teilmessung/Rechtefehler und fortsetzbare Inventur. | Tatsächliche Android-Volumes/Quota, interner und USB-Platzgewinn fehlen. Verifizierte bestehende USB-Migration nicht umgeschrieben. |
| Galileo/XMLTV | Installierter BINGIE machte versehentlich auch Detailbilder von Hero-Mindestgrößen abhängig. Detail-Kontext getrennt, exakter Event-/Quell-/Revisionscache und gezielter Retry; bewusste Deaktivierung erhalten. | Sichtbare Android-Textur und persistente TMDB-/TVMaze-Auswahl nach Reboot getrennt prüfen. |
| Startsender/Mini-EPG | Teilindex löscht keine Startsender-Konfiguration. Aktivierte Gruppen gezielt lokal/asynchron lesen; Pending nicht als leer darstellen. | Echter Android-IR-/Busy-/Neustarttest offen. |

Der vom Nutzer korrigierte 20:14-Vorfall war ein Freeze nach Back/Stop mit anschließend **vom Nutzer gedrücktem Android-HOME**. Kein Nachweis eines selbstständigen Kodi-Absturzes. Früherer ungeordneter Neustart bleibt separat offen.

## Physisch gemessene Speicherfreigabe

[Hostbeleg](reports02993/storage-before-after.json): reale synthetische Linux-Dateien/SQLite, gleiches Device 34, **4.292.644.864 → 4.301.070.336 verfügbare Bytes**, netto **+8.425.472 Bytes**. Alter Satz mit 8.425.687 logischen Bytes entfernt; Keeper mit 2.049 Events/quick_check und Benutzerquelle erhalten. Intent/Result persistent und fsync gespeichert, kalt nachgelesen. Differenz durch Dateisystemblöcke und eigenes Journal. Dauer 33,082 ms. **Keine Android-Zahl und kein Raw-XML-Platzgewinn.**

## Visuelle Gegenprüfung

Der erste native 720p-Lauf auf `1d3df02b` bestand Titel/Text/Back, aber die betrachtete Aufnahme zeigte einen transparenten Hintergrund: skinrelatives `white.png` fehlte. **Kein visueller PASS** aus diesen Control-Gates. [Fehlerbeleg](reports02993/native-storage-before.json), [Originalaufnahme](reports02993/storage93-before-720.png).

Korrektur: drei eigene opake PNGs mit absoluten Add-on-Pfaden. Aktuelle Originalaufnahmen betrachtet: [720p](reports02993/storage93-after-720.png), [1080p](reports02993/storage93-after-1080.png). Echte Panel-/Fokus-/Button-Pixel und Back verifiziert. Englisches synthetisches Wegwerfprofil, keine Android-Aufnahme. Debugoverlay nur im Testprofil für die Aufnahme aus- und danach wieder eingeschaltet; keine Benutzer-/Skin-Einstellung verändert.

## Historische Fehler und gezielte Gegenläufe

- Zwei lokale breite Läufe liefen noch während Quelle/Delta-Fixture/PO fertiggestellt wurden: 3.933 Fälle mit 89 FAIL/3 ERROR, 3.935 mit 38 FAIL/1 ERROR. Keine finalen PASS-Belege. Ursachen: alte importierte Caches, parallele Fixture-/PO-Fertigstellung, echte Opt-out-/Dummy-Gruppenfehler und Workspace-ENOSPC. Echte Fehler korrigiert; nur vier eigene saubere abgeschlossene Worktrees entfernt, Historie/Branches/Pakete/Android-Daten erhalten. Danach lokaler Stand vor letzter UI-Textur: 3.938 PASS in 781,900 s. Finale CI nutzt unveränderlichen Checkout.
- [Historischer Transportjob](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43504728829): archivierter .74-Container beendet, Probe Exit137. Ursache nicht als OOM bewiesen. Ausschließlich fehlgeschlagenen Job einmal wiederholt: **PASS**, gesamter Workflow danach SUCCESS. Tatsächlicher `Commit and publish generated archives`-Schritt **SKIPPED**; nachgelagerter Job erzeugte nur ein PR-Testartefakt.
- Initialer .90-1080p-Lauf: `VISIBLE84_TIMEOUT`. Messpunkt 0 um 21:04:10 UTC, 450 s um 21:11:40UTC, Supervisorabbruch 21:19:06 UTC, 899-s-Messpunkt wenige Sekunden später. Container aktiv, `OOMKilled=false`, cgroup OOM 0. [Befund](reports02993/retention90-supervisor-before.json). **FAIL, kein 15-Minuten-PASS.** Nur synthetisches Gesamtbudget 30 → 45 Minuten; 900 s, 899-s-Punkt, 100 Navigationszyklen, 305-s-Sticky-Gate, drei Neustarts und sofortiger GUI-Fehlerabbruch unverändert. Add-on-/Player-Timeout nicht geändert.
- Initialer .90-720p-Lauf: [900-s-Warmphase bestanden](reports02993/retention90-initial720-warm-only.json), anschließend Cold-FAIL `SERIES85_SELECTION_WITHOUT_MANAGER_WROTE_MAPPING`. Älteres Kandidatendialog-Gate erwartete keine Datei, obwohl der neue Manager zuvor ausdrücklich Zuordnung 9003 gespeichert hatte. [Befund](reports02993/retention90-cold-before.json). Nur Testannahme korrigiert: Datei vor/nach Kandidatendialog bytegleich erhalten; ohne Vorbestand weiterhin keine Datei. Hostprüfung weist Änderungen und Löschung zurück. Keine Produktionsspeicherung geändert, nichts gelöscht.
- Überholte Gegenläufe auf `7713c1ab` nach der zusätzlich nachgewiesenen Cold-Testkorrektur abgebrochen. Aktueller unveränderlicher Prüfstand `86462cb1`, keine weiteren Änderungen während des Laufs.

## Freigabe

[Issue-Matrix](ISSUE_MATRIX_02993_DE.md), [16 offene Android-Gates](ANDROID_ABNAHME_02993_DE.md), [manuelles Testupdate](INSTALLATION_RC_02993_DE.md), [technische Übergabe](CODEX_UEBERGABE_02993_ANDROID_PLAYER_EPG_CLEANUP_2026-11-13_DE.md).

**Draft zur Prüfung. Keine vollständige P0-Abnahme oder Merge-/Release-Empfehlung.** P1 #435/#450/#427 bleibt getrennt. Keine privaten Rohlogs oder echten Zugangsdaten veröffentlicht.

Die korrigierten vollständigen Gegenläufe sind abgeschlossen. Warmphase: 720p 900.7 s, 1080p 900.1 s (exakte Werte in JSON); anschließend je drei kalte Neustarts mit bytegleicher geschützter Konfiguration, 88 Logos und persistentem Mapping 9003. Tatsächliche Zeiten ausschließlich synthetische Linux-Messwerte. Die initialen FAILs bleiben oben dokumentiert; daraus wird kein Android-PASS abgeleitet.
