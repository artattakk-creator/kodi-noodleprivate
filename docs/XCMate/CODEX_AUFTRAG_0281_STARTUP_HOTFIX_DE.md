# CODEX-ENTWICKLUNGSAUFTRAG
## XCMate 0.1.28 – Kritischer Startfehler / Android-TV-Hotfix

**Datum:** 20.10.2026  
**Projekt:** GS Media – XCMate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Produktive Version:** `0.1.28`  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Fehlerticket:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/38  
**Priorität:** P0 – Hauptmenü nicht erreichbar

---

## 1. Auftrag und Zielsetzung

Untersuche und behebe den kritischen Startfehler von XCMate 0.1.28.

Nach dem regulären Repository-Update von 0.1.27 auf 0.1.28 bleibt das Add-on beim Öffnen dauerhaft im Kodi-Ladekreis hängen. Das XCMate-Hauptmenü erscheint nicht.

**Primäres Ziel:** Das Hauptmenü muss unabhängig von laufenden EPG-Aktualisierungen, Katalogimporten, Widget-Abfragen und Netzwerkverzögerungen zuverlässig und zügig starten.

Erstelle einen minimalinvasiven, nachvollziehbaren Hotfix, ohne produktive Benutzerdaten zu verändern oder bisher funktionierende Live-TV-Funktionen zu beschädigen.

**WICHTIG: Noch keinen Merge, kein Release und keine automatische Veröffentlichung durchführen.**

---

## 2. Reproduzierter Fehler auf dem Android-TV-Gerät

**Testumgebung:**

- Kodi 21.3 Omega
- Android-TV-Box mit RK3528, ARM 32-bit
- Android TV
- XCMate 0.1.28
- Titan BINGIE MOD sowie alternativ Estuary

**Durchgeführte Tests:**

1. Erster XCMate-Start: Ladekreis läuft dauerhaft.
2. Zweiter Start: Nach 90 Sekunden weiterhin kein Hauptmenü.
3. Kodi-Neustart: BINGIE-Widgets laden dauerhaft.
4. Skinwechsel zu Estuary: XCMate startet ebenfalls nicht.
5. XCMate-Einstellungsdialog über Add-on-Informationen: Öffnet innerhalb weniger Sekunden.
6. Erneuter Start mit Kodi-Debuglogging: Nach 30 Sekunden weiterhin Ladekreis.
7. Zurück-Taste: Ermöglicht schließlich Rückkehr ins Kodi-Menü.

**Schlussfolgerung:**

Der Fehler liegt nicht ausschließlich am Titan-BINGIE-MOD-Skin oder dessen Widgets. Die Add-on-Einstellungen lassen sich separat laden. Der eigentliche Python-Plugin-Start bleibt dagegen blockiert.

Die genaue Ursache wurde noch nicht nachgewiesen.

---

## 3. Ergebnisse der Kodi-Protokollanalyse

Es wurden `kodi.old.log` und `kodi.log` vom 20.10.2026 ausgewertet.

### Älteres Protokoll

Relevante Ereignisse:

- 08:52:15 – Ein XCMate-`service.py`-Prozess kann beim Update nicht innerhalb von fünf Sekunden beendet werden.
- 08:52:39 – Kodi erkennt XCMate 0.1.28.
- 08:52:42 – XCMate-Hintergrunddienst startet.
- 08:52:43 – Hintergrund-EPG-Aktualisierung wird geplant.
- 09:24:18 – Kodi startet `default.py`.
- 09:27:11 – Der Add-on-Aufruf wird abgebrochen, ohne dass das Hauptmenü erfolgreich geladen wurde.

Relevante Originalmeldungen:

```text
CPythonInvoker(36, .../plugin.video.xtreammate/default.py): start processing

CScriptRunner: cancelling add-on script XCMate (id = 36)

GetDirectory - Error getting plugin://plugin.video.xtreammate/

CGUIMediaWindow::GetDirectory(plugin://plugin.video.xtreammate/) failed
```

Weitere Startversuche verursachen vergleichbare Verzeichnisfehler.

### Aktuelles Protokoll

- 11:04:33 – XCMate 0.1.28 ist installiert.
- 11:04:39 – Hintergrunddienst wird gestartet.
- 11:04:59 – Dienst bestätigt seinen Start.
- 11:05:04 – Hintergrund-EPG-Aktualisierung wird angestoßen.
- Bis zum Log-Export ist kein erneuter Hauptmenü-Aufruf nachgewiesen.

**Wichtig:** Die Protokolle zeigen keinen eindeutigen Python-Traceback und keinen expliziten SQLite-Lock-Fehler.

Ein blockierender Python-Aufruf ist nachgewiesen. Seine genaue Ursache ist bislang offen.

---

## 4. Konkrete Verdachtsstellen im aktuellen Code

### 4.1 `default.py`

Pfad:

`src/plugin.video.xtreammate/default.py`

Aktueller Ablauf:

```python
from main import Router
Router(sys.argv).dispatch()
```

Prüfe, ob bereits der Import von `main` oder die Router-Initialisierung blockiert.

Der bestehende Exception-Handler erfasst reguläre Exceptions, jedoch keine endlosen Wartevorgänge.

**Erforderlicher Hotfix:**

- Diagnosemarker unmittelbar beim Eintritt in `run()`.
- Marker vor und nach dem Import von `main`.
- Marker vor und nach der Router-Initialisierung.
- Marker vor und nach `dispatch()`.
- Dauer der einzelnen Phasen mit `time.monotonic()` messen.
- Nur feste Phasennamen, Laufzeiten und harmlose Fehlercodes protokollieren.
- Unbehandelte Exceptions so abfangen, dass Kodi den Plugin-Aufruf abschließen kann.
- Fehlerzustände verständlich anzeigen, ohne einen neuen endlosen Ladekreis auszulösen.

### 4.2 `main.py` – Router und Dispatch

Pfad:

`src/plugin.video.xtreammate/resources/lib/main.py`

Im aktuellen `Router.dispatch()` erfolgt vor dem eigentlichen Routing:

```python
import portals as _portals_mod
_portals_mod.import_from_settings()

action = self._params.get('action', 'root')
debug('dispatch: {}'.format(action))
```

**Besonders wichtiger Befund:** Der erwartete Diagnoseeintrag `dispatch: root` fehlt im älteren Protokoll auch nach Aktivierung des Kodi-Debugloggings.

Das deutet auf eine mögliche Blockade vor diesem Diagnosemarker hin, beweist diese jedoch nicht abschließend.

**Erforderlicher Hotfix:**

- Diagnosepunkte vor und nach `import portals`.
- Diagnosepunkte vor und nach `import_from_settings()`.
- Router-Aktion vor weiteren aufwendigen Arbeiten protokollieren.
- Sicherstellen, dass Portal-Migrationen den normalen Start nicht unbegrenzt blockieren.
- Prüfen, ob wiederholte Add-on-/Widget-Aufrufe unnötig dieselben Initialisierungen auslösen.
- Bestehendes Root-Routing und alle registrierten Aktionen erhalten.

### 4.3 `portals.py` – Portalliste und Migration

Pfad:

`src/plugin.video.xtreammate/resources/lib/portals.py`

Untersuche insbesondere:

```python
load_all()
import_from_settings()
save_all()
```

Zu prüfen:

- Verfügbarkeit von `portals.json`.
- Dateizugriff über `xbmcvfs` und lokale Python-Dateioperationen.
- Mögliche blockierende Schreibvorgänge, Migrationen oder konkurrierende Zugriffe.
- Umgang mit vorhandenen und möglicherweise unvollständigen Portaldaten.
- Verhalten bei fehlenden, defekten oder nicht lesbaren Dateien.

**Zwingende Schutzregel:** Eine nicht lesbare Portalliste darf keinesfalls stillschweigend als leere, neu einzurichtende Portalliste behandelt werden.

Keine automatische Bereinigung, kein stiller Reset und kein Überschreiben vorhandener Daten.

### 4.4 `service.py` – Hintergrunddienst

Pfad:

`src/plugin.video.xtreammate/service.py`

Prüfe insbesondere:

- `_maybe_refresh_epg()`
- `_maybe_warm_catalogs()`
- EPG-Worker und Katalog-Worker
- Initialisierung und Beendigung des Dienstes
- Gemeinsame Zugriffe von Dienst und Plugin auf Profildateien und Datenbanken
- SQLite-Busy-Timeouts und Schreibsperren
- Reaktion auf Kodi-Abbruchsignale

Das Protokoll belegt, dass der Dienst startet und eine EPG-Aktualisierung plant. Es belegt nicht, dass dieser Vorgang den Hauptmenüstart verursacht.

**Erforderlicher Hotfix, sofern durch Analyse bestätigt:**

- Keine lang laufenden EPG- oder Katalogimporte auf dem Hauptmenü-Startpfad.
- Hintergrundarbeiten müssen abbrechbar sein.
- Datenbanktransaktionen kurz halten.
- Keine unbegrenzten Lock-Wartezeiten.
- Gleichzeitige Worker-Aufrufe kontrollieren.
- Dienst und UI dürfen sich gegenseitig nicht dauerhaft blockieren.

### 4.5 `home_menu.py`, `app_routes.py`, `library_index.py`

Zu prüfen:

- `_root()` und `_show_portal_home()` in `main.py`
- `home_menu.show()`
- `app_routes.dispatch()`
- Widget-Routen und Katalogleser
- Verzeichnisabschluss mit `xbmcplugin.endOfDirectory()`

Sicherstellen, dass das Hauptmenü aus seinen vorhandenen lokalen Daten aufgebaut werden kann, ohne zuvor komplette Sender-, Film- oder Serienkataloge synchron zu importieren.

Auch bei laufender Hintergrundaktualisierung muss eine bedienbare Startansicht verfügbar bleiben.

---

## 5. Verbindliche Hotfix-Anforderungen

### HF-01 – Startphase instrumentieren

Füge gezielte, datensparsame Diagnosemarker in den Startpfad ein.

Beispiel für das gewünschte Schema:

```text
[XCMate][BOOT] ENTRY
[XCMate][BOOT] MAIN_IMPORT_BEGIN
[XCMate][BOOT] MAIN_IMPORT_DONE duration_ms=...
[XCMate][BOOT] ROUTER_INIT_DONE duration_ms=...
[XCMate][BOOT] PORTALS_LOAD_BEGIN
[XCMate][BOOT] PORTALS_LOAD_DONE duration_ms=...
[XCMate][BOOT] ROOT_MENU_BEGIN
[XCMate][BOOT] ROOT_MENU_DONE duration_ms=...
```

Das sind illustrative Marker. Implementiere sie passend zur tatsächlichen Architektur.

Fehlende Abschlussmarker sollen die blockierte Phase eindeutig erkennen lassen.

### HF-02 – Blockierenden Code identifizieren und korrigieren

Analysiere den tatsächlichen Startpfad anhand des Codes und gezielter Regressionstests.

Keine unbegründete Festlegung auf SQLite, EPG, Portaldateien oder Python-Imports.

Die konkrete Ursache beziehungsweise der engste nachweisbare Fehlerbereich muss im Pull Request dokumentiert werden.

### HF-03 – Hauptmenü vom Hintergrundimport entkoppeln

Das Öffnen von XCMate darf nicht auf vollständige Katalog- oder EPG-Aktualisierungen warten.

**Zielverhalten:**

- Hauptmenü aus lokal verfügbaren Daten anzeigen.
- Import- und Aktualisierungsstatus separat darstellen.
- Fehlende Daten über nachvollziehbare Lade-/Statushinweise behandeln.
- Langsame Netzwerkanfragen außerhalb des kritischen Hauptmenüpfads ausführen.
- Keine unbegrenzten Wartezustände.

### HF-04 – Kodi-Verzeichnisaufrufe zuverlässig abschließen

Prüfe alle betroffenen Start- und Fehlerrouten.

Kodi muss sowohl bei Erfolg als auch bei behandelten Fehlern einen korrekten Verzeichnisabschluss erhalten.

Doppelte `endOfDirectory()`-Aufrufe ebenso vermeiden wie ganz fehlende Abschlüsse.

Ein fehlgeschlagener Start darf nicht zu einem dauerhaft sichtbaren Ladekreis führen.

### HF-05 – Gleichzeitige Widget-Aufrufe absichern

Die BINGIE-Widgets sind nicht als alleinige Fehlerursache bestätigt, müssen aber gegen parallele Aufrufe getestet werden.

Prüfe insbesondere:

- `widget_live_start_group`
- `widget_recent_vod`
- `widget_recent_series`

Widget-Aufrufe dürfen keine vollständige Synchronisation erzwingen und das Hauptmenü nicht blockieren.

### HF-06 – Datenintegrität sicherstellen

Bestehende Profildaten müssen erhalten bleiben.

Dazu gehören insbesondere:

- Xtream-/M3U-/Stalker-Portale und Zugangsdaten
- Startsender und Startgruppen
- aktivierte/deaktivierte Sendergruppen
- Favoriten
- EPG-Quellen und manuelle Zuordnungen
- Cache- und SQLite-Datenbanken
- Film-/Serien-Wiedergabefortschritt
- Fernbedienungseinstellungen
- Skin- und Erscheinungsbild-Einstellungen

**Verboten als pauschale Fehlerbehebung:**

- Cache vollständig löschen
- Portaldatei löschen
- Datenbanken ungefragt zurücksetzen
- Add-on-Profil neu erstellen
- bestehende Konfiguration überschreiben

Migrationen müssen idempotent und nachvollziehbar sein; bei riskanten Änderungen ist ein sicherer Rollback vorzusehen.

### HF-07 – Fehlerbehandlung verbessern

Bei einem tatsächlichen Startfehler:

- Eindeutige Diagnosekennung schreiben.
- Exception-Klasse und sichere technische Informationen erfassen.
- Keine Zugangsdaten oder vollständigen Portal-URLs protokollieren.
- Kodi-Verzeichnis kontrolliert beenden.
- Eine verständliche Fehlermeldung anbieten.
- Bereits gespeicherte Daten unangetastet lassen.

Keine irreführende Erfolgsmeldung bei fehlgeschlagener Initialisierung.

---

## 6. Strikt eingefrorene Funktionen

Die bereits funktionierende Fernbedienungs- und Live-TV-Navigation der Version 0.1.27 ist **Freeze-Bestand**.

Nicht verändern:

- OK: Live-TV-Informations-Overlay
- Erneutes OK / Abwärts: untere Player-Bedienleiste gemäß bestehendem Verhalten
- Links: Senderliste
- Erneutes Links: Gruppenliste
- Hoch/Runter: Senderwechsel
- Zurück: Overlay beziehungsweise Navigation schließen
- Bestehende Key-Bindings und Fallback-Regeln
- Live-TV-Playerintegration
- Startsender-/Startgruppen-Persistenz

Keine neuen globalen Kodi-Keymaps installieren.

Auch keine Änderungen am globalen Kodi-Skin oder an Titan BINGIE MOD.

**Der Hotfix soll ausschließlich die Startstabilität und unmittelbar notwendige Abhängigkeiten korrigieren.**

---

## 7. Verbindliche Regressionstests

Ergänze automatisierte Tests für folgende Fälle:

| Testfall | Erwartetes Verhalten |
|---|---|
| Normales Bestandsprofil | XCMate-Root öffnet sich |
| Vorhandene Xtream-Portale | Keine erneute unbeabsichtigte Migration |
| Leeres neues Profil | Einrichtungsassistent erreichbar |
| Defekte `portals.json` | Keine Datenüberschreibung, verständlicher Fehler |
| Laufender EPG-Worker | Hauptmenü weiterhin erreichbar |
| Laufender Katalogimport | Hauptmenü bleibt bedienbar |
| Parallel aufgerufene Widgets | Kein dauerhaftes Blockieren |
| Langsame oder nicht erreichbare Provider | Kein unendlicher Startvorgang |
| SQLite-Datei zeitweise gesperrt | Begrenzte Wartezeit, sichere Reaktion |
| Wiederholtes Öffnen und Zurück | Keine hängenden Plugin-Aufrufe |
| Kodi-Neustart | Einstellungen und Daten bleiben erhalten |
| Fehler während Menüinitialisierung | Kontrollierter Verzeichnisabschluss |

Bestehende Tests müssen weiterhin bestehen.

Meldungen über erfolgreiche Tests nur mit konkreten Testergebnissen, nicht pauschal.

### Geräteabnahme

Die finale Bestätigung erfolgt auf der vorhandenen Android-TV-Box mit Kodi 21.3 und ARM 32-bit.

**Abnahmekriterien:**

1. XCMate-Hauptmenü erscheint bei normalen Starts innerhalb weniger Sekunden.
2. Kein dauerhafter Ladekreis.
3. Wiederholter Start funktioniert.
4. EPG- und Katalogjobs blockieren das Menü nicht.
5. Widgets können parallel laden.
6. Kodi bleibt jederzeit mit der Fernbedienung bedienbar.
7. Gespeicherte Portale und Einstellungen sind unverändert.
8. Die eingefrorene Live-TV-Overlaynavigation funktioniert weiterhin.

Automatisierte Tests allein ersetzen den Android-TV-Gerätetest nicht.

---

## 8. Branch, Pull Request und Versionierung

Erstelle einen separaten Arbeitsbranch, beispielsweise:

`fix/xcmate-028-startup-hang`

Erstelle einen Pull Request gegen `main` mit Verweis auf Issue #38.

**Vorgesehene Hotfix-Version nach Freigabe:** `0.1.28.1`, sofern kompatibel mit den bestehenden Repository- und Versionierungsregeln.

Die bereits veröffentlichte `0.1.28` darf nicht stillschweigend durch ein anderes ZIP mit identischer Versionsnummer ersetzt werden.

Der Pull Request muss enthalten:

- Reproduktions- und Ursachenanalyse
- Exakte Codeänderungen
- Liste der betroffenen Dateien
- Sicherheits- und Datenintegritätsbewertung
- Testresultate
- Bekannte Restrisiken
- Android-TV-Testanleitung
- Rollback-Anleitung ohne Profilverlust
- Kurzen deutschsprachigen Changelog

**Nicht eigenständig mergen oder veröffentlichen.** Erst nach Review und ausdrücklicher Freigabe.

---

## 9. Nicht Bestandteil dieses Hotfixes

Folgende Entwicklungsthemen sind ausdrücklich zurückzustellen:

- Neues XCMate-Original-Icon
- Neuer Standardhintergrund
- Space Premium Grafik-Theme
- Theme-Installer
- Weitere Design- und Spracheinstellungen
- Neue Streaming- oder EPG-Funktionen ohne unmittelbaren Bezug zum Startfehler

Diese Aufgaben bleiben in der weiteren Produktplanung, insbesondere in Issue #37.

Kein Feature-Scope-Creep im kritischen Start-Hotfix.

---

## 10. Erwarteter Abschlussbericht von Codex

Bitte liefere nach Umsetzung einen strukturierten Bericht mit:

1. **Root Cause:** Was hat den Start konkret blockiert? Falls nicht abschließend belegt, ausdrücklich kennzeichnen.
2. **Hotfix:** Welche Änderungen wurden vorgenommen und warum?
3. **Datensicherheit:** Wie wird sichergestellt, dass bestehende Benutzerinformationen erhalten bleiben?
4. **Regressionen:** Welche Tests wurden ausgeführt, mit welchen Ergebnissen?
5. **Offene Punkte:** Welche Risiken bleiben bis zum Android-TV-Test?
6. **PR-Link:** Wo kann die Änderung geprüft werden?
7. **Installationsanleitung:** Wie wird der freigegebene Hotfix über das GS-Media-Repository installiert?

**Endziel:** Ein zuverlässig startendes XCMate, ohne Datenverlust, ohne Fernbedienungsregressionen und ohne erneute dauerhafte Kodi-Ladekreise.

**BEGINNE JETZT MIT DER CODEANALYSE UND DEM HOTFIX-PR. KEIN MERGE OHNE AUSDRÜCKLICHE FREIGABE.**