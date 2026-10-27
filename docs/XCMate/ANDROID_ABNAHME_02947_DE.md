# XCMate .47 – Android-Abnahme #244 und #245

**Alle neuen .47-Fälle NOT_TESTED.** Ausschließlich Box B: Kodi21.3/RK3528 ARM32/Titan BINGIE MOD2.2.3; tatsächliche Android-Geräteanzeige privat festhalten. Box A unverändert. Update nur bewusst vom Nutzer über die vorhandene .46, keine Deinstallation, kein Downgrade, kein Profil-/Cache-/DB-Reset.

Historisch .46: Live88 vollständig horizontal PASS; Livegrafiken FAIL; Filme leer FAIL; Serien24 PASS. Zwei native Stop-Rückkehrbestätigungen, einmal RETURN_BLOCKED, kein vollständiger neuer Player-Gesamt-PASS. Diese Befunde werden nicht als .47-Ergebnis übernommen.

## Vorbereitung

- Kandidatenversion/Commit/ZIP/SHA prüfen. `live_exit_fullscreen42=EIN`, dynamischer Artworkmodus, Startsender/-gruppe, drei Widgetquellen und Portal-/Favoriten-/Resume-/EPG-Werte privat vorher/nachher vergleichen.
- Bestehende Widgets **nicht neu binden**. Keine fremden Add-ons deaktivieren, Skin-Dateien ändern oder Keymaps bearbeiten. Fehlender Skin-Hook bleibt BLOCKED; Adapter ausschließlich nach gesonderter bewusster Freigabe.
- **Kein EPG-Refresh/Neuimport, Cleanup oder bestehender DB-Umbau ohne tatsächlich verifiziertes BACKUP_VERIFIED und gesonderte Freigabe.** Zunächst ausschließlich vorhandene Daten lesen.
- Nach einem Kodi-Hänger keine weiteren Start/Stop-Zyklen. Private Rohlogs/URLs/Tokens/SMB-Daten niemals öffentlich anhängen; nur sichere WIDGET47/FLOW46/PREPARE47-Codes, Zählwerte und Zeiten übertragen.

## Zuerst Datenfluss und Sichtbarkeit

| Fall | Ausführung und Erwartung | .47 Box B |
|---|---|---|
| DATA47-01 | Home mit den bestehenden drei Reihen öffnen. Filme sind echte unterschiedliche Portaltitel mit korrekten Namen; Serien unverändert24; aktive Livegruppe vollständig. Kein generisches XCMate-Icon als vermeintlicher Film. | NOT_TESTED |
| DATA47-02 | In Widgetstatus INDEX/SELECT/ITEMS/DIRECTORY vergleichen. Filme: tatsächliche Datensätze/ListItems, bis24; SQL_GROUPS/V2_KEYS/PAYLOAD ohne dauernden BUDGET/0.−1 ist unbekannt, nicht Null. | NOT_TESTED |
| DATA47-03 | Livegruppe mit den bisher88 Sendern bis zum letzten Eintrag horizontal bedienen. Startsender genau einmal, keine12er-Grenze; richtige drei Senderklickziele. | NOT_TESTED |
| DATA47-04 | Serienreihe: gleiche24 realen Serien/Poster, drei korrekte Detail-/Staffelklicks, kein zusätzlicher generischer Eintrag. Historischer PASS schützt die Funktion, ersetzt diesen neuen Retest nicht. | NOT_TESTED |
| ART47-01 | Mindestens drei tatsächlich verfügbare Senderlogos vorne und drei weiter hinten der Gruppe sichtbar. Bei fehlendem Logo steht richtiger Sendername. Dynamische URLfreigabe ist noch kein Bild-PASS. | NOT_TESTED |
| ART47-02 | Film-, Serienepisoden-, Nachrichten-/Talksendung prüfen: genau passendes Ereignisbild oder ehrlicher Fallback. Kein beliebiges Episodenbild und keine fremde Sendung. | NOT_TESTED |
| ART47-03 | Im grafischen EPG separates kleines Logo oben links über dem Bild. Dasselbe im Livewidget bei vorhandener tatsächlicher BINGIE-Bindung. Fehlt sie: BLOCKED_NO_OVERLAY_FOCUS_BINDING, keine automatische Skinänderung. | NOT_TESTED |
| ART47-04 | Native Livekachel ohne verifiziertes Programmbild zeigt vorhandenes Senderlogo; grafische Ansicht behält neutralen Programmfallback und Logo/Name. Fehlende Quelle/Datei, DNS/Netz, Decoder und Skin getrennt notieren. | NOT_TESTED |

## Einmaliger sicherer Live-Rückweg vor weiteren Wiedergabetests

| Fall | Ausführung und Erwartung | .47 Box B |
|---|---|---|
| STOP47-01 | Genau einen Startsender starten → einmal Back aus reinem Vollbild. Bild/Ton enden, Voransicht bedienbar. Offene Overlays schließen zuvor nur ihre Ebene. Bei Hänger sofort weitere Tests stoppen. | NOT_TESTED |
| STOP47-02 | Falls im normalen Einzelvorgang eine Verzögerung entsteht: PLAYER_STOP_DONE, STOP_DONE, HOME_REQUESTED/HOME_REUSED und eventuelle RETURN-/PLAYER_STATE-Codes getrennt protokollieren. Kein weiterer Stop und kein neues Starten zum Erzwingen. | NOT_TESTED |
| STOP47-03 | Erst nach STOP47-01 PASS: Film und einzelne Episode jeweils einmal beenden; richtige Voransicht und Fokus. Keine neue20er-Stressserie ohne Regres­sionsbedarf beziehungsweise bewussten Nutzerauftrag. | NOT_TESTED |

## Gemeinsamer Guide / Bilder / lokale Daten

| Fall | Ausführung und Erwartung | .47 Box B |
|---|---|---|
| ID47-01 | Einen aktuellen Sender vergleichen: Widget, großer EPG/Programmdetails, Mini-EPG und Infoleiste haben dieselbe Sendung, Zeit und Beschreibung; gemeinsame Eventkennung in der Diagnose. Manuelle Zuordnung gewinnt. | NOT_TESTED |
| ID47-02 | Natürlichen NOW→NEXT-Wechsel beobachten: Titel/Zeit/Progress/Eventkennung/Bild wechseln zusammen. Fehlender nativer Reload-Hook bleibt BLOCKED_NO_RELOAD_HOOK. Kein Neu-Binden/erzwungener Refresh. | NOT_TESTED |
| ID47-03 | Vorhandene Tage−1/−2/−7 sowie+10/+15/+20 nur bei tatsächlich gespeicherten Daten öffnen. Fehlende Feeddaten BLOCKED_DATA_NOT_AVAILABLE; keinen Feedabruf als Abkürzung. | NOT_TESTED |
| ID47-04 | Widgetstatus zeigt konkrete Bestückung: Fakten/Events/Kanal-/Artrefs, Text-ohne-Bild versus leere DB; Bilddecoder verfügbar oder fehlend. READY/Referenz allein ist kein visueller PASS. | NOT_TESTED |
| ID47-05 | Nach normalem Kodi-Neustart vorhandene Texte, verifizierte Programmbilder und bewusste Coverwahl erhalten; bestehende Mappings/Settings gleich. Kein zusätzlicher USB-/SMB-/Löschtest. | NOT_TESTED |
| ID47-06 | Offlinefallback nur bei bewusst sicherem Zustand ohne laufende private Aufnahme/anderen Stream prüfen. Texte und vorhandene lokale Bilder bleiben; dynamische nicht gecachte Cover dürfen einen ehrlichen Fallback zeigen. | NOT_TESTED |
| ID47-07 | Ein später ausdrücklich freigegebener EPG-Import aktualisiert nur geänderte Events und betroffene Bilder; andere Quellen/Archiv bleiben. Bis Backupnachweis/Freigabe BLOCKED_BACKUP_REQUIRED. | NOT_TESTED |

## Medien und Covermanager

| Fall | Ausführung und Erwartung | .47 Box B |
|---|---|---|
| FILM47-01 | Drei verschiedene echte Filmkacheln: richtiger Film/Poster/Metadaten, Start/Back mit nutzbarem Fokus. Keine Serienverwechslung oder fremdes Portal. | NOT_TESTED |
| SER47-01 | Drei Serienziele/Staffeln unverändert; eine echte Episode und natürliches Autoplay einschließlich Staffelwechsel, Resume und bewusster Stop ohne Autoplay. | NOT_TESTED |
| PICK47-01 | Film und Serie: Covermanager mit echten grafischen Miniaturen; Poster/Backdrop getrennt, größere Vorschau, Übernehmen→explizit Speichern. Kein Platzhalter als Grafik-PASS. | NOT_TESTED |
| PICK47-02 | Gewählte Bilder in Kategorie/Details/Wiedergaberückkehr und nach normalem Neustart gleich. Gemeinsame lokale Anzeigereferenz vorhanden; Originaldatei und bestehende Wahl bleiben erhalten. | NOT_TESTED |
| PICK47-03 | Abbrechen/schneller Wechsel/keine Kandidaten/natürlicher Netzfehler: keine falsche Übernahme und keine globale Retry-/Löschaktion. Optionales TMDb nur mit tatsächlich vorhandener Nutzerkonfiguration. | NOT_TESTED |

## Performance getrennt messen

| Fall | Ausführung und Erwartung | .47 Box B |
|---|---|---|
| PERF47-01 | Normaler Kaltstart und mindestens fünf warme Liveklicks: ROUTE_ENTRY→PLAYBACK_REQUEST→FIRST_VIDEO, PREPARE47-Startgruppenmodell, GROUPS_READY und MINI_EPG_VISIBLE getrennt notieren. Anzahl/p50/p95 berichten; keine Hostzeiten als Androidwerte. | NOT_TESTED |
| PERF47-02 | Filme und Serien getrennt kalt/warm: Klick→DETAIL_READY→DETAIL_METADATA_READY→RESOLVE_BEGIN→FIRST_VIDEO. Serienregression ausdrücklich prüfen. | NOT_TESTED |
| PERF47-03 |20 normale D-Pad-Bewegungen vorne/hinten der Livegruppe: Fokus/Back reagieren, keine pro-Fokus-HTTP-Abfrage und kein synchroner DB-Vollscan. Zeitmessung von sichtbarer Bedienung getrennt vom Playerbild. | NOT_TESTED |

## Bestandsschutz

| Fall | Ausführung und Erwartung | .47 Box B |
|---|---|---|
| REG47-01 | Sieben Einstellungen/PIN6666, Original-Icon, Suchmaske, Sendergruppen/Startsender, Portale/Favoriten/EPG-Mappings und IR-Tasten unverändert. | NOT_TESTED |
| REG47-02 | Normale Film-/Seriensuche mit Postern, Details/Back und Trefferfokus; großer EPG-Senderstart, Mini-Gruppen-Rail und eigene Info-/Player-Leiste. | NOT_TESTED |
| REG47-03 | Vorhandene .46-Gesamtabnahme zusätzlich gemäß ANDROID_ABNAHME_02946_DE.md fortführen. Dortige echte historische Ergebnisse bleiben erhalten; offene Fälle nicht vorausfüllen. Keine Daten-/Profil-/Cache-Resets. | NOT_TESTED |

Pro Fall Datum/Uhrzeit Europe/Berlin, Version/ZIP-SHA, tatsächliche Box-/Kodi-/Skinversion, Schritte/Beobachtung und PASS/FAIL/NOT_TESTED/BLOCKED festhalten. Ein gemeinsamer Widget-/Guide-Gesamt-PASS erfordert tatsächliche Bilder und passende Informationen auf beiden Oberflächen. Issues bleiben offen; kein automatischer Merge.
