# .31-B – gezielte Redirect-Freigabe und tatsächlicher Ziel-Kurztransfer

Basis main 6d3555a / .30. Historische .30-Werte 12 PASS / 15 FAIL / 1 BLOCKED /
1 NOT_TESTED unverändert. USB/SMB-Enddatei und Film/Folge bleiben bis Android offen.

## Sichere Freigabe und bewusster Retry (#135/#63)

Untrusted-Downloads zeigen eine verständliche Freigabe-Anweisung; im Job steht
„Ziel prüfen/freigeben“ vor einem blinden Retry. Erstes Standardangebot:
**gesperrt lassen / nicht bestätigt**. Nur nach unabhängiger Prüfung anhand
eigener Anbieterinformationen bewusst „Vom Anbieter bestätigtes Ziel“ wählen.
Danach explizite Bestätigung der privaten Source-/Target-Origins (keine Pfade,
Queries oder Zugangsdaten). Nicht aus dem Fehlercode auf legitimes CDN schließen.

DNS-/LAN-Prüfung wie bisher im Worker. localhost/Metadaten/link-local bleiben auch
mit LAN-Bestätigung gesperrt. Exakt die angezeigte, nicht abgelaufene Pending-
Anfrage wird unter BEGIN IMMEDIATE atomar freigegeben; neue Hop-/Zieländerung
während der Bestätigung → nichts freigegeben, neu prüfen. Keine neue DB-Struktur.
Bisherige Portal+Source-Origin+Target-Origin-Bindung bleibt unverändert.

Ein zweiter bewusster Dialog darf ausschließlich diesen weiterhin fehlgeschlagenen
Redirect-Job erneut einreihen. Kein Start durch Navigation oder Grant allein,
keine Wiederbelebung abgebrochener/anderer Aufträge, Cooldown/Lease bleiben.
Status und Fehlercode werden im selben Job-Commit erneut verglichen; ein
gleichzeitig eintreffendes Cancel gewinnt gegen den bestätigten Retry.
Freigaben weiter einzeln widerrufbar. HTTPS-Downgrade, Hop-/Loop-/SSRF-/DNS-Pinning,
Header-/Cookie-Schutz, Content-/Range-/Hash-/NoReplace-Regeln unverändert.

## Source gegen Ziel unterscheiden (#136)

Neue anonyme DOWNLOAD_PHASE-Marker unterscheiden SOURCE_REDIRECT_DENIED,
SOURCE_FAILED, TARGET_PROBE_FAILED, STAGE_FAILED, TARGET_COPY_FAILED und COMPLETE.
Nur feste Klassen, bestehender gereinigter Code und Bytezahl; keine Hosts/Pfade/
Medien-/Portalnamen. Ein Source-Deny vor Payload wird nicht als SMB-Schreibfehler
verkauft. Unterbrechung/Resume behalten die bestehenden Job-/Hash-Verträge.

Einstellungen → Speicher → **Gewähltes Downloadziel testen**: nach ausdrücklicher
Bestätigung kleine neue Nonce-Datei direkt am gespeicherten Downloadziel schreiben,
Datei-fsync bzw. SMB2 Write-Through, Größe/SHA256/Readback prüfen und eigene
bestätigte Datei entfernen. Kein Provider-/CDN-Aufruf, kein Medienjob und kein
interner Ersatz. Interne/USB-/SMB-Capability und bestehende Freigaben erforderlich.
NoFollow/Exclusive und Volume-Prüfung bleiben. Lokale Cleanup-Inodeänderung →
keine Löschung. Bei unklarer/abgebrochener/ersetzter Testdatei wird sie ggf. zur
Diagnose belassen; niemals auf Verdacht einen fremden Namen löschen. Nur lokale
private SMB-Test-Zwischenkopie wird nach eigener Inodeprüfung entfernt.
Der kleine Test beweist keine vollständige Filmdatei und keine native Aufnahme.

## Host- und Android-Abnahme

58 gezielte Hosttests PASS (12 neue), einschließlich Default-Deny, enger Grant+
gezielter Retry, geänderter Pending-Anfrage, weiter gesperrtem Loopback, Widerruf,
UI-Aktionsreihenfolge, Source-/Ziel-Diagnose, echten lokalen und signierten SMB2-
Kurztransfers, Cancel ohne Write und ersetztem Inode ohne fremde Löschung.
Bestehende Redirect-/SMB-/Resume-/Hash-/NoReplace-/Player-Detailtests bestehen.

Android-Delta: ST1 einmal visuell bestätigen; kleinen Zieltest auf tatsächlichem
USB und bestehender Kodi-SMB-Quelle durchführen; dann nur belegtes CDN freigeben,
Film + Folge vollständig speichern/abspielen, Pause/Fortsetzen/Abbrechen, Retry,
Widerruf/Denied prüfen. USB lokal nach Neustart offline; SMB braucht Server.
ST2/ST5 sowie S1–S5 und vier Stunden bleiben bestätigte Baseline.

Unverändert offen: native Direct-TS-Aufnahme #126 und Poster #111; kein neuer
PASS dafür. #151/manuelle Bildsuche, Icon-Rail/Catch-up/EPG-Magazin bleiben eigene
Entwicklungen. Keine Benutzerdaten-/Bildlöschung, Keymap- oder Playeränderung.
Kein main-Merge/Release/Issue-Abschluss. Installierbare .31 im kumulativen Branch.
