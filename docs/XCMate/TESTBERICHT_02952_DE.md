# XCMate .52 – vollständiger Host- und Regressionstestbericht

Basis .51 auf `main`: `2a9a47736384e6af8e1384fddd5d719092cea9cb`. Geprüfter Quellcommit `05c7a96d0dc8984443f8c9d9c1be62a866d26794`. Branch `hotfix/xcmate-02952-epg-series`. Auftrag #257 / #242 / #231 / #232 / #58 / #98 / #183 / #100 und aktueller vollständiger .52-Nutzerauftrag.

## Ergebnis

**2.168 Tests PASS in 313.338 s; 0 Fehler, 0 Failures, 0 Skips.** Alle 2.116 bisherigen Testmethoden bleiben vorhanden und wurden ausgeführt; 52 neue. Vollständige Namen und Ergebnisse: `TESTLOG_02952.txt`; neue Methoden: `NEUE_TESTS_02952.json`; maschinenlesbare Prüfsummen und Ergebnis: `TESTERGEBNISSE_02952.json`.

Der Abschlusslauf stammt aus einem sauberen `git archive` des Quellcommits, mit regulärem Bootstrap, allen drei Upgrade-Schritten, Paket-/Repository-Build, Sprachvalidierung (de/en je 1.122 Kontexte), Prüfung aller 92 Navigationstexturen/Lizenzen und `compileall`. Reale lokale HTTP-/SMB-/Socket-, SQLite-, Großkatalog-, Player-/GUI-/Widget- und Wizard-Regressionsprüfungen liefen mit. Keine Tests deaktiviert und keine neue Kodi-Abhängigkeit. Der erste vollständige Integrationslauf zeigte drei Fehler bei altem unqualifiziertem Metadatenbestand und einen historischen Rohhash-Scopekonflikt. Die Verifikationsumgehung wurde korrigiert, die Source-Name-Proofs werden im Importstadium festgehalten und der historische Scope prüft jetzt dieselben exakten freigegebenen Deltas wie die übrigen Scopefälle. Nach einem weiteren Integrationsbefund bleibt auch der verifizierte Legacy-Faktenfingerprint bei neu im Master sichtbaren Tag-20-Events erhalten. 105 gezielte Prüfungen einschließlich der unveränderten strikten Metadatenfälle bestanden vor dem hier dokumentierten erneuten Gesamtlauf. Vorhandene Hostabhängigkeiten: Pillow, impacket 0.13.0 und simpleeval 0.9.13.

Bekannte unveränderte Warnungen: alte Escape-Sequenz in vendortem `SMBProtocol.py` und ältere Python-AST-Aliase in simpleeval. Kein neuer Laufzeitfehler. Der veröffentlichte Testlog enthält ausschließlich synthetische Testdaten; keine privaten Kodi-Logs oder echten Zugangsdaten wurden verwendet.

## Neue technische Prüfungen

| Gruppe | Anzahl | Evidenz |
|---|---:|---|
| EPG | 26 | Kalender −7/+20, Ausschluss +21/−8, Zukunft-only, kürzerer/fehlgeschlagener Feed, reicher/ärmerer Refresh, andere Titel/Episoden, drei Quellen mit unterschiedlichen IDs, Metadaten/Regie/Cast/Bildherkunft, Dubletten/Konflikte, manuelle Quellkollision, stabile IDs nach Umordnung, deaktivierte Quelle, Offline/Restart, gemeinsame Ereignisidentität, Quellen-/Tagesunion samt alten +20-Fakten, Sommer-/Winterzeit, beide Refresharten, Provider-URL-Ausfall, Backup-Sperre und indexierte Legacy-Portale |
| Serien | 16 | bestätigte Gruppenauswahl, leerer Kategoriencache, Neustart-Reconcile, Live-/Film-Daten bytegetreu als SQL-Rows erhalten, 1.201 Serien, neue Widget-IDs/Cover, keine Doppelrequests, Netzwerkfehler mit gezieltem Retry, leere Quelle ohne falschen Erfolg, Pending-/Running-Cancel, fehlende Providerkategorie, Menüstatus, vollständige Worker-Sperre über Jobdeadline, Abwahl und bestehende native BINGIE-Reload-Brücke ohne Neubindung |
| Pixel | 8 | 720/1080/1440/UHD, vollständige ganzzahlige Paare, Session-/Noncewechsel und verspätete Werte, unbekannte Auflösung, sofortiges Medienverhalten, keine fremde Session, unveränderte Zwei-Sekunden-Drosselung, Rahmen/Fallback und erhaltenes Audio |
| Bestandsschutz | 2 | alle 577 alten Quelldateien und 2.116 alten Methoden ohne zusätzliche Skip-Ausnahmen |

Die gezielten 52 neuen Prüfungen bestanden vor dem Abschlusslauf ebenfalls. Ältere .46-Tests behalten ihre Methoden und prüfen nun **zwei** statt eines Masterprogramms für den bereits vorhandenen Tag-20-Fall, da die frühere Zehn-Tages-Grenze ausdrücklich beseitigt werden soll. Versionsprüfungen wurden auf .52 fortgeschrieben. Historische enge Scope-Tests normalisieren ausschließlich die 19 exakt gehashten, einzeln überprüften .52-Deltas; keine pauschale Whitelist.

## Tatsächlicher Vorher-/Nachher-Nachweis

`REPRODUKTION_02952.json` und `tools/probe_xcmate_02952.py` enthalten den echten Vergleich mit einem unveränderten .51-Archiv. Vorher fehlen +11 und +20 im Master, Nachimport bei leerem Kategoriencache FAILED/0/kein Provideraufruf. Jetzt bleiben vier gültige Tage nach kürzerem Feed erhalten, passende Zweitquellenbeschreibung und Lückensendung werden sichtbar; gezielter Import von Gruppe b liefert 7 Serien im Katalog und dieselben 7 im Widget. Die separate Reload-Prüfung führt anschließend den bestehenden nativen Plugin-Verzeichnisaufruf aus und bestätigt echte ListItems ohne Skin-/Shortcut-Neuschreiben. **Keine Androidmessung.**

Detaillierte Ursachen und unveränderte Schutzbarrieren: `URSACHENANALYSE_02952_DE.md`. Frühere Ein-Tages-Löschung war bereits repariert; nicht als erneut bewiesene .51-Ursache ausgegeben. Der konkrete private Android-Stack liegt nicht vor; deshalb kein behaupteter Geräte-PASS.

## Bestandsschutz und Paket

**558 von 577 bisherigen Quelldateien byteidentisch**, 19 exakt gehashte Änderungen, drei additive Module in der bestehenden Architektur. Wizard .51, Player/.42-Kompatibilitätsmodus, Keymaps, Originalgrafiken, BINGIE-Routen/-Writer und Widgetverknüpfungen byteidentisch. Keine Skin-Datei wurde geändert. Alle 62 Dateien fremder WIP-Verzeichnisse blieben unverändert. Keine Geräteaktion auf Box A oder B.

ZIP: **580 Dateien, 3103751 Bytes**. CRC, sichere eindeutige Pfade, alle Quellbytes und Python-AST PASS. Zusätzlich unabhängig deterministisch rekonstruiert und byteidentisch. Keine Profile, Datenbanken, Logs, Tests oder Bytecode im Paket. `PAKETPRUEFUNG_02952.json` und `DATEIKATALOG_02952.json` dokumentieren alle Bytes.

SHA256: `1117593818b2d29d5b170fee25397c1c31a3ade6f264139371e67a784ef11644`.

Der Liefercommit ergänzt nur Berichte und geprüftes Paket zum unveränderten getesteten Quellcommit. Der finale GitHub-CI-Lauf wird im Draft-PR mit tatsächlichem Head, Lauf-/Joblink, Testanzahl, Artefakt und passender Paket-SHA dokumentiert. Der Workflow darf im PR kein produktives Paket veröffentlichen; `Commit and publish generated archives` muss übersprungen sein. Kein automatischer Merge/Release und keine Issue-Schließung.

## Android bleibt offen

`ANDROID_ABNAHME_02952_DE.md`: **24 Prüfpunkte je Box, insgesamt 48 NOT_TESTED, 0 PASS.** Box A nur nach bewusster Nutzeraktion; keine automatische Installation. Kritisch sind reale private Feedabdeckung, Langzeit-/Offlineverhalten, neue Seriengruppen mit bestehendem BINGIE-Hook, echte Decoderdimensionen und ARM32-Limits. Sind Quellen/Streams nicht verfügbar oder fehlt Backup/Platz, das konkrete Gate offen/BLOCKED lassen. Keine Sicherheitsreserve oder Sperre umgehen und keine Daten löschen.
