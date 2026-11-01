# XCMate .65 – Android-Abnahme Box B

Alle folgenden Gates zunächst ANDROID_NOT_TESTED. Frühere .64-Fehler bleiben OPEN. Box A nicht anfassen. Keine Deinstallation, kein Downgrade, kein Profil-/Cover-/EPG-/Skinreset und kein Widget-Neuverknüpfen.

.65 wird nach bestandenen technischen Gates über das reguläre GS-Media-Repository angeboten. In Kodi Aktualisierungen prüfen und als normales Update installieren. Versionsanzeige und Erfolgspopup samt Änderungen kontrollieren.

| Gate | Ausführung / erwartetes Ergebnis | Status |
|---|---|---|
| A65-01 | Installierte .65, Kodi21.3/Android, Repository und erhaltene Profile prüfen | ANDROID_NOT_TESTED |
| A65-02 | Zuerst einmal Tokenimport: Quelle/Format → private Zielprüfung → Temp/Commit → Endprüfung. USB und SMB getrennt, Quelle entfernen, Neustartpersistenz; maskierte manuelle Option. Nur echter privater HTTPS-Erfolg zählt als TMDB_OK. Bei Fehler Subcode/errno notieren, kein Import-Marathon. Sicherung/Recovery nur nach gesonderter bewusster Bestätigung | ANDROID_NOT_TESTED |
| A65-03 | Filme → Gruppen- und Indexstatus prüfen. Adult Zone anhand tatsächlicher Kategorie-ID/aktivierter Auswahl prüfen. Aktueller positiver Providercount muss lokal/Anzeige erreichbar sein; SOURCE_EMPTY, SOURCE_FILTERED, Deaktiviert und CACHED unterscheiden. Keine echte Titel-/Zugangsdatenliste veröffentlichen | ANDROID_NOT_TESTED |
| A65-04 | Film- und Seriengruppen unabhängig paginieren, insbesondere >100 Titel. Anzahl/IDs ohne Verlust/Duplikate, neu aktivierte Gruppe, gezielter Nachimport/Abbruch/Wiederholen. Widgets bleiben bewusst begrenzte Neuheiten-Auswahl | ANDROID_NOT_TESTED |
| A65-05 | Kodi-/Service-Neustart mit abgeschlossenen und ausstehenden Jobs; erhaltene Generationen, begrenzter Retry und Lease-Wiederaufnahme, keine doppelten Importe | ANDROID_NOT_TESTED |
| A65-06 | Film-/Serienwidget echte Cover, Scrollen/Details/Wiedergabe, genau ein passender Fokusrahmen, vorhandene Quellen unverändert | ANDROID_NOT_TESTED |
| A65-07 | Kleine 142×72-Live-Buttons, schneller WELT-Start und einmal Zurück im unveränderten .42-Modus. DMAX/WELT/VOX/Nitro mit tatsächlich vorhandenem EPG im Hero/Player vergleichen; warmes Jetzt/Danach Ziel ≤1 s ab sichtbarer Oberfläche. Warm/kalt und DB/GUI getrennt messen, keine Fremdsenderdaten | ANDROID_NOT_TESTED |
| A65-08 | Portale/Passwörter, Gruppen, Favoriten, Wizard, manuelle EPG-Zuordnung, Bilder, Resume/Autoplay und ursprüngliche Grafiken erhalten. Box A unverändert | ANDROID_NOT_TESTED |

## Statusoberfläche

In Filme und Serien auf der Kategorieöffnung oder einer Kategorie das vorhandene Kontextmenü (Menütaste/Lang-OK) öffnen und „Gruppen- und Indexstatus prüfen“ wählen. Suchmaske und XML bleiben bytegleich. Er liest ohne Provider-Netzaufruf. Kategorien sind paginiert; ausgewählte Gruppe zeigt lesbare Herkunfts-, Auswahl-, Import- und Bestandswerte. Providerzahl „nicht ermittelt“ bedeutet keine verifizierte aktuelle Remoteantwort. Ein vorhandener lokaler/offline Cache beweist keine aktuelle Providerverfügbarkeit.

„Gezielt nachimportieren / wiederholen“ beauftragt nur die bewusst ausgewählte aktive Xtream-Gruppe. Deaktivierte Gruppen werden nicht still aktiviert. „Nachimport dieser Gruppe abbrechen“ erhält alle anderen Jobs und den letzten gültigen Bestand. Bei Speicher-/Zugriffsfehlern kein Datenreset.

## Datenschutz

Keine Token, privaten Pfade, Anbieter-URLs, Passwörter, Rohlogs oder echten privaten Katalogtitel an GitHub senden. Für Diagnose genügen Version/Gerät, Zeit, feste Phase/Subcode/errno, anonymisierte Kategorie-/Senderkorrelation und Counts. Keine Freigabe für automatische Geräte-/Skinänderungen.
