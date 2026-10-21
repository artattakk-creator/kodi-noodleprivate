# CODEX-AUFTRAG: XCMate – EPG-Hotfix, Navigation und Version 0.1.30

**Projekt:** GS Media / XCMate  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Zielsystem:** Android-TV, Kodi 21.3 Omega, Titan BINGIE MOD, IR-Fernbedienung  
**Stand:** 21.10.2026

## 1. Verbindlicher Entwicklungsstand

- **0.1.29.4:** Draft-PR #55, Branch `fix/xcmate-0294-setup-scan-save`. Diese Version ist auf dem realen Android-TV installiert und durch ein neues EZ-Maintenance+-Backup gesichert.
- **0.1.30:** Draft-PR #50, Branch `feat/xcmate-space-premium-installer`. Bereits vorbereitet mit Space Premium, Theme-Installer, 98 Originalgrafiken und bestehender Testinfrastruktur.
- Relevante Aufgaben: GitHub Issues **#57** (neuer horizontaler EPG), **#58** (EPG-Dubletten), **#59** (Zurück-Navigation), **#60** (EPG-Matching).

**Bestehende 0.1.29.4- und 0.1.30-ZIP-Dateien nicht unter derselben Versionsnummer überschreiben. Keine eigenmächtigen Merges nach `main`, keine Releases und keine automatischen Repository-Updates.**

## 2. Ergebnisse des Android-Gerätetests

Bereits erfolgreich:

- XCMate-Hauptmenü öffnet.
- Live-TV, Filme und Serien sind erreichbar und zeigen Kataloginhalte.
- EPG öffnet und zeigt Sender.
- Zwei externe XMLTV-Quellen wurden erfolgreich importiert.
- Ein neues Backup der installierten Version wurde erstellt.

Weiterhin fehlerhaft:

### P0-A – Doppelte Kurz-EPG-Einträge

Sender: `DE| PROSIEBEN HEVC`

Im Programmführer stehen:

- `Two and a Half Men`, 15:06–15:36, Quelle Xtream Kurz-EPG
- `Two and a Half Men`, 15:07–15:36, Quelle Xtream Kurz-EPG
- `Two and a Half Men`, 15:36–16:05, zweimal identisch

Beide Detailfenster bestätigen ausdrücklich **Xtream Kurz-EPG**. Für diesen Sender erscheint außerdem **„Kein Langzeit-EPG vorhanden“**.

Code untersuchen:

- `resources/lib/epg_views.py`: `_short_guide()`, `guide_for_channel()`, `resolve_guide()`
- `resources/lib/guide_window.py`: `_load_events()`
- `resources/lib/guide_store.py`
- `resources/lib/stream_epg.py`
- Xtream-API-Client und lokaler Kurz-EPG-Cache

Anforderungen:

1. Zunächst die Herkunft der Rohdaten identifizieren. Keine unbelegte Behauptung, dass Kodi oder der Anbieter den Zeitversatz erzeugt.
2. Eine zentrale, deterministische Dublettenerkennung implementieren.
3. Gleicher normalisierter Sendungstitel, dieselbe Senderzuordnung und nahezu identische, stark überlappende Sendeintervalle müssen als mögliche Dublette erkannt werden.
4. Beispiel 15:06–15:36 gegenüber 15:07–15:36 muss zu einem sichtbaren Programmeintrag führen.
5. Exakt identische Wiederholungen ebenfalls entfernen.
6. Tatsächlich unterschiedliche Episoden mit gleichem Titel und aufeinanderfolgenden Zeiten beibehalten.
7. Datenqualität, Quellpriorität und vorhandene Beschreibungen bei der Auswahl des besseren Eintrags berücksichtigen.
8. Bereinigung konsistent für Programmführer, Now/Next, Senderliste und Live-TV-Overlay verwenden.
9. Verhindern, dass ein Kurz-EPG mit vier Rohereignissen aufgrund von Dubletten nur zwei sinnvolle Sendeplätze liefert, ohne die Anbieter-API unnötig zu belasten.

Automatisierte Regressionen für diese konkreten Uhrzeiten erstellen.

### P0-B – Fehlerhafte Zurück-Navigation

Aktuelles Verhalten: Beim Zurückgehen aus dem EPG werden teilweise erneut EPG-Daten beziehungsweise Listen aufgebaut. Ein weiterer Druck auf Zurück führt direkt aus dem gesamten Add-on.

Erwartetes Verhalten:

- Back im Detailfenster: Detailfenster schließen.
- Back in einer Unterebene: eine Ebene zurück.
- Back auf der obersten EPG-Ebene: zur XCMate-Hauptübersicht mit Live-TV, EPG, Filmen, Serien und Einstellungen.
- Dieselbe Navigationshierarchie für Filme und Serien.
- Erst Back auf der eigentlichen Hauptübersicht darf XCMate verlassen.
- Keine erneuten Remote-Katalogscans, unnötigen EPG-Importe, Endlosschleifen oder mehrfachen Fensterinstanzen beim Zurückgehen.
- Vorheriger Fokus und Auswahl möglichst erhalten.

Prüfen:

- `app_routes.py`
- `home_menu.py`
- `guide_window.py`
- `media_window.py`
- Kodi-Verzeichnisabschlüsse und `WindowXML`-Lebenszyklus

**Zusätzlicher sicherheitsrelevanter Codebefund:** `guide_window.py` und `media_window.py` verwenden Future-Callbacks, die GUI-Controls aus Worker-Threads verändern können. Diese Pfade anhand des in 0.1.29.4 reparierten Setup-Owner-Pump-Konzepts überprüfen und gegebenenfalls thread-sicher korrigieren.

Keine globale Fernbedienungs-Keymap verändern.

### P1 – Fehlendes Langzeit-EPG / Senderzuordnung

Gemessener Gerätestatus:

| Quelle | Status | Programme |
|---|---|---:|
| EPGShare01 Deutschland | READY | 9.967 |
| Kaimandura Master Deutschland | READY | 33.611 |
| Anbieter-XMLTV | WAITING | Kein Erfolg bestätigt |
| Persistenter EPG-Cache | READY | 1.676 |

Aktivierte Xtream-Sender: 2.764.  
XMLTV-Zuordnung: 288 (10,4 %).  
Automatisch über Namen: 242.  
Anbieter-ID: 46.  
Manuell: 0.

Diese Quote bezieht sich nur auf XMLTV. Viele nichtdeutsche oder alternative Streams können außerhalb der verfügbaren XMLTV-Abdeckung liegen.

Aufgaben:

1. Sender-Matching verbessern, insbesondere bei Namen wie `DE| PROSIEBEN HEVC`.
2. Zusätze wie DE/Germany, HD, FHD, UHD, HEVC, H.264/H.265 oder andere Codechangaben konservativ normalisieren.
3. Unterschiedliche Sender wie ProSieben und ProSieben MAXX beziehungsweise SAT.1 und SAT.1 GOLD keinesfalls zusammenführen.
4. Bestehende manuelle Zuordnungen behalten und stets priorisieren.
5. Quellenkonflikte und fehlende Programmabdeckung in der Diagnose kenntlich machen.
6. Keine Quelle ungefragt löschen oder deaktivieren.
7. Fehlende oder abweichende EPG-IDs über einen manuellen Senderdialog korrigierbar machen.

## 3. Neue EPG-Oberfläche für 0.1.30

Anforderungen gemäß GitHub Issue #57:

- Linke feststehende Spalte: Senderlogo und Sendername, vertikal scrollbar.
- Rechte Spalte: gemeinsame horizontale Zeitachse mit proportional breiten Sendungsblöcken.
- Start beim aktuellen Zeitpunkt, horizontales Scrollen in zukünftige Sendungen.
- Deutliche Jetzt-Markierung und sichtbarer Fokus.
- Hoch/Runter für Sender, Links/Rechts für Sendungen und Zeitposition.
- OK auf einer Sendung öffnet Aktionen: Details, Sender ansehen, Erinnerung, Merken sowie Aufnahme nur bei tatsächlich unterstützter Technik.
- Langer OK-Druck oder Kontext-/Menütaste auf einer Senderzeile öffnet das Sender-Kontextmenü: EPG zuweisen, Quelle anzeigen, Zuordnung entfernen, Favorit, Sender ausblenden und weitere sinnvolle Optionen.
- Vorhandene SQLite-EPG-Daten, Quellenverwaltung und Sender-Mappings weiterverwenden.
- Keine Netzwerkanfragen im GUI-Tastenhandler.
- Bei 2.764 Sendern sind Paginierung beziehungsweise Virtualisierung und geringe Speicherlast erforderlich.
- Fehlende Programmdaten sichtbar kennzeichnen, nicht erfinden.

Die horizontale EPG-Anzeige soll den bestehenden EPG-Menüpunkt der XCMate-Startseite nutzen.

Bestehende EPG- und Streamingfunktionen sollen weiter nutzbar bleiben; im Problemfall sauberer Fallback auf die stabile Anzeige.

## 4. Entwicklungsablauf – zwei Phasen

### Phase A: Hotfix auf Basis 0.1.29.4

1. Von PR #55 beziehungsweise dessen funktionierendem Codebestand einen **neuen separaten Hotfix-Branch** anlegen.
2. P0-A, P0-B und die betroffenen GUI-Thread-Probleme beheben.
3. EPG-Matching aus P1 ergänzen, soweit isoliert und regressionssicher.
4. Dafür einen technisch eindeutigen Testbuild **0.1.29.5** verwenden. Das bereits veröffentlichte Paket 0.1.29.4 bleibt bytegleich archiviert.
5. Neue automatisierte Regressionstests und vollständige bestehende Testsuite ausführen.
6. Reproduzierbare Kodi-Installations-ZIP samt Größe, SHA-256 und Testbericht erstellen.
7. Eigenständigen Draft-PR anlegen. **Nicht automatisch mergen oder veröffentlichen.**

Die Installation der 0.1.29.5 auf der ursprünglichen Box ist optional; der Nutzer möchte anschließend insbesondere 0.1.30 installieren.

### Phase B: 0.1.30 integrieren

1. PR #50 als bestehenden Funktions- und Theme-Stand berücksichtigen.
2. Sämtliche notwendigen Korrekturen aus Phase A in den 0.1.30-Code übernehmen; dabei Merge-/Cherry-Pick-Konflikte ausdrücklich überprüfen und nicht stillschweigend Code überschreiben.
3. Space Premium und den generischen Theme-Installer erhalten.
4. Neue horizontale EPG-Oberfläche und Sender-Kontextmenü implementieren, soweit die vollständige Testbarkeit gegeben ist.
5. Bestehende EPG-Dubletten- und Navigationsprobleme dürfen in 0.1.30 nicht wieder auftreten.
6. Ein vollständiges neues **XCMate 0.1.30 Core-Testpaket** und das gesonderte **Space-Premium-Theme-Paket** bauen.
7. Theme-Installation über die XCMate-interne Theme-Verwaltung; das Theme-ZIP ist kein Kodi-Add-on.
8. Wenn einzelne UI-Erweiterungen nicht ausreichend stabil sind, diese klar isolieren und dokumentieren, statt sie unausgereift als fertig zu deklarieren. Keine eigenmächtige Kürzung der Nutzeranforderungen.

## 5. Unveränderliche Schutzregeln

- Vorhandene IPTV-Accounts, Passwörter, Portale, aktivierte Sendergruppen, Favoriten, EPG-Quellen, Mappings, Startsender, Datenbanken und Caches erhalten.
- Keine automatische erneute Einrichtung oder Massenimporte auf dem Gerät.
- Stabile Live-TV-Overlaysteuerung nicht verändern: OK → Info, OK erneut/Runter → Steuerleiste, Links → Sender/Gruppen, Hoch/Runter → Senderwechsel, Zurück → Ebene schließen.
- Titan BINGIE MOD, TMDb Helper, xVAULT, EZ Maintenance+ und andere Add-ons nicht beeinträchtigen.
- Keine vollständigen Zugangsdaten oder Provider-URLs in Logs oder GitHub veröffentlichen.
- Kein 300-Sekunden-Gesamtlimit für laufende Katalog- oder EPG-Imports wieder einführen.
- Keine automatische Aktivierung von Space Premium; Standarddesign muss funktionieren.
- Weder `main` noch den produktiven Kodi-Repository-Index eigenmächtig ändern.

## 6. Tests und Abnahmekriterien

Automatisiert und anschließend auf Android prüfen:

- Kurz-EPG 15:06/15:07 wird zu genau einem Eintrag.
- Kurz-EPG mit tatsächlich verschiedenen unmittelbar folgenden Episoden bleibt korrekt.
- EPG-Quellenpriorität und manuelle Mappings bleiben stabil.
- Bestehende Einstellungen überstehen Neustart und Update.
- EPG → Zurück führt zuverlässig zur XCMate-Hauptübersicht.
- Filme/Serien → Zurück führen über korrekte Zwischenebenen zur Hauptübersicht.
- GUI-Worker manipulieren keine Kodi-Controls direkt.
- Mehrmaliges Öffnen/Schließen des EPG ohne Crash, schwarzen Bildschirm oder Datenreload-Schleife.
- XCMate 0.1.30 mit Standarddesign und anschließend Space Premium.
- Fernbedienungssteuerung, Startsender, Live-Overlay, TMDb Helper und xVAULT unverändert.
- Alle Funktionen auch nach Kodi-Neustart.

**Cloud-Tests sind keine bestandene Android-Geräteabnahme.** Alle noch nicht durchgeführten Gerätetests ausdrücklich als `NOT_RUN` ausweisen.

## 7. Gewünschtes Ergebnis von Codex

Bitte selbstständig bearbeiten und anschließend liefern:

1. Analyse der Ursachen mit betroffenen Dateien.
2. Draft-PR für den isolierten Hotfix mit Tests und 0.1.29.5-Test-ZIP.
3. Integrierten 0.1.30-Entwicklungsstand auf Basis von PR #50 einschließlich der Hotfixes.
4. Falls möglich vollständig umgesetzte horizontale EPG-Oberfläche mit Sender-Kontextmenü, sonst nachvollziehbaren Funktions- und Teststatus.
5. Vollständige installierbare 0.1.30-Core-ZIP.
6. Separates Space-Premium-Theme-ZIP mit Installationshinweisen.
7. SHA-256-Prüfsummen, Testprotokolle und kurze Android-Abnahmeanleitung.
8. Übersicht aller offenen Risiken und Funktionen, für die noch reale Gerätetests erforderlich sind.

**Arbeite die beiden Phasen in dieser Reihenfolge ab. Keinen Merge oder Release ohne ausdrückliche Freigabe. Ziel ist ein stabiler, vollständig installierbarer Kandidat für XCMate 0.1.30, ohne die vorhandene 0.1.29.4-Installation zu gefährden.**