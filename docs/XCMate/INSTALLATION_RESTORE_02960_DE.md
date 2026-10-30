# .60 – Testinstallation, Opt-in-Skinplan und Rücknahme

Nur Box B nach eigener Testentscheidung. Installations-ZIP und SHA256 stehen im Draft-PR; manuell als Update der bestehenden plugin.video.xtreammate installieren. Keine Deinstallation, kein Downgrade, keine Zurücksetzung. Das vorhandene Installationspopup liest die .60-Änderungen aus changelog.txt. Box A bleibt ausgeschlossen.

Die drei bisherigen Quellen bleiben im vorhandenen Widgets-Ordner. Bestehende Film-/Serienreihen nicht löschen, zurücksetzen oder erneut verknüpfen.

## BINGIE-Adapter bewusst prüfen

XCMate → Einstellungen → Aussehen und Darstellung → Widgets. Über die vorhandene Live-TV-Auswahl bzw. deren Kontextmenü „BINGIE“-Skin-Anpassung öffnen. Bei bereits vorhandener Live-Verknüpfung ist kein neues Speichern dieser Bindung nötig. Ohne laufende Wiedergabe prüfen:

1. Tatsächlich BINGIE MOD 2.2.3 und Skinshortcuts 2.1.0. Andere oder nicht exakt bekannte Skin-Dateien werden blockiert.
2. Die Vorschau zeigt den echten Diff und die SHA256-Werte der vier betroffenen Dateien. Beim Vorbereiten entstehen nur private Plan-/Sicherungsdateien; die installierten Skin-Dateien bleiben unverändert.
3. Erst die separate ausdrückliche Bestätigung übernimmt den Plan. Abbrechen/Nein verändert keine Zieldatei. Danach fordert XCMate einmal den nativen Skinshortcuts-Rebuild an. Keine generierte Benutzer-XML manuell kopieren und keine Rebuild-Schleife starten.
4. Die vorhandenen Widget-Quellen bleiben unverändert. Das neue Include wählt für diese Live-Quelle den Logo-/Hero-Consumer; normale Film-/Serien-Consumer bleiben bestehen.

Bei unbekannten Quell-Hashes, Berechtigungsfehlern oder paralleler Änderung nicht erzwingen. Die .60-Programmversion bleibt nutzbar, die Skin-Übernahme ist dann BLOCKED bis zur gezielten Prüfung der tatsächlichen Dateien. Kein pauschales Skinshortcuts-Reset.

## Skin-Rücknahme

Im selben vorhandenen Widget-Kontextmenü „Wiederherstellen“ öffnen, den zugehörigen Skinplan auswählen und die separate Wiederherstellung bestätigen. Originale und Kandidaten wurden privat mit SHA256 gesichert; Ziele werden vor jedem Schritt erneut geprüft. Ein abgebrochener Mehrdateienschritt bleibt über denselben Plan wiederherstellbar. Fremde nachträgliche Änderungen blockieren Überschreiben; keine rohe Dateikopie darüberlegen.

Die Rücknahme betrifft ausschließlich die vier Dateien dieses Plans. Sie ist keine Add-on-Deinstallation und ändert weder Portal-/EPG-Daten noch Film-/Serienbindings. Bestehende Sicherungen werden nicht gelöscht.

## Eigener TMDB-Zugang

Unter Medien & Wiedergabe das vorhandene verdeckte API-Read-Access-Token-Feld privat verwenden. API-Key v3 ist kein Ersatz für den Bearer-Token in diesem Feld. Unter EPG „TMDB-Verbindung testen“ ausführen. Der Test ist ausdrücklich und liest nur Konfiguration; er aktiviert nichts für andere Geräte/Nutzer.

Für optionale Sendungsbilder bleiben tmdb_research43 und programme_tmdb46 die beiden lokalen Schalter. Standard ist weiterhin aus. Programme müssen vorher tatsächlich im lokalen EPG vorhanden sein. Cache-/Hintergrundvorbereitung ersetzt keinen Providerimport; keine API-Anfrage beim Fokus. Bei HTTP_RATE_LIMIT warten, statt fortlaufend neu zu starten. Logo und Attribution bleiben sichtbar; öffentliche kommerzielle Nutzungsrechte sind damit nicht pauschal freigegeben.
