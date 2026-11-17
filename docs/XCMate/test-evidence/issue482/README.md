# Unveränderte native Screenshot-Belege für #482

Die PNGs stammen aus GitHub-Actions-Läufen mit echtem Linux-Kodi21.2. Inhalte und Konten sind synthetisch. Keine Android-Abnahme. Quelle und Einzelprüfsummen stehen in `mapping-pixels.json`. Keine Bildbearbeitung oder nachträgliche Beschriftung.

| Auflösung | Quelle wählen | EPG-Vorschau | Belegter Worker |
|---|---|---|---|
| 720p, echter Grid-Elternbereich | [PNG](720/epg482-source-grid.png) | [PNG](720/epg482-preview-grid.png) | [PNG](720/epg482-busy-grid.png) |
| 1080p, echter Grid-Elternbereich | [PNG](1080/epg482-source-grid.png) | [PNG](1080/epg482-preview-grid.png) | [PNG](1080/epg482-busy-grid.png) |
| 720p, nativer Dialog / synthetischer Mini-Elternowner | [PNG](720/epg482-source-mini.png) | [PNG](720/epg482-preview-mini.png) | [PNG](720/epg482-busy-mini.png) |
| 1080p, nativer Dialog / synthetischer Mini-Elternowner | [PNG](1080/epg482-source-mini.png) | [PNG](1080/epg482-preview-mini.png) | [PNG](1080/epg482-busy-mini.png) |

Der Mini-Adapter wird tatsächlich aufgerufen und sein Quell-/Kanal-Readback geprüft. Der sichtbare echte Mini-EPG-Elternbereich ist mit dieser Fixture nicht belegt und bleibt Teil der Android-Abnahme.

## Artwork und sichtbarer Status

Alle folgenden Bilder sind unveränderte Original-PNGs der erfolgreichen nativen Läufe am Produktstand38dbe103. Einzelprüfsummen und Jobs stehen in `artwork-pixels.json`. Das blaue Motiv ist ein kontrolliertes synthetisches Bild, kein echter TMDB-Film. Der Statusabschnitt injiziert Producerzustände und beweist die native Textbindung; er simuliert keine echte Benutzer- oder Anbieterfreigabe.

| Auflösung | Hero | Detail nach305s | Suche läuft | Einstellungsfehler |
|---|---|---|---|---|
| 720p | [PNG](artwork/720/visible84-hero86-final.png) | [PNG](artwork/720/visible84-sticky88-305.png) | [PNG](artwork/720/visible84-status482-running.png) | [PNG](artwork/720/visible84-status482-settings_xml_invalid.png) |
| 1080p | [PNG](artwork/1080/visible84-hero86-final.png) | [PNG](artwork/1080/visible84-sticky88-305.png) | [PNG](artwork/1080/visible84-status482-running.png) | [PNG](artwork/1080/visible84-status482-settings_xml_invalid.png) |

Weitere Originaldateien zeigen Angefordert, Deaktiviert und ein unabhängig eingerichtetes Fremdwidget. Die späten Statusbilder belegen ausschließlich den Hero-Status bei beendeter synthetischer Hintergrunddatenlane. Die dort sichtbaren VOD-/Serien-Platzhalter sind ausdrücklich **kein PASS für dauerhaft versorgte Medienreihen**.
