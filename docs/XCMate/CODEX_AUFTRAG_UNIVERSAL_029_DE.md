# CODEX – XCMate Entwicklungsübergabe
## Universeller Setup-Assistent, selektiver Medienimport, persistente Medienbibliothek und Favoriten

**Projekt:** GS Media – XCMate  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Ausgangsversion:** 0.1.28  
**Zielplattform:** Kodi 21.3 / Android TV / ARM 32-bit  
**Skin:** Titan BINGIE MOD und Estuary  
**Datum:** 20.10.2026

## 1. Arbeitsauftrag

Entwickle XCMate zu einer universellen IPTV- und Medienverwaltung mit einem durchgängigen, fernbedienungstauglichen Einrichtungsassistenten.

**Gleichberechtigt unterstützte Quellen:**

- Xtream Codes
- M3U/M3U8 über HTTP/HTTPS
- Lokale M3U/M3U8-Dateien sowie importierte Dateien von USB, NAS oder SMB
- Stalker-/MAG-Portale

Alle Quellentypen sollen grundsätzlich denselben Einrichtungsablauf und soweit technisch möglich dieselbe Oberfläche für Live-TV, Filme, Serien, Favoriten und EPG verwenden.

Keine parallelen, widersprüchlichen Einrichtungslogiken entwickeln.

Verwende vorhandene Funktionen und Datenbanken weiter. Bestehende Accounts dürfen nicht verloren gehen.

## 2. Universeller Einrichtungsassistent

Der Assistent ist als schrittweise Benutzeroberfläche mit gut lesbaren Schaltflächen, Fortschrittsanzeige und Fernbedienungsbedienung zu realisieren.

### Schritt 1 – Verbindungsart und Accountdaten

Auswahl der Quelle:

**Xtream Codes:** Serveradresse, Port, Benutzername, Passwort.

**M3U-URL:** Playlist-Adresse sowie optional XMLTV-EPG-Adresse.

**M3U-Datei:** Datei über Kodi-Dateiauswahl aus internem Speicher, USB-Gerät, Netzwerkfreigabe oder anderem unterstützten Kodi-Dateipfad importieren.

**Stalker-Portal:** Server-/Portaladresse, MAC-Adresse und erforderliche unterstützte Verbindungsoptionen.

Verbindung prüfen. Keine Zugangsdaten vollständig in Diagnoseprotokolle schreiben.

Der Benutzer kann die Quelle benennen, beispielsweise „Mein TV-Paket“.

### Schritt 2 – Playlist und Kategorien erkennen

Zuerst ausschließlich die für die Auswahl benötigten Kategorien und Metadaten einlesen.

Für Xtream Codes und Stalker die vorhandenen Kategorie-APIs verwenden.

Für M3U die Playlist zunächst analysieren und nach Gruppen aufteilen. Dabei Live-TV, Filme und Serien soweit möglich erkennen.

Ergebnisoberfläche:

**Live-TV-Gruppen**

Checkboxen für alle verfügbaren Sendergruppen.

**Filmgruppen**

Checkboxen für alle verfügbaren Filmkategorien.

**Seriengruppen**

Checkboxen für alle verfügbaren Serienkategorien.

Der Benutzer kann einzelne Gruppen, mehrere Gruppen oder alle Gruppen auswählen.

**Verbindliche Regel:** Deaktivierte Gruppen werden später weder in den normalen Medienlisten dargestellt noch unnötig synchronisiert.

Weitere Länder- und Sprachpakete werden nicht automatisch importiert. EPG-Quellen sollen ausdrücklich auswählbar sein. Aktuell sind insbesondere Deutschland und Österreich relevant; weitere Länderpakete, beispielsweise Frankreich oder Spanien, können bei Bedarf ausgewählt werden.

Rechts unten befindet sich die Schaltfläche **„Weiter“**.

### Schritt 3 – Selektiver Scan

Nach „Weiter“ werden ausschließlich die ausgewählten Kategorien eingelesen.

Ein Scanfenster zeigt fortlaufend:

- Anzahl der ausgewählten Live-TV-Gruppen und Sender
- Anzahl der ausgewählten Filme
- Anzahl der ausgewählten Serien
- EPG-Importfortschritt
- Medienmetadatenstatus
- Fortschritt pro Kategorie und Gesamtfortschritt

Wo die tatsächlichen Gesamtzahlen erst beim Lesen bekannt werden, zwischen geschätzten und bestätigten Werten unterscheiden.

Möglichst serverseitige Kategorieabfragen benutzen. Falls der Provider nur Gesamtdaten liefert, datenstrombasiert filtern, statt unnötig große Listen vollständig im Arbeitsspeicher aufzubauen.

Der Scan muss abbrechbar und auch bei sehr großen Playlists stabil sein.

Nach erfolgreichem Scan automatisch zum nächsten Fenster wechseln.

### Schritt 4 – Zusammenfassung und Speichern

Zusammenfassung der gewählten Quelle, aktivierten Gruppen und importierten Medienzahlen anzeigen.

Schaltfläche **„Speichern“**.

Beim Speichern:

- Accountinformationen dauerhaft übernehmen.
- Aktivierte Gruppen und Kategorien persistieren.
- Metadaten und vorhandene EPG-Daten sichern.
- Hintergrundaufträge registrieren.
- Gespeicherte Konfiguration auf Lesbarkeit prüfen.

Für einen abgebrochenen neuen Account keine halbfertigen Portale in die produktive Konfiguration übernehmen.

Vorhandene Accounts niemals durch einen fehlgeschlagenen Scan verändern.

### Schritt 5 – Sofort nutzbare Medienoberfläche

Nach dem Speichern XCMate unmittelbar öffnen.

Live-TV, Filme und Serien sollen schon benutzbar sein, während Zusatzdaten weitergeladen werden.

Fehlende Bilder zunächst durch einheitliche hochwertige Platzhalter ersetzen.

Cover, Poster, Fanart, Hintergrundbilder und verfügbare Metadaten anschließend progressiv ergänzen.

Bereits sichtbare Listen müssen nach einem erfolgreichen Download aktualisiert werden, ohne sie vollständig neu öffnen zu müssen.

## 3. M3U-Upload und Playlist-Editor

Neben dem Import ist eine echte Bearbeitungsmöglichkeit erforderlich.

Der Benutzer soll eine M3U- oder M3U8-Datei in XCMate importieren und anschließend innerhalb des Add-ons bearbeiten können.

**Notwendige Editorfunktionen:**

- Sender anzeigen und suchen
- Gruppen erstellen, umbenennen und verwalten
- Sender Gruppen zuordnen oder verschieben
- Sender aktivieren und deaktivieren
- Sendernamen bearbeiten
- Logos zuordnen oder ändern
- EPG-ID (`tvg-id`) bearbeiten
- Senderreihenfolge anpassen
- Doppelte Einträge erkennen
- Sender hinzufügen und entfernen
- Bearbeitete Playlist wieder als standardkonforme M3U/M3U8 exportieren

Das Original darf nicht ungefragt überschrieben werden. Arbeite mit einer privaten, persistenten Arbeitskopie.

Bei M3U-URLs müssen lokale Benutzeränderungen möglichst als separate Overrides gespeichert werden, damit sie bei einem späteren Playlist-Update nicht verlorengehen.

Berücksichtige unterschiedliche Zeichencodierungen, große Dateien, ungültige Einträge und sichere Pfadverarbeitung.

Ein Dateiupload über einen PC oder ein Smartphone kann ergänzend als gesicherter Importweg vorgesehen werden. Keinen ungeschützten HTTP-Uploadserver auf der Android-Box betreiben.

**Wichtig:** M3U-Dateien liefern nicht zwingend vollständige Film-/Serien- oder Staffelinformationen. Fehlende Informationen nicht erfinden; bei unklaren Kategorien manuelle Zuordnung ermöglichen.

## 4. Dauerhafte EPG-Verwaltung

Nutze die vorhandene lokale EPG-SQLite-Datenbank und baue die selektive Aktualisierung aus.

Anforderungen:

- EPG nur für die aktivierten, relevanten Sender aufbereiten.
- Nur konfigurierte und aktivierte XMLTV-Quellen laden.
- Manuelle EPG-Zuordnungen erhalten.
- Vorhandene EPG-Daten nach Kodi-Neustart direkt wiederverwenden.
- Bereits geladene Programme nicht bei jedem Start neu herunterladen.
- Automatische Hintergrundaktualisierung nach konfigurierbarem Intervall.
- Neue Daten sicher übernehmen; alte gültige Programmdaten bei fehlgeschlagenem Import behalten.
- Programmdaten außerhalb des gültigen Zeitraums kontrolliert bereinigen.
- EPG-Aktualisierung darf weder Live-TV noch Hauptmenü blockieren.

Ein externer XMLTV-Feed kann technisch die Übertragung eines Gesamtdokuments erfordern. In diesem Fall die benötigten Senderdaten während des Stream-Parsings filtern und nur diese persistieren.

Die tatsächliche Datenmenge vor und nach der Optimierung messen.

## 5. Permanente Cover- und Metadatenspeicherung

**Verbindlich:** Ein erfolgreich heruntergeladenes Cover darf beim normalen Wechsel zwischen Filme, Serien und Startseite nicht wieder verschwinden.

Der derzeitige Bildspeicher in `media_art.py` ist mit 64 Dateien beziehungsweise 32 MB stark begrenzt. Diese Einschränkung muss durch eine skalierbare, kontrollierte Persistenzstrategie ersetzt werden.

Anforderungen:

- Lokaler dauerhafter Bildspeicher im XCMate-Profil.
- Cover, Fanart und Hintergrundbilder unterstützen.
- Dateien nach erfolgreichem Download wiederverwenden.
- Bereits sichtbare Kacheln priorisiert herunterladen.
- Danach ausgewählte Kategorien im Hintergrund vervollständigen.
- Dateistatus und Downloadfortschritt persistieren.
- Nach Neustart mit fehlenden Downloads fortfahren.
- Konfigurierbares Speicherbudget und Überprüfung des freien Speicherplatzes.
- Kein unkontrolliertes Vollschreiben des Android-Gerätes.
- Keine stille Löschung aktiv verwendeter Bilder aufgrund eines kleinen allgemeinen FIFO-/LRU-Limits.
- Fehlgeschlagene Downloads mit begrenzter Wiederholung behandeln.
- Keine Netzwerkanfragen für bereits vorhandene gültige Bilder.

Die Medienoberflächen müssen auch bei langsamen Providern jederzeit bedienbar bleiben.

## 6. Film- und Serienstartseiten erweitern

Auf den Einstiegsseiten von **Filme** und **Serien** sollen zukünftig mehrere direkt anwählbare horizontale Cover-Zeilen angezeigt werden.

Mindestens:

**Neu hinzugefügt**

Die zuletzt beim Provider hinzugefügten Filme beziehungsweise Serien.

**Meine Favoriten**

Alle vom Benutzer gespeicherten Favoriten des jeweiligen Medienbereichs, mit lokal zwischengespeicherten Covern.

**Weiter ansehen**

Bereits gestartete, aber nicht beendete Filme beziehungsweise Serien, soweit verlässliche Fortschrittsdaten existieren.

Bei Auswahl eines Covers die passende Detailansicht öffnen.

Favoriten müssen mit Fernbedienung hinzugefügt und wieder entfernt werden können.

Eine Entfernung muss unmittelbar sichtbar sein; kein Neustart und kein vollständiger Neuimport erforderlich.

Favoriten dürfen nicht automatisch entfernt werden, nur weil ein Film oder eine Serie zu Ende angesehen wurde.

Verwende bevorzugt das bestehende `media_state.py` und die MediaWindow-Architektur.

## 7. Serienstatus und Episodenfortschritt

Für Serien sind folgende Statuswerte zu unterstützen:

- **Nicht gesehen**
- **Begonnen / Weiter ansehen**
- **Gesehen**

In der Staffel- und Folgenübersicht muss der jeweilige Status sichtbar sein, beispielsweise durch ein Symbol und eine Fortschrittsanzeige.

Erforderlich sind:

- Automatische Speicherung der Wiedergabeposition
- Fortsetzung an der letzten Position
- Automatische Kennzeichnung als gesehen bei ausreichendem Wiedergabefortschritt
- Manuelles Markieren als gesehen beziehungsweise ungesehen
- Anzeige der nächsten noch nicht gesehenen Folge
- Persistenz über Kodi-Neustarts und Add-on-Updates hinweg

Bestehende Fortschrittsdaten nicht überschreiben oder zurücksetzen.

Die Zuordnung muss eindeutig nach Account, Serie, Staffel und Episode erfolgen.

## 8. Live-TV-Gruppenliste und Sendernavigation

Die bereits festgelegten Anforderungen aus Issue #37 und #42 übernehmen.

**Gruppenliste:**

- Ausschließlich aktivierte Sendergruppen anzeigen.
- Keine Kennzeichnung „AN“ oder „AUS“ in der normalen Navigation.
- Deaktivierte Gruppen bleiben in der Gruppenverwaltung verfügbar.
- Menü-/Kontexttaste innerhalb der Gruppenliste öffnet die Gruppenverwaltung mit Checkboxen.
- Änderungen nach dem Speichern unmittelbar übernehmen.

**Senderliste:**

- Keine sichtbaren Einträge „Nächste Senderseite“ oder „Vorherige Senderseite“.
- Kontinuierliches Scrollen innerhalb der jeweiligen Gruppe.
- Technische interne Paginierung ist zulässig, aber unsichtbar.
- Liste muss auch bei Hunderten oder Tausenden Sendern flüssig bleiben.
- EPG „Jetzt/Als Nächstes“ für sichtbare Sender priorisieren.

Bereits funktionierende Senderwechsel mit ↑/↓ nicht verändern.

## 9. Kritischer Wiedergabefehler

Issue #40 ist vor dem größeren Medienumbau zu korrigieren.

**Aktueller Fehler:** Filme und Serien starten, laufen aber beim Zurückgehen zur XCMate-Oberfläche teilweise im Hintergrund weiter.

Erwartetes Verhalten:

Beim expliziten Verlassen einer laufenden XCMate-Film- oder Serienwiedergabe muss der zugehörige Stream mit Bild und Ton gestoppt werden.

Zuvor Wiedergabefortschritt zuverlässig sichern.

Auch beim Verlassen einer XCMate-Live-TV-Sitzung zur eigentlichen Kodi-Navigation darf kein unerwünschter Hintergrundstream weiterlaufen.

Wichtig: Zurück innerhalb der Live-TV-Overlays muss weiterhin nur die jeweils vorgesehene Overlay-Ebene schließen. Nicht jeden Zurück-Tastendruck pauschal als Player-Stop behandeln.

Nur XCMate-eigene Wiedergabesitzungen beenden, keine fremden Kodi-Streams.

## 10. Verbindliche technische Architektur

Entwickle einen gemeinsamen Quellenadapter mit eindeutig definierten Fähigkeiten für:

- Authentifizierung und Verbindungstest
- Kategorienabfrage
- Gruppenfilterung
- Inhaltsimport
- Wiedergabeadressen
- EPG-Ermittlung
- Metadaten
- Cover/Fanart
- Serien/Staffeln/Folgen
- Aktualisierung und lokale Persistenz

Provider-spezifische Einschränkungen transparent behandeln.

**Bereits vorhandene Module prüfen und möglichst weiterverwenden:**

`setup_wizard.py`, `portal_manager.py`, `portals.py`, `iptv.py`, `stalker.py`, `xtream.py`, `group_selection.py`, `catalog_sync.py`, `library_index.py`, `stream_epg.py`, `epg_sources.py`, `guide_store.py`, `media_window.py`, `media_art.py`, `media_state.py`, `media_progress.py`, `live_overlay.py`.

Keine doppelte Datenhaltung ohne nachvollziehbaren Grund einführen.

Persistente IDs statt bloßer Anzeigenamen verwenden.

Datenbanken atomar aktualisieren, konkurrierende Hintergrundzugriffe begrenzen und bei Ausfällen die letzte gültige Datenbasis erhalten.

Vorhandene Benutzerprofile müssen vollständig kompatibel bleiben.

## 11. Tests und Abnahmekriterien

Für alle vier Quellenarten mindestens folgende Szenarien testen:

1. Neuer Account mit gezielt aktivierten Gruppen.
2. Import einer großen M3U-Datei und einer M3U-URL.
3. Xtream Codes mit großen Film- und Serienkatalogen.
4. Stalker-Portal mit den tatsächlich verfügbaren Kategorie- und Metadatenfunktionen.
5. Erneuter Start ohne unnötigen vollständigen Datenimport.
6. Änderungen an der Gruppenauswahl ohne Verlust gespeicherter Benutzerdaten.
7. Sendernavigation ohne sichtbare Folgeseiten.
8. Cover nach erstmaligem Download auch nach Neustart vorhanden.
9. Favoriten hinzufügen, anzeigen und entfernen.
10. Serienfortschritt, Folgenstatus und Wiederaufnahme.
11. Wiedergabe verlassen: Bild und Ton tatsächlich gestoppt.
12. Langsame Provider, Verbindungsabbrüche und Speicherplatzmangel.
13. Bedienbarkeit mit Android-TV-IR-Fernbedienung.
14. Erhaltung der vollständigen Live-TV-Overlaynavigation.

Die endgültige Abnahme erfolgt auf dem realen Android-TV-Gerät.

## 12. Umsetzung in getrennten Pull Requests

Bitte priorisiert arbeiten:

**Phase A – Stabilität**

- Startup-Fehler aus Issue #38 weiter untersuchen.
- Kritischen Wiedergabefehler #40 beheben.

**Phase B – Medienverwaltung**

- Dauerhafte Cover/Fanart #41.
- Favoritenzeilen und Folgenstatus #44.

**Phase C – Live-TV-Navigation**

- Aktivierte Gruppen #37.
- Kontinuierliche Senderliste #42.

**Phase D – Universeller Einrichtungsassistent**

- Gesamten Workflow aus Issue #43 umsetzen.
- Quelladapter für Xtream, M3U und Stalker integrieren.
- M3U-Dateiimport und Playlist-Editor ergänzen.
- Selektiven Hintergrundimport fertigstellen.

Die Abhängigkeiten berücksichtigen und kleine, nachvollziehbare Änderungen bevorzugen.

Keinen ungeprüften Komplettumbau in einem einzigen großen Commit durchführen.

**Keinen Pull Request selbstständig mergen. Keine Version veröffentlichen, bevor Review und Android-Gerätetest erfolgt sind.**

## 13. Erwartetes Ergebnis

Liefere zunächst:

1. Technische Bestandsanalyse der bestehenden Module.
2. Architekturplan mit Wiederverwendung vorhandener Funktionen.
3. Geplante Änderungen pro Datei.
4. Abhängigkeits- und Prioritätsplan.
5. Gezielte Implementierung in separaten Branches und Pull Requests.
6. Automatisierte Tests und deren Ergebnisse.
7. Dokumentation der neuen Benutzeroberflächen.
8. Kompatibilitäts- und Datensicherheitsprüfung.
9. Anleitung für den Android-TV-Gerätetest.
10. GitHub-Links zu allen erstellten Pull Requests.

**VERBINDLICHE GESAMTVORGABE:**

XCMate soll aus einem IPTV-Add-on zu einer durchgängig bedienbaren, schnellen und persistenten Live-TV-, Film- und Serienoberfläche werden.

Der Benutzer wählt selbst, welche Inhalte übernommen werden. Einmal geladene Daten und Medienbilder bleiben lokal verfügbar. Neue Inhalte werden gezielt im Hintergrund ergänzt.

Die bisher funktionierende Fernbedienungsnavigation und sämtliche Benutzerdaten müssen erhalten bleiben.

**Beginne jetzt mit der Bestandsanalyse und anschließend der priorisierten Entwicklung. Keine eigenmächtigen Merges oder Releases.**