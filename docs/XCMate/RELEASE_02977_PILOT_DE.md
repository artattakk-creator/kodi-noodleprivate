# XCMate 0.1.29.77 – GS Media Pilot

Status: **PILOT_RELEASED**, öffentliches ZIP/Katalog/MD5/SHA256 und echte native Kodi-Update-Erkennung am 06.11.2026, ca. 22:49 UTC erfolgreich verifiziert.

Source-PR: [#383](https://github.com/artattakk-creator/kodi-noodleprivate/pull/383), nach zehn erfolgreichen CI-Workflows gemergt. Source-Merge: `2a498044135d27b44b53d6d35d96cba7d59ce98b`. Pilot-Release-PR [#384](https://github.com/artattakk-creator/kodi-noodleprivate/pull/384), Release-Merge `d424a17d507ae6a9e182619be288c726988bc75a`. Geprüfter Source-Head: `a2f8c29f9f1f6c2feb14ed302ba8a585709661e4`.

- XCMate: 0.1.29.77, 739 Dateien, 3.441.153 Bytes.
- SHA256: `8060b83e1b5153cb52cc7449bd4799d8b477517dcea84a6775cd3b63b4840bc8`.
- [Pilot-ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.77.zip) · [SHA256](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.77.zip.sha256).
- [Testbericht](./TESTBERICHT_02977_DE.md), [Ursachenanalyse](./IMPLEMENTIERUNG_02977_DE.md), [Android-Plan](./ANDROID_ABNAHME_02977_DE.md), [native Nachweise/Screenshots](./test-builds/02977/evidence/).

## Installation auf der bestehenden Testbox

1. Den bereits eingerichteten **GS Media Pilot** verwenden; kein neues Repository und keinen GS-Media-Installer ausführen.
2. Kodi → Add-ons → Auf Aktualisierungen prüfen. Anschließend XCMate → Add-on-Information → Versionen/Aktualisieren → **0.1.29.77 aus GS Media Pilot** wählen. Bei mehreren Quellen ausdrücklich Pilot wählen.
3. Nach erfolgreichem Update Versionsnummer .77 und Änderungs-Popup kontrollieren. Bestehendes Profil weiterverwenden; keinen Token erneut importieren.
4. Zuerst P077-01 bis P077-09: lokales EPG ohne Senderstart, echte Serien-/Filmbilder in Hero UND EPG mit Screenshots. Gesicherte Home-Vorschau nur nach Prüfung bestätigen. Normale drei Widgetquellen und ihre Verknüpfungen behalten.
5. Danach zunächst jeweils einen Serien-/Film-/Live-Back testen; nur bei Erfolg zu den je 20 Zyklen übergehen. Bei Freeze/fehlendem ACK FAIL dokumentieren, weitere Zyklen NOT_TESTED lassen.

Regulärer GS-Media-Kanal und NeoDark3 bleiben **0.1.29.76**. GS Media Installer **0.5.26**, bisherige .76-ZIPs und sämtliche anderen Komponenten bleiben unverändert.

**Android .77: ANDROID_NOT_TESTED.** Host-/Linux-/Update-Nachweise sind kein visueller Android-PASS. #380/#366/#367/#368 bleiben offen. .76-Sendungsbilder sind laut Nutzer weiterhin FAIL. Keine vollständige P0-Geräteabnahme behauptet.

## Öffentlicher Veröffentlichungsnachweis

- Tatsächliches Pilot-`addons.xml` liefert .77, zugehöriges MD5 stimmt; öffentliche ZIP-CRC, Manifest-Identität, SHA256-Datei und Pilot-Metadaten stimmen mit dem geprüften Source-ZIP überein.
- Ein echtes isoliertes Kodi 21.2 zeigt nach `UpdateAddonRepos` im nativen `addons://outdated/` die Add-on-ID `plugin.video.xtreammate` und Version **0.1.29.77** an. Installierte Metadaten-Fallversion .76, Installer-Metadaten .5.26 unverändert; kein Installer-/XCMate-Anwendungscode installiert/ausgeführt, keine Geräteprofile eingebunden.
- Öffentlicher regulärer Index samt MD5, Installer-.5.26-ZIP sowie reguläres und Pilot-.76-ZIP sind byteidentisch zum freigegebenen Ausgangs-main `2710431`. NeoDark3-Direktdatei .76 bleibt dadurch erhalten.
- Nachweise: `evidence/public-pilot77.json`, `native-pilot-update77.json`, `published-preservation77.json`, `ci-summary77.json`. Alle zehn Source-CI-Workflows PASS; abschließende Pilot-Bestandsschutzfälle 11/11 PASS.
