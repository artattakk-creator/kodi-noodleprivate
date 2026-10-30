# XCMate .61 – Ursachen und Beweisgrenzen

Basis main f0e29c1ac758e5eb48083fa2d8e70f07d185bb43 (.60), erneut abgefragt. Issue #286 und beide Nachträge vollständig gelesen; Android-FAIL hat Vorrang vor synthetischen .60-Ergebnissen.

**Bestätigter Codefehler:** home_menu Widgets öffnet absichtlich nur widget_sources49. Die echte Verwaltung widget_setup war nicht in appearance verlinkt; die Layoutvorbereitung war ausschließlich ein Kontextmenü. Deshalb war der in .60 dokumentierte Installationsweg nicht durchführbar. .61 ergänzt sichtbaren Settings-Zugang, getrennte Widget-Einrichtung im Hauptmenü und normale OK-Aktionen für Vorschau und Restore. Vorhandener Adapter: ausdrücklich bestätigbarer einmaliger Builder-Aufruf statt Sackgasse. Keine Anwendung beim Update, keine Schleife.

Vier-Dateien-Adapter, native LiveRow/Hero, Senderquelle, ursprüngliche Reihenfolge, komplette Gruppe, gespeicherte Quellen-URLs, Film-/Serienbindings und .42-Kompatibilitätsmodus bleiben unverändert. Das Fehlen von EPG/Bildern/Token darf keine Datenzeilen filtern. Nicht belegt ist, ob auf der realen Box zusätzlich eine fremde Skin-Dateiversion, abweichende Bindung, fehlerhafte generierte Includes oder Visibility vorliegt. Ohne aktives Android-Profil keine Behauptung eines Geräte-PASS.

Hosttestgrenze: native Kodi 21.2/Linux und originale BINGIE-2.2.3-Dateien; synthetischer Provider mit 88 Sendern. .61-Test beginnt mit ungepatchten vier Skin-Dateien, folgt sichtbaren Menülinks, bedient echte Vorschau/Bestätigung, lässt Produktionscode sichern/anwenden und prüft anschließend Home10000/Container2510/Fokus0,1,87/persistente Logos. Externe Helfer sind isolierte Stubs. Der Builder-Stub installiert erst nach Zustimmung die Ausgabe des unveränderten, gepinnten Skinshortcuts-2.1.0-Templatecompilers; dies ist kein Beweis des vollständigen Android-Skinshortcuts-Laufs. Android21.3 bleibt NOT_TESTED.

P0-Zwischenstand wird vor Token-Erweiterung mit unveränderlichem Commit-/ZIP-Link bereitgestellt. Kein Merge, kein produktives Release, keine Geräteinstallation.
