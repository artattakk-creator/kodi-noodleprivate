# XCMate 0.1.29.38 – Android-Abnahme

Stand: 26.10.2026. Testkandidat, kein Release. Alle neuen Gerätetests sind **NOT_TESTED**. Hosttests ersetzen weder Kodi-Rendering noch IR-, Decoder-, ARM32- oder Langzeittests. Ergebnisse je Gerät getrennt eintragen; ein PASS auf B gilt nicht für A.

## Geräte und Schutzgrenzen

| Gerät | Bekannter Stand | Zulässiger nächster Schritt |
|---|---|---|
| A | Kodi 21.2, viele interne Cover; tatsächlich installierte XCMate-Version noch UNKNOWN | Zuerst ausschließlich lesende Inventur und geprüfte Sicherung. Kein automatisches Update oder Moduswechsel. |
| B | Kodi 21.3; .37-Wiedergabe/Exit/Resume/Autoplay und dynamische Cover vom Nutzer bestanden | Dynamisch beibehalten. Keine weiteren Speicher-, Kopier-, Migrations- oder Löschtests. .38-Installation nur durch Nutzer. |

Keine Deinstallation, kein Downgrade, kein Profil-/Cache-Reset, keine Kodi-Keymap- oder BINGIE-Änderung. Keine privaten Logs, Provider-URLs, Kennwörter oder SMB-Pfade auf GitHub. Testergebnisse nennen nur Test-ID, Gerät, Version, Ergebnis, Dauer und datensparsame Beobachtung.

## Durchführung und Protokoll

Vor der Installation heruntergeladenes ZIP gegen `plugin.video.xtreammate-0.1.29.38.zip.sha256` prüfen. Als normales ZIP-Update durch den Nutzer installieren, vorhandenes Profil erhalten. Die installierte Version unter Add-on-Informationen kontrollieren. Auf A erst nach SAFE-A-01/02 und gesonderter Freigabe fortfahren. Bei Kodi-Hänger, fremder Wiedergabe, unerwartetem Speicher-/Moduswechsel oder Datenverlust sofort abbrechen und FAIL festhalten.

Pro Zeile A und B unabhängig ausfüllen. NOT_TESTED bleibt bestehen, bis die Handlung auf diesem Gerät wirklich durchgeführt wurde. Ein blockierter Test ist kein PASS. Die maschinenlesbare Ausgangsliste steht in `ANDROID_STATUS_02938.json`.

| ID | Handlung und PASS-Kriterium | A | B |
|---|---|---|---|
| SAFE-A-01 | Installierte XCMate-/Kodi-Version, Modus, internen Bildbestand und freien Speicher ausschließlich lesen; keine Änderung. A-Version dokumentieren. | NOT_TESTED | nicht anwendbar |
| SAFE-A-02 | Bestehendes Profil bei beendetem Kodi sichern lassen; Sicherung mit Inventar/Größen/SHA256 vergleichen. Keine Sicherung als geprüft behaupten, solange Kodi schreibt oder Abweichungen bestehen. | NOT_TESTED | BLOCKED_BY_USER_STOP |
| SAFE-03 | Nach freigegebenem Update Modus, Portale, Favoriten, Gruppen, EPG-Mappings, Resume und Cover mit vorherigem Bestand vergleichen. Kein impliziter Moduswechsel. | NOT_TESTED | NOT_TESTED; Modus bleibt Dynamisch |
| AUTO-01 | Portal-Autostart ausdrücklich aktiv, Startsender gültig: XCMate normal öffnen. Genau ein Start; kein doppelter Resolver/Player-Aufruf. | NOT_TESTED | NOT_TESTED |
| AUTO-02 | 20 Verzeichnis-Refreshs, Einstellungen öffnen/schließen, Back und Rückkehr innerhalb der App: kein weiterer automatischer Start. | NOT_TESTED | NOT_TESTED |
| AUTO-03 | Kompatiblen BINGIE-Einstieg `ActivateWindow(Videos,plugin://plugin.video.xtreammate/?action=app_open,return)` testen. Alternativ vorhandene `RunPlugin(...?action=app_open)`-Verknüpfung. Genau ein Vordergrundstart; keine Skin-Dateien bearbeiten. | NOT_TESTED | NOT_TESTED |
| AUTO-04 | Autostart ausgeschaltet: normal/Shortcut öffnen. Kein Start. Nach Benutzeränderung gespeicherten Zustand erhalten. | NOT_TESTED | NOT_TESTED |
| AUTO-05 | Fremdes Video/Audio läuft: Einstieg/Widget aktualisieren. Fremde Wiedergabe bleibt unangetastet. | NOT_TESTED | NOT_TESTED |
| AUTO-06 | Sichtbare 15-Minuten-Diagnosepause aktivieren/deaktivieren. Meldung sichtbar; gespeicherte Portaloption unverändert; kein `GetDirectory failed`. | NOT_TESTED | NOT_TESTED |
| AUTO-07 | XCMate vollständig zu Kodi-Home verlassen und erneut bewusst öffnen. Genau ein neuer Start; kein Start durch Hintergrunddienst allein. | NOT_TESTED | NOT_TESTED |
| AUTO-08 | Hintergrund-Widgets aktualisieren und danach App bewusst öffnen. Widget startet nichts und verbraucht den bewussten Einstieg nicht. | NOT_TESTED | NOT_TESTED |
| RAIL-01 | Live-Vollbild: fünfmal Links → Mini → Gruppen → kompakt → erweitert → Vollbild. Video läuft ohne Tune/Stop. 20 Zyklen. | NOT_TESTED | NOT_TESTED |
| RAIL-02 | Erweitert → Back/Rechts → kompakt → Gruppen → gleiche Mini-Position → Vollbild. Keine übersprungene Gruppenebene. | NOT_TESTED | NOT_TESTED |
| RAIL-03 | Beide Rails bildschirmhoch im nutzbaren Bereich, Icons lesbar, Fokus klar; Hoch/Runter/OK und native Klicks führen genau eine Aktion aus. | NOT_TESTED | NOT_TESTED |
| RAIL-04 | Suche/Favoriten/Live/Filme/Serien/großer EPG/Einstellungen/Home aus Rail öffnen; kein fremder Modal-Owner geschlossen, kein Busy-Hänger. | NOT_TESTED | NOT_TESTED |
| RAIL-05 | Filme/Serien am linken Kategorienrand: Rail öffnen, Back. Kategorie, Titel und Fokus unverändert. Detail-Linksmenü bleibt verfügbar. 20 Zyklen. | NOT_TESTED | NOT_TESTED |
| RAIL-06 | Großes EPG: Links weiterhin Zeit-/Sender-/Gruppenlogik; vom Gruppenrand Rail öffnen, zurück: Gruppe/Zeit/Sender/Fokus erhalten. 20 Zyklen. | NOT_TESTED | NOT_TESTED |
| RAIL-07 | Home-Kontextaktion „Navigation“ öffnet gemeinsame Rail; Back kehrt ins Home zurück. Dies ist keine dauerhaft eingebaute Rail im Kodi-Verzeichnis. | NOT_TESTED | NOT_TESTED |
| RAIL-08 | „Aktueller Sender als Startsender“: Abbruch ändert nichts; bestätigter eigener Sender ändert nur Sender/Gruppe des aktiven Portals, nicht Autostart. | NOT_TESTED | NOT_TESTED |
| RAIL-09 | Rubrik wechseln und zurück: Scroll-/Fokusposition dokumentieren. Vollständige rubrikübergreifende Wiederherstellung bleibt offen, wenn Kodi Fenster neu erzeugt. | NOT_TESTED | NOT_TESTED |
| MINI-01 | Sender markieren: rechts reale Vorher/Jetzt/Danach-Titel; laufender Sender bleibt unverändert. | NOT_TESTED | NOT_TESTED |
| MINI-02 | Rechts fokussiert rechte Spalte ohne Popup/Tune. Hoch/Runter bewegt reale Programme, OK zeigt vorhandene Details. | NOT_TESTED | NOT_TESTED |
| MINI-03 | Links/Back aus rechter Spalte kehrt zuerst links zurück; nächstes Links öffnet Gruppen. | NOT_TESTED | NOT_TESTED |
| MINI-04 | Sender ohne lokale EPG-Daten: keine erfundenen Programme, keine falsche Jetzt-Markierung. | NOT_TESTED | NOT_TESTED |
| MINI-05 | Mit lokal gespeicherter Historie vergangene Sendung anzeigen; ohne Historie keine künstliche Vorher-Zeile. | NOT_TESTED | NOT_TESTED |
| MINI-06 | Zukunft/Mitternacht: reale Datums-/Zeitfolge, keine Rückwärtssortierung. | NOT_TESTED | NOT_TESTED |
| MINI-07 | Schnell 30 Sender markieren. Begrenzte Worker-Abfragen; UI bleibt bedienbar, kein HTTP/SQL im IR-Callback. | NOT_TESTED | NOT_TESTED |
| MINI-08 | Gruppenwechsel und Rückkehr: richtiger Sender/Programme, keine ungefragte Wiedergabe. | NOT_TESTED | NOT_TESTED |
| MINI-09 | Großen EPG aus OSD öffnen, Senderstart und Rückkehr testen. Genau ein gültiger Start, keine Kodi-Beendigung. | NOT_TESTED | NOT_TESTED |
| MINI-10 | Manuelle vorhandene EPG-Zuordnungen bleiben wirksam; keine Änderung von Quelle oder Priorität durch bloßes Vorschauen. | NOT_TESTED | NOT_TESTED |
| LIVE-01 | Einmal OK zeigt Logo, Jetzt/Danach/Fortschritt; zweimal OK oder Runter zeigt große echte Buttons mit Fokus. | NOT_TESTED | NOT_TESTED |
| LIVE-02 | Back schließt sichtbare Controls/Info/Rail stufenweise, Video läuft. Bestehendes Back aus bereits geschlossenem Live-Vollbild bleibt bewusster App-Exit; diesen separat dokumentieren. | NOT_TESTED | NOT_TESTED |
| LIVE-03 | Play/Pause nur bei echter Fähigkeit; Seek/Timeshift nur wenn Kodi für diesen Stream Seek unterstützt. Keine erfundenen Qualitäts-/Codecwerte. | NOT_TESTED | NOT_TESTED |
| LIVE-04 | Audio, Untertitel, Bild/Ton, Information öffnen native Dialoge. Fremder Dialog bleibt Owner; Back schließt keine fremden Fenster durch XCMate. | NOT_TESTED | NOT_TESTED |
| LIVE-05 | Stop/ausdrückliches Home: eigener Player genau einmal asynchron beendet, GUI bedienbar; fremde Wiedergabe wird nicht gestoppt. | NOT_TESTED | NOT_TESTED |
| VOD-01 | Film und Episode: echte Play/Pause/Stop/Spulen/unterstützte Sprünge, Timeline/Position/Gesamt-/Restzeit. Keine neue Player-Engine. | NOT_TESTED | NOT_TESTED |
| VOD-02 | Back bei sichtbarem und verborgenem VOD-OSD beendet nicht die Wiedergabe/Autoplay-Kette. Stop beendet bewusst. | NOT_TESTED | NOT_TESTED |
| VOD-03 | Pause/Seek ohne Fähigkeit deaktiviert; Sprung am Anfang/Ende begrenzt; Rewind/Forward über Kodi VideoPlayer. | NOT_TESTED | NOT_TESTED |
| VOD-04 | Serienende → nächste gültige Episode und Staffelwechsel; Resume/Gesehen-Status richtig. | NOT_TESTED | NOT_TESTED |
| VOD-05 | Stop/Fehler/fremdes Portal: keine nächste Episode, kein Doppelstart, kein Fokusfang nach Stop. | NOT_TESTED | NOT_TESTED |
| VOD-06 | Audio/Untertitel/Bild/Info mit IR bedienen. Danach Fokus wieder auf eigener OSD-Aktion; keine Übernahme fremder Fenster. | NOT_TESTED | NOT_TESTED |
| ART-01 | Dynamische Film-/Seriencover je mindestens zwei Minuten ansehen; mindestens drei 30-s-Grenzen, kein Platzhalterblitzen bei erfolgreicher Revalidierung. Keine Speicherung/Migration auf B auslösen. | NOT_TESTED | NOT_TESTED |
| ART-02 | Scrollen, zurückscrollen, Detailansicht und Neustart: dynamische Providerbilder wieder sichtbar. Erfolg nicht als internes XCMate-Archiv ausgeben. | NOT_TESTED | NOT_TESTED |
| ART-03 | Optional kontrollierte DNS-/Netzunterbrechung im Testprofil: neue ungeprüfte URL nicht freigeben, endgültig unsichere Quelle nicht dauerhaft anzeigen. Kein privates Netzwerk ändern. | NOT_TESTED | NOT_TESTED |
| ART-04 | Lesende Diagnose: physische interne Bildanzahl/-bytes getrennt von Jobs und Kodi-Texturecache; fehlende DB ≠ bewiesene Nullbilder. Keine Speicherprobe starten. | NOT_TESTED | NOT_TESTED |
| ART-05 | Box-A-Inventur und Sicherung abgleichen, vorhandene interne Bilder weiter anzeigen. Keine Umstellung. | NOT_TESTED | BLOCKED_BY_USER_STOP |
| ART-06 | Reale USB/SD/SMB-Migration: vorbereiten → Test → Inventur → Kopie → Hash → Darstellung → explizit aktivieren. Nur A, erst nach gesonderter Freigabe; keine interne Löschung. | NOT_TESTED; APPROVAL_REQUIRED | BLOCKED_BY_USER_STOP |
| ART-07 | Optionale interne Bereinigung in Dynamisch: nur eigens freigegebenes Testprofil, Inventur + zwei Bestätigungen; Abbruch/Neustart schützt restliche Dateien. Auf A erst später gesondert freigeben. | NOT_TESTED; APPROVAL_REQUIRED | BLOCKED_BY_USER_STOP |
| ART-08 | Nach freigegebener Migration/optionaler späterer Löschung tatsächliche Bytes/Freiraum und Bilder getrennt prüfen; Kodi-Texturen/DBs bleiben erhalten. | NOT_TESTED; APPROVAL_REQUIRED | BLOCKED_BY_USER_STOP |
| DB-01 | Wartung/Artwork-Status mehrfach öffnen; datensparsame BUSY/TIMEOUT/SCHEMA-Diagnose statt Erfolg mit Nullwerten. Kein Rebuild/Reset. | NOT_TESTED | NOT_TESTED |
| FOCUS-01 | Filmsuche und Detailansicht mehrfach öffnen/zurück; verborgener Control 300 bekommt keinen Fokus. Native Sichtbarkeit/Bedienbarkeit prüfen. | NOT_TESTED | NOT_TESTED |
| REG-01 | Dreigeteilte Suche Live/Film/Serie optisch unverändert; Programmtitel, Sender, Genre, Cover, IR und Back funktionsfähig. | NOT_TESTED | NOT_TESTED |
| REG-02 | Favoriten, Portale, Sendergruppen, Startgruppe und großer EPG erhalten. Bestehende .37-BINGIE-Widget-Routen unverändert nutzbar. | NOT_TESTED | NOT_TESTED |
| REG-03 | Wizard bestehendes Profil öffnen/abbrechen, Nachimport aktivierter Gruppen und EPG-Fortschritt nur in freigegebenem Testprofil prüfen; kein Box-A-Profil überschreiben. | NOT_TESTED | NOT_TESTED |
| REG-04 | Geräteinformationen/Startdauer/Infoleiste beobachten, keine GUI-Blockade bei Katalog-/Artwork-Arbeit. Messzeiten aufschreiben. | NOT_TESTED | NOT_TESTED |
| REG-05 | Je 20 Live-/Film-/Serien-Exitzyklen, fremde Wiedergabe, Stop-Fehler und erneuter bewusster Stop; kein Hänger/Doppelstart. | NOT_TESTED | NOT_TESTED |
| REG-06 | Mehrstündiger Alltagstest mit IR, Such-/EPG-/Rubrikwechsel und Serien-Autoplay; RAM/Fehler anonymisiert beobachten. | NOT_TESTED | NOT_TESTED |

## Ausschließlich lesende Box-A-Vorprüfung

`tools/xcmate_readonly_audit_02938.py` ist ein optionales externes Werkzeug, kein automatischer Update-Hook. Im Kodi-RunScript-Aufruf ohne Argumente liest es installierte Version und Profil und zeigt eine private Zusammenfassung. Es schreibt, kopiert und löscht nichts. Vor Einsatz auf A separat durch den Benutzer starten lassen. Auf Host mit eingehängten, ruhenden Daten:

```sh
python tools/xcmate_readonly_audit_02938.py --profile /PFAD/ZUM/PROFIL
python tools/xcmate_readonly_audit_02938.py --profile /PFAD/ZUM/PROFIL --verify-backup /PFAD/ZUR/SICHERUNG --quiescent-confirmed
```

Die zweite Form prüft eine bereits vorhandene Sicherung, erstellt sie nicht. `--quiescent-confirmed` darf nur gesetzt werden, wenn Kodi/Writer wirklich beendet sind. Das Werkzeug prüft interne XCMate-Bilder sowie JSON/XML/SQLite einschließlich WAL/SHM im dokumentierten Umfang, nicht ein vollständiges Kodi-Systemabbild. Symlinks, Änderungen oder Abweichungen verhindern die Behauptung einer vollständigen Verifikation.

## Grenzen des Kandidaten

OSD-Varianten A/B/C in `OSD_VARIANTEN_02938_DE.md` sind Skizzen, keine Android-Screenshots. A ist die vorläufige technische Variante, keine Nutzer-Designfreigabe. Home nutzt eine Kontextaktion; dauerhafte Home-Rail und vollständige rubrikübergreifende Scroll-Restauration sind nicht als fertig abgenommen. Physische Metadaten-Auslagerung (#171), dauerhaftes Wizard-Scanresume nach Prozessabbruch und quellensichere manuelle Guide-Zuweisung (#98) bleiben offen. #161 EPG-Hub und #182 Widget-Neuarchitektur sind getrennte Folgearbeit. Downloads/Aufnahmen wurden nicht repariert.
