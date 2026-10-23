# Android-Abnahme XCMate 0.1.29.25

Ziel: Android TV 13 / RK3528 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD
2.2.3 / IR. **Gerätetest dieser Version: NOT_TESTED.** Vorherige PASS für
Original-Icon und Premium → Lightweight gelten weiter als Ausgangslage.

## Installation

Nach dokumentiert erfolgreicher Veröffentlichung: GS Media Repository auf
Updates prüfen, XCMate regulär auf **0.1.29.25** aktualisieren. Alternativ
das im PR verlinkte `plugin.video.xtreammate-0.1.29.25.zip` installieren;
SHA256 mit der gleichnamigen `.zip.sha256` abgleichen. Keine Deinstallation,
kein Datenreset, kein Cachelöschen. Während des Updates Wiedergabe und offene
XCMate-Dialoge regulär schließen. Kodi einmal sauber beenden/neu starten.

Bitte jeden Punkt mit PASS/FAIL/NOT_TESTED melden. Bei FAIL: Design, Ansicht,
Taste, vorher sichtbare Markierung, Uhrzeit und beobachtete Aktion angeben.
Rohlogs nicht öffentlich hochladen; nur bereinigte Codes/Fenster-IDs teilen.

## F01–F09 – Fokus und Aktionen zuerst

1. **F01 Lightweight:** Filme → verschiedene Kategorien → Posterwand.
   D-Pad bewegen; ausgewählte Kachel eindeutig sichtbar. OK öffnet genau den
   ausgewählten Film. Kategorienliste/Zurück funktionieren weiter.
2. **F02 Premium:** Dasselbe in Space Premium; horizontalen Reihen
   `Weiterschauen/Favoriten/Neu` und die große Posterwand durchlaufen.
   Rahmen muss auch bei sehr hellen/dunklen Covern sichtbar bleiben.
3. **F03 Film-Detail:** Öffnen und sofort OK drücken, bevor Metadaten fertig
   erscheinen. Anschließend mehrfach Details öffnen, verzögerte Aktualisierung
   abwarten. Erste Aktion ist markiert; OK startet diese Aktion, keine Suche.
4. **F04 Andere Aktion:** Favorit oder Posterstatus markieren, Metadatenupdate
   abwarten. Markierung und ausgeführte Aktion stimmen weiterhin überein.
5. **F05 Suche:** Suche bewusst per D-Pad markieren und OK. Nur dann öffnet
   die Suche. Abbrechen; aus der Detailsuche mit Down zurück zur Aktionsliste.
   Vorhandene ausdrückliche Kontext-Suchfunktion bleibt separat bedienbar.
6. **F06 Serien:** Serienübersicht → Serie → Staffel → Episode.
   In jeder Liste sichtbarer Fokus, korrekte OK-Aktion und funktionierendes Back.
7. **F07 Player-Rückkehr:** Film/Episode starten, regulär stoppen/zurück.
   Detail-/Episodenansicht sofort per IR bedienbar, ohne erst aus der Serie
   heraus und wieder hinein zu gehen. Kein Doppelstart/fremdes Portal.
8. **F08 Wechsel/Neustart:** Premium → Lightweight → Premium, Kodi neu starten;
   F02/F03/F06 wiederholen. Original-Icon unverändert. Bereits installierte
   Premium-Bilder sollen keinen erneuten Download benötigen.
9. **F09 Ordner unterscheiden:** XCMate-Kategorien-/Staffellisten separat von
   Speicherordnerwahl/ZIP-Dateiauswahl prüfen. Letztere sind **Kodi-Systemdialoge**.
   Bei dort fehlender Markierung separat FAIL melden, inklusive aktuell aktivem
   Design und ob es auch in Lightweight auftritt. Keine globalen Skin-/Keymap-
   Anpassungen als Voraussetzung dieser Abnahme.

## A01–A05 – Artwork

1. **A01** Bekannten fehlenden Film (z. B. Aladdin 1992) öffnen →
   **Posterstatus**. Nur Quelle-Feldname, Kandidatenzahl, Status, Versuche und
   Zeitwerte notieren; keine Bildadresse/Providerdaten veröffentlichen.
2. **A02** `DB_BUSY` bedeutet lokale Sperre, nicht Netzwerk. Status nach kurzer
   Wartezeit erneut abrufen. Bei DNS/TLS/Timeout/HTTP-Fehler den tatsächlichen
   Code melden; keine gleiche Ursache für alle fehlenden Bilder voraussetzen.
3. **A03** **Dieses Poster erneut versuchen** einmal wählen. `PENDING`,
   `RUNNING`, READY oder konkreten Endfehler beobachten. Cooldown/WAIT respektieren;
   keinen globalen Retry, keine Löschfunktion verwenden.
4. **A04** Über 240, möglichst 500 verschiedene Titel blättern, zurückscrollen,
   Kodi neu starten. Vorhandene Cover müssen lokal erhalten bleiben; neue
   erfolgreiche Downloads erscheinen ohne erneutes Öffnen der Übersicht.
5. **A05** Artwork-Status, Reserve/Budget und Pause/Fortsetzen wie bisher prüfen.
   Keine Pflicht, fast fertige Downloads eigens zu unterbrechen. Fehlende
   Providerquelle ist von internen DB-/Downloadfehlern zu unterscheiden.

## R01–R05 – Schutz und Lifecycle

1. **R01** EPG E01–E10 wie zuletzt bestätigt wiederholen, inkl. Mehrstunden-
   und Tagesnavigation, Senderwechsel/Zurück. Live-Overlay und IR-Zapping prüfen.
2. **R02** Portale, Gruppen, EPG-Zuordnungen, Favoriten, Resume und Gesehen-Status
   erhalten. Film und Episode inklusive Resume starten.
3. **R03** Natürliches Episodenende → nächste Folge prüfen; Stop darf keinen
   Autostart auslösen. **B02 Staffelübergang bleibt gesondert offen**, zählt hier
   weder als bestanden noch als Voraussetzung dieses Hotfixes.
4. **R04** Nach dem regulären Update Kodi sauber beenden/neu starten und
   XCMate/Film/Serie/EPG erneut öffnen. Neue GetDirectory-/Unknown-addon-/
   Fünf-Sekunden-Service-Meldungen mit Uhrzeit und bereinigtem Kontext melden.
5. **R05** Wenn verfügbar `FOCUS_DEFER` / `FOCUS_READY` betrachten: `key` ist
   dort die Control-ID. Dauerhaft DEFER ohne bedienbare Aktionen als FAIL melden.
   `APP_WORKER_STOP_PENDING` kennzeichnet noch laufende I/O, keinen behaupteten
   erfolgreichen vollständigen Shutdown.

## Bewusst nicht enthalten

Keine neue native Aufnahmeengine, geplanten Aufnahme-Timer oder Meine-Medien-
Ansicht in `.25`. Ein FFmpeg-Codec-Eintrag im Log bedeutet keine verfügbare
Recorder-CLI. Dafür folgt eine getrennte Entwicklung mit eigener Abnahme.
Bei kritischer Regression `.24` als unveränderte Rückfallbasis verwenden;
keine Benutzer-/Bilddaten löschen. Ergebnis zu #115/#111 und dem Hotfix-PR
zuordnen, Issues erst nach tatsächlicher Android-Bestätigung abschließen.
