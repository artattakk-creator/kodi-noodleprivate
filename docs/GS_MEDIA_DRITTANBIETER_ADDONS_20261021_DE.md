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

## TV Spielfilm
Ein eindeutig verifizierbares eigenständiges **Kodi-21-Add-on „TV Spielfilm“** konnte nicht gefunden werden. Die bisher identifizierte Software `service.takealug.epg-grabber` nutzt „TV Spielfilm“ als mögliche externe Datenquelle, ist jedoch **kein TV-Programmführer mit diesem Namen**. Quelle: https://github.com/DeBaschdi/service.takealug.epg-grabber ; Kodinerds-Katalog: https://repo.kodinerds.net/

Daher wird kein nicht überprüftes TV-Spielfilm-Paket erfunden und keine zusätzliche Hintergrund-EPG-Abfrage im GS-Media-Katalog stillschweigend aktiviert. Prüfen, welches konkrete frühere Plugin der Benutzer meinte. Separate EPG-Grabber erst nach Abgleich mit XCMate-EPG-Manager und Kodi-21.3-Tests anbieten.

## Freigaberegeln
- Keine Änderung an `plugin.video.xtreammate`, Kodi-Keymaps, globalem Skin oder vorhandenen GitHub-Releases.
- Neuer Draft-PR auf `main`-Basis ohne Merge.
- Die produktive Repository-Version `1.7.0` bleibt während der Prüfung unverändert. Nach erfolgreicher Verifikation ist die reguläre Versions-/Indexveröffentlichung eine eigene Owner-Entscheidung.
