# GS Media / XCMate – Vollinstallation auf leerem Kodi über NeoDark3 (48 Pflichtkomponenten + Branding)

> **Bild- und PDF-Dokumentation:** Jeder reale Kodi-Schritt wird parallel im [Screenshot-/Redaktionsprotokoll](HOWTO_BILDDOKUMENTATION_VOLLINSTALLATION_2026-11-09_DE.md) mit `IMG-01` bis `IMG-18`, echter Schrittbestätigung, Bildunterschrift, Fehlerfällen und Datenschutzprüfung erfasst. Das [maschinenlesbare Bildmanifest](HOWTO_GS_MEDIA_BILDMANIFEST_2026-11-09.json) reserviert die späteren Bilddateien; aktuell sind **0 Original-Screenshots aufgenommen und 0 öffentlich freigegeben**. Bitte bei jedem Installationsstand ein gut lesbares Foto des relevanten Kodi-Bildschirms bereitstellen (sensible Daten vorher abdecken). Das PDF folgt erst nach tatsächlicher Gerätedokumentation.

**Stand:** 09.11.2026 · **Gültig für:** Android-Testbox **B**, Kodi **21.3 Omega ARM32**, GS Media **Pilot 1.9.12**, Media Center Installer **0.5.26**, Ziel-XCMate **0.1.29.84**, BINGIE MOD **2.2.3**, Space Blue **0.2.0**. **Box A nicht ändern.**  
**Status:** auf GitHub tatsächlich vorhandene ZIPs, Repository-XML und Installer-Logik geprüft; **48/48 Android-Neuinstallation auf sauberer Box noch nicht vollständig abgenommen**. Die TinyURL wurde in früheren tatsächlichen Kodi-Tests verwendet, deren heutige Redirect-/Browsing-Verfügbarkeit konnte hier **nicht unabhängig bestätigt werden**. Installationen erfolgen über Kodi/Netzwerk, **ohne USB**.

> **Startentscheidung des Nutzers:** **NICHT** den vorher empfohlenen Minimalaufbau vorziehen. Nach Sicherung/resettem Testgerät direkt den **kompletten GS Media Media Center Installer** verwenden und bei erstem reproduzierbaren Fehler stoppen, diagnosieren und die Ursache an ihrem Paket-/Repo-Ursprung korrigieren. **Nicht** auf blindes Wiederholen oder häufige Factory-Resets setzen.

## 0. Vor dem Aufbau: Backup und Basissystem

1. Nur **Box B**, nicht Box A. Nach den Startfehlern vom 09.11. hat der Nutzer den Android-App-Cache bereits geleert und das ganze Gerät neugestartet, ohne Erfolg. Vollständige Neuinstallation ist dadurch gerechtfertigt, **aber nur nach Sicherung**.
2. Vor `Android → Apps → Kodi → Speicher & Cache → Daten/Speicherinhalt löschen`: vertrauliche XCMate-Provider-/TMDB-Token/EPG-Quellen, Senderzuordnungen, Kodi-Favoriten, Skin-Keymaps nach **geprüftem** Netzwerk-Backup oder separat dokumentierter privater Wiederherstellung sichern. Vorheriges `Caber Toss` sichert nur Logs. Ein unbestätigter Kopierdialog ist kein Backup.
3. Keine gesamte Android-Werkseinstellung nötig. Nach Kodi-App-Datenreset: Kodi 21.3 mit **Estuary** einmal starten, Netzwerk/Uhrzeit/Freiplatz kontrollieren. Wenn Kodi selbst jetzt ohne jedes Drittanbieter-Add-on wieder ausgeht, **STOP**: Kodi-APK/Android-Runtime prüfen, nicht 48 Add-ons installieren.
4. Die Neuinstallation enthält in **Phase 48/48** bewusst viele optionale Drittanbieter-Komponenten; sie ist **kein Minimaltest** und kann dieselben Kodi-Python-Importprobleme erneut auslösen. Genau deshalb wird jeder Erstfehler dokumentiert und später durch Installer-Version plus Regressionstest beseitigt.

## 1. Erste Eingabe: Kodi-Netzwerkquelle NeoDark3 einbinden

**TinyURL aus der bisherigen tatsächlichen Nutzer-/Projekt-Konfiguration:**  
`https://tinyurl.com/neodark3`

Kodi-Oberfläche Schritt für Schritt:
1. Kodi-Startseite → **Zahnrad (Einstellungen)**.
2. **Dateimanager** → **Quelle hinzufügen**.
3. Bei **<Keine>** / **<None>** bestätigen und **genau** `https://tinyurl.com/neodark3` eingeben (kein zusätzliches Slash an das TinyURL-Kürzel hängen).
4. Unter „Namen für Medienquelle eingeben“ **`NeoDark3`** festlegen → **OK**.
5. Quelle **NeoDark3** im Dateimanager öffnen: sie soll ein online verfügbares ZIP-Dateiverzeichnis mit `repository.gsmedia.pilot-1.9.12.zip`, `script.gsmedia.setup-0.5.26.zip` anzeigen. Falls Kodi nur Webseite/leer/Fehler zeigt, **nicht weitermachen**: Quelle durch direkten **GitHub-Pages-Verzeichnispfad** ersetzen: `https://artattakk-creator.github.io/kodi-noodleprivate/online-test/` (GitHub-Dateistand bestätigt, Live-HTTP-Directory-Test offen). Wenn auch das nicht browsbar ist, ZIP über eine **geprüfte SMB-Netzwerkfreigabe** bereitstellen, ohne USB. Die TinyURL ist kein ZIP-Einzelfile und gehört **nicht** in das „ZIP-Datei installieren“ Eingabefeld.
6. Für das erstmalige ZIP-Paket: **Einstellungen → System → Add-ons → Unbekannte Quellen** bei Kodi-Aufforderung bewusst aktivieren, nur kontrollierte GS-Media-Pakete verwenden.

**Stopp-Gate SOURCE-01:** Quelle öffnet in Kodi ZIP-Verzeichnis und beide exakten Dateien sind sichtbar. Name und Version fotografieren; anderenfalls nicht mit falscher Datei weitermachen.

## 2. Repository zuerst: GS Media Pilot 1.9.12

1. Kodi-Start → **Add-ons** → oben **Paket-/offenes-Box-Symbol** → **Aus ZIP-Datei installieren**.
2. Quelle **NeoDark3** → **`repository.gsmedia.pilot-1.9.12.zip`** → bestätigen.
3. Auf Kodi-Installationserfolg warten; bei Add-ons → **Aus Repository installieren** muss **`xcMate Repository – Test v1.9.12 – Kodi 21.3 Omega`** bzw. **GS Media Pilot** stehen.
4. Repo-Einstellungen → **„Nach Aktualisierungen suchen“**, falls Index noch keine Add-ons zeigt. Der Pilot ist `repository.gsmedia.pilot`, der normale **GS Media 1.8.1 Lite** ist eine andere ID (`repository.gsmedia`) und für dieses Vollinstallations-Ziel **nicht als erster Pflichtschritt erforderlich**.
5. **SOURCES-02-PASS:** Pilot v1.9.12 aktiv und Katalog enthält Installer `script.gsmedia.setup 0.5.26` und erforderliche Vorlagen/Quellen.

**Nicht manuell als Vorbedingung installieren:** SlyGuy, xVAULT, TMDB-Helper, Skin, Skin Shortcuts, Jurialmunkey, YouTube oder zwanzig verschiedene Repositories. Der Installer soll fehlende Versionen selbst über freigegebene Quellen auflösen und bestehende kompatible Pakete überspringen. Kodi offizielles Repository ist bereits Basis.

## 3. Genau der richtige Installer: 0.5.26

**Bevorzugter Weg (automatische Add-on-Updates aus dem Pilot):**
1. **Add-ons → Aus Repository installieren → xcMate/GS Media Pilot → Programm-Add-ons → XCMate Media Center Installer → Installieren.**
2. In den **Add-on-Informationen** Version **0.5.26** prüfen (`script.gsmedia.setup`).
3. **Add-ons → Programm-Add-ons → XCMate Media Center Installer → Öffnen**.
4. Bei Abhängigkeiten und Erststartbedingungen die Installationsliste, Mindestversionen und angezeigten Quellen kontrollieren. Auf einer wirklich frischen Installation **Neuer Installationslauf**, auf einem unterbrochenen Lauf mit gespeichertem Installationsjournal **Fortsetzen** wählen. **Nicht resetten**, wenn nur ein einzelnes Paket fehlgeschlagen ist.
5. Alternative aus derselben Kodi-Quelle, wenn der Repo-Katalog noch nicht aktualisiert: **Aus ZIP-Datei installieren → NeoDark3 → `script.gsmedia.setup-0.5.26.zip`**. Trotzdem **zuerst Pilot-Repo installieren**. Hierbei nur dieses exakte Paket installieren, keine alte 0.5.21/0.5.22/0.5.25.

Verifizierte Verteilpfade:
- Pilot Repo: `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip`
- NeoDark3 Direkt: `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup-0.5.26.zip`
- Installer .5.26 SHA256 laut veröffentlichtem Releasebericht: `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`.

## 4. Was das 48+Branding-Setup tatsächlich leisten soll

- Installer **0.5.26** enthält **48 alte Pflichtkomponenten** mit Status und Installationsjournal. Er prüft vorhandene Pakete und überspringt bereits geeignete, repariert aber niemals willkürlich Quellen durch unsichere Downloads.
- Unterstützte wichtige Kodi-/Pilot-Abhängigkeiten in aktueller Dokumentation: `repository.titan.bingie.mod >=2.0.1`, `script.bingie.helper >=1.1.2`, `script.skinshortcuts >=2.1.0`, `resource.images.skinicons.wide >=1.0.5`, `script.module.jurialmunkey >=0.2.35`, `script.module.resolveurl >=5.1.212`, SlyGuy-Repo/Helper, xVAULT und weitere vom 48er Plan deklarierte Add-ons.
- **Nach den 48 Schritten:** Der **Space Blue Manager `script.gsmedia.xcmate.branding 0.2.0`** ist eine **zusätzliche verpflichtende Abschlussbedingung**, ausdrücklich **nicht ein 49. normaler nummerierter Paketplan-Schritt**. Verifiziertes aktives **BINGIE MOD 2.2.3**, geprüftes Branding, Sicherungen, Intro/Splash und Farbschema. Daher präziser als „48 Pflichtpakete + Branding“ bezeichnen; die Anzeige kann `48/48` vor Branding zeigen.
- Der Installer soll den Abschluss erst nach vollständiger `branding_patch.status active`-/Color/Assets-Probe melden, `restart_pending` journalisieren und Kodi **beenden**. **Android startet Kodi nicht automatisch neu**: Nutzer startet Kodi anschließend selbst und prüft Space-Blue-Skin, Intro, Senderlogos, Widgetzeilen, EPG, Player und Back.
- **Nicht als 49/49 oder „vollständig Android-PASS“ beschönigen**, bevor wirklich erfolgreich auf dieser Box durchlaufen. Hosttests bestanden; volle Android-Installation bleibt eine neue Abnahme.

## 5. Bei Fehlern: anhalten, Ursache reparieren, fortsetzen

**Prinzip: KEIN zweiter Gesamt-Reset wegen eines Paketfehlers.** Bei `sicher angehalten`, `SOURCE_BLOCKED`, `KODI_CATALOG_VERSION_TOO_OLD`, `ImportError`, `ModuleNotFoundError`, Freeze oder Skin-/Branding-Prüffehler:

1. **Auf dem Fehlerbild bleiben.** Foto der **gesamten Meldung** inkl. Paketnummer `N/48`, exakter Add-on-ID (z. B. `script.module.jurialmunkey`), Fehlercode, Installationsphase und erkennbarem Versionsstand aufnehmen.
2. **Kodi-Log auf Netzwerkfreigabe sichern** (Caber Toss, sofern lauffähig), private Inhalte nicht in öffentliche GitHub-Tickets hochladen. Datum/Uhrzeit notieren. Android-Kill ggf. separat mit logcat, da Kodi-Log den eigentlichen Absturz nicht zwingend enthält.
3. Fehler von uns gegen **tatsächlich vorhandenen Pilot-Katalog** `online-test/addons.xml` und das passende Original-ZIP sowie Installer-Lebenszyklus/Quellenregel prüfen, bevor ein Fix gebaut wird. Fehlende Version, falsches Upgrade-Bridge-Parent, Source-Block, defekte Kodi-Python-Imports, Skinfehlkonfiguration und Volumemangel strikt unterscheiden.
4. **Ein neues gezieltes Installer-Update** (z. B. nächster `0.5.27`-Kandidat, nur wenn erforderlich) mit reproduzierbarem Negativ-/Regressions-Test und originalen ZIP-Hashes bauen; als neuen Pilot-Installationsstand veröffentlichen **nur nach Nutzerfreigabe**. Bestehende .5.26 nicht still überschreiben.
5. Danach aktualisierten Installer über **NeoDark3/Pilot** auf der Box installieren, denselben **Journal-Installationslauf mit `Fortsetzen`** wiederaufnehmen. Die zuvor erfolgreich verifizierten Komponenten bleiben erhalten, keine pauschale Deinstallation.
6. Wenn nach `48/48` Kodi aussteigt, **prüfen, ob es ein geplanter `restart_pending`-Abschluss oder ein echter Crash** ist. Anhand Journaleintrag/Branding-/Skinstatus unterscheiden; nicht jeden automatisch beendeten Kodi-Lauf als Absturz etikettieren.

## 6. Akzeptanz / Messpunkte

| Prüfpunkt | Erwartung | Initial |
|---|---|---|
| INST-01 | `NeoDark3` Kodi-Netzwerkquelle zeigt ZIPs | NOT_TESTED |
| INST-02 | `repository.gsmedia.pilot 1.9.12` aktiv, Index aktualisiert | NOT_TESTED |
| INST-03 | `script.gsmedia.setup 0.5.26` auf frischem Kodi installiert | NOT_TESTED |
| INST-04 | Fortschritt 1/48 bis 48/48; bei Fehler klarer Stop + `Fortsetzen` | NOT_TESTED |
| INST-05 | Original-BINGIE MOD 2.2.3 / alle Mindestabhängigkeiten | NOT_TESTED |
| INST-06 | Extra Space Blue 0.2.0 geprüft aktiv (Assets/Farben) | NOT_TESTED |
| INST-07 | Geplanter Kodi-Quit mit Journal, manueller Neustart stabil | NOT_TESTED |
| INST-08 | XCMate .84 beginnt ohne Python-/SlyGuy-/XVault-Importfehler und ohne EPG-/Diskfull-Loop | NOT_TESTED |
| INST-09 | Senderlogos/Live-Hero/Filme/Serien/EPG/Player/Zurück funktionieren | NOT_TESTED |

**Bei Neustart-/Python-Ausfall erneut:** Eine frische Kodi-Installation beseitigt nicht zwingend einen Add-on-/Runtime-Bug. **Stop** und Ursache pro Paket reproduzieren, ggf. Kodi Standard-Python ohne Add-ons prüfen; nicht 10 zusätzliche Repos unkontrolliert installieren.

## 7. Dokumentation und Quellnachweise

- `docs/XCMate/INSTALLER_0526_MANDATORY_SPACE_BLUE_START_2026-11-06_DE.md`: 48+Branding Vertrag und veröffentlichte .5.26.
- `online-test/addons.xml`, `online-test/index.html`, `online-test/manifest.json`: Pilot 1.9.12, Installer .5.26, Add-on-IDs und ZIP-Pfade tatsächlich auf GitHub verfügbar.
- `docs/XCMate/HOWTO_KODI_213_ANDROID_NEUINSTALLATION_XCMATE_GRUNDVERSION_2026-11-09_DE.md`: Alternativer Minimalweg **nicht** als Standard für diesen 48er Nutzerauftrag.
- `docs/XCMate/CODEX_MASTER_02985_ZWEI_BAUSTELLEN_2026-11-09_DE.md`: Separater .85-Entwicklungsauftrag, nicht bereits veröffentlicht.
- `https://kodi.wiki/view/Add-on_manager`: Kodi-ZIP-/Repo-Installation.
- `https://github.com/artattakk-creator/kodi-noodleprivate/issues/401`: Python-/Speicher-/Recovery-Ticket.

**Aktueller Status:** Dies ist eine **konkret ausführbare Anleitung und Abnahme-Matrix**, kein Beweis für einen live bestandenen 48/48-Android-Wizard. Der Nutzer gibt den nächsten konkreten Bildschirm-/Fehlerstand vor; wenn `NeoDark3`-Quelle in Kodi nicht geöffnet wird, direkt URL/Quellenauflösung prüfen, nicht blind Repo-/Installer-Versionen wechseln.
