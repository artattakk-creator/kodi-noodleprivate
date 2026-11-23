# GS Media Setup 0.5.27 · Testbericht und LG-webOS-Testplan

**Stand:** Entwicklungskandidat zu Issue #490. Basis ist `main` bei `4a81c1569d56c1497ae29f5d568d1195787b52ec` und das byteidentische 0.5.26-ZIP aus diesem Stand. Geräteabnahme, Merge und Release stehen aus.

## Verifizierte Ergebnisse

| Prüfung | Ergebnis |
| --- | --- |
| Build und Regression von 0.5.26 | 103 Host-Vertragsprüfungen bestanden. Reproduzierter SHA256 `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`. |
| 0.5.27 und fokussierte Regression | 92 Tests und 33 Subtests bestanden. Enthalten sind 15 neue Pakettests, BINGIE-/Branding-, TMDB- und Speicherregressionen. |
| Paketdurchlauf auf simuliertem Omega/Android und Piers/webOS | Je 48/48 bestätigte Pakete mit der vollständigen 0.5.26-Reihenfolge. Genau eine Wizard-Startbestätigung, native Paketanfragen, fehlender Readback mit Stopp, explizites Fortsetzen ohne erneuten Download bestätigter Pakete. Höher versioniertes XCMate bleibt installiert. |
| BINGIE 2.2.3, Skin Shortcuts 2.1.0 und Space Blue | Aus dem tatsächlichen Upstream-BINGIE-ZIP stimmen alle vier SHA256-Originale. Im lokalen Test wurden alle vier Patches und die Layoutdateien zurückgelesen. Mit dem echten Space-Blue-Manager 0.2.0 sind neun Dateiänderungen und 176 Farbwerte geprüft. |
| Piers-API und Quellen | Kodi-Quellbaum meldet `xbmc.gui` 5.18.0 mit ABI 5.17.0 und `xbmc.python` 3.1.1 mit ABI 3.0.0. Host-Tests prüfen einen inkompatiblen Core-Import, Piers-Katalog mit konkurrierender Quelle, Altversion mit Upgrade-Metadaten und Skin Shortcuts 3.x. |
| Journal, Sicherung, Rollback | Synthetisches Profil mit SQLite-WAL und privater Token-Datei gesichert und separat lesbar wiederhergestellt. Konfigurationsrollback erhält eine zweite verifizierte Kopie zwischenzeitlicher Änderungen. |
| Skin-Entscheidung und Kaltstart | Native Ja-/Nein-Zustände, fehlgeschlagener Wechsel und erneute Nachprüfung eines noch startenden Kodi wurden simuliert. |
| TMDB und EPG | Standardwahl „Beibehalten“, abgelehnter und bestätigter Ersatz mit privatem Readback, URL-Allowlist, Redirect-Ablehnung, Größen-/Formatgrenzen und 401/403 simuliert. Freiwillige Einrichtung delegiert Bildfreigaben und Storage an vorhandene XCMate-Oberflächen. Der Agent erscheint mit Status „noch nicht verfügbar“. |

Der Host-Test beweist Paketlogik, Datei- und Datenbankoperationen. Er enthält keine Messung von Kodi-GUI-Rendering, echter native Paketauflösung, DRM, Geräteberechtigungen oder Live-EPG. Der Stand der Downloads aus den Netzwerken der Zielgeräte und ein produktiver GS-Media-TMDB-Endpunkt sind offen.

Die Quellenbelege zur Skin-ABI, zum nativen Paketdialog und zur SQLite-Katalogprüfung liegen in den Piers-Dateien `addons/xbmc.gui/addon.xml`, `addons/xbmc.python/addon.xml`, `xbmc/interfaces/builtins/AddonBuiltins.cpp` und `xbmc/addons/AddonDatabase.cpp`. [Kodi Piers Referenzstand](https://github.com/xbmc/xbmc/tree/60b9c6b0f7fe7bbb932f7140b4662627f94d7400)

## Konkrete Blocker und Voraussetzungen

- **Skin Shortcuts auf neuem LG-System.** Der offizielle Piers-Quellzweig führt Version **3.0.5**. Das fest gebundene BINGIE-Layout nutzt Skin Shortcuts 2.x. Sobald Kodi 3.x als geeignete Dependency auswählt, stoppt der Installer vor der betreffenden Paketanfrage mit `BLOCKED_INCOMPATIBLE_DEPENDENCY`. Eine bereits aktive, geeignete 2.x-Installation wird wiederverwendet. Ob Kodi am Zielgerät die geprüfte Pilot-Version 2.1.0 nativ auflösen kann, bleibt zu prüfen. Der veröffentlichte Gerätekatalog konnte in der Cloud nicht abgefragt werden. [Piers Skin Shortcuts 3.0.5](https://github.com/xbmc/repo-scripts/blob/piers/script.skinshortcuts/addon.xml)
- **Piers-Paket- und Laufzeitnachweise.** Das Gerät muss den erwarteten aktiven Repository-Katalog bereitstellen. Der Installer prüft den lokalen Piers-Katalog schema 33 im Lesemodus, Paketquellen, erforderliche APIs und das native Pillow-Modul vor den Konfigurationsänderungen. Ein unbekanntes Schema, fremde konkurrierende Quellen, fehlende Binärabhängigkeiten und schreibgeschützte Pfade führen zum Stopp. xVAULT, SlyGuy und die optionalen InputStream-Binaries sind am Gerät zu prüfen.
- **Speicher und bestehendes XCMate.** Der verfügbare lokale Platz muss für die tatsächliche Profilsicherung, SQLite-WAL und die größte atomar zu schreibende Datei reichen. Die Sicherung kann bei großen aktiven Profilen entsprechend wachsen. Speicher, der von XCMate auf einem externen Datenträger verwaltet wird, bleibt am vorhandenen Ort.
- **Native Dialoge.** Kodi kann beim InstallAdd-on-Aufruf selbst eine Bestätigung für ein Paket verlangen. Der Wizard bestätigt diese Dialoge nie automatisch. Ist BINGIE bereits aktiv, öffnet der Wizard den nativen Estuary-Wechsel mit Hinweis „Ja = Estuary, Nein = BINGIE“. Bei einem neuen BINGIE-Wechsel gilt im Kodi-Dialog „Ja = BINGIE, Nein = bisheriger Skin“. Beim Ablauf des Countdowns gilt Kodis Rückkehr zum vorherigen Skin.
- **EPG Agent und TMDB.** Der Agent hat weiterhin keinen freigegebenen Produktionsendpunkt. Das Backend bleibt `PARTIAL_COVERAGE / TMDB_LIVE_PENDING / AUDIT_INCOMPLETE`. Der optionale HTTPS-Import benötigt eine ausdrücklich eingerichtete geschützte Datei auf `gs-media.eu` und persönliche Zugangsdaten. [#449](https://github.com/artattakk-creator/kodi-noodleprivate/issues/449) · [#485](https://github.com/artattakk-creator/kodi-noodleprivate/issues/485) · [Draft #486](https://github.com/artattakk-creator/kodi-noodleprivate/pull/486) · [EPG-Agent Draft #7](https://github.com/artattakk-creator/xcmate-epg/pull/7)

## Geräteprüfung nach ausdrücklicher Freigabe

1. Prüfsumme am Rechner mittels `sha256sum -c script.gsmedia.setup-0.5.27.zip.sha256` bestätigen. Auf dem LG-Gerät Kodi 22 Piers, verfügbaren Speicher, aktiven Skin und freigegebenes Pilot-Repository prüfen. Vorher eine private Geräte-Sicherung anlegen. Den bestehenden Stand von XCMate, TMDB, Provider-EPG, sichtbaren Bildern im Mini-/Groß-EPG, Logos und Favoriten erfassen. Token und Provider-IDs aus dem Protokoll auslassen.
2. ZIP auf eine vom Gerät lesbare Ablage übertragen, in Kodi über **Add-ons → Aus ZIP-Datei installieren** auswählen und GS Media Setup öffnen. Kodis Sicherheits- und Berechtigungsdialoge wie angezeigt behandeln. Start einmal bestätigen. Fortschritt und jedes festgestellte Abhängigkeitshindernis dokumentieren. Bei einem Stopp die Komponente und Kodi-Ursache erfassen, korrigieren und dann fortsetzen.
3. Eine Fehlerprobe im isolierten Testprofil ausführen, etwa eine Kodi-Paketbestätigung ablehnen oder eine erwartete Quelle zeitweise unerreichbar machen. Anzahl der bestätigten Pakete notieren und nach Wiederherstellung fortsetzen. Einen config-seitigen Stopp mit unveränderter Originaldatei verifizieren und den angebotenen Rollback testen. Kodi-eigene Prompt- und Speicherberechtigungen separat erfassen.
4. Bei einem erfolgreichen Lauf **BINGIE behalten** und Kodi über den Wizard beenden. Auf LG Kodi über die webOS-Startseite erneut öffnen. Die Startseite in 720p/1080p mit der Fernbedienung prüfen. XCMate-Hero, Live-TV-Widget, Senderlogos, Film- und Serienreihen müssen sichtbar sein. Mini- und Groß-EPG müssen weiterhin die zuvor erfassten Bilder zeigen. Eine manuelle Zuordnung prüfen. Nochmals kalt starten und Skin, Widget-Zustand, Player-Präferenzen, Favoriten und EPG vergleichen.
5. Auf einem separaten Testprofil den nativen Abschluss mit **Nein** ausführen. Nach zwei Kaltstarts den vorherigen Skin und dessen Einstellungen prüfen. Der BINGIE-Entwicklungskandidat bleibt installiert. Auf einem bereits aktiven BINGIE-Testprofil auch den nativen Estuary-Fallback prüfen.
6. In der freiwilligen Einrichtung vorhandenen TMDB-Token beibehalten sowie lokalen Import mit Test-Token und ausdrücklich erlaubten Ersatz erproben. Für Bild-EPG Quelle und Speichermodus intern, dynamisch, USB und später prüfen. Für USB am Gerät Zielprüfung, verfügbaren Platz und Rendernachweis im XCMate-Werkzeug verwenden. Anbieter-/Text-EPG muss bei jeder Wahl verfügbar bleiben. Der Agent bleibt inaktiv.
7. Die Matrix auf Kodi 21.3 Omega/Android wiederholen. Die Android-Anleitung führt über den Android-Startbildschirm. Die LG-Abnahme erfordert einen erfolgreichen echten 48er-Lauf inklusive BINGIE und den Sichtnachweisen in Schritt 4.

## Paket lokal bauen und Profilsicherung prüfen

```sh
python tools/build_gsmedia_setup_0527.py --out /pfad/zum/pruefordner
python -m unittest discover -s tests -p test_gsmedia_setup_0527.py
```

Die Sicherung befindet sich im Kodi-Profil des Installers unter `addon_data/script.gsmedia.setup/backup-0527-*`. Die lokale Datei `setup-0527-finish.json` verweist auf den Sicherungsordner. Die Sicherung kann private Daten enthalten. Den Ordner nur lokal aufbewahren. Der Wizard kann die verwalteten Skin-, Widget- und Player-Dateien mit geprüftem Readback zurückspielen. Vorher im Zweifelsfall Kodi auf Estuary stellen.

Für eine XCMate-Profilwiederherstellung Kodi vollständig beenden und das geprüfte ZIP mit SHA256-Datei auf dem Rechner bereithalten. Der Wiederherstellungsbefehl erzeugt eine **neue private Kopie** und prüft jede Datei. Profile und aktive Datenbanken auf dem Gerät bleiben bis zur gezielten Offline-Übernahme erhalten.

```sh
python tools/restore_gsmedia_setup_0527.py \
  --installer /pfad/script.gsmedia.setup-0.5.27.zip \
  --setup-profile /pfad/script.gsmedia.setup \
  --backup backup-0527-KENNUNG \
  --out /pfad/xcmate-wiederhergestellt
```
