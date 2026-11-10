# XCMate .88 – Android-Abnahme Box B, Kodi 21.3 / RK3528

Alle Tests **ANDROID_NOT_TESTED**. Host-/Linux-Tests sind keine Geräteabnahme. Box A nicht verändern. .88 ist ausschließlich ein manuell installierbares kumulatives Test-ZIP; keine reguläre Repository-Veröffentlichung.

| ID | Durchführung / Nachweis | Status |
|---|---|---|
| A88-01 | Bestehendes .87-Profil sichern; ZIP als Update installieren. Provider, Startgruppe, EPG-Mappings, Token, Favoriten, Fortschritt, Space Blue unverändert. | ANDROID_NOT_TESTED |
| A88-02 | Startgruppe vollständig öffnen/scrollen: echte Senderzahl und verfügbare/verifizierte/lokal gespeicherte/tatsächlich sichtbare Logos separat zählen. Ziel 88 reale Items; fehlende Quellbilder separat dokumentieren. | ANDROID_NOT_TESTED |
| A88-03 | Rail, Hero-Fallback und Detail: richtiges Logo, proportional, lesbarer Name nur wenn Logo fehlt. Keine Gruppenüberschrift als Sender. | ANDROID_NOT_TESTED |
| A88-04 | Artwork-Verwaltung → Speicher und Artwork-Bestand: Free/Total/Reserve/Poolvergleich dokumentieren. Unter Reserve RAM_ONLY zulässig, niemals PERSISTED behaupten. Keine automatische Verschiebung/Bereinigung. | ANDROID_NOT_TESTED |
| A88-05 | Scrubs/vergleichbares passendes Programm in Details öffnen. Mindestens 5 Minuten Bild betrachten, bei 0/45/120/305 Sekunden Screenshots; Netz unterbrechen. Bild bleibt, keine 45s-Leerwarnung; anschließender Sender-/Ereigniswechsel korrekt. | ANDROID_NOT_TESTED |
| A88-06 | Gleicher Sender/Zeitpunkt in Mini-EPG, Groß-EPG, Home und Details: Titel/Start/Ende/Jetzt/Danach/Fortschritt vergleichen. Keine neuen Reader.close-Exceptions. | ANDROID_NOT_TESTED |
| A88-07 | Merken → erneut drücken (Entmerken), Kodi neu starten, anderen Eintrag erhalten; keine doppelten Einträge. Bestehende Merkliste im Groß-EPG aufrufen. | ANDROID_NOT_TESTED |
| A88-08 | Jetzt umschalten aus großem EPG, Mini-/Live-Overlay und eigenständigen Details: genau ein Start, richtige Quelle, vorhandener Back-/Exit-Ablauf unverändert. | ANDROID_NOT_TESTED |
| A88-09 | Beim bekannten .87-Adapter die neue .88-Layoutvorschau prüfen und ausdrücklich bestätigen. Dann Home-Hero auf 1080p und 720p gegen Originalfoto 4 vergleichen: Motiv rechts, weicher Verlauf/Texte links, kompakte Rail, alle eigenen/fremden Reihen sichtbar. Originalfoto für endgültigen Vergleich erforderlich. | ANDROID_NOT_TESTED |
| A88-10 | Alle vorhandenen Reihen inkl. MP3 Streams, SHOUTcast, Im/Neu im Kino, Serien/Trends: Name, Reihenfolge, Pfad, Navigation und Neustart prüfen. | ANDROID_NOT_TESTED |
| A88-11 | Technische Widgetverwaltung (bestehender Bereich „Experimentell“) → XCMate-Logo in BINGIE: Vorschau/Bestätigung, richtige transparente Grafik, Rücknahme aus Backup prüfen. Keine anderen Skin-Einstellungen verändern. | ANDROID_NOT_TESTED |
| A88-12 | Fernbedienung alle Ebenen, Details horizontal drei Buttons, Beschreibung scrollen, Back; Filme/Serien/Live starten und verlassen, Autoplay/Resume unverändert. | ANDROID_NOT_TESTED |

Fehler mit Test-ID, Zeit, Ansicht und anonymisierten Diagnosecodes melden. Keine Provider-URLs, Token, SMB-Zugänge oder Rohlogs auf GitHub hochladen. Kein Merge/Release vor ausdrücklicher Freigabe.
