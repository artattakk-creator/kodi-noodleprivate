# XCMate 0.1.27 – Implementierung und Prüfbericht

**Aktualisierung:** [PR-Synchronisierung und en/de-Stabilisierung](STABILISIERUNG_027_SYNC_LOKALISIERUNG_DE.md)
mit 338 Tests ist der aktuelle Stand. Frühere Code-/CI-Abschnitte bleiben Historie.

Stand: 19.10.2026. **Entwicklungskandidat, keine Produktivveröffentlichung.**
Basis `main` / `823ae26`, Branch `feat/xcmate-027-catalogue-home`.
Parallel ergänzte Dokumentationsbasis `main`/`fbfb56c` konfliktfrei in den Entwicklungsbranch übernommen.
Produktiv bleibt **0.1.26**. Der Nutzer bestätigt dessen grundsätzliche Android-TV-Funktion;
die detaillierte Einzelabnahme ist damit nicht ersetzt.

Arbeitsgrundlage: alle drei 0.1.27-Aufträge, zentrale Übergabe, Langzeit-EPG-Plan,
Serienfortschritts-Spezifikation und Issues #21, #23, #24, #25, #26.
Ergänzende Nutzerentscheidung: mehrtägiges EPG wiederverwenden und Neuheiten lokal
behalten, damit Widgets auch ohne neuen Abruf gefüllt bleiben.

## Stand und Abgrenzung

| Bereich | Im Kandidaten implementiert / Cloud geprüft | Auf Android-TV noch zu prüfen |
| --- | --- | --- |
| Bestehendes Live-TV | Overlay, Recovery, Remote-Module und Player bytegleich; sieben Kern-Spiel-/Autostartmethoden AST-identisch zur Basis | Erste OK-Infobar, alle drei Ebenen, Links/Gruppen, Stop, Fokus jeweils 10× |
| Start/Einstellungen | Sechs Hauptpunkte; zehn Einstellungskategorien; aktive Accountauswahl; vorhandene Verwaltungsrouten | Skin-Darstellung, Ein-/Rücknavigation, mehrere reale Accounts |
| Filme/Serien | Eigene WindowXML-Oberflächen, horizontale Rail, Gruppen, 4-/6-spaltige Posteransicht, paginierte Kategorien | Renderer, echte Fernbedienung, Providerbilder, Auflösung/Schriften, Vollbildrückkehr |
| Details/Progress | Echte Anbieter-Metadaten, Favoriten, identitätsgebundene Movie-/Episode-Bookmarks, Resume und manueller Serienfortschritt | Stream-Seek, tatsächliche InfoTag-Erhaltung, Neustart/Abbruch, Episodenwahl |
| Suche | Ein Suchwort, drei echte getrennte Trefferzahlen, 48er-Seiten, aktive Gruppen und Account-ID | Eingabe, BINGIE-Ansichten, große reale Kataloge |
| Widgets | Drei lokale Quellen mit Kodi-ListItems, Live-Startgruppe/Now-Next, korrekte Detail-/Spielziele | Drei sichtbare BINGIE-MOD-Reihen und konkrete installierte Skinversion |
| Langzeit-EPG | Persistenter 10-Tage-Index; 7/10 Tage Tagesnavigation, echte Reichweite, Details, Zuordnungen, Erinnerung/Storno | Reale Quellen, Zeitzone, Logoanzeige, Gruppennavigation, Neustart/Benachrichtigung |
| Aufnahmeordner | Vorhandener Schlüssel, Dateirundtest vor Änderung, Speicherplatz soweit VFS verfügbar | Android-USB/SAF/SMB-Berechtigungen und reale Engine |

Die Zeitachsenalternative ist der im Hauptauftrag erlaubte **barrierefreie Tageslistenmodus**:
Sender links, Programme des gewählten Tages rechts, Datumsnavigation oben. Keine grafische
Mehrsender-Zeitmatrix als fertig behaupten. Fehlende Tage bleiben ausdrücklich leer.

## Nachvollziehbare Implementierungsschritte

1. **Lokale Datengrundlage** (Commit `643692b`): `library_index`, `media_data`, `media_state`, `media_art`,
   `guide_store`, `guide_timers`, `epg_cache_policy`, `recording_probe`; keine neue Fremdbibliothek.
2. **Menü und Oberflächen** (Code-/Integrationscommit `3731db7`): `home_menu`, `media_window`, `guide_window`, zwei eigene
   XML-Dateien und eigene neutrale Grafiken. Bestehende Konten-/Quellen-/Gruppenverwaltung
   wird wiederverwendet; keine neue Profildatenmigration.
3. **Suche und Widgets:** additive `app_routes` plus kleine Routeranbindung.
   Die alten Such-, Widget- und Spielrouten bleiben registriert.
4. **Diensteinbindung:** `app_services` mit begrenztem Hintergrundindex/Artwork und separatem
   MediaSession-Polling. Fehler dieser Zusatzfunktionen unterbrechen das Live-Overlay nicht.
5. **Regression, Paket und Abnahmeplan:** strikte API-/Callbackmodelle, echte SQLite-/HTTP-Tests,
   isolierter Repositorybau, ZIP-Dateivergleich, Dokumentation und Entwurfs-PR.

`WindowXML` wird ausschließlich mit nativen Positionsparametern konstruiert; Python-Daten
folgen über `configure()`. `WindowXML.onInit()` gehört zum echten Kodi-Lebenszyklus.
Das bestehende programmgesteuerte `WindowDialog` wird nicht umgebaut. Kein Erfolgstest
ruft dessen fehlendes `onInit()` künstlich auf. Native Liste/Panel bewegen im Modell den
Fokus **vor** dem Python-Callback; OK wird ausschließlich in `onClick` verarbeitet.

Referenz der API-Prüfung: Kodi-Tag
[`21.0-Omega`](https://github.com/xbmc/xbmc/tree/21.0-Omega/xbmc/interfaces/legacy),
Tagobjekt `60c450005472e6d38929bb28c07d00589102818d`.
`ControlList`, `WindowXML`, Dialog, ListItem, Control-Methoden sowie
`InfoTagVideo.setUniqueIDs/getUniqueID` gegen die tatsächlichen Signaturen geprüft.
Strikte Tests erkennen unbekannte Konstruktorargumente und Render-/Callbackausnahmen.
Die nativen Android-Bindings sind in der Cloud nicht ausführbar.

## Cachepolitik: Nutzerzusatz vom 19.10.2026

- **EPG bleibt erhalten:** lokal gespeicherte echte Programme bis Tag zehn; Importdatum
  und letzte verfügbare Sendung sind verschiedene Angaben. Öffnen, Datum, D-Pad und Widgets
  lösen keinen XMLTV- oder Katalogdownload aus.
- Der optionale Hintergrunddienst prüft beim bisherigen Aktualisierungsintervall zuerst die
  tatsächliche Programmdeckung. Sind sämtliche vertretenen Kanäle ab jetzt noch mindestens
  **24 Stunden lückenlos** versorgt (maximal 60 Sekunden Rundungsabstand), wird kein Neuimport
  gestartet. Ein 10-Tage-Guide kann so mehrere Tage liegen bleiben. Ein einzelner ferner
  Titel reicht nicht als Deckungsnachweis; leere, defekte oder lückenhafte Kanäle verhindern
  das Überspringen. Prüfung ausschließlich im Worker. Automatik und Safe-Mode bleiben
  unter den vorhandenen Nutzereinstellungen. Explizites „EPG aktualisieren“ umgeht die
  Wiederverwendung; es verändert keinen manuellen Quelleneintrag.
- Ein kürzerer Folgeimport ersetzt nur den tatsächlich neu abgedeckten Kanalzeitraum.
  Bereits gespeicherte spätere Programme außerhalb dieses Bereichs bleiben erhalten.
  Fehlgeschlagene und übergroße Importe rollen zurück; keine leere produktive Datenbank.
  Vergangene Programme werden bei Imports bis auf einen Tag Rückblick entfernt.
- Der vorhandene schnelle JSON-Fallback bleibt bis zehn Tage lesbar; auch reine echte
  Tag-9-Daten bestehen die Import-Brauchbarkeitsprüfung. Die 48-Event-Grenze des schnellen
  Overlay-Resolvers bleibt unverändert. Der neue Guide fragt bis 100 Programme **je Seite** ab.
- **Neuheiten:** `recent_days=10`, `recent_keep=100` pro Medientyp als vorläufige Vorgaben.
  Zulässige effektive Werte: 1–30 Tage, 24–500 gespeicherte Rail-Einträge.
  Beide Werte über XCMate → Einstellungen → Darstellung → Kodi-Einstellungen änderbar.
  Zehn Tage bedeuten Kennzeichnung als „Neu“, keine Löschfrist für die Widgetfüllung.
- Die Rail zeigt zuerst belegte jüngste Upload-/First-Seen-Daten, danach ältere Titel,
  zuletzt verfügbare Titel ohne belastbares Datum. Ältere Titel sind als älter gekennzeichnet;
  ohne Datum heißt es „Verfügbarer Titel · Hinzufügedatum unbekannt“. Der erste Katalogscan
  macht nicht den gesamten Bestand künstlich neu.
- Widget zunächst 24 Karten plus „Alle anzeigen“, intern bis 100 standardmäßig; die eigene
  Rail blättert mit 24 Einträgen weiter. Kategorien und Suche bleiben unabhängig davon
  vollständig paginiert. 100 ist **keine** Grenze für den vollständigen Katalog.
- Leerer oder fehlgeschlagener Folgeabruf lässt den letzten gefüllten lokalen Index stehen.
  Bewusst deaktivierte Bereiche/Gruppen bleiben ausgeblendet. Ein erfolgreich veränderter
  nichtleerer Katalog wird regulär übernommen; keine Garantie für inzwischen entfernte
  Anbieterstreams. Kaltcache zeigt einen echten Lade-/Wartungszustand statt erfundener Titel.

### Zusätzlicher Speicher und Netzwerkgrenzen

| Ablage | Grenze und Inhalt |
| --- | --- |
| `library_v1.sqlite` | 64 MiB SQLite-Seiten, höchstens 200.000 Eingangszeilen je Katalog; begrenzte Metadaten, IDs, keine Spiel-URLs |
| `guide_v1.sqlite` | 80 MiB SQLite-Seiten, höchstens 200.000 Programme je Portal, zehn Tage, Aliase separat |
| `media_art_v1/` | Höchstens 64 Dateien **und** 32 MiB; max. 3 MiB/Bild, 4096 je Dimension, 8 Megapixel; PNG/JPEG-Header vor Kodi geprüft |
| `media_state_v1.sqlite` | Nur IDs/Favoriten/Positionsdaten, getrennte Transaktionen pro Schlüssel; keine Passwörter oder Spiel-URLs |
| `guide_timers_v1.sqlite` | IDs/Zeit/Sender-/Sendungstext; erledigte Erinnerungen nach 30 Tagen entfernen |

Grenzen sind Budgetobergrenzen, kein reservierter Speicher. SQLite-Journale und bereits
vorhandene Anbieter-/XMLTV-JSON-Caches kommen hinzu; insbesondere ist dies **keine Zusage,
dass der gesamte Profilordner höchstens 176 MiB groß wird**. Das vollständige Suchverzeichnis
benötigt mehr als nur die 100 Rail-Einträge. Auf dem Gerät tatsächlichen Profil-/RAM-Verbrauch
messen. Bestehende XMLTV-Roh-/GZIP-/Programm-/Kanalgrenzen bleiben aktiv und werden nicht
zum Kaschieren von `PROVIDER_LIMIT` erhöht.

Artikelmetadaten werden erst nach gezielter Detailauswahl im Worker nachgeladen
(max. 2 MiB, 10 Sekunden Gesamtbudget). Bilder ausschließlich über begrenzte Worker/Queues
(max. 3 bzw. 32 Aufträge, HTTP max. 3 MiB/6 Sekunden). Native GUI und Widgets erhalten
**lokale** Bildpfade; keine Provider-URLs an den GUI-Bildlader. Schnelle Fokuswechsel
verwerfen veraltete Resultate. Ein explizit bestätigtes Kaltcache-Laden läuft im Hintergrund;
Pfeiltasten führen keine HTTP-Aufrufe aus. Ein Hintergrundbild darf sich nachträglich ergänzen.

## Behobene nachgewiesene Fehler / Schutzmechanismen

- Bisherige Zeit-/UI-Grenzen: alter JSON-Fallback und Brauchbarkeitsprüfung nur sieben Tage;
  separater persistenter Guide und zehn Tage Fallback verhindern Verlust echter späterer Daten.
- Bisheriger Dienst erzwang jeden Automatik-Intervallabruf, selbst mit brauchbarem Mehrtagesguide;
  neue lückenbewusste Wiederverwendung vermeidet diese unnötigen Downloads.
- Kategorie-/Such-/Widget-Index berücksichtigt aktuelle Gruppenänderungen auch **vor** dem
  nächsten Hintergrund-Reindex. Explizite ungültige Account-ID fällt nicht in anderen Account.
- Native Panelbewegung kann vor LEFT-Callback auf die vorige Zeile springen;
  ursprüngliche Auswahl am linken Rand wird vor dem Öffnen der Gruppen wiederhergestellt.
- Leere Gruppen behalten einen sichtbaren Gruppenfokus. Rückkehr aus Details/Video erhält
  Auswahl und Seitenposition; späte Metadaten dürfen keine verlassene Ansicht öffnen.
- Während einer Guide-Sender-/Datumsabfrage alte Programme sofort sperren, damit schnelles OK
  keine Erinnerung/Sendungsaktion dem falschen Sender zuordnet.
- Unbekannte Episode oder fremdes Video erhält weder Bookmark noch Seek. Episode wird aus
  dem gecachten gültigen Serienkatalog abgeleitet, nicht aus frei gelieferten URI-Parametern.
- Gleichzeitige Favoriten-/Fortschrittsänderungen verschiedener Kodi-Interpreter verlieren
  einander durch SQLite-Transaktionen nicht. Defekte Profildatei bleibt unverändert erhalten.
- Fehlgeschlagene lokale Indeximporte erhalten fünf Minuten automatische Wiederholpause
  (Commit `96b2c2a`); keine erneute Großverarbeitung alle 15 Sekunden bei vollem Datenträger.
  Manuelle Aufträge bleiben unabhängig.
- Aufnahmeordner wird erst nach eigenem UUID-Dateirundtest gespeichert; Fehler löscht
  ausschließlich die eigene Testdatei, keine fremden Dateien.

## Tests und Build (aktueller Sprachkandidat)

- **338/338 Tests bestanden**, vor und nach isoliertem Repositorybuild; 25 neue Sprachtests.
- **26/26 HTTP-/Cache-/XMLTV-Tests zusätzlich mit httpx 0.28.1 bestanden**.
- Syntax, drei isolierte ZIPs, Installerkopien und Index-MD5 geprüft; nur XCMate übernommen.
- **0.1.27 / Dienstbuild 27:** 308392 Bytes, **96 Dateien** bytegenau zu Quellen, CRC OK.
- SHA-256 `ab53aeb1f4e4e01473e2f935faabaf4480742ed268d6abc8dea69436bb62b16e`.
- [Test-ZIP](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.27.zip)
  · [SHA](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.27.zip.sha256).
- Finaler CI-Nachweis und neue Sprach-/Upgrade-Abnahme im
  [Stabilisierungsbericht](STABILISIERUNG_027_SYNC_LOKALISIERUNG_DE.md).
  Alte grüne Läufe unten belegen ausschließlich die historische Fassung vor dieser Runde.

Reproduzierbar lokal: `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -v`.
Der vollständige Repositorybuilder läuft ausschließlich in einer Wegwerfkopie, da er auch
andere Add-on-Pakete/Artworks generiert. Zurück übernommen werden nur 0.1.27-XCMate-ZIP und SHA.
Die `addons.xml` im Entwicklungsbranch bleibt auf veröffentlichtem Stand **0.1.26**.

Neue Regressionen: getrennte 1/2/1-Treffer, 53.664 Titel mit vollständigen letzten Seiten,
Account-/Gruppentrennung, 100er-Rail mit älteren/undatierten Fallbacks, leere Folgeantwort,
480 echte Guide-Ereignisse bis Tag zehn, kürzerer/fehlerhafter Folgeimport, Kanonisch/Alias-
Priorität, Sommer-/Winterzeit, Reminder-Deduplizierung/Storno/verpasster Termin, 10-Tage-
Wiederverwendung mit Lückenprüfung, ordentliche native Fokus-/Click-Reihenfolge, Foreign-
Playback/Resume/Stop/Shutdown, beschädigter Zustand, VFS-Schreibverweigerung, Engineprobe.

## Bewusst offene Folgestufen

1. **Auto-Next mit Countdown**, portalweite Continue-Watching-Reihe, komplette Staffel-/Serien-
   Resets und alle konfigurierbaren Komfortoptionen der Serien-Spezifikation. Vorhanden sind
   manuelles Weiterschauen/nächste Folge sowie Seen/Unseen/Reset je Episode, kein Auto-Next.
2. **Automatisches Umschalten**, vollständige EPG-Aufnahmeplanung, Konflikte, Sleep/Wakeup,
   Android-Hintergrundstart. Es gibt nur lokale Erinnerungen bei laufendem Kodi, kein Tune/Record.
   Claims erfolgen vor Benachrichtigung gegen Doppelmeldungen; bei Absturz genau zwischen
   Claim und Anzeige kann eine Benachrichtigung ausbleiben. Keine Exactly-once-/Weckgarantie.
3. **Android-Aufnahmeengine:** Diagnose prüft ausschließlich einen vorhandenen ffmpeg-Kandidaten
   per `-version`, Timeout 2 s; kein Installieren, kein Aufnehmen. PVR-Mapping, USB/SAF,
   Providerverbindungen und kurze echte Testaufnahme bleiben Voraussetzung für späteren Scheduler.
4. **Neue UI/Index/Widgets für M3U und STB** sowie portalübergreifende gemeinsame Suche sind
   noch offen. Neue Suche betrifft den aktiven Xtream-Account und aktive Gruppen. Alte Routen
   bleiben erhalten, Medienbereich führt diese Portaltypen in ihre vorhandenen Listen zurück.
   Keine erfundenen 0-Treffer als vollständig importierter Fremdportalkatalog.
5. Grafische Mehrsender-Zeitmatrix zusätzlich zur fertigen Tagesliste; zuletzt gewählte EPG-
   Gruppe über Sitzungen speichern; weitere Anbieterbilderformate außer PNG/JPEG; Aufwachen
   bei ausgeschaltetem Kodi. Neue Erinnerungen werden nicht in alte Reminderdateien migriert.
6. **Grafik-Sprint / Issue #27:** Während der Funktionsimplementierung kamen auf `main`
   die vollständigen [Space-Premium-Vorgaben](DESIGN_FREEZE_SPACE_PREMIUM_THEME_ARCHITECTURE_DE.md)
   und der [98-Slot-Plan](GRAPHICS_V2_ASSET_PLAN_027_DE.md) hinzu; beide und Issue #27 inklusive
   Nutzerkommentar vollständig gelesen. Space Premium ist alleiniger freigegebener Zielstil.
   Die zwei technischen neutralen Fallbackbilder dieses Funktionskandidaten sind keine finale
   Designfreigabe. 512er-Icon/Full-HD-Home-Vorschau und deren Sichtabnahme, Theme-Resolver,
   Fanart-Metadatenpfadkorrektur und anschließende Einzelassetproduktion bleiben separater
   Grafik-Sprint. Vorhandene Branding-/Live-Texturen nicht still ersetzen; Designs 2/3 nicht bauen.
7. **Realer Android-/BINGIE-MOD-Nachweis** einschließlich Skinversion, Screenshots, Kalt-/Warm-
   Zeiten und Speicherwerten. Alle neuen nativen Funktionen bleiben bis dahin ungeprüft am Gerät.

Kein automatischer Merge, keine Produktivversion, kein Main-Indexupdate und keine Skin-/Keymap-
Änderung. Ursprungs-/Lizenzhinweise werden erhalten; dieser PR entscheidet keine offene Rechtefrage.

Nächster Schritt nach grünem Cloud-Build: [Android-Abnahme](ANDROID_TESTPLAN_027_DE.md),
[BINGIE-Konfiguration](BINGIE_MOD_WIDGETS_027_DE.md), anschließend ausdrücklich freigegebener
regulärer Repository-Updateweg. Offene Issues nicht vor Geräteabnahme pauschal schließen.

## Historische GitHub-Übergabe vor Synchronisierung/Lokalisierung

[Entwurfs-PR #28](https://github.com/artattakk-creator/kodi-noodleprivate/pull/28),
Hauptcode `3731db7`, Datenmodule `643692b`, ergänzende Ressourcenhärtung `96b2c2a`.
Die parallelen Main-Designbeschlüsse wurden in `c643e0e` übernommen. Der erste PR-Lauf
[39256740591](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39256740591)
bestand mit damals 312 Tests; der abschließende Stand enthält 313 Tests einschließlich
Fehler-Rückoff und wird erneut als PR-Kandidat geprüft. Finaler Code-/Paketstand `b63d98a` in
[CI 39257022639 erfolgreich geprüft](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39257022639):
**313/313 Tests**, Build/Syntax/Upload erfolgreich, Produktions-Publish übersprungen.
[CI-Artefakt xcmate-review-28](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39257022639/artifacts/12187784190),
ID `12187784190`, 287969 Bytes Artefaktarchiv, Ablauf 02.11.2026, enthält CI-ZIP und eigene SHA.
Artefaktmetadaten und Uploadstatus sind überprüft. Die im Branch gespeicherte lokale ZIP
ist gesondert vollständig bytegeprüft; CI-ZIP-Zeitstempel können eine andere Paket-SHA ergeben.
Der anschließende Übergabecommit verändert ausschließlich Dokumentation, weder Quellen noch ZIP.
PR bleibt Entwurf; keine automatische Issue-Schließung oder Veröffentlichung.
