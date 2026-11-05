# XCMate 0.1.29.74 – Android-Abnahme

Stand: Testkandidat, kein Merge, keine Veröffentlichung. Alle folgenden Geräteprüfungen sind **ANDROID_NOT_TESTED**. Host-/Linux-Nachweise sind kein Android-PASS.

## Installation und Schutz

1. Vorhandene Version, Kodi-Version, Box und Skin-Version notieren. Box A unverändert lassen; zunächst nur die vereinbarte Testbox verwenden.
2. Das vollständige Test-ZIP aus diesem Branch und die benachbarte SHA256-Datei beziehen. Hash prüfen. Über Kodi → Add-ons → Aus ZIP-Datei installieren als kumulatives Update installieren. Keine Deinstallation, kein Profilreset, keine Neuinstallation des Komponentenpakets.
3. Erfolgsdialog muss Version .74 und Änderungen anzeigen. Bisherige Portale, Passwörter, Startgruppe/-sender, Favoriten, EPG-Mappings, TMDB-Zugang, Resume und Widgets prüfen. Keine Zugangsdaten oder Rohlogs auf GitHub hochladen.
4. Das Paket verändert keine Skin-XML und keine gespeicherte Widgetverknüpfung. Ein vorhandener .66-Fokusadapter wird ausschließlich nach bewusster Vorschau/Bestätigung aktualisiert: Einstellungen → Experimentell → technischer BINGIE-Widgetdialog → Layout prüfen/vorbereiten. PIN wie bisher. Erst SHA-Prüfung, Backup und Vorschau; bei unbekannter Skinänderung abbrechen. Wiederherstellen muss den eigenen geprüften vorherigen Stand zurückbringen.

## Kurze P0-Prüfung

| ID | Durchführung und erwartetes Ergebnis | Status |
|---|---|---|
| W74-01 | Aussehen und Darstellung → Widgets: genau Live-TV/Startgruppe, Neueste Filme, Neueste Serien direkt als native Quellen erreichbar; keine Slot-/Freischaltungspflicht. | ANDROID_NOT_TESTED |
| W74-02 | In BINGIE manuell hinzufügen, speichern, Home und Kodi-Neustart: alle drei gewählten Quellen bleiben erhalten. Bestehende Positionen/andere Widgets bleiben unverändert. Keine automatische Einrichtung auf alleiniger XCMate-Installation. | ANDROID_NOT_TESTED |
| F74-01 | Optionalen geprüften Adapter nur nach ausdrücklicher Bestätigung anwenden. Live/Filme/Serien per Hoch/Runter, horizontal erste/mittlere/letzte Position; je genau ein Rahmen am tatsächlich fokussierten Item. | ANDROID_NOT_TESTED |
| F74-02 | 1080p und 720p, verschiedene Poster-/Quadrat-/Landscape-Reihen, Hero-Wechsel, manueller Widget-Reload und Kodi-Neustart: keine verschobenen/geisterhaften Rahmen. | ANDROID_NOT_TESTED |
| A74-01 | Mit vorhandenem XMLTV-/Provider-Eventbild Mini-EPG, großen Guide, Details und Home öffnen: dieselbe richtige Sendung/Bildquelle. Fehlendes Bild nicht einer anderen Sendung zuordnen. | ANDROID_NOT_TESTED |
| A74-02 | Mit bewusst freigegebenem eigenem TMDB-Zugang Verbindung/aktiven Bildabruf prüfen. TMDB benötigt beide bisherigen Freigaben; TVmaze bleibt ohne Benutzerentscheidung aus. Ergebniscode und sichtbare Bildfläche getrennt protokollieren. Token nie abschreiben. | ANDROID_NOT_TESTED |
| A74-03 | Eindeutige Serie/Episode über TVmaze bei ausdrücklicher Freigabe prüfen. Sport/Talk/News ohne Beweis darf kein beliebiges Film-/Serienbild bekommen. Attribution/Logo erhalten. | ANDROID_NOT_TESTED |
| A74-04 | Quelle deaktivieren/Opt-out, Netzunterbrechung, Helper nicht verfügbar: klare Diagnose und begrenzter Retry; kein globaler Cache-Reset, keine Endlossuche. | ANDROID_NOT_TESTED |
| H74-01 | Home 15 Minuten ohne Navigation, laufende Hintergrundjobs: Logos, Film-/Seriencover, gültiges Jetzt/Danach bleiben. Screenshot/ Uhrzeit notieren. | ANDROID_NOT_TESTED |
| H74-02 | Gleiches nach 30 Minuten; bekannte aktuelle Sendung darf beim realen Ende korrekt auf nächste wechseln. | ANDROID_NOT_TESTED |
| H74-03 | Gleiches nach 60 Minuten; danach Hoch/Runter, horizontal scrollen, Hero wechseln, manuellen Reload prüfen. Keine ungewollten Fremdsenderbilder. | ANDROID_NOT_TESTED |
| H74-04 | Kurzzeitiger Netzfehler/EPG- oder Katalog-Hintergrundimport: keine Schrumpfung 24→7/23→9 allein wegen Bildstatus/Lesefehler. Echte Löschungen und bewusster Quellen-/Gruppenwechsel müssen dagegen wirksam werden. | ANDROID_NOT_TESTED |
| R74-01 | Live-TV starten, Overlayebenen schließen, einmal Zurück aus Vollbild; .42-Kompatibilitätsmodus unverändert. | ANDROID_NOT_TESTED |
| R74-02 | Filme/Serien/Suche, Fernbedienung, Resume und staffelübergreifendes Autoplay prüfen. Keine Keymap-/Skin-Einstellungen geändert. | ANDROID_NOT_TESTED |
| R74-03 | Upgrade eines deutlich älteren vorhandenen Profils prüfen, ohne Rücksetzen; Daten/Widgets bleiben. Box A erst nach gesonderter Freigabe. | ANDROID_NOT_TESTED |

Je Test **PASS / FAIL / ANDROID_NOT_TESTED** mit Box/Kodi/Skin/Version und tatsächlicher Beobachtung erfassen. Bei FAIL nur bereinigte Diagnosecodes teilen. Ein gefundenes Bild, ein vorhandenes ZIP oder grüne Hosttests ersetzen keinen Sichttest am Android-Gerät.
