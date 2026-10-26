# .42 – kumulative Änderungen ab veröffentlichter .41

Basis `354afc1cc524ec3b01001770e6afe6aec5fea70c`. Implementierung `b6a4a9a`, Testfixture und nativer Nachweis/Androidplan `48d188b`, anschließend Lieferung/Testergebnisse. Kein Merge und kein produktiver Indexwechsel.

Zehn eigene Quellpfade sind ausdrücklich freigegeben: ein neues Live-Modul, Guard-/Quarantäne-/LateReturn-Anpassungen in drei Exit-Modulen, eine neue optionale Einstellung samt zwei Übersetzungen, Version/Changelog/Servicebuild. Alle381übrigen Add-on-Dateien bleiben bytegleich. VOD-/Serienzweig bleibt unverändert.

Die Test-Hook-JSON dokumentiert ausschließlich die konkreten erlaubten P0-Blöcke; historische Verträge laufen unverändert darüber weiter. Keine alten Testmethoden entfernt; drei Versionsassertions und ein boolescher Settings-Stub dem aktuellen Paket angepasst. Die größere Schutzfixture enthält die Namen aller1479Baseline-Testmethoden sowie SHA256 der381unveränderten Quelldateien.

Dateiliste (inklusive Paket-/Prüfdateien, dieser Katalog ergänzt sich selbst):

- `docs/XCMate/AENDERUNGEN_02942_DE.md`
- `docs/XCMate/ANDROID_ABNAHME_02942_DE.md`
- `docs/XCMate/ANDROID_STATUS_02942.json`
- `docs/XCMate/AUFTRAGSNACHWEIS_02942.json`
- `docs/XCMate/DATEIKATALOG_02942.json`
- `docs/XCMate/ISSUE_MATRIX_02942_DE.md`
- `docs/XCMate/KODI_NATIVE_PROOF_02942.json`
- `docs/XCMate/NEUE_TESTS_02942.json`
- `docs/XCMate/SCHUTZPRUEFUNG_02942.json`
- `docs/XCMate/TESTBERICHT_02942_DE.md`
- `docs/XCMate/TESTERGEBNISSE_02942.json`
- `docs/XCMate/TESTLOG_02942.txt`
- `docs/XCMate/URSACHENANALYSE_02942_DE.md`
- `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.42.zip`
- `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.42.zip.sha256`
- `src/plugin.video.xtreammate/addon.xml`
- `src/plugin.video.xtreammate/changelog.txt`
- `src/plugin.video.xtreammate/resources/language/resource.language.de_de/strings.po`
- `src/plugin.video.xtreammate/resources/language/resource.language.en_gb/strings.po`
- `src/plugin.video.xtreammate/resources/lib/exit_jobs.py`
- `src/plugin.video.xtreammate/resources/lib/live_exit.py`
- `src/plugin.video.xtreammate/resources/lib/live_stop42.py`
- `src/plugin.video.xtreammate/resources/lib/native_stop41.py`
- `src/plugin.video.xtreammate/resources/settings.xml`
- `src/plugin.video.xtreammate/service.py`
- `tests/fixtures/xcmate_02942_allowed_paths.json`
- `tests/fixtures/xcmate_02942_protection.json`
- `tests/fixtures/xcmate_02942_reviewed_hooks.json`
- `tests/stabilization_contract_02941.py`
- `tests/stabilization_contract_02942.py`
- `tests/test_repository_layout.py`
- `tests/test_xcmate_branding.py`
- `tests/test_xcmate_cumulative_02922.py`
- `tests/test_xcmate_kodi21_overlay.py`
- `tests/test_xcmate_live_stop_02942.py`
- `tests/test_xcmate_scope_02942.py`
- `tools/verify_xcmate_02942_protection.py`

Native Hängerfreiheit weiterhin offen. BoxA ausgeschlossen, BoxB dynamisch. Kein Skin-/Keymap-/DB-/Cache-/Profil-/Dateneingriff.
