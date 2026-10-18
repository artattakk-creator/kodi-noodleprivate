# CODEX-ARBEITSAUFTRAG – XCMate Live-TV-Infobar, EPG und Fernbedienung stabilisieren

**Verbindliche Nutzerfreigabe für die ANFORDERUNGEN:** 18.10.2026  
**Repository:** `artattakk-creator/kodi-noodleprivate`  
**Ausgangsbasis:** aktuell `main` mit **XCMate 0.1.24**, technische Kodi-ID `plugin.video.xtreammate` unverändert lassen.  
**Statusnachtrag 18.10.2026:** Anforderungen auf `fix/xcmate-infobar-epg-navigation` als **0.1.25-Testkandidat implementiert**; **237 lokale Tests bestanden**, CI/PR siehe [aktuellen Status](CODEX_STATUS_CURRENT_DE.md). **Nicht auf main veröffentlicht, nicht auf Android-TV abgenommen.** [Implementierungsbericht, Paket und vollständiger Geräteplan](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md). Der folgende Text bleibt die verbindliche Anforderung und historische Ausgangslage.
**Arbeitszweig:** neuen `fix/xcmate-infobar-epg-navigation` oder vergleichbaren Branch von aktuellem `main` verwenden und PR erstellen; nicht direkt nach `main` mergen.

## 0. Was Codex zuerst lesen muss

1. **Diese Arbeitsanweisung vollständig.**
2. [Verbindliche vollständige UX-/State-Machine-Spezifikation](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) – detaillierte Tastenbelegung und Progressbar-Logik.
3. [Android-TV-Gerätetest XCMate 0.1.24](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md) – jetzt sichtbare Senderliste und unteres OSD, aber leeres EPG, langsame/unsichere Bedienung.
4. [Aktueller Release-/Codex-Status](CODEX_STATUS_CURRENT_DE.md); [Designsystem](DESIGN_SYSTEM_DE.md).
5. GitHub-Issues [#17 – neue Bedienlogik](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#13 – EPG-Status, Import, Vorschau](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#12 – Fernbedienungsstabilität](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) und [#14 – späterer separater XCMate Skin](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).

**Vorgabe:** Den bereits erfolgreichen TV-`WindowDialog`-Start aus 0.1.24 erhalten; nicht wieder Kodi-weite Player- oder Keymap-Hänger einführen. Der neue `XCMate Skin` ist ein *späteres* unabhängiges Projekt, kein Blocker für die hier verlangte funktionsfähige Infobar im Add-on.

## 1. Muss-Bild: ERSTES OK zeigt genau eine kompakte Senderinformation

**Dieses Schema ist die verbindliche inhaltliche und visuelle Referenz für das erste OK.** Es sind **ausschließlich Platzhalterwerte**, KEINE real eingelesenen EPG-Daten:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  [ SENDER-LOGO ]   WELT HD                                                  │
│                    JETZT: Aktueller Sendungstitel       20:15 – 21:45 Uhr  │
│                                                                              │
│                    █████████████████████░░░░░░░░░░░░  59 / 90 Min.          │
│                    59 Minuten vergangen               Noch 31 Minuten      │
│                                                                              │
│                    DANACH: Nächster Sendungstitel      ab 21:45 Uhr        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Visuelle Ausführung:** Über dem laufenden, weiterhin sichtbaren TV-Bild eine **niedrige untere transparente Leiste** in dunklem, hochwertigem Slate-/Grau mit dezenten blauen/silbernen Akzenten entsprechend `DESIGN_SYSTEM_DE.md`. Senderlogo links, kanalbezogene Textinformationen klar gegliedert daneben; Progressbar als gut erkennbare horizontale Strecke. Mindestens zwei Informationszeilen (JETZT/DANACH), gute Lesbarkeit aus TV-Distanz, genügend Randabstand/Safe-Area. Kein sofortiges Aufblenden aller Stop-/Spul-/Konfigurationstasten. Kein unlesbarer Kleintext, kein Abschneiden am unteren Bildschirmrand. Definierte Asset-Icons statt Unicode-Zeichen, die als kleine Kästchen erscheinen.

**Funktionale Regeln:**
- Kanal-Logo und Kanalname immer aus lokalem Metadatenkatalog; bei fehlendem Logo einen neutralen Platzhalter zeigen.
- **JETZT** = realer aktueller Sendungstitel, **Start–Ende** als Uhrzeit im lokalen Kodi-Zeitzonenformat.
- **Fortschrittsbalken**: nur aus validierten Zeitstempeln `start <= now < stop`, `stop > start`; `progress = max(0,min(1,(now-start)/(stop-start)))`. Daneben Zeit vergangen und Restlaufzeit in Minuten, niemals aus der Wiedergabezeit des Streams abgeleitet.
- **DANACH** = nächste zeitlich folgende Sendung mit Titel und mindestens Beginn, wenn vorhanden.
- Bei fehlendem EPG: `Für diesen Sender keine EPG-Daten verfügbar` und Senderlogo/-name trotzdem sofort anzeigen. **Kein fiktiver Titel, kein Fake-Fortschrittsbalken, keine 0/0-Minuten.**
- Bei laufender Infobar Zeitwerte mit reduziertem Timer aktualisieren, nicht per Netzwerkanfrage je Sekunde.
- First-OK = ausschließlich `INFO_BAR`, **keine Playeraktion** und kein Kodi-Standard-OSD.

## 2. Fernbedienungs-Zustandsautomat – verbindliche Abfolge

`LIVE_FULL` (Video ohne eingeblendete XCMate-Elemente)
- **1× OK → `INFO_BAR`** (die oben dargestellte Infobar).
- **Links → `CHANNEL_LIST`** (lokal und schnell).
- Hoch/Runter behält das separate bereits geplante direkte Zapping zum vorherigen/nächsten Sender bei, wenn kein Menü offen ist.

`INFO_BAR`
- **OK erneut ODER Runter → `PLAYER_CONTROLS`**. Auf dem zweiten OK **nur Menü öffnen**, NICHT automatisch Pause/Stop/„Weitere“ anklicken.
- Links → `CHANNEL_LIST`.
- Zurück → `LIVE_FULL`, Video läuft weiter.
- Nach kurzer konfigurierbarer Inaktivität automatisch ausblenden.

`PLAYER_CONTROLS`
- Sichtbare horizontale Hauptleiste mit **Pause/Fortsetzen, Stop, Timeshift/Spulen nur wenn technisch unterstützt, Weitere**.
- **Weitere → `MORE_SETTINGS`**: Ton/Audio, Bild/Videoeinstellungen, **Untertitel**, EPG, allgemeine XCMate-Einstellungen, Sendergruppen. Die Funktionen mit Kodi-Omega-kompatiblen API-Aktionen verbinden.
- Hoch/Runter/Links/Rechts/OK navigieren mit eindeutig sichtbarem Fokus; OK führt genau **eine** gewählte Aktion aus. Zurück schließt nur diese Ebene.
- Untertiteloption ausdrücklich vorsehen; „EPG“ darf nicht bloß die Kanalliste mit umbenannter Überschrift öffnen.

`CHANNEL_LIST`
- Links aus dem TV-Bild öffnet die Senderliste **ohne synchrone API-/XMLTV-Abfrage**.
- Senderzeile: **Senderlogo, Sendername, JETZT-Titel, Start–Ende**, optional kompakte Fortschrittsanzeige und folgende Sendung.
- Hoch/Runter bewegen Fokus **genau eine** Senderzeile; OK auf Sender tune't **genau diesen**, kein Seitenlink darf als Sender gespielt werden. Links öffnet Gruppen.
- Deutlich unterscheiden: aktuell wiedergegebener Sender und momentan fokussierter Sender.
- Zurück schließt nachvollziehbar, ohne Wiedergabe zu stoppen.

**Technisches Muss:** Kodi Omega verwendet `onControl` und native `onAction`-Ereignisse teils nacheinander. Keine doppelten OK-/D-Pad-Aktionen, keine verlorenen Focus-Events, keine unerwartete Wiedergabeunterbrechung. Globales Fallback-Keymapping **standardmäßig AUS**, BINGIE MOD und andere Add-ons uneingeschränkt nutzbar. Den bereits behobenen `ControlList(_itemHeight,_space)`-Fehler nicht wiederherstellen.

## 3. P0/P1: EPG zuerst wirklich stabilisieren – Datenkette vollständig prüfen

**User-Befund am echten Android-TV:** XCMate 0.1.24 zeigt Senderliste und OSD erstmals sichtbar, **aber keine Jetzt-/Danach-Einträge** und keine nutzbare EPG-Ansicht. Die älteren EPG-Diagnosen aus 0.1.23: `PROVIDER_LIMIT → NO_NEW_GUIDE` und externe `DOWNLOAD_FAILED`. **Nicht ungeprüft behaupten, diese exakten Quellfehler seien unter 0.1.24 neu reproduziert** – neue Diagnose erfassen.

Technischer Pfad, den Codex Ende-zu-Ende untersuchen muss:

```text
Provider-XMLTV / externe XMLTV-Feeds / Xtream get_short_epg
    → Download / Dekompression / Parsing / Limits (mit exakter Fehlerstufe)
    → normalisierter persistenter EPG-Cache
    → manuelle und automatische stream_id ↔ epg_channel_id ↔ XMLTV-ID-Zuordnung
    → gemeinsamer LOCAL now/next Resolver für JETZT/DANACH/Start/Ende
    → INFO_BAR, CHANNEL_LIST, EPG-Detailvorschau
```

**Bereits identifizierte Software-Lücke:** `main._live_channels()` verwendet `epg_views.cached_short_guide`, wenn normalisiertes EPG fehlt. `live_overlay._render()` verwendet bisher nur `guide_for_channel(load_cache(...))`. Der **lokal bereits verfügbare** Xtream-Kurz-EPG-Fallback muss beiden Ansichten konsistent zur Verfügung stehen. `guide_for_channel` in `epg_views.py` liefert derzeit `now_time/next_time`, aber der Infobar fehlen vollständige validierte Start-/Stop-Timestamps und damit Prozent/Restzeit; gemeinsames Modell entsprechend erweitern, rückwärtskompatibel.

**Separater EPG-Button:** `live_overlay._epg()` prüft für laufenden Sender `get_short_epg(...cached_only=True)` und startet sonst eine Hintergrundabfrage mit Hinweis „Gleich erneut öffnen“. Die eigentliche `guide`-Ansicht rendert dieselben Kanalnamen wie die normale Liste. Gewünscht: eine **wirkliche benutzbare Programmübersicht** mit laufendem Titel, nächsten Sendungen und Zeiten, plus verständlicher Status-/Fehleranzeige, wenn keine Daten importiert wurden. Hintergrunddownload bleibt im Worker; UI danach gezielt aktualisieren, ohne Fokus zu stehlen. Manuelle IDs/Overrides respektieren.

**Pflicht zu #13:** Der eigenständige EPG-Status muss Quellenname/Index (keine Secrets), Last-success, Fehlerklasse und Stadium, Grenzart (Bytes/Kanäle/Programme/Zeit), importierte Sender-/Programmanzahl sowie Matching-Quote zeigen. Fehlende oder ungültige XMLTV-Daten dürfen nicht als „erfolgreich geladen“ gemeldet werden. Die 80-MiB-Schutzgrenze bei XMLTV nicht unkontrolliert erhöhen. Kleinere DE-/AT-/CH-Quellen getrennt testen. Vorhandene Cache-Daten und manuelle Zuordnungen bei Fehlern nicht löschen.

**Abnahmekriterium:** Mindestens ein **echter** regulärer Sender mit tatsächlich geladenem, korrektem Now-/Next-Eintrag (inklusive Von–bis und Progress) auf **dem Android-TV**. Fixtures alleine sind nicht ausreichend.

## 4. P0/P2: Performance – Senderliste muss verzögerungsarm aufgehen

Befund: Links ruft Liste inzwischen auf, aber Nutzer berichtet **starke Verzögerung**; im alten Portal-Katalog wurden **53.664 Sender**, in der aktuellen Ansicht **2746 Sender / 28 Seiten** protokolliert.

Codex soll zunächst die Latenz **messen und nach Phasen aufteilen**: Kategorie-Filter/Index, Cache-Hit/Disk-I/O, EPG-Routing, `ControlList.reset/addItems`, Fokusvergabe, eventuelle Network-I/O.

Anschließend:
- Sender nach Kategorie / `stream_id` **im Hintergrund vorkatalogisieren**, statt bei jeder Eingabe lange Listen abzuklappern.
- Für tatsächlich sichtbare Zeilen (und höchstens den aktuellen paginierten Ausschnitt) normalisierte Now-/Next-Daten **lokal vorhalten**. Nur bei EPG-Version-, Sender- oder Zeitfensterwechsel invalidieren.
- Bestehende 100er-Paginierung und korrekte absolute Sender-IDs beibehalten; auf echten Bildschirm möglichst **wenige, gut lesbare sichtbare Zeilen** statt 100 Zeilen pro GUI-Refresh. Eingabe darf nicht warten, bis für alle 53.664 Sender EPG verfügbar ist.
- **Niemals HTTP/Download/komplette XMLTV-Verarbeitung aus `onAction`, `onControl`, `_render` oder bei Links/OK starten.** Background-/service-Pfade nutzen.
- Als **Ziel** (nicht behaupteter Messwert): warme Senderliste bis sichtbarem Fokus möglichst unter 500 ms, Infobar unter 250 ms; am Gerät messen, bei langsamer Hardware begründet anpassen.
- Keine UI-weiten Hänger, keine ungebremsten Threads/Dateien und kein vollständiges Neuladen beim Öffnen oder Schließen.

## 5. Codex-Aufgabenfolge (Reihenfolge ist verbindlich)

**A – P0 Stabilität:** 0.1.24-Overlay-Start erhalten. Fernbedienungszustände sauber modellieren und D-Pad/OK/Zurück, `onControl` vs `onAction` mit strikten Kodi-21-Tests prüfen. UI soll selbst bei fehlendem EPG benutzbar bleiben.

**B – P1 EPG-Daten:** EPG-Refresh/Kategorien/Fehlerursachen und ID-Matching prüfen, echten Kurz-EPG in gemeinsamen lokalen Resolver einbinden. EPG-Status und eine verifizierbare Programmanzeige aus Issue #13 bauen.

**C – INFO_BAR-Layout:** Exakt dargestellte kompakte erste OK-Leiste mit Logo, JETZT-/DANACH-Zeilen, Start/Ende, gültiger Progressbar und Restzeit. Bei fehlenden Daten ehrlicher Missing-State.

**D – PLAYER_CONTROLS:** Zweites OK oder Runter → untere Steuerung; weitere Optionen inkl. Untertitel/EPG; saubere Fokus-/Safe-Area- und Style-Ausführung.

**E – CHANNEL_LIST:** Links → schnelle Senderliste; Name/Icon/Jetzt/Von–bis und ggf. Progress pro sichtbarer Senderzeile; Fokus und tatsächliches Umschalten korrekt.

**F – Qualitätsprüfung:** automatisierte Regressionstests und GitHub-CI + dokumentierter Android-Akzeptanzplan, einschließlich großer Kataloge, Zeitzonen, ungültiger EPG-Timestamps, fehlender Logos/EPG-Daten, Untertitel-/Ton-/Videoeinstellungen, 1×/2× OK, Back/Stop, Fremd-Add-ons und Kodi-Neustart.

Falls ein einzelner PR zu groß wird: **zuerst separaten P0/P1-Daten-/Remote-PR, danach UI-/Performance-PR** mit klarer Kompatibilität und Tests, statt unprüfbare Megakorrektur. Aber sämtliche Anforderungen in der Übergabe verbindlich erhalten.

## 6. Vor Abgabe an den Nutzer

Codex liefert im PR:
- **Exakte Versionsnummer** des neuen Kandidaten, Dateien/Diff, branch name, Commit und prüfbare Testanzahl.
- Werksfähiges XCMate-Testpaket sowie eigene korrekte **SHA-256** des betreffenden ZIPs. Beim automatischen GS-Media-Publish ZIP-Prüfsumme neu berechnen, nicht eine veraltete Branch-Prüfsumme verwenden.
- Testnachweis für: First OK INFO_BAR, Second OK/Down Controls, Linksliste/Fokus, echte EPG-Now/Next-/Progress-Rechnung, gefilterte Senderlisten, fehlendes EPG, EPG-Quellenfehler, keine Kodi-weiten Seiteneffekte.
- Aktualisierte `CODEX_STATUS_CURRENT_DE.md`, `README.md` und diesen Auftrag mit **Implementiert / CI bestanden / auf main / Android bestätigt** als getrennten Stati. Historische Fehlerberichte bewahren.
- **Keine Aussage „fertig“**, wenn die Kodi-21-Bindings nur mit Mocks getestet wurden und noch kein realer Android-Test erfolgte.
- **Keine eigenmächtige Veröffentlichung auf `main`**; separater PR mit Reviewerklärung, danach Nutzerfreigabe und gewohnter GS-Media-Kodi-Repository-Updateweg.

## 7. Direkt einzufügender Codex-Startauftrag

> Bitte arbeite die verbindliche Datei `docs/XCMate/CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md` ab. Beginne mit dem realen 0.1.24-Gerätebefund und den Issues #17, #13 und #12. Erhalte das inzwischen sichtbare TV-Overlay, stabilisiere D-Pad/OK und EPG-Import samt lokalem Kurz-EPG-Fallback. Implementiere EXAKT die kompakte erste-OK-Senderinfo mit Logo, Jetzt/Danach, Von–bis, Fortschrittsbalken und Restzeit; zweites OK oder Runter öffnet erst die Playersteuerung. Links öffnet eine mit EPG versehene, deutlich schnellere Senderliste. Nutze korrekte Kodi-21-API-Signaturen und keine Netzwerkarbeit im GUI-/Tastenpfad. Arbeite mit Branch + CI + PR; **kein Merge nach main** ohne Freigabe. Dokumentiere den realen Android-Abnahmeplan und halte die zentrale Übergabe aktuell.
