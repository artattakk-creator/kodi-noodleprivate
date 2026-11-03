# XCMate .71 / Issue #352 – Setup, Gruppen und Legacy-Import

Basis: main bcfe131becdaec86ba0d9880cc67ca8d524c5a4f, XCMate .70. Der reguläre Quellstand bleibt kumulativ; keine alten Entwicklungsbranches übernommen. .71 ist ein Testkandidat, kein produktives Release.

## Beleglage und Grenzen

Der verbindliche Auftrag P0_SETUP_GRUPPEN_PERSISTENZ_2026-11-03_DE.md und Issue #352 wurden vollständig gelesen. Die dort dokumentierten vier neuen Android-Rohlogs liegen diesem Auftrag nicht als lesbare Dateien vor; ihre Befunde werden als dokumentierte Gerätebeobachtung übernommen, nicht als neu durchgeführte Rohlogforensik ausgegeben. Frühere Logs anderer Boxen ersetzen sie nicht.

Ziel ist TX60Pro / Allwinner / Android API 29, Kodi 21.3 ARM32, XCMate .70, GS-Media-Setup .5.19, Pilot-Repository 1.9.12, BINGIE 2.2.3. Keine Gleichsetzung mit RK3528. Die 48/48 Komponenten sind eine Nutzer-/Logangabe; ihr Zustand auf dem Gerät ist hier nicht ausgelesen.

## Nachgewiesene Codepfade

### Discovery und irreführender Netzwerkfehler

Der echte .54-Wizard führt zwei absichtliche, serialisierte Discovery-Jobs aus: Anmeldung, anschließend Kategorien. DISCOVER_DONE → DISCOVER_BEGIN allein beweist keinen doppelten Trigger. Der vorhandene Owner und ein nicht blockierender Worker-Slot bleiben erhalten; ein tatsächlich belegter zweiter Auftrag hat jetzt XM-SETUP-DISCOVERY-BUSY statt XM-SETUP-NET.

Nach erfolgreicher Anmeldung lädt der Kategorienjob Live-, Film- und Seriengruppen und ruft Session.checkpoint auf. Dieser prüfte chmod/fchmod und POSIX-Modusbits streng. Ein Fehler dort wurde als generischer OSError DRAFT_CHECKPOINT_FAILED an die GUI gegeben und dort XM-SETUP-NET zugeordnet. Das ist eine reproduzierte lokale Fehlerkette; ohne den konkreten Android-errno ist nicht bewiesen, dass alle fünf dokumentierten Gerätefehler genau dadurch entstanden.

Android-emulierter App-Speicher kann synthetische Modusbits oder nicht unterstütztes chmod liefern. .71 erkennt ausschließlich den Kodi-eigenen, konfigurierten Android/data/org.xbmc.kodi/files/.kodi-Profilunterbaum mit passendem Prozess-UID und ohne Symlinks als Android-App-Backend an. Andere Pfade, fremde Eigentümer und Symlinks erhalten keine pauschale Ausnahme. POSIX-Prüfungen bleiben auf anderen Backends streng. Scheitert der Nachweis auf dem echten Gerät, bleibt die Speicherung gesperrt und wird als lokaler Speicher-/Checkpointfehler gemeldet; kein behaupteter Erfolg.

Der gleiche fchmod-Pfad existierte im EPG-Checkpoint unmittelbar vor der Portal-Veröffentlichung. Der End-to-End-Test mit simuliert nicht unterstütztem chmod hat auch diese zweite Save-Blockade gefunden. Beide Writer verwenden dieselbe Capability-Prüfung; der EPG-Writer schließt seinen Dateideskriptor jetzt auch bei frühem Fehler.

Kategorien werden erst nach vollständigem Abruf aller Arten gemeinsam in den Entwurf übernommen. Fehler, Cancel und Retry behalten Eingaben und vorherige Auswahl; keine automatische Endlosschleife. Passwörter bleiben aus dem Wiederaufnahme-JSON ausgeschlossen.

### Gruppen, Startgruppe und Veröffentlichung

Der neue Button „Startgruppe“ öffnet nur nach ausdrücklicher Auswahl einen nativen Dialog. Der vorhandene Weiter-/Speichern-Ablauf erhält keinen zusätzlichen Zwangsdialog. Gewählte Gruppen und Startgruppe sind getrennte Angaben; eine nicht mehr ausgewählte Startgruppe wird vor Veröffentlichung abgewiesen.

Neue Katalogdaten werden weiterhin unter einer unveröffentlichten Portal-ID vorbereitet. Unter dem vorhandenen Profil-Schreiblock wird zuerst ein begrenztes Konfigurationsbackup mit bytegenauem Readback und SHA256 angelegt. Gruppen aller drei Arten und EPG-Konfiguration werden vor dem Portal-Gate geprüft. Nach Veröffentlichung liest _verify erneut Portal, Auswahl und Katalog über frische Verbindungen. Fehler rollen ausschließlich die neue ID zurück; bestehende Portale und ihre Datensätze bleiben erhalten.

Nichtgeheime Startgruppen-/Sender-IDs werden jetzt auch im Wiederaufnahme-JSON bewahrt. Ein eigenständiger Python-Prozess prüft im Test die tatsächlichen JSON-Dateien nach Save; das ersetzt keinen Kodi-Neustart auf Android.

### Wiederholter Legacy-Import und Kodi-Verzeichnisfehler

Die alte Aktion beendete ein leeres Verzeichnis und rief danach Container.Refresh auf. War die aktuelle Route import_legacy_settings, konnte sie damit sich selbst erneut starten. Erfolgreicher PORTALS_MIGRATION_DONE und nachfolgender GetDirectory-Fehler sind deshalb keine widersprüchlichen Belege für generell fehlschlagende Migration.

.71 entfernt den Self-Refresh. Ein positiver Plugin-Handle rendert nach der Migration genau ein bedienbares Ergebnisverzeichnis ohne Autoplay oder automatischen Wizard-Neustart. Ein RunPlugin-Handle wird nicht mit endOfDirectory(-1) beendet. Der Menüeintrag wird als Aktion gekennzeichnet; Widget-Routen werden nicht geändert.

Alle gültigen Legacy-Slots werden zu einer Liste aufgebaut und einmal atomar veröffentlicht. Vorher schrieb add jeden Slot einzeln; ein Fehler nach dem ersten Slot konnte beim Retry wegen der inzwischen nichtleeren Portalliste weitere Slots auslassen. Bestehende Portale bleiben ein idempotenter No-op. Keine automatische Migration beim normalen Root-/Widget-Aufruf.

### GS-Media-Setup und BINGIE separat

Main enthält das tatsächlich veröffentlichte .5.19-ZIP (SHA256 92756415de0f09cc0f2094f2f5fc1226a64d5bc573c3f5f6103029062da81f60). setup_catalog_0516.py ist darin vorhanden; der ältere .5.16-Paketfehler wird nicht als weiterhin reproduziert behauptet. Eine AST-Prüfung verifiziert alle lokalen setup_*-Importe.

Der bestehende Postboot-Service wartete zwölf Sekunden und bewertete danach einen einzigen GUI-Skin-Snapshot. Das ist anfällig für noch laufende GUI-/Skininitialisierung. Das separat gebaute Begleitupdate .5.20 wartet begrenzt auf zwei stabile aktive BINGIE-Samples. Bei Abort, anderer Skinwahl oder weiter initialisierender GUI bleibt der vorhandene Restart-Marker ausstehend. Keine automatische Skinaktivierung, kein erneuter 48-Komponenten-Installationslauf und kein falsches „Installation kaputt“ allein wegen der GUI-Startphase. Andere Patch-/Widget-/Player-Verifikationen bleiben unverändert.

.5.20 wird aus dem exakten main-ZIP gebaut. Außer Manifestversion, Service und neuer Readiness-Hilfe sind alle Dateien bytegleich. Die 48 installierten Komponenten werden weder neu installiert noch gelöscht; ihre reale Geräteabnahme bleibt NOT_TESTED.

## Neue Diagnose

SETUP71 protokolliert AUTH_BEGIN/DONE, GROUPS_BEGIN/DONE, CHECKPOINT_DONE/FAILED, SELECTED, COMMIT_BEGIN/DONE und READBACK_DONE mit pseudonymer Sitzung, Gruppenanzahlen, errno sowie sicheren Modul-/Zeilenpositionen. Keine rohen Exceptions, Quelltextzeilen, Provideradressen, Passwörter oder Token. Die Schreibprobe läuft ausschließlich im Worker, verwendet den effektiven Kodi-Home-/Profil-/Add-on-Pfad, prüft statvfs, schreibt/liest eine eigene Probe und entfernt nur diese Datei. SQLite quick_check verwendet eine read-only Verbindung; BUSY und beschädigte/unlesbare Daten werden nicht als belegter voller Datenträger ausgegeben.

Root 100 Prozent ist weiterhin kein Beweis für fehlenden Platz am Kodi-Datenpfad. Der ältere guisettings.xml-Ladefehler und fremde Permission-denied-Zeilen rechtfertigen weder Datenbank-Reset noch eine Root-/Partitionsänderung.
