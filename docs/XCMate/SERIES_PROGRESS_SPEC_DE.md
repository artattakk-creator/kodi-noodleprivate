# Spezifikationsnachtrag 0.1.29.21 – neuer Serien-Featuremodus

Der aktuelle ausdrückliche Auftrag #85 nach Android-Test 48 ersetzt für den neuen .21-Kandidaten die historische Vorgabe „Autoplay Aus / 10 Sekunden bestätigen“: bewusst gestartete eigene Episoden laufen bei natürlichem Ende nahtlos bis Stop/Serienende weiter, standardmäßig Ein für die Sitzung, im eigenen Player jederzeit schaltbar. Keine Migration vorhandener Einstellungen. Die historische Beschreibung unten bleibt als Projektstand erhalten und ist keine Behauptung einer bestehenden Implementierung in .20.

Implementierung/Abnahme: `AUTOPLAY_02921_DE.md`, `ANDROID_TEST_02921_DE.md`; Android NOT_TESTED, eigener Draft, kein Merge/Release.

---

> **AKTUALISIERUNG 22.10.2026 – NEUER VERBINDLICHER NUTZERWUNSCH [#85](https://github.com/artattakk-creator/kodi-noodleprivate/issues/85):** Wenn eine Serienepisode bewusst gestartet wurde, soll XCMate nach ihrem **regulären Ende automatisch und ohne weiteren Tastendruck** die nächste tatsächlich vorhandene Folge **derselben Serie und desselben Portals** abspielen. Am Staffelwechsel folgt die erste vorhandene Episode der nächsten regulären Staffel (Specials/Staffel 0 nicht blind einreihen). Das geht weiter, **bis der Nutzer ausdrücklich Stop/Verlassen wählt** oder keine Folge mehr existiert. Ein manueller Stopp auch während des Übergangs verhindert zwingend den nächsten Start. **Nur Serien; nicht Filme, Live-TV, Trailer oder fremde Kodi-Wiedergabe.** Unklare Metadaten, Abspielfehler und Offlinezustände führen zu kontrolliertem Abbruch statt Fehlstart/Endlosschleife. Ein Folgeende darf nur **einmal** verarbeitet werden; Resume/Watched, neue Playback-Session und XCMate-OSD-Titel müssen konsistent aktualisiert werden. Aktivierung als **neuer Autoplay-Funktionsmodus für absichtlich gestartete Serien**, zur Laufzeit im eigenen Player-OSD abschaltbar; keine heimliche Veränderung bestehender produktiver Settings. **Diese Anforderung ersetzt für die neue Umsetzung die ältere Empfehlung „Default Aus + 10-Sekunden-Pflichtcountdown“ weiter unten in dieser historischen Spezifikation.** Sie ändert NICHT rückwirkend Kodi-/XCMate-Benutzereinstellungen. Der [vorhandene Player-Draft #84 / 0.1.29.15](https://github.com/artattakk-creator/kodi-noodleprivate/pull/84) beinhaltet Autoplay **noch nicht**; für das Feature ist ein eigener neuer Draft **0.1.29.16** *vorgeschlagen* (Version erst gegen Repo prüfen). Android NOT_RUN, kein Merge/Release ohne Nutzerfreigabe. **Unter Version 0.1.30 bleiben.**
> **AKTUALISIERTER VERBINDLICHER NUTZERWUNSCH 22.10.2026 – [#85 Serien-Autoplay](https://github.com/artattakk-creator/kodi-noodleprivate/issues/85):** Bei einer bewusst gestarteten Serie soll nach jedem **regulären** Episodenende die **nächste tatsächlich vorhandene Episode derselben Serie/des selben Portals** automatisch starten, **auch über Staffelgrenzen hinweg, bis der Nutzer Stop/Exit wählt**. **Keine verpflichtende 10-Sekunden-Countdown-Bestätigung, kein erneutes OK pro Episode**. Dieses neue Ziel **ersetzt für die künftige Auto-Next-Funktion** die ältere, unten in Abschnitt 1 skizzierte Default-Aus-/Countdown-UX, **ohne bestehende produktive XCMate-User-Settings automatisch zu ändern**. Im neuen Serien-Player-Sitzungsmodus standardmäßig aktiv; im eigenen Player-Menü während der Sitzung abschaltbar. Autoplay nur bei verifiziertem natürlichem Episodenende und XCMate-eigener Session; nie bei manuellem Stop/Back-Exit, Kodi-Abbruch, Playback-Fehler oder Fremdplayer. Staffel 0/Specials überspringen, keine Endlosschleifen/Doppeltstarts. **PR #84 / 0.1.29.15 implementiert es noch NICHT**; separater Kandidat **0.1.29.16** nach Versionsprüfung, ohne 0.1.29.15-ZIP zu überschreiben und ohne 0.1.30. Siehe [#85](https://github.com/artattakk-creator/kodi-noodleprivate/issues/85) für Testmatrix.

# XCMate – verbindliche Spezifikation Serienfortschritt

**Teilimplementierung 0.1.27, 19.10.2026:** ID-gebundene Episode-/Movie-Bookmarks, manuelles
Resume/Weiterschauen/nächste Folge, Seen/Unseen/Reset einzelner Episoden implementiert und
getestet. [Bericht, Abweichungen und offene Android-Abnahme](IMPLEMENTIERUNG_027_KATALOG_WIDGETS_EPG_DE.md).
**Noch offen:** Auto-Next samt Countdown/Optionen, Continue-Reihe auf Serienstartseite und
Staffel-/Serienreset. Als erste Stufe isoliertes `media_state_v1.sqlite` mit getrennten
Transaktionen statt gemeinsamem JSON-Snapshot, damit parallele Kodi-Interpreter nicht
gegenseitig Änderungen überschreiben. Eine vorhandene `series_progress.json` wird weder
überschrieben noch migriert. Neue getaggte MediaSession und Polling ergänzen ausschließlich
neue Spielrouten; bisherige Live-/Movie-/Episode-Routen bleiben unverändert. Das alte Modell
unten beschreibt das vollständige Ziel, nicht bereits alle gelieferten Funktionen.

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
