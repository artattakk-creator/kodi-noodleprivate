# XCMate 0.1.29.30 – ausführbare Android-Delta-Abnahme

Kumulativer Testkandidat aus separaten Drafts #144 (Stabilität), #145 (Speicher),
#146 (Jetzt-EPG), #148 (Splash), #147 (PO). Kein Release/OTA, kein main-Merge.
Grundlage: [Delta-Testpolitik auf main](ANDROID_DELTA_TESTPOLITIK_AB_02930_20261024_DE.md).
Diese Anleitung ersetzt die längeren pauschalen Regressionsempfehlungen der
Teil-Dokumente: **einmal S1–S5, danach nur die unten betroffenen Delta-Gates**.
Keine erneute vollständige Episode nötig, wenn der unveränderte Autoplay-Code
und die fünf Smokes keinen Regressionshinweis liefern.

Historische .29-Abnahme unverändert: **12 PASS / 16 FAIL / 0 NOT_TESTED**.
A03 war FAIL. M01–M03 und neun weitere Regressionen waren PASS. Host-CI ändert
keinen dieser Android-Werte rückwirkend. Für .30 sind unten alle Gerätefelder
zunächst NOT_TESTED. Bei Vorblocker abhängige Felder BLOCKED/NOT_TESTED erfassen.

## Installation und Datenerhalt

1. ZIP und gleichnamige `.sha256` vom **Testbranch** laden. Auf dem Rechner:
   `sha256sum -c plugin.video.xtreammate-0.1.29.30.zip.sha256` (Windows:
   `Get-FileHash plugin.video.xtreammate-0.1.29.30.zip -Algorithm SHA256`).
2. In Kodi „Addons → Aus ZIP-Datei installieren“ wählen und .30 über .29
   installieren. Bestehendes Profil behalten. Keine Cache-, Portal-, EPG-,
   Favoriten-, Resume-, Bild- oder Job-Löschung durchführen.
3. Kodi einmal regulär neu starten. Addon-Information muss **0.1.29.30** zeigen.
   Dies ist ein manueller Kandidat; der reguläre Updatekanal bleibt bei .29.
   Die alte .29-Installation bleibt als Rückfallpaket verfügbar.

## Fünf kurze Grundprüfungen (ein zusammenhängender Durchlauf)

| ID | Ausführen / erwartetes Ergebnis | .30 |
|---|---|---|
| S1 START | XCMate öffnen; Home/IR reagieren, Portale vorhanden, kein Freeze/Absturz. | NOT_TESTED |
| S2 MEDIEN | Filme und Serien öffnen, je ein Detail, Links-Menü und Back; Fokus bedienbar. | NOT_TESTED |
| S3 LIVE | Bekannten Sender aus der globalen Suche starten; Info/Links, Stop/Back. | NOT_TESTED |
| S4 EPG-GUIDE | Großen EPG öffnen, „Jetzt ansehen“ starten und beenden. Das ist nicht A03. | NOT_TESTED |
| S5 ERHALT | Originalicon, Portale, Gruppen, Mappings, Favoriten, Resume und Autoplay-Einstellung vorhanden. | NOT_TESTED |

## 1. Speicherstabilität #141

**D-MEM1:** Einstellungen → Wartung → Stabilität/Langzeittest → vier Stunden
starten. Messwerte anzeigen: `pointer_bits=32` für den echten ARM32-Test; 64-Bit
ersetzt diesen Nachweis nicht. Mindestens mehrere Stunden Idle, dazwischen einen
bekannten Live-Stream, Medien/Guide/Suche und genehmigte USB-/SMB-Arbeit aus den
anderen Delta-Gates nutzen. Im Menü Phasen IDLE/LIVE/FILM/SERIES/EPG/USB/SMB/UPDATE
markieren. Optional acht Stunden. Addon speichert begrenzte numerische Samples im
privaten Profil (`stability_samples.jsonl` und eine Vorgängerdatei).

RSS/PSS, Threads, FDs, Artwork-Inbox und Portal-Calls gegenüber echten JSON-Reads
vergleichen. Ohne Profiländerung keine Read-/Parseflut, keine MemoryErrors oder
ROOT_MENU_FAILED. Calls können weiter zählen. Prozessspeicher umfasst Kodi und
Playerdecoder; allein zunehmende RSS beweist kein Python-Leck. Fehlendes PSS ist
UNAVAILABLE. Ein Neustart beginnt neue Interpreterzähler.

**D-MEM2:** Nach dem .30-Kaltstart einen regulären Service-Neustart/erneutes Update
des gleichen genehmigten Testpakets testen, Menü danach bedienbar. Kein Invoker-
Kill als Erfolg werten. Der erste .29→.30-Wechsel kann den alten Interpreter nicht
rückwirkend reparieren. Keine aktiven Aufnahmen durch Update abbrechen.

Ausführlicher Messablauf/optionales ADB-Tool:
[STABILITAET_02930_A_DE.md](STABILITAET_02930_A_DE.md).
Status D-MEM1 / D-MEM2: **NOT_TESTED / NOT_TESTED**.

## 2. Speicherquellen #136 – vor Download-/Aufnahme-E2E

**D-ST1:** Beide getrennten Menüeinträge öffnen: „Aufnahmeordner (Live-TV/TS)“ und
„Downloadordner (Filme/Folgen)“. Erste Auswahl zeigt intern / USB / vorhandene
Kodi-Samba-Verbindungen. Unter SMB vorhandene Kodi-Quellen, unter USB angebundene
Geräte; anschließend Ordner innerhalb der Quelle. Abbrechen ändert nichts.

**D-ST2:** Explizit USB als Downloadziel wählen, speichern, Kodi neu starten.
Auswahl bleibt USB. Eine fertige lesbare Datei prüfen (mit D-DL1/2 kombinieren).
Aufnahmeziel dabei bewusst getrennt belassen.

**D-ST3:** Bestehende Kodi-SMB-Quelle wählen, eigenen vertrauenswürdigen Account
und Zielfreigabe bestätigen, speichern, Neustart. Echte Übertragung und Lesen
prüfen; Kodi-Wiedergabe benötigt zusätzlich Kodis eigene Freigabe-Anmeldung.
Keine Gast-/SMB1-/unsignierte Rückstufung. SMB erfordert erreichbaren Server.

**D-ST4:** USB entfernen oder Quelle unerreichbar machen. Klarer Fehler, kein
interner Ersatz. Bei LINK:38 ausschließlich feste STORAGE-Marker aufnehmen:
PICKER_ACTION, SOURCE_CATEGORY, PROBE_BACKEND, code/step/errno. CAPTURE/NATIVE,
DOWNLOAD/TARGET und INTERNAL_STAGE sind verschiedene Fehlerorte. Keine Rohlogs,
Hostnamen, Freigabepfade oder Credentials veröffentlichen.

**D-ST5:** SMB während Kopie unterbrechen, wiederherstellen und Retry ausführen.
Bis zur Größen-/SHA256-Verifikation kein COMPLETE. Geprüfte vollständige lokale
Stage darf wiederverwendet werden. USB-Abziehen/Ersetzen darf nicht intern schreiben.
Status D-ST1 … D-ST5: **je NOT_TESTED**.

## 3. Film-/Episodendownload #135/#63

Erst nach positivem Zieltest. Unterstützte einzelne Mediendateien verwenden;
Manifest/HLS/DASH und DRM sind keine freigegebenen Dateidownloads.

**D-DL1:** Autorisierten ganzen Film auswählen → Links → Download. Bei bisher
unbekanntem Provider-/CDN-Wechsel nur die eigene belegte Zielverbindung freigeben.
Bytes >0 und COMPLETE erst nach vollständiger Datei; keine pauschalen Redirect-
Freigaben. Geheimnisse bleiben lokal, HTTPS-Downgrade/unsichere Ziele gesperrt.

**D-DL2:** Eine ganze Folge herunterladen; Serie/Staffel/Folgennummer korrekt.
Film und Folge jeweils auf intern, physischem USB und SMB ausführen, soweit Ziel
verfügbar. Ergebnisse pro Ziel festhalten, nicht zu einem pauschalen PASS bündeln.

**D-DL3:** Während Übertragung Pause, Fortsetzen und bewussten Abbruch/Retry prüfen.
Keine Doppeljobs/Überschreibung fremder Dateien; keine beschädigte COMPLETE-Datei.

**D-DL4:** Nach Kodi-Neustart Film/Folge aus Downloads abspielen. USB lokal auch
mit ausgeschaltetem Netzwerk prüfen. SMB ist nur bei erreichbarem SMB-Server
abspielbar und wird nicht als netzunabhängig bezeichnet.
Status D-DL1 … D-DL4: **je NOT_TESTED** (pro Ziel gesondert).

## 4. Sofortaufnahme #126

**D-REC1:** Separaten geeigneten Aufnahmeordner wählen/proben. Bekannten direkt
unterstützten MPEG-TS-Sender starten und ca. zwei Minuten aufnehmen. Bytes >0.
Fehler der Speicherprobe von HLS/DASH/TS-Sourcefehler unterscheiden.
**D-REC2:** Manuell beenden; erst nach sicherem Publish COMPLETE.
**D-REC3:** Lokale Aufnahme abspielen, nach Neustart auch offline.
**D-REC4:** Sichere Unterbrechung prüfen: erhaltene part/Fehlerstatus, keine falsche
fertige Datei, keine Portaldatenänderung. Native LINK:38 kann diese Gates blockieren;
die neue Staging-Alternative für Downloads lockert keinen Capture-Vertrag.
Status D-REC1 … D-REC4: **je NOT_TESTED**.

## 5. Jetzt-EPG-Suche #140 / ehemaliges A03

**D-EPG1:** Den tatsächlich gerade laufenden Titel eines Senders im großen EPG
ablesen und exakt in der globalen Suche eingeben → Live-Tab. Auch bei vorhandener
Kurzzeitcache-Abdeckung ohne aktuelle XMLTV-Zeile muss der Titel gefunden werden.
**D-EPG2:** Gefundenen passenden Sender starten, Stop/Back wie S3. Explizite manuelle
Zuordnung muss maßgeblich bleiben; keine Sendung eines anderen Senders/Portals.
**D-EPG3:** Bei fehlendem Treffer den anonymen SEARCH_EPG-Snapshot ansehen:
now_count, xml_now/short_now, manual_missing, alias_count, source_count,
name_hits/programme_hits/matched und NO_EPG/NO_CURRENT_EPG/EPG_UNAVAILABLE/EPG_PARTIAL.
Nur diese Zähler teilen; keine Titel/IDs/URLs oder privaten Kodi-Rohlogs.
Status D-EPG1 … D-EPG3: **je NOT_TESTED**.

## 6. Poster #111

**D-ART1:** Ein wirklich fehlendes Cover in Details → Links → Poster erneut laden.
**D-ART2:** Nachladung mit belegter alternativer Provideradresse desselben Titels
oder eindeutige Ursache (keine Adresse, ungültig, Netzwerk/Cache/Speicherbudget).
Keine zufällige Titelzuordnung und keine komplette Queue-/Cache-Löschung.
**D-ART3:** Vorhandene READY-Poster und nachgeladene Datei nach Neustart erhalten;
bei erfolgreichem Download sichtbares Cover aktualisiert.
Status D-ART1 … D-ART3: **je NOT_TESTED**.

## 7. Hintergrund und Sprache #122/#142

**D-UI1–4:** Home, Filmstart, Serienstart und Suche öffnen: identischer originaler
Space-Splash, lokal/offline, gut lesbarer Text. Fokuswechsel/Cover-Nachladen ersetzt
auf Start-/Suchseiten den Splash nicht. Details dürfen echte Fanarts verwenden.
Originalicon bleibt gleich. Premium-Aktivierung ist keine Voraussetzung.
**D-I18N1:** DE und EN auswählen, SMB-Passwortprompt öffnen: lesbare Übersetzung,
keine POParser-Meldung. Keine Passwörter/Adressen in geteilten Ergebnissen.
Status D-UI1–4 / D-I18N1: **je NOT_TESTED**.

## Kopierbarer Ergebnisblock

```text
XCMate 0.1.29.30 / Kodi-Version: ... / Android-Gerät: ... / Datum: ...
S1 START: NOT_TESTED
S2 MEDIEN: NOT_TESTED
S3 LIVE: NOT_TESTED
S4 EPG-GUIDE: NOT_TESTED
S5 ERHALT: NOT_TESTED
D-MEM1/2: NOT_TESTED
D-ST1/2/3/4/5: NOT_TESTED
D-DL1/2/3/4: intern NOT_TESTED; USB NOT_TESTED; SMB NOT_TESTED
D-REC1/2/3/4: NOT_TESTED
D-EPG1/2/3 (A03): NOT_TESTED
D-ART1/2/3: NOT_TESTED
D-UI1/2/3/4: NOT_TESTED
D-I18N1: NOT_TESTED
Vorblocker / fester Fehlercode: ...
Unveränderte tiefe Baseline nicht erneut geprüft; keine neuen Regressionen: ...
```

Einträge nach echter Ausführung auf PASS oder FAIL ändern. Vorblocker als
BLOCKED/NOT_TESTED mit festem Fehlercode kennzeichnen. Die .29-Historie bleibt
unverändert; CI_ONLY ist kein ANDROID_PASS. Kein Merge/Release ohne Freigabe.
