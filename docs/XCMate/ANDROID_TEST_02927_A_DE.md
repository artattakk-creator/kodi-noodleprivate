# .27-A – isolierter Such-Live-P0-Test (#125)

Nur Draft-Testpaket, kein vollständiger Releasekandidat. Basis .26-Nutzerabnahme:
15 PASS / 6 FAIL. Die genaue Quelle des zweiten nativen Kodi-Busy-Dialogs ist
weiter nicht bewiesen. Dieser Patch entfernt den verschachtelten Plugin-Resolver
aus dem Such-Live-Pfad. Der EPG-Pfad bleibt bytegleich zur bestandenen .26.

Nach Owner-Release prüft `search_live` tatsächlichen Fenster-/Busy-Zustand,
Player, LiveSession, aktuelles Portal und erlaubten Sender. Danach verwendet es
direkte `Player.play(url, ListItem)`-Übergabe mit Live-InfoTag wie Startsender.
Keine festen Sleeps, kein Dialog-Schließen, kein Container.Update/PlayMedia,
keine GUI-Aktionen aus einem Worker. Feste anonyme Gründe und Zufallskorrelation.

Android Kodi 21.2, Lightweight; je Zeile PASS/FAIL/NOT_TESTED erfassen:

- [ ] A01 Suche Upload mehrfach: Eingabe, Kategorien, Film-/Seriendetails, Back.
- [ ] A02 Live-Sendernamen suchen, Live-Treffer starten: Bild/Ton, kein Kodi-Ende.
- [ ] A03 EPG-Jetzt-Titel suchen und den richtigen Live-Sender starten.
- [ ] A04 OK zweimal schnell: nur ein Start; Stop und erneut suchen/starten.
- [ ] A05 Info-/Gruppen-/IR-Overlay und Zurück aus eigenem Live-TV.
- [ ] A06 Eigenen laufenden Live-Sender wechseln; fremde Wiedergabe nicht ersetzen.
- [ ] A07 Großes EPG Jetzt/Danach, Gruppen, Senderstart weiterhin PASS.
- [ ] A08 Film/Serie, Resume, Staffel-Autoplay und manueller Stop unverändert.

Alle neuen Geräteprüfungen zunächst NOT_TESTED. Bei Fehler nur bereinigte
SEARCH_LIVE-Stufen/Reason-Codes weitergeben, keine Stream-URLs oder Rohlogs.
Sofortaufnahme, Skinshortcut, Such-Neugestaltung und SetupWizard gehören zu
eigenen Schritten. Vollständiger Wizard #43 und Suchansicht #127 bleiben
verbindliche Gates des nächsten vollständigen Releasekandidaten.
