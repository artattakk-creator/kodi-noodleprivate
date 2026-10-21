# XCMate 0.1.29.4 – P0-Hotfix: Einrichtungsassistent, Gruppen-Checkboxen, Scan und Speichern

**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate`  
**Ausgangsversion:** 0.1.29.3, Draft-PR #52  
**Zielversion:** 0.1.29.4  
**Zielsystem:** Android-TV, Kodi 21.3 Omega, Titan BINGIE MOD / Estuary

## 1. Ausgangssituation

Version 0.1.29.3 wurde auf einer funktionierenden Android-TV-Box installiert und tatsächlich getestet.

Folgender Ablauf wurde beobachtet:

- Xtream-Account wird angenommen, Serververbindung und Kategorieerkennung funktionieren.
- Kategorien werden angezeigt, aber anstelle verständlicher Checkboxen erscheinen teilweise unlesbare Zeichen.
- Der aktuelle Fernbedienungsfokus ist kaum beziehungsweise nicht sichtbar.
- Es ist nicht erkennbar, welche Kategorie aktiviert oder deaktiviert ist.
- Ein Wechsel zu **Filme** beziehungsweise **Serien** ist mit der IR-Fernbedienung nicht zuverlässig möglich.
- Die Schaltflächen in der unteren Leiste lassen sich nur blind erreichen.
- Der Scan importierte offenbar rund 2.400 Sender und benötigte mehrere Minuten.
- Nach Auswahl von **Speichern** stürzte Kodi ab und musste vollständig neu gestartet werden.

Alle genannten Fehler sind vor der nächsten Freigabe zu beheben.

## 2. Bedienoberfläche vollständig korrigieren

Der Einrichtungsassistent soll drei eindeutig erkennbare, separat anwählbare Bereiche anbieten:

**Live-TV | Filme | Serien**

Jeder Bereich erhält eine eigene scrollbare Kategorienliste mit:

- Echten grafischen Checkboxen für aktiviert/deaktiviert – keine vom Schriftfont abhängigen Unicode-Platzhalter.
- Deutlich sichtbarem Fokusbalken über die gesamte Zeilenbreite, vorzugsweise türkis/blau mit hohem Kontrast.
- Separater visueller Kennzeichnung der aktivierten Kategorien, auch wenn der Fokus auf einer anderen Zeile liegt.
- Dauerhaft markiertem aktiven Bereichsreiter.
- Sichtbarem Auswahlzähler, zum Beispiel „12 von 43 Gruppen aktiviert“.
- Aktionen **Alle auswählen**, **Alle abwählen**, **Zurück**, **Weiter** und **Abbrechen**.

Die Navigation muss mit einer gewöhnlichen Android-IR-Fernbedienung funktionieren: Hoch/Runter für Listen, Links/Rechts für Bereiche und Bedienelemente, OK zum Umschalten einer Checkbox.

Beim Umschalten darf die Liste nicht unnötig vollständig zurückgesetzt werden. Die bisherige Fokus- und Scrollposition bleibt erhalten.

Die Auswahl für Live-TV, Filme und Serien muss getrennt gespeichert werden. Kein automatisches Einschalten abgewählter Gruppen.

Leere Bereiche müssen ausdrücklich „Keine Kategorien vorhanden“ anzeigen und weiterhin navigierbar sein.

Dateien insbesondere prüfen: `setup_window.py`, `XCMateSetup.xml`, zugehörige Kodi-Controls, Grafiken und Sprachdateien.

## 3. Scan ohne globale Laufzeitbegrenzung

Ein vollständig laufender Import darf **nicht wegen einer festen Gesamtzeit von beispielsweise 300 Sekunden abgebrochen werden**.

Prüfen und entsprechend überarbeiten:

- `utils.py` – `http_stream()` mit bisherigem `max_seconds=300`
- `source_adapters.py` – Stalker-Paginierung mit bisheriger 300-Sekunden-Deadline
- weitere Scan-/Katalogfunktionen auf feste Gesamtlaufzeitlimits

Es soll kein globales Zeitlimit für den vollständigen Katalogscan geben.

**Wichtig:** Verbindungsaufbau-, Lese-Inaktivitäts- und Sicherheits-Timeouts müssen erhalten bleiben, damit defekte Server, Endlosschleifen und festhängende Verbindungen das Gerät nicht dauerhaft blockieren. Solange tatsächlich Fortschritt erfolgt, muss der Import weiterlaufen können.

Ein Scan von 5, 10, 20 oder mehr Minuten muss grundsätzlich möglich sein.

Fortschritt laufend anzeigen: aktueller Bereich, aktuelle Gruppe, eingelesene Elemente und tatsächlich gespeicherte Elemente. Kein vorgetäuschter Prozentfortschritt.

Der Scan bleibt kontrolliert abbrechbar. Speicher- und Datenmengenverarbeitung müssen auch für große Anbieterlisten geeignet sein.

## 4. Absturz beim Speichern untersuchen und beheben

**Höchste technische Priorität.**

Untersuche speziell `WorkWindow.work()`, `ThreadPoolExecutor`, `Future.add_done_callback()`, `SetupWindow.saved()`, `WindowXML.close()` sowie `Draft.save()`.

Prüfe, ob Kodi-GUI-Control-Updates, Dialog-Schließungen oder andere WindowXML-Operationen aus einem Worker-Thread stattfinden. Diese müssen über einen Kodi-kompatiblen, nachweislich sicheren Übergang zur GUI-Verarbeitung ausgeführt werden.

Außerdem untersuchen:

- SQLite-Verbindungen und Transaktionsgrenzen
- Profil-Schreiblocks und mögliche Deadlocks
- Fehlerbehandlung beim Kopieren von Daten zwischen Staging- und Produktivdatenbanken
- atomare Veröffentlichung der neuen Portalkonfiguration
- Wiederverwendung oder mehrfachen Aufruf des Speicherns
- Ressourcenfreigabe und Worker-Lebenszyklus

Ein Fehler darf weder Kodi zum Absturz bringen noch bestehende Accounts beschädigen.

## 5. Speicherroutine verifizieren

Nach dem Speichern müssen folgende Daten durch erneutes Einlesen aus dem permanenten Profil überprüft werden:

- Account-ID, Portaltyp und Account-Konfiguration
- ausgewählte Live-TV-, Film- und Seriengruppen
- tatsächlich gespeicherte Sender-, Film- und Serienanzahlen
- Datenbankintegrität und Zuordnung zum neuen Account
- optionale EPG-Einstellungen

Erfolg erst melden, wenn die entscheidenden Daten nachweislich persistent vorhanden sind.

Nach erfolgreicher Speicherung muss der Account nach vollständigem Kodi-Neustart weiterhin verfügbar sein.

Bei einem Fehler: Verständliche Fehlermeldung und Fehlercode statt Absturz. Bestehende Accounts und Einstellungen unangetastet lassen. Teilweise fehlgeschlagene neue Importe dürfen keinen scheinbar vollständig gespeicherten Account erzeugen.

Keine Zugangsdaten, Tokens oder vollständigen Stream-URLs in Logs schreiben.

## 6. Verbindliche Regressionstests

Automatisierte Tests mindestens für:

1. Sichtbaren Fernbedienungsfokus und tatsächlichen grafischen Checkbox-Zustand.
2. Wechsel zwischen Live-TV, Filme und Serien, einschließlich Rückwechsel.
3. Auswahl, Deaktivierung und Erhalt der Scrollposition.
4. Lange laufende Scans mit simulierter Dauer über 300 Sekunden und fortlaufendem Fortschritt.
5. Fehlerhafte beziehungsweise nicht reagierende Provider und sauberen Benutzerabbruch.
6. Import von mindestens 2.400 Sendern plus separaten Film-/Serienkategorien.
7. Speicherung, Readback-Prüfung und simulierten Kodi-Neustart.
8. Fehlgeschlagene Speichervorgänge mit Rollback ausschließlich für den neuen Account.
9. Thread-sichere GUI-Verarbeitung; keine GUI-Manipulation oder WindowXML-Schließung aus Worker-Threads.
10. Erhalt aller eingefrorenen Live-TV-Fernbedienungsfunktionen.

Die bisher funktionierende Live-TV-Overlay-Navigation, Startsenderlogik, EPG-Bestandsdaten, Favoriten, TMDb Helper, xVAULT und Titan BINGIE MOD dürfen nicht verändert oder beeinträchtigt werden.

## 7. Lieferung

- Neue vollständige Version **XCMate 0.1.29.4** erstellen.
- Separaten Entwicklungsbranch und Draft-PR verwenden.
- Änderungen dokumentieren und sämtliche automatisierten Tests ausführen.
- Vollständiges Kodi-Installationspaket `plugin.video.xtreammate-0.1.29.4.zip` erstellen, CRC, Paketstruktur und SHA-256 überprüfen.
- ZIP als manuell installierbare Testversion für unsere GS-Media-/Neo-Dark-Onlinequelle vorbereiten.
- Keine eigenmächtige Veröffentlichung als automatisches Repository-Update und kein Merge nach `main`.
- Bestehende Version 0.1.29.3 als Vergleichsversion erhalten.
- Echte Android-/IR-Fernbedienungsprüfung als offene Abnahme ausweisen, nicht durch erfolgreiche Mock-Tests ersetzen.

**Erwartetes Ergebnis:** Der Anwender kann einen Xtream-Account vollständig einrichten, sichtbar getrennt TV-/Film-/Seriengruppen per Checkbox auswählen, auch große Kataloge vollständig importieren, den Account fehlerfrei speichern und nach einem Kodi-Neustart wiederverwenden.

Bitte zunächst die konkreten Root Causes ermitteln und dokumentieren, dann alle Korrekturen implementieren und einen vollständigen Testbericht sowie die neue installierbare ZIP liefern.