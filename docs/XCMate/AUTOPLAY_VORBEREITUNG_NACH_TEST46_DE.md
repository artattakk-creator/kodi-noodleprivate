# #85 – technische Vorbereitung nach Android-Test 46

Stand 22.10.2026. **Vorbereitung, nicht implementiert.** .19 ist jetzt main und Android-Tests 42–46 sind für geprüfte Abläufe PASS. Manuelle Next-Funktion, Resume, Seen und IR bilden die Basis. Artwork-.20 bleibt eigener Draft; kein Autoplay-Hook in seinen Dateien. Erst separates Folgepaket auf geeigneter geprüfter Hauptbasis, eigene freie 0.1.29.x-Version, Branch/Draft/ZIP/SHA/Android-Abnahme; keine Version vorsorglich reservieren oder leeren Implementierungs-PR behaupten.

[Vorheriger detaillierter Plan](AUTOPLAY_FOLGEPLAN_NACH_02919_DE.md) bleibt fachlich gültig. Erneut geprüft: PR #84 ist offen/Draft, Head `b178721b5d35145f9b562f0030da3ec81b550ca2`, Basis .11 `79cb6ad`. Seine OSD-Ownership, Kodi-21.2-Capabilities und gefilterte Aktionsregistrierung sind mögliche selektive Vorarbeiten. Er enthält **keine Ended/Stopped-Zustandsmaschine** und darf heutige .19-Stop-/Next-/EPG-/Owner-Korrekturen nicht durch einen alten Gesamtbranch ersetzen.

## Konkrete Modulgrenzen für den separaten Branch

| Baustein | Wiederverwendung / notwendige Ergänzung |
|---|---|
| `media_sequence.py` aus .19 | Getestete lokale Folge-/Staffelordnung, Lücken, Serienende, Portal-/Serienprüfung, keine Specials/ambigen Ziele. Bytegleich in .20. |
| `media_intent.py` / Resolver | Geprüfte neue Nonce pro Folge. Kein Playerstart aus Callback, kein fremder Resolver/Portal. Neuer Übergabeauftrag erst nach gültigem Endevent und Cancel-Prüfung. |
| Kodi-Player-Beobachter | Ein dauerhafter, auf Kodi 21.2 geprüfter Observer für AV-Start/Ended/Stopped/Error. Beim bestätigten eigenen AV-Start Kontext/Nonce merken; am Ende sind InfoTag/URL möglicherweise schon leer. `isPlayingVideo()==False` allein niemals als Endevent werten. |
| Neuer Autoplay-Koordinator | IDLE → STARTING → PLAYING → ENDED_PENDING → STARTING(next) / CANCELLED / FINISHED. Begrenzte Eventqueue, Owner verarbeitet, Nonce+Generation deduplizieren. Keine GUI-/HTTP-Arbeit im Callback. |
| Stop/Back/Shutdown | Vor jedem eigenen Stop Cancel-Generation erhöhen und vorgemerkten Next verwerfen. Auch Stop nach Endevent, aber vor/neben Resolver, gewinnt. Stopped/Error/Kodi-Ende erzeugen keine Next-Anforderung. Neue/fremde Session entwertet alten Kontext. |
| OSD aus #84 | Nur kompatible Ownership/API-/Fokus-/Aktionsstücke nach Port auf neue Basis. Neue Option „Nächste Folge automatisch“ nur für eigene Episodensitzung; Aus schließt auch vorgemerkten Übergang aus. Back bei sichtbarer Leiste blendet nur aus, expliziter Exit beendet die Kette. |
| Fortschritt | Letzten gültigen Resume/Seen-Checkpoint vor Übergabe sichern. Neuer OSD-Titel/Staffel/Folge/Poster gehören zur neuen Nonce. Vorhandene manuelle Next-Aktion bleibt explizit und funktionsfähig. |

## Abnahmevertrag vor einem eigenen Android-Testpaket

- Natürliches Ende startet S1E1→S1E2→S1E3 und nächste gültige Staffel ohne Bestätigung; bewusster Start mitten in Staffel setzt relativ dazu fort.
- Jede eigene Endevent-ID höchstens einmal; doppelte/verspätete Callbacks, Sessionwechsel, leerer InfoTag und Starts während laufender Übergabe testen.
- Stop/Back mit Beendigungsabsicht vor Endevent, in Queue und vor Resolverfreigabe: **null neue Starts**, kein Hintergrundton. Fehler, Shutdown, Film, Live und Fremdplayer ebenfalls null Autoplay.
- Fehlende/ungültige Quelle und Offline kontrolliert beenden, keine Endlosschleife. Serienende kein Wrap-around. Keine neuen Einstellungen ungefragt migrieren.
- Eigene Tests für OSD-Schalter/IR/Ownership sowie Gesamtregression, danach echter Android-Test mit kurzen erlaubten Episoden, Staffelgrenze und Stop im Übergang. Bis dahin NOT_TESTED; keine automatische Integration in .20/main.
