# XCMate 0.1.29.85 – Implementierung und Ursachenanalyse

Basis: veröffentlichtes .84, `faf83b833a14ac1cc937692e10a058d6a4dd462b`. Ein Branch `fix/xcmate-02985-two-workstreams`, ein Draft-PR. Kein Merge und kein Repository-Release freigegeben. Installer 0.5.26 und Box A unverändert.

## Baustelle A – implementiert

- `artwork_temp85`: Neuer, ausschließlich XCMate-eigener temporärer Bereich `artwork_temporary85`. Standard 16 MiB/64 Bilddateien; konfigurierbar, harte Obergrenzen 64 MiB/256. Höchstens 3 MiB pro vollständig dekodiertem Bild. LRU/TTL und kurzlebige aktive Pins; nur eigene indexierte Dateien können entfernt werden. Vorhandene Archive, Kodi-Thumbnails und fremde Dateien bleiben unverändert. Unbekannte Restdateien zählen gegen Limits beziehungsweise blockieren kontrolliert; sie werden nicht blind gelöscht.
- Journal: Eigentumsmarker, Dateiinode/-gerät, Größe und SHA256; atomare Indexveröffentlichung mit fsync. Ein nach Body-Rename unterbrochener Commit wird verifiziert wiederaufgenommen. Symlinks, geänderte Journalziele und unklare Eigentümerschaft werden abgewiesen. Aktive Dateireferenzen können nicht durch den eigenen LRU verdrängt werden. Auch Metadaten und unjournalisierte Crash-Reste sind begrenzt.
- `render_temp85`, `widget_assets69`, `render_cache81`: Vorhandene Worker wiederverwenden. Sichtbare Cover begrenzen; vorübergehende Downloadfehler mit Backoff behandeln. Alte Archive nur lesen, keine Migration. Quellensicher geprüfte HTTPS-Referenzen und vorhandene Kodi-Texturen bleiben bei Reservesperre nutzbar. Ein URL-/Decode-Erfolg ist kein Android-Pixelnachweis.
- `home_loading85`: `LOADING_CATALOG`, `LOADING_ART`, `READY_PARTIAL`, `READY`, bestätigtes `EMPTY`, `ERROR_RETRYABLE`. Nach 60 Sekunden endet ein erfolgloser Busy-Zustand. Keine erfundenen Prozentwerte. Film-/Serienpositionen und 620-Pixel-Hero bleiben konstant. Letzte Medien-Viewportposition je Art merken, auch bei Fokuswechsel zu Live-TV.
- `widget_snapshot85`, `widget_readonly56`, `widget_fast69`: Kurzer 24-Zeilen-Memo mit DB-/WAL-Dateigeneration und Policybindung. Semantischer Digest ignoriert ausschließlich Bildlease-/Prozentfortschritt, nicht echte Quell-/Bild-/Metadatenänderungen. Gleiche bereits vorbereitete Inhalte lösen keine wiederholten kompletten Read-only-Neuladungen aus.
- `epg_snapshot75`: Schreibreserve vor neuen Checkpoints prüfen und Fehler begrenzt zurückstellen. Bestehenden gültigen Snapshot erhalten. `programme_events46` nutzt bei vorübergehend nicht verfügbarem Schedule einen bereits quellensicher gebundenen lokalen Snapshot; kein unvalidiertes Übernehmen fremder Kurzcaches.
- `programme_revision85`, `programme_requests68`, Detailfenster: `EVENT_CHANGED`, `SOURCE_CHANGED`, `FILE_INVALID`, `EXPIRED`, `POLICY_CHANGED`, `NO_SOURCE_FACTS` unterscheiden. Neuer aktueller Proof wird dedupliziert angefordert; bei fehlenden Quelldaten maximal drei gezielte Metadaten-Leseversuche. Alte/falsche Bilder werden nie unter neuer Identität legitimiert.
- `storage_report85`: Schreibfreie Diagnose des tatsächlich verwendeten Profil-, EPG-, Archiv- und Temp-Pfads: statvfs, Geräteidentität, passender Mounttyp und effektive Reserve. Ausgabe enthält Zahlen/Hashes statt privater Pfade. VFS-/SMB-Ziele werden hier nicht automatisch getestet.

### Bestätigte Codeursachen und Grenzen A

Die .84-Codepfade enthielten wiederholbare Warm-/Readonly-Republication bei ablaufenden Empfangsbelegen, eine fehlende Reserveprüfung am EPG-Checkpoint und keine begrenzte neue Bilddateilebensdauer. Diese Pfade sind mit synthetischen Tests überprüfbar. Die reale anonymisierte Loganalyse belegt zusätzlich starke Speicher-/EPG-Probleme, aber nicht deren vollständige physische Ursache.

Das untersuchte reale Log meldet **26.935.296 B frei bei 80.685.957 B Reserve** auf einem FUSE-Pool von ungefähr 3,76 GiB. Das ist weder ein Beweis für Bilderverbrauch noch für einen separat nutzbaren großen Android-Speicher. .85 senkt keine Reserve und schafft keinen physischen Platz. Bei dieser Lage bleiben persistente Writes gegebenenfalls ausdrücklich blockiert; direkte geprüfte Darstellung/RAM-Fallback bleiben möglich. Kein Hardware-Erfolg behauptet.

## Baustelle B – implementiert

- `programme_candidates85`: Höchstens drei TMDB-TV-Suchseiten/60 Kandidaten und acht unabhängige Werkdetails. Vollständigkeit und mehrdeutige Werke getrennt behandeln. Offizielle Alternativtitel prüfen; Genre-/Episodenfelder sind bei anderweitig eindeutiger Identität nicht zwingend. Bei unbekanntem Medientyp erfolgt zusätzlich begrenzte Filmabgrenzung. Verlässliches Werkjahr/Land/externe Werk-ID beeinflussen die Entscheidung; Sendername oder API-Reihenfolge allein beweisen nichts.
- `programme_tvmaze85`: Zustimmung respektierende Werk-/Alternativnamensprüfung. Bestehende genaue Staffel-/Folgenprüfung bleibt erhalten. Keine abgeleiteten Episodenbilder oder EPG-Fakten aus einem Serienvorschlag.
- Mehrdeutige Serien dürfen nach Nutzerwunsch ein Poster als **„Bildvorschlag – Zuordnung nicht bestätigt“** zeigen. Das bleibt `PROVISIONAL_TV85` und wird nicht als bestätigter positiver Werk-/Episodenbeleg gespeichert. TV-/Film-Konflikte, Opt-out und ausgeblendete Werke behalten den sicheren Fallback.
- `series_manager85`, `series_requests85`, `XCMateSeries85.xml`: Kontexttaste im EPG-Detail oder Links bei fokussiertem Zurück-Button. Zuweisen/Ändern, Automatik, Vorschlag ausblenden. Auswahlfenster mit Titel, Originaltitel, Jahr, Land, Beschreibung, Poster, Quelle und ID. Listen-OK allein speichert nichts; eigener Bestätigungsbutton. Abbrechen verändert keine Zuordnung. Kandidaten und Vorschaubilder laufen auf dem bestehenden Dienstworker; zusätzliche Poster bei Bedarf nachfordern. Fremde Modaldialoge werden nicht geschlossen.
- `programme_mapping85`: Explizite Nutzerwahl atomar in einem begrenzten privaten JSON-Journal mit Cold-Readback speichern. Profil, Provider-Konto, Sender, stabile EPG-Quelle und Werkidentität gemeinsam binden, nicht Ausstrahlungsstart. Fehlende Quellenfakten erhalten einen Konfigurationskontext-Hash. Keine privaten Identitätswerte/URLs/Tokens in Logs. Je Werk eigener Mapping-Epoch; Ändern/Automatik/Verbergen invalidiert nur dessen Bildproofs. Bei fehlendem Schreibraum wird kein Speichererfolg behauptet.

### Grenzen B

Eine redaktionelle oder semantische Plot-Deutung ist kein automatischer Identitätsbeweis. Ohne belastbare unterscheidende Fakten bleibt Ghosts UK/US mehrdeutig; die manuelle Auswahl löst diesen Fall bewusst. Kandidatenbilder und vollständige Bedienung auf Android sind noch zu prüfen. Ein in den Logs anonymisierter Cachefehler wird keiner benannten Serie als nachgewiesene Ursache zugeschrieben.

## Offen / ausdrücklich kein PASS

- Alle realen Box-B-Bild-, Fokus-, Ladezeit-, Speicher- und Persistenztests: `ANDROID_NOT_TESTED`.
- Physischer Speicherpool und tatsächlich schreibbares alternatives Android-Ziel auf Box B: offen. Externe/SMB-End-to-End-Tests ohne gesonderte Freigabe nicht durchgeführt.
- Historische freie Speicherprobleme, Kodi-Library-Views und vollständiger Importcursor unter echtem ENOSPC sind nicht durch einen Hosttest physisch repariert. Keine Datenbank-Recreation.
- Zusätzliches neues Eventbild direkt in der Mini-EPG-Liste (P1): offen; funktionierende Mini-EPG-Details bleiben geschützt.
- .85 bleibt Draft/Testkandidat; .84-Pakete, Indizes und alle drei Veröffentlichungswege bleiben byteidentisch.
