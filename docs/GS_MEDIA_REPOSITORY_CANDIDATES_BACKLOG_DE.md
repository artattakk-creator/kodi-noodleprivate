# GS Media Repository – Kandidaten- und Prüfliste (1.8.1 Lite)

**Status 02.11.2026:** Bei Veröffentlichung von 1.8.1 sind ausschließlich die drei bereits bestehenden GS-Media-Add-ons im Katalog freigegeben:

| Add-on-ID | Status | Hinweis |
| --- | --- | --- |
| `repository.gsmedia` | **FREIGEGEBEN – 1.8.1** | Kodi-Repository-ID bleibt unverändert |
| `plugin.video.xtreammate` | **BESTAND – .66** | Schon im bisherigen Repo; Live-TV/EPG/Artwork weiterhin P0 (#307); keine Behauptung einer erfolgten Android-Freigabe |
| `plugin.video.noodleprivate` | **BESTAND – 0.4.2** | Schon im bisherigen Repo; keine neue Abnahme erfolgt |

**Abgrenzung:** `freigegeben` bedeutet für das Repository nur: der Eintrag ist weiterhin im bereits bestehenden GS-Media-Katalog zulässig; es ist keine pauschale Aussage über Funktion, Content oder rechtliche Unbedenklichkeit. XCMate .66 bleibt defekt und wird separat repariert.

## Nicht freigegeben – TODO, nicht im 1.8.1-Katalog

Die externen Sammelkataloge, die in 1.8.0 über weitere `<dir>`-Einträge erreichbar waren, sind in 1.8.1 entfernt. Ihre Projekte sind nicht gelöscht, sondern für die nächste Integrationsphase zurückgestellt:

| Projekt / Katalog | Prüfung vor Aufnahme |
| --- | --- |
| Cumination / `repository.dobbelina` | Genaue erforderliche Versionen, Abhängigkeiten, Kodi 21/Android ARM32, Lizenz und Nutzungsrechte prüfen |
| SMR / ResolveURL (`Gujal00/smrzips`) | Nur tatsächlich benötigte Versions-Pins und Abhängigkeiten als geprüfte Pakete anbieten; keinen gesamten Sammelkatalog verknüpfen |
| xVAULT / `mojomedia1812/xVAULT` | Kompatibilität, Änderungsstand, Herkunft und Nutzerzustimmung prüfen; Original-Repository bleibt separat installierbar |
| Titan BINGIE MOD (Nexus/Omega) | Aktuell vorhandenen Skin 2.2.3 + Helper-Dependency-Closure erhalten, neue Pakete/Kataloge erst nach Android-Test |
| EZ Maintenance+ / `repository.peno64` | Optional, Risiken für Kodi-Daten/Cache prüfen; keine Cleanup-Automation ohne ausdrückliche Zustimmung |
| mr-evil1 Kodi Media / TiViMate | Eignung, Lizenz und kompletter Fremdkatalog vor Neuaufnahme prüfen |
| jurialmunkey / TMDb Helper | Nicht automatisch aktualisieren; Kompatibilität mit BINGIE 2.2.3 und XCMate-Token-/Artwork-Pipeline prüfen |
| MP3 Streams Echoed (`plugin.audio.m3sr2019`) | Pin/Hash/Originalquelle, 404 im alten PR #303 und Kodi-Kompatibilität beheben |
| Legacy MP3 Streams (`plugin.audio.mp3streams`) | Alternative zum Echoed-Paket, Doppelung/Abwärtskompatibilität prüfen |
| SHOUTcast (`plugin.audio.shoutcast`) | Originalquelle und Manifest, Kodi 21/ARM32, Installation/Playback prüfen |
| Pluto.TV (`plugin.video.plutotv`) | Kein ungeprüfter externer automatischer Mirror; Version/Repo-Pin + Test |
| SlyGuy-Komponenten | Nur für wirklich benötigte Add-ons; **kein** Pflicht-Bestandteil von BINGIE |
| GS Media Setup Wizard (`script.gsmedia.setup`) | Draft PR #306, read-only Vorschau; erst nach Tests als Optionalpaket aufnehmen |

## Freigabeverfahren

1. Für jeden Kandidaten ein konkretes Issue mit **Add-on-ID**, Herkunft, Lizenz, offizieller Upstream-Version, SHA256/ZIP, benötigten Manifest-Abhängigkeiten sowie Test- und Rollbackplan erstellen.
2. Keine gesamte unkontrollierte `<dir>`-Drittanbieter-Sammelquelle hinzufügen. Einzelne geprüfte Add-ons nur mit expliziter Freigabe in `APPROVED_ADDON_IDS` in `tools/build_repository.py` aufnehmen.
3. CI muss Versionen, Abhängigkeiten, ZIP/CRC/Index, Kodi 21.3 Android ARM32 und die installierte Bestandssituation prüfen. **NOT_TESTED** ist nicht **PASS**.
4. Kein automatisches Installieren, Deinstallieren, Bereinigen, Zurücksetzen oder Löschen von Kodi-Benutzerdaten. 
5. Bisher installierte Drittanbieter-Add-ons und **separat** konfigurierte Fremd-Repositories bleiben auf der Kodi-Box technisch vorhanden. Der 1.8.1-Lite-Katalog nimmt lediglich die **GS-Media-seitige** Anbietung/Updatequelle weg; andere eigenständige Repos bleiben unabhängig.
6. Sobald ein Kandidat alle Gates besteht: separater PR für späteres Repository-Patchrelease, nicht stillschweigend in 1.8.1.

Referenzen: #305 (Gesamtplan), #307 (XCMate P0), PR #303 (abgelöster, rot geflaggter Sammelimport), PR #306 (Wizard), PR #309 (1.8.0 Basis).
