# XCMate 0.1.29.94 – Implementierungsstand

Master #458, kumulativer Entwicklungszweig; **kein Merge, kein Release**.

## Überprüfte Basis

- main `85c9f1b9dc4aafea6eae6a055961ff159ad6e254`: Source .92, Pilot .93.
- Vollständiger .93-Source-PR #455 `f2e87846fe63b75b16916f1b9121aaee49553a8e` lokal übernommen, nicht nach main gemergt.
- Source/Pilot-Paket .93: 876 ZIP-Mitglieder bytegleich; SHA256 `48e0822827c2a8e8a854a812cbac0d0fb3407f6f6b9a5c3c2c2213f20fe77a95`.
- Beide vollständigen Übergaben aus Dokumentations-PR #459 übernommen. Getrennte Roadmap bleibt erhalten.
- .90-Fallback, vorhandene .93-Pakete, Installer 0.5.26 und sämtliche Repository-Kataloge unverändert.
- Während der Entwicklung wurde main durch den separat freigegebenen Archivierungs-PR #461 auf `b830fad1a19247cc08750970dc56edae0b8c2361` aktualisiert. Dieser Stand ist ausschließlich in den .94-Featurebranch eingeflossen. Die 227 dort archivierten historischen Binärdateien werden nicht wieder veröffentlicht. Historische Tests lesen ihre im Archivdokument festgelegten, hashgeprüften Originalbytes nur in einem wegwerfbaren Testklon aus Git. Aktive .90/.93-Pakete und Kataloge bleiben bytegleich zu main `b830fad1`.

## Bestätigte Ursachen und Änderungen

1. Neue Xtream-Drafts starteten mit `provider_epg=False`; beim Speichern wurde dadurch `epg_show=False`. Der neue Default verwendet ausschließlich die konfigurierte Adapter-XMLTV-Adresse. Explizites globales/Provider-Opt-out wird separat gespeichert und beim Resume erhalten. Unbekannte alte Abschaltzustände werden nicht als Zustimmung interpretiert.
2. Nachgerüstete Quellen entfernten keine globale EPG-Sperre. DACH-Paket und benutzerdefinierte/internationale Quellen fragen erforderlichenfalls ausdrücklich nach Reaktivierung. Vorhandene Quellen bleiben idempotent.
3. Window-Property bedeutete nur „angefordert“. Private atomare Auftragsdatei, UUID, echte Worker-Lock-ACK, 15-Sekunden-Annahmefrist, Abbruch und getrennte Quellenphasen ergänzen denselben Importer. Empfangene HTTP-Bytes werden vor Content-Encoding-Dekompression gezählt. Ohne zuverlässige Gesamtgröße gibt es keine Prozentbehauptung.
4. Reguläre Veröffentlichung hatte kein vollständiges unabhängiges Source-Readback. Der Datensatz-Hash wird innerhalb der Commit-Transaktion erzeugt und über eine neue read-only SQLite-Verbindung mit Quelle und Revision verglichen. Doppelte XMLTV-Zeilen werden nicht als zusätzliche gespeicherte Datensätze gezählt.
5. EPG-Manager baute alle zwei Sekunden die gesamte Quellenliste mit DB-Inventur neu. Nun werden ListItems anhand stabiler Quellenschlüssel aktualisiert; Statuspolls lesen nur kleine Auftragsdateien asynchron. Einzelne Quellen haben reale Zähler, Spinner und gegebenenfalls einen Bytebalken. Schließen ist kein Cancel.
6. Fehlende Mini-EPG-Gruppen wurden ausschließlich bei gesetztem Partial-Flag nachgeladen. Gezielter asynchroner lokaler Gruppenread funktioniert auch bei vollständigem, aber unvollständigem/stalem Hauptindex. Vier Gruppenstatus, Generation-/Portal-/Indexidentität, begrenzte Retries und Cache schützen vor falschen Leerlisten.

## Speichervertrag und Grenzen

Streaming legt keine vollständigen Rohdateien an. Deshalb ist die korrekte unmittelbare Raw-Bilanz **0 Dateien / 0 Bytes**. Nach Commit und Readback wird die reale gleiche Volume-ID einschließlich `statvfs.bavail` und getrennten DB/WAL/SHM-Klassen protokolliert. Unbekannte Rohdateien bleiben `SKIPPED_UNPROVEN`. Vorhandene journalisierte .93-Backuprotation und begrenzte .92-Retention bleiben erhalten; Upgrade-Wartung wird für .94 erneut fällig. Kein blindes VACUUM und kein manuelles Löschen aktiver WALs.

## Prüfung

Erste unveränderte .93-Reproduktion: drei gezielte FAIL, bewusstes Opt-out PASS. Der vollständige lokale Lauf besteht **3.975 unittest-Tests**, einschließlich 27 gezielter .94-EPG-/Gruppentests; zusätzlich bestehen elf pytest-Brandingtests und die Validierung aller 17 PO-Kataloge. Testklon und Lauf sind im Protokoll mit dem geprüften Source-Commit ausgewiesen. Die archivierten Eingaben verkleinern weder Testauswahl noch Assertions. Ein sauberer, bereits vollständig getesteter Source-Stand ist Voraussetzung des Klon-Runners; uncommittete Codeänderungen werden abgelehnt.

Native Linux-Kodi-21.2-Läufe in **1280×720 und 1920×1080** bestehen mit dem exakten .94-ZIP: reale GUI-Aktionen für Aktualisieren, Abbrechen und Zurück; gzip-/HTTP-Bytezähler; echte Worker-ACK; 600 gespeicherte und unabhängig erneut gelesene Programme; eine Senderzuordnung; erhaltener Fokus und LastGood. Die Quellenliste wird nicht neu aufgebaut. Screenshots und maschinenlesbare Resultate stehen unter [reports/02994](reports/02994). Synthetische Loopback-Quellen ersetzen ausdrücklich keine Prüfung der privaten Providerverbindung oder öffentlicher DACH-Feeds auf Android.

Der GitHub-Volltest einschließlich vollständigem pytest-Lauf und bestehender langer Kodi-Regressionsprüfungen ist als PR-Gate eingerichtet. Den jeweils letzten CI-Stand zeigt [PR #460](https://github.com/artattakk-creator/kodi-noodleprivate/pull/460/checks); zeitgebundene Nachweise und Grenzen enthält der [Testbericht](TESTBERICHT_02994_DE.md). Alle echten Android-Prüfungen bleiben **ANDROID_NOT_TESTED**.

Nicht als behoben behauptet: RK3528-Decoderfreeze, selbstständiger Android-Prozessabbruch, Kodi-App-Präsenz nach Werksreset. Hier fehlen neue reale Android-Belege. USB/NAS-Migration, MP3-Alben, Google Drive, Widget-Restore-Altlasten und Redesign werden weiterhin separat bearbeitet; Joomla-Gateway bleibt zurückgestellt.
