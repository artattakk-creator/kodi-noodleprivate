# GS Media Setup 0.5.27 · Komponenten und Abnahme

Die 48 IDs und ihre Reihenfolge entsprechen Installer 0.5.26. Dieselbe Liste gilt für Android und LG webOS. Repositories, die Kodi vor einem Paket zusätzlich einrichten muss, zählen als Voraussetzungen außerhalb der 48. Ein Strich bei der Mindestversion bedeutet, dass 0.5.26 keinen Mindeststand festlegt.

Die Imports stammen soweit verfügbar aus den Paketmanifesten von Pilot oder BINGIE Omega. Weitere Angaben stammen aus dem 0.5.26-Plan. Bei „Kodi-Katalog“ prüft der Installer die am Gerät gemeldeten Pflichtabhängigkeiten. Die tatsächliche Piers-Verfügbarkeit und Binärkompatibilität richten sich nach dem Zielgerät. Optionale Imports werden bei vorhandenen Installationen berücksichtigt.

| Nr. | Add-on-ID | Mindestversion | Vorgesehene Kodi-Quelle | Bekannte Pflichtimporte mit Mindest-API und besonderer Bedarf |
| --- | --- | --- | --- | --- |
| 1 | `script.module.simplejson` | 3.17.0 | `repository.xbmc.org` | Kodi-Katalog |
| 2 | `script.bingie.helper` | 1.1.2 | `repository.gsmedia.pilot` | `xbmc.python` 3.0.0, `script.module.simplejson` 3.17.0 |
| 3 | `script.module.unidecode` | 0.4.14 | `repository.xbmc.org` | Kodi-Katalog |
| 4 | `script.module.simpleeval` | 0.9.10 | `repository.xbmc.org` | Kodi-Katalog |
| 5 | `script.skinshortcuts` | 2.1.0 | `repository.gsmedia.pilot` | `xbmc.python` 3.0.0, `script.module.unidecode` 0.4.14, `script.module.simpleeval` 0.9.10. BINGIE benötigt 2.x. Offizieller Piers-Quellstand 3.0.5 ist ein Blocker. |
| 6 | `script.module.simplecache` | 2.0.2 | `repository.titan.bingie.mod` | `xbmc.python` 3.0.0 |
| 7 | `script.module.requests` | 2.9.1 | `repository.xbmc.org` | Kodi-Katalog |
| 8 | `script.module.beautifulsoup4` | 4.9.3 | `repository.xbmc.org` | Kodi-Katalog |
| 9 | `script.module.arrow` | 1.1.0 | `repository.xbmc.org` | Kodi-Katalog |
| 10 | `script.module.thetvdb` | 1.0.34 | `repository.titan.bingie.mod` | `xbmc.python` 3.0.0, `script.module.requests` 2.9.1, `script.module.simplejson` 3.17.0, `script.module.simplecache` 2.0.2, `script.module.arrow` 1.1.0 |
| 11 | `script.module.musicbrainz` | 0.7.0 | `repository.titan.bingie.mod` | `xbmc.python` 3.0.0 |
| 12 | `script.module.infotagger` | 0.0.5 | `repository.xbmc.org` | Kodi-Katalog |
| 13 | `script.module.metadatautils` | 1.30.0 | `repository.titan.bingie.mod` | `xbmc.python` 3.0.0, `script.module.requests` 2.9.1, `script.module.beautifulsoup4` 4.9.3, `script.module.thetvdb` 1.0.34, `script.module.musicbrainz` 0.7.0, `script.module.simplecache` 2.0.2, `script.module.arrow` 0.15.5, `script.module.infotagger` 0.0.1 |
| 14 | `script.skin.helper.service` | 1.30.0 | `repository.titan.bingie.mod` | `xbmc.python` 3.0.0, `xbmc.addon` 12.0.0, `script.module.simplejson` 3.3.0, `script.module.simplecache` 2.0.2, `script.module.metadatautils` 1.30.0 |
| 15 | `script.skin.helper.widgets` | 1.30.0 | `repository.titan.bingie.mod` | `xbmc.python` 3.0.0, `xbmc.addon` 12.0.0, `script.module.metadatautils` 1.30.0, `script.module.simplecache` 2.0.2 |
| 16 | `script.skin.helper.backgrounds` | 1.0.36 | `repository.titan.bingie.mod` | `script.module.simplecache` 1.0.0, `script.module.metadatautils` 1.1.0 |
| 17 | `resource.images.skinbackgrounds.titanium` | 1.0.0 | `repository.titan.bingie.mod` | `kodi.resource` 1.0.0 |
| 18 | `resource.images.skinicons.wide` | 1.0.5 | `repository.gsmedia.pilot` | `kodi.resource` 1.0.0 |
| 19 | `resource.images.backgroundoverlays.basic` | 1.0.0 | `repository.titan.bingie.mod` | `kodi.resource` 1.0.0 |
| 20 | `resource.images.studios.coloured` | 0.0.23 | `repository.titan.bingie.mod` | Kodi-Katalog |
| 21 | `script.module.pil` | 5.1.0 | `repository.xbmc.org` | `xbmc.python` 3.0.0. Native Python-Erweiterung Pillow, unter webOS gebündelt. Import und PNG-Test auf dem Gerät erforderlich. |
| 22 | `script.module.addon.signals` | 0.0.6 | `repository.xbmc.org` | Kodi-Katalog |
| 23 | `script.module.jurialmunkey` | 0.2.35 | `repository.gsmedia.pilot` | `xbmc.python` 3.0.1, `script.module.requests` 2.9.1, `script.module.infotagger` 0.0.5 |
| 24 | `plugin.video.themoviedb.helper` | 5.4.16 | `repository.xbmc.org` | `xbmc.python` 3.0.1, `script.module.requests` 2.9.1, `script.module.pil` 1.1.7, `script.module.addon.signals` 0.0.6, `script.module.jurialmunkey` 0.2.2, `script.module.infotagger` 0.0.5, `script.module.beautifulsoup4` 4.9.3 |
| 25 | `plugin.program.autocompletion` | 2.1.2 | `repository.titan.bingie.mod` | Kodi-Katalog |
| 26 | `plugin.video.youtube` | 7.0.2.2 | `repository.xbmc.org` | Kodi-Katalog |
| 27 | `skin.titan.bingie.mod` | 2.2.3 | `repository.titan.bingie.mod` | `xbmc.gui` 5.17.0, `script.bingie.helper` 1.1.2, `script.skinshortcuts` 2.1.0, `script.skin.helper.service` 1.30.0, `script.skin.helper.widgets` 1.30.0, `script.skin.helper.backgrounds` 1.0.36, `resource.images.skinbackgrounds.titanium` 1.0.0, `resource.images.skinicons.wide` 1.0.5, `resource.images.backgroundoverlays.basic` 1.0.0, `resource.images.studios.coloured` 0.0.23, `plugin.video.themoviedb.helper` 5.4.16, `plugin.program.autocompletion` 2.1.2, `plugin.video.youtube` 7.0.2.2 |
| 28 | `plugin.video.xtreammate` | — | `repository.gsmedia.pilot` | `xbmc.python` 3.0.0, `script.module.pil` 5.1.0. Vorhandenen Stand und Profil erhalten. Version des verfügbaren Pakets beim Neuaufbau prüfen. |
| 29 | `script.module.six` | — | `repository.xbmc.org` | Kodi-Katalog |
| 30 | `script.module.kodi-six` | — | `repository.xbmc.org` | Kodi-Katalog |
| 31 | `script.module.resolveurl` | 5.1.212 | `repository.gsmedia.pilot` | `script.module.six`, `script.module.kodi-six`, `script.module.pyqrcode` |
| 32 | `script.module.resolveurl.xxx` | 2.1.44 | `repository.gsmedia.pilot` | `script.module.resolveurl` 5.1.0 |
| 33 | `script.common.plugin.cache` | — | `repository.xbmc.org` | Kodi-Katalog |
| 34 | `script.module.websocket` | 0.50.0 | `repository.xbmc.org` | Kodi-Katalog |
| 35 | `script.module.inputstreamhelper` | — | `repository.xbmc.org` | Kodi-Katalog |
| 36 | `plugin.video.cumination` | 1.1.206 | `repository.gsmedia.pilot` | `script.module.six`, `script.module.kodi-six`, `script.module.resolveurl` 5.0.00, `script.module.resolveurl.xxx` 2.0.1, `script.common.plugin.cache`, `script.module.websocket` 0.50.0, `script.module.inputstreamhelper`, `script.module.requests` |
| 37 | `plugin.video.xvault` | — | `repository.xvault` | `xbmc.python` 3.0.0. Optionale native InputStream-Add-ons Adaptive, FFmpeg Direct und RTMP. |
| 38 | `repository.slyguy` | 0.0.9 | `repository.gsmedia.pilot` | Keine Pflichtimporte im geprüften Manifest |
| 39 | `slyguy.dependencies` | 0.0.30 | `repository.slyguy` | `repository.slyguy` |
| 40 | `script.module.slyguy` | 0.86.96 | `repository.slyguy` | `slyguy.dependencies` 0.0.30, `repository.slyguy` 0.0.9 |
| 41 | `slyguy.trailers` | — | `repository.slyguy` | `script.module.slyguy` 0.86.96 |
| 42 | `script.module.routing` | — | `repository.xbmc.org` | Kodi-Katalog |
| 43 | `plugin.audio.m3sr2019` | 2026.1.0 | `repository.gsmedia.pilot` | `xbmc.python` 3.0.0, `script.module.beautifulsoup4`, `script.module.requests`, `script.module.routing` |
| 44 | `script.module.xbmcswift2` | 19.0.0 | `repository.xbmc.org` | Kodi-Katalog |
| 45 | `script.module.xmltodict` | 0.12.0 | `repository.xbmc.org` | Kodi-Katalog |
| 46 | `plugin.audio.shoutcast` | — | `repository.xbmc.org` | `xbmc.python` 3.0.0, `script.module.xbmcswift2` 19.0.0, `script.module.xmltodict` 0.12.0 |
| 47 | `script.ezmaintenanceplus` | 2026.04.05.0 | `repository.gsmedia.pilot` | `script.module.requests` 1.0.0 |
| 48 | `script.cabertoss` | — | `repository.xbmc.org` | Kodi-Katalog |

## Zusätzliche Pflichtschritte

- GS Media Pilot muss als vorhandene freigegebene Quelle aktiv sein. BINGIE-Originalrepository ab 2.0.1 und xVAULT-Repository können vor ihren Zielpaketen nativ eingerichtet werden. Kodi bestätigt gegebenenfalls den Download.
- Space-Blue-Manager `script.gsmedia.xcmate.branding` ab 0.2.0 aus Pilot mit `xbmc.python` ab 3.0.0. Prüft Logo, Splash, Intro, XML und Farben nach dem Schreiben.
- BINGIE 2.2.3 und Skin Shortcuts 2.x, vier gebundene Original-/Ziel-Hashes, Layoutdateien, xVAULT-Spieler bzw. erhaltene Benutzervorgaben sowie Skin-Auswahl und Kaltstart werden zusätzlich geprüft.

[BINGIE Omega-Katalog](https://github.com/AchillesPunks/repository.titan.bingie.mod/blob/d9f334ecc33c7d0e137dd1728af18815c512e577/omega/addons.xml) · [Piers Skin Shortcuts](https://github.com/xbmc/repo-scripts/blob/piers/script.skinshortcuts/addon.xml) · [Piers Pillow-Manifest](https://github.com/xbmc/xbmc/blob/60b9c6b0f7fe7bbb932f7140b4662627f94d7400/addons/script.module.pil/addon.xml).
