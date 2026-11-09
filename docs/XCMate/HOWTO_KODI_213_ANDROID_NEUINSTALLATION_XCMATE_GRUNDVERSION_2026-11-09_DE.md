> **Nutzerentscheidung 09.11.2026:** Für Box B ist jetzt die **volle 48-Komponenten-Installation plus Branding** gewünscht; dieses Dokument beschreibt nur den alternativen Minimalaufbau. Die verbindliche [NeoDark3-Vollinstallationsanleitung](HOWTO_GS_MEDIA_KODI_213_VOLLINSTALLATION_48_PLUS_BRANDING_NEODARK3_2026-11-09_DE.md) beginnt mit `https://tinyurl.com/neodark3`, Pilot 1.9.12 und Installer 0.5.26.

# How-to: Kodi 21.3 / Android – XCMate von einer leeren Installation aus neu einrichten

**Stand:** 09.11.2026 · **Status:** veröffentlichte Pakete/Kataloge auf GitHub geprüft; die hier beschriebene **Neuinstallation auf einer zurückgesetzten Android-Testbox wurde noch NICHT praktisch vollständig abgenommen**.  
**Zielgerät:** **Box B (Testbox)**, Kodi 21.3 Omega auf ARM32/RK3528; **Box A nicht verändern**.  
**Ziel:** reproduzierbarer, **USB-freier** Aufbau ausschließlich über Kodi/Netzwerk, ohne verdächtige Alt-Konfigurationen. **Zwei Ebenen:** A = **schlankes XCMate-Kernsystem**, B = **optional vollständiger Media Center Installer mit BINGIE MOD/Space Blue**. Nicht beide gleichzeitig unkontrolliert installieren.

> **ACHTUNG: Android „Daten löschen“ ist ein destruktiver Vorgang.** Diese Anleitung stellt keine Nutzer-Konfiguration wieder her und macht nichts auf dem Gerät automatisch. Erst nach geprüftem Backup der gewünschten Daten und nur auf Box B vorgehen. Kodi auf Android entfernt bei vollständiger App-Deinstallation ebenfalls Userdata und Add-ons. Kein Werksreset der gesamten TV-Box notwendig.

## 0. Warum wir neu beginnen / Befund

Kodi-Logs vom 09.11.2026, 18:17–18:20: wiederholte XCMate-Startabbrüche `START_FAILED ModuleNotFoundError`, SlyGuy `No module named xml.dom`, YouTube `No module named importlib.resources.readers`, Skin Helper `cannot import name expat from xml.parsers`; Kodi `MyVideos131.db` fehlt u. a. `movie_view`/`tvshow_view`. Zuvor anhaltende `DISK_FULL`-/`RESERVE_BLOCKED`-Ereignisse bei XCMate-EPG/Bildablage. Weder voller Android-Prozessabsturzmechanismus noch exakte Python-Import-Root-Cause sind aus den kurzen Logs bewiesen. Android-App-Cache bereits geleert und Gerät neu gestartet, **ohne Abhilfe**. Ein kontrollierter Testbox-Reset ist deshalb vertretbar, keine Zusage, dass damit ein Programmfehler beseitigt wird.

## 1. Bestand sichern – Pflicht vor Datenlöschung

1. **Box identifizieren:** Hier nur Testbox **B**, *nicht* ältere/eingerichtete **Box A**. Vorhandenen Kodi-21.3-Installationsstand, lokale Versionen und den Verlauf der Neustarts notieren. Screenshots/Fotos des Setup-Assistenten sind sinnvoll.
2. **Kodi-Profil sichern** auf eine getestete **Netzwerkfreigabe (SMB)**, ohne USB. Android-Kodi-Profil in diesen Logs: `/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/`, in Kodi als `special://home/`; Einstellungen unter `special://profile/` bzw. `userdata/`. Relevante Daten: `userdata/addon_data/plugin.video.xtreammate/` (Account-/Gruppen-/EPG-/TMDB-Konfiguration), `userdata/favourites.xml`, `userdata/keymaps/`, `userdata/sources.xml`, `userdata/addon_data/skin.titan.bingie.mod/`, plus eigene Einstellungen/EPG-Quellenlisten. Dateien können Zugangsdaten enthalten: **nur privat übertragen, nicht in GitHub hochladen, nicht als Chattext senden.**
3. Für ein **vollständiges Notfallbackup** nach Möglichkeit offizielles Kodi-Programm-Add-on `Backup` (Kodi.tv-Repository) auf eine **erreichbare SMB-Freigabe** nutzen: https://kodi.wiki/view/Add-on:Backup . Alternativ Kodi-Dateimanager `special://home/` ↔ SMB, aber nur, wenn auf genau diesem Gerät die **Kopie plus tatsächliches Readback** erfolgreich ist. Ein erfolgloser Kopieren-Dialog ist **kein Backup**.
4. Der bereits verwendete **Caber Toss 1.0.2 kopiert nur Diagnose-Logs**, kein vollständiges Kodi-Profil. Wenn Backup wegen der Kodi-Startfehler nicht funktioniert: vor dem Reset zumindest wichtige private Zugänge und Zuordnungen außerhalb von Kodi sicher rekonstruieren und entscheiden, ob der unwiederbringliche Verlust der Restdaten akzeptabel ist. Unbekannte Providerpasswörter oder TMDB-Tokens **nicht** „aus dem Gedächtnis“ vorgeben.
5. Backup **prüfen**: Zielordner ist vorhanden, Größen plausibel, mindestens eine gesicherte Konfigurationsdatei öffnet sich. Einen sicheren Wiederherstellungspunkt auf dem PC behalten. Backup nicht automatisch vollständig in die neue Installation zurückspielen: siehe §8.

## 2. Testbox B zurücksetzen – erst nach geprüfter Sicherung

1. Android-TV-Oberfläche öffnen → **Einstellungen → Apps → Kodi → Beenden erzwingen**.
2. **Speicher & Cache → Speicherinhalt/Daten löschen** (**nur jetzt**, nach Backup). Das löscht die Kodi-Anwendungsdaten samt Add-ons und Nutzerprofil; die Android-TV-Einstellungen und andere Apps werden nicht zurückgesetzt.
3. **Kodi selbst muss nicht deinstalliert werden**, solange die offizielle Kodi-21.3-APK zuverlässig startet. Wenn schon die leere Installation reproduzierbar Python-/GUI-Probleme zeigt, erst die APK/Architektur/Android-Runtime prüfen, gegebenenfalls offizielle Kodi-21.3-ARM32-APK frisch installieren. Keine Kodi-22-Vorabversion als direkte „Lösung“ über die kaputte Installation legen.
4. **Richtigen freien Speicher prüfen**: Im vorherigen Log hatte das ausgewählte FUSE-Volume ca. 27 MB frei bei ca. 81 MB XCMate-Sicherheitsreserve. Nach Reset sowohl Android-Freiwert als auch die von Kodi/XCMate gemeldeten **tatsächlichen Datenvolume-Werte** erfassen. Wenn der ausgewählte Volume weiter unter Reserve liegt, **stoppen** und Speicher-/Mount-Ursache untersuchen, statt unsichere Cache-Limits zu deaktivieren.
5. Beim ersten Kodi-Start nur **Estuary** aktiv, Sprache bei Bedarf Deutsch, korrekte Uhrzeit/Zeitzone, WLAN/LAN; angefragte Android-Speicherberechtigungen nur soweit für Dateien nötig. **Noch kein Skin, kein Installer, kein Portal, kein SlyGuy, YouTube, xVAULT oder TMDB-Helper installieren.**
6. **Baseline-Prüfung:** Kodi dreimal vollständig beenden/öffnen (inklusive einem echten Android-Geräteneustart, falls möglich), Home/Settings/Add-on-Manager aufrufen. Fehlerfreie Navigation und keine wiederholten Python-Standardbibliothek-Importfehler erwarten. Wenn Estuary-Basissystem bereits aussteigt, **nicht** mit weiteren Add-ons fortfahren; Kodi-/Android-App-/logcat-Probleme separat untersuchen. Kleine abgespeicherte Notiz: **BASE-01–03 PASS/FAIL**.

## 3. Online-Paketquellen (verifizierte Repository-Dateien, keine USB-Installation)

**GitHub-Repository:** https://github.com/artattakk-creator/kodi-noodleprivate

| Zweck | Kodi-Add-on-ID / Version | Datei über HTTPS |
| --- | --- | --- |
| GS Media **Lite**, schlankes Haupt-Repo | `repository.gsmedia 1.8.1` | https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/repository.gsmedia-1.8.1.zip |
| GS Media **Pilot**, nur für erweiterten Installer | `repository.gsmedia.pilot 1.9.12` | https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/repository.gsmedia.pilot-1.9.12.zip |
| XCMate über reguläres Repo | `plugin.video.xtreammate 0.1.29.84` | https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.84.zip |
| Vollinstaller (optional **erst in Phase B**) | `script.gsmedia.setup 0.5.26` | https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup-0.5.26.zip |

**Kodi-Online-Quelle** (im Projekt so vorgesehen):
- Test-/Pilot-Ordner: `https://artattakk-creator.github.io/kodi-noodleprivate/online-test/`; Kürzel `NeoDark3`. Dort sind nach GitHub-Dateistand die **genannten ZIP-Dateien** verlinkt. **Einschränkung:** Die externe Erreichbarkeit bzw. Kodi-HTTP-Ordnerauflistung dieser GitHub-Pages-URL konnte bei Erstellung der Anleitung **nicht unabhängig erfolgreich geprüft** werden.
- Regulärer Ordner: `https://artattakk-creator.github.io/kodi-noodleprivate/` (Dateistand auf GitHub vorhanden; gleicher Prüfvorbehalt).
- **Nur wenn die Quellen in Kodi tatsächlich aufgelistet werden:** `Einstellungen → Dateimanager → Quelle hinzufügen → HTTPS-Ordneradresse eintragen → Namen vergeben (GS-Media / NeoDark3)`. Dann im Add-on-Browser **„Aus ZIP-Datei installieren“** und die Repo-ZIP aus dieser Quelle auswählen.
- **Robuster alternativer Netzwerkweg ohne USB:** Die **oben genannten exakten ZIP-URLs** am PC herunterladen, anhand Versions-ID prüfen und in eine von Kodi lesbare **SMB-Freigabe** legen. In Kodi `Einstellungen → Dateimanager → Quelle hinzufügen → Netzwerkfreigabe (SMB)`; dort dieselbe ZIP über **„Aus ZIP-Datei installieren“** auswählen. Kodi kann nicht aus einem bloßen Raw-GitHub-Link im URL-Textfeld des ZIP-Dialogs „installieren“; es benötigt eine tatsächlich navigierbare Datei/Quelle.
- Bei Bedarf: `Einstellungen → System → Add-ons → Unbekannte Quellen` nur für bewusst selbst ausgewählte vertrauenswürdige Pakete einschalten; Quelle, Version und mögliche Berechtigungen prüfen. Keine unnötigen fremden Repos.

**Wichtig:** *Regulär*, *Pilot* und *NeoDark3* sind **keine drei getrennten GitHub-Repositories**: regulär und Pilot sind zwei Kodi-Kataloge im selben Repo, NeoDark3 ein Direktzugang. `repository.gsmedia 1.8.1` ist eine **Lite-Freigabeliste**; es ist absichtlich **kein automatischer 48-Paket-Vollkatalog**. Das erklärt, weshalb der Vollinstaller zum Teil Pilot-Abhängigkeiten benötigt.

## 4. Phase A – minimaler XCMate-Kernaufbau (empfohlen als erster Funktionstest)

1. Nach erfolgreichem Estuary-Basistest **nur `repository.gsmedia-1.8.1.zip`** installieren. In Kodi: **Add-ons → Paket-Symbol → Aus ZIP-Datei installieren**, Quelle auswählen, Repo-ZIP installieren.
2. **Aus Repository installieren → GS Media Repository → Video-Add-ons → XCMate → Installieren** (Menübezeichnungen können je nach Sprache leicht abweichen). Kodi installiert die deklarierten Abhängigkeiten; `plugin.video.xtreammate` benötigt `xbmc.python >=3.0.0`, `script.module.pil >=5.1.0`; `requests` ist in der Add-on-XML optional. **SlyGuy Common, YouTube, xVAULT und TMDB-Helper sind keine Pflichtabhängigkeiten von XCMate.**
3. Die installierte Version **0.1.29.84** im Kodi-Add-on-Informationsdialog überprüfen. Automatische Updates für XCMate während der laufenden Fehlerdiagnose bewusst prüfen/ggf. auf Benachrichtigung statt automatischer Installation setzen.
4. XCMate **zunächst ohne Live-Provider** öffnen und schließen; Kodi ganz beenden und wieder starten, sicherstellen, dass `XCMate service started`/Setup ohne `START_FAILED` läuft. Der eigenständige Erststart-Wizard wird bei fehlendem Portal ggf. angezeigt; nicht „fertig“ behaupten, solange kein Provider hinterlegt ist.
5. **Kleinen, kontrollierten Portaltest** durchführen: ein bewusst autorisiertes Xtream-/M3U-/Stalker-Konto konfigurieren, Verbindung testen, zuerst **nur eine kleine Live-TV-Sendergruppe** auswählen und eine EPG-Quelle (Provider oder externe) aktivieren, nach Verfügbarkeit scannen. **Nicht sofort 15.000 Inhalte oder alle EPG-Länder** laden. Startgruppe/Sender zuweisen, speichern, Kodi neu starten und Senderliste, Jetzt/Danach, Stream-Start, Zurück und EPG prüfen. Zugangsdaten niemals in Logs/GitHub veröffentlichen.
6. **Abnahmepunkt A:** 3 Kodi-Neustarts, XCMate startet, Portalverbindung/kleiner Import und einfacher Live-Test funktionieren, Speicherreserve wird eingehalten. Bei Neustart-/Importfehlern hier **stoppen**, Kodi-Logs per Caber Toss sichern (privat), den Fehler nicht durch Installieren weiterer Add-ons verdecken.

## 5. Phase B – BINGIE MOD + Space Blue (optional / erst nach stabilem Phase-A-Ergebnis)

**Nur auf Box B und nach separatem Backup/Snapshot des eben funktionierenden Estuary+XCMate-Zustands.**

Option **B1 – minimaler Skin-Test (weniger Drittprogramme)**:
1. **GS Media Pilot 1.9.12** zusätzlich installieren, falls für BINGIE-/Skin-Abhängigkeiten benötigt; dabei ausdrücklich die korrekte Pilot-Repo-ZIP verwenden. Im Kodi-Katalog enthält Pilot u.a. original `repository.titan.bingie.mod 2.0.1`, `script.bingie.helper 1.1.2`, `script.skinshortcuts 2.1.0`, `script.module.jurialmunkey 0.2.35` und weitere Bridges.
2. Im Kodi-Add-on-Browser `Aus Repository installieren` das **Titan BINGIE MOD 2.2.3**-Skinpaket und von Kodi gemeldete notwendige Abhängigkeiten auswählen. Nicht gleichzeitig 48 weitere optionale Komponenten installieren. **Estuary** erst bei sichtbarem vollständig gestarteten BINGIE verlassen; beim Skin-Aktivierungsdialog bewusst bestätigen.
3. Drei Kodi-Neustarts mit BINGIE testen; Senderlogos/Widgets/Hero noch nicht als garantiert korrekt darstellen, bevor echte Box-Screenshots vorliegen.
4. Branding **Space Blue 0.2.0** wird normalerweise durch den vollständigen Installer verwaltet; bei manuellem Skin-Pfad **nicht unkontrolliert Shell-/XML-Dateien überschreiben**. Branding entweder über geprüftes separates Patch-Management nach sicherem Backup/Freigabe oder über B2.

Option **B2 – komplettes GS Media Media Center (experimenteller 48er Installer)**:
1. **Vorher `repository.gsmedia.pilot 1.9.12` installiert und aktiviert.** Die dokumentierten Kodi-Abhängigkeitsbrücken können ohne den Pilot-Katalog stoppen.
2. `script.gsmedia.setup 0.5.26` aus regulärem oder Pilot-Katalog (`Programm-Add-ons`) bzw. geprüfter NeoDark3-ZIP installieren; Bezeichnung **„XCMate Media Center Installer“**.
3. Installer **nur nach erneuter Zustimmung** starten und tatsächliche Paketliste prüfen; ursprünglich **48 Pflichtkomponenten** inkl. diverser externer Add-ons/Quellen, dann Branding-Manager 0.2.0 und Kodi-Beenden. Er ist **nicht geeignet als minimaler erster Clean-Boot-Test**, da vorher zuletzt SlyGuy/YouTube/Skin-Helper-Importfehler auftraten. Falls sich eine minimale Auswahl nicht anbietet, nicht als schlanken Installer bezeichnen.
4. Bei `SOURCE_BLOCKED`, `KODI_CATALOG_VERSION_TOO_OLD`, unerwartetem Paketursprung, Python- oder Speicherfehler **sofort sicher stoppen, Logs sichern**. Fehlerhafte Abhängigkeiten nicht mit unkontrollierten Repos/Versionen umgehen. Bereits vorhandene passende Add-ons sollten übersprungen werden. Abschluss **nicht** als bestätigt behandeln, solange nicht alle Pflichtschritte und Skin-Patch-Status tatsächlich erfolgreich gemeldet sind.
5. Dokumentierter Abschluss: Installer prüft aktiven BINGIE 2.2.3 + Space Blue Manager 0.2.0 (`branding_patch.status active` mit abgeglichenen Assets/Farben), markiert `restart_pending` und beendet Kodi; **Kodi muss auf Android anschließend manuell gestartet werden**. Branding/Navigation/Widgetpositionen/Video-Intro danach separat testen.
6. **Bekannte Grenze:** Installer .5.26 GitHub-/Host-CI PASS, **voller 48/48-Kaltgeräte-Neuaufbau nicht als Android-PASS bestätigt**. Wenn SlyGuy importfehler erneut auftritt, Installationsstufe/Paket-ID notieren, nicht mit weiterem „Reparaturpaketstapeln“ antworten.

**B1 und B2 sind alternative Pfade, kein Zwang, beide hintereinander auszuführen.** Für die Fehlerisolation zunächst B1 erwägen, die B2-Vollinstallation bewusst getrennt testen.

## 6. Abnahmeprotokoll – vor jeder weiteren Stufe stoppen können

| Test | Pflicht / Ergebnis |
| --- | --- |
| CLEAN-01: frisches Kodi 21.3 / Estuary | dreimaliger Start/Exit ohne Crash, Python-Import-Servicefehler und DiskFull |
| CLEAN-02: Speicher, gewählter Mount und Reserve | genauer `statvfs`-Pfad/Free/Reserve notiert; genug freier Speicher |
| CLEAN-03: GS Media Lite 1.8.1 | Kodi erkennt Quelle, Repo aktiv; nur deklarierte Pakete |
| CLEAN-04: XCMate 0.1.29.84 ohne andere Dritt-Add-ons | Starts/Widgets/Service stabil, kein `START_FAILED` |
| CLEAN-05: kleiner Portal-/EPG-Test | erster Sender, Jetzt/Danach, Exit/Back, neue Konfiguration hält Neustart |
| CLEAN-06: optional BINGIE 2.2.3 | nach Skin-Aktivierung drei stabile Starts, Fokus/Logo/EPG |
| CLEAN-07: optional Vollinstaller 0.5.26 | nur tatsächlich erreichte Schritte und Skin-Branding-Endstatus als PASS markieren |
| CLEAN-08: Kodi Python + Video-DB | keine `xml.dom`/`xml.parsers.expat`/`importlib.resources.readers`-Importfehler; fehlende `movie_view`/`tvshow_view` read-only prüfen, *nicht* manuell SQLite anlegen |
| CLEAN-09: Bild-/EPG-Lasttest | nur nach stabilem Aufbau; Ghosts/Modern Family/Serien, begrenzte 5 sichtbare Bilder/Cache; #401/#406 bleiben offen |

**Dokumentiere für jeden Schritt:** Datum, Box B, Kodi-/Skin-/Repo-/Installer-/XCMate-Version, PASS/FAIL/NOT_TESTED, exakte erste Fehlermeldung, Zeitpunkt und anonymisierte Logzeile. *Stop on first failure*, kein vollständiger Katalog-Import und keine Auto-Restore-Routine, bis Startbasis stabil ist. Bei Android-Aussteigen ohne Kodi-Trace zusätzlich `logcat` / Android-Absturzbericht für tatsächlichen Prozess-Tod ermitteln (keine Notwendigkeit, Gerätezutaten öffentlich zu machen).

## 7. Umgang mit Backups und Updates

- **Nur gezielt Einstellungen** (Zugänge, favorisierter Sender, manuell konfigurierte EPG-/Skin-/Keymap-Einstellungen) aus gesichertem Backup übernehmen und nach jedem Import erneut testen; niemals das gesamte alte `userdata`-/`addons`-/`addon_data`-Archiv auf einmal zurückkopieren.
- Insbesondere `MyVideos131.db`, `Textures13.db`, alte Add-on-Module/`__pycache__`, `Database` und Bildcaches **nicht** in den neuen Zustand zurückkopieren. Sie bleiben im gesicherten Archiv als forensischer Bestand unverändert.
- Wenn ein Fehler **vor Installation irgendeines Dritt-Add-ons** wiederkehrt, das als **Kodi-/Android-/APK-Baselinefehler** an #401 berichten; tritt er **erst nach Pilot oder Vollinstaller** auf, Zeitpunkt und Paketstufe eindeutig dokumentieren.
- Kodi-Auto-Updates und Add-on-Quellen bewusst einstellen; die veröffentlichte .84 bleibt so lange aktiv, bis eine separat getestete .85 ausdrücklich freigegeben wird. Beim Neuaufbau **Box A niemals automatisch konfigurieren oder als Datenquelle überschreiben**.

## 8. Quellnachweise und Grenzen

GitHub-Projektquellen:
- `src/repository.gsmedia/addon.xml`: reguläres **Lite 1.8.1** mit eigener Freigabeliste;
- `src/plugin.video.xtreammate/addon.xml`: .84 Pflichtabhängigkeiten `script.module.pil`/Python, `requests` optional;
- `online-test/addons.xml` und `online-test/manifest.json`: Pilot **1.9.12**, Wizard **0.5.26**, verifizierte ZIP-Pfade;
- `docs/XCMate/INSTALLER_0526_MANDATORY_SPACE_BLUE_START_2026-11-06_DE.md`: 48er Plan/Branding/restart-pending, **ANDROID_NOT_TESTED**;
- `docs/XCMate/CODEX_MASTER_02985_ZWEI_BAUSTELLEN_2026-11-09_DE.md`: zukünftige .85-Reparatur, keine veröffentlichte .85.
Offizielle Kodi-Dokumentation:
- Android-Installation und App-Deinstallation: https://kodi.wiki/view/HOW-TO:Install_Kodi_for_Android
- Kodi-Datenpfade: https://kodi.wiki/view/Kodi_data_folder
- Add-on-Installation aus ZIP/Netzwerk: https://kodi.wiki/view/Add-on_manager
- Backup-Add-on: https://kodi.wiki/view/Add-on:Backup

**Aktuelle Verifikation:** Existenz und Versionen in GitHub auf `main` geprüft; **keine tatsächliche neue Kodi-/Android-Installation durchgeführt**. Keine Gewähr, dass ein externes Kodi-HTTP-Directory auto-indexiert wird, jede Third-Party-Abhängigkeit auf diesem Gerät funktioniert oder das Löschen der App-Daten allein Python-/Firmware-Probleme behebt. Diese Dinge sind Gegenstand der dokumentierten Box-B-Tests.
