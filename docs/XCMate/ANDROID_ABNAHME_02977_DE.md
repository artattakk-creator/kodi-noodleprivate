# Android-Abnahme XCMate 0.1.29.77

Alle Fälle initial **ANDROID_NOT_TESTED**. Box A nicht ändern. Auf der .76-Testbox kumulatives Pilot-Update installieren; keine Deinstallation, kein Reset. Installer 0.5.26 nicht ausführen. Keine privaten Logs/Token/Provider-Adressen öffentlich hochladen.

| Test | Ausführung / PASS-Bedingung | Status |
|---|---|---|
| P077-01 Bestand | Vor/nach Update identische Portale, Gruppen, Startsender, Favoriten, EPG-Mappings, Widgets, Sprache, Space Blue, Film-/Serienindex und Resume. Token lokal nur auf Unverändertheit vergleichen; keinen Wert übertragen. | ANDROID_NOT_TESTED |
| P077-02 Freigabe | Vorhandener Token wird ohne Neuimport benutzt. Gemeinsame Bildquellendiagnose zeigt TMDB-Verbindungsstatus und TVMaze. Bewusste Deaktivierung bleibt nach Neustart aus. Fehlender/ungültiger Token: präziser Status, keine Beschädigung. | ANDROID_NOT_TESTED |
| P077-03 Start | Ohne vorherigen Senderstart Startseite öffnen: lokale Jetzt/Danach-Daten, Senderlogos, konfigurierte Startgruppe und erste fünf. Ladefolge Live → Filme → Serien beobachten. Keine HTTP-Abfrage im Fokuscallback. | ANDROID_NOT_TESTED |
| P077-04 XMLTV | Eindeutig laufendes Programm mit XMLTV-/Providerbild ohne TMDB: richtiges echtes Bild im Hero und großen sowie Mini-EPG-Detail. Identischer anonymisierter Event-Key, Quelle und Zeitintervall. | ANDROID_NOT_TESTED |
| P077-05 Serie | Eindeutig identifizierte aktuelle Folge: eigenes TMDB, anschließend bei passendem Fallback TVMaze prüfen. Zwei geräteseitige Screenshots Hero/EPG mit Zeitstempel. Exaktes Episodenbild von gekennzeichnetem Serien-Fallback unterscheiden. | ANDROID_NOT_TESTED |
| P077-06 Film/Negativ | Eindeutiger Film mit korrektem Artwork. Mehrdeutiger Titel/News/Sport: kein fremdes Filmbild. Kein Platzhalter als Sendungsbild zählen. | ANDROID_NOT_TESTED |
| P077-07 Persistenz | Fokuswechsel, Tabwechsel, Kodi-Neustart und kurzzeitiger Netzfehler: richtige vorhandene Bilder/EPG erhalten. Erneuerung abgelaufener URL-Lease, keine 6h-Sperre nach neuer Quellenfreigabe. | ANDROID_NOT_TESTED |
| P077-08 Adapter | Diagnose muss echten Adapter/Control 296751 erkennen. Falls Zustimmung erforderlich: Einstellungen → Aussehen → Widgets → technische BINGIE-Integration, Vorschau/Sicherung prüfen, gezielt bestätigen. Unbekannte Skinversion als BLOCKED dokumentieren. | ANDROID_NOT_TESTED |
| P077-09 Layout | 720p/1080p: großes vollflächiges Bild, feste Hero-Höhe, rechte Tabelle, Jetzt/Danach/Logo/Fortschritt; genau eine aktive Leiste; korrekter Fokusrahmen bei mindestens 20 Auf/Ab-/Links/Rechts-Wechseln. | ANDROID_NOT_TESTED |
| P077-10 Serie-Exit | 20 echte Serien-Back-/Stop-Zyklen: genau ein Stop, nativer ACK, bedienbare vorherige Serie/Suche, Fortschritt erhalten. Overlays schließen nur eigene Ebene. Timeout/Freeze ist FAIL, kein Erfolg aus endenden Decoderthreads. | ANDROID_NOT_TESTED |
| P077-11 Film-Exit | Dasselbe 20-mal für Filme, auch aus Suchansicht. | ANDROID_NOT_TESTED |
| P077-12 Live-Exit | Dasselbe 20-mal Live-TV; vorhandenen .42-Kompatibilitätsmodus beibehalten. | ANDROID_NOT_TESTED |
| P077-13 Rennen | Natürliches Episodenende/Staffelwechsel/Resume, manuell nächste Folge; Back/Stop/Fehler/Kodi-Ende starten keine nächste Folge. Kein Doppelstart/fremder Playerstop. | ANDROID_NOT_TESTED |
| P077-14 Diagnose | Bildquellen-Diagnose: Event → Match → Quelle → sichere URL/HTTP → Cache → Lease → Property → echtes Control/Texture. fehlende Kodi-Views getrennt melden; keine DB-Neuanlage. | ANDROID_NOT_TESTED |
| P077-15 Kanal | Pilot bietet .77; regulär/NeoDark3 weiterhin .76; Installer .5.26. Neue Pilot-Installation als Update über bestehendes Profil. | ANDROID_NOT_TESTED |

**Freigabegate:** P0-Bilder erst PASS mit richtigen, sichtbaren Android-Bildern in Hero UND EPG plus Filmnachweis. URL_READY, Control vorhanden, Texturecache-Hit und Linux-Screenshot allein reichen nicht. P0-Exit/Layout erst nach erfolgreichen Gerätezyklen. Bei fehlenden Bildern ANDROID_FAIL erfassen, nicht warten und als PASS werten.
