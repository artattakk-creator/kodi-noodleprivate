# XCMate 0.1.27 – PR #28 synchronisiert und en/de stabilisiert

Stand: 19.10.2026. **Draft-Kandidat, kein Merge und keine Veröffentlichung.**
Dieser Bericht ergänzt den [bisherigen Funktionsbericht](IMPLEMENTIERUNG_027_KATALOG_WIDGETS_EPG_DE.md)
und ist für ZIP, Lokalisierung und aktuellen Prüfstand maßgeblich.

## A. GitHub und kontrollierte Synchronisierung

- Main-Basis: `345b93da663858831725ef0962319bbd22b406d1` / **0.1.26 produktiv**.
- Vorheriger PR-Head: `2681fc9d75db6fe56f912d2a6a489732daf1dc64`.
- Branch: `feat/xcmate-027-catalogue-home`, [bestehender Draft-PR #28](https://github.com/artattakk-creator/kodi-noodleprivate/pull/28).
- Main-Integration als echter Mergecommit **`e933ea0`**, kein Rebase, Force-Push oder History-Rewrite.
- Lokalisierungs-/Testcommit **`d9efed9`**. Paket und Übergabe separat danach; den aktuellen
  Head und Checkstatus zeigt der PR. Der neue CI-Nachweis wird nach Upload ergänzt.
- 13 Main-Commits gegenüber der zuletzt integrierten Basis `fbfb56c` übernommen. Ausschließlich
  Dokumentation und Staging: Sprachpaketplan, aktuelle Drive-Verweise, Grafikarchiv/Manifest.
- Drei Konflikte: `CODEX_STATUS_CURRENT_DE.md`, `README.md`,
  `CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md`. Beide Seiten erhalten:
  Funktions-/Testergebnisse des PR und neuere Sprach-/Design-/Archiventscheidungen von Main.
  Veraltete CI-/Paketangaben sind als Historie eingeordnet, keine neuen Funktionen entfernt.

Die zehn verbindlich genannten Dokumente, der vollständige neue Auftrag und die ergänzenden
Main-Änderungen wurden gelesen. Die angegebene aktuelle Drive-Übergabe
`12yo2Ukev2haMhVxzz7QEuMSq-PIh900_` ist aus der Cloud beim Abruf mit **HTTP 403** nicht
zugänglich. Deshalb gemäß Auftrag GitHub als Arbeitsgrundlage. Kein behaupteter Abgleich
mit dem Inhalt der Drive-Datei oder mit dortigen Grafik-Binärdaten; kein Blockieren der
übrigen autorisierten Arbeit. Main und alle neueren Drive-Archivverweise bleiben erhalten.

## B. Implementierung

### Sprache und Kodi 21

- **207 neue Kodi-String-IDs `32400–32606`** vollständig in `en_gb/strings.po` und
  `de_de/strings.po`, einschließlich aller sechs Homepunkte, zehn Settingsbereiche,
  Untermenüs, Medien-/EPG-Oberflächen, Suche, Widgets, Reminderstatus und Engine-/Speicherdiagnose.
- `localization.py::tr` verwendet **`xbmcaddon.Addon().getLocalizedString(int)`**. Kodi wählt
  die installierte Nutzersprache. Fehlende/leere Texte, Lookupfehler oder falsche Formatfelder
  fallen **nur für die betroffene Zeichenkette** auf gebündeltes Englisch zurück.
- Englisches PO einmal lokal lesen und pro Interpreter cachen; kein Netz, keine Dateien
  pro Pfeiltaste, keine externen Userdata-Packs importieren. Formatfelder samt Formatangaben
  prüfen, gültige übersetzte Feldreihenfolge zulassen; numerische IDs und alle bestehenden
  Übersetzungen bleiben erhalten. Neue Texte ergänzen die vorhandenen PO-Dateien.
- Metadaten-Basissprache `en_gb`. **Keine** Kodi-Spracheinstellung oder Add-on-Präferenz
  überschreiben. Deutsche Kodi-Bestandsprofile liefern weiter deutsche Texte; bei unbekannter
  Gerätesprache Englisch als Fallback. `lang_priority` bleibt unverändert ein Inhaltsfilter.
  Kein neuer Sprachpaketmanager oder unabhängiger XCMate-Sprachauswahldialog in diesem Auftrag.
- Home-/Settings-/Suchkategorien speichern String-IDs statt zur Importzeit übersetzter Texte.
  Erneutes Öffnen verwendet die aktuelle native Lokalisierung, nicht alte deutsche Konstanten.
- Statische Texte der zwei neuen XML-Fenster sind leer vorbelegt und werden im **echten
  `WindowXML.onInit()`** über Addon-Lokalisierung gesetzt. Keine Annahme, dass ein globales
  `$LOCALIZE` die Add-on-eigenen IDs automatisch auflöst. Kontrolle/Fokus/Action-IDs unverändert.
- Die fünf neuen nativen Settingslabels verwenden numerische PO-IDs. Bereits geöffnete Kodi-
  Einstellungsfenster können Labels cachen: nach Sprachwechsel schließen und neu öffnen,
  bei Bedarf Kodi neu starten. **Kein sofortiger dynamischer Settingswechsel garantiert.**
- UI-Beschriftungen und Now/Next-Plot der **neuen** Widgets lokalisiert; originale Sender-/
  Film-/Sendungstitel und Beschreibungen bleiben Daten des Anbieters und werden nicht übersetzt.
  Reminderzustände bleiben intern `pending/notified/cancelled/missed`, nur Anzeige übersetzt.

Betroffene Runtime-Dateien: `home_menu`, `app_routes`, `media_window`, `guide_window`,
`guide_store`, `guide_timers`, `media_data`, `media_progress`, `recording_probe`, neues
`localization`; beide PO-Dateien, `addon.xml`, neue Settingslabels und beide neuen XML-Fenster.

### Freeze und neu abgesicherte Fehlerfälle

- Live-TV-Overlay, Recovery, Remote-Module und Player weiter bytegleich zur 0.1.26-Basis;
  sieben Kern-Spiel-/Autostartmethoden AST-identisch. **`main.py`, `service.py`, `utils.py`
  in dieser Stabilisierungsrunde nicht geändert.** Keine globale Sprach-/Keymap-/Skinänderung.
- Keine Portal-/Favoriten-/EPG-/Cachemigration, kein Profilreset. Bestehende Settingsattribute
  und beide alten PO-Dateiinhalte mit neuer Freeze-Fixture gegen 0.1.26 geprüft.
- Vorherige Ursache: neue Oberfläche umging Kodi-Lokalisierung mit deutschen Literalen,
  einschließlich XML- und nativen Settingslabels. Neue Stringschicht beseitigt diese Pfade.
- Zusätzliche Regression: Guide-Reaktivierung darf beim Übersetzen statischer Controls
  nicht den ausgewählten Sender-/Datumsheader oder Fokus auf den Initialzustand zurücksetzen.
- Englische Suchzählung mit Singular „1 match“, echte Gesamtzahlen/Paging unverändert.
- Vorhandene Daten-/Medien-/EPG-/Widgetfunktionen, Hintergrundjobs und Cachewiederverwendung
  bleiben erhalten. Grenzen: Zehn-Tage-EPG nur aus echten Daten; Neuheiten zehn Tage/100 Titel
  als einstellbare Vorgabe, ältere/undatierte Auffüllung weiterhin ehrlich gekennzeichnet.

## C. Qualität und Installationspaket

| Prüfung | Ergebnis |
| --- | --- |
| Ausgangssuite vor Änderungen | **313/313 bestanden** |
| Gesamtsuite nach Änderungen | **338/338 bestanden**, vor und nach isoliertem vollständigem Build |
| Neue Sprachregressionen | **25/25 bestanden**; keine bisherigen Schutztests entfernt |
| HTTP-/EPG zusätzlich mit httpx 0.28.1 | **26/26 bestanden** |
| Kodi 21/Omega | Strikte GUI-/Callback-/API-Verträge und bestehende Live-Navigationstests bestanden |
| Syntax | `compileall` aller Add-on-Sourcen in Wegwerfkopie erfolgreich |
| Build | Alle drei Repository-Pakete, Index-MD5, Installerkopien geprüft; nur XCMate-Testpaket übernommen |
| XCMate-Testpaket | **0.1.27 / Dienstbuild 27, 308392 Bytes, 96 Dateien** |
| ZIP-Inhalt | Alle Dateien bytegenau zum Quellbaum, CRC fehlerfrei, beide PO-Sprachen enthalten |
| Produktionsindex | `addons.xml` bleibt **0.1.26**, MD5 und Produktiv-ZIP unverändert |

SHA-256 des **aktuellen lokalen Branch-Testpakets**:

`ab53aeb1f4e4e01473e2f935faabaf4480742ed268d6abc8dea69436bb62b16e`

[Installierbare ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.27.zip)
· [SHA-Sidecar](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.27.zip.sha256).
CI erzeugt ein eigenes Archiv mit anderen ZIP-Zeitstempeln; dessen beigefügte eigene SHA nutzen.
Ein alter grüner 313-Test-Lauf gilt ausdrücklich **nicht** als Prüfung des neuen Sprachcodes.

Neue Tests prüfen reale PO-Dateien und neue Menü-/Fenster-/Widgetrouten: Englisch/Deutsch,
0.1.26-Präfix/Settings-Erhalt, simuliertes deutsches Altprofil, englisches Profil trotz deutschem
IPTV-Filter, einzelner fehlender Text, unbekannte Sprache, leere/defekte Formatübersetzung,
Reihenfolge von Formatfeldern, Native-Lookupfehler, Offline-Fallbackcache, echte Suchzahlen,
Providertext-Erhalt, Reminderzustände und Guide-Reaktivierung. Verwendete native API-Verträge
bleiben die für Kodi-Tag `21.0-Omega` dokumentierten Signaturen. Kein WindowDialog-onInit
künstlich als Erfolg ausgegeben.

## D. Noch notwendige Abnahme und offene Punkte

**Android-TV weiterhin offen:** vollständiger [Geräteplan](ANDROID_TESTPLAN_027_DE.md),
einschließlich deutschem 0.1.26-Upgrade ohne Sprach-/Datenreset, englischen Menüs/Settings,
Fenster-Neuöffnung nach Sprachwechsel, fehlender Übersetzung, dreier BINGIE-Reihen und aller
Live-Freeze-Fälle. Cloudmodelle sind kein Android-Renderer-/Hardware-Nachweis.

Nicht in dieser Runde geliefert: grafische EPG-Zeitmatrix, Auto-Tune, vollständige
Aufnahmeplanung/Android-Aufnahmeengine/Wakeup, vollständige neue M3U-/STB-Medienoberfläche,
portalübergreifende neue Suche, Auto-Next-Countdown, serienweite Resets und Continue-Reihe.

**Grafik-Sprint #27:** einzig freigegebenes Zieldesign bleibt Space Premium. Bestehende
Runtimegrafiken weder ersetzt noch neu generiert; keine vorzeitige Integration der vier
Drive-Grafiken, keine Varianten 2/3. `artwork/xcmate/space-premium/` unverändert aus Main
übernommen (README/Manifest, keine vier Binärdateien). Bekanntes `fanart.png`/`fanart.jpg`-
Manifestproblem bleibt für separaten Grafik-PR dokumentiert, hier bewusst nicht korrigiert.

**Sprachpaketmanager #29:** weiterhin offen. Kein externer PO-/ZIP-Loader, Downloadkatalog,
Installieren/Löschen oder Userdata-Packs. en/de bleiben im Add-on vorinstalliert.

**Rechtekette #19:** offen; bestehende Herkunfts-/Urheber-/GPL-Vermerke vollständig erhalten,
keine eigenmächtige Lizenzentscheidung. Die neue Lokalisierung klärt die offene Rechtsfrage nicht.

## E. Freigabestatus

PR #28 bleibt Draft. Kein Main-Merge, kein Tag, kein GS-Media-Publish und kein Issueabschluss.
Produktivversion und produktive 0.1.26-ZIP bleiben unverändert. Erst ausdrückliche Freigabe
nach Review/Gerätetest erlaubt den dokumentierten regulären Repository-Updateweg.
