# XCMate 0.1.29.43 – technische Änderungen und Grenzen

Basis: `main` `451f4cf0995cc09ada4b9eb4090906320d36a9fb` (.42). Auftrag #221, Rendering #220, Roadmap #194. Die ältere Planung #219 und der falsche Verweis #218 ersetzen diese Aufträge nicht. Keine Geräteinstallation, Main-Änderung oder Veröffentlichung durch diesen Kandidaten.

## Mini-EPG zuerst (#220, Regression #211/#208)

Der Fehlerpfad ist im Code und im nativen Setter-Modell reproduziert: `.42 visible(True)` schaltet zuerst sämtliche fünf grünen Bilder sichtbar; erst das nachfolgende `_paint()` blendet vier wieder aus. Kodi darf zwischen diesen einzelnen Aufrufen rendern. Das ist ein belegter unerwünschter Zwischenzustand; ein tatsächlicher GPU-/Android-Fix ist damit noch nicht bewiesen.

`.43` zeigt ausschließlich den berechtigten Fokusrahmen. Beim Wechsel werden alte Rahmen zuerst ausgeblendet. Zeilentext und Sichtbarkeit sind vorbereitet, bevor die Spalte eingeblendet wird. Ein Wertcache vermeidet identische native Schreibaufrufe. Die blanke native Liste bleibt für Navigation sichtbar; sie zeichnet weiterhin keine zweite Textebene. Gleiche Zeilenzahl benötigt keinen Listen-Rebuild. Auswahl bleibt über Event-Start/Ende statt veränderliche Titel erhalten; NOW und Fokus bleiben unabhängig. Überlappende Providerdaten erhalten genau eine NOW-Markierung. Historische Programme werden weiterhin vor dem Limit ausgefiltert.

Reproduzierbar: `python tools/probe_xcmate_mini_02943.py`. [Messung](MINI_RENDER_PROBE_02943.json): 200 identische Ticks, vorher **9.000** native Setter, danach **0**; maximal gleichzeitig sichtbare Rahmen vorher **5**, danach **1**. Listenresets bei identischen Daten bereits vorher 0, danach 0. Keine erfundene Verbesserung dieses Werts, keine echte Android-Latenz-/GPU-Messung. Zehn neue Mini-Tests beobachten jeden Setter, nicht bloß den Endzustand. Kein behaupteter atomarer Kodi-GUI-Batch.

## Live-Exit unverändert

`live_stop42.py`, `native_stop41.py`, `live_exit.py`, `exit_jobs.py`, vorhandene Keymaps sowie die freigegebene Medien-/Such-XML bleiben bytegleich zur .42. `live_exit_fullscreen42` bleibt standardmäßig AUS; das vorhandene EIN auf Box B wird weder überschrieben noch auf Box A übertragen. Kein Player-Rewrite, kein Thread-/Timeout-Trick, kein Decoderwechsel. Die einzelne echte .42-Beobachtung vom 27.10.2026 mit EIN bleibt ein historischer Teil-PASS. Fünf/zwanzig Zyklen und alle .43-Gates sind NOT_TESTED. „Fühlbar schneller“ bleibt PERF_BETTER_USER_OBSERVED.

## Katalog und Suche (#74/#102/#127/#159/#201)

Infinite Scroll und Genresuche existierten bereits und werden erhalten. Das akzeptierte Coverlayout (108×162, lesbare Titel, Fokusrahmen) und die eingefrorene Suchmaske mit Live-TV/Filmen/Serien werden nicht umgestaltet. Bestehende Tests für 1.703 Titel, begrenzte 240 sichtbare Datensätze, Zurückscrollen, Adult-Kategorien, Resume und Genrefilter bleiben erhalten. Neue Seitenproben decken 0/1/23/24/25/48/49/500/1.703 Einträge für beide Medienarten ab.

Neu: Seiten prüfen vor/nach dem Lesen Katalogrevision und Aktualisierungskennung. Ein anderer Datenstand wird nicht an die alte Liste angehängt. Stattdessen lädt der bestehende Worker neu und sucht die markierte Sender-/Titel-ID an ihrer tatsächlichen Position. Bei geschrumpftem Katalog wird genau eine gültige letzte Seite nachgeladen. Endstatus meldet das echte Katalogende. Widget-Detailaufrufe lesen ihre einzelne ID jetzt im Datenworker, nicht im GUI-Completion-Callback.

Suchzeilen ergänzen Sprache, bekannte Qualitätskennzeichen, Staffelzahl und aktuellen Portalnamen ausschließlich aus vorhandenen typisierten Metadaten. Keine aus Dateinamen geratenen 4K-/Sprach-/Staffelangaben. Providerfelder werden im bestehenden Katalogpayload erhalten; keine Schemaänderung oder Neuindizierung. Live-Suchalgorithmus, Tabstruktur und Layout bleiben erhalten. Rock/Rocky, 48→0→48, Tab-Rückkehr und laufende Programmtitel müssen nochmals auf Android geprüft werden.

## Explizite Cover-/Metadatenzuordnung (#111/#151)

Der bisherige Dynamic-Retry liefert nur NOT_REQUESTED und sucht keine neuen Quellen. Im dynamischen Modus führt dieser Aufruf nun zum eigenen Auswahlfenster; der bestehende persistente Queue-Retry bleibt erhalten. Zusätzlicher Detailmenüeintrag „Cover/Bild suchen und zuordnen“ gilt für Filme und Serien.

Quellen: gezielte Provider-Detailaktualisierung, optionale offizielle TMDb-API (Werke oder Personen), offizielle Wikimedia-Commons-Bildsuche und lokale PNG/JPEG-Auswahl. Keine Google-HTML-Suche, kein fremder Scraper, keine Katalog-/Poster-Bulkdownloads. Providerfehler bleiben als PROVIDER_REFRESH_UNAVAILABLE sichtbar, vorhandene Kandidaten gehen nicht verloren.

Der eigene WindowXMLDialog öffnet erst im Owner-Pump nach der Aktion. Ein Datenworker pro Dialog, höchstens zwei Forschungsvorgänge pro Interpreter. Ergebnisse werden nur am Owner angewendet. Geschlossene Fenster ignorieren späte Ergebnisse. Ein fertiges, noch nicht konsumiertes Ergebnis darf nicht durch die nächste Quellenwahl verloren gehen. Kein Container.Update/RunPlugin/Playeraufruf und kein Schließen fremder Modaldialoge.

Bildvorschau lädt und validiert ausschließlich den ausdrücklich gewählten Kandidaten im Worker. Erst „Bild übernehmen“, dann separates „Speichern“ schreibt eine Zuordnung. Metadaten haben eine eigene Feldauswahl mit Vorher/Nachher-Werten und Bestätigung. Erlaubt sind Plot, Genre, Jahr, Rating, Regie, Besetzung, Dauer; Titel, Portal und Medien-ID werden nicht ersetzt. Personenbilder bleiben als Person/Ersatzbild gekennzeichnet und liefern keine Filmmetadaten. Quellen, Lizenzhinweis, Remote-ID/Medientyp und URL-Fingerprint werden getrennt für Bild und Metadaten gespeichert, keine Provideradresse im Manifest.

Private `media_choices43`-JSON-Dateien sind nach Portal, Medienart und ID getrennt. Bilder werden SHA256-adressiert, nach Schreiben geprüft und atomar referenziert. Bestehende Providerdaten bleiben separat erhalten. Manuelle Entscheidung gewinnt gegen Provider-/Fallback-Aktualisierung in Liste, Detail, Suche und eigenen Widgetrouten. Vorschau/Abbrechen erzeugt keinen dauerhaften Profilbestand. Reset entfernt ausschließlich die eigene Zuordnung bzw. eigene Metadaten, niemals die Bilddatei. Vorhandenes Archiv, Queue, Texturecache, Resume und Datenbanken bleiben erhalten. Nur eigene neue temporäre Vorschau-/Commitdateien werden bereinigt.

Manueller Bestand: höchstens 64 MiB (oder kleineres konfiguriertes Budget), zusätzlich unveränderte physische Sicherheitsreserve. Höchstens acht temporäre Vorschauen, je maximal 3 MiB. Kein automatischer Wechsel von Dynamic zu Intern/Extern; nur die ausdrücklich gespeicherte Auswahl liegt lokal. Fehlerhafte Manifeste werden nicht überschrieben; beschädigte Dateien bleiben liegen, Darstellung nutzt den letzten guten Stand oder Providerfallback. RAM begrenzt auf acht Profile; Hashprüfung nur für tatsächlich gelesene Seiten.

HTTP: alle DNS-Antworten öffentlich, direkte Verbindung zur geprüften IP mit ursprünglichem TLS-Hostnamen; bestehender Transport unverändert wiederverwendet. Keine Redirects, Credentialweitergabe, Cookies oder Proxy-/Kodi-Pipeoptionen. API-Bearer nur an den festen TMDb-Host; Bildrequests erhalten ihn niemals. Feste datensparsame Fehlercodes für Auth/404/429/Server/Timeout/TLS/DNS/Format/Limit. JSON maximal 1 MiB, Bild 3 MiB, PNG/JPEG vollständig dekodiert, begrenzte Dimensionen. Deadlineprüfung zwischen Reads ersetzt keine harte DNS-Gesamtlaufzeit; langsame OS-DNS-Auflösung bleibt im begrenzten Worker.

Pillow wird von Kodi 21.3 als `script.module.pil` 5.1.0 ausgeliefert, optionaler Import im Manifest macht es zugänglich. Keine Hostbinärdateien im Paket. Gepinnte Kodi-Quelldateien: [PIL-Beleg](KODI_PIL_PROOF_02943.json). Sonderbuild ohne Decoder meldet IMAGE_DECODER_MISSING; niemals unvalidiertes Bild als Erfolg speichern.

Optionaler automatischer TMDb-Fallback ist AUS und benötigt zusätzlich einen eigenen Read-Token. Nur ausgewählte Detailansicht, keine syntaktisch gültige Providerposter-Adresse, exakter normalisierter Titel + Jahr und genau eine Werk-ID. Eine vorhandene, aber per HTTP defekte Provideradresse löst aktuell keinen automatischen API-Fallback aus; dafür bleibt die explizite TMDb-Quellenwahl. Keine automatische Wahl bei Aladdin 1992/2019-/Namenskollision, Personen oder fehlendem Jahr. Cache/Backoff begrenzt Requests; 401/429 löst keine Schleife aus. Automatischer Fallback füllt fehlendes Poster/Plot, keine Medienidentität. Manuelle Auswahl bleibt vorrangig. TMDb-Nutzung/Rechte und Commons-Lizenzangaben sind unter Lizenzen dokumentiert; keine pauschale Lizenzfreigabe für Providerbilder.

## Ehrlich verbleibender Umfang

- **#151 PARTIAL:** manuelle Auswahl, lokales Fortbestehen, separate Felder und die drei Onlinequellen implementiert. Alle Kandidaten vorab als Thumbnail laden, manuelle Metadaten vollständig in den providerbasierten Genre-/Suchindex integrieren und EPG-Bildauswahl sind FOLLOW_UP. Aktuell erhalten Kandidaten nur nach validierter expliziter Vorschau ein lokales Thumbnail; keine automatische Bildschleife.
- **#111 PARTIAL:** gezielter manueller Wiederholungs-/Quellenwechsel und optionaler Fallback vorhanden; reales Aladdin-/Android-Netzwerkverhalten NOT_TESTED. Kein Versprechen, fehlende oder verbotene Providerbilder herzustellen.
- **#108 PARTIAL/DEFERRED:** bestehender Katalogsync bleibt erhalten; keine automatische Löschung verwaister Bilder, neue Retentionssteuerung oder globale Jobreaktivierung.
- **#206/#207 PARTIAL/BLOCKED:** eigene IndexReader-/Widgetrouten geprüft und manuelle Bilder ergänzt. Tatsächlicher BINGIE-Skin, Logo-Größe und externe SkinShortcuts-XML-/Pythonfehler nicht repariert. Optionaler .41-Adapter bleibt uninstalliert; getrennter reversibler Auftrag nötig.
- **#98/#161/#64 sowie Storage/Downloads/Aufnahmen DEFERRED:** keine Quellen-/Mappingarchitektur, Fernbedienungslerner, Migration oder Lösch-/Speichertests eingeschleust.

Alle funktionalen .43-Aussagen sind Host-/Codebefunde. Android, IR-Rendering, reale APIerreichbarkeit und Geräte-Ressourcen bleiben bis Nutzerprüfung NOT_TESTED.
