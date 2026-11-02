# XCMate 0.1.29.68 – Testbericht

Entwicklung in Draft-PR #314 zu #313. Gepinnte Ausgangsbasis: `4d8ba5ef2c7bf997af437e230ef1ec52e1e747e8`. Sämtliche tatsächlichen Android-Abnahmen stehen aus; die .67-Fehlerberichte werden nicht überschrieben.

## Verbindliche Gates

1. Vollständige Hosttests des aktuellen PR-Commits inklusive aller 2768 bisherigen Methoden und unveränderter Skipbedingungen.
2. Neue .68-Tests zu GUI-freien Aufträgen, acht sichtbaren Sendungen, Quellen-/Profil-/Revisionsisolation, Queuegrenze/Priorisierung/Fairness, realem SQLite→Matching→PNG-Pfad, Speicher-Lesediagnose, Zustimmung und dynamischen Startgruppen.
3. Historische native Kodi-21.2-/BINGIE-2.2.3-Transport-, Widget-, Home-, Fokus- und Wiedergabetests bleiben aktiv.
4. Neue native PNG-/JPEG-Tests beginnen mit ungefülltem Sendungsbildcache, verwenden synthetische TMDB-Transportantworten und echte produktive Matching-/Queue-/Dateipfade. Native Screenshot-Pixel werden für Hero, gemeinsamen Guide-/Mini-Preview-Renderer und Programme-Detaildialog ausgewertet. Das ersetzt keine echte Android-Fernbedienung im Guide.
5. Die vollständigen Kodi-TS/HLS-Decoder-/Fehlerfälle bleiben unverändert. Die .42-Stopimplementierung ist unverändert.
6. ZIP-CRC, Inventar, Quellbytes, Add-on-ID/-Version, private Dateiausschlüsse und Repositoryindex werden vor Bereitstellung kontrolliert. Das Repository erhält vor Freigabe keinen neuen produktiven Index.
7. Separater synthetischer Kalt-/Warm-Benchmark. Warme RAM-Reads dürfen weder SQLite noch Dateien/HTTP aufrufen. Zeitmessungen sind Hostwerte, keine Android-Messung.

## Status

Die endgültigen Laufnummern, Ergebnisse, Paket-SHA256 und Artefaktlinks werden nach dem letzten abgeschlossenen CI-Lauf im PR ergänzt. Ein laufender oder abgebrochener Lauf gilt nicht als grünes Gate. Frühere Testpakete dieses Branches sind keine endgültigen Abnahmekandidaten.

## Issue-Abnahmematrix

| Bereich | Implementierung | Host/Native | Android |
| --- | --- | --- | --- |
| #313 sichtbare Guide-/Detail-Bildaufträge | umgesetzt, Service-Broker und bestehende Queue | endgültiger CI-Lauf ausstehend | NOT_TESTED |
| #313 Hero-Bildnachladung | fokussierter Eventauftrag und gemeinsamer Cache | endgültiger CI-Lauf ausstehend | NOT_TESTED |
| #313 Mini-Start/Ladezustände | lokale Modelle und RAM-EPG, getrennte Ladeanzeige | endgültiger CI-Lauf ausstehend | NOT_TESTED |
| #313 dynamische Startgruppen/* | umgesetzt, 0–256 und Seitengrenzen | endgültiger CI-Lauf ausstehend | NOT_TESTED |
| #313 zentrales Bildmenü/Negativcache | umgesetzt, keine Auto-Zustimmung | endgültiger CI-Lauf ausstehend | NOT_TESTED |
| #313 DB-Limit/physischer Speicher/Reserve | reine exakte Diagnose, keine automatische Bereinigung | endgültiger CI-Lauf ausstehend | reale Werte NOT_TESTED |
| Arrow/metadatautils/Skin Helper | Diagnose separat, keine Fremdmodifikation | externe Reparatur BLOCKED bis isolierte Reproduktion | NOT_TESTED |
| Fehlender fremder Widget-Reload-Hook | kein ungefragter Skinpatch | separat offen bei fehlendem Hook | NOT_TESTED |
| Frühere Live-/Exit-Gates #307 | .67/.42-Funktionen erhalten | bestehende Hostgates aktiv | weiterhin offen |
| #306/#312 Installer/Wizard | außerhalb dieses Hotfixes | nicht übernommen | nicht Bestandteil |

Keine privaten Logs, Provider-Adressen oder echten Tokens wurden als Testdaten verwendet. Reale Box-B-Bild-/EPG-Probleme werden erst nach Geräteprüfung als behoben bezeichnet.
