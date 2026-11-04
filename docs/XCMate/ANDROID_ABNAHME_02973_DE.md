# Android-Abnahme XCMate 0.1.29.73

Jeden Test getrennt protokollieren: Box A (Kodi 21.2 / ältere vollständige Installation), Box B (Kodi 21.3 / .72), Datum, tatsächlich installierte Ausgangsversion, Ergebnis und datensparsamer Diagnosecode. **Voreinstellung für jedes Feld: ANDROID_NOT_TESTED.** Host-PASS ist kein Android-PASS.

Box A zunächst nur nach ausdrücklicher Gerätefreigabe prüfen. Keine Ferninstallation, Deinstallation, Neuinitialisierung, Daten-/Cache-Löschung oder Wiederholung des 48-Komponenten-Installers. Kein Merge/produktives Release durch diese Anleitung.

## Test-Build installieren

1. Vorhandene Einstellungssicherung nutzen; Portal-, Gruppen-, EPG-/TMDB-, Favoriten-/Resume- und Widgetbestand vorab notieren. Keine privaten Daten auf GitHub hochladen.
2. `test-builds/02973/plugin.video.xtreammate-0.1.29.73.zip` und `.zip.sha256` aus dem Draft laden. SHA256 prüfen; auf einem Rechner im gleichen Ordner: `sha256sum -c plugin.video.xtreammate-0.1.29.73.zip.sha256`.
3. Kodi → Add-ons → Aus ZIP-Datei installieren → genau dieses Paket über die vorhandene Installation aktualisieren. Version .73 und Installationspopup/Änderungen kontrollieren. Keinen Downgrade durchführen.
4. Das ist ein manuelles Testupdate; der reguläre Pilot-Kanal bleibt unverändert. Bei Problemen Code, Uhrzeit, Bereich und Zustand melden; keine Rohlogs/Zugangsdaten öffentlich anhängen.

## Katalog / Hintergrundstatus (#357)

| ID | Ausführbarer Test | Erwartung | Box A | Box B |
|---|---|---|---|---|
| CAT-01 | Vor/nach Upgrade Portale, 3.357 Sender (sofern vorhandener Gerätebestand), Gruppen/Startsender, EPG/TMDB, Favoriten, Resume vergleichen | Bestand erhalten; tatsächlichen Gerätebestand protokollieren | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-02 | Neueste Filme/Serien öffnen, dann bislang nicht importierte Kinderfilm-/Serienkategorie | Wartet/läuft statt irreführender endgültiger Leermeldung; gezielte Nachforderung | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-03 | Bereits laufenden Altimport beobachten, Kategorien wechseln | Keine konkurrierende Neuinitialisierung, späterer Kategorieinhalt erscheint ohne neue Einrichtung | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-04 | Einstellungen → Portale/Provider → vorhandenen Provider → Gesamten Katalog aktualisieren | Live/Filme/Serien vorgewählt; EPG optional; vorhandene Verbindung, keine Passwortabfrage | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-05 | Einmal bestätigen, Maske verlassen, mehrere Kodi-Menüs mit Fernbedienung öffnen | Auftrag persistiert, Oberfläche bedienbar, eine nonmodale Anzeige, keine Popupflut | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-06 | Aktuelle Gruppe und Zähler vergleichen | Tatsächlicher Gruppenname/Gruppe/Titelzahl; Wartet bei Warteschlange, keine erfundene Gesamtmenge | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-07 | Statusaktion erneut öffnen, aktiven Auftrag prüfen | Vorhandener Job statt parallelem Doppelimport | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-08 | Nach einer fertigen Gruppe über Status abbrechen, danach fortsetzen | Verifizierte Gruppen erhalten, keine Teilgruppe; Fortsetzung am Cursor | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-09 | Während Import Kodi normal beenden und erneut starten | Unterbrechung/Fortsetzung nachvollziehbar, kein falscher Abschluss | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-10 | Bei temporärem Providerfehler erneut Status prüfen | Fehlercode/begrenzte Wiederholung, alter Bestand bleibt nutzbar | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-11 | Abschlussbericht und Kategorien/Neueste öffnen; Kodi neu starten | Titelzahlen/Readback plausibel, Daten persistent, deaktivierte Gruppen bleiben deaktiviert | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| CAT-12 | Während Import Live-TV starten, Overlays/Back verwenden | Keine Statusüberdeckung im Player; bestehender .42-Kompatibilitätsmodus bleibt unverändert | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |

Bei fehlenden Titeln nicht den Profilbestand zurücksetzen: Status und Kategorie-ID privat sichern, Warteschlange/Head-Generation diagnostizieren lassen. Bei leerer Anbieterantwort kann der alte gültige Inhalt bewusst erhalten bleiben.

## BINGIE-Widgets

| ID | Test | Erwartung | Box A | Box B |
|---|---|---|---|---|
| WID-01 | Einstellungen → Aussehen/Darstellung → Widgets | Bestehende drei Quellen und gewohnte Routen vorhanden | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| WID-02 | Bereits verknüpftes Widget wählen, Diagnose lesen, Reparatur ablehnen | Keine Datei, Position oder Einstellung geändert | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| WID-03 | Bewusst vorhandene Verknüpfung reparieren/neu aufbauen | Nativer Skinshortcuts-Aufbau; Titel/Position/Fremdwidgets erhalten | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| WID-04 | BINGIE Home: Live-Startgruppe, Neueste Filme, Neueste Serien | Echte Inhalte, keine URL-Textanzeige; Startgruppe vollständig | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| WID-05 | Katalog aktualisieren, auf Home zurück, danach Kodi neu starten | Reihen aktualisiert und weiterhin vorhanden; Cover/Klick/Back funktionieren | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| WID-06 | Nur wenn erforderlich: vorhandenen Reparaturplan über Rückrollfunktion wiederherstellen | Ursprüngliche Verknüpfungsbytes und eigene Einstellungen zurück; keine Skin-Änderung | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |

Standalone richtet keine neuen Home-Widgets automatisch ein. GS-Media-Komplettinstallation bleibt ein eigenständiger Installerablauf und wird hier nicht ausgeführt. Eine fehlende gespeicherte Verknüpfung benötigt manuelle Auswahl; ein Netzwerk-/Datenfehler wird nicht durch Skin-Reset „repariert“.

## Internationale EPG-Quellen

| ID | Test | Erwartung | Box A | Box B |
|---|---|---|---|---|
| INT-01 | EPG-Manager → Internationale EPG-Quellen öffnen | Kontinente, 104 Kandidaten und45 reine Metadaten, ISO ohne Dubletten; bestehende Quellen erhalten | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-02 | Ohne Aktivierung schließen, Netzwerk-/Quellenstatus prüfen | Kein automatischer Länderdownload, alles Neue aus | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-03 | Ein Land/eine offiziell freigegebene Quelle zur Prüfung auswählen | HTTPS/XML/GZIP-Prüfung im Worker; Fortschritt/Abbruch bedienbar | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-04 | Bei positivem Beleg Aktivierung ablehnen | Keine neue aktive Quelle und kein Mapping-Schreibvorgang | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-05 | Genau eine positiv geprüfte Quelle ausdrücklich aktivieren | Bestehender EPG-Importer, belegte Sender-/Sendungszahlen und Zeitraum; keine Massendownloads | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-06 | Quelle mit offener Nutzungsprüfung/ungeprüftem Muster bzw. Downloadfehler auswählen | Klarer Sperr-/Fehlercode, keine falsche Freigabe; alter EPG bleibt | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-07 | Manuelle Zuordnung und vorhandene DACH-/Provider-Prioritäten vergleichen | Unverändert; alternative Quelle separat wähl-/priorisierbar | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| INT-08 | Neustart/24h-Intervall, Speicher und Importbericht kontrollieren | Nur aktivierte Quellen aktualisiert, keine unnötige dauerhafte Probe-Datei | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |

FreeEPG bleibt bis zur Nutzungsprüfung gesperrt. Keine alle104 Länder betreffenden Downloads anstoßen. Größere Proben können aus konservativem Größen-/Zeitbudget abgewiesen werden; das ist kein erfolgreicher Feednachweis.

## Sprache und Regression

| ID | Test | Erwartung | Box A | Box B |
|---|---|---|---|---|
| LNG-01 | Sprache auf Kodi übernehmen/Deutsch/Englisch umstellen, Neustart | Wahl erhalten, nur XCMate geändert | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| LNG-02 | Jede der15 neuen Varianten: Kernnavigation, Katalogdialog/Status, Länder/Quelle prüfen | Übersetzung/Unicode/Platzhalter lesbar; nicht übersetzte Alttexte Englisch | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| LNG-03 | Arabisch mit gemischten IDs/Zahlen/Sendertiteln und Fernbedienung prüfen | RTL/Glyphen/Fokus eigens dokumentieren; keine pauschale RTL-PASS-Behauptung | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| REG-01 | Live-TV, Mini-/großer EPG, Senderstart, Links/Back/Stop | .72-Verhalten erhalten, kein Hänger | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| REG-02 | Film-/Seriensuche, Cover, Wiedergabe, Resume, Autoplay/Staffelwechsel | Bestehende Funktionen erhalten | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |
| REG-03 | Nach normalem Kodi-Neustart Provider-/EPG-/TMDB-/Favoriten-/Skin-/Keymap-Bestand vergleichen | Keine verlorenen Werte, keine erzwungene Migration | ANDROID_NOT_TESTED | ANDROID_NOT_TESTED |

Fehler als FAIL mit Zeitpunkt und Code protokollieren. Nicht durchgeführte Tests bleiben ANDROID_NOT_TESTED. Ohne ausdrückliche Freigabe erfolgt kein Merge und kein produktives Repository-Update.
