# XCMate / Codex – aktueller Projekt- und Release-Status (verbindliche Übergabe)

> **NEUER VERBINDLICHER CODEX-AUFTRAG 19.10.2026 – Ziel 0.1.27:** [Sechs-Punkte-Hauptmenü, Einstellungen, großer gruppenbasierter EPG und Aufnahmepfad](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) · [Issue #23 Startmenü/Settings](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23) · [Issue #21 7–10-Tage-EPG und Timer](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). **Neuer Android-0.1.26-Befund:** Update über Kodi hat funktioniert, Nutzer bestätigt erfolgreiche grundsätzliche Live-TV-/Menübedienung und gelungene Optik; die detaillierten 10×-Fernbedienungstests sind noch nicht dokumentiert. **Unverändert erhalten:** erste OK-Infobar, dreistufige Playersteuerung und Kodi-native Remote. **Neu:** Startseite **nur** Startkanal, Live-TV, EPG, Filme, Serien, Einstellungen. Unter Einstellungen Accounts/Portale, Startkanal, EPG, Gruppen, optional lernbare Fernbedienung, Player, Aufnahmeordner (`recordings_folder` beibehalten), Darstellung, Wartung/Diagnose. Großer EPG startet in Sendergruppe des Startkanals, Links → Gruppenwechsel, Tage 7–10 nach tatsächlich verfügbarer Quelle. **Noch kein Build/Release 0.1.27**: 0.1.26 bleibt produktiv; Implementierung auf neuem Branch mit Tests/PR, keine eigenmächtige Veröffentlichung. GPL-/Herkunftsvermerke bewahren.


> **RELEASE-STATUS 19.10.2026 – VERBINDLICH:** **XCMate 0.1.26 ist im regulären GS Media Kodi Repository veröffentlicht.** [PR #22](https://github.com/artattakk-creator/kodi-noodleprivate/pull/22) geprüft/übernommen, Merge `cfbe1207fc344c77fbe2042b07f10a2e21fefc03`. [250/250 PR-CI-Tests](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39230063504) erfolgreich; automatischer [Publish-Workflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39240004268) erfolgreich; `addons.xml` und `addon.xml` bestätigen beide **0.1.26**; produktive ZIP hat **262100 Bytes**, veröffentlichte SHA-256 **`4fc88c80202d4c81c07817bb622ea2072cc6ba0c07c01ac45bc420fb809a752a`**, unabhängig gegen reale ZIP überprüft. **Android-TV-Abnahme der 0.1.26 ausstehend**: LEFT aus Live → Senderliste → Gruppen, dreistufiges OSD, Fokus, Pause/Stop/Seek und Inputdiagnose müssen auf dem Gerät geprüft werden. Erste 0.1.25-Infobar sollte laut Freeze unverändert sein, jedoch noch nicht unter 0.1.26 bestätigt. **Nicht enthalten:** 7–10-Tage-EPG, Auto-Tune oder Aufnahmeplanung. Die darunter stehenden Hinweise `Produktiv 0.1.25`, `0.1.26 nur Testkandidat` beschreiben den historischen Branch-Stand und sind nicht mehr aktuell. Der vorgängig dokumentierte Upstream-Lizenzkonflikt aus [Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19) ist weiterhin **ungeklärt**; dieses Release löst die Rechtsfrage nicht.


## Aktuell: 0.1.26-P0-Kandidat geprüft, Android-Abnahme offen – 19.10.2026

**Produktiv bleibt 0.1.25.** Entwicklungsbranch `fix/xcmate-026-remote-three-level`,
Basis `3f5e898`. [Vollständige Änderungen, Testbericht, ZIP und Android-Plan](IMPLEMENTIERUNG_026_P0_REMOTE_OSD_DE.md).
Die erste OK-Infobar ist unverändert; die folgende 0.1.25-Gerätemeldung bleibt der reale Ausgangsbefund.

**GitHub:** [Entwurfs-PR #22](https://github.com/artattakk-creator/kodi-noodleprivate/pull/22),
Code-/Paketcommit `902b3dd`. [CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39229913403),
Build/Tests/Upload grün, Produktions-Publish übersprungen.
[Testartefakt xcmate-review-22](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39229913403/artifacts/12176890835)
mit eigener CI-Paket-SHA, bis 02.11.2026 verfügbar.

- **P0 implementiert:** nativer Links-Dispatch trotz altem Remote-Profil, zusätzliche gelernte
  Aliase erhalten, kein Profildateizugriff pro Taste; drei getrennte Ebenen Info → Player →
  Einstellungen mit Up/Down/Back. Dynamisches Play/Pause, getrenntes Stop, Seek/Live-Ende nur
  bei Kodi-Freigabe. Keine globale Keymap oder fremde Add-on-Änderung.
- **Ursache präzise:** Profilkollision am Altcode reproduziert; konkretes damaliges Android-Profil/
  Action-ID weiterhin unbekannt. Omega stellt Python-Callbacks auch nach nativer Listennavigation zu.
  Neue 64-Event-Diagnose mit Mapping/Fokus/Modus und LEFT-Zählern bleibt nach Stop/Restart verfügbar.
- **250 Tests bestanden**, vor/nach isoliertem Build; 39 strikte Overlaytests, 24 HTTP-/EPG-Tests
  zusätzlich mit httpx. Erste Infobar-Controldefinitionen bytegleich und Renderfunktion AST-identisch
  zu `main`. Native Android-Bindings/Renderer nicht in der Cloud geprüft.
- **Test-ZIP 0.1.26 / Dienstbuild 26:** 262100 Bytes, 77 Dateien bytegenau geprüft,
  SHA-256 `751f47fc0fddd17ac8f576abc3e13dc6455c143ebd00d419b85acf2d765aaa3a`.
  [ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.26.zip).
  Produktionsindex/0.1.25-Pakete unverändert; kein Merge/Publish.
- **P1/P2 separat:** [Analyse und Folgeplan](PLAN_EPG_LANGZEIT_TIMER_DE.md). Die 48h-Grenze ist
  eine Statuszählung, die 48er-Grenze beschneidet UI-Ereignisse. Noch kein 7/10-Tage-Browser,
  Auto-Tune oder EPG-Aufnahmescheduler. Android-Aufnahmeengine nicht nachgewiesen.
- **Nächste Abnahme:** Kandidat installieren, Kodi neu starten, Version/Build 26 kontrollieren;
  LEFT 10/10 und drei Ebenen, Seek-Fähigkeit, Fokus, Isolation und gespeicherte Diagnose prüfen.
  Erst danach ausdrückliche Freigabe für normalen GS-Media-Repositoryupdateweg. Issues #12/#20
  bis Geräte-PASS offen lassen. Keine 0.1.26-Funktion als auf Android bestätigt ausgeben.

Die nachfolgenden Release-/Kandidatenabschnitte dokumentieren frühere Stände.

> **AKTUELLER ANDROID-TV-TEST VON XCMate 0.1.25 – 19.10.2026:** Die **kompakte 1×-OK-Infobar funktioniert** und ist optisch freigegeben (**Freeze**). **P0 offen:** D-Pad **Links** öffnet im TV-Vollbild weder Senderliste noch beim zweiten Links die Gruppen; Sender-EPG ist nur über OSD-Button erreichbar. **Neue verbindliche Menüfolge:** 1× OK Infobar → 2× OK oder Runter echte Tape-Deck-Playerleiste → weiteres Runter Einstellungen mit Bild/Ton/Untertiteln/EPG/Sendergruppen. **P1/P2:** 7–10-Tage-EPG (nur echte Feed-Reichweite) mit Erinnerung, ausdrücklich optionalem Auto-Umschalten und nur bei funktionsfähiger Aufnahmeengine geplanten Aufnahmen. [Vollständiger Codex-Folgeauftrag](ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md); [Issue #20 Links und OSD](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20), [Issue #21 Langzeit-EPG und Timer](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). **Keine neue Add-on-Version freigegeben oder gebaut**, aktuell bleibt 0.1.25. Arbeiten auf eigenem Branch, PR/Tests, kein Merge ohne Nutzerfreigabe.


> **Lizenz-/Herkunfts-Audit 19.10.2026:** [Vollständiger Datei-/Codevergleich XCMate 0.1.25 und unabhängiger V2-Umbauplan](CODE_ORIGIN_LICENSE_AUDIT_025_DE.md) · [Rechteklärungs-Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19). Der früheste GS-Media-Fork-Snapshot (13.10.) verglichen mit 0.1.25 ergibt 6 Python-Module bytegenau unverändert und teils hohe Altzeilen-Überlappung in `main.py`, `player.py`, `epg.py`. **Dringender offener Rechtekonflikt:** Upstream-`addon.xml` deklariert GPL-2.0-only, aber mr-evil1s Root-`LICENSE` vom 01.10.2026 sagt „Alle Rechte vorbehalten“ und untersagt Kopieren/Modifizieren ohne schriftliche Genehmigung. **Kein rechtsgültiger Schluss zugunsten einer Lizenzvariante; keine Umstellung auf proprietär, keine Entfernung der Herkunftshinweise.** Externe juristische Prüfung der Rechtekette und Original-ZIP-Vergleich erforderlich. Dieses Audit ist separat von der XCMate-0.1.25-Android-Abnahme; **Produktionscode und Lizenzdateien unverändert**.

## VERBINDLICHER NEUER RELEASE-STAND 18.10.2026 – XCMate 0.1.25 veröffentlicht

- **Version im öffentlichen GS Media Kodi Repository: `0.1.25`**, aktualisierbar über Kodi »XCMate → Informationen → Aktualisieren«. Addon-ID bleibt `plugin.video.xtreammate`.
- Nach Nutzerauftrag wurde [PR #18](https://github.com/artattakk-creator/kodi-noodleprivate/pull/18) aus `fix/xcmate-infobar-epg-navigation` geprüft, vom Entwurf auf Review gesetzt und als `601c421b004f746341ecf3a8c0f7bf1200a7c84d` nach `main` gemergt. Kein Änderungskonflikt (`behind_by=0`).
- GitHub-PR-[CI-Run 39155542397](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39155542397) **237/237 Tests bestanden**; automatischer [Push-/Publish-Run 39156573306](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39156573306) **erfolgreich**, ebenfalls 237 Tests.
- `src/plugin.video.xtreammate/addon.xml` und `addons.xml` zeigen beide **0.1.25**, `addons.xml.md5` im Build neu erzeugt. Veröffentlichte ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.25.zip` (**259497 Bytes**), SHA-256 `0022633e056940fb6a338b1d5ccb01ce2585d6093652242e7579b0b5b7418ae3`; eigene SHA-256-Berechnung gegen die veröffentlichte Paket-Sidecar **erfolgreich**. Der frühere Branch-Testpaket-Hash `583026db...` ist **nur historisch** und gilt nicht für das neu gepackte Produktionspaket.
- **Implementierte Änderungen laut PR:** 1× OK kompakte EPG-Infobar, 2× OK/Runter Player-Steuerung; lokaler Now-/Next-Resolver und EPG-Status & Vorschau; vorberechnete Katalog-/EPG-Indizes, 8 sichtbare Senderzeilen, Cache-Härtung, lokale Logo-Icons.
- **Echter Android-TV-Test steht aus**: weder erfolgreiches EPG/Import noch native 1×/2× OK, fokussierte Tasten oder Beschleunigung gelten als verifiziert. Cloud-Zugriff auf öffentliche DE/AT/CH-Feeds laut Codex an ProxyError gescheitert, nicht als Provider-Ausfall bewerten. [Geräteplan](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md). Bestehende Issues [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17) bis zur Gerätetest-Abnahme offen. Separater XCMate Skin [#14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14) bleibt zukünftig.
- **Nächster Schritt:** Auf Android-TV normal über GS-Media-Kodi-Repository von `0.1.24` auf `0.1.25` aktualisieren; Kodi ganz neu starten; unter Diagnose `service build=25` bestätigen; ersten und zweiten OK-Druck, Down/Links, EPG-Quellenstatus, echtes JETZT/DANACH + Start/Ende + Fortschrittsbalken, Senderwechsel und Fokus prüfen; Fremd-Add-on/VOD/Stop gegentesten. Neue Fehlerstände dokumentieren; keine Issue-Schließung ohne reale Abnahme.
- **Hinweis:** Unterhalb dieser neuen Überschrift verbliebene Tabellenangaben »nicht in main / 0.1.24 produktiv« sind historische Codex-Kandidatenangaben, **nicht** der aktuelle Status. Bei künftigen Codex-Chats diesen Block als erste Statusquelle verwenden.


## Entwicklung 0.1.25 – aktuelle Übergabe (18.10.2026)

**Branch:** `fix/xcmate-infobar-epg-navigation`, Basis `09b04e0` von `main` (0.1.24). **Implementierung und vollständiger Android-Testplan:** [IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md).

| Status | Ergebnis |
| --- | --- |
| Implementiert | Erstes OK: kompakte echte Senderinfo; zweites OK/Runter: Bedienung; Links: acht sichtbare EPG-Senderzeilen, 100er-Seiten; Untertitel und echte Programmseite. |
| Daten | Gemeinsamer lokaler XMLTV/Kurz-EPG-Resolver mit manuellen Overrides, Quellenstatus & Vorschau, atomarer Cache, alter brauchbarer Cache bleibt lesbar. |
| Lokal geprüft | **237 Tests vor/nach isoliertem Build**, **24 HTTP-/Cache-Tests zusätzlich mit httpx**, strikte Omega-Verträge, 75 Paketdateien bytegenau geprüft. |
| GitHub-CI / PR | [Entwurfs-PR #18](https://github.com/artattakk-creator/kodi-noodleprivate/pull/18), Code-/Paketcommit `297b934`; [CI-Run 39155424177 erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39155424177). Test-/Build-/Upload-Schritte erfolgreich, Produktions-Publish übersprungen. |
| Auf main / veröffentlicht | **Nein: regulär bleibt 0.1.24. Kein eigenständiger Merge/Publish.** |
| Android bestätigt | **Nein: sämtliche 0.1.25-Abnahmeschritte offen.** 0.1.24-Overlaybilder belegen kein neues EPG oder neues OK-Verhalten. |

**Testpaket 0.1.25 / service build=25:** [ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.25.zip), 259497 Bytes, SHA-256 `583026db01ffceb410e67784113e479746d1ea4e91cea38727d3a3b86f7775b4`. Der Builder erzeugt für jedes neue XCMate-ZIP automatisch eine neue Sidecar-SHA; Kandidatenhash nicht auf ein später neu gepacktes Main-ZIP übertragen.

**Konkrete Ursachen und Änderungen:** Der bisher fehlende Kurz-EPG-Pfad des Overlays ist mit normaler Senderliste/Kontext und Vorschau vereinheitlicht. Neue manuelle ID wirkt auch bei altem Alias. Die Ownership-Prüfung liest auf Tastendruck keinen vollständigen Katalog mehr; Index/Snapshot werden im Dienst vorbereitet. Keine HTTP-/XMLTV-/Cache-Leseoperationen im TV-Render-/Inputpfad. Erster OK-Druck löst keine Playeraktion aus. Quellenstatus ist pro Portal/Quelle persistent; XMLTV-Einlesen und erfolgreicher Cache-Commit bleiben getrennt.

**Prüfgrenzen:** Öffentliche DE-/AT-/CH-Testabrufe scheiterten in der Cloud jeweils vor Datenempfang mit `ProxyError` (0 Bytes); keine Aussage zu Feedverfügbarkeit oder neuen Gerätefehlern. Layoutbilder sind ausdrücklich Fixturemodelle ohne nativen Renderer. Android-Latenz, Fokus und mindestens ein echter Sender mit Now/Next/Von–bis/Progress müssen am TV bestätigt werden. Issues #12/#13/#17 bleiben offen, Skin #14 bleibt separat.

**Review-Artefakt:** [xcmate-review-18](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39155424177/artifacts/12147205646), API-bestätigt bereitgestellt, 14 Tage verfügbar. Die dokumentierte bytegenaue ZIP-Prüfung betrifft das eingecheckte lokale Paket; das neu gepackte CI-Artefakt enthält seine eigene SHA.

**Nächster Schritt:** Entwurfs-PR/CI und Kandidat prüfen, vorbereiteten Android-Test durchführen. Erst danach mit Nutzerfreigabe der normale GS-Media-Updateweg. Quellen, Konten und Zuordnungen behalten, globale Keymap aus. Noodle Private, andere Add-ons und Produktionsindex unverändert.

## Vorheriger Produktions- und Geräteverlauf (0.1.24 und älter)


**AKTUELLER CODEX-ARBEITSAUFTRAG:** [CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md) – **zuerst lesen**. Die vorherige UX-Spezifikation [TV_OSD_EPG_REMOTE_UX_SPEC_DE.md](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) gilt ergänzend; [Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), EPG [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), Fernbedienung [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12). **Kein neues Add-on veröffentlicht**: `main` enthält weiterhin 0.1.24 plus Dokumentationsänderungen. Erstes OK = kompakte Senderinfo (Logo, Jetzt/Danach, Von–bis, Fortschritt, Restzeit), zweites OK/Runter = Player-Menü, Links = schnelle EPG-Kanalliste. Gerätebild bestätigt nur den Overlaystart, nicht die noch fehlenden Funktionen.

**Stand:** 18.10.2026  
**Veröffentlichte XCMate-Version:** `0.1.24` (18.10.2026, reguläres GS-Media-Kodi-Repository). **Android-TV-Gerätetest teilweise positiv:** Dialog, Senderliste, Fokus und unteres OSD erstmals sichtbar, aber zuverlässige Bedienung/EPG/Listenlatenz noch offen. **Gesamtabnahme ausstehend.** Die 0.1.23 zeigte `TypeError` im TV-Dialog; Codekorrektur und EPG-Diagnose in 0.1.24 implementiert. Siehe [Testbericht](KODI21_FIX_024_DE.md) und [Ursprungsübergabe](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md).
**Technische Kodi-ID:** `plugin.video.xtreammate` – nicht ändern  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Hauptbranch:** `main`  
**Codex-Entwicklungsbranch:** aktuell `fix/xcmate-infobar-epg-navigation` (0.1.25-Kandidat); der 0.1.24-Branch wurde über PR #16 übernommen und ist historisch.
**Übernahme 0.1.22:** [Pull Request #11](https://github.com/artattakk-creator/kodi-noodleprivate/pull/11), Merge-Commit `c14d7815bf0ca2e93dd3e1fa5225ca1df36c8f54`.
**Veröffentlichung 0.1.22:** GitHub-Action [Publish GS Media Kodi updates](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39126897807) erfolgreich; `addons.xml` meldet XCMate `0.1.22`, ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.22.zip` vorhanden.
**Letzter geprüfter Repository-Stand nach Auto-Publish (vor dieser Statusaktualisierung):** `9b590ea2dc0983fa75b084582431065211de1484`.

**VERBINDLICHER CODEX-ARBEITSAUFTRAG:** [Vollständige Android-TV-Codex-Übergabe 0.1.23 / P0 TypeError und EPG](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md). Der hier folgende Ablauf ist die detailreiche historische Diagnosedokumentation; die neue Datei enthält den konsolidierten P0/P1-Plan und den sicheren nächsten Branch-/PR-Ablauf.

## Neue verbindliche Live-TV-UX-Spezifikation – 18.10.2026

**Neue Nutzeranforderung, noch nicht umgesetzt:** [vollständiges Bedienkonzept für XCMate-TV-Infobar, Senderliste, EPG & Performance](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) und [Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17).

- **1× OK bei laufendem TV** öffnet INFO_BAR **mit Senderlogo/-icon, Sendername, aktuellem EPG-Titel, Start-/Endzeit, Fortschrittsbalken, vergangener/verbleibender Zeit und nächster Sendung**. Keine primäre Pause/Stop-Schaltfläche.
- **Zweites OK oder Runter bei geöffneter INFO_BAR** öffnet PLAYER_CONTROLS mit Untermenü für Audio/Ton, Video/Bild, Untertitel, EPG, Systemeinstellungen. Zweites OK darf keine Aktion versehentlich aktivieren.
- **Links** öffnet eine **schnelle, aus lokalem Cache vorbereitete Senderliste**, pro sichtbarer Zeile Sendername/-icon, Jetzt-Titel, Beginn/Ende und nach Möglichkeit Next/Progress. Mehrfache langsame Katalog-/EPG-Ladungen im D-Pad-Event-Handler vermeiden. Maßgeblich sind echte Android-Latenzmessungen.
- **Datenvorbedingung:** EPG-Sender-/Source-Matching und Kurz-EPG-Fallback im Live-Overlay mit der regulären Senderliste vereinheitlichen (Issue #13). Bei fehlenden EPG-Daten eindeutigen Missing-State statt Fake-Titel/Progress. Große Gruppen (2746/53664 Sender) und 100er-Paging performant halten. Alte Kodi-Fontglyphenfehler separat.
- **Zustandsmodell:** `LIVE_FULL → INFO_BAR → PLAYER_CONTROLS → MORE_SETTINGS`, `Links → CHANNEL_LIST`; `Down` in INFO_BAR öffnet Menü, während Hoch/Runter im reinen Vollbildzustand die bisherige Senderwechsel-Funktion erhält. Sichere Kodi-Fokus-/onControl-/onAction-Deduplizierung.
- **Status:** reiner Dokumentationsauftrag, kein neues Add-on, keine Kodi-Veröffentlichung und keine Android-Abnahme. Weiterhin Version 0.1.24 auf `main`. Codex soll auf neuem Branch + PR vorgehen und die Umsetzungsreihenfolge P1-EPG-Daten → zweistufige Infoleiste → Caching/Geschwindigkeit → Design für späteren XCMate Skin beachten.

## NEUER Android-TV-Gerätetest 0.1.24 – wesentlicher Fortschritt, EPG weiter offen (18.10.2026)

**Priorität für den nächsten Codex-Einstieg:** [vollständiger neuer Gerätebefund / End-to-End-EPG und Fernbedienung](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md).

- Drei Nutzerfotos zeigen tatsächlich das XCMate-`WindowDialog` **über laufendem TV**: `XCMate · EPG`, Kanalansicht mit `2746 Sender`, `Seite 2/28` und sichtbarer Fokusmarkierung, unteres OSD mit `Weitere` sowie eine zweite Leiste mit `Ton / Bild / EPG / Einstellungen / Sendergruppen`. Gegenüber 0.1.23 ist der P0-`TypeError` im beobachteten Ablauf praktisch überwunden. Der EPG-Modus ist aber nur eine Senderliste ohne Sendetitel.
- **Unbestätigt/offen:** Zuverlässiges Umschalten und Durchsteuern mit D-Pad/OK/Zurück (Nutzer meldet noch Unzuverlässigkeit), öffnender EPG-Button und tatsächlicher Guide-Import. Fokusbilder beweisen nicht alle Tastenaktionen. Issues #12 und #13 OFFEN lassen.
- Codebefund: `live_overlay._render()` benutzt `load_cache` für Guide-Zeilen, **nicht** den `cached_short_guide`-Fallback der regulären Kodi-Senderliste. `_epg()` zeigt lediglich vorhandenen Kurz-EPG zum aktiven Sender oder triggert asynchrones Nachladen mit Info „Gleich erneut öffnen“. Keine EPG-Timeline vorhanden.
- Zusätzlich die fehlenden Symbolglyphen (leere Kästchen) und mögliche Unterkanten-/Safe-Area-Darstellung bei der späteren UI-Pflege erfassen; `XCMate Skin` als separater Zukunftsplan.
- **Nächster Gerätetest:** tatsächlich installierte 0.1.24 und `service build=24` in Diagnose bestätigen, gezieltes OK auf `EPG` der Extras-Zeile mit Ergebnisfoto, nach ~30–60 s wiederholen, danach EPG-/Source-/List-Diagnose aufnehmen. Einen EPG-tauglichen Sender wählen und separat D-Pad/OK-Kanalwechsel testen; keine globale Keymap einschalten.

## Veröffentlichungsnachtrag 0.1.24 – verbindlicher Stand ab 18.10.2026

- **Freigabe/Übernahme:** Der Nutzer beauftragte explizit die Prüfung und Übernahme per regulärem Kodi-Update. GitHub-PR [#16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16) geprüft und über Merge-Commit `199f4d1231ce01f5d3c15d6db7ec253df721be9a` nach `main` übernommen.
- **CI:** GitHub [Run 39143441999](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143441999) erfolgreich mit **213/213 Tests**; aktualisierte Kodi-GUI-Vertragstests und EPG-Regressionen enthalten.
- **Produktive Veröffentlichung:** [Push-/Publish-Workflow 39143872867](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143872867) erfolgreich. `src/plugin.video.xtreammate/addon.xml` und `addons.xml` weisen beide `0.1.24` aus; ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.24.zip` im `main` vorhanden und über das bestehende GS-Media-Repository abrufbar. `addons.xml.md5` aktualisiert.
- **Build-Prüfsumme:** GitHub Actions hat die 242152-Byte-ZIP neu gepackt; die Kandidaten-SHA `1100ea73...` gilt **nur für das historische Branch-Paket**. Die veröffentlichte 0.1.24-ZIP hat SHA-256 `ddb4a7eb29fece8213f0254af9fb0b8fb949466746a026d0fed75342b8acb376`; die Sidecar-`.zip.sha256` wurde auf diesen Wert korrigiert. Bei späteren Releases sollte der CI-Paketbau Prüfsummen automatisch neu schreiben (separater Build-Hardening-Auftrag).
- **Gerätestatus:** **Nicht** behaupten, dass der P0 auf Android behoben ist, solange sichtbare TV-Sidebar, Fokus und Fernbedienung nicht an Version 0.1.24 bestätigt sind. Globale Keymap deaktiviert lassen, BINGIE MOD/fremde Add-ons gegenprüfen. EPG-Verarbeitung und echte Jetzt/Danach-Inhalte ebenfalls noch offen. Issues [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) offen lassen; XCMate Skin [#14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14) später.
- **Nächster Schritt:** Auf Android-TV in Kodi `XCMate → Aktualisieren` auf 0.1.24, Kodi vollständig neu starten, `service build=24` in `TV-Fernbedienung: Diagnose` prüfen; Live-Sender und TV-Overlay/Focus/DPAD/OK/Zurück testen; danach EPG-Quellenfehlercodes und Senderliste untersuchen. Details im [Abnahmeplan 0.1.24](KODI21_FIX_024_DE.md).

## Implementierung nach Android-Befund: Testkandidat 0.1.24 (18.10.2026)

**Aktueller Test-/Änderungsbericht:** [KODI21_FIX_024_DE.md](KODI21_FIX_024_DE.md). P0-Codekorrektur lokal geprüft, Android-Abnahme offen. Die vollständige Ausgangsübergabe und Issues #12/#13 wurden gelesen.

**GitHub:** [Entwurfs-PR #16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16), Code-/Paketcommit `1dc780f`; [CI-Run 39143315938 erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143315938). Review-Artefakt `xcmate-review-16` erfolgreich hochgeladen; Produktions-Publish übersprungen. Prüfgrenzen des Cloud-Artefaktdownloads stehen im vollständigen Bericht. Kein Merge und keine Veröffentlichung auf `main`.

- API-Fehler nachgewiesen: `ControlList(itemHeight, space)` wird von den strikten Omega-Signaturen mit `TypeError` abgewiesen. Korrigiert auf `_itemHeight`, `_space`; zuvor 18 Starttests rot, jetzt 23 strikte Dialog-/Callbacktests grün. Weitere direkte Kodi-GUI-Aufrufe und lokale Aliase werden mit einem repositoryweiten Signaturtest geprüft.
- Navigator rendert höchstens 100 Sender je Seite statt bis zu 53.664 EPG-Zeilen. Seitenlinks, letzter Sender und absolute Tune-Zuordnung getestet. Derselbe `WindowDialog.onInit`-Fehler im Tastenanlerndialog ebenfalls korrigiert.
- Persistente sichere Fehlerstufe/-klasse für Dialoge und EPG; EPG unterscheidet Download, Parse, Merge, HTTP/XMLTV-Eingangs- und Entpackgrenzen sowie Kanal-/Sendungslimits. `DOWNLOAD_FAILED` war bisher ein Catch-all nach bereits erfolgreichem Lesen; 3,59 MB belegen keine Größenüberschreitung. Reale externe Gerätefehler bleiben bis zum nächsten Abruf unbekannt.
- **213 Tests bestanden**, vor und nach isoliertem Build; Syntaxprüfung und ZIP-/Indexprüfungen bestanden. **19 HTTP-/EPG-Tests** zusätzlich mit httpx 0.28.1 bestanden. XCMate-ZIP 0.1.24: **242152 Bytes**, SHA-256 `1100ea73a974dfe92d731d4384826a15c20c0be9cac5dc5d205f8ca03f267286`; alle 56 Paketdateien stimmen bytegenau mit den Quellen überein.
- **Issue #13 nicht vollständig umgesetzt:** eigener EPG-Status-/Titelvorschau-Menüpunkt und dauerhafte Quell-/Portalübersicht bleiben offen. Keine Bestätigung funktionierenden Geräte-EPGs. Kein Skin-Neubau.
- **Veröffentlicht bleibt 0.1.23.** Kandidat und SHA liegen im Entwicklungsbranch; PR-CI stellt ein zusätzliches Review-Artefakt bereit. `addons.xml`, produktive ZIPs, Noodle Private und fremde Add-ons unverändert. Keine globale Keymap aktiviert.

**Nächste Freigabestufe:** PR prüfen; erst nach ausdrücklicher Merge-Freigabe den vorhandenen Publish-Workflow auf `main` ausführen lassen. Danach reguläres GS-Media-Repositoryupdate auf Android, Kodi-Neustart, Version 0.1.24 / Dienstbuild 24 kontrollieren und den verlinkten Android-Testplan durchführen. Issue #12 bleibt bis zur Geräteabnahme offen.

## Historische Befunde und frühere Übergaben

Die folgenden Abschnitte dokumentieren 0.1.23 und ältere Stände; für die aktuelle Implementierung und nächsten Schritte gilt der obige 0.1.24-Testbericht.

## P0 eingegrenzt durch FÜNF DIAGNOSEFOTOS von Android-TV / XCMate 0.1.23 (18.10.2026)

**Version am Gerät jetzt definitiv bestätigt: 0.1.23.** Wiedergabe und Sitzungserkennung sind erfolgreich; das programmatisch erzeugte **TV-`WindowDialog` scheitert mit `TypeError`**. Es liegt eine konkrete, überprüfbare API-Inkompatibilität im Overlay-Code nahe, also nicht erneut auf Verdacht Stream-Mapping/Remote-Keymap verändern.

- **Gerät:** Hintergrunddienst `LÄUFT`, Heartbeat 0,1 s, 1497 Schleifen, allgemeiner Dienstfehler „keine gemeldet“. `Letzte Live-Beobachtung: Video JA / XCMate-Sitzung JA`; `Live-Sitzungswiederherstellung: XCMate-Live-Stream erkannt`; `ownership`-Verlauf enthält `URL_IDENTITY`.
- **TV-Dialog:** `Letzte TV-Einblendung: TV-Dialog-Fehler: TypeError`; `Auto-TV-Popup: Fehler: TypeError`. Persistierter Verlauf `CANDIDATE_CREATED → SHOW_FAILED → CLOSED` mehrfach. Zuletzt erneut `CANDIDATE_CREATED`, **kein** Erfolg. `catalog=True, channels=53664`. Kein Fokus-/Inputnachweis für das echte TV-Overlay. Native Keymap ist ausgeschaltet (erwünscht).
- **Sehr starke Ursache:** In `src/plugin.video.xtreammate/resources/lib/live_overlay.py` nutzt `_build_controls()` bei `xbmcgui.ControlList` die Schlüsselwortparameter **`itemHeight=46, space=3`**. In der tatsächlichen Kodi-API-Signatur heißen diese **`_itemHeight`**, **`_space`** mit Unterstrich. Nach Kodi-Dokumentation ist das eine inkompatible Python-Binding-Signatur ([offizielle ControlList-Referenz](https://xbmc.github.io/docs.kodi.tv/master/kodi-base/d8/de1/class_x_b_m_c_addon_1_1xbmcgui_1_1_control_list.html)). `LiveNavigator.show()` ruft zuerst `_build_controls()` auf, dann erst `SHOW_REQUESTED`; eine ungültige ControlList-Signatur löst **`TypeError` vor `SHOW_REQUESTED`** aus, wird als `SHOW_FAILED` protokolliert und der Dialog geschlossen. **Bis zum `kodi.log`-Traceback als starke, nicht als endgültig bewiesene Ursache führen.**
- **Separates Skalierungsthema:** Der Xtream-Index enthält 53.664 Live-Sender. Kodi-UI darf nicht alle Sender oder Now/Next-Aggregate bei jedem Render/Fokuswechsel durchlaufen. Auswahl pro Gruppe bzw. sichtbar begrenzte Lazy-Liste; keine massive GUI-Blockade.
- **Unabhängiger XML-Testdialog:** 9 registrierte Events, zurück (Action-ID 92), `WindowXMLDialog Default/720p` funktioniert. Dies ist **nicht** das gescheiterte `WindowDialog`.
- **EPG:** `NO_NEW_GUIDE`, nach `PROVIDER_LIMIT` (Anbieter-XM LTV erreicht ein Limit). Zusätzlich externe `epg_source: DOWNLOAD_FAILED`, `source_index=2`, `failed=2`, `bytes=3591764`, `limit_bytes=83886080`. Die 3,59 MB liegen unter 80 MiB; der zweite Fehler ist **nicht automatisch eine Größenüberschreitung**, sondern zunächst ein Abruf-/Verarbeitungsfehler. Siehe [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13). Keine erfolgreichen neuen Sendetitel nachgewiesen.

**Codex-Handlungsauftrag:** Zunächst minimale `ControlList`-API-Korrektur und sämtliche übrigen `xbmcgui`-Konstruktorsignaturen überprüfen. Unbedingt **Kodi-Omega-strikte Tests**, welche `itemHeight`/`space` mit `TypeError` verwerfen und `_itemHeight`/`_space` bzw. nachträgliche Setter akzeptieren. `LiveNavigator.show()` inklusive Control-Aufbau und sichtbarem Fokus als Testfall durchlaufen. Fix separater Branch und PR, `main` bis GitHub-CI und Release-Freigabe unverändert. Beim TV-Gerät nach Update echte Sidebar und Tastenevents neu abnehmen, ohne andere Kodi-Add-ons zu beeinträchtigen. Details und Historie in [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12). 

## Realgerät-Rückmeldung nach 0.1.23-Freigabe: TV-Navigation weiterhin nicht geöffnet (18.10.2026)

Der Nutzer startete den gespeicherten Startsender manuell und drückte OK; daraufhin meldete Kodi/XCMate wieder **„TV-Navigation konnte nicht geöffnet werden“**. Der Bericht kam **nach** der Freigabe von 0.1.23, aber die tatsächlich installierte Add-on-Version wurde dabei **nicht explizit erneut überprüft**; zunächst als *mutmaßlicher 0.1.23-Test* kennzeichnen, bis die Version in der Diagnose/den Add-on-Informationen bestätigt ist. Der identische Fehler ist für 0.1.22 bereits gesichert.

In 0.1.23 kommt diese Benachrichtigung aus dem `except` in `service.py` nach erfolgreicher Erstellung eines Navigator-Kandidaten, beim optionalen Keymap-Setup oder beim Anzeigen des Live-TV-Dialogs. Im Dialog-`show()`-Fehlerfall wird `dialog: SHOW_FAILED` persistiert; die genaue Python-Ausnahmeklasse kann in `TV-Fernbedienung: Diagnose` bzw. `kodi.log` stehen. **Ohne Geräte-Diagnose kein spezifischer Fix und keine weitere Versionsfreigabe behaupten.**

**Verbindlich nächster Schritt:** installierte Add-on-Version 0.1.23 überprüfen; Stream stoppen; XCMate → `TV-Fernbedienung: Diagnose` öffnen; komplette Fotos inklusive `=== Gespeicherte Live-/EPG-Diagnose ===`, `Letzte TV-Einblendung`, `Auto-TV-Popup`, `service build=23`, `dialog`/`focus`/`ownership`/`input` sichern. Nach Neustart kann die persistente Diagnose weiterhin vorhanden sein. Fehlermeldung im Log `XCMate WindowDialog startup failed` suchen, sensible Provider-Daten vor Weitergabe entfernen. Siehe [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12). 

## Veröffentlichungsnachtrag 0.1.23 – 18.10.2026 (aktuell maßgeblich)

**XCMate 0.1.23 ist nach [PR #15](https://github.com/artattakk-creator/kodi-noodleprivate/pull/15) in `main` veröffentlicht.**
- GitHub-PR-CI: [202 automatisierte Tests bestanden](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39136334056).
- Merge-Commit: `510b7953b158384d4ab56d3381efad08bfe4efc7`.
- Automatischer Publish-Workflow: [erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39136445020).
- `addons.xml` und `src/plugin.video.xtreammate/addon.xml` weisen **Version 0.1.23** aus. Veröffentlichte ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.23.zip`, 239771 Byte.
- Die GitHub-Actions-Verpackung erzeugte einen **byteweise anderen ZIP-Container** als der Codex-Testbranch bei gleicher Dateigröße. Die anfänglich veraltete SHA-256-Sidecardatei wurde nach Messung der veröffentlichten ZIP korrigiert: `570b71356782516c95cfdcaf64f6a65d722860fbe5a2bc2935d71eb422ebff99`. Der ursprünglich unten genannte Codex-Branch-Hash `d3242e...` ist **nur der historische Kandidatenhash**, nicht der Release-Hash.
- Die Aussage im unten folgenden Abschnitt „nicht nach main übernommen“ beschreibt den **damaligen Testkandidatenstand** und ist durch diesen Veröffentlichungsnachtrag überholt.
- **Neuer bestätigter 0.1.22-Gerätebefund:** Das reale Live-TV löste die Meldung **„XCMate Navigation konnte nicht geöffnet werden“** aus (siehe [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12)). Der Dienst hat damit eine Ausnahme während des Overlay-Startversuchs erkannt; genaue Exception ohne Geräte-Diagnose noch nicht belegt.
- **Geräteprüfung 0.1.23 ausstehend:** Nach Kodi-Repo-Update zuerst Add-on-Version und `service build=23` bestätigen, anschließend Navigation, Dialog/Fokus und EPG im Diagnosetool erfassen. **Nicht** behaupten, dass der P0 auf Android bereits behoben ist.
- Offene Pläne: EPG-Status-/Titelvorschau [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) und [XCMate Skin #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).

## Bearbeitung Issue #12 – Testkandidat 0.1.23 (18.10.2026)

**Status:** Auf `fix/issue-12-live-session-diagnostics` implementiert und lokal geprüft. **Nicht nach main übernommen, nicht produktiv veröffentlicht; Issue #12 bleibt bis zur Android-Abnahme offen.**
Ausgangsstand der Untersuchung: `aa0c3c39d13f1ad120440d2a9c75a0cf59435e1e`. Zwischenzeitliche reine Statusergänzungen aus `main` bis `131ecf6d4615e06156b25d2a71aebcd1725c7d3e` sind übernommen; die Planung für #13/#14 bleibt erhalten.
Implementierung: `dbd6c20`; weitere Diagnoseregressionen und finale Paketfassung im selben Branch. Maßgeblich sind der aktuelle Branchstand und die untenstehende ZIP-Prüfsumme.

### Gesicherte Beobachtung und Grenze der Ursachenanalyse

Der reale Fehlerstand 0.1.22 bleibt verbindlich: Live-TV spielt, OK erreicht nur Kodi-OSD, XCMate-Navigation greift nicht und normale Senderliste bleibt ohne Jetzt/Danach.
Es liegen weiterhin keine Gerätewerte vor, die **eine einzige konkrete Fehlerstelle** in der Zulassung-/Dialogkette beweisen.
Die folgenden Codefälle wurden lokal reproduziert und korrigiert; daraus folgt noch kein Nachweis, dass der Fehler am Fernseher beseitigt ist.

### Korrekturen und gezielte Diagnose

- **Stream-Zuordnung:** Die bisherige bytegenaue URI-Gleichheit verwirft auch äquivalente Schreibweisen (Hostschreibweise, Standardport, URL-Encoding). Der Vergleich normalisiert diese Bestandteile, hält aber Protokoll, Origin, Zugangspfad, Query-Token und Pfadsegmentgrenzen getrennt. Deaktivierte und bei URL-Recovery mehrdeutige Portale werden abgewiesen.
- **Session am Start:** `_play_live` leitet die Session aus einer verifizierten konfigurierten Live-Adresse ab; fehlende/falsche zusätzliche sid-Parameter machen daraus keine beliebige XCMate-Sitzung. Ein vorgegebener Portalbezug bleibt bindend.
- **Redirects:** Ein XCMate-eigenes ListItem erhält über die Kodi-21-`InfoTagVideo.setUniqueIDs`-API nur pid/sid, Zeit und eine zufällige aktuelle Sessionkennung. Die laufende Player-Metadatenkennung muss exakt zur aktuellen Session passen. Damit kann ein veränderter getPlayingFile-Pfad bestätigt werden. Ein unbekannter Redirect **ohne** passende aktuelle Itemkennung wird weiterhin abgewiesen; kein pauschales Übernehmen anderer Videos. Bei Senderwechsel gilt die bestehende begrenzte Acht-Sekunden-Toleranz auch für die vorherige verifizierte Itemkennung.
- **Dienst/Anzeige:** Navigator-Aktivierung wartet auf Kodis tatsächliches FullscreenVideo-Fenster; eine schon aktive Video-Pipeline allein reicht nicht. Abgewiesene Kandidaten werden höchstens einmal pro Sekunde neu geprüft. Der Dienst meldet eine feste laufende Codekennung `build=23`, unabhängig von der im Plugin angezeigten installierten Version.
- **Fokus/Eingaben:** Anzeigeanforderung, Aufbaufehler, tatsächliche Focus-ID und oberste Dialog-ID sowie aktuelle Dialogzugehörigkeit werden getrennt protokolliert. Ein Startstatus ist kein Fokusbeweis. Der native Eingabezähler startet pro neuem Navigator bei null. Abgewiesene native Aktionen werden vor dem Rücksprung als `ACTION_REJECTED` protokolliert; nach bereits geschlossenem Fenster gesendete Folgecallbacks heißen `ACTION_IGNORED_CLOSED`. Ungültige/abgelaufene Marker heißen `MARKER_INVALID/MARKER_EXPIRED`. Ein anderer Kodi-Dialog wird nicht gewaltsam verdrängt. Die globale Keymap bleibt opt-in.
- **EPG der normalen Senderliste:** Die sichtbaren bis zu 24 Sender werden als kurzer Auftrag dem langlebigen Dienst übergeben. Die GUI wartet auf keinen Download. Maximal ein Short-Guide-Worker mit drei parallelen Abrufen; aktuelle Jobs werden nicht doppelt gestartet. Erfolgreiche Daten werden 30 Minuten, fehlgeschlagene Abrufe nur 30 Sekunden zurückgestellt. Zustandstabellen sind begrenzt.
- **Jetzt/Danach aktualisieren:** Nach erfolgreichen Short-Guide-Abrufen wird ausschließlich dieselbe noch geöffnete XCMate-Senderseite aktualisiert. Andere Add-ons und FullscreenVideo werden nicht aktualisiert. Auch ein fertiger XMLTV-Refresh kann die aktuell passende Senderseite aktualisieren. Ein leerer Download löst keine Refresh-Endlosschleife aus.
- **Manuelle XMLTV-Aktualisierung:** Der Aufruf wird an den Dienst übergeben; die kurzlebige Plugin-Instanz startet keinen eigenen Download mehr. `REQUESTED` und tatsächliches `RUNNING/READY` sind getrennt. Ein laufender Dienst ist Voraussetzung für die Ausführung.
- **Persistente Diagnose:** `live_diagnostics.py` speichert pro Komponente höchstens 16 kleine Ereignisse in `xcmate_diagnostic_*.json` im privaten Add-on-Profil. Neueste Window-Properties werden beim Stop/Shutdown und EPG-Abschluss auf Disk gesichert. Die Diagnose ist ohne Wiedergabe lesbar und kann einen Kodi-Neustart überstehen, sofern das private Profil beschreibbar ist. Es werden nur feste Statuscodes, Zeitstempel, Zahlen und boolesche Werte gespeichert; keine Provider-URL, Zugangsdaten, Kanalnamen oder Runtime-Sessionkennung.
- **EPG-Status:** Gespeichert werden Anforderung/Laufstatus, letzte erfolgreiche Importzeit, Sender-/Sendungszahlen, Eingangsbytes der Quelle, Limit-/Format-/Downloadfehler sowie Jetzt-/Danach-Treffer der sichtbaren Seite. Einstieg weiterhin `TV-Fernbedienung: Diagnose`, zusätzlich Sender-Kontextmenü `EPG-/Live-Diagnose`. Dies ist die Issue-12-Diagnose, noch nicht die vollständige Quellen-/Titelvorschau aus Issue #13.
- **Grenzen bleiben erhalten:** Große DE-MASTER-Dateien können weiterhin am 80-MiB-Limit scheitern. Byte-, Programm- und Senderlimits werden als unterschiedliche Codes protokolliert; die Limits wurden nicht erhöht. Ein bloß gestarteter Download gilt weiterhin nicht als erfolgreicher Import.

### Testergebnisse und Paket

- **202 lokale unittest-Tests bestanden, keine Fehler und keine übersprungenen Tests.** Gesamtsuite auch nach dem vollständigen Repository-Build in der separaten Buildkopie erfolgreich.
- **18 neue Issue-12-Tests**: URI-Gleichwertigkeit und Gegenbeispiele, passende/veraltete/fremde Itemkennungen, deaktivierte/mehrdeutige Portale, Sessionableitung im tatsächlichen Wiedergabepfad, ListItem-Weitergabe an setResolvedUrl, persistente Diagnose einschließlich Neustart, Worker-Auftragskette und selektiver Seitenrefresh.
- **Vier zusätzliche Kodi-Dienst-/Dialogregressionen**: keine Anzeige vor Fullscreen-Aktivierung; begrenzte Übernahme der vorherigen Identität während eines Redirect-Senderwechsels; empfangene, aber abgewiesene native Aktionen; unterscheidbare ungültige/abgelaufene Session-Marker.
- Der Senderlisten-Integrationstest führt die tatsächliche `_live_channels`-Funktion aus: erste Darstellung ohne EPG → Dienstauftrag → erfolgreicher Short-Guide → Container.Refresh → erneute Darstellung mit echten synthetischen Jetzt-/Danach-Titeln und Trefferzählung.
- **15 bestehende HTTP-/Cache-/XMLTV-Grenztests zusätzlich mit installiertem httpx ausgeführt**, einschließlich tatsächlicher lokaler HTTP-Requests über beide HTTP-Backends.
- Python-Kompilierung, ZIP-Integrität und Verzeichnislayout, Manifestversion sowie byteweiser Abgleich jedes Paketbestandteils mit dem Kandidatenquellcode erfolgreich.
- Keine echten Android-Tests dieser Änderungen; kein GitHub-CI-Ergebnis für diesen neuen Branch behaupten. Noodle Private, andere Add-ons, Produktionsindex und Veröffentlichungsworkflow sind gegenüber main unverändert.
- Paket: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.23.zip`, **239771 Bytes**.
- SHA-256: `d3242e3d8a08b5690b7b5a8c8d01b40747d9e4f9f2086b64d174332dbbf61905`; daneben als `.zip.sha256` hinterlegt.
- Automatische PR-/Issue-Kommentar-Erstellung ist derzeit durch den bestätigten Proxy-CONNECT-403 für `api.github.com` blockiert. Die öffentliche Issue-Seite wurde gelesen; Git-Zugriff funktioniert. Branch und Übergabe können deshalb bereitgestellt werden, ohne einen erstellten PR oder geschlossenen Issue vorzutäuschen.

### Nächster kontrollierter Android-Test mit 0.1.23

1. Das Kandidaten-ZIP als XCMate-Update installieren, nicht deinstallieren und keine Profile löschen. Kodi vollständig neu starten. Installierte Version 0.1.23 kontrollieren; globale Fallback-Keymap für diesen Test ausgeschaltet lassen.
2. Normale Senderliste öffnen und kurz auf den begrenzten Short-Guide warten. Erscheinen Jetzt/Danach? Bei Bedarf `EPG-/Live-Diagnose` im Sender-Kontextmenü öffnen: `epg_list` liefert die sichtbare Trefferquote; `epg/epg_source` unterscheiden Anforderung, Importerfolg und Quellengrenzen.
3. Einen bekannten Xtream-Live-Sender starten. Nach Erreichen des Vollbilds Links, Hoch/Runter, OK und Menü prüfen. Erscheint die XCMate-Sidebar? Ist der Fokus sichtbar? Bleibt nur Kodi-OSD erreichbar?
4. Wiedergabe stoppen, **ohne Kodi-Neustart** `TV-Fernbedienung: Diagnose` öffnen. Den neuen gespeicherten Abschnitt vollständig erfassen. Besonders wichtig: `service build=23`, `session`, `ownership`, `dialog`, `focus` und `input` samt Zeitpunkten/Verlauf.
5. Interpretation: `URL_NOT_VERIFIED` = keine bestätigte Zuordnung; `ITEM_IDENTITY` oder `URL_IDENTITY` = Zuordnung gelungen; `WAIT_FULLSCREEN` = GUI noch nicht bereit; `SHOW_REQUESTED` allein beweist keine Aktivierung; `ACTIVE_DIALOG/OTHER_DIALOG` und Focus-ID grenzen die Oberfläche ein; `WAITING_FOR_ACTION/count=0` zeigt fehlende Eingaben im aktuellen Navigator. Die alten 18 XML-Popup-Ereignisse sind davon getrennt.
6. Danach ein Video aus einem anderen Add-on starten und dessen normale Bedienung prüfen. Bei erneutem Kodi-Neustart muss die vorherige Live-/EPG-Diagnose weiterhin über ihren Zeitstempel erkennbar sein; der neue Dienststart darf seinen eigenen Status erneuern.
7. Für XMLTV gesondert eine kleine bestehende Quelle manuell aktualisieren und tatsächliches READY, Importzeit, Zahlen und Sender-Matching prüfen. Ein XMLTV-Limitfehler darf nicht als erfolgreiche EPG-Abnahme zählen.

Offen bleiben die tatsächliche Kodi-Metadatenübernahme auf Android, Redirect-Verhalten des Providers, native Langdruck-Action-IDs, sichtbare Dialog-/Fokusdarstellung mit BINGIE MOD, EPG-Abdeckung und der getrennte VOD-Rückkehrfehler. **Kein P0-/P1-Geräte-PASS ohne diesen Test.** Die vollständige EPG-Status-/Titelvorschau (#13) und XCMate Skin (#14) bleiben eigene geplante Aufgaben.

## Zuerst lesen – maßgebliche Unterlagen

1. [Zentrale Übersicht](README.md).
2. [Codex-Fehlerbericht, Ressourcenlimits, alle Geräte-Abnahmeschritte für 0.1.22](KODI21_FIX_022_DE.md) – stammt aus der Testkandidatenphase; deshalb ist die Aussage »nicht veröffentlicht« dort **historisch**, nicht aktueller Release-Status.
3. [Technischer Projektkontext](PROJECT_HANDOFF_DE.md) – enthält auch ältere Versionsangaben.
4. [Roadmap, offene Fehler und QA](ROADMAP_AND_QA_DE.md).
5. [Vorheriger 0.1.21-Zwischenstand](TV_REMOTE_EPG_RECOVERY_021_DE.md).

## Was Codex tatsächlich geändert hat (0.1.22)

- `live_overlay.py`: korrekter programmatischer Kodi-21-/Omega-`WindowDialog`-Lebenszyklus, Control-Konstruktion vor `show()`, `onControl` statt bisherigem unpassenden `onClick`, sichtbarer Fokus mit mitgelieferten Texturen und deduplizierte Tastenevents.
- `service.py`: stärkere Überprüfung der XCMate-eigenen Live-TV-Sitzung und Bereinigung bei fremder Wiedergabe.
- `utils.py`, `network_io.py`: Cache-Writable-Probe und Fallback; HTTP-Daten und Dekomprimierung begrenzt.
- `epg.py`, `epg_io.py`, `epg_sources.py`, `main.py`: ungültige XMLTV-Programme einzeln auslassen; bounded streaming; EPG-Refresh asynchron.
- Neue Tests: `tests/test_xcmate_kodi21_overlay.py`, `tests/test_xcmate_epg_limits.py` und Änderungen an Regressionstests.
- Noodle Private und fremde Add-ons wurden nicht verändert.

**Geprüft:** Pull-Request-GitHub-CI vom 18.10.2026: **180 Python-Tests erfolgreich**; Python-Syntax, Build und ZIP-Prüfungen erfolgreich. Der Release-Push-Workflow war erfolgreich. Das ist kein Ersatz für Gerätetests.

## Wichtige Einschränkung

Die neue XMLTV-Obergrenze beträgt **80 MiB entpackte XMLTV-Daten pro Quelle**, 150.000 Sendungen insgesamt und weitere dokumentierte Limits. Ein zuvor analysierter DE-MASTER-XMLTV-Datensatz war ca. 100 MiB unkomprimiert und kann dadurch bei dieser Version abgewiesen werden. Das ist ein **offenes Kompatibilitäts-/Abnahmethema**, nicht als funktionierendes EPG bewerten. Prüfe gegebenenfalls kleinere DE/AT/CH-Quellen und diskutiere später Streaming-Senderfilterung, ohne das Speicherlimit unkontrolliert zu erhöhen.

## BESTÄTIGTER Realgeräte-Test: XCMate 0.1.22 – Live-TV-Navigation schlägt fehl (18.10.2026)

**Versionsnummer 0.1.22 vom Nutzer bestätigt.** Die nachfolgenden Beobachtungen beziehen sich auf echtes Live-TV, nicht auf den separaten XML-Popup-Diagnosetest.

- **Positiv:** XCMate startet, reguläre Senderliste lässt sich öffnen, ein Xtream-Sender lässt sich starten und abspielen. Kurzes OK öffnet zügig und zuverlässig das **Kodi-Standard-Videoplayer-Menü**.
- **P0 offen:** Eigenes XCMate-Live-TV-Overlay / XCMate-OSD ist nicht erreichbar. Links öffnet keine XCMate-Senderliste; Hoch/Runter schaltet keine Sender; langes OK bzw. der gewünschte zusätzliche Bedienbereich mit Video-/Audio-/Untertitel- und Systemeinstellungen ist nicht erreichbar. **P0 nicht als behoben abschließen.**
- **P1 offen:** Reguläre XCMate-Senderliste zeigt **keine EPG-Jetzt/Danach-Angaben**. Ein zuvor gemeldeter Hintergrunddownload wurde nur gestartet, seine erfolgreiche Verarbeitung und Xtream-Senderzuordnung nicht bestätigt.
- Technischer Hypothesenpfad im Code: `main._play_live` meldet Xtream-LiveSession nur bei vorhandenem pid/sid; `service` startet Dialog nur für bestätigte Sessions, `LiveNavigator.owns_playback` gleicht laufende URL mit konfiguriertem Portal ab. **Ob eine bestimmte Prüfung fehlschlägt, muss mit Geräte-Diagnose und Kodi-Log geklärt werden**, nicht unbelegt behaupten.
- Mögliche weitere Ursache EPG: 80-MiB-Grenze für XMLTV verhindert großes deutsches DE-MASTER; andere Ursachen sind EPG-Downloadfehler, leerer Cache, unpassende Channel-IDs oder Zeitfenster.

**Nachverfolgung:** [GitHub-Issue #12 – Realgerät: XCMate-Fernbedienung greift nicht, Senderliste ohne EPG](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12). Codex soll auf einem neuen Fix-Branch arbeiten und mit Geräte-Logs testen; keine ungetestete direkte Veröffentlichung auf `main`.

**Nächster konkreter Geräteschritt:** Live-TV-Sender starten, dann ohne Kodi-Neustart Wiedergabe beenden und sofort `XCMate → TV-Fernbedienung: Diagnose` öffnen. Die Felder für letzte Live-Beobachtung, Sitzungswiederherstellung, Auto-TV-Popup, TV-Einblendung, Eingabepfad, native Tastenereignisse und letzte Fehler vollständig fotografieren. Bei weiterem Black Screen ggf. `kodi.log`/`kodi.old.log` anonymisieren und auswerten. Die getrennten VOD-Abbruchprobleme bleiben offen.

## Android-TV-Diagnose mit drei Fotos – 18.10.2026

**Installierte Add-on-Version bei diesen Screenshots weiterhin nicht verifiziert** (ggf. 0.1.21, nicht als erfolgreiche 0.1.22-Geräteabnahme interpretieren).

**Hintergrunddienst (Foto 1):**
- Dienststatus **LÄUFT**, letzte Lebenszeichen-Aktualisierung **0,1 Sekunden**.
- **533** Dienstschleifen, Dienstphase „läuft“, letzter Dienstfehler „keine gemeldet“.
- Letzte Live-Beobachtung „noch nicht geprüft“; Sitzungswiederherstellung „noch keine Prüfung“; TV-Einblendung „noch nicht gestartet“; Diensteingabe noch nicht verarbeitet.
- Autostart-Diagnosemodus **PAUSIERT**.

**Separater XML-Popup-Test (Fotos 1–2):**
- Darstellungsweg `WindowXMLDialog – Default/720p`.
- Popup-Status `XML: PER ZURÜCK GESCHLOSSEN`.
- **18** registrierte Popup-Eingabeereignisse.
- Letzte Taste `Zurück (Navigation)`, Kodi-Aktions-ID **92**.
- Zuletzt gespeicherter Fokusstatus **„Testfeld“**.
- Der Code `popup_probe.py` setzt bei Richtungstasten den internen `focus_index` abwechselnd auf Testfeld/Schließen. Der Diagnoseeintrag ist **kein Beweis für einen sichtbaren Fokuswechsel auf dem Display**. Nutzer konnte eine tatsächliche sichtbare Fokusbewegung nicht sicher erkennen.

**Reales Live-TV-Overlay (Fotos 2–3):**
- Auto-TV-Popup / TV-Einblendung **nicht gestartet**; XCMate-Stream erkannt **NEIN**; Video läuft **NEIN**.
- Globale Kodi-Tastenbelegung **INAKTIV**; Tastenübernahme nicht überprüft; Eingabepfad nicht aktiv; **0 native TV-Overlay-Tastenereignisse**.
- Diese Werte sind konsistent mit einem Popup-Test **ohne** Live-TV und **kein** fehlgeschlagener Live-TV-Fernbedienungstest. XML-Popup (`WindowXMLDialog`) und echtes Player-Overlay (`WindowDialog`) sind getrennte UIs.

**Bewertung:** GUI des unabhängigen XML-Testdialogs erfolgreich, Dienst aktiv; **noch kein Nachweis** für sichtbaren Fokus und Fernbedienung im tatsächlichen XCMate-Live-TV-Overlay. Zuletzt gemeldeter schwarzer Bildschirm nach VOD-Wiedergabe bleibt ein separater offener Fehler.

**Nächster kontrollierter Test:** Zuerst Version in Kodi-Add-on-Info feststellen. Falls `0.1.21`, normal über GS Media Repository auf `0.1.22` aktualisieren und Kodi neu starten. Ohne Aktivierung der globalen Keymap einen XCMate-Live-Sender manuell starten; Foto/Video des tatsächlichen Overlays mit Fokus und Verhalten bei Links/Hoch/Runter/OK/Zurück, danach sicher stoppen. Bei Fehlern anonymisiertes `kodi.log` und ggf. `kodi.old.log` sichern. Nicht aus dem bloßen Popup-Test auf funktionierende Live-TV-Steuerung schließen.

## Android-TV-Rückmeldung vom 18.10.2026 (Versionsstand noch NICHT bestätigt)

**Achtung: Der Nutzer vermutet, dass beim Test noch XCMate 0.1.21 installiert war.** Die untenstehenden Beobachtungen dürfen daher nicht als Erfolg oder Misserfolg der 0.1.22-Korrekturen gewertet werden, solange die auf dem Fernseher angezeigte Versionsnummer nicht geprüft ist.

- XCMate-Hauptmenü war wieder aufrufbar.
- In `Konfigurieren` öffnete sich die EPG-Verwaltung, und eine Meldung bestätigte den **Start** eines Hintergrunddownloads. Ob XMLTV-Dateien vollständig geladen und korrekt zugeordnet wurden, ist noch unbestätigt.
- `Neueste Filme` zeigte eine Liste; ein Film ließ sich starten und abspielen.
- Bei der Rückkehr bzw. beim Versuch, die VOD-Filmwiedergabe zu stoppen, erschien ein schwarzer Bildschirm und der Nutzer konnte nicht normal zurück navigieren. Ursache ungeklärt; **VOD/Player-Rückkehr als separaten offenen Fehler führen**, nicht vorschnell auf das Live-TV-Overlay zurückführen.
- Der separat gestartete XCMate-Popup-Diagnosetest zeigte ein Fenster. Tasteneingaben wurden durch wechselnde Kodi-Keycodes und akustisch wahrgenommen; **eine sichtbare Fokus-/Cursorbewegung war nicht eindeutig feststellbar**.
- Noch kein Diagnose-Screenshot bzw. Gerätelog zur Auswertung übermittelt. Ein Kodi-Neustart war wegen des schwarzen Bildschirms in Betracht gezogen worden.

**Diagnosedaten:** `popup_probe.py` schreibt Popup-Status, letzte Taste, Anzahl und Fokus in `xbmcgui.Window(10000)`-Properties. Diese **können beim vollständigen Kodi-Neustart verschwinden**. Bilder vor dem Neustart bevorzugen. Kodi-Protokoll und ggf. `kodi.old.log` nach dem Neustart prüfen; Logs vor einer Weitergabe von Zugangsdaten bereinigen.

**Nächster Test:** Zunächst Versionsnummer auf Android-TV kontrollieren. Falls noch 0.1.21, über das GS-Media-Kodi-Repository auf 0.1.22 aktualisieren, Kodi neu starten und Start/EPG/Popup/Fokus/VOD-Abbruch getrennt testen. Erst danach Folgereparatur auf einem Codex-Branch planen.

## Verbindliche Aufgaben für den Android-TV-Abnahmetest

1. Kodi aus dem GS-Media-Repository regulär auf XCMate `0.1.22` aktualisieren, Add-on- und Profildaten beibehalten und Kodi vollständig neu starten.
2. BINGIE MOD, Filmwiedergabe aus einem anderen Add-on, XCMate-Hauptmenü und XCMate-Konfiguration getrennt prüfen. Keine Endlos-Spinner.
3. XCMate-Live-Sender starten; sichtbare Senderliste, Fokus und Links/Rechts/Hoch/Runter/OK/Zurück/Menü prüfen; keine doppelten OK-Events.
4. Live-TV beenden und ein Video aus einem anderen Add-on öffnen; Tasten müssen normal reagieren, kein XCMate-Popup darf verbleiben.
5. EPG-Manager öffnen, kleine DE/AT/CH-Feeds einzeln laden und manuelle Senderzuordnungen nach Neustart wiederfinden. Große DE-Master-Datei wegen Limit gesondert bewerten.
6. Cache-Verzeichnis per Dateibrowser speichern und die Fallback-Funktion testen, ohne vorhandene Daten zu löschen.
7. Bei Problemen: `kodi.log` auf dem Android-TV auswerten, nur anonymisierte Fehlerstellen teilen, niemals Xtream-Credentials oder private Token ins Repository/Chat kopieren.

## Zusammenarbeit ChatGPT ↔ Codex – so bleibt alles nachvollziehbar

- **Codex arbeitet für künftige Korrekturen auf einem separaten Branch und erstellt einen Pull Request** mit Änderungszusammenfassung, Tests, tatsächlicher Version, Geräte-Risiken und Artefakten. Nicht unbemerkt `main` überschreiben.
- **Nach jedem Codex-Release** die aktuelle Version, Pull Request, Commit, GitHub-CI, öffentliches Paket, funktionale Änderungen, dokumentierte offene Gerätefehler und die nächste Aufgabe **in dieser Datei aktualisieren**. Den Überblick in `README.md` ebenfalls aktualisieren. Historische Berichte aufbewahren.
- **Für manuelle Statuskontrolle** GitHub-`main`, offene Pull Requests, CI-Runs, `addons.xml`, `addon.xml`, ZIP-Prüfsumme sowie diese Datei vergleichen. Erst danach von einer veröffentlichten Version sprechen.
- ChatGPT kann den fremden laufenden Codex-Chat **nicht direkt live mitlesen**. Sichtbar und überprüfbar sind hochgeladene Branches, PRs, Commits, Tests, Artefakte und Dokumentation. Nicht gepushte Arbeit und Android-TV-Funktionen können dadurch nicht bestätigt werden.
- **Kein ungeprüftes Weiterentwickeln parallel auf `main`**, solange Codex denselben Bereich bearbeitet. Laufende Android-Tests und echte Logs entscheiden die nächste Priorität.

## Neue verbindliche Produktausbaustufen (18.10.2026)

**Produktname für den separaten Kodi-Skin: `XCMate Skin`**. Nicht „GS Media Skin“. Das bestehende XCMate-Add-on behält seine ID `plugin.video.xtreammate`.

1. **Zuerst EPG unabhängig von einem Skin wirklich sichtbar machen – [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13).** Nutzer kann in 0.1.22 EPG-Downloads anstoßen, sieht aber weder den erfolgreichen Import noch Jetzt/Danach in der Senderliste. Zuerst Menüpunkt **EPG-Status & Vorschau** mit Quelle, Ergebnis, Importzeit, Sender-/Sendungszahlen, Matching-Quote, konkreter Fehlermeldung und echten Now-/Next-Titeln aus vorhandenem Cache; keine Hintergrunddownloads durch bloße Öffnung. `EPG jetzt` existiert bereits in XCMate (Route `epg_now`), liefert aber keine detaillierte Importdiagnose; tatsächliche Datenverfügbarkeit ungeklärt.
2. **Danach Machbarkeitsprototyp `XCMate Skin` – [Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).** Als separater Kodi-Skin, nicht als Überschreibung des laufenden BINGIE MOD. Ziel: Kodi-TV-Oberfläche mit Senderliste/EPG, sichtbar fokussierbarem Player-OSD, Links=Senderliste, Hoch/Runter=Senderwechsel, OK=Bedienleiste, Zusatzmenü für Video/Audio/Untertitel/Einstellungen. Existierenden Xtream-/EPG-Kern aus XCMate weiterbenutzen, Skin ist Darstellung/Steuerung; Kodi bleibt Videoplayer.
3. **Fokus und globale Tastenbelegung zuerst auf Android-TV nachweisen**; Skin-Wechsel muss sicher rückgängig zu machen sein. Keine Vermischung der EPG-Fehler mit dem ungeklärten Live-TV-Fernbedienungsfehler [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12). Vor vollständigem BINGIE-MOD-Fork ursprüngliche Lizenz und benötigte Abhängigkeiten prüfen.

**Status:** Diese beiden Erweiterungen sind geplant/dokumentiert, **nicht** als implementiert oder auf Android verifiziert melden. Priorität: EPG-Datensichtbarkeit vor neuer Skin-Oberfläche. Der bestehende Code darf nicht gleichzeitig ohne abgestimmten Branch in `main` weiterentwickelt werden.

## Geplante Prioritäten

- **P0:** Keine Kodi-weiten Hänger oder Eingriffe in BINGIE MOD, korrekter Add-on-Start.
- **P1:** Fernbedienung und sichtbarer Fokus/Popup im Kodi-Live-TV.
- **P2:** EPG-Quellen/EPG-ID-Matching und manuelle Zuordnung, speziell Sky und RTLup.
- **P3:** Cache-Sicherheit, Profilpersistenz, ressourcenschonende große XMLTV-Feeds.
- **P4:** Freigegebenes grafisches Design, Farben und Komfortfunktionen.

**Aktueller nächster Schritt:** PR zum geprüften Kandidaten 0.1.24 prüfen; regulärer Repository-Updateweg erst nach ausdrücklicher Merge-Freigabe. Android-Testplan in [KODI21_FIX_024_DE.md](KODI21_FIX_024_DE.md). #12 und #13 bleiben offen.
