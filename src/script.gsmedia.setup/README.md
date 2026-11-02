# GS Media Setup 0.2.0 – aktive Vorprüfung / Draft

Stand 02.11.2026. Dieser Branch basiert auf main/XCMate 0.1.29.68 und portiert
den ursprünglichen Wizard-Entwurf aus Draft-PR #306 auf den aktuellen Stand.

## Implementiert
- Vier Installationsprofile: Basis (BINGIE + XCMate), Medien, Musik, Kombiniert.
- Kodi Addons.GetAddons per read-only JSON-RPC: installierte Version und enabled.
- UNKNOWN bei RPC-Fehler (nie als fälschlich fehlend auslegen).
- Historische direkte/teilweise transitive Manifest-Abhängigkeiten: sortiert,
  sodass bekannte Dependencies vor konsumierenden Add-ons stehen.
- Abgleich gegen den aktuell lokal installierten Add-on-Bestand.
- Konservative Paketquellen-Gates: BINGIE-Review-Patches, MP3 Echoed 404,
  unvollständige xVAULT/Cumination/Fremd-Abhängigkeiten bleiben BLOCKED.
- Tatsächliche BINGIE-Abhängigkeiten im alten Snapshot: 13 direkte Imports.
- XCMate-Manifest auf aktueller main-Basis mit PIL.
- Kein Autostart, keine Downloads, kein InstallAddon, keine Änderungen an Kodi.

## Nicht implementiert / BLOCKED
Kein installierender Wizard, kein vollständiger rekursiver originaler
Upstream-Manifest-Resolver, kein gepinnter ZIP/SHA-Katalog, keine Paket-
Verteilung, kein GS-Media-BINGIE-Skin-Fork, keine Skin-Aktivierung, kein
Resume nach Kodi-Neustart, kein Backup/Restore, keine automatische Reparatur.
Eine lokale Kodi-Abnahme steht aus.

## Nächste Entwicklungsphase
1. Repository-1.8.2-Katalog/Abhängigkeitsmatrix aus PR #312 (originale ZIPs,
   Versionen, SHA256, Lizenzen und weitere Kodi-21.3-ARM32-Tests) prüfen.
2. BINGIE-MOD-2.2.3-Basis mit GS-Media-Patches rechtssicher als getrenntes
   versioniertes Paket/Adapter bereitstellen; keine installierten Skins patchen.
3. MP3 Streams Echoed 2026.1.0 aus legaler Originalquelle oder geprüftem
   Quellbackup rekonstruieren; keine personenbezogenen privaten Backups uploaden.
4. Auf bestätigte Paketquellen dann erst den nutzerbestätigten Kodi InstallAddon
   Executor, Fortschrittsjournal, Resume und Healthchecks aufsetzen.
5. Vor irgendeinem Merge GitHub-CI, Kodi 21.3 und echte Android ARM32-Tests.

Referenzen: Issue #317 (Master), #305, #315, Draft PR #306, #312.
Kein Merge zu main ohne separate Nutzerfreigabe.
