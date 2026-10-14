# XCMate – verbindliche Spezifikation Serienfortschritt (noch NICHT implementiert)

**Priorität:** P1, nach Stabilisierung des Android-Startsenders und der Fernbedienung.  
**Ziel:** TV-Fernbedienungsfreundliches „Weiterschauen“, automatisch nächste Folge, Gesehen-Status, sicheres Fortsetzen. Keine Annahme, dass das System im Stand 0.1.9 schon existiert.

## Nutzerfunktionen und Einstellungen

1. `Nächste Folge automatisch abspielen`: Aus / Ein (Default zunächst **Aus**). Bei Ein nach normalem Abspann/Wiedergabeende 10-Sekunden-Countdown mit „Jetzt abspielen“, „Abbrechen“, damit kein unbeabsichtigter Datenverbrauch erfolgt. Optional später Modus „ohne Rückfrage“.
2. `Fortsetzen anbieten`: standardmäßig Ein. Für eine begonnene Episode Auswahl „Bei MM:SS fortsetzen“ oder „Von Anfang an“; falls bewusst von Anfang: Position nach stabiler Wiedergabe ersetzen, nicht bereits beim Dialog öffnen.
3. `Gesehene Folgen markieren`: standardmäßig Ein. Ab **90 %** oder höchstens **120 Sekunden Restlaufzeit** gilt eine Episode als gesehen; Grenzfälle und sehr kurze Clips gesondert behandeln.
4. `Weiterschauen` auf Portal-/Serienstartseite; pro Serie aktuelle Folge, letzte Position und nächster Titel. Staffel-/Folgenlisten zeigen `✓ Gesehen`, `▶ Begonnen: 23:41 / 51:00`, `○ Ungesehen`.
5. `Fortschritt zurücksetzen` pro Episode, Staffel, Serie (mit Bestätigung); `Folge als gesehen/ungesehen markieren` per Kontextmenü; Einstellungen pro XCMate/Portal respektieren.
6. Reihenfolge **Staffelnummer → Episodennummer**, nicht Dateiname/Uploadzeit; keine automatische Wiedergabe eines Specials mit nicht eindeutigem Folgeschlüssel.

## Persistentes Datenmodell

Profilpfad `special://profile/addon_data/plugin.video.xtreammate/series_progress.json`. JSON mit `schema_version: 1`, `updated_at`, `episodes` und Schlüsseln auf Basis von `portal_id`, `series_id`, `season_number`, `episode_id`. Niemals Credential-URLs oder Passwörter im Verlauf speichern.

Episode-Beispiel (keine realen Kundendaten):

```json
{
  "schema_version": 1,
  "episodes": {
    "portal-uuid|series-42|season-2|episode-230": {
      "position_sec": 1428,
      "duration_sec": 3050,
      "watched": false,
      "completed_at": null,
      "updated_at": "2026-10-14T09:00:00Z"
    }
  }
}
```

- Position nur nach plausibler Dauer (z. B. mindestens 60 s angesehen) regelmäßig schreiben (alle 10–15 s), außerdem bei Stop/Pause/Abbruch/Kodi-Exit nach Möglichkeit; Schreibzugriffe begrenzen.
- Atomare Speicherung: Temp-Datei im selben Verzeichnis, `flush/fsync`, `os.replace`, Schreiblock, Schema-Version; defekte Datei nicht stillschweigend überschreiben. Bei abruptem Android-Stromverlust darf maximal das letzte Intervall fehlen.
- `completed` überschreibt nicht irrtümlich weitere Episoden. Beim erneuten Anschauen einer gesehenen Folge Entscheidung „Neustart“ / „Fortsetzen“, sofern Bookmark existiert.
- Bei unbekannter/wechselnder Provider-Episoden-ID zusätzliche stabile Identitätsprüfung mit Staffel + Episodennummer; keine zwei Episoden zusammenführen, wenn IDs widersprüchlich sind.
- Der Status gehört zum jeweiligen Portal, nicht zum globalen Kodi-Videoverlauf; mehrere Portale dürfen nicht kollidieren.

## Kodi-Integration

- Spielpfade `_series_episodes` und `_play_episode` in `main.py` mit einem zentralen Controller verbinden.
- Playback-Session enthält nur nicht geheime IDs/Metadaten. `xbmc.Player`-Callbacks für `onAVStarted`, `onPlayBackEnded`, `onPlayBackStopped` plus periodische Positionsmessung in einem überwachten Dienst; asynchrone Event-Reihenfolge sauber behandeln.
- Ein Seek zur gespeicherten Position erst dann, wenn Player bereit ist; maximal Dauer minus Sicherheitsabstand (z. B. 30 s). Live-TV und Filme werden von dieser Serienlogik ausdrücklich ausgeschlossen.
- Am regulären Wiedergabeende Episode „gesehen“ setzen und ausschließlich bei aktivierter Option die nachfolgende Episode derselben Serie auflösen; Metadaten zunächst aus lokalem Cache, bei Bedarf außerhalb des UI-Threads nachladen.
- Nur **ein** Auto-Next-Start je Abschlussereignis; keine Endlosschleifen bei Streamfehlern, Abbruch oder nur 1 Sekunde Wiedergabe. Manuelles Stoppen soll kein Auto-Next auslösen. Staffelgrenze optional vom Nutzer bestätigen lassen.

## Definition of Done / Regressionstests

- [ ] Folge nach 17:30/45:00 abbrechen → Wiedereinstieg bei ca. 17:30.
- [ ] Kodi hart neu starten → Bookmark ist noch da, korrekte Serie/Folge.
- [ ] Staffel 1 Folge 5 wird vollständig zu Ende gespielt → gesehen, nächste Folge korrekt vorgeschlagen.
- [ ] Auto-Next Aus → keine Folgewiedergabe.
- [ ] Auto-Next Ein → ein Countdown, genau ein Folge-Start; Zurück unterbricht.
- [ ] Serienwechsel, Portale und parallele Geräteprofile verwechseln den Fortschritt nicht.
- [ ] Netzwerk-/Kodi-Abbruch sowie leere/abweichende Episodenlisten führen zu keinem Absturz.
- [ ] Gesehene-Markierung und Weiterschauen unter Titan BINGIE MOD auf Android geprüft.
- [ ] Datenmigration, atomarer Schreibtest, keine Geheimnisse in Logs.
