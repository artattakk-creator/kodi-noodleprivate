# XCMate 0.1.29.33 – kurze gestufte Android-Abnahme

24.10.2026 · Kodi 21.2 / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD. **Alle neuen Gates NOT_TESTED.** .32 bleibt historisch 7 PASS / 10 FAIL. Host-/CI-PASS ist keine Android-Abnahme.

ZIP und SHA256 aus dem Draft beziehen. In Kodi über bestehender .32 installieren; keine Deinstallation, kein Downgrade, kein Profil-/Cache-Reset. Unter Add-on-Information **0.1.29.33** prüfen. Einmal kurzer Bestandssmoke für Live-TV/EPG, Film-/Seriendetails, Autoplay, Originalicon/Bestandsdaten; kein Vierstundenlauf.

## Zuerst nur drei Funktionsgates

| ID | Ausführen | PASS nur wenn | Status |
| --- | --- | --- | --- |
| A1 | Im großen EPG einen aktuell laufenden Sendungstitel ablesen. Über Suche eingeben; bis Scanabschluss warten (`+` bedeutet Teilstand). | Native Suchansicht öffnet und bleibt sichtbar/bedienbar. Passender **Programmtitel** ist vor Back als Jetzt-Information am passenden Sender sichtbar. Bewusste Auswahl funktioniert. Sendernamen-Hits allein zählen nicht. | NOT_TESTED |
| A2 | Nach eindeutigem Sendernamen aus EPG und globalem Suchmenü suchen. Down in Liste, dann bewusst OK auf Sender. Stop und Back. | Treffer vor Back wählbar, genau ein Start auf bewusste Auswahl. Kein Busy-Abbruch/ungefragter Home-Wechsel, Rückkehr zum gemerkten Guide-Ausschnitt. | NOT_TESTED |
| A3 | In Film-/Serienansicht Suche öffnen; Keyboard bestätigen, zwischen Tabs/Ergebnissen wechseln, neue Suche/Abbruch, dann Back. | Gültiger sichtbarer Fokus, keine schwarze Kodi-Seite, kein Ghost-Start; Detail-/Guide-Kontext korrekt. | NOT_TESTED |

**Erst nach A1–A3 PASS** die folgenden Gestaltungsgates und gegebenenfalls die erweiterte NAVSEARCH-/REG-Prüfung aus dem .32-Testplan erneut durchführen. Bei einem Blocker weitere Gates NOT_TESTED mit Blocker-ID lassen; keine neue 17-fache FAIL-Matrix verlangen.

## Dann Gestaltung und lokale Bildaktualisierung

| ID | Ausführen | PASS nur wenn | Status |
| --- | --- | --- | --- |
| SEARCHUI-01 | Sender mit vorhandenem lokalem Logo suchen; Live-TV-Tab. | Logo links sichtbar, Sendername als eigene Titelzeile, Typ „Sender“ und verfügbare echte Jetzt-Sendung darunter. Ohne lokales Jetzt-EPG neutraler Hinweis. | NOT_TESTED |
| SEARCHUI-02 | Bekannten Film mit vorhandenem Cover suchen. | Poster, Filmtitel, Typ „Film“, vorhandenes Jahr/Genre sauber lesbar; OK öffnet richtige Details. | NOT_TESTED |
| SEARCHUI-03 | Bekannte Serie mit vorhandenem Cover suchen. | Serienposter/-titel und Typ „Serie“ sichtbar; optionale Metadaten korrekt. OK öffnet richtige Serie, Detail/Back/Autoplay bleibt erhalten. | NOT_TESTED |
| SEARCHUI-04 | Begriff mit Treffern in mehreren Rubriken, Tabs mit Links/Rechts und OK bestätigen, Down zur Liste, mehrere Zeilen durchgehen. | Inhaltstyp klar getrennt, sichtbarer Neonfokus auf genau einem bedienbaren Element, keine Bildcontrols im Fokuspfad. | NOT_TESTED |
| SEARCHUI-05 | Treffer ohne Cover/Logo ansehen; sofern ein Bild danach vom bestehenden Artwork-Worker fertig wird, denselben Treffer markiert lassen. | Lokales typgerechtes Ersatzbild, stabiler Aufbau. Nachgeladenes Bild erscheint ohne Fokus-/Positionssprung und ohne neu gestartete Suche. | NOT_TESTED |
| SEARCHUI-06 | Mehrfach schnell Tabs, Down/Up, Back und erneute Suche; BINGIE und wenn verfügbar Estuary kurz vergleichen. | Kein Freeze/Crash, keine leeren kaputten Zeilen, keine ungewollten Playerstarts. Originalgrafiken, Profile, Portale, EPG/Resume bleiben erhalten. | NOT_TESTED |

## Falls ein Gate scheitert

Test-ID, Uhrzeit, Skin/Auflösung, unmittelbar sichtbaren Bildschirm und Fokuszustand notieren. Nur redigierte `SEARCH_NAV`-/`SEARCH`-/`FOCUS`-/`SEARCH_EPG`-Phasen aus dem passenden .33-Zeitraum verwenden. Erwarteter Busy-Pfad: `GUIDE_CLOSED → BUSY_DEFERRED → ASYNC_QUEUED → ASYNC_READY → SEARCH_OPEN/SEARCH_GUI_READY`. Echte fremde Dialoge dürfen blockieren; sie werden nicht geschlossen. `BLOCK_CONTEXT/OWNER` verhindert veraltete/fremde Übergaben.

Keine privaten Rohlogs/Provider-/SMB-Adressen veröffentlichen. Downloads/Aufnahme bleiben zurückgestellt. **#98 MAP-01–11 ist erst nach Suchabnahme ein separater Entwicklungs- und Testzyklus**, noch nicht Bestandteil dieses Pakets. Kein Merge/Release/OTA/Issue-Schluss ohne Nutzerfreigabe.
