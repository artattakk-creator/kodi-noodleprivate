# .93 – Issue- und Freigabematrix

Master #454, Draft #455. Keine Merge-/Releasefreigabe. FIXED_HOST ist keine Android-Abnahme.

| Issue | Stand | Noch offen |
|---|---|---|
| #452 / #442 Player | FIXED_HOST: kein zweiter Stop; verlorene ursprüngliche Quittung nur durch wirklich ausgeführte spätere FIFO-Quittung ersetzen; 120 simulierte Zyklen, einheitliche Session-Korrelation. .42-Einstellung und Medienpfad geschützt. | Native Rockchip-Queueblockade und eigenständiger ungeordneter Prozessabbruch OPEN. Android Exit-Reason/Stacks, IR und 30–90-min-Soak fehlen. Keine behauptete Decoder-Reparatur. |
| #443 EPG-Speicher | FIXED_HOST: eng bewiesene ältere Guide-Backups mit geprüftem letzten Recovery-Satz journalisiert begrenzen; geöffnete/unbekannte/korrupte Dateien schützen. Reale Linux-Dateimessung netto +8.425.472 Bytes, keine Android-Zahl. Rohfeeds liegen im RAM, Raw-Delete korrekt 0. | Android-Retention/Reboot/offline und tatsächlicher Platzgewinn; große Legacy-Quellen-/DB-Konsolidierung und unbewiesene Raw-Altbestände bleiben OPEN/SKIPPED_UNPROVEN. |
| #443 Diagnose / USB | FIXED_HOST: eigenes deutsches Diagnosefenster, übersetzte Zustände, Größen/Volume/Freelist, partielle bzw. nicht lesbare Messungen, fortsetzbare Traversierung. Bestehende verifizierte USB-Migration unverändert. | Native Titel/Back/Screenshot und tatsächliche RK3528-Volumes/Quota/USB-Freiraum separat prüfen. Internes Originalbild nur gesondert doppelt bestätigt. |
| #433 Artwork | FIXED_HOST: kleine EPG-Bilder nicht an Hero-Mindestgrößen messen; Home-Negativcache darf explizite Details nicht blockieren; Fallback ausschließlich exakte XMLTV-/Provider-Events, kein altes automatisch erkanntes anderes Werk. Bewusste Quellendeaktivierung erhalten. | Galileo/TVMaze/TMDB auf Android, Readback/Reopen/Reboot und sichtbare Textur getrennt. Kein pauschaler Bilder-PASS. |
| #451 Startsender/Gruppen | FIXED_HOST: temporär fehlender Startsender behält IDs; gewünschte Gruppe lokal/asynchron/generationengeprüft, 137 Sender ohne EPG, Pending statt falsch leer, kontrolliertes Nachindizieren über bestehenden Worker. | Native Teilgruppen-/IR-Prüfung und echter Android-Katalog-Busy/Reboot. |
| #445 Bestand | .90-Fallback, reguläre .91, Pilot .92, Installer .5.26, Token, Profile, Quellen, persönliche Widgets unverändert. Keine neue Home-Geometrie. | Aktuelle native sechs Reihen/Logo/Hero/Stop-Matrix und alle Gerätegates getrennt. |
| P1 #435/#450/#427 | Bewusst getrennt, keine ungeprüfte Draft-Übernahme. | Restore-Pläne, MP3-Alben und zusätzliche Mapping-UX nach P0-Stabilisierung. |

Der Masterauftrag wird nicht als vollständig erledigt erklärt, solange die Android-Player-P0s und Gerätebelege offen sind. [Ursachen/Retentionvertrag](CODEX_UEBERGABE_02993_ANDROID_PLAYER_EPG_CLEANUP_2026-11-13_DE.md), [Testbericht](TESTBERICHT_02993_DE.md), [Gerätematrix](ANDROID_ABNAHME_02993_DE.md).
