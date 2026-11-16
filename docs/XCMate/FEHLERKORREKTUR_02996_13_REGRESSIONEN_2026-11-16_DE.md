# XCMate .96 – abschließende Fehlerkorrektur

Arbeitsauftrag #469, bestehender Draft-PR #471 und Branch `fix/xcmate-02996-groups-artwork-mapping`. Dieser Bericht ergänzt den historischen roten Stand `98bc3b16`; dessen Fehlerlisten bleiben erhalten. Kein Merge und keine Veröffentlichung. Modell-B / #472 bleibt unberührt.

## Nachgewiesene Ursachen der 13 Fehlfälle

| Fehlfälle | Ursache | Korrektur und Nachweis |
|---|---|---|
| Render81 / NameError | Eine Quellenfreigabe war versehentlich in die numerische Rangfunktion geraten; `setting_bool` war dort undefiniert. Ein Import allein hätte einen falschen booleschen Rang erzeugt. | Rang wieder numerisch, Freigabe unverändert in `allowed()`. Neuer Test prüft Rang und getrennten Opt-out. RED: NameError; GREEN mit XMLTV-/Mapping-/Render-Suite. |
| TMDB60 ×2, Programme56 ×3, Pipeline68 | Die optionale Cinematic-`images`-Abfrage wurde bereits bei allgemeinem Identitätsmatching und kalter lokaler Materialisierung gestartet. Sie verbrauchte die PNG-Antwort des unveränderten Testtransports; danach `StopIteration` bzw. `FETCH_FAILED`. | Zusatzabfrage ausschließlich im expliziten Home-Hero-Pfad nach Identitätsprüfung. Allgemeine Suche → Details → Bild unverändert. Die ursprünglichen sechs Bildtests und ihre Persistenz-/Ergebnisprüfungen bleiben erhalten. Neue Admission-Tests auch für warmen Cache und Detailansicht. |
| Native Home 720p/1080p, außerhalb der 13 | Derselbe `StopIteration` brach den echten Plugin-Seed ab; Kodi meldete daraufhin `Files.GetDirectory`-Fehler `-32602`. Kein Beleg für eine fehlerhafte JSON-RPC-Signatur. | Zwei Host-Regressionen führen die unveränderten AST-Blöcke des tatsächlichen nativen Movie-/TV-Seeds aus. Beide RED vor Korrektur, danach GREEN. Native Fixture, RPC-Aufruf und spätere Pixel-/Receiver-Prüfungen wurden nicht abgeschwächt. Ein neuer nativer Lauf bleibt erforderlich. |
| MenuIcons45 | Neuer Xtream-Quellenauswahldialog benutzte ungeschmückte Strings. | Vorhandenen gemeinsamen Multiselect-Adapter verwenden. Tatsächlichen Wizard-Callback mit Auswahl, Abbruch und neutralem Legacy-Nicht-Xtream-Picker prüfen. |
| Provider58 ×3 | Bisherige Tests verlangten einen abschaltbaren Provider-Baseline-Schalter. Der verbindliche .96-Auftrag fordert die Grundversorgung immer aktiv und nachvollziehbare Historie. | Kontraktprüfung über echte UI-Callbacks: frische Portalwerte statt veralteter Zeile, Erhalt anderer Portale/Felder, Verlauf und Readback, aktiver Startfokus 401, deaktivierte Informationsschaltfläche 410, kein versehentlicher Import. |
| OverlayLifecycle | Lang-OK öffnet in .96 zuerst die Auswahl EPG-Zuweisung/Extras; der alte Test erwartete sofort Extras. | Echte Owner-Pump mit Auswahl Extras durchlaufen; alte Fokus-/Back-Prüfungen behalten. Zusätzliche Mapping-/Abbruchtests schützen Player, Sender und Fokus. |
| Token61 | Das Menü wurde verbindlich zum gemeinsamen Drei-Quellen-Artwork-Hub erweitert; der alte Test verlangte das alte Einzellabel. | Neue Überschrift plus identischer bestehender Routingpfad bis zum tatsächlichen Hub-Callback geprüft. Tokenbyte-/Import-/Aktivierungsassertionen bleiben bestehen. |

## Zusätzliche unabhängige Review-Funde

1. **Manuelle Bildidentität:** Automatisches Cinematic-Ranking und ein neuer gleichnamiger Cachetreffer konnten ein ausdrücklich gespeichertes Bild ersetzen. Die gültige gespeicherte `work87`-Bildreferenz hat jetzt Vorrang. Manuelle Bilder umgehen Enrichment, Alternativen und automatischen Posterwechsel, auch bei warmem Cache. Vier neue Tests zunächst RED, danach GREEN; Home und Details müssen dieselbe bestätigte URI behalten.
2. **XMLTV-Provenienz:** Der gemeinsame Worker-DTO, lokale Bildmaterialisierung und temporäre Cachekontexte verwarfen `xmltv96`. Dadurch blieb ein widerrufenes Bild anzeigbar. Die geprüfte Quellen-/Kanal-/Ereignis-/Revisionsbindung wird nun an allen drei Grenzen weitergegeben. Anzeigezulassung prüft auch die Ereignisidentität ohne GUI-SQL. Ausdrückliche XMLTV-Zuordnungen tragen `manual85`; sie gelten nicht als entsorgbare automatische Derivate. Vier reale Resolve/Status/Local/Cache-Regressionen reproduzieren den Fehler und prüfen den Widerruf. Legacy-Automatikbilder ohne neue Provenienz bleiben kompatibel.
3. **Bereits geöffnete Senderliste:** Ein veralteter Logo-Override blieb im vorbereiteten Channel-Modell nach Reset/Änderung erhalten. Eine verifizierte, profil-/konto-/sendergebundene RAM-Referenz aktualisiert jetzt denselben vorhandenen Channel. Verifiziertes Providerfallback bleibt erhalten; Profil-/Kontowechsel widerruft alte Referenzen. Keine Datei-, Hash-, SQL- oder Settings-Lektüre im neuen GUI-Auflösungspfad, keine Zugangsdaten in Channel-Repräsentationen. Der früh erkannte Widget-Import wurde aus dem direkten Overlay-Konstruktor entfernt. Sieben neue Regressionen plus alle 41 Overlay-Tests PASS.
4. **XMLTV ohne externe Suchfreigaben:** Der allerletzte unabhängige Randfalltest wies nach, dass eine ausdrücklich gewählte alternative lokale XMLTV-Quelle bei deaktivierten TMDB/TVMaze/Helper/Katalog-Suchen vor der Workerqueue abgewiesen wurde; ein direkter Resolve überschreibt außerdem READY mit AWAITING_BACKGROUND_REFRESH. Beide realen Fälle wurden RED reproduziert. Der Dienst lässt jetzt die lokale Auswahl zu, ohne `allow_lookup` zu aktivieren; erfolgreiches READY bleibt erhalten. Ein dritter Test schützt den ausdrücklichen XMLTV-Opt-out und den gespeicherten Mappingbestand. XMLTV-Suite: 18 PASS. Der davor begonnene Gesamtgegenlauf von `3b63ae8d` wurde ausdrücklich zugunsten dieses neuen Quellstands beendet; er gilt nicht als Abschlussnachweis.

## Bisheriger Gegenlauf dieser Korrekturrunde

- Alle ursprünglichen 13 Fehlfälle: **13 PASS**, 2,00 s.
- Alle .96-Suiten plus sämtliche Dateien der 13 Fehlfälle: **286 PASS**, 3 Warnungen aus `simpleeval`, 16,86 s. Spätere Logo-Ergänzungen sind darin noch nicht enthalten.
- Eigene XMLTV-Provenienztests einschließlich realem temporärem Cache: **15 PASS**, 1,18 s.
- Cinematic-Agent: **175 fokussierte PASS** nach den vier manuellen RED-Regressionsnachweisen.
- Mini-/Menü-Agent: **212 fokussierte PASS**.
- PO-Validierung: alle 17 Sprachkataloge PASS. Compile und Diffprüfung bestanden.

Dies ersetzt keine vollständige abschließende Host-/CI-Prüfung und keine Android-Abnahme. Aktuelles Gesamtresultat, geprüfter Commit, ZIP/SHA und native Kodi-Ergebnisse werden nach den vollständigen Läufen ergänzt. Alle physischen Android-Tests: **ANDROID_NOT_TESTED**.
