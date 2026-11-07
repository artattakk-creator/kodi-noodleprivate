# XCMate 0.1.29.78 – Ursachen, Reparatur und Grenzen

Basis: `80932cc20502dc267018bfded4f2a8cc0ce77e24` (.77), Auftrag #385 sowie #366/#367/#368/#380. Die .77-Android-Fehler bleiben bestätigte FAIL. Die neue .78 ist **ANDROID_NOT_TESTED**. Es wurden keine neuen privaten Rohlogs verarbeitet oder veröffentlicht.

## Home: Datei vorhanden bedeutet nicht Skin geladen

Das bisherige Gate prüfte die vier/fünf Adapterdateien. Die aktive Include-Wurzel, zentrale Variablenregistrierung und tatsächlich geladenen Controls fehlten als zwingende Voraussetzungen. Der bisherige native Testbuilder kopierte immer sein kompiliertes Ergebnis und führte ReloadSkin aus; ein übersprungener echter SkinShortcuts-Neuaufbau war darin nicht abgebildet. Dadurch konnte `SKIN_PATCH_VERIFIED` trotz nicht geladener Variablen/Controls erscheinen.

Die .78 verifiziert acht Dateien als zusammenhängenden Include-Verbund: Home.xml, Includes.xml, IncludesVariables.xml, IncludesHomeWidgets.xml, IncludesHomeBingie.xml, IncludesBingie.xml, template.xml und overrides.xml. Die 16 eigenen Variablen liegen zentral; Home besitzt einen unabhängigen Laufzeitmarker. Erst aufgelöster Marker und sechs reale Controls erlauben `RUNTIME_READY`. `SKIN_FILES_VERIFIED` allein ist keine Renderabnahme. Fehlender Marker verursacht keine wiederholten getControl-Ausnahmen.

Vorher werden gespeicherte SkinShortcuts, Skin-Einstellungen und generierter Cache ausschließlich lokal inventarisiert und privat gesichert (700/600, SHA256/Readback). Keine Portale/Token einlesen, keine Defaults über Nutzerreihen schreiben. Die acht Dateischritte sind hashgeprüft, atomar pro Datei und mit Rollback; das Original bleibt im Transaktionsbackup. Ein bewusstes Wiederherstellen setzt einen Opt-out gegen erneutes automatisches Patchen.

Nur der exakt bekannte eigene .77-Adapter wird unter der ausdrücklichen #385-Freigabe automatisch korrigiert. Unbekannte/fremde Skin-Anpassungen werden nicht blind überschrieben. Dafür bleibt die bestehende explizite Vorschau unter **Einstellungen → Experimentell → Widget-Einrichtung** beziehungsweise im Widget-Kontextmenü. Die normalen drei Widgetquellen und ihre Routen bleiben erhalten.

Der vorhandene Worker ergänzt fehlende Reload-Hooks ausschließlich in generierten eigenen Widget-Verbrauchern; gespeicherte Verknüpfungen, Reihenfolge und fremde/Kino-Quellen bleiben bytegleich. Ein vorhandenes statisches `reload=...` bleibt erhalten und wird um einen echten Hook ergänzt. Bei Builder-Cache-Hit wird erst nach freier Home-GUI einmal ReloadSkin angestoßen, niemals während Wiedergabe, Editor oder fremdem Modal. Nach Neustart kann die eigene Verbraucherkontrolle ohne erneuten Skinpatch fortgesetzt werden.

## Film-/Serienlisten, Bilder und EPG

Die 24/24 vorhandenen Datensätze sind kein nachgewiesener Providerverlust. Ein gleich großer, älterer Schreiber konnte jedoch eine neuere veröffentlichte Kataloggeneration ersetzen. Die .78 erhält in diesem Fall die bestätigte Generation. Quellen ohne explizite pid werden nur dem tatsächlich aktiven Portal zugeordnet; explizite fremde Portal-IDs bleiben ausgeschlossen. Das native Kein-Dialog-Sentinel 9999 ist nun auch beim Widgetrefresh zulässig.

Bildreferenzen mit öffentlichen, erlaubten Resize-Parametern werden nicht mehr pauschal verworfen. XMLTV-/Provider-HTTP-Metadaten können ausschließlich auf denselben HTTPS-Host normalisiert werden; es wird keine Klartextverbindung aufgebaut. Credentials, geheime Queryparameter, private DNS-Ziele, Protokolldowngrade und fremde Eventidentitäten bleiben gesperrt. Ein vorübergehender DNS-Ausfall widerruft nicht die schon bestätigte, noch gültige Referenz derselben Quelle; eine tatsächliche private DNS-Antwort widerruft sofort. Keine neue Freigabe durch DNS-Fehler.

Ein abgelaufener/futuristischer erster Alias verdeckt keine aktuelle Sendung einer folgenden gültigen Provider-ID mehr. Manuelles Mapping bleibt vorrangig. Die .77-Kette mit Eventfingerprint, Match, Token-/Opt-out-Regeln, HTTPS-Prüfung, tatsächlichem Bilddecode und gemeinsamem Cache wird weiterverwendet; der vorhandene TMDB-Token wird nicht neu importiert oder verändert. Ein URL-Erfolg ist kein sichtbares Bild: native Tests prüfen tatsächliche Pixel in Hero und Programmdetails.

## Navigation und Stop

BINGIE Home selbst ist für einen handle=-1-Aufruf bereits ein gültiger Rückkehranker. Ein konkurrierender Root-Dispatch samt Busy-/ANCHOR_TIMEOUT-Rennen entfällt dort. Eigene Verzeichnis-URLs und ausführbare Builtins werden an einer strikten, einmal quotierten Grenze getrennt; als Verzeichnis gespeicherte eigene ActivateWindow-Hüllen werden nur im generierten Verbrauchercache entpackt.

Fünf Sekunden ohne ACK bleiben eine Beobachtungsgrenze, keine erfolgreiche Stop-Bestätigung. Solange ein nativer Stop unbestätigt läuft, bleiben Player-Abfragen und weitere Stops gesperrt. Ein echtes spätes FIFO-ACK schließt denselben Job mit `late_ack78=true` ab. Der Live-Rückweg hat danach einen eigenen Zustand `return_pending78`: keine falsche STOP_TIMEOUT-Meldung nach ACK, keine automatische zweite Stop-Operation. Erst exakte Session, weiterhin gültiges ACK, freie GUI und keine neue/fremde Wiedergabe geben die Rückkehr frei. Historische Testmethoden bleiben erhalten; ihre späten ACK-Erwartungen wurden an den ausdrücklich geänderten Vertrag angepasst.

## MyVideos131 und offene Gerätediagnose

Fehlende movie_view/tvshow_view/musicvideo_view werden weiterhin mit query_only und begrenztem Lesezeitbudget untersucht. Es gibt **keinen belegten sicheren Schema-Reparaturplan** für die private Android-Datenbank. Deshalb keine View-Neuanlage, DB-Löschung oder Bibliotheksmigration. XCMate-Providerwidgets bleiben unabhängig nutzbar. Eine fremde „Neu im Kino“-Quelle, die tatsächlich fehlende Kodi-Views benötigt, bleibt bis gerätespezifischer Diagnose **BLOCKED**; ihre Verknüpfung wird erhalten. Eine funktionierende synthetische Kinoreihe beweist die Render-/Erhaltungsfähigkeit, nicht die Reparatur jeder fremden Kodi-Datenquelle.

Installer 0.5.26, Space Blue, bestehende Profile, Favoriten, Provider, EPG-Mappings, Resume und Autoplay werden nicht zurückgesetzt. Die Sofortveröffentlichungsfreigabe gilt nur für das hashgebundene .78-Paket, ausdrücklich ohne Android-PASS.
