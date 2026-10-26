# XCMate .39 – Ursachen, Korrekturen und Beweisgrenzen

Basis: `d8a20a2b7887878c3d5192e355b5c642a2bdebd5`, main .38 nach Nutzer-Merge #184 (`e87f606`). Master #193 und #182/#183/#185–#192 einschließlich aller Kommentare vollständig gelesen. Keine Übernahme alter Experimentbranches. .38-Paket/Produktionsindex und Geräte unverändert.

## Lokales EPG und Widgets (#182)

Vorher lasen die drei Widget-Routen beziehungsweise der Live-Now/Next-Pfad den kleinen Kompatibilitätscache, der große EPG dagegen `guide_v1.sqlite`. Dadurch konnten dieselben Sender je Ansicht abweichende Daten bekommen. `local_epg.py` liest jetzt die erfolgreich veröffentlichte bestehende Guide-Datenbank über read-only SQLite-Verbindungen. Metadaten, Aliasse und Programme liegen in einer Lesetransaktion. Kein paralleler EPG-Speicher, keine Schema-/Quellprioritätsänderung und kein #161-Intervallmerger.

Großer EPG, Live-/Mini-Snapshot und Live-Widget nutzen diesen gemeinsamen Leser und dieselbe Normalisierung. Manuelles Mapping gewinnt; ein fehlendes manuelles Ziel fällt nicht auf die Provider-ID zurück. Zeitfortschritt und Rollover werden aus realen Start-/Endzeitstempeln berechnet. Mini-EPG liest GUI-seitig ausschließlich vorbereitete RAM-Daten; der Worker kann echte Historie lesen. Vor der ersten Guide-Publikation bleibt der alte lokale Live-Kompatibilitätsfallback erhalten. Widgets importieren und hydrieren keinen vollständigen JSON-Katalog.

Die drei Widget-Routen bleiben erhalten. Live zeigt höchstens zwölf Sender, Startsender zuerst. Standard-Video-Plot vermittelt Jetzt/Danach auch ohne Unterstützung der Zusatzproperties; Fortschritt wird nicht als Kodi-Gesehen-/Resume-Wert ausgegeben. Sichtbare Auswahl plant keine Short-EPG-Providerjobs mehr. Der unabhängig getaktete Hintergrundimport respektiert `epg_auto_refresh`; das separate Katalog-Prefetch bleibt optional.

**Offene Darstellungsgrenze:** Ein von BINGIE zwischengespeichertes ListItem ändert seine Properties nicht von allein. Der lokale Rollover ist getestet; fortlaufende Home-Anzeige benötigt den vorhandenen Widget-Refresh oder eine ausdrücklich gewählte Skinbindung. Deren reales Verhalten ist NOT_TESTED. Keine Nutzerwidgets oder Skin-Dateien überschrieben. `WIDGET_ADAPTER_02939_DE.md` beschreibt das getrennte Opt-in und das Abnahmegate.

## Streamdaten und OSD (#183/#186)

`stream_details.py` liest ausschließlich whitelisted Kodi21-InfoLabels einer bestätigten eigenen Session. Pro sichtbarer Oberfläche höchstens ein Sample in zwei Sekunden; bei Stop/Sessionwechsel werden alte Felder verworfen. Fehlende Pixelgröße, Scanart oder HDR-Angabe bleibt unbekannt; keine Schätzung aus „HD/4K“ im Namen und kein v22-Live-Bitrate-Feld. Tonkanäle beschreiben den Stream, nicht den AVR-Ausgabemodus. Feldtabelle und Grenzen in `KODI21_STREAMFELDER_02939_DE.md`.

Transportbuttons und lokale Icons sind größer; Einstellungen liegen in einer kleineren zweiten Zeile. A ist die technische Arbeitsvariante, B eine alternative Skizze. Keine visuelle Nutzerabnahme behauptet.

Ein reproduzierbarer **Hostpfad** ist abgedeckt: Kodi-VideoOSD 12901 über einer gültigen eigenen Session blockierte bislang das erneute XCMate-OSD. Jetzt wird ausschließlich dieses Standard-VideoOSD gezielt geschlossen; erst nach tatsächlicher Freigabe kehren eigene Controls zurück. Audio-/Bild-/Untertitel-/Busy-/fremde Python-Dialoge werden nicht geschlossen. Die ID ist in Kodi Omega `xbmc/guilib/WindowIDs.h` belegt. Der konkrete sporadische Android-Auslöser bleibt unbekannt; Host-Replay ist kein Nachweis einer Android-Root-Cause.

## VOD-Back, Stop und Herkunft (#185/#192)

Bestätigter Codefehler: .38 behandelt Back auch bei verborgenem VOD-OSD nur mit `hide_bar()`. .39 blendet beim ersten Back das sichtbare OSD aus; Back aus bereits verborgenem Vollbild fordert genau einen asynchronen eigenen Stop an. Serien-Autoplay wird bei manueller Beendigung abgebrochen, natürliches Episodenende bleibt getrennt.

Der ursprüngliche native Medien-/Suchdialog hält einen RAM-Memento mit Modus, Query, Tab, Kategorie, Offset, Staffel und Fokus. Zwischen Interpretern wird nur ein opaker Origin-/Intent-Token ausgetauscht, keine Provider-URL und kein Querytext. Nach Stop stellt der ursprüngliche GUI-Owner denselben nativen Fenstergegenstand wieder her. Keine Root-/Directory-Neuladung. Fremde Wiedergabe verwirft den Return, fremde Modals verzögern ihn. Ein nicht mehr verfügbarer nativer Owner wird als `NATIVE_RESTORE_FAILED` gemeldet und nur der eigene Pump freigegeben.

Die vollständigen Tests fanden eine Regression beim manuellen Next über Staffelgrenzen. Diese wurde korrigiert: Zielstaffel/-episode, Next-Zustand und Fokus 330 stimmen wieder; alle bisherigen Manual-Next-Tests bleiben erhalten. Zusätzlich verhindert ein Pending-Start-Guard wiederholte konkurrierende VOD-Resolver durch IR-Repeats. Expliziter Startabbruch gibt den Guard frei.

`playback_exit.identity()` fängt den legitimen Stop-Race zwischen `isPlayingVideo()` und `getVideoInfoTag()` ab. Zeit-/Dauerzugriffe bleiben owner-geprüft und abgesichert. **MediaCodec Buffer/InstanceGuard/null-size ist damit nicht als Treiberfehler behoben bewiesen.** Kein Codec-/Player-Engine-Rewrite, kein fremder Player-Stop. Echte H.264/H.265-/ARM32-Races bleiben Geräteabnahme.

## Rail, Mini und Cover (#187–#189)

Neue Live-Kette: Vollbild → Mini → Gruppen **mit** schmaler Rail → vollständige Navigation. Back/Rechts kehrt deterministisch zurück. Rail-Hide leert zusätzlich Labels und Bildreferenzen und deaktiviert Fokusflächen. Die bislang mögliche native Geisterdarstellung wird defensiv verhindert; ein echter Kodi-Repaint muss auf Android geprüft werden.

Mini-EPG: schmalere Gesamtfläche, rechte Zeilen 40 statt 58 Pixel, kleinere Schrift und native Neon-Fokusfläche. Die laufende Sendung bleibt separat grün markiert, auch wenn der Benutzer ein anderes Event fokussiert. Reale Daten, kein Tune durch Fokus, 720p-/1080p-Geometrie im Hostmodell geprüft.

Coververlust beim Listen-Neuaufbau ist reproduziert: .38 hielt Referenzen nur an der bisherigen ListItem-Position, die Suchansicht baute neue Items ohne diese Historie. .39 hält höchstens 256 bereits angezeigte Row-/Quellreferenzen im Fenster-RAM und verwendet sie beim Wiederaufbau. Ein neuer oder geänderter Bildursprung erbt keine Freigabe. Nur dieselbe schon angezeigte Quelle bleibt während ausstehender Revalidierung erhalten; endgültige DNS-Ablehnung entfernt sie. TTL/DNS/SSRF-Zulassung, bestehende Archive und Kodi-Texturecache unverändert. Keine automatische Archivierung oder globale Retry-/Löschaktion.

## Suche und 19–49-Sekunden-Verzögerungen (#190/#191)

Ein laufender Suchcursor wurde durch jede neue Short-Cache-Revisionsmeldung invalidiert. In der Fixture mit 2.905 Sendern/456 Aliassen erzeugt der .38-Code bei 20 solchen Änderungen 21 Cursor, .39 einen. Der aktive Cursor bleibt bis zur Publikation stabil; abgeschlossene Ansichten reagieren weiter auf echte Katalog-/Mapping-/Guide-Änderungen und reale Zeitgrenzen. Neue Queries können einen begrenzten vorbereiteten Snapshot wiederverwenden (maximal ein Portal, bis 6.000 Sender und 4 MiB serialisierter Live-Payload, höchstens 30 Sekunden). Kein geteiltes veränderbares Ergebnis-/Fokusobjekt.

Lokale Sendernamen werden vor EPG und Medien-Queries veröffentlicht, auch beim Einstieg aus dem Film-Tab. Danach erfolgt Anreicherung in begrenzten Worker-Slices. `BENCHMARK_SUCHPERFORMANCE_02939.json` enthält den direkten Hostvergleich; diese Zeiten sind **Datenpublikation ohne GUI**, keine Android-Vorher-/Nachher-Messung.

Zwei weitere Codepfade konnten GUI-/Service-Reaktion verzögern: vollständige lokale Katalogvorbereitung beim Navigatorbau und synchrone Diagnosedateien auf Fokus-/Owner-/Renderpfaden. Katalogvorbereitung ist jetzt single-flight im Datenworker. Diagnostik puffert begrenzte Übergänge und schreibt außerhalb des GUI-Pfads; der Writer hält dabei keinen Callback-Inbox-Lock. Fehler vor „CLOSED“ und letzter EPG-Erfolg bleiben beim Flush erhalten. GUI-Close startet keinen neuen Dateischreiber.

Neue numerische UI39-Marks trennen Callback-Eingang, Ownerprüfung, Katalog, RAM-Snapshot, Controls-Aufbau, natives Show und GUI-Anwendung; langsames App-Service-Polling wird getrennt gemeldet. Das ist **kein physischer IR-Zeitstempel und kein Beweis des ersten decodierten Bildframes**. Die privaten Logs belegen End-to-End-Fälle bis 49.057 ms; ob dort Decoder, Kodi-GUI, Profil-I/O oder mehrere Phasen dominieren, bleibt mit den neuen Android-Marks zu prüfen. Kein bloßes Erhöhen eines Timeouts.

## Bestandsschutz und Restabnahme

Keine Box verändert. A erhält in diesem Zyklus weder Update noch Eingriff. B bleibt Dynamisch, ohne zusätzliche USB-/SMB-/SD-, Speicher-, Kopier-, Migrations-, Lösch- oder Massendownloadtests. .38-ZIP/Index, Originalgrafiken, Suchmasken-XML, Portale, Gruppen, Startsender, Resume/Gesehen/Autoplay und Mappings geschützt. Private Rohlogs nicht geöffnet oder veröffentlicht; ausschließlich bereits anonymisierte Issuebefunde verwendet.

Alle .39-Android-Gates NOT_TESTED. Home-Widget-Dauerrefresh/Rendering, physische IR-/GUI-Latenz, tatsächliche Streamfeld-Verfügbarkeit, sporadischer OSD-Auslöser und Rockchip-Decoderursache bleiben offen. #98 Quell-ID-Mapping, #161 EPG-Hub, Downloads/Aufnahmen und die geerbten Metadaten-/Wizard-Resume-Blocker werden nicht stillschweigend als erledigt markiert. Kein Merge oder Produktionsrelease.
