# XCMate .67 – Host-, Kodi- und Paketnachweis

Arbeitsstand: Draft-PR #308, kumulative Basis .66. Maßgeblich ist der erfolgreiche **Publish GS Media Kodi updates**-Lauf am aktuellen PR-Head. Keine Android-PASS aus Hosttests ableiten.

## Nachvollziehbare Gates

- Syntax: compileall für Produktionscode und neue native Playback-Fixtures.
- Gezielte .67-Tests: echte SQLite-Fehlersimulation, Alias-/Manual-Priorität, begrenzter RAM-Fallback, Transport, URL-Segment-Encoding, Short-EPG-Cooldown/429, Diagnose, TVmaze-Identität/Bildhosts, TMDB-Reihenfolge, gezielter Retry und GUI-I/O-/Attributionsregeln.
- Unveränderter historischer Bestand: alle **2719 bisherigen Testmethoden einschließlich bestehender Skip-Bedingungen**; alle **653 .66-Quelldateien** vorhanden. Exakte Änderungen über benannte Reviewed-Hook-Fixtures nachvollziehbar, keine entfernten Altmethoden.
- Native Kodi-Linux-Wiedergabe: fünf echte Dekodierungen (TS/HLS/extensionlos, vier Startkerne) sowie tatsächliche Ablehnung von 504/HTML. Ausschließlich synthetischer Loopback-Anbieter; kein privates Portal. API-Kurz-EPG-Aufrufe müssen null sein. Neustart während des Tests ist FAIL.
- Bestehende acht native Kodi/BINGIE-GUI-/Transportprüfungen einschließlich 88 Sendern, 803 Gruppen, Film-/Seriencovern, Fremdposter-/Musikfokus und identischer lokaler TMDB-TV-Art auf Home/Details bleiben aktiv.
- Ergänzende native Prüfung des gemeinsamen Guide-/Mini-Vorschau-Renderers mit lokalem Ereignis, sichtbarem TMDB-Logo und Pixelnachweis; der Test ersetzt keine Android-Guide-/IR-Abnahme.
- PO-Validierung, Originalicon-/Lizenzprüfung und gesamte unittest-discover-Suite.
- Paket: vollständige Übereinstimmung aller ZIP-Dateien mit src, CRC, keine doppelten/unsicheren Pfade, keine Datenbanken, Rohlogs oder privaten Profildateien; kanonischer Builder und Kodi-Indexprüfung.

## Artefakte und Ergebnisgrenzen

Das Artefakt `xcmate-review-308-<sha256>` enthält `plugin.video.xtreammate-0.1.29.67.zip`, zugehörige `.sha256`, `test-results.log` und `build-verification.json`. Diese JSON enthält den tatsächlich getesteten Commit, Testanzahl, Dauer, Dateianzahl, ZIP-Größe und SHA256. Kodi-Evidenz liegt in den getrennten Artefakten `kodi21-live67-playback-<commit>` und `kodi21-helper57-transport-<commit>`. Prüflauf und konkrete Ergebnisse werden im PR verlinkt. Ein fehlgeschlagener oder veralteter Lauf ist keine Abnahme.

Bisherige Zwischennachweise: 19 gezielte neue Hosttests PASS. Der frühere vollständige Vorlauf fand den fehlenden Icon-Wrapper des neuen Diagnose-Senderdialogs; korrigiert und erneut zu prüfen. Der erste neue native Wiedergabelauf brach im isolierten Container ab; ein solcher Zwischenlauf zählt nicht als PASS. Entscheidend ist der abschließende grüne Nachweis am PR-Head.

## Issue-Abnahmematrix

| Bereich | Code-/Hoststatus | Echte Android-Abnahme |
|---|---|---|
| #307 EPG-Kerntext/automatischer Alias | Reproduziert und repariert; genaue Tests im CI | NOT_TESTED |
| #291 lokaler Snapshot / Revision / Abkühlung | Begrenzter Fallback und Regression; vorhandener Refresh bleibt erhalten | NOT_TESTED |
| #307 Live-Format / native Übergabe | Live-spezifische Reparatur und native Tests; 504-Geräteursache UNCONFIRMED | NOT_TESTED |
| #300 eigener TMDB-Zugang / Preview / Attribution | Direkter Supplier, lokaler Cache, gezielter Retry, Credits; optionaler TVmaze-Fallback | NOT_TESTED |
| Widget-/Medienbestand / .42-Stop | Unveränderter Bestand plus Regression erforderlich | NOT_TESTED |
| #303/#306 Repository/Wizard | Außerhalb dieses Hotfixes, nicht übernommen | NOT_TESTED |

Box A bleibt unverändert. Kein Merge, kein produktives Release, kein Geräteeingriff und keine Datenlöschung. Abschlussbericht und tatsächliche CI-Ergebnisse haben Vorrang vor Planwerten.


## Zwischenzeitlicher main-Fortschritt

Repository 1.8.1 Lite wurde während dieser Arbeit außerhalb dieses PR nach main gemergt (eb8aae1557eb221fe7601b00d64adc7e401530c4). Der Hotfix entwickelt dessen Repository-/Wizard-Funktionen nicht weiter und übernimmt keinen experimentellen Wizard-Branch. Die bereits veröffentlichten main-Änderungen bleiben kumulativ erhalten. Die neue Repository-Versionsprüfung wird lediglich auf den ausdrücklich beauftragten XCMate-Stand .67 aktualisiert; alle ursprünglichen Methoden bleiben bestehen.


## Vollsuite und historische Testmodelle

Der erste vollständige .67-Lauf am Head 75c68a7 führte 2766 Methoden aus und fand Fehler im optionalen Vorschaupfad der alten nativen API-Modelle. Kein PASS dieses Laufs: Die Ergebnisse sind historischer Fehlernachweis, kein freigegebenes Paket. Die Vorschau prüft nun vollständige native Control-/Monitor-Fähigkeiten, bleibt abbrechbar und vermeidet identische Setter bei 200 unveränderten Wiederholungen. Ihr echtes Verhalten wird unabhängig mit vollständiger Kodi-API und sichtbaren Bildpixeln geprüft. Der bestehende Live-Kern und seine alten Assertions werden unverändert ausgeführt.

Zwei alte Scope-Prüfungen wurden an den ausdrücklich autorisierten Auftrag angepasst: Der AST-Routingvergleich normalisiert ausschließlich die vollständig gepinnten .67-Deltas, prüft danach weiterhin sämtliche anderen Routen; die frühere experimentelle programme_tvmaze59.py bleibt verboten, ausschließlich die neue opt-in programme_tvmaze67.py ist zugelassen. Keine alten Methoden oder Skip-Dekoratoren entfernt. Das minimale Startup-Player-Testdouble akzeptiert den neuen expliziten Live-Parameter; seine ursprünglichen Resolver-/Direktstart-Assertions bleiben erhalten. Die betroffenen Modelle und Datenintegritätsfälle werden zusätzlich vor den langen nativen Läufen geprüft.

Die fortgeltenden Fokus-/Hero-Sichtbefunde aus #300 und die vier konkreten EPG-Kanalfälle aus #291 stehen im kumulativen Box-B-Androidplan weiterhin auf NOT_TESTED.
