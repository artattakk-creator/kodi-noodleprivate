# XCMate 0.1.29.67 – Android-Abnahme Box B

Ziel: Kodi 21.3 ARM32 / Titan BINGIE MOD 2.2.3. **Alle Tests zunächst NOT_TESTED.** Box A bleibt unberührt. Die historischen .66-FAILs bleiben erhalten. Kein Reset, keine Deinstallation, keine Änderung gespeicherter Widget-URLs oder ungefragte Skinänderung.

Das ZIP stammt ausschließlich aus dem erfolgreichen CI-Lauf des PR #308. Vor Installation SHA256 mit der beigefügten Datei vergleichen. Es ist ein Testupdate derselben Add-on-ID. Kein automatisches Repository-Release.

| Gate | Ausführung und PASS-Kriterium | Status |
|---|---|---|
| LIVE67-01 | BINGIE Home: ersten Startgruppensender mit OK starten. Bild/Ton sichtbar, keine EPG-Abhängigkeit. Einmal Zurück: bedienbare Ansicht, bestätigter .42-Modus unverändert. Bei Hänger zunächst abbrechen und Befund melden. | NOT_TESTED |
| LIVE67-02 | XCMate-Startsender starten, Bild/Ton und korrektes Zurück. | NOT_TESTED |
| LIVE67-03 | Großen Guide öffnen und Sender starten, genau ein Start, keine fremde Home-/Directory-Ansicht. Guide erneut öffnen und wiederholen. | NOT_TESTED |
| LIVE67-04 | Mini-EPG über Links öffnen, anderen Sender auswählen und starten. Focus, Sendergruppen und Zurück funktionieren. | NOT_TESTED |
| LIVE67-05 | Insgesamt mindestens drei verschiedene reale Sender prüfen; TS und soweit vom Anbieter unterstützt HLS. Format nur bewusst in Einstellungen → Live-TV umstellen, Ergebnis/gewählte ISA-Präferenz notieren, anschließend ursprüngliche Wahl wiederherstellen. Nicht unterstütztes HLS ist NOT_TESTED mit Grund. | NOT_TESTED |
| LIVE67-06 | Live-Stream prüfen für einen funktionierenden und einen fehlgeschlagenen Sender. Nur Code, HTTP-Status, MIME-/Präfixklasse notieren. Kein URL-/Passwort-Screenshot. Diagnose startet keine Wiedergabe. Bei 504 nicht pauschal Provider schuld nennen. | NOT_TESTED |
| LIVE67-07 | Bei realem Netz-/Startfehler kein Retry-Sturm, kein blockierter Fokus, spätere erfolgreiche Wiedergabe bleibt möglich. Fehler nicht absichtlich an privaten Zugangsdaten erzeugen. | NOT_TESTED |
| EPG67-01 | Derselbe Sender auf Home, im großen Guide, Mini und Infobar: Jetzt/Danach und Zeiten stimmen mit gespeicherter Quelle überein. | NOT_TESTED |
| EPG67-02 | Automatischer Sender mit früher leerer Provider-ID-Anzeige zeigt gültiges Programm aus lokalem Alias/Provider-Mapping. Drei betroffene Sender vergleichen. | NOT_TESTED |
| EPG67-03 | Vorhandene manuelle Quellenzuordnung bleibt exakt erhalten; konkurrierende Quelle mit gleicher Kanal-ID darf sie nicht überschreiben. Kein Speichern einer Testzuordnung nötig. | NOT_TESTED |
| EPG67-04 | Bereits geladenen Guide schließen/öffnen; während fehlgeschlagenem optionalem Kurz-EPG bleiben gültige lokale Daten sichtbar. Keine Datenbank auf dem Gerät beschädigen. Die DB-Fehlersimulation bleibt Hosttest. | NOT_TESTED |
| EPG67-05 | Nach Kodi-Neustart lokale EPG-Daten, Startgruppe, Favoriten und Zuordnungen vorhanden. Fortschritt/24h-Refresh nachvollziehbar, keine wiederholten 88er-Ladeschleifen. | NOT_TESTED |
| EPG67-06 | WELT, NITRO, einen noch nie fokussierten Sender mit nachgewiesener Quelle und einen ohne Quell-EPG nach Kaltstart vergleichen. Alle Ansichten nutzen denselben lokalen Stand. Fälligen 24h-Refresh und Offline-Neustart beobachten; falls noch nicht fällig, Refresh-Gate NOT_TESTED belassen. Keine Gerätezeit oder DB-Dateien manipulieren. | NOT_TESTED |
| ART67-01 | Vorhandener eigener TMDB-Zugang aktiv: belegbare Sendung wählen; lokales Bild erscheint auf Home und in Details, auch ohne installierten Helper. Token nie anzeigen oder veröffentlichen. | NOT_TESTED |
| ART67-02 | Dieselbe belegte Sendung im großen und Mini-EPG fokussieren: lokale Vorschau erscheint, beim Fokuswechsel kein Bild der vorherigen Sendung. | NOT_TESTED |
| ART67-03 | TMDB-Bild: originales dezentes Logo unten rechts. Provider-/XMLTV-/TVmaze-Bild: kein TMDB-Logo; korrekte Quelle. Unbelegte Sendung: ehrlicher Platzhalter. | NOT_TESTED |
| ART67-04 | Optional TVmaze bewusst einschalten und eindeutig belegte Serie prüfen; Serienfallback ist beschriftet. Mehrdeutige/fehlende Bilder nicht als Erfolg zählen. Danach ursprüngliche Einstellung wiederherstellen. | NOT_TESTED |
| ART67-05 | Über/Credits zeigt offizielles Logo und den vollständigen vorgeschriebenen Attributionstext. Heruntergeladenes Bild nach Neustart wiederverwendbar. | NOT_TESTED |
| REG67-01 | Film-/Serienwidgets: Cover, Kategorien, Fokus, Suche und automatisches Aktualisieren funktionieren; gespeicherte Widgetverknüpfungen unverändert. | NOT_TESTED |
| REG67-02 | Film/Serienfolge starten, Zurück, Resume und staffelübergreifendes Autoplay prüfen. .42-Live-Stop-Einstellung und Fernbedienung unverändert. | NOT_TESTED |
| REG67-03 | Portale/Passwörter, Token, Favoriten, Gruppen, Originalicon, Cover und EPG-Mappings nach Update und Neustart erhalten; Installationspopup zeigt .67 und Änderungstext. | NOT_TESTED |

Zusätzlich gilt die vollständige Sichtabnahme aus [#300](https://github.com/artattakk-creator/kodi-noodleprivate/issues/300) weiter, ausschließlich auf **Box B**: HOPE/Filmwidget, Coco mit nachfolgender Musikreihe, Lupin mit nachfolgender Fremdreihe, eigene Loki-/Serienreihe und flache Live-Senderbuttons. Je erste, zweite und letzte Kachel, horizontaler/vertikaler Wechsel, Home-Rückkehr, fehlende Fanart und lange Titel prüfen. Genau ein Rahmen auf der tatsächlichen Kachel, kein Text über Reihenüberschriften. Bestehende Fremdwidgets nicht neu einrichten oder Skin-Dateien ändern. Nicht verfügbare Auflösungen/Fremdquellen ausdrücklich NOT_TESTED markieren. Die fünf realen Android-Fotobefunde bleiben bis zu passenden neuen Sichtbelegen offen; native Linux-Screenshots ersetzen sie nicht.

Ergebnis bitte pro Gate als PASS / FAIL / NOT_TESTED mit kurzer Beobachtung und Kodi-Version melden. Für Live zusätzlich Sender nur anonymisiert, Startweg, Format, Dauer bis Bild/Ton, Back-Ergebnis und feste Diagnosecodes. Kein Rohlog öffentlich hochladen. Kein Merge ohne ausdrückliche Freigabe.
