# XCMate 0.1.24 – Android-TV-Gerätetest: Live-Overlay erstmals sichtbar, EPG weiter offen

**Stand:** 18.10.2026, nach Veröffentlichung von XCMate 0.1.24 über den regulären GS-Media-Kodi-Updatekanal. **Testquelle:** drei Nutzerfotos vom laufenden Fernseher mit verbaler Rückmeldung. Fotos stammen aus der Chat-Konversation und sind **nicht** als Originalbilder im Repository gespeichert. Für den Softwarestand 0.1.24 spricht der unmittelbar vorausgegangene Release-/Updateablauf; **die angezeigte Versionsnummer ist auf diesen drei neuen Fotos selbst nicht sichtbar**. Nächste Diagnose bitte nochmals explizit auf `0.1.24` prüfen.

## 1. Sichtbar und sicher bestätigt – früherer P0-Fehler überwunden

- **Erstmals sichtbar:** ein XCMate-eigenes `WindowDialog`-Sidebarfenster *über laufendem TV-Video*, nicht bloß der separate XML-Diagnosetest. Foto 1 zeigt `XCMate · EPG`, Liste und helle Fokusmarkierung auf einer Zeile.
- Die Sidebar meldet `2746 Sender · Seite 2/28 · Alle aktivierten Gruppen`. Darunter Kanalzeilen wie `4K RELAX 9` bis `4K RELAX TURKEY 4K`. Der Screenshot mit Seite **2/28** belegt, dass Paging/Seitenwechsel **mindestens bis Seite 2** erreicht wurde; er belegt nicht, ob ein Senderwechsel per OK am Gerät erfolgreich funktioniert.
- Foto 2 zeigt eine eigenständige untere XCMate-Bedienleiste mit `Pause / Weiter`, `-10 s`, `+30 s`, `Stop` und `Weitere`, mit sichtbarer Auswahlmarkierung auf **Weitere**.
- Foto 3 zeigt eine zweite Bedienzeile mit `Ton`, `Bild`, `EPG`, `Einstellungen` und `Sendergruppen` (Markierung auf **Sendergruppen**); die erste Zeile bleibt sichtbar.
- Nutzer bestätigt ausdrücklich: Senderliste und unteres sowie erweitertes OSD werden jetzt geöffnet, **Fernbedienungsnavigation wirkt aber noch nicht zuverlässig**. Einzelne Tasten und Aktionen sind noch nicht kontrolliert durchgetestet. Der ehemalige Dialog-`TypeError` ist in dieser Situation offenbar nicht mehr aufgetreten. **Issue #12 nur als teilweise behoben, nicht abschließen.**

## 2. EPG nicht erfolgreich bestätigt

- Foto 1 zeigt Titel `XCMate · EPG` über der Senderliste, aber **keine Sendungstitel, Startzeiten, Jetzt-/Danach-Einträge oder Programmvorschau**.
- Laut Nutzer ist der EPG-Bereich über das Zusatzmenü weiterhin nicht zuverlässig aufrufbar bzw. liefert keine sichtbaren Ergebnisse. **Nicht behaupten, dass ein Klick auf die `EPG`-Schaltfläche eindeutig fehlgeschlagen ist**, solange gezielter OK-Test und neue Diagnose fehlen.
- **Quellcode (main 0.1.24), zwei unabhängige Pfade:**
  - `resources/lib/live_overlay.py::_render()` für `mode=='guide'` rendert denselben `ControlList`-Kanalbaum wie `mode=='channels'`; nur Überschrift/Footer unterscheiden sich. `guide_for_channel(load_cache(portal_id),c.tvg_id,stream_id)` hängt `Jetzt/Danach` nur an, wenn der **XMLTV-/EPG-Cache** passend gefüllte Daten enthält. **Keine vollwertige EPG-Timeline, keine detaillierte Guide-Seite.**
  - `resources/lib/main.py::_live_channels()` nutzt bei fehlendem `guide_for_channel`-Treffer `epg_views.cached_short_guide(...)` als zusätzlichen Xtream-`get_short_epg`-Fallback; das **Overlay `live_overlay.py::_render()` nutzt diesen vorhandenen Fallback nicht**. Das ist eine konkrete funktionale Inkonsistenz, unabhängig davon, ob Provider-/XMLTV-Import funktioniert.
  - `live_overlay.py::_execute('extras',index=2)` ruft `_epg()` auf. Dort prüft der Code `XtreamClient._get_json('get_short_epg',cached_only=True)` für den **laufenden** Stream und danach nur direkte `guide[tvg_id]`-Einträge. Bei fehlenden Daten startet `get_short_epg(...force_refresh=True)` **asynchron** und zeigt `EPG wird im Hintergrund geladen. Gleich erneut öffnen.` an. Nach Abschluss wird **kein geöffnetes Overlay automatisch aktualisiert**. In der Guide-Listenansicht existiert deshalb selbst bei erfolgreich geladenem kurzem Xtream-EPG keine sichtbare Fallback-Integration. `_epg()` beachtet möglicherweise manuelle Stream→XMLTV-Zuordnungen in der Guide-Cache-Suche nicht vollständig.
- **Historische echte Geräte-EPG-Diagnose aus 0.1.23:** `PROVIDER_LIMIT → NO_NEW_GUIDE` und `epg_source DOWNLOAD_FAILED` (zweiter Quellenversuch, 3.591.764 eingelesene Bytes, Limit 83.886.080). Für 0.1.24 fehlen **neue Diagnosedaten**, um zu wissen, ob die feinere Fehlerklassifikation einen konkreten neuen Grund liefert. Alte Fehlerwerte nicht als neuen 0.1.24-Downloadfehler ausgeben.
- **Ziel aus Issue #13:** eigener `EPG-Status & Vorschau`-Menüpunkt in XCMate, Quelle/[Index], letztes erfolgreiches Einlesen, Fehlerklasse/-stufe, Sender-/Programmzahl, Match-Quote, ein überprüfbarer echter Now-/Next-Eintrag – vor Skin-Integration. `EPG` darf bei fehlenden Daten nicht bloß auf eine weitere leere Kanalliste führen.

## 3. GUI/Navigation – sichtbare Probleme und gezielter Test

- TV-Overlay zeichnet sichtbar; dunkle graublaue Flächen, weiß-blauer Auswahlbalken. Aktuelles Erscheinungsbild ist ein **Funktionsprototyp**, noch nicht die freigegebene endgültige Oberfläche des geplanten `XCMate Skin` (Issue #14).
- Einige Symbolzeichen `⏯`, `⏪`, `◀`, `⋯` oder andere Sonderzeichen erscheinen auf Fotos als **leere Kästchen**. Wahrscheinlich fehlen die entsprechenden Glyphen im verwendeten Kodi-/Skin-Font; per Skin-kompatiblen Schriftzeichen oder Asset-Icons korrigieren. Dies ist ein visualisierter Fehler, die genaue Fontursache ist noch zu prüfen.
- Text und Bedienelemente nahe der unteren/seitlichen Displaygrenze erscheinen teilweise abgeschnitten oder ungünstig überlagert. Display-Videoaufnahmen, Overscan und echte Kodi-Safe-Area unterscheiden; auf dem Fernseher selbst nachmessen und keine Kamera-Crop-Vermutung als technischen Nachweis ausgeben.
- Navigation genauer erfassen: echte Links/Rechts/Hoch/Runter/OK/Zurück-Events, Auswahl-/Fokuspositionen, Öffnen und Schließen der Gruppenliste, Wechsel der 100er-Seiten, Auswahl eines Senders und Zusatzmenü-EPG-Klick. Besonders `onAction` versus `onControl` auf Kodi Omega gegen doppelte Bewegung prüfen.
- Aktueller Overlay-Code `onAction` für native D-Pad-Bewegung in Kanal-/Guide-Liste verlässt sich auf `ControlList`-Eigendynamik, während `handle_command` für den Bridgepfad explizit Positionen bewegt; damit Geräteverhalten (Focus/NativeActionCount) messen, bevor ein Fehler oder Fix angenommen wird.
- Sicherheit: Globale Fallback-Keymap bleibt ausgeschaltet; BINGIE MOD und andere Add-ons müssen weiterhin ungestört spielen/stoppen.

## 4. Abnahmeplan am Fernseher – kurze, nachvollziehbare Testfolge

1. `XCMate → TV-Fernbedienung: Diagnose` nach Start und Stop öffnen; **0.1.24 und `service build=24`** bestätigen; vollständige Screenshots von `dialog`, `focus`, `input`, `epg`, `epg_source`, `epg_list`.
2. **Senderliste:** Overlay öffnen, Hoch/Runter jeweils einmal, Markierung beobachten; dann **OK** auf einen anderen Sender als derzeit gespielt. Erfolgreichen Kanalwechsel bzw. Fehler klar protokollieren; Zurück schließen, Links Gruppenliste testen. WELT/Das Erste/ZDF oder andere tatsächlich mit EPG angebotene Sender bevorzugen, **nicht nur 4K RELAX-Testsender**.
3. **Unteres OSD:** OK öffnet Leiste; `Weitere` mit OK anwählen; `EPG` ausdrücklich fokussieren und **OK** drücken. Ergebnis protokollieren: Textviewer mit Titeln? Benachrichtigung „EPG wird …“? Gar keine Reaktion? Nach 30–60 Sekunden **EPG erneut öffnen** und Ergebnis fotografieren.
4. **Guide-Seitenansicht:** Links/Navigation gemäß definierter Aktion in `XCMate · EPG` wechseln. Prüfen, ob nur Senderliste ohne `Jetzt/Danach` erscheint oder Titel angezeigt werden.
5. **Quellenstatus:** Im Hauptmenü EPG-Verwaltung und aktuell gespeicherte Quellreihenfolge `[1],[2],…` ansehen (keine Zugangsdaten teilen), DE-EPGShare01 als kleinere Quelle einzeln im Hintergrund aktualisieren, dann vollständige `epg`/`epg_source`/Match-Diagnose prüfen. Die große Kaimandura-Datei kann 80 MiB Entpacklimit überschreiten; nicht blind erhöhen.
6. **Isolation:** Stream beenden; Film aus anderem Add-on abspielen und stoppen, prüfen, ob Kodi-Standardbedienung normal bleibt.

## 5. Codex-Auftrag für nächste Version, noch kein Release

**P1 Vorrang nach P0-Sichtbarkeitsfortschritt:** EPG-Probleme entlang `Source → Download → Parse → persistierter Cache → XMLTV-/Xtream-ID-Zuordnung → Jetzt/Danach → `live_overlay._render()` und `_epg()`` reproduzierbar klären. Fehlenden `cached_short_guide`-Fallback im Overlay ergänzen, ohne bei Fernbedienungsdruck Netzwerk im GUI-Thread auszuführen. Eine klare Status-/Vorschauansicht aus Issue #13 realisieren. Keine „EPG funktioniert“-Behauptung ohne sichtbare Titel/Zeiten.

**P0/P2 verbleibend:** Native Fernbedienung am Gerät zuverlässig machen und Fokusfälle reproduzieren, ohne die erneute Öffnung des Overlay zu gefährden; `XCMate Skin` zunächst nur als gesonderte Design-/Machbarkeitsphase (#14). GUI-Glyphen durch unterstützte Icons ersetzen und TV-Safe-Zones prüfen.

**Arbeitsweise:** Neuer separater Branch, Tests und PR; keine parallelen Änderungen auf `main`, kein automatisches Release ohne Nutzerfreigabe. Echte Android-Abnahme vor Schließen der Issues.

**Verweise:** [Projektstatus](CODEX_STATUS_CURRENT_DE.md) · [0.1.24-Technikbericht](KODI21_FIX_024_DE.md) · [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) · [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) · [XCMate Skin #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).
