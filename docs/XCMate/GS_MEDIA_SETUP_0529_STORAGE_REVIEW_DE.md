# GS Media Setup .5.29 – separater Entwurf für #443/#445

Basis: Main 002ba995, veröffentlichte .5.26 ZIP (SHA256 5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af). Keine Übernahme der offenen .5.27/.5.28-Branches. Keine Änderung an produktiven Paketen, Katalogen oder installierten Geräten.

Nach vollständiger Komponenteninstallation, vor Skinaktivierung und Prefetch: Installer schließt seinen Fortschrittsdialog, übergibt an das eigene native XCMate-Speicherfenster und wartet auf eine Nonce-gebundene Antwort. Aktive EPG-Datenbanken bleiben intern. Bild-EPG sowie interner/USB/NAS/später-Wunsch werden im XCMate-Kontext ausgewählt. Kopie/Hash-/Bildprüfung und Neustart gehören zum vorhandenen XCMate-Migrator; keine Erfolgsmeldung für unvollständige Migration.

Frische Installerabläufe erhalten ein kleines atomar gespeichertes Auswahljournal. Bereits bestehende Installerzustände ohne dieses Journal bleiben unverändert. Das Skript führt weder erneut die 48 Komponenten aus noch importiert es fremde Add-on-Globals. .91 oder ältere XCMate-Versionen: Auswahl ausdrücklich vertagt, bestehende Bildfreigaben geschützt. Kompatibel mit dem Source-Entwurf .92, allein kein Ersatz dafür.

Host: 8/8 PASS, echte Dateien und ZIPs; Upgrade ohne Journal, frischer Nonce-Handoff, zu alte XCMate-Version, vertagte Wahl, Symlink/defektes Journal, Reserveblockade, reproduzierbares Paket, identische 31 unveränderte Basismitglieder. Nur addon.xml und setup_auto_ui50.py geändert, setup_storage92.py ergänzt. Keine Token/Providerdaten im Paket.

Android/Kodi-End-to-End: ANDROID_NOT_TESTED. Vor Freigabe mit .92 auf einer ausdrücklich dafür freigegebenen Testinstallation prüfen: Ja/Nein/Später, USB fehlt, gleicher Pool, echter USB mit gemessener Reserve, NAS unbekannte Kapazität/Offline, Abbruch/Neustart, Wiedereintritt ohne erneute Auswahl, Erhalt aller 48 Komponenten und bestehenden Nutzerwerte. Bestehende Boxen nicht neu installieren.

ZIP: test-builds/installer0529/script.gsmedia.setup-0.5.29.zip. SHA256: 674eaea4254395a5963c24012b09f9a59632cb8bb57b29f652c65cf9f77ff30e.

Status: DRAFT, abhängig vom XCMate-.92-Speicherfenster. Kein Merge und keine Veröffentlichung beauftragt.
