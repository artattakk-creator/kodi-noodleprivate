# GS Media Setup Wizard 0.5.28 · QA und Geräteabnahme

Stand 19. November 2026. Die Hotfix-Identität `gsmedia-setup-0528-catalog-496` basiert auf dem vollständigen 48-Pakete-Installer aus Draft #491 (`8f8569294f29a50ba99a23e2de58ecae846bcfed`). Die Variante für den optionalen TMDB-Cloudimport aus #428 bleibt zurückgestellt und benötigt für eine spätere Auslieferung eine eigene Versionsnummer. [Issue #496](https://github.com/artattakk-creator/kodi-noodleprivate/issues/496) · [Draft #491](https://github.com/artattakk-creator/kodi-noodleprivate/pull/491) · [Draft #428](https://github.com/artattakk-creator/kodi-noodleprivate/pull/428)

## Fehler bei 3/48

`Addons.GetAddons` liest pro JSON-RPC-Aufruf den aktuellen Katalog und begrenzt `start` und `end` auf das verfügbare halboffene Intervall. Bei einem leeren Ausschnitt kann `addons` fehlen. Der Regressionstest reproduziert den alten Stopp mit einer ersten Seite von 200 aus 201 Einträgen. Nach einem Repository-Update hat der nächste Aufruf nur noch 199 Einträge und meldet `[199,199)`. 0.5.27 verwirft die gültige Kodi-Antwort sofort, weil `start` von der Anfrage abweicht. `UpdateAddonRepos` stößt Hintergrundjobs an. Die Repository-Datenbank kann alte Zeilen entfernen, bevor sie Ersatzzeilen schreibt. Auch ein unveränderter Repository-Checksum beweist deshalb keinen stabilen Katalog. [Kodi 22 RC2 `HandleLimits`](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/json-rpc/JSONUtils.h#L67-L79) · [JSON-RPC-Ausgabe](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/json-rpc/AddonsOperations.cpp#L123-L127) · [Update-Aufruf](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/builtins/AddonBuiltins.cpp#L373-L380) · [Repository-Cache](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/addons/AddonDatabase.cpp#L785-L849)

Ein zweiter reproduzierbarer Fehlstopp entsteht durch gültige, für den Installationsplan fremde Kodi-IDs mit Zeichen wie `@` oder `!`. 0.5.28 zählt solche Zeilen bei der Pagination mit und hält die engere ID-Validierung für Installationsziele bei. Welche konkrete Antwort den gemeldeten LG-Stopp ausgelöst hat, bleibt offen. Die Gerätelogs enthalten den auslösenden JSON-RPC-Rückgabewert nicht. [Kodi 22 RC2 Add-on-Validierung](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/addons/addoninfo/AddonInfoBuilder.cpp#L35)

## Verhalten des Hotfixes

- Auf webOS läuft die Aktualisierung außerhalb des Scans. Änderungen der Gesamtzahl, Überschneidungen zwischen Seiten und eine geänderte SQLite-Revision verwerfen alle bisher gelesenen Seiten. Der Scan startet bei null, höchstens dreimal mit je bis zu zwölf Seiten und einer abbrechbaren Pause von 0,5 Sekunden. Ein ungültiges Schema oder widersprüchliche Metadaten stoppen sofort. Fehlende Seitenmarker sind nur zulässig, wenn die erste Antwort den vollständigen Katalog abdeckt.
- Identische Duplikate auf derselben Seite benötigen eine eindeutige freigegebene Quelle und übereinstimmende Paketpfad-, Status- und Abhängigkeitsdaten im aktiven Kodi-Cache. Vor dem nativen Installationsaufruf prüft der Wizard den ausgewählten Pfad und die Abhängigkeitskette innerhalb derselben beobachteten Katalogrevision erneut. Die vorhandenen API-/ABI-, `broken`-, Pillow-, BINGIE- und Skin-Shortcuts-Prüfungen gelten weiter. Kodi kann seinen Katalog zwischen dem letzten Preflight und seiner eigenen Paketauflösung erneut aktualisieren. [Kodi 22 RC2 `InstallAddon`](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/builtins/AddonBuiltins.cpp#L53-L60) · [Native Paketauflösung](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/addons/AddonInstaller.cpp#L328-L371)
- Ein Diagnoseeintrag enthält Versuch, Seite, angefragte und gelieferte Grenzen, Eintragszahl, Schematypen, Duplikat-Kontext und Subcode. Bei einem Scan-Stopp zeigt der Wizard den Subcode, eine Debug-ID und den Hinweis zum Fortsetzen. Vollständige Payloads, Paketpfade, Anmeldedaten und Token fehlen in den neuen Diagnoseeinträgen.
- Der vollständige Installationsplan, die einmalige Wizard-Zustimmung zum Start bzw. Fortsetzen und Kodis eigene Paket- und Skin-Dialoge gelten auf beiden Plattformen weiter. Beim bestätigten Fortsetzen übernimmt `.28` das geprüfte `.27`-Journal atomar nach `auto-setup-0528.json` und gleicht es mit den tatsächlich installierten, aktiven Add-ons ab. Die alte Journaldatei bleibt bytegleich. Beide Versionen teilen dieselbe Ausführungssperre. Der Fortschritt zählt bestätigte Installationen. XCMate `.99` behält Vorrang vor älteren Paketversionen. Backup, Rollback, bestehende XCMate- und Skin-Einstellungen, EPG, Bildquellen und TMDB-Token folgen den Schutzregeln aus #491. Für die freiwillige Nachkonfiguration gelten weiterhin die vorhandenen Benutzerentscheidungen.

## Automatisierte Prüfung und Kompatibilität

| Prüfung | Ergebnis |
| --- | --- |
| 0.5.28-Katalog, Installationsfluss, Paket und 0.5.27-Regression | 43 Tests bestanden. Abgedeckt sind Einzel-/Mehrseitenlisten, leere Antwort, geänderte Anzahl/Revision, fehlende oder falsche Marker, Grenzvolumen, Duplikate, Quellenkonflikte, falsche IDs, anhaltende Fehler und Abbruch während des Wiederholens. |
| XCMate-, Profil- und Skin-Regression | Zusammen 148 Tests bestanden. Enthalten sind die Installer-Tests und die fokussierten Prüfungen zu BINGIE, Branding, TMDB-Token und EPG-Speicher. |
| Unveränderte 0.5.26-Basis | Alle 103 Host-Vertragsprüfungen bestanden. Der erneute Basis-Build ergab SHA256 `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`. |
| Kodi 21 Omega / Android | Simulierter Start, Abbruch und Fortsetzung von drei tatsächlich vorhandenen Paketen bis 48/48 in der vorgesehenen Reihenfolge bestanden. Ein Wizard-Fortsetzungsdialog, vorhandenes XCMate `.99` erhalten. Physische Android-TV-Box ausstehend. |
| Kodi 22.0-RC2 Piers (`21.90.902`) / LG webOS 11.2.0 ARM 32-bit | Kodi-RC2-Quellvergleich und Host-Reproduktion bestanden. Simuliert von 3/48 bis 48/48 mit Katalogprüfung, bestätigtem Paketstand und XCMate `.99`. Physischer Lauf und Bilddarstellung ausstehend. |
| Installationsdatei | Zwei Builds bytegleich. CRC und SHA256 geprüft, Version `0.5.28`, 134.735 Bytes, 41 ZIP-Einträge, davon 34 bytegleich mit 0.5.27. |
| Regulär, Pilot und NeoDark3 | Lokale Auslieferungsprobe bestanden. Alle drei Routen verwenden dasselbe ZIP und dieselbe SHA256-Datei. Beide Kataloge melden `0.5.28` und stimmen mit ihrer jeweiligen MD5-Datei überein. |

Das Host-Ergebnis misst Wizard-Verhalten und simulierte Kodi-Rückmeldungen. Paketauflösung aus dem Gerätenetz, native Binärmodule, echte Dialoge, Rendering und Neustartpersistenz sind Teil der Geräteabnahme. Auf Piers kann das offizielle Skin Shortcuts 3.0.5 mit der für BINGIE geprüften 2.x-Linie konkurrieren. Auf einem neuen LG-Profil ist die native Auflösung der Pilot-Version 2.1.0 zu prüfen. Ungeeignete Kandidaten müssen weiterhin blockieren. [Piers Skin Shortcuts](https://github.com/xbmc/repo-scripts/blob/piers/script.skinshortcuts/addon.xml) · [QA der Basis 0.5.27](GS_MEDIA_SETUP_0527_QA_DE.md)

## Geräteabnahme vor Freigabe

1. Auf dem LG-Gerät genaue Kodi- und webOS-Version, ARM32, Pilot 1.9.12, vorhandenen Skin, XCMate `.99` und freien Speicher erfassen. Private Profilsicherung anlegen. Ausgangszustand von Anbieter-EPG, TMDB-Datei, Bildquellen, Favoriten, Logos, manuellen Zuordnungen sowie Mini- und Groß-EPG festhalten. Geheimnisse und Provider-Daten nur lokal prüfen.
2. Geprüftes ZIP über **Add-ons → Aus ZIP-Datei installieren** einspielen. Im gesicherten 0.5.27-Abbruchprofil den angezeigten Stand 3/48 mit der Kodi-Add-on-Liste vergleichen und einmal im Wizard fortsetzen. Die drei bestätigten Komponenten sollen keine neue Paketinstallation auslösen. Einen vollständigen 48/48-Lauf mit nativer Paketauflösung nachweisen. Auf einem gesonderten Testprofil den frischen Start prüfen.
3. In einem Testprofil während der Repository-Aktualisierung abbrechen und erneut fortsetzen. Bei einem Stopp die Komponente, Debug-ID und die zugehörigen strukturierten Katalogeinträge sichern. Keine vollständigen JSON-RPC-Payloads weitergeben. Den zuletzt bestätigten Paketstand mit der Kodi-Inventarliste abgleichen. Einen anhaltend unsicheren Katalog, eine abgelehnte native Paketbestätigung und eine Konfigurationssperre mit geprüftem Rollback separat testen.
4. Native Paketquellen, BINGIE 2.2.3, Skin Shortcuts 2.1.0 und die benötigten Binärmodule prüfen. Im nativen Skin-Dialog **Ja** wählen. Kodi vollständig beenden und zweimal neu über die webOS-Startseite starten. BINGIE-Home, Live-TV, XCMate-Film-/Serien-Widgets, Logos sowie sichtbare Bilder im Mini- und Groß-EPG auf dem Fernseher prüfen. Einstellungen, Favoriten, EPG-Bestand, manuelle Zuordnungen, Bildquellen und Token nach beiden Starts mit dem Ausgangszustand abgleichen.
5. Auf einer separaten Profilkopie im nativen Skin-Dialog **Nein** wählen und den vorherigen Skin nach zwei Kaltstarts bestätigen. In der freiwilligen TMDB-/Bild-EPG-Nachkonfiguration **Beibehalten** und **Später** mit dem bestehenden Profil prüfen. Speicheroptionen und einen beabsichtigten Token-Ersatz nur an Testdaten prüfen.
6. Die 48er-Reihenfolge, Start und Fortsetzen, die optionalen Nachinstallationsschritte, den finalen Skin-Entscheid und zwei Kaltstarts auf einer Kodi-21-Android-TV-Box wiederholen. Pro Gerät die bestätigten Pakete, Sichtprüfung, Persistenz und eventuell verbleibende Blocker protokollieren.

## Reproduzierbares Paket und Auslieferungsprobe

```sh
scratch=$(mktemp -d)
python3 tools/build_gsmedia_setup_0528_catalog.py \
  --out "$scratch/zip" --release-plan-out "$scratch/channels"
(cd "$scratch/zip" && sha256sum -c script.gsmedia.setup-0.5.28.zip.sha256)
cmp "$scratch/zip/script.gsmedia.setup-0.5.28.zip" \
  docs/GS-Media/test-builds/0528/script.gsmedia.setup-0.5.28.zip
python -m pytest -q tests/test_gsmedia_setup_052{7,8_*}.py \
  tests/test_xcmate_{bingie_branding,branding,tmdb_token_02961,storage_02992,shared_storage_02983}.py
```

SHA256 des Test-ZIP `bbe7e87e384b1336d94cd79eae7332384d9a079d340769c1217c87d7d799133e`. [ZIP](test-builds/0528/script.gsmedia.setup-0.5.28.zip) · [SHA256-Datei](test-builds/0528/script.gsmedia.setup-0.5.28.zip.sha256) · [Geprüfter Auslieferungsplan](test-builds/0528/release-plan.json)

| Kanal | Katalog / MD5 | Installationsroute |
| --- | --- | --- |
| Reguläres GS Media Repository | `addons.xml` / `addons.xml.md5` | `script.gsmedia.setup/script.gsmedia.setup-0.5.28.zip`, verlinkt aus `index.html` |
| GS Media Pilot | `online-test/addons.xml` / `online-test/addons.xml.md5` | `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.28.zip`, mit aktualisiertem `online-test/manifest.json` |
| NeoDark3 | Pilot-Katalog / Pilot-MD5 | `online-test/script.gsmedia.setup-0.5.28.zip`, verlinkt aus `online-test/index.html` |

Der Builder erzeugt die Kanaldateien in einem separaten Verzeichnis. Er prüft die erwartete 0.5.26-Ausgangsbasis und verweigert eine Kollision mit einem anderen 0.5.28-ZIP oder Änderungen an den erwarteten Ausgangskatalogen. Nach Geräteabnahme und Freigabe die Auslieferungsprobe gegen die dann gültigen Kataloge wiederholen und alle drei Downloadwege erneut prüfen. Live-Kataloge, Release und Merge bleiben bis dahin ausstehend.

## Dateiumfang gegenüber Draft #491

- `tools/build_gsmedia_setup_0528_catalog.py`
- `tools/gsmedia_setup0528/overlays/addon.xml`
- `tools/gsmedia_setup0528/overlays/default.py`
- `tools/gsmedia_setup0528/overlays/service.py`
- `tools/gsmedia_setup0528/overlays/resources/lib/setup_auto_store50.py`
- `tools/gsmedia_setup0528/overlays/resources/lib/setup_auto_ui50.py`
- `tools/gsmedia_setup0528/overlays/resources/lib/setup_compat27.py`
- `tools/gsmedia_setup0528/overlays/resources/lib/setup_source27.py`
- `tests/test_gsmedia_setup_0528_catalog.py`
- `tests/test_gsmedia_setup_0528_flow.py`
- `tests/test_gsmedia_setup_0528_package.py`
- `docs/GS-Media/GS_MEDIA_SETUP_0528_QA_DE.md`
- `docs/GS-Media/test-builds/0528/release-plan.json`
- `docs/GS-Media/test-builds/0528/script.gsmedia.setup-0.5.28.zip`
- `docs/GS-Media/test-builds/0528/script.gsmedia.setup-0.5.28.zip.sha256`
