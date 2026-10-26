# CODEX-ARBEITSAUFTRAG – XCMate 0.1.29.40

**Projekt:** GS Media – XCMate IPTV für Kodi 21  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Ausgangsversion:** `0.1.29.39` auf `main`  
**Zielversion:** `0.1.29.40`  
**Zielgerät:** Android-TV-Box B, RK3528 ARM32, Kodi 21.3, Titan BINGIE MOD  
**Priorität:** P0 – Wiederherstellung der Wiedergabe- und Playerstabilität

## 1. Verbindliche Entwicklungsregeln

Version 0.1.29.39 wurde über PR #198 auf `main` gemergt und auf Box B installiert.

Die neue Version muss **vollständig kumulativ auf dem aktuellen `main` aufbauen**.

Unbedingt beachten:

- Keine Deinstallation, kein Downgrade und kein Zurücksetzen bestehender Installationen.
- Keine Veränderung von Portalzugängen, Sendergruppen, Startsendern, EPG-Zuordnungen, Favoriten oder Wiedergabeständen.
- Keine automatische Datenbanklöschung, Cachebereinigung oder Neuindizierung als vermeintliche Fehlerbehebung.
- Box A bleibt vollständig unangetastet.
- Box B verwendet dynamisches Artwork. Keine ungefragte Speicher-, USB-, SD-, SMB- oder Migrationsaktion.
- Bestehende funktionsfähige Fernbedienungs- und Overlay-Funktionen erhalten.
- Original-XCMate-Icon beibehalten.
- Änderungen in einem eigenen **Draft-PR** entwickeln.
- **Kein automatischer Merge nach `main` und keine automatische Releasefreigabe.**

**Die P0-Fehler haben absoluten Vorrang vor neuen Features.**

## 2. Ausgangslage: Android-Test 0.1.29.39

GitHub-Abnahmebericht:

https://github.com/artattakk-creator/kodi-noodleprivate/issues/204

Ergebnisse:

- 21 Testfälle
- 10 PASS
- 8 FAIL
- 3 NOT_TESTED

Die Version ist auf Android derzeit nicht freigabefähig.

### Neue Logauswertung

Analysiert wurden:

- `kodi.old(20261026-161828).log`
- `kodi(20261026-161823).log`

Wichtig: Das ältere Log beginnt unter `.38`. Erst um **16:04:55 Uhr** wurde die installierte `.39` bestätigt. Vorherige Ereignisse dürfen nicht als neue `.39`-Regression gewertet werden.

Die privaten Logs können Zugangsdaten und Netzwerkinformationen enthalten. Niemals ungekürzt ins öffentliche Repository übernehmen.

---

## 3. P0-A – Filme und Serien starten nicht mehr

**GitHub #202:**  
https://github.com/artattakk-creator/kodi-noodleprivate/issues/202

### Nachgewiesener Fehler

Im neueren Kodi-Log wurden neun VOD-Startversuche erkannt.

Kodi öffnet jeweils zunächst den Stream über `VideoPlayer::OpenFile`. Anschließend löst XCMate selbst einen `PLAYER_EXIT EXIT_INTENT` aus.

Die gemessenen Abstände zwischen Start und Stop-Anforderung betragen:

`1.623 / 1.368 / 1.339 / 1.199 / 0.913 / 0.638 / 0.732 / 1.335 / 1.307 Sekunden`

Beispiel vom 26.10.2026:

- 17:09:04.578 – Kodi öffnet den Filmstream.
- 17:09:05.754 – Android-Videodecoder wird initialisiert.
- 17:09:05.885 – XCMate meldet `EXIT_INTENT`.
- 17:09:06.092 – `PLAYER_STOP_START`.
- 17:09:06.105 – Kodi meldet `OnExit`.

### Codex-Auftrag

Die tatsächliche Ursache der vorzeitigen Stop-Anforderungen ermitteln und dauerhaft beheben.

Insbesondere untersuchen:

- `playback_exit.py`
- `exit_jobs.py`
- `media_osd.py`
- `media_return.py`
- `media_intent.py`
- `media_window.py`
- Player-Ownership und Session-Identität
- Fullscreen-Erkennung während des Startvorgangs
- Asynchrone Player-Callbacks und zeitliche Race Conditions

**Besonders kritisch:** `playback_exit.poll()` kann einen Stop auslösen, wenn ein zuvor bestätigter Vollbildzustand verlassen wurde. Prüfen, ob Kodi während des initialen Starts kurzzeitig den Fensterstatus ändert und XCMate dies fälschlich als Wiedergabeende interpretiert.

Für jeden `EXIT_INTENT` muss künftig eine eindeutige Ursache protokolliert werden, beispielsweise:

- `USER_STOP`
- `USER_BACK`
- `FULLSCREEN_EXIT`
- `OWNER_CHANGED`
- `AUTOPLAY_CANCEL`
- `PLAYBACK_ENDED`
- `STARTUP_ABORT`

Diese Ursachen sind Vorschläge für die Instrumentierung, keine bereits bestätigten Diagnosen.

**Akzeptanz:** Filme und Episoden starten zuverlässig und werden nicht ohne tatsächlichen Stop- oder Exit-Wunsch beendet.

---

## 4. P0-B – Kodi hängt beim Zurück aus Live-TV

**GitHub #203:**  
https://github.com/artattakk-creator/kodi-noodleprivate/issues/203

### Nachgewiesener Ablauf

26.10.2026 um etwa 16:28 Uhr:

- 16:28:37.654 – `LIVE_EXIT STOP_REQUESTED`
- 16:28:37.924 – `PLAYER_EXIT EXIT_INTENT`
- 16:28:38.212 – `PLAYER_STOP_START`
- 16:28:38.466 – Kodi beginnt `CVideoPlayer::CloseFile()`
- 16:28:38.979 – Altes Log endet ohne protokolliertes `PLAYER_STOP_DONE`.
- 16:30:00 – Kodi startet neu.

Der Nutzer meldet eine vollständige Blockade der Fernbedienung.

### Codex-Auftrag

Zusammenhang zwischen Live-Overlay, Back-Taste, Stop-Worker, Kodi-Decoderfreigabe und Navigation analysieren.

Prüfen:

- Doppelte oder überlappende Stop-Anforderungen.
- Thread-Deadlocks und blockierende Player-Aufrufe.
- Nicht abgeschlossene `exit_jobs`.
- Fehlerhafte Window-/Modal-Ownership.
- Verlorene GUI-Fokuszustände.
- `LIVE_EXIT RETURN_BLOCKED` nach Player-Stop.
- MediaCodec-/Rendererprobleme beim Streamende.

Der GUI-Thread darf nicht auf einen möglicherweise blockierenden nativen Player-Stop warten.

Ein Timeout muss sicher erkannt werden und darf keinen zweiten unkontrollierten Stop auslösen.

**Akzeptanz:** Live-TV lässt sich über die definierte Zurück-/Stop-Bedienung zuverlässig verlassen, ohne Kodi zu blockieren.

---

## 5. P0-C – Rücksprung, Wiedergabestände und Serien-Autoplay

**Verwandte Issues:** #185, #202, #203

Nach erfolgreicher Wiederherstellung des Film- und Serienstarts müssen folgende Funktionen geprüft und erforderlichenfalls korrigiert werden:

1. Filmstart aus dem Filmkatalog.
2. Filmstart aus Suchergebnissen.
3. Serienepisode aus einer Staffel starten.
4. Zurück-Taste bei sichtbarem Player-OSD.
5. Zurück-Taste im reinen Vollbild.
6. Stop über Player-Bedienelement.
7. Rücksprung auf die ursprüngliche Ansicht mit erhaltenem Fokus und Scrollposition.
8. Wiedergabe fortsetzen / Resume.
9. Automatischer Start der nächsten Serienepisode.
10. Manueller Stop verhindert den nächsten Autoplay-Start.

**Wichtig:** Serien-Autoplay war beim `.39`-Test als FAIL markiert, konnte aufgrund der nicht startenden Episoden aber nicht isoliert beurteilt werden.

Erst die Grundwiedergabe reparieren, danach Autoplay separat abnehmen.

---

## 6. P1-A – Infobar und Player-OSD

**GitHub:** #183, #186

Android-Ergebnisse:

- 39-09 Infobar beim ersten OK: FAIL
- 39-10 Große Playerbuttons vorhanden: PASS
- 39-11 Technische Streaminformationen vorhanden: PASS
- 39-12 Unerwünschter Kodi-OSD-Fallback: FAIL

### Aufgaben

- Das erste OK muss zuverlässig die definierte XCMate-Infobar öffnen.
- Kodi darf bei regulärer XCMate-Navigation nicht unbeabsichtigt sein eigenes OSD übernehmen.
- Playerbuttons übersichtlich gruppieren und besser ausrichten.
- Streamdetails nach Bild, Ton und Untertiteln gliedern.
- Kleine passende Icons für Auflösung, Codec, Bildrate, HDR, Audio und Untertitel ergänzen.
- Fehlende technische Werte nicht erfinden.
- Vorhandene funktionierende Bedienelemente nicht ersetzen oder unbrauchbar machen.

Das vollständige Icon-Redesign aller XCMate-Menüs bleibt als eigener späterer UI-Auftrag #200 bestehen. Hier nur gezielte OSD-Korrekturen vornehmen.

---

## 7. P1-B – Globale Suche und flackernde Ergebnislisten

**GitHub #201:**  
https://github.com/artattakk-creator/kodi-noodleprivate/issues/201

Aktuelle Erkenntnisse:

- Die Suche nach `Rock` findet grundsätzlich wieder Live-TV, Filme und Serien.
- Filmresultate werden zeitweise sehr langsam aufgebaut.
- Nach Reiterwechseln verschwinden Ergebnisse vorübergehend.
- Die Ergebnislisten blitzen/flackern sichtbar.
- Protokollierte Renderfolgen enthalten unter anderem `5 → 0` und `48 → 0 → 48`.
- EPG-Anreicherung dauerte in einem Suchlauf rund 39 Sekunden.

### Codex-Auftrag

- Ergebniszustände pro Query, Portal, Kategorie und Generation getrennt verwalten.
- Bereits bestätigte Ergebnisse bei noch laufenden Hintergrundabfragen sichtbar erhalten.
- `INDEX_PENDING` darf nicht als endgültige leere Trefferliste ausgegeben werden.
- Keine vollständigen ListItem-Rebuilds bei unverändertem Datenbestand.
- Keine späten Worker-Callbacks auf eine inzwischen andere Suchsitzung anwenden.
- Film-, Serien- und Live-Ergebnisse getrennt paginieren und inkrementell aktualisieren.
- Fokus, Scrollposition und Cover während der Aktualisierung erhalten.
- Lange Filmabfragen und EPG-Enrichment dürfen die GUI nicht blockieren.

Ziel: **stabile, flackerfreie Suche mit reproduzierbaren Ergebnissen auch bei schnellen Reiterwechseln.**

---

## 8. P1-C – Mini-EPG, großes EPG und UI-Latenz

**GitHub:** #182, #187, #191

Die Logs zeigen sporadisch:

- Mini-EPG-Wartezeiten bis etwa 16,2 Sekunden.
- Live-Infobar-Anzeigezeiten bis etwa 33,8 Sekunden.

Diese Zeiten sind End-to-End-Messungen und dürfen nicht automatisch als reine Renderzeit interpretiert werden.

### Aufgaben

- Blockierende Netzwerk-/EPG-Arbeit aus der GUI-Navigation entfernen.
- Bereits vorhandene lokale EPG-Snapshots wiederverwenden.
- Großen und kleinen EPG für dieselben Sender und Uhrzeiten auf Now/Next-Konsistenz prüfen.
- Unterschiedliche Vorschauhorizonte zwischen großem und kleinem EPG sind zulässig.
- Rechten Mini-/Detail-EPG-Bereich etwas schmaler gestalten.
- Lange Sendungstitel maximal zweizeilig umbrechen.
- Jetzt-Markierung und Fernbedienungsfokus beibehalten.
- Keine neue Datenquelle beim bloßen Öffnen einer EPG-Leiste synchron herunterladen.

---

## 9. P1-D – Navigation und Kodi-Kompatibilität

**GitHub:** #188, #192

- Zurückbleibende Menütexte und Geisterbeschriftungen korrigieren.
- Bereits funktionierende schmale Gruppen-Icon-Leiste beibehalten.
- MediaCodec-Timeouts, `InstanceGuard locked`, `null size` und Rendererfehler getrennt von XCMate-Stop-Auslösern analysieren.
- Keine Decoderwarnung ohne Beleg zur alleinigen Ursache erklären.
- Keine zusätzlichen Kodi-globalen Keymap- oder Skinänderungen.

Die vorhandene BINGIE-MOD-Installation bleibt unverändert.

---

## 10. Verbindliche Teststrategie

### Automatisierte Tests

Bestehende Tests vollständig ausführen und die kritischen Fälle ergänzen:

- Vorzeitiger Fullscreen-Wechsel während eines VOD-Starts.
- Stop-Intent ohne Benutzeraktion wird verhindert.
- Expliziter Stop beendet genau die eigene Session.
- Mehrfacher Stop verursacht keinen Doppelabbruch.
- Fremde Player-Sessions werden nicht übernommen.
- Netzwerk- und Decoderfehler führen zu kontrollierter Rückkehr.
- Suchergebnis bleibt trotz verzögerter Teilantwort erhalten.
- EPG-Refresh läuft während der Fernbedienungsnavigation.
- Kodi-Neustart mit bestehendem Profil und alten Einstellungen.

### Android-Abnahme

Codex muss eine neue, per Checkbox überprüfbare Abnahmeliste für Box B erstellen.

Mindestens:

- 20 erfolgreiche Filmstarts.
- 20 erfolgreiche Episodenstarts.
- 20 Live-TV-Back-/Stop-Zyklen.
- 20 VOD-Back-/Stop-/Rücksprung-Zyklen.
- Serien-Autoplay und manueller Stop.
- Suche `Rock` und `Rocky` mit 20 Reiterwechseln.
- Keine flackernden oder vorzeitig gelöschten Ergebnislisten.
- Wiederholtes Öffnen von Mini-EPG und Infobar.
- Player-OSD und technische Streaminformationen.
- Kein Kodi-Hänger, keine unbeabsichtigte Playerübernahme.
- Keine Veränderung gespeicherter Portale, Sendergruppen, Favoriten oder Resume-Daten.

**Alle Android-Tests zunächst NOT_TESTED.**

Erfolgreiche Hosttests oder CI sind nicht mit Android-PASS gleichzusetzen.

---

## 11. GitHub-Issue-Verwaltung

Nach der Implementierung den aktuellen Zustand aller betroffenen Issues prüfen:

- #182 / #183
- #185 / #186 / #187 / #188
- #189 / #190 / #191 / #192
- #201 / #202 / #203 / #204

GitHub-Roadmap:  
https://github.com/artattakk-creator/kodi-noodleprivate/issues/194

Je Issue dokumentieren:

- Behobener Codepfad.
- Zugehöriger PR/Commit.
- Automatisierter Teststatus.
- Android-Testfälle und erwartetes Ergebnis.
- Noch offene Fehler.
- PASS / FAIL / BLOCKED / NOT_TESTED.

**Kein Issue nur wegen eines erfolgreichen Commits oder PRs schließen.**

Schließen mit `completed` erst nach vollständig belegter, positiv bestätigter Abnahme.

Die bereits geplanten späteren Funktionen zu Portalverwaltung, internationalem EPG, öffentlichen Playlists, Experimentell-PIN und Menü-Icons bleiben als eigenständige Issues erhalten.

Für Version `.40` haben die produktionskritischen Fehler Vorrang. Größere neue Features dürfen die Stabilisierung nicht gefährden.

---

## 12. Erwartete Lieferung

Codex soll liefern:

1. Analyse der wahrscheinlichsten Ursachen mit Verweisen auf konkrete Codezeilen.
2. Implementierung der priorisierten Korrekturen.
3. Eigener Draft-PR für XCMate `0.1.29.40`.
4. Vollständige kumulative Testausführung einschließlich Regressionstests.
5. Bereitgestelltes Test-ZIP mit SHA256-Prüfsumme.
6. Android-Installations- und Abnahmeanleitung.
7. Dokumentation aller bearbeiteten und weiterhin offenen Issues.
8. Nachvollziehbare Liste aller Änderungen gegenüber `.39`.

### Abschlussregel

Zuerst **P0-Wiedergabe und Kodi-Hänger beheben**, danach die übrigen P1-Korrekturen integrieren und testen.

Weder automatisch nach `main` mergen noch die produktiven Installationen verändern.

**Ziel: XCMate 0.1.29.40 als zuverlässig testbaren, kumulativen Stabilisierungskandidaten für den weiteren Weg zur Version 1.0 bereitstellen.**