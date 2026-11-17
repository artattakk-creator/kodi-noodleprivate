# Bildabruf .90/.97 und EPG-Zuweisung #482 – Reviewbericht

Stand: 17.11.2026. Draft-PR [#484](https://github.com/artattakk-creator/kodi-noodleprivate/pull/484). **Kein Merge und keine Veröffentlichung freigegeben.** Dieser Bericht wird nach den laufenden Gesamt-/Pixelprüfungen ergänzt; ausstehende Nachweise sind keine PASS-Ergebnisse.

## Quellenbasis und Bestandsschutz

| Stand | Unveränderliche Quelle |
|---|---|
| Veröffentlichte .90 | `9bbf75040378dcaead9128880a909fe7978143a4` |
| Veröffentlichte .97 | `f0f6649edf075338bb6a806eff231eb718948368` |
| QA-/Anforderungsbasis #483 | `1cea11d75c6f61accc39142aeb1c0004a88da4cb` |
| Produktprüfung vor letzter Layoutkorrektur | `929167cbbc56ce8badbbcc534ebca2a3dcc62b8e` |

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
8. Echte 720p-Screenshots zeigten eine abgeschnittene dritte Statuszeile. Das Panel bietet nun drei vollständige Statuszeilen und zwei vollständige Kanalzeilen. Neue Pixelprüfung ist erforderlich; reine Geometrieassertions ersetzen sie nicht.

## Reproduzierbare Tests und unabhängige Reviews

Beide projektlokalen QA-Profile wurden vor Änderungen unabhängig angewandt; beide Erstanalyseberichte wurden abgewartet. Die Client-API bietet keinen Custom-Agent-Selektor. Stattdessen lesen getrennte, ausschließlich lesende Subagenten die vollständigen TOML-Profile und verwenden die darin festgelegten Modelle/Efforts. Keine automatische Custom-Agent-Interception behauptet.

Jeder bestätigte Reviewbefund wurde zuerst als roter Regressionstest reproduziert. Anschließend korrigiert und erneut unabhängig geprüft. Testsetups für absichtlich leeres Vollkatalog-Browsing setzen wegen der neu verlangten Suchvorbelegung nun ausdrücklich `query=''`; ihre ursprünglichen Pagination-/Quellidentitätsassertions bleiben erhalten.

| Prüfung | Tatsächlicher Stand |
|---|---|
| Neue Artwork-/Mappingfälle einschließlich später Reviewbefunde | RED vor jeweiliger Korrektur nachgewiesen |
| Betroffene Host-Suite am letzten Layoutstand | **101 PASS** in 7,83 s; überlappende Teilmengen werden nicht addiert |
| Unabhängiger Artwork-Review auf 929167cb | 8 PASS; eigener gesunder Matcher/Decoder/Detailpfad, Settingsschutz ohne Netzwerk, Reservefallback PASS |
| Unabhängiger Mapping-Review auf 929167cb | 69 PASS; eigene echte Async-Save-/Cancel-/Readback-Repros PASS |
| Alle 17 PO-Kataloge | PASS |
| Review-ZIP CRC und jeder Member gegen aktuelle Quelle | PASS, 901 Dateien |
| Erste vollständige GHA-Pytestsuite b5dd5f9 | **4197 PASS / 7 FAIL**, keine grüne Gesamt-CI |
| Lokale vollständige Suite im eingeschränkten Sandboxlauf b5dd5f9 | **4076 PASS / 128 FAIL**; überwiegend gesperrte Socketerstellung, außerdem Versions-/Paketverträge und altes Pagination-Setup |
| Unveränderte QA-/97-Baseline, vollständige GHA-Pytestsuite | **4119 PASS / 62 FAIL** in 911,21 s; darunter veraltete Versions-/Quellhash-/Paketverträge |
| Vollständige finale Hosttests | Laufen; Ergebnisse folgen |
| Native Linux-Kodi-Grid/Mini-Dialogstrecke c5f02ea6 | 720p/1080p funktional PASS; synthetischer Mini-Elternowner ausdrücklich separat |
| Native929-Pixelprüfung | 720p zeigte Statusclipping; Quellenpicker- und Aufnahme-Synchronisierung korrigiert, Nachprüfung läuft |
| Nativer Bildpfad c5f02ea6, 720p | Erwartete echte synthetische Bildpixel in Hero und Detail nach 305 s vorhanden; neuer Statusabschnitt scheitert an absichtlich geschützter, falsch vorbereiteter Testrevision |
| Native finale Statusbindung und Lesbarkeit | Noch ausstehend; Fixture nutzt nun die vorhandene verifizierte Snapshotrevision, ohne Produktguard zu ändern |
| Physische Android-RK3528-/Kodi21.3-Abnahme | **ANDROID_NOT_TESTED** |

Die erste GHA-Suite scheitert an sechs historischen .96-Versions-/Paketverträgen sowie einem durch Suchvorbelegung veralteten Preview53-Paginationssetup. Das Setup wurde korrigiert. Die historischen Vertragsprüfungen werden nicht übersprungen oder abgeschwächt; die unveränderte .97-Basis wird separat geprüft. Die Hashfixture beschreibt exakt die überprüften aktuellen Quellbytes; sie erlaubt keine beliebigen Änderungen. Das historische .96-ZIP wird nicht ersetzt.

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

## Grenzen der nativen Belege

Der vorhandene native Harness verwendet tatsächliches Linux-Kodi21 mit BINGIE2.2.3, echte sichere Bildübertragung, Decoder, Texturen und Screenshots; die Inhalte und APIantworten sind synthetisch. Der neue Statusabschnitt injiziert ausschließlich Producerzustände, um deren reale Hero-Textbindung isoliert zu prüfen; er belegt nicht, dass ein echter Provider denselben Fehler geliefert hat.

Ein gesundes Hostbild ist kein nativer Pixelnachweis. Ein nativer Linuxnachweis ist kein Androidnachweis. Der Mini-Persistenzadapter wird tatsächlich verwendet, sein bisheriger nativer Elternowner ist jedoch synthetisch; die Mini-Elternspalte muss auf der Box geprüft werden. Eine 27-MiB-Kapazitätsinjektion in Python ist kein echter voller Android-Datenträger. Nicht überprüfte Grenzen bleiben offen.

## Reviewpaket

[Installierbares .97-Review-ZIP](test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip) · [SHA256](test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip.sha256)

SHA256: `474700daf3c666faf11aa61688882b39af8788c53e81fa7357d3b328b0a97e59`.

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
| MAP482-F | Nullprogramme, voller Worker, schneller Quellenwechsel/Abbruch | Save erklärt gesperrt; keine alten Treffer/Callbacks, keine Daten-/Playeränderung |
| REG482-A | Live-TV, Film, Serie/Autoplay, sechs Widgets und Favoriten | Bisherige Funktionen und Benutzerkonfiguration erhalten |

Keine Beschädigungen künstlich auf dem Benutzerprofil erzeugen. Fehlersimulationen gehören in die isolierten Host-/CI-Fixtures. Private Logs nicht öffentlich hochladen. Ein Scheitern ist als FAIL mit datensparsamem Code zu dokumentieren, nicht als vermeintlicher Erfolg.
