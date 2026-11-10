# Android-Abnahme XCMate 0.1.29.87 – Box B

**Alle folgenden Gates: ANDROID_NOT_TESTED.** Linux-Kodi und Hosttests sind separate Evidenz. Box A, Original/Pilot/NeoDark3 .86 und Installer 0.5.26 unverändert lassen. Test-ZIP nur nach bewusster Benutzerinstallation als kumulatives Update verwenden; keine Deinstallation, kein Reset, keine Profilkopien veröffentlichen.

## Testkandidat installieren

1. Nur Box B verwenden. Das separate ZIP aus Draft #416 herunterladen; Begleit-SHA256 auf dem heruntergeladenen Paket prüfen. Kein Repository hinzufügen oder umstellen.
2. Kodi → Add-ons → Paket-Symbol → Aus ZIP-Datei installieren → `plugin.video.xtreammate-0.1.29.87.zip`. Als kumulatives Update über .86 installieren; weder deinstallieren noch Kodi-Daten löschen. Version .87 und den bestehenden Profilbestand kontrollieren.
3. Zuerst Home/Logos/EPG sowie je einen Live-/Film-/Serien-Start und Zurück testen. Bei Freeze/Indexfehler sofort FAIL dokumentieren; keine 100 fehlerhaften Zyklen erzwingen. Nach bestandenem Smoke folgen alle Gates einschließlich F1.
4. Keine automatische Artwork-Migration. Erst S1 dokumentieren; bei identischem Kapazitätspool S2 als BLOCKED führen. Neue Pfadnamen schaffen keinen freien Speicher.
5. Bestehenden TMDB-Token unverändert lassen. Der optionale Einrichtungs-/Gatewayprototyp benötigt eine später geprüfte API und wird für diese Bilder-/GUI-Abnahme nicht vorausgesetzt. Keine Zugangsdaten oder Rohlogs öffentlich posten.
6. Ergebnisse getrennt nach Auflösung/Kalt-/Warmstart mit PASS/FAIL/ANDROID_NOT_TESTED, realen Zeiten und privaten Screenshots erfassen. Die normalen Updatekanäle liefern weiterhin .86; dieses Paket wird ausschließlich manuell zur Abnahme angeboten.

Vorher privat Version/Profil, Startgruppe/Startsender, TMDB-Zugang, Favoriten, Resume, manuelle EPG-Zuordnungen, Widgetnamen/-reihenfolge/-pfade und SkinShortcuts sichern bzw. inventarisieren. Keine Tokens oder URLs in öffentliche Protokolle.

| Gate | Ausführung und PASS-Kriterium | Status |
|---|---|---|
| A1/L1 | Kalt-/Warmstart: konfigurierte Startgruppe vollständig; Namen und Fokus auch ohne Logo verwendbar. Bei vorhandener Cachebasis ≤5/≤2 s nach Home-Anzeige. 88 ist nur Testbestand, auch andere Gruppengrößen testen. | ANDROID_NOT_TESTED |
| A2/L2 | Echte Logos in Rail und Senderlogo-Fallback sichtbar; Source-/Scope-Wechsel keine falschen Senderbilder. Screenshot, Kontrolle nach Kodi-Neustart/offline. URL/REFERENCE_READY allein kein PASS. | ANDROID_NOT_TESTED |
| S1 | Speicherdiagnose: aktive Mountidentität, tatsächliche freie Bytes, Reserve ≥1 GiB, Schreibbudget und letzter Write/Rename/Readback. Kein falscher Speichergewinn bei zwei Ordnern auf demselben Pool. | ANDROID_NOT_TESTED |
| S2 | Nur wenn tatsächlich separater berechtigter Pool vorhanden: Ziel bestätigen, eigene Probe, kopieren, SHA prüfen, Bildtest ausdrücklich bestätigen, erst dann aktivieren. Originale/SQLite/Fremddateien unverändert. | ANDROID_NOT_TESTED |
| S3 | Gleicher/unklarer/ungeschützter Pool, ENOSPC oder API34-Rechtefehler: verständliche Sperre, keine automatische Auslagerung. Kein Poolnachweis = BLOCKED, nicht PASS. | ANDROID_NOT_TESTED |
| S4 | Migration abbrechen/fortsetzen; kein Verlust, keine Doppelüberläufe, keine automatische Bereinigung. Kodi-Neustart nach Aktivierung. | ANDROID_NOT_TESTED |
| H1 | Desperate Housewives, American Dad und mindestens drei weitere reale aktuelle Sendungen: korrektes Werk, breites TMDB-Backdrop bevorzugt, verifiziertes Szenenbild/offizielles Poster/Fallback. Reale Time-to-first-image getrennt messen. | ANDROID_NOT_TESTED |
| H2 | CSI: Vegas und schneller Senderwechsel: kein Schwarz-/Mini-Thumbnail-Rückfall bei unverändertem Event, niemals Bild des vorherigen Events. Now/Next/Fortschritt bleiben korrekt. Cold/Warm/offline. | ANDROID_NOT_TESTED |
| D1 | Mini-EPG→Detail→Links→Zuordnung: TMDB-TV Charmed 1998 vs 2018, Monk; TMDB-Movie und TVMaze-TV. Quelle/ID/Jahr/Medium prüfen, bestätigen, SAVED/Readback, Bild im ursprünglichen Detail, nach Neustart erhalten. | ANDROID_NOT_TESTED |
| D2 | Arbeiter 5/30 s beschäftigt, fehlende Rechte/Speicher, EPG-Wechsel, Back/Cancel/Kodi-Ende: jeweils korrekter Status, kein pauschales „Abgebrochen“, kein späterer Doppel-/Fremd-Save. EPG-Wechsel ausdrücklich neu bestätigen. | ANDROID_NOT_TESTED |
| F1 | 100× Home→Live→Sender→Mini-EPG→Details→Zurück→Filme→Serien→Zurück während Hintergrundreload. Null native Indexfehler, XCMate-Directoryfehler, 5-s-Kills und Fokusverluste. | ANDROID_NOT_TESTED |
| G1 | Sieben verschiedene Icons; Links Sender→Gruppen→Icon-Rail→Labels, Hoch/Runter/OK/Back. Lokal/offline und nach Artwork-Refresh stabil. Verlassen führt zu XCMate-Home. | ANDROID_NOT_TESTED |
| E1/C1 | EPG auch vor erstem Senderstart lokal vorhanden; DB-/Netzfehler überschreiben keine gültigen Daten. Erst Rail/Logos/erste fünf Events, danach Filme/Serien. Ehrliche kleine Statusanzeige. | ANDROID_NOT_TESTED |
| I1 | 1080p und 720p: feste große Hero-Höhe, links ~2/3 Bild ohne Infotafel, rechts ~1/3 lesbare Infos, Attribution unten rechts; Poster proportional, aktive Rail direkt darunter, Fokus exakt. | ANDROID_NOT_TESTED |
| I2 | Normale vertikale Home-Seite: MP3 Streams Echoed, SHOUTcast, Im/Neu/Frisch im Kino, Diese Woche aktuell/Trend, fremde Serien und ≥2 freie externe Widgets sichtbar und erreichbar. Nicht nur drei XCMate-Reihen prüfen. | ANDROID_NOT_TESTED |
| I3 | Vor/nach Update/Nachladen/Neustart: alle Namen, Reihenfolge, Pfade, Aktivierungen, Shortcuts gleich; zehnmal zwischen Fremdwidgets wechseln, OK/Audio-/Video-/Kategorierouten korrekt. | ANDROID_NOT_TESTED |
| I4 | Vorübergehender Fremdquellenausfall: Definition/Position bleiben, ehrlicher Quellstatus oder eigener letzter Datenstand; später wieder befüllt. Keine ersatzweisen XCMate-Items. | ANDROID_NOT_TESTED |
| R1 | Live-TV-, Film- und Serienwiedergabe/Zurück; Autoplay/Staffelwechsel/Resume, Favoriten/Startsender/manuelle Mappings/TMDB-Zugang erhalten. | ANDROID_NOT_TESTED |

Private ursprüngliche Layout-Screenshotdatei aktuell **REFERENZBILD_NICHT_VERFÜGBAR**. Kein pixelgenauer Vorher/Nachher-Vergleich behauptet. Neue echte Geräte-Screenshots und redigierte Stufencodes pro Gate ergänzen. Ein fehlender separater Speicherpool ist ein reales Hardware-/Rechte-Gate, keine Einladung zum Reserveabschalten.

**Freigabe:** Noch kein Merge und kein Release. Erst tatsächliche Box-B-Abnahme sowie erneute ausdrückliche Nutzerfreigabe.

## Nachträge P0-J/K

| Gate | Ausführung | Status |
|---|---|---|
| J1 | Vor/nach .86→.87, Kodi-Neustart und später ausdrücklich freigegebenem Repoupdate: private Token-Datei byteidentisch und Zugriffsrechte erhalten; lokal vergleichen, keine Token-/Hashwerte veröffentlichen. Echte autorisierte TMDB-Abfrage prüfen. | ANDROID_NOT_TESTED |
| J2 | Ungültige/gesperrte vorhandene Datei, Legacy-Fallback nur bei fehlender Datei, Opt-out und alter Installer: keine stillen Überschreibungen oder Neuimporte. Bewusst gelöschte Kodi-Daten können keinen Bestand erhalten. | ANDROID_NOT_TESTED |
| K1 | Optionaler Gateway bleibt ohne reale Konfiguration aus. Altbox mit Token bleibt lokal. Neue Box erst nach authentifizierter Adminfreigabe; lokale Gerätezulassung über Update/Neustart erhalten. | ANDROID_NOT_TESTED / Server BLOCKED |
| K2 | Gerätewiderruf, Replay, falsches Zertifikat, Ausfall, Ablauf, Abbruch und fehlende Rechte: ehrlicher Status, keine offene TMDB-Anfrage und keine geheimen Werte im Installerjournal. | ANDROID_NOT_TESTED / Server BLOCKED |

Gateway-Client ist ein Entwicklungsprototyp. Infrastruktur, produktive Serverimplementierung und Sicherheits-/Nutzungsbedingungenprüfung fehlen; siehe `GATEWAY_02987_ENTWURF_DE.md`. Installer .5.27 wird eigenständig geprüft und nicht mit .5.26 verwechselt.
