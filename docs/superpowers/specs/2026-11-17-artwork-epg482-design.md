# .90 → .97 Artwork-Regression und EPG-Dialog #482

Basis: QA-Branch 1cea11d75c6f61accc39142aeb1c0004a88da4cb, unveränderte veröffentlichte .97-Produktquelle f0f6649edf075338bb6a806eff231eb718948368. Referenz .90: 9bbf75040378dcaead9128880a909fe7978143a4. AGENTS.md und beide lokalen QA-Profile gelten. Zwei unabhängige read-only Erstanalyseberichte liegen vor; erst danach beginnen Tests und Implementierung.

## Entscheidung und Grenzen

Der Nutzer hat Analyse → beide Berichte abwarten → Regressionstests → minimale Korrektur → beide erneut prüfen → Draft ausdrücklich beauftragt. Routineentscheidungen werden hier dokumentiert; keine zusätzliche Planfreigabe. Inline-Implementierung durch den Hauptagenten, unabhängige QA durch die beiden bereits gestarteten Prüfer. Projektlokale Custom-Agent-Auswahl ist nicht verfügbar; gleichwertige Subagenten lesen die vollständigen TOML-Profile und verwenden deren Sol-high/Sol-medium-Einstellungen.

Ein minimaler gemeinsamer Controller bleibt beiden EPG-Einstiegen erhalten. Keine zweite Mapping-Datenbank, kein anderer Player, kein Quellen-Import beim bloßen Suchen. Alternative vollständiger XMLTV-Scan bei leerer Suche wird verworfen: Ein lokaler Nichttreffer oder DB_BUSY ist kein fehlender Feed. Kalte Quelldaten werden nur nach ausdrücklicher Ladeaktion begrenzt gelesen. Vorschläge normalisieren Schreibweisen, wählen aber niemals selbst eine Zuordnung aus.

Artwork benötigt keinen pauschalen Decoder-/Reserve-Rewrite: Beide Versionen liefern bei gesundem Consent in der unabhängigen Hostprobe richtige dekodierte Bilder; dynamischer Fallback arbeitet auch bei 64 MiB freiem Platz und 1-GiB-Archivreserve. Korrigiert werden nachgewiesene stumme Policy-Abbrüche, verlorene Settings-Fehler und fehlende Live-Hero-Statusweitergabe. Ungültige Einstellungen bleiben gesperrt; keine automatische Wiederherstellung oder Token-/Opt-in-Änderung.

## EPG-Zielablauf

Beim Öffnen konfigurierte Quellen anzeigen, Provider stets als Basis; lokaler Status/Anzahl. Suchfeld aus fokussiertem Sender vorbelegen; Kabel Eins/Kabel 1 HD/Kabel1HD als auswählbare Vorschläge, +1/regionale Varianten nicht still gleichsetzen. Lokale Suche meldet Nichttreffer/Busy/Timeout getrennt. Auswahl startet echte reversible Vorschau in Elternansicht und Dialog. Nur vorhandene konsistente Programmdetails autorisieren Save. Der bestehende atomare Quelle+Kanal-Commit mit Cold-Readback, Parent-Apply und Konflikt-/Rollback-Schutz bleibt erhalten. Cancel bleibt schnell; abgelehnte Jobs behaupten niemals eine laufende Arbeit. Source-Wechsel verwirft alte Ergebnisse. Kurze lesbare Statuszeile, tatsächlicher Spinner und sichere Fokuspfade bei 720p/1080p.

## Artwork-Zielablauf

Eventgebundene Statuswerte unterscheiden explizit deaktiviert, später, beschädigte Policy, ungültige Settings, wartend, laufend, gefunden und Fehler. Keine Provider-URL, kein Token und keine privaten Exceptiontexte gelangen in Properties/Logs/PR. Home-Hero und Details zeigen diese Zustände, ohne gültige Last-good-Bilder zu verlieren. Quelle/Profil/Programmwechsel darf keinen fremden Status übernehmen. Bestehende Quelle-/Reserve-/URL-Sicherheit bleibt unverändert.

## Nachweise

Neue Tests zuerst RED, dann GREEN mit realen synthetischen SQLite-/Konfigurations-/Bildbytes und tatsächlichen asynchronen Jobs. Erhalt der #474-/Mini-/Grid-Persistenzfälle. Native Kodi-Linux-Tests mit tatsächlichen Renderpixeln und lesbaren Mappingzuständen in 720p/1080p. Android immer ANDROID_NOT_TESTED. Vollständige Hosttests ausführen; bereits auf unveränderter .97-Basis fehlgeschlagene historische .96-Artefaktverträge getrennt benennen, niemals wegskippen oder als PASS melden.

Kein Merge, keine Veröffentlichung, kein Schreiben in Installations-/Repository-Kanäle und keine Änderungen an realen Profilen, SkinShortcuts, Sendern, Token, EPG-Daten, Sicherungen oder .90-Fallback.
