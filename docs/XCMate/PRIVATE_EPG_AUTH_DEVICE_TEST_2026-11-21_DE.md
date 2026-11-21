# XCMate: privater EPG-Zugang – Gerätestart und Test

Status 21.11.2026: **Kodi-UI-Code im Featurebranch**, keine Produktionsfreigabe. Der normale private Feed
`artattakk-creator/xcmate-epg-private/manifest.json` ist derzeit `PRIVATE_PENDING`;
`xcmate-epg.xml.gz` existiert noch nicht als autorisierte reale Generation.

## Zugang sicher einrichten (pro Kodi-Gerät getrennt)

1. Als Eigentümer in GitHub unter **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens** einen **separaten** PAT pro eigenem Gerät erstellen:
   - Resource owner: `artattakk-creator`
   - Repository access: *Only select repositories* → `xcmate-epg-private`
   - Repository permissions: `Contents: Read-only` (Metadata: read implizit)
   - Ablaufdatum festlegen; kein Schreibrecht, keine Organisations- oder Konto-Vollmacht.
2. Keine PAT-Werte in Support-Chats, GitHub-Issues, ZIPs, Screenshots oder Logdateien kopieren.
3. Nach Integration des Featurebranches und geschützter Geräteinstallation in
   **XCMate → Einstellungen → EPG → XCMate EPG Agent → Privaten GitHub-Zugang eingeben**
   den PAT über die verdeckte Kodi-Eingabe einmalig hinterlegen.
4. **Token-Datei importieren (USB / interner Speicher / Netzwerk)** ist
   alternativ zur manuellen Eingabe. Eine **Textdatei**, zum Beispiel
   `xcmate-reader-token.txt`, enthält ausschließlich die eine Zeichenfolge
   `github_pat_...` als erste und einzige Zeile (optional abschließender
   Zeilenumbruch). Alternativ `{"token":"github_pat_..."}` als JSON.
   Im XCMate-Dialog Dateibrowser öffnen und Datei wählen:
   - **USB:** Android `/storage/...` bzw. das vom Kodi-Browser sichtbare Laufwerk;
     auf LG nur, wenn USB/Kodi-Berechtigungen den Pfad erlauben.
   - **Interner Speicher:** eine von Kodi zugängliche Datei.
   - **Netzwerk:** zuvor unter Kodi-Dateimanager angebundene
     SMB- oder NFS-Freigabe auswählen; SMB-Zugangsdaten nur in
     Kodis Quellenverwaltung, niemals in der Token-Datei-URL.
   Der Browser zeigt lokale Laufwerke und vorhandene Netzwerkquellen; es
   werden **keine** HTTP-, FTP- oder Plugin-URLs als Tokenquelle akzeptiert.
   Kodi liest über `xbmcvfs.File.readBytes` höchstens 1025 Byte,
   validiert das Token, speichert es atomar nur im lokalen
   `epg-agent/reader-token.txt` (Restriktion 0600 unter POSIX), danach
   erfolgt eine separate authentifizierte Statusabfrage des privaten Repos.
   Abbruch, ungültiges Format, übergroße Dateien oder Netzwerkfehler dürfen
   einen vorhandenen Token **nicht ersetzen**. Keine Datei wird in GitHub
   hochgeladen; der ursprüngliche Token auf USB/Netzwerk bleibt erhalten.
   Nicht benötigte Token-Dateien anschließend aus unsicheren Freigaben
   eigenständig entfernen; Tokens niemals weitergeben.
5. **Geschützten EPG-Serverstatus abfragen** ruft ausschließlich das authentifizierte
   Produktionsmanifest ab. `PRIVATE_PENDING` bedeutet: Server erreichbar, noch kein vollständiger
   echter EPG. `PRIVATE_READY` mit echtem Nachweis erlaubt den nächsten Importversuch.
6. Nur wenn Backend und Rechte-/Clientgates wirklich PASS sind, **XCMate EPG Agent aktivieren**
   und manuelle Aktualisierung auslösen. Anbieter-EPG bleibt unabhängig.

## Abnahmepfad für den angefragten vollständigen echten Lauf

- Backend: genau 3 berechtigte Originalquellen (EPGShare01 DE/AT, Kaimandura DE);
  **keine** künstlichen 3 Sender/84 Programme; tatsächliche Sende-/Zeithorizonte nennen.
- Verifizierter vollständiger Universal-XMLTV mit TMDB-/TVMaze-/XMLTV-Bildrollen
  sowie bestätigten Senderlogos, Artwork-Herkunft, SHA256, DTD, Mapping und LastGood.
- Private Auslieferung: Payload zuerst, authentifizierter Remote-SHA-/Bytes-Readback,
  danach Manifest zuletzt `PRIVATE_READY`; anonymer Zugriff ohne Daten.
- Geräte: eigener PAT, authentifizierter GET, EPG-Anzeige, Mini-/Groß-EPG,
  BINGIE-Hero, Detailcover, Now/Next, Neustart/Offline, manuelle Zuordnungen,
  Provider-Fallback auf Android/Kodi21 und separat LG/webOS/Kodi22.
- Beim Serverfehler, abgelaufenen Token oder defekten Payload keine lokalen
  Mappings löschen und LastGood nicht überschreiben.

**Nicht enthalten:** Ein Gerätetest, ein vollständiger Feed oder eine produktive
24h-Automatik. Für die Backend-Produktivfreigabe gilt
https://github.com/artattakk-creator/xcmate-epg/issues/14 .
