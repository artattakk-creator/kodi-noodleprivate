# XCMate 0.1.29.77 – Verbindlicher Änderungsauftrag

> **Neuer Stand nach Installation von .76 (06.11.2026):** Der Nutzer bestätigt weiterhin fehlende Sendungsbilder auf Android. Diese Beobachtung hat **Priorität P0 und Status FAIL**. Der bisherige Wartestatus für .77 ist aufgehoben: Codex soll **.77 auf Basis von .76 jetzt umsetzen**. Maßgeblicher [neuer Codex-Startauftrag](./CODEX_START_02977_BILDER_FIRST_2026-11-06_DE.md). Installer .5.26 bleibt eingefroren.


> **AKTUELLE FREIGABE (06.11.2026) – ERSETZT DIE OBEN BZW. UNTEN STEHENDEN PILOT-ONLY-VORGABEN FÜR .76:** Der Nutzer hat XCMate **0.1.29.76 ausdrücklich auf ALLEN Installationszugängen** freigegeben. Veröffentlicht über [PR #382](https://github.com/artattakk-creator/kodi-noodleprivate/pull/382), Release-Commit `b0b43a254cde7c07e2bc20310d587891484191c8`. Reguläres GS Media `addons.xml` = .76; GS Media Pilot `online-test/addons.xml` = .76; NeoDark3-Direkt-ZIP = .76. Alle ZIPs sind identisch (SHA256 `c6b3813a6b2e9289251d3e14ea8425e0fe3fb35ee9a01dda457aa81a27e081cc`). **ANDROID_NOT_TESTED**, keine Behauptung bestandener Geräteabnahme. Zuerst .75→.76 auf der Android-Box testen; 0.1.29.77 **ausgesetzt** bis zur Auswertung. GS Media Installer 0.5.26 und TMDB-Token unverändert lassen.


> **NEUE NUTZERENTSCHEIDUNG (06.11.2026) – GILT VOR ALLEN .77-ANWEISUNGEN IN DIESEM DOKUMENT:** Erst XCMate **0.1.29.76 auf Android testen**. Der Quellcode wurde bereits in [PR #370](https://github.com/artattakk-creator/kodi-noodleprivate/pull/370) nach main gemergt; das unveränderte geprüfte ZIP ist nach [Release-PR #381](https://github.com/artattakk-creator/kodi-noodleprivate/pull/381) **jetzt im GS Media Pilot** veröffentlicht ([Download .76](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.76.zip), SHA256 `c6b3813a6b2e9289251d3e14ea8425e0fe3fb35ee9a01dda457aa81a27e081cc`). **Die zuvor dokumentierte direkte .75→.77-Installation und die unmittelbare .77-Umsetzung sind ausdrücklich AUSGESETZT, nicht mehr zur Ausführung freigegeben.** Zuerst .75→.76 auf der Testbox installieren und die dort verbleibenden Fehler erfassen; danach den Umfang einer möglichen .77 neu festlegen. Regulärer Kanal unverändert .74; Installer 0.5.26 weiterhin eingefroren. Android-.76-Abnahme steht aus.

Datum: 06.11.2026 · Status: **AUFTRAG ERFASST / NOCH NICHT IMPLEMENTIERT**

**Masterticket:** [GitHub #380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380)

**Neuer verbindlicher Codex-Einstieg:** [CODEX_UEBERGABE_02977_KUMULATIV_2026-11-06_DE.md](./CODEX_UEBERGABE_02977_KUMULATIV_2026-11-06_DE.md). Die reale Android-Box hat laut Log XCMate **0.1.29.75**, während die bereits nach \`main\` gemergte Codebasis **0.1.29.76** ist. **Codex muss alle .76-Änderungen kumulativ in .77 übernehmen; .76 wird NICHT separat auf Kodi installiert.** Neues Pilot-ZIP \`0.1.29.77\` zunächst ausschließlich im Testkanal; regulärer Kanal .74 bis zur ausdrücklichen Freigabe unverändert. Source-Merge nach grünem CI erwünscht. Bestehenden TMDB-Token nicht verändern. Installer 0.5.26 bleibt eingefroren.


## Nutzerentscheidung

Die Installationsroutine **GS Media Installer 0.5.26 ist erfolgreich durchgelaufen und wird eingefroren**. Alle Folgearbeiten betreffen ausschließlich `plugin.video.xtreammate` (XCMate), kumulativ auf Source-Version `0.1.29.76`. Kodi-Profile, vorhandene Sender-/EPG-/Widget-Einstellungen, SkinShortcuts, Space Blue und der bestehende TMDB-Read-Access-Token sind vollständig zu schützen.

Der Nutzer meldet am 06.11.2026 erneut einen Freeze beim **Verlassen einer Serie** (neuer Fall; kein zugehöriger Log). Außerdem fehlen weiterhin real sichtbare EPG-Bilder und der vergrößerte BINGIE-Hero ist nicht zufriedenstellend eingebunden. Drei separate Freischaltungen für Bildquellen werden ausdrücklich nicht akzeptiert.

## P0-1 – Serielles/Film-/Live-Playback sicher verlassen

**IST:** In der älteren Android-.74-Logserie [#368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368) ist ein spezifischer Live-TV-Back-Stop dokumentiert: `USER_BACK` → `NATIVE_STOP_POSTED` → `STOP_TIMEOUT` / `NATIVE_QUEUE_UNRETURNED`, native Stop-Barriere ohne ACK. **Der nun gemeldete Serien-Hänger darf nicht ohne Logs mit diesem Live-Fall gleichgesetzt werden.**

**SOLL:** Für `series`, `movie/vod`, `live` ein konsistenter, sessiongebundener Stop- und Rückkehrvertrag mit genau einem Stop pro Player-Eigentümer. Kodi-Playerzustand, Stop-Intent, native Queue/ACK, OnStop/EOF, Autoplay, OSD, Zurück und Ziel-Fenster getrennt prüfen. Keine Endlosschleife oder blockierende GUI-Wartezeit. Return erst nach bestätigtem Stop; bei nicht quittiertem Stop ein sauber diagnostizierbarer Schutzfall, kein erfundener Erfolg. Wiedereinstieg in vorherigen XCMate-Kontext ohne Verlust von Staffel-/Episoden-Fortschritt. Rückwärtskompatibilität zum .42-Exit-Kompatibilitätsmodus.

**Referenzdateien:** `native_stop41.py` (nur Live), `live_exit.py`, `exit_jobs.py`, `playback_exit.py`, Serien-Autoplay-/Navigator-Routinen. Separate Android-Stop-/Decoder-/AudioSink-Diagnose auf RK3528. Tests: mindestens 20 wiederholte Stop-Rückwege je Medientyp, OSD/Back, Folgeepisode, EOF/Netzstörung, Fremdplayer-Schutz. Keine Roh-URLs/Token/Providerdaten im Log.

## P0-2 – Bildquelle automatisch, aber kontrolliert

**Verbindliche Prioritäten:**
1. Verifiziertes, zur aktuellen EPG-Sendung passendes **XMLTV- bzw. Provider-Bild** automatisch übernehmen (kein TMDB-Token erforderlich).
2. **Spielfilm:** bei bereits importiertem gültigen Token eigene **TMDB**-Bildermittlung; eindeutige Titel-/Jahr- oder sicher nachgewiesene Filmidentität.
3. **Serie/Episode:** eigene TMDB-Suche mit vorhandenem Token und **TVMaze standardmäßig als Serien-/Episoden-Fallback** mit verifizierter Titel-/Episodenidentität. TVMaze nicht als verlässlichen Film-Provider behaupten.
4. Weitere freigegebene Kodi-/lokale Quellen nur bei gültiger Identität. Kein willkürliches oder falsches Artwork bei Sport, News, Talk, mehrdeutigen Titeln und fehlender Episodenidentität.

**Freigabe-UX:** Nutzer hat für seine Installation die automatische Aktivierung bereits ausdrücklich beauftragt. Ein *gültiger* TMDB-Import aktiviert zugleich die verknüpften Lookup-Einstellungen `programme_tmdb46` und `tmdb_research43`; die bereits vorhandene, valide Token-Installation wird per einmaliger autorisierter Migration aktiviert, ohne erneuten Import. Für TVMaze `programme_tvmaze67` nach einmaliger verständlicher Information standardmäßig als Fallback an, eigenständiger Opt-out jederzeit möglich. Ein ausdrücklich manuell vorgenommener Opt-out muss Bestand haben; kein ständiges Reaktivieren beim Start. Fremddienst-Abfragen nur nach zulässiger Nutzerfreigabe, mit klarer Quellenanzeige.

**TMDB-Token-Schutz – striktes P0:** vorhandene Token-Datei und ggf. Legacy-Kodi-Einstellung nicht ändern, löschen, überschreiben, umbenennen, zurücksetzen oder erneut hochladen. Read-only Gültigkeits-/Fingerprint-Prüfung vor/nach dem Update. Token niemals in GitHub, in Diagnosen oder in Kodi-Logs ausgeben, keine Token-Bytes aus Box in CI kopieren. Ungültiger Token → eindeutiger Status, keine unberechtigten Anfragen. Kodi-Profile und Geräte-Konfigurationen nicht neu initialisieren.

**Warum heute defekt:** `programme_settings68.py` verwendet Default `False` für beide TMDB-Flags sowie für TVMaze. `tmdb_access61.imported()` aktiviert die TMDB-Lookups bislang nur für Importvariante `choice==6`. `programme_art46.enqueue()` kann ohne TMDB-Freigabe und ohne direkte XMLTV-/Providerbild-URL frühzeitig `NO_IMAGE` für 6 Stunden setzen, auch wenn andere autorisierte Fallbacks existieren. Andere URL-/Renderer-Pfade können unabhängig blockieren: `programme_urls55`, `programme_image69`, `programme_requests68`, `hero_epg63`. Diese Ursachen dürfen nicht durch blindes globales Allowlisting oder falsche Bilder überspielt werden.

## P0-3 – Bilder wirklich anzeigen und BINGIE-Startseite reparieren

- EPG-Quelle → Event-Fakten → Artwork-Matching → sicherer Bildhost/HTTPS/Redirect/Content-Type → lokaler Cache/URL-Lease → Event-ID/Profil/Gültigkeit → **tatsächlich sichtbare Textur** in Mini-EPG, Groß-EPG-Details und BINGIE-Hero nachweisen.
- Ein einziges Event teilt sich dieselbe gültige Bildreferenz. Fehlende Bildquelle transparent mit Sender-Fallback statt falschem Filmbild. Negative Caches nach Änderung einer Bildfreigabe gezielt revalidieren, positives Artwork erhalten.
- **Vergrößerter stabiler Hero**, vollflächiges laufendes Sendungsbild, Senderlogo und feste Jetzt-/Danach-/Fortschritts-Informationen. Darunter genau eine kompakte horizontale aktive Sender-/Coverleiste. Fokusrahmen exakt an der fokussierten Kachel, nie nach unten versetzt oder in andere Zeilen ragend; kein Schrumpfen/Abschneiden beim Scrollen.
- Priorität: lokales EPG + Startgruppe → Logos/Now/Next/Hero/sichtbare fünf Sender → Filme → Serien → restliches Artwork. Kein HTTP oder schweres SQL im Kodi-UI-Thread. Native Home-Bindings und echter Texture-Nachweis auf Kodi 21.3/Android, nicht nur synthetische Hostdaten.
- Ein **einziger verständlicher Bildquellenstatus** in den XCMate-EPG-Einstellungen mit Quelle, Token vorhanden/gültig, aktiviert/deaktiviert, Matching, Fetch, Cache, Skin-Bindings – Statuscodes ohne URL oder Geheimnisse. Keine drei separat zu betätigenden Schalter.

## Test- und Veröffentlichungs-Gates

1. Bei bestehendem gültigem TMDB-Token aus früherem Import: vor/nach Update identischer tokenfreier Fingerprint und Gültigkeitsstatus; TMDB-Bildsuche aktiviert ohne neues Importieren. Alle Importvarianten und expliziter Opt-out getestet.
2. TVMaze bei eindeutiger Serie aktiv und als Fallback funktional; gültiges XMLTV-/Providerbild funktioniert auch ohne TMDB; Film-Suche über TMDB; unklare Episoden/News liefern keine falschen Bilder.
3. Nach vorherigem `NO_IMAGE` kontrollierte neue Suche bei Freigabe, korrekte Event-ID, Quelle und lokale Persistenz; gleiches echtes Bild im EPG und Hero. Hosttests + sichtbarer Android-Screenshotnachweis.
4. Serien-Exit nach Kodi-Stop/ACK zuverlässig zurück (20× auf Android), Filme und Live ebenso. Bei fehlendem ACK genaues, nicht blockierendes Fehlerverhalten belegt.
5. Keine Datenlöschung, kein Zurücksetzen, kein Downgrade; XCMate **0.1.29.77** zunächst nur **GS Media Pilot**, regulärer Kanal erst nach ausdrücklich bestandener Geräteabnahme und Freigabe. **Installer 0.5.26 bleibt eingefroren.**
6. Ohne bestätigte Android-Tests **ANDROID_NOT_TESTED / ANDROID_FAIL**, keine falsche PASS-Meldung. Build/CI/ZIP-SHA/Quellvergleich dokumentieren.

## Codex-Kurzstart

> GitHub-Repository `artattakk-creator/kodi-noodleprivate`, Issue #380 und diese Datei lesen. Die kumulative XCMate-Version 0.1.29.77 auf .76 bauen. Priorität: Serien-Exit-P0, automatische EPG-Bildquellen mit unverändertem TMDB-Token und TVMaze-Fallback, echter BINGIE-Hero-/Fokus-/Artwork-Nachweis. Installer 0.5.26 NICHT ändern. Änderungen samt Regressionen, Privatdatenschutz, CI und Geräteabnahme dokumentieren. Pilot-Paket erst nach Hosttests bereitstellen; regulären Kanal nicht vor Gerätefreigabe verändern.

### Referenzen
- [Master-Issue #380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380)
- [Event-Bilder #366](https://github.com/artattakk-creator/kodi-noodleprivate/issues/366)
- [Hero/Fokus/EPG #367](https://github.com/artattakk-creator/kodi-noodleprivate/issues/367)
- [Live-TV-Stop/ACK #368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368)
- [XCMate .76 PR #370](https://github.com/artattakk-creator/kodi-noodleprivate/pull/370)


## Lognachtrag 06.11.2026 – private Android-Abnahme (XCMate 0.1.29.75)

Diese Ergänzung basiert auf zwei **privat übermittelten**, vollständig ausgewerteten Kodi-Dateien mit insgesamt 53.655 Zeilen: erster Start 17:51:53–21:27:45 und zweiter Start 21:28:07–21:30:12. Die Rohdateien enthalten vertrauliche Geräte-/Netzwerk-/Providerinformationen und dürfen **nicht** auf GitHub gespeichert werden. Es werden nur anonymisierte Prozessmeldungen und Aggregatzahlen dokumentiert. Der öffentliche, detailliertere sanitizierte Logbefund steht als Kommentar in Master-Issue #380.

### A. Serien-Exit / Player-Stop konkret belegt

**21:24:34.287** \`[PLAYER_EXIT] EXIT_INTENT reason=USER_BACK kind=media\`. **21:24:34.574** Fortschrittssnapshot \`DONE\`; **21:24:34.576** \`PLAYER_STOP_START\`; **21:24:34.762** \`VideoPlayer: waiting for threads to exit\`. Kodi meldet anschließend das Ende der Audio- und Video-Threads, aber **nicht** \`VideoPlayer: finished waiting\` und XCMate nicht \`PLAYER_STOP_DONE\`. 21:27 Socket-/JSON-RPC-Serverfehler, neuer Kodi-Start ab 21:28. Dies stützt den gemeldeten Freeze beim Medien-/Serien-Exit; **genaue Native-Thread-Ursache bleibt unbewiesen**. Am selben Abend **21:10:25** war ein Live-TV-Stop via \`STOP75 ACK\` in ca. 2.029 ms nachweislich erfolgreich. Codex: Media- und Live-Routen getrennt untersuchen; kein Stop-ACK-PASS allein aufgrund endender Decoderthreads.

### B. EPG und Bildquellen

Im langen Log **18.145** \`EPG63 DB_READ\`-Einträge: **16.935** \`EPG_DATA_MISSING\`, **729** \`READY\`, **444** \`EPG_CACHE_UNAVAILABLE\`, **37** \`EPG_DB_BUDGET\`. Überwiegend Provider-ID-Mapping ohne Daten, einige Stream-Alias-Einträge dagegen \`READY\`. Das sind wiederholte Abfragen, nicht 16.935 individuelle Programme. Klärung von Quellabdeckung, Sender-Matching, DB-Budgets und 24-h-Cachevorgaben ist P0.

\`PROGRAMME68\`: **636** \`BLOCKED_IMAGE_HOST_OR_URL\`, **1.064** \`AWAITING_BACKGROUND_REFRESH\`, **79** \`FETCH_FAILED\` und nur **22** \`IMAGE_URL_READY\`. \`ART70\`: **57** \`NO_CONFIRMED_IMAGE\`, **1** \`FOUND\`. Der beobachtete 24er-Filmwidget-Lauf enthält **24 Platzhalter**, 0 lokale bzw. gematchte Bilder. Bereits im kurzen neuen Log stehen weitere \`EPG_CACHE_UNAVAILABLE\` und blockierte Bild-URLs. Sichere URL-Akzeptanz *gezielt* reparieren, nicht alle Hosts freigeben, und erfolgreiche Referenzen bis zum sichtbaren Kodi-Texture-Control verfolgen.

### C. BINGIE Home / Kodi-Datenbank

\`HOME75 RENDER_CONTROL_MISSING\` **24×**, \`FOCUS_OVERRIDE\` **3×**: Vorhandensein/Aktivierung der spezifischen XCMate-Hero-Skin-Controls samt 1080p-Geometrie und Fokusrahmen prüfen. Ein installiertes Space-Blue-Manager-Add-on ist kein Nachweis für einen aktiven XCMate-Home-Patch.

Kodi \`MyVideos131.db: no such table: movie_view\` **20×** im langen und **8×** im kurzen Log. Datenbankschema/Views als unabhängige Kodi-Fehlerquelle untersuchen; **kein destruktives DB-Löschen** ohne Datensicherung und Ursachenprüfung.

### D. Versions- und Bestandsbeleg

Beide Kodi-Starts melden **\`plugin.video.xtreammate 0.1.29.75\`** sowie **\`skin.titan.bingie.mod 2.2.3\`**. Der Brand-Manager 0.2.0 ist installiert, die Patch-Aktivität selbst dadurch nicht nachgewiesen. Der Installer ist im historischen ersten Start als 0.5.21 und im zweiten als 0.5.22 verzeichnet; diese Logdateien sind **kein Gerätebeleg für .5.26**, ändern aber nicht dessen vereinbarten Freeze. Ein TMDB-Tokenwert/-Pfad ist aus den Logs **nicht zu veröffentlichen oder zu ersetzen**; die bloße Add-on-Liste beweist weder Tokenintegrität noch Lookup-Aktivierung.

**Abnahme bleibt OFFEN**: .77 nicht gebaut/veröffentlicht; Kodi-21.3-Android-RK3528-Test für Media-Exit, Now/Next/EPG, ein echtes korrektes Hero-/Programmbild und stablilen Fokus verpflichtend.
