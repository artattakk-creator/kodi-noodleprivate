# GS Media – Drittanbieter-Add-ons (Kodi 21.3)

Stand: 21.10.2026. Dies ist ein **Draft-Integrationsstand**, keine Veröffentlichung.

## Cumination
Bereits Bestandteil von `src/repository.gsmedia/addon.xml`: Der Dobbelina-Index liefert `plugin.video.cumination` unverändert von seinem Urheber, der Gujal/SMR-Index stellt die Resolver bereit. Kein zusätzlicher Source-Fork und keine doppelten ZIPs notwendig.

Quellen:
- https://github.com/dobbelina/repository.dobbelina
- https://github.com/Gujal00/smrzips

## MP3 Streams Echoed
Das Upstream-Projekt https://github.com/Echo-Storm/MP3-Streams-2026-Kodi bezeichnet seine Python-3-Neufassung als Kodi-21-kompatibel. Version `2026.1.0`, Add-on-ID `plugin.audio.m3sr2019`. Es stellt eine Standalone-ZIP, aber derzeit keinen nachgewiesenen Kodi-Repository-Index bereit.

Der neue Builder `tools/import_mp3_streams.py` ruft das veröffentlichte Paket auf dem Buildhost ab und verifiziert dessen Git-Blob-ID `ebc7f51129fb24f7db0c9d85c8c5c03ec3f97929`. Er lehnt veränderte Dateien, falsche IDs/Versionen, gefährliche ZIP-Pfade, Symlinks, doppelte Einträge und Größenüberschreitungen ab. Nur ein verifiziertes Paket wird als `plugin.audio.m3sr2019/plugin.audio.m3sr2019-2026.1.0.zip` im Repository ausgegeben und in `addons.xml` aufgenommen. Das Paket übernimmt unverändert die Upstream-Metadaten, Lizenz und Python-Quellen; keine Providerlogik ist verändert.

Die lokalen Offline-Tests verwenden ausschließlich synthetische Test-ZIPs. **Vor Merge/Release:** echter Upstream-Download aus CI, Original-ZIP/Quellprüfung, Lizenzprüfung, Gesamtsuite und Android-21.3-Funktionstest. Bestehende `main`-Releases dürfen nicht beeinträchtigt werden.

## TMDb Helper, Pluto TV, SHOUTcast und EZ Maintenance+
- **EZ Maintenance+** ist bereits über den unveränderten peno64-Repoindex in GS Media 1.7.0 verfügbar; keine Kopie und keine neue Einbindung.
- **TMDb Helper** wird ab Kodi 21 über den Omega-Katalog des Originalautors `jurialmunkey/repository.jurialmunkey/master/omega/zips/` inklusive der gemeinsam gepflegten Modulpakete angeboten. Dies ist **kein installierter zweiter Repository-Add-on**, sondern eine zusätzliche `<dir>`-Quelle der GS Media Repository-Definition. Dieser Upstream-Katalog enthält auch weitere Add-ons von jurialmunkey.
- **Pluto.TV** `plugin.video.plutotv` **1.6.2** und **SHOUTcast** `plugin.audio.shoutcast` **2.5.2+matrix.1** werden gezielt über das offizielle Kodi-Omega-Downloadarchiv in unserem Buildhost bezogen, ZIP-CRC/Pfad/Version/Python/Größen geprüft, ohne Byteänderung der Original-ZIPs in unseren Katalog aufgenommen. Keine unnötige Duplikation des gesamten Kodi.tv-Katalogs. Die Paket-Versionen werden **fest gewählt**, für Updates sind spätere ausdrückliche Anpassungen/Prüfungen nötig. Kodi besitzt trotzdem weiterhin sein offizielles Kodi.tv-Repository als Standardquelle für abhängige Module.

Veröffentlichungsvoraussetzung: CI-Build und Quellen-HTTP-Test, zwei Original-ZIPs und die Kodi-21.3-Installation praktisch testen. Nicht unterstellen, dass die Angebote von Pluto oder SHOUTcast unabhängig von ihren Live-APIs immer streamen.

## TV Spielfilm
Ein eigenständiger **Kodi-21-Programmführer „TV Spielfilm“** konnte nicht nachgewiesen werden. Ein historisches Kodinerds-Addon `plugin.video.tvspielfilm_de` Version **1.2.4 (2020)** existiert zwar, ist aber laut Original-`addon.xml` ein **Mediatheken-Addon** und nutzt Kodi-Python **2.25.0** – daher kein Ersatz für den gewünschten Fernsehprogrammführer. Die bisher identifizierte Software `service.takealug.epg-grabber` nutzt „TV Spielfilm“ als mögliche externe Datenquelle, ist jedoch **kein TV-Programmführer mit diesem Namen**. Quelle: https://github.com/DeBaschdi/service.takealug.epg-grabber ; Kodinerds-Katalog: https://repo.kodinerds.net/

Daher wird kein nicht überprüftes TV-Spielfilm-Paket erfunden und keine zusätzliche Hintergrund-EPG-Abfrage im GS-Media-Katalog stillschweigend aktiviert. Prüfen, welches konkrete frühere Plugin der Benutzer meinte. Separate EPG-Grabber erst nach Abgleich mit XCMate-EPG-Manager und Kodi-21.3-Tests anbieten.

## Freigaberegeln
- Keine Änderung an `plugin.video.xtreammate`, Kodi-Keymaps, globalem Skin oder vorhandenen GitHub-Releases.
- Neuer Draft-PR auf `main`-Basis ohne Merge.
- Die produktive Repository-Version `1.7.0` bleibt während der Prüfung unverändert. Nach erfolgreicher Verifikation ist die reguläre Versions-/Indexveröffentlichung eine eigene Owner-Entscheidung.
