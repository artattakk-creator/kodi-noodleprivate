# XCMate .57 – vollständiger Host- und Regressionstestbericht

**2.418 Tests PASS in 326.144 s, 0 Failures/Errors/Skips.** Alle 2.369 vorherigen Testmethoden und deren Skipbedingungen erhalten; 49 neue Methoden. Vollständiger synthetischer Hostlog `TESTLOG_02957.txt`, neue Methoden `NEUE_TESTS_02957.json`, maschinenlesbarer Bericht `TESTERGEBNISSE_02957.json`.

Sauberer git-archive-Quellstand `4a882d813c962a4fdd2a96f556dc73b8013ca34a` auf main .56 `34e7e17aff797e736447cae3760667a2ffa9563a`. Bootstrap, historische Upgrades, Repository-/Paketbuild, Sprachvalidierung (je 1.131 Kontexte), 92 Navigationstexturen mit Herkunft/Lizenz und Python-compileall bestanden. Python 3.12 mit Pillow, impacket 0.13.0 und simpleeval 0.9.13. Echte lokale HTTP-/Socket-/signierte SMB2-/SQLite-/WAL-/Großdaten-/Unterbrechungsfälle wurden ausgeführt; keine netzbedingten Skips. Die vorhandenen Vendor-Syntax-/AST-Warnungen wurden nicht durch ungefragte Vendoränderungen verdeckt.

## Neuer Funktionsnachweis

Ohne XCMate-eigenen TMDb-Token: öffentlicher Helper-Erkennungs-/Such-/Detailsweg, vollständiger Harry-Potter-Titel/Jahr/ID, unabhängige Details, fehlendes Genre/Jahr nur bei Cross-Type-Eindeutigkeit, falsche Fortsetzung/Remake/Seitenbegrenzung/fehlende ID, deaktivierter oder unbekannter Helper, unsichere URLs und `image://`-Wrapper. Serien-ID und unterschiedliche Episoden-ID, Saison/Folge/Showtitel/Untertitel, kein Parentposter als exakter Still; generische Serienbilder zurückstellen und sichtbar kennzeichnen. Kaputtes Fanart → gültiges Poster sowie kaputter Episodenstill → gekennzeichneter Serienfallback durch denselben URL-Validator, ohne zweite Metadatenrecherche.

Echter lokaler Guide/Event-/Artworkindex verbindet EPG-Control 110 und Widget über identische Event-ID/URL. Persistenz nach RAM-Neustart, Quellen-/Mapping-/Zeit-/Sender-/Titelgrenzen, vorhandene positive .56-URLs ohne globalen Retry, Abbruch ohne späte Datenpublikation, priorisierte angekündigte Filme in bereits begrenzter lokaler Seite. Vorhandener SQLite-Medienkatalog, Portal-/Gruppen-/Jahresschutz und öffentliche Kodi-Libraryfälle. RPC auf separatem Thread, GUI-/Player-/Settingsbefehle ausgeschlossen, maximal ein nativer Aufruf trotz wiederholtem Timeout, Abbruch und begrenzte private Fehlerrückgaben. Box-B-Prüfer verlangt ausdrückliche Endpunktauswahl, verweigert Credential-URLs und protokolliert Offline/Metadaten niemals als Android-PASS.

## Echter Kodi, getrennt von Mocks und Android

Zusätzlich ausgeführt: Docker/Kodi **21.2 Omega auf Linux**, frisches isoliertes Profil, eigenes **synthetisches** Plugin. Native ListItem-Tags und JSON-RPC mit Film-/Serien-/Episoden-IDs, nativer Bild-Wrapper, Hintergrund-Reentrancy innerhalb Kodi, paralleler Ping bei drei Sekunden langsamem Plugin, unveränderte GUI/Dialog/Player. Lokaler Bericht `KODI_HOST_TRANSPORT_02957.json`: Ping nach 208 ms, kein Playerstart. Wiederholbares Werkzeug `tools/run_kodi_helper57_contract.py`; eigener verpflichtender CI-Job vor dem Paketjob. Containergrundlage auf Digest gepinnt, TLS-/Proxy-/CA-Vorgaben eingehalten, keine Produktivprofile oder Geräte eingebunden.

**Dies ist kein echter TMDb-Helper-/API-/Bild-/Android-Erfolg.** Helper 6.19.4 wurde als öffentliche Schnittstellenreferenz geprüft; die tatsächliche Box-B-Version ist unbekannt. Der echte native Transporttest und die synthetischen Lookup-/Bildreferenztests werden deshalb nicht als heruntergeladene/angezeigte Filmbackdrops ausgegeben.

## Bestandsschutz und Zwischenbefunde

606 Paketdateien: sämtliche 602 vorherigen Dateien erhalten, 592 byteidentisch, zehn exakt deklarierte überprüfte Deltas und vier neue Adaptermodule. 60 Routing-/Widget-/Wizard-/Import-/Player-/Skin-Dateien zusätzlich auf direkte identische Rohbytes geprüft; keine Normalisierung für diese Schutzgates. Historische Prüfer normalisieren ausschließlich die exakt gehashten .57-Deltas, neue Tests prüfen den heutigen Adapter direkt. 62 fremde WIP-Dateien in anderen Arbeitsbäumen SHA256-unverändert. Box A und Box B unverändert, keine Rohlogs/Providerdaten veröffentlicht.

Eine erste neue Testfixture führte die zwei optionalen Quelleinstellungen fälschlich als scheinbar gespeicherte Werte. Bestehende Tests erkannten dies über die Erwartung unveränderter Einstellungen. Die Fixture isoliert nun die neuen Backends nur über Defaultleser, ohne Einstellungen zu erfinden. Eine fehlende PO-Leerzeile trennte den letzten alten String nicht für den strikten gebündelten Leser; beide Sprachdateien sind korrigiert und sämtliche Referenzen geprüft. Ein neuer Rohhash-Test erwartete eine erfundene Mindestzahl100 statt der tatsächlich aufgelisteten 60 Dateien; er prüft nun exakt60 und weiterhin alle Bytes. Der gemeinsame Serienfixture-Schlüssel wird nach Änderung des Testtitels korrekt neu gebildet. Kein alter Test entfernt/übersprungen oder Produktivrouting zur Anpassung eines Tests verändert. Ein früher provisorischer Gesamtlauf wurde bei einer Neuverbindung der Ausführungsumgebung unterbrochen; er ist kein Abschlussnachweis. Maßgeblich ist allein der hier dokumentierte saubere Gesamtlauf.

## Paket und Abnahme

`plugin.video.xtreammate-0.1.29.57.zip`: 3,162,223 Bytes, 606 Dateien. SHA256:

`4fdb7de5292632cf8b4f29ec73680014429f85bfadc30e731c0606b6e40a1b09`

CRC, sichere Pfade, keine Symlinks/Profile/DBs/Rohlogs/Bytecodes, jede Sourcebyte-/AST-Prüfung und unabhängiger deterministischer ZIP-Nachbau PASS. Paketbericht, Dateikatalog und Schutzbericht enthalten die Einzelbelege. Abschließende GitHub-CI am finalen Delivery-Head und Paketgleichheit werden im Draft-PR verlinkt; kein main-Merge oder Release.

**Acht Android-Gates NOT_TESTED, Gerätezugriff BLOCKED_DEVICE_ACCESS.** Ausführbarer öffentlicher Metadatenprüfer und deutsche H57-01 bis H57-08-Abnahme liegen bei. Reale Helper-Version, Bildbeschaffung, korrekte sichtbare Harry-Potter-/Episodenbilder, echte Event-/URL-/Pixelgleichheit nach Neustart sowie Decoder-/Fernbedienung bleiben Geräteabnahme. Ohne separate Skinfreigabe kein Heroadapter-Eingriff. TV Spielfilm ohne autorisierte API blockiert, TVmaze optional nicht neu implementiert. Wizard #269 weiterhin separat offen. Kein behaupteter Abschluss von #273/#274 ohne echte Bildabnahme.
