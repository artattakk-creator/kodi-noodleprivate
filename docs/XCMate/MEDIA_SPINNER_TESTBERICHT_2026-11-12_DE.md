# Kleine Skin-Folgeänderung – beschriftete Medienreihen und nativer Ladekreisel

Abhängigkeit: Draft-PR #437, keine Zusammenführung und keine Veröffentlichung. Version bleibt .90; das Review-ZIP ist kein freigegebenes Kodi-Update. Diese Änderung ist separat vom Uhr-Routing-Fix zu prüfen.

## Implementierung

`widget_skin90.py` übernimmt die echte `multiimage`-Animation aus BINGIEs `widget_header_multi` in die beiden eigenen Medienreihen. Die ursprünglichen Bildpfade, Framezeiten (85 ms), Transparenz, Farbe und Seitenverhältnisse bleiben erhalten. Zwei quellenspezifische Bedingungen trennen Filme und Serien. Es gibt keine neuen Netzwerkworker oder Polling-Schleifen.

Der bereits vorhandene `home_loading85`-Status begrenzt die Anzeige auf tatsächlich vorgemerkte Arbeit und maximal 60 Sekunden pro unveränderter Generation. Kodi `IsUpdating` allein kann den Spinner nicht dauerhaft aktiv halten. Danach zeigt die bestehende Statuszeile den Fehler-/Leerzustand. Die Spinnerfläche (24×24, links 868/oben 2 innerhalb der eigenen Reihe) liegt nach der gespeicherten Überschrift und vor dem Statustext, oberhalb der Cover. Titel, 244-Pixel-Reihenhöhe, Coverposition, Fokus und alle ursprünglichen Pfade bleiben unverändert.

Der bestehende Skin-Transaktionsweg übernimmt Vorschau, ausdrückliche Bestätigung, private Sicherung, Hashprüfung, atomare Anwendung und Rollback. Keine Skinänderung auf einem Gerät wurde ausgeführt. Unbekannte Änderungen an eigener Reihen-Geometrie oder nativer Animation blockieren die Anwendung.

## Teststand

| Prüfung | Ergebnis |
| --- | --- |
| BINGIE-Multiimage, begrenzter Status, Fehler/leer, Geometrie, idempotent, fremde Includes/Dateien unverändert | PASS – 7 Tests, 3,688 s |
| Bestehende .90-Startup-/Fokus-/Bestandsschutzfälle | PASS – 12 Tests, 2,924 s |
| Sämtliche Skin-Regressionsdateien | PASS – 52 Tests, 33,005 s |
| Kumulative historische Scope-Tests | PASS – 169 Tests, 81,837 s |
| Review-ZIP: CRC, SHA256 und alle 855 Quelldateien | PASS |
| Vollständige aktuelle Hosttestsuite / GitHub-CI | NOT_TESTED – separat starten |
| Rotierende Animation und Überschriften auf echter Kodi-21.3-Android-Box | NOT_TESTED |
| Allgemeine native Gesamtgates aus .90 | weiterhin offen, siehe PR #437 |

Die alten Source-/Geometrie-Guards behalten ihre Sollwerte. Nur die vollständige bekannte neue Quelldatei wird für historische Source-Guards auf ihre Vorgängerbytes abgebildet. Zur alten MediaRow-Hashprüfung werden ausschließlich zwei exakt geprüfte hinzugefügte Spinner entfernt; jede andere Layoutabweichung bleibt ein Fehler. Der vorige #437-ZIP wird gegen dessen Commit e1164eee geprüft, der neue Skin-ZIP separat gegen den gesamten aktuellen Quellbaum.

## Review-Paket

`docs/XCMate/test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip`

SHA256: `828c2a270b9266d505619378c24fd17cd54eaca616bb85189fc352d9f4f79389`.

Die veröffentlichten Kanäle und Installer .5.26 bleiben bytegleich.

## Noch erforderliche Geräteprüfung

Alle Punkte zunächst NOT_TESTED: Filme/Serien mit gespeicherter Überschrift; echter langsamer Katalog-/Coverjob zeigt nur den jeweiligen Ladekreisel; gefüllte/leere/fehlgeschlagene Antwort beendet ihn; nach 60 Sekunden kein endloses Drehen; Umschalten zwischen Reihen, nativer Fokusrahmen und Coverklick; keine Überlagerung von Hero/Leiste; Fremdwidgets und persönliche Reihenfolge; Neustart und Rollback über die gesicherte Transaktion. Daten- oder Cache-Reset ist dafür nicht vorgesehen.
