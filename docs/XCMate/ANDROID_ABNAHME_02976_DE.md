# XCMate 0.1.29.76 – Hintergrundvorbereitung getrennt von sichtbarer Darstellung

Unveröffentlichter kumulativer Folge-Draft auf main b3024e9620e8924e880a70fc92ca70e4b5a5658b (.75). Die Antwort des Nutzers erlaubt verifizierte Vorbereitung unsichtbarer Zeilen als Freigabe der nächsten Hintergrundphase; sichtbares Rendering bleibt separat nachzuweisen.

Die veröffentlichte .75 und beide Updatekataloge bleiben unverändert. Keine automatische Installation, kein Merge und kein Release dieses Folge-Drafts. Bestehende .75-Abnahmeresultate gelten historisch, nicht als Geräte-PASS für .76.

## Kurze Geräteprüfung

Nur nach bewusster Installation des Test-ZIPs als Update auf dem freigegebenen Testgerät durchführen. Keine Deinstallation, kein Profilreset, keine erneute Widgeteinrichtung. Box A bleibt unberührt. Bestehende BINGIE-Adapterzustimmung bleibt erforderlich; dieses Update aktiviert keinen Adapter automatisch.

| Test | Ablauf und erwartetes Ergebnis | Android |
|---|---|---|
| PREP76-01 | Kodi neu starten, Startseite auf Live-TV stehen lassen. EPG, Logos und Hero bzw. ehrlicher sendergebundener Fallback erscheinen. | ANDROID_NOT_TESTED |
| PREP76-02 | Ohne Filme/Serien zu öffnen Hintergrundvorbereitung abwarten. Erst LIVE_HOME_READY, danach MOVIES_PREPARED, SERIES_PREPARED und REST_WARM_BEGIN. Keine Serien-Massenarbeit vor geprüfter Filmseite. | ANDROID_NOT_TESTED |
| PREP76-03 | Während PREP76-02 Fokus auf Live-TV lassen. Keine Umschaltung oder zweite Leiste; keine MOVIES_VISIBLE_READY/SERIES_VISIBLE_READY vor tatsächlichem Öffnen. | ANDROID_NOT_TESTED |
| PREP76-04 | Filmleiste öffnen. Genau eine aktive Leiste, unveränderte Hero-Höhe, korrekte Cover oder neutrales Ausblenden bei fehlenden Bildern. Erst jetzt MOVIES_VISIBLE_READY. | ANDROID_NOT_TESTED |
| PREP76-05 | Serienleiste öffnen. Erst jetzt SERIES_VISIBLE_READY. Fernbedienung, Fokus und Zurück prüfen. | ANDROID_NOT_TESTED |
| PREP76-06 | Bestehende Portale, Startgruppe, Favoriten, EPG-Zuordnungen, Cover, Resume und Widgetpositionen nach Neustart kontrollieren. Keine Datenveränderung erwartet. | ANDROID_NOT_TESTED |
| PREP76-07 | Bereits deaktivierte bzw. nachweislich leere Medienbereiche dürfen Folgephasen nicht dauerhaft blockieren. Fehlgeschlagener Import darf nicht als leerer Erfolg gelten. Nur bestehende Testkonfiguration verwenden. | ANDROID_NOT_TESTED |
| PREP76-08 | Kurzer Live-TV-Start/Zurück sowie Film-/Serienwiedergabe mit vorhandenem .42-Kompatibilitätsmodus prüfen. Bekannter nativer ARM32-Stop ohne ACK aus #368 bleibt offen. | ANDROID_NOT_TESTED |

PREPARED bezeichnet verifizierte Referenzen/lokale Dateien oder eine neutrale Fallback-Darstellung, keine erfolgreiche Dekodierung durch Kodi. VISIBLE_READY setzt native Control-, Label- und Geometriebeobachtung voraus; endgültige Bild-/Texture-Abnahme erfolgt separat durch native Screenshottests und Android-Prüfung. In beiden Fällen werden keine privaten URLs oder Zugangsdaten protokolliert.
