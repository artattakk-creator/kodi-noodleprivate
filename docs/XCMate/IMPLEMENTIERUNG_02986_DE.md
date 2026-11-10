# XCMate 0.1.29.86 – Implementierung und Freigabestand

Basis: `c6124922d067361e37db4dd325710ea89a96002e` (`main`, veröffentlichte .85).
Branch: `fix/xcmate-02986-android-live-hero-mapping`. Auftrag #409, Zusammenhänge #401/#406/#407.
**Folge-Review-Build. PR #410 wurde am 10.11.2026 um 14:03:35 UTC durch den Repository-Inhaber gemergt (36b903c). Dieser Agent hat keinen Merge ausgeführt. P0-F/G bleiben im selben Branch, in Folge-Draft #412, ohne Kanalveröffentlichung oder Geräteinstallation.**

Aktuelle kumulative Basis: `36b903c06daa7b7fb5903f9de568237c18b9e2a1`. Die Quellschutz-Verträge bleiben gegen die veröffentlichte .85 c612492 gepinnt; A–E werden nicht zurückgebaut.

## Bestätigte Codepfade und Korrekturen

A: `live_items62.basic()` rief pro Sender Artwork-Auflösung auf; darin konnte selbst die Auswahl einer Provider-Bildadresse bereits auf Bilddateien zugreifen. Der neue `live_rail86` erzeugt die vollständige Identitätsleiste mit einem Gruppen-Read und einem gebündelten Logo-Nachweis. EPG kommt aus dem RAM-Snapshot; es blockiert den Verzeichnisaufbau nicht. Beide bestehenden Live-Widget-URLs verwenden dieselbe schnelle Darstellung, die URLs und der Widgets-Ordner bleiben erhalten. Senderklicks behalten `play_live`/`source_play` und den bisherigen Widget-Token.

`logo_manifest86` führt einen eigenständigen, account-/profil-/gruppen-/quellengebundenen Nachweis. Verifizierte lokale Dateien sowie vorhandene Kodi-Textur-Nachweise werden zuerst gelesen. Der bestehende Provider-Worker lädt begrenzt nach und schreibt nach vollständiger Reserveprüfung atomar. RAM-/Kodi-Renderer-Fallback bleibt bei Schreibblockade möglich. Keine automatische Zieländerung, keine Löschung, keine zusätzliche Datenbank. Ungültige Quelle oder geänderter Dateistempel kann keinen fremden Nachweis übernehmen.

B: Der bisherige Resolver konnte ein Feedbild vor der eigenen TMDB-Suche wählen und eine früh zurückgegebene Cache-Referenz endlos erneuern. Im Home-Pfad werden bestätigte breite TMDB-Backdrops, große verifizierte Szenenbilder und offizielle Poster getrennt behandelt. Mindestgrößen: breite Bilder 960×540 mit Seitenverhältnis 1,3–2,5; offizielle Poster 500×700 mit Verhältnis 0,45–0,85. Kleine XMLTV-Bilder, Providerposter und unbestätigte Vorschläge sind keine Hero-Hauptbilder. Offizielle Poster verwenden einen eigenen großen proportionalen Modus.

Die Auswahl und die Quelle sind an dieselbe Sendung und Mapping-Generation gebunden. Die letzte zulässige Darstellung bleibt hinter dem Nachfolger erhalten; ein Kandidat mit geringerer Qualität verdrängt sie nicht. Remote-Kandidaten werden im eigenen Kodi-Bildcontrol vorbereitet; der Worker verlangt danach eine tatsächlich decodierbare Kodi-Textur. Lokale Bilder werden vollständig decodiert und gegebenenfalls gehasht, bevor sie zur Darstellung freigegeben werden. **Diese Receipts sind keine Behauptung sichtbarer Android-Pixel.** Ereigniswechsel, Opt-out, explizite Quellenwiderrufe und Integritätsfehler dürfen nicht an fremden Bildern festhalten.

C/E: Die Skin-Erweiterung verändert ausschließlich den per Digest bekannten eigenen .85-Hero. Alle übrigen Includes, Templates, Overrides, persönlichen SkinShortcuts und Widget-Pfade bleiben byteidentisch. Eigene Controls für Texturvorbereitung und kompakten Status werden ergänzt. Die vorhandenen Film-/Serien-Ladeanzeigen bleiben erhalten. Zwischengespeicherte Medien dürfen nach der Identitätsleiste vorbereitet werden; sie warten nicht mehr auf eine vollständige externe Hero-Suche. Ein identischer Live-Identitäts-/Logo-Datensatz erzeugt keine neue Veröffentlichung allein wegen geänderter EPG-Texte oder Fortschrittswerte.

D: `series_requests85` blockierte die Recherche bislang vor der Suche auf exakt vorhandenen lokalen EPG-Fakten. Der neue Recherchepfad nutzt denselben vorhandenen Worker, verlangt für die reine Suche aber keine EPG-Daten. Freitext, erneute Suche, Quellenwechsel TMDB-TV/TMDB-Movie/TVMaze und begrenzte Folgeseiten bleiben auch bei null Treffern erreichbar. Charmed-Alternativabfragen unterscheiden die Originalserie und den Reboot über unabhängig gelesene Werkdetails. Kandidaten enthalten Werktyp, Titel, Jahr, Land, Beschreibung und geprüfte Posterreferenz. Kein Suchtreffer wird automatisch gespeichert.

Vor einer ausdrücklichen Speicherung werden Werk-ID, Details und der aktuelle Profil-/Portal-/Sender-/Werk-Kontext erneut gelesen. Veraltete/fehlende EPG-Fakten lassen Suche/Vorschau zu, verhindern aber einen falschen Speichererfolg. Film- und Seriendetails bieten denselben Manager sowie den bisherigen Artwork-Picker. Die vorhandene .85-Mappingdatei wird kompatibel um den Werktyp erweitert. Bewusste TV-/Filmwahl übernimmt keine Episodenfakten. Eigene ausdrücklich gewählte Bilder werden begrenzt gelesen, decodiert, kopiert und gehasht; Originale bleiben erhalten. SMB-Zugriff nur auf die ausdrücklich ausgewählte einzelne Datei, kein automatischer Share-Test oder Scan.

Zusätzliche bei der nativen Prüfung bestätigte Übergabefehler: `programme_requests68` ließ `role81` aus der internen Ergebnis-Payload weg. Damit konnte ein vollständig geladenes TMDB-Backdrop seine Typfreigabe auf dem Weg zum Hero verlieren. Die Rolle wird jetzt einschließlich Cache-/Status-Handoff erhalten. Die Qualitätsprüfung bleibt am decodierten Original; ein von Kodi verkleinertes Cachebild muss separat decodierbar sein und sein passendes Seitenverhältnis nachweisen. Eine kleine Originalquelle erhält dadurch keine höhere Bildklasse.

Die Kontexttaste 117 öffnet in Film-/Seriendetails denselben linken Bildmanager; das bestehende Episoden-Gesehen-Menü bleibt erhalten. „Kein Bild verwenden“ ist eine dauerhafte, reversible Einzelwahl im vorhandenen atomaren Override-Manifest. Weder Widget-Last-good noch Providerjobs dürfen sie überstimmen. EPG-Opt-out wird vor Cache-/Netzwerkzugriff ausgewertet; gespeicherte Originalbilder werden nicht entfernt. Nach bestätigter Änderung ist nur die betroffene bestehende Widgetquelle einmalig aktualisierbar, ohne neue Route oder allgemeine Reloadschleife.

Der kompakte Live-Status unterscheidet offene Logo-/EPG-/Bildreferenzen, blendet sich nach vollständiger Freigabe aus und endet nach 60 Sekunden bei fehlenden Ergebnissen in einem statischen Diagnosehinweis. Es gibt keine erfundenen Prozentwerte. Status und Control-Receipt sind ausdrücklich keine Android-Pixelabnahme.

Bei Kaltstart kann der bereits unabhängig bestätigte Werk-Kandidat jetzt seine **exakt passende** Kodi-Cache-Textur verwenden, bevor erneut ein Bilddownload versucht wird. Auch dieser Weg verlangt unveränderte Quellenfreigabe, zulässige Kandidaten-Proof-Klasse, korrekte Cache-URL, owned-file-Dekodierung und ausreichende tatsächliche Bildmaße. Es gibt keine Cache-Suche nur anhand ähnlicher Titel und keine Umdeutung von XMLTV-Miniaturen zu TMDB-Backdrops.

Manuelle Bildentscheidungen werden auch auf einen unveränderten Film-/Serien-Widget-Snapshot angewendet. Dieser Weg übernimmt **ausschließlich Bilder/Opt-out**. Provider-Handlung, Jahr und übrige Metadaten bleiben autoritativ; der vorhandene strenge .58-Regressionstest bleibt unverändert. Ohne individuelle Bildwahl bleibt das ursprüngliche Katalog-DTO byteinhaltlich gleich. Der Katalog wird für eine Bildänderung weder neu importiert noch geleert.

## P0-F – native Indizes, Owner-Abbruch und begrenzte Wiederholungen

Verbindlicher neuer Befund: [bereinigte Android-.85-Analyse](ANDROID_LOGANALYSE_02985_BOXB_2026-11-10_134323_DE.md), Master Abschnitt 8. Die 18/165 nativen Indexmeldungen haben keinen beweisenden Python-Stack. Daher wird weder eine bestimmte Serie noch ein bestimmtes Modul als bestätigter Android-Verursacher behauptet.

Zwei konkrete Risiken im Code sind abgesichert: Native XML-Verzeichnislisten können `Container.NumItems=24` melden, aber keine Python-ListItems exponieren (`ControlList.size()=0`). Früher folgte trotzdem `getListItem(i)`; Kodi konnte bereits vor der abgefangenen Python-Ausnahme eine C++-Indexmeldung schreiben. Alle entsprechenden nativen Zugriffe laufen jetzt über `gui_guard86`: echte Kontrollgröße, -1/außerhalb, geschlossenes Fenster, erwartete Zeilenlänge und aktuelle Generation/Ansicht vor und nach dem Zugriff prüfen. Ein nicht exponiertes natives Widget nutzt den bestehenden verifizierten Reload-Hook; keine neue Route. Kandidaten-, Such-, Cover- und Gruppenauswahl verwenden denselben Guard. Auch ein negativer Guide-Gruppenindex ist ausgeschlossen.

Der bestehende Owner-Pool führt langlaufende Jobs in einem kooperativen Fenster-/Generationskontext aus. Keine zusätzliche Worker-Lane. Abbruch vor neuen Aufrufen, während Transportreads und vor Ergebnisübernahme; bei HTTP höchstens 1 s je Socket-Operation, höchstens 4 s kooperatives Gesamtbudget und keine automatischen HTTP-Retries in diesem UI-Kontext. Andere Threads/Servicejobs behalten ihre bisherige Policy. Cachetreffer bleiben möglich. Ein geschlossener Owner bekommt keine späten GUI-Ergebnisse. Kodi-Abbruch wird als `ROUTE_CANCELLED` erfasst; nach Owner-Rückkehr startet dann keine neue Navigation. Ein Betriebssystem-DNS-Aufruf lässt sich in Python nicht zuverlässig hart abbrechen; diese Grenze bleibt offen und wird nicht als garantierter Android-Invoker-Fix ausgegeben.

`GUI86` protokolliert ausschließlich feste Route/Code, numerische Control-/Index-/Größen-/Generations-/Thread-/Fensterwerte, bekannte Exceptionklasse und Projekt-Basename/Zeile/Funktion aus echten Traceback-Frames. Keine Exceptionnachricht, Quellzeilen, Argumente, URLs, Titel oder Tokens. Identische Meldungen sind zeitlich und mengenmäßig begrenzt.

Der lokale EPG-Reader verwendet bei fehlenden Daten 30/60/180/300 s Retry-TTL; neue EPG-Revisionen lösen die Pause sofort. Gute bestehende Snapshots werden nicht überschrieben. Negative Ereignisdiagnosen erhalten einen profil-/quellen-/faktenrevisionsgebundenen Cross-Invoker-Lease. Die bereits bestehende negative Bildjob-Sperre und ihr 30/120/300/900-s-Backoff bleiben erhalten. `CACHED_ITEMS_READY` wird bei identischer semantischer Generation nicht 688-mal erneut protokolliert; das ist eine Log-Deduplizierung und kein erfundener Nachweis vorheriger 688 kompletter Builds.

Ein zusätzlicher nativer Linux-Test führt 100 echte Plugin-Invoker-/Detail-/Back-Zyklen (einschließlich direktem `media_detail`) unter lokalen EPG-/Widget-Hintergrundaktualisierungen aus. Er zählt C++-Index-, Dispatch-, Directory- und 5-s-Invokerfehler ab seinem eigenen Start. Er ersetzt nicht die 100 Zyklen auf Box B.

## P0-G – sieben lokale Icons und getrennte Navigationsebenen

Alle sieben Hauptpunkte verwenden bereits unterschiedliche vorgepackte MIT-Tabler-PNGs (Lupe, Herz, Fernseher, Film, Playlist, Zahnrad, Haus/Start). Manifest, Original-SVG-Hashes, Lizenz und alle vier Zustände werden geprüft. Es gibt keinen Laufzeitdownload und keinen gemeinsamen generischen TV-Fallback. Das letzte Label heißt nun lokalisiert „Verlassen“ und behält die vorhandene Aktion `xcmate_home`/`USER_HOME`; der Player-Stop-Mechanismus bleibt unverändert.

Verstecken entfernt Sichtbarkeit, Beschriftung und Fokusfähigkeit, behält aber die bereits geladene lokale Icon-Textur. Unveränderte Icons werden beim Wiedereinblenden nicht geleert und neu hochgeladen. Links folgt jetzt ausdrücklich Sender → Gruppen → fokussierte Icon-Rail → ausgeklappte Labels; der Rückweg durchläuft dieselben Ebenen. Ein bestätigter Fehler war das Überschreiben eines gerade erfolgten Restore-Wechsels zurück zu `nav_icons`; das wird nun vermieden. Zwei ältere Navigationsregressionen wurden um die neue ausdrücklich geforderte Zwischenebene erweitert, ohne Methoden/Skips zu entfernen. Der Modell-ControlImage bewahrt jetzt wie Kodi seine Konstruktor-Textur.

Native Pixelprüfungen betrachten dieselbe echte `RailView` über BINGIE in 720p und 1080p: sieben verschiedene tatsächlich gerenderte Glyphen, D-Pad-Fokus, auf-/eingeklappte Ansicht und gleichbleibende Auswahl. Persönliche BINGIE-Hauptmenü-Icons/Shortcuts werden nicht ersetzt. Die gerätespezifische sichtbare Rail bleibt ANDROID_NOT_TESTED.

## Ehrliche Grenzen

- Ein anderer nutzbarer Android-Speicherpool wurde auf der physischen Box **nicht** nachgewiesen. `EXTERNAL_UNAVAILABLE` ist ein zulässiger negativer Befund, kein behaupteter Speichergewinn. Der neue Logo-Writer nutzt ausschließlich das vorhandene lokale Ziel und seine volle Reserve. VFS-Ziele werden nicht automatisch als neues Logo-Archiv aktiviert.
- Die reale Sichtbarkeit aller persönlichen Reihen, insbesondere „Frisch im Kino“ und „Diese Woche aktuell“, benötigt Box-B-Prüfung. Byteerhalt und synthetische Kodi-Reihen ersetzen diese nicht.
- Android-Warm-/Kaltstart-SLO, P50/P95, 20 Minuten CSI: Vegas, Mount-/Rechteprüfung und die realen Charmed-/Monk-Matches bleiben **ANDROID_NOT_TESTED**.
- Kein neuer Referenz-Screenshot wurde geliefert. Es gibt keine erfundene Designfreigabe.
- Bestehende Player-/Exit-/Portal-/Speicherreserve-Implementierungen und Installer 0.5.26 bleiben unverändert.

## Tests und Paket

Siehe `TESTBERICHT_02986_DE.md`, `ANDROID_ABNAHME_02986_DE.md` und `test-builds/02986/`.
Automatisierte Ergebnisse werden erst nach abgeschlossenen Läufen eingetragen. Regulär, Pilot und NeoDark3 bleiben auf den bestehenden veröffentlichten Bytes.
