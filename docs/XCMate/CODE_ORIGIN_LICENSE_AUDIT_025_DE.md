# XCMate 0.1.25 – Code-Herkunfts- und Lizenz-Audit / Weg zur unabhängigen Neuentwicklung

**Prüfdatum:** 19.10.2026. **Version:** `plugin.video.xtreammate` 0.1.25 (GS Media Kodi Repository).  
**Art:** technischer Vorabaudit anhand von GitHub-Dateien und reproduzierbarem Versionsvergleich; **keine rechtsverbindliche Lizenzfreigabe und kein vollständiges Upstream-Byte-für-Byte-Audit**.  
**Ziel:** bestimmen, welche Komponenten für eine *vollständig ohne übernommenen mr-evil1-Code* neu geschriebene und ggf. eigenständig/proprietär lizenzierbare XCMate-V2-Version ersetzt werden müssen. **Keine Codeänderung und keine Lizenzumstellung durch dieses Dokument.**

## 0. Entscheidender rechtlicher Befund: WIDERSPRÜCHLICHE Upstream-Lizenzangaben – vor weiteren Strategien klären

**Upstream:** [mr-evil1/kodi-media-repo](https://github.com/mr-evil1/kodi-media-repo), Modul `plugin.video.iptvmaster` / Name `TiViMate Kodi`.

1. Das [Upstream-Addonmanifest](https://github.com/mr-evil1/kodi-media-repo/blob/main/plugin.video.iptvmaster/addon.xml) trägt **`<license>GPL-2.0-only</license>`**. Diese Deklaration existierte nach GitHub-Historie bereits in der Version vom **13.06.2026** und war beim späteren Upload vom 26.09.2026 ebenfalls vorhanden (historische Commits `e72ab96b3f82cdd0c8920023eedba55c968d50d0` und `3108eb07b8cf3d5584715d3ad51b7811b98cddb3`).
2. Die separate [Upstream-Repository-Root-LICENSE](https://github.com/mr-evil1/kodi-media-repo/blob/main/LICENSE) besagt aber **„Alle Rechte vorbehalten“** und verbietet das Kopieren, Modifizieren, Verbreiten, Verkaufen oder Verwenden des dortigen Quellcodes ohne vorherige schriftliche Genehmigung. Sie wurde laut [Commit `708b5a6`](https://github.com/mr-evil1/kodi-media-repo/commit/708b5a6ac444efc4d341cade33191d773c8f8883) **am 01.10.2026** erstellt – also **vor** dem ersten hier nachgewiesenen XCMate-Stand vom 13.10.2026.
3. Diese Aussagen **stehen für die Verwertungsrechte zumindest scheinbar im Konflikt**. Es ist ohne zusätzliche Erklärungen unklar, ob die Root-LICENSE den Addon-Inhalt überlagern soll oder nur andere Repo-Bestandteile betrifft, ob die GPL-Angabe selbst eine verbindliche Autorisierung darstellt und ob die als `TiViMate Kodi` bezeichnete Grundlage alle nötigen Rechte hat. **Weder GPL-Wirksamkeit noch Rechtswidrigkeit der bisherigen Verbreitung lässt sich aus den zwei Dokumenten sicher ableiten.**
4. Aktuelle XCMate-Dateien [`src/plugin.video.xtreammate/addon.xml`](../../src/plugin.video.xtreammate/addon.xml) und [`LICENSE`](../../src/plugin.video.xtreammate/LICENSE) deklarieren **GPL-2.0-only** und `GS Media (Fork of mr-evil1)`. [`ORIGIN_AND_CHANGES.txt`](../../src/plugin.video.xtreammate/ORIGIN_AND_CHANGES.txt) nennt die Basis `TiViMate Kodi 2026.06.12.1`.
5. **Risikostufe HOCH / externe juristische Prüfung:** Alle historische Upstream-Lizenzversionen, Originalpaket-LICENSE, Rechtekette und ggf. explizite Lizenzbestätigung von mr-evil1 prüfen und dokumentieren. **Nicht** allein aufgrund des `addon.xml`-Labels annehmen, das gesamte Ursprungsprogramm sei nachweislich und widerspruchsfrei GPL-lizenziert. Bis Klärung keine Umstellung auf „Closed Source“ oder Entfernung der Attribution. Ein Anwalt für IT-/Open-Source-Recht sollte Rechtekette und aktuelle Weitergabe bewerten.

**Rechtsrahmen:** [GNU GPL v2 Originaltext](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html), insbesondere Ziff. 1–3 (Modifikationsvermerke, Weitergabe, vollständiger zugehöriger Quellcode); [§ 69a UrhG](https://www.gesetze-im-internet.de/urhg/__69a.html) (Schutz von Programmausdruck, nicht der abstrakten Ideen und Grundsätze). Auch bei geklärter GPL-Rechtslage lässt sich eine vorhandene abgeleitete Codebasis nicht allein durch Umbenennung, Obfuscation oder Ersetzen des Lizenzlabels proprietär neu lizenzieren.

## 1. Prüfmethodik und Grenzen

- **Verifizierbarer Vergleichsstand in GS Media:** frühester XCMate-Quellcode-Commit `52144f5d864c5a0617fd7ddd7a38c1bf635b4949` vom **13.10.2026, 21:18 UTC** vs. `main` mit Version 0.1.25, innerhalb von `src/plugin.video.xtreammate/`.
- Repository-Daten über GitHub-Git-Trees: gleiche Pfade und identische Git-Blob-SHA = **bytegenau unverändert**. Ergänzend 12 veränderte Python-Dateien: Vergleich der *mindestens zwölf Zeichen langen, nicht offensichtlichen Kommentar- oder Docstring-Zeilen* nach Trim, jeweils unter Berücksichtigung ihrer Häufigkeit. Zusätzlich Übereinstimmung zusammenhängender Fenster von **fünf Codezeilen**. Das sind **Wiederverwendungsindikatoren**, weder ein gerichtsfestes Copyright-Maß noch ein Anteil der „fremden Rechte“; identische triviale Syntax kann ebenfalls zählen, umbenannte/codestilistisch geänderte Fremdteile bleiben möglicherweise unentdeckt.
- Der 13.-Oktober-Snapshot ist **bereits ein veränderter Fork**, nicht das unveränderte Original-Addon. Das ursprünglich bei mr-evil1 verteilte Programm liegt öffentlich primär als ZIP `plugin.video.iptvmaster-2026.06.12.1.zip` vor, **nicht als in GitHub aufgefalteter Lib-Quellbaum**. Dieses binäre Originalarchiv konnte über die verfügbaren Repository-Werkzeuge **nicht entpackt und gegen XCMate zeilenweise geprüft werden**. Ein endgültiges Audit muss die Original-ZIP samt darin enthaltenen Dateien, Copyrightvermerken und Lizenzdateien nachholen. Bis dahin „unverändert seit erstem Fork“ als starken Provenienzhinweis behandeln, nicht als definitive juristische Herkunftsbescheinigung.
- Keine Prüfung unbekannter vorbestehender Fremdquellen in den später hinzugefügten Modulen, der Herkunft erzeugter Grafiken/Fonts, älterer Commit-Autorenlizenzen oder möglicherweise benötigter Einwilligungen. Ein „neu hinzugefügt“ bedeutet **nicht automatisch frei von Drittcode**.

## 2. Inventar: Stand 0.1.25 vs. frühester GS-Media-Fork

| Kategorie | 13.10. (Fork-Start) | XCMate 0.1.25 |
|---|---:|---:|
| Dateien unter `src/plugin.video.xtreammate/` | **37** | **75** |
| Python-Dateien | **18** | **37** |
| Python-Codevolumen (Bytes der Python-Dateien, kein LOC-/Rechteanteil) | **236.453** | **451.938** |
| Seit Start unveränderte Dateien (alle Formate) | – | **19** |
| Seit Start geänderte Dateien (gleicher Pfad) | – | **18** |
| Seit Start neu hinzugekommene Dateien | – | **38** |
| Seit Start unveränderte Python-Module | – | **6** |
| Seit Start neu hinzugekommene Python-Module | – | **19** |

**Unveränderte Python-Dateien / Rewrite zwingend prüfen, wenn vollständig fremdcodefrei angestrebt wird:**  
`resources/lib/export_import.py` (6.382 Bytes), `iptv.py` (13.759), `recordings.py` (5.231), `reminders.py` (3.947), `sleep_timer.py` (1.644), `stalker.py` (23.905). Summe **54.868 Bytes** bytegenau unverändert im Vergleich zum frühesten Fork-Snapshot.

**Weitere unveränderte Dateien:** `LICENSE`, `fanart.jpg`, `icon.png`, und alte Grafiken unter `resources/media/` (`catchup.png`, `epg.png`, `favorites.png`, `recordings.png`, `search.png`, `series.png`, `settings.png`, `tv.png`, `tv_overlay_bg.png`, `vod.png`). **Grafikherkunft separat prüfen**; Unverändertheit seit dem ersten GS-Media-Commit beweist nicht, dass die Grafik von mr-evil1 stammt, und kann ebenso eigene GS-Media-Grafik sein.

### Veränderte Python-Kernmodule: belegte Übernahme ganzer Altcodeabschnitte

| Modul | Noch wortgleiche alte längere Codezeilen¹ | Identische 5-Zeilen-Codefenster² | Für wirklich neuen Client |
|---|---:|---:|---|
| `main.py` – Haupt-Router, Menü, VOD, Serien, EPG | **96 %** | **84 %** | **Neuarchitektur und Neuschreibung – P0** |
| `player.py` – Kodi-Playback, Streams | **98 %** | **81 %** | **Neu schreiben – P0** |
| `portal_manager.py` – Portal-Management | **≈100 %** | **89 %** | **Neu schreiben – P0** |
| `portals.py` – Portale, Profile | **93 %** | **88 %** | **Neu schreiben – P0** |
| `utils.py` – Netzwerk, Cache, Settings, IO | **93 %** | **80 %** | **Neu schreiben – P0** |
| `epg.py` – XMLTV und EPG-Verarbeitung | **89 %** | **73 %** | **Neu schreiben – P0** |
| `xtream.py` – Xtream-API | **88 %** | **67 %** | **Neu schreiben – P0** |
| `setup_wizard.py` – Einrichtungsassistent | **88 %** | **71 %** | **Neu schreiben – P1** |
| `live_overlay.py` – TV-Dialog, Remote | **64 %** | **22 %** | **Trotz neuer UI alte Teile prüfen/neu schreiben – P1** |
| `service.py` – Kodi-Dienst | **76 %** | **13 %** | **Service-Rumpf unabhängig neu schreiben – P1** |
| `group_selection.py` – Gruppenauswahl | **34 %** | **0 %** | **Vorhandene Reste abgleichen; ggf. neu schreiben – P1** |
| `default.py` – Entrypoint | **86 %** | **0 %** | **Kleinen Einstieg neu aufsetzen – P2** |

¹ Anteil der originalen, mindestens zwölf Zeichen langen nicht kommentierten Quellzeilen, die in der aktuellen Datei noch exakt vorkommen; keine Bewertung des neuen Codes oder der juristischen Schutzfähigkeit. ² Anteilswert fünf aufeinanderfolgender Vergleichszeilen im alten Fork-Snapshot, die auch im aktuellen Modul in derselben Reihenfolge stehen. **Insbesondere `main.py` wurde signifikant ergänzt, aber nur wenig vom frühen Bestand ersetzt.** Eine „neue Oberfläche“ macht den darunterliegenden Kern nicht originär.

### Neu hinzugekommene Python-Module – gesonderte Provenienzprüfung

`epg_errors.py`, `epg_io.py`, `epg_preview.py`, `epg_sources.py`, `epg_status.py`, `epg_views.py`, `latest_media.py`, `live_diagnostics.py`, `live_recovery.py`, `logo_cache.py`, `metadata_views.py`, `network_io.py`, `popup_probe.py`, `remote_bridge.py`, `remote_control.py`, `remote_profiles.py`, `service_health.py`, `startup_preferences.py`, `tv_data.py` – **19 neue Python-Dateien** nach frühestem XCMate-Snapshot.

Wahrscheinlich eigenständige *neue Module* relativ zum Fork-Snapshot, aber **kein endgültiger Nachweis**, dass ihre Methoden unabhängig von mr-evil1/GPL oder anderen Drittquellen entstanden sind. Eingebundene oder aus Altcode übernommene Methoden, API-Entwürfe, Grafik-Assets und Kompatibilitätscode gesondert prüfen. Unabhängige Module könnten als eigene Werke lizenzierbar sein, wenn Rechteinhaberschaft, unabhängige Ausdrucksform und Trennung rechtlich belegbar sind. **Als Teil des derzeitigen mutmaßlichen GPL-Ableitungswerks bleibt die Programmauslieferung weiterhin den anwendbaren Fremdrechten unterworfen.**

## 3. Architektur für eine tatsächlich unabhängige XCMate V2

**Zielbild: Kodi weiterverwenden, aber keine fremden schutzfähigen Python-Codebestandteile des mr-evil1-Clients übernehmen.** Standard-Kodi-API, M3U/XMLTV-Formate sowie technische Xtream-/Stalker-Protokollinformationen dürfen als Spezifikationsgrundlage untersucht werden; nicht den ursprünglichen Quelltext, kreative Struktur/Tabellen oder dessen geschützte Implementierungsdetails kopieren.

**A. Neuer Kern ohne Codeübernahme (P0):**
1. **Anwendungsarchitektur**: neues Add-on-Entrypoint, Routing, Menü, Zustandsverwaltung, Error Boundary; `main.py` und `default.py` **von Grund auf** ersetzen. Tests als reines Black-Box-Verhalten definieren.
2. **Provider-/Streaming-Layer**: eigene Xtream-/M3U-/Stalker-Clients mit authentifiziertem Zugriff, Fehlerbehandlung, Timeouts, Playlisten-Parser, Stream-URL-Aufbau, Catch-up; ersetzt `xtream.py`, `iptv.py`, `stalker.py`, `player.py`.
3. **Datenhaltung/Portale/Cache**: neues persistentes Profil-/Credential-Handling, Scheduler, ETag/TTL, atomare Schreibvorgänge, migrationstaugliches Schema; ersetzt `utils.py`, `portals.py`, `portal_manager.py` sowie Alt-Hilfsroutinen. Migration separat aus bekannten **Dateiformaten**, nicht durch Copy/Paste der Originalimplementierung.
4. **EPG-Kern**: neuer begrenzter XMLTV-Parser, Dekompression, externe und Anbieterquellen, manueller Sender-ID-Resolver, lokaler Now/Next, Fortschritt, Status und Quellendiagnose; `epg.py` einschließlich aller neuen abhängigen EPG-Dateien auf Herkunft prüfen/gegebenenfalls unabhängig schreiben.
5. **Geschäftsfunktionen**: eigene Favoriten, Erinnerungen, Aufnahmen, Such- und Gruppenmodell, Backup/Restore, Sleep-Timer; ersetzt die **6 unveränderten Module** und Altroutinen aus `main.py`.

**B. Oberfläche und Plattform (P1):**
6. **Live-TV-Overlay / Remote**: neue XCMate-eigene Kodi-Window-/Action-State-Machine, Fokus, 1×/2×-OK-Infobar, Sender-EPG-Liste, Menü, sichere Input-Isolation; `live_overlay.py` und neue Begleitmodule (z. B. `tv_data.py`, `remote_profiles.py`) unabhängig prüfen/rekonstruieren. Das aktuelle UI-Design als Anforderungsbeschreibung ist weiter nutzbar, **nicht** den alten Quellcode übernehmen.
7. **Service-Hintergrundbetrieb**: neuer Lifecycle, Playback-Erkennung, Index-Warmup, kuratierter EPG-Refresh, Cache-/Logo-Worker, Diagnosen, Android-Recovery; `service.py`, `live_recovery.py` usw. nach Provenienz neu entwerfen.
8. **Einstellungen und Lokalisierung**: neues `settings.xml`, Sprachressourcen, Setup-Assistent; ursprüngliche Texte/Sprachstrings und nicht freigegebene Icons neu formulieren/ersetzen.

**C. Werkzeuge, Logos und Marktauftritt (P2):**
9. **GS Media Repository-Builder und CI** sind vom separaten Repo aus betrachtet eigene Infrastruktur; vor einer V2-Übernahme Entstehung/Lizenz und Copy-Paste prüfen. Kodi-Paketstandard und GitHub-Actions-Konzepte können übernommen werden.
10. **Grafiken, Schriften, Markenzeichen, Texte, Vorlagen** auf Nutzungsrechte untersuchen. Nur Assets mit geklärtem GS-Media-Recht übernehmen; für zweifelhafte alte Symbole eigene Neufassungen.
11. **Neue V2-Produktdokumentation**: Ursprung nicht verschleiern, sondern rechtlich sauber formulieren, z. B. `independently implemented for Kodi` erst nach belegtem Neuaufbau. Eigenständig entworfene Marke und Softwarecode sind unterschiedliche Fragen.

## 4. Vorgehensweise ohne unbeabsichtigte Codeübernahme

1. **Rechtefrage klären** (Upstream-Konflikt GPL vs. „Alle Rechte vorbehalten“ sowie mögliche TiViMate-Fremdrechte); bei ungeklärten Rechten nicht davon ausgehen, dass eine unveränderte Veröffentlichung risikolos ist.
2. **Baseline sichern:** offiziellen Original-ZIP `plugin.video.iptvmaster-2026.06.12.1.zip`, Hash, Inhalt, Lizenztexte, Commits und Datum unveränderlich archivieren. Prüfliste pro Altdatei: Provenienz / Rechteinhaber / Lizenz / fremde Implementierung / API und Testreferenz.
3. **Neues V2-Repository mit neuem Quellbaum** anlegen; eigene Spezifikationen aus beobachtbarem Verhalten und offenen Formaten ableiten, nicht Source-Snippets in V2 kopieren. Für belastbare Clean-Room-Evidenz funktionale Spezifikationen und eine organisatorisch getrennte Implementierung/Review erwägen; genaue Anforderungen mit Rechtsberatung festlegen.
4. **Schrittweise neu implementieren**: zunächst Auth/Portal, Xtream/M3U/Stalker, Wiedergabe, Cache, EPG, UI/Remote, Benutzer-Features. Werkzeuge und Testdaten frei lizenziert/selbst erzeugt; keine echten Zugangsdaten im Repo.
5. **Provenienz und Lizenz-Scanner** im CI: SPDX-Dateiinventar, Lizenztexte aller Drittbibliotheken/Assets, Herkunft jedes Code-Snippets, Ähnlichkeitsprüfung mit Original und frühem XCMate-Snapshot. Hohe Übereinstimmung nur nach dokumentierter Analyse/Risikoentscheidung tolerieren.
6. **Migration ohne Löschung:** alte 0.1.25-Daten nur lesend migrieren, separat und vollständig testen; Nutzer sollen die GPL-Version behalten können. Umstellung der Add-on-ID nur mit eigenem Migrationskonzept; alter Kodi-Updatekanal darf nicht „stillschweigend“ durch eine proprietäre Lizenz ersetzt werden.
7. **Prüfung vor kommerzieller Freigabe:** Source Chain of Title inkl. AI-/Codex-generierter Beiträge, mögliche fremde Logos, Third-Party-Notices und Rechteverträge von einem juristisch qualifizierten Spezialisten prüfen.

## 5. Strategische Optionen – was „eigenständig“ konkret bedeutet

| Ziel | Erforderlich |
|---|---|
| **Eigenes XCMate-Produkt unter GS-Media-Marke, Open Source** | Schon heute als eigenständige *Weiterentwicklung / Distribution eines Forks* beschreibbar, aber mit ehrlichem Ursprung und **nach Klärung** des oben genannten Lizenzkonflikts. Keine Behauptung „komplett selbst geschrieben“. |
| **Eigene Weiterentwicklung behalten, Codeverschleierung als Produktschutz** | Kein sicherer Weg zu unabhängig/proprietär: Verschleierung ändert bestehende Rechte und mögliche Herausgabepflichten nicht. |
| **Separaten, wirklich unabhängig erstellten GS-Media-Cloud-Dienst** | Neue Server-Implementierung unter gesonderter Rechteprüfung möglich; funktionale Trennung und Lizenzbewertung erforderlich, API allein garantiert keine Rechtsunabhängigkeit. |
| **Vollständig originärer und potenziell proprietärer XCMate-V2-Client** | **Neuentwicklung aller oben genannten Altcode-Abhängigkeiten**, Lizenz- und Ähnlichkeitsprüfung, rechtskonforme Wiederverwendung ausschließlich eigener/erlaubter Bestandteile, eigenständiger Release-/Datenmigrationsplan. |
| **Originalen Kern ohne Neuentwicklung kommerziell anders lizenzieren** | Allen relevanten Rechteinhabern entsprechende Rechte abkaufen bzw. ausdrückliche kommerzielle Zweitlizenz mit eindeutiger Reichweite erwerben; nicht durch Änderung der `addon.xml` erreichbar. |

**Arbeitsumfang:** kein belastbarer Stundenwert ohne Architektur-/Testumfang. Der Iststand umfasst allein **37 Python-Dateien und ~452 KB Python-Quelltext** plus Assets/Tests. Eine vollständige unabhängige Neuentwicklung samt realen Kodi-Android-Abnahmetests ist **ein größeres Mehrmonatsprojekt**, nicht ein einfaches Refactoring oder automatisches Entfernen von Copyright-Headern.

## 6. Verbindliche Schlussfolgerung und nächste Entscheidung

**XCMate 0.1.25 ist technisch ein deutlich erweiterter und individuell gebrandeter Kodi-Fork, aber NICHT ausreichend belegt als vollständig unabhängig entwickelter Code.** Der hohe Anteil wortgleicher alter Kernzeilen und 6 komplett unveränderte Module stehen einer entsprechenden Behauptung entgegen.

**Höchste Priorität ist der Upstream-Lizenzkonflikt**, nicht die Verschleierung. Ohne Rechteklärung und direkten Vergleich des Original-ZIP keine endgültige Lizenz- oder Herkunftsfreigabe. Parallel kann eine sauber getrennte **V2-Architekturspezifikation** entstehen. Für ein gänzlich eigenständiges/geschlossenes Produkt müssen u. a. `main.py`, `player.py`, `xtream.py`, `iptv.py`, `stalker.py`, `epg.py`, `utils.py`, `portals.py`, `portal_manager.py`, Backup/Aufnahmen/Erinnerungen/Setup und der Service als neu geschriebene Implementierungen vorliegen; die neuen Begleitmodule benötigen ebenfalls ein Provenienz-Audit.

**Keine funktionalen oder lizenzrechtlichen Änderungen am XCMate-Add-on durch dieses Audit.** Die bisherige Version bleibt `0.1.25`. Bestehende Ursprungs-/Lizenzhinweise nicht entfernen.
