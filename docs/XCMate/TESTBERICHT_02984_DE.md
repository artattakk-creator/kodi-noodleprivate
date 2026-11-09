# XCMate 0.1.29.84 – Testbericht und Abnahmegrenzen

Stand: 09.11.2026. [Bestehender Draft-PR #405](https://github.com/artattakk-creator/kodi-noodleprivate/pull/405), Master #403 / übergeordnet #395. Kein Merge, keine Veröffentlichung und keine Änderung auf Box A/B. Installer 0.5.26 eingefroren.

## Host- und CI-Nachweise

| Prüfung | Ergebnis |
|---|---|
| Alle .84-Fokustests, finaler Source | **69 PASS / 5,060 s**. |
| Abschnitt E + bestehende TMDB-/EPG-Movie-Regressionsmodule, finaler Source | **46 PASS / 2,968 s**. Überschneidet die 69 Tests, nicht addieren. |
| Vollständiger lokaler Vorlauf vor abschließender Probe-Korrektur | **3.405 Tests / 529,286 s: FAIL, ein Ressourcenfehler**. Alle anderen Tests bestanden. SQLite-Sortierdatei im begrenzten Workspace voll; kein Produktcode für diesen Fehler geändert. |
| Derselbe echter HTTP-/200.000-Titel-/SQLite-Readback-Stresstest mit SQLITE_TMPDIR auf größerem /tmp-Volume | **1 PASS / 60,471 s**. Keine Testgrenze oder Datenmenge reduziert. |
| Finale vollständige CI | Erwartete **3.408 Tests** (3.339 bestehende + 69 neue). Ergebnis/Commit/Links nach finalem Lauf im PR; noch kein PASS aus einem früheren Source ableiten. |
| BINGIE-Branding pytest | **11 PASS / 0,17 s**. |
| Kodi-PO-Validierung | **17 Kataloge PASS**, Unicode/Platzhalter gültig. Das beweist keine vollständige Übersetzung jeder Sprache. |
| Compile / ZIP / Reproduktion | **PASS**, 786 Dateien, jeder Sourcebyte/CRC geprüft; zweimal erzeugte ZIPs byteidentisch. |
| Veröffentlichungsschutz | **PASS**, veröffentlichte .83-Kanäle und Installer 0.5.26 unverändert. Kein Publisher ausgeführt. |

Die vollständige Suite umfasst den .83-Bestand von **3.339 unittest-Methoden** sowie die .84-Erweiterungen. Kein alter Test entfernt, keine neuen Skip-Bedingungen. Bestehende Erwartungswerte nur bei ausdrücklich verändertem Layout/zulässiger TV-Werksuche aktualisiert; Sicherheitsassertions bleiben. Ein alter Persistenztest wurde von globalem Modulzustand isoliert und prüft weiterhin echte gespeicherte Live-Gruppen und das Passwort.

Gezielte Abschnitt-E-Prüfungen: The Middle ohne Genre/Jahr/Staffel/Folge, eindeutiges Jahr, Mehrdeutigkeit, unvollständige Treffer, gleichnamiger Film, offizielle/unbestätigte King-of-Queens-Alternative, falsche ID/Jahr, exakt bestätigte Episode ohne Still, falscher Untertitel, Opt-out/Token-Erhalt sowie Filmabfragen bei jetzt/+6 h/+12 h. Zusätzlicher PNG-Transport-/Lease-/GUI-Control-/Hero-ListItem-Test für beide Serien; das ist ein Hostmodell und kein Android-Pixelnachweis.

Vorherige rote Läufe bleiben nachvollziehbar: [CI 42636934599](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42636934599) hatte 3.405 Tests mit einem Fehler und einer fehlgeschlagenen Assertion. Ein ungültiger Stillpfad löste unzulässig den zusätzlichen Work-Fallback aus; er wird nun vor dem dritten Request abgewiesen. Der alte Unknown-Genre-Test erwartete null TV-Anfragen; jetzt erlaubt er die neue sichere TV-Suche, verlangt aber weiterhin keinerlei Movie-/Bildanforderung und keinen Titelraten-Erfolg. Abgebrochene Läufe wurden nie als PASS gezählt.

Der aktuelle GitHub-Gesamtstatus und der getestete Commit werden nach Abschluss der finalen Workflows im PR dokumentiert. Ein grüner früherer Workflow wird nicht als grüner finaler Commit ausgegeben. CI prüft zusätzlich ZIP-Reproduktion, veröffentlichten Kanalschutz, Sprachdateien, Bestandsregressionen, natives Home und Player-ACKs. Keine Workflow-Veröffentlichung.

## Native Kodi-21.2-Bildprüfung (Linux, synthetisch)

[1080p + 720p, Lauf 42636934136](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42636934136), Source `ede6eacf93379d854caa3707ebcf438702b8a33a`: beide Jobs **PASS**. Dies belegt die aktuelle 620er Rendergeometrie vor den abschließenden Diagnose-/Stillpfadkorrekturen; die finale CI wiederholt diese Gates.

| Nachweis | Ergebnis / konkrete Grenze |
|---|---|
| Frisches Profil, echte ListItems im nativen Home | 88 Live-Sender, 24 Filme, 24 Serien; tatsächliche InfoLabels statt Python-Listenobjekt allein. |
| Anfangs-Logo → Eventbild | Begrenztes Logo **560 × 280**, anschließend Eventbild erst nach echter Dekodierung. Erste Live-Route trägt das Logo bereits vor Eventbereitschaft. |
| Sichtbare Texturen | Lokale Kodi-Datei vollständig mit Pillow dekodiert und SHA256 geprüft; echte Screenshotpixel im Hero und in Posterreihen. URI/REFERENCE_READY allein genügt nicht. |
| Licht-/Geometriegate | Hero 620, Rail top 640, Reihen 244; heller synthetischer Event unter rechter **90%-Navy-Tafel**, tatsächliche Hintergrundpixel dunkel. Native Fokus-/Scrollprüfungen. |
| Priorität | Fünf aktuelle Eventreferenzen vor Film- und Serienphase; Vorbereitungs-/Rendernachweise getrennt. Kein erfolgreicher Import von 24 Postern mit einer tatsächlichen 24er Bildschirm-Sichtmenge gleichgesetzt. |
| Warm + zwei echte Offline-Kodi-Neustarts | Jeweils **PASS**, Wiederfinden exakter aktueller Kodi-Texturen; keine vorausgefüllten eigenen Bildarchive. |
| Eigene Archivdateien im Druck-Fixture | **0 neue XCMate-Bildarchivdateien**; geschützte Fixturekonfigurationen unverändert. Das beweist keinen global begrenzten Kodi-Texturecache. |
| Kapazitätsstörung | 27 MiB nur in XCMates Python-Messung. Tatsächlicher Hostspeicher bleibt schreibbar für Kodis C++-Texturen. **Kein physischer ENOSPC-Test.** |
| Android | **ANDROID_NOT_TESTED**. Kein echtes TMDB-Konto, Providerstream oder Nutzerscreenshot in CI. |

1080p-Messung innerhalb des Logo-Prüfabschnitts: erstes bestätigtes Logo 5.989 ms, nach Offline-Neustarts 3.904 / 3.594 ms. Das sind synthetische Fixturezeiten inklusive definierter Wartebarrieren, keine vergleichbaren Android-Startup-Zeiten und kein behaupteter Performancegewinn. Relative Phasenzeitpunkte schließen Fixtureaufbau/Worker-Sperren ein und sind kein Produkt-Ladezeitbenchmark.

Zusätzlicher nativer [Home-/Player-Lauf 42636934234](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42636934234): 1080p-Home und 20 Stop-ACK-Zyklen je Medientyp (60 gesamt) bereits PASS; der 720p-Test enthält eine **1.800-Sekunden-Workerpause**. Endstatus im finalen PR-Kommentar ausweisen. Wiedergabestabilität auf Linux ersetzt keinen RK3528-/MediaCodec-Test.

Die Bildartefakte stehen in den verlinkten CI-Läufen. Synthetische Screenshots wurden direkt im Chat weitergereicht. Keine privaten Fotos oder Kodi-Rohlogs veröffentlicht.

## Paket

[Installations-ZIP](test-builds/02984/plugin.video.xtreammate-0.1.29.84.zip) · [SHA256-Datei](test-builds/02984/plugin.video.xtreammate-0.1.29.84.zip.sha256)

Version **0.1.29.84**, **3.527.307 Bytes**, 786 Dateien.

```text
25dc865c5fcb261e5e2bdad037d5bdae5b557b5f94902f8f84932fdf6a304e58
```

Die frühere .84-ZIP und deren Prüfsummen sind durch dieses neu erzeugte Paket ersetzt. Der zugehörige Commit steht im abschließenden PR-Bericht; `.84` wurde weder nach main gemergt noch in einen Updatekatalog eingetragen.

Reproduzierbarer Builder: `python tools/package_xcmate71.py <Ausgabeordner>`. ZIP-Inhalte werden byteweise gegen `src/plugin.video.xtreammate` geprüft, CRC geprüft; keine Logs, Datenbanken, Zugangsdaten oder .pyc im Paket. Installer und reguläre/Pilot-/NeoDark3-Indizes werden nicht aktualisiert.

## Offene Abnahmeblocker

- Alle IMG84-01..08, VIS84-01..10 und SERIES84-01..05 auf Box B: **ANDROID_NOT_TESTED**.
- Neuer temporärer **Bilddatei**-LRU mit Byte-/Objektlimit, Pins/Refcounts und Eventende+Grace: **OPEN**. Begrenzte Referenzmetadaten sind kein Ersatznachweis.
- Vollständige Cover-Viewportsteuerung aller BINGIE-Varianten: **PARTIAL / OPEN**; bestehender begrenzter 24er-Widget-/Legacy-Archivpfad bleibt erhalten.
- Dauerhafter Metadaten-Importcursor bei blockierten Writes: **OPEN**; RAM-Wiederaufnahme und optionales Referenzjournal implementiert.
- Tatsächliche Android-Kapazität, endgültiges Layout und #401-Migration: **OPEN / nachgelagert**, keine Datenbewegung und kein vermeintlicher Speichergewinn.

**Keine Merge-/Releasebereitschaft behauptet.** Sichtbar richtige Serienbilder auf Box B und die offenen Lifecycle-Anforderungen bleiben echte Freigabebedingungen. [Ursachen/Dateien/Scope](IMPLEMENTIERUNG_02984_BILDER_ZUERST_DE.md) · [ausführbare Android-Matrix](ANDROID_ABNAHME_02984_DE.md).
