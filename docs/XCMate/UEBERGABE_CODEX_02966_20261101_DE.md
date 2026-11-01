# XCMate / GS Media — CODEX-MASTERÜBERGABE für das nächste kumulative Update

**Stand:** 01.11.2026, Nutzerabnahme Android, vorbereitet für Codex.
**Auslösesatz:** „Codex, mach mit XCMate weiter. Lies die Masterübergabe auf GitHub und erstelle das nächste kumulative Update.“
**Verbindliche Quelle:** dieses Dokument auf `main` im Repository `artattakk-creator/kodi-noodleprivate` plus verlinkte GitHub-Issues. Nicht auf den Chatverlauf oder auf private Screenshots beim Nutzer angewiesen sein. Kein unaufgefordertes Nachfragen nach bereits dokumentierten Anforderungen.

## 0 — Repository, Ausgangspunkt und Arbeitsweise

- Repo: https://github.com/artattakk-creator/kodi-noodleprivate
- Kodi-Add-on-ID: `plugin.video.xtreammate`; Projektname **XCMate**, kostenlos, GS Media.
- Aktueller belegter GitHub-Release-/Merge-Ausgangspunkt **0.1.29.65**: PR https://github.com/artattakk-creator/kodi-noodleprivate/pull/299 (am 01.11.2026 auf `main` gemergt). Native und Host-Tests grün, reale Android-Abnahme laut `docs/XCMate/ANDROID_ABNAHME_02965_DE.md` zunächst `ANDROID_NOT_TESTED`. Die Nutzerfotos des 01.11. beweisen **nicht**, welche genaue Version auf dem Gerät installiert ist; aktuelle Version im Android-Test aktiv prüfen.
- Nächster normaler kumulativer Versionskandidat: **0.1.29.66**, sofern `main` vor der Umsetzung noch .65 ist. Bei neuerem HEAD Versionsplanung konfliktfrei anpassen, **niemals .65 oder bereits gemergte Fixes zurücksetzen**.
- Add-on auf Kodi 21.2/21.3 Omega und Android TV 13/ARM32/RK3528; Skin **Titan BINGIE MOD 2.2.3**, Skinshortcuts 2.1.0. Box A ist ein bestehendes Produktivprofil; keine Fernänderung/Reset. Box B kann lokal zur Abnahme dienen, wenn tatsächlich verfügbar.
- Codex: zuerst aktuellen `main`, offene Issues, jüngste PRs und README/Code lesen. Arbeit auf neuem Branch; mit Tests, testbarem ZIP, SHA256, CI-Nachweis und nachvollziehbarem PR. Kein weiterer eigenständiger Feature- oder Skin-Architekturstrang. **Eine .66 mit einer zusammengeführten P0-Abnahme** statt mehrerer konkurrierender Versionszweige.
- **Merge-Freigabe:** Für .65 war im Issue #298 ein eigener bedingter Auto-Merge ausdrücklich genehmigt. Diese historische Freigabe nicht still auf .66 übertragen. Ohne neue Freigabe PR vollständig vorbereiten, Prüfungen laufen lassen und den Nutzer über Status informieren; Merge erst bei entsprechender Autorisierung und bestandenem Gate. Niemals Tests umgehen oder einen Android-PASS erfinden.

## 1 — Maßgebliche GitHub-Referenzen

- **#300** [P0 Android-Fokus-/Hero-Fehler, TMDB_OK und Bildstatus, aktueller Nachtrag](https://github.com/artattakk-creator/kodi-noodleprivate/issues/300). Enthält die konkrete Fünf-Bilder-Fokusmatrix, den Nachtrag der vier EPG/TMDB-Fotos und das **zurückgestellte** Skin-Adapter-TODO.
- **#291** [P0 Home → WELT / Nitro: EPG- und lokale Snapshot-Latenz, alle Sender](https://github.com/artattakk-creator/kodi-noodleprivate/issues/291).
- **#298** [voriger Master .65: Tokenimport, EPG-Latenz, vollständiger VOD/Serienindex und Adult-Zone-Gruppe](https://github.com/artattakk-creator/kodi-noodleprivate/issues/298); historisch gemergt, **nicht alles real auf Android abgenommen**.
- [PR #296 .64](https://github.com/artattakk-creator/kodi-noodleprivate/pull/296) enthält frühere Fokus- und Tokenänderungen, deren native Tests eine noch fehlerhafte reale Darstellung nicht ausschließen.
- [PR #299 .65](https://github.com/artattakk-creator/kodi-noodleprivate/pull/299): Token-Zielzugriff, dauerhafte Katalogjobs/Paging, RAM-Handoff/EPG-Performance.
- Weitere Projektkontexte: #295, #297, #293, #284, #277, #257, #206, #239, #276.
- Testbasis: `docs/XCMate/TESTBERICHT_02965_DE.md`, `docs/XCMate/ANDROID_ABNAHME_02965_DE.md`, `docs/XCMate/ISSUE_MATRIX_02965_DE.md`, `docs/XCMate/URSACHEN_02965_DE.md`.

## 2 — Aktueller Nutzerbefund 01.11.2026: sauber zwischen PASS und FAIL trennen

### TMDB-Token: nach Import jetzt echter Authentifizierungs-PASS

- Nutzer bestätigt erfolgreichen Import, Bildschirm zeigt ausdrücklich **`TMDB · TMDB_OK`** und „TMDB-Verbindung erfolgreich. Authentifizierung und Antwort bestätigt.“
- Das ist ein **realer erfolgreicher API-Konnektivitätstest**, nicht der Beweis, dass TMDB-Artwork zu einer EPG-Sendung gefunden und dargestellt wurde. Keine weiteren Formatänderungs-/USB-Tokenexperimente ohne Hinweis auf ein neues Importproblem.
- Nicht bewiesen sind Tokenpersistenz nach Kodi-Neustart, Artwork-Mapping, tatsächlicher HTTP-Bilddownload, lokaler Cache-Write oder Image-Texture-Ausgabe. Dies sind getrennte Stufen.

### EPG-Texte: für einen besuchten Sender belegt; allgemeine Abdeckung FAIL/OPEN

- Nutzerfotos: `XCMate - LIVE-TV` mit **88 Sendern**, links Senderliste, rechts `DE| NITRO HEVC`: `NOW 11:00–11:55 MacGyver`, Folgeprogramme. Detailansicht mit MacGyver-Titel, Zeit, Dauer, vollständiger deutschsprachiger Beschreibung.
- BINGIE-Home: Nitro-Logo, `MacGyver`, Jetzt 11:00–11:55, Fortschritt, Beschreibung und Danach – also **Text/Programme-Handoff funktioniert bei diesem Sender**.
- Nutzerbeobachtung: EPG erscheint anscheinend **erst für Sender, die bereits einmal fokussiert/angewählt wurden**. Kodi startet auf WELT; nach Senderwechsel auf Nitro erscheinen Nitro-Daten. Kein belastbarer Nachweis für vollständigen persistenten EPG-Import über **alle** gewählten Sender, Startgruppe und Gruppen.
- Das kann Importumfang, Quellenzuordnung, Xtream/Xmltv-ID, Snapshot-Handoff/Revision, On-Demand-Refresh oder Sichtbarkeits-/Fokuslogik betreffen. Diagnose benötigt Kette und Gegenproben; Ursache NICHT vorwegnehmen.

### EPG-Bilder: FAIL trotz erfolgreicher TMDB-API

- MacGyver-Detailansicht: Platzhalter (Berg-Icon), Hinweis **„Sendungsdaten vorhanden; Bildstatus noch nicht bestätigt.“**
- BINGIE-Hero von Nitro/MacGyver: weiterhin allgemeine XCMate-Space-Grafik statt sendungsbezogener Fanart/Still.
- **Zu untersuchen:** EPG-Event -> Titel-Normalisierung -> Serien-/Episoden-/Filmresolver (TMDB/TVMaze nach Konfiguration) -> Kandidat/Matchscore -> verwendbares Artwork -> sichere HTTPS-Beschaffung -> persistente lokale Cache-Datei -> Kodi-abspielbarer Bildpfad/Texture -> Hero- und Details-Property -> tatsächlicher sichtbarer Render.
- Keine Sperre der EPG-Texte durch Bilder. Keine TMDB-Pflicht für VOD-Filme/-Serien; Provider-Bilder dort bevorzugen. Fehlende Bilder nicht durch zufällig falsche Poster ersetzen, negative Ergebnisse inkl. Ursache und Retry-Zeit speichern, Bildquelle nennen wenn vorhanden.

### BINGIE-Fokus und Hero: realer P0-FEHLER weiterhin OPEN

Fünf ältere Fotos vom selben Tag in Issue #300: Bei HOPE/Coco/Lupin sitzt der helle Fokusrahmen teilweise **eine gesamte Widget-Reihe zu tief**, obwohl das Hero bereits das oben ausgewählte Item darstellt; „Loki“ und Live-TV-Senderbutton sind Gegenproben mit richtig sitzendem Rahmen. Mehrfacher Überlauf von Filmbeschreibungen in Widgetüberschriften/Posterreihen.

Aktuelles Codefundament: `resources/lib/widget_skin50.py`, `widget_skin64.py`, `skin_upgrade63.py`, `resources/bingie64/IncludesXCMate64.xml`. BINGIE-Dateien werden **nach Hash-/Backup-/Diff-/Zustimmungsprüfung** verändert: `xml/IncludesHomeWidgets.xml`, `xml/IncludesHomeBingie.xml`, `shortcuts/overrides.xml`, `shortcuts/template.xml`. Untersuche aktive tatsächliche XML/GlobalFocus/WidgetFocus, Z-Order, Scroll/Container-ID, geometrische Platzierung und verzögerten Focus-Property-Wechsel. Korrektur **am tatsächlichen Control** statt pauschal x/y nach oben zu verschieben. Alle Reihen einschließlich Drittanbieter/Musik und flachen 142×72-Live-Kacheln abdecken. Hero-Texthöhe, Umbruch/Trunkierung und Zeilenabstand korrigieren.

## 3 — P0-A: persistente, vollständig befüllte EPG-Datenbank / Jetzt-Danach sofort auf Home

### Sollarchitektur

1. Lokale `guide_v1.sqlite` als kanonische persistente Quelle für alle aktiv gewählten Portale/Sender, pro Provider/Profil getrennt und ohne Cache-Vermischung. **Kein Fokus- oder Zapp-Ereignis darf Voraussetzung für den Erstimport des EPG eines Senders sein.**
2. Quellmanager für **Provider-Xtream-EPG/XMLTV**, **EPGShare** und **Calamura/Kaimandura** (genauen Namen/konfigurierten Endpoint *aus vorhandener Nutzerkonfiguration* statt aus Vermutung beziehen). Externe Quellen nur, wenn tatsächlich konfiguriert/aktiviert. Mehrere Quellen mit Priorität, Provenienz, Konfliktauflösung, Sender- und Event-Mapping sowie manueller Auswahl je Kanal über bereits bekannte EPG-Kontextmenüs.
3. Bei Quelle: `attempt_at`, `success_at`, HTTP/VFS-Status, Parse-/Coverage-Ergebnis, Quellrevision, `min_event_start/max_event_end`, Eventanzahl, Mappingquote, EPG-Ende und nächster Refresh als verständliche Diagnose speichern. Ein fehlgeschlagener Download oder eine teilweise XMLTV-Antwort darf die gültige alte Datenbank **nicht löschen**.
4. **Spätestens alle 24 Stunden** fälligen Hintergrund-Refresh sicher anstoßen, inklusive Nachholprüfung nach Kodi-Neustart/Offlinephase; manuelles „Jetzt aktualisieren“ im Manager. Aktualisierungen transaktional/inkrementell zusammenführen: neue Sendungen, Korrekturen, geänderte Anfangszeiten, Sender-/Event-Deduplizierung, Änderungen der Prioritätsquelle und Fallback; alte gültige Daten bis erfolgreichem atomarem Ersatz behalten.
5. Gewünschtes Langzeitfenster **7 Tage Vergangenheit / 20 Tage Zukunft**, aber ausschließlich soweit die echten Quellen solche Events bereitstellen. Niemals fiktive Lückenfüllung oder garantierte 20 Tage behaupten. DST/Zeitzonen (Europe/Berlin), Eventzeitformat, Duplikate von Serientiteln, wechselnde Sendernamen/alias und Provider-IDs testen.
6. Die sichtbaren **88 Sender** sind ein konkreter Testumfang. In der Startgruppe sowie anderen aktiv gewählten Gruppen müssen **auch noch nie besuchte Sender** mit gültiger Quelle Now/Next sofort aus lokaler DB erhalten. Nicht verfügbare Programme korrekt als `SOURCE_EMPTY`, `UNMAPPED`, `EVENT_OUT_OF_WINDOW`, `STALE`, `DB_UNAVAILABLE` differenzieren. Auf „Programme vorhanden“ aus dem Screenshot einer einzelnen Sendung nicht als Vollständigkeitsbeleg schließen.
7. Home-Hero, Senderbuttons, Programmguide, Mini-EPG, Detailfenster, Live-Infobar und Player müssen dieselbe revisionskonsistente DB/Snapshot-Versorgung nutzen. **Keine synchrone Provider-EPG- oder TMDB-HTTP-Abfrage im UI-/Fokus-/Fernbedienungs-Hotpath**, keine neuen sekundenlangen Imports nach Senderwechsel.
8. Bestehender `RAM-first`-Snapshot aus .65 erhalten, aber Kaltstart aus persistenter DB korrekt befüllen und Revision/Mappings invalidieren. Kein vollständiges DB-Neuladen unter Sperre bei jedem Fokuswechsel; SQL/Lock/Timer/UI-Publikationszeiten getrennt messen.
9. Benutzerlesbares EPG-Log (keine rohen Code-Traces) und EPG-Manager: pro Quelle letzter erfolgreicher Abruf, verbleibende Abdeckung/Zeitraum, Anzahl Events/Mappings, Gründe für Senderlücken. Manuelle Zuordnung ohne Datenverlust, testweise Änderung in der Oberfläche sichtbar.

### Nicht verhandelbare Abnahme

- Kodi kalt neu starten mit Netzwerk online und einmal offline. **Nie zuvor fokussierten** Sender mit nachgewiesenem Event in einer konfigurierten XMLTV-Datei auswählen: Jetzt/Danach bereits auf Home korrekt; dann Live-Player, EPG-Detail, zurück zu Home ohne Neuimport. Mit WELT/Nitro und weiteren Sendern inklusive zweiter Gruppe vergleichen.
- Quell-Update mit geänderter Folge/Eventzeit simulieren; DB enthält danach neue/korrigierte Daten, andere gültige Programme bleiben erhalten. 24-h-Fälligkeit, gescheiterter Abruf, atomarer Fallback und Kodi-Neustart wiederholen.
- Warmes EPG-Now/Next in erster brauchbarer Anzeige **Ziel <= 1 s** nach sichtbarer Player-Oberfläche (wie #291), ohne Playback-Verzögerung. Kalte und warme Zeiten getrennt berichten; keine unbelegte Leistungszusage.
- Daten-/Mapping-Diagnostik unabhängig vom GUI: anhand anonymisierter IDs pro Quellsender `source -> import -> map -> event -> guide revision -> now/next -> UI`.

## 4 — P0-B: Sendungsbilder von TMDB/TVMaze tatsächlich anzeigen

- Erhaltenen privaten TMDB-Token nur über vorgesehenen sicheren Speicher laden, keine Token/Secrets/URLs im Commit oder unbereinigten Log.
- Prüfen, ob `TMDB_OK` auch nach Kodi-Neustart erfolgreich ist und private Zielpfade weiterhin funktionieren. Keinen Import wiederholen, wenn bereits `TMDB_OK`.
- MacGyver (NITRO, 01.11.2026 11:00–11:55) ist **Beweis- und Diagnosefall** für den Bildstatus, nicht die Behauptung, dass TMDB genau für diese Sendung ein Still bereitstellen müsse. Bei eindeutigem Treffer ein echtes Fanart/Episodenbild zeigen; bei keiner verfügbaren Aufnahme Fallback mit korrektem Status. Serien-Suche, Episodenmetadaten, Titelvarianten, Originaltitel, Jahr und Quellenpriorität korrekt auflösen; bei negativem Match kein falsches Poster.
- Art URL und Bilddatei lokal mit Event-Identität, Attribution und begrenztem Cache/TTL speichern; getrennte Zustände `NO_MATCH`, `NO_ARTWORK`, `FETCH_ERROR`, `CACHE_ERROR`, `GUI_NOT_UPDATED`. Home/EPG-Detail beide synchron zum aktiven Event aktualisieren. Keine stale Bilder beim Fokuswechsel; Side effects anderer Widgetreihen vermeiden.
- Provider-VOD-Welt bleibt unberührt: Filme/Serienposter und Suche kommen aus dem Provider/Index. Nur Live-TV-EPG-Bilder über optionalen TMDB/TVMaze-Resolver.

## 5 — P0-C: Fokus, Hero und Bild-/Textlayout korrigieren

- Verbindlich **Issue #300 vollständig** (Fünf-Bilder-Matrix + Android-Nachtrag) übernehmen.
- Eigene, gematchte Fokusrahmen nur an aktiven Controls (unterschiedliche Postergrößen/Live-Buttons), globale BINGIE-Frames für XCMate-Widgetitems konfliktfrei ausblenden, fremde Widgets unverändert korrekt; Focus-Transform beim vertikalen/rechten/links Scrollen und bei Hero/GUI-Refresh korrekt.
- Kein „Fokusrahmen auf unterem Coco, Hero oben Lupin“ mehr; keine Doppelrahmen, kein Restfokus nach Wechsel, Text darf keine Widgettitel überdecken.
- Exakte tatsächlich verwendete generierte Skin-XML prüfen, Skinshortcuts-Rebuild/Cache, Animation, Position/Dimension/Z-Order, 720p/1080p/4K/DPI/Fonts/Overscan.
- Nur vorhandene **opt-in, hash-geprüfte Skin-Adapter-Änderung** mit Preview, Sicherung, Rollback und ausdrücklichem Nutzer-Ja; keine stillen globalen Skinpatches und keine fremden XML überschreiben. Keine Neuinstallation/Globalreset.

## 6 — P0-D: Suche und Medienindexierung aus .65 real abnehmen / gezielt nachbessern

- Issue #298 / PR #299 mit echten Android-Daten überprüfen: vollständige Filme- und Seriengruppen, Kategorie-ID/aktivierte Auswahl, `Adult Zone` (wird vom Nutzer erwartet), >100/>1000 Paging, dauerhaft verwaltete Importjobs, Neustart, Nachimport, Retry/Abbruch und echte Suchergebnisse.
- **Kein pauschaler Inhaltsfilter aufgrund der Gruppenbezeichnung.** Deaktivierte Gruppe, `SOURCE_EMPTY`, `SOURCE_FILTERED`, `CACHED`, `FAILED`, `INDEX_INCOMPLETE` separat zeigen; nicht einfach „Provider liefert nichts“ unterstellen.
- Globale Suche (Live/Filme/Serien), Genre, laufende Sendung und direkte Film-/Serientreffer gegen den tatsächlichen vollständig indexierten Providerbestand testen. Widgets können reduzierte Neuheitenlisten zeigen, die Gesamtsuche darf nicht auf diese 24/48 Titel beschränkt sein.
- Änderungen fokussiert und ohne großflächiges Rewrite der Kodi-/Skin-/Player-Router, ohne Wiedergaberegression.

## 7 — Bestandsschutz / explizit NICHT jetzt umsetzen

- **Kein neuer Skin-Adapter-Architekturumbau** / keine Verallgemeinerung auf andere Skins in .66. Späteres TODO unter Issue #300: optionaler, skinversionspezifischer Patch mit Installation-/Aktivierungseinwilligung, Preview/Backup/Rollback, Kernfunktionen unabhängig; Titan BINGIE MOD 2.2.3 ist heute die einzige nachgewiesen unterstützte Variante.
- Keine automatische Änderung am Box-A-Gerät oder vorhandenen Nutzerprofilen. Kein Deinstallieren, Downgrade, Skin-/Widget-/EPG-/Katalogreset, keine Passwort-/Portal- oder Favoritenlöschung.
- Bewährter Startsender WELT, flache Live-Kacheln, funktionierende Filme-/Serienwidgets und -Cover, Player-Start, Kodi-`Zurück`/Stop-Kompatibilitätsmodus .42, Staffel-Autoplay, Resume, Wizard-Daten, EPG-Quellen und manuelle Zuordnung erhalten.
- Aufnahme/Download, Remote-Anlern-Manager, vertikale dritte Navigationsebene, großer Skin-Relaunch/Space Premium, PVR/Multiview nicht als neue Featurebaustelle aufnehmen.
- Kein stiller Ersatz/Einbetten von TMDB-Token, keine öffentlichen privaten Quellen-/Provider-Daten.

## 8 — Testmatrix / Ausgabe-Artefakte / Freigabe

**Host/native:** vollständige bestehende Regression ohne entfernte Prüfungen/Skips; native Kodi-21.2/21.3-BINGIE/Skinshortcuts-Fälle; neue Tests für 88 Sender-Mapping, mehrere XMLTV-Quellen, 24-h-Catch-up, DST, Konflikte, Quellfehler/Offline, DB-Sperren, EPG-Bildpipeline, fehlende Bilder, Fokusgeometrie aller Widgettypen, schnelle Medien-/Seriensuche, 100/1000 Titel und Index-Lease/Paging/Retry; Screenshots/Bildvergleich mit fokussiertem und unfokussiertem Control.

**Reales Android:** separates Protokoll `A66-01` bis `A66-12`; nicht automatisch aus Linux-Test auf Android-PASS schließen.
- A66-01 installierte Version/Kodi/Gerät + Datenbestand vor/nach Update.
- A66-02 Token bereits gültig / `TMDB_OK` nach Neustart, ohne neue Eingabe.
- A66-03 MacGyver EPG-Details: Text, Bildstatus, echte Bildanzeige falls verfügbar.
- A66-04 BINGIE-Home: NITRO/MacGyver und korrektes Sendungsbild bzw. ehrlicher Fallback.
- A66-05 88 Sender-Startgruppe inkl. nie besuchtem Sender aus **nachweislich vorhandenem** XMLTV-Event ohne vorherigen Zapp.
- A66-06 Provider-EPG/EPGShare/Calamura: Mapping, 24-h-Update, Ereignisänderung, Quellenausfall.
- A66-07 Offline-Kaltstart: bestehendes EPG bleibt verfügbar.
- A66-08 Wechsel Home -> Live -> Detail -> Home: konsistente Now/Next-Revision, Latenzmessung.
- A66-09 Fokusrahmen HOPE/Lupin/Coco/Serien, Wechsel Drittanbieter-Musik/Film/Serie.
- A66-10 Live-TV-Button-Fokus, Heldenbild/Description ohne Textüberdeckung.
- A66-11 Filme/Serienindex und Suche inkl. bewusst aktivierter Adult-Zone-Gruppen.
- A66-12 Bestandsschutz: WELT-Start, Live-Zurück, Resume/Autoplay, Portale/EPG/Favoriten/Skin-/Widget-Links.

**Statuspolitik:** pro Gate `PASS`, `FAIL`, `BLOCKED` oder `ANDROID_NOT_TESTED`, Quelle des Belegs, Version, Repro und Hinweis auf noch offene Einschränkungen. Grün in CI ≠ Android PASS. Keine künstlichen Testdaten als echte Provider-Daten ausgeben. Nichts ohne tatsächlichen Beleg als `TMDB_ART_OK` markieren.

**Update-/Releasekette:** `main`-HEAD vor Branch fixieren; additive .66-Änderungen; strukturiertes Changelog/Ursache/Tests/Abnahmematrix; Installer `plugin.video.xtreammate-0.1.29.66.zip` oder bei neuem Versionsstand nach Versionsplan; SHA256-Datei; CRC/Source-ZIP-Bytevergleich; sicheres ZIP ohne private Keys; CI des exakten HEAD; GS-Media-Publish mit `addons.xml`, `addons.xml.md5` und ZIP-Integritätsnachweis (falls Merge genehmigt). Bei roten Gates PR offen + ehrlicher BLOCKED-Bericht.

## 9 — Fertiger Codex-Startprompt

> Öffne `artattakk-creator/kodi-noodleprivate`, lies `docs/XCMate/UEBERGABE_CODEX_02966_20261101_DE.md` vollständig und bearbeite die zusammengeführten P0-Aufträge #300, #291 und die real noch offenen Android-Abnahmen aus #298. Starte vom aktuellen `main`, erzeuge den nächsten **kumulativen** XCMate-Kandidaten (voraussichtlich .66), führe alle Schutz-/Host-/nativen Tests aus und stelle einen dokumentierten PR samt Android-Abnahmematrix, Installations-ZIP und SHA256 bereit. Wenn ein Gate scheitert, offen mit BLOCKED dokumentieren. Keine automatische Skin-Architekturauslagerung, keine Box-/Profil-Resets, keine erfundenen Android-PASS. Frage nicht noch einmal nach bereits hier dokumentierten Projektanforderungen. Für das Mergen eine konkrete Freigabe einholen, sofern sie nicht in einem neuen Auftrag ausdrücklich gegeben wird.
