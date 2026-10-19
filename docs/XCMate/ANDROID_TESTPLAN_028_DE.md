# XCMate 0.1.28 – Android-TV-Abnahme und regulärer Updateweg

**Alle Gerätefälle OFFEN.** Die positiven Live-/Remote-Befunde beziehen sich auf **0.1.27**.
Cloudtests des neuen Codes sind keine Geräteabnahme.
[Bericht und Paketnachweis](IMPLEMENTIERUNG_028_PERFORMANCE_EPG_UI_DE.md) ·
[weiterhin gültige Detailfälle 0.1.27](ANDROID_TESTPLAN_027_DE.md).

## Vorbereitung und Installation

1. Kodi 21/Omega-Build, Android-Version, Gerät/RAM, BINGIE-MOD-Version, Auflösung und Remote
   notieren. Möglichst kleinen Stick **und** stärkere Box separat prüfen.
2. Bestehendes XCMate-Profil und 0.1.27-Installationsdatei sichern. Konten, Gruppen, Favoriten,
   Startsender, EPG-Quellen/-Zuordnungen, Remote-Mappings und Resume vor/nach Update vergleichen.
3. Die verifizierte **0.1.28-Test-ZIP** und SHA aus dem Draft-PR verwenden. Über Kodi aus ZIP
   installieren, dieselbe Add-on-ID, keine Deinstallation/Datenlöschung und keine zweite Beta-ID.
   Kodi vollständig neu starten; Version **0.1.28**, Dienstbuild **28** kontrollieren.
4. Kein Skin-/Keymap-Import. Vorhandenes 0.1.27-Profil weiterverwenden. Einen Kaltstart nur im
   separaten gesicherten Testprofil simulieren; Produktionscache nicht als Fehlerfix löschen.
5. Je Fall PASS/FAIL/nicht ausführbar, Uhrzeit, sichere Diagnose und reproduzierbare Schritte.
   Keine Provider-URL, Zugangsdaten, Tokens oder private XML-Dateien öffentlich anhängen.

## A – Live-TV-Freeze vor allem anderen (je 10 Zyklen)

- 1× OK → kompakte echte Infobar; 2× OK/Runter → Player; weiteres Runter → Optionen.
- Links → Sender, zweites Links → Gruppen; alle Pfeile, OK, Menü, Back mit einem Ereignis.
- Hoch/Runter im Vollbild zappt genau einmal, Listennavigation bewegt genau eine Zeile.
- Fokus, Pause/Weiter, Stop und zulässiges Seek prüfen; Back aus jeder Ebene korrekt.
- Fremdes Kodi-/Noodle-Video: kein XCMate-Overlay, Stop oder fremdes Resume/Seek.
- Keine automatische globale Keymap. Remote-/Dienstdiagnose nach Stop und Neustart noch lesbar.

## B – Pre-Play / Verbindungsphase (alle noch am Gerät zu prüfen)

- Startsender über Home, direkte Live-TV-Liste, Widget, Navigator-Sidebar und D-Pad-Zapping.
- Name/Logo/echtes lokales Jetzt/Danach vor dem ersten Videobild. Fehlende Daten klar leer;
  Fortschritt nur bei gültigem aktuellen Intervall. Verbinde/Puffert sichtbar.
- Nach richtigem Videostart Übergabe ohne doppelte Dialoge, Fokusverlust oder Kodi-OSD.
  Infobar blendet nach regulärer Dauer aus; anschließend unveränderte Tastenfolge aus A.
- Back und Stop während Aufbau, unerreichbarer Stream, Netzverlust, erneute Senderwahl,
  Portalwechsel, schnelles Zapping, alter verspäteter Callback, mindestens 60s Timeout.
  Kein nachträglich gestarteter falscher Sender und kein Ghost-Dialog.
- Dienst fehlt/Neustart: begrenzter Fallback, gespeicherter Code
  `PREPLAY_SERVICE_UNAVAILABLE`; Anzeige nicht als erfolgreich gezeichnet werten.
- Prüfen, ob Kodis eigene Busy-Anzeige die Pre-Play-Leiste verdeckt. Native Renderer-/Z-Order-
  Befunde dokumentieren; Cloud-ACK ist allein kein sichtbarer Frame-Nachweis.

## C – Große Kataloge, Gruppen und Abbruch

- Filme und Serien jeweils kalt/warm öffnen. Fenster und Zurück sofort bedienbar; kein
  Fehlerton, kein Vollimport aller drei Typen und keine minutenlange reguläre Sperre.
- Erste aktivierte/gewählte Kategorie zuerst; andere aktive Gruppen schrittweise vollständig.
  Deaktivierte Gruppen nicht herunterladen, außer unvermeidbarer Antwort eines Providers,
  der Kategorieparameter ignoriert; dann nicht indizieren. Diagnosezähler prüfen.
- >200.000 Providerzeilen, >80 MiB Antwort, SQLite >64 MiB; letzte Seite und echte Gesamtzahl.
  Kein künstliches Abschneiden der Sammlung; tatsächlichen Speicherbedarf notieren.
- Während Import schließen/Back, sofort anderer Bereich, Kodi neu starten, Netz trennen und
  Datenträger voll simulieren **nur im Testprofil**. Alter vollständiger Bestand bleibt lesbar.
- Gleiches Fenster mehrfach öffnen: keine identischen parallelen Großimporte.
- Favoriten/Resume/Startsender behalten; neue undatierte Baseline nicht „alles neu“.
  Widgets bleiben mit gespeicherten älteren/undatierten Karten gefüllt.

## D – Suche

- Vom Film- und Serienbereich eine bekannte Phrase in allen drei Rubriken suchen.
- Vollständige reale Zahlen für bereits importierte aktive Gruppen, jeweils letzte Seite.
- Fehlender/laufender/fehlgeschlagener Index unterscheidbar von echten null Treffern.
  Während Hintergrundimport aktualisieren; neue Treffer erscheinen.
- Umlaute, Akzente, Groß-/Kleinschreibung, mehrere Accounts mit gleichen IDs, deaktivierte Gruppen.
- Lokale Navigation/Eingaben verursachen keine direkten HTTP-Aufrufe; Back bleibt möglich.

## E – EPG und Startgruppe

- Anbieter, Kaimandura DE, EPGShare DE und AT **einzeln und kombiniert**; tatsächlichen Import-
  status, letzte erfolgreiche Zeit, Programmzahl, aktive Deckung und letzte Sendung notieren.
- Zuerst Startsender, dann sichtbare Startgruppensender, übrige Startgruppe und andere aktive
  Gruppen. Dieselben Now/Next-Daten in Homewidget, Infobar, Senderliste und Tagesguide.
- Manueller Refresh: REQUESTED → RUNNING → echtes READY/PARTIAL_SUCCESS/Fehler. Angefordert
  ist kein Erfolg. Parserfehler mit sicherer Datei/Zeile sichern, nicht die private Feed-URL.
- DE-TypeError und AT-ValueError gezielt erneut prüfen. Aktuelle Originalfeeds wurden in der
  Cloud wegen HTTP 403 **nicht** erfolgreich geprüft; diesen Punkt nicht überspringen.
- GZIP/HTTP-Kompression, normale XMLTV-Deklaration, invalide Einzelsendungen und gesamte kaputte
  Quelle. Letzter Guide bleibt erhalten, weitere Quellen können erfolgreich sein.
- Manuelle und eindeutige automatische Zuordnung; gleiche Namen aus mehreren Ländern müssen
  ohne sichere ID mehrdeutig bleiben. Keine willkürliche Senderzuordnung.
- Tag 7–10 soweit Quelle reicht; kürzerer Folgefeed erhält spätere Tage. Nach Kodi-Neustart
  kein erneuter Gesamtfeed, solange aktive echte 24h-Deckung vorliegt. Offline/volle Platte:
  vorhandene Programme lesbar; keine fingierte vollständige Abdeckung.

## F – Sprache und Core-Darstellung

- Kodi deutsch + XCMate English, Kodi englisch + XCMate Deutsch, dann Kodi übernehmen.
  Nach Neustart weiterhin eigene Wahl; `lang_priority` und globale Kodi-Sprache unverändert.
- Neue Menüs/Medien/Guide/Widgets prüfen. Native Kodi-Einstellungen und eingefrorene alte
  Live-/Legacytexte sind ausdrücklich noch nicht vollständig unabhängig übersetzt.
- Hintergrund-/Panel-/Icondeckkraft, fünf Farben, drei Fontstufen in Medien/Guide testen.
  Vorschau → Abbrechen erhält alten Wert; Übernehmen/Neustart persistent; Reset vollständig.
- Fokus/Lesbarkeit, lange DE-/EN-Texte, 720p/1080p/4K, kleine Coverlabels. Fehlende Skinfonts,
  beschädigte Preferences oder fehlende Ressourcen ergeben Core-Fallback.
- Bestehende Live-UI/BINGIE unverändert. Kein Space-Premium-Paket automatisch installiert.
  Optionaler Theme-/Language-Pack-Installer ist in diesem Kandidaten noch nicht geliefert.

## Messprotokoll (pro Gerät, kalt und warm)

| Messung | 0.1.27 | 0.1.28 | Status |
| --- | --- | --- | --- |
| Klick → erster sichtbar gezeichneter Pre-Play-Frame | offen | offen | Gerätetest |
| Klick → erster Video-Frame / warmes Zapping | offen | offen | Gerätetest |
| Live-Liste → erste benutzbare Senderzeile | offen | offen | Gerätetest |
| Filme/Serien → Fenster / Kategorie / erstes echtes Poster | offen | offen | Gerätetest |
| Vollständiger Hintergrundimport je Typ und aktiver Gruppenanzahl | offen | offen | Gerätetest |
| Startsender → erstes gültiges Now/Next / Suchdauer | offen | offen | Gerätetest |
| Back → geschlossener Dialog und freier Fokus, während Import | offen | offen | Gerätetest |
| RSS/RAM, Profil-/SQLite-/Artwork-/Texturcachegröße | offen | offen | Gerätetest |

Cloudwerte des Berichts getrennt führen. Ein neutrales Ersatzbild ist kein erstes echtes Poster.
Keine Millisekunden- oder RAM-Garantie ohne reale Hardwaremessung.

## Freigabe und regulärer Repository-Updateweg

Draft-PR bleibt offen, bis die P0-Fälle geprüft sind. Kein eigenmächtiger Merge/Publish.
Erst nach ausdrücklicher Freigabe: finalen Main-Abstand/CI prüfen, PR reviewen/mergen und den
bestehenden Main-Publish-Workflow den normalen GS-Media-Repositoryindex erzeugen lassen.
Anschließend ZIP/Manifest/SHA/Index-MD5 und reguläres Kodi-Update 0.1.27 → 0.1.28 kontrollieren.
Bis dahin bleibt `addons.xml` produktiv auf **0.1.27**, die Test-ZIP ändert diesen Weg nicht.
Ein Downgrade nur mit bewusst gesichertem Profil/0.1.27-Paket; keine automatische Datenlöschung.
