# XCMate .50 – Widgetverknüpfung und tatsächliche BINGIE-Home-Integration

Stand: 28.10.2026 (Europe/Berlin). Auftrag #252 vollständig mit den neuen .49-Android-Befunden gelesen, Referenzen #250, PR #251/.48 und PR #253/.49. Basis `main` .49: `bc278a32a0e9a3bc8763189c09ffa9195d4dddf3`. Branch `hotfix/xcmate-02950-bingie-home`.

## .49 bleibt aus Nutzersicht FAIL

Die neue Geräteabnahme auf Box A belegt: Der gewünschte direkte Einrichtungsablauf und Home-Hero waren in .49 nicht geliefert. Die 2.035 bestandenen Hosttests der .49 sind kein Android-PASS. Die .49-Dokumentation bleibt historisch erhalten; die neue .50-Abnahme beginnt vollständig mit NOT_TESTED.

| Pfad | .47 | .48 | .49 | .50 |
|---|---|---|---|---|
| Widgets unter Darstellung | Dialog mit Status, URL-Texten und optionalem Adapter | zusätzlich eigenständige Hero-Demo | drei browsebare Quellordner, Speicherung weiterhin im nativen BINGIE-Picker | exakt drei direkte Aktionen **Live-TV / Filme / Serien**, Home-Ziel und tatsächliche bestätigte Profilspeicherung |
| Native Bindings | Laufzeitfunktionen vorhanden; kein direkter XCMate-Profilwriter | gleich | nur Browse-Protokoll anhand älterer 2.0.3-Referenz getestet | bestehende Skinshortcuts-2.1.0-Profildatei; private Sicherung, Auswahl einer freien Position oder ausdrückliche Umstellung eines eigenen Live-Bindings, nativer Reader liest Ergebnis |
| Live Home | native große Kacheln / kein XCMate-Hero-Consumer | separate `WindowXMLDialog`-Vorschau, Skinintegration ausdrücklich blockiert | gleich | vier konkret vorbereitete Skinänderungen: echte Home-Region, kleine horizontale Logos, nativer Template-/Quellanschluss, nur nach Freigabe |
| Daten / Klickziele | drei vorhandene Endpunkte | gemeinsame lokale EPG-/Artwork-DTOs | unverändert | Medienendpunkte unverändert; Live-Endpunkt mit explizitem `home50=1` verwendet ausschließlich die konfigurierte Startgruppe |

Im ältesten relevanten Projektcode `.27` waren die drei Quellfunktionen direkt unter Darstellung verlinkt; `widget_setup` zeigte dort bereits eine Anleitung. Ein automatischer Profilwriter aus .47/.48/.49 ist im verglichenen Code nicht belegt. Der frühere Nutzerablauf konnte über die native BINGIE-Auswahl speichern; daraus folgt kein Beleg für eine damalige automatische XCMate-Skinspeicherung.

## Was die Gruppenkacheln erklären – und was nicht bewiesen ist

`home_live → Router._live_groups()` ist der reguläre Gruppenbrowser. `widget_live_start_group` liefert im geprüften .49-Code Sender aus einem lokalen Katalog, nicht diese Gruppenauswahl. Ein aktueller Geräte-Dispatch-Trace liegt zu dem gemeldeten Klickpfad nicht vor; der exakte .49-Aufruf wird deshalb nicht nachträglich behauptet. Sicher ist: .49 gab dem Benutzer Quellverzeichnisse statt der verlangten bestätigten Verknüpfung, und die separate Hero-Demo war keine Home-Integration.

.50 entfernt diese Mehrdeutigkeit beim Speichern: Der Zielwert wird konkret und überprüfbar auf den richtigen Widget-Endpunkt gesetzt. Eigene Legacy-Live-Bindings mit `home_live`, `live_groups` oder `widget_groups` und **derselben expliziten Portal-ID** können nur nach ausdrücklicher Wahl auf den neuen Live-Endpunkt umgestellt werden. Fremde Konten und Film-/Serienbindings werden nicht ersetzt. Neue datensparsame Marker unterscheiden `WIDGET50 event=BINDING_SAVED` (nur Profilnachweis) und `HOME50 source=LIVE_START_GROUP code=… rows=…` (tatsächlich geladene Quelle); keine URLs, Zugangsdaten, Titel oder Profilpfade im Log.

Ein weiterer deterministisch reproduzierter Unterschied: Der allgemeine `initial_group()` priorisiert die Gruppe des Startsenders vor `start_group_id`. Das bleibt für bestehende Navigation unverändert. Der neue Home-Pfad prüft die explizite Startgruppe separat; ein Startsender in einer anderen Gruppe zieht diese nicht mehr ins Home-Widget. Bei fehlender/gesperrter Gruppe gibt es eine ehrliche leere Quelle samt Diagnose statt Gruppenmenü oder Rückfall auf alle aktivierten Gruppen.

## Native Quelle erstmals exakt geprüft

Aus dem veröffentlichten BINGIE-Repository wurden **Skin 2.2.3** und **Skinshortcuts 2.1.0** gelesen. Der vorige .49-Test verwendete nur den älteren 2.0.3-Explorer; diese Referenz reichte für den real geforderten Ablauf nicht aus.

Skin-Archiv-SHA256: `7216dcf7efeac7cb668cde97bdde45b681ed77b5e9007368d3b46c3c98e52e8b`. Weitere Quellen-/Datei-/Auszugshashes in `bingie223_reference50.json` und der gepackten `resources/bingie50_reference.json`. Acht unveränderte öffentliche XML-/Lizenzdateien und unveränderte Originalmethoden aus Skinshortcuts unter Testfixtures, Lizenzen mitgeliefert. Dies sind öffentliche Referenzdaten, kein Export von Box A.

Der Original-Profilleser verarbeitet nach dem Speichern die reale `.properties`-Datei erneut und liefert `widgetPath`, `widgetTarget`, `widgetName`, `widgetType` an der gewählten Position zurück. Der Original-Templatecompiler verarbeitet alle acht Positionen. Der originale Widget-Registry-Loader sieht die drei neuen nativen Kandidaten. Kodi-21.3-Header bestätigen den Abbrechen-Standard `DLG_YESNO_NO_BTN = 10`.

## Direkte Speichervorgänge

Der sichere Writer unterstützt ein bereits gespeichertes, eindeutig identifiziertes BINGIE-Home-Profil: aktive Skin-ID/Version, Skinshortcuts-Version 2.1.0, erzwungene nicht geteilte Menüs, vorhandene `skin.titan.bingie.mod-mainmenu.DATA.xml`, eindeutige Home-ID `10000` und bestehende Home-Properties. Keine Materialisierung unbekannter Defaults und kein Raten nach übersetzten Namen.

Es wird nur **eine** vorhandene Datei im aktuellen Kodi-Profil verändert: `addon_data/script.skinshortcuts/skin.titan.bingie.mod.properties`. Die fünf gewählten Widgetfelder werden gezielt aktualisiert/ergänzt; alle anderen Werte und Formatbytes bleiben erhalten. Nicht leere Film-/Serienpositionen werden nicht überschrieben. Bereits passende Medienbindings behalten ihren Namen und Reload-Hook. Eigene Live-Umstellung erfordert explizite Zielwahl und separate Speichervorschau. Neue Links pinnen die Portal-ID und verwenden die vorhandenen XCMate-Reload-Hooks; Live erhält zusätzlich einen minutenweisen nativen Info-Token für Now/Next-Wechsel.

Die Originaldatei, Kandidat, SHA256 und tatsächlicher privater Rücksicherungstest sind vor jeder Zustimmung vorhanden. Änderungen nach der Vorschau, Profilwechsel, andere Skinversion, beschädigte Daten, zu große ARM32-Profile, paralleler nativer Editor/Builder und laufende Wiedergabe werden blockiert. Keine native Stop-Anweisung als Vorbereitung. Beim Speichern wird ausschließlich der native, im echten Home.xml belegte Skinshortcuts-Build aufgerufen. „Profil gespeichert / Neuaufbau angefordert“ behauptet keinen bereits sichtbaren Home-Erfolg.

Bei unbekanntem/noch nicht gespeichertem/umbenanntem Home oder Einzelwidgetmodus bleibt der direkte Writer **BLOCKED**. Auf ausdrücklichen Wunsch wird der originale BINGIE-Editor geöffnet. Nach Aktivierung des separat geprüften Patches stehen dort echte **XCMate · Live-TV / Filme / Serien**-Kandidaten bereit. Das ist eine reale assistierte Ausweichmöglichkeit, kein One-Click-Versprechen für ein unbekanntes Profil. Kein globales Umschalten von Benutzereinstellungen.

## Tatsächlicher Home-Renderer

Die Integration arbeitet in `IncludesHomeBingie.xml`, `IncludesHomeWidgets.xml`, `shortcuts/template.xml` und `shortcuts/overrides.xml`. Sie wird **nicht automatisch installiert**. Die Oberfläche erstellt einen lokalen prüfbaren Plan und zeigt alle vier Vorher-/Nachher-SHA256 an. Nur eine gesonderte ausdrückliche Bestätigung wendet ihn an; vorher bleibt der Skin unverändert. Unbekannte Dateistände werden blockiert. Die bekannte additive .46-Programme-Card-Variante wird erhalten.

Der Hero liegt in der echten oberen Home-Region, die kleine horizontale Leiste im vorhandenen Widget-Grouplist. Native globale `ListItem`-Properties beziehen sich wie in BINGIE auf den fokussierten Sender; keine variable Container-ID-Erfindung, kein `RunPlugin`-/Datenbank-/Netzaufruf im Fokuscallback. Der Hero verwendet ausschließlich das verifizierte ProgrammeImage oder den ehrlichen neutralen Programme-Platzhalter. Kleine Logos haben eine eigene Property. Nur OK verwendet den bewährten Player-URL; keine neue Playback-Engine und kein Fokus-Autoplay. Die .42-Stopstrategie bleibt bytegleich.

Alle acht Templatepositionen behalten ihre Control-ID. Nur ein qualifizierter XCMate-Live-Pfad mit `home50=1` wählt den neuen Consumer ohne Kürzungslimit. Für Filme/Serien bleiben die nativen Widgetparameter erhalten. Fremde Widgets und vorhandene Layouts werden nicht ersetzt. Detailtexte und globale fixe Fokusrahmen werden nur beim Fokus auf der neuen Live-Leiste ausgeblendet, um Überlagerungen zu vermeiden.

## Rückrollen und Grenzen

Private Pläne unter `widget50_plans/<ID>/` enthalten Originale, Kandidaten, Prüfsummen und Zustandsjournal. Definitionen werden vor den Aufrufern installiert; Wiederherstellung erfolgt in umgekehrter Reihenfolge. Normale Schreibfehler stellen bekannte eigene Änderungen zurück. Prozessabbrüche zwischen Dateien sind explizit wiederherstellbar; fremde spätere Änderungen werden nicht überschrieben. Die Tests provozieren Fehler vor/nach jeder der vier Ersetzungen sowie Prozessabbrüche und prüfen die exakten Ursprungsbytes.

Kein Box-A-Zugriff, kein Profil-/Cache-/Datenreset, keine Coverlöschung, kein Downgrade und kein automatischer Merge. Die vorhandenen Service-, Player-, EPG-, Portal-, Artwork-, Medien-/Widget-Reader und Autorefresh-Implementierungen bleiben bytegleich; nur die dokumentierten sechs bisherigen Quelldateien erhalten Version-/Sprach-/Routeänderungen. Der echte Android-/IR-/Bild-/Back-/Neustarttest bleibt offen, siehe `ANDROID_ABNAHME_02950_DE.md`. Layoutgeometrie und Originalcompiler sind keine Android-Pixelabnahme.
