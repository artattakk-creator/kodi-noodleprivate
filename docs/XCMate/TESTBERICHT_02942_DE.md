# XCMate0.1.29.42 – vollständiger Host-Testbericht

Stand26.10.2026. Basis `354afc1cc524ec3b01001770e6afe6aec5fea70c`, geprüfter Quell-/Teststand `48d188bcc0664f2ce64fcdc6845852a62f6ab7f7`. Dies ist ein **opt-in Live-Lifecycle-Kompatibilitäts-/Diagnosekandidat**. Native RK3528-Hängerfreiheit und alle neuen Android-Gates **NOT_TESTED**, keine Behauptung „Decoder repariert“.

## Ergebnisse

- **1.514 Tests PASS in 229.990s**, 0FAIL, 0ERROR, 0SKIP. Alle **1.479 bisherigen Testmethoden erhalten**, 34neue Native-Lifecycle-Vertragstests und eine umfassende Schutzprüfung. Vollständiger synthetischer Hostlog: [TESTLOG_02942.txt](TESTLOG_02942.txt), Methodenliste: [NEUE_TESTS_02942.json](NEUE_TESTS_02942.json).
- Gezielte .42-Suite34PASS, vorherige .41-Native-Stop-Suite9PASS, Kodi21-Overlay40PASS und .37-Suites48PASS. Die Gesamtsuite enthält diese Tests erneut; die Summen sind nicht zusätzlich zu1.514 zu addieren.
- Gettext DE/EN jeweils948Kontexte PASS, 92lokale Navigationstexturen/Provenienz PASS, Pythoncompileall/AST PASS. Vorhandene unveränderte SMB-Vendor-Docstring-SyntaxWarning unter Python3.12, kein neuer Syntaxfehler.
- **381 .41-Quelldateien bytegleich**, insbesondere VOD-/Serienplayer, Resume/Autoplay, EPG/Mini, Widgets/Updatehinweis, alle Skins/Originalgrafiken, Portale/Artwork-Modi und Remote-/Keymap-Module. .41ZIP, Produktionsindizes und Publish-Workflow unverändert. 62Dateien anderer lokaler WIP-Stände unverändert. [SCHUTZPRUEFUNG_02942.json](SCHUTZPRUEFUNG_02942.json).
- Zwei unabhängige deterministische Builds erzeugten bytegleiches ZIP. 391reguläre Dateien, 2,660,129Bytes; CRC, Pfade, eindeutige Mitglieder, vollständiger Quellbyte-/AST-Abgleich PASS; keine Profile, Datenbanken, Rohlogs oder Symlinks im Paket. [DATEIKATALOG_02942.json](DATEIKATALOG_02942.json).
- SHA256: `d28675d19671871d0370e5c538c0cac35783ec7c9a61cb71a82b32d9919b2d80`.
- GitHub-CI inklusive heruntergeladenem Artefaktabgleich wird vor endgültiger Übergabe im **Draft-PR** mit Run-/Artefaktlink dokumentiert. Keine produktive Veröffentlichung für den PR.

## Aussagekraft und Fehlergeschichte

Die Hostmodelle können den nativen Codec nicht ausführen. StrategieA simuliert bewusst ein Hängen bei Stop im Fullscreen; StrategieB verlässt diesen Modellzustand zuerst. Das ist kein reproduzierter Android-Decoderfehler. Separat bleibt ein modellierter nativer Hänger **nach** Fullscreen-Deinit korrekt ein Timeout, ohne Fake-Home/StopDone. FIFO-Prepare und native Stop-Barriere sind getrennte Verträge. Auch Deadline-Ablauf vor dem nächsten Poll kann eine verspätete Barriere nicht in Erfolg umwandeln.

Der erste vollständige Lauf hatte1514Tests mit8Failures/10Errors:16resultierten aus gesperrten lokalen Loopback-/SMB-Sockets der Sandbox, zwei aus einem älteren Kodi-Testmodell ohne `utils.setting_bool`. Letzteres wurde in der Fixture ergänzt, keine Assertion entfernt oder Test übersprungen. Ein isolierter HTTP-Test bestätigte danach den Netzwerkweg; der endgültige Gesamtlauf oben hatte den notwendigen lokalen Netzwerkzugang und ist vollständig grün. Die erfolglosen Umgebungsläufe werden nicht als Produktfehler, Gerätebefund oder Erfolg umgedeutet.

Die bestehende Suite verwendet ausschließlich isolierte Hostfixtures, teils echte lokale HTTP-/SMB-Server; es erfolgte **kein** Speicher-/SMB-/USB-/SD-Test auf Box A oder B. Private Android-Rohlogs wurden nicht geöffnet/veröffentlicht. Native Quellbelege: [KODI_NATIVE_PROOF_02942.json](KODI_NATIVE_PROOF_02942.json). Ein ausführlicher API-/Logabgleich und die verbliebenen Ursachenhypothesen stehen in [URSACHENANALYSE_02942_DE.md](URSACHENANALYSE_02942_DE.md).

## Android-Freigabegates

**Vor Live-Test auf Box B neue Option unter Add-on-Konfigurieren → Wiedergabe ausdrücklich EIN schalten. Standard AUS lässt den bekannten .41-Pfad unverändert.** Anleitung: [ANDROID_ABNAHME_02942_DE.md](ANDROID_ABNAHME_02942_DE.md).

Startsender → **einmal** Live-Back → ausschließlich nach PASS Film-Back und kurze Regression → fünf weitere Live-Zyklen → nur nach deren PASS zwanzig weitere. Bei Freeze sofort abbrechen. Alle sieben neuen Gates NOT_TESTED. Historische .41-Abnahme #215 unverändert; weitere40-Gate-Abnahme erst nach P0 fortsetzen. Kein Merge/Release/Issue-Close/Geräteinstallation.
