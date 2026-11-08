# XCMate 0.1.29.82 – Android-Abnahme

**Alle Fälle zunächst ANDROID_NOT_TESTED.** Box A nicht verändern.
Nur auf der ausdrücklich vorgesehenen Testbox ein kumulatives ZIP-Update über
Kodi installieren. Keine Deinstallation, kein Profil-/Cache-Reset.
Regulär, Pilot und NeoDark3 bleiben bis gesonderter Freigabe auf .81.

Vorher Version, Kodi 21.2/21.3, Gerät, Artworkmodus und sichtbare Widget-Reihen
notieren. Keine Token, Provideradressen, privaten Profile oder Rohlogs teilen.
Pro Fall PASS / FAIL / ANDROID_NOT_TESTED und tatsächliche Zeit notieren.

| Fall | Durchführung und erwartetes Verhalten | Status |
|---|---|---|
| A82-01 | Upgrade .81; Portale, Token (nur Vorhandensein), Gruppen, EPG-Zuordnung, Favoriten, Resume und Benutzerwidgets einschließlich Neu im Kino erhalten | ANDROID_NOT_TESTED |
| A82-02 | Startseite kalt öffnen, ohne Senderstart oder Pfeiltaste: lokales Jetzt/Danach, Startgruppenlogos, Hero sowie Film- und Serienreihe sichtbar; Zeiten ab Home-Öffnung getrennt notieren | ANDROID_NOT_TESTED |
| A82-03 | Home 30 Minuten stehen lassen; mindestens drei kontrollierte Katalog-/EPG-/Artaktualisierungen; 88 Startgruppensender und 24 Filme sowie Serien prüfen; keine unveränderte READY→PARTIAL-Abwertung/Play-Platzhalter/verschwundene Logos | ANDROID_NOT_TESTED |
| A82-04 | Bestehende Art-DB-Schutzpause beobachten, falls vorhanden: genau ein gesunder Worker, ein gedrosselter Pausencode mit Pause-bis; GUI und letzte Bilder bleiben nutzbar; nach Freigabe kontrollierte Wiederaufnahme | ANDROID_NOT_TESTED |
| B82-01 | Vorhandene Artwork-Status-/Diagnoseansicht öffnen: Free/Total, effektive Reserve, Budget, Mount-/Backendklasse und anonyme Volume-Korrelation erfassen; PROFILE_PROGRAMME gegen PROFILE_METADATA/KODI_TEXTURES vergleichen | ANDROID_NOT_TESTED |
| B82-02 | Nur falls gewünscht: angebotenen sicheren Schreibtest ausdrücklich bestätigen; 4 KiB eigene Testdatei rückgelesen oder klarer Reserve-/Offlinecode; bestehende Bilder unverändert | ANDROID_NOT_TESTED |
| B82-03 | Bei wirklich knappem Ziel bleibt neue Archivkopie blockiert, bestehende Cover werden weiter gelesen; keinen freien Speicher vortäuschen und Reserve nicht herabsetzen; keine automatischen Moves | ANDROID_NOT_TESTED |
| C82-01 | Zwischen Live/Film/Serie wechseln, auf SAT.1 Gold länger bleiben, scrollen/zurück; ausgewählter Sender und Logos bleiben erhalten; kein schwarzer Zwischenframe bei unverändertem Event | ANDROID_NOT_TESTED |
| C82-02 | Kodi zweimal normal neu starten; vorhandene Providerposter und Senderlogos wieder sichtbar; Film-/Serienreihe ohne vorherigen Fokuswechsel | ANDROID_NOT_TESTED |
| C82-03 | Modern Family, Yuna/Stitch, Croods, Harry Potter, Mockingjay sowie American Dad/Percy Jackson vergleichen; richtiger Titel/Jahr/Quelle, kein unbewiesener Alias; Goldrausch als positiver Vergleich; ungeprüfte Titel einzeln NOT_TESTED lassen | ANDROID_NOT_TESTED |
| C82-04 | Großen und Mini-EPG öffnen, tatsächlichen Senderfokus, Jetzt/Danach, Details und sichtbare passende Bilder prüfen; manuelles Mapping erhalten | ANDROID_NOT_TESTED |
| D82-01 | Live starten → Overlay schließen → Vollbild-Zurück → bedienbare vorherige Ansicht; bestehender Kompatibilitätsmodus erhalten; zuerst ein, dann fünf Zyklen | ANDROID_NOT_TESTED |
| D82-02 | Film über Detail-Play tatsächlich wiedergeben, Stop/Zurück und Resume prüfen; Serie einschließlich nächster Episode/Staffel und gezieltem Stop ohne Autoplay | ANDROID_NOT_TESTED |
| D82-03 | 720p und 1080p soweit verfügbar: Full-bleed-Backdrop, proportionaler Posterfallback, halbtransparente Informationen, enge Reihen, korrekter Fokus, kein großer Katalogdialog | ANDROID_NOT_TESTED |

Bei B82-01 darf eine tatsächlich gemessene Reserveblockade nicht als PASS einer
Speicherreparatur gewertet werden. Bei fehlender Mount-/Schreibprobe-Evidenz:
**BLOCKED – Android-Speicherklasse ungeklärt**, inklusive anonymer Zahlen.
Keine DB-Pause durch Beschädigen/Umbenennen einer Nutzerdatenbank erzwingen.
Fault-Injection gehört ausschließlich zu den isolierten Host-/CI-Fixtures.

Abschluss: echte Messzeiten für Cache verfügbar, ListItems veröffentlicht,
Skin-Control aktiv und tatsächlich sichtbares Bild getrennt festhalten.
Kein Test wird allein wegen HTTP200, einer Bild-URL oder eines internen
Ready-Logeintrags als sichtbar erfolgreich bewertet.
