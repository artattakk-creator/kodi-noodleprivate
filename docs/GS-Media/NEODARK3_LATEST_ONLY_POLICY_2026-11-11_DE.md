# NeoDark3 – nur die aktuelle XCMate-ZIP im öffentlich sichtbaren Hauptverzeichnis

Stand 11.11.2026. Nutzerwunsch: keine historische XCMate-Versionsliste in `online-test/index.html`; das Verzeichnis `online-test/` soll genau eine **aktuell veröffentlichte** direkte XCMate-ZIP plus ihre `.sha256` enthalten. Repositories und Installer bleiben unberührt. `0.1.29.90` ist derzeit nur Draft-PR #431 und **nicht freigegeben**; aktuell veröffentlicht ist `0.1.29.89`.

## Einmalige Bereinigung
- Direkt unter `online-test/` wurden XCMate `.78` und `.80` bis `.88` (10 ZIP-Dateien und 10 passende `.sha256`) entfernt.
- Direkt `online-test/plugin.video.xtreammate-0.1.29.89.zip` + `.sha256` erhalten.
- `online-test/index.html` enthält nur die XCMate-.89-ZIP, `repository.gsmedia.pilot-1.9.12.zip`, `repository.gsmedia-1.8.1.zip` und `script.gsmedia.setup-0.5.26.zip`.
- **Andere Verzeichnisse**, insbesondere `online-test/plugin.video.xtreammate/` (Pilot und Rollback), `plugin.video.xtreammate/` (regulär), `docs/XCMate/test-builds/`, andere Repos, externe Abhängigkeiten, Benutzer-/Kodi-Daten **nicht** geändert. Bereits verwendete historische direkte URLs werden künftig nicht mehr verfügbar sein; die ältere ZIP-Historie bleibt in Git/GitHub-Releases und separaten Kanalordnern nachvollziehbar.

## Pflicht bei jeder zukünftigen XCMate-Veröffentlichung
1. Nur nach expliziter Releasefreigabe den Pilot-Katalog `online-test/addons.xml` auf die neue Version umstellen.
2. Neue, geprüfte ZIP und deren passende SHA256 zunächst in reguläres/Pilot-Archiv stellen; **direkt in `online-test/` nur die neue veröffentlichte Version**.
3. Die bisherige direkte ZIP und SHA256 aus `online-test/` entfernen; keine anderen ZIP-Dateien löschen.
4. `online-test/index.html` **ersetzen**, nicht die alte Liste um weitere XCMate-Versionen verlängern.
5. `python3 tools/verify_neodark3_latest_only.py` erfolgreich ausführen; GitHub-Action `neodark3-latest-only.yml` prüfen.
6. Repositories, Installer- und Fremd-Add-on-Dateien unangetastet lassen. Neuen Release und GitHub Pages/Onlinequelle nach dem Merge prüfen.

**Nicht** den .90-Draft automatisch veröffentlichen. Diese Bereinigung ist nur eine Verzeichnis-/Installationsquellenpflege, kein XCMate-Code-Release.
