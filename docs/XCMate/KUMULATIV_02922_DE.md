# XCMate .22 – kumulativer Updatekandidat auf .21

**Aktuelle Basis:** main `3307e006a9de9fd53236ec881191851291731c98` (23.10.2026), einschließlich .21-Merge `5a634043410b615d0e270a0d9fca2174690f78f1`, Repository-Publishing `c0ad3a3` und verbindlichem Updatepfad. Add-on-ID `plugin.video.xtreammate`, Zielversion `0.1.29.22`.

## Umsetzung und Historie

PR #110 bleibt derselbe Draft mit Branch `fix/xcmate-02922-guide-navigation`. Der aktuelle main wurde durch einen normalen Merge in den Entwicklungsbranch übernommen, Versions-/Changelog-/Sprach-/Dokumentationskonflikte gezielt aufgelöst. Keine Force-Push-Aktion, keine Änderung von main. Alte EPG-Arbeit und alte ZIP-Stände bleiben in der Git-Historie erhalten und sind ausdrücklich überholt. Alle kommenden Versionen entwickeln sich kumulativ; kein Downgrade oder Deinstallieren zwischen Gerätetests.

Die .21-Implementierungen von Autoplay, Player-OSD, Player-Intent/Ownership, MediaWindow, Service, Folgenordnung, Resume/Gesehen und Artwork sind bytegleich zur aktuellen Hauptbasis, ebenso die beiden Autoplay-/OSD-Testdateien. Die vorhandenen 46 gezielten .21-Fälle sind Teil des vollständigen kumulativen Laufs. Natürliches Ended, Staffelwechsel/Nummernlücken, Stop-Priorität, Fehler/Shutdown, Doppelstartschutz und manueller Next bleiben unverändert. Alte PR #84/#50 wurden nicht vollständig gemergt.

Die EPG-Änderungen aus #110 wurden erhalten: ausschließlich eine erlaubte Startgruppe, Startsender an Originalposition, begrenzter Acht-Sender-Viewport, separate Gruppenansicht, lesbare Sender-/Programmfokussierung, IR-Kopfzugang und Refresh ohne Fokusdiebstahl. Der aktuelle Auftrag konkretisiert **Zurück aus Gruppen → vorige EPG-Ansicht**. Dafür gibt es einen lokalen Snapshot mit Gruppe, Offset, Zeile, Cursor, Zeitausschnitt und Fokuszone; Cancel der Gruppenansicht schreibt keine Startkonfiguration. Back-Repeat ist entprellt; Back im Raster führt Home. Auswahl einer anderen Gruppe lädt ausschließlich deren Sender und zeigt währenddessen keine alten Sender unter dem neuen Titel. Details: `EPG_NAVIGATION_02922_DE.md`.

## Original-Icon

Selektiv übernommen wurde allein die geprüfte Originaldatei aus dem Space-Premium-Branch: `themes/xcmate/space-premium/assets/branding/icon-512.png`, Originalcommit `3aa97ad0e6eb307eb861a76e59551d10966fa713`, Git-Blob `c6649e18f972a633f942b0010682c500239e7f42`, 512×512 RGB, 402058 Bytes. SHA256 **81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135**. Quelle und Zieldatei wurden binär verglichen; kein alternatives Bild generiert. Ziel `src/plugin.video.xtreammate/icon.png`, Kodi-Metadaten weiterhin `<icon>icon.png</icon>`. Der Builder paketiert diese Originalbytes; Themepräferenzen ändern die Add-on-Metadaten/Originaldatei nicht. Prüfung von Source und ZIP sowie Appearance-Roundtrip ist automatisiert. Anzeige im echten Kodi-Iconcache nach direktem Update/Neustart: **NOT_TESTED**, kein Cache-Clear.

## Frische kumulative Prüfung

Vollständiger neuer Hostlauf und CI mit dem kombinierten Quellstand; keine Übernahme der alten 733 oder .21-Testzahl als neues Ergebnis. Enthalten sind die bisherigen Autoplay-/OSD-/EPG-/Playback-/Daten-/IR-Regressionen, drei zusätzliche Gruppen-Back-Fälle und drei Icon-/Datenfortbestand-/Autoplay→Stop→EPG-Live-Handoff-Fälle. Echte lokale SQLite-Dateien und Dateien, Kodi-Callbacks/GUI/Decoder als Hostmodelle. Die Player- und Artwork-Freeze-Nachweise bleiben erhalten.

Ergebnis/komplette Ausgabe: `TESTERGEBNISSE_02922.json`, `TESTLOG_02922.txt`. ZIP wird frisch aus exakt geprüften Quellen gebaut; CRC, keine doppelten/unsicheren Pfade, alle Sourcebytes, Original-Icon und unabhängige Byte-Reproduktion geprüft. Python-3.11-Grammatik wird unter Host-Python 3.12 geprüft; das ist keine ausgeführte Android-/ARM32-/3.11-Laufzeit.

Alle Android-Punkte bleiben **NOT_TESTED**, bis der echte Nutzerlauf bestätigt wird. Anleitung `ANDROID_TEST_02922_DE.md`: direkt .21 → .22, Portale/Einstellungen erhalten, Autoplay/Staffelwechsel/Stop/Schalter, EPG Startgruppe/Gruppen/Schrift/IR, Original-Icon und Neustart mit Resume/Favoriten/Artwork prüfen.

## Überholte Artefakte und offene Punkte

Der bisherige unabhängige .22-Stand `781d0a07cea791a6dffd1a4b76a58dfac627e9c5` (SHA256 `e6f3616bcbf7832f1c3f5cd1852fd853f7892a785a05e50d382e1fc28feb9ec7`) und die frühere Variante `e50849db53c1d69c9ca64ebe1f5f6331085f8e1e` (SHA256 `f38419ce2506301ea9a0d8c0a2b1b463c582a0e1ecbae42a55feb992b30d71d3`) sind **ÜBERHOLT / NICHT ALS UPDATE VON .21 INSTALLIEREN**. Alte CI-Artefakte mit diesen Prüfsummen sind keine neuen Pakete. Nur die neue kumulative Prüfsumme und der neue gepinnte ZIP-Link im aktualisierten PR #110 gelten.

Artwork-Downloadpause bleibt BLOCKED_UI / NOT_TESTED; vorhandene Bilder/Jobs nicht löschen oder neu herunterladen. #98 Quellenwahl/manuelle EPG-Zuordnung mit Vorschau und explizitem Speichern bleibt eigenständig; #58 ist nicht durch „ungeordnet“ als Dublettenbefund bewiesen. Das volle Space-Premium-Theme und externe Speicher-/Streaming-/Katalogaufgaben bleiben offen. Keine Änderungen produktiver Portal-/Start-/Mapping-/Keymap-/Nutzerdaten, keine Reset-/Import-/Löschfunktion, kein Merge/Release/OTA-Indexupdate für .22.

## Frischer Host-Nachweis dieses kumulativen Pakets

**785/785 PASS in 95.682 s**, 0 Fehler/Fehlschläge/unkontrollierte Worker-Ausnahmen. Neue Paket-SHA256: `886839ba128c36dcc716dc063b8b4c4a8a965e07f4372692b000729db517862f`. Original-Icon im ZIP bytegleich zur freigegebenen SHA256. Sämtliche .21-Autoplay-/Player-/Service- und Artwork-Dateien, produktiver Index, bestehende ZIPs und 35 fremde WIP-Dateien unverändert geprüft. Aktuelle GitHub-CI wird am finalen Commit ausgeführt und in PR #110 verlinkt. Android NOT_TESTED.

## Abschließender Dokumentationsabgleich

Während der Entwicklung kam auf main `8457896e7a6d1f575aff5024bea8daa6dc80e22e` hinzu (nur `ANDROID_TEST_49_02921_DE.md`, keine Source-/Paketänderung). Dieser Nachtrag wurde ebenfalls normal in den Draft integriert und der dortige alte .22-Sperrverweis auf den neuen kumulativen Kandidaten aktualisiert. Programmcode, Original-Icon und ZIP sind bytegleich zum frischen 785-Test-Hostlauf auf Basis `3307e00`; Source-/Teststand `eb954c2` bleibt maßgeblich. .22-Android weiterhin NOT_TESTED. CI wird am abschließenden Dokumentations-/Paketstand erneut automatisch ausgeführt und im PR verlinkt.
