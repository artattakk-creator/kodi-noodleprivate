# .50 – tatsächliche BINGIE-Home-Integration, nur nach Einzelfreigabe

Dies ist ein **Prüfarchiv, kein installierbarer Skin**. Nicht in ein Kodi-Skinverzeichnis entpacken. Es ändert keine Box. Die eigentliche Aktivierung erfolgt ausschließlich über die geprüfte .50-Oberfläche nach privater Gerätesicherung und ausdrücklicher Bestätigung. Hostreferenz: veröffentlichtes `skin.titan.bingie.mod-2.2.3.zip` und `script.skinshortcuts-2.1.0.zip` aus `AchillesPunks/repository.titan.bingie.mod/omega`. SHA256 in `manifest.json` und `resources/bingie50_reference.json`.

## Vier genau abgegrenzte Dateien

| Datei | Änderung |
|---|---|
| `xml/IncludesHomeWidgets.xml` | Zwei neue Includes: `XCMate50.LiveRow` mit kleinen Senderlogos und `XCMate50.Hero`. Kein Ersetzen bestehender Film-/Serienlayouts. Die bekannte .46-Programme-Card-Erweiterung wird als additive Variante akzeptiert und erhalten. |
| `xml/IncludesHomeBingie.xml` | Hero wird wirklich im bestehenden Home-Hauptcontainer gerendert. Die bisherige Detailfläche und fixe Fokusrahmen werden nur beim Fokus auf einem .50-Live-Sender verborgen, damit sich Texte/Rahmen nicht überlagern. Header und andere Reihen bleiben erhalten. |
| `shortcuts/template.xml` | In allen acht nativen Widgetpositionen entscheidet ein enges Bedingungspaar: normale Quelle → unveränderte `widget_base`-Parameter; XCMate-Live-URL mit `home50=1` → `XCMate50.LiveRow` mit derselben nativen Control-ID. Die neue Live-Leiste besitzt kein Kürzungslimit. |
| `shortcuts/overrides.xml` | Drei native Widgetkandidaten `XCMate · Live-TV`, `XCMate · Filme`, `XCMate · Serien`. Der Original-Skinshortcuts-Selektor erhält direkt `widgetPath`, `widgetTarget`, `widgetType`, `widgetName`. Kein Navigieren zu Portalgruppen als Ersatz. |

`REVIEW.patch` zeigt den vollständigen Unterschied. Das Prüf-ZIP enthält dieselben Kandidaten und die Lizenz. Es enthält **keine private Gerätesicherung** und ersetzt diese nicht. Die installierte Box kann bereits zulässige oder unbekannte Änderungen haben; maßgeblich ist immer die vor Ort geprüfte SHA256. Unbekannte Dateistände werden blockiert, nicht überschrieben.

## Prüfung, Zustimmung, Anwendung

1. .50 als XCMate-Update installieren. Keine Neuinstallation und kein Zurücksetzen. Ohne laufende Wiedergabe **XCMate → Einstellungen → Aussehen und Darstellung → Widgets** öffnen. Drei Auswahlen: Live-TV, Filme, Serien. Kontextmenü → **BINGIE-Home-Layout prüfen/vorbereiten**. Bei Live-TV wird dies auch angeboten, wenn der Hero-Patch noch fehlt.
2. .50 prüft aktive Skin-ID, Version 2.2.3, Skinshortcuts 2.1.0, bekannte Quelldatei-Hashes, Schriftarten und einen inaktiven nativen Editor/Builder. Originale und Kandidaten werden privat unter dem XCMate-Profil in `widget50_plans/<ID>/` gespeichert: Modus 0600, SHA256, tatsächlicher Rücksicherungstest in einer separaten privaten Prüfdatei. Noch keine Skinänderung.
3. Alle vier Vorher-/Nachher-Prüfsummen im Textfenster prüfen. Erst **„Ja, diese vier Skindateien freigeben“** führt die Änderungen aus; Standard ist Abbrechen. Definitionen werden vor den Aufrufern installiert, Rollback umgekehrt. Vor jedem atomaren Dateiaustausch wird der aktuelle Hash erneut geprüft. Die native BINGIE-Skinshortcuts-API baut Home neu und lädt den Skin ausschließlich nach eigenem erfolgreichem Build. Keine Hash-/Cachelöschung und kein direkter Eingriff in das generierte `script-skinshortcuts-includes.xml`.
4. Nach Abschluss Live-TV erneut auswählen, freie Home-Position wählen und die **separate** Verknüpfungsvorschau prüfen. Die Profilspeicherung ändert nur die ausdrücklich gewählte freie Position bzw. die ausdrücklich ausgewählte eigene Live-Verknüpfung. Film-/Serienverknüpfungen werden nie ersetzt. Bereits richtige Verknüpfungen bleiben samt Namen und Reload-Hooks bestehen.

Für unbekannte/noch nicht gespeicherte/umbenannte Home-Profile oder Einzelwidgetmodus gibt es keine geratenen Profileditierungen. Die native BINGIE-Einrichtung kann nach ausdrücklicher Auswahl geöffnet werden. Dort: Home → gewünschte Widgetposition → Widgetauswahl → **XCMate · Live-TV / Filme / Serien**. Diese Kandidaten sind nach Aktivierung des separat freigegebenen Patches echte native Quellen, keine URL-Textanzeige. Einzelwidgetmodus bei Bedarf bewusst im nativen Editor ändern; .50 ändert diese Benutzereinstellung nicht selbst.

## Rückrollen / Unterbrechung

Unter Widgets → Kontextmenü → **Verifizierte Widget-Sicherung zurückrollen**. Angewandten bzw. unterbrochenen Plan auswählen und Wiederherstellung ausdrücklich bestätigen. Alle Backup-/Kandidaten-Hashes werden erneut geprüft; jeder aktuelle Zielhash muss genau Vorher oder Nachher entsprechen. Spätere Fremdänderungen führen zur Sperre **ohne Überschreiben**. Eine normale Schreibstörung stellt bereits geänderte eigene Dateien zurück; ein Prozessabbruch bleibt anhand von Originalen, Kandidaten und Zustandsjournal explizit wiederherstellbar. Verknüpfung und Skinlayout haben getrennte Pläne. Kein Download-/Cover-/EPG-Reset.

Bei nativ fehlgeschlagenem BINGIE-Neuaufbau gilt die Anzeige als FAIL; ein verifizierter gespeicherter Profilwert ist kein Home-Pixel-PASS. Bei unbekannten späteren Skinversionen nicht die öffentlichen Originaldateien aus diesem Repository über die Geräteinstallation kopieren. Die private Sicherung bewahren und den tatsächlichen Dateistand prüfen lassen.

## Geräteabnahme bleibt offen

Original-Compiler/Profilleser und 88-Sender-Daten werden am Host getestet. Skinreferenzsimulation ist kein Android-Test. Fokuswechsel, native vertikale Navigation zwischen Reihen, Logo-/Bilddecodierung, OK/Back, Neustartpersistenz und Medien-Autorefresh auf Box A bleiben **NOT_TESTED**. Kein automatischer Merge, kein Release und keine Anwendung auf Box A durch die Entwicklung.
