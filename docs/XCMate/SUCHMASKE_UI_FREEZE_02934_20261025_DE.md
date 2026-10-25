# XCMate 0.1.29.34 – VERBINDLICHER UI-FREEZE der globalen Suche

**Datum:** 25.10.2026  
**Basis:** Android-Test von `plugin.video.xtreammate` **0.1.29.34** auf Kodi 21.2, Android TV 13, RK3528 ARM32, Titan BINGIE MOD.  
**Nutzerentscheidung:** **„Die Suche ist übrigens sehr gut gestaltet jetzt, dass man immer Live-TV, Filme und Serien da drin hat. Also diese Suchmaske finde ich super. Da darf nichts mehr dran geändert werden.“**

## 1. Verbindlicher Bestandsschutz / unveränderliche UI-Baseline

Die **vorhandene Suchmaske, ihr Layout, ihre Struktur und ihr Fernbedienungsverhalten sind eingefroren**, bis der Nutzer ausdrücklich eine konkrete Änderung freigibt:

- **Drei jederzeit sichtbare Suchbereiche/Tabs: Live-TV, Filme, Serien**. Struktur, Reihenfolge, Titel, Tab-Navigation, Fokusdarstellung, sichtbare Ergebnis-Typisierung, Abstände und vorhandene Skin-Gestaltung **nicht umbauen**.
- Bereits funktionierendes Such-Ergebnislayout mit **Senderlogos** sowie **sichtbaren Film- und Serienpostern/Covern**, Metadaten- und Fokusdarstellung **beibehalten**.
- IR-Fernbedienung: Hoch/Runter/OK/Zurück, Tabs/Fokus, Medienauswahl, Detail-/Staffel-/Episodennavigation und **Zurück zur identischen Suchmaske mit Suchkontext** schützen.
- Der aus **PR #158** reparierte Guide→Search-Handoff, der Guide→Senderstart und **Zurück aus der Suche zum Guide** bleiben erhalten.
- **Kein neuer Skin, keine Poster-Galerie, kein neuer Tab, keine Änderung des Layouts oder der Bildschirmhierarchie** unter dem Vorwand eines Performancefixes. Weder Neugestaltung noch Änderung der visuellen Komponenten ohne gesonderte Nutzerfreigabe.
- Bestehendes **Original-XCMate-App-Icon**, optionales Space Premium, alle Portale/Favoriten/EPG-Mappings/Resume/Autoplay/Daten unangetastet.

### Was innerhalb des Freeze ausdrücklich erlaubt und nötig ist

**Technische Optimierungen hinter der unveränderten Oberfläche**, insbesondere Datenbank-Indizes, lokale Sendernamen-Treffer, begrenzte Background-Worker, inkrementelles Nachladen von EPG-Informationen in bereits vorhandene Ergebnisfelder und Abbruch veralteter Suchen **ohne Layout-/Navigations-/Fokuswechsel**. Vorher/Nachher das gleiche UX-Verhalten und optische Suchmasken-Skelett verifizieren. Fehlende echte EPG-Infos dürfen nicht erfunden werden.

## 2. Android .34 – aktuelle positive und negative Befunde

### G4 Film-/Seriensuche: vom Nutzer getestete Teilfunktionen PASS

- **Film- und Seriensuche reagiert relativ schnell** im Vergleich zu Live-TV; keine genaue Stoppuhrmessung.
- **Film-/Seriencover werden sichtbar angezeigt.**
- Filme und Serien lassen sich in ihren **Detailbereich** öffnen.
- **Serien-Staffeln und Episoden** sind erreichbar.
- **Zurück führt wieder in die Suche**, nicht in ein leeres Fenster oder ungefragt auf Home.
- **Die dreigeteilte Suchmaske Live-TV | Filme | Serien wird ausdrücklich positiv bewertet und eingefroren.**
- **Autoplay/Wiedergabefortsetzung wurde in diesem .34-Test NICHT beobachtet** und bleibt für G4 als separater Unterpunkt **NOT_TESTED**; aus früheren PASS-Werten folgt kein neuer .34-Autoplay-PASS.

### G2/G3 Live-TV/EPG-Suche: Matching funktioniert, Geschwindigkeit FAIL

- **G2 Sendernamen-Suche aus großem EPG:** echter Sender mit Icon gefunden; direkter Senderstart zügig; Zurück führt zum großen EPG. **Suchergebnislatenz laut Nutzer gefühlt fast 60 Sekunden** – **PERF-01 FAIL**; keine technische Zeitmessung.
- **G3 Suche nach aktuell laufendem Programmtitel:** echter Titel gefunden, aber **gefühlte fast 120 Sekunden Wartezeit** – **PERF-02 FAIL**. Treffer-OK und Back dieses konkreten Programmtitels noch nicht separat dokumentiert; G3-Gesamtgate daher nicht automatisch PASS.
- Fehlende „Jetzt“-Angabe bei einem früheren Sendernamens-Treffer konnte nicht validiert werden; nicht als mangelhaften Matcher oder kompletten SEARCHUI-01-PASS umdeuten.
- **G1 aus großem EPG gestarteter Sender funktioniert** im bestätigten Einzelversuch; vollständiger Mehrfach-/Reopen-Test noch nicht protokolliert.
- Zusätzlich [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88) Startgruppe im großen EPG und [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17) Mini-EPG-Fokus auf aktuellem Sender noch offen, **außerhalb des Suchmasken-UI-Freeze** als separate Navigationskorrekturen.

## 3. Verbindlicher Codex-Entwicklungsvertrag

**Priorität: Live-TV-/Programmtitel-Suche beschleunigen, das Suchfenster äußerlich exakt erhalten.**

1. Für `search_data.LiveSearch` und `media_search` die aktuelle tatsächliche **End-to-End-Zeit** instrumentieren: `QUERY_ACCEPTED`, `FIRST_NAME_RESULT`, `FIRST_PROGRAMME_RESULT`, `UI_FIRST_RENDER`, `EPG_FINAL`, `UI_IDLE`; fix kodierte datensparsame Phasen und monotone Zeiten, keine vertraulichen Suchtexte/Provider-URLs/IDs.
2. Ohne die bestehende 3-Tab-Ansicht umzubauen, Sendernamen möglichst sofort **aus dem bereits lokalen Katalog-/Suchindex** liefern und anzeigen; Programmtiteltreffer effizient über vorhandene zeitlich gültige lokale EPG-/NowNext-Daten suchen. Spätere EPG-Anreicherung **innerhalb der bestehenden Labels** erlauben, mit sauberer Session-/Generation-Gültigkeit und stabilem IR-Fokus; alte Suchen abbrechen. `EPG_PARTIAL` ist kein belegter Endstatus.
3. Prüfen, ob maximal 64 Sender je `LiveSearch.step()`, massenweise `cached_short_guide`-Lookups, erneutes VOD-/Serien-SQL pro Slice oder GUI-Thread-Rückgaben Latenz verursachen; **nur messen, nicht aus dem Code allein Root Cause behaupten**.
4. Performance-Abnahme für Start mit leerem/warmem Cache, Portal mit Tausenden Sendern, vorhandene bzw. fehlende EPG-Daten, Treffer spät in Katalogreihenfolge. Erste Ergebnisse in **wenigen Sekunden statt 60–120 Sekunden** anstreben; keine ungestoppten Zeiten als exakte Messdaten ausgeben.
5. **UI-Freeze als hartes Regression-Gate:** Screenshot-/Kodi-Fokus-/Control- und Navigation-Snapshots nur als Vergleiche soweit real verfügbar; bei fehlenden Referenzen keine erfundene Pixelidentität behaupten. Dieselben drei Tabs, derselbe Aufbau und Fokus, derselbe Cover-/Logo-Platz, Filme/Serien weiterhin schnell, Details/Staffeln/Episoden/Back wie jetzt. Unveränderte Programmtreffersemantik, keine Dubletten, kein Ghost-Resultat und kein versehentlicher Playerstart.
6. Separater kleiner **kumulativer Draft-PR** von dann aktuellem `main` (bei Stand dieser Dokumentation **.34**) mit Host-Tests, Test-ZIP/SHA256 und kurzer Android-Abnahme; **kein autonomer Merge, kein Release**, keine Profil-/EPG-/Cover-Löschung und kein Downgrade.

**Abnahme:** Suchmasken-UI & Film-/Serien-Navigation **nicht neu gestalten**; Live-Suche performant machen; danach nur erforderliche gruppen-/EPG-bezogene separate Fehler beheben. Offene Issues [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140), [#127](https://github.com/artattakk-creator/kodi-noodleprivate/issues/127) und [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143) nicht ohne reale Tests schließen.
