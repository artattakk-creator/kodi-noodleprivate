# GS Media Setup 0.5.27 – separater optionaler Pairing-Entwurf

Auftrag #417 / #415 P0-K. Basis `6c748388e04ef021de0e6e7df193c1ab812c260c`, unverändertes veröffentlichtes Setup .5.26 SHA256 `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`. Kein Installer wird ausgeführt, kein Katalog aktualisiert, keine Box verändert.

Der Review-Builder liest ausschließlich das hashgeprüfte bestehende .5.26-Paket. Genau fünf Mitglieder unterscheiden sich: neue Versionskennung; optionaler Schritt nach bestätigten 48 Komponenten vor Abschluss; separater Menüpunkt zum späteren Fortsetzen; Clientadapter; ein unsichtbares öffentliches Statusfeld. Alle übrigen Mitglieder bleiben bytegleich. Keine neue Skin-/Komponenten-/Tokeninstallation. Bestehende Setup- und Neustartprüfungen bleiben.

Der Adapter erfordert einen tatsächlich installierten XCMate-.87-Client (Draft #416). Kein Server konfiguriert, lokaler Token vorhanden, Opt-out oder ältere .86: sichere optionale Auslassung. Nach freiwilliger Wahl wird die .87-UI verwendet; Geräteverifier und Berechtigung verbleiben ausschließlich im privaten XCMate-Profil. Installer speichert nur `SKIPPED`, `PENDING`, `PAIRED`, `AUTH_FAILED` oder `SERVER_UNAVAILABLE`. Ein Pairingfehler macht die bestätigte Komponenteninstallation nicht zum Fehler. Pending kann im neuen separaten Menü fortgesetzt werden.

Host: drei Tests PASS, darunter 100 Zyklen mit je sieben Zuständen (700 Statusfälle), Schutz sämtlicher unveränderter .5.26-Paketmitglieder und deterministische ZIP-Reproduktion/CRC. Die UI-/Clientobjekte sind in diesen Tests injiziert. Kein echter Installerlauf oder echter Gateway. CI des eigenen `pairing527`-Jobs liefert Build-/Schutzbelege. Geerbte Repo-Workflows prüfen separat den unveränderten .86-Basisstand; deren Status nicht mit diesen drei Tests verwechseln.

Paket: `test-builds/0527/script.gsmedia.setup-0.5.27.zip`, SHA256 `56729fe34168d6e3102f4f91574a24abf88faad667b84bc129c0683305829efd`. Keine produktive Nutzung vor Server-/Client-/Android-Abnahme und ausdrücklicher Freigabe.

**BLOCKED:** Reale Serverimplementierung, Domain, TLS, authentifizierte Adminverwaltung/MFA, persistenter Replay-/Widerrufsschutz und Nutzungsbedingungenprüfung fehlen. Dieser Entwurf installiert oder provisioniert keinen Server. Automatische Tokenversorgung wird nicht behauptet. Alle physischen Android-Tests, 720p/1080p, echte Neubox, Altbox und Wiederaufnahme: **ANDROID_NOT_TESTED**.

Android-Abnahme nach Infrastrukturfreigabe: bestehende lokale Datei/Opt-out schützen; ohne Server überspringen; neue Anfrage→Pending→Später→Wiederaufnahme; authentifizierte Adminfreigabe→erlaubter TMDB-Test; Ablehnung/Ablauf/Widerruf/TLS-/Serverausfall→fester Status; keine Secrets in Journal/Logs; alle 48 Komponenten, BINGIE/Space Blue, Profile und Benutzerwidgets erhalten. Keine Neuinstallation bestehender Boxen.

Kein Merge und kein Release; .5.26 und alle .86-Kanäle unverändert.
