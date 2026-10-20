# CODEX – XCMate 0.1.29.2
## Integrationsprüfung, Qualitätssicherung und Vorbereitung eines vollständigen Release-Kandidaten

**Projekt:** GS Media – XCMate  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Aktuelle produktive Version:** 0.1.28  
**Geplante Zielversion:** 0.1.29.2  
**Zielgerät:** Android-TV-Box, Kodi 21.3 Omega, ARM 32-bit  
**Skins:** Titan BINGIE MOD und Estuary

## 1. Ziel des Auftrags

Bereite aus den bereits bestehenden fünf Entwicklungs-Pull-Requests einen vollständigen, konsistenten und getesteten Release-Kandidaten **XCMate 0.1.29.2** vor.

Der Benutzer möchte von **0.1.28 direkt auf 0.1.29.2** aktualisieren können.

Es sollen keine fünf einzelnen Installationsschritte erforderlich sein.

**Wichtig: Dies ist zunächst ein Integrations-, Prüf- und Release-Vorbereitungsauftrag. Noch keine eigenmächtigen Merges und keine Veröffentlichung.**

## 2. Vorhandene Pull Requests prüfen

Die folgende Entwicklungsreihenfolge wurde bereits vorbereitet:

| Reihenfolge | PR | Branch | Entwicklungsversion |
|---|---|---|---|
| 1 | #39 | `fix/xcmate-028-startup-hang` | 0.1.28.1 |
| 2 | #45 | `fix/xcmate-owned-playback-exit` | 0.1.28.2 |
| 3 | #46 | `feat/xcmate-persistent-media` | 0.1.29 |
| 4 | #47 | `feat/xcmate-active-continuous-live` | 0.1.29.1 |
| 5 | #48 | `feat/xcmate-universal-setup` | 0.1.29.2 |

Diese Pull Requests sind gestapelt und bauen aufeinander auf.

Bitte zunächst prüfen:

1. Sind alle fünf PRs weiterhin offen und unverändert?
2. Stimmen ihre Basisbranches und Commit-Abhängigkeiten?
3. Enthält der aktuelle Branch von PR #48 sämtliche Änderungen aus #39, #45, #46 und #47?
4. Gibt es Mergekonflikte, doppelte Änderungen oder versehentlich überschriebene Funktionen?
5. Gibt es nicht beabsichtigte Änderungen an anderen Kodi-Add-ons oder am GS-Media-Repository?
6. Ist die Versionsnummer `0.1.29.2` im vollständigen Integrationsstand konsistent?

Wenn der Branch von PR #48 bereits den gesamten benötigten Code enthält, verwende diesen als Ausgangspunkt für einen isolierten Release-Kandidaten.

Keine unnötige zweite Implementierung derselben Funktionen durchführen.

## 3. Kritische Integrationsprüfung

### A – Startverhalten

Prüfe die Änderungen aus PR #39.

Der bisherige Fehler unter 0.1.28 war ein zeitweise endloser Ladekreis beim Öffnen von XCMate.

Nach erzwungenem Beenden von Kodi, Löschen des Android-App-Caches und Neustart war das Hauptmenü wieder erreichbar.

Die tatsächliche Ursache ist nicht abschließend nachgewiesen.

Anforderungen:

- Start ohne blockierende Netzwerkoperationen.
- Keine langen synchronen EPG- oder Katalogimporte beim Menüstart.
- Hintergrunddienste dürfen die Benutzeroberfläche nicht blockieren.
- Diagnosemarker ohne Zugangsdaten.
- Fehlerfälle kontrolliert behandeln.
- Bereits gespeicherte Konfigurationen erhalten.

### B – Wiedergabe und Zurück-Taste

Prüfe PR #45 besonders sorgfältig.

Nach dem Verlassen einer laufenden Film- oder Serienwiedergabe müssen Bild und Ton tatsächlich gestoppt werden.

Die Wiedergabeposition muss vorher gespeichert werden.

Ein XCMate-Stopp darf niemals fremde Kodi-Streams beenden.

Die bisher funktionierende Live-TV-Overlaynavigation bleibt erhalten.

### C – Persistente Cover und Favoriten

Prüfe PR #46.

Erwartet werden:

- Dauerhaft gespeicherte Film- und Seriencover.
- Persistente Hintergrundgrafiken.
- Platzhalter nur bis zum erfolgreichen Nachladen.
- Kein erneuter Download bereits vorhandener Bilder bei jedem Seitenwechsel.
- Horizontale Reihen für Neuheiten, Favoriten und Weitersehen.
- Favoriten direkt hinzufügen und entfernen.
- Gesehen-/Ungesehen-Status für Serienfolgen.
- Wiederaufnahme gespeicherter Wiedergabepositionen.

Das Speicherbudget muss kontrollierbar sein, ohne den Android-Gerätespeicher unkontrolliert zu füllen.

### D – Sender- und Gruppenlisten

Prüfe PR #47.

Erwartet werden:

- Nur aktivierte Sendergruppen sichtbar.
- Keine Kennzeichnung „AN“ oder „AUS“ in der normalen Gruppenliste.
- Gruppenverwaltung über eine eigene Fernbedienungsaktion.
- Deaktivierte Gruppen bleiben gespeichert und können wieder aktiviert werden.
- Keine sichtbaren Einträge „Nächste Senderseite“ oder „Vorherige Senderseite“.
- Durchgehendes Scrollen auch bei sehr großen Sendergruppen.
- EPG „Jetzt“ und „Als Nächstes“ bleibt schnell verfügbar.

### E – Universeller Einrichtungsassistent

Prüfe PR #48.

Gleichberechtigte Unterstützung für:

1. Xtream Codes
2. M3U/M3U8-URL
3. M3U/M3U8-Dateiimport
4. Stalker-/MAG-Portale

Einheitlicher Workflow:

**Accountdaten → Kategorien laden → Checkbox-Auswahl → selektiver Scan → Ergebnis → Speichern → Hintergrundvervollständigung**

Zusätzlich:

- M3U-Playlist-Editor
- Gruppen- und Senderverwaltung
- EPG-Zuordnung
- Import und Export
- Persistente Benutzeränderungen
- Selektiver Film- und Serienimport
- Fortlaufender Cover-/Metadatendownload
- Berücksichtigung der Providerfähigkeiten

Die vorhandenen Account- und Gruppeninformationen dürfen durch den neuen Assistenten nicht verändert oder zurückgesetzt werden.

## 4. Verbindlicher Freeze der funktionierenden Fernbedienung

Die Android-Gerätetests für Version 0.1.28 haben folgende Funktionen bestätigt:

**BESTANDEN:**

- Gespeicherten Startsender starten.
- Bild und Ton funktionieren.
- OK öffnet vollständige XCMate-Infoleiste.
- Senderlogo, aktuelle und nächste Sendung sowie Fortschrittsbalken sichtbar.
- Zweites OK öffnet die untere Bedienleiste.
- Links öffnet die Senderliste schnell.
- Senderliste zeigt EPG-Daten.
- Links erneut öffnet die Gruppenliste.
- Hoch/Runter wechselt Sender zuverlässig.

Diese funktionierenden Verhaltensweisen müssen erhalten bleiben.

Neue Fernbedienungsfunktionen dürfen keine globalen Kodi-Keymaps verändern.

Die Korrekturen an Gruppenliste und Wiedergabestopp dürfen keine Regressionen in der Overlaynavigation verursachen.

## 5. Datenintegrität

Vor jeder Freigabe prüfen, dass folgende Daten erhalten bleiben:

- Xtream-Codes-Zugänge
- M3U- und Stalker-Portalprofile
- Zugangsdaten und Providerkonfiguration
- Aktivierte/deaktivierte Sendergruppen
- Aktivierte Film- und Seriengruppen
- Startsender und Startgruppe
- EPG-Quellen und manuelle Zuordnungen
- Favoriten
- Wiedergabefortschritt
- Gesehen-/Ungesehen-Status
- Lokale EPG-Datenbanken
- Medienbibliothek und Cover
- Benutzerdefinierte Fernbedienungseinstellungen

Bestehende Dateien und Datenbanken nicht pauschal löschen oder zurücksetzen.

Neue Datenbankstrukturen benötigen sichere, wiederholbare Migrationen.

Bei fehlgeschlagenen Migrationen alte Daten erhalten und Fehler protokollieren.

## 6. Automatisierte Prüfungen

Führe die vollständigen bestehenden Tests auf dem integrierten Stand aus.

Zusätzlich gezielt prüfen:

- Kodi-21.3-API-Kompatibilität.
- Python-Syntax und Add-on-Abhängigkeiten.
- Multithreading und SQLite-Zugriffe.
- Gleichzeitiger EPG- und Coverdownload.
- Große Sender-, Film- und Serienkataloge.
- Unvollständige M3U-Playlists.
- Fehlgeschlagene Stalker-Authentifizierung.
- Abbruch des Einrichtungsassistenten.
- Instabile Internetverbindung.
- Neustart während Hintergrundimporten.
- Persistenz aller Einstellungen.
- Kodi-Wiedergabe und Zurück-Tastenverhalten.
- Favoriten und Wiedergabefortschritt.
- Speicherplatzmangel und Wiederaufnahme von Hintergrundaufgaben.

Vorhandene Testergebnisse aus den Einzel-PRs nicht einfach als Integrationsnachweis übernehmen. Die vollständige zusammengeführte Codebasis erneut testen.

Dokumentiere erfolgreich bestandene und fehlgeschlagene Tests getrennt.

## 7. Release-Kandidat erstellen

Wenn die Integrationsprüfung erfolgreich abgeschlossen ist, bereite einen vollständigen Release-Kandidaten vor.

**Version:** `0.1.29.2`

**Paketname:**

`plugin.video.xtreammate-0.1.29.2.zip`

Anforderungen:

- Vollständiges, direkt über Kodi installierbares Add-on-Paket.
- Korrekte Add-on-Verzeichnisstruktur.
- Versionsnummer im `addon.xml` prüfen.
- Sämtliche benötigten Python-, XML-, Sprach- und Grafikdateien enthalten.
- Keine Entwicklungsdateien, Zugangsdaten oder Testgeheimnisse im Installationspaket.
- ZIP-Struktur automatisch validieren.
- SHA-256-Prüfsumme erstellen.
- Installations- und Updatepfad von 0.1.28 prüfen.

Der Release-Kandidat soll zunächst als überprüfbares Artefakt verfügbar gemacht werden, ohne das bestehende offizielle Paket oder den produktiven Kodi-Repository-Index zu verändern.

Falls die vorhandene CI-Infrastruktur Artefakte bereitstellen kann, diese verwenden.

**Noch keine Veröffentlichung unter der produktiven Updatequelle.**

## 8. Integration in den Hauptbranch vorbereiten

Erstelle einen überprüfbaren Integrationsplan.

Bei Freigabe sollen die fünf gestapelten PRs in der korrekten Abhängigkeitsreihenfolge integriert werden.

Vermeide doppelte Commits und bereits enthaltene Änderungen.

Der Hauptbranch `main` darf erst nach ausdrücklicher Freigabe verändert werden.

Erst danach sollen die Release-Dateien und der Kodi-Repository-Index für XCMate 0.1.29.2 aktualisiert werden.

Die Version des eigenständigen GS-Media-Repository-Add-ons `repository.gsmedia` ist davon zu unterscheiden und nicht ohne konkreten Grund zu erhöhen.

## 9. Rollback- und Updatekonzept

Stelle sicher, dass der Benutzer bei Problemen wieder auf die bisher funktionierende Version 0.1.28 zurückgehen kann.

Vor der ersten Installation auf dem Android-TV-Gerät muss eine Datensicherungsanleitung bereitstehen.

Wichtig:

- Kein Zurücksetzen von Kodi.
- Kein Löschen der Add-on-Daten.
- Keine Neuinstallation sämtlicher Kodi-Add-ons.
- Keine automatische Entfernung gespeicherter Accounts.

Falls ein einfacher Downgrade aufgrund einer Datenbankmigration nicht sicher ist, muss dies vor der Veröffentlichung ausdrücklich dokumentiert und eine Wiederherstellungsstrategie bereitgestellt werden.

## 10. Erwarteter Codex-Abschlussbericht

Bitte nach Abschluss der Arbeiten einen strukturierten Bericht mit folgenden Informationen ausgeben:

1. Aktueller Zustand aller fünf Pull Requests.
2. Bestätigung der vollständigen Änderungsübernahme in 0.1.29.2.
3. Gefundene Integrationskonflikte und deren Behebung.
4. Übersicht der geänderten Dateien.
5. Ergebnis der vollständigen automatisierten Tests.
6. Sicherheits- und Datenintegritätsprüfung.
7. Bestätigung der unveränderten Live-TV-Fernbedienungsfunktionen.
8. Ergebnis der ZIP- und Versionsprüfung.
9. Speicherort beziehungsweise Artefaktlink des Release-Kandidaten.
10. SHA-256-Prüfsumme.
11. Konkrete Anleitung für Update und gegebenenfalls Rollback.
12. Noch offene Risiken und erforderliche Android-Gerätetests.
13. Empfehlung, ob die Version zur Freigabe bereit ist.

**Gib keine pauschale Erfolgsmeldung aus, wenn eine Prüfung nicht durchgeführt werden konnte. Nicht auf dem realen Android-Gerät ausgeführte Tests ausdrücklich als offen kennzeichnen.**

## 11. Freigabegrenze

Du darfst:

- Den Code untersuchen.
- Pull Requests vergleichen.
- Fehler in Entwicklungsbranches korrigieren.
- Tests erstellen und ausführen.
- Einen isolierten Release-Kandidaten bauen.
- Dokumentation und Prüfberichte erstellen.

Du darfst ohne ausdrückliche Benutzerfreigabe NICHT:

- Die fünf Pull Requests mergen.
- Den Hauptbranch verändern.
- Das produktive Repository aktualisieren.
- Die ZIP-Datei als öffentliche XCMate-Aktualisierung veröffentlichen.
- Gespeicherte Benutzerprofile löschen.
- Bestehende Add-ons oder Kodi-Konfigurationen zurücksetzen.

## Abschließende Anweisung

**Beginne jetzt mit der vollständigen technischen Integrationsprüfung von PR #39, #45, #46, #47 und #48.**

**Bereite anschließend einen einzigen vollständigen, getesteten Release-Kandidaten XCMate 0.1.29.2 vor.**

Keine fünf separaten Nutzerinstallationen.

Nach Abschluss den Prüfbericht vorlegen und auf Freigabe warten.