# XCMate .65 – Technischer Test- und Releasebericht

Verbindlich ist der endgültige grüne CI-Lauf am exakten PR-HEAD. Zwischenstände sind kein Releasebeleg.

- Vollständiger .64-Bestandsschutz: 644 ursprüngliche Quelldateien, 2.618 vorhandene Testmethoden und ihre Skip-Bedingungen bleiben erhalten. Nur komplette exakt hinterlegte Deltas werden normalisiert.
- Token: echte synthetische private Profile mit gesperrtem Root-Listing, fehlenden Unterordnern, Directory-Flag-Fallback, O_PATH, Symlink/Elternschutz, bestätigter/abgelehnter Recovery, Inode-Race, vorhandener ungültiger Datei, errno/Subcodes und Logredaktion. Sicherungen und Symlink-Ziele bleiben erhalten.
- Katalog: Film/Serie, 0/1/48/100/1.205 Einträge, zwei Portale, vollständiges Paging/Count/Search/Widget, fiktive Adult-Zone-Bezeichnung ohne Filter, numeric IDs 0, leere/fremde Antworten, kalter Offline-Cache, Legacy-Teilsnapshot, Head-Schutz, Abbruch/Crash/Lease, gezielter Retry ohne alten Phantom-Erfolg.
- Medienoberfläche: sichtbarer fernbedienbarer Indexstatus für beide Arten, Auswahl/Count getrennt, keine Remote-Verfügbarkeit aus CACHED vortäuschen, Cancel nur einer Kategorie.
- EPG: gespeicherte DMAX/WELT/VOX/Nitro-Fixtures, Warm-Handoff ohne SQL/HTTP, Mapping-/Portalwechsel, teure Metadaten ohne Verlust anderer Sendertexte, echte SQLite-Sperre und kein Kompatibilitäts-Vollreload bei Contention.
- Vorher/Nachher: tools/benchmark_xcmate65.py lädt die exakt eingefrorenen .64-Quellen aus dem geprüften Schutzmanifest. Root-Verweigerung und SQL-Zugriffe im warmen Home werden gegen .65 gemessen. JSON im CI/nativen Belegartefakt; keine Android-Latenzmessung.
- Alle bisherigen sieben nativen Kodi21.2/Linux-Strecken einschließlich BINGIE2.2.3, Skinshortcuts2.1.0, vollständiger Live-Gruppe, zehn Serienpostern und Fokusframes bleiben Pflicht.
- Kanonisches ZIP: Quell-Bytevergleich, CRC, sichere/eindeutige Pfade, kein privater Zustand, Manifestversion und regulärer Repositoryindex samt MD5. Neue SHA256 aus dem endgültigen Paket.
- Release erst nach gesamter grüner Regression, keinem behind-Stand, geprüftem Secret-/Code-Diff und mergeable=true. Regulärer Merge mit erwartetem HEAD. Danach Publish bis Ende prüfen; main/src, addons.xml, addons.xml.md5 und reguläres ZIP müssen übereinstimmen.

Konkrete CI-Links, Testzahlen, Messwerte, SHA256, Commit und Publikationsnachweis im Abschluss von PR #299 / Master #298. Bei rotem Gate bleibt PR offen und Status BLOCKED. Keine erzwungenen Statuschecks oder grünen Ersatzbehauptungen. Android A65-01 bis A65-08 bleiben ANDROID_NOT_TESTED.
