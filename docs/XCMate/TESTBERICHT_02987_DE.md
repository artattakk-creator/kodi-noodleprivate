# XCMate 0.1.29.87 – Testbericht

Status: **Entwicklung / vollständige Verifikation läuft**, kein Release, kein Android-PASS.

- Basis: `48cbdc2fbdb32d2f0225b8db2398b25b4fcc4d6e`.
- Gezielte übernommene GUI/Navigation/Mapping/Speichertests: **104 PASS**.
- Neue Zuordnungs-/Logo-/Speichertests verwenden reale temporäre Dateien, atomare Readbacks und injizierte, ausdrücklich synthetische API-/Volume-Identitäten. Keine echten Providerzugänge, keine Android-Poolbehauptung.
- Komplette Hostsuite: läuft. Früher Baseline-Versuch im knappen Host-`/tmp` scheiterte an sieben realen Host-Speicherpreflights; diese Werte sind kein Android-Befund. Wiederholung mit Testdaten unter `/workspace` und SQLite-Temporärdaten im eigenen `/dev/shm`-Ordner.
- GitHub-CI und tatsächlicher Linux-Kodi-Renderer 720p/1080p: ausstehend. Unabhängige synthetische Fremdplugins, echte native Directory-/Fokus-/Texture-/Pixelprüfungen und Neustarts; keine physischen Android-Tests.
- Physische Android-Gates A/S/L/H/D2/F/G/C/E/I: **ANDROID_NOT_TESTED**.
- Layout-Rohreferenz: **REFERENZBILD_NICHT_VERFÜGBAR**.

Die finale ZIP-Prüfsumme, aktuelle CI-Links, Messwerte und vollständigen Fallzahlen werden nach Abschluss ergänzt. Der Testkandidat liegt unter `test-builds/02987/`, sein `.sha256` gehört ausschließlich zu diesem Build. Original/Pilot/NeoDark3 .86 und Installer 0.5.26 bleiben unverändert.
