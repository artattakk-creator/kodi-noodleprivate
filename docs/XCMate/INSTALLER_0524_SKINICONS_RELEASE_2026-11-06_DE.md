# GS Media Media Center Installer 0.5.24 – Skin Icons 1.0.5 (06.11.2026)

**Status:** CODE/PACKAGE/GITHUB-RELEASE PASS; **ANDROID NOT TESTED**. Die lokale Kodi-Geräteabnahme ist ausdrücklich offen.

## Android-Auslöser
Beim Wiederaufnehmen von Installer 0.5.23 stoppten **19 von 48 Komponenten** mit
`KODI_CATALOG_VERSION_TOO_OLD:resource.images.skinicons.wide`.

BINGIE MOD 2.2.3 verlangt `resource.images.skinicons.wide >= 1.0.5`; der globale Kodi-Katalog kann die ältere offizielle Version 1.0.3 melden, obwohl das BINGIE-Omega-Originalrepository 1.0.5 enthält. Der zuvor pauschale globale Katalogvergleich hat den Abbruch erzeugt.

## Technische Korrektur
- Kumulative Basis: 0.5.21 + vollständige 0.5.22-Overlays + 0.5.23-Overlays + vier 0.5.24-Overlays. Keine Rücknahme früherer Fixes.
- `setup_auto50.rows()` ordnet die erforderliche originale Resource in genau dieser Version dem vorhandenen GS Media Pilot zu.
- `setup_auto_ui50.py` verwendet bei fehlender Resource **und** bei bestehender älterer Version den nativen Pilot-Parent `script.gsmedia.upgrade.resource.images.skinicons.wide`. Dessen Version wird getrennt gegen 0.1.0 geprüft; anschließend muss Kodi die Ziel-Resource **mindestens 1.0.5, aktiviert** über JSON-RPC bestätigen. Ein bestehender passender 1.0.5-Bestand wird übersprungen.
- `setup_origin_guard52.py` gestattet vorübergehend und nur nach Setup-Zustimmung für diese benannte Resource die Kodi-Quellenauswahl *Any repository*. Automatische Updates werden in dieser Zeit pausiert, beide Einstellungen mit atomarem Journal gesichert und bei Erfolg/Fehler/Neustart wiederhergestellt. Keine dauerhafte Änderung.
- Das Original-ZIP wird unverändert aus dem Upstream nach **GS Media Pilot** gespiegelt; Build verweigert Veröffentlichung bei abweichendem Git-Blob, CRC, Pfadlayout, Add-on-ID oder Version. Keine Umbenennung des Originals.
- Zuvor installierte xVAULT-/xImage-Komponenten, die 48er-Journaldatei, EPG, Widgets und Benutzer-Player bleiben bestehen.

## Original-Resource
- Herkunft: [AchillesPunks BINGIE Omega](https://github.com/AchillesPunks/repository.titan.bingie.mod)
- Paket: `resource.images.skinicons.wide-1.0.5.zip`
- SHA-256: `1b4469973407cc46eb80d227877cdac5f755fcb562c2b0f9129a149e1d73596d`
- Geprüfter originaler Git-Blob: `cf9edf81fe32b2262f6fe296e0db04361697b7c2`
- [Bereitgestellte ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/resource.images.skinicons.wide/resource.images.skinicons.wide-1.0.5.zip)
- Ressourceneintrag in `online-test/addons.xml`; eigenes SHA256-File im Add-on-Ordner; `manifest.json` enthält Herkunft und Pin.

## Installer 0.5.24 – drei Kodi-Installationswege
Alle drei ZIP-Kopien sind **byteidentisch** (Git-Blob `5950623c777af7074056de84c0579c394ebf9dc3`, SHA256 `48a29757ca295cac3ca98f406b4e53de5c855729b0d2ad812aeee8605cda2267`):
1. [Regulärer GS Media Add-on-Datadir](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/script.gsmedia.setup/script.gsmedia.setup-0.5.24.zip)
2. [GS Media Pilot Add-on-Datadir](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.24.zip)
3. [NeoDark3 ZIP-Direktzugang](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup-0.5.24.zip)

*Hinweis: Drei Installationszugänge sind keine drei separaten GitHub-Repositories.* Zwei Kodi-Kataloge verweisen innerhalb von `artattakk-creator/kodi-noodleprivate` auf ihre jeweiligen ZIP-Dateien. NeoDark3 ist ein zusätzlicher Direktzugang zum Pilot-Verzeichnis.

## Nachweise
- Fix-PR [#377](https://github.com/artattakk-creator/kodi-noodleprivate/pull/377); Merge `8d67509054906ee5e4a30d5e218f78436c6c3503`.
- PR-GitHub-Actions-Lauf `42267657341`: **SUCCESS** einschließlich echtem Upstream-Download, Pinned-Blob, ZIP-CRC, XML-Katalog- und MD5-Prüfungen.
- Vollständige Veröffentlichung auf main `51ddf5a1b2a6bc160c4782d6034de3bad3442188` mit beiden `addons.xml`, MD5, NeoDark3-Index, Manifest und allen drei ZIP-Kopien.
- Version 0.5.23 bleibt in Pilot und regulärem Add-on-Datadir erhalten; keine vorhandenen ZIPs überschrieben.
- Ursprungsfehler [#376](https://github.com/artattakk-creator/kodi-noodleprivate/issues/376) bleibt bis zur **echten Android-Abnahme** offen.

## Geräte-Abnahme
1. Kodi 21.3: im vorhandenen GS Media Repository Installer auf 0.5.24 aktualisieren. GS Media Pilot muss installiert und aktiviert sein.
2. Installer starten und **bestehenden Fortschritt weiterführen**, keinesfalls Kodi-Profil löschen oder Add-ons deinstallieren.
3. Der Fehler bei 19/48 darf nicht wiederkehren; `resource.images.skinicons.wide 1.0.5` muss im Kodi-Inventar als **installiert und aktiviert** bestätigt werden. Anschließend muss die Installationsroutine mit 20/48 und weiter fortfahren.
4. Bestehende xVAULT/xImage-Konfiguration, Skin Shortcuts, TMDB, EPG und Kodi-Updatequellen auf Erhalt prüfen.
5. Weitere unabhängige Quell- oder Paketversionsfehler als neues Gerätefeedback dokumentieren. **Nicht behaupten, dass alle 48 real auf Android erfolgreich installiert wurden.**
