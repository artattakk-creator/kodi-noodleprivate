# XCMate 0.1.29.2 installieren; Theme-Installer 0.1.30 im Review

Stand: 20.10.2026. [Verbindlicher Auftrag](CODEX_AUFTRAG_INSTALLATION_THEME_030_DE.md).

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

## B – Space Premium 1.0.0: Originale fehlen in dieser Laufzeit

**0/98 Originaldateien heruntergeladen oder decodiert.** Mastertracker und alle acht
Kategorieordner sowie Originalordner und direkte Tracker-Downloadwege sind am
Netzwerkproxy mit `Tunnel connection failed: 403 Forbidden` blockiert. Das ist keine
Aussage, dass die Dateien auf Drive fehlen oder die Nutzerfreigabe nicht vorliegt.

[Maschinenlesbarer Zugriffs-/Fehlbestandsbericht](SPACE_PREMIUM_ASSET_PRUEFUNG_030.json)
enthält alle 13 Versuche und 98 **historische Referenzpfade** aus dem Repositoryplan.
Da der aktuelle Mastertracker nicht lesbar ist, sind diese Namen **keine bestätigte
aktuelle Drive-Masterliste**. Die definitive Namens-/Maß-/Hashprüfung ist noch offen.

Zur Fortsetzung benötigt diese Laufzeit eine übergebene ZIP mit **allen 98 unveränderten
Originalen in den acht Kategorieordnern**, den **Mastertracker als exportierte Datei**
und vorhandene JSON-Manifeste/SHA-256-/Herkunfts- und Lizenzhinweise. Bereits vorhandene
Teil-ZIPs können zusammen übergeben werden; keine Neuproduktion oder Konvertierung.

Es gibt daher **kein** `XCMate-Space-Premium-1.0.0.zip`, keine tatsächlichen
Space-Premium-Layoutabbildungen und keinen vorgetäuschten Vollständigkeitsnachweis.
Kein Original wurde verändert, ersetzt oder neu generiert. Der GitHub-Katalog ist
absichtlich leer. Auch die in Tests erzeugten 98 Mini-Bilder sind keine Produktassets.

## C – Separater Installer-Branch, kein Release

Branch `feat/xcmate-space-premium-installer`, vorgeschlagener Core **0.1.30**;
0.1.29.2 und seine veröffentlichte ZIP bleiben bytegleich. Technischer Vertrag,
Limits und Integrationsgrenzen: [THEME_FORMAT_INSTALLER_030_DE.md](THEME_FORMAT_INSTALLER_030_DE.md).
Neue Funktionen: **Einstellungen → Darstellung & Sprache → XCMate-Designs**,
installierte Designs mit Version/Aktivierung, GitHub-Katalog, lokaler ZIP-Import,
Standarddesign und bestätigtes Entfernen. Downloads/Prüfungen laufen in einem
abbrechbaren Worker. Der Wechsel stoppt keine Wiedergabe und wartet gegebenenfalls
auf die nächste nach der Wiedergabe geöffnete Ansicht.

Neue Tests und endgültige Prüfsumme des **Core-Testpakets** stehen im
[Theme-Testbericht](TESTERGEBNISSE_THEME_030.json). Dieses Paket enthält den Installer,
**kein vollständiges Space-Premium-Design**. Den separat vorbereiteten Android-Testplan
für den Installer enthält [ANDROID_TESTPLAN_THEME_030_DE.md](ANDROID_TESTPLAN_THEME_030_DE.md).
Keine eigenmächtigen Merges, Releases oder globalen Skin-/Keymapänderungen.

### Geprüfter Installer-Testkandidat

**496/496 Tests** (34 neue Theme-Regressionen), 66,514 s; ergänzend 40/40
HTTP-/EPG-/Cache-Prüfungen in 1,201 s. Syntax und strikte Kodi-GUI-Argumenttests grün.
Der tatsächliche Kodi-21.3-Dialog-Header wurde erneut vom gepinnten Commit gelesen;
sein SHA-256 stimmt mit der vorhandenen API-Fixture überein.

[Core-Test-ZIP 0.1.30](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.zip)
([SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.zip.sha256)):
**124 Dateien / 389.577 Bytes**, SHA-256
`dca16f1ebb37ac650f426bb167b615f947b20b3e50468577559b9d07e5c27a12`.
ZIP-CRC, Pfade, exakte Dateiliste und jeder Quellbytevergleich bestanden; zweiter
Bau mit dem offiziellen kanonischen Packer erzeugt identische ZIP-Bytes.
Der vollständige Repositorybuilder lief ausschließlich in einer isolierten Kopie;
nur diese XCMate-Test-ZIP und ihre Prüfsumme wurden zurückkopiert. Produktivindex,
veröffentlichte 0.1.29.2 sowie Noodle-/Repository-Add-ons bleiben unverändert.

Der erste Gesamtlauf fand eine echte Startregression: Lesen ohne optionales Theme
erzeugte einen Ordner. Behoben durch read-only Lesen der Auswahl; der unveränderte
Bestandstest zur Profilerhaltung besteht wieder. Zwei Versions-Assertions wurden
auf den neuen Core-Kandidaten umgestellt; ein älteres GUI-Testfixture erhielt den
tatsächlichen Profilpfad-Vertrag und einen expliziten Importpfad. Die Freeze-
Referenzdateien wurden **nicht** angepasst, und kein `WindowDialog.onInit` erfunden.

[Draft-PR #50](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50): Der vorherige Stand bestand zwei CI-Läufe, dessen binäres Paket ist durch den oben genannten Kandidaten ersetzt. Ein zusätzlicher Regressionstest bewies, dass ein kleines PNG zuvor ein stark expandierendes iCCP-Farbprofil einschleusen konnte. Jetzt sind alle PNG-Nebenmetadaten einschließlich begrenzt entpackter iCCP/zTXt/iTXt-Inhalte auf zusammen 1 MiB begrenzt. Der neue Test scheiterte vor der Korrektur und besteht danach; die gesamte Suite ist mit 496 Tests erneut grün. Die aktuelle PR-CI prüft genau diesen Kandidaten nochmals. Keine Originalgrafik wurde verändert.

**Letzter Implementierungsstand bestätigt:** [CI 39469067207](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39469067207) auf `2c9c8a483f8d2789d902ac3218eab7210ce813b9` und [Katalogprüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39469067294) erfolgreich. [Aktuelles CI-Artefakt](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39469067207/artifacts/12285862589) enthält den oben genannten inneren ZIP-SHA-256 im Namen. Upload erfolgreich, **Produktivveröffentlichung SKIPPED**. Die lokale Suite umfasst 496 Tests; der direkte CI-Rohlog-/Binärdownload wurde nach der vorangegangenen Transportablehnung nicht erneut versucht. Es wird kein heruntergeladener CI-Binärnachweis behauptet. Diese abschließende Dokumentation verändert Core, Tests und ZIP nicht.
