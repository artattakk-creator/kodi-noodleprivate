> **UPDATE NACH RELEASE – 21.10.2026:** **XCMate 0.1.29.5 ist nach Integration von PR #61 in `main` regulär veröffentlicht.** GitHub-Merge `c6e7050d5b0ba5bf88943dcf9d55107f0af38fed` (manuelle Konfliktauflösung für drei Übergabedateien), erfolgreicher Publish-Workflow [39639332756](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39639332756); `addons.xml` und ZIP zeigen **0.1.29.5**. Paket 387.805 Bytes, SHA-256 `b9b527e64abd736403b721b33e065ffe1d57ea9ced8352ab23f49f7b0119c88a`. **Android-Gerätetest 0.1.29.5 noch offen**; EZ Maintenance+-Backup von 0.1.29.4 behalten. Phase-A-Issues #58/#59/#60 sind im Code bearbeitet, aber keine Geräteabnahme; PR #50/0.1.30 bleibt gesondert offen und muss die Hotfixes später übernehmen. *Ältere Release-Baseline-Angaben darunter sind historische Snapshot-Werte.*

# XCMate – verbindlicher Projektstatus und Übergabe

**Stand:** 21.10.2026, nach Klärung Multiview / paralleler Aufnahme.  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Produkt:** XCMate von GS Media, nichtkommerzielles Kodi-IPTV-Add-on.  
**Add-on-ID:** `plugin.video.xtreammate` (nicht ändern).  
**Testgerät:** Android-TV-Box, Kodi 21.3 Omega, Skin Titan BINGIE MOD; zusätzlich Estuary testen.  
**Verantwortung:** Codex entwickelt und testet Code; ChatGPT prüft Konzepte, Issues, Dokumentation und Ergebnisse; **Merge/Release nur nach ausdrücklicher Nutzerfreigabe**.

> **DIESE DATEI IST DIE MASSGEBLICHE NEUE EINSTIEGSÜBERGABE.** Frühere Dokumente wie `PROJECT_HANDOFF_DE.md`, `NEW_CHAT_COPY_BLOCK_DE.md` und `CODEX_STATUS_CURRENT_DE.md` bewahren historische Teilstände, darunter veraltete Angaben „0.1.29.4 nicht gemergt“. Nicht als heutigen Release-Status auslegen. Nach dem hier angegebenen Datum den tatsächlichen GitHub-Stand erneut prüfen; dies ist eine Momentaufnahme.

## 0. Zuständigkeit, Chat-Wechsel und Codex-Fortsetzung

- **Dieses Gespräch läuft in ChatGPT, nicht in einer Codex-Entwicklungsumgebung.** ChatGPT koordiniert Architektur, Entscheidungslage, Issue-Spezifikationen und diese Dokumentation.
- **Codex ist der getrennte Entwicklungsworkflow** für Implementierung, Tests, Draft-PRs, ZIP-Paketierung und Changelog. Codex soll zum Wiedereinstieg diese Datei, den [Codex-Folgeauftrag](CODEX_FOLGEAUFTRAG_2026-10-21_DE.md) sowie offene Issues samt Kommentaren lesen, dann Branches und PRs erneut live prüfen.
- **Neuer ChatGPT-Chat:** Den kopierfertigen Abschnitt „Kurze Übergabe für einen neuen Chat“ am Ende dieser Datei senden und diesen GitHub-Link einfügen. Die aktuelle Codebasis und Branchstände können sich seit dem Dokumentationszeitpunkt geändert haben.
- **Wichtig:** Ein ChatGPT-Chatwechsel startet weder automatisch Codex noch eine neue Entwicklungsaufgabe. Ohne ausdrückliche Freigabe keine produktiven Änderungen, Merges oder Releases. Dokumentationsänderungen in `docs/` sind keine neue Add-on-Version.
## 1. Verifizierter Versions-, GitHub- und Gerätestand

| Bereich | Bestätigter Stand | Noch offen |
| --- | --- | --- |
| **Release-Basis** | **XCMate 0.1.29.4** in `main`; PR [#55](https://github.com/artattakk-creator/kodi-noodleprivate/pull/55) gemergt (Merge-Commit `8967070255b48ca5555cb48e7451f2c45b4684e5`). | Kein Beleg, dass alle neu gemeldeten EPG-/Navigationsfehler behoben sind. |
| **GS Media Repository** | Publish-Workflow [39616215954](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39616215954) erfolgreich; `addons.xml` listet XCMate **0.1.29.4**; Repository **1.7.0**. | Keine neuen produktiven Paketänderungen ohne Abnahme. |
| **Android** | Nutzer hat **0.1.29.4** installiert und vollständiges **EZ Maintenance+**-Backup erstellt. XCMate-Hauptmenü, Live-TV, Filme, Serien und EPG sind zugänglich. | EPG-Dubletten, schwaches Matching und Back-Navigation sind real gemeldet; Aufnahme/Downloads nicht real funktionsgeprüft. |
| **0.1.30** | Draft-PR [#50](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50), Branch `feat/xcmate-space-premium-installer`, offen/nicht gemergt, Head bei diesem Snapshot `e889b259773717aac7c7b222a02bed8e6ed4aa7d`; **98 Space-Premium-Originalbilder**, generischer Theme-Installer und getrennte Test-ZIPs. | PR #50 basiert auf älterem Integrationsstand und muss die später gemergten **0.1.29.4**-Fixes berücksichtigen. **Android-IR-/UI-/Theme-Abnahme offen**; historisch 509/509 CI-Tests nur für damaligen PR-Zustand. |
| **Dokumentation** | Frühere Protokolle, Testpläne und Codeberichte in `docs/XCMate/`. | Diese Übergabe bei neuen Testergebnissen fortschreiben. |

**Aktueller regulärer Updatepfad:** GS Media Repository über Kodi; nur XCMate 0.1.29.4 ist hier als veröffentlichter Stand bestätigt. Manuelles Paket: https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.4.zip . Kein Draft-PR-Paket als veröffentlicht bezeichnen.

**Freeze / Rollback:** Backup/Portale/Accounts, aktiviert/deaktivierte Sendergruppen, Startgruppe/-sender, Favoriten, EPG-Quellen und Zuordnungen, Resume-Positionen, gewohnte Live-TV-IR-Belegung und andere Kodi-Add-ons strikt erhalten. Niemals zum Test Kodi deinstallieren, Add-on-Daten pauschal löschen, Produktiv-ZIPs überschreiben oder eigenmächtig Releases auslösen.

## 2. Verbindliche aktuelle Arbeit – offene Issues

| Priorität | Issue | Auftrag / tatsächlicher Status |
| --- | --- | --- |
| **P0** | [#58 – EPG-Dubletten](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58) | Kurz-EPG-ProSieben: „Two and a Half Men“ **15:06–15:36** und **15:07–15:36**, Quelle **Xtream Kurz-EPG**; auch Mehrfachanzeigen; gezielt normalisieren/deduplizieren ohne echte Folgen zu verschlucken. Kodi-GUI-Arbeit aus Worker-Callbacks prüfen. **Offen**. |
| **P0** | [#59 – Zurück-Navigation](https://github.com/artattakk-creator/kodi-noodleprivate/issues/59) | Back aus EPG/Medien soll zuverlässig zur XCMate-Hauptübersicht führen, nicht EPG erneut laden oder Add-on verlassen; Navigation/Fokus ohne neue Imports bewahren. **Offen**. |
| **P0** | [#60 – Sender-EPG-Matching](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60) | Realer Stand: **288/2.764 = 10,4 %** XMLTV-Matches (242 Name, 46 Anbieter-ID, 0 manuell), 2.476 ungemappt. EPGShare01 DE und Kaimandura DE READY; Anbieter-XMLTV WAITING ist **kein Beweis für Nichtverfügbarkeit**. DACH-Varianten, HEVC/HD-Suffixe konservativ zuordnen, manuelles Matching und Quellenstatus. **Offen**. |
| **P1** | [#57 – Programmzeitschrift](https://github.com/artattakk-creator/kodi-noodleprivate/issues/57) | Kurz-EPG (im laufenden Player) **trennen** vom Langzeit-EPG (= **XCMate-Programmzeitschrift**, horizontaler Zeitraster). Links fixierte Senderlogos/-namen, rechts synchronisierte Zeitachse/Jetzt-Linie/Programmdauer, Details, TV-Highlights, Filter, EPG-Zuordnung per Kontexttaste/lang OK. Ziel 7–10 Tage **bei echter Quellenabdeckung**. TMDB-Bilder/Metadaten und Catch-up-Markierung (siehe unten). **Geplant, nicht fertig abgenommen**. |
| **P1** | [#64 – universelle Fernbedienung](https://github.com/artattakk-creator/kodi-noodleprivate/issues/64) | **Rot/Grün/Gelb/Blau** sowie weitere empfangene Tasten frei mit XCMate-Aktionen belegen: Taste auswählen/anlernen -> Aktion wählen -> speichern/testen. Box-/Fernbedienungsprofile, Export/Import, kontextabhängige Aktionen, sichere Fallbacks; bestehendes Live-Mapping unangetastet. **Geplant**. |
| **P1/P2** | [#62 – Aufnahme + Auto-Umschalten](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62) | EPG-Timer für Erinnerung, automatischen Senderwechsel, geplante/Sofortaufnahme; Aufnahme-Engine auf Android tatsächlich lauffähig machen; **Sender A im Hintergrund aufnehmen und gleichzeitig Sender B im normalen EINZIGEN Live-Videoplayer ansehen/wechseln**. Unabhängiger Recorder von Kodi-Videoplayer; USB/HDD/SMB-Speicher und Abbruchbehandlung. **Geplant, Geräteaufnahmetest offen**. |
| **P2** | [#63 – VOD-/Seriendownloads](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63) | Film, Episode/Staffel berechtigt auf benutzergewähltes dauerhaftes USB/HDD/SMB-Ziel speichern; Queue, Resume soweit unterstützt, Status, Offline-Wiedergabe, Neustart und Disk-Fehler. **Geplant**. |
| **Später / kein aktiver Auftrag** | [#65 – X-Wall/Oberflächen](https://github.com/artattakk-creator/kodi-noodleprivate/issues/65) | Optionale Integration anderer Add-ons/Netflix-artiger Widget-Oberflächen erst nach Kernarbeiten; „X-Wall“ konkrete Kodi-ID/Integration ungeklärt. Keine Umsetzung in laufendem 0.1.30-Auftrag. |
| **Ausdrücklich gestrichen** | [#66 – Multiview](https://github.com/artattakk-creator/kodi-noodleprivate/issues/66) | **Geschlossen: not planned.** Kein PiP, Split-Screen, Mehrfach-Videofenster, Android-Multidecoder oder Multi-Player-Helper. Nicht aus älteren Beschreibungen wieder einplanen. |

Weitere bereits bekannte Bugs unabhängig betrachten, z. B. [#40](https://github.com/artattakk-creator/kodi-noodleprivate/issues/40) verzögerter Stop/Spinner und ältere #37/#38. Keine unbelegte Geräteursache behaupten.

## 3. Festgelegte Produktentscheidungen

### Kurz-EPG, Programmzeitschrift, Metadaten
- **Kurz-EPG:** während laufender Wiedergabe durch OK/Links: Senderlogo, Jetzt/Gleich, Uhrzeit, Fortschritt; lokal und sofort, keine neue HTTP-Anfrage pro IR-Taste; Xtream-Kurz-EPG als asynchroner Fallback.
- **Langzeit-EPG = TV-Programmzeitschrift:** eigener XCMate-Menüpunkt, mehrere Tage, horizontale synchronisierte Zeitleiste, Details, Sendungsbilder, Such-/Filterfunktionen und Aktionen.
- **EPG-Datenquellen:** Xtream-Provider, EPGShare01 DE/AT/CH, Kaimandura und weitere ausdrücklich konfigurierte XMLTV-Feeds. Mappings und Quellenpriorität erhalten. Im `xmltv_stream.py` werden u. a. Titel, Beschreibung, Kategorie, Icon, Episode, Rating gelesen, aber die aktuelle `guide_store.py`-Persistenz speichert nur einen Teil – Schema nichtdestruktiv erweitern.
- **TMDB** ist für das **nichtkommerzielle XCMate** primäre Quelle für Filme/Serien: Poster, Backdrops, Episoden-Stills, Beschreibungen, Cast, Staffel/Folge, Genres/Rating, soweit vorhanden. Nutzungsbedingungen/Attribution, lokale Token-Speicherung, kein falsches automatisches Matching. TMDB liefert **keine linearen Sendezeiten**. TVmaze optional nach Lizenzprüfung; keine unlizenzierte TV-Spielfilm-Übernahme.

### Catch-up / Restart-TV
- Nutzer meldet tatsächlich vorhandene Catch-up-Sender des IPTV-Anbieters.
- Xtream `get_live_streams` kann `tv_archive` und `tv_archive_duration` enthalten. `xtream.py` besitzt **bereits** `catchup_url()`.
- Im aktuellen `library_index.py` lässt `FIELDS` diese Catch-up-Felder weg; **Erkennung/Anzeige ist noch nicht durchgängig implementiert**. Catch-up-Metadaten aus Xtream/M3U sicher übernehmen, Senderkennzeichen/Rückspul-Icon, Archivdauer und Filter; tatsächliche Archivwiedergabe separat testen.
- Für vergangene Sendungen sind historische EPG-Daten erforderlich; aktueller Langzeit-Cache konzentriert sich auf zukünftige Einträge. Catch-up-Flag ≠ garantiert funktionierende Wiedergabe.
- Server-Catch-up benötigt **keine lokale FFmpeg-Aufnahme**. Nicht mit lokalem Timeshift verwechseln.

### Aufnahme ohne Multiview
- **Endgültige Vorgabe:** Sender A aufnehmen, Sender B ansehen; der Nutzer hat mehrere gleichzeitige Provider-Streams bereits selbst getestet. Die tatsächliche Android-Aufnahmeengine und Dateiausgabe sind weiterhin separat abnahmebedürftig.
- `guide_timers.py` kann aktuell nur erinnern, **nicht** automatisch umschalten/aufnehmen. `recordings.py` hat FFmpeg-basierten Sofortaufnahme-Code, `recording_probe.py` prüft dessen CLI-Verfügbarkeit – beides ist **kein nachgewiesenes Aufnahmebackend auf Android**. In `home_menu.py` besteht eine Aufnahme-Verzeichniswahl mit Schreibprobe.
- Kein generischer „FFmpeg-ZIP herunterladen und ausführen“-Ansatz auf Android versprechen; **VLC-Installation stellt XCMate nicht automatisch eine FFmpeg-CLI zur Verfügung**. Geeignete Aufnahmeengine/Helper-App oder direktes Schreiben kompatibler ungeschützter Streams untersuchen. Store-Link erst für verifizierte kompatible App.
- Recorder und sichtbarer Player brauchen **unabhängige Lebenszyklen**. Zapping von B nach C, EPG-Benutzung oder VOD-Browsing darf Recorder A nicht stoppen. Aufnahme nur auf nachweisbar schreibbarem Speicher mit Status/Fehleranzeige; kein automatisches Aufwecken einer schlafenden Box zusagen.
- Im EPG getrennte Aktionen: „Jetzt ansehen“, „Automatisch umschalten“, „Aufnahme planen“, „Jetzt aufnehmen“ bei realer Unterstützung, „Erinnern“, „Merken“. Event-Zeitplan/UTC/DST, Konflikte und fehlende Funktionen klar behandeln.

### Bedienung, Speicherung, Architektur
- `remote_profiles.py` kennt aktuell nur sechs lernbare Befehle; allgemeingültigen Tasten-/Farbbutton-Aktionskatalog einführen. Android-System-/Home-/Lautstärketasten und andere Kodi-Add-ons schützen; `remote_control.py` / `remote_bridge.py` besitzen eigenes Keymap-/Session-Gating.
- VOD-Episode und Film nur bei technisch/rechtlich unterstützten Quellen herunterladen, keine DRM-Umgehung, `.part`-Datei/Resume/atomare Übernahme und sicheres Offline-Abspielen.
- **0.1.30 / Space Premium:** Theme-Installer und 98 Originalgrafiken aus Draft-PR #50 bewahren; unabhängige Core-/Theme-Pakete; nie die veröffentlichte 0.1.29.4 automatisch ersetzen. Andere Medienquellen/volle Medienzentrale erst nach Fertigstellung aktueller Arbeiten.
- XCMate ist **nichtkommerziell**; Lizenz-/Attributionsbedingungen von TMDB, TVmaze und Dritt-EPG weiterhin einzeln einhalten.

## 4. Prioritäten, Arbeitsweise und Testabnahme

1. **Zuerst aktuelle Branches/Commits/Issues und alle Issue-Kommentare live prüfen.** Dieses Dokument ist Snapshot, keine Zusicherung über spätere Codex-Ergebnisse.
2. **Phase P0:** #58 Dubletten, #59 Navigation, #60 Matching, GUI-Thread-/Performance-Sicherheit. Wenn sinnvoll gesonderte **0.1.29.5 Testversion** in Draft-PR; 0.1.29.4 niemals überschreiben.
3. **Phase P1:** #57 horizontaler Langzeit-Guide/Kurz-EPG-Trennung, Catch-up-Badges, TMDB/Detailpanel, manuelles Mapping; #64 universelle Tastenprofile; vorhandenen PR #50 **mit neuem main/0.1.29.4 synchronisieren**, ohne Grafiken zu verlieren.
4. **Phase P2:** #62 Auto-Umschalten und funktionierender unabhängiger Recorder mit **Aufnahme A + Wiedergabe B**; #63 Medien-Downloadmanager. Wo Android-Backend noch fehlt, transparent getrennt in Draft/Folgeversion planen.
5. **Nicht jetzt:** #65 weitere Oberflächen/Medienquellen. **Niemals:** #66 Multiview/PiP/Split.
6. **Testmatrix:** Python-Tests, Kodi-21-API-Kompatibilität, SQLite-Schemamigration, hoher Senderbestand (2.764), XMLTV-Multiple-Feeds, schwache/offline Verbindung, 720p/1080p/Estuary/BINGIE, echte IR-Tasten, Android-Speicherberechtigungen/USB/SMB, EPG-/Aufnahme-Timer und unabhängige Wiedergabe/Recorder-Sessions.
7. **Strikte Statussprache:** „im Code“, „automatisiert getestet“, „Android real getestet“, „veröffentlicht“ getrennt führen. Keine Erfolgsmeldung zu ungetesteten Recordings, Catch-up-Playback, Downloads oder Multi-Sessions.
8. **Ergebnis jeder Codex-Etappe:** Integrationsmatrix je Issue (vorhanden/neu/fehlt), betroffene Dateien, Tests/Fehler, neue Draft-PRs, getrennte ZIPs mit SHA-256, Android-Testanleitung, Blocker, Release-Empfehlung. **Kein Merge/Release/Produktivindex ohne explizites Ja des Nutzers.**

### Wichtige Links
- [Codex-Folgeauftrag vom 21.10.2026](CODEX_FOLGEAUFTRAG_2026-10-21_DE.md)
- [PR #50 – 0.1.30 Draft/Space Premium](https://github.com/artattakk-creator/kodi-noodleprivate/pull/50)
- [PR #55 – 0.1.29.4 gemergt](https://github.com/artattakk-creator/kodi-noodleprivate/pull/55)
- [Hotfix 0.1.29.4](HOTFIX_0294_SETUP_SCAN_SAVE_DE.md)
- [Android-Testplan 0.1.29.4](ANDROID_TESTPLAN_0294_SETUP_SCAN_SAVE_DE.md)
- [Historische große Projektübergabe](PROJECT_HANDOFF_DE.md)
- [Historischer neuer-Chat-Block](NEW_CHAT_COPY_BLOCK_DE.md)

## 5. Kurze Übergabe für einen neuen Chat

> Wir entwickeln **XCMate** (Kodi 21.3/Android, Titan BINGIE MOD), Repo https://github.com/artattakk-creator/kodi-noodleprivate, ID `plugin.video.xtreammate`. **Main/GS-Media-Repository enthält 0.1.29.4** nach Merge PR #55 und erfolgreichem Publish. **0.1.30 / Space Premium** liegt in **Draft-PR #50**; Android-Abnahme offen und 0.1.29.4-Fixes müssen eingebunden werden. **Zuerst #58 EPG-Dubletten, #59 Back, #60 XMLTV-Matching**, dann #57 horizontale Programmzeitschrift/kurzes In-Player-EPG/TMDB/Catch-up-Kennzeichnung, #64 freie Farbtasten-/Fernbedienungsprofile, #62 automatische Umschaltung und **Sender A aufnehmen während Sender B läuft**, #63 USB/HDD/SMB-Film- und Episodendownloads. **#65 X-Wall spätere Idee; #66 Multiview/PiP/Split ausdrücklich gestrichen.** EZ Maintenance+-Backup von 0.1.29.4 existiert; kein Merge/Release/Update ohne Freigabe. Aktuellen GitHub-Stand vor neuen Maßnahmen prüfen. Verbindliche Detailübergabe: [PROJEKTSTATUS_UEBERGABE_2026-10-21_DE.md](PROJEKTSTATUS_UEBERGABE_2026-10-21_DE.md).
