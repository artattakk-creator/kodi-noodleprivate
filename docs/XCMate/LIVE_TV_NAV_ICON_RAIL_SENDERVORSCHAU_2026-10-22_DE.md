# XCMate – Live-TV: fünf Links-Ebenen + senderbezogene Rechts-Programmvorschau

**Verbindlicher Nutzerwunsch 22.10.2026.** Entwicklungsbasis: `main` mit Version **0.1.29.13**. Status: **SPEZIFIZIERT, NICHT IMPLEMENTIERT**. Details/Akzeptanzkriterien: [Issue #94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94) und [Issue #95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95).

## A. Gewünschte Live-TV-Links-Stufen (Overlay über weiterlaufendem Stream)

```text
LIVE_FULL
  LINKS → CHANNELS        bisherige Senderliste mit Jetzt-EPG
  LINKS → GROUPS          bisherige Sendergruppenliste
  LINKS → NAV_ICONS       NEU: schmale vertikale reine Icon-Leiste
  LINKS → NAV_EXPANDED    NEU: Icon-Leiste ausgeklappt mit Beschriftungen
  LINKS → LIVE_FULL       alle XCMate-Menüs zu, laufender TV-Stream sichtbar
```

Von beiden Iconzuständen per Hoch/Runter navigierbare native Kodi-Fokuselemente, Auswahl per OK, lesbare Focusfarben, D-Pad- und IR-Dedupe, vertikale Position merken.

**Icon-Reihenfolge (unverändert übernehmen):**
1. 🔍 Suchen → XCMate-Suchfunktion
2. ♡ Favoriten → XCMate-Favoriten
3. 📺 Live-TV → eigene Live-Senderliste/aktueller aktiver Gruppenkontext
4. 🎬 Filme → XCMate-Filmbrowser
5. 📺 Serien → XCMate-Serienbrowser
6. ⚙️ Einstellungen → XCMate-Einstellungen
7. ↩️ Verlassen → **XCMate-Hauptmenü**, NICHT nur TV-Vollbild/Kodi-Homescreen

**Wichtige Unterscheidung:** Fünftes Links schließt **nur alle Menüs** und lässt laufendes Live-TV sichtbar; die **explizite Menüoption „Verlassen“** wechselt zu XCMate-Hauptübersicht. Übergang Video/Window/Plugin so auflösen, dass keine versteckte Hintergrund-Audiowiedergabe und kein Kodi-Prozessabsturz entstehen. Der genaue Player-Stop/Handoff wird Kodi-sicher implementiert, nicht als direkter GUI-Callback-PlayMedia/Container.Update-Mix. Rechts oder Back sollen kontrolliert zu vorherigem Zustand zurückkehren; das eindeutige fünfmalige Links-Verhalten hat Vorrang.

**Design:** Schmale halbtransparente Rail im Standardgrau mit bestehenden/kompatiblen eigenen XCMate-Piktogrammen, im zweiten Zustand expandierend Labels; Safe Area, 720p/1080p/Android-IR/BINGIE MOD und Estuary. Keine Änderungen anderer Kodi-Keymaps; Space Premium nur kompatibel/optional.

## B. Rechts im Mini-EPG → Sendungen des tatsächlich markierten Senders

```text
LIVE_FULL → LINKS → CHANNELS [Sender A markiert, Video B läuft]
                         RECHTS → CHANNEL_PROGRAMMES[A]
                                     Jetzt, Danach, weitere Sendungen
                                     HOCH/RUNTER → Programme
                                     OK → Programmdetails
                                     LINKS/BACK → CHANNELS [Sender A weiter markiert]
```

**Nicht** ohne OK auf Sender A umschalten. Die Programmdaten stammen aus aktivem Portal, gespeichertem Xtream-Kurz-EPG/externem XMLTV-Cache und verbindlicher manueller EPG-ID-Zuordnung. Nur echte, noch relevante Sendungen mit Datum, Beginn, Ende, Titel, optional Langtext und EPG-Quellenstatus anzeigen. Der Menüpfad soll auch bei fehlenden/ungenügenden Daten funktionieren: „Keine weiteren Programmdaten verfügbar“, keine Erfindung von 7–10 Tagen.

**Code-Hinweis:** `live_overlay.py::_handle_command` besitzt aktuell `channels→right→hidden` und `guide→right→hidden`; `_epg()` setzt `self._guide_sid=self.sid` auf den **laufenden** statt **markierten** Sender. Bereits vorhandene `guide`-Modus-Funktionen/Events gezielt wiederverwenden, aber korrekt an den fokussierten Kanal binden und `_guide_return` / Zurück stufenweise steuern. Vollbild-Rechts („vorheriger Sender“) und Player-Control-Rechts bleiben unverändert. Kein Netzwerkladen im Kodi-Key-Callback und kein unkontrolliertes SQL im GUI-Thread.

## C. Konsistenz/Abnahme

- Bestehendes OK→Infoleiste→Playersteuerung, Hoch/Runter-Zapping nur im TV-Vollbild, Links→Mini-EPG→Gruppen, Native-/Bridge-Keymap und Gruppenfilterungen dürfen nicht regressieren.
- **P0-Blocker [#89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89)** beim großen EPG→„Jetzt Sender ansehen“ weiter getrennt verfolgen; niemals im selben Browser-/Tasten-Test dieses Menü verwenden.
- [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17) alte Live-TV-Steuerung, [#64](https://github.com/artattakk-creator/kodi-noodleprivate/issues/64) Fernbedienungskontexte, [#21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21) EPG-Langzeit, [#93](https://github.com/artattakk-creator/kodi-noodleprivate/issues/93) EPG-Reichweite als Abhängigkeiten beachten.
- Testcases: 20× fünf Links-Transitions über echten laufenden Stream; native IR-Fokus/Back/Rechts in jeder Stufe; alle sieben Menü-OK-Routen; zwei unterschiedliche markierte Sender A/B vs laufendes Video C; 100+ Sender Pagination; Fehlende EPG-Daten; kein Senderwechsel durch Rechts; keinerlei Kodi-Ausfall/Freeze/OSD-Hijacking.
- Änderungen als überprüfbarer Featurebranch/Draft-PR auf Basis `main`, mit Unit-/Integrationstests und separatem Android-Test-ZIP; **kein Merge oder OTA-Release ohne ausdrückliche Nutzerfreigabe**. Hauptrepo, Portale, Senderlisten, EPG-Mappings, Favoriten, Resume und bestehenden Video-Player-Datenbestand erhalten.
