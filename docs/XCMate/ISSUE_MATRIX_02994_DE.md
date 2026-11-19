# XCMate 0.1.29.94 – Issue- und Abnahmematrix

Stand 14.11.2026. **Implementiert/Host-PASS ist keine Android-Abnahme. Keine Issues automatisch schließen.**

| Auftrag | Implementierungsstand | Nachweis / Grenze |
|---|---|---|
| #458 / #457 – Provider-Default, globale Freigabe, Nachrüstung | Implementiert | Reproduktion .93 und neue Opt-out-/Persistenz-/DACH-Tests PASS; reale Anbieter- und DACH-Downloads ANDROID_NOT_TESTED |
| #458 – Job, ACK, Progress, Cancel/Retry | Implementiert | Hosttests und natives Kodi 720p/1080p PASS; echte Zeit-/Byte-/Parser-/Commit-/Readbackzähler, kein Fake-Fortschritt |
| #458 / #451 – Mini-EPG-Gruppen bei Teil-/Vollindex | Implementiert | Asynchroner gezielter Gruppenread ohne EPG; stale Future/Generation/Busy/Leere/100+-Sender im Testumfang; RK3528-Unterhaltung/4K ANDROID_NOT_TESTED |
| #458 / #454 / #443 – EPG-Rondell, Rohdaten, Readback | Implementiert mit Schutzgrenzen | 7d/20d, Streaming ohne Raw-Kopie, eigene Stage nach Commit weg, unabhängiger Readback; unbekannte Altlasten geschützt. Host-Bilanz vorhanden, kein Android-Platzgewinn behauptet |
| #452 / #454 – STOP/BACK und spontane Prozessabbrüche | Bestehende .93-Korrekturen übernommen, Hardwareursache offen | Linux-Regressionsgates; kein neuer Decoderfix oder Android-FIXED-Status |
| #433 – XMLTV-Bild, TMDB-/TVMaze-Save/Readback | Bestehende Umsetzung geschützt | Regressionsumfang erhalten; reale Sendungsbild-/Manuell-Zuordnung am Gerät ANDROID_NOT_TESTED |
| #427 / #161 – Abdeckung und manuelle EPG-Zuordnung | Additive Job-/Mapping-/Readbackdiagnose | Kein neuer kompletter Zuordnungsmanager; bestehende manuelle Mappings erhalten |
| #443 / #106 – Artwork USB/SMB/NAS, Installer-Speicherseite | Separat offen | Keine neue Migration in .94 und kein Installerwechsel |
| #435 / #436 – Widget-Restore-Plan-Retention | Separat offen | Keine ungeprüfte Löschung von Skin-Sicherungen |
| #450 – MP3-Albumcover | Separat offen | Bestehende MP3-Widgetfunktion erhalten |
| #444 – Home-Filmgruppenfilter | Separat offen | Keine Änderung der Bibliothek oder persönlichen Widgetpfade |
| #108 – allgemeine Artwork-/Katalogbereinigung | Separat offen | Nicht mit EPG-Raw-Lebenszyklus verwechseln |
| #411 – BINGIE-Redesign | Separat offen | Bestehendes Home, sechs Reihen/MP3, Logos und SkinShortcuts erhalten |
| #434 – Drive-Backup | Separat offen | Kein bestehender Drive-Ordner als fertige Sicherung ausgegeben |
| #449 – geschützter TMDB-Import | Separat offen | Vorhandener Token unverändert; keine Secrets in Paket/Protokoll |
| #417 – Joomla-/TMDB-Gateway | Ausdrücklich zurückgestellt | Nicht implementiert |
| Veröffentlichung / Main | Nicht freigegeben | Draft #460, ZIP und SHA; kein Merge und keine Änderung an Pilot/Regulär/NeoDark3 |

Vollständiger [Testbericht](TESTBERICHT_02994_DE.md), [Android-Matrix](ANDROID_ABNAHME_02994_DE.md), [priorisierter Originalbacklog](BACKLOG_PRIORISIERT_AB_02994_2026-11-14_DE.md).
