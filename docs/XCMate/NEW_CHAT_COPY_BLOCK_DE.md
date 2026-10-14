# Übergabeblock für einen neuen XCMate-Chat

Wir setzen mein Kodi-/IPTV-Projekt **XCMate** (GS Media) fort. Arbeite direkt im GitHub-Repository https://github.com/artattakk-creator/kodi-noodleprivate auf `main`.

**WICHTIG: Bitte zuerst diese GitHub-Dateien lesen:**
1. `docs/XCMate/README.md`
2. `docs/XCMate/PROJECT_HANDOFF_DE.md`
3. `docs/XCMate/ROADMAP_AND_QA_DE.md`
4. `docs/XCMate/SERIES_PROGRESS_SPEC_DE.md`
5. `docs/XCMate/DESIGN_SYSTEM_DE.md`

**Letzter geprüfter Projektstand am 14.10.2026:** XCMate 0.1.10, GS Media Kodi Repository 1.7.0. Der angezeigte Name lautet XCMate. Die technische Kodi-ID `plugin.video.xtreammate` bleibt bewusst unverändert, damit automatische Updates und Kodi-Profil/Zugangsdaten erhalten bleiben.

**Zielgerät:** Android-Kodi-Box mit Titan BINGIE MOD. **Dringend P0:** Startsender springt auf dem echten Gerät teils weiterhin in eine leere Kodi-Verzeichnisansicht; Links/Hoch/Runter/OK, Senderliste und Player-Zusatzleiste funktionieren auf dem Gerät bislang nicht zuverlässig. 0.1.10 trennt Kodi-Playable-`setResolvedUrl` und direkten `RunPlugin`-Autoplay-Start, korrigiert die OK-Funktion im Player-OSD und wurde in GitHub CI gebaut. Es gibt weiterhin keine bestätigte erfolgreiche Android-Gerätetest-Rückmeldung. Bitte die Diagnose und Kodi-Logs analysieren, nicht blind Erfolg behaupten.

**Neue verbindliche Anforderung:** Bei Serien Gesehen-Status und Fortschritt pro Folge dauerhaft speichern; nach Abbruch an der letzten Position fortsetzen; optional automatisch nächste Folge in korrekter Staffel-/Folgenreihenfolge abspielen; „Weiterschauen“-Ansicht. **Noch nicht implementiert.** Details, Datenmodell und Akzeptanztests stehen in `SERIES_PROGRESS_SPEC_DE.md`.

**Design-Freeze:** Nutzer hat silbernes **XCMate**-Logo vor dunklem Planeten und großflächige monochrome Weltraumgrafik ausdrücklich freigegeben. Graues („Slate“) UI ist Standard, weitere UI-Farben sollen später frei wählbar werden. Freigegebene Quellbilder: `grafik.png` und `imagegen.png` aus dem vorherigen Chat. Bitte in `DESIGN_SYSTEM_DE.md` prüfen und nichts eigenmächtig durch anderes Branding ersetzen. Ob Grafik-Binärdateien schon auf GitHub liegen, gesondert verifizieren.

**Weitere Funktionen:** Xtream/M3U/Stalker, getrennte Live-/Film-/Seriengruppen per Checkbox, Cache-first, XMLTV-EPG mit zusätzlichen Quellen und manueller Zuordnung, Jetzt/Danach, Film-/Serienbeschreibungen und Trailer, BINGIE-Widgetordner. „Im Repo implementiert“ ist nicht gleich „auf Android geprüft“.

**Arbeitsweise:** Immer tatsächlichen GitHub-Head und Quellcode lesen, Problem reproduzieren, Änderung und Tests erstellen, Build abwarten, ZIP und `addons.xml` kontrollieren und Status in den GitHub-Übergabedokumenten fortschreiben. Keine Zugangsdaten oder private IPTV-URLs posten/committen; möglichst Repository-Update statt manueller Neuinstallation.

Bitte beginne mit einem kurzen GitHub-Statuscheck und schlage den nächsten klar abgegrenzten Schritt vor.

**Neu – verifizierte TiviMate-Fernbedienung (14.10.2026):** 10 Nutzerfotos aus TiviMate 5.3.3 liegen vor (Player- und EPG-Zuordnungen inkl. Langdruck sowie Suchoptionen). **Verbindliche Referenz**: `docs/XCMate/TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md`. Der Draft-PR #3 mit `tivimate_keys.py` und Tests hat grünes GitHub-CI, ist aber **noch nicht in Kodi aktiviert oder als Add-on-Version veröffentlicht**. Weitere Einstellungsfotos werden nach und nach geliefert und müssen ergänzt werden. Funktional TiviMate-ähnlich nachbauen, keine proprietären Assets/Quellen übernehmen. Die Stabilisierung von Startsender und Android-Fernbedienung (P0) bleibt offen.
