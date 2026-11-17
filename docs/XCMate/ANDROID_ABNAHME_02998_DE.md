# XCMate 0.1.29.98 – Android-Abnahme

**Stand 17.11.2026: alle Geräteprüfungen ANDROID_NOT_TESTED.** Native Linux-Kodi-Bilder sind keine Android-Abnahme. Keine automatische Installation, Veröffentlichung oder Profiländerung durch Codex.

Review-ZIP: `test-builds/02998/plugin.video.xtreammate-0.1.29.98.zip`
SHA256: `d37d34fbb5be5e46154b912d3ce960f6e248431fcf7d0a9651fa9785b20a12c3`.

Erst nach gesonderter Nutzerfreigabe das ZIP als kumulatives Update von .97 installieren; weder deinstallieren noch Profile, Datenbanken, Caches oder Einstellungen zurücksetzen. Box A bleibt unangetastet. Die bisher veröffentlichte .97 und das geschützte .90-Paket werden durch diesen Entwicklungsauftrag nicht ersetzt.

Vor dem Test auf Box B Kodi-Version, Auflösung, installierte XCMate-Version und Anzahl konfigurierter Portale/EPG-Quellen/Widgets notieren. Keine Zugangsdaten, Tokens, privaten URLs oder Rohlogs auf GitHub veröffentlichen.

| Gate | Ausführung auf RK3528/Kodi21.3/BINGIE | Erwartung | Status |
|---|---|---|---|
| A98-01 | .97 → .98 über ZIP aktualisieren; neu starten | .98 im Add-on; Profile, Portale, Token und Quellen unverändert; kein erneuter Tokenimport | ANDROID_NOT_TESTED |
| A98-02 | Home mit konfigurierter Startgruppe öffnen, anschließend fünf Minuten auf derselben Sendung bleiben | Senderlogos, Jetzt/Danach, richtige Hero-Textur und vorhandene Benutzerwidgets sichtbar; kein Bildverlust | ANDROID_NOT_TESTED |
| A98-03 | Sendungsdetails und automatische Bildsuche mit bestehender Freigabe öffnen | Quellrichtiges, tatsächlich sichtbares Bild; verständlicher Lade-/Fehlerstatus; kein bloßer READY-Nachweis | ANDROID_NOT_TESTED |
| A98-04 | Bestehende ausdrückliche Bild-Opt-outs prüfen, ohne sie zu überschreiben | Keine unerlaubten Bildabfragen; Provider-EPG unabhängig verfügbar; Speicherprobleme verständlich, ohne Reserve abzuschalten | ANDROID_NOT_TESTED |
| A98-05 | In Mini-EPG und großem EPG „EPG zuweisen“ öffnen | Tatsächlich konfigurierte Quellen, vorbefüllte Sendersuche, bedienbarer Fokus und lesbare Statusfläche; keine abgeschnittenen Texte | ANDROID_NOT_TESTED |
| A98-06 | Kandidat wählen, Vorschau vergleichen, Quelle/Kanal wechseln; mit Zurück abbrechen | Reversible Vorschau, keine stille Speicherung, ursprüngliche Ansicht/Gruppen/Fokus wiederhergestellt; kein Playerstart | ANDROID_NOT_TESTED |
| A98-07 | Bewusst gewählte Testzuordnung speichern, Dialog schließen, wieder öffnen und Kodi neu starten | Sichtbare Save-Bestätigung, korrekte quellenspezifische Bindung und Programme in Elternansicht sowie Cold-Readback; anschließend Originalzuordnung kontrolliert wiederherstellen | ANDROID_NOT_TESTED |
| A98-08 | Film/Serie/Live-TV starten/verlassen; fremde Widgets und Fernbedienungsnavigation prüfen | Bestehende Wiedergabe, Back, Resume/Autoplay, sechs Reihen und frei konfigurierte Widgets unverändert | ANDROID_NOT_TESTED |

Bei FAIL genaue Aktion, Zeitpunkt, Ansicht, sichtbaren Status und anonymisierte Diagnosecodes notieren. Keine Hardware-, Decoder-, echten Netzwerk- oder Mini-Elternansichtserfolge aus simulierten Hosttests ableiten. Es besteht keine Freigabe zur Aktualisierung des regulären, Pilot- oder NeoDark3-Katalogs.
