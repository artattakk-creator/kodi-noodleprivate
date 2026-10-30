# Android-Abnahme .58 – Box B, Kodi 21.3 / RK3528 ARM32

Alle neuen Gates: NOT_TESTED. Kein autorisierter Gerätezugang in der Codex-Sitzung (BLOCKED_DEVICE_ACCESS). Box A bleibt unangetastet. Historische Nutzer-FAILs aus .57 sind keine Messwerte des neuen Kandidaten. Dieser Draft enthält keinen nachgewiesenen nativen Rockchip-Freeze-Fix.

## Vorbereitung und Reihenfolge

1. ZIP/SHA256 aus dem Draft-PR prüfen. Nur Box B nach eigener Testentscheidung regulär mit dem Test-ZIP aktualisieren; keine Neuinstallation, kein Downgrade, kein Reset. Popup muss Installation erfolgreich, .58 und Änderungen nennen; keinen Live-Exit-PASS versprechen.
2. Bestehende Einstellungen vor dem Test ansehen: Portal, Startgruppe, Startsender, Artwork-Modus und Wert des vorhandenen Live-Kompatibilitätsmodus dokumentieren. Keine Secrets/URLs exportieren. Modus nicht ungeprüft ändern.
3. Wegen bekanntem Freeze zuerst A58-LIVEEXIT-01 einmal ausführen. Bei Hänger sofort alle weiteren Wiedergabe-/Belastungstests beenden. Keine mehrfachen Stop-Versuche. Beobachtete Uhrzeit notieren, privaten Kodi-Log sicher aufbewahren, nur anonymisierte relevante Ereignisse weitergeben. Erzwungener Kodi-Neustart ist kein PASS.
4. Erst wenn der einzelne Back-Vorgang PASS ist: weitere fünf Start/Back-Zyklen mit verschiedenen Sendern; danach optional 20. Anschließend Medienregression. Live-Home erst nach stabiler Rückkehr und eigener Entscheidung prüfen; Hero bleibt separates Skin-Opt-in.

| Gate | Ausführbare Prüfung / erforderlicher Beleg | Status |
|---|---|---|
| A58-LIVEEXIT-01 | Startsender starten → Overlays schließen jeweils nur ihre Ebene → einmal Back aus reinem Vollbild. Stream stoppt genau einmal; bedienbare ursprüngliche Ansicht, kein Replay/Black Screen/STOP_TIMEOUT. Bei PASS weitere fünf Zyklen. Aktuellen Modus und anonymisierte STOP58/PLAYER_EXIT/LIVE_EXIT/RETURN48-Ereignisse notieren. Fehlendes natives ACK ist FAIL, kein erlaubter Ersatz-Home. | NOT_TESTED |
| A58-PROVIDER-01 | EPG-Manager: sichtbaren Anbieter-Button mit Pfeilen/OK erreichen. Aus→Ein und Ein→Aus prüfen, Zustand beim erneuten Öffnen und nach Kodi-Neustart prüfen. Anderes Portal unverändert. Aktivierung darf nicht Import-READY behaupten. Optional 720p/1080p-Lesbarkeit/Fokus ansehen. | NOT_TESTED |
| A58-PROVIDER-02 | Anbieter aktivieren, Jetzt aktualisieren, Abschluss abwarten. Bericht: Quelle provider, tatsächliche Sender-/Sendungszahl, Zeitraum, Erfolg oder konkreter Fehler. Drei echte Sender: Jetzt/Nächste/Details vergleichen. Quelle aus: weiterer Refresh lädt Anbieter nicht, vorhandene Programme bleiben. Keine fehlenden Providerdaten erfinden. | NOT_TESTED |
| A58-PROVIDER-03 | Bestehende DACH-XMLTV-Quellen weiter vorhanden. Im großen EPG auch Sender ohne EPG markieren → Kontextmenü EPG zuweisen → Provider wählen/suchen → echte Rastervorschau → Abbrechen stellt Ausgangszustand wieder her. Externe Quelle mit gleicher Kanal-ID vergleichen → Speichern → Groß-/Mini-EPG und Neustart prüfen. Zusätzliche eigene XMLTV-Adresse nur falls tatsächlich vorhanden; Duplikat des Anbieterfeeds wird nicht neu aufgenommen. | NOT_TESTED |
| A58-WIDGET-01 | Vorhandene Filmverknüpfung behalten. Auf tatsächlichem BINGIE Home mindestens zehn unterschiedliche Filme mit richtigen Providerpostern, korrekten Details/Klickzielen sichtbar. Home-Screenshot ohne private Informationen, nicht nur PUBLISHED protokollieren. Bei Unsichtbarkeit Diagnose getrennt nach Bindung, Consumer, Directory, Sichtbarkeit sichern; nicht pauschal neu einrichten. | NOT_TESTED |
| A58-WIDGET-02 | Entsprechend zehn Serien mit Provider-Covern. Beide Reihen nach Kodi-Neustart vorhanden und nach Katalogaktualisierung weiter nutzbar. Medienwidgets dürfen den Helper auch bei nicht erreichbarem Helper nicht abfragen. Frühere manuelle Medienkorrekturen außerhalb Widgets bleiben erhalten. | NOT_TESTED |
| A58-WIDGET-03 | Bisher nicht eingebundene Live-Home-Reihe erst nach Exit-PASS und eigener Zustimmung prüfen. Vollständige Startgruppe mit mindestens 88 Sendern; horizontal bis Ende navigieren. Fokus startet nichts, OK genau einen Sender. Fehlende EPG-/Sendungsbilder verstecken weder Logo noch Sender. Hero nicht automatisch installieren. | NOT_TESTED |
| A58-SAFE-01 | Portallogins/Passwörter, Gruppen, Startsender, Favoriten, manuelle Mappings, Provider-/XMLTV-Daten, dynamische/interne Cover, Resume, staffelübergreifendes Autoplay, bestehende Film-/Serienwidgets, Fernbedienung, Wizard und Skinshortcuts unverändert. Keine Box-A-Aktion. Nach erstem Live-Back-PASS zusätzlich Film-/Serien-Back testen. | NOT_TESTED |

## Diagnose richtig bewerten

PUBLISHED ist nur interner Snapshot. DIRECTORY/ITEMS stammt aus dem Pluginaufruf; ein generiertes Widget ist noch kein sichtbares Home-Bild. Der vorhandene Widgetstatus liefert consumer58 mit gehashtem Profilbezug, Hashwerten und festen Codes. BINDING_PRESENT heißt gespeicherter eigener Verweis; SKIN_CONSUMER_MISSING heißt kein belegter generierter Verbraucher; SKIN_CONSUMER_UNVERIFIED heißt unbekannte Include-Definition; SKIN_CONSUMER_HIDDEN erfordert eine tatsächliche Home-Laufzeitmessung. HOME_ITEMS_PRESENT beweist Einträge, weiterhin keine korrekt dekodierten Bildpixel. Ist Home nicht aktiv oder ein Dialog geöffnet, bleibt Home NOT_OBSERVED. Keine Profile zurücksetzen, um eine Diagnose zu erzeugen.

STOP58 unterscheidet vorbereitende Queue und native Stop-Queue. Die gespeicherte Session wird nur als Hash ausgegeben. Bei Freeze existiert möglicherweise keine bedienbare Diagnoseansicht; dann erst nach sicherem Neustart den privaten Kodi-Log untersuchen. Keine weiteren Starts bei unbestätigtem nativem Stop erzwingen.

## Ergebnisvorlage

Für jedes Gate genau PASS / FAIL / NOT_TESTED, installierte Version, Kodi-Version, Uhrzeit/Zeitzone und kurze Beobachtung eintragen. Für Live-Exit zusätzlich aktuellen Kompatibilitätsmodus, Zyklenzahl und ACK-Code; für Widgets sichtbare Anzahl und Bildquelle. Keine Rohlogs oder Screenshots mit Provider-URLs/Passwörtern veröffentlichen. Keine automatische Freigabe oder Issue-Schließung.

Unterstützende W58-01..09 aus #276: Quellenvertrag/Helper-Version, zehn Filme, zehn Serien, bestehende Bindungen, Live-Gruppe, Provider/Mapping, Exit und Bestandsschutz werden durch obige Gates abgedeckt. Das originale Hero-Opt-in bleibt separat und NOT_TESTED.
