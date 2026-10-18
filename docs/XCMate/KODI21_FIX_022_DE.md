# XCMate 0.1.22 – Testkandidat für Kodi 21 / Android TV

Stand: 18.10.2026. Branch: `fix/xcmate-kodi21-overlay-epg`.
Ausgangsstand: `391388368637fc98eddcf5b123d445a6515a7efc` (0.1.21).
Keine Produktionsveröffentlichung; Android-TV-Abnahme steht aus.

## Behobene Ursachen

- `LiveNavigator` ist ein programmatischer `WindowDialog`. Kodi Omega ruft für
  diesen Dialog kein Python-`onInit()` auf. Die Controls entstehen jetzt einmalig
  vor `show()`, der Fokus wird nach dem Anzeigen gesetzt. Fehler schließen auch
  teilweise aufgebaute Fenster. Erneutes Anzeigen dupliziert keine Controls.
- Programmatische Controls melden Klicks über `onControl(Control)`, nicht über
  `onClick(control_id)`. Native Controls verarbeiten ihre Aktion vor dem
  Python-`onAction`-Callback. Native Listenbewegung wird deshalb nicht nochmals
  angewandt; OK wird ausschließlich im Klick-Callback ausgeführt. Angelernte
  alternative OK-Actions und die optionale Bridge bleiben getrennt bedienbar.
  Ein zeitliches Debounce verschluckt keine schnellen, separaten OK-Tastendrücke.
- Eigene graue Normal-/Fokustexturen für Liste und Buttons vermeiden die
  Abhängigkeit von skinspezifischen Fokusgrafiken. Zeilenhöhe und Abstand werden
  im Konstruktor gesetzt; die nachträglichen Setter sind in Omega wirkungslos.
- Dienst und Eingabecallbacks prüfen die laufende URL gegen die konfigurierten
  Xtream-Live-Adressen. Fremde Wiedergabe schließt den Dialog; Stop und Shutdown
  räumen Befehle und den zugehörigen Sitzungsmarker auf. Ein bereits neuer Marker
  eines anderen Portals wird nicht gelöscht. Beim Senderwechsel wird die alte,
  verifizierte Live-Adresse höchstens acht Sekunden toleriert, weil Player.play
  asynchron arbeitet. Die globale Keymap bleibt ausdrücklich opt-in.
- Ein vorhandener Cache-Ordner wird durch einen eindeutig benannten, sofort
  entfernten Schreibtest geprüft (Ergebnis höchstens 30 Sekunden gecacht).
  Entzogene Berechtigungen oder `File.write() == False` führen zum privaten
  Cache; ein Schreibfehler nach erfolgreichem Probezugriff wird dort wiederholt.
  Die gespeicherte Ordnerwahl sowie Konten, EPG-Quellen und Mappings bleiben erhalten.
- Ungültiges Datum, ungültige Zeitzone, fehlender Zeitstempel und umgekehrtes
  Sendungsintervall betreffen nur den jeweiligen Programmeintrag. Die Diagnose
  nennt die Anzahl ausgelassener Einträge, keine Zugangsdaten oder Quell-URLs.
- HTTP-Lesen, HTTP-GZIP und XMLTV-GZIP sind begrenzt. XMLTV-GZIP wird während
  `iterparse` entpackt, statt vorab eine komplette zweite XML-Kopie zu erzeugen.
  Die manuelle EPG-Aktualisierung schließt die Verzeichnisanfrage und startet
  einen Hintergrundworker. Die Sendergruppen im Player verwenden den geladenen
  Katalog; beim Tastendruck startet kein Kategorien-Download.

API-Belege aus dem offiziellen Omega-Quellcode:

- https://github.com/xbmc/xbmc/blob/Omega/xbmc/interfaces/legacy/WindowDialog.cpp
- https://github.com/xbmc/xbmc/blob/Omega/xbmc/interfaces/legacy/Window.cpp
- https://github.com/xbmc/xbmc/blob/Omega/xbmc/interfaces/legacy/Control.cpp
- https://github.com/xbmc/xbmc/blob/Omega/xbmc/interfaces/legacy/Control.h

## Ressourcenbudgets und Grenzen

Pro HTTP-Antwort höchstens 80 MiB sowohl empfangene als auch HTTP-entpackte
Daten; ein Gesamtzeitbudget von 60 Sekunden umfasst die Wiederholungen. Ein
einzelner Socket-Lesevorgang bleibt zusätzlich durch den Request-Timeout begrenzt.
Native und externe XMLTV-Dateien dürfen nach GZIP-Dekomprimierung ebenfalls
höchstens 80 MiB umfassen. XML-Verarbeitung: höchstens 60 Sekunden, 10.000 Sender
und 150.000 Programme; die zusammengeführten Quellen teilen das Programmbudget.
Sendungstitel werden auf 512, Beschreibungen auf 4.096 Zeichen begrenzt.
Überschreitungen lehnen die Quelle ab, statt weitere Daten zu allokieren.
Der letzte funktionierende Portalguide bleibt bei einer vollständig fehlgeschlagenen
Aktualisierung erhalten. Diese Grenzen sind kein Nachweis einer bestimmten
Speicherspitze auf dem Fernseher.

Einzelne EPG-Refreshes werden pro Python-Prozess serialisiert. Der STB-Short-EPG-
Fallback verwendet höchstens vier parallele Anfragen, 10.000 Sender und startet
nach Ablauf seines 60-Sekunden-Budgets keine weiteren Senderanfragen. Bereits
laufende Anfragen können noch bis zu ihrem Request-Timeout weiterlaufen.

## Lokale Prüfung

- Gesamtsuite: **180 Tests erfolgreich, keine Fehler oder übersprungenen Tests**.
- 14 Kodi-Omega-Lebenszyklus-/Eingabe-/Diensttests: `show()` löst im Modell
  ausdrücklich kein `onInit()` aus; native Listenbewegung und Klick kommen vor
  `onAction`. Auch der ursprüngliche 0.1.21-Code wurde gegen den neuen
  Initialisierungstest geprüft: Er scheitert erwartungsgemäß am fehlenden Aufbau.
- 15 neue Cache-/EPG-/HTTP-Prüfungen: echte Schreib-/Lesevorgänge mit simulierten
  VFS-Berechtigungsfehlern, gemischte gültige/ungültige Programme, GZIP-Expansion,
  Größen-/Zeit-/Sender-/Programmgrenzen, Mappings nach Modulneustart sowie
  tatsächliche Requests an einen lokalen Testserver. Die HTTP-Prüfungen wurden
  zusätzlich mit installiertem httpx über beide Backends ausgeführt.
- Paketbau und Python-Kompilierung erfolgen in einer Arbeitskopie außerhalb des
  Checkouts. Paketinhalt, Versionsmanifest und Prüfsumme werden gesondert geprüft.
- Noodle Private und andere Add-ons werden nicht verändert. Der Produktivindex
  bleibt auf dem Ausgangsstand; nur die Kandidaten-ZIP wird auf diesem Branch ergänzt.

Die Tests simulieren die Kodi-API; sie sind kein gestartetes Kodi und kein
Nachweis funktionierender Android-Events oder BINGIE-MOD-Darstellung.

## Installationsdatei und Android-Abnahme

Kandidat: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.22.zip`.
SHA-256 liegt daneben in `.zip.sha256`. Nicht das Repository-Installer-ZIP
verwenden. Vorher das bestehende Kodi-Profil lokal sichern. XCMate nicht
deinstallieren und keine Profildaten löschen. Die globale Fallback-Keymap für
den ersten Test ausgeschaltet lassen.

1. Kandidaten-ZIP über Kodi → Add-ons → Aus ZIP-Datei installieren einspielen.
   In den Add-on-Informationen **0.1.22** prüfen; Kodi vollständig neu starten.
2. BINGIE-MOD-Startseite, einen Film aus einem anderen Add-on, XCMate-Hauptmenü,
   Einstellungen und EPG-Verwaltung jeweils öffnen und schließen. Kein endloser
   Ladeindikator; bestehende Konten und manuelle EPG-Zuordnungen sind vorhanden.
3. Einen XCMate-Xtream-Live-Sender starten. Die Senderliste muss sichtbar sein;
   Hoch/Runter bewegt den Fokus um genau eine Zeile. Links öffnet Gruppen,
   Rechts führt zurück zur Senderliste bzw. zum Live-TV. OK startet genau den
   markierten Sender. Senderwechsel kann wenige Sekunden benötigen.
4. Bei verborgenem Menü: Links öffnet Sender; Hoch/Runter schaltet Sender.
   OK öffnet die Player-Leiste; Links/Rechts/Hoch/Runter bewegt dort den sichtbaren
   Fokus. Ein weiteres OK führt genau eine Aktion aus. Schnelle getrennte
   OK-Tastendrücke prüfen. Menü öffnet Zusatzfunktionen; in der Gruppenliste
   schaltet Menü die markierte Gruppe ein/aus. Zurück geht die Navigation zurück.
5. EPG-Taste/Anlernfunktion prüfen; fehlende EPG-Daten starten einen Hintergrund-
   abruf, während die Fernbedienung bedienbar bleibt. Langdruck separat prüfen,
   soweit Kodi und die Fernbedienung entsprechende Actions liefern.
6. Stop drücken: Wiedergabe und Dialog enden. Danach einen Film aus einem anderen
   Add-on starten; dessen Steuerung muss normal funktionieren. Auch direkt von
   Live-TV zu fremder Wiedergabe wechseln: XCMate muss den Dialog freigeben.
7. Cache-Ordner auswählen und Kodi neu starten. Schreibbarkeit anschließend
   entziehen oder den Datenträger entfernen: interner Cache muss übernehmen,
   Favoriten/Konten/Quellen/Mappings bleiben erhalten. Keine fremden Dateien löschen.
8. Bestehende XMLTV-Quellen einzeln aktualisieren. Währenddessen weiter navigieren;
   Offline/unerreichbare Quelle testen. Sky-/RTLup-Zuordnung kontrollieren und eine
   manuelle Zuordnung nach Neustart überprüfen. Große Feeds können an den
   dokumentierten Budgets abgewiesen werden.

Offen bis zur Geräteabnahme: tatsächliche Fokusdarstellung auf BINGIE MOD,
Android-Action-IDs und Langdruck, Fokus konkurrierender Kodi-Dialoge, reale
Provider-Weiterleitungen und Senderwechsel, Speicherverbrauch auf dem TV sowie
die Ursache des früheren Kodi-weiten Hängers. Bei Fehlern Zeitpunkt, Kodi-Version,
Fernbedienungsaktion und anonymisierten Logausschnitt festhalten; keine kompletten
Stream-/EPG-URLs mit Zugangsdaten teilen.
