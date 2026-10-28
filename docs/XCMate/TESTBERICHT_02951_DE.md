# XCMate .51 – vollständiger Host- und Regressionstestbericht

Auftrag #255, Datum 28.10.2026 (Europe/Berlin). Basis `main` .50: `54759f965aef97b45c846042010d5ae1aa1f8ff3`. Geprüfter Quellbuild: `42e7940032fa40bb7fb2aa5d1d943f8f655f9d32`. Branch `hotfix/xcmate-02951-wizard`.

## Ergebnis

**2.116 Tests PASS in 318.758 s; 0 Fehler, 0 Failures, 0 Skips.** Alle 2.078 bisherigen Testmethoden erhalten; 38 neue. Testnamen und komplette Ergebnisse stehen in `TESTLOG_02951.txt`, zusätzliche Methoden in `NEUE_TESTS_02951.json`, maschinenlesbare Daten einschließlich Log-SHA in `TESTERGEBNISSE_02951.json`.

Der Abschlusslauf erfolgte aus einem sauberen `git archive` des oben genannten Commits mit regulärem Bootstrap, allen drei Upgrade-Schritten, Repository-Build, PO-Validierung (de/en jeweils **1.122 Kontexte**), 92 unveränderten Navigationstexturen/Lizenzen und Python-Syntaxprüfung. Alle bestehenden Socket-/SMB-/SQLite-/Großkatalog-/EPG-/Player-/GUI-/Widgettests wurden ausgeführt, ohne sie zu deaktivieren. Die allein für frühere BINGIE-Originalcompiler-Tests notwendige Hostabhängigkeit `simpleeval==0.9.13` bleibt bestehen; keine neue Kodi-Abhängigkeit.

Bekannte unveränderte Warnungen: `SMBProtocol.py` enthält eine alte Escape-Sequenz; simpleeval verwendet ältere Python-AST-Aliase. Kein neuer Laufzeitfehler und kein dafür übersprungener Test. Der Log enthält ausschließlich synthetische Hostdaten, keine privaten Kodi-Rohlogs und keine echten Portalzugänge.

## Neue Prüfungen

- **Settings (12):** exakte Settings-IDs und Typabbildung, keine Übernahme aus aktivem Portal, vollständige/partielle Daten, fehlendes verdecktes Passwort, bestätigte Verwendung mit Nein-Vorgabe ohne Werte im Dialog, Ablehnen/Manuell/Abbrechen, Korrektur ungültigen Hosts, M3U-URL/-Datei und STB einschließlich Default-MAC und ungültigem Settings-Typ.
- **Gruppen/GUI (14):** 1.201 Gruppen je Typ, höchstens 32 neue Zeilen je Pump, kooperatives 8-ms-Erzeugungsbudget bei künstlich langsamen ListItems, frühe Bedienbarkeit, lazy Tabs, cursorstabile Toggle-Aktionen ohne Add-on-Abfrage, begrenztes Alle/Keine, schneller Tabwechsel und spätes Hidden-Click, Abbruch mitten im Aufbau, Reaktivierung ohne Discovery-Doppelstart, Owner-Thread, 0/1 Gruppen und Fokus nach M3U-Neuzuordnung, neutrale XML-Flächen/Fortschritt sowie redigierte Marker.
- **Worker/Speichern (10):** echte Threadlebensdauer nach Back, nicht blockierende und prozessübergreifende Sperre, Fehler beim Fensteraufbau und Dateisystem-Lock, keine zweite Draft-Konstruktion bei belegtem Slot, Watchdog und unterdrücktes spätes Apply, Fortschrittsbudget, differenzierte AUTH/NET/TIMEOUT-Meldungen sowie echter Staging-Save mit 2.400 Sendern und verifiziertem Bestandsportal.
- **Bestandsschutz (2):** sämtliche 573 bisherigen Quelldateien vorhanden, neun exakte freigegebene Wizard-/Versions-/Sprachänderungen; sämtliche 2.078 bisherigen Methoden ohne neue Skip-Dekoratoren.

Die vorhandenen Wizard-Storage-Regressionsfälle prüfen zusätzlich vollständige SQLite-Neuverbindung nach Save, selektive Gruppenindexierung, Rescan nach Abwahl, Rollback bei Kopierfehler und Verifikationsabweichung, Prepublication-Cancel, M3U-Datei-/HTTP-Streaming, Stalker-Seiten und EPG-Import. Die bisherigen Original-Skinshortcuts- und BINGIE-Tests bleiben vollständig erhalten.

Drei ältere UI-/Argumentprüfungen wurden passend zu #255 aktualisiert: neutrale statt grafischer Fokusfläche; genau die drei Wizard-Picker dürfen einfache Texte verwenden; die native Argumentprüfung bleibt strikt und der Inputaufruf verwendet explizite Kodi-Argumente. Der kleine isolierte First-Run-Adapter stellt jetzt auch die neu benötigten Kodi-Module korrekt vor der Konfiguration bereit. Kein Test entfernt, keine pauschale Ausnahme für andere Menüs.

## Nachweisbare Verbesserung und Grenzen

Vorher: bei 1.201 Kategorien pro Typ 3.603 synchrone Zeilen und Bildpfadabfragen vor nutzbarer Auswahl; wiederholte Abfrage bei jedem Toggle; Alle/Keine bearbeitet die volle Liste in einem Callback. Jetzt: nur aktiver Tab, höchstens 32 Zeilen/Schritt, Bildpfad einmal pro Fenster, keine Add-on-Abfrage beim einzelnen Toggle. Die 8 ms begrenzen kooperativ die Python-Schleife und können einen einzelnen nativen Kodi-Aufruf nicht unterbrechen. Das sind Host-/Codebefunde, keine gemessenen RK3528-Bildraten.

Der tatsächliche Android-Hang-Stack liegt nicht vor. Eine alleinige Gerätegrundursache ist daher nicht behauptet. Plattform-DNS lässt sich nicht sicher aus Python töten; Watchdog gibt die GUI frei, fordert Abbruch an und hält den Worker-Slot bis zur tatsächlichen Rückkehr. Für echten Anbieterzugriff, Android-Rendering, IR-Fokus, Kodi-Neustart und vollständigen Geräteabschluss gilt weiterhin **NOT_TESTED**.

## Bestand und Paket

**564 von 573 alten Quelldateien byteidentisch**, neun exakt gehashte Änderungen und vier additive Dateien (drei Wizard-Helfer und ein neutrales 1×1-Pixel). Live-TV, .42-Kompatibilitätsmodus, Player, EPG-/Artwork-Pipeline, Widgetrouten/-Writer, Skinshortcuts, Portale, Profile, Favoriten, Resume und Autoplay unverändert. Alle 62 fremden WIP-Dateien vor/nach Arbeit unverändert. Keine Geräteaktion, keine Skinänderung auf einem Gerät, keine automatische Installation.

ZIP `plugin.video.xtreammate-0.1.29.51.zip`: **577 Dateien, 3095162 Bytes**. CRC, eindeutige/sichere Pfade, AST und sämtliche Quellbytes PASS. Das Paket wurde zusätzlich unabhängig deterministisch rekonstruiert und stimmt bytegenau überein. Keine Test-/Profilereste, Datenbanken oder Logs im Add-on-ZIP.

SHA256: `15824fdb3d5bd69e210bc834a3a99640dc066344a61ac0034fc571ce563bf421`.

Der finale Liefercommit enthält nur noch Testbericht und geprüftes Paket zusätzlich zum getesteten Quellbuild. Der unabhängige GitHub-CI-Lauf und dessen exakter Kopf/Paket-SHA werden im Draft-PR dokumentiert. Der produktive Veröffentlichungsschritt darf im PR-Lauf nicht ausgeführt werden. Kein automatischer Merge/Release, Issue #255 bleibt offen.

## Android

**W51-01 bis W51-16: alle NOT_TESTED, kein Android-PASS.** Siehe `ANDROID_ABNAHME_02951_DE.md`. Box B prüfen; eine frische Instanz nur in ausdrücklich bereitgestellter Testumgebung. Keine vorhandene Box für diesen Test zurücksetzen. Box A bleibt unangetastet.
