# XCMate .85 – Android-Abnahme auf Box B

**Alle folgenden Gates: ANDROID_NOT_TESTED.** Kein Host-/Linux-PASS wird übertragen. Box A bleibt unberührt. Erst nach Freigabe .85 als kumulatives ZIP-Update installieren; keine Deinstallation, kein Profil-/Cache-Reset. Kodi 21.3/BINGIE 2.2.3, zuerst 1080p, wenn möglich zusätzlich 720p. Vorher Version, freie Kapazität/Reserve und vorhandene Widgetpositionen privat festhalten.

## A – Start, EPG, Speicher, Bilder

| Gate | Durchführung und tatsächliches PASS-Kriterium | Status |
|---|---|---|
| START85-01 | Kaltstart ohne vorherigen Senderstart: echte horizontale Logos, großer Hero mit begrenztem Senderlogo, lokales Jetzt/Danach und Fortschritt erscheinen. Zeit bis sichtbar messen. | ANDROID_NOT_TESTED |
| START85-02 | Erste fünf sichtbare Sender: passende Eventbilder priorisiert nachladen. Ohne Bild bleibt richtiges Senderlogo; keine Blockade. Private Ereignisidentitäten/Bildquelle dokumentieren. | ANDROID_NOT_TESTED |
| START85-03 | Von 1..5 auf 2..6 und zurück: nur neues Event 6 neu vorbereiten, kein erneuter Komplettscan. Fokus/Hero/Reihenposition unverändert. | ANDROID_NOT_TESTED |
| START85-04 | Film- und Serienreihen zunächst mit verständlichem Status, danach progressive echte Cover. Keine großen Play-Symbole als angebliche Poster. Bereits vorhandene Cover sofort wiederverwenden. | ANDROID_NOT_TESTED |
| START85-05 | Offline/gesperrte Datenbank: kein endloser Busy-Zustand; nach spätestens 60 s verständlicher Fehler/Teilstatus. Eine noch nicht geladene Kategorie niemals als bestätigt leer melden. | ANDROID_NOT_TESTED |
| REV85-01 | Unveränderte Sendung mindestens 30 Minuten fokussieren: Logo, ganze Leiste und bestätigtes Bild bleiben stabil, kein wiederholtes Komplett-Widgetreload. | ANDROID_NOT_TESTED |
| REV85-02 | Reales EPG-Rollover: sofort korrektes neues Event/Logo, alte Bilder nicht falsch übernehmen. Source-/Eventwechsel getrennt diagnostizieren. | ANDROID_NOT_TESTED |
| REV85-03 | Ungültige eigene Testbilddatei nur auf freigegebener Testkopie: FILE_INVALID und begrenzte Wiederherstellung; keine fremden Bilder zulassen. Keine echten Nutzercaches löschen. | ANDROID_NOT_TESTED |
| EPG85-01 | Kurzzeitige DB-/Netzwerkstörung: bestehende gültige lokale EPG-Fakten bleiben erhalten; Groß-/Mini-Details öffnen/schließen bedienbar. | ANDROID_NOT_TESTED |
| SPACE85-01 | Wartungsdiagnose: tatsächliches Volume, Gesamt/frei/Reserve vergleichen. Gleicher Pool wird nicht als Speichergewinn verkauft. Bei Reserveblockade explizit kein Persistenz-PASS. | ANDROID_NOT_TESTED |
| CACHE85-01 | Nur neuen eigenen Tempbereich beobachten: Byte-/Objektobergrenzen, aktive Pins, Wiederverwendung nach Kaltstart. Alte Archive/Kodi-Texturen unverändert. | ANDROID_NOT_TESTED |
| COVER85-01 | 30 unterschiedliche echte Events und mehrere Film-/Serienkategorien mit echten Providerbildern prüfen; mindestens drei Filme und zwei Serien nach Neustart erneut sichtbar. Quelle, Bildzuordnung und Pixel getrennt bewerten. | ANDROID_NOT_TESTED |

## B – Serienerkennung und manueller Manager

| Gate | Durchführung und tatsächliches PASS-Kriterium | Status |
|---|---|---|
| GHOST85-01 | Ghosts ohne Jahr: UK 2019 und US 2021 niemals anhand erster Trefferposition als bestätigt deklarieren. Vorschlag sichtbar unbestätigt oder korrektes Logo. | ANDROID_NOT_TESTED |
| GHOST85-02 | Mit belastbarem Jahr/Land beide Werke getrennt prüfen; kein falsches Episodenstill. | ANDROID_NOT_TESTED |
| SERIES85-01 | Kontexttaste im Groß-/Mini-EPG-Detail; zusätzlich Links nur beim Zurück-Button. Fremde Dialoge bleiben unberührt; alle vier Aktionen erreichbar. | ANDROID_NOT_TESTED |
| SERIES85-02 | Kandidaten mit Titel/Jahr/Land/Poster/Plot/Quelle/ID prüfen. Fernbedienung nach unten bis Kandidat 6..8; Poster nachladen. Listen-OK speichert nicht versehentlich. | ANDROID_NOT_TESTED |
| SERIES85-03 | Richtigen Ghosts-Kandidaten ausdrücklich bestätigen, neue Ausstrahlung öffnen, Kodi neu starten: dieselbe bestätigte Werk-ID nur für passenden Provider/Quelle verwenden. | ANDROID_NOT_TESTED |
| SERIES85-04 | Zuordnung ändern, Automatik wiederherstellen, Vorschlag ausblenden und erneut aktivieren. Andere Serien/Provider/Profile unverändert. Bei Schreibfehler kein Erfolgshinweis. | ANDROID_NOT_TESTED |
| SERIES85-05 | Cobra 11, Die Rosenheim-Cops/Rosenheim Cops, M*A*S*H/M.A.S.H., Modern Family, The Middle, King of Queens: tatsächlichen EPG-Titel privat festhalten, Alias/Identität und sichtbares richtiges Serienbild prüfen. | ANDROID_NOT_TESTED |
| SERIES85-06 | Positive Kontrollen taff, Morden im Norden und mehrere Warner-TV-Filme; funktionierende Filmabfrage bleibt korrekt. Keine EPG-Texte überschreiben. | ANDROID_NOT_TESTED |
| SERIES85-07 | TMDB/TVMaze bewusst deaktivieren: Deaktivierung respektieren, gespeicherten Token unverändert erhalten. | ANDROID_NOT_TESTED |

## Gemeinsame Regression

| Gate | Durchführung | Status |
|---|---|---|
| REG85-01 | Live-TV, Film und Serie starten und Zurück/Stop prüfen; je fünf Zyklen, Autoplay und Resume erhalten. | ANDROID_NOT_TESTED |
| REG85-02 | Bestehende Widgets einschließlich Neu im Kino, Favoriten, Gruppen, Startgruppe/-sender, Suche, Space Blue und SkinShortcuts nach Neustart unverändert. | ANDROID_NOT_TESTED |
| REG85-03 | Upgrade von älterer eingerichteter Version nur auf gesonderter Testkopie vorbereiten; keine Tests auf Box A ohne Auftrag. Kein Token-/Provider-/EPG-Verlust. | ANDROID_NOT_TESTED |

Abnahmeprotokoll: Gate, PASS/FAIL/NOT_TESTED, Version/Kodi/Auflösung, sichtbare Beobachtung, Start-/Endzeit, datensparsame Diagnose. Keine privaten Rohlogs/URLs/SMB-Daten in GitHub. Bilder nur nach tatsächlicher sichtbarer Prüfung als erfolgreich markieren.
