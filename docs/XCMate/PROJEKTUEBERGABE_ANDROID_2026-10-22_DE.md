# XCMate – Projektübergabe und Android-Abnahme (22.10.2026)

> **GitHub-/Android-Stand 22.10.2026:** 0.1.29.11 / [PR #80](https://github.com/artattakk-creator/kodi-noodleprivate/pull/80) wurde auf Android **funktional mit Restbefunden** abgenommen (Bildspeicherstatus 10/10, Filme/Serien, Resume, EPG und Live-TV PASS). Die [bereinigte Logauswertung](ANDROID_LOG_AUSWERTUNG_02911_2026-10-22_DE.md) dokumentiert weiterhin SQLite-BUSY und Android-MediaCodec-Warnungen; Issues #69/#75/#86/#87 bleiben offen. **0.1.29.13 / [PR #82](https://github.com/artattakk-creator/kodi-noodleprivate/pull/82) wurde auf ausdrücklichen Nutzerauftrag nach `main` gemergt** (Merge [`dcee6d2`](https://github.com/artattakk-creator/kodi-noodleprivate/commit/dcee6d2a57a9d7b3dad4e1257f688b13fabbf79b)). Der [Publish-Workflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39733665167) war erfolgreich, und **`addons.xml` bietet 0.1.29.13 regulär an**. **Android-Ersttest des neuen horizontalen EPG: Layout positiv, Gruppen-/Logo-/Zuordnungs-Blocker in Issue #88**. Feature-Drafts .14/.15 bleiben separat und ungemergt. Keine weiteren Merges/Releases ohne erneute Freigabe.

> **Nutzerauftrag 22.10.2026: künstliche Bremsen entfernen.** 512-MiB-Artwork-Default + 4096-MiB-Cap, feststeckende SPACE_FULL-Jobs und unnötige SQLITE_BUSY-Sperrpausen systematisch lösen; **SQLite-WAL/Dateisperren als Integritätsschutz bewahren**. [Codex-Arbeitsauftrag](CODEX_AUFTRAG_BREMSEN_ABBAU_2026-10-22_DE.md) · [Issue #90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90) · [Issue #91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91). Vor Umsetzung zuerst den [P0-Kodi-Absturz #89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89) isolieren. **Auftrag erfasst; entsprechende Codefixes noch NICHT implementiert / kein neues OTA-Release.**

## 0.1.29.13 – Android-Test: positives Layout, kritische Restfehler (22.10.2026)

**Layout/OK-Kontextmenü:** Die neue horizontale gemeinsame Zeitachse und der grundsätzliche UI-Aufbau gefallen dem Nutzer; die Auswahl per OK und das erscheinende Aktionsmenü funktionieren zunächst. Die funktionale EPG-Abnahme ist **NICHT bestanden**.

- **P0 KODI-PROZESSABSTURZ:** EPG → Sendung auswählen → OK-Menü → **„Jetzt Sender ansehen“** beendet Kodi vollständig, Neustart nötig. Den Menüpunkt bis zur Korrektur nicht erneut bedienen; aktuelle Ursache nicht bewiesen. Der Hand-off in `guide_grid_window._actions` schließt das Window und ruft sofort `PlayMedia(plugin://...)` auf. Prüfung/isolierter Fix in [#89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89), **vor weiteren EPG-Wiedergabetests**.
- **P1 EPG-Start-/Gruppenhierarchie:** **Vorrangige präzisierte Nutzeranforderung (überschreibt „erst Gruppenliste“):** EPG startet **sofort mit horizontalem Raster der gespeicherten Startsendergruppe**, dabei **gespeicherten Startsender sichtbar markieren**, ursprüngliche Senderreihenfolge erhalten (ggf. Viewport auf Senderposition setzen). Innerhalb des EPGs **Links** → Liste aktivierter Sendergruppen, Hoch/Runter wählen, OK → ausschließlich Sender/EPG dieser Gruppe. Back führt kontrolliert eine Ebene zurück, ohne Kodi/XCMate zu verlassen. Kein `category=None`-All-Sender-Start. In [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88).
- **P1 Senderlogos:** Im realen Guide fehlen Logos. Lokalen Cache, `stream_icon` und Texturpfade kontrollieren. Letzter Nutzerstatus 514/512 MiB Artwork, viele `SPACE_FULL`-Jobs; nicht direkt als ausschließliche Logo-Ursache bewiesen.
- **P1 512-MB-Artwork-Sperre DRINGEND ENTFERNEN:** `art_store.budget()` erzwingt 512 MiB Default/max. 4096 MiB; Nutzer verlangt keine künstliche 512-MiB-Blockade. Sicheres Budgetmodell ohne starres Kleinlimit, physische Freispeicherreserve erhalten, bestehende Bilder nicht löschen, `SPACE_FULL`-Queue datenschonend reaktivieren, sichtbare Senderlogos vor Hintergrundcovern priorisieren. [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90), vorhandene Artwork-/DB-Befunde [#41](https://github.com/artattakk-creator/kodi-noodleprivate/issues/41) und [#69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69) beachten.
- **P1 EPG-Daten und Details:** Nur ein Teil der EPG-Daten sichtbar; XMLTV-Kanalzuordnung direkt am gewählten Sender aus dem Raster mit gespeicherten Daten/Quellen, Vorschau/Bestätigung und kontrollierter Aktualisierung gewünscht ([#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60), [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88)). OK → Details liefert bislang nur Kurztext; Nutzer wünscht Langbeschreibungen, Episodenbilder/Fanart und verfügbare Programminformationen aus tatsächlichen XMLTV-/Providerdaten, ggf. verifiziertem Metadata-Enrichment. Fehlende Infos ehrlich anzeigen, kein Schein-TMDB-Matching oder HTTP im GUI-Thread.
- **Schutz:** 0.1.29.13 ist bereits via GS Media Repo veröffentlicht, **kein weiterer Merge/Release** durch Testbericht. 0.1.29.11 ist der zuletzt funktional geprüfte Arbeitsstand (mit dokumentierten SQLite-/Codec-/Filmimport-Restbefunden). Ein neuer Fix muss auf `main`/0.1.29.13 aufsetzen und als eigener **Draft-PR/Test-ZIP** geprüft werden. Filme/Serien/Live-Overlay, Portal-/EPG-Daten, Favoriten und Resume bleiben unverändert.

## Grunddaten und Schutzregeln

- Projekt: **GS Media XCMate**, Kodi-IPTV-Add-on `plugin.video.xtreammate`.
- Repository: https://github.com/artattakk-creator/kodi-noodleprivate
- Testgerät: Android TV 13, Rockchip RK3528/ARM32, Kodi 21.2 Omega, Titan BINGIE MOD 2.2.3, IR-Fernbedienung.
- **Letzter auf Android funktional getesteter Stand: 0.1.29.11 (mit offenen SQLite-/Import-/Codec-Befunden); 0.1.29.8 ist die ältere bestätigte stabile Rückfallbasis.** Die getestete Film-/Seriennavigation ist vor Regressionen zu schützen. Issue [#73](https://github.com/artattakk-creator/kodi-noodleprivate/issues/73) abgeschlossen: 20/20 Öffnen-Schließen, 6/6 Doppel-Zurück, Film- und Episodenrückkehr PASS.
- **Versionsgrenze strikt unter 0.1.30.** Alte ZIPs niemals überschreiben. Keine eigenmächtigen Merges, Releases, Datenbank-Löschungen, Profil-Migrationen, globalen Keymap-Änderungen oder Issue-Schließungen ohne reale Abnahme.
- Vor dem ersten Android-Test Profilbackup, vorhandene Portale, EPG-Mappings, Sendergruppen, Favoriten, Artwork und Resume-Daten erhalten; vertrauliche Logs vor Veröffentlichung bereinigen.

## Gestaffelte Android-Abnahme (0.1.29.11 funktional PASS; 0.1.29.13 veröffentlicht, Gerätetest offen)

| Reihenfolge | Version | Draft-PR | Schwerpunkt | Berichtete automatisierte Tests | Android |
|---|---|---|---|---|---|
| 1 | 0.1.29.11 | [#80 – MERGED](https://github.com/artattakk-creator/kodi-noodleprivate/pull/80) | Bildspeicherstatus und SQLite-BUSY | 568 PASS; CI PASS | **Funktional PASS mit Restbefunden** |
| 2 | 0.1.29.13 | [#82 – MERGED/PUBLISHED](https://github.com/artattakk-creator/kodi-noodleprivate/pull/82) | Horizontaler EPG-Programmguide | 584 PASS; Publish PASS | **Layout PASS, Gruppen/Logos/Mappings ausstehend (#88)** |
| 3 | 0.1.29.14 | [#83](https://github.com/artattakk-creator/kodi-noodleprivate/pull/83) | Film-/Serien-UI, grüner Fokus, Fanart | 580 PASS | NOT_RUN |
| 4 | 0.1.29.15 | [#84](https://github.com/artattakk-creator/kodi-noodleprivate/pull/84) | Eigenes XCMate-Media-Player-OSD | 581 PASS | NOT_RUN |

**Achtung:** 0.1.29.13 ist jetzt in `main`; .14 und .15 bleiben **nicht kumulative Feature-Drafts** auf Grundlage von .11. Ihre Integration muss die neuen .13-Änderungen bewusst erhalten, technisch prüfen und gesondert auf Android abnehmen. Die zurückgezogene Version **0.1.29.12/PR #81 niemals installieren** (ungültiges Kodi-API-Capability-Feld).

### Test 1 – 0.1.29.11, Issue #75 und #69

Unter .8 schlug `art_status` fehl: `DISPATCH_FAILED error=OTHER`, außerdem `artwork db: code=BUSY phase=QUERY sqlite=5`. Dies beweist **keine** Beschädigung der Datenbank.

- Test-ZIP: https://github.com/artattakk-creator/kodi-noodleprivate/raw/refs/heads/fix/xcmate-02911-art-status/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.11.zip
- SHA256: `428a23ae8a627075da779b3bff0618d1ca70b535aa44a12355ed22e95e912faa`
- ZIP installieren, Versionsanzeige prüfen, Kodi vollständig neu starten. Bildspeicherstatus **10×** öffnen/schließen; gesperrte Datenbank muss einen verständlichen Teilstatus liefern; Diagnose und Einstellungen prüfen; EPG, Live-TV, Filme und Serien auf Grundfunktion testen. Bei FAIL sofort Testkette anhalten, Zeitpunkt/Log erfassen; keine Daten verändern.

### Test 2 – 0.1.29.13, EPG-Guide (Issue #57)

- Reguläres ZIP / Kodi-Repository: https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.13.zip
- SHA256: `485d59229aaf288de1b6392fc3169cc7d5b718402609fe40b0cd6a2391bdb091`
- Soll: fixe Senderlogo-Spalte, horizontale gemeinsame Zeitskala, nach Dauer skalierte Sendungsblöcke, Jetzt-Markierung, neongrüner Fokus. Hoch/Runter Senderzeilen; Links/Rechts Sendungen; OK Details/Aktionen; Zurück schließt Kontext bzw. Guide; Sprünge zu Jetzt/20:15/Tagen sowie Gruppenwechsel und Suche.
- Noch offen: erweitertes XMLTV-Mapping, TMDB, Catch-up, echte Aufnahme, Quellenvollständigkeit für 7–10 Tage. Issues #60, #58, #62. Auch fehlende EPG-Daten müssen kontrolliert behandelt werden.

### Test 3 – 0.1.29.14, Medien-UI (Issue #74)

- Test-ZIP: https://github.com/artattakk-creator/kodi-noodleprivate/raw/refs/heads/feat/xcmate-02914-media-focus/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.14.zip
- SHA256: `995ba0a4fc263de9a55fb3568adeeb8cc4866c912cacedf27617aaec3b6ecf84`
- Prüfen: Suchfeld/Kategorien oben; Reihenfolge Weiter ansehen → Favoriten → Neu hinzugefügt; größere Poster, mehrzeilige Titel, vertikale Navigation, sichtbare neongrüne Fokusumrandung auf allen navigierbaren Elementen; je Film korrektes großflächiges Fanart mit dunklem Textverlauf und neutralem Fallback; keine fremden/stale Hintergrundbilder. Keine vorhandenen Appearance-Settings verändern.

### Test 4 – 0.1.29.15, XCMate-Player-OSD (Issue #79)

- Test-ZIP: https://github.com/artattakk-creator/kodi-noodleprivate/raw/refs/heads/feat/xcmate-02915-media-osd/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.15.zip
- SHA256: `ef02da17cad658858ea9a98c10ce28d95e67d0f86a2ac20b21ba6c223db8e34d`
- Prüfen: Filme und Serienepisoden mehrfach starten; OK öffnet XCMate-OSD, Zurück schließt nur OSD, bewusstes Stop beendet Bild/Ton; Play/Pause, Seek wo unterstützt, Tonspur, Untertitel, Bild-/Tonsettings, Poster/Titel/Laufzeit, Fokus, Resume. Kein Eingriff in fremde Kodi-Wiedergaben oder Live-TV-Overlay.
- Geplanter, noch **nicht aktiver** Downloadbutton siehe Issue #63.
- **Serien-Autoplay ist ausdrücklich NICHT Bestandteil dieses Kandidaten.**

## Entwicklungsauftrag danach: Serien-Autoplay – Issue #85

- Verbindliches Issue: https://github.com/artattakk-creator/kodi-noodleprivate/issues/85
- Historische Spezifikation mit verbindlichem neuen Vorrang: https://github.com/artattakk-creator/kodi-noodleprivate/blob/main/docs/XCMate/SERIES_PROGRESS_SPEC_DE.md
- Geplanter Kandidat **0.1.29.16**, nur nach Prüfung auf bereits vergebene Versionsnummer, als **eigener Draft-PR auf Grundlage von PR #84**. ZIP .15 unangetastet lassen.

**Soll:** Nach dem regulären Ende einer vom Nutzer bewusst gestarteten Serienepisode die nächste tatsächlich vorhandene Episode derselben Serie und desselben Portals **automatisch ohne weiteres OK** abspielen, auch über Staffelgrenzen. Fehlende Episodennummern überspringen, aber numerische Reihenfolge behalten; Staffel 0/Specials nicht automatisch einreihen; am wirklichen Serienende aufhören, kein erneuter Start von Episode 1. Manueller Stop und Stop während Übergangs brechen die gesamte Kette ab, ohne Hintergrundton. Opt-out für die aktuelle Sitzung im eigenen OSD; bestehende produktive Einstellungen nicht heimlich ändern. Nur bei verifiziertem natürlichem Ende fortsetzen; nicht bei Netzwerkfehler, Kodi-Ende, manuellem Stop, Film, Trailer, Live-TV oder fremden Add-ons. Ereignisse idempotent verarbeiten (keine Doppelfolge); Resume/Gesehen, Session-Ownership, Titel/Poster/Fortschritt im OSD sauber aktualisieren. Keine GUI-Blockierung oder Endlosschleife bei fehlenden Folgen.

Technische Anknüpfungspunkte: `media_progress.py`, `media_osd.py`, `media_window.py`, `media_data.py`, `media_state.py`, `media_intent.py`, `service.py`; kanonische Folgenliste aus `media_data.episode_records()` wiederverwenden.

**Abnahme:** Folge bis Ende → automatische nächste; mehrere Folgen; Staffelwechsel; manueller Stop während Wiedergabe und Übergang; Start mitten in späterer Staffel; Lücken/Serienende/Fehler; Watched/Resume; zuverlässiges Kodi/IR nach Stop; keine Regression des Live-TV-Overlays. Status: SPEZIFIZIERT / NICHT IMPLEMENTIERT / ANDROID NOT_RUN.

## Weitere bekannte Baustellen

- Artwork-/Speicherprofile, lokal/USB und SMB: Issue [#41](https://github.com/artattakk-creator/kodi-noodleprivate/issues/41), Draft [#78](https://github.com/artattakk-creator/kodi-noodleprivate/pull/78), vollständiger direkter SMB-Zugriff offen. Speicherbudget/-ort nicht anfassen.
- Aufnahme / automatisches Umschalten: Issue [#62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62), nur mit real bestätigter Android-Unterstützung.
- Externe XMLTV-Quellen, Sender-Matching und manuelle EPG-Zuordnung: Issue [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60).
- Space Premium, 98 Grafiken: PR [#50](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50) **zurückgestellt**; keine 0.1.30.1.

## Verbindlicher Ablauf im nächsten Chat

1. Zunächst **nur** Android-Test 0.1.29.11 / PR #80; in kurzen Einzelschritten führen und nach jedem Schritt Nutzerergebnis abfragen.
2. Jeden Befund mit installierter Version, PASS/FAIL, exakter Beobachtung, Uhrzeit, ggf. Screenshot und **bereinigtem** `kodi.log` dem zuständigen Issue zuordnen.
3. Nach bestandenem Test separat .13, danach .14, danach .15; bei Fehler sofort stoppen. Kein vorzeitiges Zusammenführen.
4. Anschließend #85 / .16 entwickeln lassen und separat abnehmen. Ein kumulativer Integrationskandidat kommt **erst nach** den Einzelabnahmen.
5. Codex-Codearbeiten: eigener Branch, automatisierte Tests, installierbares ZIP, SHA256, Draft-PR, Android-Testanleitung; **keine eigenmächtigen Merges/Releases**.

Siehe auch [Integrationsdokument](https://github.com/artattakk-creator/kodi-noodleprivate/blob/feat/xcmate-02914-media-focus/docs/XCMate/INTEGRATION_02911_BIS_02914_DE.md).
