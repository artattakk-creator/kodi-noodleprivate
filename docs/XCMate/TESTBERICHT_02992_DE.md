# Testbericht .92 – laufende vollständige Prüfung

Gezielt bestanden: 29 neue .92-Tests (Speicher/Metadaten/Integrität/Mapping/Home-Filter/Releasevertrag), 40 Tests in Speicher-/Mapping-/externen Bildmodulen, 81 bestehende Kernprüfungen (Migration inkl. 20.000 Bildern, EPG-Grenzen, Bildsuche, sechs Reihen), 39 Spinner-/Sechsreihenprüfungen. Diese Gruppen überlappen; nicht als Summe unterschiedlicher Tests ausgeben. Sprachkatalogvalidierung PASS.

Vollständige Hostsuite wird auf dem endgültigen Source ausgeführt; GitHub-CI folgt auf dem Draft-PR. Erster Gesamtlauf abgebrochen, weil er einen inzwischen korrigierten EPG-Syntaxfehler enthielt. Nicht als PASS gewertet. Historische Publikationsprüfungen wurden auf den tatsächlich veröffentlichten Main-Stand aktualisiert; .91-Artefaktprüfungen bleiben erhalten, .92 hat eigene vollständige Paket-/Sourceprüfungen.

Lokaler nativer Kodi-Versuch: BLOCKED_ENV_STORAGE, Docker apt konnte wegen fehlenden Platzes im Test-Overlay nicht installieren (vor Kodi-Start). Kein Android- oder Anwendungs-FAIL daraus abgeleitet. Native Linux-Kodi-720p/1080p-Läufe in GitHub Actions auswerten, besonders tatsächliches Down 2530→2540; keine Move-Mocks, geänderten Sollwerte oder zusätzlichen Skips.

Echte RK3528-/Android-Tests: vollständig ANDROID_NOT_TESTED. Reale interne Entlastung, USB-Bilddarstellung und Player-Freeze werden erst am Gerät abgenommen. Implementierungsbericht listet OPEN-Punkte ausdrücklich; insbesondere kein behaupteter Fix eines nativen Decoderhangs.

## Nachprüfung der ersten vollständigen Läufe

Erster abgeschlossener Source-Stand 97555c1e: 3.898 Hosttests ausgeführt. CI: 27 FAIL, keine ERROR; lokal zusätzlich zwei Speicherfehler der Testumgebung. Die FAILs waren veraltete Freeze-Baselines nach der bereits genehmigten .91-Veröffentlichung, alte Reserve-Fault-Injection an der nun ersetzten Bulk-Prüfung, fehlende native Speicher-Kategorie/Icon-Picker und der beauftragte .92-Migrationsdelta im historischen Rohbyte-Guard. Diese Prüfungen wurden nicht entfernt/übersprungen: Baseline fest auf 002ba995, negative Speicherungstests an die tatsächliche begrenzte Metadatenprüfung gebunden, zusätzliche .92-Scopeprüfung bleibt streng.

Nach Korrektur: 169 historische Scopeprüfungen PASS, 119 betroffene Speicher-/Mapping-/Einstellungsprüfungen PASS; danach 56 aktuelle Speicher-/Release-/Icon-/Native-Einstellungsprüfungen PASS. Gruppen überlappen. Zweiter kompletter finaler Lauf erforderlich, bis dahin keine vollständige grüne CI behaupten.

Lokale Großlast-Nachprüfung PASS, nachdem ausschließlich eigene vollständig gespeicherte Installer-Worktree-/fehlgeschlagene Docker-Testartefakte entfernt wurden: 200.005 Filme + 200.005 Serien, je 109.380.521 HTTP-Bytes, DB 309.526.528 / 621.731.840 Bytes; 27,404 / 27,409 s, Peak-RSS 33.008 KiB. Keine reale Android-Speicherbereinigung daraus ableiten.

Native Linux Kodi 21.2, erster RC: tatsächlicher Home75-Fokus und Hero in 720p/1080p PASS, zwei echte Kodi-Neustarts mit 88/24/24 Inhalten und unveränderten 34 geschützten Dateien PASS. 60 Stop-/ACK-Zyklen PASS. CI-Run 43389588346 scheiterte anschließend an den inzwischen korrigierten historischen Kanalprüfungen. Sechs-Reihen-720p inklusive Audiowiedergabe PASS; 1080p-Audio FAIL mit ActiveAE-InitSink/BusyDialog. Der Testcontainer wird nun an seinen ausdrücklich erzeugten PCM-Sink xcmate_native gebunden; keine Abschwächung der echten Audio-Clock-/ACK-Prüfung. Neuer CI-Nachweis steht aus.
