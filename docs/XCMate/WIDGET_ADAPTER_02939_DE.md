# .39 – bestehende BINGIE-Widgets und getrenntes Opt-in

Die vorhandenen drei Routen bleiben bestehen; keine Nutzerverknüpfung und keine Titan-Datei wurde verändert:

```text
plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=PORTAL_ID
plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=PORTAL_ID
plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=PORTAL_ID
```

Live ist auf zwölf Sender der konfigurierten Startgruppe begrenzt, Startsender zuerst. Film-/Serienreihen verwenden weiter den bestehenden lokalen Katalog. Keine Widget-/Fokus-Aktion startet TV oder lädt pro Kachel Provider-EPG. Native dynamische Bildanforderungen von Kodi sind von EPG-Providerabfragen zu unterscheiden.

`XtreamMate.Now/Next/Start/Stop/Progress` werden mit echten lokalen Werten befüllt; `Progress` liegt zwischen 0 und 1 beziehungsweise ist bei unbekanntem Event leer. Derselbe Inhalt steht als Standard-Video-Plot zur Verfügung. Keine Verwendung von Kodi-Watched-/Resume-Progress für Sendungsfortschritt. `cacheToDisc=False` sorgt dafür, dass ein erneuter Plugin-Aufruf frische lokale Zeitwerte berechnet.

Ein bereits im Skin zwischengespeichertes ListItem braucht einen Widget-Refresh oder eine passende Skinbindung, damit seine Anzeige weiterrollt. **Fortlaufendes Home-Rollover und tatsächliche BINGIE-Darstellung sind NOT_TESTED.** Die lokale Berechnung ist hostgetestet, nicht automatisch jede Skin-Kachel. Falls BINGIE Now/Next/Progress nicht darstellt oder nicht aktualisiert, ist das ein offenes Abnahmegate, kein Beweis fehlender EPG-Daten.

Ein später ausdrücklich gewählter Adapter soll nur die vorhandene Zeile lesen: Standard-Plot als Fallback, getrennte Now-/Next-/Uhrzeittexte, ausschließlich echte EPG-Progresswerte und ein kontrollierter lokaler Refresh zum Eventwechsel. Er darf keine Nutzerwidgets ersetzen, keine Kodi-Keymap schreiben, keinen Vollkatalogreload auslösen und kein Provider-HTTP auf Fokus erzeugen. Vor Installation wären der konkrete BINGIE-Build, dessen Refresh-Mechanismus und ein sichtbarer Vorher-/Nachher-Test erforderlich. Dieser Adapter wird mit .39 nicht automatisch installiert oder als bereits bewiesene Skinfunktion ausgegeben.
