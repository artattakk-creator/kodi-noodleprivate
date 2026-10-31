# XCMate 0.1.29.61 – abgeschlossener Host-Testbericht

2536 Hosttests in 405.131 Sekunden: **PASS, 0 Fehler, 0 Fehlschläge, 0 übersprungene Tests**. Ausgeführt aus sauberem Git-Export des Add-on-Quellstands `d1c3941a632222a1190d0a044f365a73153b5f28`. Native-/CI-Head `09ed0eb9c5e1384fd2e363d18d2ee0fe0210cc98` hat denselben Add-on-Baum `89ecfeee9aeac07df6dc16d10cb25b55d97e4244`; danach nur Änderungen an Testablauf und Dokumentation. Alle 2.514 Methoden der .60-Basis und ihre Skip-Bedingungen bleiben erhalten. 22 neue Methoden prüfen Menüzugang, Bestandsschutz, Token-Dateisicherheit und Neustart.

Vollständige Hostausgabe: [HOSTTESTS_02961.log](HOSTTESTS_02961.log), maschinenlesbare Ergebnisse: [TESTERGEBNISSE_02961.json](TESTERGEBNISSE_02961.json), [Paketprüfung](PAKETPRUEFUNG_02961.json). [GitHub CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41149649303) ist vollständig grün: 2.536 Tests in 378,706 Sekunden, alle vier nativen Prüfungen PASS, Testpaket hochgeladen und mit derselben SHA256 wie das lokale ZIP. Getesteter CI-Head `09ed0eb9c5e1384fd2e363d18d2ee0fe0210cc98`. Der nachfolgende Commit enthält ausschließlich diesen Bericht und Belege; Add-on-Baum und ZIP bleiben gleich. Der produktive Veröffentlichungsschritt wurde nachweislich SKIPPED.

## Native Prüfung

- Neue sichtbare Menüfolge mit nativen Fernbedienungseingaben, echter Vorschau und Zustimmung, Produktionsbackup und Vier-Dateien-Adapter, danach freigegebene Rückkehr zu Home10000/Container2510: PASS.
- Ohne Token und ohne EPG 88 Sender, ursprüngliche Reihenfolge, Fokus auf 0/1/87, zwei dekodierte Logos und letzte Kachel als Sendername bei fehlendem Logo: PASS.
- Neutraler lokaler Hero, passende Senderidentität, kein Playerstart durch Fokus: PASS. Pixel, ListItem-Properties und Screenshot-SHA256 separat geprüft.
- Bestehender unveränderter nativer .60-Test mit EPG, zwei lokalen Sendungsbildern und echtem Kodi-Neustart: PASS. Der durch CI gefundene Revisionsverlust ist damit korrigiert.
- [Menü-/Home-Rohbefund](evidence02961/native-menu-home61.json), [EPG-/Neustart-Rohbefund](evidence02961/native-epg-home60.json). Bilder [Sender 0](evidence02961/home61-0.png), [Sender 1](evidence02961/home61-1.png), [Sender 87 ohne Logo](evidence02961/home61-87.png) sind ausdrücklich synthetische Hostbelege.

Kodi 21.2/Linux, originale gepinnte BINGIE-2.2.3-Dateien und unveränderter Skinshortcuts-2.1.0-Templatecompiler. Externe Helfer sind Stubs; der Builder-Harness installiert die native Compiler-Ausgabe erst nach echter Zustimmung und genau einmal. Vollständiger Skinshortcuts-Lauf, Android21.3, RK3528-Player und reale Bindungen auf Box B bleiben ANDROID_NOT_TESTED. Die Tests beweisen keine realen TMDB-Zugangsdaten oder Android-Pixel.

## Daten- und Paketschutz

619 bisherige Add-on-Dateien erhalten, 606 davon roh bytegleich; 13 exakte Änderungen durch Hash-/Text-Normalisierung geprüft, zwei neue Module. Quellen-URLs und passive Widgets, Binding-/Transaktionscode, Player/.42-Kompatibilität, EPG-/Portal-/Favoriten-/Resume-Code und originale Grafiken unverändert. 62 geschützte Dateien fremder Arbeitsstände unverändert. Kein Gerät angesprochen, kein Benutzerprofil, Benutzer-Cache, Portal, Benutzerbild oder Benutzerdatenbank gelöscht.

Installations-ZIP: 621 Dateien, 3.197.861 Bytes; CRC, sichere Pfade, AST, alle Quellbytes und unabhängiger deterministischer Neuaufbau PASS. SHA256 `f03ea0284e74e44d5e1c3ca568a18bb28569b8e1e747a25426155da49d4f89d5`. Keine privaten Token-Dateien oder Benutzerdaten enthalten. Der frühe P0-Stand `24882ec` und die zwischenzeitliche Prüfsumme `d06c…` sind durch dieses Paket ersetzt.

## Korrigierte Zwischenbefunde

Erster Vollauf: alte Versions-/Menüanzahl-Erwartungen angepasst; im zweiten Lauf eine verbliebene Drei-Aktionen-Erwartung auf die weiterhin erhaltenen ersten drei Quellen plus zwei neue Layoutaktionen präzisiert. Native Testautomatisierung musste die tatsächlichen Menüeingaben und das Ende der Layout-Invocation abwarten, bevor Home fokussiert wird. Die Sicherheitsreserve blockierte korrekt einen synthetischen Import bei vollem Cloud-Dateisystem; ausschließlich doppelte eigene Test-Skinextraktionen und disposable Container entfernt. Keine Reserve deaktiviert, keine Benutzerdateien entfernt. Abschließende Läufe wiederholen die Pflichtprüfungen ohne diese Zwischenfehler.

## Android

[B-61-01 bis B-61-04](ANDROID_ABNAHME_02961_DE.md) bleiben **ANDROID_NOT_TESTED**. Zuerst die reale Senderkachel, Fokus und vollständige Gruppe ohne Token/EPG prüfen; erst danach Hero/Player und Dateiimport. Kein Merge oder Release und kein Schließen von #286.
