# Codex-Übergabe – XCMate 0.1.29.84: BILDER ZUERST
Stand: 09.11.2026. **P0**. **Verbindlich:** nicht die Migration allein als Erfolg werten; der Nutzer sieht zurzeit **keine Senderlogos, keine Live-/EPG-Programmbilder auf BINGIE und keine Film-/Seriencover**.

**Maßgebliche GitHub-Vorgänge:** [#403 – sichtbare Bilder zuerst](https://github.com/artattakk-creator/kodi-noodleprivate/issues/403), [#401 – Speicher/Journal](https://github.com/artattakk-creator/kodi-noodleprivate/issues/401), [#398 – Android-Kapazität](https://github.com/artattakk-creator/kodi-noodleprivate/issues/398), [#395 – Startseitenmaster](https://github.com/artattakk-creator/kodi-noodleprivate/issues/395), [#106 – Migration intern/USB/SMB](https://github.com/artattakk-creator/kodi-noodleprivate/issues/106).

## 1. Kurzdiagnose / echte Logs

Nutzer-Logs: kodi.old(20261109-115006).log, kodi(20261109-115004).log. Beide sind privat, nicht committen: altes Log enthält eine SMB-URL mit Benutzername/Passwort. Nur redigierte Zeit-/Zeilenverweise.

| Beobachtung | Beweis aus altem Log |
|---|---|
| VOD/Serie-Daten vorhanden, Artwork fehlt | WIDGET47 Zeile 660 (Serie) / 667, 711 (VOD) / 795 (Serie): 24 Items, 0 local/matched images, 24 placeholders |
| Live-Widgets ohne anzeigbare Bilder | WIDGET47 Zeile 1019: NO_RENDERABLE_REFERENCE trotz 36 logo_sources/36 poster_sources; anderes Mal 88 selected |
| Startseite publiziert Referenz, nicht Bild | HOME82 121× CACHED_ITEMS_READY mit local_images=0, approved_refs=0, android_render_verified=false; HOME74 REFERENCE_PENDING |
| EPG-Quelle ist nicht grundsätzlich tot | IMAGE77 18× HTTP_RESPONSE IMAGE_DECODED; 95× LOCAL_CACHE RAM_ONLY; 62× MATCHED_EVENT_FACTS SOURCE_MISSING (Pipeline-Stufen/Events nicht 1:1) |
| Speicherdruck | ART_STORAGE82 13× FUSE 4,034,297,856 Byte total, rund 28 MiB nutzbar; ARTWORK 22× enroll DISK_FULL; Programme-DB 50× PROGRAMME_DB_IO und 5× DISK_FULL |
| Migrator nicht gestartet | ART_STORAGE83 12:20:44 und 12:37:24 JOURNAL_RESERVE_BLOCKED (USB, SMB); 12:42:51 TARGET_SAME_CAPACITY_POOL (Android Movies) |

Kodi-Systeminfo zugleich /storage/emulated/0 angeblich 256 GB total/144 GB frei; XCMate-Dateipfadstatvfs ca. 3,76 GiB total, nur 27 MiB available. Unterschied offen, niemals ignorieren, Quell-/Zielpool nicht frei erfinden. Nutzer hat leere Movies/XCMate/Artwork/{media,logos,fanart}/<Profil> gesehen. Nutzer bestätigt, dass Caber Toss Logdateien auf SMB speichern **kann**. Das ist ein Schreibnachweis für eine Anwendung/einen Pfad, nicht automatisch XCMate-Render-PASS.

## 2. Entscheidung: .84 hat Bildanzeige als harte Abnahme

**Priorität 1 – LIVE STARTBILD:** Startsender/aktuelle Sendung und Startgruppe. Sofort Senderlogos aus geprüften Quellen bzw. verifizierten lokalen Dateien anzeigen; erst Startsender + die ersten fünf Logos/EPG-Bilder, dann die restliche Gruppe. Bei passender verifizierter Sendungsquelle (TVMaze/TMDB/Provider-EPG) echtes Hero; falls keine Quelle, station logo oder eindeutiger neutraler Platzhalter. Keine Bildverwechslung zwischen Sendungen. Jetzt/Nachher und Sendernamen, Senderfortschritt und Fokusrahmen stabil lassen. Keine Generik-Icons, wenn echte Logos zulässig vorliegen; keine leeren Statusfelder.

**Priorität 2 – FILM UND SERIE:** Die vorhandenen 24 Items je Widget müssen Bildreferenzen erhalten. Providerposter/-fanart als Primärquelle; kein TMDB Helper als Pflicht. Bestehende katalogisierten Inhalte/Providerdaten nicht grundlos neu indexieren. Prüfe Sicherheitsfilter und Statuspfade genau: Quelle existiert, URI erlaubt, DNS-/HTTPS-Approval, Darstellung im Kodi ListItem, Texture-Cache, tatsächliche Anzeige. Unter reserviertem Speicher darf optionaler JSON-/SQLite-Artwork-Status nicht sämtliche bereits zulässigen *Anzeigereferenzen* verschwinden lassen.

**Priorität 3 – EPG/PROGRAMME:** IMAGE_DECODED bedeutet nicht Bild im GUI. RAM_ONLY ist gerade kein persistiertes Bild; nur sichere explizit zeitlich und eventgebundene HTTPS-Referenz nach existierenden Credential/URL/DNS/Redirect/SSRF-Prüfungen als display-only Fallback bereitstellen, wenn das Kodi-Backend sie real rendern kann. Sonst ehrlicher Platzhalter und Diagnosecode. Richtige Sendung/Staffel/Titel-Jahr-Abgleich; Attribution und Programmdetails unverändert.

**Priorität 4 – RECOVERY/STORAGE:** Wo Last-Good-Bild/erlaubte externe URI existiert, nicht durch neue fehlgeschlagene Metadatenwrites auf 0/Platzhalter zurückfallen. Programme- und Artwork-Worker bei DISK_FULL/SAFE_RESERVE_BLOCKED budgetieren/backoff, nicht auf jedem Widgetrefresh neue Persistenzversuche. Keine Datenbanklöschung, kein blindes Lock-Brechen, Reserve niemals pauschal abschalten. #401-Journal-Bootstrap nur wenn ohne Risiko möglich und für Bild-DoD erforderlich; ansonsten eigenständiger, nachgelagerter Fix. Aktuelle Artwork-Moduswahl und alle bestehenden Nutzerkonfigurationen beibehalten.

## 3. Verdächtige Codepunkte, systematisch testen

- src/plugin.video.xtreammate/resources/lib/widget_art44.py: prepare() schreibt referenzierte JSON-Metadaten via tempfile, art() findet bei Nicht-Dynamic sonst nur lokale Bilder. Bei knapper Reserve sind diese Schritte getrennt zu behandeln; keinerlei ungeprüfte URL-Adoption.
- artwork_config.py: persistent() anhand mode; Nutzerprofil nicht still von internal auf dynamic ändern.
- artwork_visible.py: bounded worker DNS/Public-IP-Approval, kurze TTL, Kodi URL-Optionen, retention; darf nicht zu SSRF/Credential-Bypass werden.
- widget_assets69.py: Quellenprüfung samt Login-Secrets, image lease, Window-Referenzen, recovery/caching; prüfen, warum widget refs/count=0 und warum valid provider source nicht zu Renderquelle wurde.
- media_art.py, widget_items45.py, widget_render47.py, widget_live47.py, widget_cache82.py, widget_skin*.py: tatsächlicher Übergang bis Kodi ListItem.setArt und Home/Timer, nicht nur Quelle/JSON.
- programme_pipeline77.py, programme_transport77.py, programme_art46.py, programme_image69.py, programme_widgets46.py, programme_assets47.py: EPG-Foto decodiert→RAM_ONLY→scoped display/texture; separate, überprüfte Fallback-Möglichkeit ohne persistente DB. Keine Bildfalscherkennung/Token-Leaks.
- home_lkg82.py, home_publication74.py/80.py: last-good bei unveränderter Source-Revision nicht auf REFERENCE_PENDING/PARTIAL zurückfallen.

## 4. Sichtbarkeits-Testplan

- Host: 27 MiB intern verfügbar, EPG image decoded but no persisted file, verified URL lease valid/expired, provider logo/source vorhanden aber blocked, 24 Filme + 24 Serien, view refresh, temporär Offline/Netzwerkabbruch, Crash/restart, 30-sec-DNS-Lease/redirect, wrong EPG event, Kodi texture fail, repeated missing DB writes, FUSE same pool.
- Hardware Box B (Kodi 21.3 ARM32/RK3528 BINGIE MOD): Startgruppe sichtbar; echte Senderlogos und Startsender; mindestens ein *wirklich verfügbares und zum EPG passendes* Live-Hero-/Programmbild, sowie sichtbares Film- und Serienposter. Dazu Screenshot+redigierte Kodi-Texture-Prüfung, Quellen-/Match-/Render-Zahlen, Fokus-/Zurück-/Neustart-Test. Ein Event ohne Bildquelle darf neutrale Fallbackgrafik zeigen, zählt **nicht** als Eventbild-PASS.
- In UI angeben: Quelle fehlt vs URL aus Sicherheitsgründen blockiert vs Bilddekodierung gelungen vs Dateireserve blockiert vs Bild wird aktuell geladen vs Kodi-Textur nachgewiesen. Keine falschen PASS-Zähler.
- Bestandsschutz: Box A, Provider-, TMDB-Zugänge, EPG-Quellen/Mapping, Kodi MyVideos131 DB, Favoriten, SkinShortcuts/Branding und Setup Wizard 0.5.26 unangetastet. Keine Raw-Logs/SMB-URI-Credentials öffentlich.

## 5. Liefervertrag

**Ein** .84-Branch: fix/xcmate-02984-artwork-visible-first, vom aktuellen main. Testen, CI, Changelog, ZIP+SHA256, PR gegen main, Bewertung PASS/FAIL/NOT_TESTED im Issue #403. Den alten exklusiven .84-Branchvorschlag aus #401 NICHT zusätzlich starten. **KEIN automatischer Merge, KEIN Release in regulär/Pilot/NeoDark3 ohne Freigabe.** Google Drive nicht entwickeln. WebDAV ist höchstens späteres P2 und kein Release-Blocker. Dokumentationslink zu diesem Auftrag im Issue #401/#395 hinterlegen.
