# XCMate 0.1.29.53 – Ursachen und Umsetzung

## Basis und Grenzen

Kumulative Basis: main .52, `e17c2b2311481fa83f6f9f8ee560837eb369ce6e`. Eigener Branch `feat/xcmate-02953-epg-wizard`; Master #259 und vollständiger .53-Nutzerauftrag. Die .52-Implementierung für sieben lokale Kalendertage Vergangenheit, bis einschließlich Tag +20, quellensichere Ergänzung, LastGood und Serien-Nachimport bleibt erhalten. Kein konkurrierender EPG-Datenspeicher. Keine Änderungen an Player, Keymaps, Geräten, fremden Skins oder bestehenden Bilddateien.

## A: EPG-Manager, Bericht und Aktualisierung

Bisher verteilte Quellenverwaltung, Guide-Zuordnung und Importstatus unter einer Oberfläche zusammengeführt. `epg_manager53` verwendet die vorhandenen Quelleneinträge, Presets und Importjobs. Anzeige: Aktivierung/Priorität, bestätigte Erfolge/Fehler, reale gespeicherte Sender-/Programmzahlen und Zeitraum. Statistik liest die bestehenden `programmes`/`guide44_inputs` im Read-only-Snapshot; Zahlen betreffen den veröffentlichten Masterimport, nicht jede Providerzeile oder Kodi-Kurzzeitvorschau. Kurzfristig erst im gemeinsamen Faktenindex gespeicherte manuelle Kandidaten werden beim nächsten regulären Masterimport in diesen Masterzahlen erfasst.

`epg_report53` beobachtet den bestehenden Import und erfasst Quellergebnisse erst nach dessen Veröffentlichung. Bis 16 Berichte / 1 MiB pro Portal, atomar/private temporäre Datei, keine URLs, Sendungstexte oder Zugangsdaten. Lesbare deutsche Übersicht statt JSON/SQL/Tracebacks. Eine Jobanforderung wird ausdrücklich nicht als erfolgreicher Download dargestellt. Bei SQL-Zeitbudget oder unlesbarem Altbestand „nicht sicher lesbar“, kein erfundener Nullbestand. Fehler beim Bericht dürfen einen erfolgreichen EPG-Import nicht nachträglich scheitern lassen.

Früherer Standard 12 h wird im Setting und Cache-Fallback auf 24 h vereinheitlicht, ohne explizite Werte zu überschreiben. Service plant nach tatsächlicher letzter Aktualisierung statt bloßer Zukunftsabdeckung; bestehendes LastGood dient beim Neustart als Altersanker. Fehlgeschlagene Quellen allein nach 15 Minuten / 1 Stunde erneut, höchstens drei Versuche innerhalb des normalen Intervalls. Erfolgreiche Quellen werden dabei nicht erneut geladen. Backup-/Import-/Katalogsperren bleiben erhalten; manuelle Anforderung weiterhin jederzeit möglich, tatsächliche Ausführung respektiert diese Schutzbarrieren.

## A: echte Vorschau im ursprünglichen Raster

Der vorhandene kurze OK-Senderkontext bleibt erhalten. `guide_mapping48` zeigt ein schmales rechtes Zuordnungsfenster; nach der Kandidatenwahl bleibt es sichtbar und bedienbar. Die ursprüngliche Guide-Instanz erhält nur die betreffende Senderzeile, ohne neue Fenster-/Directory-Übergabe. Uhrzeiten und Beschreibung sind scrollbar, weitere Zeiträume und vorige/nächste Kanalseiten verfügbar. Kein automatischer Playerstart. Der dichte Raster-Autopan bleibt während der Vorschau gesperrt.

Abbruch restauriert Originalzeilen, Gruppen, Senderfokus, Zeilen-/Seitenposition, Ursprung, Cursor, Kategorie und Kopfzeile. Späte Worker-Ergebnisse nach dem Schließen werden nicht angewendet. Vorschau nutzt RAM-Mappings aus stabiler Quell-ID + XMLTV-Kanal-ID; keine Konfigurations-/DB-Schreiboperation. Eine neue Quellpriorität oder globale Aliasänderung entsteht dadurch nicht.

Zusätzlicher nachgewiesener Randfall: Der vorhandene Import speichert Sendungen nur für passende aktive Sender, während sein Namenskatalog weitere XMLTV-Kanäle enthält. Bei einem bislang ungemappten Kandidaten konnten deshalb Name/ID vorhanden, die lokale Sendungsliste aber leer sein. `epg_candidate53` liest bei ausdrücklicher Auswahl fehlende Katalog-/Programmdaten über den vorhandenen Streaming-Transport und SAX-Parser begrenzt in RAM. Kein Netzwerk auf gewöhnlichem Guide-Fokus. Ganzer XML-/gzip-Abschluss muss gültig sein; Abbruch, beschädigte Dateien, DTD/Entities oder Ressourcenlimit verwerfen den RAM-Versuch vollständig. Keine ganze XML-DOM-Struktur.

Grenzen: ein Quellkatalog und ein Kandidat je Dialog; maximal 20.000 Kanalnamen / 4 MiB, maximal 512 Programme / 4 MiB für genau eine Quell-/Kanal-ID, 64 MiB komprimierte und 256 MiB dekodierte Eingabe, Parserdeadline 45 s zusätzlich zu bestehenden Transporttimeouts. Sehr große ALL_SOURCES1-Feeds können deshalb ausdrücklich blockiert werden; keine unbeschränkte ARM32-Anreicherung und kein falscher Erfolg. Lokale Kandidaten sind davon unabhängig. Eine reale Erstanforderung kann bis zur Daten-/Netzwerkgrenze dauern; Android-Latenz ist nicht gemessen.

Erst explizites Speichern veröffentlicht solche ausgewählten RAM-Fakten additiv im bereits vorhandenen gemeinsamen Fakten-/Metadatenindex und liest die exakte Quell-/Kanal-/Zeit-/Titelidentität zurück. Danach wird genau die gewählte Senderbindung atomar gespeichert. Bei Schreib-/Verifikationsfehler keine erfolgreiche Bindung; bereits autorisiert geschriebene gültige Fakten dürfen erhalten bleiben. Während dieser kleinen Save-Transaktion verhindert die vorhandene Rückkehrbarriere einen verspäteten Commit nach Abbruch. Lokale bereits gespeicherte Kandidaten benötigen weiterhin nur den kleinen Konfigurationsschreibvorgang. Raster, Mini-EPG, Infobar und Home verwenden anschließend denselben quellensicheren Resolver.

Automatische Namensbeweise unterscheiden zusätzlich ausdrücklich bekannte SD/HD/UHD-, +1- und Länderabweichungen. Unklare Zuordnungen werden nicht geraten; eine ausdrückliche manuelle Auswahl bleibt möglich. WELT und Comedy Central DE werden mit kollidierenden Quellen und Varianten synthetisch geprüft.

## B: Wizard und Passwort

Vorher brach die Einrichtung bei Fehlern/Back ab und räumte ihren nur temporären Arbeitsstand auf. Bestätigte Eingaben und Gruppenauswahl hatten keinen fortsetzbaren Lebenszyklus. Jetzt speichert `wizard_resume53` nichtgeheime Eingaben, Auswahl, abgeschlossene Phase und überprüfbare Staging-Referenz in einem privaten Entwurf. Ordner 0700 / Dateien 0600, Symlink-/Besitzprüfung, Größenlimits und explizite Verwerfensbestätigung. Keine Änderung bestehender Portal-IDs und keine allgemeine Profilbereinigung.

Das Passwort bleibt im RAM derselben laufenden Einrichtung bei Back, Retry und erneuter Eingabe verfügbar. Neu manuell eingegebene Passwörter sind standardmäßig zunächst sichtbar, optional verdeckt; bereits gespeicherte Geheimnisse werden weder unmaskiert angezeigt noch als Textvorbelegung in Kodi-Eingabedialoge gegeben. Zusammenfassungen und Fehler enthalten keine Passwörter.

Es wird ausdrücklich kein Passwort in den Restart-Entwurf serialisiert. Nach Kodi-Neustart werden Server/Benutzer/Gruppen/geeigneter Scan wiederhergestellt; nur ein ungespeichertes Passwort muss neu eingegeben werden. Eine unterstützte geschützte plattformweite Geheimnisablage wurde nicht nachgewiesen. Bereits regulär gespeicherte Portale bleiben unverändert. Credential-haltige M3U-URLs werden ebenfalls nicht komplett abgelegt; dann ist erneute URL-Eingabe nötig.

`wizard_flow53` bietet Retry, Back, Später und bestätigtes Verwerfen. Der vorhandene .51-Worker-Lease wird vor dem Bearbeiten geprüft, verhindert parallele Fortsetzungen und bleibt bei langsam auslaufender Arbeit wirksam. Nur gültige aktuelle Staging-Signaturen werden wiederverwendet; geänderter Anbieter, beschädigter oder alter Scan erfordern neue Prüfung, ohne die Auswahl stillschweigend zu löschen. Ein Absturz nach bereits erfolgter Portalveröffentlichung erzeugt beim Fortsetzen kein zweites Portal. Speicherfehler geben offen an, wenn nur RAM-Erhalt möglich ist. Neutrale Wizard-Buttons bleiben erhalten.

Zusätzliche Integrationskorrektur: Die .52-Tabelle `source_aliases52` fehlte bisher in der Wizard-Promotion. Sie wird für ausschließlich die neue Portal-ID mitkopiert und exakt nachgelesen; alte Portalzeilen bleiben unberührt.

## C: bestehende BINGIE-Integration und Grenze der Freigabe

Die .50-Widgetverwaltung, drei direkte Widgetaktionen, Home-Datenquelle, Reload-Brücke und optionaler Skinadapter bleiben byteidentisch. Neue Tests prüfen vollständige 88-Sender-Startgruppe ohne fremden Startsender-Fallback, gespeicherte Quellbindung im gemeinsamen Raster/Home/Mini-Modell, unveränderte Film-/Serienpfade und .52-Pixelanzeige. Vorhandene .50-Tests prüfen zudem den tatsächlichen vorbereiteten Skincompiler samt Backup/Rollback.

Eine neue reale BINGIE-Hero-Darstellung auf einem Gerät ist dadurch **nicht** abgenommen. Fehlt die bereits freigegebene .50-Integration, bleibt deren Aktivierung **BLOCKED_SKIN_APPROVAL**: Änderungen an `xml/IncludesHomeWidgets.xml`, `xml/IncludesHomeBingie.xml`, `shortcuts/overrides.xml` und `shortcuts/template.xml` erfordern die gesonderte ausdrückliche Nutzerfreigabe mit bestehender Vorschau, Backup, Prüfsummen und Rollback. .53 schreibt keine fremde Skin-Datei und überschreibt keine Skinshortcuts-Verknüpfung. Reale Darstellung, Fokus und automatische Aktualisierung: Android NOT_TESTED.

## Nachtrag: Kodi-Update-Popup

Auf direkten Nutzerwunsch enthält das bestehende sichere einmalige Update-Popup jetzt passende Änderungen. .53 zeigt eine kurze de/en-Zusammenfassung zu EPG-Manager/Live-Vorschau, 24-h-Standard/Berichten, erhaltenen Wizard-Eingaben/Gruppen und dem exakten Passwortverhalten. Andere Versionen können passende lokale Changelogpunkte anzeigen. Keine Netzabfrage. Die bestehende Verschiebung bei Player/fremden Dialogen und einmalige Bestätigung pro installiertem Versionswechsel bleiben erhalten.

## Reale Quellen-/Gerätegrenzen

Öffentliche Kaimandura-DE-MASTER- und EPGShare01-DE1-Abrufe wurden am 28.10.2026, 21:55 Uhr Europe/Berlin, vom Netzwerkproxy dieser Arbeitsumgebung bereits beim HTTPS-Tunnel mit 403 abgewiesen. **BLOCKED_NETWORK**, kein Nachweis eines Feedfehlers, fehlender WELT-/Comedy-Abdeckung oder Android-Netzwerkproblems. Es wurden keine Regeln umgangen und keine privaten Feeds/Logs veröffentlicht. Reale Quellenabdeckung und 7/+20 tatsächlich gelieferte Tage bleiben auf beiden Boxen NOT_TESTED. Hosttests verwenden ausschließlich synthetische Daten. Box A und B wurden nicht geändert.
