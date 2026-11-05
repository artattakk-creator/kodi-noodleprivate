# Android-Abnahme XCMate 0.1.29.75

Status aller nachfolgenden Geräteprüfungen: **ANDROID_NOT_TESTED**. Host-/Linux-Screenshots sind kein Android-PASS. Zunächst Box B (Kodi 21.3 / ARM32 / RK3528); Box A bleibt unangetastet.

## Installation aus dem vorhandenen Pilot-Kanal

1. Bestehende Kodi-/XCMate-Installation beibehalten. Keinen Installer erneut starten, nichts deinstallieren oder zurücksetzen.
2. Nach dokumentierter Pilot-Veröffentlichung: vorhandenes **GS Media Pilot**-Repository auf Aktualisierungen prüfen.
3. XCMate → Informationen → Versionen: **0.1.29.75 aus GS Media Pilot** auswählen. Bei zuvor regulärer Herkunft kann dieser manuelle Herkunftswechsel erforderlich sein. Kein neues Repository einrichten.
4. Alternativ das unten im Testbericht verlinkte geprüfte .75-ZIP als Update installieren. Das Erfolgsfenster muss Version und Änderungen nennen.
5. Der reguläre GS-Media-Katalog bleibt auf .74. Automatische reguläre Veröffentlichung ist bis zur separaten ausdrücklichen Android-Freigabe gesperrt.
6. Für das neue native Home-Layout den vorhandenen BINGIE-Adapter-Dialog verwenden: Änderungen und SHA-Backup ansehen, dann bewusst zustimmen. Wird ein unbekannter Space-Blue-Skin-Hash gemeldet: **BLOCKED_SKIN_HASH**, nicht mit Dateien aus fremden Installationen übergehen. Vorhandene Einstellungen bleiben erhalten.

## Zuerst Live-TV-Exit (#368)

Startsender starten → einmal Zurück aus reinem Live-Vollbild. Offenes Overlay zunächst nur auf seiner Ebene schließen. PASS ausschließlich bei beendetem eigenen Stream, native ACK-Rückkehr, Kodi `VideoPlayer: finished waiting`, bedienbarer Zielansicht und keinem zweiten Stop. Bei FAIL restliche Dauerschleifen auslassen und Statuscodes/Zeit notieren. Danach 20 Back-Zyklen, schneller Senderwechsel, Back kurz nach Start, nach 60 Minuten sowie EOF/Stall prüfen. Fremde Player und Dialoge dürfen nicht beendet werden. Vorhandenen .42-Kompatibilitätswert vor/nach Update notieren; .75 ändert ihn nicht.

## Hero75-R1 bis R8

| ID | Durchführung | Status |
|---|---|---|
| HERO75-R1 | Kodi kalt starten, keinen Sender abspielen: Startgruppe, Logos, lokales Jetzt/Danach und korrektes Bild oder senderidentischer Fallback; alle Infos rechts | ANDROID_NOT_TESTED |
| HERO75-R2 | Film mit Provider-Fanart: Bild links, Details ausschließlich rechts, eine Filmzeile | ANDROID_NOT_TESTED |
| HERO75-R3 | Film nur mit Hochkantposter: unverzerrt, kein generisches Bildsymbol | ANDROID_NOT_TESTED |
| HERO75-R4 | Live → Film → Serie mehrfach; Fokus, Bild, Metadaten und Quelle identisch, eine Rail | ANDROID_NOT_TESTED |
| HERO75-R5 | Positiver TMDB-/TVmaze-Fall und reines Providerbild: richtige Rolle unten rechts, kein altes/falsches Logo | ANDROID_NOT_TESTED |
| HERO75-R6 | Mindestens 20 echte horizontale/vertikale Fernbedienungsschritte; Menü auf/zu; keine Überlagerung oder Hero-Verkleinerung | ANDROID_NOT_TESTED |
| HERO75-R7 | 1920×1080 und 1280×720: Tabelle/Quelle innerhalb rechter Box, Rahmen am aktiven Item | ANDROID_NOT_TESTED |
| HERO75-R8 | Offline/EPG-Lesetimeout/fehlendes Bild: gültigen Text behalten, keine fremde Identität, keine GUI-Sperre | ANDROID_NOT_TESTED |

## H75-01 bis H75-10

| ID | Durchführung | Status |
|---|---|---|
| H75-01 | EPG-gedeckter Startsender ohne Tune, Kaltstart und Neustart | ANDROID_NOT_TESTED |
| H75-02 | Mindestens zehn Live-Sender, darunter ohne Eventbild | ANDROID_NOT_TESTED |
| H75-03 | Alle drei Hauptbereiche, genau eine aktive Zeile | ANDROID_NOT_TESTED |
| H75-04 | Mindestens 20 Cover horizontal; Providerbilder und korrekter Hero | ANDROID_NOT_TESTED |
| H75-05 | Mindestens 20 vertikale Bereichs-/Unterkategorieschritte; feste Geometrie | ANDROID_NOT_TESTED |
| H75-06 | Exakt ein itemlokaler Fokusrahmen, kein unterer Geisterrahmen | ANDROID_NOT_TESTED |
| H75-07 | Verschiedene Menüicons und korrektes Schließen/Öffnen | ANDROID_NOT_TESTED |
| H75-08 | Reale Film-, Serien- und EPG-Bildquelle; gleiches Event in Details und Home | ANDROID_NOT_TESTED |
| H75-09 | Offline/Online und Sendungswechsel; Snapshot und Fortschritt korrekt | ANDROID_NOT_TESTED |
| H75-10 | 60 Minuten aktives Home, Scrollen, Neustart und Datenvergleich auf Kodi 21.3 | ANDROID_NOT_TESTED |

## PREFETCH75-1 bis PREFETCH75-8

| ID | Durchführung | Status |
|---|---|---|
| PREFETCH75-1 | Fünf EPG-gedeckte Sender kalt ohne Tune; Text vor externer Bildsuche | ANDROID_NOT_TESTED |
| PREFETCH75-2 | TMDB bewusst AN; Fokus und sichtbare fünf vor rotierendem Rest | ANDROID_NOT_TESTED |
| PREFETCH75-3 | Beide TMDB-Freigaben/TVmaze AUS: null neue Drittanbieter-Lookups; XMLTV/Provider weiter nutzbar | ANDROID_NOT_TESTED |
| PREFETCH75-4 | Bei voller 24er Eventqueue scrollen: Fokus priorisiert, keine Doppelstarts/Profilvermischung | ANDROID_NOT_TESTED |
| PREFETCH75-5 | Zwischen gleichen Events wechseln: keine neue identische Bildsuche | ANDROID_NOT_TESTED |
| PREFETCH75-6 | Echte Sendegrenze, neue Guide-Revision und manuelle Zuordnung; keine alte Fanart/Quelle | ANDROID_NOT_TESTED |
| PREFETCH75-7 | Offline, DNS, HTTP 429, Speicherschutz und SQLITE_BUSY sauber unterscheiden | ANDROID_NOT_TESTED |
| PREFETCH75-8 | Beide Auflösungen und 60 Minuten: positiver echter Film-Event in Details und Home sichtbar | ANDROID_NOT_TESTED |

## LOAD75-A bis LOAD75-F

| ID | Durchführung | Status |
|---|---|---|
| LOAD75-A | Kaltstart mit vorhandenen VOD-/Serienjobs: keine neuen automatischen Coverjobs vor Live-Ready | ANDROID_NOT_TESTED |
| LOAD75-B | Kein sicherer externer Live-Match: Text + senderbezogener Fallback geben Live frei | ANDROID_NOT_TESTED |
| LOAD75-C | Einzelne Filmcover defekt: übrige Zeile/Fallback nutzbar, danach Serienphase | ANDROID_NOT_TESTED |
| LOAD75-D | Gedrosselte Last: tatsächliche Phasen, Queue-Tiefe und Laufzeiten erfassen | ANDROID_NOT_TESTED |
| LOAD75-E | Während Live-Warmup direkt Serien wählen: Fokus reagiert, kein blockierendes Gate | ANDROID_NOT_TESTED |
| LOAD75-F | Neustart, Profil-/Startgruppenwechsel, 20 Fokuswechsel; Daten/Token unverändert | ANDROID_NOT_TESTED |

Je Test PASS/FAIL/BLOCKED/NOT_TESTED, Uhrzeit und ausschließlich bereinigte Statuscodes festhalten. Private Bilder/Logs/URLs/Tokens nicht öffentlich hochladen. Zusätzlich Portale, Passwörter, Favoriten, EPG-Mappings, Resume/Autoplay, Startgruppe, bestehende Widgetpfade und Space Blue vergleichen. Ein unbekannter Skin oder fehlender echter Bildnachweis ist kein PASS.
