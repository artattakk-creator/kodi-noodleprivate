# Android-Abnahme XCMate 0.1.29.72 — Issue #355

TX60Pro, Kodi 21.3 ARM32. **Sämtliche Gerätestests zunächst NOT_TESTED.**
Host-/Linux-Kodi-Erfolge sind keine Android-Abnahme. Issue #355 bleibt offen,
bis der echte Provider erfolgreich geprüft wurde. Kein Merge/Release erfolgt.

## Vorbereitung

1. Das geprüfte .72-Test-ZIP mit der beiliegenden SHA256 verwenden. Kodi →
   Add-ons → Aus ZIP-Datei installieren → Paket als vorhandenes Add-on updaten.
   Nicht deinstallieren, kein neues Repository, keinen 48-Komponenten-Installer starten.
2. Im Installations-/Update-Popup Version .72 und die Änderungen kontrollieren.
3. Vorher im vorhandenen Provider Portal-ID, 53 Live-Gruppen/3.357 Sender,
   Startgruppe, Favoriten, EPG, TMDB, Film-/Serienfortschritte und Widgets prüfen.
   Zugangsdaten, Tokens und private URLs nicht in Screenshots/Supporttext übernehmen.
4. XCMate → Einstellungen → Portale/Provider verwalten → **bestehenden Provider**
   öffnen → **Katalog aktualisieren (Filme / Serien)**. Keine neue Verbindung anlegen.

| Test | Schritte und erwartetes Ergebnis | Status |
|---|---|---|
| VOD-01 | Beide Bereiche prüfen. Bei erneut 0/0 müssen echte Leere, API-/Auth-/Netz-/Formatfehler sichtbar unterschieden werden. Kein Erfolg und keine Behauptung „Anbieter hat keine Filme“. Mit dem anderen Player dieselben Kontobedingungen vergleichen. | NOT_TESTED |
| VOD-02 | Gefundene Film-/Seriengruppen auswählen, **Starten**. Fortschritt und Ergebnis mit DB-Readback ablesen. Titel danach direkt unter XCMate → Filme/Serien sichtbar; selbe Portal-ID. | NOT_TESTED |
| VOD-03 | Film-only, Serien-only, beide separat ausführen. Live-Senderzahl, Live-Gruppen, Startsender/Startgruppe und EPG unverändert; kein Live-/EPG-Neuimport. | NOT_TESTED |
| VOD-04 | Bei bereits auftretenden Anbieterfehlern Code notieren; keine Zugangsdaten ändern oder absichtlich kaputte Konten erzeugen. Keine leere/fehlerhafte Antwort darf alte Titel löschen. Paging/Netztrennung sind im Hosttest abgedeckt. | NOT_TESTED |
| VOD-05 | Identische Auswahl zweimal nachscannen. Keine Duplikate; „unverändert“ nachvollziehbar, Favoriten/Resume behalten. Neue Titel bei späterem Anbieterzuwachs ergänzen. | NOT_TESTED |
| VOD-06 | Während eines größeren Imports **Abbrechen/Zurück**. GUI bleibt bedienbar; nur vorher vollständig geprüfte Gruppen dürfen sichtbar sein. Später erneut öffnen und wiederholen. Hard-Kill/ENOSPC/readonly wurden isoliert getestet und sollen am produktiven Gerät nicht künstlich erzwungen werden. | NOT_TESTED |
| VOD-07 | Neue Kategorien prüfen. Checkboxen ändern/abbrechen, vorhandene Auswahl bleibt erhalten. Erst bestätigtes Starten aktiviert erfolgreich importierte Gruppen; bereits bestehende andere Gruppen werden nicht deaktiviert. | NOT_TESTED |
| VOD-08 | Sichere Diagnose mit `[XCMate][VODSYNC]`, Phase/Code/Zahlen prüfen. Keine Hosts, Tokens, Zugangsdaten oder Titel in diesen Diagnoseereignissen. Private Sicherung/Manifest vorhanden; keinen Restore am produktiven Gerät ausführen. | NOT_TESTED |
| VOD-09 | Live-TV Start/Zurück, großer EPG/Mini-EPG, Suche, Film-/Serien-Widgets mit Covern, Navigation, Autoplay/Staffelwechsel, Resume, EPG-Zuordnungen, TMDB und alle 48 Komponenten unverändert funktionsfähig. Keine Skin-/Keymapänderung. | NOT_TESTED |
| VOD-10 | Kodi normal neu starten. Gleiche Provider-ID, 3.357 Live-Sender, neue Filme/Serien, Auswahl und Metadaten persistent. Aktuelle Titel abspielen und Fortschritte kontrollieren. | NOT_TESTED |

## Rückmeldung

Pro Test **PASS / FAIL / NOT_TESTED**, installierte Version, gefundene/gewählte/
veröffentlichte Gruppen und DB-Readback je Bereich nennen. Bei Fehlern Phase und
Diagnosecode notieren. Nicht ungeprüft Rohlogs öffentlich hochladen.

Ein teilweise abgeschlossener Nachscan wird als PARTIAL ausgegeben. Eine
abgebrochene oder fehlerhafte Gruppe ist kein erfolgreicher Vollimport. Bei
Speichermeldung keine Bilder/Datenbanken löschen und keine Reserve deaktivieren;
zuerst den konkreten sicheren Fehlercode auswerten.
