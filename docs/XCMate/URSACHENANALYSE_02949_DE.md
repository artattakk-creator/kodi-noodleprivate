# XCMate .49 – Widgetauswahl #252

Datum: 28.10.2026 (Europe/Berlin). Kumulative Basis `main` .48, `0f825fbd8b7280aea6dae6c236c23533b6dc3f02`; separater Branch `hotfix/xcmate-02949-widget-picker`. .49 war auf main/Remote-Branches/Tags noch nicht belegt. Issue #252 vollständig samt Hotfix-Nachtrag gelesen; keine Kommentare vorhanden.

## Tatsächlicher Fehlerpfad .47 / .48

| Stelle | .47 | .48 | .49 |
|---|---|---|---|
| Deutscher Abschnitt #36004 / Widgets #32443 | „Darstellung & Bedienung“ / „BINGIE-MOD-Widgets einrichten“ | gleich | „Aussehen und Darstellung“ / „Widgets“; IDs bleiben gleich |
| `settings_sections45.render` + `DIALOG_ACTIONS` | `widget_setup` als nicht abspielbare **Nicht-Ordner-Aktion** | gleich | `widget_setup` ist regulärer Ordner; Status/Anleitung bleiben getrennte Aktionen |
| `app_routes.dispatch(widget_setup)` | Directory zuerst beendet, danach Python-Auswahldialog | gleich; nur separate Hero-Demo hinzugefügt | drei echte Kodi-Ordner vor einmaligem erfolgreichen `endOfDirectory`, `cacheToDisc=False`, Content `files` |
| Widgetquellen im Manager | Textviewer mit Plugin-URLs | gleich | Primär direkt browsebar; optionaler Hilfedialog erklärt die tatsächliche BINGIE-Auswahl und Speicherung, ohne URL-Textviewer |
| Laufzeitquellen | `widget_live_start_group`, `widget_recent_vod`, `widget_recent_series` vorhanden | vorhanden und funktionierende Medienpfade | **identische Routen/Parameter und Implementierung** |

Die drei Widgetfunktionen fehlten nicht. Bestätigt ist ein schon in .47 vorhandener Einrichtungs-/UX-Pfadfehler; .48 fügte keinen echten BINGIE-Hero-Binder hinzu. Kein belegter neuer Datenbank-/Playerfehler wird aus dem Einrichtungsfehler abgeleitet.

## Native Browse-/Save-Grenze

Skinshortcuts liest per `Files.GetDirectory`, bietet Plugin-Einträge mit `filetype=directory` als Unterordner an und stellt innerhalb des gewählten Quellordners **Use as widget** bereit. Beim Bestätigen liefert es `widget=Addon`, `widgetTarget=videos` und den gewählten Ordner als `widgetPath` zurück. BINGIE/Skinshortcuts speichert diese Auswahl selbst; XCMate schreibt keine Skin-XML oder Bindings und meldet bei bloßem Durchstöbern keinen Speichererfolg.

`.49` liefert drei Ordner mit `isFolder=True`, `IsPlayable=false`, Portal-ID und exakt den vorhandenen Runtime-URLs. Öffnen zeigt echte Live-/Film-/Serientitel; zum Speichern nicht einen Titel starten, sondern **Als Widget verwenden** für den aktuellen Quellordner wählen. Bei einem alten `RunPlugin(widget_setup)` mit Handle −1 wird einmal die normale Kodi-Quellansicht geöffnet, ohne auf einen nicht vorhandenen Directory-Handle zu warten.

## Quellbeleg und Hostmodell

Originale, unveränderte Methoden `LibraryFunctions.explorer` und `_detect_plugin_content` aus `MikeSiLVO/script.skinshortcuts` **v2.0.3**, Commit `3816843a8069d237d38f13f3d0cbd991677dff28`, Datei `resources/lib/skinshorcuts/library.py`. Gehashter Auszug, Herkunft und GPL-2.0-only-Lizenz separat unter `tests/fixtures/skinshortcuts_*`. Der Hosttest führt diese Originalmethoden aus: Kodi-JSON-RPC-/Dialoggrenze simuliert, dahinter echte XCMate-Home-/Settings-/Quellrouten und echte lokale Testkataloge. Jede Quelle wird vollständig durchstöbert, **Use as widget** gewählt, der zurückgegebene Binding-URL serialisiert und erneut geladen; Cancel liefert kein Binding.

Öffentlicher BINGIE-Referenzconsumer: `AchillesPunks/skin.titan.bingie.mod`, Commit `1197a8e421b2836a1c18ea7223b5b6a1f4f2d7ff`, Version **2.2.2**. `shortcuts/overrides.xml` bietet `addons://sources/video` als Widgetquelle; `xml/script-skinshortcuts.xml` verwendet Widgetauswahl-Control 312 und `widgetName`-Properties. Die tatsächlich installierte **2.2.3** samt eigenem Skinshortcuts-Fork liegt nicht als exakter Gerätesnapshot vor. Deshalb sind diese Belege ein nativer Protokoll-/Referenztest und **keine Android-/Pixel-/Persistenzabnahme dieser konkreten Installation**. Keine Fremdaddoninstallation, kein Monkeypatch und keine Skinänderung vorgenommen.

## Bestandsschutz / Scope

Sieben genau abgegrenzte bestehende Quelldateien geändert: Manifest, Changelog, zwei Sprachkataloge, Route, Aktionsklassifizierung und optionaler alter Manager. Ein neues kleines Quellverzeichnis-Modul. **Alle übrigen 558 .48-Quelldateien bytegleich**, darunter Portale, EPG/Mapping, Cover, Mediendaten, Widget-Reader/Klickziele, Film-/Serien-Autorefresh, .42-Stopstrategie, Autoplay, Resume, alle Settings-IDs und Skinadapter. Keine neue Datenbank/Migration, kein Cache-/Profilreset, kein Löschen von Bildern und kein Schreiben auf eine Box. Die .48-Hero-Demo bleibt separat; echte Hero-Skinintegration folgt später.

Alle bisherigen 2.021 Testmethoden bleiben erhalten. Neue Prüfungen decken realen Menüpfad, drei Ordner/Leaf-Contenttypes, einmalige Directory-Freigabe, Legacy-Handle, explizite Portal-ID, Anleitung, Sprache, unveränderte Dateien und den Original-Explorer ab. Technische Ergebnisse im Testbericht; Android zunächst NOT_TESTED, siehe kurze Drei-Schritt-Abnahme. Kein automatischer Merge/Release und keine Issue-Schließung.
