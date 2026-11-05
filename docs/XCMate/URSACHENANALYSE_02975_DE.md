# XCMate 0.1.29.75 – Ursachen und Grenzen

Basis: `ad5c337c0ca9ea6f85e458c17383fb32c19e3fc2`, kumulativ auf .74; Auftrag #366/#367/#368 und vollständige .75-Übergabe gelesen. Keine privaten Rohlogs oder Gerätebilder im Repository.

## Nachgewiesene Add-on-Fehler

1. `hero_epg63.poll()` brach bei fehlendem Progress-Control 296301/296302 vor dem Bank-Commit ab. Jetzt bleiben Titel, Jetzt/Danach, Bild, Quelle und Identität atomar verfügbar; der optionale Balken ist separat diagnostiziert.
2. Der bisherige lokale EPG-Handoff überlebte keinen Kodi-Prozessneustart. `epg_snapshot75` ergänzt einen privaten, auf 2 MiB/512 Sender begrenzten Checkpoint der bestehenden Now/Next-Datensätze. Profil, Provider-Zugangsfingerprint, Konfiguration, Guide-Generation und echte Ereigniszeiten werden geprüft. Kein zweiter Guide, keine Änderung der Zuordnungen. Ein fehlgeschlagener Checkpoint beeinträchtigt den Guide nicht. Eine neue Guide-Generation oder Mappingänderung gewinnt.
3. Native Home-Captions und Scroll-Animationen konnten hinter dem neuen Hero weiterzeichnen. Der geprüfte .75-Adapter reserviert Bild links (1080/1620 = 66,7 %) und Tabelle rechts (540/1620 = 33,3 %), darunter einen festen 440-Pixel-Viewport pro aktiver Rail. Hochkantposter bleiben unverzerrt. Native Templates und alle gespeicherten Widgetpfade bleiben erhalten.
4. Eine reine Fokuszuweisung verdeckte einen Fehler der verschachtelten Rail-Navigation. Echte Kodi-Auf/Ab-Aktionen wurden deshalb ergänzt. Der native SkinShortcuts-Compiler erzeugt jetzt explizite Nachbarziele aus den tatsächlich konfigurierten Slots; störende Home-Scrollanimationen bleiben außerhalb dieses Layouts. Keine Keymap und kein Python-IR-Umleiter.
5. Kodi-Bildvariablen dürfen nicht als InfoLabel-Argument für `String.IsEmpty` behandelt werden. Die neue Bild-/Quellenwahl bindet direkt an die passende Bank, Identität und Profil. Eine aktive Bank ohne Bild darf weder ein altes ListItem-Bild noch dessen TMDB-Logo übernehmen.
6. Senderlogos verloren ihre kurze Freigabe unabhängig von vorhandenen Titelzeilen. Der bestehende .74-Referenznachweis wird für Live weiterverwendet, ein gültiges Logo nicht durch leere optionale Anreicherung überschrieben. Jede Live-Kachel behält eine Senderbeschriftung, auch bei später fehlschlagendem Texture-Fetch.
7. XMLTV-/Provider-Eventbilder konnten an der pauschalen CDN-Hostliste scheitern. `programme_origin75` erlaubt ausschließlich eine exakte, autoritative Event-Bildadresse nach öffentlicher, gepinnter DNS-/TLS-/Bildprüfung; niemals einen ganzen neuen Host. HTTPS, keine Zugangsdaten, keine Query/Fragmente, keine privaten/lokalen/literalen IP-Ziele, kein Redirect. Kurzfristige profilgebundene Nachweise; Renderer macht keine Netzwerkprüfung. TMDB/TVmaze bleiben separat opt-in. Alte betroffene Negativergebnisse werden pro Event einmal neu bewertet, kein globaler Jobreset.
8. Nach verspätetem, positivem Stop-FIFO-ACK konnte das leere Kodi-Vollbildfenster 12005 die vorhandene Rückkehrwiederherstellung dauerhaft blockieren. Dieser Rückweg ist jetzt zugelassen, weiterhin nur nach exakter Session-/ACK-Prüfung, ohne aktive/neue/fremde Wiedergabe oder fremden Dialog. 20 Host-Zyklen prüfen genau einmalige Navigation ohne zusätzlichen Stop.

## Ladepriorität und Nachweisgrenzen

`home_schedule75` ist eine dünne Gate-Schicht über vorhandenen Workern. Sie gilt auch während des BINGIE-Splashs, nicht erst im bereits sichtbaren Home. Lokales EPG und Senderlogos kommen zuerst. Fokus plus tatsächlich sichtbares Fünferfenster gehen vor Rotation; absolute Senderposition und Position im Viewport werden unterschieden. Bestehende 24er Eventqueue und Provider-Worker bleiben begrenzt.

Ein `queue.put`, eine URL oder eine vorbereitete Veröffentlichung ist **kein** sichtbares Rendering. Deshalb sind `MOVIES_PREPARED` / `SERIES_PREPARED` getrennt von den nativen `*_VISIBLE_READY`-Beobachtungen. In der strikten Auslegung der Spezifikation wird die automatische nächste Phase erst nach der tatsächlichen Anzeige der vorherigen Medienreihe freigegeben. Ein direkter Nutzerfokus bleibt unabhängig priorisiert und blockiert die Navigation nicht. Die mögliche Freigabe unsichtbarer, bereits geprüfter Reihen ist dem Nutzer als konkrete Präzisierungsfrage vorgelegt; ohne Antwort bleibt die strengere Renderbedingung erhalten.

Empfängerbeobachtungen prüfen native Labels, Sichtbarkeit, Fokus und feste Geometrie. Sie behaupten keinen erfolgreichen JPEG-Decode; Pixelnachweise stammen aus separaten nativen Screenshottests. Alle privaten Android-Nachweise bleiben ausstehend.

## Skin- und Datenbestandsschutz

Der Adapter ist **nicht automatisch auf Installation anzuwenden**. Bestehender Ablauf: Vorschau → SHA-Sicherung → ausdrückliche Zustimmung → nativer SkinShortcuts-Neuaufbau; vollständiger Restore bleibt möglich. Vier bekannte Integrationsdateien plus das exakt geprüfte originale `IncludesBingie.xml` für größere, spezifische Menüicons. Der originale, von Kodi tolerierte verschachtelte Kommentar wird im Kandidaten syntaktisch repariert; Restore liefert jedes ursprüngliche Byte zurück. Unbekannte Space-Blue-/Skin-XML wird blockiert und nicht überschrieben. Einstellungen, Branding, Intro, gespeicherte Shortcuts und Widgetpositionen werden nicht zurückgesetzt.

`kodi_schema75` diagnostiziert MyVideos131 ausschließlich lesend mit begrenztem `integrity_check` und Viewprüfung. Keine Datenbank wird angelegt, repariert, migriert oder gelöscht. Andere Kodi-Schemaversionen werden nicht als aktuelle Kodi-21-Bibliothek ausgegeben.

## Nicht bewiesene Ursachen / weiterhin offene Hardwareprüfung

- Die Logzahlen beweisen weder eine einzelne Netzüberlastungsursache noch einen Wechsel zwischen zwei Guide-Datenbanken.
- Es ist nicht bewiesen, dass alle 181 blockierten Android-Bildadressen gültige Provider-/XMLTV-Bilder waren. Der konkrete neue Pfad ist in Hosttests geprüft; reale private Endpunkte fehlen.
- Ein vorhandener TMDB-Token beweist keinen Lookup-Opt-in oder einen positiven Match. Es wird nichts stillschweigend aktiviert.
- **#368: Ein nativer RK3528-/MediaCodec-/AudioSink-Stop ohne zurückkehrendes FIFO-ACK ist nicht durch diese Python-Reparatur nachweislich behoben.** 5-/10-Sekunden-Evidenz verwendet nur Window-Properties, keinen Player-Lock, keinen zweiten Stop, keine verlängerte Stop-Frist und keinen falschen Erfolg. Der vorhandene explizite .42-Kompatibilitätsmodus und seine Einstellung bleiben erhalten. Echte Android-ACK-/Kodi-`finished waiting`-/GUI-Nachweise sind Freigabebedingungen für den regulären Kanal.

## Nachgewiesener Host-Fehler der isolierten Navigationstestfixture

Die reale Kodi-API `xbmcvfs` fehlte in der alten Omega-Overlay-Fixture. Bei 2.000 Modellschritten entstanden 70.738 erfolglose Importsuchen in `profile_scope`; Profiling weist 9,417 s unter Importauflösung aus (mit Profiler, kein Android-Messwert). Ein vollständiger Host-Discovery hatte den Fehler durch zuvor geladene Module verdeckt. Die Fixture stellt jetzt die echte konstante VFS-Übersetzung nach; die unveränderte 5-s-Grenze und sämtliche Funktionsassertions bleiben bestehen. Lokal benötigt der komplette Einzelfall einschließlich Setup 0,856 s. Es wurde dafür kein Player-, Routing- oder Add-on-Code geändert.
