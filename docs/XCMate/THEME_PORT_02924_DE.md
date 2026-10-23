# XCMate 0.1.29.24 – optionaler Theme-Installer

Kumulativer Draft auf main .22 mit dem separaten Grafik-Kandidaten .23 (#112). Kein Merge, Release oder OTA. .23 und .24 sind Geräte-Testkandidaten, keine Nutzerfreigaben. Nach Änderungen aus der .23-Abnahme muss dieser Folgebranch entsprechend nachgezogen werden.

## Implementierung

Selektiv aus #50 übernommen: theme_catalog, theme_package, theme_store, theme_render, theme_ui; bestehendes profile_transaction bleibt identisch. Kein alter .30.1-Core. Der Renderer verwendet die aktuellen .22/.23-Layouts und IDs: großes EPG 310–315, bestehende Media-Rails, Live- und eigenes Media-OSD. Die transparenten .22-Guide-Fokusrahmen, weißen Guide-Texte und Hit-Rechtecke bleiben erhalten. Nur lokale Texturen, unfokussierbare Dekoration und Detailaktions-Icons ändern sich. Eingabe-/Owner-/Player-Verträge werden nach exakt invertierten visuellen Hooks weiterhin gegen die ursprünglichen Hashes/AST geprüft; alte Freeze-Digests werden nicht ersetzt.

Pfad: Einstellungen → Darstellung & Sprache → XCMate-Designs → Designs verwalten. Standard – XCMate Lightweight funktioniert ohne Paket. Space Premium – GS Media zeigt Nicht installiert / Installiert / Aktiv, bietet offline Original-Vorschau, expliziten HTTPS-Download mit Installation, Aktivieren, Standard-Rückwechsel und ausschließlich Theme-Entfernung. Laufende Wiedergabe verschiebt einen Wechsel bis zum nächsten geöffneten XCMate-Fenster nach Wiedergabeende. Bestehende native Fenster behalten ihre Textur-Snapshots. Kein automatischer Download bei Start, Auswahl oder Neustart.

appearance.validate übernimmt das Theme-Feld. Atomare selection.json ist maßgeblich; appearance_v1 hält die Auswahl zusätzlich als Migrationspräferenz. Alte vorhandene Auswahl wird bei fehlender selection.json ausschließlich aus bereits installierten, passenden lokalen Paketen wiederhergestellt. Fehlendes/defektes/inkompatibles Paket führt zu Core-Fallback, ohne die Präferenz oder Medien zu löschen.

## Paket und Downloadpfad

Alle 98 Originalbild-Hashes entsprechen PR #50. Kompatibilität wurde vor dem Manifest-Port durch 37 Installer-/Sicherheits-/XML-Vertragstests auf .24 geprüft; anschließend alle 98 Originale vollständig dekodiert und das reale Paket installiert. Min-Version ist nun .24. Das angepasste Manifest/README ändern den Paket-Hash, nicht die Bildbytes:

`79a37cd1568611054d87697045e6879664677f05348c7af93836e4d70872bdf9` · 19.772.195 Bytes.

Der Review-Katalog ist an Commit 0452bc9 gebunden, das Paket an 8ab1a566877ed0a71573f90d0f82b11457bf9da4. Beide sind über kontrollierte HTTPS-Pfade dieses Repositorys abrufbar. Der echte HTTPS-Abruf des Katalogs und 19,8-MB-Pakets, SHA256, Installation von 98 Originalen, Aktivierung und Auswahl nach Modul-Neustart wurden auf dem Host bestanden (HTTPS_THEME_02924.json). Der produktive main-Katalog bleibt unangetastet. Vor einer späteren Freigabe muss dessen gewünschter Veröffentlichungspfad separat geprüft werden; dieser Draft benötigt kein produktives Repository-Update.

Downloader und Installer begrenzen Größe, Zeit, Dateien, Dekompression, Pixel und Metadaten; keine Redirects/fremden Hosts, ausführbaren Layouts, Zip-Slip-/Symlinkpfade oder unbestätigten Prüfsummen. Private temporäre Stage, Reserveprüfung, atomare Auswahl, begrenzte Versionen und Rollback. Bestehende Dateien/READY-Jobs bleiben erhalten. Das Core-ZIP enthält lediglich eine originale Offline-Vorschau, nicht das Premium-Paket oder alle Grafiken.

## Grafikzuordnung und Grenzen

Die historische Zuordnung 86 verwendet/bedingt + 12 Reserve ist unverändert als SPACE_PREMIUM_ORIGINAL_MATRIX_PR50.json dokumentiert. Die aktuelle portierte Matrix nennt jeden der 98 Originalpfade und aktuelle Verbraucher. 87 Dateien sind angebunden/bedingt; das bisherige Reserve-Heute-Icon wird am bereits funktionierenden Jetzt-Kopfbutton genutzt. Die übrigen elf ursprünglichen Reservebilder bleiben im Paket. Es wurden keine funktionslosen Controls erzeugt. Branding bleibt die unveränderliche Core-Originaldatei, auch bei Premium; ein Theme kann das Add-on-Icon nicht überschreiben.

Tatsächliche gleichzeitige Sichtbarkeit hängt vom geöffneten Bereich, verfügbaren Providerbildern, Fehler-/Leerzustand, Player-Fähigkeiten und Kodi-Widget-Layout ab. Aufnahmen-/Downloadmanager und Timeline sind Folgephasen; deren bisherige Reserveicons sind noch keine zugesagten Funktionen. Kein globaler BINGIE-Skin-/Keymapwechsel, kein Kodi-Bilddatenbankzugriff, keine Portal-/EPG-/Resume-Migration.

Android 13 ARM32 / Kodi 21.2 / BINGIE MOD wurde hier nicht ausgeführt. Fokuslesbarkeit, gerätespezifisches HTTPS/Zielmedium und sichtbares Original-Icon müssen real abgenommen werden. #37/#41/#90/#111 bleiben bis zur entsprechenden Gerätebestätigung offen. #85 B02 bleibt ausdrücklich außerhalb aktiver Tests.
