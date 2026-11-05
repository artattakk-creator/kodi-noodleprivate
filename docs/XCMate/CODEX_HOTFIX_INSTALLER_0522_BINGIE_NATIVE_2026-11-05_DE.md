# CODEX – P0-Hotfix XCMate Media Center Installer 0.5.22

**Auftrag vom 05.11.2026 | Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Fehler-/Masterissue:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/364  
**Status:** Auftrag dokumentiert, Hotfix **noch nicht implementiert/getestet**.  
**Priorität:** P0 – Kodi 21.3 / Android TV / NeoDark3 / GS Media Pilot.  
**Ausgangsversion:** `script.gsmedia.setup` 0.5.21 (identische Logik wie 0.5.20, lediglich addon.xml-Name/Version angepasst), `script.gsmedia.bingie.bootstrap` 0.1.0, `repository.gsmedia.pilot` 1.9.12.

## 1. Beobachtungen und Evidenz

Beim Start über das **reguläre** GS Media Repository erschien:
```
2 von 48 Komponenten geprüft.
SOURCE_BLOCKED:script.bingie.helper:PILOT_CATALOG_NOT_INSTALLED
Keine Daten gelöscht. Nach Korrektur wiederaufnehmen.
```
Nach separater Einrichtung von NeoDark3/GS Media Pilot folgt nun in Kodi:
```
XCMate Native BINGIE Repository & Helper
Failed to install a dependency
```
Dieser zweite Dialog verrät **nicht**, welche Dependency gescheitert ist. **Unbedingt konkrete fehlgeschlagene Add-on-ID aus `kodi.log` ermitteln**, etwa `CAddonInstallJob[...]: failed to find/install dependency ...`. Nicht allein aufgrund des Screenshots eine einzelne Ursache als bewiesen ausgeben.

Verifiziert aus `online-test/addons.xml`:
- `script.gsmedia.bingie.bootstrap` 0.1.0 verlangt gleichzeitig `repository.titan.bingie.mod` >=2.0.1 und `script.bingie.helper` >=1.1.2.
- `script.bingie.helper` >=1.1.2 verlangt `script.module.simplejson` >=3.17.0.
- `repository.titan.bingie.mod` und `script.bingie.helper` liegen im Pilot-Katalog. `script.module.simplejson` fehlt als Paket im Pilot; **nur** der interne Resolver `script.gsmedia.upgrade.script.module.simplejson` ist enthalten. Das echte Modul liegt im offiziellen Kodi-Omega-Repository: https://mirrors.kodi.tv/addons/omega/script.module.simplejson/.
- `script.bingie.helper-1.1.2.zip` in `online-test/script.bingie.helper/` ist bytegleich mit dem abgeglichenen Upstream-ZIP (Git-Blob `c209ef019b71fc7d89860966cdf1beec082e070f`).
- Die Pilot-`repository.titan.bingie.mod-2.0.1.zip` ist **nicht vollständig bytegleich** mit dem abgeglichenen Upstream: `addon.xml` und `icon.png` sind identisch, `fanart.jpg` unterscheidet sich. Deshalb ausdrücklich **nicht** behaupten, diese gesamte ZIP sei identisch zum unveränderten Original. Upstream/Version/Lizenz und Herkunft bei eventuellem Ersatz überprüfen.
- Kodi-Abhängigkeitsresolver verwendet offizielle Repository-Versionen bzw. die Herkunft des Eltern-Add-ons; bloßes Vorhandensein in irgendeinem fremden Katalog reicht nicht immer. Kodi-Referenz: https://xbmc.github.io/docs.kodi.tv/master/kodi-base/d2/d97/class_a_d_d_o_n_1_1_c_addon_repos.html.

## 2. Ziel und Reihenfolge – kein künstliches gemeinsames Bootstrap-Require

Einrichten/fortsetzen **ohne Neuinstallation** und **ohne Zerstörung des 48-Schritte-Journals**. Bestehender Installername muss exakt `XCMate Media Center Installer` bleiben, ID `script.gsmedia.setup`.

A. **PILOT_PRECHECK**: Pilot-Repo `repository.gsmedia.pilot` ermitteln (installiert/aktiv, Version, Katalog lädt). Wird der Installer aus dem regulären GS Media Repository gestartet, darf er den fehlenden Pilot nicht stillschweigend voraussetzen. Fehlende Pilot-Quelle nur mit klarer Zustimmung aus einer vom Projekt kontrollierten ZIP + festem Hash installieren. Wenn native automatische ZIP-Installation auf Kodi 21 nicht zuverlässig/sicher möglich ist, **kontrolliert anhalten** und eine genaue Benutzeranleitung zur Installation aus NeoDark3 anzeigen. Anschließend Resume, kein Neulauf.

B. **BINGIE_REPO_PRECHECK**: `repository.titan.bingie.mod` >=2.0.1 separat und zuerst aus einer verifizierten zulässigen Quelle installieren; installierte ID und Aktivierung prüfen; Kodi Repository-Index aktualisieren und tatsächliche Einträge prüfen. Keine gleichzeitige Abhängigkeitsinstallation per `script.gsmedia.bingie.bootstrap` 0.1.0.

C. **SIMPLEJSON_PRECHECK**: echtes `script.module.simplejson` >=3.17.0 prüfen, einschließlich Origin, aktiviert/Version. Falls nötig, aus offiziellem Kodi-Repository via nativer Kodi-Funktion installieren. Kein unbelegter Mirror, kein nur „erfolgreich installiert“ markierter Bridge ohne echtes Modul. Bei Kodi-Repo offline/unzugänglich aussagekräftig stoppen und Resume anbieten.

D. **BINGIE_HELPER_INSTALL**: `script.bingie.helper` >=1.1.2 erst danach aus zulässigem Original-/Pilot-Repo installieren und die tatsächliche Installation/Version/aktiviert-Zustand verifizieren. Nur dann die entsprechende Setup-Komponente in Journal als PASS markieren.

E. **RESUME**: vorhandenen sicheren Fortschritt (z. B. 2/48) transaktional weiterschreiben; bereits erfolgreich durchlaufene Komponenten nicht neu installieren, keine inaktive Quelle als installierbar behandeln, kein optimistisches Erledigt-Markieren durch bloßen `InstallAddon`-Aufruf. Fehlgeschlagenen Bootstrap nach erfolgreicher separater Vorbereitung als erfüllt markieren bzw. aus aktivem Plan entfernen, ohne den Gesamtplan zu verkleinern oder Komponenten zu überspringen.

F. **Meldungen**: diagnostiziere pro Stufe `ADDON_ID`, benötigte und gefundene Version, Source/Origin, Blockiergrund und nächsten sicheren Schritt. Benutzerfreundliche Ausgabe, z.B. `BINGIE_HELPER_BLOCKED:script.module.simplejson:NOT_INSTALLED`. Keine Passwörter, private URLs, Logs oder Tokens ausgeben. Behandle Offline/HTTP/Hash-/Permission-/Versionfehler gesondert.

## 3. Quellcode und Paketbau

- Aus `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.21.zip` den tatsächlichen bestehenden Python-Quelltext extrahieren, Änderungen minimal und nachvollziehbar darauf aufbauen. Im Repo liegen derzeit nur ZIP-Pakete, dazu u.a. unterstützende Dateien unter `tools/gsmedia_setup352/`, die **nicht** automatisch vollständig den Paketinhalt repräsentieren.
- Gefährliche automatische Python-Datei-Manipulation ohne Quellverifikation vermeiden. Nur eine neue ZIP-Version veröffentlichen, deren `addon.xml` und Module tatsächlich aktualisiert wurden.
- Ziel: Installer `0.5.22`. Falls nötig `script.gsmedia.bingie.bootstrap` auf `0.1.1` korrigieren, dabei die Doppeldependency **entfernen oder ersetzen**, sodass der Bootstrap nicht erneut den gleichen Kodi-Origin-Fehler triggert. Er darf nicht einfach passiv „grün“ melden, während BINGIE-Repo/Helper fehlen.
- Syntax- und Packaging-Checks: JSON/XML valide, ZIP-Inhalt/CRC, Versionsstring und angezeigter Name, IDs, Abhängigkeiten, Installationsreihenfolge und Reproduzierbarkeit. ZIP-SHA256 als Textdatei.

## 4. Verbindliche Regressionstests

1. Frische Kodi-21.3-Installation: nur **reguläres** GS Media Repository, Pilot fehlt → korrektes Consent/Bootstrap oder klarer sicherer Haltehinweis.
2. Pilot installiert und aktiviert, offizielles Kodi-Repo aktiv, `simplejson` vorhanden → BINGIE Repository vor Helper; PASS.
3. Pilot vorhanden, `simplejson` fehlt → zuerst offiziell installieren; **kein** Helper-Abhängigkeitsfehler.
4. Pilot vorhanden, aber Katalog veraltet, deaktiviert oder HTTP-Timeout → sinnvolle Diagnose, kein blindes Weiterlaufen.
5. BINGIE Repository fehlt oder sein Parent-Origin wird nicht aufgelöst → staged install/refresh, sicherer Stop.
6. Bereits vorhandener BINGIE Helper wird **nicht** überschrieben oder downgraded.
7. Kodi meldet `Failed to install a dependency` → die exakte Add-on-ID und die benötigte Version werden protokolliert.
8. Fehlhash/Internet offline/korrupter ZIP → SOURCE_BLOCKED bleibt erhalten und Daten/Journal bleiben unverändert.
9. Resume bei 2/48, mehrfacher Neustart, Wiederholung, Crash zur Hälfte → keine Doppelinstallation und kein Verlust von Kodi-Profil, BINGIE-Fokus/Widgets, XCMate, Provider, EPG, Favoriten, Tokens.
10. Integrationstest mit realem Android/Kodi 21.3: **ANDROID_NOT_TESTED** bis Nutzer auf Testbox bestätigt. Keine synthetischen Tests als Android-Abnahme ausgeben.

## 5. Ausschließlich Testkanal veröffentlichen

**Fertiges und durch CI geprüftes Ergebnis direkt im Testverzeichnis ablegen:**

- `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.22.zip` (katalogkonformer Paketpfad)
- `online-test/script.gsmedia.setup-0.5.22.zip` (NeoDark3-HTTP-Dateimanager-Direktlink)
- `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.22.zip.sha256` und optional direkte SHA-Datei
- aktualisiertes `online-test/addons.xml` mit **ID `script.gsmedia.setup`, Name `XCMate Media Center Installer`, Version `0.5.22`**; `online-test/addons.xml.md5` neu berechnen
- `online-test/manifest.json` entsprechend aktualisieren (Wizard-Version, Diagnose, Teststatus, ggf. BINGIE-Bridge)
- falls BINGIE Bootstrap `0.1.1` gebaut: neue ZIP unter `online-test/script.gsmedia.bingie.bootstrap/`, zugehörigen Index aktualisieren.
- `online-test/index.html`: für Kodi HTTPDirectory **sichtbarer Linktext exakt gleich relativer href-Dateiname** (z. B. `<a href="script.gsmedia.setup-0.5.22.zip">script.gsmedia.setup-0.5.22.zip</a>`). Zunächst Repo-ZIP, dann Setup-ZIP, keine unnötigen Links.
- NeoDark3: https://artattakk-creator.github.io/kodi-noodleprivate/online-test/ ; der TinyURL-Alias `https://tinyurl.com/neodark3` ist **nicht** als funktionierend verifiziert. GitHub Pages URL und ZIP-Download-Status nach Veröffentlichung prüfen.
- Alle ZIP-/Hash-/Manifest-/Index-Konsistenzen per CI prüfen. **Nicht** das reguläre `addons.xml`, `addons.xml.md5`, reguläre Installer-ZIP oder `src/plugin.video.xtreammate` für diesen Hotfix ändern. Keine Änderungen am Space-Blue-Branding.
- Entwicklungs-PR nach `main` erstellen, dort Tests und SHA nachweisen. Der Nutzer hat die **Veröffentlichung eines Testkandidaten im NeoDark3/Pilot-Verzeichnis** ausdrücklich beauftragt: Nach grüner CI, überprüfter ZIP-/Katalog-Konsistenz und ohne offene P0-Blocker den PR nach `main` mergen und **ausschließlich** die Pilot-Testdaten veröffentlichen; die echte Android-Abnahme bleibt `ANDROID_NOT_TESTED` bis zum Gerätetest. Bei nicht erfülltem Test-/Sicherheitsgate nicht mergen, sondern die Ursache melden. **Niemals** automatisch über das reguläre GS-Media-Repository verteilen.

## 6. Ergebnisbericht an Auftraggeber

Exakte Fehler-ID aus Kodi-Log oder ehrlich `UNVERIFIED_WITHOUT_DEVICE_LOG`; geänderte Quellen; SHA-256 aller gebauten ZIPs; Link auf PR, Test-URL/Dateien; bestandene Host-/Kodi-Tests, fehlende Android-Tests; bestätigte Resume-Position und Verifikation ohne Skin-/Widget-Datenverlust.

**Nicht erledigt melden, bevor Test-ZIPs, Pilot-Katalog, MD5 und NeoDark3-Listing tatsächlich im Zielbranch und nach Merge auf `main` vorliegen.**
