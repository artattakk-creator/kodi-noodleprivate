# CODEX-ARBEITSAUFTRAG – XCMate 0.1.29.41

**Projekt:** GS Media – XCMate IPTV für Kodi 21  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Aktuelle Hauptversion:** `0.1.29.40` auf `main`, PR #205  
**Neue Zielversion:** `0.1.29.41`  
**Master-Auftrag:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/213

**Zielgerät:** Android-TV-Box B, RK3528 ARM32, Kodi 21.3, Titan BINGIE MOD 2.2.3.

## 1. Verbindlicher Auftrag

Entwickle auf Grundlage des aktuellen `main` eine kumulative Version **XCMate 0.1.29.41**, die alle bisher identifizierten kritischen Fehler berücksichtigt.

Priorität hat die **stabile Live-TV-Wiedergabe einschließlich funktionierender Zurück-Taste**.

Weitere verbindliche Aufgaben:

- Mini-EPG-Darstellungsfehler reparieren.
- Falschen Mini-EPG-Zeitfensterwechsel korrigieren.
- Film-, Serien- und Live-TV-Widgets stabilisieren.
- BINGIE-MOD-Widgetdarstellung verbessern.
- Einmaliges Versions-Pop-up nach jedem echten Add-on-Update integrieren.
- Bestehende Film-/Serienwiedergabe, Suche, Navigation und Resume-Funktionen absichern.

Alle Reparaturen müssen im GitHub-Master-Issue #213 und in den jeweiligen Einzelissues mit Codeänderungen und Testergebnissen dokumentiert werden.

## 2. P0 – Live-TV friert beim Zurück ein

**Issue #203 – absolute Priorität**

https://github.com/artattakk-creator/kodi-noodleprivate/issues/203

### Reproduzierter Fehler

Unter XCMate `.40` funktioniert das Abspielen von Live-TV, jedoch hängt Kodi beim Verlassen mittels Zurück-Taste vollständig.

Die aktuellsten Android-Logs vom 26.10.2026 zeigen:

| Uhrzeit | Ereignis |
|---|---|
| 20:21:22.170 | `LIVE_EXIT STOP_REQUESTED` |
| 20:21:22.172 | Fernbedienung `action=92` |
| 20:21:22.709 | `EXIT_INTENT reason=USER_BACK kind=live` |
| 20:21:22.710 | `STOP_QUEUED` |
| 20:21:22.974 | `PLAYER_STOP_START` |
| 20:21:23.347 | Kodi `CVideoPlayer::CloseFile()` |
| 20:21:23.353 | Kodi `CVideoPlayer::OnExit()` |
| 20:21:23.514 | `OutputPicture timeout waiting for buffer` |
| 20:21:23.842 | Log endet ohne `PLAYER_STOP_DONE` |
| 20:22:34 | Kodi-Neustart |

Die Zurück-Taste wurde also erkannt. **Die Blockade tritt während des nativen Beendigungs- beziehungsweise Rückgabeablaufs auf.**

Ein konkreter Deadlock ist noch nicht bewiesen und muss untersucht werden.

### Verbindliche Fernbedienungssteuerung

| Aktueller Zustand | Zurück-Taste |
|---|---|
| Mini-EPG / Senderliste | Overlay schließen, Live-TV läuft weiter |
| Gruppenliste | Zur Senderliste zurück |
| Infobar | Infoleiste ausblenden |
| Player-Einstellungen | Zur vorherigen Player-Leiste zurück |
| Reines Live-TV-Vollbild | Eigenen Stream beenden und zur Herkunftsansicht zurückkehren |
| Film-Vollbild | Eigenen Film kontrolliert beenden und zurückkehren |

**Die Zurück-Taste darf keinesfalls deaktiviert werden.**

### Zu untersuchende Codebereiche

- `live_overlay.py`
- `live_exit.py`
- `exit_jobs.py`
- `playback_exit.py`
- Kodi WindowDialog-Lebenszyklus
- Kodi `CVideoPlayer::CloseFile`
- MediaCodec- und AudioTrack-Freigabe
- Asynchrone Stop- und Rücksprungsteuerung

Prüfe insbesondere, warum der bereits in `.40` eingesetzte Stop-Worker zwar `PLAYER_STOP_START` ausführt, aber nicht zurückkehrt und Kodi dennoch blockiert.

Ein Stop-Timeout darf keinen zweiten unkontrollierten Stop verursachen. Ein Timeout darf auch nicht fälschlich als erfolgreich beendete Wiedergabe protokolliert werden.

**Ziel:** Live-TV mit der Fernbedienung zuverlässig verlassen, ohne Kodi-Neustart.

## 3. Film- und Serienwiedergabe absichern

**Issues #202 und #210**

Unter `.40` gibt es inzwischen einen nachweislich erfolgreichen Filmtest:

- Filmstart: 19:53:57 Uhr
- Film lief etwa 5 Minuten 27 Sekunden.
- `USER_BACK` um 19:59:24 Uhr.
- `PLAYER_STOP_DONE` um 19:59:25 Uhr.

Die früheren sofortigen Stopps nach ein bis zwei Sekunden traten in diesem Test nicht auf.

**Diesen Fortschritt unbedingt erhalten.**

Ein früher berichteter Movies-Hänger bleibt separat ungeklärt und darf nicht mit dem späteren Live-TV-Hänger gleichgesetzt werden.

Pflichttests:

1. Film aus Katalog starten und abspielen.
2. Film aus Suchergebnissen starten.
3. Serienepisode starten.
4. Film/Serie über Zurück beenden.
5. Resume-Position prüfen.
6. Serien-Autoplay und manuellen Stop prüfen.
7. Rückkehr mit erhaltenem Fokus und Suchzustand.
8. Keine Übernahme fremder Kodi-Player.

## 4. P1 – Mini-EPG: Überlagerte Texte beseitigen

**Issue #211**

https://github.com/artattakk-creator/kodi-noodleprivate/issues/211

Unter `.40` erscheinen rechts im Mini-EPG verschiedene Textbausteine übereinander. Die Anzeige ist teilweise unlesbar.

### Nachgewiesene Codeursache

`mini_epg.py::MiniProgramme` erzeugt aktuell zwei übereinanderliegende Textdarstellungen:

- Eine native `ControlList` mit Sendungszeiten und Titeln.
- Fünf zusätzliche `ControlLabel`-/`ControlTextBox`-Zeilen an denselben Koordinaten.

Beide werden sichtbar geschaltet.

### Reparatur

Nur **eine sichtbare Textebene** pro Programmzeile verwenden.

Dabei erhalten bleiben müssen:

- Native Fernbedienungsnavigation.
- Aktive Sendungsmarkierung.
- Separater Auswahlfokus.
- Maximal zweizeilige Programmtitel.
- Kompakte rechte EPG-Spalte.
- Korrekte Zeilenabstände.
- Keine überlappenden oder stehenbleibenden Beschriftungen.

Test bei 1920 × 1080 sowie 1280 × 720.

## 5. P1 – Mini-EPG zeigt plötzlich vergangene Sendungen

**Issue #208**

https://github.com/artattakk-creator/kodi-noodleprivate/issues/208

### Beobachtung

Das Mini-EPG zeigt zunächst kommende Sendungen, beispielsweise bis nach 23 Uhr.

Nach der Hintergrundaktualisierung springt die Darstellung auf zurückliegende Sendungen.

Das große EPG ist nicht betroffen.

### Technische Untersuchung

Relevante Bereiche:

- `mini_epg.py`
- `epg_views.py`
- `tv_data.py`
- `guide_viewport.py`
- `local_epg.py`

Bisherige Codeanalyse:

`events` enthält zunächst aktuelle und kommende Programme.

Später übernimmt `programme_events` auch historische Sendungen aus einem Rückblickfenster. Diese Liste erhält in `MiniProgramme.render()` Vorrang.

Zusätzlich kann die Begrenzung auf 256 Elemente zukünftige Sendungen abschneiden, wenn vorher historische Einträge einsortiert werden.

### Reparaturziel

Das Mini-EPG zeigt standardmäßig:

**Jetzt → Danach → weitere kommende Sendungen.**

Vergangene Sendungen dürfen nicht ungefragt die Vorschau ersetzen.

- Filterung anhand tatsächlicher Start-/Endzeiten.
- Erst Zeitfenster auswählen, dann Eintragslimit anwenden.
- Späte Worker-Ergebnisse dürfen keine neuere Senderauswahl überschreiben.
- Großes und kleines EPG müssen bei Jetzt/Danach übereinstimmen.
- Unterschiedliche Vorschauhorizonte bleiben zulässig.
- Bestehende manuelle EPG-Zuordnungen und Quellen unangetastet lassen.

## 6. P1 – Film-, Serien- und Live-TV-Widgets reparieren

**Issues #207, #206 und #26**

### Fehler A: XCMate IndexReadError

Bei den Widgets werden weiterhin `IndexReadError`-Fehler protokolliert.

In den aktuellen `.40`-Logs:

- Live-TV-Widget schlägt nach ca. 8,3 Sekunden fehl.
- Filmwidget schlägt nach ca. 9,2 Sekunden fehl.
- Andere Widget-Aufrufe dauern teilweise über 20 Sekunden.

Prüfen:

- SQLite-Lesezugriffe und Sperren.
- Zu knappe Reader-Timeouts.
- Parallele Home-Widget-Abfragen.
- Indexzustand und Ergebnis-Caching.
- Fehlende konkrete SQLite-Fehlerdiagnostik.

**Keine Datenbank löschen oder vollständig neu indizieren, nur um den Fehler zu umgehen.**

### Fehler B: BINGIE Skin Shortcuts

Zusätzlich wurden unabhängig von XCMate Fehler im externen `script.skinshortcuts` festgestellt:

- `Element.getiterator` – nicht kompatibler Python-Aufruf.
- `ElementTree.ParseError: mismatched tag`.

Die genaue XML-Eingabe, die den ParseError verursacht, ist noch zu identifizieren.

Bitte kompatible Skin-Shortcuts-Integration ermitteln.

Fremde Skin-Dateien ausschließlich nach ausdrücklicher Freigabe verändern. Keine automatische Skin-Neuinstallation und kein Shortcut-Reset.

### Neues Live-TV-Widget-Layout

Verbindlicher Nutzerwunsch:

- Senderlogos ungefähr **50 % kleiner** als bisher.
- Kompakte, sauber ausgerichtete Senderkacheln.
- Keine übergroßen Grafiken.
- Beim Markieren eines Senders per Fernbedienung erscheint das EPG des jeweiligen Senders.
- Anzeige von Jetzt, Danach, Uhrzeiten und tatsächlichem Sendungsfortschritt.
- Kein Kanalwechsel beim bloßen Markieren.
- Kein Netzwerkabruf für jeden einzelnen Fokuswechsel.

Falls BINGIE dafür einen spezifischen Skin-Adapter benötigt, zunächst eine versionierte, reversible Lösung ausarbeiten.

Bestehende Startseitenkonfigurationen dürfen nicht überschrieben werden.

## 7. Pflichtfunktion: Versions-Pop-up nach Update

**Issue #209 – in Version `.41` verbindlich implementieren**

https://github.com/artattakk-creator/kodi-noodleprivate/issues/209

Nach einem tatsächlich erfolgreich installierten XCMate-Update soll einmalig ein Pop-up erscheinen:

**XCMate erfolgreich aktualisiert!**

**Installierte Version: 0.1.29.41**

Die Versionsnummer muss dynamisch aus der installierten Add-on-Version ausgelesen werden.

Anforderungen:

- Nur einmal pro tatsächlichem Versionsupdate.
- Nicht bei jedem Kodi-Neustart.
- Version lokal in `addon_data` persistent merken.
- Keine irreführende Aktualisierungsmeldung bei bloßer Repository-Veröffentlichung.
- Nach Bestätigung über OK oder Zurück nicht erneut anzeigen.
- Bei laufendem Film oder Live-TV Pop-up zurückstellen, niemals die Wiedergabe unterbrechen.
- Keine blockierenden GUI-Dialoge im Hintergrundservice-Thread.

Auch nachfolgenden Updates muss diese Funktion automatisch zur Verfügung stehen.

## 8. Bestehende Funktionen absichern

Die in `.40` bereits eingeführten Änderungen dürfen nicht regressieren.

Insbesondere zu prüfen:

- Globale Suche nach `Rock` und `Rocky`.
- Suchtreffer in Live-TV, Filme und Serien.
- Kein Blitzen beziehungsweise `48 → 0 → 48` bei Reiterwechseln.
- Erste OK-Taste öffnet XCMate-Infobar.
- Technische Bild-, Ton- und Untertitelinformationen.
- Kein unbeabsichtigter Kodi-OSD-Fallback.
- Gruppenliste, Navigation und Auswahlfokus.
- Startkanal und Startgruppe bleiben gespeichert.
- Cover bleiben bei Kategorie- und Reiterwechsel erhalten.

Offene Probleme nachvollziehbar ihren jeweiligen GitHub-Issues zuordnen.

## 9. Automatisierte Tests

Vollständige bestehende Host-Test-Suite ausführen.

Zusätzliche gezielte Tests implementieren für:

- Kodi-Back-Action 92 in allen Overlayzuständen.
- Asynchronen Live-Stop mit kontrollierter Rückkehr.
- Nicht beantworteten nativen Stop.
- Doppelte Stop-Anforderungen und wechselnde Player-Sessions.
- VOD-Start ohne vorzeitigen Exit.
- Mini-EPG ohne doppelte Textdarstellung.
- Mini-EPG-Snapshot mit historischen und zukünftigen Programmen.
- Widget-Reader bei SQLite-Timeout/Sperren.
- Film- und Serienwidget-Routing.
- Versions-Pop-up nach echtem Upgrade.
- Kein Versions-Pop-up nach erneutem Kodi-Neustart.

Host-Tests müssen PASS sein, sind aber ausdrücklich **kein Ersatz für die Android-Abnahme**.

## 10. Android-Abnahme Box B

Codex soll eine neue vollständige Testmatrix für `.41` vorbereiten.

**Kritische Reihenfolge:**

1. Normaler XCMate-Start einschließlich gespeichertem Startkanal.
2. Filmstart, kurze Wiedergabe und Zurück.
3. Live-TV starten und einmal kontrolliert mit Zurück verlassen.
4. Erst nach Erfolg fünf weitere Live-Back-Durchläufe.
5. Danach reguläre 20-Zyklen-Stabilitätsabnahme.

**Bei einem vollständigen Kodi-Hänger Tests sofort abbrechen.** Keine 20 absichtlich provozierten Totalausfälle.

Anschließend:

- Mini-EPG-Layout und zukünftige Sendungen.
- Film- und Serienwidgets.
- Kompakte Live-Senderlogos mit Fokus-EPG.
- Globale Suche.
- Resume und Serien-Autoplay.
- Einmaliges Versions-Pop-up nach Update.
- Kodi-Neustart und Persistenzprüfung.

Alle Android-Testfälle initial als `NOT_TESTED` dokumentieren.

## 11. Verbindlicher Bestandsschutz

Diese Anforderungen sind ausnahmslos einzuhalten:

- **Box A vollständig unangetastet lassen.**
- Box B nicht deinstallieren oder downgraden.
- Keine Portale oder Konten zurücksetzen.
- Keine Gruppen, Favoriten oder Resume-Daten löschen.
- Keine vorhandenen EPG-Mappings überschreiben.
- Artwork-Profil **Dynamisch** beibehalten.
- Keine unaufgeforderte Cache- oder SQLite-Bereinigung.
- Keine USB-, SD-, SMB- oder Speicher-Migration.
- Kodi-Skin und bestehende Fernbedienungskonfiguration erhalten.
- Niemals private Portal-URLs, Tokens oder vollständige Kodi-Rohlogs in öffentliche GitHub-Issues aufnehmen.

Version `.41` muss vollständig kumulativ aus `.40` hervorgehen.

## 12. GitHub-Dokumentation und Lieferung

**Master-Issue:**

https://github.com/artattakk-creator/kodi-noodleprivate/issues/213

Codex soll nach Implementierung liefern:

1. Einen neuen **Draft-Pull-Request** für `.41`.
2. Vollständige Liste aller geänderten Dateien.
3. Root-Cause-Analyse je behobenem Fehler.
4. Zuordnung der Commits zu den GitHub-Issues.
5. Vollständige Host-Testresultate.
6. Reproduzierbare Regressionstests.
7. Ein installierbares Test-ZIP mit SHA256-Prüfsumme.
8. Android-Installations- und Abnahmeanleitung.
9. Übersicht noch offener Probleme und Risiken.
10. Nachweis, dass keine bestehenden Benutzerdaten migriert, gelöscht oder überschrieben werden.

**Alle tatsächlichen Reparaturen müssen nach Umsetzung im jeweiligen Issue dokumentiert werden.**

Ein erfolgreiches CI-Ergebnis darf niemals automatisch zum Schließen der Issues führen.

### Abschlussregel

Zuerst den **P0-Live-TV-Zurück-Hänger** dauerhaft beseitigen. Danach Mini-EPG, Widgets und die weiteren Regressionen korrigieren.

Der einmalige Versions-Pop-up ist eine verbindliche Anforderung der nächsten Version.

**Kein automatischer Merge nach `main`. Keine automatische Releasefreigabe. Erst Codex-Draft, Testpaket, Android-Abnahme und anschließend ausdrückliche Nutzerfreigabe.**