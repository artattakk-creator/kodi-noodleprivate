# Issue #474 – Disney Channel: quellensichere manuelle EPG-Zuordnung

## Umfang und Quellstand

Draft-PR: https://github.com/artattakk-creator/kodi-noodleprivate/pull/478

Produktimplementierung: `c8de1da626f6cb0dc377296cd9cd859a4dfa6785`, Branch `fix/issue474-source-qualified-epg-save`, vollständige .96-Basis `e651a2afbb1edb0d7b3ebe25e3b08860e6e6ee81` aus #471. Der PR ist bewusst auf dessen Sourcebranch gestapelt. Aktuelles `main/src` enthält noch .92; Pilot enthält bereits .96. Kein stiller Downgrade und kein Sammelimport aller .96-Änderungen in diesen fachlichen Fix.

Keine neue Versionsnummer und keine Veröffentlichung: Das aktualisierte .96-Paket ist ausschließlich ein unveröffentlichter Review-Build. Die bestehenden Kanalpakete, Installer, Modell-B-Branch #472 und Sourcebranch #471 sind unverändert. Die ältere unveränderte .96-Sicherung bleibt über den Basiscommit erreichbar; ihr ZIP-SHA256 lautet `249d7908d83cf7808d950e938e572fc046c2b0fc767aeebd3195b18b87b9d740`.

## Bestätigte Ursachen, nicht mit Gerätehypothesen verwechseln

1. Der lokale Reader deduplizierte Programmreihen anhand der XMLTV-Kanal-ID, obwohl zwei Sender dieselbe ID in unterschiedlichen Quellen verwenden können. Im echten SQLite-Repro bestimmten Senderreihenfolge und Fallback den falschen/fehlenden Datenstand. Die Korrektur hält flüchtige Views pro stream_id und Quelle; keine neue Datenbank und keine Datenmigration.
2. Bisher erfolgten Schreibvorgang und unabhängiger Readback nicht als eine geschützte Transaktion. Ein Readback-Fehler konnte bereits veränderte Persistenz hinterlassen.
3. Der Dialog bestätigte das Speichern vor der tatsächlichen Aktualisierung der aufrufenden Ansicht. Der große Guide startete erst nach Dialogende eine asynchrone Aktualisierung. Eigene Erfolgsmeldung fehlte.

Diese reproduzierten Codefehler beweisen nicht nachträglich die Ursache des unaufgezeichneten Android-Vorgangs gegen 20:58. Das vorliegende Backup endet um 18:25. Fehlende manuelle Zuordnungen darin sind kein Beweis des späteren Fehlers. Ebenso sind Settings-XML- und SQLite-Timeout-Ereignisse kein automatischer Kausalnachweis.

## Umsetzung

- `local_epg`, `epg_views`, `guide_grid_data`, `programme_snapshot47`, `epg_fallback67`, `tv_data`: sender-/quellenqualifizierte Full-/Text-/RAM-/retained-facts-Views, source-sicheres Now/Next und Grid, unveränderte Legacy-Dict-Schnittstelle. Explizite manuelle Identität bleibt auch bei legitimen Programmlücken erhalten.
- `epg_binding48`: bestehende Profilsperre und atomarer JSON-Store; ausgewählte Tupel schreiben, kalt unabhängig lesen, RO-Ansicht vorbereiten. Unbekannte Konfigurationsfelder und andere Portale/Sender erhalten. Bei Fehlern ausschließlich eigenes, noch unverändertes Tupel zurückrollen. Neuere fremde Auswahl niemals überschreiben.
- `mapping_context96`, `guide_mapping48`: vorhandener Worker führt Schreiben/Readback/Ansichtsvorbereitung aus; GUI-Owner wendet den verifizierten Stand an und bestätigt erst danach sichtbar. SQLite-Interrupt ist kein leeres erfolgreiches EPG. Veraltete oder profilfremde Receipts werden abgewiesen; kein SQL/HTTP/JSON-Read im GUI-Bestätigungsabschnitt. Dort nur begrenzte bestehende Profilsperre und eine Dateimetadatenprüfung.
- Fehlversuch: Dialog offen, fester Diagnosecode ohne private Exceptiontexte, ursprüngliche Zuordnung wiederhergestellt, soweit eindeutig. Unbestätigter Rollback/Konflikt ausdrücklich als unsicher gemeldet. Mini-Vorschau kann nach vorübergehendem Renderfehler erneut verwendet werden.
- Bestätigter Erfolg: tatsächlicher Eltern-View aktualisiert, sichtbare Meldung „EPG-Zuordnung gespeichert und geprüft“, manuelle Grid-Kennzeichnung. Bestehende Revision signalisiert Now/Next-/Hero-Readern den Wechsel. Kein neuer Player-/Routing-/Servicepfad.
- Abgebrochene Elternsitzung: noch nicht bestätigte Worker-Receipts werden selektiv zurückgerollt statt nachträglich stillen Erfolg zu erzeugen.

## Unabhängiger Review

Ein separater, ausschließlich lesender Reviewer prüfte Implementierung und Anforderungen in isolierter Kopie. Er fand vier verbleibende Befunde: P1 geschluckter SQLite-Abbruch, P1 fehlende gewöhnliche Exception-Bereinigung, P2 veraltete/profilfremde Bestätigung und P2 verlorene Mini-Preview-Epoch nach Fehler. Zuvor hatte er den Grid-Fehler `state` statt `code` identifiziert.

Alle Befunde wurden anschließend durch den Autor real RED reproduziert, korrigiert und mit gezielten GREEN-Tests abgesichert. Der unabhängige Bericht lautete zunächst **changes required**; es wird kein zweiter unabhängiger Gesamt-Review behauptet. Die dokumentierte Schließung ist Autor-Nachprüfung. Der Reviewer selbst änderte keine Dateien.

## Testnachweise

- Neue Regressionen: 11 Quellen-/Viewtests und 17 Speicher-/GUI-Tests, darunter Disney plus zwei weitere Sender, umgekehrte Reihenfolge, Quellenkollision, Reimport, frische Reader, gespeicherte leere Quelle, Real-Grid-/Mini-Anwendung, Schreib-/Readback-/Renderfehler, konkurrierende Auswahl, Profilwechsel, Retry und späte Worker.
- Gezielte betroffene Suite: **59 PASS in 4,16 s**. Zusätzliche Cold-Publication-/Issue474-Suite nach Vertragskorrektur: **38 PASS in 5,40 s**.
- Der alte Cold53-Test erwartete eine Exception aus Kodis onClick. #474 verlangt stattdessen sichtbare, retryfähige Fehlerbehandlung. Die ursprüngliche Byte-Unverändert-Invariante bleibt; zusätzlich werden genau ein Publikationsversuch, offener Dialog, `saved=False` und sichtbarer Fehlercode geprüft. Kein Skip, XFAIL oder Verschlucken eines Test-Exitcodes.
- Vollständige unittest-/pytest- und CI-Ergebnisse: Abschlussnachtrag unten. Kein Zwischenlauf wird als finaler Erfolg dargestellt.
- Sprachdateien: **17 Kataloge PASS**.
- Paket: 899 Dateien, 4.767.331 Bytes, CRC PASS, bytegenauer Sourcevergleich PASS, reproduzierbarer Build PASS.

### Native Kodi-Verifikation

https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44056443448

| Ziel | Ergebnis | Beleg |
|---|---|---|
| Kodi 21.2 Linux, 1280×720 | PASS | Job 133946938783 |
| Kodi 21.2 Linux, 1920×1080 | PASS | Job 133946938633 |
| Echte Android-RK3528-Box | ANDROID_NOT_TESTED | Kein physischer Zugriff/keine Geräteabnahme behauptet |

Die nativen Läufe entpacken exakt das Test-ZIP, zeigen den echten Kodi-Mappingdialog und prüfen Vorschau ohne Byteänderung, Abbruch, Save-Cold-Readback, Anwendung im tatsächlichen GuideSnapshot sowie absichtlich fehlgeschlagenes Schreiben bei offenem Dialog und unveränderten Dateibytes. Datenquelle ist ein synthetischer Loopback-XMLTV-Server, Elternbesitzer ein synthetischer Mini-Adapter-Owner. Das ersetzt weder echte Fernbedienungs- noch Provider-/Android-Abnahme.

Lokaler zusätzlicher Docker-Versuch war durch den Speicherplatz der Entwicklungsumgebung blockiert. Ausschließlich der eindeutig diesem fehlgeschlagenen Build zugehörige Cache `3bxt3mj8g6qhdktf4ebd2c91s` wurde freigegeben, keine allgemeinen Prune-/Profil-/Backup-Löschungen. Die oben genannten erfolgreichen nativen Nachweise stammen tatsächlich von GitHub-Runnern mit ausreichendem Platz.

## Review-Paket

ZIP: [plugin.video.xtreammate-0.1.29.96.zip](test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip)

SHA256: `64d08c78581d074a9c86fee26ba94011119c1ab0f297de6a0bc9afee13cf1ba9`

Prüfsummendatei: [plugin.video.xtreammate-0.1.29.96.zip.sha256](test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip.sha256)

Kein reguläres Kodi-Update verfügbar gemacht. Automatischer Versionsvergleich kann einen gleichnummerierten .96-Reviewbuild nicht als neue Version erkennen. Keine Deinstallation, kein Profilreset oder Downgrade empfohlen. Ein gezielter Gerätetest dieses Pakets erfolgt nur nach Nutzerentscheidung; vorher eigenes gültiges Profilbackup erhalten.

## Android-Abnahme – alle zunächst ANDROID_NOT_TESTED

| Gate | Tatsächlicher Ablauf |
|---|---|
| MAP474-01 | Disney im großen Guide → EPG zuweisen → Quelle und Kanal wählen → echte Vorschau; Zurück erhält alte Zuordnung/Ansicht. |
| MAP474-02 | Erneut auswählen → Speichern: sichtbare Bestätigung erst nach Aktualisierung; manueller Hinweis, richtige Sendung im Grid. |
| MAP474-03 | Mini-EPG am Disney-Sender zuweisen und speichern; Now/Next, Zeit-/Gruppen-/Fokusposition stimmen. |
| MAP474-04 | Zwei Quellen mit gleicher Kanal-ID vergleichen, zusätzlich zwei andere Sender; keine gegenseitige Überschreibung. |
| MAP474-05 | Dialog schließen/erneut öffnen, Gruppe wechseln, Home-Hero und Now/Next prüfen. |
| MAP474-06 | Kodi neu starten, Senderlistenrefresh und später normalen XMLTV-Import ausführen; bestätigte Zuordnung bleibt Quelle+Kanal. Nicht ungefragt einen Import starten. |
| MAP474-07 | In sicherer Testkopie fehlende Schreibberechtigung/Busy/Readbackfehler: Fehler sichtbar, Dialog offen, alte Konfiguration unverändert. Auf echter Box keine Rechte oder Daten absichtlich beschädigen. |
| MAP474-08 | Live/Film/Serie/Back, manuelle Bilder, TMDB-Token, Portale, Favoriten, Benutzerwidgets und SkinShortcuts unverändert. |

## Separate Folgearbeiten

- #468: Settings-/Extraktionsintegrität, tatsächliche Ursache ungültiger XML-Dateien und konkurrierende Kodi-Settings-Writes; .96 besitzt bereits Schutz/Readback/Bestätigungs-Recovery. Kein blindes altes Profil wiederherstellen und keine Consent-Defaults erraten.
- #464 / #467: globale EPG-Readbudgets, Busy/Lock-Ownership und gruppenweise Snapshot-Performance getrennt messen und korrigieren. Der Save-Fix macht einen Timeout sichtbar, er behebt nicht pauschal alle Geräte-Timeouts.
- #479: auf unverändertem main reproduzierte alte Archiv-/Pilot-CI-Baselines; getrennt vom Produktfix und von Automatisierung #477.
- Automatisierung #477 bleibt ungemergt/PREPARED_NOT_ACTIVE. Kein API-Key, kein kostenpflichtiger Runner und keine Veröffentlichung.

## Abschlussnachtrag

Vollständige Laufresultate werden nach tatsächlichem Abschluss mit geprüftem Commit-SHA ergänzt. Bis dahin ist der Draft ausdrücklich noch kein Merge-/Android-Freigabenachweis.
