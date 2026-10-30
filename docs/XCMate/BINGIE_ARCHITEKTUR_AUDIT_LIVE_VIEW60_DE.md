# XCMate / Titan BINGIE MOD – Architektur-Audit und sichere Live-TV-View

**Stand:** 30.10.2026. **Draft / nur Source; keine Installation, kein Merge, keine Box A/B verändert.**

## Quellen (unterschiedliche Versionen nicht gleichsetzen)
- BINGIE-MOD-Quellcode: https://github.com/AchillesPunks/skin.titan.bingie.mod (aktuelles abgefragtes `addon.xml`: **2.2.2**, GPL-2.0).
- Offizielles BINGIE-Kodi-Repository: https://github.com/AchillesPunks/repository.titan.bingie.mod, `omega/skin.titan.bingie.mod/skin.titan.bingie.mod-2.2.3.zip` (dort **2.2.3** gepackt).
- Box-B-Log: installierter Skin **2.2.3**, XCMate **.58**, Kodi 21.3 / RK3528 ARM32. Keine Rohlogs in GitHub.
- XCMate-Referenz P0 #281, .58 #278, geplante TVmaze-Anreicherung #280 (getrennt), bereits vorhandener Opt-in-Skin-Adapter `widget_skin50.py`.

**Wichtig:** Die in diesem Audit textlich inspizierten BINGIE-XML-Dateien stammen aus dem öffentlichen `skin.titan.bingie.mod`-Quellbranch (2.2.2). Die exakten Bytes der **2.2.3**-Distribution müssen vor jedem Patch/Beta-Fork gesondert gegen das 2.2.3-ZIP validiert werden; eine 2.2.2-Datei darf nicht blind auf 2.2.3 gepatcht werden.

## Beobachtungen aus dem BINGIE-Quellcode
1. `Home.xml` ruft `script.skinshortcuts` mit `buildxml` auf; `shortcuts/template.xml` generiert pro Widget-Slot (bis zu acht) `widgetPath`, `widgetTarget`, `widgetType`, `contentStyle`, `widgetid`-Parameter.
2. `xml/IncludesHomeWidgets.xml` definiert `widget_base` → `widget_base_normal` → `widget_base_content_normal` → `<content target=... browse="never">widgetPath</content>`. Native Kodi DirectoryProvider-URL muss wirklich aufgerufen werden.
3. `widget_base_normal` enthält unter anderem die Sichtbarkeitsbedingung `Container(widgetid).IsUpdating + Control.IsVisible(widgetid) | Integer.IsGreater(Container(widgetid).NumItems,0)`. Bei Initialzustand ohne Items ist zu verifizieren, ob die Kombination mit `submenuVisibility` und `ShowAllWidgets` einen unsichtbaren/nie befüllten Container erzeugt. **Hypothese, kein bewiesener Rootcause!**
4. `WidgetBaseBingieIncludes` verwendet unter aktiven Trailerbedingungen `<onunfocus ...>PlayerControl(Stop)</onunfocus>`. Ein Live-IPTV-Widget soll diese Aktion **nicht** auslösen; bisher kein Nachweis, dass sie den beobachteten Crash verursachte.
5. Unterschiedliche Layouts (poster, landscape, fixed-focus, circular), `preloaditems=5`, Animations-/Trailer-/SkinHelper-Funktionen und häufige Metadatenabfragen sind potenzielle Kostenfaktoren. Performanceprofil auf Box B fehlt; keine erfundenen Millisekundenwerte.

## Warum Film-/Serienwidgets nicht sichtbar sind (Auswertung)
- Die .58-Logs belegen erfolgreiches **Service-Publishing**: 24 VOD- und 24 Serien-Items, echte Providerposter zugeordnet. **Nicht belegt:** Kodi-Directory-Invocation, Skinshortcuts generierte Consumer-ID, sichtbarer Home-Container, Pixel/Poster auf dem TV.
- Im bestehenden XCMate-Code ist der dynamische Ablauf bereits vorgesehen: `widget_query44.small` sortiert nicht-Live nach `added DESC`, liest 24 Titel aus `items_v2`/`titles` und `widget_data41.snapshot` aktualisiert den Cache nach Politik-/Katalogänderung. Kodi-Home muss den Plugin-Pfad tatsächlich öffnen; ein `PUBLISHED`-Status ist nur der Hintergrund-Snapshot.
- Codex soll **zuerst** die schadhafte Schnittstelle im Issue #281 finden, nicht einfach den Katalog neu importieren, Skinshortcuts löschen oder die Bildquelle wechseln.
- Diagnosen müssen exakt unterscheiden: `BINDING_PRESENT`, `GENERATED_CONSUMER_PRESENT`, `DIRECTORY_INVOKED`, `ITEMS_READY`, `HOME_ITEMS_PRESENT`, `ACTUAL_PIXELS_VISIBLE`. Der zusätzliche Verlauf vom tatsächlichen Kodi-Plugineintritt bis zum erzeugten Home-Container ist bisher nicht positiv nachgewiesen.

## Sichere Live-TV View – Stufe 1
- Neu: `resources/lib/live_view60.py` + `resources/skins/Default/720p/XCMateLiveView60.xml`.
- Ausschließlich `Einstellungen → Experimentell (PIN) → Live-TV-Ansicht – sichere Vorschau`.
- Zeigt komplette **lokal indexierte Startgruppe** bis Schutzgrenze 2.000 Sender horizontal mit kleinen Senderlogos; Fokus (0,35 s Debounce) aktualisiert nur **einen** lokalen EPG-/Bild-Datensatz (`widget_render47`/Cache). Titel, Jetzt/Nächste, Beschreibung, Fortschritt und großes Sendungsbild; ohne vorhandenes Bild bleibt die Senderzeile erhalten.
- **Kein AutoPlay und kein Abspielen auf OK**, keinerlei `PlayerControl(Stop)`, kein PVR-Fensterwechsel, kein Schreiben in BINGIE-Dateien/Widget-Profil. Kein Netzwerkkatalogscan bei Fokus.
- **Nicht das BINGIE-Home-Widget selbst**, sondern eine risikoarme Vorschau, um die Oberflächenlogik unabhängig von Skinshortcuts/Player auf Box B zu prüfen. Die native BINGIE-Home-Integration bleibt ein **separates, explizites Opt-in nach erfolgreicher P0-BINGIE-Diagnose**.
- Der bereits existierende `widget_home50.py`-Live-Home-Source (komplette Startgruppe) und das BINGIE-Anpassungsmodul `widget_skin50.py` bleiben **unverändert**; keine automatische Skinpatch-Ausführung.
- **Auf Android: NOT_TESTED**; Offline-Checks in `tests/test_xcmate_live_view60_safe.py`; in dieser PR keine neue Add-on-ZIP/version. Vor späterem Rollout auf aktuellen main-Stand rebasen und kumulative Versionsnummer nutzen.

## Empfehlung „GS Media BINGIE Lite“ (separater Architekturentscheid, noch nicht implementiert)
1. Zuerst P0-BINGIE-Bindings/Consumer reparieren und **messen**: Kaltstart Home bis erste Pixel, Kodi Directory-Walltime, SQL-Zeit, Anzahl gleichzeitig aktiver Widgets, Bildgröße/-Cache, RAM/Texture-Load und Fokus-Latenz.
2. Wenn erforderlich, **separater Skin-Fork mit eigenem Add-on-ID** (z. B. `skin.gsmedia.bingie.lite`), eigenem Repository und Branding, GPLv2 + Urheberhinweise + Quellcodeveröffentlichung. Keine unbemerkte Überschreibung des installierten BINGIE-Skins.
3. Lite-Design: native Kodi-Container, höchstens 3 Starterreihen (Live-TV, neueste Filme, neueste Serien), providerbasierte Poster, Bild-/EPG-Hero ausschließlich lokal im Cache, keine automatische Trailer-Wiedergabe, keine SkinHelper-Vollmetadatenabfragen pro Fokus, begrenztes Image-Prefetch, klare Status-/Empty-Platzhalter.
4. Pilot auf Box B als **zweiter separat installierbarer Skin**, nie als Update des alten Skins. Box A unverändert; reversible Umschaltung. Der bestehende Skin bleibt bis erfolgreicher Vergleichsmessung Standard.

## Nächste Entwicklungs-Gates
- GitHub-CI / Unit-Tests, XML-Validierung, dokumentierte Diff-Rechte/Version, keine Unterbrechung von #281.
- Box B später: 88 Sender inkl. letzte Sender, Fokus ohne Playerstart, schnelle Now/Next-Sichtbarkeit, No-EPG-Fallback, Navigation Zurück, keine Player-Stop-Aktion; Film/Serien-Home weiterhin separat P0.
- **Kein Merge ohne Nutzerfreigabe.**
