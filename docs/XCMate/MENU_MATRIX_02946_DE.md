# XCMate .46 – Menü-, Icon- und Einstellungsprüfung

Jede Zeile ist auf Box B **ANDROID_NOT_TESTED**. Host prüft lokale transparente Dateien, native ListItems, unveränderte IDs/Hit-Rechtecke/Remote-Links und richtige Funktionszuordnung. Medienposter/Logos behalten ihre Inhaltspfade. Icons sind unfokussierbar. Keine Bilddownloads bei Menübewegung. Native Kodi-Contextmenus, Keyboard, Browse und Yes/No haben keine eigenen Zeilenicons und bleiben unverändert.

## Sieben Rubriken und komplette Settings-Unterwege

| Ebene | Aktion / Parameter | Semantik / lokale Datei | Android |
|---|---|---|---|
| Hauptbereich accounts | settings_section / accounts | user.png | NOT_TESTED |
| Hauptbereich live | settings_section / live | tv.png | NOT_TESTED |
| Hauptbereich epg | settings_section / epg | calendar.png | NOT_TESTED |
| Hauptbereich media | settings_section / media | play.png | NOT_TESTED |
| Hauptbereich appearance | settings_section / appearance | palette.png | NOT_TESTED |
| Hauptbereich system | settings_section / system | drive.png | NOT_TESTED |
| Hauptbereich experimental | settings_section / experimental | flask-lock.png | NOT_TESTED |
| accounts | account_select {} | check.png | NOT_TESTED |
| accounts | portal_manager {} | user.png | NOT_TESTED |
| accounts | setup_wizard {} | wand.png | NOT_TESTED |
| accounts | native_options45 {"group": "accounts"} | user.png | NOT_TESTED |
| live | startup_settings {} | tv.png | NOT_TESTED |
| live | groups_manager {} | list.png | NOT_TESTED |
| live | favourites {} | star.png | NOT_TESTED |
| live | native_options45 {"group": "live"} | tv.png | NOT_TESTED |
| epg | guide_browser {} | calendar.png | NOT_TESTED |
| epg | epg_sources {} | database.png | NOT_TESTED |
| epg | guide_status {} | activity.png | NOT_TESTED |
| epg | guide_backup44 {} | shield.png | NOT_TESTED |
| epg | refresh_epg {} | refresh.png | NOT_TESTED |
| epg | native_options45 {"group": "epg"} | calendar.png | NOT_TESTED |
| media | native_options45 {"group": "media"} | play.png | NOT_TESTED |
| media | media_favourites {"kind": "vod"} | movie.png | NOT_TESTED |
| media | media_favourites {"kind": "series"} | series.png | NOT_TESTED |
| appearance | theme_manager {} | palette.png | NOT_TESTED |
| appearance | ui_language {} | globe.png | NOT_TESTED |
| appearance | appearance_settings {} | palette.png | NOT_TESTED |
| appearance | remote_setup {} | remote.png | NOT_TESTED |
| appearance | widget_setup {} | grid.png | NOT_TESTED |
| appearance | native_options45 {"group": "appearance"} | palette.png | NOT_TESTED |
| system | artwork_manage {} | image.png | NOT_TESTED |
| system | art_status {} | activity.png | NOT_TESTED |
| system | native_options45 {"group": "system"} | drive.png | NOT_TESTED |
| system | settings_section {"section": "information"} | info.png | NOT_TESTED |
| system | settings {} | settings.png | NOT_TESTED |
| information | device_info {} | info.png | NOT_TESTED |
| information | branding_status {} | info.png | NOT_TESTED |
| information | about_xcmate {} | info.png | NOT_TESTED |
| information | xcmate_licenses {} | document.png | NOT_TESTED |
| experimental | widget_adapter45 {} | grid.png | NOT_TESTED |
| experimental | settings_section {"section": "downloads"} | download.png | NOT_TESTED |
| experimental | settings_section {"section": "recordings"} | record.png | NOT_TESTED |
| experimental | settings_section {"section": "diagnostics"} | activity.png | NOT_TESTED |
| experimental | native_options45 {"group": "experimental"} | flask-lock.png | NOT_TESTED |
| downloads | downloads_manage45 {} | download.png | NOT_TESTED |
| downloads | download_folder {} | drive.png | NOT_TESTED |
| downloads | download_capabilities {} | info.png | NOT_TESTED |
| downloads | download_target_test {} | activity.png | NOT_TESTED |
| recordings | record_now {} | record.png | NOT_TESTED |
| recordings | recordings_manage {} | record.png | NOT_TESTED |
| recordings | guide_timers {} | clock.png | NOT_TESTED |
| recordings | recording_folder {} | drive.png | NOT_TESTED |
| recordings | recording_capabilities {} | info.png | NOT_TESTED |
| diagnostics | stability_test {} | activity.png | NOT_TESTED |
| diagnostics | remote_diagnostics {} | activity.png | NOT_TESTED |
| diagnostics | service_recover {} | refresh.png | NOT_TESTED |
| diagnostics | popup_probe {} | activity.png | NOT_TESTED |
| diagnostics | clear_cache {} | trash.png | NOT_TESTED |
| diagnostics | art_retry {} | refresh.png | NOT_TESTED |
| diagnostics | art_db_health {} | shield.png | NOT_TESTED |
| diagnostics | autoplay_diagnostic_mode {} | activity.png | NOT_TESTED |
| diagnostics | remote_learn {} | remote.png | NOT_TESTED |
| diagnostics | recording_folder {"check": "1"} | drive.png | NOT_TESTED |

## Weitere eigene Oberflächen

| Oberfläche | Iconumsetzung / Umfang | Android |
|---|---|---|
| Home und native Plugin-Verzeichnisse | Zentrale Funktionsregistry; Startsender/LiveTV, Filme, Serien, EPG, Einstellungen, Suche, Favoriten | NOT_TESTED |
| Accounts/Portale und Xtream/M3U/STB-Import | Hinzufügen, Bearbeiten, Auswählen, Entfernen, Provider-/Quellauswahl; vorhandene Bestätigungen | NOT_TESTED |
| Wizard und Gruppen-/Playlisteditor | Originale Status-Checks bleiben; Toolbar-/Listenglyphen ohne neue Fokusziele | NOT_TESTED |
| Große EPG-Gruppen/Events/Kontextauswahl | Gruppen-/Sendungslistenglyphen und native Auswahl; nativer Contextmenu ausgenommen | NOT_TESTED |
| Filme/Serien/Details/Staffeln/Episoden | Inhaltscover erhalten; Aktionen Play/Favorit/Info/Trailer usw. zentrale Glyphen | NOT_TESTED |
| Linkes Detailmenü | Download, Manager, Poster-Retry, Bildsuche, Metadaten und bestehende Aktionen; experimentelle Aktionen PIN | NOT_TESTED |
| Cover-/Metadaten-/Quellen-/Kandidatenauswahl | Native ListItems; echte Vorschaubilder nicht überschreiben | NOT_TESTED |
| Suche, Tabs und Treffer | Original-Such-XML bytegleich; erzeugte eigene Menüdekoration; Titelcover erhalten | NOT_TESTED |
| Darstellung/Sprachen/Themeverwaltung | Palette/Globus/Info/Bestätigung; keine zusätzlichen IR-Ziele | NOT_TESTED |
| Widgetstatus und optionaler Adapter | Raster/Info/Back; Adapter extra PIN und Bestätigung | NOT_TESTED |
| Experimentell: Aufnahmen/Downloads/Timer/Diagnose | Aufnahme/Download/Clock/Activity/Shield/Trash; direkte Routen ebenfalls gesperrt | NOT_TESTED |
| Player/erweiterte Info und technische Auswahl | Bestehende Transport-/Audio-/CC-/Infoicons und Bedienung erhalten | NOT_TESTED |

## Sämtliche nativen eigenen Select-/Multiselect-Aufrufstellen

Die folgende statische Liste enthält alle dekorierten Aufrufstellen; zusätzlich bleiben die bereits iconbestückten `stream_details.py`-ListItems bestehen. Sie ist eine Prüfliste, keine Geräteabnahme.

| Modul | Zeilen der Auswahl | Android |
|---|---|---|
| app_routes.py | 151 | NOT_TESTED |
| appearance.py | 163, 170, 173 | NOT_TESTED |
| artwork_status.py | 71 | NOT_TESTED |
| artwork_ui.py | 58, 62, 76 | NOT_TESTED |
| capture_ui.py | 25, 27, 62 | NOT_TESTED |
| download_trust_ui.py | 15, 46 | NOT_TESTED |
| downloads_ui.py | 20, 54, 68 | NOT_TESTED |
| epg_preview.py | 101, 126 | NOT_TESTED |
| epg_sources.py | 327, 340, 358, 394, 404, 430 | NOT_TESTED |
| export_import.py | 39, 52, 121 | NOT_TESTED |
| group_selection.py | 156, 209, 212, 261 | NOT_TESTED |
| guide_grid_window.py | 220 | NOT_TESTED |
| guide_timers.py | 69 | NOT_TESTED |
| guide_window.py | 228 | NOT_TESTED |
| localization.py | 66 | NOT_TESTED |
| main.py | 670, 796 | NOT_TESTED |
| media_osd.py | 186 | NOT_TESTED |
| media_picker43.py | 181, 260, 317 | NOT_TESTED |
| media_window.py | 766, 923, 932 | NOT_TESTED |
| playlist_editor.py | 54, 61, 76, 81 | NOT_TESTED |
| popup_probe.py | 119 | NOT_TESTED |
| portal_manager.py | 28, 59, 79, 116, 127 | NOT_TESTED |
| recordings.py | 174 | NOT_TESTED |
| remote_control.py | 168 | NOT_TESTED |
| remote_profiles.py | 117 | NOT_TESTED |
| setup_window.py | 241, 297 | NOT_TESTED |
| setup_wizard.py | 75 | NOT_TESTED |
| sleep_timer.py | 61 | NOT_TESTED |
| stability_monitor.py | 91, 94 | NOT_TESTED |
| startup_preferences.py | 37, 49 | NOT_TESTED |
| storage_sources.py | 40, 53 | NOT_TESTED |
| theme_ui.py | 94, 106, 110, 126 | NOT_TESTED |

Settings-IDs/Typen/Defaults/Optionen werden gegen `tests/fixtures/xcmate_02945_settings_baseline.json` geprüft. Alte Rubrik-Aliase: {"startup": "live", "groups": "live", "remote": "appearance", "player": "media", "storage": "system", "maintenance": "system", "about": "system", "designs": "appearance"}. Keine automatische Werteänderung. Bei nativen Settingsrelativbedingungen werden außerdem die ursprünglichen referenzierten Ziel-IDs geprüft.

## Neue .46-Menüs und vollständige Dateipräsenz

Alle vorhandenen35lokalen Glyphen sind in beiden Varianten (70PNG) vorhanden, siehe weiter aktive Registrytests. Jede unten genannte Datei ist im Add-on enthalten. Alle Android-Sichtprüfungen bleiben NOT_TESTED.

| Name | Action / Control | Icondatei | Vorhanden | Android |
|---|---|---|---|---|
| Sendungsdetails | programme_details46 / bestehende Guide-Detailaktion | menu45/calendar.png | PASS | NOT_TESTED |
| Details schließen | XCMateProgramme46 /501 | menu45/full/back.png | PASS | NOT_TESTED |
| Optionaler Programme-Widgetadapter | widget_adapter46 | menu45/grid.png | PASS | NOT_TESTED |
| Adapter vorbereiten | TEST, eigene native Auswahl | menu45/grid.png | PASS | NOT_TESTED |
| Original wiederherstellen | TEST, eigene native Auswahl | menu45/shield.png | PASS | NOT_TESTED |
| Bestehenden Reloadadapter prüfen | widget_adapter45 (Alias unverändert) | menu45/refresh.png | PASS | NOT_TESTED |
| Adapter bestätigen | nicht vorausgewählte Bestätigung | menu45/shield.png | PASS | NOT_TESTED |
| Abbrechen/Zurück | jede eigene Adapterauswahl | menu45/back.png | PASS | NOT_TESTED |
| Programm-Bildcachebudget | native_options45 group=epg | zentrale Settingsauswahl, keine fremde Kodi-Zeilenänderung | PASS | NOT_TESTED |
| Optionales TMDb für Programme | native_options45 group=epg | zentrale Settingsauswahl | PASS | NOT_TESTED |

Kodi-Widget-Kontextmenü „Sendungsdetails“ nutzt die native ListItem-Contextmenu-API; diese unterstützt keine eigenen Zeilenicons und gehört zu den bereits dokumentierten nativen Ausnahmen. Kein globales Keymap-/Info-Tasten-Patching. Programmbild/Logo sind Inhaltsebenen und keine zusätzlichen Fokusziele.
