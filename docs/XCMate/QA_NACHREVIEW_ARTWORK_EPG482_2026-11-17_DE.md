# Unabhängige QA-Nachreviews – Artwork und EPG #482

Dieser Bericht fasst die ausschließlich lesenden Agentenberichte zusammen. Er ist vom Hauptagenten redaktionell konsolidiert; Ergebnisse werden nicht zu einer erfundenen Android-Abnahme zusammengezählt. Beauftragte Profile: [artwork_qa](../../.codex/agents/artwork_qa.toml) und [epg_mapping_qa](../../.codex/agents/epg_mapping_qa.toml). GitHub-Draft: [#484](https://github.com/artattakk-creator/kodi-noodleprivate/pull/484).

## Gemeinsamer geprüfter Produktstand

`38dbe103416c0040be0285be55f657c0dbe8dbd7`, ZIP SHA256 `16c81e587cfe1739ae463ec69ba6d142ab75146e47c8273ae6a779ec750a1042`.

Beide Agenten bestätigten unabhängig denselben Commit und dieselbe Prüfsumme. Der nachfolgende Commit 835bea99 verändert ausschließlich nativen Testharness und Workflow, keine Produktdatei, Hosttest oder ZIP. Sein zusätzlicher nativer Lauf44099402205 ist ebenfalls SUCCESS (vier Jobs); die getrennten Fokusreceipts stehen bei den Belegen. Keine Agentenänderungen an Produktcode, Benutzerprofil oder GitHub.

## Initialanalysen und iterative Befunde

Beide ursprünglichen Analysen an 1cea11d7 wurden vor Implementierung abgewartet. Der Artwork-Agent reproduzierte stumme Policyblockaden und verlorene Settingsfehler. Der Mapping-Agent reproduzierte falsches Loading bei abgelehntem Submit, fehlende Suchvorbelegung, impliziten Coldtransport, Nullprogramm-Speicherfreigabe und Statusclipping.

Die Nachreviews fanden weitere tatsächliche Defekte, die mit zunächst roten Tests korrigiert wurden:

- Artwork: fehlende terminale Hero-Statusmeldungen.
- Mapping: ausgefallener Retry nach Coldtimeout, auswählbare alte Treffer nach Quellenfehler, inkonsistente Normalisierung und ein vor dem Matching wirkendes400-Row-Limit.
- Mapping:20.000-Kanal-Abfrage erreichte den späten gültigen Treffer nicht innerhalb des bestehenden150-ms-Budgets. Normalisierung wurde optimiert; Zeitbudget nicht erhöht.
- Native Pixelprüfung: dritte Statuszeile abgeschnitten. Auf84Pixel und vollständig sichtbare Listenzeilen korrigiert.

Die vollständige Suite deckte zusätzlich acht durch eine neue allgemeine Textbehandlung verdrängte alte Detailerklärungen auf. Diese waren von den ersten schmalen Agententests nicht erfasst worden. Die ursprünglichen älteren Tests blieben unverändert; die neue Behandlung wurde auf neue Policy-/Settingsfehler eingeschränkt. Der Artwork-Agent prüfte danach die alten Detailzweige ausdrücklich mit. Unabhängige Agententests ersetzen deshalb keine vollständige CI.

## artwork_qa – abschließender Hoststand

Unabhängig ausgeführt: **66 Tests PASS** in 9,31 s, darunter neue Artwork482-Fälle, Pipeline68 und bestehende ArtStatus70-Fälle. Zusätzlich eigene reproduzierbare Prüfungen:

- Gesunde echte SQLite-/Eventkette, eigener TMDB-Matcher mit synthetischer API, sichere Bildübertragung/PNG-Decoder, korrekte lokale Bildbytes und sichtbarer Detail-Consumer im Hostmodell: PASS.
- Tatsächlicher Worker bei ungültigen Settings: `SETTINGS_XML_INVALID` bleibt erhalten, verständlicher Text, null Netzwerkaufrufe, private Testbytes unverändert: PASS.
- 64 MiB verfügbar bei 1 GiB Archivreserve: vorhandener dynamischer Fallback weiter funktionsfähig, Reserve nicht umgangen: PASS.
- Zehn Hero-Statusreproduktionen und neue/alte Detailerklärungen: PASS.
- Keine neuen bestätigten Hostblocker.

Partielle echte720p-Pixel an c5f02ea6 wurden unabhängig angesehen und SHA-geprüft: großes korrektes synthetisches TMDB-Motiv im Hero sowie identisches Motiv in den Details nach 305 s. Native Farbrundung `(20,79,130)` entspricht der synthetischen Quelle `(20,80,130)`. Der unabhängige Fremdwidget-Screenshot zeigt sein eigenes anderes Motiv und null Pixel der TMDB-Testfarbe. Das ist kein vollständiger finaler Lauf und kein echtes Film-/Androidbild.

**Final: ARTWORK_QA_PASS im geprüften Host-/nativen Linuxscope.** Der Agent hat alle 14 finalen Original-PNGs in 720p/1080p visuell geprüft und ihre SHA256-Werte selbst gegen die Joblogs abgeglichen. Beide nativen Schritte sind SUCCESS. Bestätigt sind306,03/306,11 s Bildstabilität, vier lesbare Statusfälle, 13 erhaltene Fremdwidget-Definitionen und zwei echte Offline-Kodi-Neustarts. [Unveränderter Originalbericht des Agenten](test-evidence/issue482/artwork-qa-final.md).

Die früheren Fixturefehler (ungültige Testrevision beziehungsweise nicht gesicherter Home-Fokus) wurden getrennt behandelt; kein Produktguard wurde deaktiviert. Das zusätzliche Observerexperiment835bea99 hat dieselben Produkt-/Test-/ZIP-Bytes und ist ebenfalls mit vier nativen PASS abgeschlossen und wird als eigener Lauf ausgewiesen. Die späten Statusbilder beweisen keine dauerhafte VOD-/Serienversorgung bei beendeter synthetischer Hintergrundlane. Der scoped PASS ist weder eine grüne Gesamtsuite noch eine Android-/Releasefreigabe.

## epg_mapping_qa – abschließender Host-/Nativebericht

Unabhängig **69 Tests PASS**. Eigene20.000-Kanal-Probe: Treffer35,8 ms, Nichttreffer35,6 ms bei unverändert 150 ms Budget. Echte asynchrone Mini/Grid-Adapter, Quelle+Kanal-Save, unabhängiger Cold-Readback, neuer Reader, schnelle Cancellation, späte Ergebnisse und ausbleibende Playeraktionen erneut geprüft. Kein verbleibender wichtiger bestätigter Hostbefund.

Alle **zwölf finalen PNGs** aus Linux-Kodi21.2 wurden unabhängig in 720p/1080p angesehen:

- Beide Quellenpicker tatsächlich offen; Provider mit lokalem Kanalstand sichtbar.
- `PREVIEW_READY` und `MAPPING_BUSY` vollständig lesbar, kein Clipping und keine Toastüberdeckung.
- Sendername, EPG-ID, Quelle, Programme und Buttons sichtbar.
- Save nach gültiger Vorschau aktiv, nach abgelehntem Preview sichtbar gesperrt; Retry und Abbrechen vorhanden.
- Echter Grid-Elternbereich zeigt Programme und quellensicheren VORSCHAU-Marker „noch nicht gespeichert“.

| Gate | Bewertung des unabhängigen Prüfers |
|---|---|
| E1 | PASS im Host-/nativen Fixturescope; konfigurierte optionale Quellenvarianten im Host geprüft |
| E2 | PASS für nativen Dialog und echtes Grid; sichtbare echte Mini-Elternspalte nicht belegt |
| E3 | PASS für geprüfte native Status-/Layout-/Buttonzustände |
| E4 | PASS im geprüften synthetischen Persistenzscope |
| E5 | Linux 720p/1080p im ausgewiesenen Scope PASS; Android UNKNOWN |

[Unveränderte PNGs und Einzelprüfsummen](test-evidence/issue482/README.md). Quelle: [Actions44096702746](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/44096702746), Jobs134085602729/134085602630. Der Mini-Elternowner ist synthetisch; diese Bilder dürfen nicht als native Mini-Now/Next-Elternpixel ausgegeben werden.

## Verbleibende Freigabegrenzen

Physische RK3528-/Kodi21.3-/BINGIE-Prüfungen, vollständige reale Mini-Elternnavigation und Persistenz auf der Benutzerbox: **ANDROID_NOT_TESTED**. Vollständige CI-Ergebnisse und finale Artwork-Belege siehe [Haupttestbericht](TESTBERICHT_ARTWORK_EPG482_2026-11-17_DE.md).

Weder dieser Bericht noch Agenten-/CI-Ergebnisse erteilen Merge- oder Veröffentlichungsfreigabe.
