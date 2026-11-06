# XCMate 0.1.29.76 – Testbericht zum unveröffentlichten Folge-Draft

Basis: main `b3024e9620e8924e880a70fc92ca70e4b5a5658b` (.75). Datum: 06.11.2026. Diese Version setzt ausschließlich die Freigabe um, unsichtbare Film-/Serienseiten automatisch nach verifizierter Bild-/Fallback-Vorbereitung zuzulassen. Sichtbares Rendering bleibt getrennt.

## Funktionsnachweis

| Zulassung | .75 | .76 |
|---|---|---|
| Filmvorbereitung | Live-TV nativ bereit | Unverändert |
| Serienvorbereitung | Filmleiste tatsächlich geöffnet | Alle aktivierten Filmseiten verifiziert vorbereitet |
| Restliche Hintergrundarbeit | Serienleiste tatsächlich geöffnet | Alle aktivierten Serienseiten verifiziert vorbereitet |
| Sichtbarkeitsnachweis | Native Beobachtung | Weiterhin ausschließlich native Beobachtung, separat von der Phase |

Neue Tests: **19 PASS** (16 Ablauf-/Datenprüfungen, 3 kumulative Schutzprüfungen). Unter anderem: echte Veröffentlichung im bestehenden Worker, unveränderter Fokus, kein falscher Sichtbarkeitsnachweis, Queue allein nicht ausreichend, ungültige/veraltete Signaturen, Provider-Policy und Quellreferenzen, mehrere Portale, deaktivierte Bereiche, bestätigtes Leer-Ergebnis gegenüber Indexfehler, Kontextwechsel während Prüfung und fehlender Datensatz bei identischer Veröffentlichungssignatur.

Vorhandene .75-Vertragstests: **43 PASS**. Zusätzliche Branding-Pytests: **11 PASS**. Erster Gesamt-Hostlauf: **3.113 Tests in 537,865 s, 3.111 PASS und 2 Speicherfehler des Testhosts**. Beide unveränderten Fälle bestehen nach Bereitstellung freien, beschreibbaren temporären Speichers in gezielter Wiederholung. Drei neue Bestandsschutztests wurden anschließend zusätzlich bestanden; damit sind alle 3.116 aktuellen Unittest-Fälle abgedeckt, aber der erste Gesamtlauf war ausdrücklich kein vollständig grüner Lauf. Die frische Gesamt-CI wird mit ihrer Head-Commit-ID im abschließenden PR-Testkommentar ausgewiesen. Kein Android-Ergebnis wird daraus abgeleitet.

## Echter Kodi-21.2-Linux-Test, 1280×720

**PASS:** 29 Bild-/Fokusfälle mit nativer Screenshot-Pixelprüfung, 20 echte Up/Down-Eingaben, horizontale Leiste, feste Hero-Geometrie `270,20 / 1080×580`, fehlende optionale Progress-Controls sowie nativer Kodi-Neustart. Nach Neustart alle 88 Sender, 24 Filme und 24 Serien vorhanden, 32 geschützte Dateien SHA256-unverändert.

Nach automatischer Film-/Serienvorbereitung: `phase=3`, `prepared=[vod,series]`, `visible=[live]`, Fokus bleibt Live-TV. Erst anschließendes tatsächliches Öffnen erzeugt `MOVIES_VISIBLE_READY` und `SERIES_VISIBLE_READY`.

Der synthetische Neustartlauf protokollierte LIVE_HOME_READY um 04:30:20.939 UTC, MOVIES_PREPARED um 04:30:23.973, SERIES_PREPARED/REST_WARM_BEGIN um 04:30:24.003, MOVIES_VISIBLE_READY erst um 04:30:24.379 und SERIES_VISIBLE_READY erst um 04:30:27.472. Die Zeitabstände enthalten absichtliche Test-Wartezeiten und Screenshotarbeit; sie sind keine Provider-/Android-Latenzmessung. 29 Screenshotfälle: 2008,64–3425,60 ms, Median 3103,93 ms inklusive Test-Wartezeiten.

Maschinenlesbare Nachweise: [native720-home75.json](test-builds/02976/native720-home75.json), [native720-post75.json](test-builds/02976/native720-post75.json). Der `.75`-Name bezeichnet die weiterverwendete native Teststrecke, der getestete Quellstand ist .76.

## Host-Umgebung und Wiederholungen

Der erste große HTTP-Katalogtest scheiterte in SQLite mit `database or disk is full`. Nach Entfernen ausschließlich reproduzierbarer expandierter Skin-Testkopien aus `/tmp` und mit `SQLITE_TMPDIR=/tmp` besteht derselbe Test: je **200.005 Titel**, je **109.380.521 HTTP-Bytes**, SQLite bis **621.731.840 Bytes**, VOD 34,565 s und Serien 31,981 s. Keine Produktdaten oder Bilder wurden entfernt, keine Produkt-Speicherschutzgrenze verändert. Die Legacy-Skin-Migration meldete im Gesamtlauf ebenfalls `OSError: [Errno 28] No space left on device` und besteht separat unverändert in 1,310 s. Die ursprünglichen Fehler werden nicht als bestandener erster Gesamtlauf ausgegeben.

Nachweise: [ursprünglicher Gesamtlauf](test-builds/02976/host-initial.log), [HTTP-Wiederholung](test-builds/02976/http-writable-temp.log), [Legacy-Wiederholung](test-builds/02976/legacy-recheck.log), [neue Tests](test-builds/02976/new.log), [Branding](test-builds/02976/pytest.log). Maßgeblich für den frischen Gesamt-CI-Lauf sind die Checks und der abschließende Testkommentar des Draft-PRs; [Actions des Entwicklungsbranches](https://github.com/artattakk-creator/kodi-noodleprivate/actions?query=branch%3Afix%2Fxcmate-02976-prepared-home-gates).

## Paket und Grenzen

[ZIP](test-builds/02976/plugin.video.xtreammate-0.1.29.76.zip): 3.426.830 Bytes, 729 Dateien, CRC und Dateivergleich mit Quellstand PASS. [SHA256-Datei](test-builds/02976/plugin.video.xtreammate-0.1.29.76.zip.sha256):

`c6b3813a6b2e9289251d3e14ea8425e0fe3fb35ee9a01dda457aa81a27e081cc`

Regulärer Katalog, Pilot-Katalog und veröffentlichte .75-ZIP bleiben bytegleich zum freigegebenen main-Stand. Es wird weder gemergt noch veröffentlicht. Keine Änderungen an Routing, Layout, Player, Portalen, Einstellungen oder Datenbanken. Die Artefakte enthalten ausschließlich synthetische Testdaten.

**Android:** sämtliche PREP76-01 bis PREP76-08 `ANDROID_NOT_TESTED`; [Anleitung](ANDROID_ABNAHME_02976_DE.md). Kein neuer ARM32-/MediaCodec-PASS; #368 ohne nativen Stop-ACK bleibt offen. Kein neuer einstündiger Soak für .76. Automatische Vorbereitung ist ausdrücklich kein Beweis für dekodierte oder sichtbare Bilder.
