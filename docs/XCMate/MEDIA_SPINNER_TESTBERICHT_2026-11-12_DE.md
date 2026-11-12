# BINGIE-Header und Spinner – aktuelle Referenz

Der ursprüngliche Zwei-Reihen-Stand wurde im **bestehenden Draft #438** auf den verbindlichen Sechs-Reihen-Auftrag erweitert. Maßgeblich sind der [vollständige Implementierungs-/Testbericht](SIX_ROWS_TESTBERICHT_2026-11-12_DE.md), die [Android-Checkliste](ANDROID_ABNAHME_PR438_DE.md) und die kuratierten Belege in test-builds/media-spinner/evidence.

Gemeinsame verifizierte Original-BINGIE-Animation: 24×24, 85-ms-Frames, 12 Pixel rechts der gemessenen Überschrift. Echte Typ-InfoLabels vor den ersten Items; unabhängiger Ladezustand, begrenzte GUI-Deadline auch bei pausiertem Datenworker. Leere Zusatzreihen behalten einen kompakten Header. Neue eigene Info-IDs liegen unter Kodis 24-Bit-Grenze. Alle nativen und fremden Definitionsknoten außerhalb der geprüften eigenen Ergänzung bleiben erhalten.

Der minimale clock50-Fix bleibt separat in #437. Er lässt sich bei exakt bekanntem altem Adapter unabhängig anwenden, ohne die neue Skin-Erweiterung zu installieren. Skinänderungen weiterhin nur über bestehende Vorschau-/Bestätigungs-/Sicherungs-/Hash-/Rollback-Transaktion. Keine Benutzerbox wurde verändert.

Review-Version weiterhin **0.1.29.90**, keine Veröffentlichung. Aktuelle Paketreferenz ist ausschließlich die mitgeführte SHA256-Datei:

[ZIP](test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip) · [SHA256](test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip.sha256)

Physische Android-21.3-Prüfungen bleiben NOT_TESTED. Linux-Kodi-Renderer, synthetische Quellen und UI-State-Injektionen werden im Hauptbericht ausdrücklich getrennt ausgewiesen.
