# Medienreihen 0.1.29.9 – separater Testkandidat zu #74

Basis: Navigations-Hotfix 0.1.29.8, Draft PR #76. Keine Veröffentlichung,
kein reguläres Update. Zuerst 0.1.29.8 auf Android abnehmen.

## Oberfläche

Kategorien und Suche stehen im festen Kopf. Darunter folgen Weiter ansehen
(112), Meine Favoriten (111), Neu hinzugefügt (110). Kodi scrollt den
494 Pixel hohen Ausschnitt vertikal; jede Reihe scrollt horizontal.
Poster: 164 × 246 Pixel bei 720p, mit 64 Pixel hoher mehrzeiliger Titelzone.
Leere Reihen werden auf ihre Überschrift verkürzt und beim Fokus übersprungen.
Fokus und ausgewähltes Objekt bleiben bei Details/Zurück erhalten.

Die Datei MEDIA_RAILS_0299_LAYOUT.svg zeigt ein geometrisches Schema,
keinen aufgenommenen Kodi-Bildschirm. Schrift und Lesbarkeit am TV bleiben
Teil der Geräteabnahme.

## Native Steuerung und Schutzgrenzen

Der Kodi-grouplist 600 übernimmt Clipping und Scrollposition. Kodi 21.2
GUIControlGroupList::OnMessage(GUI_MSG_FOCUSED) erkennt auch verschachtelte
Fokusziele über GetControl(). Python Window.getControl unterstützt diesen
Typ nicht; deshalb wird nur die umgebende normale Gruppe 620 angesprochen.
Die Tests verweigern Python-Zugriff auf 600 ausdrücklich.

Vorhandene interaktive IDs bleiben erhalten. Die Tests frieren 13 Module
sowie Playback-, Close-, Such- und Owner-Methoden aus dem Hotfix ein.
Keine Änderung an Live-TV, EPG, Datenbanken oder Speicherbudget.

## Theme-Kompatibilität und spätere PR-50-Integration

PR #50 bleibt unverändert, bis eine positive Android-Abnahme vorliegt.
Die Theme-Hooks über IDs 110/111/112 bleiben erhalten. Sein derzeitiger
XML-Decorator sucht Poster nur in direkten Wurzelkindern; dieser Selektor
muss bei der späteren Integration auf `.//control` erweitert werden.
Nur Layout-Kinder vom Typ itemlayout/focusedlayout dekorieren, damit keine
Doppel-Dekoration entsteht. Shade erhält exakt die jeweilige Poster-Geometrie.

Der dort fest platzierte Such-Icon muss die neue Suchposition (y=80 auf
Landing, sonst y=32) übernehmen; der bisher feste Rail-Gradient darf nicht
über Titel/Text wandern. Er gehört als Dekoration in die jeweilige Reihe
oder entfällt. Mehrzeilige Textboxen dürfen nicht wieder in einzeilige Labels
umgewandelt werden. Kategorie-/Suchbuttons, Mausflächen, Fokusziele und
Reihenfolge bleiben unverändert. Diese Anpassungen sind ein konkreter
Integrationsauftrag, noch keine getestete Kombination mit SpacePremium.
Die 98 Originalassets werden unverändert weiterverwendet.

## Android-Abnahme – NOT_RUN

1. Erst den Hotfix-Testplan vollständig bestehen lassen; Kodi-Profil sichern.
2. Separates 0.1.29.9-ZIP installieren, Filme und Serien jeweils 10-mal öffnen.
3. Mit Weiter-ansehen- und Favoritenbestand: Startfokus 112, Down → 111 → 110,
   Up zurück bis Kategorien. Suche im Kopf erreichbar, Down zur ersten Reihe.
4. Horizontale Auswahl am rechten Rand, Details öffnen, Back: gleiches Objekt.
5. Jede Reihe muss vollständig in den Ausschnitt scrollen; Titel, zwei Zeilen,
   Fokusrahmen und Poster dürfen nicht abgeschnitten sein. Kleine und lange Titel,
   1080p/4K-Skalierung sowie echte IR-Fernbedienung prüfen.
6. Mit leeren Weiter-/Favoritenreihen: Neu vollständig erreichbar, keine leeren
   Fokusziele. Keine Netzwerkabfragen durch reine D-Pad-Bewegung.
7. Kategorien → Gruppe → erweiterte Ansicht → Details/Staffel/Episode und zurück;
   schnelle zwei absichtliche Back-Drücke, Suche, Resume, Play/Stop erneut prüfen.
8. EPG und Live-TV unverändert testen. 20 Minuten Laufzeit, Fokusfehler/Freeze zählen.

Bei Fehler: Kandidat nicht freigeben, dokumentierter Rückfall 0.1.29.6 bleibt.

## Host-Verifikation

564/564 Tests bestanden, 79,825 s. ZIP-CRC, sichere Pfade, vollständiger
Quellvergleich, Python-AST und byteidentische unabhängige ZIP-Reproduktion
bestanden. Hash und Paketgröße stehen in TESTERGEBNISSE_0299_MEDIA_RAILS.json.
Dies ersetzt keine native Android-Abnahme. Der gestapelte PR richtet sich
zunächst gegen den Hotfix-Branch; dessen Workflow startet nur bei PRs nach main.
