# XCMate 0.1.29.16 – isolierter EPG-Testkandidat

Basis: `main` / `d7d6937ec592795219e9f91e5e4b265e7799c121`, Add-on 0.1.29.13.
Branch: `fix/xcmate-02916-epg-handoff`. Kein Merge, Release oder OTA-Update.

## P0 #89: Player-Übergabe

Vorher rief `_actions()` innerhalb des nativen OK-Callbacks unmittelbar `Window.close()` und `PlayMedia(...)` auf. Kodi 21.2 `xbmc/interfaces/legacy/Window.cpp`, `Window::close()` sendet `TMSG_GUI_PREVIOUS_WINDOW`; erst `Window::dispose()` entfernt Fenster/Control-Referenzen. `close()` bedeutet daher nicht, dass der Python-Callback, Owner-Pump oder der äußere Navigation-Lock beendet sind. Die bisherige Reihenfolge ist ein nachgewiesener Lifecycle-Konflikt; der genaue native Absturz auf dem RK3528 ist ohne Tombstone/logcat noch nicht bewiesen.

Jetzt erfasst der Callback nur eine einmalige Senderanforderung und sperrt Folgeeingaben. Der Owner schließt nach Rückkehr aus dem Callback; `open_grid()` gibt ausschließlich die abgetrennte Anforderung zurück und löst eigene Window-/Future-Callback-Referenzen. Erst **nach** Rückkehr aus `run()` und Freigabe des Navigation-Locks führt `after_close` die Übergabe aus. Das eigene Fenster muss inaktiv und der modale Dialog beendet sein (maximal zwei Sekunden, abbrechbar; kein Zwangsschließen fremder Fenster). Aktiver Account und Sender werden erneut im lokalen Reader geprüft. Ein zwischenzeitlich anderer Player, Audio oder Live-Session-Nonce verhindert die Übergabe. Es gibt keinen `Player.stop`, direkten Stream-Start, neuen Autoplaypfad oder zweiten Versuch.

Die Übergabe nutzt exakt die funktionierende Live-TV-URL aus `add_index_item`: Xtream `play_live`, M3U/STB `source_play`. Kodi ruft den bestehenden Resolver mit gültigem Plugin-Handle auf. Decoder-/Streamfehler bleiben beim vorhandenen Resolver. Bei abgebrochener Übergabe erscheint eine Meldung, das bisher unterlegte XCMate-Menü bleibt erhalten. Nach Ende/Fehlschlag wird kein Guide automatisch wieder gestartet. Persistente Startgruppe und Startsender werden nicht geändert.

## #93: Diagnose und separat reproduzierter Navigationsfehler

Im großen EPG markierten Sender wählen → OK (oder Kontextmenü) → **Senderdiagnose: Langzeit-EPG**. Die Diagnose arbeitet auf dem Worker, die Textanzeige auf dem Fenster-Owner. Sie zeigt:

- lokale Sender-ID, Provider-EPG-ID, manuelle Zuordnung oder automatische Kandidaten und Alias → kanonische CID;
- tatsächlich verwendetes Viewport-Mapping und CID; unabhängig davon den gesamten gespeicherten Horizont jedes Zuordnungskandidaten;
- ersten/letzten Programmeintrag, Anzahl, min(start)/max(stop) je Quelle, Quellenname, Status und letzten Erfolg;
- Programme je lokalem Tag und bis zu drei echte Einträge nach 14:00 am gewählten Cursortag;
- Cursor, Drei-Stunden-Ursprung, Fokus-ID, Loading-Flag und Anzahl nativer Zellen;
- den **separaten lokalen SHORT_EPG-Cache**, ausdrücklich ohne Gleichsetzung seiner Reichweite mit `guide_v1.sqlite`.

Der bestehende `guide_store.horizon()` verwendet einen schreibenden Schema-Connector. Deshalb benutzt die neue Diagnose äquivalente SELECT-Abfragen über `mode=ro`, 50 ms Lockwartezeit und 400 ms Query-Deadline. Kein Anlegen einer fehlenden DB, Import, Mapping-Write, Reparatur, HTTP oder Cache-Reset. BUSY/Queryfehler bedeuten unbekannte Coverage, nicht fehlende Programme. Quellenindizes beziehen sich wie im bestehenden Guide auf die aktuelle Quellenkonfiguration. Die Anzeige bleibt lokal; Sender-/Programmeinträge enthalten persönliche Informationen und gehören nicht ungeprüft in öffentliche Issues.

**Separat behobener, mit echter SQLite reproduzierter Fehler:** Ein langer Eintrag 12–15 Uhr überlappt Einträge 13–13:30 und 14–14:30. Die bisherige Auswahl blieb beim ersten langen Eintrag; Rechts wählte wiederholt dessen Array-Nachfolger mit Start 13 Uhr, obwohl der Cursor schon dort stand. Der Regressionstest scheiterte vor dem Fix mit einem nicht fortschreitenden Cursor. Die neue Auswahl bevorzugt den zuletzt begonnenen laufenden Eintrag; Richtungstasten wählen nur Startzeiten strikt in ihrer Bewegungsrichtung, sonst bewegen sie die Zeit um 30 Minuten. Leere Intervalle werden weiter durchlaufen. Keine Änderung am Import oder an der Dublettenbereinigung.

Dies ist ein belegter Fehler dieser Datenkonstellation, **noch kein Nachweis**, dass genau diese Überlappung beim Android-Sender die Sperre um 14 Uhr ausgelöst hat. Die neue Diagnose ermöglicht diesen Abgleich. Quellenweite READY/9.967 bzw. 33.573 Programme allein beweisen keine Zuordnung des markierten Senders. Die alte Einzelvorschau bleibt ein Kurzzeitcache-Blick.

## Abgrenzung zu weiteren vollständig gelesenen Issues

| Issue | Berücksichtigt / weiterer separater Auftrag |
|---|---|
| #88 | Startgruppe/Startsender am ursprünglichen Ordinal, Gruppenebene und fehlende Logos: unverändert offen, kein Umbau in diesem P0-Fix. |
| #90 | 512-MiB-Budget, 4096-MiB-Clamp und erschöpfte SPACE_FULL-Jobs: separater Artwork-Fix, keine Budget-/Profilmigration hier. |
| #91 | SQLite-/Queue-Politik, Retry und Ressourcenlimits: keine Sperren/WAL/Integritätsprüfungen abgeschaltet. Diagnose nutzt eigenen begrenzten Read-only-Zugriff. Bestehendes Verhalten bei Fehlern eines normalen Viewport-Loads bleibt ein separater Prüfpunkt. |
| #92 | Fokus-Text und nicht erreichbarer Header: weiterhin offen. Diagnose ist über das erreichbare OK-/Kontextmenü zugänglich. Tagesbuttons sind auf dem Host getestet, ihre IR-Erreichbarkeit ist nicht mitbehoben. |
| #94 | Linke Live-TV-Icon-Rail: eigenes Feature, LiveNavigator unverändert. |
| #95 | Vertikales Zukunfts-EPG für markierten Mini-EPG-Sender: eigenes Feature, kein Autotune hinzugefügt. |

Portale, Sendergruppen, Favoriten, EPG-Zuordnungen, Resume, Artwork-Dateien und funktionierende Live-TV-/Fernbedienungspfade werden weder zurückgesetzt noch migriert. Bestehende ZIPs und produktiver Updateindex bleiben unverändert.

## Validierung

Vollständige Ausgabe und maschinenlesbarer Bericht: `TESTLOG_02916.txt`, `TESTERGEBNISSE_02916.json` nach abgeschlossenem Testlauf. Die Tests laufen auf Python 3.12 mit Kodi-Control-/Callback-Modell und echter SQLite, nicht auf Android. Alle ausgelieferten Python-Dateien werden zusätzlich mit der Python-3.11-Grammatik geprüft; kein behaupteter Python-3.11-Runtime-Lauf.

Neue Regressionen prüfen Callback ohne Play/Close, volle Owner-Schleife, Lock-Freigabe vor Übergabe, wiederholtes OK/Back, einmalige Ausführung, deaktivierten/falschen Account, fehlenden Sender, fremden Video-/Audioplayer und geänderte Session. Die Diagnose prüft DB-Bytegleichheit, Aliasauflösung, manuelles fehlendes Mapping, fehlende DB, echten exklusiven SQLite-Lock und getrennten Kurzcache. Navigation prüft echte acht Tage, Lücken, Überlappungen, Vor-/Zurück über Drei-Stunden-Grenzen und Mitternacht. Bestehende Tests decken 2.501 Sender, dichte Raster, EPG-Deduplikation, DST-Kalendertag mit 25 Stunden, Media/Resume und Live-Navigation weiter ab.

ZIP-Verifikation: CRC, sichere Pfade, keine Profile/Logs/DBs/Secrets, keine Doppeleinträge, jede Datei bytegleich zum Quellbaum, unabhängiger reproduzierbarer ZIP-Neubau, SHA256. Der Builder läuft ausschließlich in einer Wegwerfkopie. Nur ZIP und Prüfsumme des neuen Kandidaten werden übernommen; keine `addons.xml`-/Website-/Release-Änderung.
