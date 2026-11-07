# XCMate 0.1.29.78 – Test-/Buildbericht

Auftrag #385, kumulativ ab .77 (`80932cc20502dc267018bfded4f2a8cc0ce77e24`). **Android: ANDROID_NOT_TESTED.** Die bestätigten .77-FAIL werden nicht umetikettiert. CI-/Veröffentlichungsnachweis und endgültiger Merge-Stand werden nach tatsächlichem Abschluss in #385 ergänzt; ein offener Draft allein ist keine Veröffentlichung.

## Installationspaket

- Version: **0.1.29.78**, Add-on-ID `plugin.video.xtreammate`.
- [Review-ZIP](test-builds/02978/plugin.video.xtreammate-0.1.29.78.zip), 3.451.947 Bytes, 746 Quelldateien.
- SHA256: `4c66e66d95a5cba5eb35690ddc74168f852bcc2dad38d2ba8bb004f671cb191d`.
- ZIP-CRC, Inventar, sichere Pfade und bytegenaue Source-Parität geprüft. Keine privaten Profile, Datenbanken, Logs oder Token im ZIP.
- Installer **0.5.26 unverändert**, ZIP-SHA256 `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`.

## Reproduzierbare Prüfungen

`SQLITE_TMPDIR=/tmp python -m unittest discover -s tests -v` ist der vollständige Hostlauf. CI baut vorher zusätzlich alle regulären Pakete/Indizes. Die 739 bisherigen Quelldateien sowie alle alten Testmethoden und Skip-Bedingungen bleiben mit exakt geprüften Deltas erhalten. Der aktuelle vollständige Lauf und CI sind beim Öffnen des Drafts noch in Prüfung; maßgeblich ist der abschließende grüne Actions-Lauf, kein vorweggenommener PASS.

Bereits ausgeführte ergänzende Nachweise:

| Prüfung | Ergebnis |
|---|---|
| 117 bestehende Owner-/Navigation-/Exit-Regressionen einschließlich spätem ACK und fremden Modals | HOST_PASS |
| 67 gezielte Home-/Quellen-/Scope-/Release-Prüfungen; zusätzlich bekannte .77-Adapter vs. unbekannte Skinänderung | HOST_PASS |
| 52 bestehende Settings-PIN-/Suchfenster-/Native-Init-/Scope-Prüfungen nach finaler Settingskorrektur | HOST_PASS |
| 11 bestehende pytest-Brandingprüfungen | HOST_PASS |
| 17 gettext-Kataloge, 92 PNG-Navigationstexturen und Herkunft/Lizenz | HOST_PASS |
| Natives Kodi/BINGIE Home 1280×720: 31 Bild-/Fokusfälle, 20 echte Richtungsaktionen | HOST_PASS |
| Natives Kodi/BINGIE Home 1920×1080: dieselben Prüfungen | HOST_PASS |
| Jeweils echter Kodi-Neustart, eigener Reload-Hook, zusätzlicher Skinreload, 88/24/24 Einträge | HOST_PASS |
| .78 auf Android 21.2/21.3 ARM32, reale Provider-/TMDB-Bilder | ANDROID_NOT_TESTED |

Die Home-Prüfung enthält eine bereits vor der Reparatur vorhandene, nichttriviale Nutzerkonfiguration mit „Neu im Kino“, Film-/Serien-, Musik- und weiteren Fremdreihen. Ein absichtlich cachetreffender Builder führt **keinen** Skinreload aus. Der echte Produktionspfad muss genau einmal nachladen, zentrale Variablen und sechs reale Controls bestätigen, alle Nutzerdateien bytegleich erhalten und nach Neustart weiterhin 88/24/24 liefern. Echte PNG-/JPEG-Texturpixel derselben synthetischen Eventidentität werden im Hero und in Programmdetails geprüft. `TEXTURE_PENDING` bleibt sichtbar von READY unterschieden. Diese Linux-Tests verwenden farbige synthetische Bilder und einen isolierten Provider, keine privaten Android-Daten und keine echte Sendungsbild-Abnahme.

[720p Live](test-builds/02978/evidence/720-home75-live-5.png) · [1080p Live](test-builds/02978/evidence/1080-home75-live-5.png) · [Kino-Reihe](test-builds/02978/evidence/1080-home75-foreign-poster-0.png). JSON-Nachweise liegen im selben evidence-Ordner.

Native Media-Exit-Prüfung: `python tools/run_kodi_media77_contract.py --report-dir /tmp/xcmate78-native-media` (20 Stops/ACK je Live, Film und Episode); Ergebnis wird nach abgeschlossenem Lauf ergänzt. Die neue gezielte Late-ACK-Simulation prüft darüber hinaus ACK nach Ablauf der unveränderten Fünf-Sekunden-Beobachtungsgrenze, genau einen Stop und geschützte GUI-Rückkehr.

## Fehler während der Entwicklung

Der erste Volltestlauf war rot: alte Mock-Parser bildeten korrekt quotierte Builtins nicht ab; historische Late-ACK-Erwartungen widersprachen dem neuen #385-Vertrag; das zusätzliche versteckte Settingsflag stand zunächst außerhalb einer Kategorie. Diese Fehler wurden korrigiert, ohne Testmethoden/Schutzprüfungen zu entfernen. Ein großer SQLite-Sortiertest scheiterte zusätzlich an vollgelaufenem temporärem Testspeicher; ausschließlich reproduzierbare extrahierte Host-Skin-/Compilerkopien wurden entfernt, die Beweisdateien erhalten. Ein erster nativer Cache-Hit-Test deckte ein ASCII-Encodingproblem im **synthetischen Builder** und eine fehlende RAM-Receipt nach Test-Neustart auf; UTF-8 und getrennte Erststart-/Neustartprüfung wurden korrigiert. Rote Vorläufe werden nicht als bestandene Builds ausgegeben.

## Issue-Matrix / Grenzen

- **#385 / #367:** Include-/Variablen-/Runtime-Gate, eigener Cache-Hit-Fallback, Erhalt alter Reihen, Generationsschutz, Reload und native Fokusprüfung implementiert; Android offen.
- **#366 / #380:** sichere exakte URL-Normalisierung, erlaubte Resize-Parameter, DNS-Fehlertrennung, aktuelle Aliasauflösung und tatsächlich gebundene synthetische Texturen; echte korrekte Sendungsbilder auf Android offen. Vorhandener Token und bewusste Opt-outs bleiben erhalten.
- **#368:** später Stop-ACK, getrennte GUI-Rückkehr, Schutz vor zweiten Stops/fremden Playern; echter Rockchip-/MediaCodec-Abbau bleibt Android-Abnahme.
- **MyVideos131 / fremde Kinodatenquelle:** read-only Diagnose erhalten, keine unbelegte DB-Reparatur. Fehlende Views einer tatsächlichen Fremdquelle bleiben **BLOCKED** bis Schema-/Quellennachweis am Gerät; gespeicherte Reihe wird erhalten.

[Ursachenanalyse](URSACHENANALYSE_02978_DE.md) · [Android-Abnahme](ANDROID_ABNAHME_02978_DE.md).

## Veröffentlichung nach grünem Source-CI und Merge

Die explizite Benutzerfreigabe gilt ausschließlich .78 und erlaubt Veröffentlichung **vor** Android-Abnahme. `tools/release_channel75.py` prüft dafür Version, #385, ausdrückliche Kanalflags, NOT_TESTED ohne Android-PASS und den exakten ZIP-Hash. Fehlende/falsche Freigabe, falscher Hash und .79 bleiben gesperrt.

Vorgesehene, anschließend öffentlich zu verifizierende byteidentische Pfade:

- Regulär: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.78.zip`
- Pilot: `online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.78.zip`
- NeoDark3 direkt: `online-test/plugin.video.xtreammate-0.1.29.78.zip`

`tools/publish_xcmate78_all.py --public` prüft beide echten Feed-MD5, alle drei ZIPs/SHAs, Source-Parität, NeoDark3-Link und den unveränderten Installer. Native Update-Erkennung wird getrennt über `tools/run_channels78_native.py --channel regular|pilot --report-dir ...` geprüft: alte installierte Metadatenfixtures, echte öffentliche Repository-URLs und Kodi AddonBrowser; keinerlei Installer-/App-Code ausführen und keine produktiven Profile mounten.
