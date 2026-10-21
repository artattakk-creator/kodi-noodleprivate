# Artwork 0.1.29.10 – separater Feature-Testkandidat zu #41

## Stand und Grenzen

Basis ist ausschließlich der Navigations-Hotfix 0.1.29.8 / PR #76.
Der UI-Kandidat 0.1.29.9 / PR #77 ist ein unabhängiger Geschwister-Branch.
Die höhere Testversionsnummer bedeutet keine Veröffentlichung und keine
Freigabe für die Box. Die Kombination UI + Artwork + SpacePremium bleibt
bis zur Android-Abnahme und gesonderten Integration offen.

Dies ist eine konkrete lokale/USB-Implementierung. **Direkte SMB-/VFS-Ziele
sind weiterhin nicht vollständig implementiert:** Kodi liefert dort keine
verlässliche freie Laufwerkskapazität. Der Dialog erklärt die Grenze und
lässt das bisherige Ziel bestehen; ein direkter Backend-Aufruf pausiert mit
CAPACITY_UNKNOWN. Es werden keine Python-Dateisystemfunktionen auf smb://
angewandt und keine Zugangsdaten in die Diagnose übernommen. Ein eigener
VFS-Adapter mit verifizierbarer Kapazität, atomarem Commit und gepuffertem
Verfügbarkeits-Snapshot wäre für echte SMB-Unterstützung noch erforderlich.
Ein eingebundenes Laufwerk muss als lokaler, beschreibbarer Pfad verfügbar
sein. Android-13-SAF/content:// und reale USB-Schreibrechte: **NOT_RUN**.

## Speicherpolitik

`art_storage.py` verwaltet ausschließlich die Bilddateien. Der allgemeine
cache_dir und die lokale Job-Datenbank werden nicht verschoben. Ohne explizite
Auswahl bleibt media_art_budget_mb erhalten (Standard 512 MiB). Die alte
stille Obergrenze von 4096 MiB entfällt auch für bisherige größere Eingaben.
settings.xml und seine Defaults bleiben bytegleich zur Hotfix-Basis.

Einstellungen → Speicher → Artwork-Speicher:

| Profil | Zugewiesenes Budget |
|---|---:|
| Kleine Box | 256 MiB |
| Standard | 1024 MiB |
| Große Mediathek | 16384 MiB |
| Automatisch | vorhandene Bildbytes + tatsächlich freier Platz − Reserve |
| Experte | 32 bis 1048576 MiB, einschließlich >4 GiB |

Die Reserve wird ausdrücklich in MiB gewählt (32 bis 1048576). Die Oberfläche
zeigt Werte und fordert vor dem Speichern Bestätigung an. Es gibt keine
ungefragte Umstellung auf Große Mediathek/Auto. Der Worker prüft vor HTTP und
vor dem Dateicommit die Kapazität am tatsächlichen Bildziel. Die Prüfung vor
HTTP reserviert konservativ bis zu 3 MiB für ein einzelnes Bild. Tatsächliches
ENOSPC und Schreibrechtfehler bleiben eigene Zustände.

Der tatsächliche Bildverbrauch umfasst auch nicht in Jobs erfasste .img-Dateien
und liegengebliebene eigene temporäre Bilddateien. Ein Worker-Snapshot wird
spätestens nach 60 Sekunden erneuert, erfolgreiche Writes werden unmittelbar
verbucht; es gibt keinen Vollscan bei jedem Bild oder Fernbedienungsdruck.
Bilder werden nicht zur Durchsetzung eines kleineren Budgets entfernt.

## Queue und Vollständigkeit

- Alle aktuell lokal importierten, aktiven VOD-/Serienkataloge werden in Seiten
  von 48 Titeln gescannt. Disabled Portale/Medienarten/Kategorien bleiben außen vor.
- Alle gültigen HTTP(S)-Adressen aus cover, stream_icon, movie_image und jedem
  gespeicherten backdrop_path-Listeneintrag werden erfasst. Exakte gleiche URLs
  teilen einen SHA256-Job/Dateinamen. Unterschiedliche URLs desselben Bildinhalts
  bleiben getrennte Dateien; keine unbelegte inhaltliche Deduplizierung behauptet.
- Quellen ohne gültige Poster-/Fanart-Adresse werden im Kataloginventar gezählt.
  Ein Poster als sichtbarer Fanart-Fallback verschleiert die fehlende Fanart-URL nicht.
- Prioritäten: Weiter ansehen 0 → Favoriten 5 → sichtbar 10 → übriger Katalog 20.
  Auch die vorbereitenden ID-Scans sind auf 48 Datensätze je Durchlauf begrenzt.
- Scanposition, Inventar und Jobs bleiben in SQLite erhalten. Eine gescheiterte
  Queue-Schreiboperation darf die Scanposition nicht vorrücken. Bei neuer
  Katalogrevision/aktiver Auswahl beginnt deren Inventarisierung erneut.
- Bereits geprüfte Bilddateien bleiben erhalten und werden nicht erneut geladen.
  Der Service startet den Worker auch nach bereits abgeschlossenem Katalogscan
  erneut. Es gibt einen lokalen Thread, einen SQLite-Lease und zusätzlich eine
  prozessübergreifende exklusive Dateisperre über die vollständige Downloadphase.
  Ein abgelaufener Lease kann dadurch keinen zweiten parallelen Download starten.
- HTTP bleibt auf 3 MiB/Bild und 6 Sekunden begrenzt, mit maximal drei Versuchen
  und Backoff. Überdimensionierte/ungültige/nicht erreichbare Bilder bleiben
  nachvollziehbare Fehler, keine zugesagte Vollständigkeit.
- QUOTA_FULL ist das zugewiesene Budget; DISK_LOW/DISK_FULL betrifft den echten
  freien Platz. STORAGE_OFFLINE, PERMISSION_DENIED, CAPACITY_UNKNOWN, MIGRATING
  und POLICY_INVALID werden getrennt behandelt. Kapazitätspausen verbrauchen
  keine Netzwerkversuche. Eine globale persistente 60-Sekunden-Pause verhindert,
  dass eine volle Queue tausende Jobs nur zum erneuten Scheitern durchläuft.
- Nach bewusster Budgeterhöhung werden Kapazitätsjobs freigegeben. Alte
  SPACE_FULL-Jobs mit bereits drei Versuchen werden dabei ebenfalls reaktiviert;
  READY-Dateien und echte Downloadfehler bleiben erhalten. Weiterhin ein Download
  nach dem anderen. Die bisherige ausdrückliche Retry-Aktion bleibt verfügbar.

Das Inventar zeigt vollständig=1 nur für den aktuell importierten lokalen
Katalog, nicht für unimportierte Titel beim Anbieter. Weiterhin können URLs
fehlen oder unzugänglich sein. Kein falsches Versprechen aller Anbieterbilder.

## Migration und Ausfall

Die Zielauswahl ist getrennt von der Profilwahl. Vor Start erfolgt eine
Bestätigung. Kopieren/Hashprüfung laufen ausschließlich im Hintergrund.
Das Ziel erhält ein dediziertes XCMateArtwork/media_art_v1-Unterverzeichnis
und einen Volume-Marker. Ein entfernter oder falscher Datenträger wird nicht
unter gleichem Namen als leerer interner Ersatzordner neu angelegt.

Der Worker pausiert neue Jobs. Die Migration erwirbt eine prozessübergreifende
exklusive Sperre; ein bereits laufender begrenzter Download darf vorher enden.
Kopieren erfolgt in 1-MiB-Blöcken, mit Reserveprüfung, fsync und SHA256-Prüfung
vor atomarem Rename. Jede endgültige Datei wird nochmals geprüft. Konflikte
mit abweichenden vorhandenen Zieldateien werden nicht überschrieben. Erst wenn
alle Bilder bestätigt sind, wechselt die atomar gespeicherte Konfiguration.
Originalbilder, DB, Profil und Portaldaten werden nicht gelöscht.

Ein lokales Journal zeigt COPYING/VERIFIED/Fehler und Zähler. Nach Abbruch oder
Kodi-Prozessende bleibt das bisherige Ziel aktiv. Die erneute Auswahl desselben
Ziels verifiziert vorhandene Kopien und setzt kontrolliert fort; keine automatische
unbestätigte Migration beim Neustart. Bei abgezogenem USB nach erfolgreichem
Wechsel stehen die erhaltenen alten lokalen Bilder als Rückfall bereit, neue
Downloads pausieren. Auf dem neuen Ziel später geladene Bilder bleiben auf USB
und sind während dessen Abwesenheit nicht verfügbar; kein Datenverlustversprechen
für einen physisch beschädigten Datenträger.

## Diagnose

Artwork-Status zeigt Profil, Bildziel, Laufwerkskapazität/freien Platz, zugewiesenes
Budget, tatsächliche Bildbytes, Reserve, Jobzahlen und Pausengrund. Daneben stehen
Katalogabdeckung und fehlende URL-Arten sowie der vorhandene artwork_db-Gesundheits-
Snapshot (Code, letzte Prüfung, gemeldeter SQLite-Code, Backup, Reparaturbedarf).
OK erklärt nur die letzte Datenbankprüfung. Es behauptet weder komplette Bilder
noch erfolgreichen USB-Zugriff. Altes SPACE_FULL bleibt ausdrücklich mehrdeutig;
die Messwerte 514/512 MiB und die unterschiedlichen READY/SPACE_FULL/PENDING-
Momentaufnahmen beweisen keinen physisch vollen Android-Datenträger.
Die bestehende Backup-/Indexreparatur bleibt bestehen, keine pauschale Neuerstellung.

## Android-Abnahme – NOT_RUN

1. Zuerst 0.1.29.8 gemäß P0-Plan bestehen lassen. Kodi-Profil sichern. Für diesen
   isolierten Kandidaten keinen vorhandenen UI-/Theme-Teststand überschreiben.
2. Nach Installation ist das alte Budget unverändert, vorhandene Bilder bleiben.
   Filme/Serien/EPG/Home/Live jeweils mehrfach öffnen und Back/Stop prüfen.
3. Große Mediathek oder Auto bewusst wählen; Budget und Reserve kontrollieren.
   Bei >4 GiB muss die Anzeige diesen Wert tatsächlich behalten.
4. Mit voller alter 512-MiB-Quota: Budget erhöhen, READY unverändert, PENDING
   sinkt kontrolliert, keine parallele Massenanforderung. Kodi neu starten,
   Queue und Bilddateien müssen weiter vorhanden sein und fortgesetzt werden.
5. Mit kleinem Budget sicher QUOTA_FULL erzeugen. Tatsächlich kleinen freien
   Speicher nur auf einem Testvolume simulieren, die Android-Box nie bis null
   füllen. DISK_LOW/DISK_FULL müssen anders angezeigt werden. Reserve beachten.
6. Nur einen dedizierten beschreibbaren USB-Testordner wählen. Kopie bestätigen,
   Fortschritt ansehen, Abschluss VERIFIED, Stichproben nach Neustart. Originale
   müssen vorhanden bleiben. Android-Berechtigungsdialoge konkret protokollieren.
7. Migration kontrolliert unterbrechen; altes Ziel bleibt aktiv, erneute Auswahl
   setzt nach Prüfung fort. USB nach erfolgreicher Migration entfernen: ältere
   lokale Bilder sichtbar, neue Jobs STORAGE_OFFLINE, kein interner Ersatzordner.
   Wieder verbinden, ausdrückliches Retry bzw. nächsten Pausenablauf prüfen.
8. Read-only/falscher Datenträger sowie direktes SMB/content:// testen: eindeutige
   Ablehnung/Pause, keine Änderung des aktiven Ziels, keine Zugangsdaten im Log.
9. Nach Katalogscan Inventar und Provider-Stichproben vergleichen. Fehlende
   Poster-/Fanart-URLs und HTTP-/Bildfehler dürfen keine komplette Abdeckung vortäuschen.
10. 20 Minuten IR-Navigation; reine D-Pad-Bewegung darf keine HTTP-Abfrage starten.
    Bei Fehler keine Freigabe, keine Datenlöschung; dokumentierter Rückfall 0.1.29.6.

## Verifizierte Host-Ergebnisse

582/582 Regressionstests bestanden, 82,265 Sekunden, keine Fehler/Skips.
Davon 24 neue Speicher-/Migration-/Queue-Tests, einschließlich 17.638
persistenter Jobs, Abbruch/Hashfehler/USB-Ausfall und echter Sperre zwischen
zwei Python-Prozessen. Bestehende 19 Artwork-Recovery-/Start-Routentests und
11 Persistenztests bleiben bestanden. Die physische Großspeicher-/Low-Disk-
Kapazität wird kontrolliert simuliert; es wurden keine GiB zum Füllen eines
realen Datenträgers geschrieben.

ZIP: 410905 Bytes, 134 Dateien. CRC, sichere Pfade, Quellvergleich, Python-AST
und byteidentische unabhängige ZIP-Reproduktion PASS.
SHA256: ac967a294f50147ef41491aac76ce52076bcd4e9fe244c64efecaaf652b8e668.
Details: TESTERGEBNISSE_02910_ARTWORK.json und TESTLOG_02910_ARTWORK.txt.
14 geschützte Dateien (Live, Remote, Player, EPG, Owner und settings.xml) sind
bytegleich zur Hotfix-Basis: ARTWORK_02910_PROTECTED.json. Das betrifft nicht
art_store/media_art: Diese werden in diesem separaten Feature bewusst geändert.
Native Android-/SAF-/USB-/SMB-Abnahme bleibt NOT_RUN.
