# XCMate 0.1.29.4 – Android-/IR-Test und manuelle Installation

Stand 21.10.2026. **Alle Gerätetests NOT_RUN.** Ziel: Android-TV ARM32, Kodi **21.3 Omega**, zunächst Estuary, danach Titan BINGIE MOD. Keine Geräteabnahme aus Cloud-/Mocktests ableiten. [Geprüfte Dateien und Prüfsummen](HOTFIX_0294_SETUP_SCAN_SAVE_DE.md), [vollständiger Arbeitsauftrag](CODEX_AUFTRAG_0294_SETUP_SCAN_SAVE_DE.md).

## Sicherung und Installation

1. Kodi sauber beenden und sicherstellen, dass es nicht mehr schreibt. Gesamtes tatsächliches `special://userdata/addon_data/plugin.video.xtreammate/` einschließlich versteckter Dateien/Unterordner und **DB/WAL/SHM zusammengehörig** sichern. Auch konfigurierte externe Bild-/Metadaten-/Cacheordner und eigene Keymaps sichern. Dateianzahl/Größen und möglichst SHA-256 vergleichen. Android-Profilpfade können abweichen; keine einzelnen gerade schreibenden SQLite-Dateien herauskopieren.
2. Keine App-Daten löschen, Konten zurücksetzen, Deinstallation oder Kodi-Reset. Vorhandene Accounts, Live-/Film-/Seriengruppen, EPG-Quellen, Mappings, Favoriten/Resume/Startsender dokumentieren; Zugangsdaten in Sicherung geschützt aufbewahren und nicht veröffentlichen.
3. Geprüfte **0.1.29.4-Test-ZIP** aus neuem Draft-PR/Actions beziehen. Äußeres CI-Artefakt entpacken; ausschließlich die innere `plugin.video.xtreammate-0.1.29.4.zip` verwenden. Bei ZIP direkt aus GitHub „Download raw file“, kein HTML speichern. Größe **382936 Bytes**, SHA-256 `7b914eb02756751978df5b80f0cf574760fc9d2215cb06ed4b7fe9123534f69f`.
4. GS-Media-/Neo-Dark-Onlinequelle kann diese Datei manuell bereitstellen/auswählen; hier wird **keine produktive Quelle umgestellt oder befüllt**. Test-URL im Branch: `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/fix/xcmate-0294-setup-scan-save/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.4.zip`. HTTP/Hash vor Gerätetest prüfen; keine automatische Repositoryaktualisierung für diesen Kandidaten.
5. Kodi → Add-ons → Aus ZIP-Datei installieren → Datei auswählen. Bestehende Add-on-ID `plugin.video.xtreammate` behalten, Version **0.1.29.4 / Service-Build 29** prüfen, Kodi neu starten. Installierter anderer Skin, globale Keymap und andere Add-ons bleiben erhalten.

## Verbindliche Fälle

| ID | Aktion und Soll | Status |
|---|---|---|
| A01 | Update über 0.1.29.3, Bestandskonten/-gruppen/-quellen und gespeicherten Startsender vergleichen; keine automatische Neuanlage/Vollimporte | NOT_RUN |
| A02 | Account mit gültiger legitimer Xtream-Testquelle anlegen. Bei Discovery nur sichtbares Abbrechen fokussiert; keine leere Liste im Fokus | NOT_RUN |
| A03 | Falsche Anmeldung/Server nicht erreichbar: verständlicher sicherer Fehlercode, Erneut versuchen und Abbrechen sichtbar; keine Zugangsdaten im Log | NOT_RUN |
| A04 | Reiter Live-TV/Filme/Serien oben einzeln per Links/Rechts/OK erreichen, zwischen allen hin und zurück. Aktiver Reiter bleibt markiert, wenn Fokus in Liste/Buttons liegt | NOT_RUN |
| A05 | Checkboxen tatsächlich als PNG an/aus, auch ohne fokussierte Zeile klar erkennbar. Fokusbalken volle Breite, Schrift/Checkbox kontrastreich unter Estuary und BINGIE | NOT_RUN |
| A06 | Hoch/Runter scrollen, Checkbox bei Index über 99/100/101 und Ende umschalten. Keine Sprünge zum Anfang, keine andere Scrollposition; Bereichswechsel erhält je eigene Liste/Cursor | NOT_RUN |
| A07 | Gruppen getrennt an-/abwählen, Alle auswählen/Alle abwählen; Zähler korrekt. Bereits abgewählte Gruppen bleiben aus, keine Auto-neu-Aktivierung | NOT_RUN |
| A08 | Quelle mit leerem Bereich: „Keine Kategorien vorhanden“, Zähler 0, Reiter/Weiter/Zurück/Abbrechen weiterhin per IR erreichbar | NOT_RUN |
| A09 | Untere Buttons über Links/Rechts/Hoch/Runter sichtbar erreichen, OK genau einmal. Einzelne IR-Impulse und lange Wiederholung getrennt prüfen; kein doppeltes Umschalten | NOT_RUN |
| A10 | Ohne Auswahl Weiter: XM-SETUP-SELECT, korrekt bedienbarer Zustand, kein Account veröffentlicht | NOT_RUN |
| S01 | Mindestens 2400 Sender und getrennte Film-/Seriengruppen selektiv importieren. Bereich, Gruppe sowie echte gelesen/gespeichert-Zahlen beobachten; während unbekannter Dauer kein Prozentversprechen | NOT_RUN |
| S02 | Anbieter/gedrosselte Testquelle mit tatsächlicher Dauer >5, >10 und möglichst >20 Minuten bei fortlaufendem Fortschritt: kein 300-s-Gesamtabbruch | NOT_RUN |
| S03 | Serververbindung unterbrechen/Read-Stall: endlicher Fehler über Netzwerk-/Inaktivitätsgrenzen; Retry/Abbruch bedienbar, kein dauerhaft blockiertes Kodi | NOT_RUN |
| S04 | Discovery/Scan/optionalen XMLTV-Import abbrechen, auch bei großem Katalog; GUI schließt bedienbar, kein später wieder geöffnetes Fenster/kein unvollständiger Account | NOT_RUN |
| S05 | Zusammenfassung → Zurück → Gruppen abwählen/andere wählen → erneut scannen. Alte Staging-Inhalte verschwinden; nur aktuelle Auswahl wird gespeichert | NOT_RUN |
| P01 | Speichern genau einmal: UI bleibt bedienbar; Fenster erst nach erfolgreichem permanentem Readback schließen. Kein Kodi-Absturz, keine hängenden Worker | NOT_RUN |
| P02 | Schnelles mehrfaches OK/Speichern sowie Back beim Save: kein Doppelaccount, kein mehrfacher Save; Abbruch vor Veröffentlichung erzeugt keinen Account. Bereits vollständig atomar veröffentlichter Save ist kein halber Import | NOT_RUN |
| P03 | Account, Portaltyp/-konfiguration, getrennte Gruppen und tatsächliche Live-/Film-/Serienzahlen erneut aus Profil prüfen; alte Accounts/Favoriten/EPG bleiben unverändert | NOT_RUN |
| P04 | Optionaler EPG: Einstellungen, Quellen und Mappings erhalten; importierte Daten auch nach Neustart aus dauerhaftem Guide verfügbar, einschließlich Sender außerhalb des 256er Cache-Warmstarts | NOT_RUN |
| P05 | Kodi vollständig beenden, Prozessende prüfen, neu starten: neuer Account vorhanden, gleiche Gruppen/Zahlen, abgewählte Gruppen bleiben aus, konkrete Sender/Filme/Serie nutzbar | NOT_RUN |
| P06 | Nur im gesicherten Testprofil kontrollierten Speicher-/Schreibfehler erzeugen. Verständlicher Code statt Erfolg/Absturz; neue ID wird zurückgenommen, alte Account-/Quellkonfiguration bleibt | NOT_RUN |
| F01 | Live-Freeze: erstes OK Info, zweites OK/Runter Controls, Links Sender, weiteres Links Gruppen, Hoch/Runter Zap, Back Ebenen schließen, Menu – identisches Verhalten | NOT_RUN |
| F02 | Startsender/-gruppe, Now/Next aus bestehendem EPG, Favoriten/Resume, TMDb Helper, xVAULT und BINGIE-Funktionen vor/nach vergleichen; globale Keymaps unverändert | NOT_RUN |
| F03 | 720p/1080p/4K: Fokus-/Button-Geometrie, Safe Area, Text/Checkboxen; Start-/Scan-/Savezeit und RAM erfassen, keine Performanceabnahme aus Cloudzeiten ableiten | NOT_RUN |

Je Fall Datum/Uhrzeit, Gerät/Android/Kodi/Skin/Core, Ausgangskontoanzahl, Gruppen und tatsächliche Zahlen, genaue IR-Sequenz, Dauer/RAM, Soll/Ist, Fehlercode und Ergebnis dokumentieren. Kein echtes Passwort, Token oder Stream-URL in Screenshots/öffentlichen Logs.

## Falls Kodi erneut abstürzt

Keine Profil-/Cachelöschung als Reparatur. Uhrzeit/letzte Aktion notieren, `kodi.log` **und `kodi.old.log`** sowie vorhandenen Android-Crashauszug sichern, vor Weitergabe bereinigen. Prüfen, ob der neue Account bereits vollständig gespeichert ist; nicht blind mehrfach neu anlegen. Ohne Crashlog keine alleinige native Ursache behaupten. Die Worker-GUI-Regressionsursache ist im Code belegt und korrigiert; der konkrete Android-Crash bleibt bis zur Gegenprobe offen.

## Rückkehr und regulärer Updateweg

Vergleichsversion **0.1.29.3** ist unverändert gesichert: 376662 Bytes, SHA-256 `3c1f54a6d4ffdf6c069c483ade06867c18ff528414724a13656011f3d30189af`. Bei Bedarf Kodi beenden und diese ZIP über dieselbe ID manuell installieren. Für den exakten alten Datenstand vollständige zusammengehörige Sicherung inklusive externer Caches/DB/WAL/SHM zurückspielen; keine einzelnen DB-Dateien mischen. Neue korrekt gespeicherte Accounts nicht ungefragt löschen.

Erst nach Android-Ergebnissen entscheidet der Benutzer über Merge und einen **separat freigegebenen** regulären GS-Media-/Neo-Dark-Repositoryupdate. Danach dessen tatsächlichen Index/Hash und angebotene Version am Gerät prüfen. Dieser Auftrag führt keinen Merge, kein Release und keine automatische Produktivveröffentlichung aus. PR #52/0.1.29.3 und PR #50/0.1.30 bleiben als getrennte Vergleichs-/Entwicklungslinien erhalten.
