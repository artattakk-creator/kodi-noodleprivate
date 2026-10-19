# XCMate 0.1.27 – drei BINGIE-MOD-Widgetreihen

**Testkandidat; produktiv bleibt 0.1.26.** Keine automatische Skinänderung.
Die Routen sind mit strikten Kodi-ListItems/Metadaten lokal getestet. Auf einem echten
Android-TV mit Titan BINGIE MOD sind Anordnung, Renderer, Fokus und konkrete Menünamen
**noch nicht geprüft**. Die installierte BINGIE-MOD-Version beim Test protokollieren.

## Vorbereitung

1. Test-ZIP aus dem [Implementierungsbericht](IMPLEMENTIERUNG_027_KATALOG_WIDGETS_EPG_DE.md)
   nach SHA-Prüfung in Kodi installieren und Kodi vollständig neu starten.
2. In XCMate → Einstellungen → Accounts & Portale gewünschten Xtream-Account aktivieren.
   Unter Startkanal & Startgruppe den vorhandenen Startkanal kontrollieren; keine Zugangsdaten
   oder EPG-Zuordnungen überschreiben. Gruppen je Medienart aktiviert lassen.
3. Vorhandenen Katalog einmal erfolgreich laden. Bei leerem Cache zeigen die neuen Film-/Serien-
   Seiten „Katalog im Hintergrund laden“. Danach sind die neuen Routen lokal verfügbar.
   EPG importiert nur echte Quellen; fehlendes EPG wird durch Widgets nicht erfunden.
4. Vorhandene Homescreen-Reihen und Widgetquellen notieren oder die vom Skin angebotene
   Sicherungsfunktion verwenden. Bestehende Reihen zunächst behalten.

## Exakte Quellen

`PORTAL_ID` ist die interne Account-ID, **kein Host und kein Passwort**. Die drei fertigen
URIs werden mit der richtigen ID unter XCMate → Einstellungen → Darstellung & Sprache →
„BINGIE-MOD-Widgets einrichten“ angezeigt. Sie lassen sich auch über die dortigen drei
„Widget-Quelle“-Ordner im Kodi-Widget-Quellenauswahldialog auswählen.

| Reihe | Route | Karten und Auswahl |
| --- | --- | --- |
| 1 · Live-TV | `plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=PORTAL_ID` | Aktive Gruppe des tatsächlichen Startsenders, Startsender zuerst; Logo, echte Now/Next-Werte; OK spielt direkt |
| 2 · Neueste Filme | `plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=PORTAL_ID` | Filmcover; OK öffnet XCMate-Detailseite, nicht ungefragt den Film |
| 3 · Neueste Serien | `plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=PORTAL_ID` | Seriencover; OK öffnet Serien-/Staffel-/Folgendetails |

Die URLs bleiben stabil und enthalten ausschließlich Action und Portal-ID. Ein anderes
aktives Portal ersetzt nicht still den Account einer bestehenden expliziten Widget-URL.

## Manuell in BINGIE MOD einrichten

1. Skin-Einstellungen öffnen, dort **Hauptmenü konfigurieren / Menü anpassen** wählen.
   Je nach installiertem Skinbuild heißen diese Punkte anders. Ziel ist der Widgeteditor
   des gewünschten bestehenden Home-Menüpunkts, keine Bearbeitung der Skin-XML-Dateien.
2. Eine zusätzliche Widget-Reihe anlegen. Als Quelle **Video-Add-ons → XCMate → Einstellungen →
   Darstellung & Sprache → Widget-Quelle 1: Live-TV aus Startkanalgruppe** auswählen.
   Im Quellendialog gegebenenfalls „Hier als Widget verwenden“/„Diesen Ordner verwenden“
   wählen, statt einen einzelnen Sender auszuwählen. Name „XCMate · Live-TV“.
3. Zwei weitere Reihen auf die gleiche Weise aus **Widget-Quelle 2: Neueste Filme** und
   **Widget-Quelle 3: Neueste Serien** anlegen; Reihenfolge Live-TV → Filme → Serien festlegen.
4. **Live-TV:** Logo-/Querformatkarten und verfügbare Titel-/Plotzeile wählen, nicht alle Logos
   als 2:3-Filmplakate strecken. Now/Next steht in `XtreamMate.Now`/`XtreamMate.Next` und im
   normalen Kodi-Plot. Der Skin muss den Plot in seiner Infodarstellung anzeigen; spezielle
   XCMate-Properties werden von fremden Skins nicht automatisch in jede Kartenansicht eingebaut.
5. **Filme/Serien:** Posterformat **2:3**, horizontale Reihe, Titel und Infobereich aktivieren;
   Fanart/Background über ListItem-Art, soweit vom gewählten Layout unterstützt.
6. Speichern und auf den Homescreen zurückkehren. Initiale lokale Indizierung/Artwork läuft
   im Hintergrund; einmal Widget aktualisieren oder Home neu öffnen, wenn Bilder erst danach
   fertig wurden. Keine periodische vollständige Katalogaktualisierung pro Hover konfigurieren.

Die genaue deutsche Menübeschriftung und unterstützte Kartenansicht lassen sich ohne
installierte Skinversion nicht belastbar vorgeben. Beim Gerätetest Screenshot/Version und
abweichende Schritte ergänzen; keine unbestätigte automatische Einrichtung verwenden.

## Daten und Grenzen

- Live zunächst 48 Sender pro Seite plus korrektes Weiterblättern; Startsender auf erster
  Seite. Aktivierte Gruppe aus tatsächlichem Startsender, sonst gespeicherte Startgruppe,
  sonst erste gültige Gruppe. Manuelle EPG-Zuordnung hat Vorrang vor alten Aliasdaten.
- Neuheitenwidget 24 Karten plus „Alle anzeigen“; Rail standardmäßig 100 Titel, zehn Tage
  „Neu“-Kennzeichnung. Ältere/undatierte Titel erhalten ehrliche Kennzeichnung in Plot und
  `XCMate.AddedStatus`; Anzahl/Zeitraum in Kodi-XCMate-Einstellungen änderbar.
- Kein Listen-/XMLTV-HTTP pro Widgetaufruf. Lokaler Index und lokale Bildpfade; Artwork aus
  begrenztem Hintergrundcache. Bei fehlendem Katalog verständliche Statuskarte statt Fakefilm.
- Ein Konto-/Gruppenwechsel kann eine vorhandene Widgetquelle bewusst leer machen. Das ist
  keine Aufforderung, einen anderen Account ungefragt zu verwenden.
- Neue Quellen derzeit Xtream; bisherige generische Widgetrouten bleiben verfügbar.

## Geräteabnahme und Rückbau

Drei horizontale Reihen fotografieren, Live-OK und Film-/Seriendetails prüfen, nach Stop/
Vollbild zurückkehren, Fokus erhalten. Netzwerk trennen und bereits gefüllte Reihen erneut
öffnen: keine Katalogdownloads, gecachte Titel/Artwork bleiben verfügbar. Warm-/Kaltzeiten
und Profilgröße messen. Fehlende neue Providerdaten dürfen ältere lokale Titel nicht als
frisch importierte Neuerungen ausgeben.

Zum Rückbau ausschließlich die drei neu angelegten Reihen im Skineditor entfernen bzw.
notierte alte Quellen wieder einstellen. XCMate ändert weder Skin-Dateien, fremde Add-ons,
Benutzer-Widgets noch globale Keymaps. Keine Skin-Dateien ersetzen oder Nutzerdaten löschen.
