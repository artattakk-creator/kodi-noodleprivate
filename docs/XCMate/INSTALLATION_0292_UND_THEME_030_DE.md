# XCMate – veröffentlichte 0.1.29.2 und geprüfter Testkandidat 0.1.30

Stand **21.10.2026**. Bestehender [Draft-PR #50](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50), ausschließlich `feat/xcmate-space-premium-installer`. Kein Merge, Release oder Produktivindex-Update. Frühere Drive-403-/0-von-98-Aussagen sind historisch; alle 98 Originale sind vorhanden.

Maßgeblich: [vollständiger Prüfbericht](PR50_PRUEFBERICHT_030_20261021_DE.md), [Maschinenbericht](TESTERGEBNISSE_THEME_030.json), [Android-Testplan](ANDROID_TESTPLAN_THEME_030_DE.md).

## A – Tatsächlich veröffentlichte Installation

PR [#49](https://github.com/artattakk-creator/kodi-noodleprivate/pull/49) wurde am
20.10.2026 zusammengeführt. Main-Stand der Prüfung:
`116d653efb95df18a4ba750cb33d108fc2e2c276`. Der Veröffentlichungsworkflow
[39454694462](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39454694462)
war erfolgreich. Der frühere Plan gestapelter Merges ist damit **historisch**.
In diesem Auftrag wurde nichts erneut zusammengeführt oder produktiv veröffentlicht.

[Veröffentlichtes Installations-ZIP](https://github.com/artattakk-creator/kodi-noodleprivate/blob/116d653efb95df18a4ba750cb33d108fc2e2c276/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip)
– GitHub **Download raw file** verwenden.

- Version **0.1.29.2**, Add-on-ID `plugin.video.xtreammate`, Service-Build **29**.
- **375.229 Bytes / 120 Dateien**, ZIP-CRC und referenzierte Metadatengrafiken gültig.
- SHA-256: `55b6b74e262b30cca37eaf8d251753e5cfb5fcfe06f3e13bd28d3452f56b73d6`.
- Produktiver `addons.xml` führt ebenfalls 0.1.29.2; dessen MD5 stimmt.
- Keine mitgelieferten Profil-/Accountdateien, Datenbanken, WAL/SHM, Logs oder Bytecode.
- Tatsächliche GitHub-Dateibytes über Contents-API/Base64 heruntergeladen und mit der
  lokalen ZIP und Prüfsummendatei verglichen. Raw-API-Transport lieferte hier einen
  Transformationsfehler; der alternative Base64-Download war vollständig erfolgreich.

Maschinenbericht: [INSTALLATIONSPRUEFUNG_PUBLISHED_0292.json](INSTALLATIONSPRUEFUNG_PUBLISHED_0292.json).
Wiederholbar mit `python -B tools/verify_xcmate_installation.py` auf dem veröffentlichten
Main-Stand. Auf einem späteren Buildindex mit 0.1.30 erwartet das Werkzeug bewusst
weiterhin die explizit gewählte veröffentlichte Version und meldet einen Unterschied.

### Vollständige Sicherung vor dem Update

1. Kodi sauber beenden und prüfen, dass kein Kodi-Prozess mehr läuft. Erst dann
   kopieren. Nicht bei noch schreibendem SQLite einzelne DB-Dateien herausziehen.
2. Das **gesamte** Verzeichnis
   `special://userdata/addon_data/plugin.video.xtreammate/` in einen neuen datierten
   Sicherungsordner kopieren, einschließlich Unterverzeichnissen/versteckter Dateien.
   Der übersetzte Pfad liegt auf Android gewöhnlich unter
   `Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.xtreammate/`;
   Kodi-Profile können einen anderen Profilpfad verwenden. Tatsächlichen Pfad prüfen.
   Android-Dateimanager benötigen gegebenenfalls gesonderten Zugriff auf diesen Ordner.
3. Auch ausgewählte **externe Cache-, Cover- und Metadatenordner** vollständig
   sichern. Welche dazugehören, in XCMate-Einstellungen nachsehen. Diese Ordner
   können außerhalb des Add-on-Profils liegen.
4. Bei jeder SQLite-Datei vorhandene gleichnamige **`-wal` und `-shm`** mitkopieren.
   Nicht löschen und nicht eine alte DB mit einer neuen WAL kombinieren. Kodi bleibt
   während des gesamten Kopiervorgangs beendet. Eine bestehende WAL ist kein Fehler.
5. Portal-/Accountdaten, Gruppen, EPG-Quellen und manuelle Zuordnungen, Favoriten,
   Fortschritt/Folgenstatus, Startsender/-gruppe sowie Fernbedienungsbelegung sind
   im Gesamtprofil enthalten. Zusätzlich vorhandene eigene
   `special://userdata/keymaps/` sichern, ohne eine neue globale Keymap zu aktivieren.
   Benutzerdefinierte Profile/settings/startup-Dateien nicht aus der Kopie auslassen.
6. Dateianzahl/Größen und nach Möglichkeit SHA-256-Listen von Original und Sicherung
   vergleichen. Sicherung geschützt aufbewahren; sie enthält echte Zugangsdaten und
   gehört nicht in öffentliche Issues oder den Theme-Quellordner.

**Keine App-Daten löschen, keine Konten zurücksetzen, keine Deinstallation und kein
globaler Kodi-Reset.** Ein Update unter derselben Add-on-ID erhält das Profil; die
Sicherung ermöglicht die Wiederherstellung bei einem Geräte- oder Kopierfehler.

### Regulärer Updateweg und direkte ZIP-Installation

Nach der Sicherung Kodi starten. Ist das GS-Media-Repository bereits eingerichtet:
**Add-ons → Aktualisierungen suchen → XCMate → Versionen/Aktualisieren → 0.1.29.2**.
Repository-Quelle/Version kontrollieren. Kein zusätzliches konkurrierendes Repository
installieren und keine alte Zwischenversion nacheinander einspielen.

Alternativ die oben geprüfte ZIP unter **Add-ons → Aus ZIP-Datei installieren** über
die bestehende ID installieren. ZIP vorher vollständig herunterladen und SHA-256
vergleichen, dann 0.1.29.2 und Build 29 prüfen. Kodi anschließend neu starten.
Noodle Private und Titan BINGIE MOD bleiben unverändert.

Rollback: Kodi beenden, unveränderte 0.1.28-ZIP über dieselbe ID installieren und bei
Bedarf die **zusammengehörige vollständige Sicherung** einschließlich externer Bilder
und DB/WAL/SHM wiederherstellen. Eine ZIP allein rollt Nutzerdaten nicht zurück.
Neu eingerichtete M3U-/Stalker-Adapterkonten sind in 0.1.28 nicht vollständig nutzbar.

### Android-TV-Abnahme: vollständig offen

Der detaillierte [A–D-Gerätetestplan](ANDROID_TESTPLAN_UNIVERSAL_029_DE.md) gilt weiter;
seine früheren Aussagen zu einem noch ausstehenden Merge/Repositoryupdate sind durch
die obige bestätigte Veröffentlichung ersetzt. Ziel Kodi **21.3 Omega / ARM32**,
zunächst Titan BINGIE MOD, anschließend Estuary. Pro Fall Uhrzeit, Aktion,
Soll/Ist-Ergebnis und datensparsame Diagnosecodes festhalten.

| Schritt | Prüfung | Abnahmekriterium | Status |
|---|---|---|---|
| 1 | Sicherung, Update, Profilvergleich | Accounts, Gruppen, Quellen, Mappings und Fortschritt unverändert | NOT_RUN |
| 2 | Je 10 Kalt-/Warmstarts, Hauptmenü und BINGIE-Widgets | Bedienbar; kein Hänger/automatischer Vollimport | NOT_RUN |
| 3 | Startsender/-gruppe und aktivierte Gruppen | Richtige Auswahl; deaktivierte Gruppen bleiben aus | NOT_RUN |
| 4 | OK, OK erneut/Runter, Links, Links erneut, Hoch/Runter, Back/Menu | Bewährte Ebenen/Fokus; keine doppelten/verlorenen Einzelschritte | NOT_RUN |
| 5 | Jetzt/Danach, schneller EPG, offline nach Neustart | Echte Daten; kein Download in Tasten-Callbacks | NOT_RUN |
| 6 | Senderliste über 99/100/101 und 999/1000 | Kontinuierlich, keine falsche Senderzuordnung | NOT_RUN |
| 7 | Film und echte Serienfolge, Back auch unmittelbar beim Start | Bild/Ton stoppen zuverlässig; Resume bleibt | NOT_RUN |
| 8 | Favoriten, Gesehen/Ungesehen, Weiter ansehen | Sofort korrekt; nach Neustart persistent | NOT_RUN |
| 9 | Mehr als 64 Cover/Fanarts, danach Neustart/offline | Bestehende Bilder bleiben; Budget verdrängt keine gültigen Bilder | NOT_RUN |
| 10 | Universeller Assistent: Auswahl/Weiter/Zurück/Abbruch/Save | Nur gewählte Inhalte; bestehende Konten unverändert | NOT_RUN |
| 11 | Große M3U, USB/SMB, Editor/Overrides/Export/Wiederimport | Lokale Änderungen und Originalquelle erhalten | NOT_RUN |
| 12 | Stalker mit geeigneter legitimer Testquelle | Echte Kategorien/Links/Folgen; Anbietergrenzen ehrlich sichtbar | NOT_RUN |

Ohne reales Ergebnis wird 0.1.29.2 **nicht als am Gerät abgenommen** markiert.
Die frühere sporadische Android-Startursache #38 bleibt unbewiesen.

## B – Jetzt vorbereitete Installationsdateien für den Gerätetest

1. Nach vollständiger Sicherung die [Core-Test-ZIP 0.1.30](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.zip) über **Kodi → Add-ons → Aus ZIP-Datei installieren** unter derselben ID aktualisieren. 125 Dateien, **785.140 Bytes**, SHA-256 `0334e765a71b540a88ac51a6c7bf924ebc3df1f98b9e29f31df9fa068ed58c9f`; [Prüfsummendatei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.zip.sha256). Das permanente freigegebene 512er-Core-Icon ist enthalten. Die 98 optionalen Themebilder sind separat.
2. [Space Premium 1.0.0](../../themes/xcmate/space-premium/XCMate-Space-Premium-1.0.0.zip) vollständig herunterladen: **19.772.084 Bytes**, SHA-256 `8fc7f312a65fa5ecdbe68d3487939a25d685de29717896a0a1113c8d41176ae2`. In **XCMate → Einstellungen → Darstellung & Sprache → XCMate-Designs → lokales ZIP importieren** auswählen; danach installierte Version prüfen und gezielt aktivieren. **Theme-ZIP niemals mit Kodis Add-on-ZIP-Installer öffnen.** USB/SMB-VFS ebenfalls im Gerätetest prüfen.
3. Originale 98/98 und 106 Keys sind geprüft, Theme bytegleich reproduziert und unabhängig aus GitHub-Blob-Bytes bestätigt. Aktuell sind **86 Originalbilder** über echte Verbraucher oder bedingte Fallbacks angebunden, **12 ohne Verbraucher**: siehe [vollständige Matrix](SPACE_PREMIUM_RENDERER_MATRIX_030.json). Das ist keine vollständige visuelle Android-Abnahme und kein Versprechen gleichzeitiger Sichtbarkeit aller Bilder.
4. **Online-Katalog** bleibt an GitHub `main` gebunden. Katalog und Theme-ZIP liefern dort derzeit **HTTP 404**; der Installer erklärt dies. Kein Drive-Fallback und kein vorgetäuschtes Online-Angebot. Erst nach späterer ausdrücklicher Freigabe müssen **beide** realen URLs auf dem Android-Gerät HTTP 200 und die unveränderten Hashes liefern.

**509/509 Gesamttests**, zusätzlich 37/37 fokussierte Diagnose-/Exit-/Renderer-Tests. Beide Builds, Syntax, API-Verträge, ZIP-CRC, Quellbytes und reproduzierbare Pakete bestanden. Aktuelle CI-Nachweise stehen im [Prüfbericht](PR50_PRUEFBERICHT_030_20261021_DE.md), nicht in alten 496-Test-Angaben.

## C – Erhaltung und Rückkehr

Themeimport/-wechsel arbeitet ausschließlich im optionalen `themes_v1`-Bereich und verändert keine Konten, EPG-Quellen, Mappings, Favoriten, Resume oder globalen Keymaps. Bei Video/Audio bleibt ein Designwechsel bis zur nächsten Ansicht nach Wiedergabeende vorgemerkt. Beschädigte/inkompatible Auswahl fällt auf das Core-Design zurück.

Rollback des **0.1.30-Tests**: Kodi beenden; oben geprüfte unveränderte **0.1.29.2** über dieselbe ID installieren. Der alte Core ignoriert `themes_v1`. Für den exakten vorherigen Datenstand die vollständige zusammengehörige Sicherung inklusive externer Caches und DB/WAL/SHM zurückspielen. Keine App-/Kontodaten löschen.

Issue #40 bleibt offen: Der doppelte asynchrone Stop ist automatisiert bewiesen und abgesichert; die Ursache des sporadischen Android-Ladehängers ist unbewiesen. Lokale Diagnose und Android-Gegenprobe sind vorbereitet. #37 und #38 bleiben separate bekannte Probleme. Kein reguläres Repositoryupdate von 0.1.30 vor Benutzerfreigabe und Geräteprüfung.
