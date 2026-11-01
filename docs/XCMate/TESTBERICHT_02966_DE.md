# XCMate .66 – Technischer Testbericht

Maßgeblich sind der letzte grüne CI-Lauf am exakten PR-HEAD, seine Artefakte und die Abschlussdokumentation in PR #302 / Master #301. Frühere rote Entwicklungsläufe bleiben nachvollziehbar; kein Gate wird übersprungen. Kein Android-PASS aus Hosttests.

## Pflichtprüfungen

- Alle 647 ursprünglichen .65-Quelldateien und 2665 Methoden/Skip-Bedingungen erhalten; nur exakt hinterlegte Änderungen in Snapshotverträgen.
- Neue .66-Tests: unabhängige Quellenplanung, Katalog-Wartephase, 24-h-Cap bei erhaltenem Setting, erfolgreiche/fehlgeschlagene/deaktivierte Quellen.
- 88 nie fokussierte Sender, persistenter Offline-Kaltstart, drei konfigurierte Quellen, Now/Next für alle Sender, Mapping-/Portalgrenzen, Lückengründe und DST.
- Eindeutige Zeitkorrektur derselben Quelle, unveränderte andere Programme, konservative mehrdeutige Intervalle, legitime aufeinanderfolgende MacGyver-Titel und Transaktionsrollback.
- TV ohne Folgennummer, Produktionsjahr/Remake-Konflikt, unabhängige Details, vollständige Suchseite, Opt-in, fehlendes Artwork, persistente lokale Datei mit SHA und identischem Event.
- Native vierdateibasierte BINGIE-Vorschau/Ja/Nein/Hashschutz/Rücknahme; lokale Framegeometrie und korrekte Property-Reihenfolge.
- Vollständige Film-/Seriensuche über >1000 Titel, abgeleiteter Genreindex, getrennte Portale, aktivierte/deaktivierte Kategorie. Widgets bleiben bewusst kleinere Neuheitenlisten.
- Alle bisherigen sieben nativen Kodi-/BINGIE-Strecken plus neue gemischte Fremdwidget-/Musik-/Poster-/Live-Fälle. Kontur gegen die tatsächlichen synthetischen Kachelpixel vergleichen, nicht nur Item-ID. Textkollisionen und Home-/Detailbild prüfen.
- Volle Regression, PO-/Icon-/Syntaxprüfung, Manifest .66, kanonisches ZIP, CRC, sichere Pfade, Source-Bytevergleich, SHA256 und keine privaten Dateien.

## Messungen und Ausgabe

tools/benchmark_xcmate66.py misst alle 88 Sender beim lokalen Kaltread und warmen RAM-Read, ohne HTTP. tools/run_kodi_home66_contract.py erzeugt den tatsächlichen nativen Kodi-Versionswert, Screenshots, Kontur-/Kachelgrenzen, Fremdwidgetfälle und Bildnachweis. Alle Fixtures sind als synthetisch / NOT Android gekennzeichnet.

Die bestehende historische .64/.65-Messung bleibt als Regression erhalten, ist kein Android- und kein vollständiger Versionsvergleich. Reale 1-s-Anzeigezeit, tatsächliche Providerzahlen und TMDB-Artwork müssen auf Box B separat abgenommen werden.

Finale Testanzahl, Laufzeiten, CI-Links, eventuelle BLOCKED-Gates und ZIP/SHA stehen am exakten HEAD im PR-Abschluss. PR bleibt ohne neue Freigabe offen; kein produktiver Publish-Nachweis wird vor einem tatsächlich genehmigten Merge behauptet.
