# XCMate .51 – Wizard-Hotfix zu #255

Basis: `main` .50, `54759f965aef97b45c846042010d5ae1aa1f8ff3`. Kumulativ, keine Übernahme experimenteller Wizard-Branches. Befund und Prüfstand: 28.10.2026.

## Belegt

1. `.50 setup_wizard.input_data()` legt ein neues Dictionary an und fragt Host/User/Pass erneut ab. Die tatsächlich deklarierten Kodi-Settings heißen `new_portal_xc_host`, `new_portal_xc_user`, `new_portal_xc_pass`; die typabhängigen M3U-/STB-Felder tragen ebenfalls das Präfix `new_portal_`. Der Wizard hat diese nicht gelesen. Das ist von `portals.json` und alten `playlistN_*`-Settings zu unterscheiden.
2. `.50 SetupWindow._groups()` erstellt alle drei Listen synchron, auch die unsichtbaren Film-/Seriengruppen. Jede Zeile ruft `_item_state()` auf; das ermittelt über `menu_icons45.state_icon()` erneut `xbmcaddon.Addon().getAddonInfo('path')`. Bei 1.201 Gruppen je Typ sind das 3.603 Bildpfadabfragen während eines einzigen Listenaufbaus. Jeder OK-Klick wiederholt eine solche Abfrage; Alle/Keine aktualisiert sämtliche Zeilen in einem Callback. Zusätzlich fragt `tr()` bei der Auswahlzählung die Add-on-Lokalisierung erneut ab.
3. Im eigenen Wizard-XML wird `lightweight_splash.jpg` ausdrücklich als `texturenofocus` sämtlicher Buttons eingesetzt. Das widerspricht dem gewünschten neutralen Design.
4. `.48` begrenzt konkurrierende Discovery-Aufrufe. Der vollständige Scan-/Save-Worker hat bisher keine fensterübergreifende Lebensdauersperre. Ein nach Abbruch noch nicht zurückgekehrter Plattformaufruf darf nicht durch erneutes Öffnen weitere Jobs erzeugen.

## Nicht bewiesen

Issue #255 enthält keinen exakten Android-Crash-/Hang-Stack. Die beschriebenen synchronen Aufrufe und fehlenden Schutzmechanismen sind reproduzierbare Codebefunde, aber **kein Nachweis der einzigen Ursache des gemeldeten Android-Hängers**. Native GUI-/DNS-/Dateisystemblockaden bleiben Geräteprüfungen. Hostzeiten dürfen nicht als RK3528-Latenzen ausgegeben werden.

## Umsetzung

- `wizard_settings51.py` liest ausschließlich die neuen Eingabefelder des eigenen Add-ons `plugin.video.xtreammate`. Kein Zugang aus dem aktiven oder einem fremden Portal wird geraten. Settings-Typen 0/1/2/3 werden korrekt auf M3U-URL/M3U-Datei/Xtream/STB abgebildet. Die Standard-MAC allein gilt nicht als konfigurierter Zugang.
- Vor der Nutzung erscheint eine Bestätigung mit Vorgabe **Nein**, ohne Server/User/Pass im Text. Vollständige Daten werden verwendet; fehlende Pflichtfelder werden erfragt. Passwörter werden nicht als sichtbare Standardwerte wieder geöffnet. Ablehnen führt zur manuellen Einrichtung. Abbrechen startet keinen Scan. Keine Settings werden gelöscht, zurückgeschrieben oder heimlich mit Bestandsportalen zusammengeführt.
- `wizard_groups51.py` lädt nur die gewählte Liste. Pro Owner-Pump-Schritt entstehen höchstens **32 Zeilen oder 8 ms Python-Erzeugung**; die Grenze ist kooperativ und kann einen einzelnen nativen Kodi-Aufruf nicht unterbrechen. `addItems()` wird mit diesen begrenzten Blöcken aufgerufen. Die ersten Zeilen sind schon nutzbar, während weitere hinzukommen. Andere Tabs bleiben bis zur Auswahl leer.
- Bildpfade und häufige Zeilentexte werden einmal pro Fenster vorbereitet. Ein einzelner Toggle verändert nur die betroffene Zeile und Auswahlzählung, ohne Add-on-Abfrage, Reset oder Cursorbewegung. Alle/Keine setzt die Datenauswahl und aktualisiert die Zeilen ebenfalls begrenzt; ausstehende Markierungen bleiben pro Tab erhalten.
- Alle Control-Änderungen bleiben im Python-Fensterowner; Worker liefern Daten und koaleszierten Fortschritt. Reaktivierung startet die Discovery nicht erneut. Verspätete Klicks unsichtbarer Listen werden verworfen.
- `wizard_session51.py` hält eine nicht blockierende OS-Sperre über die gesamte tatsächliche Worker-Lebensdauer, auch nach Back/Abbruch. Aufräumen und Freigabe erfolgen einmalig nach Jobende. Erneutes Öffnen währenddessen zeigt `XM-SETUP-WORKER-BUSY`, ohne zweiten Draft/Executor. Die Lockdatei bleibt bestehen; die OS-Sperre wird beim Schließen des Deskriptors freigegeben.
- Bestehende Discovery-Grenze: 25 s kooperatives Requestbudget. Zusätzlich schließt ein UI-Watchdog nach 35 s Discovery bzw. 180 s ohne Scan-/Save-Fortschritt das Fenster kontrolliert und fordert Abbruch an. DNS oder einen nativen Betriebssystemaufruf kann Python nicht sicher töten; die Sperre bleibt bis zur tatsächlichen Rückkehr erhalten. Das wird als Timeout gemeldet, nicht als erfolgreicher Abschluss. Große laufende Scans erneuern das Budget über echte Fortschrittsmeldungen. Save meldet tatsächliche Kopierblöcke und Verifikationsphase.
- Das vorhandene Staging, die neuen zufälligen Portal-IDs, Indexverifikation und die gezielte Fehler-Rücksicherung bleiben erhalten. Hardwareabbruch unmittelbar nach endgültiger Portalpublikation kann eine bereits gültig gespeicherte Einrichtung hinterlassen; bestehende Portale werden nicht verändert.
- Das eigene Wizard-XML verwendet ein einziges neues weißes 1×1-Pixel mit neutralen Farbwerten für Flächen, Fokus und Fortschritt. Checkboxen bleiben kleine Auswahlindikatoren; keine Poster/Fanart hinter Text. Original-Icon bleibt erhalten.

## Diagnose und Schutzgrenze

Marker: `SETUP_DISCOVER_DONE`, `GROUPS_RENDER_BEGIN/END`, `GROUP_FOCUS`, `GROUP_TOGGLE`, `SETUP_SAVE_BEGIN/END`, `WORK_TIMEOUT`; alte Save-Marker bleiben erhalten. Nur anonyme Sessionkorrelation, monotone Zeit, festes Medientypkürzel und begrenzte Zähler. Keine Gruppen-/Portalnamen, Kanal-IDs, Hostnamen, URLs oder Zugangsdaten. Fokusmarker werden gedrosselt.

Keine Änderung an Widgetrouten, BINGIE-Dateien/-Writer, Skinshortcuts-Profilen, Player, .42-Kompatibilitätsmodus, EPG-Mapping, Artwork-Pipeline, Resume/Autoplay, Fernbedienungs-Keymaps oder Geräteeinstellungen. Keine Geräteaktion auf Box A/B. Nur der eigene Einrichtungsassistent und seine Sprach-/Versionsressourcen ändern sich.

Die reale Geräteabnahme einschließlich nativer Renderzeiten, Fernbedienung, Anbieteranmeldung, Speichern und Kodi-Neustart bleibt **NOT_TESTED**; siehe Android-Anleitung.
