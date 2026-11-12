# XCMate .90 – sechs BINGIE-Reihen: Implementierung und Testbericht

**Review-Build, kein Release.** Der minimale Uhr-Fix bleibt in Draft **#437**. Der vorhandene darauf aufbauende Skin-Folge-Draft **#438** ergänzt sechs Standardreihen. Kein Merge, Versionssprung, Repository-Release oder Benutzergeräte-Eingriff. Main bleibt 4336dd56; Installer **0.5.26** und veröffentlichte Pakete bleiben unverändert.

## Ergebnis und Beweise

- **PASS:** vollständige [Host-CI 43267201346](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43267201346), **3.854 unittest-Fälle in 931,223 s**, 11 Brandingtests, 17 PO-Kataloge; keine neuen Skips. ZIP bytegleich in CI reproduziert.
- **PASS:** 248 kombinierte gezielte Quellen-, Spinner-, Deadline-, Storage- und historische Scope-Fälle in 112,946 s; Teilmenge der vollständigen Suite.
- **PASS:** finaler nativer Sechs-Reihen-Lauf [CI 43268495432](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43268495432), 720p/1080p, alle sechs Reihen in vier Prozesszyklen, echte Header-/Cover-/Fokus-/Animationspixel, drei Videodirectory-Klicks/Back pro Zyklus, lokale WAV, Metadatenaktualisierung bei weiterlaufendem Audio, Stop-ACK und weitere IR-Eingabe.
- **ANDROID_NOT_TESTED:** Box B/Kodi21.3/RK3528, echte Anbieter/API-Inhalte und Audiodienste. Historische Android-FAILs bleiben erhalten.

Tatsächlicher nativer Host: **Kodi21.2, Debian 2:21.2+dfsg-4, Linux x86_64**, BINGIE MOD 2.2.3. Keine Android-/Kodi21.3-Geräteabnahme behaupten. Synthetische lokale Pluginverzeichnisse, Poster und WAV prüfen den realen Renderer. Spinner-Terminalzustände zusätzlich ausdrücklich per UI-State injiziert; Queue-/Deadline-/Profilverhalten separat auf dem Host geprüft.

Produktionsquellstand: `9664fca531f0b2dd4df4bf80e3af329e9f7ded1c`; nativer Testablauf `c91b0db06ed7ab7314f9ce9229635b34dcd0cc56`. Spätere native Testverbesserungen verändern weder src, Testsuite noch ZIP; Bytegleichheit per Git-Diff geprüft.

## Quellen und Standardfolge

Privates Backup nur read-only untersucht, keine Rohkonfiguration oder Zugangsdaten eingecheckt. Unter unverändertem Hero und Senderlogos:

| Reihe | Vorhandene Quelle | Container | Ziel |
| --- | --- | --- | --- |
| Filme | widget_recent_vod | vorhanden, Referenz 1520 | Videos |
| Serien | widget_recent_series | vorhanden, Referenz 1530 | Videos |
| Im Kino | optionaler TMDB-Helper: now_playing/movie | 29761 | Videos |
| Disney | gespeicherter Helper-Discover: Anbieter 337/DE, movie | 29762 | Videos |
| Diese Woche im Trend | gespeicherter Helper: trending_week/tv | 29763 | Videos |
| MP3s | vorhandener Browse-Pfad von plugin.audio.m3sr2019 | 29764 | Music |

Disney ist die vorhandene Metadaten-/Verfügbarkeitsauswahl, keine behauptete Streaminglizenz. **Kein Bewertungsranking.** Eigener TMDB-Token wird nicht an Helper weitergegeben. Installiert/aktiviert bedeutet nicht authentifiziert: fehlende/deaktivierte/mehrdeutige Quellen haben eigene Fehlerzustände, keine erfundene Ersatzquelle.

Audio nutzt vorhandenen Widget-Pfad oder tatsächlichen Music-Menüpfad. Automatische Play-/Shuffle-/Lösch-/Favoritenänderungsrouten sind als Datenquelle gesperrt. Ordner öffnen im Musikfenster; echte Streamauflösung benötigt Geräteprüfung.

Realer Konfigurations-Readback erkannte alle vier Zusatzquellen eindeutig. Erster FAIL fand die exakt benötigte Variable TMDbHelper.Widgets.Reload; sie ist nun gezielt zugelassen. Werte werden read-only übernommen, kein globaler Hook gepulst und keine gespeicherte URL umgeschrieben.

## Darstellung, Ladeablauf und Bestandsschutz

Gemeinsame Original-BINGIE-Komponente für sechs Reihen: gemessener Titel, 24×24-Animation, 85-ms-Frames, 12 Pixel rechts davon. Typ über echtes Home-InfoLabel vor den ersten Items, ohne fremde XCMate-ListItemproperties vorauszusetzen. Header auch bei Wartet/leer/Fehler sichtbar.

Leere Zusatzreihen belegen 26 Pixel. Nativer Coverbereich wird vor der Anfrage freigegeben und bei Inhalten erhalten; kein selbstblockierendes NumItems-Cold-Gate. Poster/Thumb und Audio-Icons proportional. Bestehende Film-/Serien-Geometrie, Hero, Rail, Icons und Fokusgrafiken erhalten.

Vier Zusatzquellen nach bestehender Live-/Film-/Serien-Vorbereitung einzeln über Kodis DirectoryProvider. Keine neuen Netzwerkworker, Vollkatalogscans oder GUI-SQLite-Abfragen. Artwork-Pending nach Profil/Provider/Reihe; Katalog-Pending aus bestehendem aktuellem Service-Memo/aktivem Gruppenjob.

Maximal 60 Sekunden Spinner. Core-GUI-Tick erzwingt die Frist auch bei Datenworkerpause/-neustart; alter Timeout beendet keine neue Generation. Zusatzquellen starten nach Timeout keinen weiteren Provider, solange Kodi den alten noch als aktiv meldet. Last-good-Pfade/Items bleiben erhalten.

Native leere Fremdcontainer unterscheiden leeren Erfolg und Quellfehler nicht belastbar: EMPTY_OR_ERROR plus Prüfhinweis, kein erfundener API-PASS. READY bedeutet nachgewiesene Items, keinen behaupteten frischen externen Download. Pid-lose Quellen folgen bestehender Portalpräferenz. GUI darf keine Dateien/SQLite/DNS öffnen oder Threads erzeugen; eigener Test schützt dies.

Private Consumer stehen nach Serien, vor weiteren Benutzerreihen, ohne gespeicherte Slots zu überschreiben. Serien-Abwärtsverbindung führt durch gefüllte Extras zum alten Ziel; Fremdreihen-Rückwärtsverbindungen bleiben original. Unbekannte IDs/Includes oder mehrdeutige Home-Gruppen blockieren die Ergänzung.

Bestehender Skin-Transaktionsweg: Vorschau, ausdrückliche Bestätigung, private Sicherung, Hashprüfung, atomare Anwendung, Rollback. Generierter Cache privat gesichert; SkinShortcuts read-only. Keine Benutzerbox geändert.

## Bestätigte Ursachen und Korrekturen

| Befund | Korrektur |
| --- | --- |
| clock50 verwirft gültige URL, keine MediaRows | #437 neutralisiert nur exaktes Token vor Validator, echte URL unverändert |
| Originalheader unterdrückt eigene Reihen samt Spinner | gemeinsamer eigener Header mit verifizierter Originalanimation |
| Konstanter Typ als erstes String.IsEqual-Argument: Extraspinner unsichtbar | echtes Typ-InfoLabel vor den ersten Items, kompatibler Core-Fallback |
| Vier leere Vollhöhen schieben Serien aus Viewport | kompakte Header und explizite Coverbereich-Freigabe |
| Dynamischer ID-Text ist kein numerisches Navigationsziel | regulärer SetFocus-Builtin mit InfoLabel-Auflösung |
| Präfix-IDs überschreiten 24-Bit-Infofeld | private IDs 29761–29764, alle zusammengesetzten IDs unter 2^24 |
| Globales Pending lässt fremde Reihen drehen | profil-/provider-/reihenspezifische Queue und Job-Memo |
| Workerpause lässt Busy stehen | synchronisierte GUI-Deadline, keine neuen Worker/Jobabbrüche |
| Sieben Mock-Importfehler im ersten lokalen Gesamtlauf | doCleanups verschachtelter Testfixtures korrigiert; produktive EPG-Funktionen erhalten |
| Headless-Audio ohne Sink, Stop während Open | nur Testcontainer: virtueller PulseAudio-Ausgang, reale PCM-Uhr, native Open-/Stop-/GUI-ACKs |

Fehlgeschlagene Zwischenläufe bleiben auf GitHub nachvollziehbar: 43249630477 (Serienpixel), 43251229556 (Fokus/Pixelmessung), 43252762231 (Info-ID), 43253926886 (Screenshot nach Audio), 43255518698 (Spinnerbedingung), 43258101813 (headless Audio), 43267193624 (Test noch im Musikvisualisierungsfenster statt Home). Keine Verlängerung eines produktiven Player-Stop-Timeouts.

Kodi21.3-Quellcode verifiziert: CGUIInfo::GetData1 maskiert 24 Bit; CGUIAction::GetNavigation akzeptiert literale Zahlen, ExecuteXBMCAction löst InfoLabels für Builtins auf. Keine Kodi-Core-Dateien kopiert/verändert.

## Review-Paket

[ZIP](test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip) · [SHA256](test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip.sha256)

**0.1.29.90**, **4.677.376 Bytes**, **859 Dateien**; CRC, Quellbytes und unabhängige CI-Reproduktion PASS.

`45cc791788f1990bdaeff051004d6f0b1013e5923be9cda9ba1cb2f73cf9a5d2`

Veröffentlichte .90-Kanäle behalten SHA256 `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`; Review-Paket nicht dorthin kopiert.

## Android-Einzelmatrix

| Reihe | Echter Anbieter | Header/Spinner | Cover/Items | IR/Klick/Zurück | Drei Neustarts |
| --- | --- | --- | --- | --- | --- |
| Filme | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Serien | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Im Kino | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Disney | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Diese Woche im Trend | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| MP3s | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |

[Android-Checkliste](ANDROID_ABNAHME_PR438_DE.md). Native Linux-/UI-Fehlerinjektion ersetzt keine Geräteprüfung.

## Offene Masteraufgaben

| Bereich | Status |
| --- | --- |
| EPG Home/Mini/Groß/Details (#161/#430) | lokale guide_v1-/Mapping-/Snapshot-Komponenten erhalten; echter Gleichstand/Last-good bei BUSY weiter NOT_TESTED |
| Galileo XMLTV → Details, manuelles SAVE_BLOCKED (#433) | historischer ANDROID_USER_REPORTED_FAIL offen; keine unbelegte Berechtigungsursache |
| ARM32-Reserve/SQLite-BUSY/Logo-Vollständigkeit (#430) | Hostschutzregressionen PASS, reale Mount-/Reserve-/Pixelprüfung offen; Reserve nicht deaktiviert |
| Rolling-Cache/Referenz-GC (#108) | weitere Implementierung; vorhandene Pins/TTL/Quota erhalten, kein blindes Löschen |
| Live-/Film-/Serien-Exit (#174) | historischer Android-FAIL offen; synthetischer Audio-ACK behebt keinen Rockchip-Decoderfehler |
| Altlasten-/Backup-Bereinigung | keine Löschung; aktives Wizard-Staging, WAL, Originale, letzte Sicherung geschützt; Remote-/Restore-Nachweis fehlt |

Widget-/Header-/Quellenblock hostseitig prüfbar. Der gesamte EPG-/Artwork-/Exit-Masterauftrag ist ausdrücklich nicht geschlossen. Dokumentierte Reihenfolge: zuerst Widget-Geräteabnahme, danach größerer EPG-/Cache-Umbau.

## Kuratierte native Belege und Messwerte

[Host-Summary](test-builds/media-spinner/evidence/host-summary.json), [720p](test-builds/media-spinner/evidence/native-720p.json), [1080p](test-builds/media-spinner/evidence/native-1080p.json). Vier Prozesszyklen pro Auflösung: alle sechs Reihen, Core 88/24/24, Zusatzquellen je sechs Items, Header/Fokus/Texturpixel, Spinner-Endzustände, drei Videoklicks/Back, native Audiouhr/Stop/IR. Gespeicherte Original-Widgetdatei bleibt pro Zyklus hashgleich. Zusatzquellenplan ist ausdrücklich eine Test-Fixture; reale Konfigurations-Discovery wird getrennt read-only geprüft.

Beobachtete Ladefolge in allen acht Durchläufen: **Im Kino → Disney → Diese Woche im Trend → MP3s**, nie zwei aktive zusätzliche Provider. Die einzelnen Start-/READY-Zeitpunkte seit Zusatzphasenbeginn stehen unverändert in den JSON-Belegen, inklusive aller Neustarts. Die künstlichen Quellen warten jeweils 600 ms; diese Linux-Messwerte sind keine Prognose für Android oder reale Anbieter.

Originale native Screenshots mit UI-Ladezustands-Injektion: [Filme](test-builds/media-spinner/evidence/1080p/filme.png), [Serien](test-builds/media-spinner/evidence/1080p/serien.png), [Im Kino](test-builds/media-spinner/evidence/1080p/im-kino.png), [Disney](test-builds/media-spinner/evidence/1080p/disney.png), [Trend](test-builds/media-spinner/evidence/1080p/diese-woche-im-trend.png), [MP3s](test-builds/media-spinner/evidence/1080p/mp3s.png); [zweiter Kino-Animationsframe](test-builds/media-spinner/evidence/1080p/im-kino-frame-2.png). Einfarbige Poster sind absichtliche synthetische Texturen, keine echten Providerbilder.

## Abschließende unabhängige Schutzfälle

Der minimale Uhr-Fix bleibt auch dann funktionsfähig, wenn der neue Skinadapter noch nicht bestätigt wurde: ausschließlich beim exakt geprüften alten Adapter dürfen die eigenen generierten MediaRows repariert werden. Test bestätigt zwei Konversionen und bytegleiche acht Definitionsdateien/SkinShortcuts, keine Installation der sechs neuen Consumer ohne deren Marker.

Metadaten auf dem tatsächlich sichtbaren Home dürfen weiterlaufen, während Musik/TV im Hintergrund spielt. Der neue Lader verändert keinen Player und keinen Fokus. Vollbild/Modaldialoge bleiben gesperrt. Ein direkter Hosttest verbietet dabei Player-/Builtin-Aufrufe. Native Zusatzprüfung kehrt aus der konfigurierten Musikvisualisierung mit echtem Back nach Home zurück und prüft Metadaten-Refresh bei weiterlaufender PCM-Uhr, anschließend Stop/IR.

Diese zwei Schutzfälle sind im aktuellen Quellstand 9664fca531f0b2dd4df4bf80e3af329e9f7ded1c enthalten. 27 gezielte Fälle und 248 kombinierte Schutzregressionen in 112,946 s sind PASS. Der finale native Lauf 43268495432 bestätigt Hintergrund-Audio und Metadatenaktualisierung in allen acht Prozesszyklen.

Gemessene Zusatzphasen vom Start bis vier Quellen READY: **3.298–4.021 ms**; zusätzlicher Home-Metadatenrefresh während Audio: **849–1.669 ms**. Je künstliche Quelle 600 ms Wartezeit. Kein Leistungsversprechen für reale Dienste/ARM32. Die acht Einzelmessungen stehen in den JSON-Belegen.
