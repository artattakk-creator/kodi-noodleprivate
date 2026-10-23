# XCMate 0.1.29.29 – kumulativer Android-Testkandidat

Stand: 24.10.2026. Basis main c17cb4f (.28). Enthält die getrennten Drafts
#137 (Redirects #135) und #138 (Downloadziele #136). Kein vollständiger RC,
kein main-Merge/Release/OTA. .28-ZIP und Produktionsindex bleiben erhalten.

## Gesicherter Ausgangsstand

.27: **13 PASS / 15 FAIL / 0 NOT_TESTED** unverändert. A01–A08 Suche/Live PASS,
#125 geschlossen. .28: Menü-/Downloadmanager-Erreichbarkeit laut Nutzer **Teil-PASS**;
mindestens ein REDIRECT_UNSUPPORTED-Download nachgewiesen; USB/SMB als erfolgreiches
persistentes Ziel nicht bestätigt. Keine vollständige .28-Auswertung erfinden.
Weitere abgeschnittene Fehlercodes im privaten PDF nicht gleichsetzen. PDF/Rohlogs
bleiben privat. Alle neuen .29-Gerätefelder zunächst **NOT_TESTED**.

## Installation

Nur das **kumulative C-ZIP** mit beigefügter SHA256 verwenden. Isolierte A/B-
CI-Pakete sind Review-/Diagnosestände mit gleicher Versionsnummer und enthalten
jeweils nur einen Teil der Reparaturen. Kodi → Addons → Aus ZIP-Datei installieren,
bestehendes XCMate aktualisieren. Keine Deinstallation, Datenrücksetzung oder
Portal-/EPG-Neuimporte. Quelle und Herkunft der Testdatei berechtigt wählen.

## 1. Menü und Zielwahl

Film-/Seriendetails: Links bzw. sichtbarer **Aktionen**-Button → Downloads verwalten.
Rechts/Zurück muss nur das Menü schließen und die Detailposition bewahren.

XCMate → Einstellungen → Speicher → **Downloadziel wählen: intern / USB / SMB**.
Kodi-Dateiquellen/USB-Mount vorher in Android/Kodi freigeben. Ziel wählen, tatsächliche
Prüfung abwarten, Fähigkeiten ansehen, gegebenenfalls Staging erlauben und Übernahme
bestätigen. Danach Kodi neu starten und „Downloadziel und Fähigkeiten prüfen“ aufrufen.
Aufnahmeziel separat prüfen. Ohne bestätigte Auswahl bleibt der alte gemeinsame
Ordner Standard; Fehler/Cancel bewirken keinen internen Rückfall. Bestehende
Aufträge behalten ihren alten Zielordner – für einen neuen Zieltest einen neuen,
noch nicht heruntergeladenen Film bzw. eine andere einzelne Folge verwenden.

Native lokale Ziele benötigen unverändert sichere No-Replace-/fsync-Fähigkeit.
Geeignete andere lokale USB-Ziele verwenden nach Zustimmung eine vollständige
lokale Zwischenkopie, exklusiven neuen Zielnamen, Datei-fsync und Rücklese-Hash.
Dabei wird keine atomare Sichtbarkeit zugesichert: eine unterbrochene Datei kann
im Dateimanager sichtbar bleiben; XCMate gibt sie nicht als COMPLETE frei.
SAF-`content://` ohne passenden zugreifbaren Mount bleibt mit konkreter Diagnose
gesperrt; das Addon umgeht keine Android-Berechtigungen.

SMB: **authentifiziertes signiertes SMB2.002/2.1**. Gegebenenfalls im Picker eigenen
SMB-Account ausdrücklich nur auf diesem Gerät speichern. Kodi braucht für die
Wiedergabe zusätzlich seine eingerichtete Freigabe-Anmeldung. Keine Gast-/SMB1- oder
unsignierte Rückstufung, keine SMB3-encryption-required/Kerberos-only-Unterstützung.
Server-Sicherheit nicht herabsetzen; ein geeignetes anderes Ziel verwenden.
SMB-Freiraum unbekannt, lokale Staging-Kapazität geprüft. **SMB braucht Netzwerk**.

Vollständige lokale Zwischenkopien bleiben für Wiederherstellung erhalten und
benötigen zusätzlichen internen Platz. Unterbrechung/Retry kopiert den geprüften
Stage neu zum Ziel; kein blindes Anhängen an SMB-Teildateien und kein erneuter
HTTP-Download einer bereits vollständigen unveränderten Zwischenkopie. Pause/
Abbruch während TRANSFERRING möglich; der abschließende Publish-Schritt ist geschützt.

## 2. Redirects zuerst auf geeignetem internem Ziel prüfen

Einen rechtmäßig herunterladbaren direkten Film starten. Unbekannter anderer
Origin bleibt mit **REDIRECT_UNTRUSTED_TARGET** gesperrt; das ist eine ausstehende
Vertrauensentscheidung. Im Manager fehlgeschlagenen Auftrag auswählen, Diagnose
lesen, **Redirect-Ziel für dieses Portal prüfen/freigeben** wählen. Die private
Anzeige nennt Quelle/Ziel (Schema, Host, Port), ohne Medienpfad/Query. **Nur nach
unabhängiger Bestätigung**, dass das ein vertrauenswürdiger Provider/CDN ist,
freigeben. Freigabe ist portal- und quellgebunden, widerrufbar und startet noch
keinen Download. Anschließend im Manager ausdrücklich **Erneut versuchen** wählen.

Private RFC1918-/ULA-Server benötigen eine weitere ausdrückliche LAN-Zustimmung.
Loopback/Metadaten/Link-Local, ungültige Protokolle, HTTPS→HTTP, Schleifen und
überlange Ketten bleiben gesperrt. Nicht ungeprüft alle nachgefragten Hosts freigeben.
Authorization/Cookies/private Providerheader wechseln nie automatisch den Origin.

Erwartet: Bytes >0 → COMPLETE → Wiedergabe. Anschließend Kodi neu starten und
auf lokalem Speicher ohne Netzwerk abspielen. Denselben Ablauf für eine gezielt
ausgewählte Serienepisode prüfen. Pause/Resume/Retry testen; bei SOURCE_CHANGED
keinen alten Dateianteil ungeprüft anhängen. Freigabe im Manager je Portal wieder
widerrufen und nicht freigegebene Weiterleitung auf Blockade prüfen.

## Ergebnisvorlage

PASS / FAIL / NOT_TESTED je Zeile, bei Blockade den konkreten Blockierungsgrund
ergänzen. Historische .27-FAIL-Werte dadurch nicht umklassifizieren.

| ID | Prüfung | Ergebnis |
| --- | --- | --- |
| M01 | Film und Serie: Links/Aktionen öffnet sichtbares, fokussierbares Menü | NOT_TESTED |
| M02 | Rechts/Zurück/Refresh bewahrt Detailposition und Fokus | NOT_TESTED |
| M03 | Alle Menüaktionen per IR, keine unbeabsichtigte Wiedergabe | NOT_TESTED |
| ST01 | Standardziel/Einstellungen und vorhandene Daten unverändert | NOT_TESTED |
| ST02 | USB wählen, speichern, Neustart; Download COMPLETE und lokal offline abspielen | NOT_TESTED |
| ST03 | SMB wählen, speichern, Neustart; COMPLETE und Kodi-VFS-Wiedergabe bei erreichbarem Server | NOT_TESTED |
| ST04 | Downloadziel unabhängig vom Aufnahmeziel, beide behalten ihre Auswahl | NOT_TESTED |
| ST05 | Voll/read-only/entfernter USB/SMB-offline/FAT32-Grenze/SAF/Kollision: sicherer verständlicher Fehler | NOT_TESTED |
| ST06 | Zielkopie pausieren/abbrechen/erneut versuchen; Stage erhalten, kein falsches COMPLETE | NOT_TESTED |
| ST07 | SMB-Netzunterbrechung und Wiederverbindung; Wiederholung aus Stage | NOT_TESTED |
| RDX01 | Tatsächlicher Provider/CDN-Film nach überprüfter Freigabe: Bytes >0, COMPLETE, Wiedergabe | NOT_TESTED |
| RDX02 | Eine einzelne echte Episode über autorisierte Weiterleitung vollständig speichern/abspielen | NOT_TESTED |
| RDX03 | Fehlende/widerrufene Freigabe bleibt gesperrt, keine privaten Daten in öffentlichen Logs | NOT_TESTED |
| RDX04 | Pause/Resume/Retry und korrektes Verhalten bei Quell-/Validatorwechsel | NOT_TESTED |
| DL01 | Fertigen Film und Folge nach Kodi-Neustart aus interner/angeschlossener USB-Ablage offline abspielen | NOT_TESTED |
| CAP01 | Direct-TS mindestens zwei Minuten, aktiv erst nach Bytes, manuelles Finish | NOT_TESTED |
| CAP02 | Fertige Aufnahme lokal/offline; HLS/DASH-Formatfehler getrennt von Speicherfehlern | NOT_TESTED |
| ART01 | Einzelposter-Retry/Alternative, gültige Cachebilder erhalten, Persistenz nach Neustart | NOT_TESTED |
| A01–A08 | Abgenommene globale Suche/Such-Live unverändert PASS halten | NOT_TESTED |
| REG01 | Großes EPG, Sendestart, Live-IR/Overlay, Staffelautoplay/Stop/Resume | NOT_TESTED |
| REG02 | Originalicon, Portale, Gruppen, Favoriten, EPG-Zuordnungen und Gesehen-Status | NOT_TESTED |

Bei FAIL: ID, Aktion, Status und festen Reason-/CODE@STAGE:ERRNO-Wert notieren.
Nur anonymisierte DOWNLOAD_REDIRECT/DOWNLOAD/CAPTURE/DETAIL_MENU-Stufen öffentlich
teilen. Hostnamen, komplette URLs, Query/Token, SMB-Passwörter, private Pfade,
Titel und IDs aus Rohlogs entfernen. Kein privates PDF ins Repository.

## Technische Nachweise und offene Arbeit

`DOWNLOAD_REDIRECT_02929_DE.md` beschreibt Trust-/Header-/DNS-/Resume-Vertrag.
`DOWNLOAD_TARGETS_02929_DE.md` beschreibt Backends, Fähigkeiten und Abhängigkeiten.
`HOST_E2E_02929.json`: acht echte kombinierte HTTP-Redirect-Transfers (Film/Folge
je intern, simuliertes natives/gestagtes USB und echter signierter SMB2-Testserver),
je 404.305 Bytes MP4, SHA256-Abgleich und vollständiger strikter FFmpeg-Decode.
Das ist **kein Android-/physischer USB-/Kodi-VFS-PASS**.

Host-Reproduktion: `python tools/smoke_downloads_02929.py fixture.mp4 report.json`
mit selbst erzeugter MP4-Datei, FFmpeg und installierter Host-Testabhängigkeit
Impacket 0.13.0. Der bewusst gepatchte Loopback-Adressprüfer gilt nur im Fixture;
Produktions-SSRF-/IP-Pin-/TLS-Entscheidungen sind separat negativ/positiv getestet.
Impacket und Fixtures werden nicht ins Kodi-Installations-ZIP gepackt.

Weitere unabhängige Draft-Entwicklungen bleiben offen: #127 Suchdarstellung mit
belegten Bildern/EPG/Metadaten; #43 kompletter automatischer Xtream/M3U/Stalker-
Wizard mit Gruppencheckboxen, EPG/Matching, progressivem Cover-/Metadatenimport,
Fortschritt, Startgruppe/-sender und Neuinstallationsabnahme. **Beide sind Pflicht
vor einem vollständigen RC.** Außerdem #120 Live-Shortcut, #122 Original-Splash,
#123 Sendungsdetails, #98 Quellenwahl im EPG und #115 Premium-Fokus/Navigation.
#131/#126/#111/#63 bleiben bis zur jeweiligen echten Geräteabnahme offen.

## Paket und Testergebnis

`plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.29.zip`
(2.003.455 Bytes, 244 Quelldateien; enthält private reine Python-SMB-Abhängigkeiten
und deren Lizenzhinweise).

SHA256: `805e29885bf39e3e2c60e3af82ebcd9f3ccf82b6cebd24ebd3d7e47e4eb58ab5`

997 lokale Tests PASS in 113.580 s, 0 Fehler, 0 übersprungene Tests, keine
Thread-Exceptions. Syntax, ZIP-CRC/Pfade, vollständiger Quelldateiabgleich und
bytegenau reproduzierbarer Build PASS. Vollständiger Testlog und maschinenlesbarer
Bericht neben dieser Anleitung; CI-Nachweis zum endgültigen Liefercommit im
kumulativen Draft-PR. Die Schutzprüfung wurde nicht abgeschwächt: die zunächst
beanstandete Ergänzung an window_navigation.py wurde zurückgenommen; die neuen
Picker werden lokal als nicht abspielbare Dialogaktionen eingebunden.
