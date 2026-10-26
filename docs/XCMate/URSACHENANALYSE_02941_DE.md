# XCMate .41 – Ursachenanalyse und Reparaturnachweis

Stand: 26.10.2026. Kumulativ auf main .40 `6c362a45582350c694e4e18c13581cd57cd31d70`, Merge #205 `c351e80010913eaad058aa7bac0cf37316a29f72`. Getesteter Quellstand edacc729a369ddcc867f090a55bb4b630265a5e4. Alle neuen Android-Gates NOT_TESTED. Keine privaten Rohlogs geöffnet/veröffentlicht; nur anonymisierte öffentliche Befunde aus Master #213 und Einzelissues gelesen.

## P0 #203 – synchroner Stop blieb trotz Python-Worker synchron

Der neue .40-Gerätebefund ist spezifisch: Back action92 um20:21:22 erkannt, USER_BACK live, PLAYER_STOP_START20:21:22.974, Kodi CloseFile/OnExit20:21:23.347/353, OutputPicture-Timeout20:21:23.514, Log-Ende20:21:23.842 ohne STOP_DONE; Neustart20:22:34. Das ist keine deaktivierte Rücktaste und kein Beleg für generell defekte Filmstarts.

**Belegter API-Vertrag aus Kodi21.3:** `xbmc/interfaces/legacy/Player.cpp::Player::stop()` ruft `SendMsg(TMSG_MEDIA_STOP)`. `ApplicationMessenger.cpp` setzt bei SendMsg(wait=true) ein WaitEvent und wartet auf die Bearbeitung im Kodi-Hauptthread. Einen Python-Thread davorzusetzen ändert diesen nativen Wartevertrag nicht. Das widerlegt die Annahme, ein zurückkehrender Python-Service allein garantiere einen nichtblockierenden Stop. Die vollständige native Audio-/MediaCodec-/Renderer-Deadlockkette ist ohne Kodi-Threadstacks weiterhin **nicht bewiesen**; insbesondere keine erfundene GIL- oder Treiberdiagnose.

`ModuleXbmc.cpp::executebuiltin(function,wait=false)` verwendet dagegen `PostMsg(TMSG_EXECUTE_BUILT_IN)`. `PlayerBuiltins.cpp` führt PlayerControl(Stop) über `g_application.StopPlaying()` aus. `GUIBuiltins.cpp` bestätigt SetProperty(...,home) als Main-Queue-Aktion. Gepinnter Commit **a3a448d26b8d560a65655dab2cd122994dc4e146**, Quellen/kleine Originalauszüge in [KODI_NATIVE_STOP_PROOF_02941.json](KODI_NATIVE_STOP_PROOF_02941.json).

### Implementierter Pfad

- [native_stop41.py:12](../../src/plugin.video.xtreammate/resources/lib/native_stop41.py#L12): Nochmals ausschließlich aktuellen own-Live-Token prüfen; feste `PlayerControl(Stop)`-Nachricht mit **wait=False** posten. Kein URL-, Token- oder Providertext im Befehl. VOD benutzt weiterhin den positiv beobachteten .40-Checkpoint-/Stop-Pfad.
- Danach eine zweite feste SetProperty-Nachricht mit neuem Hex-Jobnonce in **dieselbe FIFO-Warteschlange**. Diese kann erst nach Rückkehr von Kodis StopPlaying ausgeführt werden. Posting und früher onPlayBackStopped-/isPlaying=False-Zustand sind **keine** Abschlussbestätigung.
- [exit_jobs.py](../../src/plugin.video.xtreammate/resources/lib/exit_jobs.py): Quarantäne bis exakt passender Main-Queue-Barriere; kein Warten auf Player.stop im Python-Live-Worker, kein zusätzlicher Playerlock-Zugriff während Stop. Ein alter/falscher Nonce bestätigt nichts. Nach fünf Sekunden TIMEOUT, ohne Retry oder Home-Erfolg. Späte Barriere protokolliert LATE_NATIVE_RETURN und lässt den Timeout als fehlgeschlagen stehen. Auch ein Fehler beim Posten der Barriere nach möglicherweise bereits gepostetem Stop bleibt STOP_POST_UNCONFIRMED/quarantänisiert; niemals einen unklaren Post automatisch wiederholen.
- [live_exit.py](../../src/plugin.video.xtreammate/resources/lib/live_exit.py): Timeout bleibt ein fehlgeschlagener Exit, kein falsches STOP_DONE/HOME_REQUESTED. Normale Rückkehr erst nach bestätigtem Native-Return und tatsächlich beendeter eigener Wiedergabe; neue/fremde Session verhindert Navigation und fremde Announcement-Löschung.
- Traces enthalten festes Stage/Reason, Sessionhash, Thread-ID, monotone Millisekunden, Window-/Dialog-ID. Decoderwarnungen aus Kodi-Core getrennt korrelieren; keine privaten Streamadressen/Fehlermeldungstexte geloggt.

**Back bleibt unverändert aktiv:** Senderliste→blankes Video; Gruppen→Senderliste; Info→ausblenden; Optionen→Player; Player→Info; blankes Live-Video→ein eigener Stop/Return. Hosttests action92,20 Zyklen, Release, Fremdplayer, neue Sessions, falsche/fehlende/späte Barriere und unklarer Queue-Post. Keinen zweiten Stop durch Timeout auslösen.

### Praktische Grenze / Freigabegate

Das entfernt den belegten synchronen Python→Main-Wartepfad und beweist die geänderte Abschlusslogik. Der Stop läuft weiter in Kodis unveränderter Engine und kann einen unabhängigen nativen Treiber-/Rendererfehler nicht gewaltsam heilen. Kodi bietet hier kein atomisches „compare session token and stop“ und keine Rücknahme bereits geposteter Main-Nachrichten: Ownership wird unmittelbar vor Posting geprüft, neue XCMate-Starts werden gesperrt und eine spätere fremde Session nicht navigiert. Externe Playerwechsel und echte native Hängerfreiheit bleiben zwingende Android-Gates. **Nicht als dauerhaft Android-behoben oder produktiv freigegeben behauptet.** Erst1→5→20 sichere Gerätezyklen, bei Totalausfall sofort abbrechen.

## #202/#210 – positive .40-VOD-Probe erhalten

Film19:53:57 bis USER_BACK19:59:24 und PLAYER_STOP_DONE19:59:25 nach5m27s ist ein enger echter Teil-PASS. Der früher gemeldete Movies-Hänger bleibt mangels passendem Stack separat unklar; keine Gleichsetzung mit dem späteren Live-Hänger. `playback_exit.py`, `media_progress.py`, `media_autoplay.py`, `media_return.py`, `media_window.py`, `media_intent.py` und VOD-Decoder sind zu .40 bytegleich. Live hat einen eigenen neuen Dispatchzweig; VOD-Sample vor Stop, Resume/Gesehen und Autoplaycancel bleiben unverändert.

## #211 – zwei deckungsgleiche Textebenen

.40 füllt native ControlList mit vollständigen Zeit-/Titelzeilen und zeichnet an denselben Positionen weitere fünf Label/TextBox-Zeilen. Beide sichtbar, daher deterministische Überlagerung. [mini_epg.py](../../src/plugin.video.xtreammate/resources/lib/mini_epg.py) lässt die native Liste **sichtbar, aktiviert und fokussierbar**, füllt aber ausschließlich leere Zeilen und setzt beide Textfarben transparent. Nur eigene Zeitlabels und maximal zweizeilige TextBoxen zeichnen Text. Native D-Pad/Scroll/OK bleiben erhalten; eigenes Highlight ist unabhängig von NOW-Farbe. Kein unsichtbarer, unfokussierbarer Ersatzcontrol.

Ein eigener virtueller Fünfer-Viewport folgt der nativen Auswahl über5+ Programme; bei Hide werden alle eigenen Texte geleert. 720p/1080p, lange nichtlateinische Titel,20 Öffnen/Schließen und getrennte NOW/Fokus-Tests. Derselbe neue Einzeltextebenen-Test auf unverändertem .40-main FAIL, auf .41 PASS.

## #208 – History vor LIMIT verdrängte Zukunft

`guide_for_channel.events` enthält stop>now, der spätere Worker veröffentlichte aber unfiltrierte `programme_events` aus now−6h. Mini bevorzugte diese und begrenzte vor dem Zukunftsfilter auf256. Damit konnte eine zuerst korrekte Vorschau in History kippen.

- [local_epg.py:26](../../src/plugin.video.xtreammate/resources/lib/local_epg.py#L26): SQL-Untergrenze **jetzt**, nicht now−6h, bevor LIMIT greift. Selektierte SID behält den bisherigen Zukunftshorizont bis10 Tage, ohne Vergangenheit vor die Zukunft zu schieben. Großes EPG/Mapping/Quellenprioritäten nicht umgeschrieben.
- [mini_epg.py:6](../../src/plugin.video.xtreammate/resources/lib/mini_epg.py#L6): gültige reale Intervalle mit stop>now **vor Sortierung/Limit**, kein vergangenes Fallback als Jetzt.
- [tv_data.py:99](../../src/plugin.video.xtreammate/resources/lib/tv_data.py#L99): programme_events auch im Worker zeitgefiltert; neue Requestgeneration und Refresh-Seriennummer verhindern späte Veröffentlichung einer alten SID/Auswahl. Zeitrollover kann aus der größeren vorhandenen RAM-Programmliste neu berechnet werden.

Real-SQLite-Probe mit300 historischen Slots plus NOW/NEXT hält Zukunft trotz256er-Limit. Manueller Mapping-/Quellenvertrag und gleiche NOW/NEXT-Policy wie großes Raster erhalten. Zeitfilter-Replay auf .40 FAIL, .41 PASS. Keine EPG-Daten gelöscht oder neu importiert.

## #207 – interne Widget-Lesefehler unabhängig von Skinshortcuts

Reader.rail/page führte für12/24 Homekacheln vollständige DISTINCT-Counts, GROUP BY und eine Sortierung `added IS NULL,added DESC,ordinal` aus. Extrem knappe per-Query Budgets und mehrere parallele Skinaufrufe konnten dabei IndexReadError auslösen; die Logs enthalten keinen konkreten SQLite-Untercode. **Die individuelle Ursache der8–9-s-Androidaufrufe ist mangels Untercode weiterhin nicht rückwirkend festgestellt.**

[widget_data41.py](../../src/plugin.video.xtreammate/resources/lib/widget_data41.py) liest die bestehende Bibliothek mode=ro. Begrenzter SELECT ohne Vollkatalog-COUNT/GROUP/Expression-Sort, NULL liegt bei added DESC ohnehin hinten. IDs werden in einer maximal96er-Kandidatenmenge dedupliziert, Ausgabe12 Live bzw24 Medien. Startsender vorn und aktivierte Gruppen bleiben wirksam. Keine neuen Indizes/DDL in der Bibliothek; selected_categories ist TEMP im jeweiligen Reader.

Pro Anfrage insgesamt750-ms SQL-Budget, proStatement max250ms und max50ms Lockwait. Keine unendliche Retry-Schleife. Frische bestätigte Seiten15s gemeinsam pro Profil/Portal/Kind, Last-good bei Fehlern höchstens10min mit Policy-/Gruppen-/Startsenderprüfung. Cross-Interpreter-Dateilock vermeidet gleichzeitige gleiche Refreshes; konkurrierender Aufruf nimmt Cache oder verständliche fehlend-Zeile, kein Widget-Dispatchcrash. Ein bestätigtes echtes Leerresultat bleibt leer. Neues eigenes begrenztes Profil-JSON ist Metadatencache, keine Bildarchivierung/Migration. Defekter vorhandener Index wird nicht ersetzt, gelöscht oder neu aufgebaut.

Feste Diagnose `WIDGET41 kind/code/rows/stale/ms`: SQLITE_BUSY/LOCKED/CORRUPT/NOTADB/INTERRUPT oder BUDGET etc., keine rohe SQLite-Exception mit Pfad/URL. Hosttests mit echter Exklusivsperre, parallelem Dateilock, LKG, fehlendem/defektem Index, allen drei Quellen und20.005 Filmen. Messung ausschließlich Hostdaten, kein behaupteter kompletter Kodi-Home-Renderzeitgewinn.

## #206/#26 – versionierter optionaler BINGIE-Adapter

[Integrationspaket](../../integrations/titan-bingie-mod/0.1.29.41/README_DE.md): Include/Manifest für skin.titan.bingie.mod2.2.3, reservierte IDs90241–90243. Logo80×45 in160×90-Kachel ist50% der Kachelabmessungen; tatsächliche Alt-Skingröße auf Box B nicht gemessen. Kompakte Reihe, separate fokussierte NOW/NEXT/Uhrzeiten/echter Prozentbalken, zwei Posterreihen mit Fokus. Quellen bleiben die drei vorhandenen Add-on-Routen.

[widget_focus41.py](../../src/plugin.video.xtreammate/resources/lib/widget_focus41.py) hat nur dann eine Wirkung, wenn das **nicht automatisch gesetzte** Skinsetting xcmate41.adapter.enabled aktiv ist. Bounded RAM-Bank pro12 Sender, acht echte Events jeSender, maximal64KiB. Fokus wird nur aus dem eigenen Container gelesen, Uhrzeiten/Progress bis1Hz aktualisiert, kein SQL/HTTP/Popup/Tune pro Fokus. Bank höchstens1h gültig; danach ehrliches fehlend bis regulärem Widgetrefresh. Keine neue automatische Hintergrund-Netzquelle. Natürlicher Eventwechsel innerhalb der Bank getestet.

**BLOCKED für tatsächliche bestehende Home-Einbindung:** Ohne ausdrückliche Skinfreigabe wird nichts in fremde Home-/Include-Dateien kopiert oder aktiviert. Einbindeort, Platz, Schriftarten, IDs und reales Rendering müssen an der konkreten BINGIE-Kopie geprüft werden. Read-only Preflight prüft Version, XML und ID-Kollisionen; reversible Schritte und Dateien sind konkret vorbereitet. Kein funktionsfertiger installierter Skinadapter behauptet.

Externe Skinshortcuts-v2.1.0-getiterator-Fehler sind unabhängig. `.iter()` ist die Python3-API; `mismatched tag` benennt hingegen noch keine konkrete XML-Eingabe. Geprüfte öffentliche BigNoid-master-Version1.0.18/Python2 ist kein kompatibles Update. Offizielle Matrix-Metadaten nennen2.0.3/Python3, das ist kein ungeprüfter Austausch-/Downgradeauftrag für die installierte BINGIE-Fork2.1.0. Der externe Fix bleibt **BLOCKED bis konkrete kompatible Paket-/Eingabeprüfung und Freigabe**. Kein Monkeypatch, keine Neuinstallation oder Shortcutbereinigung.

## #209 – einmaliger tatsächlicher Updatehinweis

[update_notice41.py](../../src/plugin.video.xtreammate/resources/lib/update_notice41.py) liest installierte Version dynamisch aus xbmcaddon, vergleicht numerische Versionsteile und schreibt ausschließlich eigenes `xcmate_update_notice.json` im addon_data-Profil atomar. Keine Meldung bei gleicher Version oder bloßem Repository-Publish, keine Meldung beim Downgrade. Übersprungene Versionen führen einmal zur final installierten Version. OK **und Back** quittieren; zwei Neustarts wiederholen nicht. Fehlgeschlagene/noch nicht angezeigte Dialoge bleiben pending, zeitlich begrenzte Retryplanung; parallele GUI-Presenter sind gesperrt.

Neue Installation ohne verlässliche Vorgängerversion bekommt nur eine Baseline. Für den ersten echten .40→.41-Übergang ohne alten Notice-Marker wird vor dem ersten .41-Service-Diagnoseeintrag die vorhandene **persistierte eigene Servicebuild-Historie bis40** read-only als Vorgängerbeleg verwendet. Auf einer Altinstallation ohne diesen Beleg ist ein Upgrade von einer Erstinstallation nicht sicher unterscheidbar: dann konservative Baseline, keine erfundene Meldung. Die regulär laufende Box-B-.40 besitzt diesen Diagnosepfad; dessen echte Geräteprüfung bleibt Pflicht.

Service erkennt/plant nur ein RunPlugin. Der gesonderte Plugin-/GUI-Dispatch zeigt den nativen Dialog ausschließlich bei Kodi Home/Videos ohne Medium, Modal, Navigationlease oder Stopquarantäne. Keine Player.stop-/Window-Aktivierung zum Herstellen dieser Bedingungen. Aktiver Stream wird nie für die Meldung beendet. Noch nicht dargestellte Meldung bleibt über Neustart erhalten. Marker und begrenzte Widgetcaches sind die einzigen neuen Profildateien; keine vorhandenen Profileinstellungen ersetzt.

## Bestandsschutz und nachfolgende Arbeiten

Alle1.435 alten Methoden erhalten; neue Testfälle und exakte .41-Hunks separat. Originalicon/98 Themebilder,163 historische UI-Vertragsdateien, Suchmasken-XML und sechs Ergebnis-/Tabcontrols bytegleich zu .40. Player-/Resume-/Autoplay-/Portale-/EPG-Store-/Artwork-Modus-/Keymapmodule unverändert, kein Bibliotheks-/Guide-Schema geändert. .40-ZIP, Produktionsindex und Publish-Bedingung unberührt. Box A komplett ausgeschlossen, B bleibt Dynamisch; keine zusätzlichen Speicher-/USB-/SD-/SMB-/Migrations-/Löschtests auf Geräten.

Neue Roadmap-Anforderungen wie erweitertes Remote-Mapping #64 bleiben nach dem eingefrorenen #213-Auftrag separat; keine neuen globalen Keymaps, keine alten experimentellen Branches. Keine Downloads-/Aufnahmenreparatur. Kein automatischer Merge/Release/Install und keine Issue-Schließung vor Nutzer-/Android-Abnahme.
