# XCMate – Roadmap nach dem .46-Testkandidaten

Maßgeblich: vollständiger Master #241, #240, #194, Übergabe #238 und Feature #239. .45 ist veröffentlicht; .46 ist ein Draft, keine neue Gerätefreigabe. Dieser Stand ersetzt keine historischen Android-Protokolle und schließt keine Tickets.

Neueste direkte Chat-Freigabe27.10.2026: Der bereits fertige SQLite-Umbau wird nach Gesamtprüfung in .46 mitgeliefert, entgegen der zwischenzeitlichen Verschiebung in #242. Keine Freigabe zum Merge. #242 bleibt bis vollständiger realer Abnahme/Konsolidierung offen.

1. **P0 Live-Stop/Bestand/EPG:** zuerst einmal Back, belegte Late-Return-Erholung oder native Queueblockade korrekt protokollieren; keine Stressserie bei Freeze. Box A schützen, bestehendes EIN-Liveexit, Autoplay/Resume/Profile erhalten. EPG nur read-only, bis echte konsistente Sicherung BACKUP_VERIFIED dokumentiert ist (#231). Kein erzwungener Bilder-Refresh.
2. **Gemeinsame .46-Abnahme #239/#240/#241:** grafische reale Sendungsdetails und bestehende Live-Widgetreihe zusammen prüfen. gemeinsame SQLite-Datenbasis, echte−7/+20-Kalendertage nur mit gelieferten Daten, Herkunft/Staffel/Folge/Offline, Senderlogooverlay, Fokus/Info/OK, Now→Next, vollständige aktive Startgruppe (>12/Ende), repariertes Filmwidget, historische Serienbefüllung und unveränderte Bindungen. Fehlender BINGIE-Hook oder Renderer bleibt BLOCKED (#229/#230/#206/#207), optionaler Adapter nur nach Nutzerfreigabe.
3. **Performance/Covermanager und .45-Regressionsabnahme:** echte Thumb-/Preview-/Save-Persistenz, Kalt/Warm-Phasen, p50/p95. sieben Rubriken, PIN6666/Direktrouten, alle eigenen Menüicons (#195/#200), unveränderte Referenzinfobar (#100), Suche Film/Episode (#227), manuelle Cover/Metadaten (#228/#151), Mini/Rail/Kategorien (#223–#226). Historische Verbesserungen bewahren.
4. **Nach stabiler Suche/Player/Widget-Abnahme separat:** vollständiger quellensicherer manueller EPG-Chooser mit echter Preview/Save/Cancel (#98) und übrige Hub-Gates (#161); keine Vermischung mit einer Datenresetmigration.
5. **Nur beauftragte Folgeblöcke:** Wizard/Gruppenindexierung, weitere UI-/Releasegates und Lizenz-/Ressourcenabnahme laut #194. Programm-Bildcache bleibt begrenzt/konfigurierbar; weitergehende automatische Lösch-/Retentionsverwaltung nur mit eigener klarer Spezifikation, keine alten Cover löschen.
6. **Nachrangig:** vollwertige Aufnahmen/Downloads, Fernbedienungslernen, Multiview/PVR, Space Premium als Standard und externe Storage-/Artwork-Migrationen. Bestehenden Code erhalten, nicht als neu abgenommen darstellen.

Pro Kandidat: neue Issue-Matrix mit Code/HOST_PASS/ANDROID_NOT_TESTED/BLOCKED, genaue echte Gerätebelege, ZIP/SHA/CI, Nutzerreview. Kein Main-Merge oder Produktivrelease ohne ausdrückliche Freigabe.
