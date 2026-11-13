# XCMate .93 – Testbericht und Abnahmestatus

13.11.2026, Entwicklung auf main .92 `3e1d6f87787baa95d24cc4e7c83c24914db31364`. Master #454. Keine Veröffentlichung oder Mergefreigabe.

Erste gezielte Prüfungen: 14 neue P0-Tests und 16 bestehende Kapazitäts-/Artwork-Tests, **30 PASS**. Zusätzlich 63 bestehende Repository-/Release-/Navigationstests PASS nach Fortschreibung der ausdrücklich veröffentlichten Pilot-.92-Basis und des neuen .93-Manifests. Historische .92-Pakete werden in ihrer tatsächlichen damaligen Source-/Indexbasis reproduziert; der vollständige aktuelle .93-Delta bekommt einen eigenen strengen Guard. Kein Test entfernt oder Skip hinzugefügt.

Vollständige Host-/CI- und native 720p/1080p-Prüfung laufen beziehungsweise werden im Draft dokumentiert. Dieser Zwischenstand ist noch kein Gesamt-PASS. Frühere Fehlversuche und die aktuelle Ursachenmatrix siehe [Übergabe](CODEX_UEBERGABE_02993_ANDROID_PLAYER_EPG_CLEANUP_2026-11-13_DE.md).

| Bereich | Nachweis / Grenze |
|---|---|
| Fehlende Stop-Quittung | FIXED_HOST für pünktliche, verlorene ursprüngliche Quittung und einen tatsächlich ausgeführten späteren FIFO-Probe. Ohne Queue-Fortschritt kein Success; kein zweiter Stop/kein Player-Zugriff. Reale native Decoderblockade OPEN. |
| EPG-Raw | Tatsächlich RAM-only, 0 Bytes Raw-Delete. Keine erfundene Dateibereinigung; unbewiesene alte Raw-Dateien SKIPPED_UNPROVEN. |
| Guide-Backups | FIXED_HOST: echte SQLite-Kopien/Hashes/Keeper-/Journal-/Abbruch-/Readback-Tests. Physische Hostmessung separat, kein Android-Platzgewinn behauptet. |
| Speicher-UI/Scan | FIXED_HOST für Lesetext, Teilmessung, Resume, Symlink und Rechtefehler. Nativer Dialogtitel/Back/Screenshot separat nachweisen. |
| Galileo/XMLTV | FIXED_HOST: BINGIE installiert, kleines 320×180-XMLTV-Bild trotz fehlgeschlagener manueller TMDB-Abfrage; richtige Bildquelle, URL-Zulassung und Eventbindung. Kein echter Android-Render-PASS. |
| Startsender/Gruppen | FIXED_HOST: TEMPORARILY_UNAVAILABLE ohne Reset; 137 Gruppensender ohne EPG, gezielte lokale Lesung, Busy-Backoff. Echter Android-IR-Gruppenwechsel offen. |

**Offen:** Android-RK3528 Stop-Freeze und eigenständige Prozessabbruchursache; echte USB-/Quota-/Platzgewinnabnahme; große Legacy-Quell-/DB-Konsolidierung/gesamter Orphan-GC; optionale P1 #435/#450/#427. Aktive DB/WAL, Quellen, Bildreferenzen, letzter Recovery-Satz, Installer .5.26 und .90-Fallback geschützt.

Alle [16 Gerätegates](ANDROID_ABNAHME_02993_DE.md) stehen auf **ANDROID_NOT_TESTED**. Keine vollständige P0- oder Merge-Empfehlung aus Host-PASS ableiten. Paket/SHA werden neben dem ZIP und im PR aktualisiert; frühere Entwicklungsprüfsummen sind nicht automatisch endgültig.
