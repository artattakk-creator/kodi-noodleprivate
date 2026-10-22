# XCMate 0.1.29.16 – gebündelte Android-Abnahme

**Datum:** 22.10.2026. **Gerät:** Android TV 13 / RK3528 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD; normale IR-Fernbedienung. **Installationsweg:** reguläres Update aus GS Media Repository. **Version:** 0.1.29.16, PR #96 bereits zuvor auf Nutzerfreigabe gemergt, GitHub-CI/602 Hosttests PASS; diese Hosttests ersetzen keine Android-Abnahme.

## Ergebnisse nach tatsächlich durchgeführter Nutzerprüfung

| Test | Gemeldetes Häkchen | Präzisierte fachliche Bewertung | GitHub |
|---|---|---|---|
| 1 – Live-TV-Baseline | FAIL | Startsender, Bild/Ton, Infoleiste mit EPG und Mini-EPG: **PASS**. Stop aus unterer Leiste: **FAIL**; kurz Kodi-Schwarzbild mit rotem Fortschrittsbalken/drei Punkten, dann automatischer Neustart desselben Startsenders samt Infoleiste. Zweimal Zurück verlässt Kodi. Ob nativer Absturz vs Kodi-/Android-Exit, ohne Log unklar. | #97 |
| 2 – Großes EPG öffnen | PASS | Fenster, Pfeilnavigation, Rückweg: **PASS**; Schrift der fokussierten Sendung verschwindet: **FAIL als Teilaspekt**. | #57, #92 |
| 3 – Senderdiagnose: Langzeit-EPG | PASS | Diagnosedialog öffnet und ist lesbar: **GUI PASS**. First/Last jeweils nur Gedankenstrich, Days leer: **senderbezogene Datenlage ungeklärt**, kein Nachweis einer erfolgreichen Langzeitzuordnung. | #93, #60 |
| 4 – Über 14 Uhr navigieren | PASS | Frühere Navigationsgrenze in getesteter Sequenz **nicht mehr reproduzierbar**. Wunsch: ←/→ springt von tatsächlich sichtbarem Sendungsblock zu Sendungsblock. | #93 |
| 5 – Fokusschrift/Kopfbuttons | FAIL | Fokusauswahl macht Sendungsbeschriftung unsichtbar; Kopfzeile über viele Sender hochzuscrollen ist unzumutbar. Nutzer wünscht z. B. **blaue Farbtaste**, andere Taste oder Doppeldruck als Shortcut zu Jetzt/Header. | #92 |
| 6 – Startgruppe und Logos | FAIL | Keine sichtbaren Logos, keine Trennung nach Sendergruppen. Einstieg soll direkt in konfigurierter Startsendergruppe erfolgen, Startsender sichtbar fokussieren; Links öffnet Gruppenwahl. | #88, #90 |
| 7 – Programmdetails | PASS, aber laut Nutzer „teilweise“ | OK→Details lässt sich öffnen und Basistext erscheint (**Teil-PASS**). Episoden-/Sendungsbilder fehlen, Dialogüberschrift „Plot“ statt sinnvollem Titel, Gestaltung unzureichend (**Rich-Details FAIL**). | #88 |
| 8 – Alter Programmführer: Dubletten | PASS | Bei diesem Nachtest **keine Doppelanzeige gemeldet**. Frühere echte SAT.1-HEVC-Doppelanzeige unter .13 bleibt historisch reproduziert; da .16 keinen Dedup-Fix enthielt, #58 weiterhin offen bis deterministischem Test. | #58 |
| 9 – Filme/Serien öffnen und zurück | PASS | Kataloge/Zurück funktionieren, ohne Wiedergabe. Issue #67 bleibt nach vorheriger 10/10-Abnahme geschlossen. | #67 |

**Nicht getestet:** Neuer EPG→OK→„Jetzt Sender ansehen“-Playback-Handoff (#89) in .16; wegen der bereits fehlerhaften regulären STOP-/Exit-Funktion (#97) absichtlich ausgelassen. Die Details aus #94 (zusätzliche linke vertikale Icon-Rail) und #95 (Rechts aus Mini-EPG zu zukünftigen Sendungen) wurden ebenfalls **nicht getestet und sind noch nicht implementiert**.

## Qualifizierte Gesamtbewertung

- **Android 0.1.29.16 = FUNKTIONALER TEIL-PASS, KEINE GESAMTABNAHME.** Kein neuer Merge oder Release freigegeben.
- **P0:** Normalen Live-TV-Stopp bzw. die Exit-Schleife #97 beheben. Sicheres Verlassen muss die **XCMate-Hauptübersicht** wieder anzeigen, ohne erneuten Startsender und ohne Kodi-Exit. Kodi-Exit-Ursache offen.
- **P0:** EPG-Playback-Handoff #89 bleibt NOT_TESTED; nach stabiler STOP-/Exit-Baseline behutsam auf Android testen.
- **P1:** Lesbarkeit/Shortcut #92; EPG-Startgruppe, Gruppenwahl, Logos, Rich-Details/Manuell-XMLTV #88/#60; senderbezogene Langzeitdiagnose mit klarem Leerstatus und Blocksprünge #93.
- **P1 dringend:** Künstliches 512-MiB-Artworkbudget sowie wartende SPACE_FULL-Queue #90; SQLite-/Queue-Stabilität #91 getrennt und **ohne deaktivierten Datenbankschutz** untersuchen.
- **P2 / spätere Integration:** #94 Icon-Rail (fünf Links-Stufen), #95 Zukunftssendungen des im Mini-EPG **markierten** Senders; #58 reproduzierbare Dedup-Mischfälle.

## Sicherheits- und Datengrenzen

- Kodi-Log, Android-logcat/Tombstone und Spiel-URLs können Provider-Zugangsdaten, API-Tokens oder private Hosts enthalten: **nicht ungefiltert in öffentliche GitHub-Issues/PRs hochladen**. Diagnosezahlen und Fehlerklassen anonymisieren.
- Keine Cache-/Profil-/Datenbanklöschung, kein Portalreset, kein Verschieben von Live-Keymaps außerhalb des XCMate-Kontexts; Rückfall-ZIP 0.1.29.11 und getestete Vorversion .13 erhalten.
- Quellweit importiertes XMLTV (EPGShare01, Kaimandura) belegt **keine senderbezogene Zuordnung**. Diagnose-Striche nicht ohne per-Sender-DB-Prüfung einem Importdefekt gleichsetzen.

## Quellen/Issues

- [#97 Live-TV-STOP/Exit](https://github.com/artattakk-creator/kodi-noodleprivate/issues/97)
- [#89 EPG-Player-Handoff](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89)
- [#93 Zeitnavigation/Senderdiagnose](https://github.com/artattakk-creator/kodi-noodleprivate/issues/93)
- [#92 Fokus/Shortcut](https://github.com/artattakk-creator/kodi-noodleprivate/issues/92)
- [#88 Startgruppe/Logos/Rich-Details](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88)
- [#58 Dubletten](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58)
- [#60 XMLTV-ID-Mapping](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60)
- [#90 Artworkbudget](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90)
- [#91 SQLite-/Queue-Engpässe](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91)
- [#94 Live-TV-Icon-Rail](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94)
- [#95 Zukunfts-EPG im Live-Overlay](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95)
- [#67 stabile Filme-/Serienfenster, bereits CLOSED](https://github.com/artattakk-creator/kodi-noodleprivate/issues/67)

**Folgeauftrag:** siehe CODEX_SAMMELAUFTRAG_NACH_02916_2026-10-22_DE.md. Nur Dokumentation, keine freigegebene Codeintegration.