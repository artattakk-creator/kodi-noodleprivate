# Testbericht .92 – laufende vollständige Prüfung

Gezielt bestanden: 28 neue .92-Tests (Speicher/Metadaten/Integrität/Mapping/Home-Filter/Releasevertrag), 40 Tests in Speicher-/Mapping-/externen Bildmodulen, 81 bestehende Kernprüfungen (Migration inkl. 20.000 Bildern, EPG-Grenzen, Bildsuche, sechs Reihen), 39 Spinner-/Sechsreihenprüfungen. Diese Gruppen überlappen; nicht als Summe unterschiedlicher Tests ausgeben. Sprachkatalogvalidierung PASS.

Vollständige Hostsuite wird auf dem endgültigen Source ausgeführt; GitHub-CI folgt auf dem Draft-PR. Erster Gesamtlauf abgebrochen, weil er einen inzwischen korrigierten EPG-Syntaxfehler enthielt. Nicht als PASS gewertet. Historische Publikationsprüfungen wurden auf den tatsächlich veröffentlichten Main-Stand aktualisiert; .91-Artefaktprüfungen bleiben erhalten, .92 hat eigene vollständige Paket-/Sourceprüfungen.

Lokaler nativer Kodi-Versuch: BLOCKED_ENV_STORAGE, Docker apt konnte wegen fehlenden Platzes im Test-Overlay nicht installieren (vor Kodi-Start). Kein Android- oder Anwendungs-FAIL daraus abgeleitet. Native Linux-Kodi-720p/1080p-Läufe in GitHub Actions auswerten, besonders tatsächliches Down 2530→2540; keine Move-Mocks, geänderten Sollwerte oder zusätzlichen Skips.

Echte RK3528-/Android-Tests: vollständig ANDROID_NOT_TESTED. Reale interne Entlastung, USB-Bilddarstellung und Player-Freeze werden erst am Gerät abgenommen. Implementierungsbericht listet OPEN-Punkte ausdrücklich; insbesondere kein behaupteter Fix eines nativen Decoderhangs.
