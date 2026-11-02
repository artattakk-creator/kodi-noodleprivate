# XCMate .69 – Android-Abnahme Box B

Alle Tests zunächst **NOT_TESTED**. Host-/Linux-Kodi-PASS ersetzen diese Geräteabnahme nicht. Box A unverändert lassen. Auf Box B das innere plugin.video.xtreammate-0.1.29.69.zip aus dem CI-Testartefakt über Kodi „Aus ZIP-Datei installieren“ als kumulatives Update installieren. SHA256 des inneren ZIP mit der beigefügten .sha256-Datei vergleichen. Kein Downgrade, Reset, Cachelöschen oder erneuter Tokenimport.

Vorher notieren: Kodi-Version, Gerät/Android-Version, bestehender .42-Live-Kompatibilitätsmodus, aktive Startgruppe, Favorit, manuelles EPG-Mapping, Serien-Resume und Artwork-Modus. Bestehende Einstellungen beibehalten. Nach Update einmal das Versions-/Änderungspopup kontrollieren.

**Erste Kurzabnahme:** Startsender → einmal Live-TV-Zurück → bedienbares Home. Bei FAIL zunächst keine 20 Wiederholungen. Danach großer EPG → Detail → Zurück, Mini-EPG → Detail → Zurück. Erst bei erfolgreichem kurzen Ablauf gesamte Matrix.

| ID | Ausführung / erwartetes Ergebnis | Status |
|---|---|---|
| DB-01 | Read-only Speicherdiagnose öffnen. Freie Bytes, Reserve 32 MiB + 65.536, DB/WAL/SHM und Artworkbudget notieren. Reserveblockade von echtem ENOSPC unterscheiden. Gerät nicht absichtlich füllen. Hardwarewerte fehlen hier. | NOT_TESTED |
| DB-02 | Vorhandene Fehlerklassen/Seitenlimit/Locks prüfen. Keine DB sperren, kürzen oder löschen. FULL/LOCK-Injektionen werden ausschließlich im Hosttest ausgeführt. Gerätefall ohne vorhandene Störung NOT_TESTED belassen. | NOT_TESTED |
| DB-03 | Dasselbe sichtbare Programm 18-mal fokussieren/öffnen. Keine 18 identischen API-Lookups bei unveränderter Revision; fixe Statuscodes und begrenzter Backoff. | NOT_TESTED |
| DB-04 | Manuell zugeordneten Sender und Stream-Alias im großen/kleinen EPG vergleichen; Quellen und lange Historie erhalten. | NOT_TESTED |
| DB-05 | Portale, Gruppen, Favoriten, vorhandene Cover, EPG, Resume und Einstellungen vor/nach Neustart vergleichen; nichts zurücksetzen. | NOT_TESTED |
| ART-01 | Bekannten eindeutigen Film und Serie mit bereits eingerichtetem eigenem TMDB-Zugang öffnen. API-Erfolg, korrekt zugeordnetes HTTPS-Bild und tatsächlich sichtbares Bild getrennt belegen. TMDB_OK allein ist kein Render-PASS. | NOT_TESTED |
| ART-02 | Sendung mit vorhandenem XMLTV-/Providerbild in beiden Details und Hero anzeigen. Keine falsche Nachbarsendung. | NOT_TESTED |
| ART-03 | Geeigneten Fall ohne andere passende Quelle mit eingeschaltetem TVmaze prüfen; eindeutige Zuordnung und sichtbares Bild. Fehlt geeigneter Fall: NOT_TESTED. | NOT_TESTED |
| ART-04 | URL-only-Modus (lokales Zusatzarchiv ausgeschaltet): dieselbe Sendung im großen EPG, Mini-EPG, Details, Jetzt/Danach und Hero vergleichen. Kodi darf seinen Texturecache verwenden. | NOT_TESTED |
| ART-05 | Portal/Quelle/Sendung wechseln, gleiche Titel/IDs beachten: kein altes/fremdes Bild. Nur anonymisierte Diagnose teilen; keine URLs, Tokens oder SMB-Zugänge veröffentlichen. | NOT_TESTED |
| ART-06 | Falls echte Schreibblockade vorhanden: geprüftes Bild mit RAM_ONLY und exaktem Speichergrund anzeigen; später Recovery ohne erneute Suche prüfen. Keine künstliche Geräteblockade erzeugen. | NOT_TESTED |
| ART-07 | Netzwerk-/Nichttrefferfall: Job terminiert, begrenzte Wiederholungen, kein dauerndes PENDING. Nachrichten/Sport/Sendepause erzeugen keinen Helper-Dauerlauf. | NOT_TESTED |
| HOME-01 | Kaltstart/Fokuswechsel: keine generischen Poster/Hero-Texturen und keine leeren Poster-Kacheln. Fehlende Bilder neutral; echte Bilder später einblenden. | NOT_TESTED |
| HOME-02 | Kaltstart nach Kodi-Neustart und warmes Zurück zum Home messen: erste bedienbare Navigation, Logo, EPG-Titel, erstes Film-/Serienposter; jeweils Sekunden notieren. Kein Full-Reload pro Fokuswechsel. | NOT_TESTED |
| HOME-03 | Filme und Serien: Provider-Cover, Fokus, Trailer manuell und Rückkehr prüfen; Resume und staffelübergreifendes Autoplay erhalten. | NOT_TESTED |
| HOME-04 | Eigene Startgruppe vollständig durchscrollen (aktuell 88, kein Limit). Andere vorhandene Gruppen inkl. leer/1/5/17/120/256 soweit verfügbar prüfen; keine Nutzerdaten für Test künstlich verändern. | NOT_TESTED |
| HOME-05 | Schnell verschiedene Sender fokussieren: lokaler Jetzt/Danach-Text sofort, Hero exakt zur fokussierten Sendung; Fokus allein startet keinen Player. | NOT_TESTED |
| EXIT-01 | Eigener Live-Stream → Back → STOP_DONE → HOME_VISIBLE/COMPLETE und wirklich bedienbares Home. Ein Log COMPLETE ohne sichtbares Home reicht nicht. | NOT_TESTED |
| EXIT-02 | Während Bild-/EPG-Nachladen fünf, anschließend 20 Live-Zurück-Zyklen; keine Doppelstarts und kein Hänger. | NOT_TESTED |
| EXIT-03 | Großen und Mini-EPG je zehnmal öffnen → Sendungsdetails → Back, auch schneller Sender-/Zeitwechsel und fehlende Bildquelle. Fokus/Gruppe/Zeitposition erhalten. | NOT_TESTED |
| EXIT-04 | Überlagerte eigene Ebene nur schließen; fremden Dialog/Player unberührt lassen. Nach fremdem Dialogschluss wieder bedienbar. Kein Kodi-Abbruch nötig. | NOT_TESTED |

Pro Test dokumentieren: PASS/FAIL/NOT_TESTED, Uhrzeit, Gerät/Kodi, konkrete Beobachtung und höchstens feste anonymisierte Statuscodes. Keine privaten Rohlogs in GitHub. Fehlende Echt-API-/Bild-/Hardwareprüfung offen lassen. Merge und produktive Veröffentlichung erfordern gesonderte Freigabe.
