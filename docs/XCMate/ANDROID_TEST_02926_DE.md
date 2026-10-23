# XCMate 0.1.29.26 – Suche und einfache Sofortaufnahme

**Nur Android-Testkandidat / Draft. Kein reguläres Update veröffentlicht.**
Basis: `main` `.25`, Commit `5bd7349eae89db85a5b0deac8362478d559d5007`.
Die 23 Lightweight-PASS aus `.25` bleiben die Ausgangsbasis; eine erneute
Android-Abnahme von `.26` liegt noch nicht vor. Original-Icon, Premium-Grafiken,
Portale, Gruppen, EPG, Artwork, Favoriten und Resume werden nicht zurückgesetzt.

## Installation und Reihenfolge

1. ZIP `plugin.video.xtreammate-0.1.29.26.zip` und zugehörige `.sha256` aus dem
   Draft-PR laden, Prüfsumme abgleichen, über **Aus ZIP-Datei installieren**
   aktualisieren. Keine Deinstallation und keine Löschung von Benutzerdaten.
2. Kodi regulär neu starten; zunächst **Lightweight** verwenden.
3. Zuerst S01–S07 prüfen. Bei erneuter Kodi-Beendigung keine Aufnahmeversuche
   anhängen; Uhrzeit und private Crashdiagnose für #118 sichern.
4. Danach R01–R06 für die ausdrücklich gewünschte einfache Aufnahme prüfen.
   Timer, EPG-Aufnahmeplanung und Meine Medien sind in diesem Kandidaten nicht
   aktiviert. Bestehende `.25` bleibt Rückfallbasis.

## Suche – #118 / #25

- **S01** Film-/Serienübersicht → Suche → `Upload` → OK. Das aktive Medienfenster
  bleibt erhalten und zeigt die drei Rubriken **LIVE-TV-SENDER / FILME / SERIEN**.
  Kein Sprung zur Home-Seite beim Bestätigen, keine Kodi-Beendigung. Die
  Existenz von Treffern wird nicht vorausgesetzt; 0 ist ein gültiges Ergebnis.
- **S02** Ein eindeutiger Nulltreffer, sehr lange Eingabe und Sonderzeichen.
  Abbrechen der Tastatur muss die vorherige Ansicht erhalten. Zweite Suche und
  sehr schnelles OK/Back wiederholen; keine doppelten Fenster/Starts.
- **S03** Rubriken per Links/Rechts markieren und OK; Down zur Trefferliste,
  Up zurück. Counts gelten für den lokal verfügbaren aktiven Portal-/Gruppenindex,
  nicht nur für 48 sichtbare Zeilen. Vor/Zurück-Seiten bei über 48/96 Treffern.
- **S04** Film/Serie öffnen → vorhandene Details/Staffeln/Episoden; Play/Resume
  wie bisher. Back führt zur Suchphrase/Rubrik und zuletzt gewählten Zeile,
  anschließend zur ursprünglichen Medienansicht.
- **S05** Einen Begriff aus einer **tatsächlich jetzt laufenden** EPG-Sendung
  suchen. Der passende Sender erscheint mit `Jetzt: …`, sofern die lokalen
  Guide-Daten und Zuordnungen vorliegen. Zukunftssendungen zählen nicht als
  Jetzt-Treffer. Bei fehlendem EPG bleibt Sendernamensuche verfügbar und wird
  entsprechend gekennzeichnet. Keine erfundenen Sendungen.
- **S06** Live-Treffer starten. Übergabe erfolgt erst nach Ende des Suchfensters
  und Freigabe seiner Navigationssperre an den bestehenden Live-Resolver.
  Bestehendes Live-Overlay und IR-Steuerung prüfen; kein Doppelstart.
- **S07** Suche aus Einstellungen → Gruppen/Favoriten prüfen; bei geöffnetem
  Index/Hintergrunddienst und offline wiederholen. Indexfehler/noch ladender
  Index darf nicht als verlässlicher Nulltreffer dargestellt werden.

## Einfache Aufnahme – manuelles Starten, Abschließen, Abspielen

- **R01 Speicher:** Einstellungen → **Speicher & Aufnahmen** → bestehende
  Aufnahmeordnerwahl. Für diesen Kandidaten **internen lokalen Speicher**
  verwenden. Die Engine benötigt POSIX-Dateioperationen und Hardlinks.
  SMB/VFS/FAT32 sowie Android-USB-/SAF-Ziele sind **nicht freigegeben**;
  Ablehnung ist dort kein Beleg für funktionierende Aufnahmeunterstützung.
- **R02 Start:** **Sofortaufnahme starten** → Sendernamen eingeben → Sender
  auswählen → maximale Dauer (2/5/30/60/120 Minuten) → zusätzliche
  Streamverbindung ausdrücklich bestätigen. Nur wenn der Anbieter diese
  zusätzliche Verbindung erlaubt. Die Player-Wiedergabe wird nicht automatisch
  gestartet, gestoppt oder umgeschaltet. `angefordert` bedeutet noch nicht
  `recording`; Status separat kontrollieren.
- **R03 Status:** **Sofortaufnahmen / Stoppen / Abspielen** zeigt `pending`,
  `starting`, `recording`, Bytes und gegebenenfalls sichere Fehlercodes.
  Nur echte kontinuierliche HTTP(S)-MPEG-TS-Streams werden akzeptiert.
  HLS/DASH, verschlüsselte Streams, benötigte Spezialheader oder nicht
  unterstützte Portale müssen klar fehlschlagen. Kein externes FFmpeg nötig.
- **R04 Stop:** Laufende Aufnahme auswählen → Abschluss bestätigen. Dies
  schließt **nur die Aufnahme** ab, der Player bleibt unverändert. Nach
  Finalisierung erscheint `complete`; bei Fehlern `failed` oder `partial`.
  Erneuter Start während aktiver Aufnahme wird abgelehnt; keine zweite Aufnahme.
- **R05 Wiedergabe:** 2–5 Minuten aufnehmen, gezielt abschließen, fertigen
  Eintrag auswählen → Wiedergabe bestätigen. Danach Netzwerk trennen und nach
  Kodi-Neustart dieselbe lokale Datei erneut abspielen. Bild/Ton und Aufnahmeende
  prüfen. **Diese Kodi-/Android-Wiedergabe ist bislang NOT_TESTED.**
- **R06 Fehler:** Quelle trennen oder Kodi während einer Aufnahme regulär
  beenden. Unterbrochene Dateien bleiben als `.ts.part`; sie werden nicht als
  fertige Einträge abgespielt. Nach Neustart wird ein unterbrochener Auftrag
  `partial / SERVICE_INTERRUPTED`. Keine bestehende Datei löschen. Maximal
  2 GiB pro Aufnahme und 64 MiB Reserve **plus Platz für die sichere
  Finalisierungskopie**. Speicher-/Formatfehler sind keine Erfolgsmeldung.

Die erste Version unterstützt Xtream-Direct-TS und headerlose direkte
M3U-HTTP(S)-Quellen, keine Stalker-Linkerzeugung oder adaptiven/encrypted Streams.
Die Oberfläche verwaltet hier nur neue manuelle Aufträge. Alte `recordings.json`
und vorhandene Dateien werden nicht migriert oder gelöscht. Es gibt keine
automatische Fortsetzung nach Kodi-Ende und keine Aufnahme außerhalb von Kodi.

## Bestandsregression und Diagnose

Die bestätigten `.25`-Bereiche B01–B04, M01/M02/M03/M05/M06, P01–P05,
E01–E07 sowie A01/A04 wie im [Lightweight-Bericht](ANDROID_ABNAHMEERGEBNISSE_LIGHTWEIGHT_02925_20261023_DE.md)
prüfen. Poster-Timeouts A02/A03 werden hier nicht als behoben ausgegeben.
Staffelübergang B02 (Autoplay-Testserie) bleibt gesondert offen.

Öffentliche Suchmarker enthalten **keinen Suchtext**:
`SEARCH_INPUT_ACCEPTED`, `SEARCH_GUI_READY`, `SEARCH_RESULT_READY`,
`SEARCH_RETURN`, `SEARCH_WINDOW_CLOSED`, `SEARCH_WORKER_STOP_PENDING`.
Anonyme Korrelation, monotone Zeit und Owner-/Fenster-ID erlauben den Vergleich.
Ein Pending-Marker ist keine bestätigte Leak-Ursache. Bei erneutem Prozessende
privates `logcat`/Tombstone aus dem Zeitfenster sichern, nur bereinigte
Fehlerklassen veröffentlichen; keine Rohlogs/Provider-URLs/Tokens hochladen.

Bitte jeden Punkt als PASS/FAIL/NOT_TESTED zurückmelden. #118 bleibt bis zum
echten Android-PASS offen. Dieser Draft führt keinen automatischen Merge,
Release oder GS-Repository-Update aus.
