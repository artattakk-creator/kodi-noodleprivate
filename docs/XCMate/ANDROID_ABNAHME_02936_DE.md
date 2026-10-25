# XCMate 0.1.29.36 – Android-Abnahme

Stand: 25.10.2026, Europe/Berlin. **Testkandidat / Draft / NOT_RELEASED.** Ziel: Kodi 21.2 Omega, Android TV 13, RK3528 ARM32, Titan BINGIE MOD, bisherige IR-Fernbedienung. Ausgangspunkt .35 mit 15/15 funktionalem PASS. Alle folgenden Ergebnisse gelten ausschließlich für .36 und beginnen **NOT_TESTED**.

## Vorbereitung ohne Profiländerung

1. ZIP und danebenliegende SHA256-Datei vom Draft-Branch/CI-Artefakt verwenden; Hash kontrollieren (`sha256sum plugin.video.xtreammate-0.1.29.36.zip`, PowerShell: `Get-FileHash … -Algorithm SHA256`). Nicht alte Draft-Pakete mischen. Downloadlinks stehen im Draft-PR und [TESTERGEBNISSE_02936.json](TESTERGEBNISSE_02936.json).
2. Bestehendes XCMate .35 über Kodi **„Aus ZIP-Datei installieren“** auf .36 aktualisieren. **Keine Deinstallation, keine Daten-/Cache-Löschung, kein Downgrade**, keine Kodi-Keymap ändern. Der produktive Repository-Index bleibt .35; .36 ist vor Freigabe kein reguläres OTA-Release.
3. Versionsanzeige .36 prüfen. Portale, aktivierte Gruppen/Startsender, Favoriten, EPG-Zuordnungen, Cover und Resume zunächst lediglich kontrollieren. Vorhandene Quellen und Genre-Metadaten verwenden; keine neuen Anbieter anlegen oder Daten exportieren.
4. „Kalt“ = nach normalem Kodi-Beenden/Neustart, **mit erhaltenen Daten**. „Warm“ = erneuter gleicher Ablauf ohne Neustart. Kein Force-Stop während Import/Dateischreiben. Gleiche Gruppe/Sender und tatsächliche Query privat notieren; im öffentlichen Bericht anonymisieren.
5. Nach Update darf der Hintergrunddienst Genre-Metadaten in 128er-Batches lokal nachindizieren. Keine neuen Provider-/Cover-Downloads dafür. Solange nicht fertig, zeigt das vorhandene Suchstatusfeld „Lokaler Index wird geladen …“ und erhält Titelmatches. Abfrage ergänzt höchstens alle zwei Sekunden; nach 120 s Retry-Hinweis. Tatsächliche Erstvorbereitungsdauer separat notieren. Nach einem Retry-Hinweis normal erneut suchen, niemals Reset als Workaround.

## Pflichtstrecke S36

Bei jedem Gate `PASS / FAIL / BLOCKED / NOT_TESTED`, Uhrzeit und ggf. Stopuhrwert eintragen. Ein fehlender lokal belegter Programmtitel ist von einem nicht gefundenen, nur vermuteten Titel zu unterscheiden. Bei Blocker Repro festhalten und unveränderte andere Tests fortsetzen; keine Eigenreparatur der Daten.

| Gate | Konkrete Schritte | PASS nur wenn | Initial |
| --- | --- | --- | --- |
| **S36-01** | Aus großem EPG Suche öffnen; bekannten Sendernamen eingeben. Einmal kalt, dreimal warm. Live-Tab bewusst auswählen, Treffer anwählen, Back. | Erster **sichtbarer, bedienbarer** Namenstreffer in Sekunden; Ergebnis nicht vom Short-Endscan abhängig. Zeit bis Fenster und bis erster Zeile getrennt. Keine alten Query-Treffer. | NOT_TESTED |
| **S36-02** | Im Guide exakt laufenden Titel, Sender und Jetzt-Zeitraum privat notieren; unmittelbar denselben Titel suchen. Einen sicher vorhandenen XMLTV-Now-Titel und, soweit verfügbar, einen Short-Cache-Titel testen; warm wiederholen. Zusätzlich einen dort nicht vorhandenen Titel suchen. | Richtiger Sender mit **echtem Programmtitel**, deutlich schneller als 28,070 s; Engineering-Ziel <10 s für belegte lokale Daten. Kein erfundener Treffer bei unbekanntem Titel. `FIRST_PROGRAMME_MATCH`, `VISIBLE_FIRST_PROGRAMME`, `FINAL` getrennt protokollieren. | NOT_TESTED |
| **S36-03** | Live→Filme→Serien→Live bei gleicher Query; während Ergänzung neues Query; Back, Guide neu öffnen, neue Suche. | Kein unnötiger Live-Neuscan bei reinem Tabwechsel, keine Ghost-Ergebnisse, kein langer GUI-Blocker/RELEASE_TIMEOUT; alle drei Tabs und Fokus unverändert. Endscan kann separat laufen. | NOT_TESTED |
| **S36-04** | Menü-Startsender einmal kalt, dreimal warm starten. Zwischen Wiederholungen bewusst Stop/Home. Jeweils Zeit vom Tastendruck bis Info, Play-Anforderung und tatsächlichem Video notieren. | Ein korrekter Start, keine Startgruppe/-SID verändert, keine fremde Wiedergabe oder Mehrfachstarts; wahrgenommener Vorlauf verbessert. Route jetzt home_start/play_start/play_start_direct statt OTHER. Physical First Frame zusätzlich stoppen/filmen. | NOT_TESTED |
| **S36-05** | Im laufenden Vollbild IR-OK→Info, Links→Mini; schließen und zehnmal warm wiederholen. Nach normalem Neustart nochmals. Eine real vorkommende Pufferphase mitprüfen, falls erreichbar. | Info-/Mini-Steuerung ohne Vollkatalog-/Guide-Rebuild bedienbar, echte Now/Next-Daten oder ehrlicher Leerstatus; aktueller Sender fokussiert. Physischer IR→Display-Wert plus Handler-/Renderwerte getrennt; kein Fokusverlust. | NOT_TESTED |
| **S36-06** | Info→zweites OK/Runter→Weitere→EPG: großer Guide, Back zum selben Stream. Anschließend fünfmal aus Guide anderen Sender starten und Guide erneut öffnen. | Großer horizontaler Guide, kein unbeabsichtigter Stop/Home-/Busy-Wechsel; genau ein Senderstart; Links bleibt Mini, Links erneut Gruppen. | NOT_TESTED |
| **S36-07** | **20 Zyklen**: Senderstart→Info/Mini öffnen/schließen→bewusst Stop oder Back mit Exit-Absicht→Home. Varianten: Home bereits im Videos-Verlauf, anderer XCMate-Ordner, laufender Wechsel/Puffer, wiederholtes schnelles Back/Stop. Fremdes Kodi-Video separat starten und XCMate-Rückkehr prüfen. | Keine doppelte Home-URL-/Directory-Anforderung, kein GetDirectory-Fehler, kein automatisch nachlaufender Startsender, keine fremde Player-Stop-Aktion. Pro bewusster eigener Route höchstens ein Directory-Abschluss; vorhandene Home darf ohne neue Route wiederverwendet werden (`HOME_REUSED`). Fremde Dialoge nicht schließen. | NOT_TESTED |
| **S36-08** | Film-/Seriensuche mit Postern; Details, Staffel/Episode, Resume, Back. Natürliches Episodenende einschließlich Staffelwechsel; bewusst Stop. | Unveränderte Suchmaske/Logo/Cover/Fokus/Back, Medienbereiche funktionieren. Autoplay nur nach natürlichem Ende, kein Autoplay nach Stop; Fortschritt/Gesehen-Daten erhalten. | NOT_TESTED |
| **S36-09** | Großes EPG erstmals öffnen, gespeicherte Startgruppe/-sender prüfen; andere Gruppe wählen und zurück. Mini beim tatsächlich laufenden Sender öffnen. Eine bestehende deaktivierte Gruppe bewusst über vorhandene Verwaltung aktivieren, kontrollieren und eigene ursprüngliche Auswahl wiederherstellen. | Einstellungen nicht ungefragt verändert; aktuelle SID statt erster Zeile markiert; neu aktivierte Gruppe verliert keine vorhandenen gecachten Sender. Manuelle EPG-Mappings/Quellen und Favoriten erhalten. | NOT_TESTED |
| **S36-10** | GENRE-01–07 unten vollständig durchführen. | Belegtes Genre in bestehenden Film-/Serientabs auffindbar, Titelpriorität, richtige Gruppen, keine Phantomgenres/Dubletten; akzeptable Erstvorbereitung und Query-Latenz. | NOT_TESTED |
| **S36-11** | Neuer Poster-/TMDb-Fix **nicht Bestandteil**. Optional vorhandenen Einzelbild-Retry an genau einem bekannten fehlenden Poster beobachten, ohne globalen Retry. | **Kein neuer Fix-PASS ableitbar.** Konkrete Fehlerklasse/Phase datensparsam notieren; READY-Poster unberührt. Implementierungsrest #111 BLOCKED, Untersuchung .37. | NOT_TESTED / nicht enthalten |
| **S36-12** | Kodi normal neu starten, Genre erneut suchen, Medien/Guide/Resume prüfen. Bei laufender lokaler Nachindizierung Suche schließen/Kodi normal beenden und nach Neustart erneut versuchen; keine Daten löschen. | Bestehende Daten vollständig erhalten, vorbereiteter Genre-Index weiter nutzbar oder sauber wiederaufgenommen; keine Endlos-Retries, OOM-/neue DB-Fehlerschleife. C3–C5 keine separate neue Funktion dieses Pakets. | NOT_TESTED |

## GENRE-01 bis GENRE-07

| Gate | Ausführung / Erwartung | Initial |
| --- | --- | --- |
| GENRE-01 | Film und Serie mit vorhandenem Genre Sci-Fi und anderem Titel suchen: `Sci-Fi` trifft im jeweiligen bestehenden Tab. Metadaten müssen das Genre tatsächlich belegen. | NOT_TESTED |
| GENRE-02 | `Western` für vorhandene entsprechende Film-/Seriengenres. Ein Western-Titelmatch steht vor reinem Genre-Treffer; keine Dublette desselben Titels. | NOT_TESTED |
| GENRE-03 | `Science Fiction`, `sci fi`, `Science-Fiction` ergeben dieselbe belegte Genre-Menge; ursprüngliche zusätzliche Titelmatches dürfen sich je Schreibweise unterscheiden. | NOT_TESTED |
| GENRE-04 | Titel ohne Genre und Kategorie-ID ohne Genrelabel werden nicht künstlich als Western/Sci-Fi klassifiziert. Unbekannte Genrezeichenfolgen werden nicht geraten. | NOT_TESTED |
| GENRE-05 | Gemischte Query, z. B. Sci-Fi plus ein echtes Titelwort; mehrere Genres mit AND. `Sci-Fi 2024` verlangt 2024 im Titel, nicht lediglich year-Metadaten. Reihenfolge exakt Titel→Titelteil→Genre, aktive Gruppen/Portal und Pagination korrekt. | NOT_TESTED |
| GENRE-06 | Vorhandenen großen Medienkatalog verwenden; Kalt-/Warm-Query-Zeiten, Erstnachindizierung und Genre-Counts getrennt notieren. Scroll/Fokus/Poster/Detail/Staffel/Back erhalten; bei fehlender Datenmenge BLOCKED statt Fake-PASS. | NOT_TESTED |
| GENRE-07 | Nach Genreprüfung Sendernamen-/echte Now-Programmtitelsuche und drei Tabs wiederholen. Genre gilt nicht implizit für Live-TV, keine erneute Scan-/UI-Regression. | NOT_TESTED |

## Unveränderte 15 funktionale Baseline-Gates aus .35 erneut prüfen

Historische .35-Ergebnisse bleiben PASS. Die folgenden **neuen .36-Ergebnisse** sind unabhängig davon zunächst NOT_TESTED. Vollständige ursprüngliche Schritte: [ANDROID_ABNAHME_02935_DE.md](ANDROID_ABNAHME_02935_DE.md), finale historische Qualifikationen: [ANDROID_ABNAHME_02935_LOGFORENSIK_FINAL_20261025_DE.md](ANDROID_ABNAHME_02935_LOGFORENSIK_FINAL_20261025_DE.md).

| Baseline-ID | Erwartung in .36 | Neues Ergebnis |
| --- | --- | --- |
| V0 | .36 installiert, Originalicon, Profil/Portale erhalten | NOT_TESTED |
| PERF-01 | Sendername sichtbar und bedienbar, kalt/warm messen | NOT_TESTED |
| PERF-02 | Exakter belegter Now-Titel, richtiges Programm/Sender | NOT_TESTED |
| PERF-03 | Tabs/gleiche Query/neue Query/Back ohne unnötigen Neustart | NOT_TESTED |
| PERF-04 | Fehlendes EPG/Short-Timeout blockiert Namenssuche nicht | NOT_TESTED |
| ROUTE-01 | Info-EPG-Button öffnet großen Guide | NOT_TESTED |
| ROUTE-02 | Guide/Back erhält laufende Wiedergabe | NOT_TESTED |
| ROUTE-03 | Guide-Senderwechsel genau einmal | NOT_TESTED |
| ROUTE-04 | Links→Mini→Gruppen, Reaktionszeit separat | NOT_TESTED |
| GROUP-01 | Gespeicherte aktivierte Startgruppe/-sender | NOT_TESTED |
| GROUP-02 | Ausdrückliche Gruppenwahl/Fallback ohne Konfigurationsänderung | NOT_TESTED |
| MINI-01 | Tatsächlich laufender Sender richtig markiert | NOT_TESTED |
| REG-01 | Gleiche 3-Tab-Suche, Medien/Cover/Staffeln/Details/Back | NOT_TESTED |
| REG-02 | Autoplay/Resume und Staffelwechsel, bewusster Stop | NOT_TESTED |
| REG-03 | Guide→Suche→Back→Player, IR/Icon/Portal/Mappings erhalten | NOT_TESTED |

## Ausfüllbarer Zeit-/Ergebnisbericht

```text
Installiert: 0.1.29.36 | ZIP SHA256: … | Datum/Uhrzeit (Europe/Berlin): …
Kodi/Android/ABI/Skin/Remote: …
S36-01: NOT_TESTED | kalt … s | warm 1/2/3 … s | Repro/Beleg …
S36-02: NOT_TESTED | lokaler Titel belegt? … | erster sichtbarer Treffer … s | FINAL … s
S36-03: NOT_TESTED | Querywechsel/Back/Tabfolge …
S36-04: NOT_TESTED | kalt/warm Route→Play … | physisch Taste→Video … | Taste→Info …
S36-05: NOT_TESTED | kalt/warm Taste→Info … | Links→Mini …
S36-06: NOT_TESTED | 5 Wechsel …
S36-07: NOT_TESTED | Zyklen bestanden …/20 | HOME_REUSED/REQUESTED/Directory …
S36-08: NOT_TESTED | Episode/Staffel/Stop/Resume …
S36-09: NOT_TESTED | Startgruppe/aktuelle SID/Checkboxen/Mappings …
S36-10: NOT_TESTED | GENRE-01 … 02 … 03 … 04 … 05 … 06 … 07 …
S36-11: NOT_TESTED / neuer Fix nicht enthalten | optionaler Einzelbildbefund …
S36-12: NOT_TESTED | Genre-Vorbereitung … s | Neustart/Daten …
Baseline .36: … PASS / … FAIL / … BLOCKED / … NOT_TESTED (15 Gates)
Neue reproduzierbare Restpunkte für .37: …
```

Keine privaten Kodi-Rohlogs, Provider-/Stream-URLs, Kontodaten, Suchbegriffe, Portal-/Kanal-IDs oder SMB-Verbindungen veröffentlichen. Für öffentlichen Bericht genügen Gate, feste Diagnosephase/Fehlerklasse, Zahlen, zufällige Generation und anonymisierte Uhrzeit. Kein Merge/Release/Issue-Abschluss allein aufgrund des Hostberichts.
