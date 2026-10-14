# Übergabeblock für einen neuen XCMate-Chat

Wir setzen mein Kodi-/IPTV-Projekt **XCMate** (GS Media) fort. Arbeite direkt im GitHub-Repository https://github.com/artattakk-creator/kodi-noodleprivate auf `main`.

**WICHTIG: Bitte zuerst diese GitHub-Dateien lesen:**
1. `docs/XCMate/README.md`
2. `docs/XCMate/PROJECT_HANDOFF_DE.md`
3. `docs/XCMate/ROADMAP_AND_QA_DE.md`
4. `docs/XCMate/SERIES_PROGRESS_SPEC_DE.md`
5. `docs/XCMate/DESIGN_SYSTEM_DE.md`

**Letzter geprüfter Projektstand am 14.10.2026:** XCMate 0.1.12, GS Media Kodi Repository 1.7.0. Der angezeigte Name lautet XCMate. Die technische Kodi-ID `plugin.video.xtreammate` bleibt bewusst unverändert, damit automatische Updates und Kodi-Profil/Zugangsdaten erhalten bleiben.

**Zielgerät:** Android-Kodi-Box mit Titan BINGIE MOD. **Dringend P0:** Startsender springt auf dem echten Gerät teils weiterhin in eine leere Kodi-Verzeichnisansicht; Links/Hoch/Runter/OK, Senderliste und Player-Zusatzleiste funktionieren auf dem Gerät bislang nicht zuverlässig. 0.1.10 trennt Kodi-Playable-`setResolvedUrl` und direkten `RunPlugin`-Autoplay-Start, korrigiert die OK-Funktion im Player-OSD und wurde in GitHub CI gebaut. Es gibt weiterhin keine bestätigte erfolgreiche Android-Gerätetest-Rückmeldung. Bitte die Diagnose und Kodi-Logs analysieren, nicht blind Erfolg behaupten.

**Neue verbindliche Anforderung:** Bei Serien Gesehen-Status und Fortschritt pro Folge dauerhaft speichern; nach Abbruch an der letzten Position fortsetzen; optional automatisch nächste Folge in korrekter Staffel-/Folgenreihenfolge abspielen; „Weiterschauen“-Ansicht. **Noch nicht implementiert.** Details, Datenmodell und Akzeptanztests stehen in `SERIES_PROGRESS_SPEC_DE.md`.

**Design-Freeze:** Nutzer hat silbernes **XCMate**-Logo vor dunklem Planeten und großflächige monochrome Weltraumgrafik ausdrücklich freigegeben. Graues („Slate“) UI ist Standard, weitere UI-Farben sollen später frei wählbar werden. Freigegebene Quellbilder: `grafik.png` und `imagegen.png` aus dem vorherigen Chat. Bitte in `DESIGN_SYSTEM_DE.md` prüfen und nichts eigenmächtig durch anderes Branding ersetzen. Ob Grafik-Binärdateien schon auf GitHub liegen, gesondert verifizieren.

**Weitere Funktionen:** Xtream/M3U/Stalker, getrennte Live-/Film-/Seriengruppen per Checkbox, Cache-first, XMLTV-EPG mit zusätzlichen Quellen und manueller Zuordnung, Jetzt/Danach, Film-/Serienbeschreibungen und Trailer, BINGIE-Widgetordner. „Im Repo implementiert“ ist nicht gleich „auf Android geprüft“.

**Arbeitsweise:** Immer tatsächlichen GitHub-Head und Quellcode lesen, Problem reproduzieren, Änderung und Tests erstellen, Build abwarten, ZIP und `addons.xml` kontrollieren und Status in den GitHub-Übergabedokumenten fortschreiben. Keine Zugangsdaten oder private IPTV-URLs posten/committen; möglichst Repository-Update statt manueller Neuinstallation.

Bitte beginne mit einem kurzen GitHub-Statuscheck und schlage den nächsten klar abgegrenzten Schritt vor.

**Neu – verifizierte TiviMate-Fernbedienung (14.10.2026):** 10 Nutzerfotos aus TiviMate 5.3.3 liegen vor (Player- und EPG-Zuordnungen inkl. Langdruck sowie Suchoptionen). **Verbindliche Referenz**: `docs/XCMate/TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md`. Der Draft-PR #3 mit `tivimate_keys.py` und Tests hat grünes GitHub-CI, ist aber **noch nicht in Kodi aktiviert oder als Add-on-Version veröffentlicht**. Weitere Einstellungsfotos werden nach und nach geliefert und müssen ergänzt werden. Funktional TiviMate-ähnlich nachbauen, keine proprietären Assets/Quellen übernehmen. Die Stabilisierung von Startsender und Android-Fernbedienung (P0) bleibt offen.

**Weitere zehn Bilder (14.10.2026):** TV-/EPG-/Film-Ansichten und die
Player-Farbtasten (Rot/Grün EPG, Gelb Info, Blau Einstellungen) wurden
bildgenau erfasst in
`docs/XCMate/TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md`.
Die Bedienungsreferenz ist **kein** Kodi-Screenshot-Nachbau und wurde
noch nicht aufs Android-Gerät ausgerollt. Weitere Bilder ergänzen;
das XCMate-eigene Design-System und das profilwahrende Vorgehen bleiben
verbindlich.

**Dritte Fotoserie (14.10.2026), TiviMate Einstellungen:** Zehn weitere
Fotos zu Einstellungsrubriken, Allgemein, Wiedergabelisten, EPG und Optik
wurden als verbindliche UI-/Funktionsreferenz dokumentiert:
`docs/XCMate/TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md`
und `docs/XCMate/TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json`.
Gezeigte Schalterzustände sind eine individuelle TiviMate-Konfiguration,
**nicht ungefragt auf bestehende Kodi-Daten übertragen**. Fotos zeigen
eine private XMLTV-URL: nur redigierte Platzhalter öffentlich verwenden.
Android-Boot/Wake/Home-PiP sind Host-abhängig; XCMate Default bleibt Slate-Grau.
Die Menüoberflächen sind **noch nicht implementiert**, Add-on-Release bleibt
0.1.10; P0 Android-Startsender/Remote-Test ist weiterhin offen.

**Vierte TiviMate-Fotoserie (14.10.2026):** 10 Screenshots mit `Wiedergabe`,
`Sonstiges` (Suchen, Erinnerungen, Aufnahme, VOD), `Kindersicherung`
und `Über` vollständig erfasst:
`docs/XCMate/TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md`.
Felder als anonymisierte Struktur nach
`docs/XCMate/TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json` übertragen.
Einige dunkel markierte Schalter sind nicht eindeutig als ein/aus zu erkennen
(Sprachsuche, Autoplay nächste Folge, Telemetrie); Werte explizit unbestimmt.
Kein privates Nutzerkonto, kein Gerätebezeichner, kein Android-Aufnahmepfad
auf GitHub. P0 Android-Startsender/Remote offen; weder die neuen Menüs noch
Serien-Autoplay bereits produktiv. Erst CI, Build/Katalog und echter Gerätetest,
bevor neue Kodi-Funktionen als fertig gelten.

**Fernbedienung P0 Release (14.10.2026): XCMate 0.1.11** ist aus PR #4 nach
erfolgreichen GitHub-Tests über den GS-Media-Katalog veröffentlicht. 0.1.11
aktiviert bei gültigem XCMate-Xtream-Live-TV automatisch eine widerrufbare,
XCMate-eigene Fullscreen-Bridge, erfasst native `WindowDialog.onAction`
und steuert Links/OK/Hoch/Runter/Rechts/Menü/Zurück mit eigener TV-Leiste.
Externes Kodi-Video wird an Kodi weitergereicht, keine fremde Keymap
überschrieben. ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.11.zip`.
Katalog-/MD5 geprüft; 1.7.0 unverändert. **Android-Gerätetest steht aus.**
Zum Test nach Update **Kodi komplett neu starten**, dann Sender starten,
Tasten prüfen und Diagnosestatus + anonymisierte Logs auswerten. Die auf Fotos
basierende TiviMate-Spezifikation, Serienfortschritt und UI/Optik sind noch
nicht als fertige Funktionen integriert. Bestehende Portale, EPG-Mappings,
Benutzerdaten und Remoteprofile stets bewahren.


**Neue Freigabe – XCMate 0.1.12 (14.10.2026):**
Der Android-Test nach 0.1.11 meldete: DIE WELT HEVC startet, aber
XCMate-Tasten/OSD werden nicht übernommen; Kodi-Lautstärke und normales
Player-Menü funktionieren. Identifizierter Quellcode-Race in `service.py`:
Nach langer Leerlaufphase räumte der 8-s-Idle-Cleanup neue
`XtreamMate.LiveSession`-Marker während der Player-Startlatenz sofort ab.
PR #5 (https://github.com/artattakk-creator/kodi-noodleprivate/pull/5)
mit 60-s-Startschonfrist und vier Regressionstests wurde gemergt.
GitHub CI nach Merge: https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/38570255156
Ergebnis **success**; generiertes `plugin.video.xtreammate/plugin.video.xtreammate-0.1.12.zip`
(209791 Bytes), `addons.xml` mit Version 0.1.12 und MD5 vorhanden.
GitHub-Stand ist veröffentlicht, **echter Android-Gerätetest weiter offen**.
Beim nächsten Test auf der Box Kodi vollständig neu starten, erst WELT
starten und dann Links, Hoch/Runter, OK, Menü, Guide und Zurück testen.
Bei erneutem Versagen eine anonymisierte Kodi-Logpassage zu
`XCMate navigator cannot start`, `XCMate WindowDialog startup failed`,
`XCMate TV navigation unavailable` und die Ferndiagnose auswerten.
Niemals Portale, Anmeldedaten, Einstellungen oder Remoteprofile löschen.

**NEU: aktueller Release 0.1.13 (14.10.2026) – Offline-Dienstdiagnose.**
Android-Foto vom Nutzer: Keymap aktiv, kein Video, keine erkannte Session, kein TV-Overlay; der Hintergrunddienst war **zum Zeitpunkt des Fotos nicht überprüfbar**, nicht eindeutig als gestoppt bewiesen. XCMate 0.1.13 ergänzt die wiederkehrende Kodi-Home-Window-Heartbeat-/Loop-Zähler-Diagnose, speichert die letzte Stream-/Overlay-Beobachtung und bietet im Portalmenü „XCMate-Hintergrunddienst prüfen / manuell starten“ auch ohne laufendes Video. Manuelle Startanforderung per Kodi `RunScript` nur bei fehlendem frischem Heartbeat, mit Wiederholungssperre; tatsächliche Hostfunktion **noch nicht auf Android belegt**. PR #6 und GitHub CI/ZIP/Katalog bestanden, Dateiname `plugin.video.xtreammate-0.1.13.zip`. Keine bestehenden Portale, Passwörter, EPG oder Tastenprofile überschrieben. Nutzer soll nach Update Kodi vollständig neu starten, Dienststatus ohne Video prüfen, Testsender starten, später Diagnose aus dem Hauptmenü wieder öffnen und Status/letzte Beobachtungen zurückmelden. P0 Android-Remote weiterhin offen. Bilder/Optik erst danach.
