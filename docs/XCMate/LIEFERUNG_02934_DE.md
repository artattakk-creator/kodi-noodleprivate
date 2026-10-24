# XCMate 0.1.29.34 – Review-Testpaket

Draft #158 · Basis main .33 `6bb96547ec469e62c5f69e23a928842021bab4c4` · geprüfter Code/Teststand `fee5b6404d28c8441b0595f96ec6f9e137f3c760`.

- **1112 Hosttests PASS**, 0 Fehler, 0 Failures, 0 übersprungene Tests; darunter 19 neue Lifecycle-/Handoff-Fälle. Laufzeit 117,605 s.
- Kodi-Sprachen DE/EN je 788 Kontexte PASS, Python-Syntax PASS.
- ZIP: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.34.zip`, 2371950 Bytes, 255 Dateien.
- SHA256: `39a466eb4b2813d2de654ce9e174f1d862f2bac581fc1dd235941a58722c24d1`.
- CRC, sichere Pfade, jede Datei bytegleich zum Source, Python-AST und deterministisch reproduzierbarer ZIP-Neubau PASS. Kein Profil, keine DB/Rohlogs/Credentials im Paket.
- Schutzprüfung: 241 übrige Add-on-Dateien, 41 normale Medienmethoden, alle 98 Space-Premium-Bilder und 62 Dateien fremder WIP-Arbeitsstände erhalten. Production-Indizes und Release-Workflow unverändert, bisheriges .33-ZIP bleibt erhalten.

Download im Draft-Branch bzw. dessen GitHub-Actions-Reviewartefakt. Keine automatische Repository-Veröffentlichung/OTA. Über vorhandener .33 installieren; keine Deinstallation, kein Downgrade, kein Reset.

Nur **G1–G4**, jeweils **NOT_TESTED**, nach `ANDROID_ABNAHME_02934_DE.md` durchführen. Kodi-C++-Quellprüfung und Hostmodell ersetzen keine native Android-Abnahme. Bestehende Android-/Langzeit-PASS bleiben historisch unverändert. Ausführlicher Hostoutput: `TESTLOG_02934.txt`; Paketbericht: `TESTERGEBNISSE_02934.json`; Analyse: `URSACHENANALYSE_GUIDE_HANDOFF_02934_DE.md`.

Poster #111 separat als Dokumentations-/Reparaturentwurf **#157**, noch kein Poster-Codefix und kein implementierter TMDb-Fallback. #98 folgt nach stabiler Suche und Guide-Start; Downloads/Aufnahmen bleiben nachrangig. Kein Merge/Release/Issue-Schluss ohne ausdrückliche Freigabe.
