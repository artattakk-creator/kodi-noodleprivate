# XCMate .49 – Testbericht Widget-Hotfix #252

Stand: 28.10.2026 (Europe/Berlin). Basis `main` .48: `0f825fbd8b7280aea6dae6c236c23533b6dc3f02`. Quellbuild `a83df5293829939df58160b6c87531a55400c194`. Branch `hotfix/xcmate-02949-widget-picker`.

## Ergebnis

**2.035 Hosttests PASS in 296.641 s.** 0 Fehler, 0 Failures, 0 übersprungene Tests. Alle **2.021 bestehenden Testmethoden** erhalten, **14 neue**. Sauberer `git archive`-Build mit regulärem Bootstrap/Upgrade/Build. Deutsche und englische PO-Dateien mit jeweils **1.085 Kontexten**, 92 Navigationstexturen/Lizenzen und Python-Syntax gültig. Bekannte unveränderte SyntaxWarning im vendorten `SMBProtocol.py`; kein neuer Syntaxfehler. Socket-/SMB-Regressionen auf freigegebenem lokalem Host-Testnetz, keine echte Box und keine privaten Rohlogs verwendet.

`TESTLOG_02949.txt` enthält den vollständigen synthetischen Hostlauf; ausschließlich abschließende Zeilenleerzeichen normalisiert. Beide Log-SHA256 stehen in `TESTERGEBNISSE_02949.json`.

## Neue Belege

- Exakter deutscher Menüpfad und drei unmittelbar sichtbare echte Ordner, `isFolder=True`, `IsPlayable=false`, `files`-Directory und einmaliges erfolgreiches Ende ohne Diskcache.
- Echte vorhandene Leaf-Routen mit Sendern/Filmen/Serien, korrekten Contenttypes und Klickzielen; kein automatischer Playerstart beim Browsen. Alte URLs ohne `pid` und mit vorhandenem Aktualisierungsparameter bleiben gültig.
- Negative `RunPlugin`-Handles öffnen die normale Quellansicht einmal; fehlendes/deaktiviertes explizites Portal fällt nicht auf einen anderen Account zurück.
- Profil-/Skin-/Cover-/Guide-Sentineldateien, Optionen und bestehende Bindings bleiben beim Öffnen bytegleich. Status-/Hero-Demo separat erhalten.
- Englische/deutsche Beschriftungen und tatsächliche BINGIE-Speicheranleitung; kein URL-Textviewer als Einrichtungsersatz und kein vorgetäuschter Speichererfolg.
- Unveränderte Originalmethoden des gepinnten Skinshortcuts-Referenzexplorers durchlaufen XCMate Home → Settings → Appearance → Widgets → jede Quelle → **Use as widget**. Ergebnis enthält exakte alte `widgetPath`-URL, `Addon`/`videos`; serialisierter URL lädt erneut echte Elemente. Cancel liefert kein Binding. Herkunft, SHA und GPL-2.0-only-Lizenz unter Testfixtures.
- Exakter Dateischutz und Erhalt sämtlicher alten Methoden ohne neue Skips. 558 alte Quelldateien bytegleich; sieben exakt überprüfte Label-/Routing-/Versionsänderungen, ein neues Add-on-Modul. Film-/Serienwidget-Reader und Autorefresh, .42-Stop, EPG/Mapping, Profile, Cover, Autoplay/Resume, Settings-IDs und Skinadapter unverändert. 62 fremde WIP-Dateien unverändert.

Ein erster gezielter Arbeitslauf deckte einen fehlenden DialogProgress im Testmodell und die nötige Abgrenzung des älteren Freeze-Helfers von zukünftigen Baselines auf. Beides im Hostmodell korrigiert; keine Testmethode entfernt oder übersprungen. Der abschließende saubere Gesamtbuild ist der oben genannte Lauf.

## Paket

`plugin.video.xtreammate-0.1.29.49.zip`, **3,071,999 Bytes**, **566 Dateien**.

SHA256: `2b0dc58c60355c2c70cdf91589c571ee7cd12eb3e40fe7c70f66d1f9f12ab7ff`

CRC, eindeutige/sichere Pfade, keine Symlinks oder Profile/DBs/Rohlogs/Bytecode, AST-Prüfung aller Python-Dateien: PASS. Alle **566 Paketdateien bytegleich zum Quellstand**; eigene deterministische ZipInfo-Rekonstruktion ergibt exakt dieselben Bytes. Prüfkataloge in `PAKETPRUEFUNG_02949.json`, `DATEIKATALOG_02949.json`, `SCHUTZPRUEFUNG_02949.json`.

## CI und Geräteabnahme

GitHub Actions baut und testet den finalen Liefer-HEAD unabhängig; genauer Run/Ergebnis und berechneter Paket-SHA im Draft-PR. Der produktive Publish-Schritt muss bei einem PR **skipped** bleiben. Keine automatische Merge-/Releaseaktion.

**Android: W49-01, W49-02, W49-03 jeweils NOT_TESTED.** Der öffentliche BINGIE-Referenzstand ist 2.2.2, der Explorer stammt aus Skinshortcuts v2.0.3; kein exakter Snapshot der installierten BINGIE-2.2.3-/Skinshortcuts-Kombination liegt vor. Das Referenzmodell ist daher kein Nachweis echter Home-Pixel, Skin-Speicherdateien oder Neustartpersistenz auf der Nutzerbox. Dies wird durch den dreistufigen Android-Test explizit geprüft. Box A und alle Geräte unangetastet; keine Fremd-Skin-Datei geschrieben. Echte Hero-Integration bleibt ein getrennter Folgeauftrag.

Siehe `URSACHENANALYSE_02949_DE.md` und `ANDROID_ABNAHME_02949_DE.md`.
