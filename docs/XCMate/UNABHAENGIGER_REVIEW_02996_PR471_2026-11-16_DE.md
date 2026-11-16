# Unabhängiger lesender Review – XCMate .96 / PR #471

**Reviewer:** Subagent `review96_final`, ausdrücklich nur lesend. **Geprüfter Abschlussstand:** `36df57c82d4036a7820a46f36ce141247201091f`. Git-Tree `7ef3b1a6a9e708c52af57f55a478ccd1017509cc`; Addon-Subtree `d8ed67e611c23f7044cfa11e36ce5884a32b64e5`.

Der Reviewer las den vollständigen verbindlichen Übergabeauftrag, Issue #469, den konsolidierten Bericht und die Fehlerliste von `98bc3b16`. Keine Änderung am Autoren-Checkout, Index, HEAD oder Branch; keine eigenen Commits oder GitHub-Kommentare. Modell-B / PR #472 wurde weder verwendet noch geprüft. Der Bericht wird durch Root auf ausdrücklichen Nutzerauftrag veröffentlicht.

## Urteil und korrigierte Findings

Im abschließend geprüften Host-Scope **keine bestätigten offenen Critical-, Important- oder Minor-Findings**. Vier während dieses Reviews bestätigte Important-Befunde wurden durch die Autoren korrigiert und unabhängig gegengeprüft:

1. **Manuelle Bildwahl wurde ersetzt** (`programme_candidates85.py:134`, `cinematic_images96.py:53`, `hero_art86.py`). Repro: gespeichertes `/old.jpg`, neuer Cachetreffer desselben Werks und höher bewertetes `/images`-Backdrop. Home und Details konnten unterschiedliche Bilder zeigen. Nun hat die gespeicherte Referenz Vorrang; manuelle Bilder umgehen Cinematic-Enrichment, Alternativen und automatischen Posterwechsel.
2. **XMLTV-Revisionsnachweis ging an Übergabegrenzen verloren** (`programme_requests68.py:12`, `programme_art46.py`, `artwork_temp85.py:186`, `xmltv_art96.py`). Repro: echte XMLTV-Auflösung → `completed/result`, lokale Materialisierung beziehungsweise temporärer Cache → Proof invalidieren. Das ausgelieferte Bild blieb zuvor zulässig. Nun bleiben Proof und manuelle Herkunft erhalten; widerrufene und fremden Ereignissen zugeordnete Proofs werden abgewiesen.
3. **Logoänderungen erreichten vorhandene Live-Channel-Objekte nicht** (`live_overlay.py:519`, `logo_overrides96.py:19`, `live_prepare47.py`, `logo_cache.py`). Repro: echtes Speichern → Modellaufbau → Reset/Ersatz → dasselbe Channel-Objekt erneut rendern. Nun verwendet die Anzeige verifizierte gemeinsame RAM-Receipts und den Provider-Fallback. Interpreter-, Profil-/Kontowechsel und der Verzicht auf Datei-, Stat-, Hash- oder SQL-Zugriff im GUI-Pfad sind geprüft. Der opake Scope hat eine redigierte Darstellung. Keine vollständige JSON-Serialisierung von `Channel.extra` in den geprüften Konsumenten gefunden.
4. **XMLTV-only wurde von Remote-Lookup-Schaltern blockiert** (`programme_requests68.py:211`, `programme_urls55.py:348`). Repro: Provider-Event ohne eigenes Bild, gespeicherte lokale Alternative aus `source-a`, XMLTV AN, TMDB/TVMaze/Helper/Katalog AUS. Zuvor kein Enqueue; direktes Resolve überschreibt READY mit AWAITING_BACKGROUND_REFRESH. Abschließend unabhängig bestätigt: genau ein Enqueue mit **allow_lookup=False**, danach **READY / xmltv_event** und unveränderter Proof. XMLTV-AUS bleibt geschlossen und erhält die gespeicherte Zuordnung.

## Beurteilung der ursprünglichen 13 Fehler

Numerisches Ranking ist wieder von Quellenfreigaben getrennt. Optionale `/images`-Aufrufe verlassen generische Identitätssuchen und kalte Bildmaterialisierung; die originalen Bild-/Persistenztests bleiben erhalten. Die tatsächlichen nativen Movie-/TV-Seed-Blöcke werden unverändert im Host-Gegenlauf geprüft. Provider-, Menü- und Fokusprüfungen kontrollieren echte Callbacks, frische gespeicherte Werte und erhaltene Fremdfelder statt lediglich geänderter Labels. Die zwischenzeitlich erneut eingeführte frühe Widget-Abhängigkeit des direkten Overlay-Konstruktors wurde entfernt.

## Eigene unabhängige Verifikation

Isolierter temporärer Snapshot außerhalb des Autoren-Checkouts:

- **332 PASS, 0 FAIL**, 57,56 Sekunden; drei bestehende `simpleeval`-DeprecationWarnings.
- Auswahl aus 23 Testdateien: alle ursprünglichen 13 Fehlfälle, neue Reviewregressionen, Gruppen/Mini/Settings/Provider/Logos und die drei .95-Backup-/Profil-/Gate-Suiten.
- Alle **899 Addon-Dateien** bytegleich zum geprüften Commit.
- ZIP separat gelesen: **899 Mitglieder**, CRC sauber, keine fehlenden, zusätzlichen oder abweichenden Quellbytes.
- SHA256: `249d7908d83cf7808d950e938e572fc046c2b0fc767aeebd3195b18b87b9d740`.

Die frühere 329-PASS-Aussage war ein Zwischenstand vor dem letzten XMLTV-only-Befund; sie ist kein Abschlussnachweis.

Der abschließende Runtime-Diff umfasst `artwork_temp85`, `cinematic_images96`, `event_art81`, `hero_art86`, `live_overlay`, `live_prepare47`, `logo_cache`, `logo_manifest86`, `logo_overrides96`, `programme_art46`, `programme_candidates85`, `programme_image69`, `programme_match46`, `programme_requests68`, `programme_urls55`, `setup_window`, `xmltv_art96`. Umgebende Mapping-, Quellen-, Settings-, Speicher-, Provider- und Guide-Pfade wurden zusätzlich geprüft.

## Ausdrückliche Abnahmegrenzen

Die 332 Tests ersetzen keine vollständige Host-Gesamtsuite und keine aktuellen CI-Ergebnisse. Neue native Linux-Kodi-Läufe wurden vom Reviewer nicht ausgeführt.

Physisches RK3528/Kodi 21.3, echtes Android-Langpress, SMB, Zielvolumes, Neustartpersistenz und sichtbare Decoder-/GPU-Ausgabe bleiben **ANDROID_NOT_TESTED**. Die ursprüngliche Settings-Störung der privaten Box ist nicht abschließend erklärt. Kein Pixel-PASS aus Referenzbildern oder PNG-Decoding abgeleitet.

**Positiver begrenzter Host-Code-Review; vollständige CI- und Gerätegates bleiben eigene Voraussetzungen. Kein Merge und keine Veröffentlichung durch Codex.**
