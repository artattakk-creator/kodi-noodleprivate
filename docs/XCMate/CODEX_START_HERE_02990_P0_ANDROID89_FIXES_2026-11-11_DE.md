# CODEX START HERE – XCMate 0.1.29.90, Android-.89-P0-Hotfix

**11.11.2026. Bereit zur Codeumsetzung, noch keine .90-Fixes implementiert oder veröffentlicht.**

## Verbindliche Referenzen
- Repository: `artattakk-creator/kodi-noodleprivate`; Plugin `plugin.video.xtreammate`.
- **Master-Issue**: [#430](https://github.com/artattakk-creator/kodi-noodleprivate/issues/430), inklusive sämtlicher Nachträge.
- **Technischer Detailauftrag**: [CODEX_UEBERGABE_02990_ANDROID89_STARTUP_LOGO_EPG_2026-11-11_DE.md](CODEX_UEBERGABE_02990_ANDROID89_STARTUP_LOGO_EPG_2026-11-11_DE.md), vollständig lesen (Abschnitte 1–7).
- **Realer .89-Android-Test mit FAILs**: [ANDROID_ABNAHME_02989_DE.md](ANDROID_ABNAHME_02989_DE.md).
- Veröffentlicht ist **XCMate 0.1.29.89** auf main/regulär/Pilot/NeoDark3, Source-PR #426, Release-PR #429. Kodi 21.3, Android RK3528 ARM32, Titan BINGIE MOD. Aktuellen `main` SHA vor dem Branching lesen.
- GS Media Installer bleibt bei 0.5.26; Entwürfe #418 (.5.27) und #428 (.5.28) gehören **nicht** in .90.

## P0-Pflichtumfang – kein Teilbereich optional

| P0 | Auf Android beobachtet bzw. im Log belegt | Präzise technische Prüfstellen |
|---|---|---|
| **A – Senderlogo-Rail** | Beim ersten .89-Kaltstart 59/88 → 68/88 innerhalb von ca. 4½ min. Davor 58 echte `LOGO89 PERSISTED_VERIFIED`-Writes. Bestehende Logos sofort manifestbasiert anzeigen, **nur fehlende** nachladen; nach einmaligem Erstaufbau keine Downloads beim Neustart. | `station_logos88.py`, `logo_manifest86.py`, `logo_store89.py`, `live_rail86.py`, `widget_assets69.py` |
| **B – Start-EPG** | 7 `EPG_READ_TIMEOUT`, 7 `EPG_DB_BUDGET`, 5/5 `HOME_NOW_NEXT_READY` ohne READY. Gültige Now-/Next-Daten zeitnah aus verifiziertem LastGood anzeigen. | `epg_single89.py`, `epg_read69.py`, `epg_poll77.py`, `epg_handoff63.py` |
| **C – GUI/Portal** | 4 `GUI86 CALLBACK_FAILED` in Portal-/Home-/Widget-Lesewegen des .89-Neustarts. Ursache instrumentieren; sichere immutable Portal-/Profilgeneration und kontrollierte Invalidation. | `portals.py`, `portal_snapshot.py`, `widget_entry46.py`, `programme_assets47.py` |
| **D – Filme/Serien** | Beide XCMate-Widgets fehlen auf Home. Vorherige echte Film-/Serien-Daten und Cover bei SQL-Busy/Timeout nicht als `EMPTY` überschreiben. | `widget_data41.py`, `catalog_commit89.py`, `widget_refresh45.py`, `widget_runtime79.py` |
| **E – Fremdwidgets** | Selbst angelegte Widgets anderer Anbieter erscheinen ebenfalls nicht. Gespeicherte SkinShortcuts-Properties, Skin-Bindings, native Consumers, nicht den fremden Anbieter pauschal beschuldigen. | `widget_inventory87.py`, `widget_audit89.py`, `widget_skin88.py`, `script-skinshortcuts-includes.xml` |
| **F – manuelle Bildzuordnung** | TMDB-/TVMaze-Suche liefert Treffer, Auswahl lässt sich nicht dauerhaft speichern, Fehlermeldung. Eventgenauen, atomaren SAVE/READBACK bis Kodi-Neustart reparieren. | `work_manager86.py`, `work_requests86.py`, `work_search86.py`, `programme_mapping85.py` |
| **G – Sendergruppen** | Laufendes TV → LINKS öffnet Mini-EPG → nochmals LINKS: Gruppen fehlen teilweise oder nach Auswahl keine Sender. Indexed Gruppen/Sender mit Filter, SID und Generation vollständig verfügbar; DB_BUSY darf nicht zur Falschleere führen. | `live_group68.py`, `group_selection.py`, `live_catalog.py`, `live_guide_navigation.py` |
| **H – Widget-Auswahl bei Neuinstallation** | XCMate-Quellen sind im **BINGIE MOD → Shortcuts → Widget auswählen**-Fenster nicht mehr am früheren Ort. Nativen Browse-Picker mit **Live-TV-Startgruppe / Neueste Filme / Neueste Serien** wiederherstellen, mit/ohne Portal testen. | `widget_sources49.py`, `widget_binding50.py`, `app_routes.py`, `widget_manager50.py`, `shortcuts62.py` |

**P0-H ist eigenständig!** Eine sichtbare Filmreihe auf Home ist noch **kein** Nachweis, dass die Quellen im nativen SkinShortcuts-Auswahldialog nach frischer Installation wieder gefunden und gespeichert werden können.

## Fehlerbeleg / Auswertungsgrenzen
Sechs hochgeladene private Kodi-Logs, fünf unterschiedliche Datei-Inhalte und drei überlappende Laufphasen; .89 erst ab 12:57:49 installiert, **echter .89-Neustart 13:16:13**. Im echten Neustart: 59/88 um 13:17:59 → 68/88 um 13:22:30, 0/5 Home-Now-/Next READY und 4 Callback-Fehler. **Kein Beweis für vollständigen Logo-/EPG-Datenverlust.** Vor .89 beobachtete generische STORAGE_RESERVE_BLOCKED-Ereignisse nicht .89 zurechnen. `TEXTURE_CACHED` bedeutet nicht `PIXEL_VISIBLE`. Nutzerberichte zu P0-D/E/F/G/H sind echte UI-Beobachtungen, aber ohne neue Aktions-Stacktraces – die konkreten Fehlerursachen **gezielt verifizieren**, nicht erraten. Keine Rohlogs/URLs/Provider-/Token-Geheimnisse nach GitHub übertragen.

## Sofortiger Arbeitsablauf für Codex

1. Issue #430 und kompletten verlinkten Detailauftrag/Android-Test lesen; aktuellen main und vorhandene .90-Branche/PR überprüfen, **eine** .90-Entwicklungslinie verwenden.
2. Eigenen **0.1.29.90-Hotfix-Branch + Draft-PR** nutzen/anlegen. Vor Codeänderung für jeden P0-Fall mindestens einen reproduzierbaren Regressionstest erzeugen, bei dem die vorhandene .89 scheitert. Kodi-UI/Worker/SQLite/Profilgeneration isolieren; vorhandene gültige Snapshots erhalten.
3. Fixes implementieren, ohne SkinShortcuts-Properties, Portaldaten, TMDB-Token, EPG-/Gruppenmappings oder Benutzercache zu löschen. Keine 88/88-Erfolge bei Sendern ohne Logoquelle vortäuschen. Native BINGIE-Fernbedienungsnavigation separat von Mock-Tests belegen.
4. T90-01 bis T90-14 vollständig nachweisen (unten Kurzmatrix), reale Android-Ausführung **als offen markieren**, solange nur Host/Native-Linux geprüft wurde. Testbericht mit PASS/FAIL/NOT_TESTED und konkreten Artefakten.
5. Reproduzierbares ZIP `plugin.video.xtreammate-0.1.29.90.zip` und SHA256; Scope-Diff; Draft-PR gegen main; Issue #430 mit Implementierungs-/Teststatus aktualisieren. Keine Veröffentlichung bis zur nächsten ausdrücklichen Benutzerfreigabe.

## Verbindliche Tests T90-01 bis T90-14

- **01–03:** Vorher nachweislich persistierter Logo-Bestand: 2–3 komplette Kodi-Neustarts, vorhandene Logos spätestens **10 Sekunden nach Home-ready (Ziel)**, keine neuen HTTP-Downloads für gültige Dateien, begründete Missing-Source-SIDs; Test bei ~115 MB frei und gewahrter lokaler Sicherheitsreserve.
- **04–05:** Verifizierter EPG Now/Next im Home **innerhalb 30 Sekunden (Ziel)**, nicht 0/5 READY; 15 Minuten GUI + 20 Fokuswechsel, **0 CALLBACK_FAILED**.
- **06–08:** Regression Hero-/Cover-/Widget-Stabilität, Daten-/Player-Erhalt, Host-/native 720p/1080p, Android gesondert.
- **09:** Filme **und** Serien, je mindestens fünf reale Titel/Cover sichtbar, 3 Neustarts, Busy-/Timeout-Pfade ohne Datenverlust.
- **10:** Zwei unabhängige Fremdwidgets, gespeicherte SkinShortcuts-Definitionen unverändert, reale BINGIE-Controls sichtbar.
- **11:** TMDB/TVMaze suchen → Mehrtreffer → expliziten Treffer wählen → SAVE/atomarer Readback → Details schließen/öffnen → Kodi-Neustart: dieselbe Zuordnung, keine Fehlermeldung; Timeout/EPG-Revision/Lock separat.
- **12:** TV LINKS → LINKS → Gruppen → Senderliste, 20 Gruppenwechsel + 20 Senderwechsel, auch Gruppen >128 Sender, ohne leere/falsche Listen, Playback bleibt stabil.
- **13:** Vorher-/Nachher-Hashes und Inventar: Providerportale, Token, EPG-Gruppenfilter, Nutzerwidgets, SkinShortcuts, Artworks, Logos ohne unerlaubte Änderung.
- **14:** **FRISCHINSTALLATION** BINGIE → Shortcuts → Widget auswählen → XCMate zeigt alle 3 Quellen. Jede zuweisbar, WidgetPath gespeichert, nach Neustart weiterhin auffindbar und sichtbar. Ohne Portal sichere „Portal zuerst einrichten“-Führung; mit Portal direkt auswählbar. Upgrade mit fremden Widget-Definitionen unverändert.

## Sicherheits- und Freigabegrenzen

**Keine** Cache-/Datenbank-Löschung oder globaler Reset, kein unaufgefordertes SkinShortcuts-Rebuild, keine Veränderung der 1-GiB-Globalreserve, keine Pflicht für 2/6 GB beim dynamischen Bild-EPG, keine separate USB-/NAS-/Joomla-/Google-Drive-Implementierung, kein TMDB Helper. `Sendung merken` bleibt **„Jetzt umschalten“ / „Verwerfen“** (kein Snooze/Auto-Tune).

**.89 bleibt in main/regulär/Pilot/NeoDark3 bis auf ausdrückliche neue Nutzerfreigabe.** .90 nur Branch/Draft-PR/Test-ZIP + SHA256. `ANDROID_NOT_TESTED` bis echte RK3528-Box-Abnahme.

## Ein-Zeilen-Auftrag
> Arbeite XCMate 0.1.29.90 gemäß diesem Startdokument, Issue #430 und der vollständigen verlinkten Übergabe ab: P0-A bis P0-H umsetzen, T90-01 bis T90-14 testen, Nutzerdaten erhalten, .90 Branch/Draft-PR/Test-ZIP/SHA256 liefern, kein Merge oder Release.
