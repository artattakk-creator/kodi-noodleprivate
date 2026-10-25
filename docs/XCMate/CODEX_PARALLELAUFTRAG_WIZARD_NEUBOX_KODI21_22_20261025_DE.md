# XCMate – VERBINDLICHER paralleler Codex-Auftrag: Erstinstallations-Wizard und zweite Android-Box/Kodi-21.3-/Kodi-22-Testmatrix

**Aktuellster ausdrücklicher Nutzerwunsch 25.10.2026:** Den **Plug-and-Play-Ersteinrichtungsassistenten (#43) bei den Parallelarbeiten vorziehen**, um möglichst früh auf einer **zweiten Android-Box mit neuerem Betriebssystem und/oder neuerer Kodi-Version** frische Installation/Kompatibilität testen zu können. Der Wizard darf **NICHT** erst bis zur ursprünglich geplanten .44/Endphase warten.

**Verbindlicher Releaseplan:** [VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md). **Produktiver aktueller Ausgangspunkt** `main=0.1.29.35`, funktionale 15/15-PASS-Abnahme auf Bestandsbox. **Parallel ab SOFORT:** Codex eigener unabhängiger **Wizard-Draft-PR**, Basis aktuelles `main`. **Ziel: frühes Test-ZIP auf NEUER leerer zweiter Box**, ohne bestehende Box oder produktive Verteilung anzufassen. **Integrationsziel kumulative Folgever­sion .37 nach .36**, sofern vollständige DoD/Kompatibilität bestand; bei echten Blockern transparent stoppen/nächsten konkret abgestimmten Release; nicht als Vollwizard eine halbe Scheinimplementierung mergen. **.36** bleibt eigener Such-/Start-/Infoleisten-/Genre-Fixkandidat; Wizard darf seine Implementation nicht blockieren. Nach tatsächlichem `.36`-Merge den Wizard-Draft **vollständig auf neue main-Basis portieren/rebasen** und dann kumulativ für `.37` verpacken. **Nicht** .35→.37 direkt auf bestehender Box installieren.

## 1. Technische Ausgangslage / #43 als Vollvertrag

Issue [#43](https://github.com/artattakk-creator/kodi-noodleprivate/issues/43) beschreibt bereits den End-to-End-Wizard. **Gilt uneingeschränkt**: Erststart erkennt fehlendes aktives Portal, öffnet automatisch sichtbaren fernbedienbaren Setup-Wizard; bestehende Profile nie automatisch überschreiben; benennbares Portalkonto und **Xtream Codes, M3U (Datei/URL), Stalker** als separate echte Fähigkeiten mit Status, keinesfalls nicht implementierte Typen als erfolgreich ausgeben.

- **Erst Account/Konto anlegen, Zugang validieren, Art auswählen**; Klartextfehler bei Offline/Auth/SSL/Portaltyp ohne Passwörter in Meldungen oder Logs.
- **VOR Massenscan** ausschließlich Kategorie-/Gruppenmetadaten abrufen: getrennt **Live-TV, Filme, Serien**; Checkboxen nach Gruppen, Mehrfachauswahl, Alle/Keine, stabile Provider-ID, „Weiter“ und „Zurück“. Nur bewusst ausgewählte Kategorien importieren, keine Default-Alle-Gruppen-Importflut, ggf. Kategorie-abhängig serverseitig streamen/lokal begrenzt filtern.
- **EPG-Quellen** explizit wählbar Anbieter-Xtream und externe Presets **DE/AT, optional CH**, mit eindeutiger Quelle, kein automatisches beliebiges Aktivieren; Quelle/Mapping in bestehender XCMate-EPG-/Alias-Struktur persistieren, nicht konkurrierende neue Datenbank anlegen. Auto-Matching nur bei belegbaren IDs/Namen; ambige/unmapped sichtbar, spätere manuelle Zuordnung #98 verlinken; keine Phantomdaten.
- **Scan- und Importzähler** gefunden/verarbeitet/importiert/fehlgeschlagen je Live/VOD/Serien, ausgewählte Gruppen, EPG-Kanäle, Cover queued/ready/failed; ehrlicher determiniert/indeterminiert Fortschritt. Keine 100%-Fertigmeldung, bevor relevante Daten persistiert sind.
- **Cover und Metadaten** progressiv über vorhandene cache-first persistente Art-/Queue-Dienste im Hintergrund, nicht blockierend oder an Dialoglebenszeit gekoppelt; Platzhalter akzeptieren, ohne 100 % Coverage zu behaupten. Externe TMDb-Nutzung nur bei gültigen API-/Lizenz-/Attributionsregeln; manuelle Bildauswahl #151 separat.
- **Nach Vorschau explizit „Speichern“**: neuer Account, Auswahl, Startgruppe und Startsender kontrolliert und atomar persistieren. Ohne explizites Speichern kein aktiver Importzugang. Abbrechen/Offline/Restart/Re-Entry muss alle existierenden Profile/Portale, Gruppen, Favoriten, EPG-Daten, Resume/Autoplay schützen. Nach erfolgreichem Abschluss XCMate-Home oder auf ausdrücklichen Wunsch Startkanal; **kein auto-TV nach jeder Wizard-Seite**.
- **Wiederaufruf** aus Einstellungen für weitere Anbieter und gezielte Korrektur, aber keine automatisch neue Initialisierung bestehender Profile. Bei vollständig leerer Installation nach Abbruch für den nächsten Klick einen sichtbaren Resume-/Start-Wizard anbieten.

**Codeorientierung aus #43 (an aktuellem main verifizieren, nicht blind alte Zeilennummern vertrauen):** `setup_wizard.py::scan_contents()` begann früher vor Kategorienauswahl mit `xc.get_live_streams()`, `get_vod_streams()`, `get_series()`; `group_selection.py` bereits Checkboxen; `library_index.sync_kind(enabled_ids, iter_catalog(category_id))` für selektiven Import; `guide_store.py` lokaler EPG; `media_art.py`/Artwork-Jobs. **Reuse statt Legacy-Rewrite, keine fehlende Funktion über pseudo-Progress vortäuschen.**

## 2. Zwei Geräte als getrennte Testumgebungen

| Gerät/Profil | Kodi/Android | Ziel | Was ausdrücklich verboten ist |
| --- | --- | --- | --- |
| **Bestandsbox A** | Android 13 / ARM32 RK3528 / Kodi 21.2 / Titan BINGIE MOD | `.35` bestätigte Funktionen, sichere **.35→.36→.37** kumulative Updates | **Kein** Wipe, kein Downgrade, keine Wizard-Autoaktivierung auf bestehendem Konto, keine Kodi 22-RC-Umstellung dieser Box |
| **Neue Box B – Basis** | **Kodi 21.3 Omega stabil**, falls Gerät unterstützt und Nutzer wählt | **Neuinstallation** GS Media Repo→XCMate, erstes Öffnen→Wizard; medien- und IR-Abnahme; andere Android-Version/Hardware/ABI dokumentieren | Keine Migration/Übernahme von Credentials/Logs der Box A, keine behauptete Kompatibilität vor Live-Test |
| **Neue Box B – optionaler Zukunftstest** | **Kodi 22 „Piers“ RC1** auf isolierter Testinstallation/zusätzlichem sauberen Profil oder separatem Testgerät, wenn Nutzer ausdrücklich auf Vorabversion setzen will | Python-/WindowXML-/Kodi-Player-/Android-Back-/MediaCodec-/Repo-/Addon-Installationskompatibilität | **RC1 nicht als stabile Kodi 22-Vollversion bezeichnen**; keine Beta-/RC-Installation auf produktiver Box A; kein ungesichertes Upgrade oder Downgrade mit Profilverlust |

**Öffentlicher Referenzstand 25.10.2026:** Kodi 21.3 Omega ist als stabiler Android-Build verfügbar; Kodi 22 „Piers“ **RC1** wurde am **10.10.2026** veröffentlicht, ist **Prerelease**. Offizielle Quellen:
- https://kodi.tv/article/kodi-22-piers-rc-1/
- https://mirrors.kodi.tv/releases/android/arm/
- https://kodi.wiki/view/HOW-TO%3AInstall_Kodi_for_Android

**Android/ABI-Sicherungen:** Geräte-CPU/ABI `armv7a`/ `arm64-v8a` und Android-Version erfassen; nicht jede neue Box hat 64-bit-OS trotz 64-bit-CPU. Android-11+-Storage-Permissions bei Kodi-Dateizugriff beachten, keine unbemerkte universelle Media-Storage-Freigabe. Kodi-22-Python-/InfoTag-Änderungen, Abhängigkeiten, Kodi-API-/WindowXML-/Dialog-/RemoteAction-/JSON-RPC-Bindungen, Android Predictive Back und MediaCodec als separate Messmatrix. **Anpassungen nicht durch hardcoded Versionsweichen ohne echte Kodi-Versionserkennung**; Kompatibilitätslayer und Tests bevorzugen.

**Installationsvoraussetzung auf Box B:** Eigener frischer Kodi-Profilzustand ohne zuvor installiertes XCMate, GS Media Repository erreichbar und passender Repository-Index; bestehende Accountdaten der Box A keinesfalls exportieren/verwenden, sondern ausdrücklich vom Nutzer bereitgestellte Testdaten verwenden. Kodi-Skin zunächst **Estuary** als reproduzierbare Basis, danach **Titan BINGIE MOD nur sofern kompatible Version auf neuer Kodi-Basis vorhanden**; Skinfehler von XCMate-Wizardfehler trennen.

## 3. Parallelentwicklungs- und Veröffentlichungsprozess

1. **SOFORT Parallelstream WIZ-0**: Codex prüft auf aktuellem main vorhandene Implementierung, erstellt **eigenen Wizard-Branch/Draft-PR**, startet Wizard UI-/Account-/Gruppen-Selektion und Hosttests; unabhängig von .36 Such-/OSD-Patches. Gemeinsame Dateien/DB-Migrationen als Konfliktliste führen, keine parallelen unkoordinierten Commits auf main.
2. **FRÜHES ISOLIERTES TEST-ZIP**: Bei funktionsfähigem Fresh-Install-End-to-End eine **klar als `PREVIEW / NOT_RELEASED` deklarierte Draft-ZIP** mit SHA256 und explizitem Branch-Head-SHA für Box B bereitstellen. **Nie** in produktiven GS-Media-Index aufnehmen, nicht auf Box A installieren, nicht als bestätigte Kodi 22-Kompatibilität ausgeben. Versionsfelder und Kodi-Updateverhalten so wählen, dass Preview **nicht** spätere offizielle .36/.37 Updates blockiert; Versionierung der Preview verbindlich dokumentieren.
3. **Nach .36-Merge**: Wizard-Arbeiten auf letzte `main`-Basis portieren, Funktionen und vorangehende `.36`-Android-Fixliste als **ein einziges kumulatives .37-Release** bündeln. **Nicht** alten WIZ-Draft direkt mergen, wenn .36 noch fehlt oder neue Fehler enthält. Auch Installation alter `.35`-Profile auf derselben Testbox nur via sicherer regulärer Updatepath.
4. **.37 Release-Gate**: kompletter Wizard #43 und sichere Bestandsprofil-Abwehr, aktuelle Kodi 21.x-Frischinstallation durch Nutzer, CI/Host; Kodi22 nur mit explizitem Gerätetest als PASS, andernfalls als bekannte nicht-verifizierte Prerelease-Umgebung. UX Mini-EPG/Rail kommt **in .38**, wegen neuem vorrangigem Wizard und nicht gestrichen. Nutzer autorisiert Merge/Release nach Testergebnis.
5. **Nachfolgende Versionen**: alle anderen Features und Vorversionsfixes gemäß [verbindlicher .36–.46-Versionstabelle](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md); Box B wird Teil der Standard-Abnahmematrix, nicht nur Einmaltest.

## 4. Test- und Freigabekriterien (DRAFT = NOT_TESTED)

| Gate | Test | Ergebnis vor echter Geräteprüfung |
| --- | --- | --- |
| WIZ-01 | Frisches Kodi 21.3, erstes XCMate-Öffnen **zeigt sofort Wizard**, IR-Fokus/Back/Cancel funktionieren | NOT_TESTED |
| WIZ-02 | Xtream Credentials validiert / Fehler ohne Geheimnisse, benanntes Konto, wiederholbarer Offline-/Retry-Pfad | NOT_TESTED |
| WIZ-03 | M3U (URL/Datei) und Stalker tatsächlich implementiert/testbar oder als klarer **Release-BLOCKER** gekennzeichnet | NOT_TESTED |
| WIZ-04 | Vor erstem Bulk-Streamabruf: Live/VOD/Serie Gruppenkatalog; Checkboxen Alle/Keine/Einzel, nur Aktivierte importiert | NOT_TESTED |
| WIZ-05 | Anbieter/XMLTV DE/AT/(CH) bewusst aktiviert, Quelle/Auto-Mapping/fehlende Sender/NowNext lokal nachprüfbar | NOT_TESTED |
| WIZ-06 | Echte Counts für Live/Filme/Serien/EPG/Cover, Fortschritt ohne GUI-Blockade auf unterschiedlicher ARM-ABI | NOT_TESTED |
| WIZ-07 | Explizites Speichern setzt Startgruppe/Startsender, Home/Film/Serien sofort nutzbar, Cover im Hintergrund persistent | NOT_TESTED |
| WIZ-08 | Cancel, Fehler, Strom-/Kodi-Neustart während Import: sichere Wiederaufnahme/Neustart ohne halben aktiven Account | NOT_TESTED |
| WIZ-09 | **Bestehende Box A / vorhandenes Profil:** keinerlei Autostart, Mutation oder Datenverlust; 15/15 .35-PASS-Regressionen bleiben | NOT_TESTED |
| WIZ-10 | Kodi 21.3 und neuere Android-Basis (genaue Android-/CPU-/ABI-/Skin-Version protokollieren): GitHub-Repo Installation/Erststart/Live/Guide/VOD/Fokus/OSD | NOT_TESTED |
| WIZ-11 | Kodi 22 RC1 **nur wenn auf separater Testumgebung vorhanden**: Installer/Python/API/WindowXML/IR-Back/MediaCodec/Addon-Dependencies; PASS/FAIL/BLOCKED statt Kompatibilitätsbehauptung | NOT_TESTED |
| WIZ-12 | Kein Secret in Kodi-Logs/ZIP/Issues, Cache-/SQLite-/Artwork-Hygiene, Speicher-/Netzwerk-/Rate-Limits intakt, ZIP+SHA256/CI | NOT_TESTED |

**Neue auf Box B gefundene Kodi-/Android-Abweichungen** nach derselben Nutzer-Regel in den jeweils nächsten kumulativen Versionsfix übernehmen. **Keine pauschale Änderung der existierenden Kodi-21.x-IR-Navigation, keine neue Kodi-Engine, keine ungefragten Freigaben**.

## 5. Relevante GitHub-Issues und feste Parallel-Zuordnung

- **#43 – Wizard E2E:** vorgezogener verpflichtender Hauptumfang.
- #98 – sichere Quell-/Sender-EPG-Zuordnung: im Wizard nur belegte automatisierte Zuweisung/Status, umfangreiche manuelle Quelle/Kanal-Editor-UI bleibt EPG-Hub-Phase.
- #111/#151 – progressiver Poster-Fallback/Manuell-Auswahl, Wizard nur nutzbare Worker-Basis, nicht auf vollwertigen externen Imagepicker warten.
- #34/#60 – aktivierte Gruppen und Startgruppen-EPG zuerst; progressive Quellen/Cache ohne Mediengesamtimport oder Phantomdaten.
- #90/#91/#108 – Artwork-/SQLite-Budget-/Queue-Sicherheit; keine voreilige globale DB-/Artwork-Migration.
- #143 – Master-Triage/Android-Teststand, #159 Genre-Suche / .36 separater Zeitplan, #94/#95 volle Rail/Mini in .38.
- **Bestehender .36 Codex-Auftrag** [hier](CODEX_AUFTRAG_02936_PERF_OSD_SEARCH_BACKLOG_20261025_DE.md).

**Protokoll:** Implementierungsfreigabe für Codex-**Draft-Entwicklung** durch bestätigten Nutzerwunsch, **keine eigenmächtige Merge-/Publishfreigabe**. Nutzer kann mit isolierter Test-ZIP auf zweiter Box bereits testen, sobald der Wizard-Draft lauffähig ist; Beta-/RC-Kompatibilität wird erst nach realem Test bestätigt.
