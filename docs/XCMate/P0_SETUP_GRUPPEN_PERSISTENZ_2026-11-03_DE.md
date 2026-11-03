# XCMate P0 – Setup, Sendergruppen und Persistenz (03.11.2026)

**Status:** Fehler auf Android-Gerät beobachtet, Entwicklerdiagnose/Hotfix ausstehend. **Auftrag an Codex, keine Behauptung eines bereits implementierten Fixes.**

## Geräte- und Installationsstand

- Repo: `artattakk-creator/kodi-noodleprivate`, Add-on `plugin.video.xtreammate`.
- Vom Nutzer bestätigt: GS-Media-Installation mit **48 von 48 Komponenten/Abhängigkeiten abgeschlossen**; XCMate-Einrichtungsassistent kann Sendergruppen nicht zuverlässig speichern.
- Logbestätigte Versionen: Kodi 21.3 ARM32; `plugin.video.xtreammate 0.1.29.70`; `script.gsmedia.setup 0.5.19`; `repository.gsmedia.pilot 1.9.12`; `skin.titan.bingie.mod 2.2.3`.
- Aktueller Log identifiziert Box **TX60Pro / Allwinner / Android API 29**. Nicht mit anderer Projektbox (RK3528) gleichsetzen.
- Kodi-Pfad laut Startlog: `special://home/` → `/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi`. Externer/Emulated Storage „status = ok; Permissions = WRITE_EXTERNAL_STORAGE“.
- Nutzerablesung unter Kodi-Systeminformationen: `/` 1,3 GB / 100 %; `/storage/emulated/0` 227,5 GB, davon 224,5 GB frei. **Root 100 % ist kein Beweis für vollgelaufene Kodi-Datenpartition; keine Daten verschieben oder Root bereinigen ohne weiteren Befund.**

## Belege aus lokal bereitgestellten Kodi-Logs

Vier Dateien vom 03.11.2026, zwei Paare mit teils identischem Inhalt: `kodi(20261103-203203).log`, `kodi(20261103-203204).log`, `kodi.old(20261103-203158).log`, `kodi.old(20261103-203207).log`. **Rohlogs nicht in GitHub hochladen:** können persönliche Daten, Provider-Zugangsdaten und Netzwerkadressen enthalten. Zeitangaben direkt aus Log, ohne separate Zeitzonengarantie.

1. **Setup-Discovery mehrfach fehlerhaft (neuere Logs):**
   - 20:58:33 Setup-Dialog `XCMateSetup.xml` geladen.
   - 20:58:33 `[XCMate][SETUP37] stage=DISCOVER_BEGIN`, 20:58:37 `DISCOVER_DONE`, unmittelbar wieder `DISCOVER_BEGIN`; 20:58:38 `DISCOVER_FAILED`; Warnung `XCMate setup: stage=discover code=XM-SETUP-NET type=OSError`.
   - Weitere gleiche Muster um 20:58:43, 20:59:59, 21:00:02 sowie 21:30:54 (insgesamt fünf beobachtete Fehler in der längeren aktuellen Datei).
   - Die Kombination `DISCOVER_DONE` und unmittelbar folgendem `DISCOVER_BEGIN` **kann** auf doppelte Trigger, asynchrones UI-State-Problem oder weitere legitime Discovery-Schritte deuten. Ursache nicht vorwegnehmen.
   - Um 21:31:20 `stage=NATIVE_RELEASED`; keine nachweisbare erfolgreiche Gruppenpersistenz in diesen Zeilen.
2. **Route `import_legacy_settings` wiederholt (neuere Logs):**
   - Viele `[XCMate][BOOT] ROUTE action=import_legacy_settings` zwischen 21:00:18 und 21:00:52 sowie erneut 21:27–21:28.
   - Einzelaufrufe zeigen `PORTALS_MIGRATION_DONE` und `DISPATCH_DONE`; danach um 21:00:52 und 21:28:07 `GetDirectory - Error getting plugin://plugin.video.xtreammate/?action=import_legacy_settings` und `CGUIMediaWindow::GetDirectory ... failed`.
   - **Nicht behaupten, die Migration selbst scheitere immer:** Diskrepanz zwischen erfolgreichem Dispatch und Kodi-Verzeichnisfehler untersuchen. Mehrfachaufrufe/Loop, Rückgabe `endOfDirectory`, Aktivierung/Navigation sowie idempotente Migration analysieren.
3. **BINGIE-Postboot (neue Logs):** um 20:51:40 `XCMate: post-restart verification failed: POSTBOOT_BINGIE_NOT_ACTIVE`; prüfen, ob Skinaktivierung/Prüfzeitpunkt statt fehlender Installation ursächlich ist.
4. **Ältere Logs (18:04):** `CSettings: unable to load settings from special://masterprofile/guisettings.xml, creating new default settings`. Belegt Ladefehler bei diesem Start, **nicht** pauschal gesamte DB-Korruption.
5. **Ältere Logs, GS-Media-Setup:** Python-Importfehler `ModuleNotFoundError: No module named 'setup_catalog_0516'` bei Setup-Skriptstart (um etwa Zeile 470–478). Abhängigkeit/Paketierung und Migrationspfad prüfen; nicht mit XCMate-Gruppenspeicherung gleichsetzen.
6. **Ältere Logs:** `Permission denied` in anderen Kontexten (etwa Zeilen 417/420); Ursprung vor Schlussfolgerung untersuchen. Keinen bestätigten `database is locked`, `readonly database` oder `no space left` Fehler für die XCMate-Gruppen behaupten.
7. **Sonstige Auffälligkeit:** `[XCMate][START48] phase=LOCAL code=READY ... rows=0`; anhand Code und erwarteter Datenlage einordnen, kein definitiver Indexbeweis.

## Arbeitsauftrag (P0 – schrittweise, erhaltend)

### A. Diagnose vor Änderung
1. Aktuelles `main` und installierte .70 mit Add-on-Metadaten/Repoindex abgleichen. **Kumulativ** nur auf tatsächlich neuerem Versionsstand entwickeln; nie Version zurücksetzen.
2. Codepfade `XCMateSetup.xml`, `SETUP37`, `XM-SETUP-NET`, Discovery-Handler, Provider-Gruppen-API, Auswahl-/Speicheraktion, Datenbank-/JSON-Writer, Restart-Readback sowie `import_legacy_settings` verfolgen. Stacktrace und OSError errno (redigiert) instrumentieren.
3. Dateisystem-Schreibprobe am *effektiven* `special://profile`/`special://home` bzw. XCMate-Addon-Datenpfad; anschließend Datei entfernen. `os.statvfs` / Schreibbarkeit und SQLite `PRAGMA quick_check` **read-only** prüfen. Keine destruktive Reparatur vor Backup.
4. Diagnose-Logging mit Korrelations-ID pro Setup-Lauf: Discover Start/Done/Failed, Provider-Antwort-Metadaten (nur Anzahl, keine URLs/Passwörter), Gruppen geladen/gewählt/committed/neu geladen, Pfad, Zeitdauer, redigierter Fehler. Keine Secrets im Log.

### B. Korrekturen
1. Reentrancy-/Doppel-Trigger-Schutz, Cancel/Retry/Timeout und verständliche Fehlermeldung im Wizard; Änderungen erst nach belastbarer Ursachenanalyse.
2. Gruppenfilter/Startgruppe und Provider-Verbindung **atomar/transaktionssicher** sichern; Fehler sichtbar und Zustand wiederaufnehmbar. Speichern muss durch unmittelbares Readback und einen Prozess-/Kodi-Neustart überprüfbar sein.
3. Bestehende Provider-Zugangsdaten, EPG-Quellen/Zuordnungen, TMDB-Token, BINGIE-Konfiguration sowie alle Add-ons erhalten. Vor Migration Backup mit Restore-Anleitung und Prüfprotokoll.
4. `import_legacy_settings` gegen wiederholte Ausführung/Verzeichnisvertrag absichern; idempotent; Importstatus korrekt behandeln.
5. `setup_catalog_0516` Packaging-Fehler im GS-Media-Setup getrennt untersuchen/beheben, sofern noch reproduzierbar; Querverweis statt ungeprüftem Umbau.
6. BINGIE Postboot-Prüfung nach Skin-Auswahl und initialisierter GUI durchführen, ohne fremde Skin-Konfiguration blind umzuschreiben.
7. Keine Änderung an Root/Partitionen, keine Verschiebung der Android-Systemdaten und keine factory resets.

### C. Tests und Abnahmekriterien (verbindlich)
- Android ARM32/Kodi 21.3 auf TX60Pro; Hosttests ergänzend, **kein Ersatz** für Gerätetest.
- Ersteinrichtung: Provider importieren; vollständige Gruppenliste sichtbar; Gruppe(n) auswählen; explizit speichern; Wizard verlassen; XCMate neu öffnen; Kodi neu starten; identische Auswahl nachweisen.
- Repeat: mindestens drei Import-/Speicherzyklen; Erkennung exakt kontrolliert, keine fortlaufende Discovery-Schleife, kein ungehandeltes `XM-SETUP-NET`.
- Netzwerkfehler/Timeout/Provider nicht erreichbar; Wizard lässt zurück/retry ohne Verlust gespeicherter Daten.
- Legacy-Migration wiederholt aufrufen; kein UI-Endlosloop und kein `GetDirectory`-Fehler; keine mehrfach duplizierten Konfigurationen.
- Sicherung und Readback auch bei erzwungenem Speicherfehler/SQLite-Lock; kein partiell gültiger Zustand.
- Kodi-Einstellungen und Skin erhalten; Backup/Restore nachweisen; alle 48 Pakete weiterhin installiert. EPG/Widgets/Filme/Serien auf offensichtliche Regression prüfen.
- Testreport mit PASS/FAIL/NOT_TESTED, Logauszügen ohne Secrets, Commit SHA, ZIP SHA256, Versionspfad, GitHub Actions / Repoindex, Android-Einzelabnahme.

## Auslieferung und Freigabe

- Codex: eigenständigen Fixbranch/PR anlegen, nach aktuellem main rebasen; Tests + Bericht, reproduzierbares ZIP/Hash. Versionsnummer höher als tatsächlich veröffentlichter Stand wählen; **nicht** blind auf .71 fixieren, falls main schon weiter ist.
- Kein Reset/Deinstallieren/Überschreiben von Benutzerdaten. Deploy mit sicherem Upgrade, explizitem Backup und Rollback-Plan.
- **Kein automatischer Merge nach main ohne dokumentierte Abnahme**, sofern kein gesonderter ausdrücklicher Mergeauftrag erteilt wird. Gerätebefunde als NOT_TESTED kennzeichnen, wenn sie noch nicht vorliegen.

## Kurzer Codex-Startbefehl

> Lies `docs/XCMate/P0_SETUP_GRUPPEN_PERSISTENZ_2026-11-03_DE.md` und den zugehörigen GitHub-Issue. Diagnostiziere und repariere P0 (Discovery-OSError, Gruppenpersistenz, Legacy-Import-Loop) **kumulativ und datenbewahrend**. Erstelle PR, Tests und testbares Paket; dokumentiere PASS/FAIL/NOT_TESTED und verlange Android-Abnahme vor main-Merge.
