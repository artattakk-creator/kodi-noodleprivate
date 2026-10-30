# XCMate .58 – getrennte P0-Befunde und Grenzen

Basis: main cb58e38ff450a56a97178708db193ad0ad8b670f, Version .57. Auftrag #277, ergänzend #276. Stand 30.10.2026.

## Anbieter-EPG: belegte UI-/Speicherursache, lokal repariert

Der bisherige Schalter war ausschließlich hinter OK auf Quellenliste 200 und einem Ja/Nein-Dialog verborgen. Neun sichtbare Buttons boten keine entsprechende Aktion. Zudem wurde der Zustand aus einer älteren Quellenzeile invertiert und das Ergebnis von portals.update nicht überprüft. Das ist ein belegter Bedienungs-/Persistenzfehler; keine Vermutung über die privaten Providerdaten.

Neu: sichtbarer Button 410 über der Quellenliste, beschriftet „Anbieter-EPG aktivieren“ bzw. „…deaktivieren“, Startfokus bei Xtream, vollständiger Pfeiltastenpfad. Beide Bedienwege verwenden dieselbe transaktionale Funktion. Sie liest das richtige Portal unter bestehender Profilsperre, ändert nur provider_epg_enabled, speichert mit bestehendem atomarem Portal-Backend und prüft durch Re-Read. Fehlende/fremde Portale und unbestätigte Schreibvorgänge gelten als Fehler. Keine Zugangsdaten-Ausgabe. Kein Speichern von Status READY durch Aktivierung.

Jetzt aktualisieren bleibt ein ausdrücklicher zweiter Schritt. Der Service liest das Portal beim Abarbeiten der bestehenden Refresh-Anfrage frisch. Der bestehende Streaming-Importer berücksichtigt provider_epg_enabled und führt aktivierte externe Quellen weiterhin parallel in guide_v1.sqlite. Im Manager wird die lokale Übersicht nach angefordertem Import für höchstens zehn Minuten alle zwei Sekunden auf dem vorhandenen Worker gelesen; danach Quellenliste/Refresh manuell weiter nutzbar. Das ist keine Import-Abbruchfrist. Erfolgszähler und Zeitraum stammen aus gespeicherten guide44_inputs, nicht aus der Aktivierungsbestätigung.

Zusätzliche XMLTV-Adresse: nur die vom Benutzer eingegebene Adresse. Ein exaktes, normalisiertes Duplikat der tatsächlich konfigurierten Anbieter-Adresse wird abgefangen, einschließlich Standardport/Host-Schreibweise. Unterschiedliche Pfade, Querywerte und Zugangsdaten werden nicht zusammengelegt. Bestehende externe Quellen werden weder gelöscht noch umgeordnet. Kein Erraten zusätzlicher Endpunkte. Der bereits bestehende Adapter wird ausschließlich zur Ermittlung seiner vorhandenen Anbieter-XMLTV-Adresse benutzt.

Manuelle Quellenzuweisung bleibt das bestehende quellensichere Verfahren: EPG-Quell-ID plus Kanal-ID, RAM-Vorschau im großen Raster, explizites Speichern, vollständige Wiederherstellung bei Abbruch. Die Regressionen prüfen die gleiche Kanal-ID in Provider und externen Quellen, unabhängige Titel, JSON-/SQLite-Schutz und Mini-/Groß-EPG. Dieser Code wurde nicht umgebaut. Ohne echte Providerdaten ist nicht belegt, ob NO_EPG/NO_SOURCE_FACTS auf Box B nur durch Aktivierung oder zusätzlich fehlende IDs/Zuordnungen entstehen.

## BINGIE: Quellenverletzung repariert; tatsächliche Unsichtbarkeit noch nicht lokalisiert

Die historischen PUBLISHED rows=24 für VOD und Serien beweisen nur interne DTO-Veröffentlichung. Sie belegen weder einen erfolgreich abgefragten Kodi DirectoryProvider noch sichtbare Home-Kacheln. Der Nutzer hat beide Reihen bereits eingebunden; kein pauschales Neueinrichten.

Belegter Codefehler: app_routes.widget und app_services übernahmen media_overrides43.apply_many. Zusätzlich konnten widget_art44 und gemeinsame Asset-Referenzen manuelle Ersatzbilder liefern. Das widerspricht der verbindlichen .58-Regel „Medienwidgets ausschließlich Provider“. Die beiden Apply-Aufrufe entfallen. Das gemeinsame Asset-Backend erhält eine explizite Provider-Grenze für Widget-Reads/-Vorbereitung. Die normale Medienansicht behält ihre bisherige manuelle Korrekturfunktion und sämtliche Dateien. Der gemeinsame Widget-Descriptor normalisiert die Medienart, sodass auch ein Rohdatensatz ohne kind keine manuelle Bildquelle einschleust. Keine Helper-/TMDb-Abfrage für Film- oder Serienwidgets. Der vorhandene Helper bleibt ausschließlich im Live-Sendungsbildresolver.

Die neue read-only Diagnose widget_consumer58 liest die tatsächlich von Kodi ausgewählte special://profile/-Konfiguration und das erzeugte Layout im aktiven Skinpfad. Sie trennt BINDING_PRESENT/BINDING_INVALID, generierten Consumer, tatsächliche Home-Containeranzahl/Sichtbarkeit und weiterhin unbekannte Bildpixel. Stock BINGIE 2.2.3 verwendet parametrisierte widget_base-Includes; ein bloßer <content>-URL-Scan reicht nicht. Dieser Pfad wird gegen die unveränderte IncludesHomeWidgets-Definition aufgelöst. Unbekannte Definitionen bleiben unverifiziert. Laufzeitwerte werden nur auf tatsächlich aktivem Home ohne Dialog ausgewertet; eine im Einstellungsdialog unsichtbare Home-Zeile wird nicht als realer Home-FAIL gewertet. Diagnose ist über den vorhandenen Status vorhandener Widgetverknüpfungen erreichbar; keine neue Route.

BLOCKED_DEVICE_ACCESS: Die echten gespeicherten Properties, generierten XML-Dateien, HomeLayout-/Sichtbarkeitswerte und Screenshots von Box B fehlen in dieser Sitzung. Deshalb lässt sich die tatsächliche Ursache des gemeinsamen Ausblendens beider Reihen nicht belegen. Die Quellenkorrektur ist kein Nachweis, dass damit beide Home-Zeilen sichtbar werden. Keine automatische Profil-/Skinänderung oder Umverknüpfung. Android-Gates bleiben offen.

## Live-TV-Zurück: native Rückkehr nicht bestätigt; Hardware-Reparatur BLOCKED

Belegter alter Geräteablauf: 30.10.2026 09:16:19 STOP_REQUESTED → 09:16:24 STOP_TIMEOUT. Die erneute Nutzerreproduktion hat keinen belegten Zeitstempel. Der historische .42-Kompatibilitätsmodus wurde früher erfolgreich getestet; sein aktueller Wert auf Box B ist unbekannt.

native_stop41 stellt PlayerControl(Stop) und anschließend eine FIFO-SetProperty-Barriere in dieselbe Kodi-Main-MessageQueue. Erst die echte Nonce-Bestätigung beweist die Rückkehr des nativen Stops. Fehlt sie, sind ein Python-Callback, Thread-Ende oder fünf Sekunden Wartezeit kein Stop-Erfolg. CVideoPlayer/MediaCodec/AudioTrack- oder Fensterfreigabe als konkrete native Ursache ist aus den vorliegenden Auszügen nicht eindeutig unterscheidbar.

Belegter Diagnoseblinder Fleck: service.py überspringt bei exit_jobs.blocked() die folgenden Live-Exit-Beobachter. Die neue property-only Beobachtung läuft unmittelbar davor und meldet einmal pro Session/Änderung NATIVE_QUEUE_UNRETURNED, PREPARE_QUEUE_UNRETURNED, STOP_RETURNED_LATE oder STOP_NOT_POSTED, einschließlich tatsächlich gewählter direct41/fullscreen42-Strategie und echter FIFO-ACK. Keine Playerabfragen, GUI-Transitions, wiederholten Stops, Timeoutverlängerungen oder falschen HOME-Erfolge im blockierten Zustand. Die Session-Korrelation entspricht den vorhandenen Exit-Traces; keine URLs, Zugangsdaten oder Klartext-Nonce.

Der eigentliche native Stop-Ablauf und sein opt-in fullscreen42 bleiben byteidentisch. Ebenfalls unverändert: Single-flight, Fremdplayer-/Modal-Schutz, Latch gegen Replay, Late-ACK-Rückkehr, Film-/Serien-Resume und Autoplay. Der Host reproduziert eine festhängende native Queue und verifiziert, dass kein zweiter Stop oder erzwungener Home-Wechsel erfolgt. Dies ist ausdrücklich KEIN behobener Rockchip-Freeze. Ohne autorisierte Box B ist ein belastbarer A/B-Nachweis oder Decoder-Fix nicht möglich. Kein blindes Aktivieren des Kompatibilitätsmodus; keine Kodi-/Keymap-/Skinänderung.

## Sicherheits- und Abnahmegrenze

Box A und Box B wurden nicht verbunden oder verändert. Kein Reset, keine Cache-/Bild-/Portal-/DB-Löschung, keine Migration, keine Installation, kein Merge/Release. Bestehender Widgets-Ordner, Quell-URLs und Routing bleiben erhalten. Die .58 ist ein kumulativer Review-/Diagnosekandidat mit lokal repariertem Provider-Schalter und Widget-Quellenvertrag; die vollständige P0-Abnahme ist nicht erreicht. #277 und #276 bleiben offen.
