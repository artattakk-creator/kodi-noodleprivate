# XCMate 0.1.27 – verbindlicher Codex-Entwicklungsauftrag: schlankes Hauptmenü, Einstellungen und gruppenbasierter Langzeit-EPG

**Stand:** 19.10.2026. **Quelle:** expliziter Nutzerauftrag direkt nach erfolgreichem Android-TV-Update auf XCMate `0.1.26`.  
**Repository:** `artattakk-creator/kodi-noodleprivate`; Basis aktuelles `main`; Kodi-ID **`plugin.video.xtreammate`** behalten.  
**Veröffentlichung:** produktiv **0.1.26**; `0.1.27` ist eine **Zielversionsnummer, noch kein Release, kein Code-Fix und keine Geräteabnahme**.  
**UI-Referenz:** Bedienkonzept von **TiviMate** als funktionales Vorbild, aber **XCMate-eigenes** Design, Symbole, Texte und Code. Keine Kopie fremder App-Dateien, Grafiken oder proprietärer UI-Ressourcen.

## 0. Aktueller Realgerät-Stand / Freeze

- Nutzer hat **0.1.26 inzwischen über den normalen GS Media Kodi Repository-Updateweg installiert** und nach erstem Gebrauch positiv bestätigt: „Es hat auf jeden Fall funktioniert ... das ist jetzt wirklich geil. Es funktioniert.“
- Die aktuelle Infobar / Live-TV-Overlaygestaltung und dreistufige Bedienlogik sind die **bewahrenswerte Grundlage**. Bisher **keine Einzelmessung** mit zehn Links-/EPG-/Stop-Zyklen und keine Fotodokumentation des vollständigen 0.1.26-Abnahmeplans. **Nicht** „alle 0.1.26-Android-Tests bestanden“ behaupten.
- **Keine unbeabsichtigten Änderungen** an Service/Overlay, Kodi-Omega-Keymap, Player, Fernbedienungs-Fokus oder XCMate-Farben. Kein Autoplay beim Betreten des Menüs, wenn dies nicht explizit eingestellt ist. Bestehende Portal-IDs, Accounts, Favoriten, Gruppen, EPG-Zuordnungen, Cache und lokale Daten erhalten.
- Die frühere P0-Links-Bedienung wurde in 0.1.26 bearbeitet; die jetzt gewünschte **Links-Navigation im separaten großen EPG** ist eine eigene zusätzliche GUI-Anforderung. Nicht mit dem bereits funktionsfähigen Overlay verwechseln.

## 1. Exakte XCMate-Startübersicht – nur diese sechs Haupteinträge

Nach Öffnen von XCMate mit mindestens einem aktivierten Portal zeigt die **oberste Startseite genau diese sechs Navigationspunkte in dieser Reihenfolge**, keine technischen Debug- oder Konfigurationseinträge davor/dazwischen:

```text
                     XCMate

    ▶   Startkanal
    ▣   Live-TV
    ▦   EPG – Programmführer
    ▷   Filme
    ▷   Serien

    ⚙   Einstellungen
```

Das Diagramm bezeichnet Funktionen, **keine Unicode-Glyphen für die tatsächliche Kodi-Oberfläche**. Eigene PNG-/Skin-kompatible Assets nutzen. „Einstellungen“ visuell mit deutlichem Abstand als untere eigene Rubrik. UI edles Grau/Slate, passende XCMate-Icons; gut sichtbar in BINGIE MOD, auf Android-TV, mit Back/Fokus. Keine Kopie von TiviMate-Assets.

| Haupteintrag | Verhalten |
|---|---|
| **Startkanal** | Gespeicherten Startsender **direkt abspielen**, ohne das Startsender-Setup statt dessen zu öffnen. Fehlt ein gültiger Startsender, klaren Dialog mit Weg zu `Einstellungen → Startkanal & Startgruppe` zeigen; keine falsche Stream-URL verwenden. |
| **Live-TV** | Sendergruppen und Senderliste des aktiven Portals öffnen, wie Kodi-Stand erlaubt. Aktuelle Gruppe/aktuell laufender Sender sinnvoll vorausgewählt; Live-Overlay nicht durch Menüumbau regressieren. |
| **EPG – Programmführer** | Eigenen **großen gruppenbasierten EPG-Browser** öffnen (siehe §§3–4), nicht nur einen Textviewer der nächsten 3–48 Sendungen. Gruppe des eingestellten Startkanals beim Erstaufruf als **Initialgruppe** verwenden (wenn verfügbar/aktiv), nicht willkürlich „alle Sender“. |
| **Filme** | **Eigene Film-Landingpage:** horizontale `Neu hinzugefügt`-Posterreihe (alle nachvollziehbar neuen Titel lazy durchscrollbar), darunter `Filme / Kategorien` → erste aktivierte Filmgruppe, linke Gruppenleiste, rechts einklappbare vollbreite Posterwand. Cover OK → große Film-Detailansicht mit Backdrop, Metadaten, Abspielen/Neustart/Fortsetzen, Favoriten an/aus, validiertem YouTube-Trailer. **Verbindlicher Zusatzauftrag:** [Film- und Serien-UX](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md). Bestehende Filme/Neueste/Suche erhalten. |
| **Serien** | **Eigene Serien-Landingpage** mit horizontaler Neuheitenreihe, `Serien / Kategorien` und erster aktivierter Gruppe; links Gruppenleiste, rechts Posterwand (Rechts maximiert/Links Gruppen); Serien-Detailansicht mit Backdrop, Metadaten, Favoriten, Trailer, Staffeln/Folgen, Fortschritt/Fortsetzen/Weiterschauen gemäß [SERIES_PROGRESS_SPEC_DE.md](SERIES_PROGRESS_SPEC_DE.md). **Verbindliche Umsetzung:** [Film- und Serien-UX](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md). |
| **Einstellungen** | Klares neues Untermenü, siehe §2; alle technisch relevanten bisherigen Optionen bleiben erreichbar, werden aber aus Startübersicht entfernt. |

**Ersteinrichtung und mehrere Portale:** Ohne Portal wie bislang „Einrichtungsassistent“ anbieten (und Einstellungen/Account hinzufügen), statt sechs unbrauchbare Menüpunkte zu zeigen. Bei mehreren aktiven Portalen aktiven/Standard-Account sicher auswählen bzw. gespeicherte Auswahl verwenden; **die Startseite soll trotzdem die sechs Hauptpunkte** zeigen, nicht ausschließlich eine Portalliste. Accountwechsel im neuen Untermenü. Getrennte Startsender/-gruppe und Daten je `portal_id` respektieren. Bei nicht unterstütztem VOD/Serienformat einen verständlichen Hinweis anzeigen oder die Kompatibilität pro Portal dokumentieren; keine heimliche Löschung der Navigation.

**Technischer Iststand:** `main.py::_root()` verzweigt bisher nach 0/1/mehreren Portalen; `_show_portal_home()` enthält zahlreiche technisch/diagnostische Einträge, die aktuell das Hauptmenü überladen. Nicht alles löschen – Navigation **umstrukturieren**. Bisher `_maybe_autoplay_start()` beim Eintritt in eine Portalstartseite nur unter ausdrücklicher Einstellung/Diagnosemodus; die neue reine Hauptmenüanzeige darf nicht selbst einen Sender starten.

## 1a. VERBINDLICHER ZUSATZAUFTRAG: Netflix-/BINGIE-MOD-artige Filme und Serien

**NEUE Nutzeranforderung 19.10.2026:** Die sechs Hauptmenüpunkte bleiben, aber Filme und Serien öffnen nicht sofort eine einfache Kodi-Kategorieliste. Stattdessen **zuerst eine Landingpage mit horizontal scrollbarer Neuheitenreihe**, darunter `Filme/Kategorien` bzw. `Serien/Kategorien`; dann **erste aktivierte Gruppe**, links ein-/ausblendbare Gruppen-Navigation und rechts mittige/vollbreite Posterübersicht. Cover OK öffnet eine bildstarke **Film- bzw. Seriendetailseite** mit echten Titeldaten, Bewertung/Laufzeit soweit vorhanden, Titelbild/Backdrop, Filmstart/Neustart/Fortsetzen, Medienfavorit ein/aus und validiertem YouTube-Trailer. Serien zusätzlich Staffeln/Episoden und Weiterschauen.

**Maßgebliche vollständige technische und Design-Spezifikation:** [CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md). **Diese ergänzt und präzisiert ausdrücklich §1, §4, §6 und §7 des Hauptauftrags.** Insbesondere genügt eine gewöhnliche Kodi-Verzeichnisliste **nicht** für die geforderte horizontale Rail und den einklappbaren Gruppenbereich: Kodi-`WindowXML/Dialog` mit sichtbarer Android-TV-Fokusnavigation prüfen. `latest_media.recent_entries(limit=50)`, `metadata_views.py`, `get_vod_info/get_series_info` und bisherige Kodi-Player-Routen sind Startpunkte, **noch kein Nachweis der gewünschten UI und Resume-/Favoritenfunktionen**. Keine Netflix-/TiviMate-Bilder/Code kopieren, kein Live-TV regressieren.

## 1b. NEUE VERBINDLICHE ERGÄNZUNG – Freeze, Suche, BINGIE MOD Widgets (19.10.2026)

**Zusätzliche Anforderung:** [CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md](CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md) vollständig lesen und umsetzen. **Dies erweitert §§1, 1a, 4, 6 und 7**. XCMate **0.1.26-Live-TV-Infobar, dreistufiges OSD, Links-/Gruppensteuerung sowie alle bestehenden Kodi-Playerfunktionen sind FREEZE**; nur additive UI-/Such-/Widget-Module und nachgewiesene minimale Kompatibilitätsänderungen. Bestehende Portal-/Profil-/Medien- und EPG-Daten nicht löschen.

**Filme/Serien:** echtes großes Backdrop/Fanart/Hintergrundposter für den fokussierten Titel, links fixierbare Gruppenleiste, Rechts erweitert Postergrid auf gesamte Breite, Links **am linken Gridrand** öffnet Gruppen wieder, ohne Position/Fokus zu verlieren. Separate Film-/Seriendetailansichten mit echten Laufzeiten/Bewertungen.

**Gemeinsame Suche:** `LIVE-TV (N)`, `FILME (N)`, `SERIEN (N)` gleichzeitig sichtbar für dasselbe Suchwort, unabhängig paginierte tatsächliche Trefferzahlen und korrekter Detail-/Live-Playback-Einstieg. Ein globaler Such-Shortcut kommt **innerhalb** der sechs Startpunkte/Medienseiten zum Einsatz, **kein siebter Hauptmenüpunkt**. [Issue #25](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25).

**BINGIE-MOD-Startseite:** drei über den regulären Kodi-Skin-Widget-Konfigurationsweg einrichtbare horizontale Reihen **Live aus Startkanalgruppe mit EPG → neueste Filme → neueste Serien**, fokussierbare echte ListItems und lokal vorgehaltener Cache. BINGIE MOD nicht automatisch überschreiben; Kodi-Addon liefert kompatible Widget-Routen plus getestete Einrichtung. [Issue #26](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26).

## 2. Einstellungen nach TiviMate-Bedienlogik als eigener Menüzweig

**Neue oberste Einstellungen-Kategorien** (klar lesbar, Back-Stack und eindeutiger Fokus):

1. **Accounts & Portale** – vorhandene Xtream-/M3U-/Stalker-Zugänge listen; aktiven/Standard-Account wählen, anlegen/bearbeiten/deaktivieren/entfernen mit Bestätigung; Typ, Anzeigename, URL-Host und ggf. Status/Ablaufdatum/Verbindungen **nur wenn vom Provider belastbar verfügbar**. **Passwörter, Tokens und vollständige URLs mit Credentials standardmäßig maskieren**; nie in Debug-/EPG-/Gerätefotos. Bestehende `xtream_account`, `stb_account`, `m3u_account`, `portal_manager` wiederverwenden.
2. **Startkanal & Startgruppe** – Sender/Gruppe pro aktivem Portal wählen; optional Autostart beim XCMate-Eintritt **bewusster separater Schalter**, bestehende Sicherheits-/Diagnose-Pause respektieren. Kein verstecktes Einschalten.
3. **EPG** – Quellen/URLs (geschützt), automatische Aktualisierung, Quellpriorität, Importstatus, letzter Erfolg/Fehler, XMLTV-/Xtream-Zuordnung, Mapping, Datenhorizont (7 oder optional 10 Tage **nur falls vorhanden**), bevorzugte Zeitzone über Kodi-Zeitzone, Cache. Bereits existierende `epg_sources` und `epg_status` verlinken, nicht duplizieren. Statusanzeige darf Fehler nicht als Erfolg deklarieren.
4. **Sendergruppen & Favoriten** – Live-TV-/Film-/Seriengruppen pro Portal aktivieren/deaktivieren, sortieren, Startgruppe setzen; Favoriten und Suche in passenden Katalogen erhalten. Keine Deaktivierung der laufenden Sendergruppe ohne klare Rückmeldung.
5. **Fernbedienung & Tasten** – **bewährtes Kodi-21-Nativprofil bleibt Standard**. Optionaler „Fernbedienung anlernen“-Assistent für unterschiedliche Android-/TV-Remotes; Tastenwerte anzeigen, auf Duplikate prüfen, Test-/Zurücksetzen-Option mit Bestätigung, Profil sichern und nach Neustart prüfen. Erweiterte **Fernbedienungsdiagnose und Service/Poup-Test** nur unter **Erweitert / Diagnose**, nicht Hauptmenü. Kodi-globale Fallback-Keymap standardmäßig **AUS** und nur nach expliziter Entscheidung.
6. **Player & Wiedergabe** – Qualität, Player-Verhalten, Timeshift (falls verfügbar), Audio-/Untertitel-Defaults, Infoleisten-Ausblendzeit, ggf. Puffer- und Seek-Fähigkeit; bestehende Kodi-Player-Funktionen nutzen. Keine Kodi-weiten Änderungen.
7. **Aufnahmen & Speicher** – **Aufnahmeverzeichnis auswählen/ändern/anzeigen**, freier Speicherplatz und Schreibbarkeit (Android-Berechtigungen/SAF und Kodi xbmcvfs), Standardpfad, Vor-/Nachlauf für spätere EPG-Aufnahmeplanung, Verwaltung bestehender Aufnahmen; laufende/sichere Aufnahmefähigkeit prüfen. `settings.xml` enthält bereits `recordings_folder` vom Typ `folder`; `recordings.py::_rec_dir()` liest diesen Wert. **Diesen bestehenden Setting-Key unverändert wiederverwenden**; keinen zweiten konkurrierenden Aufnahmepfad erfinden. Ohne FFmpeg/PVR-Aufnahmeengine keinen funktionsfähigen Timer vortäuschen.
8. **Darstellung & Sprache** – aktuelle XCMate-Farben, Logo-/Zeilengröße, Sprache/Filter, optional künftige Farbauswahl; keine Änderungen am installierten Kodi-Skin ohne ausdrückliche Zustimmung.
9. **Wartung & Diagnose** – Portal/EPG-Refresh, Cache-Status/-Löschen nach Bestätigung, Dienstzustand, TV-Fernbedienungsdiagnose, Popup-Probe und Debug-Modus; nur hier die bisherigen Test-Menüs sammeln. Nie still Zugangsdaten/EPG-Zuordnungen löschen.
10. **Über XCMate & Lizenzen** – Version, Build, Quelle, Herkunftshinweise und Third-Party-Lizenzen. **Bestehende GPL-/Fork-Attribution nicht entfernen**; Rechte-/Lizenzkonflikt ist in [Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19) offen und separat rechtlich zu klären.

Untermenüs dürfen für Vielnutzer kompakt sein, ohne dass man mit fünf Eingaben zu einer Grundfunktion navigieren muss. Bestehende Methoden/Aktionsrouten soweit möglich beibehalten, nur UI-Einstieg reorganisieren. **Migrationsverträglichkeit** (u.a. bestehende `settings.xml`-IDs) strikt prüfen; keine Profildaten verlieren.

## 3. P1 – eigenständiger großer TV-EPG: gruppenbasiert und remote-fähig

**Nutzerziel:** Ein TiviMate-ähnlicher **vollflächiger Mehrsender-EPG**, der aus dem Hauptmenü sofort geöffnet werden kann, den aktuellen Sendergruppenbezug sinnvoll übernimmt und Tagesprogramm über **7 bis optional 10 Tage** anbietet – **nicht** die bisherige kurze Textvorschau.

**Initialisierung / Gruppe:**
- Bei erstmaligem EPG-Start **die Sendergruppe des gespeicherten Startkanals** des aktiven Portals auswählen (aus Stream-ID / gespeicherter Startgruppe ableiten, ggf. Category-ID prüfen).
- Wenn Startkanal fehlt, gelöscht ist oder seine Gruppe deaktiviert: gespeicherte Startgruppe → zuletzt im EPG gewählte gültige Gruppe → erste aktivierte Gruppe als klar dokumentierte Fallback-Reihenfolge. Eine Benutzerentscheidung zur aktuellen Gruppe während laufender EPG-Session respektieren; nicht bei jedem Back-Refresh zur Startgruppe springen.
- **Links im EPG:** Gruppen-Navigation öffnen; Gruppenliste links mit sichtbarem Fokus; OK auf andere Gruppe wechselt EPG-Kanalzeilen; Rechts/Zurück zurück zur EPG-Timeline, ohne Video abzubrechen.
- **Hoch/Runter** Senderzeilen; **Links/Rechts innerhalb der Timeline** zwischen Ereignissen/Zeiten navigieren, wobei ein klarer Steuerbereich für Gruppenwechsel existieren muss (z.B. Links am linken Rand oder explizit separat fokussierbare Gruppenleiste). Keine Kollision, bei der Links nie die Gruppen erreicht. **OK** auf Sendung öffnet Detail und verfügbare Aktionen. **Zurück** eine Ebene zurück.
- Unterscheidung zwischen aktuell laufendem Sender, fokussiertem Sender und aktiver Gruppe. Favoriten/aktivierte Gruppen je Portal respektieren.

**EPG-Oberfläche:**
- Senderliste mit Logo/Name links, horizontaler Zeitachsenbereich rechts (z.B. Heute 18–24 Uhr), farbiger Jetzt-Marker, aktuelle Sendung mit Fortschritt; per Datum vor/zurück und Stunden scrollen. Alternativ ein barrierefreier tagweise aufgebauter Listenmodus; beide mit Kodi-21-kompatiblem Fokus.
- Datumsleiste „Heute / Morgen / ...“ bis **7 Tage standardmäßig**, optional 10; lokale Uhrzeiten inkl. Sommer-/Winterzeit und Sendungen über Mitternacht korrekt.
- Sendungszelle/Detail zeigt **echten** Titel, Beginn–Ende, Beschreibung, Sender und ggf. Bild/Episode/Genre. Beim laufenden Sender identische Now/Next-Werte wie in der eingefrorenen ersten OK-Infobar, kein abweichender Cache.
- Programme erscheinen nur, wenn die externe/Anbieter-EPG-Quelle echte Daten enthält. **Niemals fehlende Tage/Sendezeiten erfinden**. „Bis Datum X verfügbar“ / „Für diese Gruppe keine Daten“ klar anzeigen. Wenn EPG-Import fehlgeschlagen, Status/Quellenverwaltung verlinken. Kein EPG-Download pro Pfeiltaste.
- Sender oder Programm auswählen: „Jetzt ansehen“, „Erinnerung setzen“, optional „Bei Sendungsbeginn automatisch wechseln“, „Aufnahme planen“ **nur wenn ausführbar**. Details zu Scheduler-Hardware und Opt-in siehe §5 / [Issue #21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21).
- Performance mit 2.746 und 53.664 Sendern, jeweils nur sichtbare Zeilen und begrenzte Programmzeitfenster darstellen. Senderkatalogindex/EPG-Cache im Hintergrund, kein Netz im UI-/Tastenpfad.

**EPG-Datenarchitektur:** [PLAN_EPG_LANGZEIT_TIMER_DE.md](PLAN_EPG_LANGZEIT_TIMER_DE.md) ist gültig und verbindlich, insbesondere:
- Bestehende `epg_views.guide_for_channel()` liefert höchstens **48** Events; `epg_preview.status_lines()` zählt für Status **+48 Stunden**; dies sind unterschiedliche Grenzen. Bitte nicht beide einfach blind auf „10 Tage“ setzen.
- Für Langzeitdaten einen begrenzten diskbasierten, nach `(portal_id, epg_id, start_utc)` indizierten Speicher erwägen, mit atomaren Imports und migrationstauglicher Fallback-Lesefunktion; Now/Next-RAM-Snapshot für TV-Overlay getrennt **schnell** lassen.
- M3U/Xtream/Stalker, manuelle XMLTV-ID-Zuordnungen und Quellprioritäten respektieren, Quellenhorizont transparent. Alte validierte EPG-Daten bei fehlgeschlagener neuer Quelle nicht löschen.
- Kodi 21 SQLite-/Python-Kompatibilität sowie Timezone-/DST- und Fokus-/EPG-Matching-Tests.

## 4. Verbindlicher Navigations-/Menü-Ablauf (regulärer Normalfall)

```text
XCMate
 ├─ Startkanal          → TV beginnt sofort (nur durch diesen bewussten Klick)
 ├─ Live-TV             → Sender / Gruppen / TV
 ├─ EPG                 → große Übersicht: initial STARTKANAL-GRUPPE
 │    ├─ Links          → Sendergruppen → OK andere Gruppe
 │    ├─ Hoch / Runter  → Sender auswählen
 │    ├─ Rechts / Links → Sendung/Zeit navigieren (ohne Gruppensteuerung zu verschlucken)
 │    ├─ Tag vor/zurück → bis zu 7/10 echte EPG-Tage
 │    └─ OK Sendung     → Details / Ansehen / Erinnern / Aufnahme (falls unterstützt)
 ├─ Filme               → Landingpage: Neuheiten-Rail → Filme/Kategorien
 │                        → Gruppen links / Posterwand rechts → Film-Detail/Playback
 ├─ Serien              → Landingpage: Neuheiten-Rail → Serien/Kategorien
 │                        → Gruppen links / Posterwand rechts → Serien-Detail/Staffeln/Folgen
 └─ Einstellungen
      ├─ Accounts & Portale
      ├─ Startkanal & Startgruppe
      ├─ EPG (Quellen, Aktualisierung, Mapping, Status)
      ├─ Sendergruppen & Favoriten
      ├─ Fernbedienung & Tasten (Anlernen optional)
      ├─ Player & Wiedergabe
      ├─ Aufnahmen & Speicher (Aufnahmepfad)
      ├─ Darstellung & Sprache
      ├─ Wartung & Diagnose
      └─ Über XCMate & Lizenzen
```

**Einschränkung:** Das Schema ist ein **Produkt-/Bedienkonzept**, kein Hinweis darauf, dass Kodi die gewünschten Dialoge schon technisch unterstützt oder dass Langzeit-EPG/Aufnahme-Hardware existiert.

## 5. Aufnahmen, Erinnerungen und Fernbedienung – echte Machbarkeitsgrenzen

- Bestehende `reminders.py` zeigt Benachrichtigungen, jedoch noch keinen zuverlässigen automatischen Senderwechsel. Auto-Tune **nur nach Opt-in**; darf fremde Kodi-Wiedergabe nicht ungefragt unterbrechen. Wenn nicht implementiert, im EPG ein ehrlicher „Noch nicht verfügbar“-Status statt funktionslosem Button.
- Bestehende `recordings.py` startet **sofortige** FFmpeg-Aufnahmen; keine vollständige EPG-Timer-/Aufnahmewarteschlange. Auf Android FFmpeg/PVR-Engine, Speicherrechte, freier Platz und Provider-Grenzen separat prüfen. **Kein Start-/Aufnahmeversprechen** bei ausgeschaltetem TV. Das Einstellen eines Pfades allein macht Aufnahmen nicht funktionsfähig.
- Bei `Einstellungen → Aufnahmen & Speicher`: bisherige `recordings_folder`-Einstellung anzeigen/ändern; die gewählte Directory-Kennung und Schreibbarkeit über Kodi/xbmcvfs abfragen, Testdatei sicher aufräumen, ggf. schreibgeschützten Pfad ablehnen und Originaleinstellung bewahren. Externe Datenträger können ausfallen; Benutzer klar warnen. Keine automatische Neuformatierung oder Datenlöschung.
- Lernbare Fernbedienung **beibehalten und optional zugänglich machen**, gerade für verschiedene Hersteller. Bewährtes Kodi-native LEFT/RIGHT/OK aus 0.1.26 nicht durch fragile benutzerspezifische Map ersetzen. Zusätzliche gelernte Aliase dürfen den Standard nicht kapern; deduplizierte `onAction`/`onControl`-Ereignisse, keine globale Kodi-Keymap standardmäßig aktivieren.
- Defekte/alte „Test“-, „Popupprobe“-, Debug- und Expertenoptionen **aus Hauptmenü entfernen, aber Funktionalität hinter Erweitert/Diagnose beibehalten**, sofern weiter für Geräteanalyse benötigt. Erst nach dokumentiertem Ersatz und Tests Code löschen.

## 6. Arbeitsschritte und PR-Schnitt

**Zielversion für den nächsten nach Review veröffentlichbaren Meilenstein:** **XCMate 0.1.27**, ohne Behauptung, dass sie schon erstellt sei.

**Phase A – zuerst sichtbare Menüstruktur / Einstellungen (PR A):**
- `main.py::_root`, `_show_portal_home` sauber umstrukturieren; neue Actions `xcmate_home`, `settings_home`, `settings_account`, `settings_epg` etc. soweit technisch sinnvoll.
- Sechs Top-Level-Einträge; aktuelle Portalauswahl inkl. Startkanal, Gruppen/Favoriten/VOD/Serien-Erhaltung.
- Unterkategorien komplett, existierende Account-/EPG-/Remote-/Aufnahmeordner-Funktionen nutzbar; Diagnose versteckt unter Wartung.
- **Keine Regression** der funktionierenden TV-Infobar/dreistufigen Fernbedienung 0.1.26.
- Tests: Menüreihenfolge 6, 0/1/mehrere Portale, Back-Stack, PIDs/Portale, Startkanal direkt starten, Autoplay unverändert/opt-in, Settings ohne Datenverlust, Aufnahmeordner und Fernbedienungs-Anlerntest erreichbar, Kategorie ohne VOD, Other Add-ons/BINGIE MOD isoliert.

**Phase A2 – Film-/Serien-UX (eigener PR oder klar separat testbare Commits, zusätzlich zu Phase A):**
- Neue `movies_home`/`series_home`-Landingpages mit **horizontalen Neuheitenreihen** und gut fokussiertem `Filme/Kategorien`-/`Serien/Kategorien`-Übergang; volle Katalogreichweite via paginiertem Viewport, nicht nur 50 Titel.
- Gruppenliste links, Posterwand rechts, **Rechts klappt linke Leiste ein**, **Links am Coverrand klappt wieder aus**; Fokus und Back-Stack persistieren.
- Vollwertige Movie-/Series-Detailseiten mit echten Artworks und Metadaten, dynamischem Favoritenstatus, Movie-Resume, Trailer und Serien-Staffeln/Episoden/Progress. Nicht nur `xbmcgui.Dialog().textviewer`.
- Kodi-`WindowXML`-/Skin-Widgets auf **tatsächliche** Machbarkeit prüfen, strikte Kodi-21-Tests und echten Android-TV-Prototyp belegen. Ergänzung: [Spezifikation Filme/Serien](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md). Bei größerem Umfang in eigene PRs aufteilen statt scheinbar fertige 0.1.27.

**Phase B – großer EPG-Browser (PR B, bei großem Umfang als Folgekandidat oder klar separater Commit):**
- Eigenes EPG-Window/Dialog unter Kodi 21; Sendergruppe des Startkanals initial, Links öffnet Gruppen, Zeilen/Timeline per Remote, Tag-/Zeitnavigation und Programme bis tatsächlicher Feed-Horizont.
- Begrenzter indizierter Hintergrundspeicher und echte Quellen-/Zuordnungsdaten, nicht nur optisch generierte Demo-Sendungen. EPG-Zeitbereiche und aktive Gruppen via separate Unit-/Kodi-Mock-Vertragstests nachweisen.
- Bestehende XMLTV-Grenzen und Fehlerdiagnose schützen; auch ohne EPG-Daten muss Guide bedienbar sein und verständliche Leermeldung anzeigen.
- Wenn die Langzeitdatenbank nicht sicher in 0.1.27 fertig wird: **keinen Schein-7-Tage-EPG als fertig deklarieren**; Phase A regulär releasable vorbereiten, Phase B auf offenem PR dokumentieren.

**Phase C – EPG-Timer/Aufnahmeplanung (eigener P2-PR später):**
- Erst Android-Hardwarefähigkeiten dokumentieren, dann Scheduler/Timer mit echten Tests; keine FFmpeg-Abhängigkeit ohne Android-Nachweis. Separate Freigabe.

**Versionierung/Release:** Für fertigen 0.1.27-Kandidaten auf neuem Branch gegenüber `main` Manifest, Tests, ZIP und SHA vorbereiten. GitHub-CI muss vollständig grün sein. PR zu `main`; **keine eigene automatische Veröffentlichung** ohne ausdrücklichen Nutzerauftrag. Bei Freigabe nur reguläres GS Media Kodi Repository (`addons.xml`, .md5, ZIP) verwenden. Kein manueller Geräte-Reset, kein Verlust der Account-Daten.

## 7. Test- und Geräteabnahme (nicht durch Mocks ersetzen)

1. Android Kodi → XCMate öffnet **genau sechs** Punkte und keine Diagnoseliste im normalen Startmenü.
2. **Startkanal** spielt direkt; danach 1× OK kompakte Now/Next-Infobar, 2× OK Player, nochmal Runter Settings, Links öffnet Senderliste und nochmals Links Gruppen – kein Verlust der 0.1.26-Funktion.
3. **Filme/Serien:** Beide Landingpages öffnen mit horizontaler Neuheitenreihe und `Kategorien`-Einstieg; erste aktivierte Gruppe, Links Gruppen öffnen / Rechts Posterwand maximieren, echte Cover-Details mit Abspielen, Movie-Resume/Favoriten/Trailer und Serien-Staffeln/Progress. **Erst Kodi-Android-Test = PASS**, nicht ausschließlich Quellcode-/Mock-Erfolg. Detailabnahme im [Medien-UX-Auftrag](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md).
4. **EPG direkt aus Hauptmenü** öffnet große Übersicht mit tatsächlich passender **Startkanal-Gruppe**. Links → Gruppen, andere Gruppe OK → neue Senderspalte; Zurück → Guide. Kein Kodi-/Skin-Hänger.
5. Heute/andere reale Tage mit Uhrzeiten, Sendungen inkl. Mitternacht/DST, fehlende Quellen transparent. Bei 24-/48h-Feed Tage +3…+9 bewusst leer anzeigen; echte 7–10 Tage nur bei ausreichend langen Datenfeeds bestätigen.
6. **Einstellungen** öffnen 10 Kategorien. Account-Daten sinnvoll/maskiert; EPG-Quellen/Mappings und Sendergruppen funktionieren, gelernte Fernbedienung auffindbar, alternative Keymap aus.
7. Aufnahmeordner auswählbar, Speicherung und Schreibbarkeitscheck nach Kodi-Neustart; keine „Aufnahme läuft“-Behauptung ohne tatsächliche Engine. Bestehende Favoriten, Portale, EPG-Zuordnungen, VOD/Serien, Noodle Private und BINGIE MOD erhalten.
8. Fernbedienungsfokus und -aktionen mit mehr als einem Tastenprofil, 2.746 und 53.664 Sendern ohne unnötige synchrone EPG-/HTTP-Arbeit testen. Tests dokumentieren, Release erst nach Review.

## 8. Verweise für Codex

- [0.1.26-P0-Implementierungs-/Geräteplan](IMPLEMENTIERUNG_026_P0_REMOTE_OSD_DE.md)
- [0.1.25→0.1.26-Geräteübergabe](ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md)
- [Langzeit-EPG und Aufnahme-/Timer-Plan](PLAN_EPG_LANGZEIT_TIMER_DE.md)
- [Zentraler Release-Status](CODEX_STATUS_CURRENT_DE.md)
- [EPG-Issue #21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21), [EPG-Fehler #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [Fernbedienungs-P0 #20](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20), [Lizenz-Provenienz #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19).

## 9. KOPIERFERTIGER DIREKTAUFTRAG

> Öffne `docs/XCMate/CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md` im Repository `artattakk-creator/kodi-noodleprivate`. Lies die gesamte Anweisung, die aktuellen Code-Router und den 0.1.26-Android-Befund. Erhalte die inzwischen funktionierende TV-Infobar, drei Player-Ebenen und Links-Navigation. Implementiere die **schlanke XCMate-Startübersicht mit genau Startkanal, Live-TV, EPG, Filme, Serien, Einstellungen** und verschiebe technische Optionen in klar untergliederte Einstellungen (Accounts, Startsender, EPG-Quellen, Sendergruppen, lernbare Fernbedienung, Player, **Aufnahmeordner**, Darstellung, Wartung). Entwickle den **echten großen gruppenbasierten 7–10-Tage-EPG** als eigene Ansicht: Startgruppe des Startkanals zuerst, Links öffnet Sendergruppen, OK wechselt Gruppe, Sendungs-Timeline mit Tagen/Zeiten aus **realen** EPG-Daten. Benutze TiviMate als Interaktionsvorbild, aber ausschließlich XCMate-eigene Quelltexte/Assets. Falls der EPG-Index noch nicht fertig ist, dies transparent im PR abgrenzen; keine Schein-Abnahme und keine nicht funktionierende Aufnahmeplanung. Neuer Branch + Kodi-21-Regressionstests + CI + PR + Dokumentationsübergabe. **Nicht eigenständig nach main mergen/veröffentlichen**.
