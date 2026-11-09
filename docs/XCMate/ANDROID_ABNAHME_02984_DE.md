# XCMate .84 – Android-Abnahme Box B

Alle folgenden Tests: **ANDROID_NOT_TESTED**. Box A unverändert lassen. Kein automatisches Update, kein Downgrade, keine Deinstallation, kein Reset. Test-ZIP erst nach Freigabe gezielt auf Box B als Update installieren. Regulär/Pilot/NeoDark3 bleiben auf dem bisherigen Stand.

Vorher Version, Kodi-Version, bestehende Artwork-Moduswahl, tatsächlichen Cache-Pfad und freien Platz notieren. Persönliche Quellen/Token/SMB-Details nicht öffentlich dokumentieren. Bei Fehlern kurze redigierte Codes und Zeitpunkte sichern; keine Rohlogs hochladen.

| ID | Durchführung / geforderter Nachweis | Status |
|---|---|---|
| IMG84-01 | .83 → .84 als ZIP-Update. Provider, TMDB-Token, Startgruppe, EPG, Favoriten, Skin und Widgets erhalten; Modus unverändert. | ANDROID_NOT_TESTED |
| IMG84-02 | Home direkt ohne Senderstart öffnen. Jetzt/Danach, Sendername und Fortschritt aus lokalem EPG. Startsender und erste fünf echte Logos sichtbar, danach gesamte konfigurierte Gruppe. Screenshot. | ANDROID_NOT_TESTED |
| IMG84-03 | Verfügbares, zum Ereignis passendes Sendungsbild im großen BINGIE-Hero sichtbar. Quelle, exaktes Matching, Kodi-Texturprüfung und Screenshot dokumentieren. Senderlogo-Fallback zählt nicht als Eventbild-PASS. | ANDROID_NOT_TESTED |
| IMG84-04 | 24 Filme und 24 Serien mit Providerpostern; sichtbare erste Bilder und passende Fanart. Scrollen, Tabs, Rückkehr und längeres Verweilen: keine Rückstufung auf Play-Icons. Screenshots beider Bereiche. | ANDROID_NOT_TESTED |
| IMG84-05 | Mini-/Groß-EPG-Details desselben Ereignisses: richtiges Bild oder ehrlicher Fallback, keine Bildverwechslung, Texte bedienbar. | ANDROID_NOT_TESTED |
| IMG84-06 | Tatsächlicher Speicher-/Reservebefund: Pfad, total/available/reserve/Dateisystem getrennt erfassen. Keine Reserveabschaltung oder automatischer Moduswechsel. Netzwerk-/Quellenfehler getrennt von Kapazität bewerten. | ANDROID_NOT_TESTED |
| IMG84-07 | Zwei reguläre Kodi-Neustarts; vorhandene Kodi-Texturen werden wiedergefunden. Kurz offline testen. Ungecachtes/abgelaufenes Bild darf als nicht verfügbar gelten, nie ein fremdes Event übernehmen. | ANDROID_NOT_TESTED |
| IMG84-08 | Live-TV, Film und Serie starten/verlassen. Fokus, Gruppen, Back, Autoplay und Resume bleiben funktionsfähig. Keine ungefragte Änderung persönlicher Skin-Einstellungen oder Keymaps. | ANDROID_NOT_TESTED |

Freigabe erst bei tatsächlichen sichtbaren Logos, mindestens einem passenden Live-Sendungsbild und mindestens einem sichtbaren Film- und Serienposter auf Box B. URL-, RAM_ONLY-, Hosttest- und Linux-Screenshot-Erfolg ersetzen diese Freigabe nicht. Reservesperre, fehlende Quelle, URL-Blockade, Dekodierung und Textur-/Sichtbarkeitsnachweis getrennt berichten.

## Verbindliche visuelle Nachträge aus dem Änderungsblock

Die zehn privaten Fotos belegen den vorherigen Gerätestand, kein .84-PASS. Native CI-Bilder sind synthetische Linux-Testbilder. Für Box B getrennt prüfen:

| ID | Durchführung / tatsächlicher Nachweis auf Box B | Status |
|---|---|---|
| VIS84-01 | Kalt-/Warmstart: reale Senderlogos und Startsenderlogo im Hero bis zum richtigen Eventbild. Logo maximal begrenzt, kein schwarzer Zwischenzustand. Zeit und Screenshot dokumentieren. | ANDROID_NOT_TESTED |
| VIS84-02 | „Im Reich des Blauwals“ bzw. derselbe eindeutig verfügbare positive TMDB-Fall: richtiger widescreen-Hero, Attribution, EPG und kein Bildwechsel zu fremdem Event. | ANDROID_NOT_TESTED |
| VIS84-03 | XMLTV „Entschlüsselt“ (Portrait) / „Alle unter einem Dach“: proportional in Hero und Details, keine verzerrten Gesichter oder aggressives Cropping. | ANDROID_NOT_TESTED |
| VIS84-04 | DS9: nur nach eindeutigem Werk-Match korrektes Serienbild mit `series_fallback`-Attribution; sonst kleines SYFY-Logo und lokale Diagnose. Kein erfundenes Episodenstill. | ANDROID_NOT_TESTED |
| VIS84-05 | Film-/Serienwidgets zeigen echte Providerposter statt ausschließlich Play-Symbolen. Jede sichtbare Quelle/Medienzuordnung prüfen, danach Tabs/Reload/Neustart. Keine privaten URLs veröffentlichen. | ANDROID_NOT_TESTED |
| VIS84-06 | Hero-Testhöhe 620, Rail tiefer, engerer Film↔Serienabstand. Erste Filmreihe sichtbar, Serienreihe durch Scrollen erreichbar, Fokus exakt am Element, kein Text-/Panel-Overlap. Finale Werte anhand echter 1080p-Screenshots beurteilen. | ANDROID_NOT_TESTED |
| VIS84-07 | Rechte 90%-Navy-Tafel auf hellstem XMLTV-/TMDB-/Logomotiv prüfen: Titel, Now/Next, Beschreibung, Progress und Quellen lesbar. | ANDROID_NOT_TESTED |
| VIS84-08 | Sichtfenster 1–5 → 2–6 und zurück: nur neues Event 6 nachladen, bestehende Bindungen behalten. Kein Massendownload. Eigener Bilddatei-LRU/Pins/Grace noch OPEN, deshalb kein Gesamt-PASS für diesen Teil. | ANDROID_NOT_TESTED |
| VIS84-09 | Kein `KODI_LIBRARY_MISSING_VIEWS`, `IMAGE_READY` oder Timeout-Technikcode im normalen Detail-/Hero-Text. Bibliotheksdiagnose getrennt und read-only; funktionierende Provider-/XMLTV-Bilder unabhängig. | ANDROID_NOT_TESTED |
| VIS84-10 | Live-/Film-/Serienstart und Exit, Fernbedienung, Back, Fokus, Gruppen, Resume/Autoplay, abgesicherte Skin-Vorschau/Upgrade/Rollback, Offline/Reload. Persönliche Widgets unverändert. | ANDROID_NOT_TESTED |

## Abschnitt E – The Middle / King of Queens

| ID | Durchführung / Abnahmekriterium | Status |
|---|---|---|
| SERIES84-01 | „The Middle“ ohne Genre/Staffel/Folge, mit und ohne EPG-Jahr: vollständige TV-Treffer + unabhängige ID-/Jahresprüfung. Wenn eindeutig und Bild vorhanden: tatsächlich passendes Serienbild im EPG und Hero, kein bloßer URL-PASS. Sonst lokale eindeutige Diagnose. | ANDROID_NOT_TESTED |
| SERIES84-02 | „King of Queens“: nur offizieller verifizierter „The King of Queens“-Alias, kein freies Artikelentfernen. Passendes Serienbild oder ehrlicher begrenzter Senderlogo-Fallback. | ANDROID_NOT_TESTED |
| SERIES84-03 | Mehrdeutige/gleichnamige Film-/Serienwerke, falsches Jahr oder falsche Episode nicht übernehmen. Eindeutige Episode ohne Still darf nur ein korrekt gekennzeichnetes Serienbild zeigen. | ANDROID_NOT_TESTED |
| SERIES84-04 | Drei Wechsel Film↔Serie, danach mehrere Stunden im EPG vorwärts: funktionierende TMDB-Filmbilder erhalten, kein Token-Reimport, keine Bilder des vorherigen Ereignisses nach Rollover. | ANDROID_NOT_TESTED |
| SERIES84-05 | Bewusste TMDB-/TVMaze-Deaktivierung erhalten; kein Netzwerkzugriff entgegen Freigabe. Aktivierungszustand und anonymisierten lokalen Diagnosegrund erfassen. | ANDROID_NOT_TESTED |

Keine Gerätefernsteuerung oder Installation in dieser Entwicklungssitzung. Offene Datei-LRU-/Cover-Viewport-/Cursor-Arbeiten stehen im [Implementierungsbericht](IMPLEMENTIERUNG_02984_BILDER_ZUERST_DE.md); diese Liste ist kein Anspruch auf vollständige Releasefreigabe.
