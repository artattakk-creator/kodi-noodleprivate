# XCMate 0.1.29.39 – Android-Abnahme

Stand: 26.10.2026. Testkandidat, kein Release. **Alle neuen Android-Gates NOT_TESTED.** Historische .38-B-01–B-15-PASS gelten nicht als .39-Abnahme; sekundäre Fehler #185–#192 bleiben bis zum realen Test offen.

**Box A ist vollständig ausgeschlossen:** kein Update, kein Eingriff, keine Inventur-/Migrationsprüfung in diesem Zyklus. Box B: Kodi21.3, ARM32/RK3528, Titan BINGIE MOD; Artwork bleibt Dynamisch. Keine zusätzlichen USB-/SMB-/SD-, Speicher-, Kopier-, Migrations-, Lösch- oder Massendownloadtests. Die Host-Suite nutzt ausschließlich temporäre Fixtures.

## Start und Protokoll

Der Benutzer prüft ZIP/SHA256 und installiert .39 bei Bedarf als normales Add-on-ZIP-Update auf B. Keine Deinstallation, kein Downgrade, kein Profil-/Cache-Reset. Version kontrollieren; Modus, vorhandene Widgets und Verknüpfungen beibehalten. Die bestehenden drei Widget-Routen stehen in `WIDGET_ADAPTER_02939_DE.md`; keine Skin-Dateien bearbeiten.

Je Gate `PASS`, `FAIL` oder `NOT_TESTED`, Dauer und kurze Beobachtung eintragen. Box A bleibt `BLOCKED_BY_USER_PROTECTION`. Bei fremdem Player-Stop, Kodi-Hänger, Profilverlust oder unerwarteter Modusänderung abbrechen. Einen nicht verfügbaren Stream/Untertitel oder nicht reproduzierten sporadischen Fehler nicht als erfolgreich getestete Funktion ausgeben. Keine Rohlogs veröffentlichen; nur bereinigte feste Eventcodes, Fenster-/Dialog-/Action-IDs und Zahlen aus UI39/OSD39/SEARCH_PERF/PLAYER_EXIT verwenden. Kodi-Core- und Fremd-Add-on-Meldungen getrennt bewerten.

## Kurzer erster Durchgang

Zunächst W39-01, I39-01, V39-01/02, N39-01, A39-01 und S39-01 prüfen. Danach die Wiederholungs- und Langzeitgates. Diese Reihenfolge ersetzt nicht die vollständige Abnahme.

| ID | Handlung und PASS-Kriterium | Box B |
|---|---|---|
| W39-01 | Die drei vorhandenen BINGIE-Zeilen öffnen: Live höchstens zwölf Sender aus Startgruppe, Startsender zuerst; Filme/Serien mit vorhandenen Covern. Keine Widget-Konfiguration überschrieben. | NOT_TESTED |
| W39-02 | Einen bereits manuell zugeordneten Sender in großem EPG, Mini, Infobar und Widget vergleichen: dieselbe reale Jetzt-/Danach-Sendung. Wenn keine bestehende Zuordnung verfügbar: NOT_TESTED; keine neue Mapping-Funktion behaupten. | NOT_TESTED |
| W39-03 | Auf Kodi-Home einen natürlichen Sendungswechsel beobachten: Jetzt/Danach/Uhrzeiten/Progress korrekt. Widget-Refresh-Verhalten notieren. Bleibt die Kachel statisch, Gate FAIL/offener Skinadapter; korrekte Backenddaten allein reichen nicht. | NOT_TESTED |
| W39-04 | 20 Fokuswechsel zwischen bestehenden Kacheln: kein Autostart, kein pro-Kachel-EPG-Import/Providerrequest, keine GUI-Blockade. Native dynamische Bildanforderungen separat behandeln. | NOT_TESTED |
| W39-05 | Sender mit fehlendem/lückenhaftem oder stale EPG: keine erfundenen Programme oder Prozentwerte. Gültige gespeicherte Daten bleiben nutzbar; kein ungefragter Komplettimport durch Widget/Fokus. | NOT_TESTED |
| W39-06 | Großes EPG bei Zukunft/Mitternacht prüfen, lokale Zeitfolge korrekt. Vorhandene manuelle Zuordnung und Quellprioritäten bleiben erhalten. DST wird zusätzlich im Hostmodell geprüft, Geräteuhr nicht umstellen. | NOT_TESTED |
| I39-01 | Live einmal OK: Logo, Name, lokales Jetzt/Danach, Zeiten und Fortschritt. Zweimal OK/Runter: große echte Playerbuttons. Ausblenddauer weiter wie konfiguriert. | NOT_TESTED |
| I39-02 | Technische Werte mit Kodi vergleichen: reale Pixelmaße, p/i nur bei Scanangabe, FPS, Codec, Audiokanäle/Sprache. Keine Qualität aus Sendernamen ableiten. | NOT_TESTED |
| I39-03 | Technische Details: Decoder/Pixelformat/Seitenverhältnis/Samplerate/Untertitel/HDR soweit gemeldet. Fehlende Angaben unbekannt; kein erfundenes SDR, keine angebliche Kodi22-Live-Bitrate. | NOT_TESTED |
| I39-04 | Audio-/Untertitelspur wechseln und zurück: neue reale Angaben erscheinen, Video bleibt dieselbe eigene Session; Streamkanäle nicht als gesicherte AVR-Ausgabe darstellen. | NOT_TESTED |
| I39-05 | 20 Senderwechsel mit Infoöffnung: alte technische Angaben nach Sessionwechsel nicht stehen lassen. Auch fehlgeschlagenen Start prüfen, soweit ein reproduzierbares Testbeispiel besteht. | NOT_TESTED |
| O39-01 | 20 OSD-Zyklen Live und 20 VOD: Transportbuttons deutlich größer als Einstellungen, Fokus mit IR sichtbar; native Klicks lösen jeweils genau eine Aktion aus. | NOT_TESTED |
| O39-02 | Pause, unterstützte Sprünge/Spulen und Timeline prüfen. Ohne tatsächliche Seek-/Pause-Fähigkeit keine Fake-Aktion anbieten. Stop beendet nur eigene Session. | NOT_TESTED |
| O39-03 | Native Ton-/Bild-/Untertiteldialoge öffnen, Back, eigene Controls wieder bedienen. Kein fremder Dialog geschlossen oder Fokus übernommen. | NOT_TESTED |
| O39-04 | Sporadischen Standard-Kodi-OSD-Fall beobachten/reproduzieren: bei eigener Session Standard-VideoOSD 12901 freigeben und XCMate-Controls wiederherstellen. Falls nicht aufgetreten, Reproduktion NOT_TESTED und übrige Zyklen separat dokumentieren. | NOT_TESTED |
| O39-05 | Fremden Kodi-Player separat verwenden: XCMate liest/übernimmt/stoppt ihn nicht und schließt seine Dialoge nicht. | NOT_TESTED |
| V39-01 | Film aus Liste/Detail starten: sichtbares OSD → Back blendet nur aus; weiterer Back im Vollbild → asynchroner eigener Stop und korrekte ursprüngliche Ansicht. 20 Zyklen, Fokus/Offset prüfen. | NOT_TESTED |
| V39-02 | Film aus Suchergebnis starten und mit Stop/Back zurück: Suchbegriff, Live/Film/Serie-Tab, Scroll und Fokus erhalten; kein Rücksprung auf XCMate-Root. 20 Zyklen. | NOT_TESTED |
| V39-03 | Serie aus Staffel-/Episodenansicht starten, Stop/Back, gleiche Herkunft und richtige Staffel/Folge/Next-Aktion. 20 Zyklen. | NOT_TESTED |
| V39-04 | Manueller Next über Staffelgrenze: genau eine gültige Folge; nach Rückkehr korrekte Staffel-/Episodenposition und weitere Next-Aktion. | NOT_TESTED |
| V39-05 | Natürliches Episodenende und Staffelwechsel: vorhandenes Autoplay läuft; Resume/Gesehen bleiben korrekt. Manueller Stop/Back/Fehler erzeugt keine nächste Folge. | NOT_TESTED |
| V39-06 | Vor sichtbarem Videostart mehrfach Play drücken: kein konkurrierender identischer Start. Bewusst Back abbrechen und später neu starten: Guard freigegeben, kein verspäteter alter Stream. 20 Wiederholungen. | NOT_TESTED |
| V39-07 | Beim Return geöffnete native Modals respektieren; fremde Wiedergabe darf keinen alten Medienreturn auslösen. Meldung `NATIVE_RESTORE_FAILED` wäre FAIL, kein stiller Erfolg. | NOT_TESTED |
| N39-01 | 20 Links-/Rückwege: Vollbild → Mini → Gruppen mit schmaler Rail → volle Navigation; Back/Rechts deterministisch zurück. Kein Tune/Stop durch bloßen Fokus. | NOT_TESTED |
| N39-02 | Nach schneller IR-Wiederholung alle Rail-Labels, Icons und Fokusflächen weg; keine Geistertexte Search/Favorites/Live TV. Auch Hintergrund nach Player-/Rubrikwechsel beobachten. | NOT_TESTED |
| N39-03 | Mini kompakter, kleinere Zeilen/Schrift, lange Titel lesbar. Rechtes Jetzt-Event bleibt grün markiert, wenn Fokus zu Vorher/Danach bewegt wird. | NOT_TESTED |
| N39-04 | Rechts fokussiert Programme ohne Popup/Tune; Links/Back zuerst zurück zu Sendern. 20 Fokus-/Gruppenwechsel, reale Daten bei Mitternacht/Lücke. | NOT_TESTED |
| N39-05 | Großer EPG: Startgruppe/Startsender, Wiedergabe-Handoff und Rückkehr unverändert; vorhandene Film-/Serien-Detailmenüs und Favoriten bedienbar. | NOT_TESTED |
| A39-01 | Dynamische Film-/Seriencover über 30/60/120 Sekunden beobachten: kein Leerblitzen bei erfolgreicher Revalidierung. Keine dauerhafte XCMate-Archivierung auslösen. | NOT_TESTED |
| A39-02 | 20 Live/Film/Serie-Suchtab- und Kategorienwechsel: bereits angezeigte sichere Cover bleiben beim Listen-Neuaufbau erhalten, Fokus/Position stabil. | NOT_TESTED |
| A39-03 | 20 Film-/Episodenstarts mit Stop/Back zur Suche/Übersicht: Cover wieder da, keine Platzhalterphase durch verlorene Row-Referenz. | NOT_TESTED |
| A39-04 | Fehlende Provider-Bildquelle von echtem Download-/DNS-Fehler unterscheiden. Unsichere/geänderte Quelle darf keine alte Freigabe erben. Keine echten privaten Quellen zum Test manipulieren; negative Fälle gegebenenfalls NOT_TESTED. | NOT_TESTED |
| S39-01 | Sendername „Rock“ beziehungsweise tatsächlich vorhandener Name: erste lokale Treffer früh bedienbar; EPG wird ergänzt. Kalt/Warm Zeiten separat notieren. Kein Programmtitel-PASS allein wegen Sendernamen. | NOT_TESTED |
| S39-02 | Einen nachweislich aktuell im lokalen EPG stehenden Programmtitel suchen: echter Programmtreffer, korrekter Senderstart und Rückkehr. | NOT_TESTED |
| S39-03 | 20 schnelle Tab-/Querywechsel während Anreicherung: kein wiederholter kompletter 2.905-Kanal-/Alias-Scan, kein verlorener Cursor/Fokus, alte Query übernimmt keine neuen Ergebnisse. | NOT_TESTED |
| S39-04 | Bestehende Film-/Serien-/Genresuche mit Covern und unveränderter dreigeteilter Suchmaske. Favoriten, Portale, Gruppen, Startsender, Mappings und Resume erhalten. | NOT_TESTED |
| L39-01 | 20 schnelle Live-Info-/Mini-Öffnungen kalt/warm. Sichtbare Zeiten messen; UI39-Owner/RAM/Build/Show/GUI-Marks und langsames APP_SERVICE_POLL getrennt bewerten. Kein Doppelstart als Timeout-Reaktion. | NOT_TESTED |
| L39-02 | Längerer Live-/VOD-Alltagstest einschließlich H.264/H.265 soweit verfügbar, Tonwechsel, Start→Stop und IR-Repeats. MediaCodec Buffer/InstanceGuard/null-size und Post-Stop-Ausnahmen anonymisiert korrelieren. | NOT_TESTED |
| R39-01 | Reguläres Öffnen mit aktivem Startsender startet genau einmal; Refresh/Widget/Back nicht erneut. Deaktivierte Option und sichtbare Diagnosepause weiterhin respektiert. | NOT_TESTED |
| R39-02 | Original-Icon/Space-Grafiken, Startgruppen, bestehender Wizard/Nachimport/EPG-Fortschritt und Datenbestand erhalten. Keine neue Profilkonfiguration auf B erzwingen. | NOT_TESTED |

## Messerfassung

Anonymisierte .38-Referenz aus Master #193: erste Sendernamen 1.642 ms, erste sichtbare Live-Reihe 24.974 ms, erster Programmtreffer 26.883 ms, Abschluss 31.878 ms; Live-Info/Mini intermittierend bis 49.057 ms. Punkte sind deutsche Tausendertrennzeichen. Das sind Geräte-Ereigniszeiten, keine isolierte Render-CPU-Zeit.

Je .39-Versuch Zeitpunkt der Eingabe, erste bedienbare Reihe/Info, Programm-Anreicherung und Abschluss erfassen. UI39 misst Callback-/Owner-/GUI-Phasen, nicht physische IR-Latenz oder den ersten decodierten Frame. Hostwerte aus `BENCHMARK_SUCHPERFORMANCE_02939.json` nicht mit Androidzeiten verrechnen. Veröffentlichung nur bereinigter Zahlen/Eventcodes.

## Offene Freigabegates

Reales BINGIE-Home-Rollover/InfoTag-Rendering, tatsächliche Kodi21-Streamfelder, sporadischer OSD-Auslöser, physische IR-/GUI-Latenz, Native-Return und Rockchip-Decoderverhalten bleiben Geräteabnahme. OSD A/B braucht gesonderte visuelle Auswahl. #98 und #161 bleiben getrennt. Keine Issue-Schließung, kein Merge oder produktiver Release vor ausdrücklicher Nutzerfreigabe.
