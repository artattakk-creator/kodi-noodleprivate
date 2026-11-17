# Bildabruf .90/.97 und EPG-Zuweisung #482 – Reviewbericht

Stand: 17.11.2026. Draft-PR [#484](https://github.com/artattakk-creator/kodi-noodleprivate/pull/484). **Kein Merge und keine Veröffentlichung freigegeben.** Host-Gesamtsuiten und native Produktprüfungen sind abgeschlossen. Auch die ergänzende native Testharness-Prüfung ist abgeschlossen und wird getrennt ausgewiesen. Ausstehende Gerätefunktionen sind keine PASS-Ergebnisse.

## Quellenbasis und Bestandsschutz

| Stand | Unveränderliche Quelle |
|---|---|
| Veröffentlichte .90 | `9bbf75040378dcaead9128880a909fe7978143a4` |
| Veröffentlichte .97 | `f0f6649edf075338bb6a806eff231eb718948368` |
| QA-/Anforderungsbasis #483 | `1cea11d75c6f61accc39142aeb1c0004a88da4cb` |
| Vollständig geprüfter Produktstand | `38dbe103416c0040be0285be55f657c0dbe8dbd7` |
| Ergänzter nativer Fokusobserver, identischer Produkt-/Testbaum und ZIP | `835bea9901602284e38ac37ecb68bb51d5fe9e1f` |

`main/src` enthält einen älteren Produktstand. Deshalb ist #484 auf den QA-Branch von #483 gestapelt, der die veröffentlichte .97 enthält. Weder #483 noch ein Produkt-PR wurde für diese Arbeit gemergt. Keine zusätzliche Versionsnummer; das ZIP ist ein ausdrücklich unveröffentlichter .97-Reviewbuild in einem eigenen Dokumentationspfad. Bereits veröffentlichte Archive und die geschützte .90 bleiben unverändert.

Keine echten Provider-, TMDB- oder TVMaze-Anfragen und keine Geräteinstallation wurden ausgeführt. Alle Konten, EPG-Ereignisse, HTTP-Antworten und Bildbytes in den Tests sind synthetisch. Bestehende Portale, Token, Opt-outs, Profile, Datenbanken, Sicherungen, SkinShortcuts, Widgetpfade und Installationskanäle bleiben erhalten.

## Nachgewiesene Ursachen und Korrekturen

### Artwork

Der unabhängige Vergleich zeigt **keinen generell defekten Decoder oder grundsätzlich ausgefallenen eigenen TMDB-Matcher**: Der gesunde synthetische Pfad liefert sowohl mit .90 als auch .97 ein korrekt dekodiertes Bild bis zum Detail-Consumer. Daraus folgt keine Android-Abnahme und keine Aussage über einen echten Provideraccount.

Bestätigt sind diese Fehlergrenzen:

1. `storage_policy92` blockiert Bildaufträge bei explizitem Nein, Später oder ungültiger Policy. Diese unterschiedlichen Zustände wurden bisher still zusammengefasst; ein vorhandener Auftrag konnte ohne sichtbaren Grund warten. Die Sperre bleibt bestehen, aber ein profil-/ereignisgebundener Status erklärt die Ursache. Eine bewusste Wiederaktivierung ersetzt den alten Policyfehler durch den tatsächlichen Anforderungszustand.
2. Ein ungültiges `settings.xml` erzeugt den richtigen Schutzfehler. Eine zweite Kandidatenabfrage konnte diesen außerhalb der bisherigen Fehlergrenze erneut werfen; `programme_urls55._run` degradierte ihn zu `FETCH_FAILED`. Der spezifische, zugelassene Einstellungsfehler bleibt jetzt bis zum Consumer erhalten. Keine automatische Settings-Reparatur und kein Tokenersatz.
3. Der Live-Hero übernahm nur erfolgreiche Bilder und ließ negative beziehungsweise laufende Zustände unsichtbar. `ArtStatus`/`ArtStatusText` erreichen nun die bestehende Beschreibungsbindung. EPG-Text und gültige Bildreferenzen bleiben unabhängig erhalten. Terminale Netzwerk-, Reserve-, Nichttreffer- und Sicherheitszustände erhalten feste, verständliche Texte; unbekannte Zustände zeigen keine fremden Fehlertexte oder URLs.

Der bereits funktionierende dynamische Fallback unter einer 1-GiB-Archivreserve und nur 64 MiB freiem Platz bleibt erhalten. Die Reserve wird weder abgesenkt noch umgangen.

### EPG-Zuweisung

1. `_submit()` kann bei belegtem Slot ablehnen. Die Oberfläche behauptete trotzdem eine laufende Abfrage. Sie meldet jetzt `MAPPING_BUSY` mit erneuter Bedienmöglichkeit; der Slot wird vor der Ergebnisveröffentlichung freigegeben.
2. Ein lokaler Nichttreffer oder SQLite-Fehler konnte implizit einen vollständigen kalten Feedabruf auslösen. Die lokale Suche unterscheidet Nichttreffer, fehlenden Index, belegte Datenbank und Zeitbudget. Ein kalter Abruf erfordert ausdrücklich **Quelle laden**, ein Retry eine erneute Benutzeraktion.
3. Die Quellenwahl startet direkt und nennt konfigurierte aktive Quellen mit lokalem Stand; Provider/Xtream bleibt Basis. Der Suchbegriff wird aus dem fokussierten Sender übernommen. Name und EPG-ID werden konservativ normalisiert; Vorschläge bleiben auswählbar und werden niemals automatisch gespeichert.
4. Nach einem fehlgeschlagenen Quellenwechsel blieben alte Listeneinträge interaktiv. Die Liste und ihre Speicherfreigabe werden jetzt vor dem Reload invalidiert. Ein später Worker darf weder eine fremde Vorschau anwenden noch Save freigeben.
5. Die SQL-Vorfilterung verlor Satzzeichen-/Akzentvarianten und konnte 400 ausgeschlossene +1-Kanäle vor dem ersten echten Treffer abschneiden. Lokaler und RAM-Katalog verwenden denselben Matcher **vor** Pagination. Für 20.000 Kanäle wurde die Normalisierung optimiert: rund 38–44 ms für einen späten Treffer statt Budgetabbruch bei 151 ms; das 150-ms-Lesebudget blieb unverändert. Das ist ein Hostmesswert, keine ARM32-Messung.
6. Eine vollständig leere Vorschau darf nicht speichern. Gültige zukünftige Programme außerhalb des aktuellen Rasterfensters bleiben zulässig. Quelle und Kanal werden gemeinsam als Vorschauproof gebunden; der vorhandene atomare Commit mit Cold-Readback, Elternaktualisierung und Rollbackschutz bleibt bestehen.
7. Ein nativer Grid-Tick konnte vor dem asynchronen `onInit` auf noch nicht initialisierte Daten zugreifen. Er wartet jetzt auf die bestehende Ready-Barriere. Kein Routing-/Player-Rewrite.
8. Echte 720p-Screenshots zeigten eine abgeschnittene dritte Statuszeile. Das Panel bietet nun drei vollständige Statuszeilen und zwei vollständige Kanalzeilen. Die anschließende unabhängige Pixelprüfung bestätigt beide Auflösungen ohne Clipping. Reine Geometrieassertions hätten diesen Nachweis nicht erbracht.

## Reproduzierbare Tests und unabhängige Reviews

Beide projektlokalen QA-Profile wurden vor Änderungen unabhängig angewandt; beide Erstanalyseberichte wurden abgewartet. Die Client-API bietet keinen Custom-Agent-Selektor. Stattdessen lesen getrennte, ausschließlich lesende Subagenten die vollständigen TOML-Profile und verwenden die darin festgelegten Modelle/Efforts. Keine automatische Custom-Agent-Interception behauptet.

Jeder bestätigte Reviewbefund wurde zuerst als roter Regressionstest reproduziert. Anschließend korrigiert und erneut unabhängig geprüft. Testsetups für absichtlich leeres Vollkatalog-Browsing setzen wegen der neu verlangten Suchvorbelegung nun ausdrücklich `query=''`; ihre ursprünglichen Pagination-/Quellidentitätsassertions bleiben erhalten.

| Prüfung | Tatsächlicher Stand |
|---|---|
| Neue Artwork-/Mappingfälle einschließlich später Reviewbefunde | RED vor jeweiliger Korrektur nachgewiesen |
| Betroffene Host-Suite am letzten Layoutstand | **159 PASS** in 11,57 s (erweiterte Suite einschließlich bestehender Status-/Quellentests); überlappende Teilmengen werden nicht addiert |
| Unabhängiger Artwork-Review38dbe103 /835bea99 | 66 PASS; eigener Matcher/Decoder/Detailpfad, Settingsschutz und Reservefallback; alle14PNG unabhängig geprüft; scoped ARTWORK_QA_PASS |
| Unabhängiger Mapping-Review38dbe103 /835bea99 | 69 PASS; eigene Async-Save-/Cancel-/Readback-Repros und alle 12 PNG geprüft; ausgewiesene native Grenzen bleiben offen |
| Alle 17 PO-Kataloge | PASS |
| Review-ZIP CRC und jeder Member gegen aktuelle Quelle | PASS, 901 Dateien |
| Erste vollständige GHA-Pytestsuite b5dd5f9 | **4197 PASS / 7 FAIL**, keine grüne Gesamt-CI |
| Lokale vollständige Suite im eingeschränkten Sandboxlauf b5dd5f9 | **4076 PASS / 128 FAIL**; überwiegend gesperrte Socketerstellung, außerdem Versions-/Paketverträge und altes Pagination-Setup |
| Unveränderte QA-/97-Baseline, vollständige GHA-Pytestsuite | **4119 PASS / 62 FAIL** in 911,21 s; darunter veraltete Versions-/Quellhash-/Paketverträge |
| Vollständige finale GHA-Pytestsuite38dbe103 | **4206 PASS / 6 FAIL** in 1046,09 s; nur sechs unten benannte historische Versions-/Paketverträge |
| Vollständige finale GHA-Unittests38dbe103 | 4201 Tests: **4195 PASS /4 FAIL /2 ERROR** in 1431,676 s; dieselben sechs historischen Verträge |
| Native Linux-Kodi-Grid/Mini-Dialogstrecke c5f02ea6 | 720p/1080p funktional PASS; synthetischer Mini-Elternowner ausdrücklich separat |
| Native finale Mapping-Pixelprüfung38dbe103 | 720p/1080p PASS; alle 12 PNG unabhängig geprüft, Status vollständig und Quellenpicker tatsächlich offen |
| Nativer Bildpfad c5f02ea6, 720p | Erwartete echte synthetische Bildpixel in Hero und Detail nach 305 s vorhanden; neuer Statusabschnitt scheitert an absichtlich geschützter, falsch vorbereiteter Testrevision |
| Nativer vollständiger Artwork-Lauf38dbe103,720p | PASS einschließlich sichtbarer vier Statusfälle,305-s-Bildstabilität,13Fremdwidgets und zwei Offline-Neustarts |
| Nativer vollständiger Artwork-Lauf38dbe103,1080p | PASS; Bildstabilität 306,11 s, vier Statusfälle, 13 Fremdwidgets und zwei Offline-Neustarts |
| Zusätzlicher nativer Fokusobserver835bea99 | **4/4 native Jobs PASS**, Run44099402205 SUCCESS; source/tests/ZIP identisch, Host/Baseline gezielt nicht wiederholt |
| Physische Android-RK3528-/Kodi21.3-Abnahme | **ANDROID_NOT_TESTED** |

Die erste GHA-Suite scheitert an sechs historischen .96-Versions-/Paketverträgen sowie einem durch Suchvorbelegung veralteten Preview53-Paginationssetup. Das Setup wurde korrigiert. Der spätere vollständige c5-Unittestlauf deckte außerdem acht durch die neue allgemeine Statusprojektion verdrängte ältere Detailerklärungen auf (4199 Tests, 12 FAIL / 2 ERROR). Diese echten Regressionen wurden mit den unveränderten älteren Tests rot reproduziert und korrigiert: Neue Detailtexte gelten nur für neue Policy-/Settingsfehler; vorhandene differenzierte Quellenhinweise bleiben maßgeblich. Die erweiterte betroffene Suite besteht 159 Tests. Die historischen Vertragsprüfungen werden nicht übersprungen oder abgeschwächt; der vollständige unveränderte .97-Basislauf ist separat dokumentiert. Die sechs verbleibenden Vertragsfehler sind unten einzeln aufgeführt. Die Hashfixture beschreibt exakt die überprüften aktuellen Quellbytes; sie erlaubt keine beliebigen Änderungen. Das historische .96-ZIP wird nicht ersetzt.

Relevante Kommandos mit installierten Testabhängigkeiten:

```sh
python -m pytest -q tests/test_xcmate_artwork482.py tests/test_xcmate_mapping482.py tests/test_xcmate_preview_02953.py tests/test_xcmate_issue474_save.py tests/test_xcmate_issue474_views.py tests/test_xcmate_mini_mapping_02996.py tests/test_xcmate_storage_logo_02996.py tests/test_xcmate_integration_02996.py
python tools/validate_kodi_po.py
python tools/run_host94_contract.py -- python -m pytest tests -q
python tools/run_host94_contract.py -- python -m unittest discover -s tests -v
python tools/run_issue482_native.py --kind mapping --resolution 1280x720 --report-dir /tmp/native482-mapping720 --addon-zip docs/XCMate/test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip
python tools/run_issue482_native.py --kind artwork --resolution 1920x1080 --report-dir /tmp/native482-art1080 --addon-zip docs/XCMate/test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip
```

Die vollständigen Hostsuiten materialisieren ausschließlich unveränderliche, bytegeprüfte historische Testinputs in einem temporären Clone. Keine Wiederherstellung in einem Installationskanal. Native Dockerläufe nur auf ausreichend großen CI-Runnern. Workflow hat ausschließlich Leserechte, keine Tokens für Provider und keinen Merge-/Veröffentlichungsschritt.

## Sechs verbliebene historische Vertragsfehler

Diese Tests scheitern auch in der unveränderten .97-Baseline. Sie werden nicht ignoriert oder als PASS gemeldet. Vier erwarten weiterhin Manifestversion .96; zwei verlangen das unveränderte historische .96-Reviewpaket beziehungsweise dessen Manifest. Das neue .97-Review-ZIP wird separat vollständig und reproduzierbar geprüft. Die Gesamt-CI ist deshalb weiterhin rot.

| Test | Fehler |
|---|---|
| `test_gsmedia_repo_180.GsMediaRepo180Tests.test_xcmate_release_unchanged` | .97 statt fest erwarteter .96 |
| `test_repository_layout.RepositoryLayoutTests.test_xtreammate_manifest_and_remote_service` | .97 statt fest erwarteter .96 |
| `test_xcmate_branding.XCMateBrandingTests.test_display_name_and_version` | .97 statt fest erwarteter .96 |
| `test_xcmate_cumulative_02922.IconContractTests.test_original_icon_bytes_dimensions_and_kodi_asset_reference` | Versionsanteil erwartet .96; Originalicon unverändert |
| `test_release_candidate96.Release96.test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes` | Historisches .96-ZIP hat anderen Dateisatz als aktuelle .97-Quelle |
| `test_release_candidate96.Release96.test_review_package_never_stages_or_authorizes_any_channel` | Festes .96-Manifesterfordernis beim .97-Build |

Eine zukünftige Pflege dieser historischen Releaseverträge gehört in einen eigenen transparenten Wartungsschritt. Es wurde kein geschütztes Paket überschrieben, um sie grün zu machen.

## Grenzen der nativen Belege

Der vorhandene native Harness verwendet tatsächliches Linux-Kodi21 mit BINGIE2.2.3, echte sichere Bildübertragung, Decoder, Texturen und Screenshots; die Inhalte und APIantworten sind synthetisch. Der native Bildmatcher wird durch einen synthetischen Kandidaten ersetzt; der tatsächliche eigene Matcher wird separat im Host gegen synthetische API-Antworten geprüft. Native Bildbelege bestätigen Transport, Decoder und sichtbare Texturen, keinen echten Anbieter-/TMDB-Account. Der neue Statusabschnitt injiziert ausschließlich Producerzustände, um deren reale Hero-Textbindung isoliert zu prüfen; er belegt nicht, dass ein echter Provider denselben Fehler geliefert hat.

Ein gesundes Hostbild ist kein nativer Pixelnachweis. Ein nativer Linuxnachweis ist kein Androidnachweis. Der Mini-Persistenzadapter wird tatsächlich verwendet, sein bisheriger nativer Elternowner ist jedoch synthetisch; die Mini-Elternspalte muss auf der Box geprüft werden. Eine 27-MiB-Kapazitätsinjektion in Python ist kein echter voller Android-Datenträger. Nicht überprüfte Grenzen bleiben offen.

## CI und unabhängige Belege

- [Vollständige Produktprüfung, Run44096702746](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44096702746): alle vier nativen Jobs PASS, beide Hostsuiten FAIL ausschließlich an den benannten sechs Altverträgen.
- [Unveränderte .97-Baseline, Run44092120323](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44092120323/job/134069650244): 4119 PASS /62 FAIL.
- [Ergänzende native Receipts, Run44099402205](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44099402205): **SUCCESS**, vier native Jobs bestanden, keine erneute Host-/Baselineausführung, keine Veröffentlichung. [Receiptdatei](test-evidence/issue482/native-focus-receipts.json) belegt Home-Fokus3580/Home50=false vor dem gezielten Wechsel und2510/Home50=true mit passendem Sender und32-stelligem Token danach. Die Guards bleiben aktiv.
- [Konsolidierte unabhängige Agentenberichte](QA_NACHREVIEW_ARTWORK_EPG482_2026-11-17_DE.md).
- [Originalscreenshots und Einzelprüfsummen](test-evidence/issue482/README.md).
- [Identischer Produkt-/Hosttestbaum zwischen den Prüfcommits](test-evidence/issue482/source-identity.json).

## Reviewpaket

[Installierbares .97-Review-ZIP](test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip) · [SHA256](test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip.sha256)

SHA256: `16c81e587cfe1739ae463ec69ba6d142ab75146e47c8273ae6a779ec750a1042`.

Das Paket enthält keine tatsächlichen Konten, privaten Logs, Token oder Benutzer-Datenbanken. Es wird nicht automatisch auf einer Box installiert oder in einen Repository-Katalog aufgenommen. Alle bisherigen Review-Prüfsummen sind damit überholt.

## Android-Abnahme – zunächst alle ANDROID_NOT_TESTED

| ID | Prüfung | Erwartung |
|---|---|---|
| ART482-A | Vorhandene Bildfreigabe und Token auf unverändertem Profil | Kein erneuter Tokenimport; passende Bilder in Hero und Details tatsächlich sichtbar |
| ART482-B | Bekanntes Provider-/XMLTV-/TMDB-Ereignis | Quelle und Bild stimmen zur Sendung; keine fremde Zuordnung |
| ART482-C | Gleiche Sendung mindestens fünf Minuten, Fokuswechsel und Kodi-Neustart | Gültiges Bild bleibt korrekt; keine schwarze Zwischenphase oder falsche Erfolgsmeldung |
| ART482-D | Bestehendes Nein/Später oder echte Schutzpause | Sichtbarer konkreter Zustand, kein ungewollter externer Abruf und kein Abschalten der Reserve |
| MAP482-A | Großer EPG und Mini-EPG: fokussierter Disney-/Kabel-Sender → EPG zuweisen | Konfigurierte Quellen direkt sichtbar, korrekter Suchvorschlag, keine Senderwiedergabe |
| MAP482-B | Kabel Eins/Kabel1HD/DE-Präfix, mehrere Quellen mit gleicher Kanal-ID | Verständliche Vorschläge; keine stille +1-/Quellenverwechslung |
| MAP482-C | Vorschau mehrerer Quellen, dann Abbrechen/Zurück | Programme in Raster/Dialog vergleichbar; ursprüngliche Zuordnung, Zeit, Gruppe und Fokus wiederhergestellt |
| MAP482-D | Quelle laden → Fehler/Timeout → erneut laden | Konkreter Fehler, bedienbarer Retry, kein endloser falscher Spinner |
| MAP482-E | Gültige Auswahl speichern und neu öffnen/Kodi neu starten | Speichern bestätigt; source+channel und richtige Programme persistent |
| MAP482-G | Große Quellkataloge bis 20.000 Kanäle | Treffer, Nichttreffer und tatsächliche ARM32-Latenz messen; Hostmesswerte nicht als Gerätetest übernehmen |
| MAP482-F | Nullprogramme, voller Worker, schneller Quellenwechsel/Abbruch | Save erklärt gesperrt; keine alten Treffer/Callbacks, keine Daten-/Playeränderung |
| REG482-A | Live-TV, Film, Serie/Autoplay, sechs Widgets und Favoriten | Bisherige Funktionen und Benutzerkonfiguration erhalten |

Keine Beschädigungen künstlich auf dem Benutzerprofil erzeugen. Fehlersimulationen gehören in die isolierten Host-/CI-Fixtures. Private Logs nicht öffentlich hochladen. Ein Scheitern ist als FAIL mit datensparsamem Code zu dokumentieren, nicht als vermeintlicher Erfolg.
