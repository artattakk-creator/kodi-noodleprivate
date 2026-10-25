# XCMate 0.1.29.35 – finale Android-Abnahme und Kodi-Logforensik
Stand: 25.10.2026 · Gerät: Kodi 21.2, Android TV 13, RK3528 ARM32, Titan BINGIE MOD, IR-Fernbedienung.

**Nutzerabnahme: 15/15 funktionale Tests PASS, 0 FAIL, 0 BLOCKED, 0 NOT_TESTED.** Nach dem vorherigen Zwischenstand von 14 PASS / 1 NOT_TESTED wurde **PERF-03 ausdrücklich zusätzlich als PASS** gemeldet. Dies ist eine **funktionale** Abnahme, keine uneingeschränkte Performance- oder EPG-Coverage-Freigabe. Die originale Gate-Liste steht in [ANDROID_ABNAHME_02935_DE.md](ANDROID_ABNAHME_02935_DE.md), historische Zwischenstände bleiben nachvollziehbar.

## 1. Versionssichere Logquellen (nicht öffentlich abgelegt)
- Zwei private Kodi-Logs vom 24./25.10.2026, insgesamt ca. 130.000 Zeilen. Rohlogs bewusst nicht veröffentlicht: enthalten möglicherweise lokale Pfade, Portal-/Stream-URLs und sonstige Identifikatoren.
- Älteres Log `kodi.old(20261025-100517).log`: 24.10. 12:42 bis 23:28, Entwicklung `.29`–`.33`. Hier liegen **111.570 alte Android-MediaCodec-Dequeue-Fehler** (55.785 Input + 55.785 Output); diese sind **nicht .35 zuzurechnen**.
- Neueres Log `kodi(20261025-100518).log`: 24.10. 23:28 bis 25.10. 11:04. `.34` erst ab **06:56:01**, `.35` **ab 10:40:23.346**. .35-Teil umfasst rund 2.100 Zeitstempelereignisse. Nicht jeden Kodi-Core-/Drittanbieterfehler als XCMate-Ursache deklarieren.

## 2. Gemessene .35-Suchzeiten aus `[XCMate][SEARCH_PERF]`
| Gesicherter einzelner Lauf | Zeitpunkt | Delta nach `QUERY_ACCEPTED` |
|---|---|---:|
| Sendername erstmals gefunden, 11 Zeilen | 10:45:01 | 1.273 ms = **1,273 s** |
| Senderliste erstmals gerendert, 11 Zeilen | 10:45:03 | 2.947 ms = **2,947 s** |
| Programmtitel erstmals gefunden, 1 Zeile | 10:51:08 | 27.781 ms = **27,781 s** |
| Programmtitel erstmals gerendert | 10:51:09 | 28.070 ms = **28,070 s** |
| Derselbe EPG-Suchlauf abgeschlossen (2.764 Sender) | 10:51:48 | 67.538 ms = **67,538 s** |
| Anderer Sendername erstmals gefunden, 6 Zeilen | 10:53:51 | 1.362 ms = **1,362 s** |
| Senderliste gerendert, 6 Zeilen | 10:53:51 | 1.808 ms = **1,808 s** |
| Hintergrundscan dieses Laufs abgeschlossen | 10:54:38 | 48.953 ms = **48,953 s** |

**Einordnung:** Name-first sichtbare Treffer binnen 1,8–3,0 s sind gegenüber früheren Minuten ein Fortschritt. EPG-Titel-Suche bleibt verbesserungswürdig. Nach `scanned=2764` laufen `EPG_PARTIAL`-/`SLICE`-Ereignisse und lokale Short-EPG-Anreicherungen weiter. Das bedeutet **nicht**, dass 130 vollständige 2.764-Sender-Scans stattgefunden haben. Es ist zu prüfen, welcher lokale Cache-Lookup, Worker oder GUI-Commit noch Fortschritt liefert. Nur geringe Anzahl aktueller Treffer in einem Snapshot beweist **nicht** die Gesamtqualität aller Quellen.

**Nutzerbeobachtung:** erster ungefähr erinnerter Jetzt-Titel „Lost … Files“ nicht gefunden; `MacGyver` nach merklicher Zeit gefunden. Exakter erster Titel, Source-ID und Zeitfenster noch unbekannt. Erst Nachweis eines lokalen EPG-Eintrags im großen Guide plus Abgleich gegen dieselbe Suchgeneration kann echten Suchfehler von unvollständigen Providerdaten trennen. Keine 100-%-Trefferquote behaupten.

## 3. Startkanal aus Menü und Info-/EPG-Navigation
- **Konkreter einzelner Menüpfad**: `DISPATCH_BEGIN` 10:54:45.256; `START_RESOLVER` 10:54:52.969; `DISPATCH_DONE` 10:55:02.023, `duration_ms=16767.3`; `VideoPlayer::OpenFile` 10:55:02.394. Also **16,767 Sekunden Dispatch** bis Plugin-Rückgabe, ca. **17,138 s bis OpenFile**. Log sagt bei der Dispatchaktion `OTHER`, daher exakten Menü-Start-Typ profilieren, nicht als hundertprozentig identifizierte Aktion ausgeben. **OpenFile ist nicht First Frame!** Ein einzelner Lauf ist kein P95-Nachweis.
- **Großer EPG aus der Infobar**: drei `LIVE_GUIDE REQUESTED → OPEN`-Paare mit **1,519 / 1,452 / 1,567 s**. Routing funktioniert, aber OPEN misst **nicht** `IR_OK→FIRST_INFO_VISIBLE` oder `LEFT→MINI_READY`: die vom Nutzer als langsam gemeldete Infozeile gesondert instrumentieren.
- **Startgruppenwahl**: wiederholt `selected_saved=1`, `start_found=1`, `start_in_group=1`, `category_star=0`, in der Startgruppe 8 Senderzeilen. Nutzer setzt GROUP-01/02/MINI-01 PASS. Drei Guide→Player-Handoffs QUEUED→DISPATCHED; keine neue .35-Guide-Senderwahl-Funktionsstörung berichtet.

## 4. Fehlerklassen nach .35
- **Vier Kodi-Core-`EXCEPTION: Kodi is not playing any media file`**, zeitnah zu Play-/Stop-Wechseln: mögliche ungeschützte Statusabfrage während transientem Playerzustand, **keine** bewiesene Fehlfunktion des funktionalen Senderwechsels. Status-Guards/Owner prüfen.
- Am Ende **doppelter `action=xcmate_home`-Routingversuch** nach `STOP_REQUESTED`, anschließend `GetDirectory`-Fehler. Verdacht auf doppelte Home-/Stop-Requests; Single-Flight/Router-Directory-Abschluss prüfen. Der Nutzer meldete dazu keinen gesonderten sichtbaren Fehler.
- Vereinzelt MediaCodec-/Buffer-/OutputPicture-Warnungen, aber **kein** historischer Dequeue-Fehlersturm. Kein Decoder-Rewrite auf Verdacht.
- **23 `STABILITY`-Samples**: RSS des gesamten Kodi-Prozesses ca. **928–988 MiB**, 89–102 Threads, `pressure=false`, `portal_oom=0`, `portal_read_errors=0`; **kein belegter XCMate-OOM**.
- Veraltete `ListItem.setInfo`-Hinweise; XCMate-eigene Stellen zur neueren Kodi-Metadaten-API prüfen, **nicht** andere Add-ons still ändern.
- `repository.bingie` (altes Kodi-Reposchema), mehrere andere veraltete Repos/HTTP-Downloadwarnungen: Drittanbieter-Thema, **nicht** der installierte Titan-BINGIE-MOD-Skin und **keine** belegte Ursache der XCMate-Suchlatenz. Keine automatische Deinstallation.

## 5. Priorität für Codex und Release-Gates
**P1:** (a) Programmtitelsuche und Short-EPG-Anreicherungsloops (#140/#127); (b) Startsender-Dispatch/First Frame (#120/#35); (c) IR→Infoleiste→Mini-EPG-Fokuszeit (#17/#35).
**P2:** Kodi-Playerzustandsabfragen, doppelte `xcmate_home`-Requests und Directory-Lifecycle (#75/#97 als historischer Kontext, #120/#17 als aktuelle Besitzer); nur aus gemessener Ursache.
**P3:** XCMate-eigene InfoTagVideo-Migration, kleine diagnostische Quellen-/Cache-Statusverbesserungen (#60/#58) ohne großen Mehrquellen-Merge.
**Erhalt:** 3-Tab-Suchmaske Live-TV/Filme/Serien, original Icon, Portal-/EPG-/Fokus-/Autoplay-Daten, jetziger Guide-Handoff, jetzt funktionierendes Gruppen-/Senderfokus-Verhalten. Kein Reset/Downgrade/Automerge.
**Getrennte Roadmap:** EPG Hub #161, vollhohe Rail Mini→Gruppen→Rail #94/#150, rechte Mini-EPG-Vorher/Jetzt/Danach-Spalte #95, Live- und VOD-OSDs, Genre-Suche #159 und Artwork #111 – nur nach Scope-/Risikoabstimmung.

Alle realen Gerätezahlen sind Einzelbeobachtungen und keine statistischen Median-/P95-Werte. Die Nutzer-Checkliste bleibt der maßgebliche Nachweis der 15 Funktions-PASS.
