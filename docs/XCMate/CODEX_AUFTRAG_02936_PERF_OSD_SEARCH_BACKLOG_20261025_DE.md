# CODEX – verbindlicher Folgeauftrag nach XCMate 0.1.29.35: Performance, Routing, Suchqualität und gezielte Rest-Issues

> **P0-COVER-NOTFALL AUF TESTBOX B (NEUESTER NUTZERBESCHLUSS 25.10.2026):** **Kein einziges Cover wird auf neuer Kodi-21.3-RK3528-Box geladen**. Das ist jetzt **MUSS in der laufenden regulären .36-Prüfversion**, nicht nur ein optionaler #111-Retry. [**Issue #168 – 0-Cover-Fehler und exakte Ursachen-/Abnahmematrix**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/168) ist verbindlich und hat für Artwork Vorrang vor altem "C2 optional". Codex soll **den bestehenden PR #163 / fix/xcmate-02936-stabilization auf aktuelles main aktualisieren**, die gesamte `media_art.request→art_store.enqueue→worker→fetch→READY→GUI`-Pipeline auf beiden Boxen prüfen, tatsächliches Dateisystem `free` gegen aktuelle 1024-MiB-Reserve/512-MiB-Limit, `media_art_paused`, Dienst/Queue/SQLite/MIGRATION/Netzwerk getrennt ausweisen; **nicht** ohne Befund physisch vollen Speicher unterstellen. Kein Reset/Deinstallation/Artwork-DB-Delete, kein globales Retry von 18k Jobs. **Alte .36-Hosttests 1214 PASS und altes ZIP/SHA auf PR-Head 656be1e sind VOR diesem Fix erstellt**, **neu testen und komplett neu bauen**, Android-Gates ART36-01..08 zunächst NOT_TESTED. `.36` enthält weiterhin Suche, Startsender, Infobar, Stop/Home, Genre UND funktionierendes Artwork; **Wizard-Draft PR #162 wurde ohne Merge geschlossen**, #43/#164/#165/#166/#167 bleiben regulär für .37. Keine eigenmächtigen Merges oder Paketerstellungen auf produktiver Box.


> **PARALLELE WIZARD-PRIORITÄT (jüngster Beschluss 25.10.2026):** `.36` behält den in diesem Dokument vereinbarten stabilen Performance-/Genre-Scope. **Parallel sofort** unabhängigen Draft für vollständigen **Erstinstallations-Wizard #43** beginnen und nachweisbares Test-ZIP nur auf leerer zweiter Android-Box mit neuem Kodi verwenden; siehe [parallel vorgezogener Wizard-/Neubox-Auftrag](CODEX_PARALLELAUFTRAG_WIZARD_NEUBOX_KODI21_22_20261025_DE.md). **`.37` wird vorrangig Wizard-Ersteinrichtung + offene `.36`-Reparaturen im gemeinsamen kumulativen Release**; UI Mini-EPG/Rechts/Jetzt und volle Rail sind entsprechend **`.38`**, Live-OSD **`.39`**, VOD **`.40`**, EPG Hub anschließend. Ältere Angaben im folgenden Text „.37 Rail/.38 Live-OSD“ sind **überholt**. [verbindlicher neuer Versionszug](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md) ist maßgeblich. Kein Wizard-Commit ungefragt in den laufenden `.36`-Branch, keine Veröffentlichung eines Preview-ZIPs im GS-Media-OTA-Index. Kodi 21.3 stabil und Kodi 22 RC1 nur als Prerelease auf separater Testbox; Bestandsbox nicht zurücksetzen.


> **NEUESTE VERBINDLICHE ANWEISUNG 25.10.2026 – [Release-Roadmap ab .35](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md) HAT VORRANG:** Jede Version enthält **neue Funktionen UND die Reparaturen aus der unmittelbar vorangehenden Android-Abnahme in EINEM kumulativen PR**. Für den nächsten Kandidaten `.36` ist **#159 Genre-Suche für Filme/Serien nun planmäßiger Feature-Bestandteil**, nicht nur beliebiger Optionalpunkt; **#111 Poster-Retry** soweit datensicher isolierbar ausdrücklich mitnehmen, riskanten Großumbau #111/#90 transparent als BLOCKED/nächste Version dokumentieren. Die Pflichtpakete B1–B4 bleiben bestehen. Alte Teilformulierung „C1 nur optional“ ist durch diesen neueren Nutzerbeschluss überholt. Danach `.37` Mini-EPG rechte Programmansicht PLUS vollhohe Rail **NACH der Sendergruppenebene**; `.38` Live-Player; `.39` VOD-Player. Android-FAIL der vorigen Version jeweils mit in den nächsten Feature-Kandidaten übernehmen. Keine automatische Merge-/Releasefreigabe.


**Nutzerentscheidung:** 25.10.2026: Jetzt an XCMate weiterarbeiten, die vollständige .35-Abnahme samt Kodi-Logs berücksichtigen, zusätzliche passende offene Issues mitbearbeiten und den Rückstand schrittweise abbauen. **Keine pauschale Änderung aller 50 offenen Issues in einem PR.**

**Repo:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on:** `plugin.video.xtreammate` · **Gerät:** Kodi 21.2 Omega / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD / IR-Remote.  
**Geprüft beim Auftrag:** `main` Add-on-Version **0.1.29.35**, PR #160 erfolgreich integriert. **Nächster Kandidat voraussichtlich 0.1.29.36**, aber vor Beginn `main`, aktuellen Repo-Index und offene PRs noch einmal prüfen. Die Versionsnummer darf nicht fest angenommene aktuelle Releases überholen oder überspringen; der PR baut **immer kumulativ vom dann aktuellen main-HEAD**.

**VERBINDLICH ZUERST LESEN:**
1. [Finale reale Android-Abnahme und versionsgetrennte Logforensik 15/15 PASS](ANDROID_ABNAHME_02935_LOGFORENSIK_FINAL_20261025_DE.md).
2. [Original-Android-Testkatalog .35 mit Schlussverweis](ANDROID_ABNAHME_02935_DE.md).
3. [Suchmaske: unveränderlicher UI-Freeze](SUCHMASKE_UI_FREEZE_02934_20261025_DE.md).
4. [Bereits beauftragte UX-Roadmap – Miniguide, Gruppen, Rail, Player, Genre](ROADMAP_NACH_02935_NAV_RAIL_PLAYER_OSD_20261025_DE.md).
5. [Zentraler EPG Hub #161 – separate mehrstufige Folgearchitektur](CODEX_AUFTRAG_ZENTRALER_EPG_HUB_QUELLENMERGE_20261025_DE.md).
6. [Issue-Triage und Release-Matrix nach .35](ISSUE_TRIAGE_NACH_02935_20261025_DE.md); die **aktuellen** Issue-States/Kommentare jederzeit auf GitHub überprüfen.

## A. Unantastbarer, auf Android **15/15 PASS** getesteter Bestand

`PERF-03` wurde inzwischen vom Nutzer ausdrücklich als **PASS** nachgemeldet: **15 PASS, 0 FAIL, 0 BLOCKED, 0 NOT_TESTED**. Kein Grund, die .35 rückwirkend als gescheitert zu markieren. **Aber:** 15 funktionale Häkchen sind weder vollständige Suchgenauigkeit noch Reaktionszeit-PASS.

**Schutzverträge:** bestehende 3-Tab-Suche `Live-TV | Filme | Serien` mit gleichen Labels/Positionen/Logo-/Cover-/Fokus-/Back-/Details-Funktionen **keinerlei UI-Redesign**; zuverlässiger `Infobar → großer horizontaler Guide`-Handoff; Vollbild Links→Mini-EPG, Links erneut→Sendergruppen; großer EPG öffnet gespeicherte Startgruppe und markiert Startsender, Mini markiert tatsächlich laufenden Sender; Guide→Senderwechsel/Back ohne Kodi-Home oder schwarzen Bildschirm; Film-/Serien-/Staffel-/Episoden-Suche; über Nacht bestätigtes staffelübergreifendes Autoplay/Resume. **Original-XCMate-Icon und Space-Premium-/Standard-Skin-Assets, Portale, XMLTV-Quellen, manuelle Mappings, Favoriten, Gruppen-Checkboxen, Startgruppe/Startsender/LiveSession, Poster, lokale SQLite-Bestände bleiben erhalten.** Keine Deinstallation/Downgrade/DB-Löschung/Cache-Purge; keine globale Kodi-Keymap.

## B. MUSS-Umfang des nächsten kleinen kumulativen Stabilisierungskandidaten

### B1 – #140/#127: EPG-Programmtitelsuche / Enrichment-Workloops

**Harter Android-.35-Nachweis:** Sendernamen-Treffer sichtbar nach **2,947 s** und **1,808 s**. Echte laufende Programm-Titelsuche: **27,781 s bis erstem Treffer, 28,070 s bis sichtbarem Treffer, 67,538 s bis `SCAN_FINAL`** mit **2.764 Sendern**. In anderem Namen-Suchlauf `SCAN_FINAL` nach 48,953 s, wobei der nutzbare Name **bereits nach 1,808 s** sichtbar war. Anhaltende `SLICE/EPG_PARTIAL`-Events bis weit nach dem initialen Katalog. **Nicht** vorschnell als dutzende volle Neuscans klassifizieren; mögliche Short-EPG-Cache-Ergänzung, noch ungemessene Generations-/Enrichment-Semantik.

**Codex umsetzen:** mit `time.monotonic`, anonymen Query-Generationen, vorhandenen `SEARCH_PERF`-Markern Pipeline in `INDEX_QUERY_DONE`, `NOW_LOCAL_MATCH`, `ENRICHMENT_STARTED`, `CACHE_BATCH_DONE`, `NO_PROGRESS_STOP`, `VISIBLE_FIRST_PROGRAMME`, `FINAL` aufschlüsseln. Korrekte Titel aus **bereits lokalem Now-EPG** direkt und effizient abfragen (bei Bedarf DB-Suchindex/normalisierte Titel, geschützt migrieren); deduplizieren, provider-/channel-/source-genau. Keine synchronen Provider-Calls, Quelle-Reimports oder pro-IR-Hover-/Suchaktion vollen Kanalscan. **Die schnelle Sendernamensuche darf nie auf den abschließenden Short-EPG-Anreicherungsdurchlauf warten.** Ein leerer oder stale Cache muss zu sauberem Nicht-Treffer bzw. Ergänzung im Hintergrund führen, nicht 60 s GUI-Blockade. Kein UI-Layout-Fix!

**Nutzerbeobachtung:** Ein nur ungefähr als „Lost … Files“ erinnerter echter laufender Programmtitel wurde nicht gefunden; `MacGyver` wurde gefunden. **Kein exakter erster String/Zeitslot/Feed nachgewiesen.** Repro-Fixtures für *im Guide vorhandener Now-Titel → globale Suche exakt gleich* und *Guide enthält Event nicht → kein falscher Treffer*; Kanalalias und Quell-Revision vergleichen. Nicht behaupten, 100 % aller Sender hätten EPG. [EPG Hub #161] erst später umfassend mergen.

**Gate:** Name weiterhin kalt/warm in Sekunden; aktueller **lokal belegter** Programmtitel bei 2.764 Sendern merklich schneller als 28 s, Engineering-Ziel erster Suchtreffer **unter 10 s** auf der Box, genauer Android-Wert Pflicht; kein UI-Stottern/alt-query Ghost-Resultate.

### B2 – #120/#35: Startsender aus Menü und langsamer Live-Start

Ein beobachteter `DISPATCH_BEGIN` um 10:54:45.256 → `START_RESOLVER` 10:54:52.969 → `DISPATCH_DONE duration_ms=16767.3` 10:55:02.023 → `VideoPlayer::OpenFile` 10:55:02.394. **Achtung: geloggte Route `action=OTHER`, der Nutzer beschreibt den Menü-Start; noch keine endgültige Action-Identität. `OpenFile` ist nicht FIRST_FRAME, und nur ein Lauf ist bekannt.**

Codepfad Portal/Katalog/LiveStart-Session/Resolver/Kodi Player einzeln messen `IR_MENU_CLICK`, `ROUTE_ACCEPTED`, `START_SID_RESOLVED`, `PORTAL_REQUEST_BEGIN/END`, `PLAY_INVOKED`, `PLAYER_STARTED`, `FIRST_VIDEO_DETECTED`. Cold-/Warm- und Wechselstart vergleichen, bevorzugt cached Startsender-ID/aktivierte Gruppe, keine Vollkatalog-Synchronisation auf UI-Thread. Bereits erfolgreiche Back-/Guide-/Autoplay-Funktionen erhalten. Keine kosmetische BusyDialog-Timeout-Erhöhung.

### B3 – #17/#35: träge OK-Infobar und Übergang zu Mini-EPG

Der Nutzer meldet **spürbar langsame Reaktion von IR-OK zur Infoleiste und weiter zum Mini-EPG**. Das funktionierende Infobar→großer EPG-Routing zeigt nur `LIVE_GUIDE REQUESTED→OPEN` **1,519 / 1,452 / 1,567 Sekunden**; es misst **nicht** OK→Info sichtbar. Deshalb separates Timing `REMOTE_ACTION_RECEIVED → LIVE_NAV_READY → INFO_WINDOW_VISIBLE → MINI_CHANNELS_VISIBLE`, Erstöffnung/Warm-Reopen und während Streambuffer; Service-Queue, WindowDialog-Aktivierung, lokale EPG/GroupIndex-Reads und evtl. blockierende Aktionen profilieren.

**Fix:** Infoleiste mit bereits lokal gespeicherten Sender-/NowNext-Werten **sofort sichtbar** machen und langsamere nichtkritische Datenteile inkrementell im Hintergrund ergänzen, Mini-Senderliste ohne vollständigen Guide-Rebuild; Fokus behalten; keine Fake-Jetzt-Titel. Kontext der zwei OK-Ebenen und der Links-Kette erhalten. Keine vorzeitige komplette Player-OSD-Optikänderung.

### B4 – #75 / geschlossene #97 als Vorgeschichte: idempotentes Stop-/Home-Routing und Playerstatus

Im .35-Log **vier** Kodi-Exceptions `Kodi is not playing any media file` nahe Play/Stop, ohne dass die Android-Senderwahl durchfiel. Nach Live-Stop gegen 11:04 zwei `action=xcmate_home`-Dispatches und ein `GetDirectory`-Fehler. **Potenzielle Race/Doppelroute, nicht als auf Gerät bestätigten Crash darstellen.**

**Fix nach reproduziertem Kontext:** Kodi-Playback-Statusabfragen nur im legalen Session-/Player-State + Exception-Guard; kein Schutz, der echte Fehler verschluckt. Stop-/Back-/Home-Routing anhand SessionNonce/SingleFlight und WindowDialog-Owner idempotent; genau ein Kodi-Directory-Abschluss nach angeforderter Route; fremde Kodi-Player unberührt, kein automatischer Startsender bei Stop. Testerprobe 20× Stop/Back/Home und Overlay öffnen/schließen, Kodi-Home-Rücksprung nur bei bewusst gewähltem Exit. #97 bleibt geschlossen, keine automatische Wiedereröffnung; #75 als diagnostisches Follow-up bis überprüft.

## C. Sinnvolle KLEINE zusätzliche Issues, aber nur hinter explizitem Scope-Gate

**C1 – #159 GENRE-SUCHE (empfohlen, getrennt committet):** Film-/Serien-`genre` ist im existierenden `library_index.py`-Payload vorhanden; bisher suchbares Feld nur Titel. `Sci-Fi / Science Fiction / Western / Thriller` soll bei **nachweisbar vorhandenen Genre-Metadaten** im gleichen bestehenden Film-/Serien-Tab Resultate anzeigen, mit konservativen Aliasen, Titel vor Genre, keine Dubletten, keine frei erfundenen Genre-Kategorien. Suche *indexiert* und ohne erneute Sekunden-/Minuten-Regression, SQLite Migration ohne Nutzerdatenverlust. **Nur wenn isoliert vollständig hosttestbar; ansonsten eigener direkt folgender Draft-PR**, nicht ein halbfertiger Genre-Fix im Kern.

**C2 – #111 POSTER-RETRY (optional, isoliert):** Einzelne VOD-Filme verlieren Poster und zeigen „Poster Netzwerkfehler“. Aktuell offener **historischer Draft-PR #157 ist nicht aktuelle main-Basis**, nicht direkt mergen. Im aktuellen main Provider-/TMDb-Poster-Status prüfen, sauber zwischen `NOT_FOUND`, Timeout, HTTP-403/429, Cache-/Speicherkonflikt differenzieren; begrenzter asynchroner Retry und manueller erneuter Versuch, nie 18.000 bestehende READY-Assets löschen oder Warteschlange global auf null setzen. **Nur wenn klein und nachweislich ohne #90/#69/#106/#108 Artwork-Migrationsprobleme lösbar**; andernfalls separater Nachfolger und #111 OPEN.

**C3 – #60/#58 EPG-Qualitätsdiagnostik (klein, kein neuer Merger):** Im bestehenden EPG-Status **getrennte** Kennzahlen für XMLTV-Mapping, tatsächlich verfügbares Now/Next, Short-EPG-Cache und fehlende Quelle/Fallback. 2.764 Sender und ~87–120 Now-Events im einzelnen Suchsnapshot sind **keine** Aussage, dass alle Quellen nur so viele Programme besitzen. Kleine lokale Analyse ohne UI-Redesign, reinen Status nicht als Datenänderung verkaufen. Umfangreiche Quell-IDs, 7-Tage-Historie, wirkliche zeitintervallbasierte Fusion, Konflikt-Merger und manuelle Mapping-UI bleiben im eigenständig beauftragten **#161/#98**. Keine riskante EPG-DB-Duplikation.

**C4 – #91 SQL/Cache-Hygiene (nur durch Logmessung):** Ein klar nachgewiesenes `SQLITE_BUSY`, unnötig angeforderter Cache-/Worker-Neuaufbau oder blockierter Query darf behoben werden, aber **SQLite-WAL/Lese-/Transaktionssicherheit und Medien-/EPG-Datenintegrität** nicht deaktivieren. Kein pauschaler Threadpool-/Timeout-Tuningblindflug.

**C5 – Kodi-21.2 InfoTagVideo:** Wo **eindeutig XCMate-eigene** `ListItem.setInfo`-Deprecations verursacht werden, minimal migrieren, ohne Metadaten/Postertest/Fokus zu stören. Keine Drittanbieter-Skin-/Plugin-Rewrites.

**Scope-Regel:** Pflichtpaket B ist Merge-Gate. **C1–C5 sind einzeln überprüfbar und dürfen weder B verzögern noch den kumulativen PR instabil machen.** Falls mehr als zwei unabhängige C-Fixes sinnvoll sind, separate kleine Folge-PRs auf jeweils aktueller main-Basis, keine Merge-Stapel auf veralteten Drafts.

## D. Explizit NICHT unbemerkt in den Stabilisierungskandidaten ziehen

- **#94/#95/#150** – bereits freigegebene **nächste UX-Phase**: **Live → Links Mini-EPG → Links Sendergruppen → Links bildschirmhohe vertikale Rail**, mit gleichmäßig über volle Bildschirmhöhe verteilten Icons; Mini-EPG **zweispaltig**, rechts immer chronologische echte „vorher | JETZT | danach“-Programmliste des links markierten Senders, Rechts-Fokuswechsel. **Hohe Produktpriorität direkt nach Stabilisierung!** Nicht durch endlose Hotfix-Iterationen verdrängen. Visueller TV-Sketch + echte IR-Abnahme.
- **#17/#100 Live-Player-Design und #79 Film/Serien-OSD**: richtige große fernbedienbare Playback-/Ton-/Untertitelbuttons, aber getrennte folgende kumulative UI-PR(s), Schutz Kodi VideoPlayer und staffelübergreifenden Autoplay.
- **#161 EPG Hub**: evolutionäre `guide_v1.sqlite`, Quellenintervalle, 7 Tage vergangene belegte EPG-Ereignisse, echte Zukunft, Quelle-ID-Konflikte, atomare Leser-Snapshots, echter Index; **umfangreich, eigene Migrations-/Android-Phasen**. Keine pauschale 7-Tage-DB-Migration im kleinen Fix.
- **#62/#63/#126/#135/#136** Aufnahmen/Downloads/Redirect/USB/SMB als eigener zusammenhängender Storage-/Streaming-Workstream, nicht halb mit Such-Patch reparieren.
- **#90/#69/#106/#108/#115** Artwork-Space-Premium/Queue/Migration als eigenes risikobegrenztes Subsystem; #111 darf höchstens lokalen sicheren Poster-Retry aufgreifen.
- **#102** Vollständiges Scrolling/24-Titel-Limit und Gesamttitelzähler in Film/Serie: im folgenden Medien-UI-/Katalog-Vollständigkeits-Release priorisieren, nicht still als durch REG-01 erledigt schließen.
- **#19** Lizenz-/Provenienz-Audit verpflichtend V2-Gate, **nicht wegen CI-Tests oder funktionaler Android-PASS als erledigt markieren**.
- Drittanbieter-Kodi-Repositories mit veralteten Formaten/HTTP sind **keine** XCMate-Code-Fehler. Nur gesonderte sichere Nutzerempfehlung, keinesfalls Add-ons entfernen.

## E. CI / Android-Abnahme (neue Gate-Tabelle – bei Draft alle NOT_TESTED)

| ID | Was muss real funktionieren? | Initial |
| --- | --- | --- |
| S36-01 | Gleicher Sendername in globaler Live-Suche weiterhin erster sichtbar bedienbarer Treffer in Sekunden, keine alte Query nach Tabwechsel | NOT_TESTED |
| S36-02 | Im Guide belegter jetzt laufender Titel kommt korrekt und deutlich schneller als 28,070 s als Live-Treffer, Quellzuordnung stimmt | NOT_TESTED |
| S36-03 | Wiederholtes Suchen, Querywechsel, kein endloser `EPG_PARTIAL`-Loop; Abbruch von stale Generationen, Original-3-Tabs/Fokus unverändert | NOT_TESTED |
| S36-04 | Kalt-/Warm-Menü-Startsender mit gemessenen Phasen und erstem Video, keine ungewollte Startkanal-Änderung | NOT_TESTED |
| S36-05 | IR OK→Info tatsächlich sichtbar und Links→Mini-Liste deutlich reaktionsschneller, jetzt/danach ehrlich, Fokus korrekt | NOT_TESTED |
| S36-06 | OK/Info→EPG öffnet großen Guide, Back/Receiver/Zapping mindestens fünfmal unverändert | NOT_TESTED |
| S36-07 | 20× Live-Stop/Back/Home ohne erneuten Startkanal, Doppel-Dispatch, fremden Playerstop oder Kodi-Directory-Fehler | NOT_TESTED |
| S36-08 | Film-/Seriensuche, Cover, Staffeln/Episoden/Resume/Autoplay bis Episodenübergang erhalten | NOT_TESTED |
| S36-09 | Aktivierte Startgruppe, Guide-Default, Mini-Aktuell-SID und Gruppencheckboxen erhalten; EPG-Quellen/Mappings unverändert | NOT_TESTED |
| S36-10 | **Falls C1 enthalten:** Sci-Fi/Western trifft Filme/Serien auch nur via belegtem Genre, Titelpriorität, kein UI-/Speed-Regress | NOT_TESTED / nur falls enthalten |
| S36-11 | **Falls C2 enthalten:** Poster-Fehler gezielt retrybar, READY-Poster/Caches intakt, Offline/Timeout führt nicht zu GIF-Spam oder DB-Reset | NOT_TESTED / nur falls enthalten |
| S36-12 | **Falls C3–C5 enthalten:** EPG-Status/DB-Integrität/Metadaten-Normalität, kein Background-OOM oder neuer Kodi-Core-Decoderloop | NOT_TESTED / nur falls enthalten |

## F. Liefervertrag und Issue-Abbau

1. **Preflight** vor Code: `git status`, `main HEAD`, `addon.xml` Version, repo-`addons.xml`, offene PRs und Issues. Vorhandene alte Branches **nicht** zu Implementierungsbasis machen. Draft #157 und die alten PRs #50/#84 usw. nur **portierbare Referenzen**, kein Downgrade- oder Paket-Mix.
2. **Mehrere nachvollziehbare Commits**: A Suchpipeline; B Startsender; C Info/Overlay; D Home/Player-State; danach je ein optionaler isolierter Fix C1..C5.
3. In **Draft-PR** echte Root-Cause-Vorher/Nachher-Timings mit anonymem `generation`/Session, Host-Testlauf + Ergebnisanzahl und CI; Paket `plugin.video.xtreammate-0.1.29.36.zip` (falls tatsächlich nächste Version), SHA256, Dateikatalog und dokumentierte sichere Migrationen. **Keine Android-PASS behaupten**, bis Nutzer Tests auf RK3528 durchgeführt hat.
4. **Issue-Abnahme statt kosmetischem Schließen**: Jedem relevanten Issue (mind. #140, #120, #17, #35, #75, #159 optional, #111 optional) einen Subtask-Diff und Test-Gate zuordnen; nach PR bei Bedarf Zustandskommentar. **Erst dann schließen**, wenn **alle noch offenen Akzeptanzkriterien des gesamten Issues** nach realem Test erfüllt sind. Bei breiten alten Issues erfüllte Teilaspekte dokumentieren, Rest in eigenem Folge-Issue offen halten; nichts rückwirkend als bestanden markieren.
5. **Keine eigenmächtigen Merges/Repository-Publishing, kein ZIP auf Android installieren, kein Cache/DB/Profile/Theme-Reset.** Der Nutzer entscheidet nach Review und Gerätetest. Neuere GUI-Phasen in der Roadmap bleiben zwingend.
