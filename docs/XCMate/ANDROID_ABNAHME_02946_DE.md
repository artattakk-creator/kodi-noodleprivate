# XCMate 0.1.29.46 – Android-Gesamtabnahme Box B

**Neueste direkte Nutzerfreigabe im Chat vom27.10.2026:** Den bereits implementierten und gezielt getesteten Datenbankumbau nach vollständiger Regression in .46 mit aufnehmen. Diese spätere direkte Weisung ersetzt für diesen Kandidaten die zwischenzeitliche Verschiebung aus #241/#242. Grafische EPG-/Widgetteile und alle P0-Fixes bleiben enthalten. #242 wird nicht eigenmächtig geschlossen; weitere Konsolidierung/Abnahme bleibt separat nachvollziehbar.


**Alle .46-Fälle ANDROID_NOT_TESTED / NOT_TESTED.** Box B: RK3528 ARM32 (Hersteller-/Androidanzeige privat verifizieren; Logmeldungen widersprüchlich), Kodi21.3, Titan BINGIE MOD2.2.3, `live_exit_fullscreen42=EIN`, bisheriger dynamischer Artworkmodus. Box A ausgeschlossen. .45 auf main ist Entwicklungsbasis, keine vollständige neue Androidfreigabe. Historische .44-Alltags-Backs >20, positive Such-/Railbeobachtungen bleiben historisch; alte .43-FAIL werden nicht automatisch fortgeschrieben.

## Vorbereitung / zwingende Stop-Gates

1. PR/Version/ZIP/SHA prüfen, Installation nur nach bewusster Nutzerentscheidung als Update über .45. Kein Main-Merge/Produktivrelease durch Codex. Keine Deinstallation, kein Downgrade, Profil-/DB-/Artwork-/Cache-/Keymap-Reset; keine zusätzlichen USB-/SMB-/Migrationstests. Bestehende Portal-/Favoriten-/Startgruppen-/Resume-/Widgetwerte vorher privat festhalten.
2. Startsender → EIN Live-Back: Bild/Ton enden und Oberfläche reagiert. Bei Freeze/STOP_TIMEOUT sofort stoppen. Erst nach PASS Film-Back, dann weitere funktionale Gates. Die native .42-Stopstrategie bleibt erhalten; .46 ergänzt eine abgesicherte Late-Return-Erholung. Frühere Erfolge bleiben historisch, neue Timeoutbefunde dürfen nicht übergangen werden. 20er-Serie bei neuem Regressionsbedarf oder ausdrücklichem Wunsch, nicht ungefragt als bestanden markieren.
3. **Kein manueller EPG-Refresh ohne dokumentiertes BACKUP_VERIFIED.** Read-only vorhandene Revision/Quellen/Mapping/Coverage und Historie prüfen. Konsistente SQLite-Backup-API-Kopie, SHA/Größe/Manifest und private Ablage; laufende DB/WAL/SHM niemals einzeln austauschen. Danach höchstens EIN gesondert genehmigter vorhandener Refresh, kein Neuaufbau. Ohne dieses Gate Import-/Ergänzungstests BLOCKED.
4. Alte Guide-Daten enthalten eventuell nur Text. Für echte Bild-/Episode-Abnahme muss ein tatsächlich gespeichertes passendes Eventbild bzw. ein bewusst konfigurierter erlaubter Bildanbieter vorhanden sein. Fehlt dies: BLOCKED_METADATA_NOT_AVAILABLE/NO_IMAGE, kein erfundener Treffer und kein Refresh als Abkürzung. Neutrale Darstellung separat als erwarteten Fallback testen.
5. Bestehende drei Widgetzuweisungen privat vor/nach vergleichen. Nicht neu einbinden. Automatische sichtbare Aktualisierung benötigt nativen Reload-Hook; Logo/Fokus benötigt Renderer. Optionaler Adapter darf ausschließlich nach **eigener ausdrücklicher Freigabe/PIN/Bestätigung** geprüft/angewandt werden. Codex hat keinen Gerätesskin geändert.

## Historischer .45-Befund und neue Master-Gates

.45: Filmwidget leer FAIL, Livewidgetgrafik/12er-Grenze FAIL, Covermanager-Vorschau FAIL; Serienwidget-Sichtbarkeit/Befüllung PASS. Medienstart grundsätzlich möglich, Latenz noch nicht abgenommen. Ältere Live-Timeouts im teilweise versionsunsicheren Log separat erfassen; neuer .46-Test bleibt überall NOT_TESTED.

| Fall | Schritte / Erwartung | Box B .46 |
|---|---|---|
| STOP46-01 | Startsender einmal starten → einmal Back. Overlays schließen nur ihre Ebene; aus reinem Vollbild Stream aus und bedienbare Ansicht. EIN-Einstellung bleibt erhalten. | NOT_TESTED |
| STOP46-02 | Nur falls ein Timeout von selbst auftritt: nichts wiederholt starten/stoppen; spätere passende native Rückkehr beobachten. Genau eine sichere GUI-Rückkehr, Timeout historisch weiter sichtbar, keine neue Sitzung gestoppt. Bei dauerhaftem Freeze beenden und privat protokollieren, keine Stressserie. | NOT_TESTED |
| STOP46-03 | Erst nach STOP46-01 PASS: Film-/Episode-Back und weitere fünf normale Livezyklen.20Zyklen nur bei Bedarf und bewusster Nutzerentscheidung, sofort beim Hänger abbrechen. | NOT_TESTED |
| PERF46-01 | Kaltstart: reale Version/Box/Startgruppe privat festhalten, Widgetklick→Videonachweis→Mini sichtbar→Gruppen bedienbar getrennt messen. Keine30s-Schätzung als Messwert übernehmen. | NOT_TESTED |
| PERF46-02 | Warm dieselbe Strecke fünfmal ohne Stress; Kaltstichproben nur normale freigegebene Kodi-Neustarts. Anzahl und p50/p95 getrennt berichten, keine künstlichen Cache-/DB-Resets. | NOT_TESTED |
| PERF46-03 | Film und Serie getrennt: Klick→erste nutzbare Details→angereicherte Details→Resolve→Video; sichtbares bestehendes Ladefeedback, IR/Back reagieren. | NOT_TESTED |
| FULL46-01 | Bestehende aktive Startgruppe mit >12 Sendern: alle Titel bis Ende horizontal durchsuchen, Anfang/Startsender genau einmal, Anzahl mit lokaler Gruppe vergleichen. | NOT_TESTED |
| FULL46-02 | Sender13,17 und letzter Sender: richtige Beschreibung/Now/Next/Logo/Details/Klickziel; Bilder begrenzt asynchron, kein Fokus-Autoplay oder blockierender Netzwerkaufruf. | NOT_TESTED |
| FILM46-01 | Bereits vorhandene Filmreihe zeigt bis24 echte verfügbare Filme statt BUDGET/0; drei korrekte Filmziele. Falls weiter leer: nur sichere stage/code/rows-Marker berichten, keine Rohlogs veröffentlichen. | NOT_TESTED |
| SER46-01 | Historisch gefüllte Serienreihe bleibt gefüllt, drei echte Serienziele und Episode; keine Neubindung. Sichtbarkeits-PASS der .45 ersetzt diesen neuen Regressionstest nicht. | NOT_TESTED |
| PICK46-01 | Film und Serie: Covermanager öffnen, Provider/Poster/Hintergrund getrennt, echte Miniaturen sichtbar; OK vergrößert richtige Auswahl. Nur Text/Platzhalter zählt nicht als Bild-PASS. | NOT_TESTED |
| PICK46-02 | Bild wählen→Übernehmen→Speichern; Detail, Kategorie, Wiedergaberückkehr und normaler Kodi-Neustart zeigen dieselbe Wahl. Metadatenfelder separat bestätigen, keine falsche Folge/Serie übernehmen. | NOT_TESTED |
| PICK46-03 | Abbrechen/Zurück, schnelle Quellenwahl, keine Kandidaten oder natürlich offline: bisheriges Bild/Metadaten gleich, verständlicher echter Fehler, kein unkontrollierter Retry. | NOT_TESTED |
| SAFE46-01 | Ohne tatsächlich dokumentiertes BACKUP_VERIFIED dürfen manuelles und automatisches EPG-Refresh nichts importieren. Gespeicherte Programme/Zuordnungen read-only nutzbar. Keine künstliche Beschädigung zum Test. | NOT_TESTED |

## Gemeinsamer SQLite-Cache und echtes20-Tage-Fenster

| Fall | Schritte / Erwartung | Box B .46 |
|---|---|---|
| DB46-01 | Widgets verwalten→Status: eigene lokale Sendungs-/Artworkdatenbank erkannt, Versions-/Budget-/IO-Zustand nachvollziehbar. READY bedeutet nicht20Tage oder Gerätefreigabe. Bestehende Guide-Datei nicht austauschen. | NOT_TESTED |
| DB46-02 | Dieselbe Sendung in Live-Widget und großem EPG-Detail öffnen: identischer Titel, Quelle, Folge/Bild/Zeiten. Kein eigener Fokus-Netzabruf. | NOT_TESTED |
| DB46-03 | Natürlichen Now→Next-Wechsel mit vorhandenem Reloadhook beobachten; Bild/Titel/Details/Progress wechseln gemeinsam. Anderen Sender kontrollieren, dessen Bildcache bleibt gültig. | NOT_TESTED |
| DB46-04 | Gespeicherte Tage−1/−2/−7 read-only, lokale Mitternacht/DST korrekt. Fehlende Historie leer, kein Catch-up erfinden. Keine Retention/Löschung ausführen. | NOT_TESTED |
| DB46-05 | Nur bei tatsächlich vorhandenen lokalen Daten Tag+10/+15/+20 im großen Raster und Tagesguide öffnen. Richtige konkrete Sendung/Quelle/Folge. Kein Feeddownload ohne BACKUP_VERIFIED und gesonderte Freigabe. Bei fehlendem20-Tage-Feed BLOCKED_DATA_NOT_AVAILABLE. | NOT_TESTED |
| DB46-06 | Lokales Bild/Thumbnail und Text nach normalem Kodi-Neustart vorhanden. Bei natürlich nicht erreichbarem Bildserver bleibt Text/LastGood; keine absichtliche Stromunterbrechung oder DB-Beschädigung. | NOT_TESTED |
| DB46-07 | Wenn später eine ausdrücklich erlaubte Quellenaktualisierung nur eine Sendung ändert, unveränderte Sendung/Bildreferenz kontrollieren. Bis Sicherungsfreigabe BLOCKED_BACKUP_REQUIRED. | NOT_TESTED |
| DB46-08 | Nicht16:9-Quelle wird proportional mit neutralen Rändern angezeigt, kein abgeschnittener Inhalt/eingebranntes Logo. Tatsächlich fehlende Bilder/Decoder/Netz/Budget separat dokumentieren. | NOT_TESTED |

## Gemeinsames EPG-/Live-Widget-Pflichtpaket

| Fall | Schritte / Erwartung | Box B .46 |
|---|---|---|
| E46-01 | Großer horizontaler EPG → reale Filmsendung → Details. Titel, Sender, Zeit/Dauer/Plot/Genre/Jahr nur wenn vorhanden; Bild passt zur gesicherten Identität. | NOT_TESTED |
| E46-02 | Echte Serie mit vorhandener Staffel/Folge/Subtitel öffnen. Richtige konkrete Folge; beliebiges Serienbild nicht als Episodenstill ausgeben. Unzureichendes Match korrekt neutral. | NOT_TESTED |
| E46-03 | Nachrichten ohne Eventbild: neutraler Nachrichten-/Sendungsplatzhalter und korrekter Text. Talkshow ebenso; kein beliebiges TMDb-Filmplakat. | NOT_TESTED |
| E46-04 | Sender ohne XMLTV/EPG: lesbarer neutraler Leerzustand; keine fremde Sendung, keine automatische Quellenänderung. | NOT_TESTED |
| E46-05 | In jeder Grafik/Platzhalteransicht Logo links oben proportional/kontrastreich; fehlt Logo, richtiger Sendername. Kein eingebranntes/falsches Logo. | NOT_TESTED |
| E46-06 | Aus Mini-EPG-/Programmmenü dieselbe Sendung öffnen. Hoch/Runter/PageUp/PageDown scrollt Beschreibung, Back nur Details. Guidegruppe/Zeit/Cursor/Fokus und laufender Stream bleiben erhalten. | NOT_TESTED |
| E46-07 | 10 schnelle Öffnen/Back, Schließen während Bildsuche, fremder Modal: keine erzwungene Dialogschließung, verspätete UI-Setter, Doppelstarts oder Home-Umwege. | NOT_TESTED |
| E46-08 | Offline vorhandene Texte und bereits verifiziertes Ereignisbild. Nur bei ausdrücklicher sicherer Netzabschaltung; Player nicht absichtlich unterbrechen. Ohne Ausführung NOT_TESTED. | NOT_TESTED |
| E46-09 | Optional TMDb AUS/Token fehlt: freundlicher realer Status, kein APIaufruf. Mit eigenem freigegebenem Token echte Titel/Jahr-/Staffel-/Folgenidentität; mehrdeutig → neutral. | NOT_TESTED |
| E46-10 | Bewusst passendes Bild im Cache, normaler Kodi-Neustart, gleiche Sendungsidentität/Herkunft und vorhandener EPG-Text bleiben. Keine alten Bilder/Jobs gelöscht. | NOT_TESTED |
| E46-11 | Großer EPG read-only gestern/vorgestern/−7 bei tatsächlich gespeicherten Daten; historische Details zeigen die gewählte Sendung, versprechen kein Catch-up. | NOT_TESTED |
| E46-12 | 720p/1080p nur bei sicher verfügbarer Auflösung: Logo/Image/Text/Fonts/Scroll/Fokus. Hostbilder keine Pixel-/Gerätefreigabe. | NOT_TESTED |
| L46-01 | Bestehende Live-Reihe ohne Neubindung: die vollständige aktive Startgruppe einschließlich mehr als12 Sendern und Ende der Gruppe, pro Kachel laufendes Programmbild oder ehrlicher Platzhalter und korrektes Logo links oben. | NOT_TESTED |
| L46-02 | Fokus auf mindestens10 verschiedene Sender: tatsächlicher Titel/Zeit/Progress und passende Beschreibung; Abgleich mit neuem EPG-Detailfenster und großem EPG. Kein Fokus-Netzabruf/-Autoplay. | NOT_TESTED |
| L46-03 | Menütaste/langer OK gemäß IR → Kodi-Kontextmenü → Sendungsdetails. Exakt fokussiertes Ereignis; Back erhält Home-/Widgetfokus. Native Info-Taste wird nicht global umbelegt. | NOT_TESTED |
| L46-04 | Normales OK auf drei Livekacheln: exakt jeweiliger Sender, bisheriger .42-kompatibler Back; niemals Programmdetail statt Player oder fremdes Portal. | NOT_TESTED |
| L46-05 | Natürlichen Now→Next-Wechsel beobachten und Uhrzeit notieren: neuer Ereignisschlüssel, Bild/Titel/Zeit/Progress selbstständig aktuell, kein Neustart oder manuelles Neubinden. Fehlender Hook ausdrücklich BLOCKED_NO_RELOAD_HOOK. | NOT_TESTED |
| L46-06 | Mindestens15min Home/20D-Pad-Wechsel: kein ständiges Flackern/Leeren/Reset/Fokusverlust. Kalt/Warm je5–10 echte Zeitmessungen, p50/p95 nur aus diesen Messungen. | NOT_TESTED |
| L46-07 | Fehlender nativer Renderer/Fokus/Logo: Widgets verwalten zeigt BLOCKED_NO_OVERLAY_FOCUS_BINDING. Datenproperties allein sind kein sichtbarer PASS. | NOT_TESTED |
| AD46-01 | Nur nach eigener Freigabe: optionalen2.2.3-Renderer vorbereiten. Original/Kandidat/SHA privat prüfen. Bis zur zweiten Bestätigung bleibt Skinhash gleich; falsche PIN/Cancel blockiert. | NOT_TESTED |
| AD46-02 | Nur bewusst bestätigen: genau eine Layoutdatei atomar angepasst, gespeicherte Quellen/Shortcuts gleich. Nach ReloadSkin L46-01–06 prüfen. Kein automatischer zweiter Adapter. | NOT_TESTED |
| AD46-03 | Falls Reload-Hook fehlt: separat ausdrücklich vorhandenen .45-Reload-Adapter prüfen/freigeben. Renderer allein zählt nicht als automatischer Refresh. Ohne Freigabe BLOCKED. | NOT_TESTED |
| AD46-04 | Nur bei tatsächlich angewandtem Adapter bewusstes Restore prüfen: exakter Originalhash, keine fremden Änderungen überschreiben. Unbekannte Skinversion/Fonts/Struktur BLOCKED; keine künstlichen Skinupdates auf Box B. | NOT_TESTED |
| V46-01 | Bestehende Filmreihe bis24 reale aktuelle Titel mit echten Postern. Drei Filmklicks exakt passende Details, kein Root oder Fokus-Autoplay. | NOT_TESTED |
| V46-02 | Bestehende Serienreihe bis24 echte Seriencover. Drei Klicks richtige Serie/Staffel; manuell Episode starten und korrekt zurück. | NOT_TESTED |
| V46-03 | Natürlich neu erfolgreich indexierter Film/Serie wird ohne Neueinrichtung sichtbar. Keine künstliche Katalog-/DB-Beschädigung zum Testen. | NOT_TESTED |
| C46-01 | Programm-Bildcachebudget standard64MiB; vorhandene globale Reserve und dynamischer Alt-Artworkmodus unverändert. Budget/Netz/Decoder/echter Diskmangel im Status unterscheiden; nicht absichtlich Speicher vollschreiben. | NOT_TESTED |

## .45-Verträge als neue .46-Regression

Alle Fälle erneut NOT_TESTED. Die verlinkten .45/.43-Protokolle bleiben unveränderte Historie. Bei optionalen Adapter-/Speichergates keine Freigabe unterstellen.

| Fall | Schritte / Erwartung | Box B .46 |
|---|---|---|
| W46-01 | Bestehende Live/Film/Serienreihen nach Update ohne Neubindung; unveränderte gespeicherte URLs und Portalzuordnung. Vollständige aktive Startgruppe ohne12er-Grenze, bis24 unterschiedliche aktuelle Filme/Serien, keine All-Films-Posterattrappe. | NOT_TESTED |
| W46-02 | Mindestens drei Logos, drei Filmposter, zwei Seriencover mit realen Metadaten ansehen; bekannte gültige Providerbilder statt generischer Platzhalter. Logo proportional; native Skin-Layoutgrenzen dokumentieren. | NOT_TESTED |
| W46-03 | Livekachel → exakt Sender, Film → exakt Film, Serie → exakt Serie/Staffeln; kein Fokus-Autoplay, Rootumweg oder fremdes Portal. Back stellt bedienbare Voransicht her. | NOT_TESTED |
| W46-04 | Sender/Now/Next/Zeiten/Progress im Widget mit Mini/Info/großem EPG gleicher Sender/Uhrzeit vergleichen. Manuelle Zuordnung gewinnt. Kein EPG erfinden. | NOT_TESTED |
| W46-05 | Natürliche erfolgreiche lokale neue Kataloggeneration abwarten. Neues Medium muss ohne Neubinden/Kodi-Neustart nach Hintergrundaktualisierung erscheinen; Ereigniszeit→sichtbare Reihe messen. Fehlender Skin-Hook ausdrücklich BLOCKED_NO_RELOAD_HOOK. | NOT_TESTED |
| W46-06 | EPG-/Logoänderung nach erfolgreicher vorhandener Hintergrundpublikation; keine leere Zwischenliste, richtige Auswahl, kein periodisches Flackern. Mindestens15min beobachten und20Fokuswechsel. Keine IR-Netzabfrage. | NOT_TESTED |
| W46-07 | Kalt/Warm je5 Stichproben bis erste bedienbare Reihe/Poster/EPG separat messen, Stichproben und p50/p95 notieren. Hauptstartgruppe gesondert. | NOT_TESTED |
| W46-08 | Nur falls ausdrücklich gewünscht: Einstellungen→Darstellung→Widgets, Adaptervorprüfung. Ohne Änderung/bei Cancel Skinhash und Shortcuts identisch. Unsupported-Version/kein Hook korrekt melden. | NOT_TESTED |
| W46-09 | Nur nach eigener Freigabe/PIN/zweiter Bestätigung: privates Original/Kandidat/SHA-Manifest prüfen, Adapter anwenden, ReloadSkin, W46-05 erneut. Gespeicherte Shortcuts unverändert. Sonstige Skinänderung darf Restore nicht überschreiben. Ohne ausdrücklichen Opt-in BLOCKED. | NOT_TESTED |
| W46-10 | Nur falls Adapter tatsächlich angewandt: Rücknahme bewusst bestätigen, Originalhash gleich, keine Daten-/Skinsettingsverluste. Kein Test künstlicher Skinupdates auf produktivem Gerät. | NOT_TESTED |
| S46-01 | Genau7 Rubriken: Account & Portale, Live-TV & Sender, EPG, Medien & Wiedergabe, Darstellung & Bedienung, System & Speicher, Experimentell. Unterfunktionen sinnvoll erreichbar. | NOT_TESTED |
| S46-02 | Experimentell mit6666 öffnen; mit666, anderer PIN und Abbrechen kein Zugriff; zurück nach Einstellungen. | NOT_TESTED |
| S46-03 | Nach Verlassen erneut eintreten: erneute PIN. Direkte Aufnahme-/Download-/Diagnoseroute ohne PIN kein Zugriff. Keine Query-/persistente Freischaltung. | NOT_TESTED |
| S46-04 | Normale gespeicherte Sprache/Player/Startgruppe/Portale unverändert. Optionseditor Abbrechen schreibt nichts, explizites Speichern nur gewählten Wert. Keine riskanten Werte probeweise ändern. | NOT_TESTED |
| S46-05 | Experimentell-Untergruppen und bisherige Aktionsaliase erreichbar; separate Bestätigung für risikoreiche Aktion durch Abbrechen prüfen, keine Löschung ausführen. | NOT_TESTED |
| M46-01 | Alle Menüoberflächen anhand MENU_MATRIX_02946_DE.md prüfen: kleines passendes Icon links/Text rechts, keine zusätzliche Fokusstation, kein Platzhalter bei Medienbildern. Native Kodi-Ausnahmen getrennt. | NOT_TESTED |
| M46-02 | Ganze Fernbedienungsstrecke Home→Settings→Unterrubriken→Details→linkes Untermenü→Guidegruppen/Tools→Back; keine toten Controls/Unsichtbarfokus. | NOT_TESTED |
| I46-01 | 1.OK: neue dreispaltige Glasleiste direkt mit Nutzerbild vergleichen: Logo/Name/Datum/Uhr, Vorher/Jetzt/Danach, grüne Zeitachse, rechte2×3Technikzellen. Kein fremdes TV-Foto/Wasserzeichen. Screenshot privat abgleichen. | NOT_TESTED |
| I46-02 | Reales1080p und falls ohne riskante Umschaltung verfügbar720p: Rundungen/Abstände/Fonts/Lesbarkeit, lange Titel, Uhr/Zeiten und Clipping. Hostbilder sind keine Gerätedarstellung. | NOT_TESTED |
| I46-03 | Tatsächliche Auflösung/Codec/Audio/Kanäle/Sprache/UT/fps mit Kodi vergleichen. Unbekannt leer, keine alten Trackwerte; realer Trackwechsel falls vorhanden. Kein Atmos erfinden. | NOT_TESTED |
| I46-04 | Echte Vorhersendung nur bei gespeicherter Historie; Now/Next aus gleicher Basis. Uhren-/EPG-Fortschritt folgt realer Zeit, kein GUI-Hänger. | NOT_TESTED |
| I46-05 | 1.OK→2.OK→Transportbuttons→Back, Links Mini→Gruppen→Rail; nach20Öffnen/Schließen keine verlorenen Badges, Geistertexte, doppelte Fokusrahmen oder neue Latenz. | NOT_TESTED |
| P46-01 | Vorhandenes EPG read-only gestern/vorgestern bis−7 im großen EPG und Mini; echte verfügbare Historie vs leer korrekt. Kein Refresh vor verifiziertem Sicherungsgate. | NOT_TESTED |
| P46-02 | Suchtrefferfilm UND Serie→Episode starten/Back; gleiche Query/Tab/Fokus und richtiger Player. Frühere Einzelbeobachtung nicht als beide PASS übernehmen. | NOT_TESTED |
| P46-03 | Cover/Metadaten manuell suchen→echte Vorschau→gezielt übernehmen→speichern, nach normalem Neustart wiederfinden. Ohne echten Kandidaten BLOCKED. Keine globalen Jobs/Cache löschen. | NOT_TESTED |
| P46-04 | Resume, natürliches Autoplay inklusive Staffelwechsel, bewusster Stop ohne Autoplay. Portale/Favs/Gruppen/EPG-Zuordnungen/Cover/IR nach normalem Neustart erhalten. | NOT_TESTED |


## Vollständige bisherige A–H-Strecke

| Fall | Prüfung / Erwartung | Box B .46 |

|---|---|---|
| A1 | Version/Kompatibilitätsmodus EIN | NOT_TESTED |
| A2 | Startsender | NOT_TESTED |
| A3 | Mini links 60–90s ohne Flackern | NOT_TESTED |
| A4 | Rechts nur ein Fokusrahmen | NOT_TESTED |
| A5 | Rechts Jetzt/Zukunft stabil | NOT_TESTED |
| A6 | Live Back beendet Bild/Ton, GUI bedienbar | NOT_TESTED |
| B1 | 1.OK Info, 2.OK Player | NOT_TESTED |
| B2 | Playercontrols/echte Streaminfos | NOT_TESTED |
| B3 | Senderliste/Gruppen | NOT_TESTED |
| B4 | Rail erreichbar; zusätzlich Ghostlabels prüfen | NOT_TESTED |
| B5 | Back je Ebene; zusätzlich visuelles Einklappen prüfen | NOT_TESTED |
| B6 | Großen EPG öffnen | NOT_TESTED |
| C1 | Filmkatalog/Kategorien; neue Fokusregeln zusätzlich prüfen | NOT_TESTED |
| C2 | >240/möglichst500 Titel Paging | NOT_TESTED |
| C3 | Details/Back/Fokus; async Nachladen zusätzlich prüfen | NOT_TESTED |
| C4 | Film aus normalem Katalog starten/stoppen | NOT_TESTED |
| C5 | Serie/Staffeln/Episoden | NOT_TESTED |
| C6 | Autoplay einschließlich Staffelwechsel | NOT_TESTED |
| C7 | Manueller Stop ohne nächstes Autoplay | NOT_TESTED |
| C8 | Resume | NOT_TESTED |
| D1 | Suche öffnen | NOT_TESTED |
| D2 | Sendername suchen | NOT_TESTED |
| D3 | Echten laufenden Programmtitel finden | NOT_TESTED |
| D4 | Rock/Rocky in passenden Tabs | NOT_TESTED |
| D5 | Genre suchen | NOT_TESTED |
| D6 | 20 Tabwechsel ohne Trefferverlust | NOT_TESTED |
| D7 | Cover/Medieninfo | NOT_TESTED |
| D8 | Suchtreffer → Film UND Episode abspielen, korrekt zurück | NOT_TESTED |
| E1 | Bildmanager eindeutig öffnen | NOT_TESTED |
| E2 | Providerkandidat vorschauen | NOT_TESTED |
| E3 | Bild bewusst übernehmen/speichern | NOT_TESTED |
| E4 | Gewähltes Bild nach Neustart | NOT_TESTED |
| E5 | Poster/Hintergrund getrennt | NOT_TESTED |
| E6 | Metadaten separat vorschauen | NOT_TESTED |
| E7 | Einzelne Metadaten bewusst speichern | NOT_TESTED |
| E8 | Optional TMDb mit eigenem Token; richtige Aladdin-Jahrgänge | NOT_TESTED |
| E9 | Commons-Bildsuche; lokal nur falls eigene Datei vorhanden | NOT_TESTED |
| E10 | Schließen während Suche/Worker | NOT_TESTED |
| E11 | Dynamische Cover bleiben bei Tab/Kategorie/Playerwechsel | NOT_TESTED |
| F1 | Home-Live-Widget kalt/warm zügig | NOT_TESTED |
| F2 | Echte Senderlogos proportional/kompakt | NOT_TESTED |
| F3 | Fokus-NOW/NEXT/Uhrzeit/Progress | NOT_TESTED |
| F4 | Neueste Filme bis24 mit echten Postern | NOT_TESTED |
| F5 | Neueste Serien bis24 mit echten Postern | NOT_TESTED |
| F6 | Konkrete Live-/Film-/Serien-Klickziele | NOT_TESTED |
| F7 | 20 Fokuswechsel/Neustart, periodischer Refresh | NOT_TESTED |
| F8 | Ehrlicher Ohne-EPG-/Index-Fallback | NOT_TESTED |
| G1 | Gemeinsamer EPG/Refresh-Bestand; nur nach Backup-Gate | NOT_TESTED |
| G2 | Gestern/vorgestern…−7, echte Historie | NOT_TESTED |
| G3 | Quellen/manuelle Zuordnungen erhalten | NOT_TESTED |
| G4 | Vorhandene Film-/Serienfavoriten erhalten; TV-Favs später | NOT_TESTED |
| G5 | Startgruppe/Startsender erhalten | NOT_TESTED |
| G6 | Startgruppen-Latenz messen, getrennt von F1 | NOT_TESTED |
| G7 | Einstellungen nach Neustart einzeln kontrollieren | NOT_TESTED |
| G8 | Einmaliger .44-Versionshinweis, danach keine Wiederholung | NOT_TESTED |
| H1 | Fünf zusätzliche Live-Back-Zyklen tatsächlich zählen | NOT_TESTED |
| H2 | 20 Live-Start/Back-Zyklen einzeln zählen | NOT_TESTED |
| H3 | Live-Dauerbetrieb entsprechend historischem Test, echte Dauer notieren | NOT_TESTED |
| H4 | Zehn Senderwechsel | NOT_TESTED |
| H5 | Drei normale Katalogfilm-Start/Stop-Zyklen | NOT_TESTED |
| H6 | Serien-Stop und reguläres Autoplay getrennt | NOT_TESTED |
| H7 | Resume erneut | NOT_TESTED |
| H8 | Normaler Kodi-Neustart/Bestandsschutz | NOT_TESTED |


## Reales Live-Back-Protokoll bei beauftragter Wiederholung

Einzelback NOT_TESTED, Filmback NOT_TESTED; fünf zusätzliche Zyklen01–05 jeweils NOT_TESTED. Die20er-Strecke nicht aus früheren Alltagsbeobachtungen vorausfüllen:

- [ ] LIVE46-20-01: NOT_TESTED
- [ ] LIVE46-20-02: NOT_TESTED
- [ ] LIVE46-20-03: NOT_TESTED
- [ ] LIVE46-20-04: NOT_TESTED
- [ ] LIVE46-20-05: NOT_TESTED
- [ ] LIVE46-20-06: NOT_TESTED
- [ ] LIVE46-20-07: NOT_TESTED
- [ ] LIVE46-20-08: NOT_TESTED
- [ ] LIVE46-20-09: NOT_TESTED
- [ ] LIVE46-20-10: NOT_TESTED
- [ ] LIVE46-20-11: NOT_TESTED
- [ ] LIVE46-20-12: NOT_TESTED
- [ ] LIVE46-20-13: NOT_TESTED
- [ ] LIVE46-20-14: NOT_TESTED
- [ ] LIVE46-20-15: NOT_TESTED
- [ ] LIVE46-20-16: NOT_TESTED
- [ ] LIVE46-20-17: NOT_TESTED
- [ ] LIVE46-20-18: NOT_TESTED
- [ ] LIVE46-20-19: NOT_TESTED
- [ ] LIVE46-20-20: NOT_TESTED

## Ergebnis dokumentieren

Pro Fall Version/Commit/ZIP-SHA, Datum/Uhrzeit Europe/Berlin, Gerät/Kodi/Skin, genaue Schritte, Erwartung/Beobachtung, PASS/FAIL/NOT_TESTED/BLOCKED und Ursache. Widget-Gesamtziel erst nach echter grafischer Detailsicht **und** sichtbarer bestehender Live-Reihe mit Logo/Fokus/Info/OK/Programmwechsel. Private Logs/URLs/Tokens/SMB-Daten nicht öffentlich veröffentlichen. Issues bleiben offen; kein Merge-/Releaseautomatismus.
