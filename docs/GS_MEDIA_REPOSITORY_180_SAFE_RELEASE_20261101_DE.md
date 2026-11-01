# GS Media Repository 1.8.0 – sicheres kumulatives Update

Stand: 01.11.2026 · Basis: `main` mit XCMate 0.1.29.66 · Scope: **nur Repository-ID, Version, Katalog-Metadaten und Branding**.

## Worum es bei 1.8.0 geht

- `repository.gsmedia` bleibt dieselbe installierte Kodi-Add-on-ID.
- Versionsnummer von 1.7.0 auf 1.8.0; Kodi erkennt die höhere Version regulär über die Add-on-Verwaltung.
- Neues Icon (Neon-Cinema/GS Media) wird bei jedem Paketbau aus `tools/render_gsmedia_icon.py` erzeugt, als `repository.gsmedia/icon-1.8.png` veröffentlicht und in `repository.gsmedia-1.8.0.zip` mitgeliefert.
- Alle **acht** zuvor vorhandenen Katalog-URLs, ihre ZIP-Quellen und der Omega-Skin-Zweig bleiben exakt unverändert.
- XCMate bleibt **0.1.29.66**, Noodle Private unverändert. Kein Wizard-/Skin-/Addon-Update wird durch dieses Release zwangsinstalliert.
- Durch das vorhandene GitHub-Actions-Publishing werden ZIP und `addons.xml` zusammen auf `main` veröffentlicht; das im Add-on definierte `addons.xml.md5` und der Versionseintrag machen 1.8.0 im Kodi-Repository erkennbar.
- **Keine** Änderungen an Kodi-`userdata`, `addon_data`, Tokens, TV-Portalzugängen, EPG oder BINGIE-Konfiguration.

## Warum der ursprüngliche PR #303 noch nicht die Freigabe ist

Der umfassendere 1.8-Entwurf unter PR #303 führte fremde Download-Pins für MP3 Streams Echoed, SHOUTcast/Pluto und eine zusätzliche TMDB-Helper-Quelle ein. Sein Build scheiterte reproduzierbar an einem 404 beim MP3-Streams-Download. Die zusätzliche jurialmunkey-Quelle bietet eine wesentlich neuere TMDB-Helper-Version an als die derzeit mit BINGIE 2.2.3 getestete Version 5.4.16. Der Abhängigkeitspfad ist noch nicht auf Android abgenommen. Deshalb werden diese Änderungen ausdrücklich **nicht** in den stabilen 1.8.0-Releasescope genommen; spätere Freigabe nach Lizenz-/Upstream-/Android-Prüfung möglich.

### Kodi-Update für eine vorhandene Box

1. Vorherige funktionierende Einstellungen/Backup aufbewahren; keine Deinstallation.
2. Kodi → Add-ons → Meine Add-ons → Add-on-Repositories → **GS Media Repository**.
3. `Versionen` beziehungsweise `Aktualisieren` auswählen; GS Media 1.8.0 aus der bestehenden Quelle installieren, wenn Kodi es im Katalog anbietet. Je nach Auto-Update-Einstellung erfolgt die Aktualisierung automatisch.
4. Nach Repository-Refresh `repository.gsmedia 1.8.0` und das neue Icon kontrollieren; XCMate muss weiterhin 0.1.29.66 sein.
5. Wenn 1.8.0 nicht angeboten wird: Repository-Aktualisierung anstoßen/Quelle prüfen. ZIP des Repositorys nur bei verifiziertem Build verwenden. Keine App-Daten löschen.
6. Ein Repository-Update behebt **nicht** die XCMate-.66-P0-Stream- und EPG-Fehler; diese sind separat unter #307 mit .67 geplant.

## Abnahme- und Veröffentlichungsregeln

- `python -m unittest tests/test_repository_layout.py tests/test_gsmedia_repo_180.py -v` und der vollständige vorhandene CI-Workflow müssen grün sein.
- Kodi-ZIP-Prüfung: korrektes Add-on `repository.gsmedia`, Version 1.8.0, ZIP-CRC, valides PNG 256×256 und `addons.xml`-Verfügbarkeit.
- GitHub `main`-Commit des Builds und der erzeugte Repository-Index müssen kontrolliert werden.
- Reale Kodi-21.3-ARM32-Installation ist **NOT_TESTED**, bis ein Nutzer sie auf der Box bestätigt.

Verknüpft: #305 Repository Lite/Wizard Planung; #307 XCMate .66 Live-TV-EPG P0; #303 alter, nicht integrierter Drittanbieter-Entwurf.
