# XCMate .40 – Änderungen gegenüber main .39

Basis `25a640869e3b4e178945ba4f549ad7e269dd292f`, getesteter Quellstand `0ab01d9e89dbf4114196fe1b8e048de975cb41d1`. 22 Add-on-Pfade, davon ein neues Python-Modul (`search_snapshot.py`); keine neue DB, Abhängigkeit, Keymap oder Skinänderung.

| Datei | Änderung |
|---|---|
| `src/plugin.video.xtreammate/addon.xml` | Version .40 |
| `src/plugin.video.xtreammate/changelog.txt` | Kumulative Änderungsnotizen und Grenzen |
| `src/plugin.video.xtreammate/resources/language/resource.language.de_de/strings.po` | Fünf DE/EN-Texte für Technikgruppen/Stopwartehinweis |
| `src/plugin.video.xtreammate/resources/language/resource.language.en_gb/strings.po` | Fünf DE/EN-Texte für Technikgruppen/Stopwartehinweis |
| `src/plugin.video.xtreammate/resources/lib/app_routes.py` | Resolverfehler noncegebunden melden, Auflösung während Stop sperren |
| `src/plugin.video.xtreammate/resources/lib/exit_jobs.py` | Reasoncodes, tatsächliche Native-Release-Prüfung, worker_done-Quarantäne ohne Doppelstop |
| `src/plugin.video.xtreammate/resources/lib/live_exit.py` | Während Stop keine Player-Abfragen; feste Exit-Ursache |
| `src/plugin.video.xtreammate/resources/lib/live_overlay.py` | Erstes-OK-Recovery, Zeilenabstand, Textbereinigung, Tune-Sperre während Stop |
| `src/plugin.video.xtreammate/resources/lib/media_intent.py` | Flüchtiges RESOLVER_FAILED je eigenem Intent |
| `src/plugin.video.xtreammate/resources/lib/media_osd.py` | Back/Stop-Reason, gruppierte Technikansicht, OSD-Recovery vor Fullscreen-Heuristik |
| `src/plugin.video.xtreammate/resources/lib/media_return.py` | Playerlock-Quarantäne und Wiederanzeige selbst ausgeblendeter nativer Suche |
| `src/plugin.video.xtreammate/resources/lib/media_search.py` | Bestätigte Seiten, sichere Teilantworten/Callbacks, Metadatenupdate statt Reset |
| `src/plugin.video.xtreammate/resources/lib/media_window.py` | Kein impliziter Stop/Reinit-Cancel, nativer Suchdialog-Return, Start-/Fehlerguard |
| `src/plugin.video.xtreammate/resources/lib/mini_epg.py` | Schmalere Spalte und fünf zweizeilige native Titel |
| `src/plugin.video.xtreammate/resources/lib/nav_rail.py` | Eigener Fokus/Label/Breite beim Hide konsistent zurücksetzen |
| `src/plugin.video.xtreammate/resources/lib/navigation_dispatch.py` | Expliziter USER_HOME-Reason |
| `src/plugin.video.xtreammate/resources/lib/play_intent.py` | Keine neue Live-Preplay-Übergabe während Stop |
| `src/plugin.video.xtreammate/resources/lib/playback_exit.py` | Kein Stop allein durch Fensterstatus |
| `src/plugin.video.xtreammate/resources/lib/search_data.py` | Medienseiten vor EPG-Prepare veröffentlichen |
| `src/plugin.video.xtreammate/resources/lib/search_snapshot.py` | Neuer begrenzter RAM-Seitenspeicher, keine DB |
| `src/plugin.video.xtreammate/resources/lib/stream_details.py` | Bild-/Ton-/Untertitelgruppen mit lokalen Icons |
| `src/plugin.video.xtreammate/service.py` | Stop-Quarantäne vor allen Player-/Navigationspolls, Build40 |

32 neue Tests in drei Dateien, alle 1.403 bisherigen Testmethoden erhalten. Die alten Fensterwechsel-Stop-Erwartungen in `test_xcmate_exit_040` wurden ausdrücklich auf den .40-Vertrag umgestellt, nicht entfernt: Fensterwechsel stoppt nicht; expliziter Back/Home stoppt nach wie vor. Das strenge Kodi-API-Modell ist um die belegte TextBox-Signatur ergänzt; frühere Quellen-Fixtures bleiben erhalten und werden über exakte .40-Hunks komponiert. Keine beliebigen Freeze-Ausnahmen.

Unverändert gegenüber .39: Original-XCMate-Icon und 98 Themegrafiken, Suchmasken-XML mit sechs Tabs-/Ergebniscontrols, `media_state`, `media_progress`, `media_autoplay`, `media_sequence`, `player`, Portal-/EPG-Datenmodule, Artwork-Modusgate, dynamischer Safe-Art-Cache und Keymaps. `.39`-ZIP, Produktionsindex und Publish-Bedingung bleiben unverändert. [Schutznachweis](SCHUTZPRUEFUNG_02940.json).

Die zusätzlich mitgelieferten Docs, Testlog, ZIP/SHA und Nachweis-JSONs sind keine produktive Veröffentlichung. Keine Geräte-/Profiländerung.
