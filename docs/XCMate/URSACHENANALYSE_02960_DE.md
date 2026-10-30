# XCMate .60 – BINGIE Home und private TMDB-EPG-Bilder

Auftrag #284, Stand 30.10.2026. Kumulative Basis main .59 `551a69a327f0bf2e54e594edadd384d2c16ae215`, gemergter PR #283. Maßgeblicher neuer Nutzerbefund: Filme und Serien sind zumindest als scrollbar bedienbare Reihen sichtbar. Deren vollständige Poster-/Klickzielabnahme bleibt offen. Live-TV fehlt auf Box B. Box A und Box B wurden in dieser Sitzung nicht verbunden oder verändert.

## Belegter Adapterdefekt und gezielte Korrektur

Der unveränderte native Live-URL-Vertrag wird vollständig ausgeführt: Plugin-Einstieg, lokaler Startgruppenkatalog, 88 eindeutige Senderziele, echte Kodi-ListItems und erfolgreiches endOfDirectory. PUBLISHED allein wird nicht als Nachweis verwendet.

Der bisherige .50/.55-Skinadapter entscheidet im laufenden Kodi mit `String.StartsWith(plugin://…literal…,plugin://plugin.video.xtreammate/)` und `String.Contains` über LiveRow statt widget_base. Im tatsächlichen Kodi-21-Home auf BINGIE 2.2.3 wurde die kombinierte Live-Bedingung für die gespeicherte XCMate-Quelle als **false**, die gegenteilige Stock-Bedingung als **true** gemessen. Der Screenshot zeigte entsprechend große generische Posterkacheln, obwohl die zusätzliche Hero-Bedingung bereits aktiv sein konnte. Das ist ein reproduzierbarer Defekt des vorhandenen Adapters. Es beweist ohne aktive Box-B-Dateien nicht allein die Ursache jeder dort unsichtbaren Reihe.

`widget_skin60` verlegt die Entscheidung in den vorhandenen Skinshortcuts-2.1.0-Templatecompiler. Er prüft den exakten Plugin-Ursprung und den vollständigen Aktionsnamen anhand des unveränderten gespeicherten Strings. Im generierten Include stehen anschließend konstante true/false-Bedingungen; Kodi muss keine vollständige Plugin-URL als InfoLabel auswerten. Verschachtelte XCMate-Adressen in fremden Pluginquellen wählen den Live-Adapter nicht aus. Die Kindparameter sämtlicher normalen Film-/Serien-Consumer bleiben erhalten.

Die neue Darstellung verwendet eine native horizontale fixedlist mit kleinen Logos, ohne Inhaltslimit. Hero, Now/Next, Uhrzeit, Beschreibung, Fortschritt und Quelle werden weiterhin über dieselben vorhandenen Programmeigenschaften gebunden. Der native Home-Test prüft Fokus 0, 1 und 87, zwei unterschiedliche dekodierte Hero-Bilder, drei Logo-Pixelbereiche und neutralen No-EPG-Zustand. Kein separates Live-View-Fenster wird dafür geöffnet. Kein Player startet beim Fokus.

Die bestehende Live-Aktion akzeptiert mit unveränderter URL auch ältere Aufrufe ohne home50-Flag; diese liefern ebenfalls die vollständige Startgruppe. Das Rendering bewahrt deren Katalogreihenfolge, statt den Startsender nach vorne zu sortieren. Startsender/-gruppe im Portal bleiben unverändert. Die Diagnose erkennt nun auch Live und den eigenen generierten LiveRow-Consumer. Bindung, generiertes Include, tatsächlicher Directory-Aufruf, ListItems und sichtbarer Home-Container werden getrennt behandelt; laufende Diagnosen behaupten keine verifizierten Bildpixel.

## Skin-Schutz und überprüfbare Hostumgebung

Es gibt **keinen automatischen Skinpatch beim Update**. Die vorhandene Widgetverwaltung erstellt nach Benutzeraktion einen privaten Vier-Dateien-Plan, zeigt SHA256 und jetzt den tatsächlichen Diff und verlangt ausdrücklich Bestätigung. Unbekannte Dateien oder Versionen werden blockiert. Die bestehende atomare Backup-/Apply-/Restore-Transaktion und Konkurrenz-/Abbruchprüfungen bleiben erhalten. Bekannte unveränderte .50/.55-Adapter können kontrolliert aktualisiert und der neue Plan wieder zurückgenommen werden. Keine generierte Benutzer-Skinshortcuts-Datei wird direkt überschrieben; ein nativer Rebuild wird nur nach bestätigter Übernahme angefordert.

Prüfgrundlage ist ausschließlich das offizielle BINGIE-2.2.3-ZIP, SHA256 `7216dcf7efeac7cb668cde97bdde45b681ed77b5e9007368d3b46c3c98e52e8b`, aus dem gepinnten Repository-Commit `f3afa9927f61713f5d0614639c18ca95a51999a1`. Keine 2.2.2-Dateien wurden als Patchbasis übernommen.

Der Host lädt echte BINGIE-Home.xml, Includes, Fonts und Texturen in Kodi Linux; die vier ausdrücklich geprüften Kandidatendateien bilden die optionale Änderung. Die synthetischen Menü-/Quellenwerte werden vom gepinnten nativen Skinshortcuts-2.1.0-Compiler verarbeitet. Externe Helper-Startskripte sind ausschließlich im wegwerfbaren Hostprofil No-ops; Registrierungsabhängigkeiten sind dort reduziert. Das native BINGIE-Startvideo wird nur in diesem Testprofil über dessen vorhandene Einstellung abgeschaltet. Produktionscode enthält keinen entsprechenden Stop oder Einstellungswechsel. Ein echter Kodi-Neustart lädt den zuvor gespeicherten Testskin und persistierte Bilder.

Die im Host gemessenen Bildbereitschaftszeiten schließen Screenshot-/Textur-/Animationsarbeit ein und sind keine Android-Latenzmessung. Der Test wartet auf echte fertig kodierte Bildpixel; weder Containeranzahl noch bloße PNG-Existenz genügen.

## TMDB-Verbindung und gemeinsamer Bildpfad

Unter EPG sowie im nativen Konfigurieren-Dialog ist „TMDB-Verbindung testen“ erreichbar. Ein einziger begrenzter HTTPS-GET auf /3/configuration verwendet den lokal hinterlegten API Read Access Token als Bearer-Header. Der GUI-Thread führt keine HTTP-Anfrage aus. Ergebnisse sind TMDB_OK, TOKEN_MISSING, HTTP_AUTH, HTTP_RATE_LIMIT, TIMEOUT, NETWORK_ERROR oder INVALID_RESPONSE. Es werden keine Tokens, Header, privaten URLs oder Exceptiontexte protokolliert. Ein API-Key wird nicht in eine URL geschrieben.

Die vorhandenen beiden Opt-in-Schalter bleiben standardmäßig false, das verdeckte Tokenfeld bleibt leer. Nichts wird für andere Nutzer oder Box A aktiviert. Der Verbindungstest allein ändert keinen Schalter. Echte eigene Zugangsdaten wurden in dieser Sitzung nicht bereitgestellt oder gelesen; realer TMDB-Zugang auf Box B bleibt NOT_TESTED. Der Cloud-Host hat außerdem keinen freigegebenen TMDB-Netzzugang. Automatisierte Auth-/Netzfälle verwenden ausschließlich synthetische Transporte.

XMLTV- und Provider-Eventbilder bleiben vorrangig. Die optionale eigene TMDB-Suche folgt vor den vorhandenen kontrollierten Katalog-/Helper-Fallbacks. Sie akzeptiert nur exakte normalisierte Titel, eindeutige vollständige Suchantworten und passende Jahres-/Detailnachweise. Episoden benötigen richtige Serie, Staffel, Folge und gegebenenfalls Episodentitel. Die konservative, bereits vorhandene Jahreslos-Filmlogik behält ihren vollständigen Eindeutigkeits- und unabhängigen Detailnachweis. Remakes, Teilseiten, ähnliche Titel und abweichende Folgen liefern kein geratenes Bild.

Ein bestätigtes TMDB-Bild wird über den vorhandenen programme_art46-Pfad validiert, größenbegrenzt und persistent gespeichert. guide_v1 und die bereits bestehende gemeinsame programme_artwork.sqlite bleiben die einzigen jeweiligen Datenbestände; keine neue Bild- oder EPG-Datenbank. Programmdetail und Home lesen denselben Ereignisschlüssel und lokalen Bildpfad. Zuverlässige EPG-Texte werden nicht durch TMDB-Daten ersetzt. Token-/Opt-in-Änderungen invalidieren passende negative URL-Nachweise gezielt. HTTP 429 pausiert weitere eigene TMDB-Anfragen mindestens fünf Minuten und berücksichtigt längeres Retry-After bis maximal einen Tag. Parallelität, Warteschlangen- und Bildbudgets bleiben begrenzt; keine Suche beim Fokus und kein vollständiger Import beim Home-Aufruf.

TMDB-Logo und Nicht-Endorsement-Hinweis erscheinen im Quellenbereich. Herkunft und Trademark-Hinweise stehen bei resources/media/tmdb60/NOTICE.txt. Die freiwillige eigene Developer-Anbindung begründet keine pauschale kommerzielle Freigabe; öffentliche Verteilung/Nutzungsrechte bleiben separat zu klären. Kein gemeinsamer Token ist enthalten.

## Bestand und Grenzen

Widgets-Ordner, widget_sources49, widget_binding50 und gespeicherte Quell-URLs bleiben byteidentisch. Das vorhandene Reload-/Clock-Verhalten dieser Quellen wird verwendet; kein neuer URL-Parameter und kein Rebind. Provider-only VOD/Serien, added-DESC-Sortierung, normale Wiedergabeziele, .59-EPG-Import und ACK→GUI-Rückkehr, .42-Kompatibilitätsmodus, Wizard, Resume und Autoplay bleiben geschützt.

PR #282 wurde vollständig als sichere Vorschau-/Architekturreferenz geprüft; sein älterer Versionsstand und der redundante Dialog werden nicht blind übernommen. .60 repariert den nativen Home-Consumer. TVmaze PR #280 bleibt getrennt.

Android ARM32/Kodi 21.3, tatsächliche Box-B-Bindungen, reale Providerposter, privater TMDB-Zugang, Decoder-/Player-Rückkehr und Neustart auf dem Gerät bleiben NOT_TESTED. Der native Host verwendet Kodi 21.2 mit kompatibler Kodi-21-GUI, nicht eine behauptete 21.3-Geräteinstanz. Kein Merge, Release, Profilreset, Geräteupdate oder Skinzugriff auf Box A/B.
