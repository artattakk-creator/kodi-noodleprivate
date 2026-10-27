# XCMate .43 – Issue-Abnahmematrix

Stand 27.10.2026, Snapshot vor PR-Anlage: **102 offene Issues**, vollständig in [OPEN_ISSUES_02943.json](OPEN_ISSUES_02943.json) mit GitHub-Links. Alle bleiben offen. Owner Implementierung: Codex; echte Android-Abnahme/Freigabe: Nutzer auf Box B. Ziel des aktiven Blocks .43; Folgearbeiten sind bewusst keinem ungeprüften Versionsversprechen zugeordnet.

Jedes offene Issue steht genau einmal im folgenden disjunkten **Planungs-/QA-Snapshot**. Das sind keine neu erfundenen Geräteergebnisse und keine Umschreibung alter Status/Fehler. Historische FAIL/PASS bleiben im jeweiligen Issue. `.43 ANDROID_PASS/COMPLETED = 0`, bestätigte `.43 Android FAIL = 0` (noch kein Gerätetest); das bedeutet keine Fehlerfreiheit. DEFERRED-Teilaufgaben anderer Issues werden in der Detailmatrix zusätzlich benannt.

| Fachlicher Snapshot | Anzahl | Konkrete IDs |
|---|---:|---|
| IMPLEMENTED / HOST_PASS | 1 | #220 |
| PARTIAL / .43 Android NOT_TESTED | 12 | #74, #102, #108, #111, #127, #151, #159, #190, #191, #201, #203, #216 |
| BLOCKED / Fremdskin oder Rechteaudit | 3 | #19, #206, #207 |
| SUPERSEDED / kein PASS | 2 | #218, #219 |
| DEFERRED / keine .43-Umsetzung | 36 | #14, #27, #29, #30, #31, #58, #60, #62, #63, #64, #65, #69, #71, #90, #98, #99, #106, #113, #115, #123, #126, #135, #136, #150, #161, #171, #172, #173, #176, #177, #180, #195, #196, #197, #199, #200 |
| OPEN / NOT_TESTED in .43 | 48 | #17, #26, #34, #35, #43, #75, #79, #87, #88, #91, #94, #95, #100, #107, #120, #140, #143, #164, #165, #166, #167, #168, #169, #170, #174, #178, #179, #181, #182, #183, #185, #186, #187, #188, #189, #192, #193, #194, #202, #204, #208, #209, #210, #211, #212, #213, #215, #221 |

## Aktiver Block und Abhängigkeiten

Alle technischen HOST_PASS-Angaben verweisen auf [Testbericht](TESTBERICHT_02943_DE.md), vollständiges Testlog und CI im Draft-PR. Android immer NOT_TESTED für .43, sofern nicht als ausgeschlossener Folgeauftrag BLOCKED/DEFERRED. Kein Issue-Close aus einem Host-PASS.

| Issue | Umfang/Dateien und Code-/Hostbefund | Android-Abnahme / verbleibender Auftrag |
|---|---|---|
| #220 | IMPLEMENTED/HOST_PASS: `mini_epg.py`, 10 Setter-/Rollover-/20-Zyklen-Tests, Vorher/Nachher-Probe 5→1 Rahmen und 9000→0 Setter/200 Ticks. | MINIFLICKER43-01–03, MINIVIS/FUTURE; sichtbares Flackern noch NOT_TESTED. |
| #74 | PARTIAL/Bestand: akzeptiertes 108×162-Layout, Railreihenfolge und Fokus erhalten; kein Redesign nach überholter großer Posterforderung. | MED43, REG43; reale Lesbarkeit/Fokus .43 NOT_TESTED. |
| #102 | HOST_PASS neue Generations-/SID-/Schrumpfungsgrenzen in `media_page43.py`/`media_window.py`; alte 1703-Titel-Scrolltests erhalten. | MED43-01–03, mindestens >240/möglichst500, Filme und Serien separat. |
| #108 | PARTIAL: bestehender katalogbasierter Sync erhalten, Seiten gegen Generationsmix geschützt. | Automatische Artwork-GC/Retention und Destruktion DEFERRED; keine Löschfunktion. |
| #111 | PARTIAL: Dynamic-Retry öffnet echte Quelle/validierte Vorschau, persistent alter Single-Job-Retry; konservativer opt-in TMDb-Fallback. | ART43-01–11; reales Aladdin, fehlende Providerbilder/HTTP/TLS .43 NOT_TESTED. |
| #127 | HOST_PASS: gleiche 3-Tab-Suche, Coverpriorität; optionale echte Sprach-/Qualitäts-/Staffel-/Quellenfelder in `search_results.py`/`library_index.py`. | SEARCH43-01–03, kein Fakewert; Gerätefunktion NOT_TESTED. |
| #151 | PARTIAL: `media_picker43.py`, `media_sources43.py`, `media_overrides43.py`, eigene XML, Lizenzen/Settings. Provider/TMDb/Commons/Local, expliziter Save und separat bestätigte Metadaten, Persistenz/Reset ohne Löschen. | ART43-01–11; proactive Kandidaten-Thumbnails, vollständige Suchindexierung manueller Metadaten, EPG-Auswahl FOLLOW_UP. |
| #159 | HOST_PASS/Bestand: existierende katalogübergreifende Provider-Genresuche unverändert, 23 alte Genrefälle erhalten. | SEARCH43-01; manuelle Genreoverrides noch kein vollständiger Index-Fix. |
| #201/#190 | HOST_PASS/Regression: Rock/Rocky, Cursor, Tab-/Trefferhaltung; kein neuer Live-Suchalgorithmus und keine Suchmaskenänderung. | SEARCH43-01–02/REG43-01; 48→0→48 nicht pauschal als Gerätefix behaupten. |
| #191 | Regression/HOST_PASS bestehender Overlaytests, kein zusätzlicher Player-/Overlayumbau. | Live-Info-/Mini-Aufruf kalt/warm und nach Tabwechsel zeitlich messen; reale 19–49s-Verzögerung bleibt NOT_TESTED. |
| #206/#207 | PARTIAL eigenes Widgetbackend: geschützte read-only Snapshots, gleiche Routen/Detail-ID; eigene Film-/Serienwidgets erhalten manuelle Bilder. | WIDGET43-01 und WIDGETMEDIA/LIVE. Fremdes BINGIE/SkinShortcuts-XML/Logo-Layout BLOCKED/FOLLOW_UP; kein Adapter installiert. |
| #203/#216 | PARTIAL historisch: genau ein .42-Android-PASS mit EIN am27.10; vier Exitdateien bytegleich, Default AUS und bestehendes Box-B-EIN erhalten. | LIVE43-01, fünf→20 Zyklen und VOD43 getrennt NOT_TESTED. Keine Behauptung nativen Rockchipfehler generell beseitigt. |
| #208/#211 | HOST_PASS alte Zukunfts-/Eintextebenentests + neue Mini-Fokusproben, keine doppelte Textliste. | MINIVIS/FUTURE/MINIFLICKER; historische Androidbefunde unverändert. |
| #221/#194 | Dieser Kandidat, vollständige Dateimatrix, Open-Issue-Inventur, Test-/Androidplan. | Nutzer-Review → expliziter Merge → danach Gesamtabnahme B; keine automatische Veröffentlichung/Issue-Schließung. |
| #98/#161/#64 | DEFERRED: keine EPG-Zuweisung, Hub oder Fernbedienungslernen in .43. | Eigener freigegebener Folgeauftrag. |
| #19 | Bestehende Rechtekette/GPL-/Ursprungsnachweise erhalten, neue API-/Bildprovenienz separat dokumentiert. | Vollständiger Rechteaudit vor v1.0 weiter BLOCKED, kein pauschaler Lizenz-PASS. |

## Vollständige Source-Dateimatrix gegenüber Main

Nur nachfolgende Änderungen sind in .43 enthalten; historische Dokumente, Keymaps, fremde Skins und vier Live-Exitdateien sind unverändert. Tests/Fixtures dokumentieren exakt erlaubte Quelländerungen; alle 1514 alten Testmethoden bleiben vorhanden. Versionasserts und beide alten Detailmenütests erwarten jetzt .43 bzw. sechs autorisierte Menüpunkte; keine Tests entfernt/übersprungen.

| Datei | Issue / Zweck |
|---|---|
| `THIRD_PARTY_METADATA_43.txt` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |
| `addon.xml` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |
| `changelog.txt` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |
| `resources/language/resource.language.de_de/strings.po` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |
| `resources/language/resource.language.en_gb/strings.po` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |
| `resources/lib/app_routes.py` | #151/#206/#207 – eigene Widget-Art und Lizenzen |
| `resources/lib/detail_menu.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/library_index.py` | #127/#159/#201 – echte Metadaten, manuelle Art, unveränderte Suchverträge |
| `resources/lib/media_art.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/media_catalog43.py` | #102/#111/#151 – Worker, Seitenidentität, Detailintegration |
| `resources/lib/media_data.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/media_metadata43.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/media_overrides43.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/media_page43.py` | #102/#111/#151 – Worker, Seitenidentität, Detailintegration |
| `resources/lib/media_picker43.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/media_sources43.py` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `resources/lib/media_window.py` | #102/#111/#151 – Worker, Seitenidentität, Detailintegration |
| `resources/lib/mini_epg.py` | #220/#208/#211 – Repaint und Auswahl |
| `resources/lib/search_data.py` | #127/#159/#201 – echte Metadaten, manuelle Art, unveränderte Suchverträge |
| `resources/lib/search_results.py` | #127/#159/#201 – echte Metadaten, manuelle Art, unveränderte Suchverträge |
| `resources/settings.xml` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |
| `resources/skins/Default/720p/XCMateArtwork43.xml` | #111/#151 – explizite Bild-/Metadatenauswahl und Persistenz |
| `service.py` | #221/#151 – Version/Build, übersetzte Opt-ins, Abhängigkeit/Lizenz/Changelog |

## Risiken / bewusst keine Integrationsbehauptung

Das eigene Auswahlfenster und PNG/JPEG-Dekodieren sind hostgeprüft, reale Kodi21.3/ARM32-Darstellung/Pillow/API/DNS noch nicht. Eigener TMDb-Token erforderlich, Rechtelage beim Nutzer; Commons liefert nur eine kleine lizenzierte Teilmenge, keine Google-Gesamtsuche. Die Vorschau zeigt zuerst Textkandidaten und erst nach Auswahl ein validiertes lokales Bild. Neue manuelle Dateien sind begrenzt, bestehende Reserve wird nicht abgeschaltet. Ein fehlender Decoder/Budget/Auth ist BLOCKED/Fehler, kein Erfolg. Keine reale Speicher-/Lösch-/Negativkorruptionsprobe auf Box B.
