# Android-Abnahme – sechs BINGIE-Reihen / PR #437 und #438

Ziel: **Box B, Kodi 21.3, Titan BINGIE MOD 2.2.3**. Alle Geräteprüfungen zunächst **NOT_TESTED**. Box A nicht verändern. Keine Neuinstallation, kein Profil-/Cache-/Datenbankreset. Review-Version bleibt **0.1.29.90**; keine Repository-Veröffentlichung.

## Vorbereitung

1. Bestehende Home-Reihen, Namen, Reihenfolge, Quellen und Positionen sowie Provider/Favoriten kurz dokumentieren. Vorhandene Sicherung behalten.
2. ZIP und SHA256 aus test-builds/media-spinner beziehen und vergleichen. Dies ist ein gezielter Update-Test, keine GS-Media-Neueinrichtung.
3. Auf Box B **Kodi → Add-ons → Aus ZIP-Datei installieren**, Review-ZIP wählen; bestehende Daten übernehmen.
4. **XCMate → Einstellungen → Aussehen und Darstellung → Widgets → BINGIE-Home-Layout prüfen/vorbereiten** öffnen bzw. angebotenen Upgrade-Dialog verwenden. Vorschau, private Sicherung und Dateiprüfsummen prüfen; nur beabsichtigte Layoutänderung bestätigen. Ohne Bestätigung wird der neue Skinadapter nicht installiert. Keine neuen Quellenordner oder Keymaps anlegen.
5. Bei unbekanntem Skin-/Profilstand oder verweigerter Hashprüfung abbrechen und Diagnosecode melden. Keine Dateien löschen oder Skin zurücksetzen.

## Einzelprüfungen

| ID | Prüfung | Ergebnis |
| --- | --- | --- |
| W6-01 | Hero und Senderlogo-Leiste; lokales Jetzt/Danach, Beschreibung und Fortschritt ohne vorherigen Senderstart | NOT_TESTED |
| W6-02 | Filme → Serien → Im Kino → Disney → Diese Woche im Trend → MP3s; persönliche Zusatzwidgets weiterhin vorhanden | NOT_TESTED |
| W6-VOD | Filme: Header auch beim Laden/Leerzustand, eigener Spinner, Cover, horizontale Navigation, Filmklick und Zurück | NOT_TESTED |
| W6-SERIES | Serien: Header/Spinner/Cover, Staffel-/Episodenklick, Resume/Autoplay unverändert | NOT_TESTED |
| W6-CINEMA | Im Kino: echte now_playing/movie-Quelle, Poster, Klickziel, Zurück und Fokus | NOT_TESTED |
| W6-DISNEY | Disney: gespeicherte Discover-Quelle Anbieter 337/DE, echte Metadaten/Poster und Klickziel | NOT_TESTED |
| W6-TREND | Diese Woche im Trend: trending_week/tv, echte Treffer, Klickziel; kein Bewertungsranking | NOT_TESTED |
| W6-MP3 | Audioquelle, Ordner im Musikfenster, echten Titel abspielen/stoppen, anschließend weiter navigieren | NOT_TESTED |
| W6-03 | Up/Down durch alle Reihen, Left/Right durch Covers/Logos; korrekter Fokus, persönliche Reihen erreichbar | NOT_TESTED |
| W6-04 | Nur tatsächlich ladende Reihe dreht; Cachetreffer ohne neue Arbeit brauchen keinen Spinner | NOT_TESTED |
| W6-05 | Erfolg/leer/Fehler beendet Spinner, spätestens 60 Sekunden; wartende Zusatzreihen melden Wartet | NOT_TESTED |
| W6-06 | Fehlender/deaktivierter Helper oder Mehrdeutigkeit ehrlich gemeldet; eigener TMDB-Token unverändert | NOT_TESTED |
| W6-07 | Cover/Logos bei kurzzeitigen Problemen erhalten; keine ungefragten Löschungen/globalen Neuaufbauten | NOT_TESTED |
| W6-08 | Kodi normal schließen/starten; alle sechs Reihen und Benutzerwidgets prüfen, dreimal wiederholen | NOT_TESTED |
| W6-09 | Fremdwidgets behalten gespeicherte Namen, Pfade und Positionen, einschließlich bisherigem Kino/Trend/Disney und Audio | NOT_TESTED |
| W6-10 | Provider, Gruppen, Favoriten, EPG-Zuordnungen, TMDB, Resume, Space Blue und SkinShortcuts vergleichen | NOT_TESTED |
| W6-11 | Bestehende Wiedergabe/Zurück prüfen; bei erstem Exit-Hänger stoppen und Logs privat sichern | NOT_TESTED |

Negative Fälle nur bei tatsächlichem Auftreten oder vorhandenem geeignetem Testprofil prüfen. Keine Inhalte/Favoriten/Verbindungen löschen und keine Add-ons deinstallieren, um Leer-/Fehlerzustände zu erzeugen. Ohne echten langsamen Job bleibt dessen Geräteprüfung NOT_TESTED; Hostfehlerinjektionen sind getrennte Belege.

## Offene Masterfälle

- Galileo/XMLTV → Details / manuelles Speichern (#433): denselben Termin, Quelle und Bild vergleichen; TMDB und TVMaze getrennt. Historischer Nutzer-FAIL bleibt bis zu neuem echten PASS erhalten.
- EPG-Synchronität (#161/#430): denselben Sender/Termin in Home, Mini, Groß und Details vergleichen; manuelles Mapping erhalten.
- Speicher/SQLite und Rolling-Cache (#108/#430): gültige Bilder unter Reserve/BUSY erhalten; aktive Referenzen und letzte Sicherung schützen. Keine Bereinigung auf Zuruf.
- Exit (#174): historischer Android-FAIL, durch diesen Widget-Patch nicht als repariert abgenommen.

Je Zeile PASS / FAIL / NOT_TESTED, Version, Quelle, Neustartverhalten und gegebenenfalls Ladezeit festhalten. Keine Provider-URLs, Tokens, Passwörter oder privaten Verbindungsdaten auf GitHub veröffentlichen.
