# Kleine Skin-Folgeänderung – beschriftete Medienreihen und nativer Ladekreisel

Abhängigkeit: Draft-PR #437, keine Zusammenführung und keine Veröffentlichung. Version bleibt .90; das Review-ZIP ist kein freigegebenes Kodi-Update. Diese Änderung ist separat vom Uhr-Routing-Fix zu prüfen.

## Implementierung

`widget_skin90.py` übernimmt die echte `multiimage`-Animation aus BINGIEs `widget_header_multi` in die beiden eigenen Medienreihen. Die ursprünglichen Bildpfade, Framezeiten (85 ms), Transparenz, Farbe und Seitenverhältnisse bleiben erhalten. Zwei quellenspezifische Bedingungen trennen Filme und Serien. Es gibt keine neuen Netzwerkworker oder Polling-Schleifen. Der zuvor globale Pending-Status wurde auf Profil/Provider/Reihe begrenzt; ein Serien- oder Logoauftrag darf keinen Filmspinner starten. Katalogaufträge werden ausschließlich aus dem bereits vorhandenen, jetzt mit Profilkennung versehenen Service-Memo gelesen; keine zusätzliche SQLite-/Journalabfrage pro UI-Tick.

Der bereits vorhandene `home_loading85`-Status begrenzt die Anzeige auf tatsächlich vorgemerkte Arbeit und maximal 60 Sekunden pro unveränderter Generation. Kodi `IsUpdating` allein kann den Spinner nicht dauerhaft aktiv halten. Danach zeigt die bestehende Statuszeile den Fehler-/Leerzustand. Eine horizontale Headergruppe lässt Kodi die tatsächliche Breite der gespeicherten Überschrift messen und platziert den 24×24-Kreisel unmittelbar 12 Pixel dahinter. Sie liegt oberhalb der Cover und vor dem Statustext. Titel, 244-Pixel-Reihenhöhe, Coverposition, Fokus und alle ursprünglichen Pfade bleiben unverändert.

Der bestehende Skin-Transaktionsweg übernimmt Vorschau, ausdrückliche Bestätigung, private Sicherung, Hashprüfung, atomare Anwendung und Rollback. Keine Skinänderung auf einem Gerät wurde ausgeführt. Unbekannte Änderungen an eigener Reihen-Geometrie oder nativer Animation blockieren die Anwendung.

## Teststand

| Prüfung | Ergebnis |
| --- | --- |
| BINGIE-Multiimage, begrenzter Status, Fehler/leer, Geometrie, idempotent, fremde Includes/Dateien unverändert | PASS – 10 Tests, 3,936 s |
| Bestehende .90-Startup-/Fokus-/Bestandsschutzfälle | PASS – 12 Tests, 3,485 s |
| Katalog-/Importregressionen | PASS – 95 Tests, 51,479 s |
| Sämtliche Skin-Regressionsdateien | PASS – 52 Tests, 39,420 s |
| Kumulative historische Scope-Tests | PASS – 169 Tests, 138,589 s |
| Review-ZIP: CRC, SHA256 und alle 855 Quelldateien | PASS |
| Vollständige aktuelle Hosttestsuite / GitHub-CI | NOT_TESTED – separat starten |
| Rotierende Animation und Überschriften auf echter Kodi-21.3-Android-Box | NOT_TESTED |
| Allgemeine native Gesamtgates aus .90 | weiterhin offen, siehe PR #437 |

Die alten Source-/Geometrie-Guards behalten ihre Sollwerte. Nur die vollständigen bekannten neuen Quelldateien wird für historische Source-Guards auf ihre Vorgängerbytes abgebildet. Zur alten MediaRow-Hashprüfung werden ausschließlich ausschließlich die exakt geprüfte horizontale Überschrift-/Spinnergruppe auf die ursprüngliche Überschrift zurückgeführt; jede andere Layoutabweichung bleibt ein Fehler. Der vorige #437-ZIP wird gegen dessen Commit e1164eee geprüft, der neue Skin-ZIP separat gegen den gesamten aktuellen Quellbaum. Die später ergänzten sechs Soll-Reihen sind einzeln in `WIDGET_EPG_FOLGESTATUS_2026-11-12_DE.md` aufgeführt; diese Skin-PR implementiert nur den Film-/Serienteil.

## Review-Paket

`docs/XCMate/test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip`

SHA256: `7142b05ec255dd513a60f10b90718e3b181cba95a50df4681628d19273fe7e9e`.

Die veröffentlichten Kanäle und Installer .5.26 bleiben bytegleich.

## Noch erforderliche Geräteprüfung

Alle Punkte zunächst NOT_TESTED: Filme/Serien mit gespeicherter Überschrift; echter langsamer Katalog-/Coverjob zeigt nur den jeweiligen Ladekreisel; gefüllte/leere/fehlgeschlagene Antwort beendet ihn; nach 60 Sekunden kein endloses Drehen; Umschalten zwischen Reihen, nativer Fokusrahmen und Coverklick; keine Überlagerung von Hero/Leiste; Fremdwidgets und persönliche Reihenfolge; Neustart und Rollback über die gesicherte Transaktion. Daten- oder Cache-Reset ist dafür nicht vorgesehen.
