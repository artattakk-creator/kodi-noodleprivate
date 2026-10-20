# Integrationsprüfung – ein Release-Kandidat XCMate 0.1.29.2

20.10.2026. [Verbindlicher Auftrag](CODEX_AUFTRAG_INTEGRATION_0292_DE.md).
**Ergebnis: für den Android-Gerätetest vorbereitet; keine Produktivfreigabe.**
Produktiv bleibt **0.1.28**, `main` unverändert auf `63b4cd6981351a398968a3795831cf024b07b2ba`.
Kein PR gemergt, kein Tag/Release, kein produktiver Repositoryindex geändert.

## 1. Alle fünf PRs und Abhängigkeiten

| PR | Status bei Prüfung | Basis | Geprüfter Ausgangs-Head |
|---|---|---|---|
| [#39](https://github.com/artattakk-creator/kodi-noodleprivate/pull/39) | OPEN / Draft / mergeable | `main` | `295f9d4` |
| [#45](https://github.com/artattakk-creator/kodi-noodleprivate/pull/45) | OPEN / Draft / mergeable | `fix/xcmate-028-startup-hang` | `27dfe33` |
| [#46](https://github.com/artattakk-creator/kodi-noodleprivate/pull/46) | OPEN / Draft / mergeable | `fix/xcmate-owned-playback-exit` | `c5cea4f` |
| [#47](https://github.com/artattakk-creator/kodi-noodleprivate/pull/47) | OPEN / Draft / mergeable | `feat/xcmate-persistent-media` | `dec3ee4` |
| [#48](https://github.com/artattakk-creator/kodi-noodleprivate/pull/48) | OPEN / Draft, QA ergänzt | `feat/xcmate-active-continuous-live` | `3150105` vor QA |

Jeder Head ist Commit-Vorfahre des nächsten. `git merge-base --is-ancestor` bestätigt,
dass #48 **alle** Änderungen aus #39/#45/#46/#47 enthält. Die vier Vorgängerbranches
wurden nicht verändert. Nur #48 erhielt autorisierte Integrationskorrekturen und
Prüfnachweise. Vollständige Head-/Basis-SHAs stehen im maschinellen Bericht.

## 2. Ein vollständiger Stand statt fünf Installationen

Der RC enthält Start-Hotfix, Wiedergabestopp, persistente Bilder/Favoriten/Folgenstatus,
aktive Gruppen, kontinuierliche Senderliste, alle Quellenadapter, Assistent und Editor.
**Ein Update 0.1.28 → 0.1.29.2 mit genau einer ZIP ist vorgesehen.** Die vier früheren
ZIP-Versionen sind historische Phasenartefakte und keine Installationsvoraussetzung.
Isoliert geprüfter Quellstand: `620a72476494888e6d812b58eb4a1f9cd0ea6e29`;
nachfolgende Bericht-/Artefaktcommits verändern diesen Quellstand nicht.

## 3. Gefundene Fehler und Behebung

Kein textueller Mergekonflikt, keine identischen Patch-IDs und keine überschatteten
Doppeldefinitionen in den Python-Modulen. Die gezielte QA fand dennoch echte Fehler:

| Gegenbeispiel vor Korrektur | Ursache | Korrektur |
|---|---|---|
| Back vor Start des Plugin-Resolvers ließ einen Film später versteckt starten | GUI-Auftrag konnte vor der Kodi-Item-Erstellung nicht storniert werden | Begrenzte opaque Start-Nonce; Resolver prüft Storno vor und nach Quellenauflösung |
| Back nach Resolve, aber vor Video/Puffern ließ spätes Video laufen | Exit-Logik verlangte vorher beobachtetes Vollbild | Explizites Storno gilt auch ohne vorheriges Vollbild; Stop weiterhin nur nach aktueller passender InfoTag-Identität, Positionsspeicherung davor |
| M3U mit gültigen ersten Zeilen und letzter EXTINF ohne URI ersetzte Altbestand | Parser akzeptierte unvollständiges letztes Element | Unvollständige Einträge verwerfen den Import; vorherige Generation/Overrides bleiben |
| Manifest referenzierte nicht vorhandene `fanart.png` | Es existiert `fanart.jpg`; Builder ersetzte JPG-Verweise pauschal | Original-JPEG korrekt referenzieren; Builder behält vorhandene JPEGs, bisheriger PNG-Fallback bleibt für fehlende JPEGs |

Die ersten drei Tests scheiterten am Ausgangsstand (3 FAIL), beide Grafik-/Buildertests
später ebenfalls vor dem Fix (2 FAIL). Dieselben Fälle bestehen danach. Zusätzlich:
Fehler additiver Artwork-Migrationen schließen die DB und protokollieren nur festen
Code `MIGRATION_FAILED`; vorhandene Zeilen bleiben erhalten und erneuter Versuch ist
idempotent. ZIP-Metadaten für XCMate sind reproduzierbar, damit lokaler/CI-RC dieselbe
Prüfsumme erhalten können. Keine neue Bildgestaltung; JPEG-Bytes bleiben unverändert.

## 4. Dateiübersicht

[Vollständige Änderungsliste gegen produktives main](INTEGRATION_0292_DATEIEN.json).
Die neuen QA-Eingriffe betreffen:

- `media_intent`, `media_progress`, `media_window`, `playback_exit`: abbrechbarer
  Startauftrag und verifizierter verspäteter Stop, ohne Live-Callbackänderungen.
- `m3u_store`: Erkennung unvollständiger Einträge vor Freigabe einer Generation.
- `art_store`: Daten-erhaltende und diagnostizierbare additive Schemafehler.
- `addon.xml`, `changelog`, `service`: korrekte Fanart, Version 0.1.29.2 / Service-Build 29.
- `tools/build_repository.py`: vorhandene JPEG-Referenz erhalten; reproduzierbare
  XCMate-ZIP. Andere Add-ons behalten ihre bisherige Verpackungslogik.
- `.github/workflows/publish.yml`: manueller Prüflauf liefert ZIP/Prüfsumme/Testlog/
  Build-JSON als Artefakt. Publish weiterhin ausschließlich `push` auf `main`.
- Integrations-/API-Regressionen und gepinnte Kodi-21.3-API-Referenz in `tests/`.

`src/plugin.video.noodleprivate`, `src/repository.gsmedia`, deren ZIPs und die
produktiven Indexdateien sind gegenüber main bytegleich. `repository.gsmedia`
bleibt **1.7.0**, Noodle Private **0.4.2**. Keine Kodi-/Skin-/Keymap-Konfiguration geändert.

## 5. Frischer vollständiger Integrationsnachweis

**462/462 Tests, 0 Fehler, 0 Failures, 0 Skips, 74,126 s**, nach offiziellem Build in
isolierter Kopie des vollständigen Git-Stands. Das ist ein neuer Integrationslauf,
keine Addition alter Einzel-PR-Ergebnisse. Gesamte Syntaxprüfung aller Add-ons ebenfalls
erfolgreich. Zusätzlich **26/26 HTTP-/EPG-Prüfungen mit httpx/urllib, 1,378 s**.
13 neue Integrationsfälle plus ein neuer gepinnter Kodi-21.3-API-Test.

Der erste Integrationslauf vor Grafikprüfung bestand 459 Tests; die zusätzliche
Paketprüfung fand den Fanartfehler. Dieser frühere Erfolg gilt ausdrücklich nicht
als endgültiger Paketnachweis. Jetzt prüfen die Suite und der CI-Artefaktschritt
auch tatsächliche Manifest-Grafikdateien.

Geprüft: abbrechende/falsche/veraltete Resolver, anderer Account/Fremdplayer,
Speicherung vor Stop, echtes 0.1.28-Profil, ursprüngliche Cover ohne erneuten Download,
parallele EPG-/Artwork-Worker mit nativen UI-Ereignissen, reale Stalker-Handshake-
Ablehnung, partielle M3U, additive Migrationsfehler, ZIP-Reproduzierbarkeit. Bestehende
Groß-/Neustart-/Abbruch-/Speicherplatztests laufen auf diesem integrierten Stand mit.

Messungen: 20.005 M3U-Einträge / 1.727.118 Bytes, 5.002 ausgewählte übernommen;
XMLTV-Selektion 400 Bytes / 2 geparst / 1 gespeichert. Großtests umfassen zusätzlich
>80 MiB HTTP, >200.000 Film-/Serientitel und 160.005 XMLTV-Programme. Cloudzeiten
sind keine Android-Performancezusage. Testprotokolle und Schlussstatus sind im
CI-Artefakt; [maschineller Integrationsbericht](TESTERGEBNISSE_INTEGRATION_0292.json).

## 6. Datenintegrität und Fehlerbehandlung

Der Upgrade-Test verwendet Module aus der **wirklich veröffentlichten 0.1.28-ZIP**,
erzeugt damit Konten aller drei Profiltypen, Gruppenauswahlen, manuelles EPG-Mapping,
Favorit, Fortschritt, Fernbedienungsprofil, Bibliothek, Guide und acht echte Bilder.
Aktuelle Module lesen den Bestand ohne Konfigurationsänderung; Bilder bleiben bytegleich,
DB-Inhalte bleiben erhalten und bekannte Bilder erzeugen keine neue HTTP-Anfrage.
Vorhandene Seen-/Resume-/Favoritentests ergänzen diesen Nachweis.

Keine pauschale Migration/Reset/Delete. Additive Tabellen/Spalten wiederholbar;
Fehler behalten alte Daten. GUI-Requests enthalten IDs/Nonce statt URL/Zugangsdaten.
Ein Startmarker alleine autorisiert **keinen** Player-Stop. Protokolle speichern
Fehlercodes/-typen, keine Provider-Exceptiontexte. Das Installationspaket enthält
keine Tests, Profile, Datenbanken, Logs, `.env`, Bytecode oder Zugangsdaten-Dateien.

Lokaler Buildvorfall: Ein Builderaufruf lief versehentlich einmal im Arbeitsverzeichnis
statt im isolierten Verzeichnis. Acht generierte Dateien wurden danach explizit aus
dem vorherigen Commit wiederhergestellt; Vergleich bytegleich, kein Commit/Push
oder Main-Update dieser Zwischenstände. Endgültiger Build ausschließlich isoliert;
übernommen wurden nur XCMate-ZIP und Prüfsummendatei. Scope abschließend erneut geprüft.

## 7. Funktionierende Live-TV-Fernbedienung

Die QA ändert `live_overlay.py` und die eingefrorenen Remote-/Player-Dateien **nicht**
gegenüber dem bereits integrierten Ausgangsstand #48. AST-/Callback-/Keymap-Regressions-
tests bleiben aktiv. Erstes OK, zweites OK/Runter, Links, Gruppen, Hoch/Runter-Zap und
Overlay-Back werden durch den Medien-Stornozweig nicht ersetzt. Gruppenänderungen aus
#47 und die schon vorhandene explizite Client-Injektion bleiben nachvollziehbare
Ausnahmen zum älteren Freeze. Globale Keymaps werden nicht neu aktiviert/geändert.

Zusätzlich tatsächliche Header und Lebenszyklusquellen aus **Kodi 21.3-Omega**, Commit
`a3a448d26b8d560a65655dab2cd122994dc4e146`, gelesen/gehasht. Strikte Konstruktorparameter
stimmen damit überein, insbesondere `_imageWidth`/`_imageHeight` bei `ControlList`.
`WindowDialog` initialisiert keine Python-`onInit`-Callbackoberfläche; `WindowXML`
ruft diese ausdrücklich auf. Die Tests modellieren genau diesen Unterschied.
**Die reale 0.1.29.2-IR-/Render-/Player-Abnahme bleibt offen.**

## 8–10. Paket, Artefakt und SHA-256

Eine direkt installierbare **`plugin.video.xtreammate-0.1.29.2.zip`**, **120 Dateien /
375.229 Bytes**, Root `plugin.video.xtreammate/`, Manifest-ID und Version geprüft.
CRC, keine doppelten/absoluten/übergeordneten Pfade oder Symlinks, jede Quelldatei
bytegleich, alle Manifest-Grafiken enthalten, Syntax und Abhängigkeiten geprüft.
Python-Standardbibliothek plus Kodi-API; `requests` bleibt optional, HTTP hat urllib-Fallback.

[RC herunterladen](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip) ·
[SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip.sha256).

`55b6b74e262b30cca37eaf8d251753e5cfb5fcfe06f3e13bd28d3452f56b73d6`

[GitHub-Prüflauf erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39449616224), geprüfter Commit `9a3fbab`.
[CI-Artefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39449616224/artifacts/12278445261): Kodi-ZIP, SHA256, Testlog und Build-JSON.
Build, Syntax, Tests, Paketprüfung und Upload erfolgreich; Publish **SKIPPED**.
Die im Artefaktnamen ausgegebene innere ZIP-Prüfsumme stimmt exakt mit der lokalen
RC-Prüfsumme überein. Der unabhängige Binärdownload des CI-Containers aus dieser
Cloud wurde mit HTTP 403 blockiert (0 Bytes); dessen Inhalt wurde deshalb hier
nicht nochmals heruntergeladen/geöffnet. Lokales identisches Quellpaket vollständig
geprüft, CI-Paketprüfung und Uploadstatus über GitHub bestätigt. Bei Actions zunächst den äußeren Artefaktcontainer entpacken;
in Kodi ausschließlich die darin enthaltene Add-on-ZIP installieren.

## 11. Ein-Schritt-Gerätetest, Sicherung und Rollback

[Ausführliche Anleitung und alle Gerätefälle](ANDROID_TESTPLAN_UNIVERSAL_029_DE.md).
Kodi vollständig beenden, gesamtes bestehendes XCMate-Profil einschließlich SQLite-
WAL/SHM und Bild-/Cacheordner lokal sichern. Keine Konten löschen/deinstallieren.
Dann **nur diesen RC** über „Aus ZIP-Datei installieren“ über dieselbe Add-on-ID
installieren; 0.1.28.1/0.1.28.2/0.1.29/0.1.29.1 müssen nicht einzeln installiert werden.
Kodi neu starten, Version und Service-Build prüfen, gespeicherte Daten vergleichen.

Rollback: Kodi beenden, unveränderte 0.1.28-ZIP über dieselbe ID installieren. Für
exakte Rückkehr zur vorherigen Datensicht vollständige Sicherung zurückspielen.
Additive Tabellen bleiben grundsätzlich lesbar/ignorierbar; neue Adapter-Accounts
und neue Funktionsdaten sind in 0.1.28 nicht vollständig bedienbar. Deshalb ist eine
ZIP allein kein Ersatz für die vollständige Sicherung. Kein Kodi-Reset notwendig.

## 12. Offene Grenzen und Android-Abnahme

Kein Androidgerät, keine echte IR-Fernbedienung, keine realen Providerzugänge oder
USB-/SMB-Hardware in der Cloud. Offen: Kalt-/Warmstart, echter Bild-/Tonstopp bei
Back während Puffern, OSD-/Fokusübergänge unter BINGIE/Estuary, Tausendersenderliste,
alle vier Quellen, Stalker-Dialekte/Header/Folgendaten, Budget-/I/O-Grenzen, Offline-
Neustart/EPG, Dateiberechtigungen und Export-Rename. Ursprünglicher Hänger #38 bleibt
unbewiesen. Nicht-Xtream-Autoplay beim Öffnen, Theme-/Sprachpaketinstaller und komfortable
selektive Bildbereinigung sind weiterhin nicht implementiert; manueller Quellenstart ja.

## 13. Freigabeempfehlung und kontrollierter Integrationsweg

**Bereit für den Android-Gerätetest. Keine Empfehlung zur Produktivveröffentlichung
vor Geräteabnahme und ausdrücklicher Merge-/Releasefreigabe.**

Der vorhandene Workflow veröffentlicht bei einem passenden **Main-Push** automatisch.
Fünf naive Einzelmerges würden daher Zwischenversionen veröffentlichen. Zur Freigabe:

1. Erst ausdrückliche Freigabe einholen. Vor dem ersten Main-Merge den Publish-
   Workflow administrativ pausieren. Dies wurde in diesem Auftrag **nicht** getan.
2. #39 → #45 → #46 → #47 → #48 in Reihenfolge integrieren; jeweils nächsten PR auf
   `main` umstellen und Diff prüfen. Merge-Commits bewahren die Commit-Abhängigkeiten;
   keine fünf unabhängigen Squash-/Cherry-Pick-Kopien derselben Vorfahren erzeugen.
3. Nach dem letzten Merge Workflow wieder aktivieren und manuell **prüfen**. Der
   `workflow_dispatch`-Pfad baut/tests/liefert Artefakt, publiziert aber **nicht**.
   Konfliktauflösungen oder Quelländerungen erfordern einen neuen vollständigen Test.
4. Nach separater Releasefreigabe offiziellen Builder isoliert ausführen. Nur
   XCMate-ZIP/SHA256 und `addons.xml`/`addons.xml.md5` als bewussten Releasecommit
   übernehmen. Andere ZIPs unverändert lassen; `repository.gsmedia` nicht erhöhen.
   Ein reiner Artefakt-/Indexcommit passt nicht in den vorhandenen Source-Pfadfilter
   und löst kein zusätzliches generisches Publish aus.
5. Erst danach Kodi „Auf Aktualisierungen prüfen“. Es wird genau das direkte Update
   **0.1.28 → 0.1.29.2** angeboten. Vorher bleibt der offizielle Index bei 0.1.28.

Keine dieser Freigabe-/Main-/Publikationsaktionen wurde ausgeführt. Auf Benutzer-
freigabe warten; ein grüner Cloudlauf ist keine Android- oder Produktionsabnahme.
