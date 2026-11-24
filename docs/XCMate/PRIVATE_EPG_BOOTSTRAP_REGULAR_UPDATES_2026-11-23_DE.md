# XCMate 0.1.29.101 (privater Erststart) → reguläre Kodi-Updates ohne Token-Leak

Status 23.11.2026: Entwicklungsbranch / Draft-PR #510, Code + Offline-CI geprüft. **Nicht auf Android/LG freigegeben, nicht nach Main gemergt.**

## Nutzerentscheidung
- Ein Read-only-GitHub-PAT darf im **privat herunterladbaren Erstinstallations-ZIP** liegen. Die ZIP ist dadurch ein **Secret**. Wer sie besitzt, kann den Token extrahieren und das private EPG-Repository bis zum Widerruf lesen. Der PAT hat ausschließlich **Contents: read** auf `artattakk-creator/xcmate-epg-private`.
- Der Token darf **nicht** in das öffentliche Repository `artattakk-creator/kodi-noodleprivate`, dessen `addons.xml`, normalen XCMate-Installations-ZIP oder Logs gelangen.
- Es soll trotzdem der normale Kodi-Repository-Updateprozess funktionieren: `src/plugin.video.xtreammate` → `tools/build_repository.py` → `addons.xml` / `addons.xml.md5` → versioniertes `plugin.video.xtreammate-<version>.zip`.

## Tatsächlich implementierter Mechanismus
1. **Privater Build**: Workflow im privaten EPG-Repo `.github/workflows/build-xcmate-private-pilot.yml` checkt fest gepinnten öffentlichen Source-Commit `c3d22cce59de68139e60a82bb244f0d79f187165` aus. GitHub Actions Secret `XCMATE_EPG_PRIVATE_READ_TOKEN` wird nur beim privaten Paketbau als `resources/private/xcmate_epg_read_token.txt` hinzugefügt. 3-Tage-Artefakt, kein öffentliches Release, keine Schreibrechte fürs Quell-Repo.
2. **Erstinstallation**: Kodi `service.py` ruft bei jedem Dienststart `ensure_local_token(epg_agent_profile())` auf. `resources/lib/epg_agent_token_bootstrap.py` prüft den verpackten Token und legt ihn **einmalig** als `special://profile/addon_data/plugin.video.xtreammate/epg-agent/reader-token.txt` ab (Unix-Dateimodus 0600, atomare Erzeugung). Ein bereits vorhandener lokaler Token wird nie überschrieben. Kein Tokentext in Logs oder GUI.
3. **Reguläre Folgeversionen**: Das öffentliche Paket ist tokenfrei. XCMate greift trotzdem auf die **persistente** `addon_data`-Datei zu. Normale Kodi-Add-on-Updates erhalten `addon_data`, sofern der Nutzer nicht explizit Add-on-Daten löscht.
4. **Public-Build-Guard**: `tools/build_repository.py` stoppt den Build, wenn im öffentlichen Quellstaging irgendein `resources/private`-Inhalt auftaucht. Dadurch kann die private Token-Datei nicht versehentlich per GitHub-Publish verteilt werden.
5. **Tests**: `tests/test_epg_agent_token_bootstrap.py` prüft private Erstinstallation, anschließendes tokenfreies Update, vorhandenen Token erhalten, ungültige Token/Symlinks ablehnen, private Datei-Rechte und den Public-Build-Guard. CI-Workflow `XCMate EPG Agent full private transport contract` inklusive Schema-5-Vertrag **PASS** (Run 45197290584).

## Grenzen / Release-Gates
- **Privater Paketbau muss nach dieser Änderung erneut gestartet werden.** Das zuerst heruntergeladene private `0.1.29.101`-ZIP stammt aus der vorherigen Codefassung und sichert den Read-Token **noch nicht** beim Kodi-Service-Start. Nicht als endgültiges Erstinstallationspaket nutzen.
- Das normale Kodi-Repository zeigt aktuell eine **ältere veröffentlichte Version** und die reguläre Veröffentlichung ist durch `tools/release_channel75.py` für neuere Versionen **ohne reale Android-PASS-Freigabe** gesperrt. Diese Sperre nicht umgehen.
- Nach privater Testinstallation `0.1.29.101`: Nachweis, dass `reader-token.txt` unter Kodi-Userdata liegt (ohne Tokeninhalt zu zeigen), Schema-5-EPG (all/de/at/en/es/pl, artwork/standard) funktioniert und der Provider-EPG erhalten bleibt. Zusätzlich erster Token-freier Upgrade-Test mit **höherer Version**, z. B. `0.1.29.102`, ohne dass Credentials verloren gehen.
- Erst danach nach Review/Freigabe `main`, Katalog-Metadaten und versioniertes Public-ZIP aktualisieren. Android-/LG-Endgeräte und Pilot/NeoDark-Kanäle gesondert prüfen.
- Ein **neu installierter Client ausschließlich aus dem öffentlichen Repository** besitzt noch keinen Token und kann ohne einmalige private Bereitstellung keinen privaten GitHub-EPG lesen. Automatische neue Gerätebereitstellung ohne einmalige private Provisionierung erfordert künftig einen echten geschützten Auth-Distributionsweg; das wird hier nicht behauptet.
