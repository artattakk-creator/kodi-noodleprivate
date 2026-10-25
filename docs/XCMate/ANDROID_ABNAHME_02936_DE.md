# XCMate 0.1.29.36 – Android-Abnahme

Stand: 25.10.2026, Europe/Berlin. **Regulärer kumulativer Testkandidat / PR #163 / NOT_RELEASED, jetzt einschließlich Artwork #168.** Box A: Kodi 21.2, Android TV 13, RK3528 ARM32, BINGIE/IR. Box B: Kodi 21.3 ARM32/RK3528, bestehendes .35-Profil; Firmware-Androidangabe und API-Level widersprüchlich, keine Android16-Kompatibilität behaupten. Historische 15/15-PASS-Abnahme gilt für Box A/.35 und wird nicht auf Box B übertragen. Alle neuen .36-Ergebnisse auf **beiden Boxen NOT_TESTED**.

**Altes .36-ZIP auf Head 656be1e / SHA256 a7cd88… ist überholt.** Neues ZIP und danebenliegende neue SHA256 verwenden. Kein Wizard-Preview #162; dieser wurde ohne Merge geschlossen. Keine erneute Einrichtung zur Testvorbereitung.

## Vorbereitung ohne Profiländerung

1. ZIP und danebenliegende **neue** SHA256-Datei vom Draft-Branch/CI-Artefakt verwenden; Hash kontrollieren (`sha256sum plugin.video.xtreammate-0.1.29.36.zip`, PowerShell: `Get-FileHash … -Algorithm SHA256`). CI-Artefakt zuerst entpacken und die darin enthaltene Add-on-ZIP installieren, nicht die äußere Artefakt-ZIP. Downloadlinks im PR, Hash/Quelle in [TESTERGEBNISSE_02936.json](TESTERGEBNISSE_02936.json).
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
| **S36-11** | **Provider-Bilderpipeline jetzt enthalten.** Einzelbild-Retry an genau einem bekannten fehlenden Poster prüfen; ergänzend ART36-01–08. Kein globaler Retry. | Quelle/Job/Fehlerklasse getrennt, echter lokaler Poster statt Placeholder, alte READY unberührt. Neuer TMDb-/Fremdbild-Lookup nicht enthalten. | NOT_TESTED |
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

## Pflichtstrecke ART36-01 bis ART36-08 – getrennt auf Box A und B

Vor dem Update, soweit noch möglich, bestehenden **Bildspeicherstatus** nur lesen und Werte notieren. Ist kein Vorher-Snapshot vorhanden, bleibt er unbekannt; dafür nicht downgraden. Nach Update denselben vorhandenen Statusbereich öffnen. Er startet weder globale Retries noch Datenbank-Reparaturen. Portaltyp und Versionsanzeige getrennt notieren. Source-Beobachtung wird durch normales Öffnen einer Film-/Serien-/Senderliste mit maximal einer sichtbaren Seite erzeugt; kein Vollimport/Cache-Purge nötig.

| Gate | Ausführung und harte PASS-Bedingung | Box A | Box B |
| --- | --- | --- | --- |
| **ART36-01** | Read-only Status vor/nach normalem Medienöffnen: **exakte Bytes** frei/gesamt/geschützte Bildreserve/Budget/erfasste Bytes/maximal nächstes Bild, separate Queue-Metadatenreserve, Pause, Source-Felder valid/no_source/invalid, Enqueue, Queue-Counts, Worker-/Lease-/READY-/Versuchszeit erfassen. `UNKNOWN` ist fehlende Beobachtung, kein Beweis für Worker-Ausfall. `0 Jobs` vs `PENDING` vs alle Fehler/erschöpft vs READY trennen. Private Quellwerte/IDs nicht exportieren. | NOT_TESTED | NOT_TESTED |
| **ART36-02** | **Drei unterschiedliche echte Filmcover** normal aus vorhandenen Metadaten nachladen. Jeweils tatsächlich sichtbares Motiv, lokaler `.img`-Pfad/Dateigröße >0 und READY-/Bildstatus. Kodi normal beenden/neustarten: dieselben drei Cover weiterhin da, kein neuer Download erforderlich. Placeholder/Fanart zählt nicht. Keine Demo-/Fixturebilder als Android-PASS buchen. | NOT_TESTED | NOT_TESTED |
| **ART36-03** | **Zwei echte Seriencover plus zwei echte Senderlogos** nachladen und nach normalem Kodi-Neustart sichtbar behalten. Quelle/keine Quelle getrennt, richtigen Sender und richtiges Serienmotiv prüfen. Großer EPG und vorhandener Live-Logo-Cache dürfen verschiedene lokale Ablagen verwenden; tatsächliche Bilddatei prüfen. | NOT_TESTED | NOT_TESTED |
| **ART36-04** | Gemessenen Speicherzustand bewerten: `RESERVE_BLOCKED` bedeutet Mindestfreiraum geschützt, **nicht null freier Flash**; `BUDGET_FULL` ist internes konfiguriertes Bildlimit; `BLOCKED_REAL_DISK` unzureichender Platz für nächsten sicheren Schreibvorgang; tatsächlicher Schreibfehler `PHYSICAL_ENOSPC` separat. Bei ausreichend Platz kein 512-MiB-Default-Hardstop. Bei Reserve-/Hardwareblock **genaue Werte + Grund, BLOCKED statt Download-PASS**. Reserve nicht blind ändern/deaktivieren, keine Partition künstlich füllen. | NOT_TESTED | NOT_TESTED |
| **ART36-05** | Tatsächlich auftretende Source-/HTTP-401/403/404/429-/DNS-/TLS-/Timeout-/INVALID_IMAGE-/CACHE_ERROR-/SQLite-BUSY-Fälle mit fester Klasse/Phase erfassen. Bestehenden Einzelbild-Retry nur gezielt, mit endlichen Versuchen/Server-Cooldown; Pause nicht automatisch aufheben. Nicht gefahrlos reproduzierbare Unterfälle bleiben NOT_TESTED, keine privaten Provider-URLs provozieren oder öffentlich kopieren. | NOT_TESTED | NOT_TESTED |
| **ART36-06** | Mehrere bereits vorhandene READY-Poster/Logos auf Box A **vorher/nachher/neuem Kodi-Start** wiederfinden. Keine Bilddateien entfernt, keine 18k-Job-Neustartwelle, keine neue Queue/Portal-/EPG-/Resume-Initialisierung. Normales begrenztes Abarbeiten bereits zulässiger Jobs ist kein globaler Jobreset. Kein globales `art_retry` zur Vorbereitung. | NOT_TESTED | NOT_TESTED |
| **ART36-07** | Während mehrere Cover ausstehen: Film-/Serienliste scrollen, Suche/IR/Live-TV/Guide bedienen, Auswahl nicht springen lassen. Neue Cover in sichtbarer Reihe ohne Fenster-Neuöffnung. Kodi normal neu starten: vorhandene PENDING-Jobs können ohne neue UI-Enqueue weiterarbeiten; falls kein passender offener Job vorhanden, Unterfall NOT_TESTED. Pausierte Jobs bleiben pausiert. | NOT_TESTED | NOT_TESTED |
| **ART36-08** | S36-01–12, GENRE-01–07 und die 15 Baseline-Gates oben auf der jeweiligen Box prüfen. Keine Rücknahme von Genre/Suche/Startsender/Info/Mini/Stop/Autoplay, keine Wizard-Preview-Dateien/zusätzlichen Keymaps. Vorhandenen Wizard lediglich unverändert lassen, seine Save-/Gruppen-/Progress-/Branding-/Geräteinfo-Nacharbeiten bleiben .37. | NOT_TESTED | NOT_TESTED |

**Bei fehlenden Quellen:** `NO_SOURCE` im lokalen Katalog und ein tatsächlich ungültiges Quellfeld getrennt festhalten. Nachweislich früher verlorenes `cover_big` wird bei einem **regulären** Metadatenimport künftig erhalten; das Update erfindet keine URL und erzwingt keinen globalen Neuimport. Wenn deshalb kein echtes Bild testbar ist, Gate BLOCKED/NOT_TESTED, kein Placeholder-PASS.

**Bei echtem Speicher-/Reserveblock:** Erst ART36-01/04 mit Zahlen ausfüllen. Dokumentieren, ob die Bildreserve oder die separate 32-MiB-Queue-Importreserve blockiert und welches generische Speicherziel betroffen ist. Keine gefälschte Kapazität, keine Cache-Löschung/Reserve-Nullsetzung als Workaround. Geräteinfo-Seite #167 kommt regulär .37; dieser Status ist kein vollständiger Hardwarebericht.

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
S36-11: NOT_TESTED | Providerbild/Einzelretry … | TMDb-Neusuche nicht enthalten
S36-12: NOT_TESTED | Genre-Vorbereitung … s | Neustart/Daten …
Baseline .36: … PASS / … FAIL / … BLOCKED / … NOT_TESTED (15 Gates)
Neue reproduzierbare Restpunkte für .37: …
Box A ART36-01 … 02 … 03 … 04 … 05 … 06 … 07 … 08 …
Box B ART36-01 … 02 … 03 … 04 … 05 … 06 … 07 … 08 …
Genaue Bytes je Box: frei … / gesamt … / Reserve … / Budget … / verwendet … / nächstes Bild …
Queue-Metadaten: frei … / Reserve … | Source-Paket valid … / no_source … / invalid …
Queue-Counts … | service/worker/enrol/transfer/logo … | Lease … | letzter READY-Zeitpunkt …
Tatsächlich heruntergeladene Bilder: Filme …/3 | Serien …/2 | Logos …/2 | nach Neustart vorhanden …
```

Keine privaten Kodi-Rohlogs, Provider-/Stream-URLs, Kontodaten, Suchbegriffe, Portal-/Kanal-IDs oder SMB-Verbindungen veröffentlichen. Für öffentlichen Bericht genügen Gate, feste Diagnosephase/Fehlerklasse, Zahlen, zufällige Generation und anonymisierte Uhrzeit. Kein Merge/Release/Issue-Abschluss allein aufgrund des Hostberichts.

## Speichervertrag / STOR-01 (.36)

Auf **Box A und Box B jeweils NOT_TESTED**: vorhandene lokale Bilder und Dateizahl ohne Reset prüfen; ART36-01–08 mit echten 3 Film-/2 Seriencovern/2 Logos einschließlich Neustart bestehen. Bestehende Speicherverzeichnisse und URL-Keys bleiben gleich, Job-DB bleibt intern. Kein neuer USB-/SMB-Schalter in .36. Neue Dateien werden vor Freigabe zusätzlich zurückgelesen und per SHA256 verifiziert. Echte Speicherblockade mit exakten Bytes als BLOCKED dokumentieren. STOR-02–10 aus dem [verbindlichen Speichervertrag](CODEX_ARTWORK_STORAGE_USB_SMB_BINDING_02936_02937_20261025_DE.md) gehören zusammen mit #106 zur regulären .37, einschließlich **USB UND SMB** und Bestandsmigration; bisher auf beiden Boxen NOT_TESTED.
