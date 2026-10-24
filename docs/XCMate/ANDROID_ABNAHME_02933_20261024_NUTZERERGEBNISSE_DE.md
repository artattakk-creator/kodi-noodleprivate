# XCMate 0.1.29.33 – Android-Abnahme: Nutzerergebnisse vom 24.10.2026

**Gerät:** Android TV 13, Rockchip RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung.  
**Version:** `plugin.video.xtreammate` **0.1.29.33**, vom Nutzer unter Add-on-Information geprüft (**V0 PASS**).  
**Integration:** [PR #156](https://github.com/artattakk-creator/kodi-noodleprivate/pull/156) nach ausdrücklicher Nutzerfreigabe gemergt, Repository-Index `addons.xml` auf .33 publiziert.  
**Bilanz des interaktiven Nutzerformulars:** **11 PASS / 3 FAIL / 0 BLOCKED / 1 NOT_TESTED**, insgesamt **15 Einzelmarkierungen**. **Gesamtfreigabe der Suchfunktion: FAIL**; **kein Android-Gesamt-PASS**.  
**Offizielle Soll-Teststrecke:** [ANDROID_ABNAHME_02933_DE.md](ANDROID_ABNAHME_02933_DE.md). Das offizielle Dokument startet mit `NOT_TESTED`-Vorbelegungen; die hier eingegangenen realen Nutzerergebnisse werden **getrennt** protokolliert und dürfen die Ursprungs-Testvorlage nicht rückwirkend umschreiben.  
**Evidenz:** ausgefülltes Chat-Testformular samt Freitext, **keine neuen privaten Kodi-Logs, Screenshots, Trace-IDs, HTTP-Statuscodes, Provider-/TMDb-Nachweise oder sonstigen zusätzlichen Geräteartefakte**. Keine ungeprüfte technische Ursache behaupten.

## 1. Einzeltestmatrix, exakt gemäß Nutzer-Markierung

| Gruppe | ID | Test | Android-Ergebnis |
|---|---|---|---|
| Installation | **V0** | Version 0.1.29.33 installiert | **PASS** |
| Grundlagen | **S1** | Hauptmenü und Fernbedienung | **PASS** |
| Grundlagen | **S2** | Filmdetails | **PASS** |
| Grundlagen | **S3** | Seriendetails | **PASS** |
| Grundlagen | **S4** | Live-TV-Grundtest | **PASS** |
| Grundlagen | **S5** | Großer EPG | **PASS** |
| Suchreparatur | **A1** | Laufende Sendung aus großem EPG suchen | **FAIL** |
| Suchreparatur | **A2** | Sendernamen suchen und Sender bewusst starten / Rückkehr | **FAIL** |
| Suchreparatur | **A3** | Film-/Seriensuche und Zurück | **PASS** |
| Suchdarstellung | **SEARCHUI-01** | Senderlogo und „läuft jetzt“ im Suchresultat | **NOT_TESTED** |
| Suchdarstellung | **SEARCHUI-02** | Filmcover im Suchergebnis | **PASS** |
| Suchdarstellung | **SEARCHUI-03** | Seriencover im Suchergebnis | **PASS** |
| Suchdarstellung | **SEARCHUI-04** | Layout und Fokus | **PASS** |
| Suchdarstellung | **SEARCHUI-05** | Fehlende und nachgeladene Bilder | **FAIL** |
| Suchdarstellung | **SEARCHUI-06** | Stabilität und Bedienung | **PASS** |

**Summe:** 6 Grund-/Installations-PASS + A3-PASS + 4 UI-PASS = **11 PASS**, A1/A2/SEARCHUI-05 = **3 FAIL**, SEARCHUI-01 = **1 NOT_TESTED**, **0 BLOCKED**. **Offizielle .33-Voraussetzung A1+A2+A3 vollständig PASS wurde nicht erreicht**, trotzdem hat der Nutzer vier spezifische SEARCHUI-Funktionen tatsächlich geprüft und positiv bewertet; ihre PASS-Werte nicht wegen der Gate-Reihenfolge nachträglich verwerfen.

## 2. Wortlaut und fachliche Einordnung der Beobachtungen

**Nutzerbericht (verkürzt auf inhaltstreue, nicht sensible Auszüge):**

> „Also die Suche aus EPG heraus funktioniert nicht.“

> „Auch das Umschalten auf den Sender funktioniert nur bedingt. Meistens lande ich wieder auf der Startseite der App. Also nur aus dem EPG heraus, das Umschalten auf den Sender funktioniert nicht richtig.“

> „Ich bin in den Filmen noch mal reingegangen, wo ein Cover fehlte, habe gesagt Poster neu laden. Da kommt nichts. Also da kommt immer noch Zeitüberschreitung der Anforderung.“

> „… ob der mittlerweile schon den Fallback auf TMDB nutzt … auf jeden Fall, das hat nicht richtig funktioniert.“

> Zu SEARCHUI-01: „… bei den Suchergebnissen konnte ich nicht testen, weil [der Sender-Treffer] nicht vorhanden [war].“

### A. #140 – Suchroute und Senderstart aus großem EPG bleiben defekt

- **A1 FAIL:** Suche aus dem großen Guide nach einer aktuellen Sendung **funktioniert weiterhin nicht**. Der mit .32 diagnostizierte BusyDialog-/Window-Release-Defekt aus [Logforensik .32](LOGFORENSIK_02932_20261024_KODI_BUSY_DIALOG_DE.md) war Ausgangspunkt für PR #156; **neue .33-Logs fehlen**, daher ist **nicht bewiesen**, ob wieder `RELEASE_TIMEOUT`, ein anderer `BLOCK_CONTEXT/OWNER`-Pfad, fehlende Ergebnisanzeige oder Titel-Matching die aktuelle .33-Ursache sind.
- **A2 FAIL:** Der kombinierte Test beinhaltet Sendersuche **und** Auswahl/Playback/Rückkehr. Der Nutzer präzisiert, dass **Senderaufruf aus dem großen EPG oft zur XCMate-Startseite statt zum Sender führt**. **Nicht behaupten**, dass der Namensmatcher für alle Sucheinstiege immer fehlschlägt; Such- und Playback-Teil separat diagnostizieren.
- **S4 PASS:** gewöhnlicher Live-TV-Betrieb funktioniert im Grundtest. **S5 PASS:** großer Guide ist zugänglich. Somit ist der **EPG→Senderstart** eine **separate, tatsächlich spürbare Regression** gegenüber dem funktionierenden normalen TV-Start, aber aus Nutzerformulierungen kein nachgewiesener Kodi-Prozessabsturz.
- In der älteren [EPG-Playback-Historie #121](https://github.com/artattakk-creator/kodi-noodleprivate/issues/121) sind vergleichbare Guide-Handoff-Probleme beschrieben; keine automatische Gleichsetzung mit der damaligen Ursache und keine stillschweigende Revision früherer PASS-Werte.
- **A3 PASS:** Film-/Serien-Suche und Zurück funktionieren für die geprüfte Medienroute. Dies ist **keine** Entwarnung für die EPG-Suche.

### B. #127 – Suchdarstellung teilweise bestätigt, Live-TV-Darstellung offen

- **SEARCHUI-02 PASS:** Filmcover **direkt in Suchtreffern** sind sichtbar, nicht nur in Details.
- **SEARCHUI-03 PASS:** Seriencover in Suchtreffern sichtbar.
- **SEARCHUI-04 PASS:** Layout und Fernbedienungsfokus für geprüfte Suchresultate.
- **SEARCHUI-06 PASS:** getestete Stabilität und Bedienung.
- **SEARCHUI-01 NOT_TESTED:** Beim Nutzer erschien **kein prüfbarer Sender-Suchtreffer**. Daraus folgt **kein** Nachweis, dass Logo/Now-EPG der Live-TV-Zeile vorhanden, korrekt oder defekt sind. Nicht als PASS oder FAIL umwerten.
- **SEARCHUI-05 FAIL:** Nutzer berichtet konkret einen **Film mit fehlendem Poster** und **„Poster neu laden“ → Timeout, weiterhin kein Poster**. Der Test umfasst zusätzlich Fallback-Bilder und asynchrones Aktualisieren **innerhalb der Suchtreffer**. **Aus dem Freitext allein nicht belegt**, ob Fallback oder Live-Artwork-Refresh *in der Suche* separat versagt haben. Nutzer-Markierung FAIL bleibt dennoch verbindlich. Details werden in #111 separat weiterverfolgt.

### C. #111 – Poster-Retry/Timeout und TMDb-Fallback als offene Diagnose

- Konkreter Film-Detail-Wiederholversuch: **„Poster neu laden“ löst weiterhin „Zeitüberschreitung der Anforderung“ aus**; Bild bleibt fehlend.
- **Unbekannt:** HTTP-/TLS-/DNS-/Rate-Limit- oder Poster-Provider-Ursache; auch **nicht belegt**, ob der automatische TMDb-Fallback in .33 implementiert ist, gestartet wurde, bei Providerfehler greift oder selbst fehlgeschlagen ist. Das ist eine zu prüfende Funktion, **keine bestätigte aktive Fallback-Nutzung**.
- Datenschutzarme Debug-Phasen pro **genau einem** fehlenden Film-Cover: `provider poster → request/timeout → fallback eligibility → TMDb lookup → candidate validation → cache/queue write → UI refresh` mit sanitisierten Gründen ohne private URL, Suchbegriff, Provider-ID, Token oder Bildinhalt. Kein pauschaler Reset aller Artwork-Jobs oder der bestehenden READY-Bilder.

## 3. Codex-Arbeitsreihenfolge nach dieser Abnahme

1. **#140 Priorität P1:** Nur **zwei kurze .33-Geräterepros** planen: (I) aus großem EPG nach einer laufenden Sendung suchen, (II) aus großem EPG „Jetzt Sender ansehen“/Senderauswahl auslösen. Jeweils getrennt loggen: betätigte Aktion, Guide Window/Modal/Owner-Handoff, Fenster-Return, `SEARCH_NAV`-`BUSY_DEFERRED`/`ASYNC_QUEUED`/`ASYNC_READY`/`BLOCK_*` bzw. `GUIDE_HANDOFF`-`QUEUED`/`SKIPPED`/`DISPATCHED` und erst danach Player-Resolver. **Zeitfenster von .33** erforderlich; **.32-Root-Cause nicht als bestätigt fortschreiben**.
2. **#111 Poster-Retry P1** unabhängig nachstellen: gewählten Film nach gezieltem Retry, konkrete Timeout-Phase, tatsächliche Fallback-Entscheidung, ArtStore-Status/Backoff und lokales Rendering messen. Kein Fallback als aktiviert behaupten, bevor Code-/Runtimepfad geprüft; #151 manuelle Bildquellenwahl weiterhin eigenständiges Ziel.
3. **#127 Rich Search** auf belegten Fortschritt begrenzen: Film-/Serienposter und Fokus aus dem Nutzerlauf **PASS**, Live-TV-Logo/Jetztzeile wegen A1/A2 **NOT_TESTED**, Poster-Retry/Artwork-Nachladen **FAIL**. Nicht vollständig schließen, bevor LIVE-Ergebnisse tatsächlich angezeigt und geprüft sind.
4. **Kumulativ ab aktuell freigegebenem .33/main** weiterarbeiten. Nur gezielter neuer Draft-PR samt Host-/Kotlin/Kodi-nativer GUI-Mocks, Test-ZIP/SHA256 und **kurzen** Android-Gates; noch **kein autonomer Merge/Release**, keine Profil-/EPG-/Cover-Löschung, kein Downgrade. Download-/Recording-Bereiche bleiben nachrangig.
5. **#98** EPG-Quellenkanalwahl mit read-only Guide-Vorschau weiterhin offen und unimplementiert, eigene Folgephase nach stabiler Grundsuche und Senderstart.

## 4. Historische Werte und Freigabe

| Version | Historischer Gerätebefund | Umgang |
|---|---|---|
| **0.1.29.31** | **9 PASS / 8 FAIL / 3 NOT_TESTED** | Unverändert erhalten |
| **0.1.29.32** | **7 PASS / 10 FAIL / 0 NOT_TESTED** | Unverändert erhalten |
| **0.1.29.33** | **11 PASS / 3 FAIL / 1 NOT_TESTED** | **NEU** – dieser Bericht; keine volle Such-/UI-Freigabe |

**#140, #127, #143, #111 bleiben OPEN.** Keine bislang fehlgeschlagenen Geräte-Gates durch Hosttest/CI ersetzen; keine privaten Kodi-Rohlogs, vollständigen Provider-URLs, SMB-Adressen oder Zugangsdaten veröffentlichen.

**Schluss:** Die .33-Mediensuche und Coverdarstellung sind deutlich verbessert (mehrere echte Android-PASS); die **EPG-Suche, der Senderstart aus dem Guide und ein gezielter Poster-Retry bleiben auf dem Gerät nicht akzeptiert**. Technische Root-Cause der neuen .33-Fehler erst nach neuen gerätezeitlich passenden Logs prüfen.
