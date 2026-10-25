# XCMate .36 – Zwischenabnahme zweite Kodi-21.3-Androidbox, Stand 25.10.2026 18:52 Uhr (Europe/Berlin)

**Quelle: unmittelbare Nutzerbeobachtung, keine neue Logdatei:** reguläres OTA-Update XCMate **0.1.29.36** auf **Box B** (zuvor ermittelte Kodi21.3 ARM32, Rockchip RK3528). Frühere Kodi-Logs stammen von .35 und beweisen keine neue .36-Crashursache. Keine neue Main-Codeänderung, kein Fix für diese Beobachtungen bereits eingebaut, weder Main-Merge noch Geräte-Reset.

## Reale Befunde nach .36-Installation

| Testbereich | Nutzerbeobachtung | Gate |
|---|---|---|
| Globale Suche und Genre | Query **„Horror“** liefert **Sender (Live), Serien und Filme**. Subjektiv „super“, also positive Suchprobe. **Horror** in Film/Serie belegt aber nicht die vollständige GENRE-01..07-Matrix; Live-Treffer können Sendernamen-/EPG-Textmatch sein, **nicht** Live-Genreklassifikation. | Teil-PASS bei Suchprobe; restliche GENRE-/S36-Gates NOT_TESTED |
| Live-TV | Sender aus Suche erfolgreich gestartet. **IR-Zurück** danach → **Kodi oder gesamte Box hängt** / keine Rückkehr möglich. Kein neues Log für Rootcause. | **S36-07 FAIL** (ein schwerer Fall), [P0 #169](https://github.com/artattakk-creator/kodi-noodleprivate/issues/169), andere UI-/Player-Gates NOT_TESTED |
| XCMate-App-Start | Start von XCMate auf Box B **27 Sekunden**. App-Start, nicht sicher Stream-First-Frame; Kalt-/Warm-Qualifikation offen. | Performance **FAIL/zu langsam**, [P1 #170](https://github.com/artattakk-creator/kodi-noodleprivate/issues/170) |
| Artwork-Statusmenü | Zunächst Nutzer dachte Menü nicht vorhanden, später **selbst gefunden**, Statusfenster verfügbar. Nicht als fehlendes Feature führen. | ART36-01 **teilweise geprüft** |
| Physischer Daten-Freiraum | Vom XCMate-Artworkstatus abgelesen: **531 MB frei von 3.847 MB gesamt**, bereits ca. **3.316 MB belegt**. Beschreibt vom Programm gemeldetes **Art-/Kodi-Ziel-Dateisystem**, nicht physische RAM-Kapazität, nicht zwingend gesamte vermarktete Flashgröße. ~13,8% frei. | ART36-01 Messwerte vorhanden |
| Artwork-Reserve | **1.024 MB** Minimum konfiguriert. **Fehlbetrag zur Reserve = 1.024−531 = 493 MB** (plus Download-/Write-Headroom). Nutzer sieht immer wieder **„Freiraumreserve voll“**. | ART36-04 **RESERVE_BLOCKED (technisch begründet), echter ENOSPC NICHT nachgewiesen**, [#168](https://github.com/artattakk-creator/kodi-noodleprivate/issues/168) / [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90) |
| Artwork-Jobzustände | **DISK_FULL 97 / PENDING 21 / RUNNING 1**, DB-Prüfstand OK, Bilddownloads aktiviert. `DISK_FULL` ist im .36-Code eine Oberklasse für den **RESERVE_BLOCKED**-Fall, nicht Beweis physisch 0 Bytes. PENDING/RUNNING sind keine READY. Der Worker ist zumindest im Status als RUNNING zu sehen; „läuft erfolgreich“ nicht bestätigt. | ART36-01 Teilbefund, ART36-02/03 **BLOCKED**, keine bestätigten echten Bilddateien |
| Aufgezeichnete Bildbytes | **0 MB** im Status: Rundung/Nullwert, aber kein positiver READY-Nachweis. Keine Behauptung, jeder mögliche Bildspeicher auf Kodi-Gerät sei leer. | Cover-Android-PASS **nicht erreicht** |

## Codeprüfung gegen echtes main .36

In `src/plugin.video.xtreammate/resources/lib/art_storage.py`:
```python
def reserve():
    return max(32*MIB,setting_int('media_art_reserve_mb',1024)*MIB)
# check(): when free < reserve + upcoming + WRITE_HEADROOM,
# returns ArtworkFailure('DISK_FULL', 'RESERVE_BLOCKED', data) unless even
# bytes for upcoming write are missing.
```
Bei `free≈531MB`, `reserve=1024MB` ist `RESERVE_BLOCKED` unabhängig vom konkreten Cover plausibel/begründet. Es fehlen mindestens rund 493MB für die Reserve, plus notwendige Bild- und SQLite-Headroom; dies ist **keine reine Netzwerkstörung oder nachgewiesene physische Vollbelegung**. Die 1024MB-Vorgabe ist auf einer 3.847MB-Nutzpartition rund 26,6% des Gesamtvolumens – sehr konservativ.

In `artwork_health_ui.py` wird Freiraum/Total gerundet in **MiB** dargestellt, `art_diagnostics` stellt den differenzierten `RESERVE_BLOCKED`-Code bereit. Hauptfensterwortlaut sollte den Zustand als „Sicherheitsreserve unterschritten: 531 MiB frei, 1.024 MiB erforderlich“ zeigen, **nicht** „physisch voller Speicher“. Die Artwork-Jobanzahl kann einen älteren blockierten Retry-Bestand enthalten; selbst wenn Platz frei wird, braucht es eine datensichere gezielte, begrenzte Recovery. **Nicht** 97 Jobs global resetten oder Vorsichtsreserve ungefragt auf 0 setzen.

## Nächste kumulative Korrektur .37

- **#169 P0** Live-/Player-Back-Hänger beheben, Zeitpfad und Android-Logs, Kodi21.3/Kodi21.2 Regression.
- **#170 P1** 27s XCMate-App-Start mit `BOOT/MAIN_IMPORT/HOME_MENU/DIRECTORY_DONE` und unabhängigen kalt/warm Stopuhrwerten profilieren. Nicht mit Startsenderzeit verwechseln.
- **#168/#90** kleinen Android-Gerätespeicher + 1024MB-Reserve benutzerverständlich diagnostizieren, adaptive/respektierte sichere Reservestrategie erwägen und **nur nach expliziter Nutzerwahl** anpassen. Lokale DB/EPG/Artwork-Kopien nicht löschen; Recovery der bereits `DISK_FULL`-blockierten Jobs prüfen.
- **#106** reguläre **USB- UND SMB-Auslagerung/Migration .37** besonders relevant, weil internes /data nur rund 3,8GB groß ist; Queue/SQLite bleibt intern, Bilder außerhalb, Offline-/Reserve-/Integrity-Checks und explizite Originalbereinigung.
- **#167** Geräteübersicht unter Wartung & Diagnose zeigt echte RAM/Flash/Kapazitäten pro Mount ohne System-Root.
- Weitere bestehende .37-Wizard-Bugs #165/#166/#164 und alte .36-Restbefunde bleiben.
- **Bis zur nächsten Phase:** Benutzer wollte zunächst **nur analysieren**. Keine weiteren risikoreichen Back-20x-Zyklen provozieren, keine Caches/DB/Portale löschen, keine Hintergrunddownloads erzwingen; neuen privaten `kodi.log/kodi.old.log` vom Hänger ablegen und später über sicheren Weg untersuchen.

**Original XCMate .36 PR #163 wurde zuvor vollständig gemergt/publiziert**, Hosttests 1250 PASS; dieser reale Android-Test zeigt dennoch **einen P0-Hänger** und **technisch erwartbar durch Reserve blockierte Cover**, kein Android-Gesamt-PASS. GUI/Hosterfolg darf nicht als Android-PASS geführt werden.
