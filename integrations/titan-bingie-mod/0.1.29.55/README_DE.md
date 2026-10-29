# XCMate .55 – BINGIE-Prüfadapter, nicht angewendet

Dieser Ordner ist **kein installierbarer Skin**. ZIP nicht in ein Kodi-Skinverzeichnis entpacken. Die Entwicklung hat keine Geräte-/Profil-/Skindateien verändert. Native Widgetauswahl und Film-/Serienwidgets funktionieren ohne diesen optionalen Hero-Adapter.

Die vom Nutzer im Chat übergebene Startseitenvorlage ist das Layoutziel: echte vorhandene BINGIE-Navigation links, großes 16:9-Sendungsbild links oben, EPG rechts, schmale blaue Senderbuttons darunter, danach vorhandene Film-/Serienposter. Beispiele aus dem Bild sind nicht im Add-on hinterlegt. Physische Reihenfolge über die native BINGIE-Konfiguration festlegen; keine besetzten Positionen umschreiben. Die tatsächliche Darstellung auf Box B ist NOT_TESTED.

## Genau vier Änderungen

| Datei | Inhalt |
|---|---|
| `xml/IncludesHomeWidgets.xml` | Bestehende XCMate-Includes für 76 Pixel hohe Senderreihe und Hero aktualisiert. Proportionale Logos, blauer eigener Fokus, neutraler Textur-Fallback. Echte ListItem-/EPG-Eigenschaften, kein Playback bei Fokus. |
| `xml/IncludesHomeBingie.xml` | Hero im echten Home-Container, bisherige konkurrierende Details/Rahmen nur beim eigenen Live-Fokus ausblenden. |
| `shortcuts/template.xml` | Nur eigene Live-Quelle mit `home50=1` wird in allen acht möglichen Positionen zur Senderreihe; gleiche native Control-ID. Film-/Serienparameter und fremde Quellen behalten den Originalpfad. Kein 12-/24-Senderlimit. |
| `shortcuts/overrides.xml` | Bereits bewährte drei native Quellen; neuer Standardweg bleibt `Video-Add-ons → XCMate → Widgets`. |

`REVIEW.patch`, Kandidaten und Vorher-/Nachher-SHA256 in `manifest.json` sind aus der gepinnten öffentlichen BINGIE-2.2.3-Referenz reproduzierbar: `python tools/build_bingie_review_02955.py`. Herkunft, Lizenz und Skinshortcuts-2.1.0-Referenz sind dokumentiert. Nur diese Versionen und exakt bekannte Quelldateien werden akzeptiert. Zusätzlich kann der exakt bekannte eigene .50-Adapter auf .55 gebracht werden; unbekannte Zwischenänderungen blockieren sicher. Ein alter .50-Anwendungsbeleg wird nicht als bereits aktives .55-Layout ausgegeben.

## Freigabe und private Sicherung auf Box B

**Vor jeder tatsächlichen Anwendung ist eine gesonderte ausdrückliche Nutzerfreigabe erforderlich.** In dieser Lieferung wurde nur auf temporären Hostreferenzen vorbereitet, angewendet und bytegenau zurückgerollt.

Nach dieser Freigabe kann der erhaltene, bisherige Kodi-Aktionspfad `RunPlugin(plugin://plugin.video.xtreammate/?action=widget_skin50)` die konkrete Vorbereitung öffnen. Er ist bewusst kein neuer Widget-Manager und kein Eintrag im einfachen Quellordner. Nur mit beendetem Player und geschlossenem BINGIE-Editor ausführen. Aktive Skin-ID 2.2.3, Skinshortcuts 2.1.0, Schriften, vier Originalhashes und privates Profil werden geprüft. Keine Ausführung per Service/Startseite/Fokus/Update.

Vor der Bestätigungsfrage liegen private Originale, Kandidaten, Modus 0600, Hashbelege und tatsächlich zurückgeschriebene `restore-check`-Prüfdateien in `widget50_plans/<Plan-ID>/`. Die Vorschau zeigt alle Hashes. Erst „Ja, diese vier Skindateien freigeben“ wendet genau diesen Plan an. Standard ist Abbrechen. Danach baut der originale BINGIE-/Skinshortcuts-Generator Home neu. Keine direkte Änderung seiner generierten Home-Datei, kein Profilreset und keine automatische Umplatzierung der Widgets.

## Rückrollen

Den vorhandenen Aktionspfad `RunPlugin(plugin://plugin.video.xtreammate/?action=widget_restore50)` erst nach Freigabe öffnen, den richtigen Skinplan auswählen und die Wiederherstellung bestätigen. Alle Original-/Kandidatenhashes und aktuellen Zielhashes werden vor dem ersten Austausch erneut geprüft. Restore akzeptiert nur die bekannten Vorher-/Nachher-Zustände. Spätere Fremdänderungen: `TARGET_CHANGED_NO_OVERWRITE`, kein Überschreiben.

Normale Schreibfehler rollen bereits ersetzte eigene Dateien zurück. Prozessunterbrechungen bleiben mit Originalen/Kandidaten/Journaldaten ausdrücklich wiederherstellbar. Installation Definitionen vor Aufrufern, Restore umgekehrt. Vorhandene BINGIE-Profile sowie Film-/Serienbindings werden nicht verändert. Sicherung aufbewahren; dieses öffentliche Reviewarchiv ersetzt keine Gerätesicherung.

## Offene Freigabegates

Android-Anzeige, Sidebar, reale Native-Picker-Speicherung, 88+ Sender, Hero-Bildgleichheit, vertikales Scrollen zu Film-/Serienreihen, OK/Back, Neustart und Autorefresh: NOT_TESTED. Ein Host-Compiler-/Restore-PASS ist kein sichtbarer Geräte-PASS. Auf Box A nichts ausführen.
