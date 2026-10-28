# XCMate .48 – Android-Abnahme Box B

**Alle neuen Gerätefälle zunächst NOT_TESTED.** Host-/CI-PASS ersetzt keinen dieser Fälle. Master #250, Geräteberichte #247/#249, ältere Logbefunde #245. Box A bleibt unangetastet. Kein automatisches Update/Reset, kein Downgrade oder Deinstallieren für diesen Test.

Kandidat: `plugin.video.xtreammate-0.1.29.48.zip`, zugehörige SHA256-Datei prüfen. Installation als kumulatives Update über `.47`; für einen **vom Nutzer selbst gewählten** frischen Box-B-Aufbau die Fresh-Fälle separat ausführen. Keine vorhandenen Profile für einen Fresh-Test löschen. Die `.47` bleibt auf `main`, bis ein Merge ausdrücklich freigegeben wird; dieses ZIP ist kein schon veröffentlichter regulärer Repository-Stand.

Notieren: Box B, genaue Kodi-/Android-/Skinversion, installierte XCMate-Version, Datum/Uhrzeit, Kalt- oder Warmstart, `.42`-Kompatmodus und Artworkmodus. Bestehende `.42`-Einstellung erhalten. Auf einer neuen Box die benötigte Hardware-Kompatibilität bewusst prüfen; nichts an Box A ändern. Kodi muss die reguläre PIL-Abhängigkeit auflösen; wenn sie fehlt, als Installations-/Decoderfehler erfassen, keinen Bilder-PASS melden.

## Reihenfolge und Abbruch

1. Start und Wizard zuerst. Wenn Kodi abstürzt/hängt: aktuelle Stufe FAIL, keine Stressfolge und keine Datenlöschung. Kodi-Log/Android-Crash bzw. ANR privat sichern; Gerätezeit notieren. Fremdaddon-Meldung allein ist keine Schuldzuweisung.
2. Nach vorhandener oder bewusst eingerichteter Testkonfiguration: Sender von **BINGIE Home** starten, länger als zehn Minuten spielen, **einmal Zurück**. Nur bei bedienbarer Rückkehr weitere Zyklen testen. Bei Hänger nicht wiederholt Stop/Back auslösen.
3. Daten/Bilder, Mapping, Covermanager und Medienregression. Bestehende Film-/Serienwidget-Bindungen bleiben erhalten.
4. Der tatsächliche BINGIE-Umbau bleibt ohne konkreten Adapterdiff/Backup/Freigabe **BLOCKED_SKIN_INTEGRATION**. Native XCMate-Vorschau separat abnehmen. Historie D04 weiterhin BLOCKED, bis das echte Zeitfenster vorliegt.

Je Fall PASS/FAIL/NOT_TESTED und Beobachtung eintragen; BLOCKED samt Ursache benutzen, wenn eine Voraussetzung fehlt. Nicht ausgeführte Tests nicht pauschal als PASS markieren.

## Start / Bestand

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| BOOT48-01 | Update `.47`→`.48`; Version stimmt. Portale, Favoriten, Gruppen, manuelle EPG-Zuordnungen, Startsender, Artworkmodus und `.42`-Einstellung erhalten. | NOT_TESTED |
| BOOT48-02 | Kodi nach normalem Beenden kalt starten; Zeit bis BINGIE sichtbar und bis drei Reihen bedienbar separat messen. Kein vollständiger Kodi-Absturz/ANR. Drei Kaltstarts getrennt notieren. | NOT_TESTED |
| BOOT48-03 | Zwei Warmaufrufe ohne neue Vollimports; Widgets und XCMate-Menüs früh lokal nutzbar. Dienststatus zeigt einen Dienst, keine wiederholte Startschleife. | NOT_TESTED |
| BOOT48-04 | Benutzergewählte frische Box B: Kodi/XCMate ohne Portal und ohne EPG starten. Kein blockierender Anbieter-/Artworkrequest; Wizard erreichbar. | NOT_TESTED |
| BOOT48-05 | Vorhandener lokaler Bestand bei bewusst nicht erreichbarem Anbieter/Internet: Start und lokale EPG-/Medienansichten bleiben bedienbar; LastGood/Fallback ehrlich. Keine Datenverluste. | NOT_TESTED |
| BOOT48-06 | Kodi regulär beenden, erneut starten. Keine neue Service-/Worker-Endlosschleife; Exit-/Startzeiten und verbleibende Warnungen unterscheiden. | NOT_TESTED |

## Installationswizard – zusätzlicher Nutzerauftrag

Auf vorhandenem Profil nur den Einstieg/Cancel prüfen, sofern kein neuer Testaccount eingerichtet werden soll. Speichern ist eine bewusste Benutzeraktion.

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| WIZ48-01 | Aus Einstellungen den Installationswizard öffnen: Auswahl/Eingabe wird sichtbar, kein leer drehendes Verzeichnis, kein Root-/Widget-Reload vor dem Dialog. Aufrufzeit messen. | NOT_TESTED |
| WIZ48-02 | Zurück/Abbrechen vor Anmeldung. Vorhandene Portale und Konfiguration unverändert; erneut öffnen funktioniert. | NOT_TESTED |
| WIZ48-03 | Bewusst neuer Testaccount: Xtream-Anmeldung und Gruppen abrufen; Ladeaktivität/Abbrechen sichtbar. Keine zwei Authentifizierungsabrufe. Discovery-Dauer erfassen. | NOT_TESTED |
| WIZ48-04 | Nicht erreichbarer Anbieter oder falsche Zugangsdaten: begrenzter Fehler mit bedienbarer Wiederholen-/Abbrechen-Aktion. Kein dauerhaftes Drehen. Bei blockierender Plattform-DNS Limitation samt Zeit dokumentieren; kein Erfolg behaupten. | NOT_TESTED |
| WIZ48-05 | Während Erkennung abbrechen und erneut öffnen. Keine parallele Erkennungsflut, kein spät angewandtes Ergebnis im neuen Fenster. | NOT_TESTED |
| WIZ48-06 | Wenige Gruppen auswählen, Scan starten; Live/Filme/Serien getrennt, Auswahl mit IR bedienbar. Kein fremdes Portal verändert. | NOT_TESTED |
| WIZ48-07 | Auf bewusst neuer Box Quelle **ohne Anbieter-EPG**, nur externe XMLTV-Quelle: nach explizitem Speichern Quelle korrekt benannt; lokale Sendung/Bildadresse/Details bleiben nach Neustart vorhanden. | NOT_TESTED |
| WIZ48-08 | Existiert bereits ein gefüllter Guide ohne verifizierte Sicherung, EPG-Übernahme muss BACKUP_REQUIRED melden; kein automatischer Reset/Refresh. Für diesen Test keine neue Sicherung/Migration erzwingen. | NOT_TESTED |
| WIZ48-09 | Experimentell: PIN `6666`; falscher PIN und Cancel bleiben gesperrt. Bestehendes Profil startet nicht ungefragt den Wizard. | NOT_TESTED |

## Live-Rückkehr – P0

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| LIVE48-01 | Home-Livewidget → Sender, >10 Minuten normal laufen lassen, einmal Back aus reinem Vollbild. Eigener Stream endet genau einmal; Kodi Home mit bestehendem Fokus ist bedienbar. Dauer und Uhrzeit notieren. | NOT_TESTED |
| LIVE48-02 | Offene Infobar/Mini-EPG/Gruppen: Back schließt jeweils nur die Ebene. Erst Back aus reinem Live-Vollbild beendet den Stream. | NOT_TESTED |
| LIVE48-03 | Regulärer XCMate-Live-Einstieg und großer EPG → Start; Rückkehr bleibt bedienbar. Kein Doppelstop, neuer Autoplay-Start oder fremder Playerstop. | NOT_TESTED |
| LIVE48-04 | Erst nach LIVE48-01 PASS: fünf vollständige Livezyklen, anschließend optional 20. Nach einem Hänger sofort abbrechen und verbleibende Zyklen NOT_TESTED lassen. | NOT_TESTED |
| LIVE48-05 | Nach erfolgreichem Live-Back Kodi Home offen lassen: bereits eingerichtete Film-/Serienreihen werden weiterhin automatisch aktualisiert; keine neue Bindung oder Neustart nötig, sofern echte Indexänderung vorliegt. | NOT_TESTED |

Fehlt im Fehlerfall `PLAYER_STOP_DONE` / FIFO-ACK, bleibt das ein nativer Stopfehler. Ein früher Playback-Callback oder `NATIVE_STOP_POSTED` allein ist kein Abschluss. Keine gefälschte „Home repariert“-Meldung bei ausbleibendem ACK.

## Gemeinsame Daten und echte Sendungsbilder

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| DATA48-01 | Drei Sender mit **nachweislich im Feed vorhandenem** aktuellem Bild wählen. Tatsächliches Bild, Titel, Zeit und Synopsis im großen EPG-Detail und Livewidget vergleichen. Neutrale Grafik/Logo allein ist kein Bild-PASS. | NOT_TESTED |
| DATA48-02 | Bei derselben Sendung Mini-EPG, Infobar, großes Raster/Detail und Hero vergleichen: identisches Now/Next, Quelle/Zeit und gleiche gehashte Eventkorrelation. | NOT_TESTED |
| DATA48-03 | Tatsächliche Serienepisode/Film mit gelieferten Metadaten: Cast, Regie, Jahr, Genre, Staffel/Episode soweit vorhanden. Keine allgemeinen oder fremden Filmposter als vermeintlich passende Episode. | NOT_TESTED |
| DATA48-04 | Nachrichten/Talkshow ohne belegtes Bild: ehrlicher neutraler Fallback; Text verfügbar; keine erfundenen Besetzungsdaten. Fehlergrund bei fehlenden Quellfakten/Decoder/Netz/Cache notieren. | NOT_TESTED |
| DATA48-05 | Reellen Now→Next-Wechsel beobachten. Titel/Bild/Zeit/Progress wechseln konsistent ohne Fokus-Autoplay und ohne sichtbare alte Programme als neue Sendung. | NOT_TESTED |
| DATA48-06 | Bereits erfolgreich geladenes Bild: zurückscrollen, Kodi neu starten, vorhandenen Offlinebestand prüfen. Kein globaler Bild-/Jobreset. | NOT_TESTED |
| DATA48-07 | Zukünftige Tage bis tatsächlich vorhandener Feedgrenze (höchstens 20) read-only prüfen. Fehlende Quelle nicht durch erfundene Daten oder erzwungenen Import kompensieren. | NOT_TESTED |
| D04 | Sieben **echte gespeicherte** Vergangenheitstage. Ohne realen Zeitraum keine Abnahme; Uhrzeit nicht verstellen, Datenbank nicht löschen. | BLOCKED_REAL_TIME_WINDOW |

## Senderleiste und großer Vorschaubereich

Einstellungen → Widgets → **Live-TV: Senderleiste und große Vorschau (.48)** öffnet ausschließlich eine eigene XCMate-Ansicht.

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| HERO48-01 | Kleine Senderbuttons; über die komplette Startgruppe (88+) bis zum letzten Sender horizontal navigieren. Jeder Fokus zeigt seine lokalen Programminfos, ohne Streamstart. | NOT_TESTED |
| HERO48-02 | Ein Event mit verifiziertem Bild: großer Bereich zeigt dieses Bild, Titel, Sender, Zeit, Synopsis, Now/Next und Fortschritt. Bildloser Sender hat ehrlichen Fallback. | NOT_TESTED |
| HERO48-03 | Auf drei verschiedenen Buttons OK: genau der gewählte Sender startet einmal. Back ohne Wiedergabe schließt nur die Vorschau; aktuelle Medienreihen nicht verändert. | NOT_TESTED |
| HERO48-04 | Tatsächliche bestehende BINGIE-Startseite: schmale Reihe + Hero statt großer Logokacheln. Erst nach konkretem Skin-Diff, Backup, SHA/Rollback und ausdrücklicher Freigabe testen. Native Vorschau reicht nicht als PASS. | BLOCKED_SKIN_INTEGRATION |

## EPG-Zuweisung im großen Raster

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| MAP48-01 | Sender markieren, lang OK (Kodi-Kontextmenü) → **EPG zuweisen**. Auch bei leerer Programmzeile erreichbar. Keine Keymapänderung. | NOT_TESTED |
| MAP48-02 | Alternative: mit Hoch zur Kopfzeile, Rechts zum sichtbaren **EPG zuweisen**-Button, OK. Derselbe Dialog erscheint. | NOT_TESTED |
| MAP48-03 | Anbieter-EPG/Xtream, EPGShare01/Kaimandura bzw. konfigurierte Quellen auswählbar. Namen/IDs nur aus lokalem Quellbestand; keine ungefragte Netzsuche. | NOT_TESTED |
| MAP48-04 | Kanal anhand Name/EPG-ID suchen, ggf. „Weitere Kanäle“. Auswahl zeigt echte Vorschau im ursprünglichen Raster; Dialogpanel klappt dazu ein. Bei fehlenden lokalen Programmen verständlicher Hinweis. | NOT_TESTED |
| MAP48-05 | Zwei Quellen mit gleicher Kanal-ID vergleichen. Anzeige muss zur gewählten Quelle gehören; bisherige Zuordnung ist bis Save unverändert. | NOT_TESTED |
| MAP48-06 | Back/Abbrechen: ursprüngliche Sender-/Quellzuordnung, Gruppen, Zeitposition, Raster und Fokus wiederhergestellt. Danach erneut öffnen. | NOT_TESTED |
| MAP48-07 | Explizit Speichern: nur ausgewählter Sender verändert. Mini/Infobar/Widget und Raster übernehmen die Zuordnung; Kodi-Neustart bestätigt Persistenz. Andere Sender unverändert. | NOT_TESTED |
| MAP48-08 | Bestehendes Legacy-Mapping ohne neue Quellbindung bleibt funktionsfähig. Kein Änderung der Quellprioritäten, kein destruktiver Guide-Refresh. | NOT_TESTED |

## Covermanager / geschützte Medienfunktionen

| ID | Handlung und echte Erwartung | Status |
|---|---|---|
| COVER48-01 | Film und Serie → Covermanager: vorhandene echte Poster-/Backdrop-Kandidaten erscheinen mit lokalen Vorschaubildern, ohne zunächst einen neuen Metadatenabruf abzuwarten. | NOT_TESTED |
| COVER48-02 | „Anbieter aktualisieren“ bewusst auslösen; Netzwerk-/Format-/Decoderfehler sichtbar und abbrechbar. Bereits funktionierende Cover bleiben erhalten. | NOT_TESTED |
| COVER48-03 | Kandidat → große Vorschau → Auswählen → Speichern. Poster/Backdrop getrennt übernehmen; nur bestätigte Wahl verändert das Medium. | NOT_TESTED |
| COVER48-04 | Nach Neustart und bei Offlinebestand gespeicherte Auswahl wiederfinden/anzeigen. Keine Originalbilddatei gelöscht. | NOT_TESTED |
| COVER48-05 | Preview abbrechen, Quellen wechseln, leere Ergebnisse: keine versehentliche Übernahme. TMDb bleibt opt-in; ohne Token ehrlicher Hinweis. | NOT_TESTED |
| REG48-01 | Drei bestehende Widgetreihen ohne Rebind. Film- und Serienposter optisch unverändert, unterschiedliche echte Medien sichtbar. | NOT_TESTED |
| REG48-02 | Drei Film- und drei Serienklicks starten/öffnen jeweils richtigen Titel; Staffel/Episode stimmt. | NOT_TESTED |
| REG48-03 | Film-/Serien-Back beendet nur eigenen Stream und stellt Detail-/Suchposition wieder her. | NOT_TESTED |
| REG48-04 | Serien-Autoplay nach natürlichem Ende inkl. Staffelwechsel, Resume und Gesehen-Status erhalten; kein Autoplay nach Stop. | NOT_TESTED |
| REG48-05 | Echte neue/entfallene Filme über **regulären** Katalogstand: automatische Filmwidget-Aktualisierung ohne Neustart/Neubindung erhalten. Keine Daten für Test löschen. | NOT_TESTED |
| REG48-06 | Suche Live/Programmtitel/Film/Serie, Originalgrafiken, Infobar, Sendergruppen, >12 Sender, Favoriten und IR-Fokus unverändert. | NOT_TESTED |

## Messprotokoll und sichere Diagnose

Je Cold/Warm getrennt mindestens fünf vorhandene Messungen sammeln, wenn die P0-Gates stabil sind. Einzelwerte/Anzahl und p50/p95 berichten; bei weniger Messungen keine vermeintlich belastbare Langzeitstatistik. Keine pauschalen 180 s als akzeptablen Start deklarieren.

| Messung | Erfasst | Ergebnis |
|---|---|---|
| Kodi Start → Home sichtbar / Widgets bedienbar | echte Uhrzeiten, Cold/Warm | NOT_TESTED |
| Wizard anklicken → Eingabe sichtbar → Gruppen sichtbar | `SETUP37` ENTRY48/QUEUED48/DISCOVER + Gerätebeobachtung | NOT_TESTED |
| Live anklicken → erstes Video → Gruppen / Mini sichtbar | vorhandene FLOW46/PREPARE47-Marker | NOT_TESTED |
| Erstes **korrektes** Mini-Now/Next → stabiler Inhalt | PROGRAMME48 MINI / Eventvergleich | NOT_TESTED |
| Scroll-/Fokuswechsel p50/p95 / >88 Sender | echte IR-/Bildschirmmessung; keine Fokus-Netzabfrage | NOT_TESTED |
| Back nach >10 min → Stop-ACK → Home bedienbar | PLAYER_EXIT / RETURN48 / LIVE_EXIT | NOT_TESTED |

Lokale Auswertung, z.B. `python tools/analyse_xcmate_flow48.py /privater/pfad/kodi.log --run-kind cold`. Ausgabe vor Weitergabe prüfen. **Keine privaten Rohlogs nach GitHub laden.** Für einen kompletten Kodi-Absturz ist zusätzlich ein nativer Android-Crash-/ANR-Nachweis hilfreich; Add-on-Marker allein können die Ursache nicht beweisen.
