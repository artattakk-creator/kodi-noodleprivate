# XCMate P0 – „Katalog aktualisieren“: sicherer Nachscan für Filme und Serien (04.11.2026)

**Status: verbindlicher Codex-Arbeitsauftrag, noch keine implementierte Reparatur.** Hauptziel: vorhandenen Xtream-/Provider-Eintrag um Film- und Serienkategorien samt Titeln ergänzen, ohne Neuersteinrichtung, Portalduplikat, Live-TV-/EPG-Änderung oder Datenverlust. Repository `artattakk-creator/kodi-noodleprivate`, Ausgangsversion mindestens `plugin.video.xtreammate 0.1.29.71` nach PR #353. Vor Implementierung neuesten main-/Testkanal-Stand auf Kumulativität prüfen; keine Version rückwärts setzen.

## Verbindliche Gerätebelege / sauber getrennte Schlussfolgerungen
Nutzer: derselbe IPTV-Anbieter zeigt Filme und Serien in einem anderen IPTV-Player, XCMate-Filmbereich ist komplett leer. TX60Pro/Allwinner, Android API 29, Kodi 21.3 ARM32. Aus bereitgestelltem `kodi(20261104-062015).log`:
- 06:50:43 `[XCMate][SETUP71] stage=AUTH_DONE` – Anmeldung erfolgreich.
- 06:50:45 `stage=GROUPS_DONE ... live=53 vod=0 series=0`.
- 06:51:37 `GROUPS_RENDER_BEGIN kind=vod total=0`; 06:52:58 `kind=series total=0`.
- 06:53:56 `COMMIT_BEGIN ... live=53 vod=0 series=0`.
- 06:54:03 `READBACK_DONE ... live=3357 vod=0 series=0` und `COMMIT_DONE`.
- Der kontrollierte Schreib-/Readback-Pfad wurde erfolgreich durchlaufen; **nicht** als Beleg interpretieren, dass die Remote-VOD-API tatsächlich leer ist. Auch nicht ohne zusätzliche Prüfung behaupten, der Provider liefere keine VOD-Inhalte. Der andere Player beweist ein VOD-Angebot, aber nicht identische API-Endpunkte/Parameter/Accounts.
- Rohlogs nicht öffentlich auf GitHub einstellen: Providerzugang, Netzwerk-/Tokensicherheit.

## Bestehende Codepfade (auf main eingesehen)
- `src/plugin.video.xtreammate/resources/lib/wizard_ui54.py`: `categories(...)` iteriert `('live','vod','series')` und ruft `d.adapter.categories(kind,remote=True)`; jede Rückgabe wird als Kategorieliste übernommen; Abbruch nur, wenn **alle** Kategorien leer sind. Daher führt `53/0/0` als vermeintlich erfolgreicher Gesamtabruf zu einem reinen Live-TV-Portal.
- `src/plugin.video.xtreammate/resources/lib/wizard_catalog54.py`: `scan(...)` nutzt `draft.adapter.entries(kind,cid,...)`, `library_index.import_group`, `heads`, `groups`, `items_v2` und private Wizard-Recovery/Receipts. Die dortige Logik wurde für **neue unveröffentlichte Portal-IDs** geschrieben und entfernt in diesem privaten Stage selektiv deselected Heads. **Nicht ungeprüft auf eine veröffentlichte Portal-ID anwenden**.
- `src/plugin.video.xtreammate/resources/lib/portals.py`: `get_by_id`, `update`; Portal-ID und gespeicherte Providerverbindung müssen unverändert bleiben.
- `src/plugin.video.xtreammate/resources/lib/setup_window.py`: Wizard ist keine vorhandene verifizierte sichere Nachscan-Oberfläche; keine erneute Ersteinrichtung als Workaround.

## P0-Funktionsumfang
1. Im vorhandenen XCMate-Einstellungsbereich/Provider-Kontextmenü die Aktion **„Katalog aktualisieren“** anbieten. Voreinstellung **Filme** + **Serien**; Live-TV und EPG im vorliegenden Auftrag deaktiviert. Je Bereich unabhängige Checkbox, `Starten`, `Abbrechen`, `Ergebnis`. Bestehendes Portal explizit wählen; Auswahl anzeigen; keine automatische Neuanlage.
2. Wenn der Nutzer nur Filme/Serien wählt, **ausschließlich** Remote-Kategorien und -Titel dieser Bereiche lesen; keine Live-TV-Neulistung, kein EPG-Download, kein TMDB-Fallback für Provider-VOD und kein BINGIE-/Skin-Patch.
3. Diagnose des Xtream-Adapters: für Filme `get_vod_categories`/`get_vod_streams`, für Serien `get_series_categories`/`get_series` als **zu prüfende Xtream-API-Verträge**; tatsächliche Adapterimplementierung/URL-Konstruktion vor Änderungen identifizieren. Prüfen: xtream vs M3U/STB-Portaltyp, Auth-/Accountstatus, Kategorie-IDs, Kategorie-/Titelformate (Array/Wrapper/leer/Fehler), HTTP/TLS/Timeout, API-Aktionsnamen, URL-Encoding, Zeichensatz, Paging, Anbieter-Abweichungen, Selektions-/Filterlogik; keine Credentials oder komplette URLs in Logs.
4. Jede Antwort differenzieren: **gültige leere Liste**, **Netzwerkfehler**, **Auth-Fehler**, **Parsing-/Schemafehler**, **per-user VOD-disabled**, **Timeout/Rate-Limit**, **fehlender Endpunkt**. Bei `vod=0` und `series=0` nach erfolgreichen Live-Gruppen sichtbare Erklärung und bewusstes Fortfahren mit Live-only; **nicht** fälschlich „Filme/Serien erfolgreich synchronisiert“ ausgeben. Weder Provider-VOD noch XCMate-Code als alleinige Ursache vor Vergleich behaupten.
5. Vor Aktualisierung lesbares, integritätsgeprüftes, privates Backup der **betroffenen** Katalog-/Selektionsmetadaten; vorhandenen .71-Sicherheits-/Lock-/Android-Storagevertrag wiederverwenden. Keine Schlüssel/Passwörter neu abfragen oder kopieren, außer vorhandene Verbindung verlangt legitime Re-Authentifizierung; keine Passwörter im Log/Backupmanifest.
6. Inkrementeller **Upsert** nach stabiler Identität `(portal_id, kind, category_id, stream/series_id)`. Bereits vorhandene Titel/Metadaten/Favoriten/Wiedergabestände, manuelle Zuordnungen und Bilder möglichst unverändert lassen; neue Titel ergänzen, geänderte Titel aktualisieren. Bei bestätigten, vollständigen API-Antworten Änderungen erkennen, ohne unkontrolliertes „Löschen aller fehlenden Titel“. **Nullantwort, Partial Response, Timeout oder Benutzer-Abbruch dürfen niemals Bestandsdaten löschen.** Etwaige Anbieter-Löschabgleiche nur als eigenes, gesondert spezifiziertes Opt-in und nicht in diesem Auftrag.
7. SQLite/JSON-Katalog-Writer und Reads mit Portal-ID-Scope, Transaktion und verifizierbarem Generation-/Head-Swap nutzen; einen fehlgeschlagenen oder abgebrochenen Teilimport nicht sichtbar veröffentlichen. Teileinheiten je Film-/Seriengruppe atomar, Crash-/Resume-Journal idempotent; kein konkurrierender Doppelscan/Index-Lock; keine „neuer Portal-ID“-Nebenwirkungen. Sicherer Neustart nach Kodi-Kill.
8. Gruppenauswahl: neue Remote-Gruppen anzeigen und auswählbar machen; bestehende explizit gewählte Film-/Seriengruppen übernehmen. Wenn noch **keine** VOD-Gruppen existieren, die gefundenen nicht stillschweigend verwerfen; Nutzer zur Auswahl führen (optional „alle neu gefundenen“). Ungewählte Gruppen dürfen nicht den bestehenden Katalog verstecken, bevor Nutzer bestätigt. Kein Portal-Duplikat.
9. UI-Fortschritt: getrennte Phasen AUTH → VOD_CATEGORIES → SERIES_CATEGORIES → VOD_ITEMS → SERIES_ITEMS → VERIFY → COMMIT; pro Bereich Gruppen gefunden, Gruppen ausgewählt, Titel gelesen, neu, geändert, unverändert, übersprungen, Fehler. Nicht blockierende Kodi GUI, Cancel/Retry, Abschlussdialog mit echten DB-Readback-Zahlen; keine Erfolgsbestätigung bei leeren ungeklärten Antworten.
10. Logging `[XCMate][VODSYNC]` mit pseudonymer Session, Art, anonymisiertem Portal-Identifikator, Phase, Anzahl, Dauer, Fehlerklasse, ggf. sicherem errno/HTTP-Status; **keine** Hostnamen, Account-IDs, Provider-URLs, Tokens, Passwörter oder Medientitel im öffentlichen Diagnoseprotokoll. Optionaler lokaler Self-Test von API-Antwortform und Katalogbestand, ohne Netzwerkdetails zu exportieren.
11. Nach erfolgreichem Commit gezielt XCMate-Filme/Serien-Ansichten und einschlägige BINGIE-Widgets invalidieren, ohne Live-TV-/EPG-Daten/Texturecache flächig zu löschen. Prüfen, dass Titel direkt unter XCMate → Filme/Serien erscheinen, unabhängig vom Skin.

## Harte Erhaltungsgrenzen
- **Kein GS-Media-48er-Installer**, kein Kodi-Reset/Deinstall, kein anderes/neues Repository, kein Portalneuanlegen.
- **Exakt dieselbe bestehende Portal-ID**; 3.357 Live-TV-Sender aus Gerätelog, 53 Live-TV-Gruppen, deren Auswahl/Startgruppe, EPG-Quellen/Zuordnungen und TMDB-Zugang bleiben unverändert. Darüber hinaus Kodi-/BINGIE-Einstellungen, Favoriten, Resume-/Watchstatus, manuelle Metadaten/Artwork-/Remote-Profile erhalten.
- Kein Anfassen von Skin-Dateien oder Keymaps. Keine automatisch aktivierte 24h-Synchronisation im P0; wenn später gewünscht, getrennt konfigurierbar und default aus.
- Ohne eindeutige Identität/validierte Antwort keine Lösch-/Versteckoperation. Testdaten synthetisch; echte Logdaten privat.

## Pflicht-Testmatrix
- **VOD-01** Reproduktion 53/0/0 mit gültiger Live-Antwort, VOD-/Serienantwort als [] oder unerwartetes Wrapper-Format. Keine stillschweigende Erfolgsmeldung für VOD.
- **VOD-02** Synthetischer Xtream-Server liefert beide Kategoriearten + Film-/Serientitel. Exakter Nachscan legt Titel im *bestehenden* Portal ab; separate Cold-Readback-/Prozessprüfung und Kodi-Menülisten zeigen Inhalte.
- **VOD-03** Film-only, Serien-only, beide; Live-/EPG-Queries exakt **0**, Live-Katalogbestand unverändert (Mengen + Digest).
- **VOD-04** Gültige leere Antwort, HTML statt JSON, API-Fehlerobjekt, HTTP 401/403/429/500, Timeout, Abbruch, Verbindungsabbruch mitten im Stream, Teilantwort/Seitenwechsel, fehlende/duplizierte IDs. Keine Datenlöschung; korrekte Meldung.
- **VOD-05** Derselbe Nachscan zweimal: idempotent, keine Duplikate, Favoriten/Resume bleiben erhalten; zusätzliche neue Titel/Metadaten-Änderungen inkrementell sichtbar.
- **VOD-06** Abbruch/SQLite-lock/readonly/ENOSPC/Kodi-Hard-Kill zwischen Stage und Commit: alter publizierter Katalog unverändert; zuverlässiger Retry/Resume.
- **VOD-07** Group selection: VOD erstmals 0 → >0; bestehende Selektion, neue/ungewählte Kategorien, all-new-option, Cancel ohne Änderungen.
- **VOD-08** Kein Credential-Leak in UI, Logs, Exceptiontexten, generiertem Support-/CI-Artefakt; Backup/Restore auf isolierter Kopie.
- **VOD-09** Native Kodi-21/BINGIE-Regressionsprüfungen: Live-TV, EPG, TMDB-Zugang, Navigation, Widgets, Suche, Filme-/Serien-Autoplay/Resume, Wizard .71; 48 Komponenten nicht neu installiert.
- **VOD-10** TX60Pro Android-Handtest (separat **NOT_TESTED** bis Nutzer testet): Provider in anderer App hat VOD, XCMate-Nachscan findet Kategorien/Titel, Kodi-Neustart, Persistenz; keine Behauptung von PASS auf Basis von Hosttests.

## Lieferung / Freigabe
- Codex: vom **aktuellsten** main aus arbeiten, erhaltend und kumulativ; neue Version über bestehendem tatsächlichen Stand wählen. Diagnose und Fix mit präzisen veränderten Codepfaden; Tests und vollständiger Testbericht unter `docs/XCMate/`.
- GitHub PR mit Issue-Verknüpfung, vollständigem Diff, ZIP + SHA256, Kodi-Index-/Updatekanal-Prüfung, CI-Belegen. Keine Rohlogs/Providerdaten hochladen. Review-Testartefakt vor regulärem Release.
- **Kein eigenmächtiger Merge/Release** vor separater Freigabe; echtes Android-PASS erst nach Anwenderabnahme. Issue nicht als gelöst markieren, solange VOD real 0/0.
- Nach Release Anleitung: Vorhandenes Add-on aktualisieren → XCMate → Einstellungen → bestehender Provider → „Katalog aktualisieren“ → Filme + Serien auswählen → Scan → Readback prüfen → Kodi-Neustart. **Kein Installer-Neustart.**

## Codex-Kurzstart
„Lies `docs/XCMate/P0_VOD_NACHSCAN_FILME_SERIEN_2026-11-04_DE.md` vollständig, analysiere die Remote-VOD-API und den aktuellen Portal-/Katalog-Lifecycle. Implementiere einen sicheren, inkrementellen Nachscan für Filme und Serien auf der bestehenden Portal-ID. Starte mit der nachgewiesenen Gerätebeobachtung 53 Live-Gruppen/0 VOD/0 Serien und 3357 Live-Sendern. Schütze sämtliche Bestandsdaten, liefere PR, reproduzierbaren ZIP-Build, SHA256 und Testmatrix. Merge und produktives Publishing erst nach ausdrücklicher Freigabe.“
