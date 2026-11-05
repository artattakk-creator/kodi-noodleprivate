# GS Media – XCMate 0.1.29.74 in regulärem und Pilot-Kanal

Datum: 2026-11-05

- Add-on-ID `plugin.video.xtreammate`, Version `0.1.29.74` auf aktuellem `main` aus PR #362.
- Installations-ZIP aus dem unveränderten, als Test-Build geprüften und im PR dokumentierten Paket `docs/XCMate/test-builds/02974/plugin.video.xtreammate-0.1.29.74.zip` kopiert.
- SHA-256 gemäß freigegebenem Testbericht: `8d3f08b1761e5f2ad6ffb061b24e6261c3b68ee35d197eab827e9fbac02f8e67`. Paket-Byteidentität der beiden veröffentlichten GitHub-Blobs wird über identische Git-Blob-SHA sichergestellt. **Keine Neuübersetzung oder Änderung des ZIP-Inhalts.**
- Regulär: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.74.zip`, `addons.xml` und `addons.xml.md5`.
- Pilot: `online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.74.zip`, `online-test/addons.xml` und `online-test/addons.xml.md5`.
- Andere Paketversionen, Repo-IDs, Installer, BINGIE-Branding und Provider-/Profildaten nicht verändert.
- Bestehendes CI-Release-Gate nach Merge #362 war **rot**: separate Branding-Test-Umgebung ohne `pytest`, historische Pilot-Snapshot-Konflikte sowie ein Legacy-Performance-Test mit 7.37 s bei 5-s-Schranke. Dies ist eine explizite **manuelle Veröffentlichung des bereits freigegebenen Test-ZIPs** auf Nutzerwunsch, kein erfolgreiches erneutes Full-CI.
- Android-TV- und echte TMDB-/Provider-Geräteabnahme stehen weiterhin aus. Test vorzugsweise auf Box B; keine Deinstallation/Konfigurationsrücksetzung.
- Das separate Programm `script.gsmedia.setup` bleibt bei 0.5.21. Der Hotfix 0.5.22 und Issue #364 werden mit diesem XCMate-Update **nicht** veröffentlicht.

Quelle: PR #362 und `docs/XCMate/test-builds/02974/README.md`.
