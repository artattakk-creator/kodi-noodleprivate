# XCMate – zentraler Projekteinstieg

> **AKTUELL – P0-Start-Hotfix 0.1.28.1 (20.10.2026):** Produktiv ist **0.1.28**,
> Main-Basis `63b4cd6`; PR #36 wurde integriert und regulär veröffentlicht.
> [Issue #38](https://github.com/artattakk-creator/kodi-noodleprivate/issues/38): intermittierender Android-Start-Hänger,
> nach Stopp/Cache-Leerung vorläufig erholt; **Geräteursache weiterhin unbewiesen**.
> [Hotfix-Bericht und Paket](HOTFIX_0281_STARTUP_DE.md) · [vollständiger Auftrag](CODEX_AUFTRAG_0281_STARTUP_HOTFIX_DE.md)
> · [Android-Test/Repository-Update/Rollback](ANDROID_TESTPLAN_0281_DE.md) · [399/399 Tests + Nachweise](TESTERGEBNISSE_0281.json).
> [Draft-PR #39](https://github.com/artattakk-creator/kodi-noodleprivate/pull/39), [CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39416216202), [Reviewartefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39416216202/artifacts/12261762240).
> Branch `fix/xcmate-028-startup-hang`, **18 neue Starttests**, zusätzlich 26 HTTP-/EPG-Tests bestanden.
> Test-ZIP **0.1.28.1**, 107 Dateien / 338.115 Bytes; Remote-/Live-Freeze und andere Add-ons unverändert.
> **Kein Merge/Release; Android-Hotfix-Abnahme offen.** Design/Theme/Sprache aus Issue #37 zurückgestellt.
> Frühere „AKTUELL“-Abschnitte unten sind historische Übergaben und keine gültige Releaseangabe.


> **AKTUELL – Entwicklung 0.1.28 (19.10.2026):** Produktiv ist **0.1.27**, Main-Basis
> `103646f`; PR #28 wurde übernommen. [Neuer Implementierungs-/Testbericht](IMPLEMENTIERUNG_028_PERFORMANCE_EPG_UI_DE.md)
> · [vollständiger 0.1.28-Auftrag](CODEX_AUFTRAG_028_PERFORMANCE_EPG_UI_DE.md)
> · [Android-TV-Abnahme und Repository-Updateweg](ANDROID_TESTPLAN_028_DE.md).
> **381 lokale Tests bestanden, 43 neue Regressionen; [CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39313972637).**
> Test-ZIP 0.1.28 / Build 28 geprüft, [CI-Reviewartefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39313972637/artifacts/12216318143).
> [Draft-PR #36](https://github.com/artattakk-creator/kodi-noodleprivate/pull/36), Branch `feat/xcmate-028-streaming-stability`; **kein automatischer Main-Merge/Publish**.
> Streaming-/Gruppenimporte, Medien-/Suchstart, großer EPG, Startgruppen-Snapshots und separate
> Pre-Play-Anzeige implementiert; eigener en/de-Schalter und Core-Darstellung vorbereitet.
> Optionale Theme-/Language-Pack-Installer und vollständige Legacy-Lokalisierung bleiben offen.
> **Geräteabnahme offen**, aktuelle DE-/AT-Originalfeeds aus der Cloud HTTP 403.
> Die folgenden 0.1.27-/älteren Kandidaten- und Releaseabschnitte sind historische Nachweise;
> für aktuelle Testzahlen, Paket und Freigabe ausschließlich den neuen Bericht verwenden.


> **AKTUELL – PR #28 synchronisiert und lokalisiert (19.10.2026):**
> `main` **345b93d** via Mergecommit **e933ea0** integriert, kein History-Rewrite.
> [Aktueller Stabilisierungsbericht, Tests und Test-ZIP](STABILISIERUNG_027_SYNC_LOKALISIERUNG_DE.md)
> · [Android-Abnahmeplan](ANDROID_TESTPLAN_027_DE.md) · [Draft-PR #28](https://github.com/artattakk-creator/kodi-noodleprivate/pull/28).
> **Lokal 338 Tests vor/nach isoliertem Build bestanden**, darunter 25 neue Sprachtests;
> 26 HTTP-/EPG-Tests zusätzlich mit httpx. 207 neue en/de-String-IDs (32400–32606).
> Englisch ist technische Basis/Fallback; deutsches Kodi-Altprofil bleibt deutsch.
> Kein Schreiben der Kodi-Sprache, keine Umdeutung von `lang_priority`, keine Datenmigration.
> Test-ZIP 0.1.27 / Build 27: **308392 Bytes, 96 Dateien**, CRC/SHA/Quellbytes geprüft.
> Alle bisherigen 0.1.27-Funktionen erhalten; Live-Overlay/Remote-/Player-Freeze geprüft.
> Neue native Android-/BINGIE-/Sprachfälle noch am Gerät abzunehmen. Space-Premium-Grafiken,
> Theme- und Language-Pack-Installer bleiben separate Aufgaben; `fanart`-Manifestfehler offen.
> Drive-Übergabe aus der Cloud **HTTP 403**, daher autorisiert GitHub als Grundlage verwendet.
> Neuer [GitHub-Prüflauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39282533858) auf `0e00227` noch **queued / kein Runner**
> (19.10.2026, 18:08 MESZ); kein CI-PASS für den Sprachcode behauptet.
> **Produktiv bleibt 0.1.26; PR bleibt Draft, kein Merge/Publish.**
> Historische CI-/Paketangaben unten ersetzen nicht den aktuellen Prüfstand des Berichts.

> **AKTUELLE GESICHERTE PROJEKTÜBERGABE (19.10.2026):** [Google-Drive-Datei XCMate_Projektuebergabe_2026-10-19_AKTUELL.md](https://drive.google.com/file/d/12yo2Ukev2haMhVxzz7QEuMSq-PIh900_/view?usp=drivesdk) im Ordner [XCMate Projekt](https://drive.google.com/drive/folders/1f_CvKdgXGdTw1FFQ2vaCUjFFlG6Pp4db). Dort sind die vier Space-Premium-Grafiken + ZIP/Preview bereits im Ordner „Grafiken/Space Premium - Set 01“, und eine neue [Language-Packs-Ablage](https://drive.google.com/drive/folders/1vOjjhTUKmgaG18X2MkYZWhQa4BCdqmep) wurde angelegt. Englische Basis- und deutsche Bestands-`strings.po` bleiben im Kodi-Quellbaum; weitere Pakete noch nicht implementiert. Die ältere Drive-Datei `XCMate_Projektuebergabe_2026-10-19.md` ist historisch, **diese AKTUELL-Fassung verwenden**. [Codex-PR #28](https://github.com/artattakk-creator/kodi-noodleprivate/pull/28) ist weiterhin Draft und noch **nicht** produktiv; `0.1.26` bleibt veröffentlicht.


> **SPRACHPAKETE – 19.10.2026:** Englisch `en_GB` ist die technische XCMate-Basis/Fallbacksprache; Deutsch `de_DE` bleibt als bereits vorhandene, mitgelieferte Sprache **unverändert installiert und wählbar**. Bestehende Kodi-Nutzersprachen nicht zurücksetzen. [Vollständiger Sprachpaket-/Kodi-21-Plan](LANGUAGE_PACK_ARCHITECTURE_027_DE.md), [GitHub-Staging `language_packs/`](../../language_packs/README.md), [Issue #29](https://github.com/artattakk-creator/kodi-noodleprivate/issues/29). Später weitere XCMate-UI-Sprachen optional laden/aktivieren/löschen unter **Einstellungen → Darstellung & Sprache**, unabhängig vom bestehenden IPTV-Inhaltsfilter `lang_priority`. **Nur Verzeichnisse/Dokumentation vorbereitet, der Sprachpaketinstaller ist noch nicht implementiert.** **Google-Drive-Archiv:** [XCMate Projekt](https://drive.google.com/drive/folders/1f_CvKdgXGdTw1FFQ2vaCUjFFlG6Pp4db) / [Language-Packs](https://drive.google.com/drive/folders/1vOjjhTUKmgaG18X2MkYZWhQa4BCdqmep). Bestehende Live-TV-/Fernbedienungsfunktionen 0.1.26 FREEZE; kein Release 0.1.27.


> **GRAFIKDESIGN FREIGEGEBEN 19.10.2026:** **Nur Variante 1 „SPACE PREMIUM“** aus der drei Designs umfassenden XCMate-Konzeptgrafik ist als neuer Standard gewählt: tiefblauer Weltraum, Erdkrümmung, verchromtes 3D-X, leuchtendes Cyan. **Der bisherige schlichte Metallgrau-Stil ist ausdrücklich verworfen**. [Verbindliche Freigabe und Theme-Architektur](DESIGN_FREEZE_SPACE_PREMIUM_THEME_ARCHITECTURE_DE.md) · [98-Asset-Produktionsplan](GRAPHICS_V2_ASSET_PLAN_027_DE.md) · [Issue #27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27). **Nur Design 1 wird jetzt gestaltet/integriert**; Designs 2 und 3 werden höchstens als spätere installierbare **XCMate-interne Grafikthemes** technisch vorbereitet, **nicht** jetzt produziert. BINGIE MOD ist und bleibt der aktive Kodi-Skin, keine globale Skin-Änderung. Zuerst Icon (512×512) und volle Home-Vorschau (1920×1080) zur Sichtabnahme; **noch keine Einzel-Assetproduktion**. **0.1.26 Live-TV/Remote FREEZE** bleibt bindend. Release bleibt 0.1.26.


> **GRAFIKSYSTEM-PLAN 19.10.2026:** [XCMate Graphics v2 – vollständiges 98-Asset-Manifest](GRAPHICS_V2_ASSET_PLAN_027_DE.md) · [Grafik-Umsetzungsissue #27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27). Im aktuellen produktiven `0.1.26`-Add-on **32 Runtime-Bilder (114.014 Bytes)**. Geplant **98 logische Grafikslots** insgesamt für Branding, sechs Home-Bereiche, zehn Settings-Untermenüs, EPG, Film/Serie, Player, Suche und drei BINGIE-MOD-Widgets. **Freigegebenes ursprüngliches XCMate-Logo/Space-Motiv beibehalten**, Details/Quellstatus in [Art-Manifest](ARTWORK_ASSET_MANIFEST_DE.md); Dynamic-VOD-Artworks aus Provider, nicht im ZIP vervielfältigen. **Manifest-Bug:** `addon.xml` referenziert `fanart.png`, vorhanden ist `fanart.jpg`; erst in geprüftem Grafik-PR korrigieren. **Live-TV-UI- und Remote-Freeze 0.1.26** bleibt; **noch kein neues Artwork generiert/installiert und kein Release 0.1.27**.


> **AKTUELLE ZUSATZANFORDERUNG 19.10.2026 – FUNKTIONALER FREEZE 0.1.26 + Suche + BINGIE MOD:** [Verbindlicher vollständiger Codex-Vertrag](CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md), [Issue #25 gemeinsame LIVE-TV/Filme/Serien-Suche](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25), [Issue #26 drei BINGIE-MOD-Home-Widgets](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26). Alle bestehenden 0.1.26-Funktionen (**Live-TV, erste OK-Infobar, 3 Player-/Einstellungsebenen, D-Pad/Links-Gruppen, Portal-/EPG-Profile**) sind **FREEZE** und werden ausschließlich durch neue Module/Routen ergänzt. In Film- UND Serien-Landingpage und Gruppen-/Posteransicht echtes Fanart/Backdrop des fokussierten Titels, links ausklappbare Gruppenleiste, Rechts vollbreites Postergrid, Links am Gridrand Gruppen erneut zeigen. Die **globale Suche** hat drei getrennte Ergebnisrubriken mit tatsächlichen Gesamtzahlen und korrekter Auswahl/Playback. **BINGIE MOD Homescreen:** drei horizontale Widgetrails in Reihenfolge 1) Live-Sender der Startkanalgruppe samt Now/Next, 2) neueste Filme, 3) neueste Serien. Die Widget-Routen liefern passende Kodi-ListItems; **keine ungefragten Veränderungen an fremden Skin-Dateien oder vorhandenen Nutzer-Widgets**. Zunächst einrichten über dokumentierte BINGIE-MOD-Skineinstellungen; echte Android-Abnahme/CI erforderlich. Aktueller Veröffentlichungsstand bleibt **XCMate 0.1.26**; Ziel 0.1.27 nur nach Codex-PR/Review/Releasefreigabe.


> **VERBINDLICHER ZUSATZAUFTRAG 19.10.2026 – FILME + SERIEN (Ziel 0.1.27):** [Netflix-/BINGIE-MOD-artige Film-/Serienoberfläche, Cover-Rail, Kategoriegruppen und Detailseiten](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md), [Issue #24](https://github.com/artattakk-creator/kodi-noodleprivate/issues/24). Ergänzt den [0.1.27-Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) und [Issue #23](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23): In beiden Hauptpunkten zuerst **horizontal scrollbare Neuheitenreihe**, darunter Kategorien → erste aktivierte Gruppe; **Links** Gruppenleiste, **Rechts** vollbreite Posterwand; Cover OK → **bildstarke Film-/Seriendetailseite** mit echten Metadaten, dynamischem Favoritenstatus, Abspielen/Neustart/Fortsetzen und validiertem YouTube-Trailer. Serien mit Staffeln/Folgen und Fortschritt gemäß [Serienfortschritts-Spezifikation](SERIES_PROGRESS_SPEC_DE.md). **Nicht vorhanden / nicht vorgeben:** vollwertiges Kodi-WindowXML-Medien-UI und garantiertes Movie-/Episode-Resume. Nutzer hat noch keinen neuen 0.1.27-Code abgenommen: **Produktivversion weiterhin 0.1.26**, Entwicklung nur auf neuem Branch/PR, keine eigenmächtige Veröffentlichung.


> **NEUER VERBINDLICHER CODEX-AUFTRAG 19.10.2026 – Ziel 0.1.27:** [Sechs-Punkte-Hauptmenü, Einstellungen, großer gruppenbasierter EPG und Aufnahmepfad](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) · [Issue #23 Startmenü/Settings](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23) · [Issue #21 7–10-Tage-EPG und Timer](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). **Neuer Android-0.1.26-Befund:** Update über Kodi hat funktioniert, Nutzer bestätigt erfolgreiche grundsätzliche Live-TV-/Menübedienung und gelungene Optik; die detaillierten 10×-Fernbedienungstests sind noch nicht dokumentiert. **Unverändert erhalten:** erste OK-Infobar, dreistufige Playersteuerung und Kodi-native Remote. **Neu:** Startseite **nur** Startkanal, Live-TV, EPG, Filme, Serien, Einstellungen. Unter Einstellungen Accounts/Portale, Startkanal, EPG, Gruppen, optional lernbare Fernbedienung, Player, Aufnahmeordner (`recordings_folder` beibehalten), Darstellung, Wartung/Diagnose. Großer EPG startet in Sendergruppe des Startkanals, Links → Gruppenwechsel, Tage 7–10 nach tatsächlich verfügbarer Quelle. **Noch kein Build/Release 0.1.27**: 0.1.26 bleibt produktiv; Implementierung auf neuem Branch mit Tests/PR, keine eigenmächtige Veröffentlichung. GPL-/Herkunftsvermerke bewahren.


> **RELEASE-STATUS 19.10.2026 – VERBINDLICH:** **XCMate 0.1.26 ist im regulären GS Media Kodi Repository veröffentlicht.** [PR #22](https://github.com/artattakk-creator/kodi-noodleprivate/pull/22) geprüft/übernommen, Merge `cfbe1207fc344c77fbe2042b07f10a2e21fefc03`. [250/250 PR-CI-Tests](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39230063504) erfolgreich; automatischer [Publish-Workflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39240004268) erfolgreich; `addons.xml` und `addon.xml` bestätigen beide **0.1.26**; produktive ZIP hat **262100 Bytes**, veröffentlichte SHA-256 **`4fc88c80202d4c81c07817bb622ea2072cc6ba0c07c01ac45bc420fb809a752a`**, unabhängig gegen reale ZIP überprüft. **Android-TV-Abnahme der 0.1.26 ausstehend**: LEFT aus Live → Senderliste → Gruppen, dreistufiges OSD, Fokus, Pause/Stop/Seek und Inputdiagnose müssen auf dem Gerät geprüft werden. Erste 0.1.25-Infobar sollte laut Freeze unverändert sein, jedoch noch nicht unter 0.1.26 bestätigt. **Nicht enthalten:** 7–10-Tage-EPG, Auto-Tune oder Aufnahmeplanung. Die darunter stehenden Hinweise `Produktiv 0.1.25`, `0.1.26 nur Testkandidat` beschreiben den historischen Branch-Stand und sind nicht mehr aktuell. Der vorgängig dokumentierte Upstream-Lizenzkonflikt aus [Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19) ist weiterhin **ungeklärt**; dieses Release löst die Rechtsfrage nicht.


> **AKTUELL 19.10.2026: 0.1.26-P0-Testkandidat**, Branch `fix/xcmate-026-remote-three-level`.
> Nativer Links-Dispatch und drei TV-Ebenen implementiert; erste OK-Infobar unverändert.
> **250 Tests bestanden**, installierbare ZIP geprüft. **Android-Abnahme offen; produktiv bleibt 0.1.25.**
> Zuerst [aktuellen Status](CODEX_STATUS_CURRENT_DE.md) und
> [0.1.26-Bericht samt Android-Abnahmeplan](IMPLEMENTIERUNG_026_P0_REMOTE_OSD_DE.md) lesen.
> [Langzeit-EPG/Timer](PLAN_EPG_LANGZEIT_TIMER_DE.md) bleibt eine separate Ausbaustufe.
> Kein Merge oder Repository-Publish ohne Freigabe. Ältere Statusaussagen unten sind historisch.

**Review:** [Entwurfs-PR #22](https://github.com/artattakk-creator/kodi-noodleprivate/pull/22),
[CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39229913403),
[installierbares CI-Testpaket](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39229913403/artifacts/12176890835).

> **AKTUELLER ANDROID-TV-TEST VON XCMate 0.1.25 – 19.10.2026:** Die **kompakte 1×-OK-Infobar funktioniert** und ist optisch freigegeben (**Freeze**). **P0 offen:** D-Pad **Links** öffnet im TV-Vollbild weder Senderliste noch beim zweiten Links die Gruppen; Sender-EPG ist nur über OSD-Button erreichbar. **Neue verbindliche Menüfolge:** 1× OK Infobar → 2× OK oder Runter echte Tape-Deck-Playerleiste → weiteres Runter Einstellungen mit Bild/Ton/Untertiteln/EPG/Sendergruppen. **P1/P2:** 7–10-Tage-EPG (nur echte Feed-Reichweite) mit Erinnerung, ausdrücklich optionalem Auto-Umschalten und nur bei funktionsfähiger Aufnahmeengine geplanten Aufnahmen. [Vollständiger Codex-Folgeauftrag](ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md); [Issue #20 Links und OSD](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20), [Issue #21 Langzeit-EPG und Timer](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). **Keine neue Add-on-Version freigegeben oder gebaut**, aktuell bleibt 0.1.25. Arbeiten auf eigenem Branch, PR/Tests, kein Merge ohne Nutzerfreigabe.


> **Lizenz-/Herkunfts-Audit 19.10.2026:** [Vollständiger Datei-/Codevergleich XCMate 0.1.25 und unabhängiger V2-Umbauplan](CODE_ORIGIN_LICENSE_AUDIT_025_DE.md) · [Rechteklärungs-Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19). Der früheste GS-Media-Fork-Snapshot (13.10.) verglichen mit 0.1.25 ergibt 6 Python-Module bytegenau unverändert und teils hohe Altzeilen-Überlappung in `main.py`, `player.py`, `epg.py`. **Dringender offener Rechtekonflikt:** Upstream-`addon.xml` deklariert GPL-2.0-only, aber mr-evil1s Root-`LICENSE` vom 01.10.2026 sagt „Alle Rechte vorbehalten“ und untersagt Kopieren/Modifizieren ohne schriftliche Genehmigung. **Kein rechtsgültiger Schluss zugunsten einer Lizenzvariante; keine Umstellung auf proprietär, keine Entfernung der Herkunftshinweise.** Externe juristische Prüfung der Rechtekette und Original-ZIP-Vergleich erforderlich. Dieses Audit ist separat von der XCMate-0.1.25-Android-Abnahme; **Produktionscode und Lizenzdateien unverändert**.

> **RELEASE-STATUS 18.10.2026 – VERBINDLICH:** **XCMate 0.1.25 ist über `main` im GS Media Kodi Repository veröffentlicht.** [PR #18](https://github.com/artattakk-creator/kodi-noodleprivate/pull/18) gemergt (Merge `601c421b004f746341ecf3a8c0f7bf1200a7c84d`), [237 CI-Tests bestanden](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39155542397), [Publish-Workflow erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39156573306); `addons.xml` = `0.1.25`. ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.25.zip` vorhanden, SHA-256 **`0022633e056940fb6a338b1d5ccb01ce2585d6093652242e7579b0b5b7418ae3`** unabhängig verifiziert. **Android-TV-Abnahme 0.1.25 steht aus**: EPG, zwei OK-Stufen, Fokus, Logo, Fortschritt, schnelle linke Liste und andere Add-ons am Fernseher prüfen. Aussagen „0.1.25 nur Testkandidat / produktiv 0.1.24“ darunter sind **historische Entwicklungsangaben**. [Implementierungsbericht](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md), [aktueller Status](CODEX_STATUS_CURRENT_DE.md).

**Aktuelle Entwicklung 0.1.25:** [Entwurfs-PR #18](https://github.com/artattakk-creator/kodi-noodleprivate/pull/18), GitHub-CI erfolgreich.  [Implementierung, 237 Tests, Paket und Android-Testplan](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md) auf `fix/xcmate-infobar-epg-navigation`. Zweistufige TV-Bedienung und lokale EPG-/Quellenvorschau implementiert. **Noch nicht auf main / nicht am Android-TV abgenommen; produktiv bleibt 0.1.24.**

**Status:** 18.10.2026: **XCMate 0.1.24 ist auf `main` und im GS Media Kodi Repository veröffentlicht** ([PR #16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16), 213 GitHub-CI-Tests erfolgreich; [Publish-Workflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143872867) erfolgreich). Der reale Android-TV-Test zeigt erstmals eine sichtbare XCMate-Sidebar mit Fokus und unterem OSD; **nicht vollständig abgenommen**, da EPG und Fernbedienung noch nicht stabil sind. Issue #12 offen. EPG-Quellfehler genauer diagnostiziert, vollständige Vorschau Issue #13 und XCMate Skin Issue #14 bleiben offen.
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Kodi-Repository:** GS Media Kodi Repository 1.7.0  
**Angezeigter Add-on-Name:** XCMate  
**Technische ID:** `plugin.video.xtreammate` (aus Kompatibilitätsgründen NICHT ändern)

Diese Dateien sind die verbindliche Arbeitsgrundlage für spätere Chats und Entwickler. **Zuerst [`CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md`](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md) als aktuellen Codex-Arbeitsauftrag und [`CODEX_STATUS_CURRENT_DE.md`](CODEX_STATUS_CURRENT_DE.md) für den Release-/Projektstand lesen**, danach `KODI21_FIX_022_DE.md`, `PROJECT_HANDOFF_DE.md` und `ROADMAP_AND_QA_DE.md`. Ältere Dokumente enthalten historische Versionsstände.

**Verbindliche nächste Ausbaustufen:** [EPG-Status & Vorschau – Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) **vor** [XCMate Skin – Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14). Beides geplant, noch nicht implementiert. Der Live-TV-Navigationsfehler wurde auch mit 0.1.23 bestätigt und bleibt in [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) offen.

**Aktuelle Bearbeitung:** [0.1.24 Kodi-21-Fix, 213 Tests und Android-Abnahmeplan](KODI21_FIX_024_DE.md) über [gemergten PR #16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16). **Normales Kodi-Repositoryupdate ist verfügbar**; Android-Abnahme noch offen. Issue #12 und #13 nicht schließen.

**NEUER Android-TV-Praxistest zu 0.1.24 (18.10.):** Echte XCMate-Senderliste, Fokusmarkierung, untere OSD-Leiste und Zusatzmenü werden erstmals sichtbar über laufendem TV dargestellt. **Noch nicht abgenommen:** zuverlässiger D-Pad-Kanalwechsel/Bedienung und EPG-Titel. Der `XCMate · EPG`-Modus zeigt derzeit nur die Senderliste ohne Jetzt/Danach; Codex soll fehlenden Kurz-EPG-Fallback und Quellenstatus untersuchen. [Gerätetest und Folgeauftrag](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md) · [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) · [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13).

**Neue verbindliche Bedienvorgabe:** [TV-OSD/EPG/Performance-Spezifikation](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) und [Umsetzungs-Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17). **1× OK:** Senderinfo mit Icon, Jetzt/Danach, Laufzeit/Fortschritt. **2× OK bzw. Runter bei geöffneter Info:** untere Player-Bedienleiste. **Links:** schneller lokaler Senderkatalog mit Jetzt, Von–bis und EPG-Fortschritt. Erst funktionsfähige EPG-Daten, dann finaler UI-/Skin-Ausbau. Noch nicht implementiert.

**AKTUELLER CODEX-ARBEITSAUFTRAG:** [CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md) – verbindlich zuerst lesen. 
**Gerätestand 0.1.24:** Echte TV-Senderliste, sichtbarer Fokus und untere Steuerung sind erstmals bestätigt; **EPG und Navigation noch nicht stabil**, Senderliste langsam. Ziel: 1× OK Infobar, 2× OK/Runter Bedienleiste, Links EPG-Senderliste. [Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12).

## Dokumente

- [0.1.25: implementierter TV-/EPG-Testkandidat und vollständige Android-Abnahme](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md)

- [**Codex-Arbeitsanweisung: Infobar, EPG-/Menüstabilisierung, schnelle Senderliste**](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md) – **verbindlicher Einstieg**.


- [NEU: verbindliche TiviMate-orientierte XCMate-Infobar, EPG-Liste, Tastenkonzept und Performance](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) – [Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17)

- [NEU: Android-TV-Test 0.1.24 – Overlay sichtbar, Navigation teilweise, EPG leer](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md)

- [0.1.24: implementierte Korrekturen, getrennte EPG-Analyse, Paket und Android-Abnahme](KODI21_FIX_024_DE.md)

- [Vollständige Android-TV-Codex-Übergabe 0.1.23 / P0 TypeError und EPG](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md) – **erste Lektüre für Codex; bestätigte Gerätewerte, Kodi-ControlList-API und Abnahmetests**.

- [Aktueller Codex- und Release-Status (verbindlicher Einstieg)](CODEX_STATUS_CURRENT_DE.md)

- [0.1.22: Korrekturen, Testbericht und Android-Abnahme](KODI21_FIX_022_DE.md)

- [Projektübergabe / Architektur / aktueller Zustand](PROJECT_HANDOFF_DE.md)
- [Neue Serienfunktion: Fortsetzen, Gesehen-Status, nächste Folge](SERIES_PROGRESS_SPEC_DE.md)
- [Freigegebenes Design / UI-Themes / benötigte Grafikdateien](DESIGN_SYSTEM_DE.md)
- [TiviMate 5.3.3: statische Navigations- und Fernbedienungsanalyse](TIVIMATE_5_3_3_NAVIGATION_ANALYSIS_DE.md)
- [TiviMate 5.3.3: Fernbedienung Player, EPG, Suchoptionen – Nutzerfotos](TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md)
- [TiviMate 5.3.3: TV-Overlay, EPG, Hauptmenü und Filmansichten – weitere Nutzerfotos](TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md)
- [TiviMate 5.3.3: Einstellungsstruktur, Allgemein, Wiedergabelisten, EPG und Optik – 10 Fotos](TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md)
- [TiviMate 5.3.3: Wiedergabe, Kindersicherung, Sonstiges, Suche, Aufnahme, VOD und Über – 10 weitere Fotos](TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md)
- [Fotoverifizierter Einstellungsvertrag als JSON (ohne persönliche Daten)](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json)
- [Originalgrafiken: Namen, SHA-256, ZIP und GitHub-Uploadstatus](ARTWORK_ASSET_MANIFEST_DE.md)
- [Popup-Entwicklungsplan 0.1.15–0.1.19 und Android-Abnahmekriterien](POPUP_UI_IMPLEMENTATION_PLAN_DE.md)
- [Roadmap, offene Fehler, Release- und Android-Testplan](ROADMAP_AND_QA_DE.md)
- [Kopierfertiger Einstiegstext für neuen Chat](NEW_CHAT_COPY_BLOCK_DE.md)

**Wichtig:** Dokumentierte Anforderungen sind nicht automatisch implementiert. Der Status jeder Funktion steht in Projektübergabe/Roadmap. Die endgültigen freigegebenen Rastergrafiken wurden im Chat bereitgestellt; prüfe vor einem Build, ob die Bilddateien im Repository liegen und ob das Add-on bereits darauf verweist. Niemals Zugangsdaten, komplette Xtream-URLs mit Zugangsdaten oder private Kodi-Profilordner committen.
