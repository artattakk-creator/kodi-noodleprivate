# XCMate 0.1.29.90 – Implementierung und Testbericht

**Status: IN PRÜFUNG – keine vollständige P0-Abnahme, kein Merge, kein Release.**

Dokumentationsstand: 11.11.2026, 18:42 Europe/Berlin. Der abschließende Lauf einschließlich der langen nativen Gates wird im [PR-Checkbereich](https://github.com/artattakk-creator/kodi-noodleprivate/pull/431/checks) und im [Master #430](https://github.com/artattakk-creator/kodi-noodleprivate/issues/430) mit Commit und Artefakten festgehalten. Ein vorbereiteter oder laufender nativer Test wird hier ausdrücklich nicht als PASS ausgegeben.

Master [#430](https://github.com/artattakk-creator/kodi-noodleprivate/issues/430), Draft-PR [#431](https://github.com/artattakk-creator/kodi-noodleprivate/pull/431). Kumulative Basis: `cb37de7103bd335a344c6738c33c4b5560ba2d4c`, veröffentlichte .89. Der Produktcode des derzeitigen ZIP wurde zuletzt in `6f8aed4dadf820c5d64cac333f4e523f8d0dc099` geändert; spätere Commits ergänzen bzw. korrigieren den Testaufbau. Der aktuelle PR-Head ist separat im PR ersichtlich.

Das .89-Android-Protokoll bleibt unverändert: dessen tatsächliche FAILs werden durch Hosttests nicht zu PASS. Sämtliche neuen Gerätefälle bleiben **ANDROID_NOT_TESTED**.

## Fehlernachweise und Reparaturen

| Bereich | Reproduzierter Fehler / technische Grenze | Umsetzung |
|---|---|---|
| A Logos | Maximal zwei Versuche je Runde, redundante vollständige Manifest-/Fallback-Lesewege, bereits eigene geprüfte Dateien unnötig durch Legacy-Recovery geschickt. | Maximal acht Versuche innerhalb bestehender Runden-/Requestbudgets, erste sichtbare fünf zuerst, bestehender Worker statt zusätzlichem Threadpool. Unverändertes Manifest nach `dev/ino/size/mtime/ctime` einmal parsen; verifizierte eigene Referenzen zuerst. Fehlende Quellen getrennt, kein erfundenes 88/88. |
| B EPG | `visible75()` und Checkpoint behandelten echte `iptv.Channel`-Objekte wie Dictionaries. Spätere sichtbare Gruppen überschrieben den vorherigen gültigen Checkpoint. | Gemeinsamer SID-Zugriff für Modell-/Dict-Daten; bestehendes begrenztes `home_epg75`-Checkpointformat weiterverwenden. Exakt gleiche Profil-/Account-/Konfigurations-/Guidegeneration zusammenführen; veraltete/fremde Ereignisse nicht übernehmen. Datei-fsync und Byte-Readback vor atomarer Aktivierung. Keine zweite EPG-Datenbank. |
| C Portal/GUI | Bereits validierte unveränderte Portaldaten verlangten erneut die globale Lesesperre und konnten an unabhängigen Profilschreibjobs scheitern. | Unveränderte Datei vor/nach abgetrennter Kopie generationstreu prüfen. Geänderte/entfernte Portaldatei benötigt weiterhin strikte Lesesperre und neue Validierung. Fehlerkategorie statt privatem Ausnahmetext protokollieren. |
| D Film/Serie | Änderung von Live-Startgruppe/-sender änderte auch die Mediensignatur; ein anschließendes SQL-Budgetproblem verlor gültigen Medien-LastGood. | Live-Startwahl nur für Live-Signatur berücksichtigen. Account-, Mediengruppen- und Quellenänderungen bleiben invalidierend. .89-Checkpoint nur über genau passende Legacy-Signatur übernehmen, keine wildcardartige Kontoübernahme. |
| E Fremdwidgets | Zwei gemeinsame/native BINGIE-Fokusfactorys waren auf Home durch `!Window.IsActive(Home)` deaktiviert. | Ausschließlich zwei exakt gehashte bekannte Knoten korrigieren. Eigene Clone-Factory und .88-Geometrie bleiben unverändert. Zusätzlich nur den exakt gehashten eigenen MediaNormal-Self-Visibility-Guard entfernen; Menü-/Quellengates und native/fremde Zeilen bleiben erhalten. Golden-Hash-Prüfung normalisiert ausschließlich diesen Guard. Unbekannte Anpassungen verweigern. Vorhandene Skin nur über bestehenden expliziten Vorschau-/Backup-/Bestätigungsablauf ändern; kein automatischer Rebuild. Dies beweist noch nicht die einzige Ursache sämtlicher Android-Fremdwidgetfehler. |
| F Zuordnung | Nach autoritativer Metadatenanreicherung konnte der Namespace mit Jahr/Land vom ursprünglichen UI-Ereignis abweichen: Commit vorhanden, ursprüngliche Ansicht fand ihn nicht. | Nur unabhängig überprüfte exakte Namespace-Hashes gemeinsam speichern; maximal zwei explizite Aliase, keine unscharfe Titel-/Senderzuordnung. Readback, Kaltladen, Ändern, Ausblenden und Automatik-Rücksetzung berücksichtigen. Lokale Schreibsperre als `PERSISTENCE_BLOCKED`, nicht als Netzwerk-Timeout. 30-s-Gesamtdeadline und .2-s-Schreibbudget unverändert. |
| G Gruppen | Nach gültiger Teilmenge und fehlgeschlagenem Voll-Future wurde der Katalog als vollständig verriegelt; Nachladen blieb aus. Asynchrone Vollübernahme konnte die explizit gewählte Gruppe zurücksetzen. | Gültige Teilgeneration als weiterhin ausstehend erhalten, nach bestehendem Backoff erneut vorbereiten. Vorherige exakte Policy-Generation im Folge-Future erhalten, erlaubte explizite Gruppenwahl beibehalten. Tune-/Stop-/Playercode unverändert. |
| H nativer Picker | Ohne Portal wurden Quellenrouten abgewiesen. Nativer Browse-Root konnte in normalen App-/Autoplay-Ablauf führen. | Gültiger passiver SkinShortcuts-Browse-Kontext bekommt drei echte bestehende Quellen mit Portal; ohne Portal Einrichtung ohne Fake-PID. Gewöhnliche Root-/Videos-Navigation und gespeicherte Leaf-URLs bleiben erhalten. Originalmanager, tatsächliches Speichern und Neustart sind eigenständige native Abnahme, kein bloßer URL-Nachweis. |

## Geänderte Produktbereiche

- Einstieg: `default.py`, `app_routes.py`, `picker_entry90.py`, `widget_sources49.py`.
- Logos/Worker: `logo_manifest86.py`, `logo_store89.py` (nur sichere Zeitdiagnose), `station_logos87.py`, `station_logos88.py`, `widget_assets69.py`.
- EPG/Portal: `programme_prefetch48.py`, `epg_snapshot75.py`, `portal_snapshot.py`, `gui_guard86.py`.
- Medien-/Live-Katalog: `widget_policy74.py`, `widget_data41.py`, `live_catalog.py`; in `live_overlay.py` ausschließlich `_load_catalog_from_disk` und `refresh_from_cache`.
- Mapping: `programme_mapping85.py`, `work_requests86.py`.
- Geprüfter Adapter: `widget_skin78.py`, `widget_skin90.py`, `skin_upgrade63.py`, `resources/bingie90_previous.json`.
- Begrenzte, datensparsame Diagnose: `startup_diag90.py`.
- Version, Changelog und Installations-/Updatehinweis: `addon.xml`, `changelog.txt`. Bestehender Hinweisablauf zeigt .90 und die vorgenommenen Änderungen.

Zusätzliche native Worker-Regression: Ein separater Logo-Retry konnte im gemeinsamen Deferred-Slot den DB-Pausenstatus überlagern und `_pending` nach DB-Freigabe belegt halten (`WORKER82_NOT_RECOVERED`). Logo-Fortsetzungen haben nun einen separaten begrenzten Due-Zustand im selben Worker. DB-Pausen-/Recovery-Quittungen werden nicht überschrieben; doppelte Admission während der Logo-Wartezeit bleibt gesperrt. 40 gezielte Start-/Worker-/Retention-/Mapping-/Scopefälle PASS. Der neue native Wiederholungslauf bleibt eigenständiges Gate.

Keine neue Datenbankschema-Migration. Keine Deinstallation, Löschung, Neuindexierung oder Datenverschiebung als Reparatur. Player-/Exit-/Autoplaycode, Kodi-Keymaps, TMDB-Schreibcode, .88-Skin-/Hero-Geometrie und Installerquellen bleiben geschützt.

## Hosttests und Messwerte

Neue Tests: `test_xcmate_startup_02990.py`, `test_xcmate_retention_02990.py`, `test_xcmate_boundaries_02990.py`, `test_xcmate_scope_02990.py` und `test_xcmate_native_harness_02990.py`.

Gezielte Nachweise:

- 45 PASS in 9,900 s: Start/Retention/Grenzen, Scope .90/.89/.88 und Branding.
- 24 PASS in 3,349 s: Mapping-/Startregressionen einschließlich neuer Lockdiagnose.
- 31 PASS in 2,871 s: tatsächlicher Einstieg, Portal-/Widget-Picker-Grenzen und Branding.
- 58 PASS in 13,081 s: zusätzliche LastGood-/Medien-/Chargenregressionen.
- 15 PASS in 5,950 s: geschützte Quellen, unveränderte Testmethoden/Skipbedingungen, historische Pakete und aktuelles .90-ZIP nach Ergänzung der nativen Home-Ready-Barriere.
- Drei reale Same-Pool-/Speicherprüfungen auf normalem Host-Dateisystem: PASS, 0,351 s.
- Branding: **11/11 PASS**, nur bestehende externe pytest-Plugin-Deprecationwarnung.
- PO-Syntax/Platzhalter: **17/17 PASS**; dies bestätigt nicht die inhaltliche Vollständigkeit aller Übersetzungen.

Aktueller vollständiger lokaler Lauf: **3.797 Tests in 600,875 s: 3.796 PASS, 1 ERROR, keine übersprungenen Fälle.** Der eine Großkatalog-Fall scheiterte mit `sqlite3.OperationalError: database or disk is full`: Python-Profildaten lagen bereits auf dem realen temporären RAM-Dateisystem, SQLite verwendete für seine große Sortierung jedoch weiterhin den kleinen Standard-Tempbereich. Erneuter unveränderter Test mit realem `TMPDIR` **und** `SQLITE_TMPDIR` auf dem ausreichend großen RAM-Dateisystem: **1 PASS in 54,115 s**. Tatsächlich per lokalem HTTP eingelesen: je 200.005 Filme/Serien, je 109.380.521 Bytes; SQLite schließlich 621.731.840 Bytes, maximal 32.660 KiB RSS. Kein Ersatz der Speicherfunktionen, keine Abschaltung einer Produktreserve. Drei Tests, die tatsächlich die Mountidentität gegen `/tmp` vergleichen, liefen weiterhin auf diesem Mount.

Weiterer vollständiger lokaler Lauf: **3.799 Tests in 628,162 s: 3.798 PASS, 1 ERROR, keine Skips**. Der große HTTP-/SQLite-Fall besteht darin mit realem TMPDIR/SQLITE_TMPDIR. Der verbleibende Fehler trat in der Reminder-Testinitialisierung auf (`xbmc.LOGDEBUG` im globalen Teststub nicht vorhanden), vor der Produktassertion. Unveränderter isolierter Wiederholungstest: **1 PASS in 0,055 s**. Das wird ausdrücklich nicht als fehlerfreier Gesamtlauf gewertet.

Die danach ergänzten UTF-8-/Home-Auswahl-Harnessprüfungen wurden separat ausgeführt; die aktuelle Gesamtdiscovery umfasst **3.801 Tests**. Alle fünf Harnessprüfungen: **5 PASS**. Der vollständige unveränderte Standardaufruf auf GitHub Actions ist weiterhin ein eigenständiges Gate; die Kombination von lokalem Lauf und gezieltem Wiederholungstest wird nicht als ein einziger fehlerfreier Standardlauf ausgegeben.

Frühere vollständige Probeläufe bleiben nachvollziehbar: 3.786 Tests/25 fehlgeschlagene Prüfungen vor Korrektur veralteter Versions-, Chargen-, Policy- und Paketannahmen; ein späterer Lauf auf dem kleinen lokalen Tempvolume meldete 21 FAIL/75 ERROR einschließlich fehlender Testabhängigkeiten. Diese Ergebnisse werden nicht als PASS gezählt. Für die Wiederholung wurden die bereits vorhandenen Testabhängigkeiten eingebunden und ausreichend große reale temporäre Speicherbereiche verwendet; die bestehenden Schutzreserven und Testassertions blieben erhalten.

Vorher-/Nachher-Messung, gleicher synthetischer Linux-x86_64-Host, Python 3.12.14, tatsächliche `flock`-Sperre:

| Messung | .89-Basis | .90 | Aussage |
|---|---:|---:|---|
| Fünf warme Portal-Callbacks während Schreibsperre | 769,121 ms, 5 Timeout | 0,382 ms, 0 Timeout | Der unveränderte verifizierte Snapshot wartet nicht auf eine unabhängige Sperre. |
| 88 Manifest-Ladeaufrufe | 88 JSON-Parse, 13,352 ms | 1 JSON-Parse, 31,321 ms | Datei-/JSON-Zugriffe reduziert; die abgetrennten Kopien kosten auf dem schnellen Host mehr CPU. **Kein CPU-Beschleunigungs- oder Android-Zeitnachweis.** |

Rohwerte: [host-measurements90.json](test-builds/02990/host-measurements90.json). 10 s für Logos und 30 s für Now/Next sind Geräteziele, keine aus diesen Messungen ableitbare Android-Garantie.

## Native Kodi-Prüfungen – Status noch offen

`run_kodi_home90_contract.py` behält sämtliche .89-Pixel-, Quellen-, Porträt-, Sticky-, Fremdwidget-, Navigations- und Merktimergates bei. Hinzu kommen 58 vor Home tatsächlich persistierte Logos, dokumentierte 115-MiB-Kapazitätsinjektion, Native-Text-/Pixelzeit, 15 Minuten Home mit 20 Fokuswechseln, drei echte Kodi-Prozessneustarts, 20×137 Gruppen-/Sendernavigation und Mapping-Readback. Reale Eingaben, C++-Controls, lokale HTTPS-Bildbytes und Screenshotpixel; synthetische Provider-/API-Daten und Kapazitäten sind ausdrücklich gekennzeichnet.

`run_kodi_picker90_contract.py` installiert den vollständigen gehashten originalen SkinShortcuts-2.1.0-Code in einem eigenen frischen Testprofil. Originalmanager/-explorer/-Speicherfunktion werden nicht durch eigene Auswahl- oder Schreibsimulationen ersetzt. Kein 48-Komponenten-Installer. Änderungen des Testcontrollers sind kein Nachweis einer Gerätebehebung.

Bereits tatsächlich bestanden: [Original-Picker unter Kodi, Commit `83695d59`](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43066450413/job/130682564319), 1 min 48 s. Frisch ohne Portal sichere Einrichtung; anschließend ausdrücklich angelegter synthetischer Provider, alle drei Quellen durch den echten BINGIE-/SkinShortcuts-Dialog gewählt, Original-Save und Wiederöffnen mit identischer Properties-Prüfsumme. Das ist ein PASS für Auswahl/Speichern, **noch nicht** für den anschließend erweiterten Neuaufbau-/Neustart-/Pixelnachweis.

Der erweiterte Picker-Test verlangt deshalb zusätzlich vom originalen Builder neu erzeugte Bindings, reale Home-Controls und Screenshotpixel sowie drei vollständige Kodi-Prozessneustarts. Er behält mindestens zwei vorhandene fremde Widgetpfade und die gesamte gespeicherte Properties-Prüfsumme. Er erfindet keine WidgetPath-Datei und übernimmt keine vorgefertigte Compilerdatei als Nachweis eines erfolgreichen Speicherns.

Bisherige fehlgeschlagene native Probeläufe offen dokumentiert:

- Erststartdialog vor dem Picker; Initialisierungsfolge im Test korrigiert.
- Singular „Add-On“ und Kodi-Elternordnerzählung im Originaldialog; Controller auf tatsächlich markierte Labels und native Navigation umgestellt.
- Fehlende UTF-8-Angabe beim Lesen eines Fixture-Skripts; korrigiert.
- Der alte Kodi-Texturecache-Nachweis erkannte den neuen, schon vorher SHA-verifizierten eigenen Logo-Pfad nicht. Zusätzlicher Nachweis verlangt genau dieselbe tatsächliche native ListItem-Referenz, Datei-/Manifestverifikation und unveränderte Pixel-/Decodetests.
- Bekannte originale SkinShortcuts-`getiterator()`-Ausnahmen werden gesondert erfasst; Original-Add-on wird nicht ungefragt auf Benutzergeräten geändert.
- Ein nativer Home-Lesezugriff konnte mit einem bereits eingereihten `ReloadSkin` kollidieren. Test wartet innerhalb seiner vorhandenen begrenzten Startschleife auf den tatsächlichen neu erworbenen Home-Owner; alle Fokus-/Pixel-/Decodetests bleiben verpflichtend.
- Kodi zählt den Elternordner `..` nicht in `NumItems`, aber in `ListItemAbsolute`. Der Picker-Controller hatte dadurch den einzigen XCMate-Eintrag abgeschnitten. Tatsächliche Elternposition berücksichtigt, durch Hostregression und anschließend erfolgreichen Originaldialog belegt.
- Eine globale Textersetzung im verschachtelten .90-Testloader entfernte zugleich den Guard-Text innerhalb der untergeordneten Loader-Anweisung. Die .84-Basis startete dadurch vorzeitig und nach Back ein zweites Mal. Nur die ausführbare Guard-Zeile wird jetzt entfernt; gezielte Hostregression. Die zeitweise zur Diagnose verwendete Instrumentierung der kopierten `default.py` wurde vollständig entfernt. Produkt-Routing und ursprünglicher nativer Navigationsvertrag bleiben unverändert.
- Originale Compilerdateien enthalten UTF-8. Der neue Checker liest sie explizit als UTF-8. Erwartet werden die tatsächlich gespeicherten Quellidentitäten; individuelle Widgetnamen werden nicht durch erfundene Testnamen ersetzt.
- Der frische Picker-Test installierte zunächst nur die XML-Unterdateien des geprüften Adapters, aber nicht dessen zugehörige SkinShortcuts-Vorlage. Der Original-Builder erzeugte deshalb nach dem richtigen Save noch die generische native TV-Kachel. Der isolierte Testaufbau übernimmt nun den vollständigen vorab geprüften Adapter einschließlich Vorlage und Overrides. Vorhandene Benutzer-Skins werden dadurch nicht automatisch geändert. Das eigenständige Pixelgate bleibt verpflichtend.
- Der originale BINGIE-Manager beginnt mit „Search“, nicht mit „Home“. Der Controller wählt jetzt die tatsächlich eindeutig benannte Home-Zeile statt Index 0; eigener Hostregressionstest. Für die frische Picker-Prüfung wird die nur im anderen Retention-Test erforderliche 27-MiB-Kapazitätsinjektion nicht verwendet: echte Hostkapazität, unveränderte Produktreserve. Da der isolierte Renderer den automatischen Dienst deaktiviert, werden dessen vorhandene Cache-/Artwork-Worker und Owner-Polls wie im übrigen nativen Home-Test kontrolliert ausgeführt; keine gefälschten Texturen oder direkten WidgetPath-Schreibvorgänge.

- Original-SkinShortcuts schreibt zunächst `widget_base`. Der bestehende eigene Consumer-Reparaturablauf kann die drei eigenen generierten Consumers anschließend privat gesichert korrigieren. Der isolierte Picker-Test rief dessen Aktivierungsvorbereitung nur einmal vor Abschluss des Original-Builders auf; später geschriebene Consumers wurden nicht weiter bis zum tatsächlichen Skin-Reload vorbereitet. Dieser Dienstschritt läuft nun in allen Wartephasen und weiter im vorhandenen Daten-Lane. Der Test verlangt anschließend `RUNTIME_READY`, sichtbare Pixel und echte Neustarts. Kein direkter Ersatz gespeicherter Widgetpfade.
- Frühe isolierte Layout-/Guardversuche ohne vollständig aktivierten Consumer bewiesen keine Ursache. Danach wurde mit unverändertem Original-Builder und vollständiger Aktivierung ein kontrollierter nativer Vergleich ausgeführt (Run 43086329694): Parameter einschließlich ID/Section sind korrekt. Original: beide Medienlisten 0/unsichtbar; nur Self-Guard entfernen: beide 24/sichtbar; nur Bounds ändern: beide 0/unsichtbar; kombiniert: beide 24/sichtbar; nur innere Gruppe entfernen: beide 0/unsichtbar. Der minimale Self-Guard-Fix ist damit reproduziert und im Produkt umgesetzt; sämtliche Bounds-/Flatten-Änderungen bleiben verworfen. Originale .88-MediaRow und MediaNormal abgesehen von genau diesem Guard sind per Golden-Hash unverändert. Die zusätzliche transparente Parameterdiagnose im isolierten Skin wurde ebenfalls entfernt: sie hätte die strikte Installed-Verifikation absichtlich verändert und damit den normalen Consumer-Reparaturweg blockiert. Die frühen Zwischenversuche gelten nicht als Produktnachweis; maßgeblich ist der spätere kontrollierte Vergleich. Ein sauberer vollständiger Lauf ohne Diagnosepatch bleibt zusätzlich Pflicht.
- Der Original-Compiler schreibt seine XML-Datei nicht atomar. Der Test wartet auf beendeten Original-Builder plus vollständig parsebares XML; ein Wiederholungslauf meldete tatsächlich einen partiellen Read. Exit-137-Versuche bleiben fehlgeschlagen, ohne unbelegten Ursachennachweis.
- Der neue native Test wechselt vor der Fremdwidget-IR-Probe ausdrücklich zur zweiten vorhandenen Sektion und wartet auf deren tatsächlichen 24er-Consumer. Down/Up muss innerhalb der fremden IDs bewegen. Danach wird die Home-Sektion wieder ausgewählt. Eine früh angekommene echte Mapping-Commitquittung wird ebenso wie die Queue-Antwort verifiziert; keine erfundene Nonce. Vor Prozessneustarts werden alle vom isolierten Test gestarteten vorhandenen Worker gestoppt und gejoint.

Native Diagnosebelege: [JSON](test-builds/02990/native-picker-admission-diagnostic90.json), [Vorher](test-builds/02990/native-picker-before90.png), [nur Self-Guard entfernt](test-builds/02990/native-picker-after-self-guard90.png). Tatsächliche Linux-Kodi-Pixel mit synthetischen Farb-Prüfbildern; im Filmbereich 40.660 Pixel der erwarteten Farbe. Der diagnostische Lauf blieb absichtlich FAIL und restaurierte seine Originaldatei; er zählt weder als sauberer Gesamtlauf noch als Android-PASS.

**Die nativen .90-Gates sind noch nicht insgesamt PASS.** Finale Runs/Artefakte und verbleibende Ursachen werden hier nachgetragen. Ein erfolgreicher Linux-Kodi-Test wäre weiterhin keine Android-Abnahme.

| P0 | Reproduzierbarer Hostnachweis | Native/Hardware-Freigabe |
|---|---|---|
| A | Begrenzte Chargen, Manifestgeneration, 115-MiB-Schutzfloor, unveränderte gültige Dateien und fehlende Quellen: PASS | 720p/1080p, sichtbare Pixel und 3 Kaltstarts separat prüfen; Android offen |
| B | Echte Channel-Modelle, bestehender Checkpoint, LastGood/Scope/Quellengrenzen: PASS | Frühe native Now/Next-Texte und 30-s-Geräteziel separat prüfen |
| C | Echte Profilsperre, geänderte Datei, immutable Snapshot und sichere Diagnose: PASS | 15 Minuten/20 native Fokuswechsel laufen; Android offen |
| D | Medien-LastGood trotz Live-Startwechsel/SQL-Fehler und Legacy-Adoption: PASS | 5 Film-/5 Seriencover und 3 native Kaltstarts separat prüfen |
| E | Zwei exakt bekannte Fokusfactorys; eigene Mediengeometrie und fremde Definitionen/Quellen geschützt; eigener Self-Guard nativ reproduziert: PASS | Originale native Controls/IR und vorhandene Reihen bleiben eigenständiges Gate |
| F | Eventgenauer Save, Aliase, atomarer Readback, Lock/Abbruch/Reset: PASS | Native Auswahl, Detail-Reopen und Kodi-Neustart separat; TMDB-TV/Movie/TVMaze auf Android offen |
| G | 20×137 indexierte Sender, fehlgeschlagenes Voll-Future und spätere vollständige Generation: PASS | 20 echte Gruppen-/Senderwechsel mit nativem Player unter WAL-Last separat prüfen |
| H | Echter passiver Einstieg, 3 Folder-Quellen, ohne Portal/ohne Fake-PID: PASS | Originaldialog-Auswahl/Speichern PASS; kompletter Builder-/Pixel-/3-Neustartnachweis noch offen |

Keine dieser Zeilen behauptet die vollständige Behebung auf der RK3528-Box. Die konkreten beobachteten Codefehler sind reproduziert; insbesondere für berichtete Fremdwidget-Ausfälle kann ohne Geräteabnahme keine ausschließliche Gesamtursache behauptet werden.

## Paket und Bestandsschutz

[ZIP](test-builds/02990/plugin.video.xtreammate-0.1.29.90.zip), [SHA256-Datei](test-builds/02990/plugin.video.xtreammate-0.1.29.90.zip.sha256).

```text
feb3317b22b39f26ff73dcb92513dc7042934bdf5d5342aa27e6a9daceb27063
```

4.663.315 Bytes, 855 Dateien. CRC PASS; jeder ZIP-Inhalt gegen den aktuellen Add-on-Source geprüft; zweiter Build byteidentisch. Keine `.log`, `.sqlite`, `.db` oder `.pyc` im Paket.

Scope-Gate prüft alle 851 vorherigen Source-Dateien gegen die .89-Basis oder genau freigegebene Byteänderungen sowie alle 361 vorherigen Testdateien mit ihren vorhandenen Testmethoden und Skipbedingungen. Bestehende Assertions wurden für beauftragte geänderte Semantik angepasst (Version .90; acht priorisierte Versuche; getrennte Live-/Medienpolicy), nicht entfernt.

Die drei veröffentlichten .89-Paketwege, Repository-Indizes/Prüfsummen, HTML-Kataloge und Installer 0.5.26 bleiben bytegleich. Der schreibfreie reguläre Veröffentlichungs-Guard bestätigt die Sperre; seine Ausgabe „PILOT_ONLY…“ erteilt **keine** Pilot-Freigabe für .90. Auch Pilot/NeoDark3 bleiben unverändert. Box A/B wurden nicht angesprochen.

## Offene Abnahme

[Android-Testplan T90-01 bis T90-14](ANDROID_ABNAHME_02990_DE.md): vollständig vorbereitet, alle Fälle ANDROID_NOT_TESTED. Noch offen sind die abschließenden nativen .90-Ergebnisse, Original-Picker-Speicherung einschließlich Neustart/Upgrade und die echte Prüfung sämtlicher P0-Anforderungen auf Box B. Keine Teilfreigabe allein wegen schnellerer Logos oder grüner Hosttests. Merge und Release bleiben bis neuer ausdrücklicher Nutzerfreigabe gesperrt.
