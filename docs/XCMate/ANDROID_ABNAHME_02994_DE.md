# Android-Abnahme XCMate 0.1.29.94

**Gesamtergebnis: ANDROID_NOT_TESTED.** Kodi 21.2/21.3 und RK3528 ARM32 separat prüfen. Host-/Linux-Kodi-Ergebnisse ersetzen keine Geräteabnahme. Kein regulärer/Pilot-/NeoDark3-Release und kein Merge ohne Freigabe.

## Vorbereitung ohne Zurücksetzen

Kodi-Version, XCMate-Version und Gerät notieren. Mit geschlossenem Kodi eine getrennte Sicherung des vorhandenen Profils und Add-on-Ordners erstellen. Bestehende Profile nicht neu anlegen. Keine Schlüssel, Passwörter oder Rohlogs auf GitHub hochladen. .90 und .93 bleiben unveränderte Archivstände. Das .94-ZIP aktualisiert die bestehende Add-on-ID `plugin.video.xtreammate`; Installer 0.5.26 bleibt bestehen.

ZIP aus dem Draft-PR herunterladen, SHA256 gegen die beiliegende Datei prüfen. In Kodi „Aus ZIP-Datei installieren“ wählen. Kein 48-Komponenten-Installer, keine Deinstallation. Installations-Popup muss .94 und die neuen EPG-/Gruppenänderungen anzeigen. Ein installiertes Paket ist noch kein erfolgreiches EPG- oder Bild-Rendering.

## Prüfmatrix

Alle folgenden Ergebnisse zunächst **ANDROID_NOT_TESTED**; je Gerät PASS/FAIL mit Zeitpunkt und datensparsamem Diagnosecode ergänzen.

| ID | Ablauf und erwartetes Ergebnis |
|---|---|
| BASE94-01 | .93 → .94: Provider, Passwort, Token, Favoriten, manuelle EPG-/Bildzuordnungen, Resume und persönliche Widgets bleiben erhalten. |
| BASE94-02 | Älteres eingerichtetes Profil separat prüfen: kein Reset, keine neue Portal-ID, Startgruppe und Startsender unverändert. |
| CFG94-01 | Neuer Xtream-Testaccount ohne externe EPG-Auswahl: Anbieter-EPG und globale Freigabe aktiv, tatsächliche Adapter-Adresse; keine erfundene URL. |
| CFG94-02 | EPG bewusst abschalten; Kodi neu starten: bleibt aus, Live-TV weiterhin bedienbar. |
| CFG94-03 | DE Kaimandura + DE/AT/CH EPGShare01 nachrüsten; erneute Auswahl erzeugt keine Dubletten. |
| CFG94-04 | Quelle bei bewusst global abgeschaltetem EPG aktivieren: Bestätigung ablehnen → bleibt aus; bestätigen → dauerhaft ein. |
| JOB94-01 | EPG-Manager → Jetzt aktualisieren: Auftragskennung, erst „Wartet“, nach tatsächlicher Dienstübernahme Bestätigung innerhalb 15 s. Ohne Dienst klarer Fehler, kein laufender Spinner. |
| JOB94-02 | Je Quelle reale Downloadbytes, XMLTV-Sender/Programme, Zuordnungen, Zwischenstand, Commit und Readback prüfen. Prozent nur bei bestätigter Gesamtgröße. |
| JOB94-03 | Während des Imports Quellenwahl und Fokus bewegen; keine zyklischen Listenneuaufbauten und kein Fernbedienungsstillstand. |
| JOB94-04 | Manager schließen und erneut öffnen: Auftrag läuft weiter, gleiche Auftragskennung und aktueller Stand. Schließen ist kein Cancel. |
| JOB94-05 | Während Download und Parser über „Import abbrechen“ abbrechen. Alte Daten bleiben lesbar; kein falsches READY, Spinner endet. |
| JOB94-06 | Wiederholen/Einrichtung fortsetzen: neue Quelle bzw. neuer sicherer Streamlauf. Setup überspringt ausschließlich unabhängig erneut geprüfte vollständige Quellen. Kein behauptetes HTTP-Byte-Resume. |
| JOB94-07 | Dienst/Kodi während eines Testimports regulär beenden; Neustart zeigt Unterbrechung oder fortsetzbare Einrichtung, kein doppelter Import. |
| JOB94-08 | Offlinequelle, ungültiges XML/GZIP und Quelle ohne passende Kanäle prüfen: unterschiedliche Diagnosen, NO_CHANNEL_MATCH erkennbar, funktionierende andere Quellen/LastGood erhalten. |
| GC94-01 | Zwei tägliche Folgeimporte: 7 Tage Historie und bis 20 Tage Vorschau nur soweit vorhanden; Zeiten/Quelle/Bildreferenzen stichprobenartig vergleichen. |
| GC94-02 | Gleiche Volume-ID und echte freie Bytes vor/nach prüfen. Streaming erzeugt keine vollständigen Raw-Archive: 0 Raw-Löschbytes ist korrekt. Unbekannte Dateien, manuell gewählte XMLTV-Dateien und letzte gültige Sicherung bleiben erhalten. |
| GC94-03 | SQLite-BUSY/niedrige Reserve: begrenzter Fehler/Retry, kein blindes VACUUM, keine gelöschten aktiven WALs, kein erfundener Platzgewinn. |
| GROUP94-01 | Unterhaltung und 4K aus Mini-EPG auswählen: lokale Sender sofort bzw. LOADING_GROUP → GROUP_READY. Dies bei deaktiviertem und leerem EPG wiederholen. |
| GROUP94-02 | >100 Sender: Seite 2, letzten Sender auswählen und tatsächlich wiedergeben. EPG darf keine Wiedergabevoraussetzung sein. |
| GROUP94-03 | Schnell A → B → A; kein verspätetes Ergebnis der falschen Gruppe/des falschen Portals. Fokus und Logos korrekt. |
| GROUP94-04 | Coldboot, frisch aktivierte Gruppe, unvollständiger und vollständiger Hauptindex, Offlineanbieter mit lokalem Bestand: keine falsche Leeranzeige. |
| REG94-01 | Live-Startsender, Gruppenwechsel und 5× BACK/Stop testen. Bei Freeze sofort stoppen und echte Android-Evidenz sichern; Decoderproblem bleibt eigener Fehlerfall. |
| REG94-02 | Film, Serie, Autoplay/Resume und Rückkehr unverändert. Spontanen Prozessabbruch getrennt von einem durch BACK ausgelösten Freeze erfassen. |
| REG94-03 | Lokale Logos, Live-Hero, Filme, Serien, Im Kino, Disney, Trend und MP3-Reihe sowie persönliche Fremdwidgets nach Coldboot prüfen. |
| REG94-04 | XMLTV-Bild aus Mini-EPG auch im Detail; manuelle TMDB/TVMaze-Auswahl speichern, unabhängig wiederlesen und wirklich anzeigen. Speicherung und sichtbare Textur getrennt beurteilen. |
| REG94-05 | Mehrere Coldboots: Kodi-App-Präsenz, Token und Portal weiterhin erhalten. Ohne logcat/ExitInfo keinen Android-Systemfehler als behoben melden. |

## Diagnose und sicherer Rückweg

Bei Fehlern Zeitpunkt, Geräte-/Kodi-/Add-on-Version, Auftragskurzkennung, Quelle und Phase notieren. Den Aktualisierungsbericht des EPG-Managers verwenden. Keine privaten XMLTV-/Stream-URLs, SMB-Verbindungen oder Token veröffentlichen.

Bei einem EPG-Problem lässt sich die betroffene Quelle oder EPG-Freigabe ausdrücklich deaktivieren; bestehende lokale Daten und Live-TV bleiben erhalten. Kein Downgrade und keine Datenbanklöschung als automatische Reparatur. Eine Profil-/Add-on-Wiederherstellung erfolgt ausschließlich aus der vorher geprüften getrennten Sicherung und erst nach Nutzerfreigabe. Die .94 ergänzt private Kontroll-/Statusdateien, ohne eine destruktive Schema-Migration der vorhandenen Datenbanken.
