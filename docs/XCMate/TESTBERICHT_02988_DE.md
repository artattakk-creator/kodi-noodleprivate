# XCMate .88 – laufender Testbericht

Stand: Entwicklung, noch keine Freigabe. Basis und Ursachen: [Implementierung](IMPLEMENTIERUNG_02988_DE.md).

- 20 neue P0-Hosttests: PASS (2,695 s), darunter echtes lokales HTTP für dekodierte Bytes, URL-/Redirect-/SSRF-Checks, Low-Space/RAM, Ereignis-/Kontobindung, Merkliste, Reader-Lifecycle.
- Neue/übernommene Geometrie-/Branding-/Scope-Auswahl: 14 PASS (5,037 s). Native Reihen außerhalb des eigenen Hero bytegleich; Assetprovenienz und Logo-Rollback geprüft.
- Historische .87-Logo-Prüfungen an neue Semantik angepasst: sichere RAM-Anzeige ist READY, aber kein eigener persistenter Archivnachweis; 8 PASS (0,550 s).
- Erster vollständiger lokaler Diagnoselauf nicht abgeschlossen: unzureichender freier Testplatz für vorhandene 1-GiB-Reserve sowie ein auf kurzlebigen Worker ausgelegter alter Test. Kein PASS für diesen Lauf. Die alte Backoff-Prüfung wird mit geprüftem Ende des Readers ohne nicht vorhandene Schließmethode weiter vollständig ausgeführt.
- Vollständiger abschließender Host-/CI-Lauf und native 720p/1080p-Prüfungen: PENDING.
- Fünf-Minuten-Fake-Clock-Hosttest ist keine reale Zeit-/Texturabnahme. Separater nativer 305s-Test vorgesehen.
- Alle Android-Prüfungen: ANDROID_NOT_TESTED. Originalfoto 4 nicht als Datei verfügbar; kein visueller Referenz-PASS.

ZIP im Reviewpfad `test-builds/02988/`, SHA256 dort. Alle veröffentlichten .87-Kanäle und Setup .5.26 bleiben unverändert. Kein Merge/Release.
