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

## Geräte- und Logstatus

Die angehängten kodi.log und kodi.old.log können wegen der ausgefallenen Arbeitsumgebung nicht gelesen werden. **Analyse dieser privaten Anhänge: BLOCKED.** Es wurden keine Zeilen, Zeitpunkte, Fehlerhäufigkeiten oder privaten Inhalte daraus behauptet oder veröffentlicht.

Nutzerbeobachtungen (Helper-Fehler, fehlendes Home-Bild) sind dokumentiert. Die nachgewiesenen Codefehler sind reale Reparaturen, ihre Zuordnung zum konkreten neuen Android-Versuch und dessen verbleibende externe Ursachen sind noch nicht verifiziert. Echter TMDB-Zugriff, konkreter Helperzustand, Geräte-Bildanzeige und alle Android-Gates: **NOT_TESTED**.

Kein automatischer Merge, Release oder Eingriff auf Box A. Draft #319; GS-Media-Setup-PR #318 und Repo-PR #312 bleiben unabhängig.
