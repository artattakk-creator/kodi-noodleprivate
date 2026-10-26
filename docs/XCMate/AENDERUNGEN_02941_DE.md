# XCMate .41 – vollständige Änderungen gegenüber .40

Basis `6c362a45582350c694e4e18c13581cd57cd31d70`, geprüfter Quellstand `edacc729a369ddcc867f090a55bb4b630265a5e4`. Keine alten Experimentalbranches übernommen.

## Commit-/Issue-Zuordnung

| Commit | Änderung | Issues |
|---|---|---|
| ffd98fb | Live-Stop ohne synchronen SendMsg-Wait, FIFO-Rückkehrbarriere, native Tests | #203/#192/#213 |
| 3dc9417 | Mini-Texte/Zukunft, Widgetbackend/Adapter, einmaliger Versionshinweis | #211/#208/#207/#206/#209/#26 |
| 7747e70 | sichere optionale GUI-Bindung und ungültige Notice-Felder; aktualisierte alte Erwartungen | #209/#207/#211/#208 |
| edacc72 | unklarer Queuepost bleibt quarantänisiert, zusätzlicher Stopfehlertest und Schutztool | #203/#192 |

## Pfade

- `docs/XCMate/AENDERUNGEN_02941_DE.md`
- `docs/XCMate/ANDROID_ABNAHME_02941_DE.md`
- `docs/XCMate/ANDROID_STATUS_02941.json`
- `docs/XCMate/AUFTRAGSNACHWEIS_02941.json`
- `docs/XCMate/CODEX_AUFTRAG_02941_DE.md`
- `docs/XCMate/DATEIKATALOG_02941.json`
- `docs/XCMate/ISSUE_MATRIX_02941.json`
- `docs/XCMate/ISSUE_MATRIX_02941_DE.md`
- `docs/XCMate/KODI_NATIVE_STOP_PROOF_02941.json`
- `docs/XCMate/NEUE_TESTS_02941.json`
- `docs/XCMate/SCHUTZPRUEFUNG_02941.json`
- `docs/XCMate/TESTBERICHT_02941_DE.md`
- `docs/XCMate/TESTERGEBNISSE_02941.json`
- `docs/XCMate/TESTLOG_02941.txt`
- `docs/XCMate/URSACHENANALYSE_02941_DE.md`
- `integrations/titan-bingie-mod/0.1.29.41/Includes_XCMate41.xml`
- `integrations/titan-bingie-mod/0.1.29.41/README_DE.md`
- `integrations/titan-bingie-mod/0.1.29.41/manifest.json`
- `integrations/titan-bingie-mod/XCMate_BINGIE_Adapter_REVIEW_0.1.29.41.zip`
- `integrations/titan-bingie-mod/XCMate_BINGIE_Adapter_REVIEW_0.1.29.41.zip.sha256`
- `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.41.zip`
- `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.41.zip.sha256`
- `src/plugin.video.xtreammate/addon.xml`
- `src/plugin.video.xtreammate/changelog.txt`
- `src/plugin.video.xtreammate/resources/language/resource.language.de_de/strings.po`
- `src/plugin.video.xtreammate/resources/language/resource.language.en_gb/strings.po`
- `src/plugin.video.xtreammate/resources/lib/app_routes.py`
- `src/plugin.video.xtreammate/resources/lib/exit_jobs.py`
- `src/plugin.video.xtreammate/resources/lib/live_exit.py`
- `src/plugin.video.xtreammate/resources/lib/local_epg.py`
- `src/plugin.video.xtreammate/resources/lib/mini_epg.py`
- `src/plugin.video.xtreammate/resources/lib/native_stop41.py`
- `src/plugin.video.xtreammate/resources/lib/tv_data.py`
- `src/plugin.video.xtreammate/resources/lib/update_notice41.py`
- `src/plugin.video.xtreammate/resources/lib/widget_data41.py`
- `src/plugin.video.xtreammate/resources/lib/widget_focus41.py`
- `src/plugin.video.xtreammate/service.py`
- `tests/exit37_fixture.py`
- `tests/fixtures/xcmate_02941_allowed_paths.json`
- `tests/fixtures/xcmate_02941_reviewed_hooks.json`
- `tests/stabilization_contract_02940.py`
- `tests/stabilization_contract_02941.py`
- `tests/test_repository_layout.py`
- `tests/test_xcmate_027_ui.py`
- `tests/test_xcmate_0281_boot.py`
- `tests/test_xcmate_branding.py`
- `tests/test_xcmate_cumulative_02922.py`
- `tests/test_xcmate_exit_02937.py`
- `tests/test_xcmate_live_exit_02941.py`
- `tests/test_xcmate_mini_02941.py`
- `tests/test_xcmate_navigation_02938.py`
- `tests/test_xcmate_rail_mini_02939.py`
- `tests/test_xcmate_update_notice_02941.py`
- `tests/test_xcmate_widget_adapter_02941.py`
- `tests/test_xcmate_widgets_02941.py`
- `tests/xcmate027_fixture.py`
- `tools/check_bingie_adapter_02941.py`
- `tools/verify_xcmate_02941_protection.py`

## Daten-/UI-Vertrag

375 Add-on-Quelldateien unverändert, neue .41-Module separat. Alle1435 alten Methoden erhalten,44 neue. Alle163 historischen UI-Vertragsdateien einschließlich Suchmaskencontrols bytegleich zu .40; exakte Hunk-Liste für11 tatsächlich geänderte bestehende Quellen. Originalicon und98 Themegrafiken, Player/VOD-Exit/Resume/Autoplay/Portal-/EPG-Store-/Keymap-/Artwork-Modusmodule bytegleich. Keine bestehenden Bibliotheks-/Guide-/Job-Schemata geändert. Produktionsindex/.40-ZIP/Publish-Bedingung unverändert.

Neue Profilzustände sind ausschließlich eigenes update_notice-JSON/Lock und begrenzte Widget-Metadatencaches/Locks mit atomaren temporären Dateien, keine Migration bestehender Daten und kein Bildarchiv. Die Schutzprüfung belegt Quell-/Test-/Artefaktschutz und unveränderte62 fremde lokale WIP-Dateien, aber behauptet keine ausgeführte Android-Inventur. Keine Box verändert.

Optionales BINGIE-Include/Review-ZIP liegt außerhalb des Add-on-Installationspakets, wird nicht geladen/aktiviert/installiert. Preflight liest nur eine bereitgestellte Kopie, kein Skin-/Shortcut-Reset. [Integrationsbeschreibung](../../integrations/titan-bingie-mod/0.1.29.41/README_DE.md).
