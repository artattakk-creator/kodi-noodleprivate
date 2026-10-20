# Android-Abnahme 0.1.29.2 – alle Gerätefälle noch OFFEN

Ziel: Kodi **21.3 / Omega**, Android-TV **ARM32**, RK3528; Tests jeweils unter
**Titan BINGIE MOD und Estuary**. Cloud-Callbackmodelle ersetzen diesen Nachweis nicht.
Produktiv bleibt 0.1.28. Kein Main-Merge/Repository-Update vor Review und Freigabe.

## Geprüfte Installationsdatei und Sicherung

[Test-ZIP 0.1.29.2](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip)
([SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.2.zip.sha256)),
119 Dateien / **373.616 Bytes**, SHA256:
`cb4727741fdfcae641a147437bf36ed0b90f9c61e6b2637db218516334742642`.

1. Kodi vollständig beenden. Vollständiges bestehendes XCMate-Profil einschließlich
   aller SQLite-/WAL-Dateien und gewähltem Bild-/Cacheordner lokal sichern. Nicht nur
   `portals.json`; auch Gruppen, EPG-Quellen/Zuordnungen, Fortschritt/Favoriten und Bilder.
2. ZIP aus dem Entwicklungsbranch als Datei herunterladen; in GitHub ggf. **Download
   raw file** verwenden. Prüfsumme vergleichen. Der produktive Repositoryindex zeigt
   weiterhin 0.1.28 und ist für diesen Test kein automatischer Installationsweg.
3. In Kodi **Add-ons → Aus ZIP-Datei installieren**: Kandidat über dieselbe ID
   `plugin.video.xtreammate` installieren. Keine Deinstallation und kein Profillöschen.
4. Version im Add-on prüfen, Kodi neu starten, bestehende Accounts/Gruppen/Quellen,
   Favoriten und Resume mit Sicherungsbestand vergleichen. Noodle/andere Add-ons testen.

## A – Start und eigener Wiedergabestopp (#38/#40)

- Zehn Kaltstarts, zehn Warmstarts und Öffnen parallel zu BINGIE-Widgets. Bei Hänger
  Uhrzeit, letzte sichtbare Oberfläche und Kodi-/XCMate-Diagnose sichern, bevor Kodi
  beendet wird. Ursprüngliche Ursache #38 ist weiterhin unbewiesen; kein Cachelöschen
  als notwendige Voraussetzung für jeden Start akzeptieren.
- Film und echte Serienfolge mindestens zwei Minuten abspielen, dann explizit zur
  XCMate-/Kodi-Navigation zurück: **Bild und Ton stoppen**. Wiederaufnahme muss den
  letzten Punkt zeigen. Schnelles/mehrfaches Back direkt beim Start ebenfalls prüfen.
- Live-TV: erstes OK Info, zweites OK/Runter Controls, Links Sender, zweites Links
  Gruppen, Menü Checkboxverwaltung. Overlay-Back schließt nur eine Ebene; erst
  tatsächliches Verlassen des Vollbilds beendet die eigene Sitzung.
- Ton/Untertitel/Bildeinstellungen öffnen: kein ungewollter Stop. Fremden Kodi-
  Stream starten, XCMate öffnen/schließen: kein fremdes Play/Stop/Fokusübernehmen.
- Diagnose nach Stop und nach Kodi-Neustart erneut öffnen: letzte Session-/Ownership-/
  Fokus-/Fehlerdaten müssen nachvollziehbar bleiben, ohne vollständige Zugangsdaten.

## B – Bilder, Rails und Fortschritt (#41/#44)

- Mehr als 64 unterschiedliche Film-/Serienbilder anzeigen, danach Home/Filme/Serien
  mehrfach wechseln und Kodi neu starten: einmal gültig gespeicherte Bilder bleiben.
  Offline dieselben Kacheln öffnen: keine erneuten notwendigen Downloads.
- Bei langsamer Verbindung fokussiertes Cover, sichtbare nicht fokussierte Kacheln,
  Detailposter und Fanart beobachten: progressive Aktualisierung ohne Schließen.
- Budget ändern, Status und explizite Wiederholung fehlgeschlagener Downloads prüfen.
  Budget erreicht: Status statt stiller Eviction; vorhandene Bilder bleiben.
- Alle drei Rails mit IR-Links/Rechts/Hoch/Runter/OK erreichen. Leere Rails dürfen
  keinen unsichtbaren Fokus festhalten. Favorit hinzufügen/entfernen: sofortige Änderung.
- „Weiter ansehen“ aus echten Fortschrittsdaten; beendete Titel verschwinden dort,
  bleiben aber Favorit. Zwei Accounts mit gleicher Medien-ID dürfen sich nicht mischen.
- Staffeln/Folgen: Gesehen/Ungesehen manuell, Prozent, nächster ungesehener Titel,
  Resume und Kodi-Neustart. Vorhandene Resume-Daten dürfen nicht zurückgesetzt werden.

## C – Gruppen und kontinuierliche Sender (#37/#42)

- Deaktivierte Gruppen fehlen in normaler Liste, keine AN/AUS-Zeilen. Menü zeigt alle
  verfügbaren Gruppen mit Checkboxen. Speichern/Abbrechen und null aktive Gruppen testen.
- Gruppe mit >100 und nach Möglichkeit >1000 Sendern: über Positionen 99/100/101 und
  999/1000 vor/zurück scrollen, OK muss exakt den markierten Sender spielen. Keine
  sichtbaren Folgeseiten; Kontext/Back und bestehendes Vollbild-Zappen prüfen.
- Erneut aktivierte Gruppen ohne lokalen Katalog: Import im Hintergrund, Navigator
  übernimmt abgeschlossene Daten; keine automatische Aktivierung neuer Länder.
- Schnelle Tastensequenzen und gehaltene IR-Tasten: weder doppelte noch verlorene
  bestätigte Einzelschritte. Keine globalen Keymaps zur Problemlösung aktivieren.

## D – vier Quellenarten, Assistent und Editor (#43)

Jeweils mit eigenen gültigen Zugangsdaten durchführen:

| Quelle | Verbindung/Erkennung | Selektiver Import | Wiedergabe/Metadaten |
|---|---|---|---|
| Xtream | Server inkl. Port, User/Pass; erst Kategorien | Nur gewählte Gruppen, keine vollständigen Film-/Seriendownloads vor Weiter | Live/VOD/echte Folgen, Header/EPG |
| HTTP-M3U/M3U8 | URL inkl. legitimer Queryparameter; keine automatische Xtream-Konvertierung | Große Playlist wird analysiert, nur Auswahl in Medienindex | Live/VOD; reine Serienlinks als einzelne Einträge |
| Datei/USB/SMB/NAS | Native Kodi-Dateiauswahl und Berechtigungen | Private Kopie, manuelle Zuordnung unklarer Gruppen | Playlistquelle entfernen: HTTP-Medien bleiben abspielbar; entfernte Mediendateien naturgemäß nicht |
| Stalker/MAG | Portal/MAC, ggf. explizite Serien-/Geräte-ID; Providerdialekt dokumentieren | Kategorien zuerst, mehr als 50 Seiten wenn verfügbar | create_link, benötigte Header, echte Staffel-/Folgenfelder; ehrlicher Hinweis bei fehlender Fähigkeit |

Für jede Quelle:

1. Vor Weiter sind keine Gruppen/Feeds vorausgewählt. Auswahl Live/Film/Serie,
   Alle/Keine, einzelne Checkboxen, Menü-Medienart bei M3U. **Weiter rechts unten**
   über IR-Fokus erreichbar. Quellenname und eingegebene Parameter korrekt erhalten.
2. Scan abbrechen und Assistent schließen: kein neuer produktiver Account, alle
   vorhandenen Konten unverändert. Langsamer/ausgefallener Provider: Fenster bleibt
   bedienbar, keine erfundenen bestätigten Zähler.
3. Zusammenfassung/Zurück/Speichern prüfen. Nach Save Home unmittelbar nutzbar;
   Bilder/weitere Metadaten dürfen nachladen. Wiederstart nutzt lokalen Index.
4. Nur gewünschte DE-/AT-/eigene EPG-Feeds aktivieren. Ohne Auswahl kein Download.
   Nach erfolgreichem Import Neustart/offline: Guide und Jetzt/Danach vorhanden.
   Feedfehler/ungültiger Zeitstempel: letzte gültige Daten und manuelle Zuordnung bleiben.
5. Nach Ablauf des kleinen Snapshots weiterhin gültige Programme aus SQLite zeigen.
   Fullscreen-Navigation während EPG-Download, Senderwechsel ohne Netzwerkwarten.
6. Gruppen ändern: deaktivierte Inhalte verschwinden, Favoriten/Resume bleiben.
   Bestehende alte Nicht-Xtream-Accounts benötigen im neuen Index explizite Auswahl;
   ihre Legacy-Daten werden nicht gelöscht.

M3U-Editor gesondert: Suche, Gruppen erstellen/umbenennen/Medienart, Sender verschieben,
Name/Logo-URL/EPG-ID, Aktivstatus, Reihenfolge, Hinzufügen/Entfernen, Duplikate.
Remote-Playlist aktualisieren und lokale Overrides erneut prüfen. Export als M3U8 in
neue Datei, Wiederimport und Metadatenvergleich; bestätigtes Überschreiben nur eines
Exports, Original und interne Arbeitskopie müssen geschützt bleiben. USB-/SMB-Rename
und tatsächliche Dateiberechtigungen am Gerät prüfen. Kein ungeschützter Uploadserver.

## Nachweise und Rückmeldung

Pro Fall Version, Skin, Quellentyp, Aktion, erwartetes/tatsächliches Ergebnis, Uhrzeit
und Diagnosecode festhalten. Erst Bild/Ton, dann Eingaben/Fokus, danach Performance
bewerten. Cloud-Messzeiten sind keine Zusage für die Android-Box. Zugangsdaten/Playlist-
URLs nicht ungeschützt in Issues/PRs einfügen. Anbieterbesonderheiten anonymisiert melden.

## Regulärer Updateweg – erst nach ausdrücklicher Freigabe

1. Review/Android-Abnahme der ZIP und aller vier Phasen; Startup-Hotfix #39 separat
   berücksichtigen. Gestapelte Reihenfolge: **#39 → #45 → #46 → #47 → #48**.
2. Nach Übernahme einer Basis den jeweils nächsten PR auf `main` umstellen, Diff
   prüfen und Tests für den resultierenden Stand erneut ausführen. Keine ungeprüfte
   automatische Kettenübernahme, kein Main-Push durch diesen Entwicklungsauftrag.
3. Erst nach Freigabe mit dem vorhandenen offiziellen Repository-Builder die
   freigegebene Version in einer isolierten Kopie bauen; ZIP, Metadaten, Checksummen
   und XCMate-Eintrag im Kodi-Index prüfen. Unverwandte Add-ons/ZIPs nicht übernehmen.
   Regulären Main-Workflow nur im freigegebenen Releasevorgang auslösen.
4. Kodi „Auf Aktualisierungen prüfen“ / „Aus Repository aktualisieren“, gleiche Add-on-ID.
   Danach bestehendes Profil und Version erneut prüfen. Kein Neuaccount-/Resetzwang.

Rollback vor Freigabe: Kodi beenden, unveränderte veröffentlichte 0.1.28-ZIP wieder
über dieselbe ID installieren; Profil nicht löschen. Für eine vollständige Rückkehr
zur alten Datensicht die zuvor erstellte **vollständige** Sicherung bei beendetem Kodi
wiederherstellen. Neue Quelladapter-Accounts sind in alter Version nicht vollständig
bedienbar; deshalb vor breitem produktivem Einsatz abnehmen. Keine automatische
irreversible Datenmigration wurde eingeführt.
