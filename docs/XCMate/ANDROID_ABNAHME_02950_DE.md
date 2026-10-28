# XCMate .50 – Android-Abnahme Widgetverwaltung / BINGIE Home

Stand: 28.10.2026 (Europe/Berlin). **Alle neuen Tests NOT_TESTED.** Historischer .49-Workflow laut #252 auf Box A: **FAIL**. Keine Umdeutung der Hosttests in eine Gerätefreigabe.

## Vorher / Installation

- Box A nicht zurücksetzen, nichts deinstallieren. `.50` nur als vom Benutzer bewusst installiertes kumulatives ZIP-Update über `.49`. SHA256 vorher prüfen. Das Entwicklungs-ZIP ist vor Merge kein reguläres Repository-Update.
- Gerät, Kodi-Version, Skin-ID/Version und Skinshortcuts-Version notieren. Zielreferenz: Titan BINGIE MOD **2.2.3**, Skinshortcuts **2.1.0**. `.42`-Kompatmodus, Startgruppe/Startsender und Artworkmodus erhalten.
- Vorhandene Home-Reihen und ihre Positionen notieren. Portale, Favoriten, manuelle EPG-Mappings, Film-/Seriencover, Resume und Autoplay unverändert lassen. Vor Profil-/Skinanpassung keine laufende Wiedergabe und kein offener nativer BINGIE-Editor/Build. Keinen Stream ungefragt beenden lassen.
- **Skinpatch nur nach gesonderter Freigabe:** vier vollständige Unterschiede, Vorher-/Nachher-Hashes und Rückrollweg unter `integrations/titan-bingie-mod/0.1.29.50/`. Nicht das öffentliche Prüfarchiv in die Geräte-Skininstallation entpacken. Maßgeblich sind die lokal vorbereiteten und verifizierten privaten Sicherungen.

## Ablauf

| Test | Handlung / tatsächliche Erwartung | Status |
|---|---|---|
| W50-01 | XCMate → Einstellungen → Aussehen und Darstellung → Widgets: **Live-TV, Filme, Serien**, direkt als drei Aktionen sichtbar. Keine Sendergruppen als Einstellungsziel. Alte Zusatzfunktionen liegen im Kontextmenü. | NOT_TESTED |
| W50-02 | Filme/Serien wählen: bestehendes korrektes Binding wird mit Position gemeldet und samt Titel/Reload-Hook beibehalten. Für eine neue bewusste Verknüpfung nur freie Position wählen. Vorschau/SHA/Backup schließen und **Abbrechen**: keine Profiländerung. | NOT_TESTED |
| W50-03 | Eine freie/ausdrücklich gewählte Position bestätigen: Backup und Rücksicherungsprüfung vor dem Speichern; nur diese Position verändert. Nativer BINGIE-Neuaufbau wird angefordert. Erst echte Home-Reihe mit richtigen Filmen/Serien ist PASS, nicht bloß „Profil gespeichert“. | NOT_TESTED |
| W50-04 | Unter Widgets → Kontextmenü → **BINGIE-Home-Layout prüfen/vorbereiten**. Vier Prüfsummen/Dateien sichtbar; private Originalsicherung vorhanden. Abbrechen lässt alle Skin-Dateien intakt. Bei unbekannten Hashes BLOCKED notieren, keinen Reset/Workaround ausführen. | NOT_TESTED |
| W50-05 | Erst nach ausdrücklicher Freigabe dieses konkreten Vier-Dateien-Patches: bestätigen. Native BINGIE-Regeneration beendet sich erfolgreich. Keine Fremd-Skindatei, kein Profilreset. Andernfalls FAIL/BLOCKED und vorhandene Sicherungen erhalten. | NOT_TESTED |
| W50-06 | Live-TV erneut auswählen und freie Position bzw. ausdrücklich angebotene eigene alte Live-Gruppenverknüpfung wählen. Speichervorschau bestätigen. Home zeigt die **konfigurierte Startgruppe**, keine Gruppenkacheln, keinen falschen Kontoinhalt. | NOT_TESTED |
| W50-07 | Mindestens **88 Sender** bis zum letzten horizontal fokussieren. Kleine Logos. Oberhalb großer Hero mit passendem echten Sendungsbild oder neutralem Platzhalter, Titel, Sender, Beschreibung, Jetzt/Nächste und Fortschritt. Jeder Fokuswechsel aktualisiert die Anzeige ohne Wiedergabestart. Bild-, Zeit- und Senderzuordnung vergleichen. | NOT_TESTED |
| W50-08 | OK auf drei verschiedenen Sendern startet genau den fokussierten Sender. Back aus Overlay schließt nur die Ebene; Back aus reinem eigenen Live-Vollbild stellt eine bedienbare Ansicht her. Erst nach einem PASS weitere fünf Zyklen. Bei Hänger keine Stop-/Back-Flut. | NOT_TESTED |
| W50-09 | Kodi regulär beenden/neustarten. Alle drei Bindings bleiben erhalten. Live weiterhin schmale Startgruppenleiste/Hero. Profile, Startgruppe, `.42`-Einstellung und Artworkmodus unverändert. | NOT_TESTED |
| W50-10 | Bestehende Film-/Serienreihen: Cover, Fokus, Navigation, Klickziel, Back, Resume und Staffel-Autoplay unverändert. Automatische Widget-Aktualisierung bei einer regulären Katalogänderung prüfen; ohne echten neuen Bestand diesen Teil NOT_TESTED lassen. | NOT_TESTED |
| W50-11 | Native vertikale Navigation zwischen Live-Leiste und Film-/Serienreihen, Menü links/Back sowie Übergang in/aus dem Hero: keine Geistertexte oder mehrfachen Fokusrahmen. Aktuelles ProgrammeImage bleibt unabhängig vom Senderlogo. | NOT_TESTED |
| W50-12 | Rückrollen bei Bedarf bewusst prüfen: Kontextmenü → Verifizierte Widget-Sicherung zurückrollen, passenden angewandten Plan wählen. Nur wenn aktuelle Hashes noch passen wird exakt wiederhergestellt. Spätere Fremdänderungen müssen sperren. Profil und Skin haben getrennte Sicherungen; keine Benutzerdateien für einen Test beschädigen. | NOT_TESTED |

## Native Ausweichmöglichkeit bei geschütztem Profil

Wenn der direkte Writer `NO_SAVED_BINGIE_PROFILE`, `HOME_ID_UNVERIFIED` oder `SINGLE_WIDGET_HOME` meldet, wird nichts geraten/umgeschaltet. Auf Wunsch **Native BINGIE-Einrichtung öffnen** bestätigen. Nach separat freigegebenem Skinpatch: Home / gewünschte Widgetposition → Widgetauswahl → **XCMate · Live-TV**, **XCMate · Filme**, **XCMate · Serien** direkt wählen und nativ speichern. Keinen Portalgruppenordner als Ersatz auswählen. Einzelwidgetmodus nur bewusst nativ ändern, wenn mehrere Reihen gewünscht sind. Eigene direkte XCMate-Links pinnen das gewählte Portal; die nativen allgemeinen Kandidaten verwenden den aktuell aktiven Account.

Bei fehlender Startgruppe/fehlenden lokalen Daten kein PASS behaupten. `HOME50 source=LIVE_START_GROUP code=START_GROUP_MISSING/START_GROUP_UNAVAILABLE` ist eine ehrliche Sperre; die vorhandene Startgruppe bewusst prüfen, keinen Import/Reset erzwingen. Ein verifiziert gespeicherter Link ist noch kein Decodier-/Home-/Neustartnachweis.

## Protokoll

Für jede Zeile PASS/FAIL/NOT_TESTED, Zeitpunkt und Beobachtung notieren. Bei einer tatsächlichen Sperre BLOCKED samt Code/Voraussetzung verwenden. Lokale Marker `WIDGET50` und `HOME50` enthalten nur Phase/Art/Position/Zeilenanzahl. Kodi-Rohlogs privat halten; keine Provider-URLs, Zugangsdaten oder Profil-/SMB-Details nach GitHub kopieren. Keine neuen Download-/Aufnahme-/USB-/SMB-/Löschtests in dieser Runde.
