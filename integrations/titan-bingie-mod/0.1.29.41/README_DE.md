# XCMate .41 – optionaler Titan-BINGIE-MOD-Adapter

**REVIEW_ONLY / NICHT INSTALLIERT / ANDROID NOT_TESTED.** Dieses separate Include ist kein Kodi-Add-on und nicht Bestandteil einer automatischen Skin-Einrichtung. XCMate .41 überschreibt weder Home.xml, Includes.xml, bestehende Widgets noch Skinshortcuts. Die enthaltenen Dateien und Kontroll-IDs sind versioniert; kein Installer wird ausgeführt.

Ziel: `skin.titan.bingie.mod` **2.2.3**, Kodi21, 720p-Koordinaten mit Kodis nativer Skalierung auf1080p. Panel90241 zeigt höchstens12 Live-Sender, Panels90242/90243 jeweils24 Filme/Serien. Logo80×45 innerhalb160×90-Kachel =50% der Kachelbreite/-höhe, proportional und zentriert. Die tatsächliche bisherige Logoabmessung auf Box B ist nicht gemessen; keine behauptete exakte Halbierung des unbekannten Alt-Skins. Kompakte klare Zeilen und Fokusrahmen statt Spotlight.

## Fokus-EPG und Sicherheit

Fokussierte Live-Kachel wird über `Container(90241).ListItem.Property(XCMate.WidgetToken41)` erkannt. Der XCMate-Service liest nur den bereits publizierten begrenzten RAM-Eventbank und aktualisiert `Window(Home).Property(XCMate.Widget41.Now/Next/Times/NextTime/Progress)` höchstens einmal pro Sekunde. Echte Ereigniszeiten bestimmen NOW/NEXT und Prozent; keine Watch-/Resume-Prozentwerte. Fehlende/veraltete Daten sind ehrlich fehlend. Kein HTTP-/SQL-/Popup-/Playerstart beim Fokus. OK nutzt weiterhin die vorhandene Item-Aktion; Medien öffnen Details, Live startet nur durch ausdrückliches OK.

Die Bindung ist **aus**, solange `Skin.HasSetting(xcmate41.adapter.enabled)` nicht ausdrücklich aktiviert wird. Das .41-Add-on setzt dieses Skinsetting niemals. Die normale, schon konfigurierte Startseite bleibt unverändert. Ohne Adapter kann die bereits vorhandene BINGIE-Reihe weiterhin den Kodi-Plot auswerten; das Add-on allein kann fremde Kachelgrößen nicht erzwingen.

## Vor Freigabe zu prüfen

1. Auf einer **Kopie** des Skins: `python tools/check_bingie_adapter_02941.py --skin-copy /pfad/zur/kopie`. Das Tool ist ausschließlich read-only, prüft ID/Version, XML-Syntax und90241–90243-Kollisionen. Ungültige XML-Eingaben werden nur mit Pfadhash/Zeile/Spalte diagnostiziert, niemals mit Originalinhalt oder Provideradresse.
2. Einbindeort und reservierten Raum der tatsächlichen Home-Ansicht prüfen. Das Include nutzt einen festen Bereich bei y270–684 in720p. Es darf nicht einfach über die bestehenden persönlichen Reihen gelegt werden. Seine Aktivierung braucht einen gesondert geprüften Home-/Include-Verweis und die ausdrückliche Nutzerfreigabe; diese Änderung ist **nicht** durchgeführt.
3. Verwendete Schriftarten, Fokus-/Poster-/Progressdarstellung, bestehende Startseitensteuerung,20 D-Pad-Wechsel und Rückkehr auf einer erlaubten Testinstallation prüfen. Jede Skin-/Shortcut-Konfiguration vor einem später genehmigten Eingriff anhand Kopie/Hashes sichern. Keine Box-A-Tests.
4. Reversibilität: nur später ausdrücklich genehmigte Include-Verweise und Enable-Setting zurücknehmen sowie die dazu neu hinzugefügte Datei entfernen; Originaldateien aus dokumentierter Kopie wiederherstellen. Kein Löschen generierter Skinshortcuts oder Widget-/Profilreset.

Bis zu dieser Freigabe/realen Abnahme bleiben #206 und der BINGIE-Darstellungsteil #26/#207 **BLOCKED / NOT_TESTED**, obwohl XML-/RAM-/Backend-Hosttests bestehen.

## Externes script.skinshortcuts – unabhängiger Fehler

Der Nutzerlog weist in seiner v2.1.0 `Element.getiterator()` unter Python3.11 aus; die moderne API ist `Element.iter()`. Das erklärt den API-Fehler, **nicht** die separate `mismatched tag`-Eingabe. Welche XML-Eingabe/Playlist tatsächlich fehlerhaft war, ist aus dem Stack nicht identifiziert. Keine XCMate-Python-Exception mit diesem externen Buildfehler gleichsetzen.

Quellprüfung 26.10.2026: `BigNoid/script.skinshortcuts` master meldet1.0.18 mit Python2.20 und verwendet nochgetiterator – **kein kompatibles Update empfehlen**. Die offizielle `xbmc/repo-scripts`-Matrix-Metadatei nennt2.0.3 mit Python3.0 und Quelle `mikesilvo164/script.skinshortcuts`. Das ist ein Python3-Abstammungsbeleg, **keine getestete Austauschfreigabe für die installierte BINGIE-v2.1.0**, und rechtfertigt keinen Downgrade. Ein kompatibles Paket muss mit der konkreten BINGIE-Fork/API sowie den tatsächlichen Eingabedateien geprüft werden. Weder Download noch Installation/Monkeypatch oder Fremddateiänderung wurden durchgeführt.

Quellen: https://github.com/BigNoid/script.skinshortcuts/blob/master/addon.xml und https://github.com/xbmc/repo-scripts/blob/matrix/script.skinshortcuts/addon.xml . #207 bleibt offen. Der XCMate-Widget-SQL-/Cachefix ist davon unabhängig bereits implementiert.
