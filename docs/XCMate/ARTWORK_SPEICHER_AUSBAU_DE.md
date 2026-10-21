# XCMate – vollständiges Artwork-Archiv, separater Ausbau zu #41

21.10.2026. Neuer konsolidierter Nutzerauftrag: **erst P0 0.1.29.8, dann separat UI/Artwork**. Dieser Plan ist keine Einstellung auf der Box und keine automatische Speicherumstellung. Ältere Issue-Kommentare „jetzt nur dokumentieren“ werden nicht als zusätzliche Freigabesperre für den ausdrücklich neu beauftragten separaten Ausbau ausgelegt. Produktive Profile/Standardwerte bleiben unverändert; jede spätere Auswahl/Migration erfolgt bewusst im Add-on.

## Belegter Iststand

Persistente URL-/SHA-Jobqueue, Bilder ohne automatische Eviction, ein Download-Lease, sichtbare Seiten vor 48er-Katalogseiten, Retry und lokaler Bildordner existieren. Nicht neu bauen. `media_art_budget_mb` ist 512 MiB, `art_store.budget()` kappt auf 4096 MiB; das ist eine Speichergrenze, kein RAM-Budget. `SPACE_FULL` vermischt Quota und echte Dateisystemreserve. Blindes Retry aller Jobs bringt bei erschöpfter Quota keinen Fortschritt. Aktuelle Nutzerwerte 514/512 MiB, READY3767, SPACE_FULL≈17667 bzw. PENDING≈17638 sind getrennte Momentaufnahmen.

## Prüffähige Umsetzungsschritte

| Schritt | Vorhandenes weiterverwenden | Konkrete Ergänzung / Abnahme |
|---|---|---|
| Speicherpolitik | Alte Budgetpräferenz und Bilder | Eigene versionierte Speicherkonfiguration; Upgrade bleibt 512 MiB bzw. bestehender Wert. Kleine Box/Standard/Große Mediathek/Auto/Experte, keine stille 4-GiB-Kappung; Werte/Reserve/effektives Budget anzeigen |
| Kapazität | check_space / atomare lokale Dateien | Tatsächliche Gesamtkapazität/freier Platz am **Bildziel**, vorhandene Dateibytes inkl. Alt-/verwaister Bilder, dynamisch freier Platz minus Reserve. Vor jedem Download prüfen. Unbekannte Kapazität oder Read-only/offline sicher pausieren |
| Externes Ziel | Kodi-VFS und vorhandene Schreibprobe | Intern/lokaler USB/Mount und geeignete VFS-Ziele getrennt behandeln. Niemals os.path/open/statvfs auf smb://. VFS-Schreib-/Rename-/Hashprüfung; SMB-Freiraum nur bei verifizierter Capability, sonst ehrlich unbekannt/pausiert. Keine erfundene Kapazität |
| Migration | Bestehende Hashdateinamen | Exklusive Wartungssperre gegen Downloads, Journal mit altem/neuem Ziel, bounded Kopierblöcke, Hash+Bytes verifizieren, abbrech-/wiederaufnehmbar. Konfiguration erst nach vollständigem geprüften Transfer committen. Alte Dateien bleiben als Rückfall, kein automatisches Löschen |
| Vollständiger Vorlauf | library_index.Reader + scan-Tabelle | Alle aktiven/importierten VOD-/Serienseiten abarbeiten; Weitersehen→Favoriten→sichtbar→Rest priorisieren. Fehlende/ungültige Provider-URLs separat zählen; URL-/Hash-Dedupe und vorhandene Bilder beibehalten |
| Queue/Resume | jobs/worker, bounded HTTP, Backoff | QUOTA_PAUSED vs DISK_FULL vs READONLY/OFFLINE vs DOWNLOAD_FAILED unterscheiden. Pausen verbrauchen keine 3 Netzwerkversuche. Budget-/Zieländerung reaktiviert kontrolliert die persistente Queue; weiterhin nur begrenzte Worker, keine 17k gleichzeitigen Jobs |
| Anzeige | status(), artwork_db.diagnostic | Ziel/Kapazität/Frei/Budget/Used/Reserve, URL-Coverage, READY/PENDING/Fehler/Pausengründe, DB-Integrität/Prüfdatum/letzter Fehler/Backup getrennt. OK erklärt nur die Job-DB, nicht vollständige Bildabdeckung |

Die Jobdatenbank bleibt lokal/WAL-konsistent; Bilddaten dürfen ein anderes Ziel haben. SMB-/USB-Ausfall darf die lokale Diagnose oder D-Pad-Navigation nicht blockieren. Remote-Existenz-/Hash-/Freiraumprüfungen nur im Worker; GUI erhält einen lokalen Snapshot bzw. verifizierte Bildreferenzen und Fallback. Ohne tragfähige VFS-/Freiraumfähigkeit keine falsche Vollunterstützung versprechen.

## Tests und Grenzen

Reale lokale temporäre Dateisysteme/SQLite plus kontrollierter VFS-Adapter: 512 MiB erschöpft, 8/16+ GiB konfiguriert, kleine Disk/Reserve, unbekannte Kapazität, Read-only, 10k+ Quellen/Jobs, fehlende URLs, Downtime/Neustart/Lease, Pausen-Reaktivierung, Migration mit Hashfehler/Abbruch/USB weg/Renamefehler, alte Dateien unverändert, bestehende Profile nicht umgestellt. Keine Tests füllen die echte Box bis null Bytes.

Android offen: physische USB-/SAF-/SMB-Berechtigung und Kapazität, Migration/Trennen/Wiederverbinden, lange reale Bildlisten und vollständige URL-Coverage. „Alle verfügbaren Bilder“ ist Ziel unter tatsächlicher Provider-/Netz-/Zielkapazität; fehlende URLs/HTTP-Fehler sind keine zu garantierenden Bilder. Kein neuer Portalimport, kein DRM-Bypass und keine pauschale DB-/Bilderlöschung.

Implementierung und Paketierung getrennt vom P0-Hotfix, eigene Draft-PR und Android-Anleitung. Bestehender `cache_dir` wird nicht als Artwork-Ziel ausgegeben. Keine automatische Installation, Migration oder Releaseaktion.
