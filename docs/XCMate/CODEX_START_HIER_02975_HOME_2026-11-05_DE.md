# Codex Übergabe: SOFORTAUFTRAG XCMate 0.1.29.75 – Live-TV zuerst, danach Filme und Serien

**Stand:** 05.11.2026 · **Projekt:** [artattakk-creator/kodi-noodleprivate](https://github.com/artattakk-creator/kodi-noodleprivate) · **Priorität:** P0  
**Quellversion auf main:** `plugin.video.xtreammate` **0.1.29.74**. Ziel: **0.1.29.75**, auf .74 kumulativ aufbauen. **Noch nicht implementiert; dieser Text ist eine verbindliche Arbeitsübergabe, kein getesteter Patch.**

**Pflichtlektüre vor jeder Änderung:**
- [Ausführliche XCMate-.75-Spezifikation einschließlich 6 Nutzerscreenshots, Kapitel 3 und 8.1–8.5](CODEX_02975_ANDROID_HOME_HERO_ONE_RAIL_SCREENSHOTS_2026-11-05_DE.md) – diese Quelle hat bei Detailfragen Vorrang.
- [Hauptissue #367 – Home, EPG, Fokus, Hero und Live/Widget](https://github.com/artattakk-creator/kodi-noodleprivate/issues/367).
- [Issue #366 – Sendungsbilder in EPG-Details und Live-Hero](https://github.com/artattakk-creator/kodi-noodleprivate/issues/366).
- [Issue #368 – Live-TV-Zurück stoppt nicht zuverlässig](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368).
- [PR #362 – Basis 0.1.29.74](https://github.com/artattakk-creator/kodi-noodleprivate/pull/362).

## Arbeitsziel – exakt in dieser Reihenfolge

1. **LIVE-TV-STARTBILD ZUERST VOLLSTÄNDIG SICHTBAR MACHEN:** Startgruppe, horizontale Senderliste mit korrekten Logos, lokale EPG-Informationen **JETZT/DANACH ohne vorherige Senderwiedergabe**, links ein korrektes großflächiges Sendungsbild bzw. stabiler senderidentischer Hintergrund, rechts die Info-Tabelle. Bereits vorhandene Daten sofort aus dem lokalen Guide-Snapshot verwenden; Netzwerk-Refresh und Bilder unabhängig und begrenzt im Hintergrund.
2. **DIE ERSTEN FÜNF SICHTBAREN LIVE-SENDUNGEN VORLADEN:** Den aktuell fokussierten Sender zuerst, dann weitere sichtbare Sender; nach geprüftem lokalem XMLTV-/Providerbild nur bei bestehender expliziter Freigabe nach TMDB/TVMaze suchen. Eine externe Suche ohne sicheren Treffer darf weder das Startbild noch das Laden der Filmcover dauerhaft blockieren. Quelle, Sendezeit, Sender, Profil und EPG-Revision binden; keine falschen Sendungsbilder.
3. **ERST DANACH FILMCOVER VORBEREITEN:** Sichtbare Filmcover aus Provider-Metadaten/Cache priorisieren, anschließend weitere Filme. Keine gleichzeitig gestartete neue Massen-VOD-/Serien-Bildpipeline bei noch unfertigem Live-Home; vorhandene bereits geprüfte Cover dürfen selbstverständlich ohne Netzwerkarbeit angezeigt werden.
4. **DANACH SERIENCOVER VORBEREITEN:** Sichtbare Seriencover nach dem Film-Ready-Gate, anschließend übrige Serien.
5. **REST NACH UND NACH IM HINTERGRUND:** Faire, bounded Queue und dynamischer Vorrang für den aktiv fokussierten Eintrag, ohne Menü- oder Scroll-Blockaden. Der Nutzer muss trotzdem sofort zwischen Live-TV, Film und Serie navigieren können.

**Freigabekriterien für die Startphasen:** `LIVE_HOME_READY` bedeutet tatsächlich sichtbare Startgruppe, Senderlogos oder ehrlich als fehlend gekennzeichnete Logos, vorhandene Jetzt/Danach-Texte in der rechten Info-Tabelle, stabiler linker Bildbereich mit korrektem Eventbild oder senderidentischem Fallback, korrekter Fokus; **kein** bloßes `queue.put()` oder `READY` ohne Kodi-Rendering. `MOVIES_VISIBLE_READY` und `SERIES_VISIBLE_READY` gelten für die tatsächlich sichtbaren Elemente und erlauben echte Fallbacks, nicht erst nach Download von Tausenden Covern. Bei nicht verfügbarem TMDB-/TVMaze-Bild darf kein unendlicher Gatesperr-Status entstehen.

## Startseiten-Layout (Nutzerentscheidung, nicht zur freien Interpretation)

- **Hero links ~66–70 %:** großflächiges, korrekt zugeordnetes Bild/Backdrop, allenfalls dezenter Titel. **Keine Beschreibung, Meta-Tabelle, Progressbar oder TMDB-/TVMaze-Logos über dem linken Bild.**
- **Hero rechts ~30–34 %:** feste, etwas transparentere, lesbare **tabellarische Informationstafel**. Live-TV: echter Sendername/Logo, Jetzt, Sendezeit, Fortschritt/Restzeit, Danach, Beschreibung, Zusatzdaten. Film/Serie: Titel, Jahr, Inhalt, Genre, Laufzeit/Episoden/Cast soweit tatsächlich vom Provider geliefert.
- **TMDB-/TVMaze-Logos klein am unteren Rand der RECHTEN Tafel** nur dann, wenn Quelle wirklich verwendet wurde; `Bild:` und `Daten:` sauber trennen. Logo-/Lizenzregeln und Opt-in beachten. Provider-/XMLTV-Quelle gegebenenfalls ebenso kennzeichnen.
- **Direkt unter dem großen Hero genau EINE aktive horizontale Zeile**: Live-Senderlogos **oder** Filmcover **oder** Seriencover. Kein gleichzeitiges Anzeigen zweier Posterzeilen.
- Hero-Bereich darf beim Scrollen **niemals schrumpfen**. Keine Überschneidung mit Rail oder Text, sauberer itemlokaler Fokusrahmen, wieder funktionsfähige verschiedene Navigationsicons, keine falschen durchscheinenden Content-Layer.

## Konkrete Codebasis – vorhandene Scheduler reparieren, keine konkurrierenden neuen erzeugen

- `src/plugin.video.xtreammate/service.py`: ruft derzeit `programme_requests68.poll()` und `widget_fast69.poll()` im selben Zyklus. `widget_fast69.prepare()` verarbeitet bereits `('vod','series')`, ohne auf ein verifiziertes `LIVE_HOME_READY` zu warten. **Diese Überschneidung ist im Code erkennbar; dass sie die beobachteten Android-Fehler alleine verursacht, ist nicht bewiesen.** Scheduler und Prioritäts-Gates im kontrollierbaren XCMate-Scope reparieren.
- `resources/lib/programme_prefetch48.py`: rotiert aktuell 8 Sender pro ca. 5 s; Startfokus plus **tatsächlich sichtbare fünf** erhalten nun Priorität vor der Rotationsmasse.
- `resources/lib/live_warm68.py`, `epg_coverage66.py`, `epg_handoff63.py`, `epg_refresh74.py`: lokaler EPG-Kaltstart/Now-Next, keine teuren synchronen GUI-Abfragen, revisions- und profilgebundene Veröffentlichung.
- `resources/lib/live_home62.py`, `live_items62.py`, `widget_home50.py`, `IncludesXCMate64.xml`: korrekte Sender-IDs, `XCMate.ProgrammeLogo46` und reale Kodi-Texture-Bindings vor Textfallback; Sendergruppenname nicht als Sendername ausgeben.
- `resources/lib/programme_requests68.py`, `programme_urls55.py`, `programme_art46.py`, `widget_assets69.py`: vorhandene priorisierte bounded Worker/Queues/Caches nutzen, keine doppelte externe Suche, fairer Backoff und korrektes Event-Key-Matching.
- `resources/lib/hero_epg63.py`: fehlende Skin-Controls `296301/296302` dürfen die gesamte Now-Next-/Bildpublikation nicht verhindern; korrekter nativer Control-/Skin-Fallback erforderlich.
- `resources/lib/widget_skin74.py` und tatsächlich installierter Titan BINGIE MOD / Space Blue: Fokus-/Hero-Geometrie anhand echter Skin-XML, Hash/Backup/Restore und vorhandener Opt-ins prüfen. Keine unbestätigte globale XML-Überschreibung.

**Externe Bildsuche:** `programme_tmdb46` + `tmdb_research43` müssen für die eigene TMDB-Sendungsbildrecherche aktiv sein; `programme_tvmaze67` ist separat opt-in. Bereits vorhandener Token allein ist keine Einwilligung. Kein ungefragtes Aktivieren. EPG-/Sendertext ist selbst bei deaktivierten Bilddiensten Pflicht.

## Abnahmebedingungen und Veröffentlichung

- **Tests aus Langspezifikation vollständig:** `HERO75-R1..R8`, `H75-01..H75-10`, `PREFETCH75-1..8`, `LOAD75-A..F`. Zusätzlich #368 Exit-Test 20× Android-Back, unter den dort definierten sicheren Native-Stop-Kriterien.
- Kaltstart auf Kodi 21.3 Android ARM32 RK3528 mit EPG-gedecktem Startsender: **kein Tune**; zuerst Live-Hero/EPG/Logos; im Prüfprotokoll müssen `LIVE_HOME_READY → MOVIE_WARM_BEGIN → MOVIES_VISIBLE_READY → SERIES_WARM_BEGIN → SERIES_VISIBLE_READY` in der tatsächlichen Reihenfolge und mit realen Rendernachweisen erscheinen. Offline-/TMDB-opt-out-/Cache-miss-/volle Queue-/Profilwechsel-Fälle prüfen.
- Echtbilder/EPG **auf Android** nachweisen; synthetische Bilder/Mocks gelten nur für Host-CI. Rendering 1920×1080 und 1280×720, mindestens 20 Scroll-/Fokuswechsel, 60-min-Home-Stabilität, Seitenmenü, Sendungswechsel und Neustart.
- Bereits protokollierte Kodi-`MyVideos131.db`-Schemafehler nur read-only untersuchen; **keine** Datenbanklöschung oder nicht freigegebenen Migrationsversuche.
- **Datenbestandsschutz:** keine Deinstallation, kein Downgrade, kein Cache-Purge, keine Löschung von Portalen, EPG-/XMLTV-Mappings, TMDB-Tokens, Favoriten, Profilen, SkinShortcuts, Space Blue, Intro, Kodi-Bibliothek oder Kodi-Einstellungen. Keine vertraulichen Logs, Personen-/Gerätedaten, Tokens, Stream-URLs oder private Nutzerbilder in öffentlichen Commits.
- **Build:** kumulative `plugin.video.xtreammate-0.1.29.75.zip` + SHA-256 + valide ZIP-/addon.xml-/Repo-Metadaten + Tests und verständlicher Bericht; PR nach `main`, bei bestandenen automatisierten Gates mergen und **nur GS Media Pilot/Test** publizieren. Das reguläre GS-Media-Repository bleibt bis **ausdrücklicher Android-Freigabe des Nutzers** auf dem zuvor freigegebenen Stand. Wenn Sicherheits-/CI-Gates scheitern, stoppen und den Blocker dokumentieren.
- Separaten `script.gsmedia.setup` Installer 0.5.22 nicht mit XCMate .75 verwechseln oder stillschweigend mitveröffentlichen.
- Abschlussbericht: Root-Cause-Hypothese vs. bewiesene Ursache sauber trennen; Dateien, Commit/PR, Teststatus, SHA, Pilot-ZIP, Rest-Risiken sowie ausdrücklich `ANDROID_NOT_TESTED` bis zur echten Geräteabnahme.

**Codex-Arbeitsanweisung:** Lies diese Übergabe, die Langspezifikation und die Issues #366–#368, beginne unmittelbar mit den konkreten Codeänderungen, führe relevante automatisierte Tests aus, baue/prüfe das ZIP und liefere bei bestandenem Gate im **Testkanal** aus. Keine Pauschalerklärung `alles gleichzeitig lädt` ohne Messung; nachvollziehbares Log der Phasen, Revisions-/Bildidentitäten, Queue-Länge, tatsächlicher Startseiten-Renderzeiten und des fehlenden Skin-Controls.

