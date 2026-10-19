# XCMate 0.1.27 – vollständiger Android-TV-Abnahmeplan

**Alle folgenden Geräteprüfungen sind OFFEN.** Cloud-Tests modellieren API-/Datenverträge,
sie ersetzen keinen Kodi-Renderer, Android-Speicherzugriff oder realen Stream.
[Implementierungsbericht/ZIP/Prüfsumme](IMPLEMENTIERUNG_027_KATALOG_WIDGETS_EPG_DE.md).

## Testvorbereitung

- Kodi-Version/Build **21/Omega**, Android-TV-Version, Gerätemodell, RAM, Displayauflösung,
  Fernbedienungsmodell, XCMate-Version/Dienstbuild **27** und konkrete BINGIE-MOD-Version notieren.
- Bisherige 0.1.26-ZIP und eine eigene Sicherung des Add-on-Profils bereithalten. Passwörter,
  Konto-URLs und Tokens weder in Screenshots noch Testbericht veröffentlichen.
- Kandidaten-ZIP und SHA herunterladen, SHA unabhängig prüfen. Kodi → Add-ons → Aus ZIP-Datei
  installieren; ggf. „Unbekannte Quellen“ selbst bewusst aktivieren. Keine Deinstallation mit
  Datenlöschung, keine Keymap und kein Skin-Patch installieren. Kodi vollständig neu starten.
- Vorher/Nachher Anzahl und Auswahl der Konten, Gruppen, Live-Favoriten, Startsender,
  manuelle EPG-Zuordnung, Quellen und vorhandene Einstellungen kontrollieren.
- Zwei Xtream-Accounts mit überschneidenden IDs, deaktivierte Gruppen, kleiner und großer
  Katalog (möglichst 2.746 und 53.664 Titel/Sender), echter langer und kurzer Guide nutzen.
  Kein öffentlicher Feed oder Provider wird als alleiniger Vollständigkeitsbeweis akzeptiert.

Ergebnisse je Fall: **PASS / FAIL / nicht ausführbar**, Zeit, erwartete/tatsächliche Aktion,
Screenshot bei UI-Fehlern, diagnosefähige sichere Datei und Reproduktionsschritte.

## A – Freeze 0.1.26: vor allem anderen

1. Startkanal spielt ohne Doppelstart. 1× OK zeigt unveränderte kompakte echte Infobar,
   2× OK/Down Playerleiste, weiteres Down Einstellungen, Up/Back zurück. Je zehn Zyklen.
2. Links im Vollbild öffnet Sender, zweites Links Gruppen; alle Pfeile, OK, Menü und Back
   einmalig wirksam. Senderwechsel/Gruppe/Favoriten samt Fokus prüfen, keine verschluckten Tasten.
3. Pause/Fortsetzen, Stop, Seeking/Live-Ende nur bei geeigneter Quelle; tatsächliche Kodi-
   Freigabe berücksichtigen. Umschalten während Downloads und EPG-Import muss bedienbar bleiben.
4. Stop/Abbruch/Neustart: gespeicherte Remote-/Dienstdiagnose unter Einstellungen → Wartung.
   Fremdes Kodi-Video und Noodle Private starten: kein XCMate-Live-Overlay oder fremder Seek.
   Vorhandene globale Keymap darf nicht automatisch aktiviert sein.

**Bei Freeze-Regression keinen Merge freigeben.**

## B – Sechs Hauptpunkte und Einstellungen

1. Exakt Startkanal, Live-TV, EPG, Filme, Serien, Einstellungen; ein/mehrere Konten.
   Ohne Account vorhandener Assistent. Hauptmenü selbst startet bei Diagnosepause kein Video.
2. Zehn Kategorien. Accountwahl bleibt bestehen, aktive Portal-ID kontrollieren. Bestehenden
   Account hinzufügen/bearbeiten/deaktivieren nur mit Testdaten, ohne Produktionskonto zu löschen.
   Kontoinformationen bewusst öffnen; keine unmaskierten Zugangsdaten in normalen Menülabels.
3. Startkanal fehlt/gelöscht/Gruppe deaktiviert: keine kaputte synthetische Spiel-URL.
   Kontrollierten Auswahlhinweis prüfen. Alle vorhandenen EPG-/Gruppen-/Remote-Verwaltungswege erreichbar.
4. Aufnahmeordner: erlaubter lokaler Ordner, USB/SMB falls verfügbar, schreibgeschützter oder
   entzogener Pfad. Nur erfolgreicher UUID-Dateirundtest ändert `recordings_folder`.
   Keine zurückgebliebene Testdatei, bisheriger Wert bei Abbruch/Fehler erhalten.
5. Engine-Diagnose ohne/mit vorhandener ffmpeg-Binary: Versionstest höchstens zwei Sekunden,
   keine Installation oder automatische Aufnahme. Positive Probe ist **noch kein Aufnahme-PASS**.

## C – Filme und Serien: Fokus und vollständige Navigation

1. Beide Landingpages: horizontale Coverrail, Kategorien darunter, fokussierter Titel mit
   echtem Anbieter-Fanart/Poster. Fehlende/ungültige/überdimensionierte Bilder zeigen eigenen
   neutralen Ersatz, kein Hänger und kein falsches Bild eines zuvor fokussierten Titels.
2. Erste aktivierte Kategorie automatisch. Links öffnet Gruppen, Rechts blendet Gruppen
   aus und erweitert Posteransicht. LEFT aus linker Spalte, auch zweiter/dritter Zeile,
   öffnet Gruppen ohne auf falsches Poster zu springen. Leere Gruppe und deaktivierte Gruppe.
3. Alle Titel über Seitentasten und Rechts am Seitenende erreichbar; >50 und >100 Titel,
   letzte unvollständige Seite und zurück. Gruppen-/Seiten-/Posterposition nach Detail-Back erhalten.
   Schnell 30× Pfeile, OK/Back während Metadatenjob; kein doppeltes Detail oder veralteter Fokus.
4. Film-/Seriendetails: echter Titel, Plot, Jahr/Genre/Bewertung/Laufzeit soweit belegt;
   fehlende Angaben ehrlich. Favorit setzen/entfernen und nach Neustart erhalten.
5. Film starten und Stop → eigene Detailseite/Posteransicht wieder nutzbar, Skinvideo verdeckt
   diese vollständig. Trailer nur bei gültiger YouTube-ID und installiertem Add-on.
6. Bei 17:30/45:00 stoppen, Kodi neu starten: Resume nahe 17:30 angeboten; tatsächlichen Seek
   testen. Neustart ab Anfang, unter 60 Sekunden alter Bookmark erhalten; danach plausibel ersetzen.
   Unseekbarer Stream: eine Erklärung, kein wiederholtes Seek. Fremdes Video nie verändern.
7. Staffeln numerisch, Episoden korrekt. Gewählte Folge startet, keine andere Serien-ID trotz
   gleicher Episode-ID in anderem Account. Seen ab 90 % bzw. maximal 120 s Rest (mind. Hälfte),
   Begonnen-/Ungesehenanzeige, manuelles Seen/Unseen/Reset per Menü und Weiterschauen/nächste Folge.
   Kein automatischer Folgestart. Automatischer Countdown/Serienreset sind offene Folgestufen.
8. Defekte Media-State-Datei nur in gesichertem Testprofil simulieren: Fehlermeldung, keine
   stillschweigende Löschung/Neuanlage; Live-TV bleibt nutzbar.
9. M3U/STB: Rückleitung in vorhandene Medienlisten kontrollieren. Neue Vollindex-UI dort
   noch nicht freigegeben; keine angeblich vollständigen Nulltreffer bestätigen.

## D – Cache und globale Suche

1. Suchwort mit Treffern in allen drei Bereichen: drei getrennte echte Zahlen, korrekte
   Live-Start-/Film-/Serien-Detailziele. Mehrere Seiten, letzte Seite, >50 Treffer,
   Groß/Klein/Umlaute, keine Treffer, ausgeblendete Gruppen und mehrere Accounts.
2. Datumslose Providerbasis: gefüllte Rail mit „Verfügbarer Titel“, nicht alle Filme als „Neu“.
   Zehn Tage Neuheiten, ältere Auffüllung und maximal 100 Railtitel standardmäßig;
   `recent_days`/`recent_keep` ändern, Kategorien vollständig erreichbar lassen.
3. Kodi neu starten und Netzwerk trennen: bereits indizierte Suche, Listen und Widgets lesen
   weiter lokal. Ein leerer/fehlgeschlagener Folgeabruf erhält die letzte gefüllte Liste.
   Ausdrückliches Deaktivieren von Account/Gruppe wirkt trotzdem sofort.
4. Kaltcache: verständlicher Zustand; explizites Katalogladen läuft im Hintergrund und
   Back bleibt möglich. Zeiten bis erster Anzeige/Navigation und Profil-/RAM-Größe messen.

## E – Drei BINGIE-MOD-Reihen

Nach [Einrichtungsanleitung](BINGIE_MOD_WIDGETS_027_DE.md) manuell erstellen. Exakte Skinversion
und reale Menüpfade ergänzen. Drei horizontale Rows fotografieren: Live-Startgruppe mit
Startkanal zuerst und echtem Now/Next; neueste Filme; neueste Serien. Logos/Posterformat,
Fokus, OK, Back, Vollbildrückkehr und Widgetaktualisierung prüfen. Film/Serie öffnet Details,
Live spielt direkt. Bestehende fremde Widgets, Skin und Noodle Private unverändert.

## F – Langzeit-EPG, Speicher und Erinnerungen

1. Hauptmenü EPG: Vollbild-Tagesliste, tatsächliche Startkanalgruppe, Links Gruppen,
   OK andere Gruppe, Rechts zurück. Fehlender Startsender → konfigurierte/erste aktive Gruppe.
   Gruppenwechsel in Sitzung respektieren. Logos und alle Fokusziele prüfen.
2. Oben Datum vor/zurück, standardmäßig sieben, optional zehn Tage. Echter +9-Tag nur wenn
   Quelle vorhanden; Kurzguide muss spätere Tage ehrlich leer lassen. Beginn/Ende, Mitternacht,
   Sommer-/Winterzeit und lokale Zeitzone; 100er-Programmseiten bei vielen kurzen Ereignissen.
3. Jetzt-Sendung und Titel mit eingefrorener Infobar vergleichen, manuelle Senderzuordnung
   vor altem Alias, Kurz-EPG-Fallback nur echte gecachte Daten. Quellen-/Reichweitenstatus
   trennt letzten erfolgreichen Import von Datum letzter Sendung.
4. Zehn-Tage-Guide einmal importieren, mehrfach öffnen/neustarten: keine Downloads durch
   Navigation. Bei aktivierter Hintergrundautomatik und noch lückenlosen 24 h alle Kanäle
   kein neuer Bulkabruf. Lücke/kurzer Guide lässt Aktualisierungsbedarf zu. „EPG aktualisieren“
   ausdrücklich testen, ohne automatische Konten-/Quellenänderung.
5. Kürzerer Folgefeed (nur 24 h) erhält alte später liegende echte Sendungen. HTTP-Fehler,
   `PROVIDER_LIMIT`, `NO_NEW_GUIDE`, `DOWNLOAD_FAILED`, ungültige Zeitstempel, defektes GZIP,
   knapper Speicher: vorheriger brauchbarer Stand bleibt. Status darf keinen neuen Erfolg erfinden.
6. Während langsamer Sender-/Datumsabfrage sofort OK drücken: vorige Sendung nicht neuem
   Sender zuordnen. Schnell Zurück: kein nachträgliches Öffnen alter Daten/Dialogs.
7. Zukünftige Sendung → fünf Minuten vorher erinnern; Duplikat, Storno, Kodi-Neustart,
   verpasste Sendung und Dienst-Neustart prüfen. Genau eine Meldung im normalen Verlauf.
   Keine Weckgarantie; Kodi muss laufen. Kein automatisches Tune/Record und keine Fake-Timeroption.
8. Profilverbrauch nach zehn Tagen und nach kürzerem/fehlerhaftem Import vergleichen.
   Budgetfehler dürfen bestehende Quellen/Konten/Favoriten/Zuordnungen nicht löschen.

## Review und regulärer Updateweg

1. Testprotokoll mit installierter ZIP-SHA, Kodi-/Skinversion und konkreten PASS/FAIL-Werten
   dem PR zuordnen. Fehler zuerst im Entwicklungsbranch korrigieren; dieselben Risiken erneut prüfen.
2. Erst nach ausdrücklicher Nutzerfreigabe PR nach `main` übernehmen. Der bestehende
   Push-Workflow baut dann Repositoryindex, ZIP und Prüfsummen. Vorher **kein** Indexbump,
   kein Publish/Release-Tag, keine automatisch erzwungene Kodi-Aktualisierung.
3. Nach freigegebenem Publish `addon.xml` und `addons.xml` vergleichen, veröffentlichte
   ZIP/SHA und Workflow prüfen. Kodi: GS Media Repository aktualisieren → XCMate → Informationen →
   Aktualisieren → Kodi komplett neu starten → Build/Version kontrollieren → Freeze-Smoke-Test.
4. Rollback: 0.1.26-ZIP ohne Profildatenlöschung installieren und neu starten; neue getrennte
   SQLite-Dateien werden von 0.1.26 nicht benutzt. Gesicherte Produktionsdaten nicht ungeprüft
   mit Testprofil überschreiben. Bibliotheks-/EPG-Neuaufbau nicht als Profilreset behandeln.

Bis zur Abnahme Issues #21/#23–#26 als implementierte Teilstufen mit offenen Gerätefällen
führen; keine vollständige Serien-/Timer-Spezifikation oder Aufnahmefunktion als erledigt schließen.
