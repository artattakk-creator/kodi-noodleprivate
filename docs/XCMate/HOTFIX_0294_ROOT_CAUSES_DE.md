# XCMate 0.1.29.4 – Befunde vor Implementierung

Stand 21.10.2026. Basis PR #52 / `32970a6688c17f0aebd6945873658e5b41a47c5a`, Vergleichsversion 0.1.29.3 bleibt unverändert. Neuer Branch `fix/xcmate-0294-setup-scan-save`, unabhängig von PR #50/#51. [Vollständiger Auftrag](CODEX_AUFTRAG_0294_SETUP_SCAN_SAVE_DE.md).

## Im Quellcode nachgewiesen

1. `WorkWindow.work()` führt `Future.add_done_callback()` aus; bei noch laufender Arbeit läuft der Callback im Executor-Thread. Er ruft `status()`, `apply()`, `SetupWindow.saved()` und `WindowXML.close()` auf. Auch Scanstatus verändert direkt Controls aus dem Worker. Python-RLock macht Kodi-Windowoperationen nicht zu Operationen des Window-eigenen Python-Threads. Vorhandene QueuedPool-Tests lassen alle Callbacks auf dem Testthread laufen und verdecken den Fehler.
2. `SetupWindow.render()` erzeugt Checkboxen mit Unicode-Glyphen, ruft für jede Umschaltung `ControlList.reset()/addItems()` auf und stellt nur den Index wieder her. Das bewahrt keinen tatsächlichen Viewport. Reiter sind in derselben unteren Zeile wie andere Aktionen, die aktive Art hat keine dauerhafte Markierung. Fokusgrafiken referenzieren `white.png` ohne eigene im Add-on garantierte Ressource. Leere Bereiche haben keinen eindeutigen Status.
3. `http_stream(max_seconds=300)` und Stalker-Paginierung `monotonic()+300` brechen auch bei laufendem Fortschritt ab. Dies ist eine Gesamtlaufzeitgrenze, kein Inaktivitätsschutz. `stream_epg` setzt ebenfalls explizit 300 Sekunden; auch `xmltv_stream.parse()` hat eine eigene 300-Sekunden-Gesamtdeadline. Stalker erkennt nur unmittelbar wiederholte Seiten, keinen A/B/A-Zyklus. Socket-/Connect-/Read-Timeouts, begrenzte Decoder und Speicherbudgets sind davon getrennt.
4. `Draft.scan()` verwendet dieselben Stagingdatenbanken nach geänderter Auswahl erneut. Alte Gruppeninhalte können erhalten bleiben. `scanned` bildet außerdem nicht ab, ob Auswahl/EPG seit dem Scan geändert wurden.
5. `Draft.save()` kopiert mehrere Produktions-/Konfigurationsdateien, prüft aber nach Veröffentlichung nur die Portalliste über `portals.add()`. Gruppen, Inhaltszahlen, DB-Zuordnung und EPG-Konfiguration werden nicht vollständig zurückgelesen. `saved` ist ohne lokalen Save-Lock kein Schutz vor zwei gleichzeitigen Aufrufen. Der Profil-Schreiblock umfasst die gesamte große Datenkopie; lokale Transaktionen sind zwar kurz, der Konfigurationslock bleibt trotzdem lange gehalten.

## Nicht nachgewiesen

Der native Android-Kodi-Absturz nach „Speichern“ ist ein bestätigter Nutzerbefund. Ohne bereinigtes Crash-/Kodi-Log ist nicht bewiesen, dass der Worker-GUI-Pfad dessen einzige Ursache war. Keine Server-/Anmeldeursache oder SQLite-Korruption wird behauptet. Reale Android-/IR-/BINGIE-Abnahme bleibt offen.

## Umsetzungsvorgabe

Worker liefern nur Daten/koaleszierten Fortschritt. Ein Window-eigener, mit Kodi-Monitor betriebener Pump verarbeitet Ergebnisse und Fensteroperationen; echte Hintergrundthreads müssen im Regressionstest scheitern, sobald sie Controls berühren. Eigene PNG-Checkboxen/Fokustexturen und getrennte Reiter/Listen mit Native-Navigation. Keine Listenresets beim Toggle. Streaming ohne Gesamtdeadline, aber mit Inaktivitäts-/Socket-/Fortschrittsschutz und Abbruch. Frisches Staging, überprüfte Veröffentlichung und Readback, begrenzter Rollback ausschließlich der neuen ID. Keine Änderungen an gefrorenem Live-TV-/Remote-/Player-/Startsendercode, EPG-Bestandskonten oder fremden Add-ons.
