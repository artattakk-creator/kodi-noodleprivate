# XCMate .93 – Testbericht und Abnahmestatus

13.11.2026, Entwicklung auf main .92 `3e1d6f87787baa95d24cc4e7c83c24914db31364`. Master #454. Keine Veröffentlichung oder Mergefreigabe.

Gezielte Prüfungen auf den jeweiligen dokumentierten Entwicklungsständen: 14 neue P0-Tests und 16 bestehende Kapazitäts-/Artwork-Tests, **30 PASS**. Zusätzlich 63 bestehende Repository-/Release-/Navigationstests PASS nach Fortschreibung der ausdrücklich veröffentlichten Pilot-.92-Basis und des neuen .93-Manifests. Historische .92-Pakete werden in ihrer tatsächlichen damaligen Source-/Indexbasis reproduziert; der vollständige aktuelle .93-Delta bekommt einen eigenen strengen Guard. Kein Test entfernt oder Skip hinzugefügt.

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


## Abschließender Quellstand in Prüfung

Aktueller Kandidat SHA256 `de5a913ab7d105dde2a19b7e2b7d1adfce74669f794fb63428bf2af3575cef48`, 4.710.157 Bytes/873 Mitglieder. **19 neue P0-Tests**; letzter Paket-/Sprach-/P0-Block 32 PASS. Voriger umfassender gezielter Block 76 PASS, Branding separat 11 PASS und 17 PO-Kataloge gültig. Vollständige aktuelle 3.938-Test-CI und native 720p/1080p noch nicht als PASS erklärt.

Der erste lokale breite Lauf (3.933 Fälle, 89 FAIL/3 ERROR) war kein stabiler finaler Snapshot: währenddessen wurden noch Code, exakte Delta-Fixture und Sprachdateien fertiggestellt. Ein Teil der Hash-/Sprachfehler stammt aus bereits importierten älteren Test-Caches; zusätzlich echte Opt-out-/Fixture-Probleme und im Großtest ein tatsächlicher temporärer Workspace-ENOSPC. Diesen Lauf nicht als PASS verwerten. Reine eigene saubere alte Git-Worktrees entfernt, deren Git-Historie, Branches, Release-ZIPs und sämtliche Android-Daten erhalten; danach im Workspace wieder rund 4 GiB verfügbar. Versions-/Pilot-Baselines und exakte historische Player-/GUI-Deltas fortgeschrieben; keine Testmethoden entfernt oder Skips erhöht. Finale CI nutzt einen unveränderlichen Checkout.

[Physischer Hostbeleg](reports02993/storage-before-after.json): freier Platz auf Device 34 **4.292.644.864 → 4.301.070.336 Bytes**, netto **8.425.472 Bytes**. Ein altes Backupset mit 8.425.687 logischen Bytes entfernt, Keeper mit 2.049 Events/quick_check erhalten, Benutzerquelle unverändert; Intent/Result tatsächlich persistent gespeichert und kalt nachgelesen. Unterschied zu logischen Bytes durch Dateisystemblöcke und eigenes Journal. Kein Android-Platzgewinn und keine Freigabe von Raw-XML behauptet (0 Bytes).


## Visuelle Gegenprüfung des nativen Speicherfensters

Der native 720p-Lauf auf `1d3df02b` bestand seine Control-/Back-Gates, aber die **tatsächlich betrachtete Originalaufnahme zeigte einen transparenten Hintergrund**: skinrelatives `white.png` fehlte, Home schien durch. Deshalb **kein visueller Speicher-PASS** aus diesem Gate. [Beleg](reports02993/native-storage-before.json), [Originalaufnahme](reports02993/storage93-before-720.png). Korrektur: drei eigene vollständig opake PNG-Texturen mit Add-on-absoluten Kodi-Pfaden; echte Panel-/Fokus-/Button-Pixel zusätzlich zum Titel/Text/Back prüfen. Debugoverlay nur im Wegwerf-Testprofil für die Aufnahme ausschalten und danach wiederherstellen. Keine Skin- oder Box-Einstellung geändert. Aktueller korrigierter Build SHA `48e0822827c2a8e8a854a812cbac0d0fb3407f6f6b9a5c3c2c2213f20fe77a95`, 4.711.998 Bytes/876 Mitglieder; alle früheren .93-SHAs überholt. 24 gezielte neue P0-/Paketprüfungen PASS; neue vollständige CI und nativer Pixelgegenlauf ausstehend.
