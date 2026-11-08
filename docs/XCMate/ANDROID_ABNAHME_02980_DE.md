# Android-Kurzabnahme XCMate 0.1.29.80

Alle Tests: **ANDROID_NOT_TESTED**. Zunächst Gates A–D durchführen; bei erneutem Freeze oder Grundfehler umfangreiche Funktionsabnahme stoppen und Zeitpunkt/letzte Aktion notieren. .79-Befunde bleiben historisch FAIL. Box A nicht verändern.

## Installation ohne Reset

1. ZIP und SHA256 aus dem .80-Draft-PR vergleichen. Das Paket aktualisiert dieselbe Add-on-ID `plugin.video.xtreammate`; keine Deinstallation, kein Profil-/Cache-Reset.
2. Auf der freigegebenen Testbox über Kodi → Add-ons → Aus ZIP-Datei installieren aktualisieren. Unter Informationen `0.1.29.80` kontrollieren; Erfolgspopup und Changelog prüfen.
3. Vorher/nachher Portale, Startgruppe/Startsender, EPG-Quellen/manuelle Zuordnungen, TMDB-Zugang (nur Vorhandensein, keinen Token teilen), Favoriten, Resume, Serien-Autoplay, Space Blue und sämtliche Benutzerwidgets einschließlich „Neu im Kino“ vergleichen.
4. .80 ist nicht im regulären/Pilot-/NeoDark3-Kanal veröffentlicht. Kein Repository-Update und kein Downgrade erforderlich.

| Gate | Ablauf und reale PASS-Bedingung | Status |
| --- | --- | --- |
| A – Idle/Bilder | Home ohne Senderstart öffnen. Jetzt/Danach/Progress lokal vorhanden; konfigurierte vollständige Startgruppe, Senderlogos und richtiges Hero-Bild bzw. korrekter Senderfallback. SAT.1 Gold/Richter Alexander Hold anwählen, 5 Minuten ohne Eingabe warten, danach 30 Minuten. Weder Logo/Fallback noch horizontale Leiste verschwinden. Kurzzeitige Netzwerkstörung darf gültige lokale Bilder/EPG nicht leeren. Sendungswechsel muss auf das neue Event umstellen, kein altes Bild festhalten. | ANDROID_NOT_TESTED |
| B – Reihen/Hero | Nach frischem Kodi-Start Filmreihe bereits ohne Fokuswechsel vollständig sichtbar. Filme/Serien/Live wiederholt wechseln, alle eigenen und fremden gespeicherten Widgets einschließlich Kino erreichbar. Großes Hero konstant, Landschaft proportional flächig, Portrait ohne Streckung, rechte halbtransparente Informationen; Fokus exakt am Element. Keine leeren oder wechselnden bereits gültigen Coverstände. | ANDROID_NOT_TESTED |
| C – Film/Exit | Filmwidget → Detailansicht → tatsächlicher Abspielbutton. Film-ID/Titel prüfen; bewegtes Video **und Ton** müssen starten, kein endloser Spinner. Back beendet nur eigenen Stream und stellt bedienbare vorherige Ansicht her. Erst nach PASS zusätzlich Film/Serie/Live jeweils 5, danach 20 Zyklen; Autoplay/Staffelwechsel/Resume/Stop weiterhin prüfen. Keine fremde Wiedergabe stoppen. | ANDROID_NOT_TESTED |
| D – EPG/Bilddetails | Comedy Central/NITRO anwählen/abspielen, großes EPG öffnen: tatsächlich angewählter Sender markiert, nicht pauschal WELT/Startsender. Lange Sender-/Programmtitel überlappen nicht; Fokus graublau. Mini-/Groß-EPG-Details öffnen/schließen; Sendungstitel und passende reale Bilder sichtbar. Mockingjay mit Teilnummer und Harry Potter gezielt prüfen: bestätigtes Bild oder endlicher sachlicher Fehler, kein dauerhaftes „ausstehend“. | ANDROID_NOT_TESTED |

## Weitere Regression und Fehlerprotokoll

Nach A–D PASS: Suche (Sender **und echte Programmtitel**, Filme, Serien), Fernbedienungsgruppen/Links/Back, manuelle EPG-Zuordnung, Jetzt/Danach an Tagesgrenzen, 88+ Sender, Film-/Serienkategorien, Neustart und Cachebeständigkeit, drei Medientypen und bestehender Decoder-Kompatibilitätsmodus. Keine zusätzlichen USB-/SMB-/Löschtests.

Pro Test `PASS / FAIL / ANDROID_NOT_TESTED`, Gerät, Kodi-Version, installierte Add-on-Version, Zeit (Europe/Berlin), Aktion, erwartete/tatsächliche Darstellung notieren. Bei Bildfehler Quelle/Event und sichtbare Textur getrennt bewerten. `VOD80`/`ART80`-/EPG-Diagnosecodes nur anonymisiert teilen; keine privaten Rohlogs, Provider-URLs, Zugangsdaten, TMDB-Tokens oder SMB-Details öffentlich posten. Bei Fehlern nichts löschen und nicht automatisch neu installieren.
