# PR #50 – XCMate 0.1.30: vollständiger Prüfbericht

Stand **21.10.2026**. [Bestehender Draft-PR #50](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50), Branch `feat/xcmate-space-premium-installer`, Ausgangsstand `5dcca09c8d4d6912d7be8e9ed04fae3d068472d5`. [Vollständiger verbindlicher Auftrag](CODEX_AUFTRAG_PR50_ONLINE_RENDERER_20261021_DE.md), [Originalkommentar](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50#issuecomment-6302773561).

**Automatisierte Prüfung bestanden; Geräteabnahme und vollständige grafische Abnahme offen.** Alle 98 Originalbilder sind vorhanden, bytegleich geprüft und paketiert. 86 Originalbilder sind zur Laufzeit angebunden; zwölf haben noch keinen Verbraucher. Issue #40 ist nicht als gelöst nachgewiesen. Draft beibehalten; **kein Merge, Release oder Produktivindex-Update ausgeführt**.

## Pakete und unabhängiger Nachweis

| Paket | Dateien / Bytes | SHA-256 |
|---|---|---|
| [Core 0.1.30](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.zip) | 125 / 785.140 | `0334e765a71b540a88ac51a6c7bf924ebc3df1f98b9e29f31df9fa068ed58c9f` |
| [Space Premium 1.0.0](../../themes/xcmate/space-premium/XCMate-Space-Premium-1.0.0.zip) | 98 Bilder / 19.772.084 | `8fc7f312a65fa5ecdbe68d3487939a25d685de29717896a0a1113c8d41176ae2` |

Beide Builds erfolgreich. Der offizielle Repositorybuilder lief ausschließlich in einer isolierten vollständigen Kopie. Nur Core-Test-ZIP und SHA-Datei wurden zurückkopiert; der produktive Index blieb unverändert. CRC, Dateiliste, sichere Pfade, jede Datei gegen aktuelle Quellbytes, Metadatenreferenzen, Abwesenheit von Profilen/Accounts/DB/WAL/SHM/Logs/Bytecode und zweiter byteidentischer kanonischer Core-Bau bestanden. Das freigegebene permanente Core-Icon hat SHA-256 `81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135`; kein optionales Theme nötig.

Theme neu mit dem Hostbuilder gebaut: bytegleich zur bestehenden 1.0.0. Alle 98 Bilder vollständig mit Pillow decodiert; SHA, Maße und Alpha gegen das vorliegende Manifest geprüft. Zusätzlich GitHub-Git-Blob `c6c72acf0179b3d4bbb197416814ac45f38a0e95` unabhängig als Base64 heruntergeladen: exakt 19.772.084 Bytes, identischer Hash, Manifest/98 Bilder/106 Keys bestätigt. Der frühere Tracker-Abgleich ist laut Nutzer bereits erfolgt; der Tracker wurde in dieser Runde **nicht neu heruntergeladen**. Keine neuen Originalgrafiken, Konvertierung oder Versionsersetzung.

## Online-Katalog und Installer

GitHub ist die einzige offizielle Online-Quelle. Der installierte Core bleibt am erlaubten **main**-Katalog gebunden; Drive dient Archiv/Quelle. Aktuelle anonyme HTTP-Prüfung: `main/addons.xml` 200, `main/themes/xcmate/catalog-v1.json` **404**, referenzierte Theme-ZIP auf main **404**. Online daher noch nicht produktiv verfügbar. Neuer lokalisierter 404-Hinweis statt allgemeinem Downloadfehler. Kein stiller Branch-/Drive-Fallback.

Katalog und Hostbuilder erlauben verschiedene Theme-IDs/Versionen; zwei unterschiedliche ausschließlich temporäre Fixtures durchlaufen den echten Downloader mit simuliertem Transport sowie Import, Aktivierung, Versionsanzeige, Update, Standardwahl und Abbruch. Keine Testgrafiken veröffentlicht. Normalisierte Versionsduplikate und leere Kompatibilitätsintervalle werden abgewiesen, fehlerhafte Wurzelform kontrolliert validiert.

Bestehende Sicherheitsgrenzen bleiben wirksam: HTTPS-Repository-Allowlist, keine Redirects, Größen-/Zeitbudgets und begrenztes Lesen; ZIP-Pfade/Typen/CRC/Hashes, PNG-Inflate und Nebenmetadatenbudget, freier Speicher, Abbruch vor Commit, atomare Revisionen/Auswahl, unveränderliche Versionen und sichere Fallbacks. Import/Download laufen im abbrechbaren Worker, nicht im Remote-Callback. Bestehende Benutzerprofile, Bildcaches, EPG-Quellen/-Mappings und Accounts werden nicht migriert oder gelöscht.

## Renderer und Freeze

[Maschinenlesbare Matrix](SPACE_PREMIUM_RENDERER_MATRIX_030.json) enthält **jede der 98 Originaldateien und jeden der 106 logischen Keys**, Hash/Properties, Verbraucher, Bedingung und Status. 61 Keys BOUND, 29 CONDITIONAL, 1 CORE_BUNDLED, 3 ALIAS_ONLY, 12 UNCONNECTED; das sind **86 tatsächlich angebundene unterschiedliche Dateien**. Tool: `python -B tools/xcmate_theme_mapping.py --output <datei>`.

Neue lokale Texture-Anbindungen: Livegruppen/-sender, Infobar, Progress-Track, Controls und Extras; EPG-Hintergründe/Zustandsicons/Programmaktionen; reale Mediaaktionen und Favorit plus/minus; Widget-Fallbacks ohne Überschreiben echter Providerbilder; Such-/Back-/Rail-/Poster-Dekorationen. Keine neue fokussierbare Dekoration. Bestehende Control-IDs, Bounds, Navigationsziele und Action-Callbacks bleiben erhalten. Keine HTTP-Aufrufe beim Navigieren; Ansichten halten lokale Snapshots. Ein EPG-Fehlerstatus bleibt bei Fokusbewegung erhalten, bis ein neues Abfrageergebnis vorliegt; nativer Callback-Test ergänzt.

**Noch unverbundene zwölf Originale:** `branding.fanart`, `branding.splash`, `branding.wordmark`, `icon.epg.auto-switch`, `icon.epg.record`, `icon.epg.today`, `icon.player.skip-back`, `icon.player.skip-forward`, `icon.shared.filter`, `icon.shared.sort`, `icon.shared.warning`, `panel.loading`. Fehlende Aufnahme-/Auto-Switch-/Skip-Funktionen werden nicht vorgetäuscht; keine neue Lade-/Startanzeige vor Klärung #38/#40. Vollständige Designabnahme ist deshalb offen, ebenso alle echten Kodi-Screenshots. Paketvollständigkeit ist keine Rendererabnahme.

Die Freeze-Referenzdateien wurden **nicht geändert**. Der AST-Vergleich normalisiert ausschließlich eng definierte Texturresolver-Hooks in drei Live-Methoden; übriger Methoden-AST bleibt gegen ursprüngliche Referenz identisch. Native Omega-Ereignisfolge mit installiertem Originaltheme wird zusätzlich gegen unveränderten Stock-Navigator verglichen: gleicher Modus, Fokus und Auswahl. Kein manuelles `WindowDialog.onInit()` als Lebenszyklus-Ersatz. Strict GUI-Signaturtests prüfen auch neue Aufrufe gegen Kodi 21.3; `getCurrentWindowId` ist im gepinnten `ModuleXbmcgui.h` vorhanden (Commit `a3a448d26b8d560a65655dab2cd122994dc4e146`, Header-SHA `98c301e4a609e808dce6a0936e7e0c6035e1667f5311d7811f122d33be739296`).

## Issue #40 – belegte Befunde und Grenzen

Issue und Kommentare vollständig gelesen. Live-BACK-Spinner ist am Gerät beobachtet, aber ohne verwertbare Fenster-/Busy-/Zeit-Logs nicht reproduziert oder kausal erklärt. VOD-/Folgen-Audiostopp und Resume bleiben am Gerät zu prüfen. Keine Annahme „Theme verursacht den Hänger“ oder „Stop-Fix löst den Hänger“.

Untersuchter Pfad: Dialog-BACK schließt zunächst Ebenen, später den Dialog; er ruft keinen Player-Stop oder Container.Refresh auf. Snapshot-Schließen setzt nur ein Event, kein Worker-Join. Vorhandene Close-/Diagnose-Checkpoints enthalten weiterhin lokale IO. Service überwacht verifizierte eigene Wiedergabe vor optionalen EPG-Jobs; erst Verlassen des zuvor gesehenen Fullscreens führt zum Ownership-geprüften Stop. Media-Rückkehr speichert Resume vor Stop mit erneuter Identitätsprüfung, fremde Streams sind ausgeschlossen.

**Nachgewiesener separater Fehler:** Kodi kann `stop()` bestätigen, bevor `isPlayingVideo()` falsch wird. Wiederholter Rückkehrcallback konnte dasselbe Item mehrfach stoppen. Regression scheitert auf Baseline `5dcca09` und besteht mit Korrektur: zweisekündiger Pending-Marker für den Fingerprint des verifizierten Items; anderes Item bleibt frei, nativer Stop-Fehler räumt Marker zum Retry. Kein atomarer, alle parallelen Interpreter umfassender CAS behauptet. Ownership-/Resume- und Overlay-Navigationspolicy bleiben erhalten.

Neue Exitdiagnose: begrenzte In-Memory-Queue (64), Servicepersistenz mit begrenzter Historie (16), erlaubte Window-/Dialog-/Busy-/Zeitdaten und Codes EXIT_REQUESTED/RESUME_CHECKPOINT/STOP_SENT/STOP_PENDING/STOP_FAILED/FULLSCREEN/NAVIGATION. GUI-Checkpoint flusht neue Exitdaten ausdrücklich **nicht** auf Disk. Sofortige INFO-Zeilen `[XCMate][EXIT]` sowie `BACK_RECEIVED` aus bestehendem Inputtrace helfen, falls der Service vor einem Hänger nicht mehr persistiert. Keine URLs, Account-/Streamnamen oder rohen Sessionmarker. Nach Beenden/Neustart lokale JSON-Diagnose, kodi.log **und kodi.old.log** auswerten; neue Tests belegen Persistenz ohne Zugangsdaten. Diagnosefehler dürfen Stop/Navigation nicht beeinflussen.

## Automatisierte Tests und CI

**509/509 Tests bestanden, 65,820 s, keine Fehler/Failures/Skips.** Vollständiges `python -B -m unittest discover -s tests -v` nach isoliertem offiziellem Repositorybau; `compileall -q src` bestanden. Zusätzliche 37/37 Diagnose-/Exit-/Renderer-Tests bestanden (4,580 s):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python -B -m unittest \
  test_xcmate_issue12 test_xcmate_exit_040 test_xcmate_theme_live_030
python -B tools/validate_xcmate_catalog.py
```

Der gezielte Einzellauf deckte zusätzlich eine ältere Fixture-Abhängigkeit von der Discovery-Reihenfolge auf (`play_intent`/Kodi-Import). Das Issue-12-Identity-Fixture stubbiert nun den separaten Handshake explizit und prüft die übergebene Session; keine Runtime-Änderung hierfür. Danach fokussierter Lauf grün. Das vollständige neue Playback-/Handshake-Verhalten wird von den vorhandenen eigenen Tests weiter geprüft.

Geprüfte Regressionen umfassen reales Original-Theme plus native WindowDialog-/WindowXML-Ereignisse, stockidentische Liveeingaben, Defektfallback, echte Mediaaktionen/Widgetart/Guide-Zustände ohne Navigation-HTTP, generischen Mehrtheme-Katalog, 404/Offline/Hash/Kompatibilität, Archiv-/Bildlimits/Cancel/atomare Installation, asynchronen Stop/Retry, Profil- und Freeze-Erhaltung. Kleine synthetische Themebilder sind ausschließlich Testfixtures.

**Alle drei CI-Läufe erfolgreich**, geprüfter Implementierungscommit `c7a7ecd77b448323979ffec60fbd5f30cbf66537`:

| Prüfung | Ergebnis / Nachweis |
|---|---|
| Gesamtsuite, Syntax, Repositorybau und Core-Artefakt | [39511206845](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39511206845) SUCCESS; Publish-Schritt **SKIPPED** |
| Katalog/alle Originalbilder | [39511206877](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39511206877) SUCCESS |
| Theme- und Core-Neubau, unveränderliche 1.0.0 | [39511202966](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39511202966) SUCCESS |

[Core-CI-Artefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39511206845/artifacts/12305232920), Name enthält den oben geprüften inneren Core-SHA-256. [Beide Pakete aus Theme-/Core-Build](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39511202966/artifacts/12306620319), [Katalogbericht](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39511206877/artifacts/12305327591). Uploads und Run-/Job-/Artefaktmetadaten bestätigt; äußere Artefaktdigests stehen im [Maschinenbericht](TESTERGEBNISSE_THEME_030.json). **Kein heruntergeladener CI-Binärnachweis behauptet**; Rohlogtransport abgewiesen, CI-Testzahl nicht direkt aus Rohlog gelesen. Die Zahl 509 stammt aus dem abschließenden lokalen vollständigen Lauf. Der erfolgreiche CI-Prepare-Schritt prüft seinerseits Testsummen/OK, exakte Quellbytes und sichere ZIP-Inhalte.

Zusätzlich nach Push die tatsächlichen Core-GitHub-Blob-Bytes `736a3e87248a95faf16fdc6040e780038e781ab9` unabhängig geladen: **785.140 Bytes**, identisch zum lokalen ZIP, SHA und CRC bestanden. Dieser unabhängige GitHub-Dateinachweis ist vom nicht heruntergeladenen Actions-Artefakt ausdrücklich getrennt. Nachfolgender Dokumentationscommit ändert keine Core-/Theme-/Test-/Workflowbytes.

## Veröffentlichungssperre und nächster Schritt

Draft-Theme-Build besitzt nur `contents: read`, erzeugt beide Artefakte und schreibt keinen Commit; vorhandene 1.0.0 muss bytegleich bleiben. Bisher automatischer Main-Publish-Schritt ist gesperrt: künftig ausschließlich expliziter Owner-`workflow_dispatch` auf main mit `publish_repository=true` (Standard **false**). Weder PR noch Push veröffentlicht generierte Repositorydateien. Dieses Opt-in wurde **nicht ausgelöst**.

Main bleibt `116d653efb95df18a4ba750cb33d108fc2e2c276`, produktiv Core 0.1.29.2, dessen ZIP bytegleich. Noodle Private, andere Add-ons, produktiver Index und globale Keymaps unverändert. Keine Tags/Releases/Merges.

Offene Gates: [vollständiger Android-Testplan](ANDROID_TESTPLAN_THEME_030_DE.md), besonders #40 mit Audio/Resume/Busy, IR/Fokus/BINGIE, reale Texture-Screenshots, Offline/Defekt, 720p/1080p/4K und RAM/Kaltstart; zwölf Renderer-Reserven; Online-HTTP-200 auf dem Gerät **erst nach späterer Freigabe**. #37 lokale Gruppengröße und #38 ~17-s-Start separat bekannt, hier weder behoben noch kausal erklärt.

Empfehlung: **PR bleibt Draft**, jetzt geprüfte Dateien lokal am Android-TV testen. Danach Benutzerentscheidung über Restintegration und Merge; erst ein freigegebener Merge macht GitHub-Themes auf main verfügbar. Regulärer Core-Repositoryupdate bleibt eine davon getrennte ausdrücklich freigegebene Aktion. Keine automatische Veröffentlichung.
