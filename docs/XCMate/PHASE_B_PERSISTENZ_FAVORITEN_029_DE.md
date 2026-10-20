# Phase B – dauerhafte Medienbilder und persönliche Coverreihen

20.10.2026. Refs #41/#44, auf Phase A / PR #45 und Start-Hotfix #39 aufgebaut.
**Entwicklungskandidat 0.1.29, keine Veröffentlichung oder Android-Abnahme.**
[Gesamtauftrag](CODEX_AUFTRAG_UNIVERSAL_029_DE.md) · [Architektur/Dateiplan](ARCHITEKTUR_UNIVERSAL_029_DE.md).

## Umsetzung und Ursache

Der bisherige Bildpfad lag bereits im dauerhaften Profil, entfernte jedoch nach jedem
Download alles oberhalb von 64 Dateien/32 MiB. Genau diese Eviction entfällt. Bestehende
Dateien im `media_art_v1` werden ohne Verschieben/Neuladen übernommen. `art_store.py`
registriert Jobs in einer zusätzlichen kleinen SQLite-Datei; keine zweite Medienbibliothek.
Status, Bytes, Priorität, Versuche und Wiederholungszeit überleben Kodi-Neustarts.

- Native PNG-/JPEG-Abmessungsprüfung und bestehende HTTP-/Pixel-/Einzelbildbudgets
  bleiben erhalten. Beschädigte Header werden nicht als gültiges lokales Bild verwendet.
  Dies ist keine vollständige native Kodi-Bilddecoder-Abnahme.
- Maximal ein gültiger datenbankgestützter Download-Lease; abgestürzte Jobs nach
  30 s wieder übernehmbar. Überholter Worker kann den Lease eines Nachfolgers nicht löschen.
- Sichtbare Seiten/Details vor ausgewählten Kategorien; eine lokale 48er-Katalogseite
  pro Servicezyklus für Hintergrundaufträge. Deaktivierte Bereiche/Gruppen ausschließen.
- Erfolgreiche Bilder niemals automatisch löschen. Bei Budget/vollem Datenträger neue
  Downloads anhalten, Status SPACE_FULL; drei begrenzte Jobversuche mit Backoff.
  Transport behält seine bestehenden zusätzlichen, zeitbegrenzten Retry-Regeln.
- **XCMate-Einstellungen → Bildspeicherbudget (MiB)**, Standard 512 MiB, wirksame Grenze
  32–4096 MiB. Vor Download zusätzlich mindestens 32 MiB freien Speicher reservieren.
  Größere Budgets sind keine freie-Speicher-Garantie. Budgetverkleinerung löscht nichts.
- **Einstellungen → Speicher → Bildspeicherstatus / Fehlgeschlagene Bilder erneut laden**:
  lokale Zähler und Budget; bewusst ausgelöster Retry. Kein Uploadserver, keine
  automatische Bereinigung aktiver Bilder. Ein komfortabler selektiver Bild-Löschdialog
  ist nicht Teil dieser Phase; Budget ggf. erhöhen oder spätere explizite Bereinigung nutzen.
- `MediaWindow` beobachtet die lokale Verzeichnisrevision und aktualisiert alle
  sichtbaren Kacheln einschließlich nicht fokussierter Titel, Details und Hintergrund.
  GUI-Callbacks laden keine Bilder direkt über HTTP. Bereits gültige lokale Dateien
  führen zu keinem erneuten HTTP-Abruf.

## Oberfläche und Status

Film- und Serien-Landingansichten haben drei eigene horizontale Kodi-Listen:
**Neu hinzugefügt**, **Meine Favoriten**, **Weiter ansehen**. Bestehende Gruppen-/Grid-
und Detailansichten werden wiederverwendet. ID 110 bleibt Neuheiten; 111/112 sind neue
Rails, 113–115 deren Beschriftungen. Leere Rails zeigen Hinweise; vertikale Navigation
überspringt leere Reihen, OK öffnet Detail, Menü in Favoriten entfernt sofort.

Die XML-Steuerung verschiebt Fokus nativ vor dem Action-Callback. Der Callback verwendet
vorherigen Fokus statt dieselbe Taste nochmals auf den schon verschobenen Fokus anzuwenden.
Das strikte Kodi-Modell wurde dafür korrigiert: native C++-Fokusbewegung ruft keinen
Python-Override von `setFocusId` auf. Neue Tests erfassen den sonst doppelten Fokuswechsel.
Back aus einem Favoritendetail stellt die vorherige Rail wieder her.

Favoriten verwenden unveränderte ID-Schlüssel in `media_state_v1.sqlite`; additive
`favourite_items`-Tabelle hält letzte lokale Metadaten. Ein fehlender Provider-/Indexeintrag
löscht keinen Favoriten. Er wird mit gespeicherter Information und Unverfügbarkeits-
hinweis gezeigt, ohne einen erfundenen Titel/Stream aufzulösen. Bereits vor diesem
Update gespeicherte Favoriten können erst beim nächsten lokalen Verfügbarkeitstreffer
vollständige Snapshot-Metadaten erhalten; vorher eindeutiger Hinweis statt Falschangabe.

Weitersehen basiert ausschließlich auf vorhandenen validen VOD-/Episoden-Positionen.
Beendete Medien verlassen diese Rail, **nicht die Favoriten**. Episodenschlüssel bleiben
Account/Serie/Staffel/Folge. Bestehende manuelle Gesehen-/Ungesehen-/Reset-Aktionen bleiben,
Folgen zeigen Prozent und Status; Staffelübersichten zeigen gesehen/gesamt und Status.
Nächste Folge berücksichtigt die erste noch ungesehene Folge auch bei Lücken im Verlauf,
statt blind hinter die höchste als gesehen markierte Folge zu springen.

## Prüfung und Grenzen

417/417 vollständige Regressionen in 60,714 s bestanden; danach abschließende
31/31 bestehende UI-Fälle und 11/11 Persistenz-/Rail-Fälle nach letzten UI-Anpassungen
bestanden. Neu: 130 unterschiedliche gespeicherte Bilder bleiben erhalten; erneut öffnen
und Modulneustart verursachen **0 zusätzliche HTTP-Aufrufe**. Queue-/Retry-/Lease-
Wiederaufnahme, Budget/ENOSPC ohne Eviction, defekter Header, Favoriten offline und nach
Medienende, Prozentstatus, Fokus, sofortiges Entfernen und Aktualisierung nicht
fokussierter Bilder geprüft. Bildfixtures sind kleine synthetische PNGs (100×150); diese Werte
sind keine Android-RAM-/Decoder-/Download-Leistungszahlen. Build-/Paketnachweis folgt unten.

Andere Add-ons, Live-Overlay/-Remote-Dateien, originale Portale, Gruppen und EPG-
Konfiguration unverändert. Englisch/deutsch erweitert; Kodi-Sprache wird nicht geändert.
Erste DB-Öffnung ergänzt ausschließlich neue Job-/Snapshot-Tabellen. Keine Löschung
bestehender Fortschritte, Favoriten oder Bilder. Große Joblisten benötigen zusätzlichen
Profilplatz; Job-Metadaten und Imagebudget sind getrennt vom SQLite-Medienindex.

## Android-Test – alle neuen Fälle OFFEN

1. Nach Phase-A-Stop-/Resume-Abnahme Film und Serie öffnen, drei Rails per D-Pad/OK
   durchlaufen. Leere Reihen und Rückkehr aus Favoritendetail, Kontext entfernen prüfen.
2. Mindestens 130 reale verschiedene Poster/Fanarts laden; Film↔Serie↔Zurück und
   Kodi-Neustart. Bereits geladene Bilder bleiben vorhanden, offline weiter anzeigen.
3. Sichtbare nicht fokussierte Kacheln erscheinen ohne Neuöffnen; Bild-/Fokus-Flackern
   und Lesbarkeit der drei Reihen auf 720p/1080p/4K beurteilen.
4. Kleines Budget konfigurieren, Download pausiert mit SPACE_FULL, bestehende Bilder
   bleiben. Budget erhöhen und Retry auswählen. Keine echte Box bis auf null Bytes füllen.
5. Kodi während laufender Downloads beenden/neustarten; Fortschritt aus Jobs weiterführen.
6. Mehrere Staffeln, manuell Gesehen/Ungesehen und automatische 90%-Schwelle prüfen;
   nächste ungesehene Folge, Weitersehen und Favoriten unabhängig voneinander.
7. Live-Remote- und Start-Hotfix-Regressionsplan unverändert ausführen. Kein globales
   Keymapping, kein Eingriff in fremde Skins. Native Bild-/Fokuswirkung bleibt Geräteabnahme.

Rollback ohne Profilverlust: Kodi beenden, Profil einschließlich SQLite/WAL sichern,
vorheriges offizielles ZIP über dieselbe ID installieren. Additive Job-/Snapshot-Dateien
bleiben unbenutzt erhalten; keine Deinstallation mit Benutzerdaten.

## Geprüftes Paket

[Test-ZIP 0.1.29](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.zip),
109 Dateien / 344929 Bytes; CRC/Syntax und alle Quellbytes geprüft.
SHA256 `92239fca8ba12169f4ded8b57a40866f15c14375bb4188c45503da6f66733ea0`.
[Maschineller Nachweis](TESTERGEBNISSE_PHASE_B_029.json).
