# Android-Abnahme XCMate 0.1.29.19 – NOT_TESTED

Basis .18, Android 13 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD / IR. Jede Checkbox erst nach echter Prüfung abhaken und separat PASS/FAIL/NOT_TESTED melden. Bei Kodi-Absturz, Hintergrundton oder Hänger abbrechen und Version/Zeitpunkt/Schritt plus bereinigten privaten Log sichern.

## Installation

- [ ] Kodi beenden, Profil privat sichern; ZIP-SHA256 prüfen. Test-ZIP manuell per „Aus ZIP-Datei installieren“, danach Neustart; Versionsanzeige **0.1.29.19**.
- [ ] Portale, Einstellungen, Sendergruppen, EPG-Zuordnungen, Favoriten, Resume, Seen und verborgene Continue-Filme vorhanden. Kein Reset/Reimport/Cachelöschen. Rückfall bleibt das unveränderte .18-Paket samt vorhandenem Profil.

## #74 Poster und Rahmen (je Filme UND Serien)

- [ ] Rails und Kategorien zeigen merklich kleinere 2:3-Poster; Schrift aus TV-Sitzentfernung mindestens so lesbar wie .18, zweizeilige Titel, keine störenden Überlappungen.
- [ ] Helles und dunkles vorhandenes Poster: aktuelles Cover direkt klar umrahmt. Left/Right in allen drei Rails und Up/Down im Kategoriepanel bewegen genau die aktive Markierung. Bei Header-/Railwechsel keine irreführend doppelte aktive Markierung.
- [ ] Reihenfolge Weiter ansehen → Meine Favoriten → Neuheiten; vertikales Scrollen und obere Kategorien/Suche per IR erreichbar. Leere Rails bleiben sicher.
- [ ] Kategorie Adult: tatsächliche lokale Gesamtzahl ablesen (keine fiktive 1.500-Sollzahl). Down über 24→25, 48→49 und >240; dann zurück hoch. Kein Right-Workaround, keine Lücken/Dubletten, Rahmen bleibt am ausgewählten Titel.
- [ ] Nach mehreren Portionen Titel öffnen → Detail → Back: gleiche Kategorie, gleicher Titel und sichtbarer Fokus. Während Nachladen Kategorie wechseln; keine fremden/stalen Inhalte.
- [ ] Möglichst 720p/1080p und Estuary zusätzlich prüfen. Optionales Theme nur falls bereits vorhanden; dafür nichts produktiv installieren/umstellen müssen.

## #44 Manuelle nächste Folge

- [ ] Serie mit bestätigtem Nachfolger öffnen: im Detail „Nächste Folge · Staffel X Folge Y“ sichtbar. Ziel muss der aktuellen lokalen Auswahl/letzten echten Wiedergabe folgen; ohne Historie ist die erste gültige Folge der anfängliche Bezug.
- [ ] Episodenliste: beliebige Folge markieren, Rechts → sichtbarer Next-Button ohne Wechsel der Bezugsfolge; Down zurück zur Liste. Alternativ ab erster Zeile Hoch → Next. Von Suche Down erreichbar. Button benennt den Nachfolger der markierten Folge, auch bei Markierung mitten in einer Staffel.
- [ ] Explizites OK auf Next startet genau diese Folge, Bild/Ton/Resume korrekt. Kein Doppelstart bei zweitem OK während Startübergang.
- [ ] Gleichen Nachfolger trotz ungesehenem/gesehenem Ausgangsstatus anbieten. Status nur an bewusst gewählten Testfolgen ändern; vorhandenes Resume anderer Folgen bleibt erhalten.
- [ ] Letzte Folge einer Staffel mit bestätigtem Nachfolger → erste vorhandene gültige Folge der nächsten Staffel. Bei Nummernlücken die nächste tatsächlich vorhandene Folge. Keine fremde Serie/Portal-ID.
- [ ] Natürliches Ende: **keine automatische weitere Wiedergabe**; richtige Staffel/Folge, bedienbarer Fokus und korrekter manueller Next-Eintrag. Detail- und Episodenansicht getrennt prüfen.
- [ ] Echtes Serienende ohne Nachfolger: kein falscher Next-Button/Detaileintrag, kein Rücksprung auf Folge 1.
- [ ] Bewusster Stop: Bild UND Ton aus; kein Folgestart auch nach 10 Sekunden. Back bleibt gestuft bedienbar, Resume nach Kodi-Neustart erhalten.
- [ ] Falls mehrere Portale vorhanden: gleiche IDs bleiben getrennt, kein fremder Episodenstart. Sonst **NOT_TESTED**, nicht PASS.

## .18-Regression

- [ ] Film-/Serienfavorit hinzufügen/entfernen und vollständigen Kodi-Neustart prüfen.
- [ ] Augen grün=ungesehen/rot=gesehen, Legende, Staffelzähler, manuelles Markieren und Persistenz; Fortschritt einer anderen Folge unverändert.
- [ ] Film aus Weiter ansehen ausblenden: Resume/Favoriten/Seen bleiben, nach Neustart verborgen, erst nach bewusster Wiedergabe wieder sichtbar.
- [ ] Bekannter guter Live-Sender → Stop → Home, kein Neustart/Hintergrundton. Bekannter EPG-Sender → Ansehen → Stop; EPG-Zeitnavigation über 14 Uhr.

Autoplay #85 ist **NOT_IMPLEMENTED** und wird separat entwickelt; die ausbleibende automatische Fortsetzung ist hier kein neuer Fehler. Ungeprüfte Schritte bleiben NOT_TESTED. Kein Merge/Release/produktives Update ohne ausdrückliche Freigabe.

## Download und SHA256

[Android-Test-ZIP 0.1.29.19](https://github.com/artattakk-creator/kodi-noodleprivate/raw/refs/heads/feat/xcmate-02919-manual-next/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.19.zip) · [SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.19.zip.sha256)

```text
9a7301943ba2f2013a5c3c86084cc55ce2d3dbe551edf6063bd76062be17dbcf  plugin.video.xtreammate-0.1.29.19.zip
```

Host: 682 Tests PASS; Android: **NOT_TESTED**. ZIP ausschließlich zur manuellen Testinstallation.
