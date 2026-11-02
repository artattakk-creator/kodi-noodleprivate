# XCMate .67 – Ursachenanalyse und Grenzen

Auftrag: #307 einschließlich Nachtrag 6564804494, #291 und #300. Der Nutzer hat die Gleichheit des angehängten Mastertexts mit Issue und Nachtrag ausdrücklich bestätigt. Kumulativ ab main .66 a9a3476bc04c3624d1451dfe03899c2220138c08; Draft-PR #308. Keine Änderungen an Box A, kein Merge oder produktives Release.

## Nachgewiesene Codefehler

1. **EPG-Kerntext ging durch optionale Anreicherung verloren.** Ein Fehler im optionalen Metadaten-/SQLite-Pfad verwarf bereits erfolgreich gelesene primäre Programme. Die Reproduktion mit echter SQLite zeigte vor der Korrektur `full_block_lost=true` und `text_block_lost=true`, danach jeweils false. Der volle Guide liest zunächst alle Kerntexte und reichert danach begrenzt an. Optionale Fehler werden mit festen Codes und gehashten IDs gemeldet; keine SQL-/Exceptiontexte.
2. **Abgelaufener automatischer STREAM_ALIAS verdeckte aktuelle Provider-ID.** Ein nicht leeres Array wurde akzeptiert, obwohl es keinen Jetzt-Eintrag enthielt. Automatisch gebundene Aliase dürfen nun die aktuelle Provider-ID desselben Senders verwenden. Aktuelle Aliase und explizite manuelle Quellenbindungen behalten Vorrang.
3. **Extensionlose /live/-URLs wurden ohne Manifestbeleg als HLS/ISA behandelt.** Die Live-spezifische Erkennung richtet sich jetzt nach belegten TS/HLS/DASH-Suffixen. Unbekannte URLs gehen an Kodis nativen Demuxer. Bekannte Formate erhalten MIME und unterdrücken einen zusätzlichen spekulativen Content-Lookup. Medien-Voreinstellungen bleiben unverändert.
4. **Wiederholte Short-EPG-Fehler ohne Portal-Abkühlung.** Fehler erzeugen nun eine portalgebundene, begrenzte Abkühlung; echte Kurz-EPG-Anfragen haben keine HTTP-Wiederholung. 429 Retry-After wird auf höchstens 900 Sekunden begrenzt. Wiedergabe benötigt keine Kurz-EPG-Antwort.
5. **Eigener TMDB-Zugang hinter optionalem Helper.** Nach vorhandener ausdrücklicher Aktivierung des eigenen Zugangs wird dieser vor dem optionalen Helper benutzt. Bereits negativ gespeicherte Helperfehler dürfen gezielt einmal pro Ereignis/Profil und fünf Minuten wieder geprüft werden. Positive Bilder und Dateien werden nicht invalidiert.

## EPG-Fallback und Bestandsschutz

Primärer SQLite-Fehler bleibt im rohen Reader als Fehler erkennbar. Anzeigeverbraucher können den letzten validierten gemeinsamen RAM-Snapshot verwenden: profil-, portal-, konfigurations-, quell- und zeitgebunden, maximal fünf Minuten alt. Bei einem neuen Guide-Tag wird ausschließlich die Guide-Tag-Prüfung gelockert; manuelle Zuordnungen und die Konfigurationsrevision bleiben verbindlich. Ein Fallback wird nie mit neuer Zeit als frischer DB-Erfolg gespeichert.

Das ist keine Wiederherstellung fehlender Daten und kein unbeschränkter alter Cache. Nach einem Neustart ohne gültigen Snapshot und mit tatsächlich unlesbarer primärer Datenbank kann kein Programm erfunden werden. Bestehende persistente .66-Fallbacks und der quellenbezogene 24-Stunden-Refresh bleiben erhalten. Es gibt keinen neuen zweiten EPG-Bestand, kein N-mal-88-Importskript, kein Löschen und keinen globalen Reset.

## Wiedergabe und begrenzte Diagnose

Der Vergleich .65 → .66 zeigte bytegleiche Player-/URL-/Stopdateien. Die konkrete Android-Ursache für HTTP 504 und Demuxfehler ist deshalb weiterhin **UNCONFIRMED**. Dass derselbe Anbieter im anderen Client läuft, wird berücksichtigt und nicht als Provider-Ausfall umgedeutet.

Die drei Einstellungen für das Live-Streamformat heißen Standard (TS), MPEG-TS und HLS. Nur eine ausdrückliche Benutzerauswahl ändert das Format; kein automatisches Durchprobieren oder Doppelstart. Vorhandene ISA-Präferenz wird für Live respektiert. Der bestätigte .42-Stop-/Decoder-Modus wird nicht geändert.

Unter Einstellungen → Live-TV gibt es **Live-Stream prüfen**. Der Nutzer wählt einen Sender seiner lokal vorhandenen Startgruppe; ein begrenzter GET liest höchstens 1 KiB. Status, grobe MIME-/Präfixklasse und gehashte Senderidentität werden gemeldet. Timeout, HTML/JSON, TS/HLS, 504 und Redirect sind getrennt erkennbar. Keine Redirect-Verfolgung in dieser Diagnose, kein Credentials-Transfer an andere Hosts, kein Autoplay, kein kompletter Streamdownload. Ein Präfixtest ist ausdrücklich kein vollständiger Wiedergabenachweis.

Kodis nativer Fehlercallback darf lediglich eine generische Meldung für die noch aktuelle eigene Live-Session auslösen. Kein Stop, Retry oder Home-Routing aus diesem Callback; die konkrete HTTP-Ursache wird dabei nicht behauptet.

## Bilder und Attribution

Gemeinsamer bestehender Ereignis-/Bildcache; keine parallele Bilddatenbank. Eigener gespeicherter TMDB-Zugang, vorhandene lokale Provider-/XMLTV-Quellen, optionaler Helper und ein separat einschaltbarer TVmaze-Fallback. TVmaze ist bei Updates aus und erfordert eine eigene Aktivierung. Exakte Serienidentität mit unabhängiger Detailbestätigung, Jahr und gegebenenfalls belegter Folge; mehrdeutige Namen und fremde Bildhosts werden abgelehnt.

Guide und Mini-EPG erhalten einen gemeinsamen lokalen Vorschau-Renderer. Ein einzelner coalescing Worker liest lokale Ereignis-/Bilddaten; GUI-Fokus löst keine HTTP-Abfrage oder SQLite-Arbeit aus. Ein veraltetes Ergebnis für den vorherigen Fokus wird nicht angezeigt.

Das originale offizielle TMDB-Logo liegt als eigener UI-Layer unten rechts ausschließlich an tatsächlich lokalen TMDB-Bildern. TVmaze/Provider/XMLTV erhalten eigene Herkunftskennzeichnung. Serienbilder sind als Serienfallback gekennzeichnet. Credits enthalten Logo und exakt:
This product uses the TMDB API but is not endorsed or certified by TMDB.

Originalbild und Logo-Datei werden nicht verändert. VOD-/Serien-Metadaten und Providerposter behalten ihre bisherigen Pfade.

## Belegumfang

Früher gezielter Lauf: 19 neue .67-Hosttests PASS; die erste vollständige Vorprüfung fand den fehlenden Menü-Icon-Wrapper des Diagnose-Dialogs. Dieser ist korrigiert; der aktuelle finale CI-Lauf ist maßgeblich.

Native Linux-Kodi-Prüfungen verwenden ausschließlich eine isolierte synthetische Installation. TS, HLS und extensionlose URL, vier Produktions-Startkerne, fehlendes Short-EPG, absichtlich defekter Guide, 504 und HTML werden geprüft. Guide-Owner/Mini-Controller werden dort synthetisch bereitgestellt; Android-IR, Rockchip-MediaCodec und tatsächliche Box-B-Startwege sind damit **nicht** abgenommen. Native BINGIE-/Artwork-Regressionsprüfungen bleiben erhalten.

Aktuelle Ergebnisse und Paketprüfsumme stehen im exakten PR-CI-Artefakt, siehe TESTBERICHT_02967_DE.md. Alle echten Android-Gates bleiben NOT_TESTED. Keine privaten Rohlogs oder realen Zugangsdaten im Repository.
