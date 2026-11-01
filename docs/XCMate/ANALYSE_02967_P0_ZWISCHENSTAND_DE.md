# XCMate .67 – P0-Zwischenstand, noch kein Installationskandidat

Basis main .66: a9a3476bc04c3624d1451dfe03899c2220138c08. Draft-PR #308, Issue #307 einschließlich Nachtrag. Keine Integration von #303/#306, kein Merge, Release, Gerätezugriff oder Datenreset.

## Reproduzierbare Codebefunde

Read-only Hostlauf https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41358036606: 653 Quelldateien und 2719 bisherige Testmethoden/Skip-Bedingungen fixiert.

1. Ein nachgewiesen vorhandenes, erfolgreich gelesenes primäres Programm geht sowohl im vollen Guide-Read als auch im Display-Read verloren, sobald optionale Metadata-Enrichment-Abfragen einen SQLite-Fehler auslösen. Beide Readers geben dann None zurück. Der neue Patch liest im vollen Pfad zuerst die Kerntexte aller Kanäle und begrenzt optionale Anreicherung; Fehler in dieser Zusatzstufe erhalten Kerntexte und geben feste, datensparsame Diagnose aus.
2. Eine nichtleere, aber abgelaufene SID-Aliasliste verdeckt ein aktuelles Programm unter der vorhandenen Provider-EPG-ID desselben Senders. Der Patch verwendet den aktuellen Provider-Eintrag nur, wenn kein aktueller Alias-Eintrag vorliegt. Explizite manuelle Zuordnungen und ein aktueller STREAM_ALIAS behalten Vorrang.
3. Ein extensionloser /live/-Pfad wird bisher ohne Manifestbeleg als HLS an InputStream Adaptive übergeben. Reproduziert, noch nicht repariert. Dies beweist nicht die konkrete Android-504-Ursache; übliche explizite .ts-URLs werden bereits als direct erkannt.
4. Player, URL-Builder, Live-Overlay, Live-Back .42 und Startpfade sind beim Vergleich .65→main .66 bytegleich. Ein direkter .66-Player-Code-Regressionsnachweis liegt damit nicht vor. Neue Hintergrundlast und Android-HTTP-/Formatprobes müssen separat untersucht werden.

## Stand und fehlende Abgabe

Sechs direkte EPG-Regressionen plus zwei Bestandsschutztests sind neu; alte Methoden bleiben unverändert. Die vollständige Regression ist vor fertiger Auslieferung Pflicht. Dieser Branch ist **noch keine fertige .67**: Paketversion bleibt vorerst .66, kein neues Installations-ZIP wird zur Abnahme angeboten.

Live-TV-504/Demux-Ursache, sichere Endpunkt-/Header-/MIME-Diagnostik, konsistenter Snapshot-Fallback bei primärem DB-Fehler, Rate-Limits für Provider-Kurz-EPG, Artworkpfad und TMDB-Attribution des Gesamtauftrags sind noch offen.

Die angehängte vollständige .67-Textdatei ist wegen der ausgefallenen Arbeitsumgebung nicht lesbar. Es wurde nach ihrer Gleichheit mit #307 und Nachtrag gefragt; zusätzliche/abweichende Anforderungen sind noch nicht bestätigt. Die sicheren gemeinsamen EPG-Reparaturen wurden begonnen, nicht der volle unbekannte Dateiinhalt als gelesen ausgegeben.

Alle Android-Fälle ANDROID_NOT_TESTED. Historischer Android-.66-FAIL aus #307 bleibt erhalten. Synthetische Befunde beweisen keine konkrete Provider-/Android-Ursache. Keine privaten Rohlogs, URLs, Zugangsdaten oder Token veröffentlicht.
