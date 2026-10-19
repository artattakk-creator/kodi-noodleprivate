# XCMate 0.1.28 – Performance, EPG und UI: Implementierungsbericht

Stand: 19.10.2026. **Reviewkandidat, nicht veröffentlicht.**
Basis ausschließlich `main` **103646f98b21c27973a6a12316dca33c0378ecff**, produktiv **0.1.27**.
Branch `feat/xcmate-028-streaming-stability`. Add-on-ID bleibt `plugin.video.xtreammate`.
[Verbindlicher Auftrag](CODEX_AUFTRAG_028_PERFORMANCE_EPG_UI_DE.md) ·
[Android-Abnahme](ANDROID_TESTPLAN_028_DE.md).

PR #28 ist inzwischen durch `ad4606f` gemergt; seine letzten beiden CI-Läufe
[39283197699](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39283197699)
und [39282533858](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39282533858)
sind **erfolgreich**. Ältere Übergabeangaben „queued / produktiv 0.1.26“ sind historisch.
Issues #17, #25, #29–#35 samt Kommentaren wurden gelesen. Kein Issue pauschal geschlossen.

## A. Nachgewiesene Ursachen und Beweisgrenzen

1. `media_window._initial()` in 0.1.27 ruft `library_index.refresh()` für **Live, VOD und Serien** auf.
   Dieser Pfad deserialisiert globale JSON-Listen, bevor aktive Kategorien gefiltert werden.
   Mehrere Fenster/Dienstläufe können dieselbe Arbeit wiederholen. Der neue Fensterstart ist lokal
   und auf den angeforderten Typ beschränkt; kein Vollimport vor der ersten Ansicht.
2. Die 200.000-Grenze wird auf **Rohzeilen vor dem Gruppenfilter** angewandt und wirft ausdrücklich
   `ValueError`. HTTP-Gesamtkörper sind auf 80 MiB, die Bibliotheksdatei auf etwa 64 MiB begrenzt.
   Diese Fehlerpfade sind am Quellstand nachweisbar. **Der vollständige Android-Traceback fehlt**;
   dies beweist nicht, welcher dieser Pfade die konkrete Nutzerexception ausgelöst hat.
3. Der Medien-/Guide-Router beendet eine erfolgreiche Fensteraktion mit `endOfDirectory(False)`.
   Das meldet Kodi einen Fehler. Die neuen erfolgreichen Fensteraktionen melden nun Erfolg,
   bevor ein Modal geöffnet wird. Dass genau dies den Geräte-Fehlerton verursacht hat, bleibt
   ohne native Kodi-Aufzeichnung eine eingegrenzte Ursache, kein Hardwarebeweis.
4. Suche liest nur den vorhandenen lokalen Index. Fehlender Index und verschluckte SQLite-Fehler
   können wie null Treffer erscheinen. Jetzt: typisierte Lesefehler, echte lokale Trefferzahlen,
   fehlende/arbeitende/fehlgeschlagene Indizes, bedarfsgerechte Arbeitsaufträge und Wiederholen.
5. Im ersten großen Stresstest wurde eine weitere quadratische ID-Abfrage sichtbar. Der fehlende
   SQLite-Index `(pid,kind,sid)` ist ergänzt. Der vorherige Lauf wurde nach etwa zwei Minuten
   abgebrochen; er ist **kein erfolgreicher Vorher-Durchlauf**.
6. XMLTV verwendet bisher `datetime.strptime` im Worker und baut Ergebnislisten im RAM auf.
   Der neue SAX-Pfad verwendet numerische Zeitstempel, begrenzte Textfelder und SQL-Staging.
   Das vermeidet den lazy `_strptime`-Import sowie vollständige Ergebnis-/Dokumentbäume.
   **Die konkrete DE-TypeError-Zeile ist weiterhin unbewiesen.** Die öffentlichen Originalquellen
   Kaimandura, DE-EPGShare und AT-EPGShare lieferten aus dieser Cloud jeweils **HTTP 403**;
   aktuelle Originaldateien konnten deshalb nicht als erfolgreich geprüft ausgegeben werden.
7. Die alte generische DTD-Abweisung kann auch den üblichen XMLTV-Marker treffen. Der neue Parser
   akzeptiert ausschließlich den **inerten** Marker `<!DOCTYPE tv SYSTEM "xmltv.dtd">`, lädt
   keine DTD und verweigert interne/andere DTDs, Entitydeklarationen und unbekannte Entities.
   Syntax, unsichere Deklaration, Feld-/Tiefenlimit, GZIP und Transport erhalten getrennte Codes.
   Dies ist kein Nachweis, dass der AT-Feed genau diesen Marker enthielt.

## B. Neue Daten- und Dienstarchitektur

### Kataloge

- `utils.http_stream` / `network_io.decoded_chunks`: HTTP in begrenzten Lese-/Dekompressionsstücken,
  stdlib **und** optional httpx; kein vollständiger `bytes`-Körper für große Kataloge.
- `streaming_json`: inkrementelles UTF-8, strikte Array-/Objekt-/Endprüfung, höchstens 512 KiB
  je Objekt und 64 Verschachtelungsebenen. **Keine Obergrenze für die gesamte Sammlung.**
- `XtreamClient.iter_catalog`: Kategorieparameter direkt verwenden. Globale Alt-JSON-Dateien
  dienen nur als gestreamter Offline-/Upgrade-Fallback. Keine Voll-Deserialisierung zum Filtern.
- `library_index.import_group`: maximal 256 Zeilen je Stagingtransaktion; SQLite-Schlüssel statt
  unbeschränkter Python-ID-Sets. Erst nach vollständigem Dokument ein atomarer Generationswechsel.
  Unterbrechung/ungültiges JSON/ENOSPC lassen den bisherigen sichtbaren Kopf unverändert.
- Additive Tabellen im vorhandenen `library_v1.sqlite`; alte `titles` bleiben lesbar, bis ihre
  Kategorie erfolgreich ersetzt wurde. Logisch getrennte Portal-/Typ-/Gruppenindizes und
  Generationen. **Keine separate Migration oder Löschung** von Favoriten/Resume/Accounts.
- Grenzen schützen Arbeitsschritte. Die alten gesamten 200k-/64-MiB-Kataloggrenzen gelten nicht
  für den Streamingpfad. Freier realer Datenträger plus 32 MiB Sicherheitsreserve werden geprüft.
  Ein umfangreicher Vollindex kann mehrere hundert MiB oder mehr auf Disk brauchen; kein
  Versprechen, dass jeder Providerbestand auf jeden Stick passt.
- `catalog_sync`: persistierte, zusammengeführte Aufträge; ein Service-Importer, eine Kategorie
  je Scheduling-Schritt, sichtbare Kategorie vor Hintergrundkategorien. Angefangene Kategorie
  wird bei Neustart erneut geladen; fertige Kategorien werden weiterverwendet. **Kein HTTP-Range-
  Resume behauptet.** Lease/Generationen verhindern gleichzeitige Doppelimporte.
- Ignoriert der Provider `category_id`, wird die Antwort einmal gestreamt, nur aktive Gruppen
  gespeichert und bereits enthaltene Gruppen werden im selben Auftrag nicht erneut abgerufen.
  Die technisch unvermeidbare Übertragung deaktivierter Daten wird lokal verworfen, nicht indiziert.
- Manuelles „Katalog aktualisieren“ beendet jetzt den Directory-Request und stellt nur Aufträge
  ein. Es ruft keinen globalen synchronen Live-Katalog auf dem Plugin-/GUI-Pfad mehr ab.
- Erste undatierte Erfassung ist eine Baseline. Alte unbekannte Daten bleiben unbekannt;
  erst später neu entdeckte IDs erhalten einen First-Seen-Zeitpunkt. Neuheitenrails behalten
  weiterhin ältere/undatierte Füllkarten und die bestehende Anzahl-/Tagekonfiguration.

### Fenster und Suche

Fenster sofort mit lokalem Index/Status, keine Netzarbeit in Remote-/Fokusereignissen.
Sichtbare Gruppen werden priorisiert; ein begrenzter Beobachter übernimmt neue Generationen
auch ohne Neuöffnung. Noch nicht gestartete Fensterjobs werden abgebrochen, späte Resultate
nach Back/Close ignoriert. Favoriten/Resume bleiben separat. Suche kann bereits importierte
Gruppen vollständig paginieren und fehlende aktive Bereiche nachfordern. Ergebnisaktualisierung
ist ausdrücklich anwählbar; ein Fehler wird nicht als echte Nulltrefferzahl verborgen.

### EPG / Startgruppe

`xmltv_stream` → `stream_epg` → bestehendes `guide_v1.sqlite`:

- SAX, GZIP-Prüfung inklusive Trailer, begrenzte Feld-/Tiefenwerte, keine vollständige XML-/JSON-
  Kopie. Aggregate 80-MiB-/150k-/200k-Grenzen verhindern den neuen Xtream-Import nicht mehr.
- Nur aktive Sender nach expliziter ID/manueller Zuordnung bzw. eindeutigem normalisiertem Namen.
  Manuelle Zuordnungen gewinnen. Unbekannte/fremde Senderprogramme werden nicht persistiert.
- Quelle zunächst in SQLite-Staging validieren; Veröffentlichung atomar. Früherer Provider/
  externe Quellenvorrang bleibt; spätere Quellen ersetzen keinen vorrangigen Senderbestand.
  Kürzere erfolgreiche Feeds erhalten spätere gespeicherte Tage außerhalb ihres neuen Bereichs.
- Gemeinsamer kleiner Now/Next-JSON-Snapshot aus dem Tagesguide für vorhandene Resolver,
  Infobar, Senderlisten und Widgets. Der Tagesguide selbst bleibt vollständig paginiert.
- `startup_preload`: Startsender → erste 16 sichtbare Startgruppensender → restliche Startgruppe
  in Portionen → weitere aktive Gruppen. Begrenzte Short-EPG-Arbeit, Startsender zuerst;
  höchstens zwei nachfolgende parallele Abfragen, acht Sekunden HTTP-Gesamtbudget je Kurzabfrage.
- Kleine persistierte Sender-/EPG-/lokale Logosnapshots; kein Verbindungsaufbau zu Videostreams.
- Automatik prüft zusätzlich die **echte aktive 24h-Deckung im Tagesguide**. Der kleine
  Vier-Ereignis-Schnappschuss erzwingt keinen erneuten Download eines noch brauchbaren 10-Tage-EPG.
  Bestehendes Opt-in für schwere automatische Bulkdownloads bleibt bestehen. Ein expliziter
  Refresh bleibt möglich und meldet ein tatsächliches Ergebnis neben dem Anforderungsstatus.
- Quell-/Cache-/Zuordnungsdateien bleiben erhalten. Staging-/Disk-/Parsefehler erhalten die
  bisherigen Daten; Lesen eines vorhandenen Guide ist auch bei zu wenig Importplatz möglich.
- Diagnose enthält Klassifikation, bekannte Python-Datei/Zeile und Zahlen; keine Exceptiontexte,
  URLs, Tokens, Quellinhalte oder Zugangsdaten. Katalogfehler bleiben in `sync_status` gespeichert;
  EPG-/Live-Diagnosen sind nach Stop und Neustart vorhanden.

## C. Pre-Play und funktionaler Freeze

`live_overlay.py`, `player.py`, `live_recovery.py` und alle Remote-Module sind **bytegleich**.
Die sieben alten Routermethoden werden weiter per Original-AST geprüft, nach Entfernung
**ausschließlich dreier exakt definierter neuer Pre-Play-Guards** vor nativen Auflösungen.
Kein allgemeines Entfernen von Assertions oder Aktualisieren der alten Referenzhashes.

`play_intent` fordert beim Dienst eine vorbereitete `PrePlayDialog`-Anzeige an und wartet
höchstens eine Sekunde auf deren noncegebundene Bestätigung. Keine Player-Auflösung im
Datenworker. Der Dienst baut Controls **vor** `WindowDialog.show()`; kein künstliches `onInit`.
Back/Stop invalidieren die aktuelle Nonce und stoppen nur ihre eigene Session. Nach verifiziertem
Player-Match und lesbarer Player-Zeit schließt Pre-Play, der normale Navigator übernimmt.
`ConnectingNavigator` erbt die bestätigten Ereignis-/Fokusmethoden, verwendet beim warmen Tune
vor dem bestehenden `Player.play` dieselben Controls/Indexdaten für Info und Verbindungsstatus.
Während Verbindungsaufbau sind Pause/Seek/Optionsaktionen gesperrt, Back/Stop möglich.
Fremdvideo, alte Nonce, Abbruch und Timeout sind gesondert geprüft.

**Technische Grenze:** Bei fehlendem Dienst/Bestätigung wird die vorher funktionierende
Wiedergabe nach begrenztem Warten erhalten und `PREPLAY_SERVICE_UNAVAILABLE` protokolliert.
Dann wird keine erfolgreich gezeichnete Pre-Play-Leiste behauptet. Cloudtests beweisen die
Callback-/Handshake-Reihenfolge, **keinen Android-Frame, AV-Codec-Start oder Z-Order**.

## D. Sprache und Darstellung – tatsächlicher Umfang

- Neue XCMate-Menüs, Medien-/Guidefenster: eigene persistierte Wahl **Deutsch / English /
  Kodi-Sprache übernehmen** unter Einstellungen → Darstellung & Sprache → Sprache.
  Mitgelieferte Kataloge, englischer Fallback pro Zeichenkette, keine Änderung von Kodi-Sprache
  oder `lang_priority`. Ein verborgenes definiertes Kodi-Setting sichert die Persistenz.
- Bestehende deutsche Kodi-Installation bleibt ohne eigene Auswahl deutsch. Native Kodi-
  Einstellungs-/Systemdialoge folgen weiterhin Kodi. Alte fest codierte Live-/Legacytexte sind
  wegen Freeze nicht vollständig umgeschrieben: **keine Behauptung einer kompletten Übersetzung
  aller Altoberflächen**. Weitere Sprachpakete/Installer bleiben separate Aufgabe #29/#30.
- `appearance`: eigener Core-Bereich mit Hintergrund-/Panel-/Icondeckkraft, Hintergrund-/Akzent-/
  Fokus-/Text-/Sekundärfarben, drei kompatiblen Fontstufen, Vorschau, Übernehmen, Abbrechen,
  Standardwerte und atomarer Persistenz. Gilt für neue Medien-/EPG-WindowXML; Originale und
  Kontroll-IDs bleiben erhalten. Alpha wird über tatsächlich unterstützte `colordiffuse`-
  Texturattribute angewandt. Kleine Coverbeschriftungen bleiben bei Groß lesbar begrenzt.
- **Teilstand #31:** Skinfonts `font12/font13/font16`, keine erfundenen Pixelgrößen und keine
  universelle „sehr groß“-Garantie. Keine globale Kodi-Font-/Skinänderung. Die eingefrorene
  Live-UI wird nicht nachträglich eingefärbt. Optionale Themeinstallation/-deinstallation,
  vollständiger Theme-Resolver und weitere Farb-/Font-/Overlayoptionen sind **nicht fertig**.
  Es wird kein vorgeblicher Downloadknopf angeboten. Space Premium wird nicht installiert;
  der Nutzervorgabe 16/98 steht in diesem PR keine neue Grafikfreigabe gegenüber.

## E. Prüfstand, Paket und GitHub

**Finaler Codecommit:** `25b13736e68f12a46589d774b6ef86cd593c96a3`. **381/381 Tests bestanden**, null Fehler,
null übersprungene Tests, vollständige Suite auf dem final gebauten Quellstand in **55,173 s**.
338 Ausgangstests bleiben erhalten, **43 neue Regressionen**. Unmittelbar vorher ebenfalls
380 Tests vor/nach isoliertem Build erfolgreich; anschließend der zusätzliche AV-Readiness-Fall.
Neue Sicherheits-/API-/Fehlerassertionen sind nicht abgeschwächt, um CI zu erzwingen.

- Reale >80-MiB-HTTP-Antworten für **VOD und Serien**, je **200.005** vollständige Titel;
  Paging/Suche bis zum letzten Datensatz, Typtrennung und SQLite über dem früheren Disklimit.
- XMLTV **160.005** geparste Programme / **160.003** zum Testzeitpunkt gültig gespeichert;
  abgelaufene erste Intervalle werden korrekt nicht als aktuelle Daten gezählt.
- Offline/Abbruch/ENOSPC/kaputtes JSON/kaputte DB, Generationen, Datenverlustschutz,
  aktive/deaktivierte Gruppen, ignorierter Kategorieparameter, gruppenübergreifende doppelte ID,
  Baseline/First-Seen, manuelle Zuordnung, Quellenvorrang, kürzerer Guide, volle Platte lesbar,
  echte Tagesdeckung, Sprache/Persistenz/Alpha/Fonts, native Click-/Fokus-/Back-Reihenfolge,
  Pre-Play-ACK/Nonce/Foreign-Video/Timeout/Playerbereitschaft, unveränderter Live-Freeze.
- **26/26** bestehende Cache-/HTTP-/EPG-Tests zusätzlich unter System-Python mit httpx bestanden.
  Zwei zusätzliche echte Transportproben (urllib **und** httpx) für gestreamtes HTTP-GZIP,
  geteiltes UTF-8, JSON und Kategorie-Queryparameter erfolgreich; kein bloßer Mockdownload.
- Syntax, drei isolierte Add-on-ZIPs, Installerkopien und isolierte Index-MD5 bestanden.
  Nur die XCMate-Test-ZIP übernommen; Produktionsindex und andere Add-ons bytegleich zur Basis.
- Kodi-Tag [`21.0-Omega/Control.h`](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Control.h),
  [`WindowXML.cpp`](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/WindowXML.cpp) und
  [`GUIControlFactory.cpp:385`](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/guilib/GUIControlFactory.cpp#L385)
  für Konstruktoren, Fensterlebenszyklus, Fontauflösung und tatsächlich unterstützte
  `colordiffuse`-Texturattribute herangezogen. Strikte Constructor-/Dialogtests bestehen.

| Cloud-Messung (finaler Lauf) | Ergebnis | Vorher / Grenze der Aussage |
| --- | --- | --- |
| VOD: 200.005 Titel, 109.380.521 HTTP-Bytes | 23,350 s; SQLite 241.090.560 Bytes | Alter Gesamtpfad kann schon an 80 MiB / 200k / 64 MiB scheitern |
| Serien: weitere 200.005 Titel, 109.380.521 HTTP-Bytes | 23,182 s; gemeinsame SQLite 484.851.712 Bytes | Kein vollständiger erfolgreicher Altvergleich behauptet |
| Prozessspitze während Katalogtest | 47.416 KiB RSS (ca. 46,3 MiB) | Gesamter Testprozess, kein Android-RAM-Wert |
| XMLTV: 95.571.948 XML-Bytes / 160.005 Programme | 3,219 s; SQLite 199.876.608 Bytes | Neuer Streamingpfad; kein Alt-PASS oberhalb alter Limits |
| Kaltes Medienfenster im strikten Callbackmodell | 9,253 ms inkl. lokaler Testarbeit | Kein gezeichneter Frame / erstes echtes Poster / Hardware-Klickwert |
| Reale Statusleiste, Videostart, Senderliste, Suche, Back auf Android | **offen** | Vollständiges Messprotokoll im Geräteplan |

**Test-ZIP 0.1.28 / Dienstbuild 28:** [335286 Bytes, 106 Dateien](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.zip).
CRC erfolgreich und **jede Paketdatei bytegenau gegen die aktuellen Branchquellen** verglichen.
[SHA-256-Sidecar](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.zip.sha256):

```text
415055a9907711e35f0797e86e5ea528bdb0c7cf2da6060c47de14eb93cdfb9c
```

Maschinenlesbar: [TESTERGEBNISSE_028.json](TESTERGEBNISSE_028.json).
GitHub-CI wird mit dem Draft-PR angefordert; dessen aktueller Run wird gesondert verlinkt.
**Noch keinen CI-PASS für 0.1.28 behaupten**, bevor ein neuer Lauf abgeschlossen ist.
CI-ZIP-Zeitstempel können eine andere Paket-SHA ergeben; der eigene verifizierte Kandidat
ist die hier verlinkte Datei samt eigener Sidecar, kein ungeprüfter Binärvergleich mit CI.

**Freigabe:** Draft-PR und Test-ZIP, kein Main-Merge, kein Tag/Release, kein produktiver Indexupdate.
Andere Add-ons, BINGIE MOD, globale Keymaps, vorhandene Konto-/Mapping-/Fortschrittsdaten unverändert.
Android-Abnahme und aktuelle DE-/AT-Originalquellen bleiben Voraussetzungen für eine Freigabe.


## F. Geänderte Dateien

Die Runtime-/Testdateien des Codecommits (Paket/Übergabe separat):

```text
src/plugin.video.xtreammate/addon.xml
src/plugin.video.xtreammate/changelog.txt
src/plugin.video.xtreammate/resources/language/resource.language.de_de/strings.po
src/plugin.video.xtreammate/resources/language/resource.language.en_gb/strings.po
src/plugin.video.xtreammate/resources/lib/app_routes.py
src/plugin.video.xtreammate/resources/lib/app_services.py
src/plugin.video.xtreammate/resources/lib/appearance.py
src/plugin.video.xtreammate/resources/lib/catalog_sync.py
src/plugin.video.xtreammate/resources/lib/epg.py
src/plugin.video.xtreammate/resources/lib/epg_errors.py
src/plugin.video.xtreammate/resources/lib/epg_views.py
src/plugin.video.xtreammate/resources/lib/guide_store.py
src/plugin.video.xtreammate/resources/lib/guide_window.py
src/plugin.video.xtreammate/resources/lib/home_menu.py
src/plugin.video.xtreammate/resources/lib/import_budget.py
src/plugin.video.xtreammate/resources/lib/library_index.py
src/plugin.video.xtreammate/resources/lib/live_diagnostics.py
src/plugin.video.xtreammate/resources/lib/localization.py
src/plugin.video.xtreammate/resources/lib/main.py
src/plugin.video.xtreammate/resources/lib/media_window.py
src/plugin.video.xtreammate/resources/lib/network_io.py
src/plugin.video.xtreammate/resources/lib/play_intent.py
src/plugin.video.xtreammate/resources/lib/preplay.py
src/plugin.video.xtreammate/resources/lib/startup_preload.py
src/plugin.video.xtreammate/resources/lib/stream_epg.py
src/plugin.video.xtreammate/resources/lib/streaming_json.py
src/plugin.video.xtreammate/resources/lib/utils.py
src/plugin.video.xtreammate/resources/lib/xmltv_stream.py
src/plugin.video.xtreammate/resources/lib/xtream.py
src/plugin.video.xtreammate/resources/settings.xml
src/plugin.video.xtreammate/service.py
tests/test_repository_layout.py
tests/test_xcmate_027_data.py
tests/test_xcmate_027_localization.py
tests/test_xcmate_027_ui.py
tests/test_xcmate_028_streaming.py
tests/test_xcmate_028_ui.py
tests/test_xcmate_branding.py
```
