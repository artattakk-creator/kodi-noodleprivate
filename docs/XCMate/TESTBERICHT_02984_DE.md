# XCMate 0.1.29.84 – Testbericht

Stand: 09.11.2026. Entwicklungsstand, keine Android-Abnahme. Hauptissue #403.

- Gezielt `.84`: 26 Tests PASS (1,538 s), einschließlich 27-MiB-Reserve, 24 Providerposter, echte PNG-Dekodierung, kurzlebige Ereignisfreigabe, Konten-/Profil-/Quellenisolation, DNS-Widerruf, Texturecache-Kaltwiederherstellung und unveränderter interner Modus.
- Bestandsschutz `.84`: vier Tests PASS (0,672 s): vollständiger Source-/Testbestand aus .83, unveränderte Player-/Skin-/Routing-/Installer-/Migrationsdateien und eingefrorene Veröffentlichungskanäle.
- Zusätzliche bestehende Fokusprüfungen: 56 PASS (40,764 s), einschließlich bestehender umfangreicher Migrationsintegritätstests. Keine Migration auf Geräten ausgeführt.
- Vollständige Host-/CI-/Native-Ergebnisse werden vor Übergabe dieses PR ergänzt. Ein einzelner grüner Fokuslauf ist keine vollständige Freigabe.
- Android Box B: sämtliche IMG84-01 bis IMG84-08 `ANDROID_NOT_TESTED`. Box A nicht verändert. P0-Bildanzeige noch nicht auf Android abgenommen.

[Ursachen und Implementierung](IMPLEMENTIERUNG_02984_BILDER_ZUERST_DE.md) · [Android-Tests](ANDROID_ABNAHME_02984_DE.md)
