# .60 – vollständiger Hostbericht und Abnahmegrenzen

Auftrag #284; aktuelle kumulative .59-Basis `551a69a327f0bf2e54e594edadd384d2c16ae215`. Getesteter Add-on-Source-Commit `085cd9f6230b5281d420bb08163e4556bee20036`. Kein Merge/Release und keine Box-A-/Box-B-Aktion.

## Vollständiger unveränderlicher Build

**2514 Tests PASS in 343.241 s**, 0 Fehler, 0 Fehlschläge, 0 Skips. Alle 2.491 bisherigen Methoden/Skipbedingungen erhalten, 23 neue. Vollständiger Output TESTLOG_02960.txt; maschinenlesbare Ergebnisse und Methodeninventar beigefügt. git-archive-Checkout, gepinnter Bootstrap/Upgrades, Repositorybau, beide PO-Dateien (1.132 Kontexte), 92 Icons/Lizenzen, Compile und Source-AST bestanden. Bekannte unveränderte vendorte SMBProtocol.py-Escape-Warnung und simpleeval-Deprecations sind keine neuen Laufzeitfehler.

Die vollständige Suite verwendet echte lokale synthetische HTTP-/SMB-Server, große XMLTV-/M3U-/SQLite-Datensätze sowie vorhandene Player-/Owner-/Wizard-/Autoplay-/EPG- und Artwork-Regressionen. Sie hat die erforderlichen Sandbox-Netzwerkrechte; kein reales USB-/SMB-Laufwerk oder Nutzerportal wurde angesprochen. Ein früher explorativer Lauf ohne diese Rechte ist kein PASS-Nachweis. Alte Tests wurden für den nun positionsunabhängigen Live-Aufbau, strengere vollständige TMDB-Antworten/lokale Bildbytes und beide gültigen endOfDirectory-Aufrufstile präzisiert; keine Methoden oder Skips entfernt. Historische Source-Freezeprüfungen normalisieren nur exakt gehashte reviewte Deltas; .60 friert seine eigene Basis zusätzlich ein.

## Echter nativer Home-/Pixelvertrag

Kodi **21.2 Linux**, echte **BINGIE MOD 2.2.3 Home.xml** und Ressourcen, native Home-ID **10000**, offizielles gehashtes ZIP und gepinnter Skinshortcuts-2.1.0-Templatecompiler. Externe Helper-Startskripte und Menü-/Providerdaten sind ausgewiesene Hostfixtures; keine echte Android-/Provider-/TMDB-Serverabnahme.

88 echte Directory-ListItems und unterschiedliche vorhandene play_live-Ziele; komplette Startgruppe und letzter Sender erreichbar. Kleine Logos, zwei unterschiedliche dekodierte Hero-Flächen, drei passende fokussierte Logos, Neutralbild ohne EPG, passende Titel/Beschreibung/Now/Next. Kein Playerstart. Die vorhandene gespeicherte Live-Quellenfactory wird unverändert benutzt. Ein zusätzlicher Directory-Test führt die historische URL ohne home50 aus. Bildnachweise prüfen fertige PNGs und tatsächliche Pixel; kein PASS aus PUBLISHED oder Containeranzahl allein.

Host-Bildbereitschaft inklusive Screenshot/Animation: Fokus 0 **3588 ms**, Fokus 1 **787 ms**. Dies sind keine IR-/Android-Latenzwerte. Der Test startet Kodi real mit dem gespeicherten Skin neu und findet vorher lokal gespeicherte Bilder wieder. Anfängliche Capture-/Fade-Frames werden nicht als endgültiger Screenshot gewertet. Vorheriger Adapterdefekt ist separat durch reale false/true-Auswertung der alten URL-Bedingungen belegt; neuer Compiler erzeugt passende konstante Bedingungen und schützt fremde verschachtelte Pluginquellen.

Zusätzlich beide unveränderten Medien-Verzeichnisse: 24 VOD- und 24 Serien-Items, exakte pid/kind/sid-Ziele und Provider-URL-Posterhashes; je zehn tatsächlich dekodierte unterschiedliche synthetische Providerposter im nativen Kodi-Testfenster. Diese Medienpixel sind ausdrücklich keine volle Android-BINGIE-Abnahme. Alle Nachweise sind getrennt beschriftet.

Auch der bestehende echte Kodi-Transportvertrag besteht: verschachtelte Worker-RPCs, richtige Film-/Episodenidentitäten, unveränderte GUI/Dialoge und kein Playerstart. Paralleler Host-Ping 209 ms; kein Test eines echten externen Helpers oder TMDB-Kontos. KODI_TRANSPORT_02960.json liegt bei.

Die drei Home-Screenshots werden mit eindeutigen Capture-Dateien erzeugt. Exakt die bereits dekodierten und geprüften Bytes werden atomar als Testnachweis übernommen; SHA256 steht im JSON und wird nach dem Kopieren verglichen. Dadurch überschreibt kein späterer asynchroner Kodi-Capture den geprüften Frame.

## TMDB / Skin / Bestand

Synthetisch geprüfte HTTP 200/401/403/429, DNS/TLS/Timeout/ungültige Antworten, Token fehlt, privater Bearer nur am offiziellen Ursprung, Rate-Limit/Retry-After, GUI-Thread frei von HTTP, ausgeschaltete Voreinstellungen, exakte Film-/Episodenidentität und Mehrdeutigkeit. Geprüfter Pfad durch echte Produktionsfunktionen: Suche → Detailnachweis → validierte PNG-Bytes → persistenter gemeinsamer Ereignis-/Bildcache → lokaler Leser nach RAM-Neustart ohne HTTP. Negative Bildzustände werden bei lokaler Freischaltung gezielt neu bewertet.

Skin-Planvorbereitung, exakte 2.2.3-Hashes, ausdrückliches Opt-in, echte Diff-Vorschau, atomare Mehrdateienübernahme, fremde Änderungen, Unterbrechung/Rollback/Restore und alte bekannte Adaptervarianten sind abgedeckt. Es wird keine Nutzer-Skinshortcuts-XML direkt geschrieben. 612 frühere Add-on-Dateien: 591 byteidentisch, 21 exakt reviewte Änderungen, sieben additive Dateien; keine entfernt. Fremde laufende Arbeiten: 62 Hashes unverändert. Original-Icon, gespeicherte Widgets-URLs/Ordner, Provider-VOD-Pfade, .59-EPG-Import, Stop/.42/Rückkehr und Wizard raw geschützt.

## Paket und CI

`plugin.video.xtreammate-0.1.29.60.zip`: **619 Dateien / 3192447 Bytes**. CRC, sichere Pfade, alle Sourcebytes, Python-AST und unabhängiger deterministischer Neuaufbau PASS. SHA256:

`9d2f16a91bafde131bf8e25da517a65c0c3e1e6457272f5df92fd6d7a1dfde39`

Die CI führt zusätzlich zum bestehenden nativen Transport-/Medienvertrag den neuen BINGIE-Home-Vertrag aus und lädt JSON/PNG-Nachweise hoch. Konkreter Lauf am finalen PR-HEAD, vollständiger Hostlog, CI-Paket mit identischem innerem ZIP-SHA und Publish-SKIPPED-Nachweis werden im Draft-PR verlinkt. Der Hash des äußeren Artefaktcontainers ist nicht die SHA des Installations-ZIPs.

## Offene Freigaben

Alle echten Box-B-/Android-ARM32-/Kodi-21.3-Punkte **NOT_TESTED**. Realer eigener TMDB-Token und private Serverantworten **NOT_TESTED**; kein Token angefordert oder veröffentlicht. Sichtbare Providerposter/Klickziele, Skin-Opt-in auf dem tatsächlichen Profil, GUI-/Decoder-Rückkehr und Neustart auf Box B bleiben Nutzerabnahme. Box A unverändert. Öffentliche kommerzielle TMDB-Nutzung nicht pauschal freigegeben. Kein Issue geschlossen. Kurze spätere PASS/FAIL/ÜBERSPRINGEN-Liste liegt bei.

## Reproduzieren

Frisches Checkout, Python 3.12 und CI-Abhängigkeiten. Bootstrap/Upgrades und Repositorybau wie im Workflow; `python -m unittest discover -s tests -v`. Native Prüfungen: `python tools/run_kodi_helper57_contract.py --report-dir transport`, `python tools/run_kodi_widget59_contract.py --report-dir media`, `python tools/run_kodi_home60_contract.py --report-dir home`. Docker und korrekte Proxy-/CA-Konfiguration erforderlich; keine Nutzerprofile oder Tokens als Fixtures verwenden.
