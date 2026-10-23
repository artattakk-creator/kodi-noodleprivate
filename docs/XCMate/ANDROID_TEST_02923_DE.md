# Android-Abnahme – XCMate 0.1.29.23

Testkandidat des Draft-Branches, kein produktives Update. Direkt über bestehende .22 installieren, nicht deinstallieren und keine Daten/Thumbnail-Caches löschen. ZIP-Prüfsumme mit beiliegender SHA256 vergleichen. Ziel: Android 13 RK3528 ARM32 / Kodi 21.2 / BINGIE MOD / IR. Jede Zeile als PASS / FAIL / NOT_TESTED dokumentieren. Hier bisher alles NOT_TESTED.

- [ ] A01 Version .23, Portale, Gruppen, Favoriten, Resume, Gesehen-Status und bisherige Cover erhalten.
- [ ] I01 Original-Icon in Kodi-Add-on-Kachel und Add-on-Info sichtbar (genauen Ort und fehlendes/altes Bild unterscheiden).
- [ ] I02 XCMate-Home-Starteintrag verwendet dasselbe Original; Einstellungen → Über XCMate → Original-Icon prüfen: ORIGINAL und CONTENT_ADDRESSED. Bei anderer Anzeige nur die sicheren Statuscodes melden.
- [ ] I03 Kodi vollständig neu starten: Icon an allen drei Orten weiterhin sichtbar. Keine globale Cachebereinigung durchführen.
- [ ] P01 Disney-Filme → Aladdin (1992): Detail → Posterstatus/erneut versuchen. Quelldatenfeld, Kandidatenzahl, Status, Versuche und Zeitwerte melden; keine Provideradresse oder Tokens posten.
- [ ] P02 Einzelnen Poster-Retry wählen, Status nach Verarbeitung erneut ansehen. Bei zweitem sofortigen Versuch greift Wiederholsperre; Rate-Limits bleiben bis zur Freigabe gesperrt.
- [ ] P03 Wenn alternative Quelle vorhanden: Bild gehört weiterhin exakt Aladdin (1992), nicht einer anderen Verfilmung. Fehlende oder ungültige Providerbilder korrekt melden, kein Erfolg ohne sichtbares richtiges Cover.
- [ ] P04 Über 240, möglichst 500 unterschiedliche Titel durchsuchen, Nachladen und Zurückscrollen prüfen; bereits sichtbare Cover bleiben erhalten. Nach Kodi-Neustart heruntergeladene Cover erneut kontrollieren.
- [ ] E01–E10 Die zehn bestandenen EPG-Navigationswege aus Test 50 erneut stichprobenweise prüfen: Startgruppe/-sender, Originalreihenfolge, Links-Gruppenwahl, Zurück, sechs Kopfbuttons, lesbarer Fokus, Zeitnavigation/Refresh.
- [ ] R01 Jetzt Sender ansehen aus großem EPG ohne Absturz; Live-Overlay, Senderwechsel und Stop ohne unerwarteten Neustart.
- [ ] R02 Normales Episoden-Autoplay innerhalb einer Staffel und manuelles Next; Stop/Back starten keine neue Folge. Resume/Gesehen und Detailnavigation bleiben bedienbar.

B02 automatischer Staffelwechsel ist auf Nutzerwunsch aus dieser aktiven Teststrecke ausgenommen; #85 bleibt offen. Theme-Wechsel ist erst im eigenständigen Theme-Kandidaten prüfbar. Sichtbare Icon-/Aladdin-Reparatur erst nach echter Android-Bestätigung abnehmen.
