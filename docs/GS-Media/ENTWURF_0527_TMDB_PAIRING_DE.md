# GS Media Setup 0.5.27 – separater optionaler Pairing-Entwurf

Auftrag #417 / #415 P0-K. Basis `6c748388e04ef021de0e6e7df193c1ab812c260c`, unverändertes veröffentlichtes Setup .5.26 SHA256 `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`. Kein Installer wird ausgeführt, kein Katalog aktualisiert, keine Box verändert.

Der Review-Builder liest ausschließlich das hashgeprüfte bestehende .5.26-Paket. Genau fünf Mitglieder unterscheiden sich: neue Versionskennung; optionaler Schritt nach bestätigten 48 Komponenten vor Abschluss; separater Menüpunkt zum späteren Fortsetzen; Clientadapter; ein unsichtbares öffentliches Statusfeld. Alle übrigen Mitglieder bleiben bytegleich. Keine neue Skin-/Komponenten-/Tokeninstallation. Bestehende Setup- und Neustartprüfungen bleiben.

Der Adapter erfordert einen tatsächlich installierten XCMate-.87-Client (Draft #416). Kein Server konfiguriert, lokaler Token vorhanden, Opt-out oder ältere .86: sichere optionale Auslassung. Nach freiwilliger Wahl wird die .87-UI verwendet; Geräteverifier und Berechtigung verbleiben ausschließlich im privaten XCMate-Profil. Installer speichert nur `SKIPPED`, `PENDING`, `PAIRED`, `AUTH_FAILED` oder `SERVER_UNAVAILABLE`. Ein Pairingfehler macht die bestätigte Komponenteninstallation nicht zum Fehler. Pending kann im neuen separaten Menü fortgesetzt werden.

Host: vier Tests PASS, darunter 100 Zyklen mit je sieben Zuständen (700 Statusfälle), Schutz sämtlicher unveränderter .5.26-Paketmitglieder und deterministische ZIP-Reproduktion/CRC. Die UI-/Clientobjekte sind in diesen Tests injiziert. Kein echter Installerlauf oder echter Gateway. CI des eigenen `pairing527`-Jobs liefert Build-/Schutzbelege. Geerbte Repo-Workflows prüfen separat den unveränderten .86-Basisstand; deren Status nicht mit diesen vier Tests verwechseln.

Paket: `test-builds/0527/script.gsmedia.setup-0.5.27.zip`, SHA256 `c3e7b649d742c80fce7685a9f31051bfac09736ae08153b04ba74377eac343d6`. Keine produktive Nutzung vor Server-/Client-/Android-Abnahme und ausdrücklicher Freigabe.

**BLOCKED:** Reale Serverimplementierung, geschützte API auf der inzwischen benannten Domain gs-media.eu, TLS-/Backendkonfiguration, authentifizierte Adminverwaltung/MFA, persistenter Replay-/Widerrufsschutz und Nutzungsbedingungenprüfung fehlen. Dieser Entwurf installiert oder provisioniert keinen Server. Automatische Tokenversorgung wird nicht behauptet. Alle physischen Android-Tests, 720p/1080p, echte Neubox, Altbox und Wiederaufnahme: **ANDROID_NOT_TESTED**.

Android-Abnahme nach Infrastrukturfreigabe: bestehende lokale Datei/Opt-out schützen; ohne Server überspringen; neue Anfrage→Pending→Später→Wiederaufnahme; authentifizierte Adminfreigabe→erlaubter TMDB-Test; Ablehnung/Ablauf/Widerruf/TLS-/Serverausfall→fester Status; keine Secrets in Journal/Logs; alle 48 Komponenten, BINGIE/Space Blue, Profile und Benutzerwidgets erhalten. Keine Neuinstallation bestehender Boxen.

Kein Merge und kein Release; .5.26 und alle .86-Kanäle unverändert.

Nachtrag K1: Die .87-UI erklärt die Unterschiede zwischen einmaligem privatem Tokenimport (Phase 1) und stärkerem Gateway. Gewünschtes Ziel ist gs-media.eu; produktive API/Hostingrechte fehlen weiterhin. Ein erfolgreicher neuer Import wird anschließend als PAIRED im öffentlichen Installerstatus geführt; bereits vorher vorhandene lokale Zugänge werden SKIPPED. Erster eigener CI-Lauf PASS: https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42882010440 – die neue Fassung wird separat erneut geprüft.

Die drei älteren HTML-Freeze-Tests .83/.84/.85 referenzierten nach der bereits veröffentlichten .86 noch den .85-Index. Sie vergleichen jetzt exakt den genehmigten .86-Stand `48cbdc2` (keine Aufweichung und keine Katalogänderung). Dieselbe Testkorrektur ist in #416 enthalten. Keine historischen Testmethoden entfernt.
