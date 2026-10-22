# Separater Folgeplan #85 – nach manueller Next-Abnahme

Stand 22.10.2026. **Plan, keine implementierte Autoplay-Funktion.** Zuerst .19 auf Android abnehmen. Danach eigenen Branch/Draft direkt von der geeigneten geprüften Hauptbasis; freie neue 0.1.29.x-Nummer erst dann prüfen, keine Reservierung/Überschreibung von .19 oder alten .15/.16-Paketen. Kein automatisches Merge/Release.

## Geprüfte Vorarbeiten

- Issue #85 enthält die ausführliche Ended-/Stop-/Nonce-/Staffel-Spezifikation, aber keine Kommentare mit belegter laufender Implementierung. Die Historientreffer zu Serien-Autoplay sind Spezifikations-/Übergabecommits; ältere Root-/Live-Autostartkorrekturen sind keine Episodenfortsetzung. Alte Versionsvorschläge und damalige main-Basis im Issue sind überholt.
- PR #84, Head `b178721`, ist weiterhin ein separater .15-VOD-OSD-Draft auf .11. `media_osd.py` prüft Media-Identität, nutzt verifizierte `Player.PauseEnabled`/`Player.SeekEnabled`, stoppt per `stop_owned`, behandelt Back bei sichtbarer Leiste als Ausblenden und bei unsichtbarer als Stop. `poll()` zeigt/räumt ein eigenes WindowDialog auf; es unterscheidet **kein Ended/Stopped-Terminalereignis** und implementiert **kein Auto-next**. Selektive spätere Wiederverwendung von Ownership, OSD-Aktionsregistrierung und Fokus sinnvoll, kein Branch-Merge auf Verdacht. Kodi-API-/IR-Tests müssen auf neuer Basis erneut laufen.
- Aktuelles `media_progress.poll()` kann eine Wiedergabelücke erkennen und Fortschritt sichern, aber kein natürliches Ende zuverlässig von Stop/Fehler unterscheiden. .18/.19-Window-Rückkehrerkennung dient nur dem Fokus, **niemals als Auto-next-Trigger verwenden**.
- Das neue reine `media_sequence` kann für kanonische lokale Reihenfolge, Kontextvalidierung und Nachfolger genutzt werden; keine Watched-Heuristik als Endereignis. Playerstart/Resolver und .17-Live-Exit unverändert schützen.

## Umsetzung in eigenem Playback-Draft

1. Kodi-21.2-Callbacks/Vertrag belegen: eigener, sauber registrierter Beobachter für `onPlayBackEnded`, `onPlayBackStopped`, `onPlayBackError`, Shutdown/Exit. Callback darf nur ein begrenztes identifiziertes Ereignis an den Owner geben, keine GUI-/HTTP-/direkten Playeraktionen.
2. Session-Zustände IDLE → STARTING → PLAYING → ENDED_PENDING → STARTING(next) oder CANCELLED/FINISHED. Eindeutiger Nonce plus Portal-/Serien-/Episoden-ID; Endevent genau einmal konsumieren. Kein False-Trigger aus `isPlayingVideo()==False`, Timeout, Decoderfehler oder fremdem Player.
3. Expliziter Start einer Serie aktiviert die gewünschte Sitzungskette, ohne pro Folge Bestätigung. Kein stilles Überschreiben gespeicherter Optionen. Vor jedem Übergang gewinnt Stop/Exit/Shutdown, auch nach Endevent und vor Resolverstart. Sichtbare OSD-Leiste Back nur ausblenden; bewusster Medienexit verwirft die Kette. Live/Film/fremde Session bleiben ausgeschlossen.
4. Nächste lokale valide Folge derselben Serie/Portal-ID; numerisch, Lücken, Staffelwechsel, keine Specials/ambigen Metadaten/Wrap-around. Fehlende Daten kontrolliert und asynchron prüfen, bei Fehler beenden statt Request-/Startschleife. Alter Fortschritt vor Übergabe sichern; neuer Nonce, Titel/Poster/OSD und Intent vollständig zusammengehörig.
5. Erst Kernzustandsmaschine isoliert testen; dann OSD-Sitzungsschalter und selektive #84-Integration in eigenem überschaubarem Schritt. Gegen main/.19 diffen, Service-/Owner-/Live-Hotfixes nicht aus .15 zurücksetzen.

## Pflichtnachweise vor Android-Paket

Natürliche Endekette mehrerer Folgen und Staffelgrenze; manueller Start mitten in Staffel; Lücken/Serienende; doppelte Endcallbacks exakt ein Start; Stop/Back während PLAYING, Endevent-Queue und Übergabe jeweils null neue Starts; Fehler/Shutdown/fremde Wiedergabe/Film/Live null Kette; fehlende ID/Cache/Quelle kontrollierter Abbruch. Resume/Seen/Favoriten persistent, OSD-Metadaten zur neuen Session, Ended und Stopped auf echtem Kodi getrennt nachgewiesen. Vollsuite, ZIP/SHA, eigener Draft, Android zunächst NOT_TESTED. Echte Abnahme mit kurzen erlaubten Testfolgen, mindestens einer Staffelgrenze und Stop im Übergang; keine Auslieferung allein auf Polling-Simulation.
