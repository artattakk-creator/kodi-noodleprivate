# XCMate .64 – Android-Abnahme Box B

Alle neuen Prüfungen zunächst ANDROID_NOT_TESTED. Historische .63-Fails bleiben dokumentiert. Box A nicht anfassen. Gerät, Version, Skin und Skinshortcuts vor Beginn lesen.

## Installation und erster kurzer Ablauf

GitHub-Artefaktcontainer entpacken, enthaltenes plugin.video.xtreammate-0.1.29.64.zip gegen die mitgelieferte SHA256 prüfen und als Update installieren. Keine Deinstallation, kein Profil-/EPG-/Cover-/Skin-Reset. Originale Widgetquellen nicht neu verknüpfen.

Ein bekanntes .63-Layout erhält eine sichtbare .64-Diffvorschau. Nur bei gewünschter Änderung ausdrücklich bestätigen; Backup und Rebuild abwarten. Unbekannte Hashes nicht erzwingen. Wiederherstellung im bestehenden BINGIE-Widgetmanager: neuesten .64-Plan auf .63 zurücknehmen, ältere Sicherung danach separat, jeweils nur bei passendem Hash.

Zuerst Home-Livefokus → WELT OK → einmal Zurück. Bei Hänger sofort abbrechen und Zeit/Gerät/Version notieren. Erst danach Film-/Serienfokus und Tokenimport prüfen.

| Gate | Durchführung / erwartetes Ergebnis | Status |
|---|---|---|
| B64-01 | Installierte .64, Kodi21.3, BINGIE2.2.3, Skinshortcuts2.1 sowie anonymisierte Quellen/Adapterhashes prüfen; nichts umkonfigurieren | ANDROID_NOT_TESTED |
| B64-02 | Komplette Live-Startgruppe, kleine 142×72-Buttons, schneller WELT-Start, bestehender .42-Modus und Zurück unverändert | ANDROID_NOT_TESTED |
| B64-03 | Ersten und mittleren Film fokussieren, unten zur Serie, zurück hoch, horizontal scrollen, zurück zu Live; genau ein passender Rahmen ohne Überhang/Geisterbild. Bilder vor/nach sichern | ANDROID_NOT_TESTED |
| B64-04 | Erste zehn echte Provider-Serienposter, Scrollen und Detailstart; Filme unverändert. URI_READY allein genügt nicht | ANDROID_NOT_TESTED |
| B64-05 | DMAX/WELT/Nitro/VOX im Home vergleichen. Vorhandene lokale Guide-Zeilen und manuelle Quellenzuordnung prüfen; schnelle Fokuswechsel niemals mit Fremdsendertext | ANDROID_NOT_TESTED |
| B64-06 | Warm/kalt getrennt messen: Home-EPG sowie erste nutzbare Player-Infoansicht, warmes Ziel ≤1 s nach sichtbarer Live-Oberfläche; Now/Next mit großem EPG vergleichen | ANDROID_NOT_TESTED |
| B64-07 | Echtes passendes Bild, kein Bild, kein EPG und Langtitel: bildfüllendes Motiv/Space-Fallback, vollständiger Text/Progress, keine Überdeckung der Reihen | ANDROID_NOT_TESTED |
| B64-08 | Ein USB-Import: Fehlerphase/Status prüfen, Quelle unverändert, lokale private Kopie, Medium entfernen, Neustartpersistenz. Nach Warnung zuerst Dateistatus prüfen statt Import-Marathon | ANDROID_NOT_TESTED |
| B64-09 | Ein SMB-Import mit gleicher privater Endprüfung, Medium danach nicht benötigt; keine privaten Pfade veröffentlichen | ANDROID_NOT_TESTED |
| B64-10 | Falsches Dateiformat und Abbruch: präziser Code/Phase, keine Secrets, vorhandene Datei erhalten; maskierte Alternative und explizite Ersetzung erreichbar | ANDROID_NOT_TESTED |
| B64-11 | Nur bei FILE_VALID echten privaten HTTPS-Test ausführen. Nur echter Erfolg zählt als TMDB_OK; danach exakter EPG-Film-/Episodenbildtreffer in Hero und großem EPG | ANDROID_NOT_TESTED |
| B64-12 | Neustart: Startgruppe, Widgets, Cover, EPG/Mappings, Portale/Passwörter, Resume/Autoplay und Zurück unverändert; Box A weiterhin unberührt | ANDROID_NOT_TESTED |

## Diagnose und Datenschutz

TOKEN64 protokolliert ausschließlich feste Phasen/Codes, numerischen errno und committed-Flag. Keine Token, Fragmente/Hashes, Pfade, URLs oder Rohfehler veröffentlichen. TOKEN_WRITE vor rename bedeutet fehlgeschlagene Übernahme; IMPORTED_SYNC_WARNING bedeutet lokal geprüft, aber Sync/Dauerhaftigkeit unbestätigt; TOKEN_COMMIT_UNVERIFIED bedeutet bereits geschrieben, Endstatus offen. Zuerst Status und nach Neustart Persistenz prüfen.

SERIES_PROVIDER_ART_MISSING, SERIES_ART_URI_REJECTED, SERIES_ASSET_CACHE_MISS, SERIES_WIDGET_BINDING_MISMATCH und bei belegtem Decoderfehler SERIES_TEXTURE_DECODE_FAIL unterscheiden. SERIES_ART_URI_READY bestätigt lediglich eine Referenz, keine sichtbaren Pixel.

EPG: bestehende guide_v1.sqlite, gleiche Portal-/SID-/Quellen-/manuelle Bindung. Keine zweite Datei kopieren. Echte Datenlücke, nicht passende Zuordnung, veraltete Revision und verzögerte UI getrennt notieren. Die im PR genannten Linux-RAM-Messwerte sind keine Android-AV-Messung.
