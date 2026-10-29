# XCMate .54 – Ursachen, Architektur und Grenzen

Basis main .53 `e8d14039fd989bd952c8fdf36cdccb8c966da434`; Branch `fix/xcmate-02954-wizard-phases`. Vollständiger Nutzerauftrag vom 29.10.2026 und #263, #255, #262, #261, #259, #249 gelesen. #260 ist inzwischen durch den Nutzer gemergt; keine alten Experimentalbranches übernommen.

## Belegte .53-Ursachen

1. `Draft.scan` umfasste Gruppen UND EPG. `Draft.save` wurde erst danach angeboten. Damit konnte ein EPG-Timeout die Veröffentlichung eines ansonsten brauchbaren Katalogs verhindern.
2. `scan` entfernte seine Arbeitsdatenbanken bei jedem Start und begann alle ausgewählten Gruppen erneut. .53 sicherte die gesamte Scan-Phase erst am Schluss.
3. Discovery hatte 25 s Gesamtlimit und auf 3 s reduzierte Requests; die GUI schloss nach 35 s. Andere Arbeit wurde nach 180 s ohne Statuscallback abgebrochen, obwohl SAX/SQLite weiter aktiv sein konnten.
4. Während XMLTV-Verarbeitung fehlten Zwischenzähler. Die Gruppenstatuszeile 222–250 kollidierte mit Reiterlinien 235–240.
5. Das Add-on-Metadaten-Fanart zeigte auf die alte Datei statt den bereits vorhandenen Lightweight-Splash.

Das sind Codebefunde, keine nachgewiesene Ursache des vollständigen nativen Kodi-/Helper-Startcrashs. Dafür fehlen aktuelle Kodi-/Android-Crash-/ANR-Nachweise. #249 und dieser Teil von #259 bleiben **BLOCKED_LOG_EVIDENCE / Android NOT_TESTED**.

## Produktiver Ablauf .54

Der tatsächliche `open_setup`-Einstieg setzt immer `phased54`. Eigener Auth-Worker prüft wirklich den Anbieter; Erfolg wird ausdrücklich mit „Verbindung erfolgreich. Zugangsdaten bestätigt.“ angezeigt. Danach starten die drei Kategorienabfragen automatisch, noch kein Vollimport. DNS, TLS, HTTP, Auth-Ablehnung und einzelne Request-Timeouts werden ohne private Exceptiontexte unterschieden. Back/Bearbeiten, Retry, Später und gezieltes Passwortbearbeiten bleiben erreichbar.

`wizard_catalog54` importiert ausschließlich ausgewählte Gruppen. Die bestehenden atomaren `library_index`-Heads bleiben der einzige Katalog-Publisher. Zusätzliche private Arbeitstabellen enthalten Gruppenfingerprint, Head-Generation, Zeilenanzahl, SHA256, Alter sowie RUNNING/PARTIAL/COMPLETE. Jeder abgeschlossene Schritt wird gesichert. Resume prüft SQLite, exakte Zeilen/Hashes und höchstens 24 h alte Beweise. Neue/abgewählte/veränderte Gruppen werden gezielt behandelt, kein pauschales Entfernen von Arbeitsdatenbanken. Eine echte leere Gruppe kann als leer bestätigt werden; nichtleere ungültige Antworten und unvollständige Daten sind kein erfolgreicher Leerimport.

Für .53-Entwürfe ohne neue Checkpoints können vorhandene atomare Gruppenheads übernommen werden: ausschließlich im nachweislich eigenen privaten Resume-Ordner, derselben Xtream-Kontoidentität, mit ursprünglicher Auswahl, aktueller passender Gruppenbezeichnung, gültigem Alter, SQLite-Prüfung und Prüfung jedes normalisierten Payloads. Unbewiesene, veraltete oder widersprüchliche Gruppen werden neu angefordert. Keine Übernahme fremder Ordner/Konten.

Nach geprüftem Katalog und ausdrücklichem Speichern verwendet .54 die vorhandene transaktionsgesicherte Portalveröffentlichung. Quellen sind registriert, Gruppen/Live/Filme/Serien verfügbar. Wiederholtes Save desselben geprüften .54-Portals liefert dieselbe ID; kein zweites Portal. Alte .53-EPG-Arbeitsdateien können diesen Katalogabschluss nicht blockieren. Fehler im nachgelagerten EPG führen nicht zum Portal-Rollback.

Die privaten direkten Daten-APIs bleiben für bestehende Aufrufer/Tests kompatibel und können weiterhin einen kombinierten Scan ausführen. Der einzige produktive Wizard-Einstieg verwendet dagegen ausnahmslos die neue getrennte Reihenfolge; diese wird mit echten Owner-/Worker-Aufrufen getestet.

## EPG nach Veröffentlichung

`wizard_epg54` setzt ein bereits gespeichertes Portal voraus. „EPG jetzt fortsetzen“, „EPG später fortsetzen“, „Ohne EPG zu XCMate“ und der EPG-Manager verwenden denselben Pfad. Manager schließt seine native Ebene vor dem Folgefenster. Nach Kodi-Neustart erkennt der Wizard die eigene bereits veröffentlichte Portal-ID und öffnet die offene EPG-Phase statt Login/Neuanlage.

Jede Quelle wird mit dem vorhandenen SAX-Importer vollständig validiert und anschließend einzeln über den vorhandenen konservativen Publisher gespeichert. Der gemeinsame Guide/Quellenarchiv-/Faktenbestand, sieben Tage Vergangenheit/bis +20 Zukunft, manuelle Zuordnungen und LastGood bleiben erhalten. Kein konkurrierender EPG-Speicher. Eine nicht erreichbare Provider-URL blockiert die unabhängigen externen Quellen nicht.

Private begrenzte JSON-Jobbelege speichern Quell-/Konfigurations-/Mapping-/Live-Katalogfingerprint, tatsächliche Source-Zeilenanzahl und Inhaltshash. Eine READY-Quelle wird nur nach erneutem vollständigem Read-only-Datenvergleich und innerhalb von 24 h übersprungen. Geänderte Daten, Auswahl, Quellenkonfiguration oder abgelaufene Belege lösen gezielte Neuverarbeitung aus. Keine rohen URLs, Zugangsdaten, Sendungstexte oder Tokens im Beleg.

Die echte Importgeneration wird vor der Anfrage gesichert. Nach Prozessabbruch werden nur die zu genau dieser belegten Generation gehörigen unsichtbaren Stage-Zeilen entfernt; andere Aufträge und veröffentlichte Programme bleiben unberührt. Ein Absturz noch vor der ersten Tabellenerstellung ist ebenfalls abgedeckt. Netzwerk-, Schreib- oder Belegfehler dürfen keinen falschen READY-Status erzeugen. Bereits veröffentlichte gültige Quelldaten bleiben auch bei anschließendem Checkpointfehler erhalten; erneuter Import ist additiv/idempotent.

Die vorhandene portalbezogene OS-Lease verhindert Konkurrenz mit regulärem Refresh und überlebt das Schließen der GUI bis zur Workerbereinigung. Während einer explizit offenen EPG-Ersteinrichtung startet der automatische Scheduler keinen zweiten Import. Der bestehende Backup-/Schema-/Speicher-Schutz bleibt verbindlich. Insbesondere kann nach Quelle 1 und Abbruch vor Quelle 2 bei einem späteren separaten Lauf zuerst eine normale verifizierte EPG-Sicherung erforderlich sein. Die Oberfläche erklärt diese Sperre. **Keine automatische Sicherung, keine Umgehung und keine Datenbanklöschung.**

Alte .53-EPG-Arbeitsarchive besitzen keine .54-Quellenfingerprints. Sie werden nicht blind als aktueller Quellenabschluss gewertet. Ihre Dateien bleiben im eigenen privaten Arbeitsordner erhalten, auch nach Katalogabschluss; Quellen müssen gegebenenfalls einmal neu validiert werden. Die verlustfreie Wiederaufnahme einzelner bereits belegter Quellen gilt für .54-Jobs. Dies ist ausdrücklich kein behaupteter unveränderter Downloadbeleg für alte .53-Fehlversuche.

## Laufzeit und Fortschritt

Kein 25-/35-/180-Sekunden-Gesamt-Abbruch mehr für aktive Wizard-Arbeit und kein zweistündiger Verfall einer nachweislich lebenden Wizard-Ownership. Der endliche Timeout für ein tatsächlich nicht initialisiertes natives Fenster bleibt. HTTP-Einzeloperationen bei Discovery behalten bis 15 s Sockettimeout, bis 60 s Responsebudget und höchstens einen Retry; XMLTV-Streams behalten ihre vorhandenen begrenzten Einzel-I/O-Timeouts ohne Gesamtdauer. TLS-Prüfung/Benutzereinstellungen werden nicht geändert.

Plattform-DNS lässt sich aus Python nicht sicher zwangsweise beenden. Benutzerabbruch bleibt kooperativ; die alte Lease bleibt bis zum echten Workerabschluss gesperrt. Es wird kein Ersatzworker parallel gestartet. Ein endloses natives DNS-Problem wird deshalb nicht als garantiert sofort unterbrechbar ausgegeben.

Fortschritt entsteht ausschließlich aus tatsächlichen Lese-, Parser-, Matching-, Batch-Commit- und Prüfoperationen: Bytezahl, gelesene/zugeordnete/gespeicherte Sendungen und Gruppen-/Quellposition. Ein koaleszierter, gedrosselter Datencallback geht an den Owner-Pump; kein GUI-Zugriff vom Worker und keine Warteschlange pro Sendung. Unbekannte Gesamtgrößen erhalten keine erfundenen Prozentwerte. Sichtbar ist auch die Zeit seit der letzten echten Messung. Animation allein erneuert keine Aktivitätszeit.

Zusätzliche Schutzkorrektur: `PrefixReader` und lokaler VFS-Reader reichen keine Null-Byte-Leseanforderung durch, die Kodi-VFS als komplettes Dateilesen interpretieren kann. Gültiges/abgeschnittenes gzip und ein solcher VFS-Adapter sind gezielt getestet. Keine Behauptung, dies beweise die Ursache von #249.

## Passwort, Oberfläche und Installationshinweis

Ein neu manuell eingegebenes RAM-Passwort kann nach Fehler/Back gezielt sichtbar oder verdeckt vorbefüllt und bearbeitet werden. Bereits regulär gespeicherte Geheimnisse werden nicht als Klartext-Default geöffnet. Nach Bestätigung steht das Kennwort nicht im Fortschritt oder in Zusammenfassungen. Keine Secrets in Fenster-Properties, Logs, Checkpoints oder Fehlern.

RAM-Erhalt gilt im laufenden Wizard-Interpreter. Nach neuem Kodi-/Python-Interpreter gibt es ohne geprüfte Credential-Ablage nur Passwort-Reentry, während Host/Benutzer/Auswahl/validierte Gruppen erhalten bleiben. Auch explizites „Später“ kann den Plugin-Interpreter beenden. Keine unbewiesene passwortfreie Wiederaufnahme über diese Grenze versprechen. Die bestehende reguläre Portal-Credential-Verwaltung bleibt unverändert.

Die Statuszone verwendet größere Schrift. Reiterlinien, Gruppenzähler und Listen haben getrennte Bereiche; große fünfstellige Zähler und Fernbedienungsfokus werden strukturell geprüft. Neutrale Buttons bleiben. Neues Metadaten-Fanart verweist direkt auf `resources/media/lightweight_splash.jpg`; alle Grafikbytes einschließlich Original-Icon und alter Fanartdatei bleiben erhalten. Kodi-Texturcache wird nicht gelöscht.

Auf ausdrücklichen Nutzerwunsch zeigt .54 bei Erstinstallation UND Update einmal **„Installation erfolgreich“**, **Version**, **Änderungen**. Das bestätigt die tatsächlich installierte Add-on-Version, nicht eine bereits abgeschlossene Portal-/EPG-Einrichtung. Das Popup wartet bei Player/Modal/Stop/Owner-Arbeit und wird nach Bestätigung nicht bei jedem Neustart wiederholt. Deutsch/Englisch und zukünftige Changelog-Fallbacks sind geprüft.

Slideshow ist mangels genehmigter echter Screenshots **BLOCKED_APPROVED_ASSETS**, als separater Folgeauftrag spezifiziert. Keine erfundenen Produktbilder, zusätzlichen Hintergrundthreads oder Netzwerkabrufe. BINGIE-Skin, Skinshortcuts, Home-Widgets und Playergrafiken werden nicht verändert. Box A und B wurden nicht bedient oder installiert.
