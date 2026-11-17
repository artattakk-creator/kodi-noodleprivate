# XCMate 0.1.29.98 – CI-Korrektur und Pilot-Vorbereitung

**Status: PILOT_READY – unveröffentlichter Prüfkandidat; separate Freigabe vor jeder Pilot-Veröffentlichung erforderlich. ANDROID_NOT_TESTED.**

Draft-PR: [#487](https://github.com/artattakk-creator/kodi-noodleprivate/pull/487). Dieser PR baut auf [#484](https://github.com/artattakk-creator/kodi-noodleprivate/pull/484), HEAD `eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a`, auf und ist gegen dessen Branch gestapelt. Kein Merge, keine Veröffentlichung, keine Geräteinstallation.

Verbindlicher Auftrag: [Korrekturauftrag](CODEX_KORREKTURAUFTRAG_02998_CI_PILOT_2026-11-17_DE.md).
Implementierungs-/Teststand: `c5ecd2ea69bb84e648cae9433d250613dceff46e`, Branch `release/xcmate-02998-ci-pilot-rc`.
[Quellidentität und historische Prüfsummen](test-evidence/02998/source-identity.json).

## 1. Bestätigte Ursachen der sechs ursprünglichen Fehler

| Fehler | Ursache | Korrektur und unverändert erhaltene Schutzfunktion |
|---|---|---|
| `test_gsmedia_repo_180...test_xcmate_release_unchanged` | Aktueller Produktstand wurde gegen die veraltete Version .96 geprüft. | Aktueller Vertrag erwartet ausdrücklich .98; die übrigen Repository-/Installerbedingungen bleiben aktiv. |
| `test_repository_layout...test_xtreammate_manifest_and_remote_service` | Derselbe veraltete Versionswert im aktuellen Manifestvertrag. | Explizite .98-Erwartung; Manifeststruktur und Servicevertrag bleiben geprüft. |
| `test_xcmate_branding...test_display_name_and_version` | Veraltete .96-Erwartung bei unverändertem Produktnamen. | Explizite .98-Erwartung; Brandingbedingungen bleiben aktiv. |
| `test_xcmate_cumulative_02922...test_original_icon_bytes_dimensions_and_kodi_asset_reference` | Versionsliteral war Teil des aktuellen Icon-/Manifestvertrags. | .98-Erwartung; Original-Iconbytes, Abmessungen und Assetreferenz werden weiter geprüft. |
| `test_release_candidate96...test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes` | Das historische .96-ZIP wurde mit dem heutigen Quellstand neu gebaut/verglichen. | Der ursprüngliche Testkörper läuft unverändert gegen den exakten .96-Gitstand in einem separaten Prozess. Das tatsächlich aufbewahrte ZIP wird vorher per gepinnter SHA und Original-Sidecar geprüft. Ein eigener .98-Test vergleicht heutige Quellbytes und reproduzierbare ZIPs. |
| `test_release_candidate96...test_review_package_never_stages_or_authorizes_any_channel` | Der .96-Paketierer wurde auf den heutigen .97/.98-Quellstand angewandt. | Originale historische Prüfungen gegen .96; zusätzlicher aktueller .98-Vertrag mit Output-, Publikations-, Hash- und manipulierten Freigabebit-Prüfungen. |

Alle sechs Originalfehler wurden vor der Korrektur erneut reproduziert: [RED-Nachweis](test-evidence/02998/original-six-red.txt). Kein Skip, kein xfail und keine pauschale Fehlerausnahme. Der historische `tools/release_candidate96.py` blieb bytegleich. Historische Module laufen in einem Kindprozess mit eigenem Importpfad, damit aktuelle Versionen und Testdoubles nicht hineinwirken.

Historischer .96-Referenzstand: `bc06f521d23ee5c1e6c9aaca456c2b3cc062f3fc`; 899 Paketdateien wurden gegen dessen Quellbytes verglichen. Das alte ZIP bleibt SHA256 `64d08c78581d074a9c86fee26ba94011119c1ab0f297de6a0bc9afee13cf1ba9`.

## 2. Änderungen und Paket

- Unter `src/plugin.video.xtreammate` ändern sich gegenüber PR #484 ausschließlich Version und News in `addon.xml`. Alle anderen Produktdateien sind bytegleich; keine neue Migration, Routing-, Player-, Consent- oder Speicheränderung.
- `tests/historical_release96.py` isoliert die unveränderten historischen Pakettests und prüft vorab das tatsächlich erhaltene Archiv samt Sidecar.
- `tools/release_candidate98.py` hat eine explizite .98-Version und einen eigenen review-only Vertrag. Manipulierte, zusätzliche, fehlende, doppelte oder unerlaubte ZIP-Einträge, geänderte Quellbytes/SHA-Dateien, unerlaubte Ausgabeorte und geänderte Freigabebits werden abgewiesen. Historische .96/.97-Reviewarchive sind zusätzlich eingefroren.
- Die vorhandenen nativen Engines akzeptieren optional einen ausdrücklich übergebenen Paketprüfer. `run_xcmate98_native.py` verwendet den strikten .98-Prüfer; der historische .96-Prüfer wird nicht global umgeschrieben.
- Die exakte Deltafixture wurde nur für die freigegebene Manifestmetadatenänderung aktualisiert; unbekannte Produktänderungen werden weiterhin abgewiesen.
- `.github/workflows/xcmate98-review.yml` hat ausschließlich lesende Repositoryrechte, keine Merge-/Releasejobs und verhindert neue Python-Bytecodeartefakte im geprüften Checkout.

Reviewpaket: [plugin.video.xtreammate-0.1.29.98.zip](test-builds/02998/plugin.video.xtreammate-0.1.29.98.zip)

SHA256: `d37d34fbb5be5e46154b912d3ce960f6e248431fcf7d0a9651fa9785b20a12c3`

4.772.893 Bytes, 901 Dateien. ZIP/CRC, Manifest, vollständige Quellbytes und bytegleicher Neubau geprüft. Upgradevertrag prüft ausdrücklich Basis .97 und Ziel .98. Keine Profile, Datenbanken, Logs oder neue Zugangsdaten werden in das Paket aufgenommen.

Das alte PR-484-Review-ZIP .97 bleibt SHA256 `16c81e587cfe1739ae463ec69ba6d142ab75146e47c8273ae6a779ec750a1042`. Die veröffentlichte .97-Pilotversion und sämtliche regulären, Pilot-, NeoDark3- und Installerbereiche sind unverändert; eine spätere Pilotfreigabe muss separat erfolgen.

## 3. Tatsächlich ausgeführte Prüfungen

| Prüfung | Ergebnis |
|---|---|
| Sechs ursprüngliche Fehler vor Fix | 6 FAIL, erwarteter RED-Nachweis |
| Historische/aktuelle fokussierte Releaseverträge | 33 PASS |
| Finale neue .98-Paket-/Inspector-/Fixtureverträge | 13 PASS |
| Gezielte Artwork-/EPG-/Mini-/Settings-/Speicherregressionen | 152 PASS |
| Sprachkatalogvalidierung | 17 PASS; Validierung bedeutet nicht vollständige Übersetzung sämtlicher Texte |
| Vollständige pytest-Suite auf finalem Stand | **4225 PASS**, 0 FAIL/ERROR, 4 Warnungen, 1108,09 s |
| Vollständige unittest-Suite auf finalem Stand | **4214 PASS**, 0 FAIL/ERROR, 983,879 s |
| Native Linux-Kodi21.2-Matrix auf finalem Stand | **4/4 PASS**: Artwork und Mapping jeweils 720p/1080p |
| Physischer Android RK3528/Kodi21.3/BINGIE | ANDROID_NOT_TESTED |

Erster vollständiger .98-Lauf auf `2f434987`: **4220 pytest PASS / 4209 unittest PASS / 4 native PASS**, Run44113762304. Dieser belegt die ursprünglichen sechs Korrekturen. Die zusätzlichen finalen Fokusguards werden nicht aus diesem älteren Lauf abgeleitet.

GitHub prüft standardmäßig einen virtuellen PR-Merge-Ref. Der finale Testref `a7f718bc498f8dc6f86bdd802a24cdb2c8e36e48` hat exakt denselben vollständigen Git-Baum `acfa4a2f6ada768f483bfc80f43c7b1e3d49d08b` wie der geprüfte Branch-HEAD `c5ecd2ea`. Quell-/Test-/Tool-/Paketidentität ist damit belegt; dies ist **kein Merge in einen Repositorybranch**. Der [Identitätsbeleg](test-evidence/02998/source-identity.json) enthält beide IDs und die Eltern.

Die vier pytest-Warnungen betreffen drei veraltete Python-AST-Namen in simpleeval und eine bestehende ungültige Escape-Sequenz beim Parsen des alten GUI-Vertrags. Sie wurden nicht unterdrückt und führten zu keinem Testfehler.

Finale vollständige CI: [Run 44117233113](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44117233113), alle sechs Jobs erfolgreich. Zusätzlich sind [Archiv-72-CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44117233138) und [Katalog-/Widget-73-CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44117233120) auf demselben Source-HEAD grün. [Pytestbeleg](test-evidence/02998/full-pytest.json), [Unittestbeleg](test-evidence/02998/full-unittest.json).

Artwork-Kontrollpunkte: bei 720p 2,03 / 46,01 / 121,04 / 305,08 Sekunden unverändert 253.204 native Textur-Messwerte, bei 1080p 2,06 / 46,09 / 121,08 / 305,22 Sekunden unverändert 253.572 native Textur-Messwerte. Jeweils vier sichtbare Statusprojektionen und 13 unveränderte fremde Widgetdefinitionen, zusätzlich zwei kontrollierte Offline-Neustarts im nativen Runner. Dies sind synthetische Linux-Kodi-Nachweise, kein physischer Speichermangel und kein echter Android-/API-Kontotest. [720p-Report](test-evidence/02998/artwork-720.json), [1080p-Report](test-evidence/02998/artwork-1080.json). Alle 26 finalen nativen PNGs besitzen [Einzelprüfsummen](test-evidence/02998/native-png-SHA256SUMS).

Die komplette Host-Suite verwendet den bestehenden `run_host94_contract.py`: 227 früher aus main entfernte historische Testdateien werden anhand unveränderlicher Git-Objekte in einen **separaten temporären Klon** materialisiert. Keine Wiederherstellung in Veröffentlichungskataloge, keine erfundenen Ersatzpakete; alle ursprünglichen Tests bleiben aktiv.

Ein ergänzender lokaler Volltest in der eingeschränkten Entwicklungs-Sandbox wurde nach **399 PASS / 21 FAIL** abgebrochen. Dort unterschritt freier temporärer Speicher die geprüfte Reserve; Loopback-Netzwerkzugriffe waren eingeschränkt. Dies ist kein erfolgreicher Volltest und wird nicht als solcher gewertet. Ein späterer lokaler Paketguard wies außerdem neu erzeugte, ungetrackte Test-Bytecodeartefakte im geschützten Branding-Verzeichnis korrekt ab; ausschließlich diese zwei selbst erzeugten Artefakte wurden entfernt und der vollständige neue 13-Test-Vertrag danach erfolgreich wiederholt. Die freigaberelevanten vollständigen Suiten laufen auf den getrennten CI-Runnern.

## 4. Unabhängige QA und nativer Testharness

Beide projektlokalen Checklisten wurden durch die bereits bestehenden unterstützten Review-Subagenten `artwork_qa` und `epg_mapping_qa` unabhängig und ausschließlich lesend geprüft. Die deklarierte Custom-`agent_type`-Auswahl ist in diesem Client nicht verfügbar; es wurde keine automatische Interception behauptet. Beide prüfen denselben finalen Commit und getrennte Checklisten; ihre Aussagen ersetzen weder CI noch Android-Abnahme.

Der Mappingprüfer hat einen verspäteten „Disabled add-ons“-Dialog des synthetischen Test-Add-ons im ersten .98-1080p-Mini-Screenshot gefunden. Dieser Bildbeleg wurde ausdrücklich nicht als ungestörter Fokus-PASS akzeptiert. Anschließend wurden ausschließlich der Testcontroller und die Fokusbelege gehärtet:

1. Nur die vollständig identifizierte englische Meldung des eigenen `Catalog73 synthetic GUI contract` wird bei vorhandenem No-Fokus quittiert; fremde Dialoge und ähnliche Texte bleiben unberührt.
2. Vorschau-/Busy-Screenshots verlangen gültige native Dialog-ID, Owner-Property und erwartetes Fokuscontrol vor und nach der Aufnahme.
3. Die Nachprüfung beobachtet ausschließlich und stellt keinen Fokus wieder her.
4. Fehlende/wechselnde Receipts verhindern PASS und den simulierten OK-Druck.

Alle vom unabhängigen Reviewer bestätigten False-PASS-/Inputguard-Fälle wurden zuerst als RED reproduziert und anschließend behoben. Der Reviewer hat den endgültigen Guarddiff bestätigt. Zwei überholte Zwischenläufe wurden gezielt beendet; sie zählen nicht als bestandene finale CI. Der ursprüngliche Run 44113762304 bleibt als separater Erstnachweis erhalten.

Finale Mapping-QA: [unabhängiger Bericht](test-evidence/02998/final-mapping-qa-c5ecd2ea.md), zwölf neue native PNGs mit [Einzelhashes](test-evidence/02998/mapping-png-sha256.txt). Beide Auflösungen bestehen Dialog-/Grid-Lesbarkeit, Vorschau, Busy/Retry/Save und strikte Fokusbelege. In beiden Mini-Vorschauframes liegt noch ein synthetischer XCMate-Erstinstallationsprompt unter dem Mappingdialog. Dieser wurde nicht zwangsweise geschlossen. Die oberste Mappingdialog-ID und der erwartete Fokus sind belegt; die Aufnahmen sind dennoch nicht insgesamt promptfrei. `fixture_prompts98_declined=0` bedeutet keine Quittierung eines passenden Catalog73-Prompts, nicht die Abwesenheit aller Prompts.

[720p-Receipt](test-evidence/02998/mapping-720.json), [1080p-Receipt](test-evidence/02998/mapping-1080.json): Mini-Dialog 13002, Grid-Dialog 13004, Vorschaufokus 200 und Retryfokus 404; nativer Adapter-Apply, quellqualifizierter Readback und Cancel ohne Mutation bestätigt. Echter Mini-Elternbereich und Android weiterhin offen. Finale Artwork-QA: **ARTWORK_QA_PASS**, A1–A5 im synthetischen Host-/Linux-Kodi21.2-Umfang für 720p/1080p. [Unveränderter unabhängiger Abschlussbericht](test-evidence/02998/FINAL-ARTWORK-QA-02998.md), SHA256 `52c7a6fd0954dd4035586ccb1bf5fe423d3304da6ef9a7ecadd420fcf999ae71`. Alle 14 neuen Artwork-PNGs wurden unabhängig angesehen und gegen direkt gelesene finale Joblogs geprüft. Kein bestätigter Artwork-Releaseblocker im ausgewiesenen Umfang. Echte API-/Token-/CDN-Verfügbarkeit, physisches ENOSPC und durchgängige VOD-/Serien-Coverversorgung sind ausdrücklich nicht damit zertifiziert.

**Konsolidiertes Gate: PILOT_READY.** Sämtliche finalen Host-/CI-/Paketgates grün, beide unabhängigen Reviews ohne bestätigten verbleibenden Blocker im ausgewiesenen Host-/nativen Umfang. Android, reale Mini-Elternpixel und reale Anbieter bleiben offen. Ein reiner Dokumentationsabschluss ergänzt diese Berichte und Screenshots; Produkt-, Test-, Tool- und ZIP-Bäume bleiben exakt auf dem getesteten Commit c5ecd2ea. Der letzte CI-Lauf gilt diesem ausdrücklich ausgewiesenen unveränderten Implementierungsstand; kein erneuter Volltest wird für reine Bericht-/PNG-Ergänzungen behauptet.

## 5. Grenzen und weitere Freigabe

- Wiederverwendete Harness-/Dateinamen und eine synthetische Screenshot-Fußzeile tragen noch ältere Nummern wie .88. Sie bezeichnen den Testaufbau. Das tatsächlich eingelesene ZIP wird vor der Ausführung ausdrücklich als .98 und gegen alle aktuellen Quelldateien geprüft.
- Native Tests verwenden echtes Linux-Kodi21.2 und BINGIE2.2.3 mit synthetischen Katalog-/EPG-/Bildquellen in Wegwerfprofilen. Es wird kein Benutzerprofil geöffnet und keine echte Portal-/TMDB-Anmeldung verwendet.
- Das installierte Review-ZIP wird strikt geprüft; ausschließlich das Wegwerfprofil deaktiviert Produktionsservice/Abhängigkeiten und ergänzt Testskripte. Das veröffentlichungsfähige ZIP bleibt unverändert.
- Die Mini-Zuweisung nutzt einen echten nativen Dialog und den produktiven Adapter mit synthetischem Mini-Elternowner; der große EPG verwendet einen echten nativen Grid-Elternbereich. Die echte Android-Mini-Elternspalte bleibt offen.
- Native Statusbilder prüfen die Projektion injizierter Producerzustände. Gesonderte Hosttests prüfen tatsächlichen Matcher, sichere Bildbytes/Decoder und gesperrte Einstellungen. Ein Statusbild ist kein Nachweis einer echten Kontoabfrage.
- Die späten Statusaufnahmen mit gestopptem synthetischem Worker sind kein Nachweis durchgehend geladener Film-/Serienposter. Fremdwidget-/Warm-/Neustartnachweise werden gesondert bewertet.
- Physische Decoder-/Player-/IR-/Netzwerkfehler gelten nicht als repariert, nur weil ein Hosttest besteht.

[Android-Abnahmeplan A98-01 bis A98-08](ANDROID_ABNAHME_02998_DE.md). [Changelog](CHANGELOG_02998_DE.md).

Erst nach vollständigen grünen Host-/CI-/Paket-/nativen QA-Gates darf hier `PILOT_READY` stehen. Das bedeutet bereit zur **gesondert freizugebenden** Pilot-Veröffentlichung, keine produktive oder physische Android-Abnahme. Regulär, Pilot und NeoDark3 bleiben bis zur jeweiligen ausdrücklichen Freigabe unverändert.
