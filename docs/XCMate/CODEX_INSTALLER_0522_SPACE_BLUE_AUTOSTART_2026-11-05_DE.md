# XCMate Media Center Installer 0.5.22 – Space Blue automatisch vor dem ersten Neustart

**Datum:** 05.11.2026 · **Projekt:** `artattakk-creator/kodi-noodleprivate` · **Priorität:** P0 für nächste Testinstaller-Version, gekoppelt an den BINGIE-Abhängigkeits-Hotfix #364.

## Verbindlicher Nutzerwunsch (05.11.2026)

Der Nutzer hat den eigenständigen **XCMate BINGIE Space Blue Manager 0.2.0** erfolgreich auf der Android-Testbox installiert und angewendet. Künftig soll der **XCMate Media Center Installer** die gesamte Mediencenter-Neueinrichtung so durchführen, dass **nach dem ersten vollständigen Kodi-Neustart Titan BINGIE MOD unmittelbar im blauen XCMate-Design startet**, mit eigenem Intro, Splash, Logo und durchgängiger Space-Blue-Palette. Kein nachträgliches manuelles Starten des Branding-Managers.

## Bereits veröffentlichte, funktionierende Komponenten

- Add-on-ID `script.gsmedia.xcmate.branding`, Version `0.2.0`, im **GS Media Pilot** `online-test/addons.xml`; **nicht** im regulären Katalog.
- Paket `online-test/script.gsmedia.xcmate.branding/script.gsmedia.xcmate.branding-0.2.0.zip`; SHA-256 `afa32cd38df59e12cf9889f05e2e080f1358ee03a169c7ce6cb211cde2d0fdaa`. Ca. 20.44 MB.
- Quellcode im Repository `script.gsmedia.xcmate.branding/default.py`, `resources/lib/branding_patch.py`, `branding_colors.py`.
- API `branding_patch.status(skin_dir, userdata, color_get)`, `supported(skin_dir)`, `plan(skin_dir, addon_dir, mode)`, `apply(skin_dir, addon_dir, userdata, mode, color_get, color_set)`. Die Restore-Funktion bleibt über den Branding-Manager verfügbar.
- Der Manager `default.py` ist **nur interaktiv**: Nutzeraktion und zusätzliche Ja/Nein-Abfrage vor Anwendung. Im Installer ist für vollautomatischen Ablauf eine **separate einmalige, protokollierte Zustimmung im Setup** erforderlich. `default.py` als blindes `RunAddon` aufrufen reicht nicht: es öffnet nur ein Auswahlmenü.
- Verifiziertes BINGIE MOD `skin.titan.bingie.mod` exakt Version `2.2.3`; unbekannte Builds bleiben gesperrt. User meldete nach seiner manuellen Anwendung: *„Das hat gut funktioniert mit dem Patch.“* Das ist eine erste Benutzerbestätigung, keine vollständige Host-/Crash-/Fresh-Install-Abnahme.

## Verbindliche Ablaufreihenfolge

1. **Vor Setup-Beginn:** Einmalige, in der Einrichtungszustimmung dokumentierte Option `XCMate Space Blue Design + Intro automatisch installieren` anbieten. Für eine frische Einrichtung darf diese standardmäßig aktiviert angezeigt werden, sie ist aber ausdrücklich abwählbar. Die Zustimmung mit Version und Timestamp im **gesicherten Installer-Journal** speichern. Kein heimlicher Skin-Patch bei bloßer Installation/Update des Installers, bei Altprofilen oder ohne diese Zustimmung. Bei nachträglich fortgesetztem 48-Komponentenlauf bleibt die ursprünglich ausgewählte Option unverändert.
2. **P0-Abhängigkeiten aus #364 zuerst reparieren:** Pilot-Katalog verfügbar, `repository.titan.bingie.mod` 2.0.1 installierbar, `script.module.simplejson` >=3.17.0 aus legitimer Originalquelle, BINGIE Helper 1.1.2 installiert. Bei Source-/Dependency-Fehler sicher stoppen. Nicht einfach zu Branding springen.
3. **Original-Skin vollständig installieren:** `skin.titan.bingie.mod` 2.2.3 installieren, dessen regulären vorhandenen XCMate-Skin-Patch/Widget-Profil/Start-Layout vollständig anwenden und prüfen. **Keine Space-Blue-Dateien einsetzen, solange eine spätere Skinpatch-Phase sie überschreiben würde.**
4. **Branding-Paket installieren (vor dem ersten End-Neustart):** `script.gsmedia.xcmate.branding` >=0.2.0 über den nativen Kodi-Add-on-Installer aus **Pilot-Repo** installieren. Paketintegrität (fixierter SHA-256), ID, Version, enabled und lokaler Installationspfad prüfen. Nicht 20 MB Asset nochmals ins Setup-ZIP kopieren, keine Drittquellen, keine privaten Tokens. Bereits installierter Manager ist akzeptiert.
5. **BINGIE aktivieren und Settings initialisieren:** `skin.titan.bingie.mod` als aktiven Skin setzen und Kodi GUI/Skin.String-Einstellungen stabil bereitstellen, damit `xbmc.getInfoLabel('Skin.String(...)')` und `Skin.SetString/Reset` **wirklich den BINGIE-Skin und nicht den vorherigen Skin** treffen. Ist Skin-Activation nur beim End-Neustart realisierbar, einen gesicherten einmaligen Pending-Schritt beim ersten Start **vor** Anzeige der finalen Home-Oberfläche ausführen und danach sauber reloaden; keine optimistische Erfolgsmeldung.
6. **Patch atomar anwenden:** In einer eindeutig kontrollierten Integrationsroutine den bereits installierten `branding_patch`-Code wiederverwenden, **nicht** dessen Dateimanipulation nachimplementieren. Mit den echten Pfaden aus `xbmcaddon.Addon('skin.titan.bingie.mod').getAddonInfo('path')` sowie `xbmcaddon.Addon('script.gsmedia.xcmate.branding').getAddonInfo('path'/'profile')`, umgewandelt via `xbmcvfs.translatePath`, arbeiten. Farb-Getter/-Setter aus `default.py` als bewährten Adapter übernehmen, `branding_colors.safe_skin_value` validieren. Import-Scope sauber kapseln, nicht fremdes `default.py` mit dessen globalem `ADDON` importieren.
   - Intro-Modus aus `Skin.String(splash_screen)` übernehmen; falls `none`, vor Anwendung ausdrücklich und persistent `netflix_default` als Teil der genehmigten Installation setzen oder sicher anhalten; keine Änderung an einer vorhandenen Nutzerauswahl ohne Schutz. Unterstützte Modi sind `netflix_default`, `netflix_alternative`, `netflix_extended`.
   - `status(...)` zuerst prüfen: `not_installed` → `supported` und Vorschau/Preflight → `apply`; `active` mit vollständigen Datei-/Farbtreffern → **idempotent SKIP**; `pending`, `error` oder `active` mit Drift → sicher STOP, Recovery-/Restore-Dialog statt automatischem Überschreiben; `restored` erlaubt neue bestätigte Anwendung nach gesichertem Preflight.
   - Bestehendes Branding-Backup unter `special://profile/addon_data/script.gsmedia.xcmate.branding/backups/` **niemals** löschen/überlagern. Bestehende Provider-, SkinShortcuts-, EPG-, Token- und Widgetdaten erhalten.
7. **Verifikation unmittelbar vor finalem Neustart:** `status` = `active`, `matched == total`, `color_matched == color_total` bei aktivem BINGIE; Intro-/Logo-/Splash-Dateien bestehen SHA-Vergleich; Journal-Gate `SPACE_BLUE_READY` erst danach setzen. Sicherstellen, dass vorherige 48-Stufen-Sicherheitsprüfung weiterhin vollständig PASS ist.
8. **Ein einziger kontrollierter Kodi-End-Neustart:** Kodi startet unmittelbar in **BINGIE MOD mit Space-Blue-Farben, korrektem Intro/Logo/Splash und bestehenden drei XCMate-Widgets**. Nach Neustart im bestehenden `tools/gsmedia_setup352/service.py` bzw. paketiertem Service erneut `status(...)` und BINGIE-aktiver-Skin prüfen; beim Fehlen/Drift `POSTBOOT_SPACE_BLUE_NOT_VERIFIED`, Journal erhalten, keinen falschen `complete`-Status und keinen Endlos-Neustart auslösen.
9. **Rückbau/Opt-out:** Der eigenständige **XCMate BINGIE Space Blue Manager** bleibt sichtbar unter Programm-Add-ons. Seine Funktion `Originalfarben, Logo & Intro wiederherstellen` muss weiterhin funktionieren. Nutzer kann Space Blue auch beim Setup abwählen, dann normales Original-BINGIE belassen.

## Negative Tests / Schutzfälle

- Frischer Installationslauf mit Zustimmung: **Reihenfolge** BINGIE/Abhängigkeiten → Skinpatch/Widgets → Space Blue → Neustart → aktiver blauer Skin mit XCMate-Intro.
- Wiederaufnahme nach Blockade bei 2/48 oder anderen Komponenten ohne Duplikate, auch wenn Branding bereits installiert ist.
- Vorhandene aktive, manuell installierte Space-Blue-0.2.0-Installation: **nicht erneut anwenden**, kein Backup überschreiben.
- Bestehendes Kodi-Profil ohne Skinpatch-Zustimmung: **kein** Branding.
- BINGIE nicht exakt 2.2.3, geänderte XML, fehlerhafte Assets, gesperrte Datei, fehlender Speicher, ZIP-Prüfsummenfehler, fehlendes Intro-Setting: **SAFE_STOP**, keine 48/48-Erfolgsmeldung.
- Kein Internet für 20-MB-Paket: sichere Pause/Resume; **kein** beschädigter halber Patch.
- Crash zwischen Backups und Apply: Patch-eigener `pending`-Status bleibt auswertbar; Recovery oder Restore ohne Datenverlust.
- Skin-Aktivierung verzögert: keine Farbstrings des falschen Skins bearbeiten.
- Doppelte Service-Aufrufe und Reboots: idempotent, kein endloser Neustart.
- Bei vorher abgewählter Option originaler Skin unverändert.
- Nach Nutzer-Restore: kein erneutes automatisches Aufbringen durch Installer-Dienst.
- Regression: 48er Journal, Installationsscreen, Kodi Home/Focus/Widgets, TMDB/xVAULT-Setup, bestehender BINGIE-Skinpatch, EPG und Providerdaten.

## Release / Verteilung

**Ziel:** den **XCMate Media Center Installer 0.5.22** des bestehenden Codex-Auftrags `docs/XCMate/CODEX_HOTFIX_INSTALLER_0522_BINGIE_NATIVE_2026-11-05_DE.md` **mit** dieser Space-Blue-Integration veröffentlichen. Keine losgelöste, inkompatible parallele Installer-Version. Falls Codex bereits 0.5.22 baut: Integration vor Freigabe aufnehmen oder auf 0.5.23 erhöhen, ohne Rückschritt.

- Nur **Pilot-Kanal** bis erfolgreiche Box-B-Abnahme: `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.22.zip`, `online-test/script.gsmedia.setup-0.5.22.zip`, ZIP.sha256, `online-test/addons.xml`, `online-test/addons.xml.md5`, `online-test/manifest.json`.
- Wenn `repository.gsmedia.pilot` Version wegen Publishing-/Katalogkorrektur angehoben werden muss: versionskumulativ, keine Repo-Downgrades; andere Add-ons nicht ändern.
- `online-test/index.html` im von Kodi erkannten HTTPDirectory-Format, Linktext **exakt Dateiname**. Nutzer verwendet NeoDark3. Skin-Branding v0.2.0-Paket selbst **nicht verändern**.
- Reguläres GS-Media-Repository `addons.xml` und XCMate Core v0.1.29.74 nicht für diesen Installer-Hotfix ändern.
- Tests: Host-Unit + ZIP-CRC/Struktur/MD5/SHA + Kodi-21-native Testumgebung; Android-Endabnahme der *neuen automatisierten Kette* erst nach Testgerätprüfung. Ein erfolgreicher **manueller** Patch-Test ist hilfreich, aber **kein** PASS für die neue automatisierte Installer-Reihenfolge.
- PR mit Testlogs und SHA nach `main` mergen, **wenn** alle automatisierten Sicherheitsgates PASS; danach echte ZIP/Katalog-Links prüfen. Bei roten Gates **nicht** als fertig ausgeben.

## Abnahme-Definition

Die Installation endet nach genau einem normalen Neustart auf dem ersten sichtbaren Kodi-Home in **Space Blue** mit dem XCMate-Intro; der Nutzer musste den separaten Manager **nicht** manuell starten. Ohne Zustimmung bleibt Original-Skin. Backup/Restore unverändert; alle bereits installierten Daten intakt. Keine Anzeige „fertig“ vor bestandenem Branding-Postboot-Gate.
