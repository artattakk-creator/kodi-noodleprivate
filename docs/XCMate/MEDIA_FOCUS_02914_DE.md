# 0.1.29.14 – große Medienreihen, Neongrün-Fokus und echte Fanart (#74)

Basis: separater Statusfix 0.1.29.11. Die funktionalen UI-Commits aus #77 /
0.1.29.9 werden gezielt übernommen; der unveränderte alte #77-ZIP wird nicht
überschrieben. Dieser Kandidat enthält weder Player #79 noch Raster #57 noch
Speicherprofile/Migration aus #78. Keine Einstellungen-/DB-/Pfadmigration.

## Änderungen

Weiter ansehen → Favoriten → Neu hinzugefügt, große 164×246-Poster mit
mehrzeiligen Titeln, Kategorien/Suche oben und nativer vertikaler Ausschnitt
bleiben aus #77 erhalten. Die neongrünen Fokusrahmen (#39FF14) betreffen Buttons,
Kategorien, Poster, Details, Staffeln und Episoden. Ein 4-Pixel-Nine-Slice-Rahmen
verhindert verzerrt dicke Ränder auf breiten bzw. hohen Controls. Die Rahmen
werden vom nativen Kodi-Fokus gerendert; keine HTTP-/Timer-Verzögerung beim
Fokuswechsel. Versteckte/Labels/leere Listen bleiben von Fokus ausgeschlossen.
Bestehende Appearance-Werte werden weder geändert noch gespeichert; der neue
explizite Fokusrahmen wird beim XML-Generieren nicht blau getönt/heruntergedimmt.

Fanart ist nun eine eigene Quelle: keine still als Hintergrund ausgegebene
Poster-Vergrößerung. Provider-Details können Hintergrundadressen in info,
movie_data oder auf der Wurzelebene liefern. backdrop_path, backdrop, fanart und
fanart_image werden geprüft, einschließlich Listen; cover_big kann Poster sein.
Nur gültige HTTP(S)-Bildadressen gelangen in die bestehende Hintergrundqueue.
Es wird keine relative TMDB-ID zu einem vermeintlich geprüften Treffer erfunden
und keine neue API-/Speichereinstellung eingeführt.

Die konkrete ausgewählte Medien-ID bleibt über den vorhandenen Owner-/Generation-
Mechanismus maßgeblich. Bereits lokale passende Fanart wird sofort angezeigt;
fehlende Bilder lädt der bestehende begrenzte Worker. Der Verzeichnisrevision-
Watcher aktualisiert das aktuelle Detail ohne Neuöffnen. Beim Titelwechsel ohne
Fanart wird der vorherige Hintergrund gelöscht und neutral ersetzt. Ein eigener
dunkler Verlauf hält Poster/Aktionen/Text vor dem farbigen Bild lesbar. Fehlende
Provideradresse, voller alter Cache oder Downloadfehler bleiben reale Grenzen;
0.1.29.11 zeigt sie unabhängig vom DB-Zustand. #78 wird nicht heimlich aktiviert.

## Prüfung

580/580 Hosttests bestanden (86,629 s), einschließlich sechs neuer Fokus-/Fanart-
Fälle und sechs übernommener Rail-Tests. Die gefrorenen Schutzsignaturen beziehen
sich nun ausdrücklich auf 0.1.29.11. media_art wird wegen der beauftragten
Fanart-Trennung nicht mehr als unverändert ausgegeben; Player, Live, Remote,
Owner, EPG und die fünf Playback-/Close-/Such-/Owner-Methoden bleiben geschützt.
ZIP-Details siehe TESTERGEBNISSE_02914_MEDIA_FOCUS.json.

## Android-Test – NOT_RUN

1. Zuerst den Statusfix testen. Danach nur dieses isolierte UI-ZIP auf der
   Testinstallation prüfen; 0.1.29.8 bleibt unveränderte Rückfallbasis.
2. Filme/Serien: Header, alle drei Reihen, Kategorien, Poster, Detailbuttons,
   Staffeln und Episoden mit echter IR-Fernbedienung. Grüner Rahmen aus normaler
   Fernsehdistanz sofort eindeutig, kein Fokus auf unsichtbaren Controls.
3. Leere Favoriten/Weitersehen, lange Titel, große Listen, horizontales/vertikales
   Scrollen und Auswahl nach Detail→Back; gleiche #73-Back-/Reopen-Prüfung.
4. Film mit bekannter Provider-Fanart öffnen: großflächiges zum Film passendes
   farbiges Bild, Poster vorn, Beschreibung/Aktionen lesbar. Screenshot erstellen.
5. Noch nicht geladene Fanart im Detail abwarten: Bild erscheint ohne Neuöffnen.
   Andere Film-ID ohne Hintergrund öffnen: neutrales Bild, niemals vorheriger Film.
6. Bei fehlenden Bildern Budget/Queue aus 0.1.29.11 ansehen. Keinen Reset und kein
   unkontrolliertes Retry der großen alten Queue auslösen.
7. Bereits gespeicherte eigene Darstellungswerte testen, ohne sie zu ändern;
   neuer Rahmen bleibt klar erkennbar. Default/Titan BINGIE MOD und Estuary prüfen.
8. Wiedergabe/Resume/Stop, Live-TV und EPG unverändert prüfen. Keine Freigabe allein
   aufgrund der Hosttests; echte TV-Screenshots und Protokoll gehören zur Abnahme.

Die vorhandene MEDIA_RAILS_0299_LAYOUT.svg ist ein älteres geometrisches Schema
für die übernommenen Reihen, kein aktueller Kodi-Screenshot.
