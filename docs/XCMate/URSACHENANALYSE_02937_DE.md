# XCMate 0.1.29.37 – Ursachen, Änderungen und Grenzen

Basis: `origin/main` **ecf85f36537b79f88cc3dfaef0fc70b10836b848**, veröffentlichte .36. Ein neuer kumulativer Branch; keine Übernahme experimenteller Preview-Branches. Die beiden verbindlichen .37-Dokumente und der Abnahmeplan haben Vorrang. Alle Android-Aussagen zu diesem Kandidaten sind **NOT_TESTED**.

## P0 Bestandsschutz (#173)

Ein neuer XML-Default hätte auch bestehende Profile ohne Modusmarker umgestellt. `.37` liest deshalb vor jeder Dateninitialisierung den Profilzustand: jedes bereits vorhandene Profilobjekt bedeutet Legacy, auch ein leerer Bildordner oder null READY. Ein neues kleines, atomar gespeichertes `artwork_config_v1.json` hält die gerätelokale Entscheidung. Legacy bleibt intern; nur ein tatsächlich leeres, nie initialisiertes Profil beginnt dynamisch. Die Wahl wird nicht mit anderen Geräten synchronisiert. Bestehende Settings/Portale/DB/READY-Zeilen/Bildbytes werden bei dieser Initialisierung nicht umgeschrieben. Profiltests decken Box-A-ähnliche Bestände, Box B ohne READY, explizite Nutzerwahl und einen unterbrochenen Markerwechsel ab.

## P0 Ausstieg (#169, #174)

**Gesichert:** #169 betrifft Box B/.36/Kodi21.3. Der spätere All-Media-Hänger #174 hat weiterhin **unbestätigte Geräte- und Versionszuordnung**. Ohne neue private Geräteprotokolle ist weder ein gemeinsamer Kodi-Crash-Auslöser noch dessen Behebung auf Android bewiesen.

**Im Code und Host reproduziert:** `stop_owned` konnte native `Player.stop()` und den Resume-SQLite-Checkpoint direkt aus einer GUI-Aktion bzw. dem synchronen Service-Poll ausführen. Ein blockierender Stop hielt den aufrufenden Ablauf fest; SQLite-Contention verlängerte den Ausstieg. Mehrere GUI-/Service-Aktionen konnten dieselbe Session bearbeiten. Die bestehende Ownership-/Autoplay-Logik war wertvoll und bleibt Referenz.

`exit_jobs.py` veröffentlicht jetzt eine kleine sitzungsgebundene Exit-Absicht. Die GUI schließt zuerst ihr eigenes Live-Overlay und kehrt zurück. Der Service startet nach kurzer Freigabezeit einen einzelnen Stop-Worker; Stop/DB laufen weder im GUI-Callback noch synchron im Service-Watchdog. Identität wird vor dem tatsächlichen Stop nochmals geprüft. Parallelrequests derselben Session werden zusammengeführt; fremde Player werden abgewiesen. Der finale Checkpoint wartet höchstens 50 ms auf SQLite; nur dieser fehlgeschlagene Fortschritt wird maximal dreimal später versucht, ohne den bisherigen Bookmark zu löschen. Bewusster Serien-Stop sperrt vorher die Autoplay-Kette; natürliches Ende verwendet weiterhin den bestehenden Autoplay-Pfad.

Nach fünf Sekunden wird ein blockierter Stop als `STOP_TIMEOUT` gemeldet und nicht erneut gestartet. **Grenze:** ein bereits blockierter nativer Kodi-C++-Aufruf kann von Python nicht sicher abgebrochen werden. Der Worker ist daemonisiert, der Service bleibt prüfbar; dies ersetzt keine echte Android-Exit-Abnahme. Ein Sessionwechsel vor Start wird abgefangen; eine atomare Lock-Garantie über Kodi-Core und Fremdplayer existiert nicht.

Logs enthalten feste Stufen/Fehlerklassen, Medientyp, gehashten Sessionbezug und Fenster-ID; keine Stream-URL. Einstieg auf Hardware: jeweils nur ein vorsichtiger Live-/Film-/Serienausstieg, danach erst Wiederholungen.

## Artwork (#172, #106, #168, #90)

Drei ausdrücklich wählbare Modi unter **Einstellungen → Artwork-Verwaltung**:

- **Dynamisch:** vorhandene HTTP(S)-Providerbilder werden nur für sichtbare Items freigegeben. Keine neuen XCMate-Archivjobs, kein Prefetch oder Reservecheck. Begrenzte Hintergrund-DNS-Prüfung, URL-/Host-/Credential-Validierung und neutrale Platzhalter. Kodi darf weiterhin seinen eigenen Texturecache verwenden; weder null Speicherverbrauch noch erfolgreiche physische Bilddarstellung wird behauptet.
- **Intern:** bestehende Pfade, Dateischlüssel, persistente Queue und feste Reserve bleiben erhalten. Vorladen aller Cover und adaptive Reserve erfordern bewusste Benutzeraktion. Es gibt einen Pause-/Fortsetzen-Eintrag. Kein globaler Neustart fehlgeschlagener Jobs.
- **Extern:** native USB/SD-Pfade oder Kodi-SMB-VFS. Unter dem ausgewählten Ziel entstehen `XCMate/Artwork/{media,logos,fanart}/<Profil-ID>`. Der zusätzliche Profil-Namensraum verhindert Kollisionen mehrerer Boxen. SQLite/Queue/EPG/Portale bleiben lokal.

Ein gemeinsamer Writer-Gate verhindert Modus-/Migrationswechsel während Bildschreibvorgängen. Externes Nachladen prüft Zielverfügbarkeit vor Jobübernahme. Offline wird weder auf intern zurückgefallen noch READY massenhaft gelöscht. GUI-Listenzeilen erhalten externe Pfade erst nach asynchroner Prüfung; langsames SMB blockiert den GUI-Callback nicht.

### Grenzen dynamischer Kodi-Bilder

HTTP-Weiterleitungen werden für zugelassene dynamische URLs mit Kodi-Transportoption `redirect-limit=0` deaktiviert; Timeout und HTTP-Fehlerbehandlung sind gesetzt. Die Unterstützung wurde im originalen `CurlFile.cpp` von [Kodi21.2](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/filesystem/CurlFile.cpp) und [Kodi21.3](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/filesystem/CurlFile.cpp) geprüft. Optionen mit Credentials/Host-Manipulation werden nicht aus Provider-URLs übernommen. Auch Hostnamen müssen beim Hintergrundcheck ausschließlich öffentliche Adressen liefern.

**Grenzen:** Kodi führt den Bildtransport aus; Python sieht dessen TLS-/HTTP-Antworten nicht direkt. Ein freigegebener URL-Status bedeutet keine heruntergeladene/gerenderte Datei. Kodis Transport bietet hier keine DNS-Pinning-Schnittstelle; DNS-Rebinding zwischen Vorprüfung und Transport ist daher nicht vollständig ausgeschlossen. Redirect-abhängige oder abgelaufene Providerbilder bleiben mit Platzhalter sichtbar und müssen auf Android diagnostiziert werden. Kein automatischer TMDb-Ersatz wurde ergänzt.

### Migration und Löschschutz

Explizite Schritte: Ziel → eigene Schreib-/Lese-/Bildprobe → Inventur → Kopieren in Batches → Größen-/SHA256-/Bildheader-/Dimensionsprüfung jeder Datei → vollständiger Mengen-/Hashvergleich → Kodi-Darstellung vom Nutzer bestätigen → separat aktivieren. Das neue interne Transferjournal speichert Fortschritt und lässt Unterbrechungen fortsetzen. Vor der Aktivierung werden neu hinzugekommene Quelldateien berücksichtigt. Kollisionsschutz überschreibt keine abweichenden Zieldateien. SMB benutzt ausschließlich VFS und geprüfte Commit-Marker statt behaupteter POSIX-Atomizität. Symlinks/Traversal/URL-Zugangsdaten werden zurückgewiesen.

Die Python-Bildprüfung prüft Header und Dimensionen, nicht sämtliche Pixel einer Datei. Die echte Dekodierung/Darstellung erfolgt für die ausgewählte Zielprobe über Kodi und muss separat vom Benutzer bestätigt werden; Android-Rendering bleibt NOT_TESTED. SHA256 belegt die identische Kopie aller vorhandenen Bildbytes.

**Originale bleiben erhalten.** Erst nach aktivierter, erneut vollständig geprüfter Migration gibt es eine weitere Aktion mit zwei Bestätigungen. Sie darf ausschließlich zugeordneten internen Bildbestand entfernen. Gemeldet werden getrennt gelöschte Bildbytes und tatsächlich gemessener freier Dateisystemplatz; zeitgleiche Fremdschreibvorgänge können die Differenz beeinflussen. Kodi-Thumbnails, Texture-DB und sämtliche Katalog-/EPG-/Portal-/Resume-DBs sind ausgeschlossen. Rückwechsel erfolgt bewusst mit derselben Kopier-/Verifikationsstrecke, niemals automatisch bei Offline.

### Speicherdiagnose

Box B `531 < 1024 MiB` belegt eine **Reserveblockade**, keinen bewiesenen physischen ENOSPC. Dynamisch benötigt kein XCMate-Archiv. Externe echte Mounts verwenden ihre eigene Kapazität; SMB ohne Kapazitätsauskunft bleibt UNKNOWN mit kontrollierten Schreib-/Readbacktests. Ein extern benannter Ordner auf derselben internen Partition behält die interne Reserve. Eine kleine lokale Metadatenreserve bleibt auch extern geschützt. Budget, Reserve, physischer Schreibfehler, Netzwerk und Queue werden getrennt ausgewiesen.

## Wizard, Gruppen und Geräte

Wizard-Worker halten nur Daten-/Abbruch-/Statusobjekte, keine Referenz auf das geschlossene native Fenster. Save/Copy/Verify/GUI-Close/Freigabe/Home erhalten feste Diagnosephasen. Home wird erst nach tatsächlicher Fensterfreigabe und ohne fremdes Modal angefordert. Parallele Roots während Setup werden abgefangen. Legacy-Profile starten den Wizard nicht erneut. Vier EPG-Quellen melden ab Beginn ihren echten Status; unbekannte Dauer zeigt Aktivität statt erfundener Prozent. Originalicon und Original-Space-Hintergrund werden referenziert.

Nachträgliche Xtream-Gruppenwahl erzeugt eine persistente, begrenzte Delta-Arbeitsliste. Import und Datensatzfilter sind auf die zusätzlich gewählte Gruppe beschränkt, auch wenn ein Provider alle Gruppen zurückliefert oder alte Gruppen älter als zwölf Stunden sind. Alte Gruppen werden nicht neu geladen. Fehlender erfolgreicher Katalog-Head wird als Fehler/Pending behandelt, nicht als „leere Quelle“. Der Service wiederholt maximal drei Versuche. Bereits vorhandene Indizes lösen beim Upgrade keinen Bootstrap-Vollscan aus.

Geräteinformationen lesen reale RAM-/CPU-/SDK-/Kernel-/Kodi-/ABI-/Prozess- und Dateisystemwerte, trennen gemeldete Firmware und tatsächliches API-Level und kennzeichnen Werbeangaben als unverifiziert. Fehlende GPU-/SMB-Kapazitätsdaten bleiben UNKNOWN. Keine privaten Pfade, Kontodaten oder Hostnamen im Bericht. Optionaler Datei-Export der Geräteinfos wurde nicht ergänzt; die Ansicht ist verfügbar.

## Startgeschwindigkeit (#170)

Der installierte Home-Pfad erstellt dieselben sechs Menüpunkte, Assets und einmaligen Directory-Abschluss ohne Import des großen Routers. Andere Aktionen und leere Profile verwenden weiterhin den vollständigen Router. Autoplay-Policy wurde als gemeinsame unveränderte Entscheidung extrahiert. Kein Netzwerk-, Katalog-, Guide- oder Hardware-Scan im Home-Aufruf. `HOME_SUBMITTED` bedeutet Directory-Abgabe, nicht physische IR-/Renderbereitschaft. Kalte Host-Prozessmesswerte stehen separat in `HOST_MESSWERTE_02937.json`; die 27 Sekunden von Box B werden dadurch nicht als behoben erklärt.

## Ausdrückliche Blocker

| Teil | Status und Ursache | Sichere Nacharbeit / Test |
|---|---|---|
| Physischer Metadaten-Offload #171 | **BLOCKED**. Verifizierter, redigierter Export und Lesen/Offline-Verhalten sind implementiert. Der lokale Suchindex bleibt vollständig; keine internen Payloads werden entfernt. Keine behauptete Platzersparnis. | Versionierte DB-Payload-Migration mit Wiederanlauf/Rollback und realem Speichervergleich separat entwickeln. META-02. |
| Ungespeicherten Wizard-Scan nach Prozessende fortsetzen | **BLOCKED**. Save-Transaktion und Laufzeit-Cancel sind geschützt; bisheriges temporäres Scan-Staging wird nicht als haltbares Restart-Journal umgedeutet. | Eigenes Draft-Journal mit Versions-/Credentialreferenzen und Crash-Injection entwickeln. WIZ-02 plus Prozessabbruch im isolierten Profil. |
| Android-Exit/Bestandsschutz/Rendering/USB/SMB | **NOT_TESTED, Freigabe blockiert**. Keine Nutzerbox wurde verbunden oder verändert; Python kann nativen Kodi-Stop nicht erzwingen. | Vollständiger verbindlicher Abnahmeplan, Box A/B getrennt. SAFE/EXIT zuerst, echte Medien/NAS erforderlich. |

Keine Downloads-/Aufnahme-Reparatur, kein Player-Rewrite, keine Keymaps, kein Reset, keine automatische Installation, kein Merge/Release und keine Issue-Schließung.
