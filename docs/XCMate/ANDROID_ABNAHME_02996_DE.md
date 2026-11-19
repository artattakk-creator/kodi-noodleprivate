# XCMate .96 – Android-Abnahme

Status aller untenstehenden Gerätegates: **ANDROID_NOT_TESTED**. Native Linux-Kodi-Tests sind keine Abnahme von Android 21.3 / RK3528. Box A bleibt unverändert. Kein Merge oder Repository-Release freigegeben.

## Vorbereitung

Das geprüfte ZIP aus diesem Draft-PR über Kodi „Aus ZIP-Datei installieren“ als kumulatives Update installieren. Keine Deinstallation, kein Profilreset und kein Löschen von Cache, Datenbank, WAL oder Sicherungen. Bestehender TMDB-Token bleibt unverändert. Aktuelle Version und Ausgangszustand der Sendergruppen, Favoriten, Widgets und manuellen Zuordnungen dokumentieren. Das Installationsfenster zeigt Version und Änderungen aus dem Changelog.

Zuerst die Gruppenstrecke durchführen. Bei FAIL nicht weitere große EPG-Imports anstoßen. Keine erneute Komplettsicherung auf Verdacht: .95-Importfreigabe unabhängig prüfen, vorhandene Sicherung erhalten.

| Gate | Durchführung und erwartetes Ergebnis | Status |
|---|---|---|
| G96-01 | Zweimal Kodi kalt starten: gespeicherter Startsender/Startgruppe unverändert, Logos und lokale Programmdaten verfügbar. | ANDROID_NOT_TESTED |
| G96-02 | Startgruppe → Unterhaltung → weitere aktive Gruppe, zehn Wiederholungen. Alle Sender erscheinen und mindestens ein Sender je Gruppe spielt auch ohne EPG. | ANDROID_NOT_TESTED |
| G96-03 | Schnell A→B→A wechseln, während EPG/Artwork beschäftigt sind. Keine fremde Gruppenantwort, kein Fokusverlust; vorhandene Liste bleibt bei Busy nutzbar. | ANDROID_NOT_TESTED |
| G96-04 | Offline/teilweise importierte Gruppe: „wird geladen“ statt falscher Leermeldung, begrenzte Retries, nach abgeschlossenem Katalogimport automatische Aktualisierung. | ANDROID_NOT_TESTED |
| E96-01 | Provider-EPG als Grundversorgung; alte Abschaltungen als Historie erhalten, optionale XMLTV-Quellen und manuelle Mappings unverändert. | ANDROID_NOT_TESTED |
| E96-02 | Unter EPG-Sicherung „Importfreigabe prüfen“: IMPORT_AUTHORIZED separat bestätigen. Erst danach einen DE/AT-Import, Commit und quellweisen Readback prüfen. | ANDROID_NOT_TESTED |
| S96-01 | Im Artwork-Menü einmal „Testkonfiguration anwenden“ ausdrücklich wählen. Vorhandener Token wird verwendet, Verbindung geprüft; XMLTV/TMDB/TVMaze AN und Bild-EPG freigegeben. Keine neue Token-Datei auswählen, wenn gültiger Token vorhanden ist. | ANDROID_NOT_TESTED |
| S96-02 | Kodi neu starten: drei Quellenschalter bleiben wirksam. Normale andere Profile werden nicht automatisch für externe Dienste angemeldet. | ANDROID_NOT_TESTED |
| S96-03 | Lesefehler verständlich diagnostiziert statt SOURCE_DISABLED. Eine Reparatur nur nach ausdrücklicher Bestätigung und nur aus geprüfter Sicherung; beschädigte Datei bleibt erhalten. | ANDROID_NOT_TESTED |
| I96-01 | Galileo oder andere konkrete XMLTV-icon-Sendung: Mini, großes EPG, Details und Hero auf korrekte Quelle/Sendung und tatsächlich sichtbare Textur prüfen. Ein Download-/READY-Marker allein genügt nicht. | ANDROID_NOT_TESTED |
| I96-02 | Details → manuelle Bildzuweisung → XMLTV / XMLTV-Bilder erneut suchen: lokale Kandidaten, Vorschau, explizites Speichern, Readback, Reopen und Neustart. | ANDROID_NOT_TESTED |
| I96-03 | XMLTV→TMDB→Automatisch sowie XMLTV→Ausblenden→Automatisch prüfen. Kein festhängender versteckter Eintrag; Quelle/Revision/Ereigniswechsel dürfen kein falsches Bild übernehmen. | ANDROID_NOT_TESTED |
| I96-04 | XMLTV AUS widerruft Anzeigezulassung, ohne Bilder/Zuordnungen zu löschen. TMDB AUS/Netzfehler lässt gültige freigegebene XMLTV-Alternativen nutzbar. | ANDROID_NOT_TESTED |
| I96-05 | Eindeutige Serie, Film und Episode: breite TMDB-Backdrops passend, unterschiedliche Bildrollen und proportionaler Poster-Fallback. Kein Pflicht-TMDB-Helper. | ANDROID_NOT_TESTED |
| I96-06 | Ein konkretes Bild ausdrücklich manuell bestätigen. Danach zwischen Hero und Details wechseln und fünf Minuten warten. Exakt diese bestätigte Bildwahl bleibt trotz neuer automatischer Backdrops bestehen; nach Neustart erneut prüfen. | ANDROID_NOT_TESTED |
| I96-07 | Manuelles XMLTV-Bild anzeigen, Quelle anschließend mit geänderter Ereignisrevision aktualisieren. Der alte Bildnachweis wird widerrufen; Worker-/lokaler Cache darf ihn nicht weiter als gültig anzeigen. Andere Sendungen und bestehende Zuordnungen bleiben erhalten. | ANDROID_NOT_TESTED |
| M96-01 | Links auf echter Senderzeile: kurzes OK schaltet um, langes OK öffnet EPG-Zuweisung genau einmal. Kein vorzeitiger Senderstart. Keine globale Keymap ungefragt ändern. | ANDROID_NOT_TESTED |
| M96-02 | Rechts auf Sendung: kurzes OK öffnet Details. Im großen EPG bleibt kurzes OK das Kontextmenü. Geräte ohne Lang-OK nutzen Kontextmenü → EPG zuweisen. | ANDROID_NOT_TESTED |
| M96-03 | Zwei Quellen mit identischer Kanal-ID vergleichen, auch >100 Treffer; echte Zeiten/Texte in RAM-Vorschau. Abbrechen stellt Fokus/Position/Programmdaten wieder her; Wiedergabe bleibt aktiv. | ANDROID_NOT_TESTED |
| M96-04 | Eine Quell-/Kanalzuordnung speichern; unabhängig zurücklesen, neu öffnen, Kodi neu starten. Genau der ausgewählte Sender ändert sich; andere Quellen/Gruppen bleiben erhalten. | ANDROID_NOT_TESTED |
| L96-01 | Senderlogo lokal und über ausdrücklich ausgewählte SMB-Datei ersetzen. PNG/JPEG-Vorschau und Bestätigung. Senderleiste, Mini, OSD, Guide, Details, BINGIE einschließlich Neustart prüfen. | ANDROID_NOT_TESTED |
| L96-02 | Logo jenseits Senderposition 512 sowie Provider-URL-/Gruppenwechsel prüfen. „Original wiederherstellen“ setzt nur einen Override zurück. Keine Roh-Providerdaten umschreiben. | ANDROID_NOT_TESTED |
| L96-03 | Live-Senderliste geöffnet lassen, über Extras/Einstellungen dasselbe Logo ersetzen und danach zurückkehren. Neues Logo ohne Katalog-Neuladen sichtbar. Anschließend nur diesen Override zurücksetzen: verifiziertes Providerlogo/Fallback sofort wiederhergestellt; andere Sender und Konten unverändert. | ANDROID_NOT_TESTED |
| C96-01 | Speicher → Artwork & Cache: 32/64/128/256 MiB, tatsächliches Zielvolume/freier Platz/reale Reserve. Vorhandene bewusste Auswahl und Archive bleiben erhalten. | ANDROID_NOT_TESTED |
| C96-02 | Dynamisch bei wenig Speicher: URL/RAM bleibt möglich, keine 1-GiB-Archivpflicht. Echte Schreibreserve und SQLite-Schutz bleiben aktiv. Kein erfundener Kapazitätsgewinn. | ANDROID_NOT_TESTED |
| C96-03 | Selektive Bereinigung zeigt Anzahl/Bytes und verlangt Bestätigung. Aktive/manuelle Bilder, Logos, Guide/WAL/Backups, Kodi-Texturen bleiben geschützt. | ANDROID_NOT_TESTED |
| R96-01 | Alle sechs Widgets plus eigene fremde Reihen; Filme/Serien, Cover, Suche, Favoriten, Resume, Autoplay inklusive Staffelwechsel. | ANDROID_NOT_TESTED |
| R96-02 | Live-TV/Film/Serie verlassen; Rückkehr entsprechend Herkunft BINGIE bzw. Plugin, kein Doppelstart, fremde Wiedergabe unberührt. | ANDROID_NOT_TESTED |

## Nachweis

Je Gate PASS, FAIL oder NOT_TESTED samt Version, Gerät/Kodi-Version, Uhrzeit und kurzer Beobachtung erfassen. Bilder separat visuell prüfen. Nur anonymisierte Diagnosecodes/Zähler teilen; keine Rohlogs mit Zugangsdaten, Stream- oder SMB-Verbindungsdaten öffentlich hochladen. Hardware-Stop-/Decoderfehler sind weiterhin gesonderte Abnahmebedingungen.
