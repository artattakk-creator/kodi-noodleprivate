> **Aktueller Einstieg (21.10.2026):** [Zentrale Roadmap](ROADMAP_AKTUELL_2026-10-21_DE.md) und [vollständige Issue-Integrationsmatrix](ISSUE_INTEGRATIONSMATRIX_DE.md). Produktiv **0.1.29.6**, Testkandidaten **0.1.29.7 / 0.1.30.1**, primäres Gerät **Kodi 21.2 / ARM32**. Die folgenden früheren Statusangaben bleiben unverändert als Historie; aktuelle Code-, CI- und Gerätebelege stehen in der zentralen Roadmap. Kein neuer Merge/Release freigegeben.

# XCMate 0.1.25 – realer Android-TV-Test und verbindlicher Codex-Folgeauftrag: dreistufiges OSD, Links-Taste, 7–10-Tage-EPG

> **Umsetzungsnachtrag 19.10.2026:** [0.1.26-P0-Kandidat](IMPLEMENTIERUNG_026_P0_REMOTE_OSD_DE.md)
> mit 250 bestandenen Tests und geprüfter Installationsdatei vorbereitet. Kein neuer Android-Test,
> kein Merge/Publish; produktiv bleibt 0.1.25. [P1/P2-Analyse](PLAN_EPG_LANGZEIT_TIMER_DE.md) separat.
> Der nachfolgende Gerätebefund/Arbeitsauftrag bleibt als unveränderte Ausgangslage erhalten.

**Stand:** 19.10.2026. **Quelle:** neue direkte Gerätemeldung des Nutzers nach Update auf XCMate 0.1.25. **Status:** Gerätebefund + Anforderung, **KEINE IMPLEMENTIERUNG UND KEIN RELEASE**. Kodi-ID `plugin.video.xtreammate` unverändert; weiter über GS Media Kodi Repository. Der vorherige 0.1.24-Dialogfehler ist für die beobachtete Szene überwunden. Der getrennte [Herkunfts-/Lizenz-Audit](CODE_ORIGIN_LICENSE_AUDIT_025_DE.md) ist nicht Gegenstand dieses Funktionsauftrags.

## 1. Harte Gerätedaten: bestätigt / nicht bestätigt / fehlgeschlagen

- **PASS, vom Nutzer ausdrücklich bestätigt:** **1× OK** über laufendem Live-TV zeigt die **kompakte untere Senderinfo mit JETZT/DANACH** im gewünschten XCMate-Stil. Inhalt/Optik als **Freeze** erhalten. „Das ist super gelöst, das sieht wirklich geil aus.“
- **Teilweise PASS:** **2× OK** zeigt eine weitere untere Steuerleiste; darunter lässt sich **„Weitere“** auswählen. Sie ist aber noch nicht die gewünschte echte Player-/Tape-Deck-Leiste, und die dritte Ebene soll ohne Umweg per weiterem **Runter** erreichbar sein.
- **FAIL:** **Links während laufendem TV-Vollbild** öffnet *nicht* die Sender-EPG-Liste. **Links in der Senderliste** öffnet *nicht* zuverlässig Sendergruppen. Nutzer vermutet grundsätzlich, dass der Links-Key verloren geht. Aufruf der Sender-/EPG-Ansicht über die **EPG-Schaltfläche in der unteren Leiste** funktioniert. **Keine numerische Kodi-Action-ID vom Gerät gesichert; exakten Fehlerpfad per neuer Tastendiagnose ermitteln.**
- **NO TEST RESULT:** 7–10-Tage-EPG, EPG-basierte programmierte Aufnahme und automatisches Umschalten per Erinnerung sind aktuell **Nutzeranforderungen**, keine unter 0.1.25 nachgewiesenen Gerätefunktionen. EPG-Now/Next der ersten Infobar bestätigt, **keine Belege für Verfügbarkeit jedes Kanals oder 7–10 Tage an EPG-Daten**.
- Keine neuen Videos/Logs im GitHub-Repository, nur protokollierte Nutzerbeobachtung. Aussagen aus 0.1.23/0.1.24 nicht mit diesem Test vermischen.

## 2. Verbindliche neue Bedienung: drei klar getrennte Ebenen

```text
                    LIVE-TV / VIDEO FULLSCREEN
                             │
                         1× OK
                             ▼
       ┌────────────────────────────────────────────┐
       │ EBENE 1: KOMPAKTE INFOBAR  [BLEIBT WIE IST] │
       │ Senderlogo · Sendername                     │
       │ JETZT: Titel · 20:15–21:45                  │
       │ ███████░░░ Fortschritt · noch X Minuten    │
       │ DANACH: Titel · 21:45                       │
       └────────────────────────────────────────────┘
                        │
                   OK oder RUNTER
                        ▼
       ┌────────────────────────────────────────────┐
       │ EBENE 2: PLAYER / TAPE-DECK                │
       │ ⏮  ⏪  ▶/⏸  ⏩  ⏭  ■                      │
       │ Zurück · Vor · Play/Pause · Live-Ende      │
       └────────────────────────────────────────────┘
                        │
                       RUNTER
                        ▼
       ┌────────────────────────────────────────────┐
       │ EBENE 3: ERWEITERTE EINSTELLUNGEN          │
       │ Bild · Ton · Untertitel · EPG              │
       │ Sendergruppen · Einstellungen             │
       └────────────────────────────────────────────┘
```

**Grafische Vorgabe:** Ebene 1 aus Version 0.1.25 **pixel-/layoutnah beibehalten**, nur funktionale Bugfixes; Stufen 2 und 3 optisch harmonisch anpassen. Icons als Kodi-kompatible PNG, Slate/Grau mit kontrastreichem Fokus und TV-Safe-Area; keine als Kästchen gerenderten Glyphen. Transport-Icons im Diagramm sind lediglich *semantische Platzhalter*, nicht die finale Fontwahl.

**Exakte Actions und Übergänge:**
- `LIVE_FULL + OK → INFO_BAR`; `INFO_BAR + OK/Down → PLAYER_CONTROLS`; `PLAYER_CONTROLS + Down → MORE_SETTINGS`. **Beim Ebenenwechsel nie automatisch einen Button aktivieren!**
- `PLAYER_CONTROLS + OK` führt genau die fokussierte Player-Aktion aus, nicht erneut eine Ebene wechseln; `MORE_SETTINGS + OK` führt genau die fokussierte Einstellung aus. `Up/Back` soll **eine Ebene nach oben** zurückführen, ohne Stream-Abbruch. Eine konsistente Lösung für `Up` vs. Senderzapping ist **zustandsabhängig** zu testen.
- **Taste Links aus `LIVE_FULL` bzw. `INFO_BAR` → `CHANNEL_LIST`** mit Senderlogo, JETZT-Titel, Von–bis, EPG; **Links innerhalb `CHANNEL_LIST` → `GROUPS`**, Rechts aus Gruppen zurück zur Liste. `Back` schließt Menüstufen logisch. Andere Kodi-Add-ons bleiben unbeeinflusst; globale Kodi-Keymap **AUS**.
- Für `PLAYER_CONTROLS`: **Play/Pause als eine dynamische Schaltfläche (▶↔⏸)**, die tatsächlichen Player-Zustand berücksichtigt; **Stop** als separat erreichbare, eindeutige Aktion, die den Kanal beendet. Der Nutzer erwägt einen kombinierten Start/Stop-Button, aber Play/Pause darf keinesfalls mit `stop()` verwechselt werden – UX-Entscheidung sicher umsetzen/dokumentieren. Eventuell reines `Play/Stop` mit bestätigbarem Neustart des letzten Kanals als optionale Alternative; Default für laufendes TV bleibt Play/Pause + Stop.
- **Tape-Deck-Vorlauf/Zurück/LIVE-Ende nur, wenn Kodi Seek/Timeshift tatsächlich unterstützt.** Auf nicht-seekablem IPTV-Live-Stream Funktionen deaktivieren oder verständlich kennzeichnen, keine falsche Seek-Behauptung oder Black-Screen. `Player.SeekEnabled`, Gesamtdauer, Live-Edge, Catch-up/Timeshift-Providerfähigkeiten prüfen. Trennung Seek ±10/30s, Rücksprung/Live-Edge, Play/Pause, Stop, ggf. Pufferposition. Kein unbeabsichtigtes `stop()` durch OK-Stufenwechsel.
- Für Ebene 3: Audio/Ton, Bild/Video, Untertitel, **EPG**, Sendergruppen und Einstellungen. Erreichbarkeit **ohne** zusätzliche Fokus-Jagd über `Weitere`, aber optional `Weitere`-Shortcut für ältere Eingabeprofile beibehalten.

## 3. P0: Warum Links auf echtem Kodi nichts tut – konkrete Codestellen

**Aktuelle `main`/0.1.25-Befunde aus `src/plugin.video.xtreammate/resources/lib/live_overlay.py`:**
- `ACTION_LEFT = 1` ist definiert (ca. Zeile 31), jedoch hat `LiveNavigator.onAction()` (ca. Zeilen 836–897) **keinen expliziten `elif key == ACTION_LEFT`-Pfad**, anders als für RIGHT, STOP, BACK und PAUSE. Nicht abgefangene Actions werden durch `remote_profiles.mapped_action(key)` ausgewertet.
- `remote_profiles.DEFAULT['left']=1` soll für Kodi Action-ID 1 zwar `'left'` zurückgeben, **aber** `mapped_action` lädt bei jedem Aufruf eine persistierte Zuordnung aus `xtreammate_remote_actions.json`. Ein altes, anderes gespeichertes `left`-Binding kann Kodi Action-ID 1 daran hindern, die Liste zu öffnen. Dies ist eine **prüfbare Ursache**, kein bereits bewiesener Gerätebefund.
- `_build_controls()` setzt `self.control.controlLeft(self.control)`, `self.control.controlRight(self.control)` (ca. 376–377) und `capture.setNavigation(self,self,self,self)`. Kodi könnte die linke Pfeiltaste bei fokussiertem Control schon auf Control-Navigation anwenden, sodass kein verwertbares `onAction(LEFT)` für den Navigator bleibt. **Hypothese am tatsächlichen Kodi-21-WindowDialog mit Logs prüfen**.
- `handle_command('left')` (ca. 740–752) **hat die gewünschte Funktion bereits implementiert**: hidden/info/guide → channels; channels → groups. Wenn `handle_command('left')` gezielt funktioniert, ist der *Dispatch/Input-Eingang* P0, nicht die Gruppen-/Moduslogik.
- `onAction()` protokolliert `NATIVE_ACTION` mit `action_id` und `button_code`; neue Diagnose soll zwischen **LEFT empfangen**, **gemappt**, **durch Kodi-Listennavigation verbraucht**, **verworfen** und **wirklichem Viewwechsel** trennen. Keine Provider-URL/Passwörter.
- Sicheres Regressionstest-Raster: `hidden/info → channels → groups → channels → hidden`; persistiertes Remote-Profil mit abweichendem `left`-Wert; `onAction(ACTION_LEFT=1)` mit tatsächlichem Fokus `capture` oder `ControlList`; Kodi-Doppeldispatch `onControl` und `onAction`; Wechsel bei sehr großen Gruppen, Seitenleiste/Fokus und Tastendruck ohne Lag. Default-Action LEFT muss **immer** oder nach expliziter verlässlicher Nutzermapping-Strategie erreichbar sein.

**Akzeptanz auf TV:** 10× aus Live-Vollbild **Links** muss 10× die Sender-EPG-Liste öffnen, 10× Links aus Senderliste muss 10× zu Sendergruppen wechseln, ohne Wiedergabeunterbrechung. Native Actions und Zielmodus jeweils in Diagnose bestätigt. Erfolgreicher Test mit OSD-Button-EPG ersetzt **nicht** den Links-Test.

## 4. P1: Vollständiger 7- bzw. 10-Tage-EPG statt nur weniger Sendungen

**Ziel:** EPG-Browser für **bis zu zehn Kalendertage** mit Tagesnavigation, Zeitachsen-/Listenmodus und suchbarer Sendungsübersicht. Standard 7 Tage, optional 10 Tage, abhängig vom Quellhorizont. **Verfügbarkeit nie behaupten:** Ein XMLTV-Feed kann nur 24–48 Stunden enthalten; Xtream `get_short_epg` kann nur wenige Sendungen liefern. Horizont je Quelle sichtbar machen: verfügbare erste/letzte echte Sendung, Zeitstempel, Quelle, Alter. Kein Erfinden fehlender Programmzeilen.

**Existierende Grenzen:** `epg_preview.py` filtert seine Anzeige auf **+48 Stunden** (ca. Zeile 73); `epg_views.guide_for_channel()` liefert nur die ersten **48 zukünftig relevanten Events** an die UI (ca. Zeile 50). `live_overlay._list_content()` rendert Guide-Einträge aus diesem Ausschnitt; es gibt aktuell keine wirkliche Tagesnavigation, Aufnahmeplanung oder Senderwechselaktion aus dem Guide. **Diese Listen-/UI-Grenzen dürfen nicht mit dem tatsächlichen Provider-EPG-Horizont verwechselt werden.** Auch die bestehenden XMLTV-Importgrenzen (~80 MiB entpackt / 150.000 Programme / 10.000 Kanäle je Importkonfiguration) können große Guides blockieren. **Nicht blind Limits erhöhen**.

**Technische Spezifikation für Codex:**
- Einheitliches Eventmodell `{portal_id, stream_id, epg_id, programme_id?, title, subtitle?, desc?, start_utc, stop_utc, source, updated_at}`; stabiler zusammengesetzter Event-Key aus Kanal/Start/Stopp/Quellenpriorität; optional Serien-/Episodenmetadaten.
- **Diskbasierter, nach Sender + Zeitfenster indizierter EPG-Speicher**, z.B. SQLite im Kodi-Addon-Profil; `(portal_id, channel_id, start_utc)` indexieren. Nicht 10 Tage × 53.664 Sender ins RAM oder alle Programme pro GUI-Klick laden. Begrenzte Hintergrundimporte, Parser-Streaming/Windowing, Crash-konsistente Transaktionen, Cachemigration ohne Verlust von Konto-/EPG-Zuordnungen.
- Tagesansicht Heute/Morgen/+2…+9, Programmliste chronologisch mit lokalen Von-/Bis-Zeiten und optional Beschreibung, Sender-Icon, Fortschritt für laufende Sendung; **Shift über Mitternacht, Sommerzeit/Zeitzone und überschneidende Quellen korrekt**.
- `now/next`-Infobar weiterhin aus gleichem lokalen Resolver; aktuelle **Infobar darf durch 10-Tage-Guide nicht langsamer werden**.
- Status: konfigurierte Quellen, `first_event`, `last_event`, `last_success`, importierte und abgeglichene Sender/Programme; Quelle ohne Langfristdaten explizit kennzeichnen.
- Führende Funktion aus EPG-Detail: `Ansehen / Zur Sendung wechseln` (bei Live oder zur rechten Zeit), `Erinnern`, `Automatisch umschalten` (nur mit Opt-in), `Aufnahme planen` (nur falls auf Gerät ausführbar), `Aufnahmeplanung ansehen/stornieren`.

## 5. P1/P2: EPG-basierte Erinnerung, Auto-Senderwechsel und Aufnahmen

**Vorhandener Code ist nur eine Grundlage, noch kein Scheduling:**
- `resources/lib/reminders.py::add_reminder()` speichert Erinnerung und `check_due()` zeigt Benachrichtigung. **`_fire_reminder()` schaltet bislang keinen Sender um**; sogar ein kleiner Tippfehler im Titel (`'eminder'`) fällt auf.
- `resources/lib/recordings.py::start_recording()` startet einen **sofortigen** `ffmpeg`-Subprozess mit gegebener Dauer; `show_record_dialog()` bietet Laufzeiten, **kein gespeichertes Start-/Ende-EPG-Schedule**. `ffmpeg` wird über PATH bzw. `/usr/bin` und `/usr/local/bin` gesucht – auf Android-TV oft nicht verfügbar. Keine erfolgreiche Aufnahme auf aktuellem Gerät nachgewiesen.

**Erinnerung:**
- Vor Sendungsbeginn frei konfigurierbare Benachrichtigung (z.B. 5 Minuten); Option **„Automatisch bei Sendungsbeginn zu diesem Sender wechseln“** separat und nur nach ausdrücklicher Aktivierung des Nutzers. Vorsicht: laufende Filme/Streams und andere Add-ons nicht ohne Opt-in unterbrechen; vor Konflikten bestätigen oder verschieben.
- Reminder-State (pending, notified, firing, completed, missed, cancelled) atomar und reboot-resistent; Timezones in UTC speichern, lokal anzeigen; kein zweifaches Tunen beim Kodi-Neustart. Zeit-/EPG-Verschiebungen später abgleichen und bei geänderter Sendungszeit signalisieren.
- Grenzen transparent: automatische Aktion kann nur ausgeführt werden, wenn Kodi-Service läuft und Gerät eingeschaltet/aktiv ist; **kein garantierter Android-Wakeup**.

**Aufnahmen:**
- Über Sender/EPG-Programm `Aufnahme planen` mit Start/Stopp, Vor-/Nachlauf, Dateiname/Pfad, freiem Speicher, Providerzugriff, ggf. Maximum paralleler Streams und Konfliktprüfung. Scheduler im Dienst mit persistenter Queue und Crash-Recovery; eindeutiger Status (geplant/läuft/fertig/fehlgeschlagen/abgebrochen), Fehlerdiagnose ohne Stream-URL/Passwort.
- Vor jeder Aktivierung **reale Aufnahmemöglichkeit auf Android prüfen**: FFmpeg-Binary vorhanden/ausführbar? Kodi PVR-Aufnahme-API verfügbar? Schreibrechte im Kodi-Datenordner/externe Platte? Datendurchsatz, freien Speicher, Provider-Multistream-Limit? Lizenz-/Verwendungsrechte des Streams? Ohne funktionsfähige Engine **Schaltfläche ehrlich deaktivieren und Grund anzeigen**, nicht „Aufnahme geplant“ als Gewissheit ausgeben.
- Bei unterstützter Engine Aufnahmen im Hintergrund unabhängig vom sichtbaren Stream ausführen; Schutz vor Doppelaufnahmen und Konflikten, Logs ohne Credentials. Bei Standby/Power-Off keine Aufnahmegarantie. Keine eigenmächtige Installation von System-Binaries oder root-relevante Kodi-Eingriffe.
- **P2 separat von P0-Links und dreistufigem OSD**, damit die Navigation zügig als kleines, prüfbares Update kommen kann.

## 6. Reihenfolge und Freigabeprozess

**Phase A – P0 (zuerst, eigenes PR):** Links-Key und dreistufiges OSD reparieren. Erste OK-Infoleiste **Freeze**. Native Kodi-21-Remote-Diagnose und Regressionstests, keine globale Keymap; Android-Gerätetest mit `LEFT` 10× und Übergängen. Codex soll Android-Abnahme verlangen statt Funktion zu behaupten.

**Phase B – P1 (separater PR oder Folgerelease):** Längere EPG-Browserarchitektur mit 7/10 Tagen, Datenhorizont und Tagesnavigation. Bestehende EPG-Import-/Quelle-/ID-Matching-Probleme müssen stabil sein. Nutzung der gleichen EPG-Daten für TV-Infobar, schnelle Senderliste und Langzeitprogramm. Große Guides speicherschonend.

**Phase C – P2:** Erinnerungen inklusive optionaler Auto-Umschaltung und danach **Aufnahmeplanung nur mit verifizierter Aufnahmeengine**. Konflikte, Speicher, Android-Wakeup und Persistenz testen. Kein „programmiert“ anzeigen, wenn hardwarebedingt nicht ausführbar.

**Phasen dürfen hintereinander als Kandidaten ausgeführt werden, ohne 0.1.25 auf dem TV zu destabilisieren.** Für jede Phase neuer Branch ab aktuellem `main`, lokale strikte Kodi-21-Tests, CI, PR, Geräteabnahmeplan, aktualisierte Dokumente. **Keine automatische Übernahme auf main oder öffentliche Veröffentlichung ohne Nutzerfreigabe.** Kodi-ID/GS-Media-Updatepfad und Kundendaten erhalten. Das separate XCMate Skin [Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14) ist kein Blocker; eigenständige UI direkt im Add-on erhalten.

**Umsetzungstickets:** [#20 P0 Links und dreistufiges OSD](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20) sowie [#21 P1/P2 Langzeit-EPG, Reminder/Auto-Tune und Aufnahmen](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21). Beide Issues sind Entwicklungsaufträge, noch keine implementierte Version.

## 7. Codeeinstiege und Referenzen

- `src/plugin.video.xtreammate/resources/lib/live_overlay.py`: `ACTION_LEFT`, `_build_controls`-Left-Control-Nav, `onAction`, `onControl`, `handle_command`, `_list_content`, `_execute`, dreistufige OSD-Zustandsmaschine.
- `src/plugin.video.xtreammate/resources/lib/remote_profiles.py`: `DEFAULT`, `mapped_action`, persistierter Mapping-Store, mögliche Profilkollision.
- `src/plugin.video.xtreammate/resources/lib/epg_views.py`: `guide_for_channel()` begrenzt ausgegebene Events.
- `src/plugin.video.xtreammate/resources/lib/epg_preview.py`: +48h-Anzeigefilter.
- `src/plugin.video.xtreammate/resources/lib/epg.py` und `epg_sources.py`: XMLTV-Parser/Importgrenzen/Quellenverarbeitung.
- `src/plugin.video.xtreammate/resources/lib/reminders.py`: Benachrichtigung, noch keine Auto-Umschaltung.
- `src/plugin.video.xtreammate/resources/lib/recordings.py`: unmittelbare FFmpeg-Aufnahmen, noch keine EPG-Planung.
- [Android-Gerätebefund 0.1.24](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md), [0.1.25-Implementierung & Geräteplan](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md), [UX-Spezifikation 0.1.25](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md), [Issue #12 Remote](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [#13 EPG](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#17 Infobar](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17).

## 8. Kopierbarer Kurzauftrag für Codex

> Prüfe zuerst `docs/XCMate/ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md`. Die reale 0.1.25-Infoleiste bei 1× OK funktioniert und ist optisch freigegeben – nicht verändern. Bei 2× OK oder Runter aus der Infoleiste muss eine richtige Tape-Deck-Playersteuerung erscheinen, bei weiterem Runter eine dritte Ebene mit Bild/Ton/Untertitel/EPG/Gruppen/Einstellungen. **P0:** Links aus Live-TV öffnet bei dem Android-Gerät aktuell gar nichts; Links aus Senderliste öffnet keine Gruppen. Analysiere Action-ID=1, Kodi-Control-Navigation, `remote_profiles.mapped_action` und persistent alte Zuordnung, behebe die echte Input-Ursache mit strikten Kodi-Tests/Diagnose. **P1:** 7–10-Tage-EPG mit echter Tagesnavigation und Quellhorizont, indexiertem Disk-Cache, Sendungsauswahl. **P2:** EPG-Erinnerungen plus ausdrücklich aktivierbares Auto-Umschalten und geplante Aufnahmen nur auf nachweislich unterstützter Kodi-/Android-Aufnahmeengine. Neuen Branch + CI + PR je sinnvoller Phase; `main` nicht ohne Freigabe ändern. Kodi 0.1.25 derzeit veröffentlicht, kein 0.1.26-Geräteerfolg behauptet.
