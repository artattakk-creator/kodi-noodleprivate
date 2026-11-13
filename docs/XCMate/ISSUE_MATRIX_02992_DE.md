# XCMate .92 – Issue-Abnahmematrix

Stand 13.11.2026, Source-Draft #448, Installer-Draft #447. Kein Merge/Release. FIXED_HOST/FIXED_NATIVE bedeutet ausschließlich den jeweils genannten Prüfbereich; es ist keine Android-Abnahme.

| Referenz | Ergebnis im Kandidaten | Noch offen / nächste Abnahme |
|---|---|---|
| #443 Speicher / #401 USB | PARTIAL – FIXED_HOST: Inventur vor Pflege/Transfer, Journal, exaktes eigenes Temp-Cleanup, begrenzte EPG-Retention, gemessene physische Bytes, USB-Hash/Render-/Neustartbarriere, Originale separat schützen, eigene Speicherseite | Größte echte Android-Datenklasse/Quota und USB-Platzgewinn ANDROID_NOT_TESTED; vollständiger Orphan-/Backup-Referenzbeweis und sichere alte DB-Kompaktierung OPEN |
| #108 Altlasten | PARTIAL – eigene exakt bekannte geschlossene Cache-Temps und abgelaufene EPG-Zeilen; keine Heuristik-Löschung unbekannter Dateien | Allgemeiner Artwork-GC nach mehreren vollständigen Snapshot-Referenzprüfungen OPEN |
| #433 / #413 manuelle Bilder | FIXED_HOST – atomare kleine Metadaten, Writerfehler getrennt, kalter Readback, gespeicherte Zuordnung von noch ladendem Bild unterscheiden | Reopen/Reboot/echte sichtbare TMDB-/TVMaze-Zuordnung ANDROID_NOT_TESTED |
| #442 / #174 Player | PARTIAL – lokaler/VFS-Pfad nicht mehr durch HTTP-Headersuffix beschädigt; 60 Linux-Kodi-Stop/ACK-Zyklen PASS; 20 globale native Gruppen-/Senderwechsel je Auflösung PASS | RK3528 MediaCodec, STOP_TIMEOUT, StreamLoss und ungeplantes Home OPEN / ANDROID_NOT_TESTED; CAddonMgr/AAC vor XCMate getrennt |
| #445 Home75 / Widgets | FIXED_HOST und FIXED_NATIVE für exakten ZIP-Sechsreihenlauf 720p/1080p, echte Audio-Clock, drei Kodi-Kaltstarts und globale Gruppennavigation; Home75-Langlauf gesondert im Testbericht | Persönliche Android-SkinShortcuts, IR, Timeout-/Kaltstartabnahme ANDROID_NOT_TESTED; zusätzliche .89-Reserve-/Cold-Logo-Matrix gesondert |
| #444 Filmgruppenfilter | FIXED_HOST – Portal-/Account-/Profilbezug, Provider-Gruppen-IDs, ausschließlich Home-Reader, neue Kategorien erst nach Nutzerentscheidung | Android-UI und unveränderte vollständige Bibliothek ANDROID_NOT_TESTED |
| #161 / #98 EPG | PARTIAL – zentrale Commit-/Revisionsprüfung vor begrenztem Now/Next-Diskcache, 7 lokale Tage Historie, Mehrquellen-/Bildmetadaten erhalten | Long-OK über alle drei Ansichten, vollständige Quell-/DB-Konsolidierung, externe XMLTV-Stream-Stage, manuelle eventgebundene XMLTV-Bildwahl OPEN; echte Mehrquellen-Abnahme ANDROID_NOT_TESTED |
| #107 Puffer | Vorhandener Einstieg in tatsächliche globale Kodi-Einstellungen erhalten; kein erfundener per-Stream-Regler | Gerätebedienung/effektive Kodi-21-Grenzen ANDROID_NOT_TESTED |
| #450 MP3-Alben | OPEN – publizierte Add-on-Albumroute statisch gefunden; persönliche Quelle unverändert | Online-/native Album- und Wiedergabeprüfung in isolierter Folgearbeit |
| #445 Detail-UX / Poster | Bestehende Senderlogos und Werkattribution erhalten | Klickbare Quellenlinks/Credits gesondert prüfen; endgültige Postermaße warten auf Referenz-Screenshot |
| Installer #447 | FIXED_HOST, 8 Tests + CI PASS; .5.29-Auswahlbrücke zu XCMate .92, Nein/Später und Bestandsprofile geschützt | Android-Neueinrichtung ANDROID_NOT_TESTED. .5.26 bleibt bytegleich, kein erneuter Komponentenlauf |

Alle 22 Android-Gates bleiben ANDROID_NOT_TESTED. Maßgeblich: [Testbericht](TESTBERICHT_02992_DE.md), [Implementierung](IMPLEMENTIERUNG_02992_DE.md), [Geräteplan](ANDROID_ABNAHME_02992_DE.md). Der vollständige Masterauftrag #445 ist damit nicht als vollständig erledigt erklärt; offene P0s verhindern derzeit eine Merge-Empfehlung.
