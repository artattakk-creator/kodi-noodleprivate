# .28-C – kumulativer Android-P0-Testkandidat

Enthält .28-A (#132) und .28-B: Menü, sichtbarer Aktionen-Button,
sicherer Speicherabschluss und getrennte Aufnahme-/Downloaddiagnose.
Zusätzlich gezielter Poster-Retry (#111). Keine vollständige Releasefreigabe.
Keine automatische Veröffentlichung, kein Merge, keine Änderung der Keymaps.

## Installation und Reihenfolge

Nur das .28-C-ZIP dieses Branches verwenden. A/B sind isolierte Diagnosepakete
mit derselben Addon-Version; nicht anhand der Versionsanzeige verwechseln.
SHA256 mit der beigefügten Datei vergleichen. Kodi: Addons → Aus ZIP-Datei
installieren, bestehendes XCMate aktualisieren. Nicht deinstallieren oder Daten
löschen. .27 bleibt veröffentlichte Rückfallbasis; ihr Nutzerergebnis bleibt
unverändert **13 PASS / 15 FAIL / 0 NOT_TESTED**.

Zuerst die Schritte in ANDROID_TEST_02928_A_DE.md (Menü) ausführen, dann
ANDROID_TEST_02928_B_DE.md (Zielprobe, Aufnahme, Downloads). Den Downloadtest
auch bei HLS/DASH-Ablehnung der Live-Aufnahme durchführen: unterstützte direkte
MP4-/MKV-Film-/Folgendateien verwenden. Genau einen Film und eine konkrete Folge
testen. Ziel bleibt der gemeinsame Aufnahmeordner; Änderung nur nach Zustimmung.

## Ergebnisvorlage für diesen neuen Kandidaten

| ID | Prüfung | Ergebnis |
| --- | --- | --- |
| M01 | Film-/Seriendetails: Links öffnet sichtbares Menü mit Fokus | NOT_TESTED |
| M02 | Sichtbarer Aktionen-Button funktioniert auch ohne Links-Event | NOT_TESTED |
| M03 | Rechts/Zurück schließt nur Menü, gleiche Detail-/Aktionsposition | NOT_TESTED |
| P01 | Zielprobe meldet Backend oder präzisen Aufruf/errno, keine Zugangsdaten | NOT_TESTED |
| P02 | Geprüfte dauerhafte Alternative nur nach Zustimmung übernehmen | NOT_TESTED |
| B03 | Direkter TS: aktiv erst mit positiven geschriebenen Bytes | NOT_TESTED |
| B04 | Mindestens zwei Minuten aufnehmen, anschließend manuell beenden | NOT_TESTED |
| B05 | Sicher finalisierte Aufnahme lokal wiedergeben | NOT_TESTED |
| B06 | Kodi neu starten, Aufnahme offline wiedergeben | NOT_TESTED |
| B07 | Abbruch/Fehler erhält eigene Teildatei und alle vorhandenen Aufnahmen | NOT_TESTED |
| D01 | Unterstützten Film vollständig laden, Status/Größe/Fortschritt stimmen | NOT_TESTED |
| D02 | Einzelne ausgewählte Episode korrekt als Download speichern | NOT_TESTED |
| D03 | Pausieren und Fortsetzen mit vorhandenem Dateianteil | NOT_TESTED |
| D04 | Abbrechen, gezieltes Retry, keine automatischen Endlosschleifen | NOT_TESTED |
| D05 | Fertige Film-/Folgendateien lokal und nach Neustart offline abspielen | NOT_TESTED |
| D06 | HLS-Live-Aufnahme abgelehnt, direkter Filmdownload trotzdem möglich | NOT_TESTED |
| R01 | Fehlendes Poster gezielt erneut laden, sichtbare Reihe aktualisiert sich | NOT_TESTED |
| R02 | Fehlgeschlagene Hauptadresse: belegte Alternative desselben Eintrags | NOT_TESTED |
| R03 | Funktionierendes Poster und andere Cachebilder bleiben unverändert | NOT_TESTED |
| R04 | Ohne Alternative: ehrlicher Status, kein fremdes Bild bei gleichem Titel | NOT_TESTED |
| R05 | Nach Neustart erfolgreich geladenes Ersatzbild weiterhin lokal | NOT_TESTED |
| A01–A08 | Bestandene .27-Suche/Live-Starts erneut auf Regression prüfen | NOT_TESTED |
| G01 | Fernbedienung, EPG, Resume, Staffelautoplay und Originalicon erhalten | NOT_TESTED |

Bei Fehlern: ID, PASS/FAIL, Aktion und angezeigten technischen Code melden.
Nur anonymisierte DETAIL_MENU/CAPTURE/DOWNLOAD-Marker weitergeben; private
Provider-URLs, Titel, Tokens und vollständige persönliche Dateipfade entfernen.
Ein blockierter neuer Folgetest bleibt NOT_TESTED mit Blockierungsgrund. Die
historischen .27-FAIL-Werte werden dadurch nicht nachträglich umklassifiziert.

## Poster-Verhalten und Grenzen

Der manuelle Retry nutzt die vorhandene begrenzte Artwork-Queue. Nach einem
fehlgeschlagenen Hauptbild kann eine bereits in genau diesem Datensatz vorhandene
Provider-Bildadresse priorisiert werden. Es wird nur das ausgewählte Poster
eingereiht, nicht zusätzlich Fanart oder eine ganze Kategorie. Erfolgreiche lokale
Bilder, andere READY-Jobs, laufende Worker-Leases und Server-Cooldowns bleiben
geschützt. Eine alte READY-Zeile ohne vorhandene gültige Datei blockiert den Retry
nicht mehr. Nach erfolgreichem Download überlebt das Ersatzbild den Neustart.

Kein Titelraten und keine externe TMDB-Titelsuche. Fehlt eine weitere belegte
Adresse, zeigt die Oberfläche dies ausdrücklich; sie kann kein Providerbild
erfinden. Weitere Bildquellen benötigen eine belastbare ID-Zuordnung.

## Offene Folgearbeiten – getrennte Draft-PRs

Diese P0/P1-Testlieferung erledigt die folgenden Aufgaben noch nicht:

| Issue | Nächste eigenständige Umsetzung und Freigabeprüfung |
| --- | --- |
| #127 | Neue Suchdarstellung mit belegten Logos/Postern/EPG/Metadaten; A01–A08 müssen PASS bleiben. Pflicht vor vollständigem RC. |
| #120 | Skin-Live-Einstieg mit gespeichertem Startsender; Player-/Owner-Rückkehr separat abnehmen. |
| #122 | Original-Space-Splash lokal für Lightweight; Originalicon und Premium-WIP schützen. |
| #123 | Fernbedienbare EPG-Sendungsdetails und exakter Positionsrücksprung. |
| #98 | Quellenauswahl je Sender mit echter Vorschau und ausdrücklichem Speichern. |
| #43 | Vollständiger Erststart-Wizard für Xtream/M3U/Stalker, Checkbox-Gruppen, EPG/Matching, progressive Cover/Metadaten, Fortschritt und Startsender/-gruppe. Pflicht vor vollständigem RC; kompletter Android-Neuinstallationstest erforderlich. |
| #115 | Premium-Fokus/OK separat; Lightweight und vorhandene Originalbilder erhalten. |

Nach P0-Geräteabnahme jede dieser Arbeiten separat entwickeln und testen. Dieser
Kandidat darf nicht als vollständige Erledigung der UI-/EPG-/Setup-Roadmap gelten.
