# 0.1.29.12 – eigener VOD-/Serien-Player (#79, #40)

## Historischer Befund

Untersucht wurden die Git-Historie von live_overlay.py/player.py/media_progress.py,
OSD-/Player-/XML-Dateibäume und Issues #17/#20/#79. Commit d7d0970 (0.1.11)
enthält ein ausdrücklich als Live-TV beschriebenes WindowDialog. 297b934 führt
die zweistufige TV-Bedienung ein; 902b3dd (0.1.26) besitzt die Tape-Deck-Reihen
Pause, -10 s, +30 s, Stop, Weitere sowie Ton/Bild/Untertitel. Die gemeldete
frühere gute Optik passt zu dieser vorhandenen Live-Leiste. Ein eigenständiges
historisches VOD-OSD ist in den untersuchten Dateien/Commits nicht nachgewiesen.
Es wird daher keine zweifelsfreie Identifikation des vom Nutzer gesehenen
Screens behauptet. Dieser Kandidat rekonstruiert ein VOD-OSD aus den Original-
XCMate-Elementen, statt einen fremden Player/Skin zu übernehmen.

Originale tv_panel/tv_normal/Transport-Symbole werden unverändert benutzt.
Ein neuer nativer neongrüner Fokusrahmen ergänzt sie. Die SVG-Modellansicht ist
keine Android-Aufnahme; echte Screenshots sind Teil der Geräteabnahme.

## Implementierung

media_osd.MediaOSD ist ein programmatischer WindowDialog wie das bewährte
Live-Overlay. Er wird auf dem vorhandenen Service-Owner-Thread aufgebaut und
gepumpt, ohne doModal/Worker-GUI-Callbacks, Netzwerk-/Katalogzugriff oder globale
Keymap. Ein transparenter sichtbarer Capture-Button nimmt OK im eigenen Vollbild
an; die Leiste legt darauf native Fokusbuttons über das Video. Kodi bleibt die
Wiedergabeengine. Metadaten/Poster kommen aus der bereits geprüften lokalen
Resolver-Session, keine HTTP-Anfrage bei Richtungstasten.

Native Links/Rechts/Hoch/Runter-Navigation bewegt den grünen Rahmen. Native
onControl verarbeitet OK genau einmal; das folgende onAction(7) löst keinen
zweiten Button aus. Reihen werden bei Capability-Wechsel neu verknüpft, ohne
versteckte oder deaktivierte Ziele. Pause/Seek werden mit Player.GetProperties
(canpause/canseek) geprüft; Seek zusätzlich mit Player.SeekEnabled und echter
Laufzeit. Bei unbekannter Fähigkeit keine aktive Scheinaktion. Ton-/Untertitel-
wahl nutzt die tatsächlich verfügbaren Player-Spuren. Bild/Ton öffnet Kodis
jeweilige Einstellungen und gibt die Capture-Ebene währenddessen frei.

- OK: Leiste einblenden, Startfokus Pause (wenn verfügbar), sonst Info.
- Back bei sichtbarer Leiste: nur Leiste ausblenden, Wiedergabe läuft weiter.
- Back bei bereits ausgeblendeter Leiste: bewusster Medien-Exit, kontrollierter
  Stop wie der bestehende Vollbild→Navigation-Pfad.
- Stop: aktuellen Resume-Checkpoint sichern, dann nur die anhand Nonce/InfoTag
  verifizierte XCMate-Medienwiedergabe beenden. Mehrfachstop bleibt idempotent.
- Fremde Wiedergabe oder neue Session: Capture sofort schließen, nichts stoppen.
- Während fremder Dialoge keine Aktivierung/Fokusübernahme. Keine Änderung am
  Live-TV-Overlay, seiner Senderliste oder Gruppensteuerung.

media_actions ist eine eigene, nach Medienart/Fähigkeit gefilterte Registrierung.
Spätere Handler erhalten geprüfte Portal-/Medien-/Staffel-/Folgen-IDs, keine URL.
Es ist **kein Download-Button registriert**, kein Downloadmanager implementiert.
Eine spätere Downloadfunktion muss Berechtigung/Quelle/Ziel/Abbruch eigens prüfen.
PR #50 wird nicht integriert; die Basisgrafiken bleiben auch unter einem späteren
Theme verfügbar. Die gemeinsame tatsächliche Darstellung ist noch abzunehmen.

## Android-Test – NOT_RUN

Basis ist der getrennte Statusfix 0.1.29.11; andere Feature-Drafts sind nicht
enthalten. Zuerst #80 / 0.1.29.11 abnehmen, Profil sichern, dann dieses ZIP.

1. Filme 10× und Episoden 10× starten, OK-Leiste aufrufen, native Fokuswege prüfen.
   Green-Frame muss unmittelbar sichtbar wechseln; kein Doppelklick auf Pause.
2. Play/Pause, Seek ±10/30 s mit echten seekfähigen und nicht seekfähigen Streams.
   Ohne bestätigte Fähigkeit keine aktive Seek-/Pause-Aktion.
3. Tonspuren wählen, Untertitel wählen/an/aus, Bild- und Toneinstellungen öffnen
   und schließen. Rückkehr zur Steuerung ohne blockierendes Capture.
4. Position/Laufzeit/Poster/Titel korrekt? TV-Lesbarkeit mit Titan BINGIE MOD und
   zusätzlich Estuary. Screenshot mit Fokus auf Pause, Tonwahl und Episodentitel.
5. Back bei offener Leiste darf nicht stoppen. Stop bzw. Back bei geschlossener
   Leiste beendet die eigene Session inklusive Ton; Resume bleibt gespeichert.
6. Zur korrekten Detail-/Staffelposition zurück, neu öffnen und fortsetzen.
   Zehn Zyklen ohne schwarzes Bild, Spinner oder MODAL_TIMEOUT.
7. Fremdes Kodi-Video starten: XCMate-OSD darf nichts stoppen/steuern. Fremden Dialog
   öffnen: kein Fokusdiebstahl. Live-TV mit OK/Links/Sendern/Gruppen unverändert.
8. 0.1.29.8 bleibt unveränderte Rückfallbasis. Keine Release-/Mergefreigabe aus
   Hosttests ableiten; #40/#79 erst nach tatsächlicher Abnahme bewerten.

## Host-Verifikation

581/581 Tests PASS (84,390 s), davon 13 neue OSD-/Ownership-/Capability-Fälle.
Die 10 Film- und 10 Episodenzyklen sind **simulierte Kodi-Kontrolltests**, keine
realen Android-Wiedergaben. CRC, sichere Pfade, Source-Bytes, Python-AST und
unabhängige byteidentische ZIP-Reproduktion PASS. Prüfsumme/Paketgröße stehen
in TESTERGEBNISSE_02912_MEDIA_OSD.json. Native Screenshots und TV-Abnahme fehlen.
