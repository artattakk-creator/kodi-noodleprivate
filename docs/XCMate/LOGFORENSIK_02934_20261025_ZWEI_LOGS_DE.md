# XCMate 0.1.29.34 – Vergleich zweier privater Kodi-Logs, 24.–25.10.2026

**Forensikstand:** 25.10.2026. **Gerät:** Kodi 21.2 Omega / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD.

**Datenschutz:** Die originalen Dateien `kodi.old(10).log` (121.345 Zeilen, 15,3 MB) und `kodi(20261025-072841).log` (6.163 Zeilen, 1,14 MB) sind **nur privat im Gespräch** ausgewertet worden, **NICHT auf GitHub hochgeladen**. Dieses Dokument enthält ausschließlich nicht-sensitive Codes, Zeilenpositionen, Zeitfenster, Kennzahlen und fachliche Schlussfolgerungen. **Keine** kompletten IP-/SMB-/Provider-/Artwork-/GitHub-Token-URLs, Zugangsdaten, echten Suchtexte, Stream-IDs oder Sitzungs-IDs veröffentlichen.

## 1. Versionstrennung und Vergleichsbasis

| Datei | Aufgezeichneter Zeitraum (Gerätezeit) | Versionen und Aussagegrenze |
| --- | --- | --- |
| `kodi.old(10).log` | **24.10. 12:42:43 – 23:28:15** | Kodi startet mit XCMate **.29**, Updates auf **.30 12:45**, **.31 16:10**, **.32 18:26** und **.33 21:49**. Kein `.34` in dieser Datei. |
| `kodi(20261025-072841).log` | **24.10. 23:28:38 – 25.10. 08:28:13** | Startet mit **.33**, XCMate **.34 wird erst 25.10. um 06:56:01** installiert (Zeile 3406). **Nur Zeilen ≥3406 als .34-Geräteevidenz** verwenden. |

**Vorsicht:** Eine Zeile `[XCMate][SEARCH] ... SEARCH_RESULT_READY` bedeutet nur *ein Ergebnisupdate*, **nicht**, dass ein für den Benutzer nutzbarer Live-Treffer gerendert wurde. Nur echte UI-Prüfung/Count beweist das. `EPG_PARTIAL` ist kein endgültiges Matching-Ergebnis.

## 2. P1 – Live-/EPG-Suchlatenz jetzt durch echte .34-Zeitspuren gestützt

**Positiv: Guide-Handoff aus PR #158 funktioniert.** Nach `.34` mindestens **drei** erfolgreiche `GUIDE_HANDOFF QUEUED → RESOLVER_REQUEST → DISPATCHED`-Folgen, Start **06:56:41 / 06:58:33 / 07:46:30**. Der große Guide→Suche-Hand-off funktioniert bei mehreren Versuchen:
- **07:49:30** `INTENT → GUIDE_CLOSED → WAIT_RELEASE → RELEASE_READY → ASYNC_READY → SEARCH_OPEN`, anschließend **07:49:33 `SEARCH_GUI_READY`**; Back/Schließen um **07:50:57**.
- **07:52:20** erneuter korrekter Guide→Suche-Handoff, **07:52:22 `SEARCH_GUI_READY`**; Back um **07:54:20**, `GUIDE_RESTORE` bestätigt.
- **07:57:10–07:57:12** dritter Guide→Suche-Handoff ebenfalls bis `SEARCH_GUI_READY`.

**Zeitlücken in aktiver Suchverarbeitung:**
- Im Suchlauf ab **07:52:22** tritt `SEARCH_RESULT_READY` **07:52:24.670** auf; dann **bis 07:53:58.752 kein weiterer solcher Commit** (**94,082 s**). Erst **07:53:58.191** erscheint der erste `SEARCH_EPG`-`EPG_PARTIAL`-Stand mit **25/2.764 Sendern**. Der Cursor-/EPG-Initialisierungspfad **vor dem ersten Slice** ist daher ein dringender Messkandidat; **nicht** beweisen, dass EPG-DB, TLS oder SQLite allein schuld sind.
- Im Lauf ab **07:49:33** erster `SEARCH_RESULT_READY` um **07:49:36** und erster `SEARCH_EPG`-`EPG_PARTIAL` erst **07:49:50**, also weitere **ca. 14 s** bis zum ersten Scan-Zwischenstand. Es kann bereits andere Tabs/VOD-Resultate betreffen.
- **07:57:13–07:59:59:** Live-Scan unter derselben Suchfenster-/Dispatch-Korrelation mit teils mehrfach auf **kleine `scanned`-Werte** zurückgesetzten Zählern (z. B. 22 → 12, 266 → 23), endet einmal bei **`READY, scanned=2764`**, **`programme_hits=1`**. Dies belegt echtes Programmtitel-Matching in einer vollständig durchgelaufenen Suchgeneration.
- **08:14:59–08:27:39:** ein weiteres lang geöffnetes Suchfenster; **08:15:19** erster EPG-Teilstand, wiederholte Zählerrücksetzungen nach Fokus-/Tab-Aktionen, u. a. **08:20:13 `scanned=23` → 08:21:48 `READY, scanned=2764`**. **Danach um 08:23:08 beginnt in derselben Suchfenster-/Dispatch-Korrelation erneut `EPG_PARTIAL, scanned=14`**. Ein vorher kompletter Katalogscan wird also sichtbar **wieder angestoßen**; möglicherweise absichtlicher neuer Tab-/Query-Anstoß oder unnötiger Re-Cursor-Aufbau. **Die Logs allein zeigen nicht**, ob der Benutzer ein neues Query angestoßen hat. UI-Tabwechsel und Reinitialisierung müssen getrennt instrumentiert werden.
- In vollständigen Scans wurden nur **108** bzw. **104** aktuelle Sendungstitel aus **2.764** durchlaufenen Live-Kanälen registriert; insgesamt wenige `programme_hits`. Das ist eine **Suchcache-/NowEPG-Snapshot-Kennzahl**, **keine verbindliche Aussage über die gesamte Provider-EPG-Abdeckung**. Fehlen echte Now-Daten, darf das Sendernamen-Ergebnis nicht warten.

**Ergebnis:** Die aktuelle Android-Geräte-Live-TV-Suche dauert laut Nutzer je nach Einstieg **ca. 60 s, 120 s und zuletzt gefühlte 180–300 s**. Insbesondere der **94-s-Commit-Abstand** und **wiederholte Full-Scans** passen zur gravierenden Latenz. Der reparierte Guide-Handoff ist **nicht** mehr der primäre Engpass.

**Codex-Diagnose/Fix ab .34/main:**
1. `media_search` / `search_data.LiveSearch.__init__`, `_now_events`, `LiveSearch.step`, `cached_short_guide`, `_search_load`, `_search_ready` **mit monotonic Phasenprofilen** prüfen: `QUERY_ACCEPTED`, `TAB_SELECTED`, `CURSOR_INIT_BEGIN/END`, `SQL_GUIDE_NOW_BEGIN/END`, `SHORT_EPG_CACHE_BATCH`, `SLICE_BEGIN/END`, `NAME_MATCH_READY`, `PROGRAMME_MATCH_READY`, `FIRST_USABLE_RENDER`, `SCAN_FINAL`, `QUERY_REPLACED` und `CANCEL_STALE`. Echte UI-Commitzahl & gezielten Live-Treffer-Zeitpunkt anonymisiert unterscheiden.
2. Bei Klick Live-TV-Tab nachfragen? **Nicht erforderlich:** mit Instrumentierung Re-Init-Ursache, Query-Fingerprint **nur anonym/generationbasiert**, Worker-Queue, SQLite-I/O und Cache-Hitzeiten beweisen. **Doppelte Vollscans derselben unveränderten Suchgeneration vermeiden**; korrekten Neuscan bei verändertem Query oder EPG-Revision zulassen. Sicheres Debounce/Cancellation der alten Generation, keine Ghost-Resultate, keine verlorenen aktuellen Now/Next.
3. Sendernamen-Treffer **sofort aus lokalem Live-Index** sichtbar/nutzbar rendern, Programmtitel aus aktuellen lokal indizierten EPG-Events inkrementell ergänzen, **kein pro-Kanal-HTTP im GUI-/IR-Pfad**. Der bestehende `LiveSearch.step` mit max. 64 Sendern/Slice und evtl. Short-EPG pro Sender ist ein nachzumessender Kostenpunkt, kein bereits endgültig bewiesener Root Cause.
4. **Abnahmetests:** Cold/Warm, Sendername vor / nach bewusstem Live-Tabwechsel, echter „Jetzt“-Titel, schnell aufeinander folgende Wechsel, gleiche Suche erneut ohne Änderung, Guide→Suche→Back und Senderstart. **Erstes nutzbares Ergebnis in Sekunden statt Minuten**, finaler Scan separat messen. **Unveränderte Suchmaske** laut [UI-FREEZE](SUCHMASKE_UI_FREEZE_02934_20261025_DE.md): Live-TV | Filme | Serien, Cover/Logo, Layout, Fokus, Back. Medien- und staffelübergreifendes Autoplay nicht anfassen.

## 3. P2 – Codec-Fehlerflut in alter .33-Sitzung (von .34 trennen!)

In **`kodi.old(10).log` unter `.33`** von **23:22:52 bis 23:27:17** wiederholen sich **55.785× `CDVDVideoCodecAndroidMediaCodec::GetOutputPicture dequeueOutputBuffer failed`** und **55.785× `GetPicture dequeueInputBuffer failed`**, gesamt **111.570 Fehler** in ca. **265 s** (~420 Logfehler/s). Der Kodi-Player beendet schließlich Video-/Audiothreads. Etwa 23 Sekunden nach Ende der älteren Logdatei startet die folgende Datei mit einem neuen Kodi-Prozess. Ob der Prozess wegen Decoderproblemen abgestürzt, geschlossen oder regulär neu gestartet wurde, ist **aus den Logs allein nicht beweisbar**.

**In der .34-Sitzung keine erneute massive dequeue-Fehlerschleife** (0 solcher Wiederholungsfehler). Es verbleiben sporadische Android `Open - null size`, `InstanceGuard locked`, `CMediaCodecVideoBuffer::ReleaseOutputBuffer`, `OutputPicture - timeout waiting for buffer` (9 Vorkommen) und mehrfach Kodi `EXCEPTION: Kodi is not playing any media file` nach Playback-Übergängen (**5 Vorkommen**). **P2-Kandidat für gezielte Hardware-/Playerstabilitätsdiagnose**, aber kein bewiesener XCMate-Serien-Autoplay-Fehler, kein Freibrief für Player-Rewrite.

**Sichere Nachverfolgung:** Welche Kodi-Playermodus-/Hardwaredecoder-Konstellation lag beim Fehler vor? Nur bei erneuter .34-Reproduktion anonymisierte Streamtyp-/Codec-/Container-Klassen, Decoder-/Player-Stop-/Resume-Ereignisse, Speicher-/Threadwerte, nicht URL oder Credentials. Vor allgemeinen Codec-Einstellungsänderungen Wiedergabequalität und Autoplay-PASS schützen. Optionale Rate-Limitierung wiederkehrender XCMate-Diagnostics darf Kodi-Core-Fehler nicht maskieren.

## 4. P2 – Xtream-Short-EPG-Timeout und geringe lokale Now-Abdeckung

**25.10. 07:00:12.769**, **Logzeile 3725**: `[plugin.video.xtreammate] Xtream API get_short_epg request failed: TimeoutError`. Das ist ein **echter XCMate-Fehler**, allerdings rund **49 Minuten vor** dem ersten analysierten Suchlauf um 07:49. **Keine zeitlich direkte Ursache** der dortigen 94-s-Lücke bewiesen. Prüfen, ob `epg_views`/Service die Short-EPG-Daten mit begrenzten Retries/Backoff verarbeitet und bei Ausfall ohne blockierenden UI-Zugriff auf XMLTV-/Provider-Cache ausweicht; EPG-Quellenpriorität und Mapping #98 getrennt.

Nur 104–108 aktuelle Titel in 2.764 komplett durchsuchten Kanälen zeigen **wenig nutzbare Now-Daten im konkreten LiveSearch-Snapshot**, nicht zwingend ein defektes gesamtes EPG oder fehlende XMLTV-Daten. Teste mehrere bekannte Kanäle und externe XMLTV-Zuordnungen getrennt, nutze echte Now-Events; kein simuliertes EPG.

## 5. P3 und externe Kodi-Fehler – nicht als XCMate-Codefehler fehlklassifizieren

| Meldung | Einordnung / sichere Maßnahmen |
| --- | --- |
| `repository.bingie`: altes Add-on-Repository-Schema / kein Kodi-21.2-Verzeichnis (nach .34 je **15** Meldungen pro Textvariante) | **Drittanbieter-Repository**, nicht automatisch fehlerhafter Titan BINGIE MOD-Skin. Repository-Metadaten/aktuelle sichere Bezugsquelle prüfen; kein unaufgefordertes Entfernen des Skins. |
| Mehrere weitere alte Repository-Definitionen (je 6× Schema-/HTTP-/Versionsfehler pro Klasse nach .34) | Nicht mehr kompatible bzw. unsicher über **HTTP** ausliefernde Drittanbieter-Repositories; benutzte Add-ons vorher prüfen, keine globalen Löschungen. |
| Vier `CCurlFile` HTTP-404 plus `CRepository failed read` nach .34 (07:56) | Kodi-Repo-Indizes veraltet/nicht erreichbar; **nicht** als kaputter XCMate-EPG-/TMDb-Poster-HTTP-Request interpretieren. Nur je Repo die abonnierte Index-URL und Sicherheit prüfen. |
| `ListItem.setInfo()` als deprecated (47 Warnungen ab .34) | Wartungsschuld; modern auf `InfoTagVideo` umstellen, **nur** mit UI-/Skin-/Metadaten-Regressionstests, sonst nicht P1. |
| `Skin has invalid include` / `unsupported control type 7` | Skin bzw. GUI-Kompatibilität bei Kodi 21.2 prüfen, fremde Skin-XML nicht im XCMate-Suchperformance-Hotfix ändern. |
| Einzelne `Trakt unauthorized` und TMDb-Helper-KodiDB-Fehler **vor .34** | Drittanbieter-Integration / optionale Authentifizierung, **kein** sicherer XCMate-TMDb-Poster-Fallback-Beleg. |
| Drittanbieter-Provider/DNS/Cloudflare-Timeouts **vor .34** | Separates Add-on-Problem, keine Root-Cause-Behauptung für die .34-Live-Suche. |

**Systemstabilität .34:** **88** `XCMate STABILITY`-Samples nach Versioninstallation: `rss_kib` **863.280–1.006.692** (ca. 843–983 MiB), `os_threads` **86–93**, `portal_oom=0`, `portal_read_errors=0`, `pressure=false`. Kein aus diesen Samples belegter OOM-/Threadleck-Crash. Speicher beobachten, aber nicht blind Caches löschen.

## 6. Entwicklungsprioritäten / Lieferung

**Priorität 1 – #140**: bis zu fünf Minuten Live-/EPG-Suchlatenz mit Fokus auf **94-s-Startlücke, mehrfachen Scan-Neustart, wiederholte 2.764-Kanal-Scans** und echte First-Usable-Result-Zeit beheben. **UI-FREEZE** zwingend; .34-EPG-Senderstart, Rückkehr, Film-/Serien-Suche, Poster und 7–8 Episoden staffelübergreifendes Autoplay unbedingt erhalten. In eigenständigem kumulativem Draft-PR ab aktueller main, Host-Tests, ZIP/SHA und Android-Latenzmessung; **kein autonomer Merge**.

**Priorität 2 – #17 / #88**: Infobar-EPG-Button zum **großen** Grid-Guide routen; **Links bleibt Mini-Senderliste**, Startgruppe und aktueller Sender korrekt fokussiert. Separate sichere Kodi-Owner-/Back-/LiveSession-Abnahme laut [Codex-Brief](CODEX_BRIEF_02935_LIVE_EPG_PERFORMANCE_ROUTING_DE.md).

**Priorität 3**: Short-EPG-Timeout / Codec-Stabilitätsbeobachtung und Kodi-21-/Repository-Hygiene; #111 Poster-/TMDb-Fallback und #98 manuelle EPG-Zuordnung weiter getrennt. Kein generischer Reset, Downgrade, Deinstallation, Profil-/XMLTV-/Artwork-Löschung oder Wiedergabe-Umbau.

**Schlussfolgerung:** Die Guide-/Playback-Reparatur der `.34` ist durch echte Log-Sequenzen bestätigt. **Die Suche startet, bleibt aber teils vor dem EPG-Cursor stehen und stößt nach bereits abgeschlossenen Scans erneut Fullscans an.** Daneben besteht ein getrennt zu beurteilendes Codec-/Drittanbieter-Repository-Warnbild. Eine technische Ursachenprüfung benötigt gezielte Code-Profilierung, keinen voreiligen Komplettumbau.
