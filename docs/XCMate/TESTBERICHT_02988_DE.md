# XCMate 0.1.29.88 – Testbericht / Draft #422

Basis: veröffentlichte .87, `2547848625df8ecd3ba089ecd6c49339c8f3c348`.
Getesteter Add-on-Quellstand: `6c1471891fa0fa2795b91c645781c2e5683d035d`, Quellbaum `2ec26545f3c25fca43fc527a34600755c31e8391`.
Spätere Commits passen ausschließlich native Testskripte bzw. diesen Bericht an; ZIP und Add-on-Quellbaum bleiben identisch. Kein Merge, keine Veröffentlichung.

## Automatisierte Hostprüfungen

| Prüfung | Ergebnis |
|---|---|
| Vollständige kumulative unittest-Suite, Python 3.12 (lokal .14 / CI .16) | **3.689 PASS in CI**, 822,949 s, 0 Fehler/Fehlschläge; ursprünglicher lokaler Gesamtlauf vor Kaltstartergänzung: 3.684 PASS in 609,505 s |
| Gezielte aktuelle Bild-, Sicherheits-, Detail-, Skin- und Bestandsschutzfälle | 99 PASS, 15,995 s |
| Zusätzliche Branding-pytest-Prüfungen | 11 PASS, 0,32 s in CI (lokal 0,11 s) |
| Kodi-PO-Validierung | 17 Sprachkataloge PASS; DE/EN jeweils 1.317 Kontexte, weitere Kataloge jeweils 51 mit bestehendem Fallback |
| Reproduzierbares ZIP | Bytegleich, 838 Dateien, 4.621.024 Bytes; CRC und alle Quelldateien geprüft |
| Diff-/Paketprüfung | Kein Whitespacefehler, keine Datenbanken, Logs, pyc oder echten Zugangsdaten im neuen ZIP |

Hostaufruf: `TMPDIR=/tmp SQLITE_TMPDIR=/dev/shm/xcmate88-final PYTHONPATH=/tmp/xcmate80-host-deps:tests python -m unittest discover -s tests -v`.
Testabhängigkeiten: Pillow 12, simpleeval 0.9.13, impacket 0.13.0, pytest 9.2. Der temporäre Testdatenträger besitzt ausreichend Freiraum für die unverändert aktive 1-GiB-Reserve. Die absichtlich niedrigen Speicherwerte der Fehlerfälle werden separat injiziert; keine physische Android-ENOSPC-Abnahme.

Gemessene bestehende Regressionen auf diesem Host: 160.005 Programme aus 95.571.948 XMLTV-Bytes in 21,403 s importiert; SQLite 303.685.632 Bytes. Der indexgestützte Widgetabruf aus 20.005 Katalogtiteln lieferte 24 Einträge in 2,836 ms. Das sind Hostmessungen, keine Android-Ladezeitprognose. Ein belastbarer Vorher-/Nachher-Vergleich auf der realen Box liegt noch nicht vor.

## Native Kodi und GitHub CI

- Vollständige aktuelle Host-CI **PASS**: **3.689 Tests in 822,949 s**, 11 Branding-Tests in 0,32 s, 17 PO-Kataloge, Compile und bytegleiche ZIP-Reproduktion. [CI 42932821507](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42932821507), geprüfter Test-/Quellstand `41bb85f13a76b1f6aab17fd5570ce1f4e7d1e359`. Der Add-on-Quellbaum und das ZIP sind identisch mit `6c14718`. Der vorangegangene vollständige Add-on-Lauf mit 3.686 Tests war ebenfalls PASS.
- Zusätzliche drei Testhüllen-Regressionen prüfen den tatsächlich verwendeten JSON-Sammler gegen leere/teilweise Testdateien, echte FAIL-Quittungen und unveränderten begrenzten Timeout. Zusammen mit vier Scope-Prüfungen 7 PASS, 0,256 s. Diese drei Tests sind zusätzlich im grünen vollständigen Lauf mit 3.689 Tests enthalten.
- **Strenger nativer Bildlauf 720p und 1080p PASS**: [42929994133](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42929994133), Jobs `130226021620` und `130226021260`. Tatsächliche Pixel im ungedimmten rechten Hero-Bereich, proportionale Portrait-/Logo-Fallbacks, Logos in der sichtbaren Rail, Film-/Serienbilder und echte Kodi-Texturen. Keine READY-Meldung allein als Bildbeweis.
- Reales offenes EPG-Detailbild: **306,09 s bei 720p / 306,18 s bei 1080p**, Checkpoints 2/46/121/305 s. Bei jedem Checkpoint 253.204 bzw. 253.572 passende Bildpixel und unveränderte Bildreferenz; negativer Status ab Sekunde 45 injiziert. Kein Fake-Clock-Ersatz für diese Messung.
- Zwei tatsächliche Kodi-Neustarts je Bildauflösung mit abgeschaltetem synthetischem Bildursprung: **PASS**, Event-Kaltstart aus dem Kodi-Cache und sichtbare lokale Logo-Fallbacks. 34 geschützte Dateien unverändert. Vollständige lokale Speicherung aller 88 Logos wird damit ausdrücklich **nicht** behauptet: Erst tatsächlich angeforderte Texturen landen im Kodi-Cache; Archiv-Schreibreserve und begrenzte RAM-Referenzen werden separat gezählt.
- Native Fernbedienungs-/Owner-Fälle: 100 Detail-/Plugin-/Back-Zyklen je warmem Bildlauf, keine Index-/Directory-/Invoker-Fehler; sieben unterschiedliche Rail-Icons, echte Fokusbewegung, 13 gespeicherte fremde Widgetdefinitionen aus sieben unabhängigen synthetischen Plugin-Quellen erhalten. 13 Darstellungsfälle, zehn Wechselzyklen und zwei echte native Audio-OK-Starts pro Bildlauf.
- Weitere breite Home-/Guide-/Filmwiedergabe bei 1080p PASS: [42929686346](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42929686346). Separate vollständige kurze 720p-Diagnose mit aktuellem Add-on-Quellbaum PASS: [42931066972](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42931066972).
- Native Playerprüfung **60 Stop-/ACK-Zyklen PASS**, je 20 Live-TV/Film/Serie: Job `130224991853` im breiten Home-Lauf. Synthetisches AV-Material wird durch Kodis echten Linux-Player abgespielt; kein Android-MediaCodec-Nachweis.
- Datenbank-Pausen-Teiltest auf vorherigem .88-Quellstand `7679289`: **1.800,84 s PASS**, 443 Wiederholungsaufrufe, ein Worker, keine unbehandelte Ausnahme, Wiederaufnahme mit demselben Worker. [42927121771](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42927121771). Der Gesamtlauf blieb **FAIL**, weil anschließend eine gerade angelegte leere Neustart-Testdatei gelesen wurde. Der native Sammler ist korrigiert und durch drei Regressionen abgesichert. Kein behaupteter kompletter 30-Minuten-Gesamt-PASS auf dem endgültigen Add-on-Quellstand.

Native Plattform: **Linux x86_64 / Kodi 21.2**, isoliertes Profil und synthetische Provider-/Bild-/Metadaten. Die echten privaten TMDB-/Provider-Zugänge wurden nicht benutzt. XCMate beobachtet injizierte 27 MiB freien Platz, während Kodis C++-Texturecache tatsächlichen freien Linux-Speicher verwendet. Kein physisch volles Android-Dateisystem, kein Kontakt mit Box A oder Box B.

Bei der Sichtprüfung wurde eine vorher zu breite Pixel-Stichprobe verworfen: Der Verlauf über einem Logo konnte zufällig ähnliche RGB-Werte liefern. Die neue Prüfung misst rechts außerhalb des Verlaufs, bei unveränderten Mindestpixelzahlen. Die aktuellen Bilder sind streng geprüft. Frühere rote/abgebrochene Läufe und eine mangelhafte ASCII-Fehlerausgabe werden nicht als Erfolg umgedeutet; UTF-8-Diagnose und JSON-Sammler wurden getrennt repariert.

Maschinenlesbare Belege: [Native Ergebnisse](NATIVE_ERGEBNIS_02988.json), [Hostergebnisse](HOST_ERGEBNIS_02988.json), [Screenshot-Hashes](evidence/02988/manifest.json). Beispielaufnahmen zeigen synthetische Farbflächen, keine echten Sendungen und keine Android-Box:

| Auflösung | Home nach Kaltstart | EPG-Details nach 305 s | Fremde Widgetreihe |
|---|---|---|---|
| 720p | [PNG](evidence/02988/native720-visible84-hero86-final.png) | [PNG](evidence/02988/native720-visible84-sticky88-305.png) | [PNG](evidence/02988/native720-visible84-foreign87-warm-1-7.png) |
| 1080p | [PNG](evidence/02988/native1080-visible84-hero86-final.png) | [PNG](evidence/02988/native1080-visible84-sticky88-305.png) | [PNG](evidence/02988/native1080-visible84-foreign87-warm-1-7.png) |

## Status des Masterauftrags

| Bereich | Implementierung / Hostnachweis | Reale Android-Abnahme |
|---|---|---|
| Logo-HTTP(S)/VFS, Scope, Redirect, SSRF, Dekodierung | PASS; Adapter und begrenzte RAM-Übergabe getestet | ANDROID_NOT_TESTED; reale 88 Senderquellen nicht zugänglich |
| Speicher-/Volume-Diagnose, Schreibreserve | PASS; keine Reserveabschaltung, keine automatische Migration oder Löschung | ANDROID_NOT_TESTED; geeigneter realer Zielpool muss gemessen werden |
| Sticky-Artwork | Host-PASS einschließlich negativer 45-s-Nachprüfung, Ereignis-/Profil-/Freigabewechsel | ANDROID_NOT_TESTED; nativer Realzeittest 306 s je Auflösung PASS |
| EPG-Reader-/Worker-Lifecycle | PASS; keine nicht vorhandene close-Methode, atomare Worker-Abgabe, begrenzter Backoff | ANDROID_NOT_TESTED; vier echte Ansichten vergleichen |
| Generationen, Widget-/SkinShortcuts-Erhalt | Host-PASS; eigene und fremde Definitionen erhalten | ANDROID_NOT_TESTED |
| Detailbuttons / Merkliste / Umschalten | Host-PASS; echte Datei/Readback und vorhandener Owner-/Player-Handoff | ANDROID_NOT_TESTED; Remote-/Streamtest erforderlich |
| Filmischer Hero / Navigation | Host-Geometrie-PASS; referenzierter Gradient, eigene Glyphen 48×48 | ANDROID_NOT_TESTED; Originalfoto 4 fehlt |
| Separates XCMate-Branding | Host-PASS; Original-Asset, Vorschau, Backup und Rollback | ANDROID_NOT_TESTED; ausdrückliche eigene Bestätigung erforderlich |
| P2-Bereinigung | Nur lesende Bestandsaufnahme; verwaist nicht behauptet | Löschfunktion bewusst nicht Bestandteil dieses Fixes |

## Testpaket und Installation

[ZIP](test-builds/02988/plugin.video.xtreammate-0.1.29.88.zip) · [SHA256](test-builds/02988/plugin.video.xtreammate-0.1.29.88.zip.sha256)

`eccbf1651c5755681b2dec091acab5e85684f7db8d938cfef2a2f7a0f6d843fd`

In Kodi auf Box B das ZIP über „Add-ons → Aus ZIP-Datei installieren“ als kumulatives Update installieren; kein Löschen, keine Deinstallation, kein Profilreset. Danach [Android-Abnahme A88-01 bis A88-12](ANDROID_ABNAHME_02988_DE.md) durchführen. Den bekannten .87-Layoutadapter nur über die angebotene Vorschau/Backup/Bestätigung aktualisieren. Der separate Branding-Patch ist ebenfalls ausdrücklich zu bestätigen.

Alle publizierten .87-ZIPs/Indizes, GS Media Setup .5.26 und Tokenreader/-writer bleiben unverändert. Regulär/Pilot/NeoDark3 enthalten keine .88-Veröffentlichung. Keine neue Laufzeitabhängigkeit vom TMDB Helper. Joomla-Gateway bleibt Backlog.

Originalfoto 4 (`1000121041.jpg`) wurde nicht als Datei übergeben; daher kein pixelgenauer Referenzvergleich. Vor Merge sind Android-Abnahme und gesonderte Freigabe erforderlich. Auf einem realen Volume mit weniger freiem Speicher als der Reserve bleibt das eigene Archiv weiterhin geschützt; ein geeigneter anderer Speicherpool ist erst auf dem Gerät nachzuweisen. Es gibt keinen behaupteten Speichergewinn. Skin-Rollback erfolgt ausschließlich über den separaten journalisierten Bestätigungsablauf; kein automatischer Add-on-Downgrade oder Datenreset.
