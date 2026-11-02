# XCMate .70 – Android-Abnahme

**Alle Geräteprüfungen zunächst NOT_TESTED.** Privatlogs sind derzeit nicht lesbar; keine erfundene Logabnahme. Nur Testbuild aus Draft #319 verwenden. Keine neue Merge-/Release-Freigabe vorausgesetzt.

Das GitHub-Testartefakt entpacken; das darin enthaltene plugin.video.xtreammate-0.1.29.70.zip über Kodi als kumulatives Update installieren. SHA256 mit der beigefügten .sha256 vergleichen. Box A unverändert lassen; keinen Token erneut importieren, keine Bilder/DBs löschen und keinen Skin neu zuweisen.

| ID | Ausführung und erwartete Beobachtung | Status |
|---|---|---|
| ART70-01 | Version .70 und Änderungspopup prüfen. Portale, EPG-Zuweisungen, Cover, Favoriten, Resume und vorhandene TMDB-Einstellungen bleiben erhalten. | NOT_TESTED |
| ART70-02 | Mini-EPG → gleiche Sendung → Details. Helper-Fehler wird verständlich erklärt, ohne ein wartendes gefundenes Bild zu behaupten. Back bleibt bedienbar. | NOT_TESTED |
| ART70-03 | Großen EPG öffnen → gleiche Sendung → Details → zurück. Quellen-/Sendungsidentität und Fokus bleiben korrekt. | NOT_TESTED |
| ART70-04 | Bekannte eindeutige Film-/Seriensendung mit bereits freigegebenem eigenem TMDB-Zugang prüfen. ART70 source=tmdb und Ergebnis getrennt vom Helper beobachten; tatsächliches sichtbares Bild kontrollieren. TMDB_OK allein reicht nicht. | NOT_TESTED |
| ART70-05 | Ein gefundenes Bild fokussieren, mehr als sechs Minuten warten, erneut Mini-/Groß-Details und Home aufrufen. Bildstatus bleibt bis zur echten TTL nutzbar, kein falsches NOT_SCHEDULED. | NOT_TESTED |
| ART70-06 | Unter EPG/Sendungsbilder die eigene Suche bewusst erneut freigeben/bestätigen (vorhandener Zugang bleibt). Ein negatives Ergebnis wird einmal neu geprüft, nicht bei jedem Fokus. Keinen globalen Reset ausführen. | NOT_TESTED |
| ART70-07 | Helper-/Netzwerkfehler: eigene TMDB-, Helper- und Speicherursache getrennt erklären. Keine Endlosschleife, kein dauerhaft als Bilddownload angekündigter Fehlerstatus. | NOT_TESTED |
| ART70-08 | BINGIE Home: Startgruppe durchscrollen, Hero exakt zur fokussierten Sendung. Bei tatsächlich fehlendem Bild neutral bleiben; lokale EPG-Texte/Logos sofort nutzbar. | NOT_TESTED |
| ART70-09 | Neue Anfrage ohne schnellen ACK: „Auftrag übergeben“, danach ggf. fehlende Dienstbestätigung; wiederholter Fokus setzt die Wartezeit nicht zurück. | NOT_TESTED |
| REG70-01 | Startsender → einmal Back → bedienbares Home; bestehender .42-Kompatibilitätsmodus unverändert. Anschließend fünf Zyklen. | NOT_TESTED |
| REG70-02 | Film-/Serienwidgets mit Covern, Suche, Detailstart und Rückkehr; Resume und staffelübergreifendes Autoplay erhalten. | NOT_TESTED |
| REG70-03 | Kodi-Neustart: Portale, Token, manuelle EPG-Mappings, Cover und Widgetbindungen unverändert. | NOT_TESTED |

Pro Fall PASS/FAIL/NOT_TESTED mit Uhrzeit in lokaler Gerätezeit, Kodi-/Android-Version und konkreter Beobachtung notieren. Nur anonymisierte feste XCMate-Statusereignisse weitergeben. Private Rohlogs oder URLs/Tokens nicht in GitHub veröffentlichen. Nicht verfügbare echte API-/Netzwerk-/Hardwarefälle offen lassen.
