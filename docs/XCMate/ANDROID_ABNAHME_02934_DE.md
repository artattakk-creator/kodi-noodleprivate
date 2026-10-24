# XCMate 0.1.29.34 – vier kurze Android-Gates

24.10.2026. Kodi 21.2 Omega · Android TV 13 · RK3528 ARM32 · Titan BINGIE MOD.
Alle neuen Tests **NOT_TESTED**. Host-/CI-PASS ist keine Android-Abnahme. .33 bleibt historisch 11 PASS / 3 FAIL / 1 NOT_TESTED; bestehende Langzeit-PASS bleiben erhalten.

Test-ZIP über der vorhandenen .33 installieren, keine Deinstallation, kein Profil-/Cache-Reset. In Add-on-Information 0.1.29.34 prüfen. Bestehende Profile, Cover, Portale und EPG-Zuordnungen behalten. Kein automatisches Repository-Update für diesen Draft.

| ID | Ausführen | PASS nur wenn | Status |
| --- | --- | --- | --- |
| G1 | Im großen EPG einen Sender markieren, OK → „Jetzt Sender ansehen“. Stop/Back, EPG erneut öffnen und einen anderen Sender starten; insgesamt möglichst vier bewusste Starts. | Jeder Klick startet genau einen gültigen Sender über den vorhandenen Live-Resolver. Kein Start im Callback, kein ungefragter Home-Wechsel, keine SKIPPED-Kette; normales Live-TV weiterhin bedienbar. | NOT_TESTED |
| G2 | Aus dem großen EPG Suche öffnen, Keyboard bestätigen; danach Back, wiederholen. | Natives Suchfenster sofort nach kontrollierter Guide-Freigabe sichtbar. Kein selbst erzeugtes Busy 10138, kein RELEASE_TIMEOUT. Back stellt Gruppe, Zeitausschnitt und Fokus wieder her. | NOT_TESTED |
| G3 | Einen gerade im EPG sichtbaren Sendungstitel suchen. Bis Scanabschluss warten; `+` bedeutet Teilstand. Treffer mit Down/OK bedienen, danach korrekt zurückkehren. | Tatsächlicher **Programmtitel** erscheint beim passenden Sender und ist vor Back bedienbar; Sendernamen-Matches allein gelten nicht als Programmtitel-PASS. Keine verspäteten Ghost-Treffer, kein Doppelstart. | NOT_TESTED |
| G4 | Bestehende Film- und Seriensuche mit bekannten Covern öffnen. Tabs, Down/Up/OK, Details und Back prüfen; kurze Serienwiedergabe/Autoplay wie bisher. | Poster/Metadaten, Fernbedienung, Fokus, Details/Back und Autoplay bleiben funktionsfähig. Originalicon, Space Premium und Profildaten erhalten. | NOT_TESTED |

Bei Blocker abbrechen und weitere abhängige Gates NOT_TESTED lassen. Test-ID, Uhrzeit, Skin, sichtbaren Bildschirm und Fokus nennen; nur redigierte .34-Phasen teilen.

Erwartete Suche: `INTENT → GUIDE_CLOSED → WAIT_RELEASE → RELEASE_READY → ASYNC_READY → SEARCH_OPEN → SEARCH_GUI_READY`; ASYNC_READY bedeutet hier freigegebener Owner, ein zusätzlicher RunPlugin-Aufruf ist im normalen Guide-Dialogweg nicht erforderlich. Back: `SEARCH_CLOSED → RELEASE_READY → GUIDE_RESTORE`.

Erwarteter Guide-Start: `QUEUED → RESOLVER_REQUEST → DISPATCHED`. Zufällige `request`, `owner`, `origin_lease`/`lease` und `ROUTE_STATE ENTRY/RETURN` helfen, parallele Aufrufe zu unterscheiden; keine Provideradressen oder Suchtexte protokollieren. Eine leere aktuelle Lease beim Resolver ist korrekt: der Guide hat seine Lease bereits freigegeben.

Echte fremde Dialoge, Kodi-Ende oder veränderte Player-Sessions müssen weiterhin blockieren. Keine Dialoge pauschal schließen. Bei SKIPPED den festen `reason` mitsenden. Private Rohlogs niemals öffentlich hochladen.

Poster-Retry #111 wird separat behandelt und ist kein neuer PASS dieses ZIPs. EPG-Zuweisung #98 folgt nach G1–G3-Abnahme. Downloads/Aufnahmen bleiben am Roadmap-Ende. Kein neuer Vierstundenlauf, Merge, Release oder Issue-Schluss ohne Freigabe.
