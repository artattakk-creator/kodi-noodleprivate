# Zwei unabhängige Codex-QA-Gates – Bildanzeige und EPG-Zuordnung

**Kontext:** XCMate Pilot 0.1.29.97, Android RK3528/Kodi 21.3/BINGIE MOD. Bilddarstellung aus Nutzersicht vollständig ohne sichtbare Hero-/Detailbilder. Das .90-Verhalten mit sichtbarem Ladefortschritt dient als fachlicher Referenzpunkt, nicht als zu kopierender unsicherer Code. EPG-Mapping-Dialog wird in Groß- und Mini-EPG geöffnet, lädt Quellen/Kanäle langsam, Treffer-OK bewirkt keine erkennbare Vorschau, Status wird abgeschnitten, Speichern bleibt deaktiviert.

**Konkrete Referenzen:**
- .90 Produktcode `9bbf75040378dcaead9128880a909fe7978143a4` (PR #431, veröffentlicht über #432).
- .97 Quelle PR #478 `bc06f521d23ee5c1e6c9aaca456c2b3cc062f3fc` plus versionsbezogener .97-Commit auf `release/xcmate-02997-pilot-issue474`; Pilot-Veröffentlichung `6e34671456495b2ce514721402b05236789382c2`.
- Bildfehler/Regression: #468, #469. EPG-Save: #474. Neue EPG-UX: #482. Native Abstürze sind **separat** #452.

## Architektur
`.codex/agents/artwork_qa.toml` – unabhängiger **nur lesender** Bild- und Anzeigeprüfer (GPT-6.1 Sol, high).

`.codex/agents/epg_mapping_qa.toml` – unabhängiger **nur lesender** Prüfagent für Quellliste, Suchvorschläge, Vorschau, verifizierten Save und 720p/1080p (GPT-6.1 Sol, medium).

`AGENTS.md` verlangt die beiden Gates explizit nach jeder Änderung in ihren Verantwortungsbereichen. Sie sind **nicht automatisch laufende Server- oder GitHub-Actions-Agenten**. Sie werden von einem Codex-Hauptagenten in einem Lauf auf dem passenden Projektbranch gestartet; falls die Codex-Version projektlokale Custom Agents nicht unterstützt, gleichwertigen read-only Review separat und den tatsächlichen Modus dokumentieren.

## Einsatzanweisung für den nächsten Codex-Hauptauftrag

> Starte die Codex-Sitzung auf **`automation/xcmate-artwork-epg-qa-20261117`** und lege einen **neuen Featurebranch von genau diesem QA-Branch** an (der QA-Branch basiert bereits auf `release/xcmate-02997-pilot-issue474` und enthält die Agentdefinitionen). Alternativ darf nach ausdrücklicher Freigabe erst Draft-PR #483 in den .97-Basisbranch gemergt werden. Beachte #468, #482, #474. Starte als erste Phase zwei **unabhängige QA-Subagenten**: `artwork_qa` für Bildabruf und tatsächliche BINGIE/Detail-Renderpixel im Vergleich .90↔.97, `epg_mapping_qa` für den gemeinsamen Groß-/Mini-EPG-Zuweisungsdialog mit Quelle→automatischer Sendername-Suche→reversibler Vorschau→Save mit Readback. Warte auf beide Berichte, priorisiere die ersten tatsächlich belegten Blocker, erstelle reproduzierbare RED-Tests und dann einen minimalen Fix. Nach der Änderung beide QA-Agents erneut unabhängig prüfen lassen. Native Kodi-Linux 720p/1080p mit sichtbaren Texturen/Layoutbelegen; Android bleibt ungetestet. Nur einen Draft-PR mit Tests, Risiken und Abnahmeplan erstellen. Keine Main-/Pilot-/NeoDark3-/Installer-Veröffentlichung, keine profil-/DB-/Token-/EPG-Bereinigung.

## Harte QA-Checks

| Gate | Mindestnachweis | Kein PASS bei |
|---|---|---|
| A1 – Bild-Auftrag | Sichtbarer Event erzeugt nach Opt-in `QUEUED`, `RUNNING` mit begründetem Status | Stille `False`-Rückgabe aus `programme_requests68.request` oder `drain` ohne UI-Hinweis |
| A2 – Quellen | Exakte TMDB/TVMaze/XMLTV-Quelle zugelassen, bestehende Consent-Flags per Readback bestätigt | `SETTINGS_XML_INVALID`, unerklärter `TMDB_DISABLED`, Quelle nur wegen Token-Präsenz automatisch aktiviert |
| A3 – Pixel | Kodi native Texture/Control + im Bild belegtes Hero- und Detailmotiv | Nur HTTP200, `URL_APPROVED`, `IMAGE_URL_READY_RAM`, `REFERENCE_HANDED` |
| A4 – Speicher | Dynamische Referenzen bei geringer Reserve gemäß Nutzer-Opt-in funktionsfähig | Zwangsreserve 1–6 GiB oder ungefragtes Löschen |
| A5 – Status | Die Oberfläche zeigt verständlich „Suche…“, „Bild gefunden“, „Keine Bildquelle“ oder spezifischen Fehler | Kein sichtbarer Arbeitszustand trotz im Hintergrund laufenden Jobs |
| E1 – Einstieg | Quellenliste aus realer Konfiguration sofort; Name/ID des aktuellen Senders als Suchvorschlag | Zum Kanal K nur durch Vollscrollen |
| E2 – Vorschau | OK auf Suchtreffer startet reversiblen EPG-Raster-/Dialog-Preview mit Now/Next | Hängende generische Meldung, falscher Sender, keine Programme ohne Erklärung |
| E3 – Buttons | Save nur bei valide gespeicherbarer Auswahl; stets sichtbarer Grund im Sperrfall, Cancel bedienbar | Stilles deaktiviertes Speichern, IR-Fokusfalle, Textabschneiden |
| E4 – Persistenz | atomare Quell+Kanal-Zuordnung, Cold-Readback, Aktualisierung Groß/Mini, Neustartbeständigkeit | Source-ID-Kollision, Save ohne Proof, nicht rücklesbarer Stand |
| E5 – Praxis | Native Kodi-Linux 720p und 1080p; danach echte Android-Abnahme | Nur Host-/Mock-Tests als Pixel- oder Android-PASS deklariert |

### Bekannte Code-Hinweise (keine unbewiesene Ursachenbehauptung)
- `art_trace81.own()` .97 führt `settings_guard96.require()` vor TMDB-Abfrage aus; Android-Lauf meldet `SETTINGS_XML_INVALID`.
- `programme_requests68.request/drain()` .97 hat neue `storage_policy92`-Abbruch-Gates; Status kann dadurch ohne `QUEUED` verschwinden.
- `home_loading85` enthält weiterhin deutsche Ladehinweise; fehlende UI-Sichtbarkeit ist separat gegen die Skin-Properties zu prüfen.
- `guide_mapping48._channels()` startet ohne vorbefüllte Suche; `_preview()` benutzt Worker-Future und aktiviert Save erst nach `apply_preview`; `onClick()` ignoriert während Future alle Aktionen außer Abbrechen.
- `XCMateMapping48.xml` enthält ein Statusfeld `103` von **474 × 55 Pixeln**, das die lange Meldung abschneidet.
- `epg_candidate53` darf bei Cold-Katalog nur kontrolliert mit expliziter Quellwahl lesen; keine ungewollten massiven/XMLTV-Neuimporte.
- Vorliegende Kodi-Logs von 11:50–11:58 stammen von einem früheren Nutzerlauf; neue EPG-Dialog-Interaktionen sind noch **nicht** durch einen zusätzlichen aktuellen Logauszug belegt.

**Status:** Agentkonfiguration und Abnahme-Gates vorbereitet, noch kein Source-Fix, keine CI/Android-Abnahme und keine Pilotfreigabe.
