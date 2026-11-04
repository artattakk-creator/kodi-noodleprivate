# XCMate 0.1.29.73 – Katalog, Widgets, optionale EPG-Quellen und Sprachen

Basis: `3b3a7f57f1f812e670288bbaaab51f7e63bac8ac` auf main, veröffentlichte .72.
Branch: `fix/xcmate-02973-catalog-widgets-i18n`.
Arbeitsauftrag: #357, #358, #359 einschließlich Kommentare vom 04.11.2026.
Status: **Testkandidat / Draft. Keine Merge- oder Veröffentlichungsfreigabe.**
Alle echten Android-Gates: **ANDROID_NOT_TESTED**, getrennt für Kodi 21.2 und 21.3.

## Nachgewiesene Codepfade und Korrekturen

1. `media_window._initial()` fordert bisher nur bei vollständig fehlendem Katalog einen Import an. Ein vorhandener Neueste-Titel-Katalog beweist keinen Kopf für die gerade gewählte Kategorie. Der neue Worker-Pfad prüft gezielt den Kategorie-Kopf und reiht genau diese fehlende Kategorie in die bestehende Delta-Warteschlange ein. Ausdrücklich bestätigte leere Antworten werden nicht in einer Endlosschleife neu angefordert. Es wird keine generelle fehlerhafte Kategoriezuordnung behauptet.
2. Der alte Status wird durch einfaches Aneinanderhängen zweier Listen und `status[0]` ausgewählt. Dadurch kann eine andere Kategorie oder ein älterer PENDING-Zustand den tatsächlichen Bestand verdecken. Die neue Auswahl ist nach Kategorie und Zeit gefiltert; frische persistente Köpfe sowie bestätigte leere Antworten sind eigene Evidenz. Der erste leere Seitenaufbau erhält bereits den Wartestatus, bevor der nächste Poll eintrifft.
3. `widget_manager50.link()` beendet ALREADY_LINKED bisher vor dem nativen Home-Neuaufbau. Die neue Diagnose unterscheidet fehlende gespeicherte Verknüpfung, veralteten Home-Aufbau, fehlenden Reload-Hook und ausstehende Daten. Nach expliziter Bestätigung wird eine vorhandene Verknüpfung repariert und der bestehende Skinshortcuts-Builder aufgerufen. Ein fehlender eigener Reload-Hook wird als zusätzlicher Parameter an exakt derselben Quelle ergänzt. Position, Titel, andere Parameter und Fremdwidgets bleiben erhalten. Private Sicherung, Hash-Vergleich, native Skinshortcuts-Leseprüfung und exakte Wiederherstellung sind getestet. Kein XCMate-Patch verändert BINGIE-Skindateien; der ausdrücklich gestartete native Builder darf seine generierten Home-Includes erneuern. Keine Widgets werden automatisch eingerichtet.

## Gesamter Katalog und Hintergrundanzeige

`Einstellungen → Portale/Provider → vorhandenen Provider auswählen → Gesamten Katalog aktualisieren`.
Die bisherige dedizierte Film-/Serienaktion bleibt zusätzlich erhalten. Der neue Dialog wählt standardmäßig Live-TV, Filme und Serien; EPG ist optional. Eine Bestätigung schreibt den Auftrag und gibt die Oberfläche sofort zurück. Es folgt keine zweite versteckte Startmaske.

`catalog_jobs73` verwendet denselben interprozessualen Schreibschutz wie die vorhandenen Delta-/Katalogworker. Bestehende Jobs werden nicht überschrieben. Pro Service-Durchlauf wird eine Gruppe mit dem geprüften .72-Streaming-/Upsert-Schreiber verarbeitet; anschließend wird der Schreibschutz freigegeben. Der neue Adapter erweitert nur den erlaubten Inhaltsscope um Live-TV. Keine Änderung von Player, Live-Navigation, Widget-Routen oder Fernbedienungsbelegung.

- Persistente Zustände WAITING, RUNNING, DONE, FAILED, INTERRUPTED; Zeitstempel, Fortschritt, Fehlercode, Cursor und Abbruchabsicht.
- Gleicher Provider und aktive Aufträge werden dedupliziert. Netzwerk-/SQLite-Fehler erhalten begrenztes Backoff; nach drei Versuchen ist eine ausdrückliche Wiederholung erforderlich. Ein konkurrierender Writer meldet WAITING/WRITER_BUSY.
- Dienstabbruch ist fortsetzbar; Benutzerabbruch bleibt unterbrochen, bis der Benutzer fortsetzt. Verifizierte Gruppen bleiben erhalten. Keine Teilgruppe wird sichtbar.
- Vor dem ersten Commit private, scoped Sicherung mit Integrität und SHA256. Die große SQLite-Sicherung hält nur den Katalog-Schreibschutz; der Konfigurationslock wird nach dem kleinen Einstellungssnapshot freigegeben, damit Status-/Einstellungsleser bedienbar bleiben. Jeder Prozess liest die unveränderte Sicherung zunächst kalt zurück. Weitere Gruppen verwenden die geprüfte Dateidentität, statt große Sicherungen pro Gruppe erneut vollständig zu hashen. Änderungen an Sicherung/Manifest erzwingen erneute Prüfung.
- Gruppenkopf, Generation und Receipt werden atomar gespeichert; separater Datenbank-Readback vor Cursorfortschritt. Vorhandene Titel, Metadaten und Bildreferenzen bleiben bei fehlenden/teilweisen/fehlerhaften Antworten erhalten. Abwesende Datensätze werden nicht gelöscht. Unvollständige API-Formate sind Fehler, keine leeren Kataloge.
- Bestehende aktivierte/deaktivierte Gruppen, Auto-Neu-Auswahl, Startgruppe/Startsender und Inhaltsbereichseinstellungen werden beim Gesamtscan nicht verändert. Neu entdeckte, bislang deaktivierte Gruppen lassen sich weiterhin im Gruppenmanager auswählen.
- Abschlussbericht enthält tatsächliche gelesene/gespeicherte Zahlen und DB-Bestand. Optionales EPG wird an den vorhandenen Import angefordert; REQUESTED bedeutet ausdrücklich noch keinen erfolgreichen EPG-Import.

Die Anzeige nutzt einen einzigen nativen `DialogProgressBG`, ohne Fokusübernahme und ohne Benachrichtigung pro Gruppe. Alte Hintergrundimporte liefern ihre tatsächlichen Gruppen-/Batchdaten über den bestehenden Sync-Callback; der Beobachter führt keine Providerabfrage aus. Wartende Aufträge heißen „Wartet“. Unbekannte Gesamtmengen werden nicht zu erfundenen Prozentwerten umgerechnet. Während Wiedergabe ist die Anzeige verborgen. Abschluss/Fehler erzeugt höchstens eine kurze Zusammenfassung. Kodis Skin bestimmt die Position des nativen Hintergrunddialogs: **exakt oben rechts / Lesbarkeit / Playerüberdeckung unter BINGIE bleiben ANDROID_NOT_TESTED**. Es wird kein ungeprüfter Skin-Adapter installiert.

## Internationale Quellen (#358)

Direkter Button im vorhandenen EPG-Manager: **Internationale EPG-Quellen**.
Der Quellenmanager wird erweitert und bleibt die einzige Konfigurations-/Importarchitektur.

- 149 eindeutige ISO-Einträge, nach Kontinent: 104 Kandidaten (72 + 32) und 45 reine Metadateneinträge ohne Downloadfunktion.
- Alle Kandidaten standardmäßig deaktiviert. Kein Download beim Öffnen/Update und keine automatische Aktivierung nach Länderwahl.
- Länderbezeichnungen aus CLDR/Babel in 17 Varianten; Lizenzen liegen dem Add-on bei. Kein neuer Laufzeitdienst.
- Die 32 zusätzlichen FreeEPG-XMLTV-Links wurden über ihre offiziellen Länderbuttons einzeln aufgelöst; Beleg: `epg/endpoint_review_02973.json`. Ein aufgelöster Link oder GZIP-Content-Type ist **kein** erfolgreicher XMLTV-Import.
- Verifikation prüft nur erlaubte registrierte HTTPS-Endpunkte, öffentliche DNS-Ziele, maximal drei Weiterleitungen derselben Origin, TLS, vollständiges XML/GZIP mit dem bestehenden SAX-Parser (inertes XMLTV-DTD-Merkmal erlaubt, keine Entitäten/externen Abrufe), Sender, Programme, Zeitspanne und Aktualität. Keine fremden/privaten Hosts, Credentials oder Protokoll-Downgrades. Begrenzte Datei-/Dekompressions-/Laufzeitbudgets und Reserveprüfung. Eigene temporäre Probe wird anschließend entfernt, bestehende Daten nicht angerührt.
- Erst frischer positiver Prüfbeleg plus geprüfte Nutzbarkeit und ausdrückliche Aktivierung übernehmen eine Quelle in den bestehenden EPG-Manager. Bestehende DACH-/Provider-Quellen, Prioritäten und manuelle/quellenbezogene Zuordnungen bleiben erhalten. Alternative Quellen können separat gewählt und im bestehenden Manager priorisiert werden. Vorhandener 24-Stunden-Scheduler, SQLite-Import und ID-/Namensmapping werden weiterverwendet.

**Offen/BLOCKED:** Die Cloud-Netzrichtlinie verweigert direkte Feed-GETs (403); der Webconnector kann GZIP-Inhalte nicht validieren und meldet bei einigen Endpunkten 503. Es gibt deshalb keine Behauptung über 104 erfolgreich getestete Feeds. Die bestehenden iptv-epg-Links sind zur Nutzung im persönlichen IPTV-Player angeboten; Aktivierung verlangt zusätzlich die Laufzeitprobe. FreeEPG-Nutzungsprüfung bleibt offen und seine Aktivierung gesperrt. Noch nicht individuell offiziell abgeglichene alternative Feedmuster bleiben gesperrt. Kein Umgehen der Netzrichtlinie und kein Spiegeln von Rohfeeds auf GitHub.

## Mehrsprachigkeit (#359)

Bestehende `localization.py` wurde erweitert, keine zweite Implementierung.
17 gebündelte Sprachvarianten plus „Kodi übernehmen“ in der bestehenden Sprachwahl. Alte Einstellungswerte/erste drei Menüpositionen bleiben unverändert. Unbekannte Sprache, fehlender Text und fehlerhafte Platzhalter fallen auf Englisch zurück.

Die neuen Abläufe enthalten 36 zentralisierte Strings, in allen 17 Katalogen vorhanden. Die 15 neuen Kataloge enthalten zusätzlich 15 übersetzte Kernnavigationseinträge, insgesamt jeweils 51. Deutsch/Englisch enthalten jeweils 1.222 Einträge. Länderbezeichnungen sind ebenfalls lokalisiert. PO-Syntax, UTF-8 und Platzhalter werden automatisiert geprüft.

**Teilweise umgesetzt, nicht vollständig übersetzt:** Ältere Dialoge außerhalb dieser 51 Einträge verwenden in den 15 neuen Sprachen Englisch. Mehrere alte Wizard-/EPG-Texte sind noch hartcodiert. Deren vollständige Zentralisierung, sprachliche Geräteprüfung und arabisches RTL-Layout bleiben offen. Es wird weder Vollübersetzung noch RTL-Abnahme behauptet. Kodi-Standardsprache, globale Skin-Konfiguration und Providerdaten werden nicht geändert.

## Tests und Lieferung

- 2.945 vorhandene Testmethoden bleiben samt Skip-Bedingungen erhalten; Basisschutz für alle 689 vorherigen Add-on-Dateien. Nur exakt dokumentierte Quelländerungen werden für historische Hashprüfungen normalisiert.
- Gezielte HTTP/SQLite-Tests: 51 PASS einschließlich erneuter .72-Rescan-Regressionen; echte 3.357 Live-Sender / 53 Gruppen, Abbruch/Fortsetzung, Writer-Konflikt, Leer-/Teilantwort, private Sicherung und Cold-Readback.
- Widget-/Sprach-/Statusprüfung: 9 PASS. Echte TLS/GZIP-/EPG-Konfigurationsprüfung einschließlich inertem DTD: 3 PASS. Historische Source-/Scope-Prüfungen: 101 PASS im Zwischenstand; die abschließende CI prüft den finalen Stand erneut.
- Nativer Kodi 21.2: Hintergrunddialog ohne Modalblockade, native Eingaben während Import, drei echte Gruppen-Commits, gespeicherter Readback für Live/VOD/Serie und Film-/Serien-Kodi-Verzeichnisantworten PASS. Nur synthetisches, isoliertes Linux-Profil; keine Android-Abnahme.
- Vollständiger finaler Hostlauf und GitHub Actions: Ergebnisse werden am Draft-PR mit Commitbezug dokumentiert. Frühere Testläufe während Codeänderungen sind keine finale Abnahme.
- Review-Workflow .72 spielt künftig seinen unveränderlichen gemergten Basiscommit ab; er darf die aktuelle .73 nicht mit einem archivierten .72-ZIP vergleichen. Neue .73-CI und kumulative Publish-PR-CI prüfen dagegen den aktuellen Quellstand. Auf PRs wird ausschließlich ein Reviewartefakt erstellt.
- ZIP und SHA256: `test-builds/02973/`. Source-/CRC-Prüfung und deterministischer Neuaufbau sind Teil der Paketierung/CI.
- Android-Plan: `ANDROID_ABNAHME_02973_DE.md`. Alle Gates zunächst **ANDROID_NOT_TESTED**.

## Issue-Matrix / Mergeentscheidung

| Issue | Implementierter Stand | Noch offen |
|---|---|---|
| #357 | P0-Kategorieanforderung/-Status, persistenter Gesamtscan, nonmodale Anzeige, vorhandene manuelle Widget-Reparatur | echte .72-/Altprofil-Upgrades, Live-Provider-Abgleich und BINGIE-Home/Neustart auf beiden Boxen; genaue native Statusposition |
| #358 | 104 deaktivierte Kandidaten +45 Metadaten, Kontinente/Alternativen, sichere Laufzeitprüfung/Opt-in, bestehender Scheduler/Mapping | individuelle positive Endpunkt- und Nutzungsprüfung; FreeEPG-Aktivierung gesperrt, reale Feed-/ARM32-Tests |
| #359 | 17 Sprachvarianten für neue Abläufe/Kernnavigation, Kodi-Übernahme/Englisch-Fallback, PO-/Unicode-/Platzhaltertests | vollständige Legacy-Oberfläche, sprachliche Abnahme, Arabisch/RTL auf Kodi |

Keines der drei Issues wird geschlossen. **Nicht mergebereit für den vollständigen Masterauftrag**, solange die genannten offenen Anforderungen und Android-Gates nicht freigegeben sind. Der Draft ist als installierbarer Prüfstand vorgesehen. Der produktive Pilot-Kanal und alle Repository-Kataloge bleiben auf ihrem vorhandenen Stand. Box A/B werden von dieser Entwicklung weder installiert noch verändert.
