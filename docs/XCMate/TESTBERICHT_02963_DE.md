# XCMate .63 – technischer Testbericht

Der verbindliche Abschlussnachweis ist der grüne CI-Lauf am exakten aktuellen HEAD von [Draft-PR #294](https://github.com/artattakk-creator/kodi-noodleprivate/pull/294). Der Abschlusskommentar nennt Run-ID, Commit, tatsächliche Testanzahl und Paket-SHA256. Die Actions-Artefakte enthalten den vollständigen Host-Testlog, build-verification.json, ZIP und SHA256 sowie native JSON-/PNG-Nachweise. Ein früherer grüner Zwischenstand ist nicht automatisch der fertige .63-Kandidat.

## Reproduzierte Ursachen und Änderungen

[Ausführliche Analyse](ENTWICKLUNG_02963_DE.md). Die bisherigen Grundfehler lassen sich am Code zeigen: getrennter Hero-Bild-/Textaufbau, leere neue Overlay-Snapshots trotz schon gelesener Daten, EPG-Textverlust bei optionalem Artworkfehler und Ablehnung von SMB-/Android-Mountpfaden vor der Tokenformatprüfung.

Die vollständige erste Regression hat außerdem die erhaltene Zukunftsrotation und das unveränderte 40-Verbindungen-Limit geprüft. Beide gemeldeten Rückwirkungen werden im Produktcode korrigiert: die vier Ereignisse des GUI-Snapshots ersetzen kein vollständiges Worker-Fenster; die vorhandene Transaktionsmetadatenzeile wird ohne zusätzliche Verbindung publiziert. Die unabhängige EPG-/Bilddarstellung teilt pro 16er-Seite dieselben vorbereiteten Informationen. Keine Erhöhung des Testlimits und keine Entfernung des Zukunftstests.

Neue Tests unterscheiden den tatsächlichen Publikationszeitpunkt eines Snapshots vom abgefragten EPG-Zeitpunkt. Ein festgehaltener ganzzahliger Batch-Zeitstempel darf einen gerade publizierten Datensatz nicht als aus der Zukunft verwerfen. Laufende Datenpublikationen, manuelle Quellenbindung, Profilwechsel und Ereigniswechsel werden getrennt validiert.

Der GUI-Pfad übernimmt vorbereitete lokalisierte Beschriftungen aus nativen ListItem-Properties/RAM und verarbeitet nur begrenzte DTOs. Ein noch nicht vorbereiteter Labelcache löst keinen Sprachdatei-Lesevorgang im Fokuscallback aus. Die native Darstellung bleibt währenddessen bedienbar.

## Automatisierte Prüfstrecke

- Alle 2.553 bisherigen Testmethoden einschließlich ihrer Skip-Bedingungen bleiben erhalten.
- Alle 624 bisherigen Quelldateien bleiben vorhanden. Genau dokumentierte, hashgenaue Änderungen werden gegen den tatsächlichen .62-Bestand normalisiert; alle anderen Dateien bleiben roh unverändert. 605 bisherige Dateien sind byteidentisch. Original-Icon, VOD-/Serien-Widgetpfade, Providerposter, Skinshortcuts-Bindings, Player-Stop/.42-Modus, Portale, Favoriten, Resume und Autoplay werden nicht pauschal umgeschrieben.
- Native Kodi21.2/Linux/BINGIE2.2.3-Prüfungen: echter Home10000/Container2510, unveränderte 88-Sender-Reihe, Fokus0/1/87, vollständige Scrollreichweite, zwei verifizierte Ereignisbilder, korrektes Neutralmotiv ohne EPG/Logo, keine Fokuswiedergabe, tatsächliche Pixel an mehreren rechten Vollflächenpunkten und weiße Titelpixel im linken Overlay.
- Warme Snapshot-Übergabe im nativen Kodi-Host: dieselben Now/Next-Titel und Ereignisschlüssel; SQLite-/HTTP-Zugriff während der Übernahme gesperrt. Dies ist eine RAM-/Frontendprüfung, kein nativer AV-Startnachweis auf Android.
- VFS-Matrix: explizite SMB-/Android-USB-/Downloads-Quellen, sichere lokale Pfade, URI-/Scheme-/Traversal-Sperren, Teilreads, EOF/Größe, unbekannte Stat-Fähigkeit, physisches Zeilenformat, CRLF, BOM/JSON/Bearer/Leerzeichen, Berechtigungs-/Lesefehler und begrenzte blockierte Aufrufe.
- Privates Tokenziel: atomare Kopie, Quellbytes erhalten, restriktive Dateirechte, Vorabvergleich, Profilwechselabwehr, sichere Erzeugung nur der beiden privaten Kinder sowie unveränderte Ablehnung privater Kind-/Dateisymlinks.
- Menü: Position4 und Remote-Back ohne Zustandsänderung; Position5 getrenntes bestätigtes Deaktivieren; einfacher Import ohne Aktivierung; separate bestätigte Aktivierung nur im aktuellen Profil; maskierte alternative Eingabe und geführte Ersetzung einer ungültigen Privatdatei.
- Adapter: exakte bekannte .62-Dateien, Vorbereitung ohne Änderung, zwingende Zustimmung, unveränderte LiveRow/Widgetbindungen, Backup, zweistufiger Restore und Ablehnung unbekannter Änderungen.
- Paket: vollständiger Build, PO-/Icon-/Pythonvalidierung, ZIP-CRC, sichere eindeutige Pfade, sämtliche Quellbytes, Manifest/Assets und SHA256. Produktions-Publish ist im PR-Lauf SKIPPED.

## Bereits gemessene Zwischenbelege

Isolierter erster VFS-Commit 24de09e: 2.559 Tests PASS in 526,737 s, alle fünf damals vorhandenen nativen Prüfungen PASS, CI 41227503154.

Kumulativer Commit c0e8bcc: 29 neue fokussierte Tests PASS und alle sechs nativen Kodi-Prüfungen PASS in CI 41232766859. Native Vollflächen-/Textpixel, Neutralmotiv, 803 tatsächliche Kataloggruppen und 88 Sender wurden geprüft. Die gemessene warme RAM-Übernahme betrug 102,929 ms beim ersten und 0,798 ms beim zweiten Testsender. Das sind Linux-Hostwerte, keine Android-Messwerte und kein Nachweis der ersten dekodierten Videoframe. Maßgeblich für die Lieferung bleibt der spätere abschließende vollständige Lauf am aktuellen PR-HEAD.

## Grenzen / offene Geräteabnahme

Die verwaltete lokale Umgebung scheiterte beim Start; ausführbare Tests laufen über GitHub Actions. Native Fixtures verwenden einen synthetischen Provider, klar markierte Testbilder und isolierte externe Helfer. Der native Skinshortcuts-Templatecompiler ist gepinnt; der Host-Builder kopiert dessen Ausgabe erst nach ausdrücklicher Zustimmung. Kein Beweis einer echten Android-Skinshortcuts-Generierung.

Reale Box B/Kodi21.3/ARM32, USB-/SMB-Treiberverhalten, eigener echter TMDB-Token und die sichtbare warme 1-Sekunden-Grenze bleiben ANDROID_NOT_TESTED. Keine Nutzerdatei/-Tokenwerte/-Fragmente/-Tokenhashes und keine privaten Kodi-Rohlogs in den Testbelegen. Keine Änderungen an Box A/B.

[Android-Testplan B63-01 bis B63-19](ANDROID_ABNAHME_02963_DE.md) · [Issue-Matrix](ISSUE_ABNAHMEMATRIX_02963_DE.md).
