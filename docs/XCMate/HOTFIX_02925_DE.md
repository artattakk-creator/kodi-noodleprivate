# XCMate 0.1.29.25 – Premium-Fokus, Artwork und Lifecycle

Stand: 23.10.2026. Basis: veröffentlichte `.24`, `main` bei
`523c264e2760d707ef9f9f4e449670292a4a7092`.
Branch: `fix/xcmate-02925-premium-focus`.

## Korrigierte Android-Ausgangslage

Original-Icon und Premium → Lightweight sind laut jüngster Nutzerkorrektur
**PASS**. Sie bleiben Regressionstests; frühere gegenteilige Angaben in #115
sind überholt. Premium-Medienfokus, OK → Suche und Poster sind weiterhin
Gerätebefunde **FAIL**. Neue Android-Abnahme dieser Version: **NOT_TESTED**.

Grundlage: [bereinigter Logvergleich](ANDROID_LOGVERGLEICH_20261023_02924_NAV_ART_REC_DE.md),
#115, #111, #41, #90, #62, #113 und #37. Keine Original-Logs übernommen.

## P0 – nachgewiesene Codepfade und Korrektur

`.24` prüfte in `setFocusId` sofort die nativen Sichtbarkeits-/Enabled-Flags.
Während des Detailaufbaus fehlen Aktionen kurzzeitig oder Kodi verarbeitet die
Sichtbarkeit erst im nächsten Frame. Dann war nur Suche `400` gültig;
`_mode_focus['detail']` speicherte den Ersatzfokus. `_detail_ready` übernahm
diesen Fokus erneut. Außerdem konnte ein veralteter `onClick(400)` unabhängig
vom echten Fokus die Suche öffnen. Down von der Detailsuche zielte auf den
in diesem Modus versteckten Kategorienbutton `120` und fiel erneut auf Suche
zurück. Diese Fälle sind in Hosttests reproduziert, keine behauptete
Bestätigung des konkreten Android-Renderablaufs.

`.25` behält das beabsichtigte Fokusziel und wartet auf dessen native
Bereitschaft im **bestehenden Owner-Pump**. Kein Worker bedient die GUI, kein
zusätzlicher Warte-/Modal-Loop entsteht. Back bleibt währenddessen wirksam.
Ein neues Detail beginnt auf Aktionen `300`; Metadaten erhalten die
ausgewählte Aktionsidentität und eine bewusst gewählte Suche. Veraltete
Such-Callbacks werden verworfen. Down aus der Suche führt zu `300` bzw.
zur Staffelliste `330`. Das XML erzwingt bei Aktivierung nicht mehr Suche:
Default ist der Kategorienbutton `120`, `always=false`.

`FOCUS_DEFER` / `FOCUS_READY` protokollieren ausschließlich Modus,
Control-ID im Feld `key`, Dispatch-Nonce und native Fenster-/Dialog-IDs.
Keine Provider-, Medien- oder Speicherpfade. Ein einzelnes DEFER beim Aufbau
ist kein Fehler; READY oder erfolgreiche Bedienung muss folgen.

## Premium-Renderpfad

Alle Mediencontainer `110/111/112/200/210/300/330` sowie die Buttons nutzen
weiter die vorhandenen Core-Dateien `xcmate_focus_neon.png`. Premium ersetzt
diese funktionalen Fokusbilder nicht mehr. Der Rahmen wird nicht durch die
Panel-/Icon-Deckkraft abgedunkelt; fokussierter Text bleibt hell. Auf
fokussierten Postern entfallen zusätzliche Premium-Schattierungen;
Schattierungen anderer Poster stehen unmittelbar nach dem Poster, vor Text.
Ein neuer Render-Namensraum verhindert die Wiederverwendung alter
generierter `.24`-XML-Dateien durch Kodi. Alte Profile/Dateien werden nicht
gelöscht. Keine Änderungen an Control-IDs, Hit-Rechtecken, Kodi-Keymaps oder
installierten BINGIE-Dateien.

**Asset-Matrix-Delta zu [`.24`](SPACE_PREMIUM_RENDERER_MATRIX_02924.json):**
`focus.media` wird nicht mehr für die Core-Medienfokusbilder gebunden.
`panel.media.poster.shade` gilt nur für nicht fokussierte Layouts.
Die 98 Originalbilder und das installierbare optionale Paket bleiben
bytegleich; keine neue Grafikinterpretation. Guide-/Live-Texturen bleiben
unverändert. Die damalige Matrix ist ein historischer `.24`-Bericht.

**Dateibrowser-Zuständigkeit:** Filmkategorien und Staffel-/Episodenlisten
sind XCMate-WindowXML. Die Speicherordnerwahl in
`home_menu.recording_folder()` und ZIP-Auswahl in `theme_ui.manage()` rufen
dagegen Kodis `Dialog.browseSingle()` auf. Deren native Dateiliste wird vom
aktiven Kodi-Skin gerendert. Dieser Patch ändert keinen globalen Dateibrowser.
Ein dort verbleibender Fokusfehler ist getrennt zu melden; keine falsche
Behauptung, er sei durch das Medien-XML automatisch behoben.

## P1 – begrenzte Artwork-Korrektur

Die Logzahlen 126/166 BUSY (50 nach `.24`) belegen Contention, aber nicht
die konkrete Providerursache eines fehlenden Aladdin-Posters.
Ein Worker liest nun Status und Versuchszähler in **einem** read-only
Snapshot statt in zwei bis drei getrennten Abfragen. Maximal 96 Keys,
keine URLs im SELECT/Ergebnis. Bei BUSY genau ein zweiter Versuch:
75 ms SQLite-Timeout pro Versuch, 25 ms Pause; Progress-Handler begrenzt
Abfragen zusätzlich. Keine längeren GUI-Timeouts.

Initiale Writer-Statements erhalten bei BUSY einmal 25 ms Abstand und
einen zweiten Versuch; bereits begonnene Transaktionen werden nicht
wiederholt. Erfolgreiche kurze Sperrerholung vergiftet die DB-Health nicht
mehr sofort für fünf Sekunden. Persistenter BUSY wird weiterhin gemeldet.
Commit-/Transaktionsfehler werden nicht als erfolgreicher Retry ausgegeben.

`DB_BUSY` hat bei fehlendem lokalen Bild Vorrang vor veraltetem Inbox-/
Netzwerkstatus. Lokale READY-Bilder bleiben unabhängig davon verfügbar.
Der Detailbericht enthält zusammengehörige Werte für Quelle-Feldname,
Kandidatenzahl, Code und Versuche. Bestehender Einzelretry mit Cooldown,
HTTP-/DNS-/TLS-/Timeout-Klassen und begrenzter Downloadanzahl bleiben erhalten.
Kein globaler Retry, kein Job-/Cache-Reset, keine Bildlöschung.

**WAL:** Read-only Verbindungen lesen vorhandene committed WAL-Daten auch
während eines Writers; mit echter SQLite geprüft. Eine laufende DB wird
nicht ungeprüft auf WAL umgestellt. Wartungssperren, Online-Backups,
Integritätsprüfung, Recovery und originale DB-Sicherheitsverträge bleiben
erhalten. Länger dauernde Android-Sperren und die konkrete externe
Posterquelle sind weiterhin Geräte-Diagnosepunkte, kein pauschales PASS.

## P1 – Service und GetDirectory

Der optionale Library-Worker prüft Stop/Abort nun zwischen seinen Stufen
und vor weiteren Portalaufgaben. Am regulären Service-Ende setzt ein
Shutdown-Event die Startsperre; der Join wartet höchstens 200 ms.
`APP_WORKER_STOPPED` und `APP_WORKER_STOP_PENDING` unterscheiden echten
Abschluss von noch laufender Arbeit. Kodi-/HTTP-Threads werden nicht gewaltsam
beendet; laufende nicht abbrechbare Provider-I/O kann weiterlaufen. Daher ist
die historische Fünf-Sekunden-Meldung **nicht als vollständig behoben** markiert.

Die dokumentierten GetDirectory-Fehler traten auch in `.22` vor Premium auf.
Der späte `.24`-Fehler ist eine zeitliche Korrelation zu FOCUS_FALLBACK,
kein belegter gemeinsamer Stacktrace. `OwnerDispatch`, `show()`-Start,
Player-Übergabe, Home-Anker und Directory-Abschluss werden nicht umgebaut.
Ebenso ist `Unknown addon id` während eines früheren Updates kein Beweis
für einen bestimmten neuen Fokusfehler. Android-Update/Neustart bleibt offen.

## Schutz, Tests und Freigabe

Gezielte Tests: verzögerte Sichtbarkeit, Suche/OK, asynchrone Aktionsidentität,
Serien/Player-Rückkehr, Back, Premium-Reihenfolge/Deckkraft/XML-Cache,
echte SQLite-Rollback-/WAL-Sperren, endliche Retries, READY-Dateihash,
private Codes und Service-Abbruch. Die alten Live-/Guide-/Owner-/Player-
Verträge bleiben geprüft. Nur der exakt eine neue `_resume_focus()`-Aufruf
und zwei erlaubte Loglabels werden beim alten AST-/Hash-Vergleich isoliert;
keine Referenzdigests ersetzt.

Die CI bricht jetzt auch beim piped Unittest-Aufruf mit Fehlercode ab
(`pipefail`), bevor ein Main-Push ein Update veröffentlichen darf.
Vollständige Ergebnisse und ZIP-Prüfung stehen in
[TESTERGEBNISSE_02925.json](TESTERGEBNISSE_02925.json) und
[TESTLOG_02925.txt](TESTLOG_02925.txt). Geräteprüfung:
[ANDROID_TEST_02925_DE.md](ANDROID_TEST_02925_DE.md).

Die jüngste Nutzerfreigabe erlaubt nach erfolgreichen technischen Gates den
Merge und das reguläre GS-Repository-Update. Die Android-Sichtabnahme bleibt
ausdrücklich offen; #115/#111 nicht voreilig schließen. Der Publish-Nachweis
wird nach dem tatsächlichen Workflow-/Indexcheck dokumentiert.

## Recorder und Folgearbeiten

`.25` aktiviert keine ungetestete TS-Aufnahme. Kodis integriertes FFmpeg
ist kein nachgewiesenes externes CLI. Die neue native Engine bleibt eine
getrennte Entwicklung/Draft mit Format-, Abbruch-, Speicher- und HTTP-Tests;
ohne echte 2–5-Minuten-Aufnahme **und Kodi-Offline-Playback** keine Integration.
EPG-Timer (#62), Medienmanager (#113) und Download-WIP bleiben getrennt.
Serien-Staffelübergang B02 bleibt offener eigener Test (#85).
