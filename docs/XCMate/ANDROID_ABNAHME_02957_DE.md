# XCMate .57 – Box B / TMDb Helper

**Gerätezugriff hier: BLOCKED_DEVICE_ACCESS. Acht Android-Gates: NOT_TESTED.** Kein ADB-/SSH-/Kodi-Endpoint, keine private Route oder Anmeldedaten eingerichtet. Nutzerbestätigung „Helper installiert“ bleibt erhalten; eine ausgelesene Version oder erfolgreiche Bildanzeige wird nicht behauptet. Box A nicht verwenden.

## Kurzer regulärer Test ohne zusätzliche API-Konfiguration

1. ZIP/SHA256 prüfen und .57 als Update über die bestehende Box-B-Installation installieren, keine Neuinstallation/Resets. Bestätigen: Installationspopup mit .57 und den neuen Änderungen. Der Draft veröffentlicht keinen regulären Repository-Updateindex.
2. Der bereits installierte **TMDb Helper** muss aktiviert sein. Für XCMate **kein eigenes TMDb-Konto/Token** eintragen. Die neue Option unter dem bestehenden EPG-Einstellungsbereich ist standardmäßig an. Einen vorhandenen eigenen Token für den Test nicht öffentlich anzeigen; vorhandene Einstellungen nicht löschen. Optionales Abschalten des direkten XCMate-TMDb-Zugangs ist eine bewusste Nutzeraktion; für den tokenfreien Nachweis muss der Erfolg tatsächlich aus `tmdb_helper` stammen.
3. Zuerst Live-TV-Zurück und Navigation/Settings testen. Bestehende Widgetbindungen unter **XCMate → Widgets** unverändert nutzen, nicht neu einrichten.
4. Den normalen Hintergrunddienst abwarten: ruhige Startbaseline mindestens 60 Sekunden, danach kleine rotierende Startgruppen-/NOW/NEXT-/Zukunftsbatches. Große Startgruppen und Netzwerkfehler können mehr als einen Umlauf benötigen. Nicht wiederholt Details öffnen, um angeblich eine Suche auszulösen: Fokus/Details starten keine Metadatensuche.
5. Einen real vorhandenen Film im großen EPG wählen. Pflichtfall Harry Potter und die Kammer des Schreckens (2002), sofern noch im aktuellen lokalen Feed. Bekannte korrekte TMDb-Film-ID **672**. Andernfalls einen äquivalenten echten Film dokumentieren, kein erfundenes EPG-Ereignis. Im Detail echtes Bild und Quelle/Credit prüfen. Gleichheit zum Hero gilt nur für dieselbe tatsächliche Sendung, nicht für ein anderes NOW-Ereignis.

## Optionaler ausführbarer Zugangstest

Normaler XCMate-Betrieb verwendet intern `xbmc.executeJSONRPC`; ein offener HTTP-Server ist **keine Voraussetzung** der Bildfunktion. Nur für einen ausdrücklich gewünschten externen Test auf Box B: Kodi → Dienste → Steuerung, HTTP-Steuerung mit eigenem Kodi-Benutzer/Passwort und erreichbarem autorisiertem LAN-/VPN-Pfad einrichten. Keine IPs raten/scannen, keine Freigabe von Box A, keine Credentials öffentlich posten. Diese Sitzung hat dafür derzeit keinen Zugang.

Auf einem eigenen Rechner mit Python 3 und dem .57-Quellbaum, optionaler authentifizierter Zugriff über die Umgebungsvariablen `XCMATE_KODI_USERNAME` und `XCMATE_KODI_PASSWORD` (Werte nicht im Kommando/GitHub veröffentlichen):

```sh
python3 tools/probe_xcmate_helper57.py --box-b \
  --endpoint 'http://BOX-B-ADRESSE:KODI-PORT/jsonrpc' \
  --report helper57-film.json
```

Bekannte reale Serienepisode gesondert prüfen:

```sh
python3 tools/probe_xcmate_helper57.py --box-b \
  --endpoint 'http://BOX-B-ADRESSE:KODI-PORT/jsonrpc' \
  --title 'EINDEUTIGER SERIENTITEL' --year 2011 \
  --season 1 --episode 1 --subtitle 'EXAKTER EPISODENTITEL' \
  --report helper57-episode.json
```

Platzhalter durch eigene bekannte Werte ersetzen. Für HTTPS eigene vertrauenswürdige CA bei Bedarf über `--ca-file` angeben; TLS-Prüfung nicht abschalten. System-/Proxy-/Zugangsrichtlinien bleiben erhalten. Keine automatischen Installationen oder Einstellungen, nur Add-on-Erkennung und die öffentlichen Such-/Detailsverzeichnisse; keine Wiedergabe-/GUI-Kommandos. Bestehende Reportdateien werden nicht überschrieben. Report enthält keine Endpointadresse, Passwörter, Rohantworten, privaten Titel oder tatsächliche Bild-URL, sondern Version, öffentliche TMDb-ID/Jahr, Bildumfang und URL-Hash. Eine korrekte Metadatenantwort bleibt **kein** EPG-Persistenz-/Pixel-/Android-PASS. Während des Tests nicht selbst navigieren, damit GUI-/Playervergleich aussagekräftig bleibt.

## Abnahmebogen

| Gate | PASS nur bei tatsächlicher Beobachtung | Status |
|---|---|---|
| H57-01 | Helper auf Box B installiert/aktiv, tatsächliche Version festhalten; .57 erhält darüber sichere Identität/Artwork ohne XCMate-Token und ohne Tastaturdialog/Fenster-/Playerwechsel. Optionalen Probebericht beilegen. | NOT_TESTED |
| H57-02 | Reales EPG-Ereignis Harry Potter (2002, ID672) oder gleichwertiger echter Film. Quelle `tmdb_helper`, korrekte Identität/Jahr, echtes passendes Backdrop oder Poster **sichtbar im EPG-Detail**, kein Platzhalter. Screenshot mit Uhrzeit, keine privaten Adressen. | NOT_TESTED |
| H57-03 | Detail und freigegebener vorhandener Hero zeigen bei **derselben** Event-ID exakt dieselbe gespeicherte URL und dasselbe Bild. Bei Zukunftsfilm bleibt aktuelles NOW-Bild bis Sendebeginn korrekt; nach Wechsel neues Bild. Falls kein Hero-Skinadapter separat freigegeben ist, Teilprüfung nicht ausführen/weiter offen lassen; keinen Skin patchen. | NOT_TESTED |
| H57-04 | Echte Serie, richtige Staffel/Folge/Showtitel. Richtiger Episodenstill; andernfalls sichtbar als **Serienbild (kein Episodenbild)** gekennzeichnet. Kein Parentposter als angeblich exakter Still, keine andere Episode. Detail/Hero-Quellenbeleg vergleichen. | NOT_TESTED |
| H57-05 | Kodi normal neu starten. Bereits vorbereitete URL bleibt im privaten Index; Detail/Fokus/Home keine neue Metadatensuche. Direkter Kodi-CDN-Bildabruf erlaubt. Kein Profil-/Cacheeingriff. | NOT_TESTED |
| H57-06 | Helper bewusst nur auf Box B vorübergehend deaktivieren/anschließend wieder aktivieren oder normalen Netzverlust beobachten: kein Installationsdialog, Freeze oder Playerstart, fester Fehlercode und ehrlicher Fallback. Abbruch/Timeout, fehlendes Bild/mehrdeutiger Titel und bestehendes manuelles EPG-Mapping prüfen. Keine Rohdaten-/DBmanipulation nötig; negative TTL/Backoff abwarten. | NOT_TESTED |
| H57-07 | Vollständige Live-Startgruppenreihe (88+ Sender), vorhandene Film-/Serienwidgets/Cover/Klickziele, Navigation/Back, EPG, Suche, Favoriten, Autoplay/Resume bleiben funktionsfähig. Bestehende Portale/Passwörter/Gruppen/Zuordnungen erhalten; Wizard #269 nicht neu testen/umbauen. | NOT_TESTED |
| H57-08 | Kein eigener XCMate-TMDb-Token für den erfolgreichen Helperfall verwendet. Quelle/Credits sichtbar; kein Lesen/Export von Helper-Credentials. Keine privaten Kodi-Rohlogs veröffentlichen. Box A unverändert, kein Skin-/Keymap-/Profilschreibzugriff durch Testkandidat. | NOT_TESTED |

Nur anonymisierte feste PROGRAMME48-/Helpercodes, Counts/Dauer, reale Version und URL-/Event-Hashgleichheit dokumentieren. Ein GUI-Screenshot beweist sichtbare Pixel; eine Host- oder Probe-URL allein nicht. Ergebnisformat `Gate | PASS/FAIL/NOT_TESTED | Uhrzeit/Beobachtung`. Bei Hänger abbrechen und Zeitpunkt sichern, keine weiteren Belastungszyklen erzwingen. Kein Merge/Release und keine Issue-Schließung ohne ausdrückliche Nutzerfreigabe.
