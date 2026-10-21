# XCMate 0.1.29.3 – Android-Ersteinrichtungs-Hotfix (21.10.2026)

**Befund am echten Gerät:** Frisch zurückgesetztes Kodi 21.3, Estuary, XCMate 0.1.29.2. Bei Konto-/Quellenanlage meldet der Assistent `Import fehlgeschlagen – ValueError – bestehende Accounts bleiben erhalten`; sichtbarer Navigationsfokus fehlt, Richtungstasten wirken erfolglos.

## Im Quellcode nachgewiesene Fehler
- `setup_window.py::SetupWindow.onInit` startete die asynchrone Anbieter-Entdeckung, während `XCMateSetup.xml` standardmäßig `<defaultcontrol>100</defaultcontrol>` besaß. Die Liste Nr. 100 ist zu Beginn noch leer; nicht sichtbare bzw. unangemessene Fokusübergänge lassen die Fernbedienung unbedienbar wirken.
- `WorkWindow.work` meldete beliebige Exception lediglich mit `type(exc).__name__` im Status. Bei einem Fehler der ersten Entdeckung blieb `stage='discover'`, ohne navigierbaren Fehlerbildschirm oder erneuten Versuch.
- Bei ausschließlich VOD-/Serien-Kategorien wurde nach der Entdeckung pauschal der Bereich Live gewählt; die leere Liste konnte erneut fokussiert werden.
- XML-Fokus für Listen war nur über die Hintergrundtextur signalisiert, ohne zusätzliche Textmarkierung. Button-Fokusfarben waren weiß und damit teils schwer erkennbar.

## Gezielte Änderung
- Während der Anbieterabfrage: **sichtbarer, fokussierter Abbrechen-Button**, Liste und Gruppenschaltflächen ausgeblendet.
- Bei Entdeckungsfehler: **fokussierter „Erneut versuchen“-Button** plus Abbrechen.
- Fehlerarten über feste, **credential-freie** Codes `XM-SETUP-AUTH/GROUPS/SELECT/EMPTY/DATA/NET/OTHER` und verständliche Hilfetexte statt generischem `ValueError`. Im Protokoll nur Phase, Typ und Code; nie Passwort, Benutzername oder Portal-URL.
- Fokus nach erfolgreicher Abfrage auf erste verfügbare Art (Live, Filme, Serien) und deren Liste.
- Fokusmarkierung `▶` für Gruppen und türkis hervorgehobene Schaltflächen; vorhandener Live-TV-Overlay-/IR-Freeze bleibt unangetastet.
- Version **0.1.29.3**; acht neue Tests in `tests/test_xcmate_0293_setup_first_run.py` plus Versionslayoutregression.

## Grenzen / gesicherter Stand
Der ValueError kann in `source_adapters.Adapter.authenticate` bei `authentication failed`, in `Draft.discover` bei `no usable categories` oder an anderen Validierungspunkten entstehen. **Seine tatsächliche Ursache beim konkreten IPTV-Account ist ohne gerätespezifischen Log-/Fehlercode nicht bestätigt**. Der Hotfix behebt den blind/unbedienbaren Fehlerzustand und schafft diagnostische Codes, garantiert aber keine Anmeldung an einem unbekannten Portal. Dieser Hotfix ersetzt auch nicht die Android-GUI-Abnahme. GUI-Änderungen aus der bestehenden Async-Callbackstruktur sind auf dem Android-Gerät mit echter IR zu testen.

## Vor Android-Freigabe
1. Prüfe lokalen/CI-Build; Test-ZIP `plugin.video.xtreammate-0.1.29.3.zip` nur aus der unveröffentlichten PR-CI laden, SHA/CRC checken.
2. Auf der frisch aufgesetzten Box unter Estuary zuerst mit bewusst ungültiger Anmeldung testen: Fehlercode und sichtbar fokussiertes „Erneut versuchen“ bzw. „Abbrechen“. Nie echte Kennwörter als Screenshot/Log veröffentlichen.
3. Danach mit echten Zugangsdaten (privat nur am Gerät) anmelden: verständlicher Status während Erkennung, Gruppenwahl sichtbar, IR ↑/↓/OK/Links/Rechts, Checkboxen und Weiter, Speichern/Neustart.
4. Mit einem Provider ohne Live-Gruppen testen, der Film-/Seriengruppen liefert; Focus muss deren Einträge zeigen.
5. Falscher Provider, leere Kategorien, kein Internet, Zurück, mehrfacher Retry, Abbruch und bestehende Portalinfos prüfen; **kein Reset und keine Datenlöschung**.
6. Bei weiterhin ausbleibendem Import nur **Fehlercode `XM-SETUP-…`**, Zeitpunkt/Schritt und bereinigtes `kodi.log` melden. Keine Account-URL, Xtream-User, Kennwörter, Tokens oder M3U-Voll-URLs in Issues oder Chat teilen.
7. Kein Merge nach `main` oder neues Release ohne Freigabe; PR #50 (0.1.30 Space Premium) erhält den Fix gesondert nach Abnahme, nicht versehentlich durch automatischen Merge.
