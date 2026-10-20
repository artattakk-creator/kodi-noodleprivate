# Übergabeblock für einen neuen XCMate-Chat

> **AKTUELL – P0-Start-Hotfix 0.1.28.1 (20.10.2026):** Produktiv ist **0.1.28**,
> Main-Basis `63b4cd6`; PR #36 wurde integriert und regulär veröffentlicht.
> [Issue #38](https://github.com/artattakk-creator/kodi-noodleprivate/issues/38): intermittierender Android-Start-Hänger,
> nach Stopp/Cache-Leerung vorläufig erholt; **Geräteursache weiterhin unbewiesen**.
> [Hotfix-Bericht und Paket](HOTFIX_0281_STARTUP_DE.md) · [vollständiger Auftrag](CODEX_AUFTRAG_0281_STARTUP_HOTFIX_DE.md)
> · [Android-Test/Repository-Update/Rollback](ANDROID_TESTPLAN_0281_DE.md) · [399/399 Tests + Nachweise](TESTERGEBNISSE_0281.json).
> Branch `fix/xcmate-028-startup-hang`, **18 neue Starttests**, zusätzlich 26 HTTP-/EPG-Tests bestanden.
> Test-ZIP **0.1.28.1**, 107 Dateien / 338.115 Bytes; Remote-/Live-Freeze und andere Add-ons unverändert.
> **Kein Merge/Release; Android-Hotfix-Abnahme offen.** Design/Theme/Sprache aus Issue #37 zurückgestellt.
> Frühere „AKTUELL“-Abschnitte unten sind historische Übergaben und keine gültige Releaseangabe.


> **AKTUELLE GESICHERTE PROJEKTÜBERGABE (19.10.2026):** [Google-Drive-Datei XCMate_Projektuebergabe_2026-10-19_AKTUELL.md](https://drive.google.com/file/d/12yo2Ukev2haMhVxzz7QEuMSq-PIh900_/view?usp=drivesdk) im Ordner [XCMate Projekt](https://drive.google.com/drive/folders/1f_CvKdgXGdTw1FFQ2vaCUjFFlG6Pp4db). Dort sind die vier Space-Premium-Grafiken + ZIP/Preview bereits im Ordner „Grafiken/Space Premium - Set 01“, und eine neue [Language-Packs-Ablage](https://drive.google.com/drive/folders/1vOjjhTUKmgaG18X2MkYZWhQa4BCdqmep) wurde angelegt. Englische Basis- und deutsche Bestands-`strings.po` bleiben im Kodi-Quellbaum; weitere Pakete noch nicht implementiert. Die ältere Drive-Datei `XCMate_Projektuebergabe_2026-10-19.md` ist historisch, **diese AKTUELL-Fassung verwenden**. [Codex-PR #28](https://github.com/artattakk-creator/kodi-noodleprivate/pull/28) ist weiterhin Draft und noch **nicht** produktiv; `0.1.26` bleibt veröffentlicht.


> **SPRACHPAKETE – 19.10.2026:** Englisch `en_GB` ist die technische XCMate-Basis/Fallbacksprache; Deutsch `de_DE` bleibt als bereits vorhandene, mitgelieferte Sprache **unverändert installiert und wählbar**. Bestehende Kodi-Nutzersprachen nicht zurücksetzen. [Vollständiger Sprachpaket-/Kodi-21-Plan](LANGUAGE_PACK_ARCHITECTURE_027_DE.md), [GitHub-Staging `language_packs/`](../../language_packs/README.md), [Issue #29](https://github.com/artattakk-creator/kodi-noodleprivate/issues/29). Später weitere XCMate-UI-Sprachen optional laden/aktivieren/löschen unter **Einstellungen → Darstellung & Sprache**, unabhängig vom bestehenden IPTV-Inhaltsfilter `lang_priority`. **Nur Verzeichnisse/Dokumentation vorbereitet, der Sprachpaketinstaller ist noch nicht implementiert.** **Google-Drive-Archiv:** [XCMate Projekt](https://drive.google.com/drive/folders/1f_CvKdgXGdTw1FFQ2vaCUjFFlG6Pp4db) / [Language-Packs](https://drive.google.com/drive/folders/1vOjjhTUKmgaG18X2MkYZWhQa4BCdqmep). Bestehende Live-TV-/Fernbedienungsfunktionen 0.1.26 FREEZE; kein Release 0.1.27.


> **GRAFIKDESIGN FREIGEGEBEN 19.10.2026:** **Nur Variante 1 „SPACE PREMIUM“** aus der drei Designs umfassenden XCMate-Konzeptgrafik ist als neuer Standard gewählt: tiefblauer Weltraum, Erdkrümmung, verchromtes 3D-X, leuchtendes Cyan. **Der bisherige schlichte Metallgrau-Stil ist ausdrücklich verworfen**. [Verbindliche Freigabe und Theme-Architektur](DESIGN_FREEZE_SPACE_PREMIUM_THEME_ARCHITECTURE_DE.md) · [98-Asset-Produktionsplan](GRAPHICS_V2_ASSET_PLAN_027_DE.md) · [Issue #27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27). **Nur Design 1 wird jetzt gestaltet/integriert**; Designs 2 und 3 werden höchstens als spätere installierbare **XCMate-interne Grafikthemes** technisch vorbereitet, **nicht** jetzt produziert. BINGIE MOD ist und bleibt der aktive Kodi-Skin, keine globale Skin-Änderung. Zuerst Icon (512×512) und volle Home-Vorschau (1920×1080) zur Sichtabnahme; **noch keine Einzel-Assetproduktion**. **0.1.26 Live-TV/Remote FREEZE** bleibt bindend. Release bleibt 0.1.26.


> **GRAFIKSYSTEM-PLAN 19.10.2026:** [XCMate Graphics v2 – vollständiges 98-Asset-Manifest](GRAPHICS_V2_ASSET_PLAN_027_DE.md) · [Grafik-Umsetzungsissue #27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27). Im aktuellen produktiven `0.1.26`-Add-on **32 Runtime-Bilder (114.014 Bytes)**. Geplant **98 logische Grafikslots** insgesamt für Branding, sechs Home-Bereiche, zehn Settings-Untermenüs, EPG, Film/Serie, Player, Suche und drei BINGIE-MOD-Widgets. **Freigegebenes ursprüngliches XCMate-Logo/Space-Motiv beibehalten**, Details/Quellstatus in [Art-Manifest](ARTWORK_ASSET_MANIFEST_DE.md); Dynamic-VOD-Artworks aus Provider, nicht im ZIP vervielfältigen. **Manifest-Bug:** `addon.xml` referenziert `fanart.png`, vorhanden ist `fanart.jpg`; erst in geprüftem Grafik-PR korrigieren. **Live-TV-UI- und Remote-Freeze 0.1.26** bleibt; **noch kein neues Artwork generiert/installiert und kein Release 0.1.27**.


> **AKTUELLE ZUSATZANFORDERUNG 19.10.2026 – FUNKTIONALER FREEZE 0.1.26 + Suche + BINGIE MOD:** [Verbindlicher vollständiger Codex-Vertrag](CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md), [Issue #25 gemeinsame LIVE-TV/Filme/Serien-Suche](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25), [Issue #26 drei BINGIE-MOD-Home-Widgets](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26). Alle bestehenden 0.1.26-Funktionen (**Live-TV, erste OK-Infobar, 3 Player-/Einstellungsebenen, D-Pad/Links-Gruppen, Portal-/EPG-Profile**) sind **FREEZE** und werden ausschließlich durch neue Module/Routen ergänzt. In Film- UND Serien-Landingpage und Gruppen-/Posteransicht echtes Fanart/Backdrop des fokussierten Titels, links ausklappbare Gruppenleiste, Rechts vollbreites Postergrid, Links am Gridrand Gruppen erneut zeigen. Die **globale Suche** hat drei getrennte Ergebnisrubriken mit tatsächlichen Gesamtzahlen und korrekter Auswahl/Playback. **BINGIE MOD Homescreen:** drei horizontale Widgetrails in Reihenfolge 1) Live-Sender der Startkanalgruppe samt Now/Next, 2) neueste Filme, 3) neueste Serien. Die Widget-Routen liefern passende Kodi-ListItems; **keine ungefragten Veränderungen an fremden Skin-Dateien oder vorhandenen Nutzer-Widgets**. Zunächst einrichten über dokumentierte BINGIE-MOD-Skineinstellungen; echte Android-Abnahme/CI erforderlich. Aktueller Veröffentlichungsstand bleibt **XCMate 0.1.26**; Ziel 0.1.27 nur nach Codex-PR/Review/Releasefreigabe.


> **VERBINDLICHER ZUSATZAUFTRAG 19.10.2026 – FILME + SERIEN (Ziel 0.1.27):** [Netflix-/BINGIE-MOD-artige Film-/Serienoberfläche, Cover-Rail, Kategoriegruppen und Detailseiten](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md), [Issue #24](https://github.com/artattakk-creator/kodi-noodleprivate/issues/24). Ergänzt den [0.1.27-Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) und [Issue #23](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23): In beiden Hauptpunkten zuerst **horizontal scrollbare Neuheitenreihe**, darunter Kategorien → erste aktivierte Gruppe; **Links** Gruppenleiste, **Rechts** vollbreite Posterwand; Cover OK → **bildstarke Film-/Seriendetailseite** mit echten Metadaten, dynamischem Favoritenstatus, Abspielen/Neustart/Fortsetzen und validiertem YouTube-Trailer. Serien mit Staffeln/Folgen und Fortschritt gemäß [Serienfortschritts-Spezifikation](SERIES_PROGRESS_SPEC_DE.md). **Nicht vorhanden / nicht vorgeben:** vollwertiges Kodi-WindowXML-Medien-UI und garantiertes Movie-/Episode-Resume. Nutzer hat noch keinen neuen 0.1.27-Code abgenommen: **Produktivversion weiterhin 0.1.26**, Entwicklung nur auf neuem Branch/PR, keine eigenmächtige Veröffentlichung.


> **NEUER VERBINDLICHER CODEX-AUFTRAG 19.10.2026 – Ziel 0.1.27:** [Sechs-Punkte-Hauptmenü, Einstellungen, großer gruppenbasierter EPG und Aufnahmepfad](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) · [Issue #23 Startmenü/Settings](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23) · [Issue #21 7–10-Tage-EPG und Timer](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). **Neuer Android-0.1.26-Befund:** Update über Kodi hat funktioniert, Nutzer bestätigt erfolgreiche grundsätzliche Live-TV-/Menübedienung und gelungene Optik; die detaillierten 10×-Fernbedienungstests sind noch nicht dokumentiert. **Unverändert erhalten:** erste OK-Infobar, dreistufige Playersteuerung und Kodi-native Remote. **Neu:** Startseite **nur** Startkanal, Live-TV, EPG, Filme, Serien, Einstellungen. Unter Einstellungen Accounts/Portale, Startkanal, EPG, Gruppen, optional lernbare Fernbedienung, Player, Aufnahmeordner (`recordings_folder` beibehalten), Darstellung, Wartung/Diagnose. Großer EPG startet in Sendergruppe des Startkanals, Links → Gruppenwechsel, Tage 7–10 nach tatsächlich verfügbarer Quelle. **Noch kein Build/Release 0.1.27**: 0.1.26 bleibt produktiv; Implementierung auf neuem Branch mit Tests/PR, keine eigenmächtige Veröffentlichung. GPL-/Herkunftsvermerke bewahren.


> **AKTUELLER ANDROID-TV-TEST VON XCMate 0.1.25 – 19.10.2026:** Die **kompakte 1×-OK-Infobar funktioniert** und ist optisch freigegeben (**Freeze**). **P0 offen:** D-Pad **Links** öffnet im TV-Vollbild weder Senderliste noch beim zweiten Links die Gruppen; Sender-EPG ist nur über OSD-Button erreichbar. **Neue verbindliche Menüfolge:** 1× OK Infobar → 2× OK oder Runter echte Tape-Deck-Playerleiste → weiteres Runter Einstellungen mit Bild/Ton/Untertiteln/EPG/Sendergruppen. **P1/P2:** 7–10-Tage-EPG (nur echte Feed-Reichweite) mit Erinnerung, ausdrücklich optionalem Auto-Umschalten und nur bei funktionsfähiger Aufnahmeengine geplanten Aufnahmen. [Vollständiger Codex-Folgeauftrag](ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md); [Issue #20 Links und OSD](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20), [Issue #21 Langzeit-EPG und Timer](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). **Keine neue Add-on-Version freigegeben oder gebaut**, aktuell bleibt 0.1.25. Arbeiten auf eigenem Branch, PR/Tests, kein Merge ohne Nutzerfreigabe.


> **Lizenz-/Herkunfts-Audit 19.10.2026:** [Vollständiger Datei-/Codevergleich XCMate 0.1.25 und unabhängiger V2-Umbauplan](CODE_ORIGIN_LICENSE_AUDIT_025_DE.md) · [Rechteklärungs-Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19). Der früheste GS-Media-Fork-Snapshot (13.10.) verglichen mit 0.1.25 ergibt 6 Python-Module bytegenau unverändert und teils hohe Altzeilen-Überlappung in `main.py`, `player.py`, `epg.py`. **Dringender offener Rechtekonflikt:** Upstream-`addon.xml` deklariert GPL-2.0-only, aber mr-evil1s Root-`LICENSE` vom 01.10.2026 sagt „Alle Rechte vorbehalten“ und untersagt Kopieren/Modifizieren ohne schriftliche Genehmigung. **Kein rechtsgültiger Schluss zugunsten einer Lizenzvariante; keine Umstellung auf proprietär, keine Entfernung der Herkunftshinweise.** Externe juristische Prüfung der Rechtekette und Original-ZIP-Vergleich erforderlich. Dieses Audit ist separat von der XCMate-0.1.25-Android-Abnahme; **Produktionscode und Lizenzdateien unverändert**.

> **AKTUELLER CODEX-ARBEITSAUFTRAG (18.10.2026, hat Vorrang vor älteren Anweisungen):** [CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md). Ausgangsbasis: veröffentlichtes XCMate **0.1.24**; auf Android-TV erstmals echte Kanal-Sidebar, Fokusmarkierung und unteres OSD sichtbar. **Noch offen:** Menü-/D-Pad-Stabilität, EPG-Daten-/Statusanzeige und langsamer Kanal-Listenaufbau. Vorgabe: **1× OK kompakte Infoleiste mit Logo/JETZT/Von–bis/DANACH/Fortschrittsbalken/Restzeit; 2× OK oder Runter öffnet erst die Player-Bedienleiste; Links öffnet schnelle Senderliste mit EPG pro Zeile.** Für Codex zuerst diesen Arbeitsauftrag, dann [UX-Spezifikation](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md), [Android-Test](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) lesen. Änderungen nur auf neuem Branch mit Tests/PR, kein `main`-Merge ohne Freigabe. Diese Datei enthält darunter historische Versions- und Fehlermeldungen.


> **AKTUELLER ARBEITSAUFTRAG 18.10.2026 (hat Vorrang vor historischen Angaben unten):** XCMate **0.1.23** ist über `main` veröffentlicht und auf dem echten Android-TV mit `TypeError` beim TV-`WindowDialog` gescheitert; die EPG-Aktualisierung lieferte keine neuen Guide-Daten. Lies **zuerst** [CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md), [CODEX_STATUS_CURRENT_DE.md](CODEX_STATUS_CURRENT_DE.md), [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) und [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13). Prüfe besonders `live_overlay.py::LiveNavigator._build_controls` und die **falsch benannten `ControlList`-Keywords `itemHeight`/`space`** gegen Kodi 21/Omega. Neuer Fix-Branch + strikte Regressionstests + PR. **`main` nicht ohne Nutzerfreigabe verändern.** Der Projektname des geplanten separaten Skins ist **XCMate Skin** (Issue #14), erst nach P0/EPG-Prüfung.

> **AKTUALISIERUNG 18.10.2026:** XCMate **0.1.22** wurde nach 180 bestandenen GitHub-CI-Tests via [PR #11](https://github.com/artattakk-creator/kodi-noodleprivate/pull/11) in `main` aufgenommen und über das GS-Media-Repository veröffentlicht. **Android-TV-Abnahme steht aus.** Dieses Dokument enthält darunter teilweise historische Versions-/Fehlerstände. Für den verbindlichen aktuellen Zustand zuerst [CODEX_STATUS_CURRENT_DE.md](CODEX_STATUS_CURRENT_DE.md) und [KODI21_FIX_022_DE.md](KODI21_FIX_022_DE.md) lesen.


Wir setzen mein Kodi-/IPTV-Projekt **XCMate** (GS Media) fort. Repository: https://github.com/artattakk-creator/kodi-noodleprivate. **Ausgangsbasis `main`, Änderungen ausschließlich in neuem Entwicklungsbranch.**

**WICHTIG: Bitte zuerst diese GitHub-Dateien lesen:**
1. `docs/XCMate/README.md`
2. `docs/XCMate/PROJECT_HANDOFF_DE.md`
3. `docs/XCMate/ROADMAP_AND_QA_DE.md`
4. `docs/XCMate/SERIES_PROGRESS_SPEC_DE.md`
5. `docs/XCMate/DESIGN_SYSTEM_DE.md`

**Letzter geprüfter Projektstand am 15.10.2026:** XCMate 0.1.17, GS Media Kodi Repository 1.7.0. Der angezeigte Name lautet XCMate. Die technische Kodi-ID `plugin.video.xtreammate` bleibt bewusst unverändert, damit automatische Updates und Kodi-Profil/Zugangsdaten erhalten bleiben.

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

**Aktueller Stand (14.10.2026): XCMate 0.1.14 veröffentlicht.**
Letztes reales Android-Foto: Hintergrunddienst LÄUFT, 2134 Schleifen;
Video JA, aber XCMate-Sitzung NEIN. Es handelt sich damit um ein
Session-/Overlay-Startproblem, nicht um einen nachweislich gestoppten
Dienst. PR #7 ändert die Service-Laufzeit: bei Player-Video ohne
Session wird `getPlayingFile()` mit den eigenen aktivierten Xtream-Portalen
und bekannten Sender-IDs **exakt** lokal abgeglichen. Nur eindeutige
Matches starten `LiveSession` neu, niemals fremde Kodi-/VOD-Videos.
Neue Diagnose zeigt `Live-Sitzungswiederherstellung`, keine URLs.
PR und Release erfolgreich (CI 38587564991 / 38587667244),
ZIP `plugin.video.xtreammate-0.1.14.zip` 215793 Bytes,
`addons.xml` 0.1.14. Nach Update Kodi neu starten, WELT-Startsender
testen, später Offline-Diagnose mit Live-Sitzung, Recovery-Ergebnis
und TV-Overlay-Ergebnis anfordern. **Noch kein Erfolg auf Android bewiesen.**
Optik und TiviMate-Fotoreferenz weiter nachrangig.

**Aktueller Release: XCMate 0.1.15 (14.10.2026)**, über PR #8,
GitHub CI #38592365190 / Publish #38592489957, ZIP
`plugin.video.xtreammate-0.1.15.zip` (219453 Bytes), Katalog
0.1.15, GS Media Repository 1.7.0. Nach 0.1.14 bleibt P0
Android-Fernbedienung unbestätigt. Die neue `popup_probe.py` ist
ein direkt aus dem Xtream-Portalmenü gestarteter, Kodi-eigener
`WindowDialog.doModal()` mit 2 fokussierbaren Buttons und
Richtung/OK/Zurück-Eventcounter – **kein Stream notwendig**.
Die TV-`LiveNavigator`-Seitenleiste ist jetzt beim ersten aktiven
Session-Start automatisch 16s sichtbar; bei keinen Tasten blendet sie
sich aus, TV läuft weiter. Offline-Diagnose zeigt Popup-Test-Events,
Auto-TV-Popup, Live-Session-Recovery und Service-Status.
**Nutzertest zwingend:** ohne Stream Popup aufrufen/Tasten prüfen,
danach TV und die automatische Sender-/EPG-Seitenleiste prüfen,
anschließend Diagnose-Screenshot. Plan für 0.1.16–0.1.19 steht in
`docs/XCMate/POPUP_UI_IMPLEMENTATION_PLAN_DE.md`.
Keine bereits funktionierende TiviMate-EPG-/Mini-TV-Oberfläche behaupten;
das verkleinerte Livevideo bleibt ein gesondertes Kodi-Rendering-Thema.

**NEUER P0-Stand, 15.10.2026: XCMate 0.1.16 VERÖFFENTLICHT.**
Nach 0.1.15 meldete Nutzer: Popup-Test konnte nicht gestartet
werden, weil beim Betreten von XCMate sofort der gespeicherte
Startsender lief und die Bedienung blockierte. Ursache im Code:
`_root()` ruft bei Einzelportal automatisch
`_maybe_autoplay_start()` auf und startet über `RunPlugin`
das Live-TV noch bevor Popup anwählbar ist. PR #9 behebt das
mit Add-on-Einstellung `autoplay_diagnostics_safe` (Standard
`true`), blockiert *nur* automatischen Start, ändert keine
Portal-/EPG-/Credential-/Remote-Konfiguration. Manuell Fernsehen
bleibt möglich. Popup-Test erste Zeile im Portalmenü; zusätzlich
separater Test-Aufruf über Kodi Add-on `Konfigurieren`.
Autostart-Freigabe bewusst im Menü / Kodi-Einstellungen.
GitHub CI und Release grün (38708867907 / 38708940824);
ZIP `plugin.video.xtreammate-0.1.16.zip`, 221251 Bytes,
`addons.xml` 0.1.16; checksum verifiziert.
**Nächster Test:** Kodi komplett neu starten, XCMate-Menü
ohne Video laden, ersten Eintrag Popup-Test, Richtungen/OK/Zurück
prüfen; danach Diagnose-Screenshot. TV erst später manuell starten.
P0 echtes Android Remote weiterhin offen. Geplante UI-Meilensteine
nach Hotfix um eine Versionsnummer verschoben.

**NEU am 15.10.2026: Release XCMate 0.1.17.**
Auf Android 0.1.16 blieb Startsender aus (gewollt),
Hintergrunddienst LÄUFT (497 Loops), aber der eigene
`xbmcgui.WindowDialog` erschien unsichtbar. Trotzdem
`Popup-Ereignisse: 16`, letzte Taste Kodi-ID 92 (Zurück)
und `Popup-Status: PER ZURÜCK GESCHLOSSEN`.
**Modal-Remote-Eingaben funktionieren grundsätzlich**, Problem
ist UI-Rendering/Fokusvisualisierung; TV-Session nicht getestet.
PR #10 mit Kodi-API-Tests grün und Publikation erfolgreich
(CI 38731122534, Release 38731226443).
ZIP `plugin.video.xtreammate-0.1.17.zip`, 223470 Bytes.
Neu: Popup-Test beginnt mit **sichtbarem Kodi-Dialog.select()**,
danach auf Auswahl **Kodi WindowXMLDialog** mit eigener
`resources/skins/Default/720p/XCMatePopupTest.xml`,
ausdrücklichen Controls und Focus-Buttons. Fehler beim Laden
gehen an normalen sichtbaren Kodi-Dialog; Diagnose ergänzt
`Popup-Darstellungsweg`. Standardmäßig pausierter
Startsender 0.1.16 bleibt aktiv. **Nutzertest:** XML sichtbar?
Foto des nativen Auswahldialogs, XML-Popups und der späteren
Offline-Diagnose. Nicht behaupten, dass XML oder Live-TV-Remote
bereits Android-getestet funktionieren. Sender/EPG feature-phase
wegen zwei P0 Hotfixes in späteren Versionen.
