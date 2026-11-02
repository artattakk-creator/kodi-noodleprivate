# XCMate .70 – Testbericht und Abnahmestatus

Basis .69: 678 Quelldateien, 2844 bestehende Host-Testmethoden. Alle bleiben erhalten; die exakten .70-Änderungen werden über eine zusätzliche Audit-Normalisierung geprüft. Kein Test wird entfernt oder übersprungen. Ein alter API-Test erwartet nun ausdrücklich REQUESTED statt leerem Ergebnis nach erfolgreicher Intent-Übergabe; dessen Datei-/SQL-/Netzwerkverbote bleiben aktiv.

## Reproduktion und Tests

- Weiterhin gültige URL und negatives Suchergebnis nach mehr als 300 Sekunden verfügbar; echte Ablaufzeit, Profil- und Richtlinienwechsel sowie ungültige Zeitwerte weiterhin abgewiesen.
- Übergabe ohne ACK, anhaltendes Warten und wiederholter Fokus mit unverändertem ersten Anforderungszeitpunkt.
- Expliziter Wiederholungsmarker mehrfach an den Gates lesbar, einmaliger neuer Lookup; kein automatisches Verwerfen positiver Bilder oder Rate-Limits.
- Betroffene .69-Helper-Negative werden ereignisbezogen einmal neu geprüft, ohne Cache-/Datenlöschung.
- Eigene API-Ursache bleibt neben anschließendem Helper-Fehler nachvollziehbar; feste, pseudonymisierte Protokolle und Schutz gegen rohe Fehler-/URL-Ausgabe.
- Native Kodi-21.2-Linux/BINGIE-2.2.3-Prüfung erweitert: der echte Produktionsstatus des synthetischen RAM-only-PNG/JPEG wird um sechs Minuten gealtert, dann weiterhin im gemeinsamen Guide/Mini-Renderer, Hero und Details als native Pixel angezeigt. Keine reale Wartezeit simulieren oder API-/Android-PASS daraus ableiten.
- Kumulative .69/.68- und ältere Regressionen, native Medien-/Widget-/Player-Prüfungen sowie vollständige Host-Discovery bleiben CI-Gates.
- ZIP: Quellbytes/Manifest, CRC, Pfade, keine privaten Profile/Logs/DBs; SHA256 und GitHub-Actions-Artefakt.

Die endgültigen Zahlen, Commit, Laufzeit und Prüfsumme stehen nach erfolgreichem Paketjob in build-verification.json und test-results.log des Artefakts. Native JSON-/Screenshot-Belege liegen unter native-evidence/. Androidplan und Ursachenanalyse werden mitgeliefert.

## Vorher / Nachher

| Kontrollierter Fall | .69 | .70 |
|---|---|---|
| Gültiges Ergebnis mit 360 Sekunden altem Status | Anzeige verwirft Status, Worker überspringt gültiges Ergebnis | Anzeige und Worker nutzen tatsächliche TTL |
| Expliziter Retry bei RAM-Negativ | früher Cache-Return kann Auftrag abfangen | einmalige neue Prüfung, danach wieder begrenzter Cache |
| Request geschrieben, noch kein ACK | leeres Ergebnis / missverständliches NOT_SCHEDULED | REQUESTED / WAITING_SERVICE |
| Helper-Fehler nur im RAM | „Ergebnis für Sitzung vorgemerkt“ | kein bestätigtes Bild, Helper-/eigene API-/Speicherursache getrennt |

## Vollständige Testserie: Isolation und deterministische Eingaben

Im ersten vollständigen Lauf: 2868 Tests, drei FAIL. Zwei alte Suchtests hielten einen Reader aus einer vorherigen Test-Fixture fest: media_catalog43 erbte den durch sys.modules noch referenzierten alten library_index.Reader. Die gemeinsame Fixture lädt diesen Wrapper jetzt zusammen mit seiner Basisklasse neu; Fehler- und Query-Count-Prüfungen bleiben unverändert. Kein Such-Produktionscode wurde dafür geändert.

Der Hero-Idempotenztest wiederholte die Abfrage bei real fortschreitender Uhr, obwohl sich der erwartete Fortschrittswert dadurch ändern darf. Er fixiert jetzt ausdrücklich die Zeit für identische Eingaben; alle atomaren Bankwechsel-, Fokus- und Datei-/SQL-Verbote bleiben erhalten. Ein kombinierter Lauf nach den neuen Artwork-Tests prüft diese drei Alt-Testmodule zusätzlich im selben Interpreter.

## Abnahmematrix

| Bereich | Code-/Hostabnahme | Geräteabnahme |
|---|---|---|
| Status nach fünf Minuten und expliziter Retry | automatisierte Reproduktion, finale CI maßgeblich | NOT_TESTED |
| Helper-/eigene API-/lokale Katalogdiagnose | Quellen getrennt, keine Zugangsdaten | NOT_TESTED |
| BINGIE/Details: gültige Bildreferenz weiter anzeigen | native synthetische Bild-/Statusprüfung | NOT_TESTED |
| Tatsächlicher externer Helper-/TMDB-Zustand dieser Box | OPEN, private Anhänge derzeit nicht lesbar | NOT_TESTED |
| Legacy-Archiv-/Speichermodi | unverändert geerbt, kein globaler Umbau in diesem Status-Hotfix | NOT_TESTED |

## Geräte- und Logstatus

Die angehängten kodi.log und kodi.old.log können wegen der ausgefallenen Arbeitsumgebung nicht gelesen werden. **Analyse dieser privaten Anhänge: BLOCKED.** Es wurden keine Zeilen, Zeitpunkte, Fehlerhäufigkeiten oder privaten Inhalte daraus behauptet oder veröffentlicht.

Nutzerbeobachtungen (Helper-Fehler, fehlendes Home-Bild) sind dokumentiert. Die nachgewiesenen Codefehler sind reale Reparaturen, ihre Zuordnung zum konkreten neuen Android-Versuch und dessen verbleibende externe Ursachen sind noch nicht verifiziert. Echter TMDB-Zugriff, konkreter Helperzustand, Geräte-Bildanzeige und alle Android-Gates: **NOT_TESTED**.

Kein automatischer Merge, Release oder Eingriff auf Box A. Draft #319; GS-Media-Setup-PR #318 und Repo-PR #312 bleiben unabhängig.
