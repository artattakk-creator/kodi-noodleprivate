# XCMate / GS Media – priorisierter Backlog ab 0.1.29.94

**Stand:** 14.11.2026  
**Quelle:** offene GitHub-Issues, Nutzerbefunde der aktuellen Android-Neuinstallation und Codex-Master #454/#458.  
**Zweck:** Keine To-do-Liste vergessen; Scope kontrolliert halten; offene Issues sind weder automatisch \`FIXED\` noch \`ANDROID_PASS\`.

## P0 – Bestandteil des unmittelbar nächsten XCMate-0.1.29.94-RC

| Thema | Issues | Muss-Abnahme |
|---|---|---|
| Erstsetup ohne externe EPG-Auswahl | #457 #458 | Xtream-Provider-EPG default on (außer explizites Opt-out), Live-Sender trotzdem ohne EPG spielbar, \`epg_show\` korrekt |
| EPG-Quellen nachrüsten | #457 #458 #161 | DACH-Feeds DE/AT/CH + Kaimandura einfügen, keine Duplikate, Quelle und globalen EPG-Schalter konsistent |
| EPG-Download/Import beobachtbar | #457 #458 | echte per-Quelle-/pro-Job Downloadbytes, Parser/Matching/Commit, lesbares ACK, Stillstand/Fehler/Cancel |
| EPG-Rondell und Speicher | #454 #445 #458 | 7d zurück / bis 20d vor, nach DB-Readback Raw-XMLTV/Stages löschen, LastGood & Backup retten, same-volume-Bytes nachweisen |
| Mini-EPG „Unterhaltung“/„4K“ leer | #451 #457 #458 | aktive Sendergruppe selektieren → Sender sichtbar, ohne XMLTV; Teil-/Vollkatalog und Coldboot geprüft |
| Startsender-/Index-Schutz | #451 #442 #454 | Startsender-Konfiguration bei Teilkatalog nicht verlieren, direkte Wiedergabe unabhängig vom EPG |

## P0 – zwingende No-Regression- / separate Ursachen-Gates

| Thema | Issues | Abgrenzung |
|---|---|---|
| STOP/BACK-Freeze und anormaler Kodi-Prozessabbruch | #452 #442 #174 #454 | .93-Fixes nicht regressieren; Android \`logcat\`/Decoder/ExitInfo nötig. Linux-PASS ≠ Android-FIX |
| XMLTV-Bild, Galileo, Ghosts/TMDB-/TVMaze-Mapping | #433 #413 #443 | Vorschaubild → Details und manuelle Save-/Readback-Regression; umfassende Bild-Persistenzreparatur ggf. eigener Fix-PR |
| Android-Speicher-/SQLite-Probleme | #443 #401 #454 | keinen neuen Reserve-/DB-Hänger durch EPG-Import/GC auslösen; echter Platzgewinn, keine Kodi-Core-DB löschen |
| BINGIE-Hero/Logos/Widgets/Token | #454 #439 #411 | vorhandene 6+MP3 Reihen, Senderlogos, Bildfallback, Branding, Benutzer-TMDB-Token und Favoriten bewahren |
| Kodi-App verschwunden nach Neustart | #452 (neue Befundnotiz) | Gerät/Android-Paketverwaltung prüfen, **kein** XCMate-Rootcause behaupten |

## P1 – technisch passende, kleinere Ergänzungen nach grünen P0-Gates

1. **#427 / #161: EPG-Senderzuordnung, XMLTV-Abdeckung, Vorschau und Persistenz.** Bei bestehendem Guide-UI tatsächliche \`READY / UNMAPPED / SOURCE_EMPTY / STALE\`-Zustände anzeigen, keine automatische falsche Zuordnung. Nur additive Diagnose/Readback in .94; komplette UI-Migration separat.
2. **#435 / Draft #436: \`widget50_plans\`-/Skin-Restore-Snapshot-Retention.** Nur letzte hashverifizierte, tatsächlich aktive Recovery-Stände behalten. Bereits geprüfter Backup-Snapshot 8 Planverzeichnisse / ca. 21,6 MB unkomprimiert; **kein** Nachweis derselben Dateien nach Android-Reset. Kein Prune ohne echten Live-SHA/Lock/Restore-Beleg. Separater Review-PR.
3. **#108: automatisch aktualisierte Kataloge & verwaiste Artwork-Referenzen sicher bereinigen.** EPG-Raw-Cleanup ist **nicht gleich** Artwork-GC; auf aktive Hero-/Bild-/Logoreferenzen und externe Volumes Rücksicht nehmen.
4. **#450: MP3-Album-Neuheiten.** Home-Reihe soll echte neue Alben/Cover statt bloßer Kategorien anzeigen. Vorab native Route/Provider prüfen, persönliche SkinShortcuts nicht überschreiben.
5. **#444: Home-only Filmgruppenfilter.** Adult-/Sport-/Boxen-Kategorien auf Home-Reihen pro Portal ausblendbar, aber **niemals** Einträge aus vollständiger Film-/Serienbibliothek oder Provider-Index entfernen.

## P1/P2 – eigene Komponenten/Release-Zyklen, nicht in .94-EPG-Hotfix drängen

1. **#443 / #106 / #401:** Echte Artwork-/Bild-EPG-Auslagerung auf USB und optional SMB/NAS mit sicherer, messbarer Migration; aktive SQLite-EPG intern behalten; Target-Pool/Reserve/Hash/Readback/Recovery. Setup-Wizard muss Bild-EPG-Auswahl und Speicherziel anbieten. **Installer-Entwicklungsstand separat von produktiver .5.26**, keine ungetesteten Installer-Drafts blind mergen.
2. **#411:** umfassendes BINGIE-Original-Look-Redesign (großer Fanart-Hero, Posterzeilen, kompakte Logos, Fokusrahmen, Navigation); frühere schnelle Startseite nicht opfern. Keine privaten Foto-Referenzen ins Repo stellen.
3. **#434:** eigenständiges XCMate-/Kodi-Backup direkt nach Google Drive (OAuth TV Device Flow), verifizierbare Sicherung/Restore, ZIP + entpackt, Multi-Ziel/-Quelle und große Sicherungen. Der angelegte Drive-Zielordner ist **keine** bestätigte Box-Sicherung. Benutzer-/Token-Daten vor Export schützen.
4. **#449:** geschützter HTTPS-TMDB-Tokenimport vom eigenen Server als gesonderter GS Media Installer-Entwurf; niemals hartcodierte Tokens, Basic-Zugangsdaten oder URL-Credentials. Bestehenden manuellen Tokenimport und Opt-outs bewahren.
5. **#417:** Joomla-/TMDB-Gateway mit Geräte-Pairing **ausdrücklich zurückgestellt**; keine implizite Umsetzung aus den verwandten Token-Issues.
6. **#407 / #445:** GS Media Setup 48/48, SlyGuy/Helper/SkinShortcuts/Branding und sauberer Online-Neuaufbau – nur bei Installer-Arbeiten als eigene Abnahme führen.

## Reihenfolge nach .94 und Abhängigkeiten

- **Zuerst:** .94-P0 A–G aus [CODEX_UEBERGABE_02994_EPG_PROGRESS_AND_RECOVERY_2026-11-14_DE.md](CODEX_UEBERGABE_02994_EPG_PROGRESS_AND_RECOVERY_2026-11-14_DE.md), native Testmatrix + ausdrücklich noch offene Android-Abnahme.
- **Danach gezielt:** Bildmapping-Persistenz #433/#413 und Player-Hardware-Gates #452, soweit .94 sie nicht beweisbar abschließen konnte.
- **Nächstes eigenständiges Paket:** physischer Speicher/USB/SMB samt Installer-Option #443/#106, ohne .94 zu blockieren, sofern .94 bereits sicher und funktional.
- **Weitere kleine Pakete:** referenzsichere Widget-Snapshot-Prune #435, MP3-Alben #450, Home-Filmfilter #444, generelle Katalog-/Artwork-Retention #108.
- **Später:** großes BINGIE-Redesign #411, Google-Drive-Backup #434, geschützter TMDB-Import #449. Joomla-Gateway #417 bleibt ausdrücklich zurückgestellt.

## Release-/Sicherheitsregel

**Jeder Punkt bleibt offen, bis Code + reproduzierbare Tests + reale Geräteabnahme (wo nötig) belegt sind.** Nicht alle Themen in ein einziges .94-Add-on-ZIP schreiben. Separate isolierte PRs, verifizierbare Artefakte, keine unaufgeforderte Veröffentlichung, keine stillen Änderungen an \`main\`-Source, regulär, Pilot oder NeoDark3. Geschütztes 0.1.29.90-Fallback und Pilot 0.1.29.93 nicht löschen. Keine Kodi-/Benutzer- oder NAS-Daten ohne gesonderte Berechtigungs-/Löschfreigabe anfassen.
