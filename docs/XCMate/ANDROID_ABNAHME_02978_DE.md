# Android-Abnahme XCMate 0.1.29.78

Alle Zeilen beginnen mit **ANDROID_NOT_TESTED**. Die .77-Befunde bleiben historisch FAIL. Host/Linux-Screenshots sind keine Android-Abnahme. Kein Reset, keine Deinstallation, keine Neuinstallation und keine zusätzlichen Speicher-/Löschtests. Installer 0.5.26 nicht starten. Zuerst nur die bisherige Testbox aktualisieren; die ältere eingerichtete Box nicht für Reparaturversuche verändern.

## Reguläres Update nach Veröffentlichung

Kodi → Add-ons → Meine Add-ons → Add-on-Repository → vorhandenes GS Media Repository bzw. GS Media Pilot → Kontextmenü „Nach Aktualisierungen suchen“. Danach XCMate → Informationen → Aktualisieren → **0.1.29.78** aus dem vorhandenen Kanal. Falls Kodi noch .76/.77 meldet, Kanalindex erneut prüfen; nicht deinstallieren. NeoDark3: vorhandene Quelle öffnen und das explizite .78-ZIP wählen; eine Installation aus ZIP ist ein kumulatives Update über die bestehende Installation.

Die drei Downloadpfade und die endgültige Prüfsumme stehen in TESTBERICHT_02978_DE.md. Das Installations-Popup muss „Installation erfolgreich“, Version .78 und die aktuellen Änderungen zeigen. Anschließend Kodi regulär neu starten, falls die Oberfläche das verlangt.

| Test | Schritte und konkreter PASS | Status |
|---|---|---|
| HOME78-01 | Bestehende Widget-Reihen vor/nach Update vergleichen, einschließlich „Neu im Kino“, Positionen, Quellen und Space Blue. Keine Defaults/Verknüpfungen verloren. | ANDROID_NOT_TESTED |
| HOME78-02 | BINGIE Home ohne vorherige Senderwiedergabe öffnen. Lokales Jetzt/Danach, Senderlogo, Fortschritt und korrektes Sendungsbild erscheinen. Kein Non-Existent Control/fehlende XCMate-Variable; FILES_VERIFIED allein zählt nicht. | ANDROID_NOT_TESTED |
| HOME78-03 | 88 Sender bzw. vollständige konfigurierte Startgruppe durchgehen. Fester Hero, genau aktive Leiste, exakter Fokus; kein Start bei Fokuswechsel, OK startet genau den Sender. | ANDROID_NOT_TESTED |
| HOME78-04 | Filme und Serien sowie Kino-/eigene/fremde Reihen erreichen. 24/24 vorhandene Titel/Cover bleiben stabil; Fokuswechsel und Rückkehr lösen kein READY/PARTIAL-Flackern aus. | ANDROID_NOT_TESTED |
| HOME78-05 | Gespeicherte Widgetkonfiguration und Cover nach Kodi-Neustart erneut prüfen. Keine mehrfachen Skinreloads; erneutes Öffnen verursacht keinen Patch-/Rebuild-Zyklus. | ANDROID_NOT_TESTED |
| IMG78-01 | Bei drei bekannten realen Sendungen Bild und Identität im BINGIE-Hero, großen EPG-Details und Mini-EPG-Details vergleichen. Richtiges sichtbares Bild und passende Beschreibung; URL_READY allein ist kein PASS. | ANDROID_NOT_TESTED |
| IMG78-02 | Vorhandenen TMDB-Zugang ohne Neuimport weiterverwenden, bewusste Opt-outs respektieren; keine Tokenwerte in Screenshots/Logs zeigen. Film-/Serienproviderbilder bleiben vorrangig. | ANDROID_NOT_TESTED |
| NAV78-01 | Alle Hauptmenüs und Widgetebenen mit IR-Fernbedienung öffnen/schließen; OK/Links/Rechts/Oben/Unten/Back prüfen. Kein ANCHOR_TIMEOUT/unsupported protocol/verschobener Fokus. | ANDROID_NOT_TESTED |
| EXIT78-01 | Startsender → einmal Live-TV-Zurück. Zuerst diesen Test abnehmen; Stop-ACK und bedienbare Rückkehr ohne zweiten Stop. | ANDROID_NOT_TESTED |
| EXIT78-02 | Nach EXIT78-01 PASS: Film und Serie je einmal verlassen. Vorherige Ansicht/Fokus, Resume, manuelles Next und Autoplay inklusive Staffelwechsel prüfen. | ANDROID_NOT_TESTED |
| EXIT78-03 | Erst danach 5 und 20 Live-/Film-/Serienzyklen. Bei langsamem Stop unterscheidet Diagnose wartendes ACK und echte Rückkehr. Fremder Dialog/Player wird nicht geschlossen/gestoppt. | ANDROID_NOT_TESTED |
| DB78-01 | Falls „Neu im Kino“ leer bleibt: tatsächliche gespeicherte Quelle und read-only Kodi-Schemadiagnose erfassen. Fehlende MyVideos131-Views getrennt melden, keine DB reparieren/löschen. | ANDROID_NOT_TESTED |
| REG78-01 | Provider, Zugang, Gruppen, Favoriten, EPG-Mappings, Suche, Resume, Autoplay und persönliche Kodi-/Skin-Einstellungen vergleichen. Installer weiterhin .5.26. | ANDROID_NOT_TESTED |

Bei FAIL Test-ID, sichtbares Verhalten, Gerät/Kodi-Version und Zeitpunkt melden. Private Rohlogs/Provider-URLs/SMB-Daten/Token nicht auf GitHub veröffentlichen. Unbekannter Skin-Hash oder nicht bestätigte Laufzeitkontrolle bleibt BLOCKED/NOT_TESTED, niemals künstlich PASS.
