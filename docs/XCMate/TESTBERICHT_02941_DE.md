# XCMate 0.1.29.41 – Testbericht und Lieferung

**1.479 Hosttests PASS**,0 FAIL,0 ERROR,0 SKIP in **230,409 s**. Alle **1.435** bisherigen Testmethoden aus main .40 erhalten, **44 neue**. Alle neuen Android-Gates **NOT_TESTED**; keine Geräte verändert, kein Merge/Release.

Basis main .40: `6c362a45582350c694e4e18c13581cd57cd31d70`, Merge #205. Vollständig getesteter Quellstand: `edacc729a369ddcc867f090a55bb4b630265a5e4`. Spätere Lieferdokumente/ZIP ändern den Add-on-Code nicht. Aktueller grüner GitHub-CI-Lauf und heruntergeladener Artefaktabgleich werden vor Übergabe direkt im Draft-PR ergänzt.

## Testpaket

- [plugin.video.xtreammate-0.1.29.41.zip](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.41.zip): **390 Dateien /2.657.296 Bytes**.
- [SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.41.zip.sha256)
- SHA256: `60b4b8fecdfddc5ad5b9adf2503758746deb6f911b31280d9c763e3fb2e882f1`
- CRC, eindeutige sichere Pfade, keine Symlinks, keine Profile/Logs/Tests/DBs im Add-on: PASS.
- Jede Datei bytegleich zur Quelle, Python-AST gültig, unabhängiger deterministischer Neubau bytegleich: PASS.
- [390 Einzeldatei-Hashes](DATEIKATALOG_02941.json), [maschinenlesbare Ergebnisse](TESTERGEBNISSE_02941.json), [vollständiges grünes Hostlog](TESTLOG_02941.txt).

Nur kumulativer Branch-Testkandidat. Produktionsindex und .40-Paket unverändert; keine reguläre Repository-Veröffentlichung.

## Gezielte Nachweise

| Bereich | Automatisierter Nachweis | Grenze |
|---|---|---|
| Live-Stop,9 neue Methoden | Kein synchroner Python Player.stop-Aufruf, feste asynchrone Queuebefehle, richtige/falsche/fehlende/späte FIFO-Barriere,20 erfolgreiche Modellzyklen, neue/fremde Session, Timeout ohne Replay, fehlgeschlagene Barriere nach möglichem Stoppost quarantänisiert | Keine native Kodi-/ARM32-Ausführung; Decoder-Deadlock nicht als geheilt behauptet |
| Mini,7 neue Methoden | Eine sichtbare Textebene bei720/1080, sichtbare/fokusfähige leere native Liste,5+ Events, unabhängiges NOW/Fokus, nichtlateinische Zweizeilentitel,20 Öffnen/Schließen,300 historische Slots vor NOW/NEXT, späte alte SID-Publikation abgewiesen, action92 in Overlayzuständen | Pixel-/Font-/Repaintdarstellung in BINGIE noch ungetestet |
| Updatehinweis,13 neue Methoden | Frischbaseline, echtes numerisches Upgrade, OK/Back, zwei Neustarts, Legacybuild40→41, Service nurRunPlugin, aktive Wiedergabe/Modals/Stop gesperrt, Repo-only/sameversion kein Popup, Downgrade/Versionssprung, Crashfenster/Corruption, fehlgeschlagener Dialog, Parallelität, Profilschutz | Echter Box-B-Update-/Dialognachweis ausstehend; Legacy ohne sicheren Vorgängerbeleg bleibt Baseline |
| Widgets,9 neue Methoden | Drei valide begrenzte Directoryquellen/Detailziele, geteilter Fresh/LKG-Cache, Fehler/Concurrency, echte SQLite-Exklusivsperre, kein globaler COUNT/GROUP, defekter Index ohne Reparatur, Adapterproperties,20.005-Titel-Fixture | Externer Skinshortcuts-Build/XML-Fehler nicht durch Backendtest abgenommen |
| Adapter,6 neue Methoden | Ausgeschaltet ohne Wirkung, Zeitrollover/Fokus aus realen RAM-Events ohne HTTP/Tune, Fokuswechsel/fehlend, XML-/Manifest/halbe Logos, read-only Preflight mit XML-/ID-Fehlern, optionale Bindingexception darf Service nicht abbrechen | Nicht installiert; konkrete Skinintegration braucht ausdrückliche Freigabe und reales Rendering |
| Bestehende1.435 Tests | Alle alten Such-/Player-/VOD-/Resume-/Autoplay-/Next-/EPG-/Portal-/Wizard-/Artwork-/Sicherheits-/Storage-Hosttests enthalten | Gerätegates separat; Storage ausschließlich synthetische temporäre Testprofile |
| Sprache,Icons,API | DE/EN je **947** gültige PO-Kontexte; **92** gepinnte lokale MIT-Tabler-PNGs unverändert; strenger Kodi21.3-GUI-API-Vertrag und compileall/AST PASS | Keine Pixel-Abnahme durch API-Modelle |

[Alle44 neuen Methoden](NEUE_TESTS_02941.json). Vor dem finalen Lauf bestanden105 neue/angrenzende Regressionen; nach der zusätzlichen Sicherung eines unklaren nativen Queueposts weitere53 Stop-/Playerregressionen grün. Ein vorheriger vollständiger Stand mit1478 Tests war ebenfalls grün; die endgültigen1479 enthalten den zusätzlichen Queuefehlerfall.

Der erste Gesamtlauf zeigte alte Erwartungen an „vergangene Programme im Mini“ und „Widget-Dispatch muss bei Lock fehlschlagen“; diese wurden ausdrücklich auf den beauftragten .41-Vertrag umgestellt. Ein Ausfall der optionalen Skin-Bindung wird jetzt sicher ignoriert und darf den Service nicht beenden. Testmethoden nicht gelöscht. Historische Freeze-Fixtures bleiben erhalten, exakte .41-Hunks werden davor komponiert.

## Fehlerbeleg gegen .40 und Kodi21.3

Zwei identische neue Mini-Replays wurden auf einem getrennten unveränderten Git-Archiv von main .40 ausgeführt: **Einzeltextebene FAIL** und **Historie-vor-Limit/Zukunft FAIL**; auf .41 beide PASS. Es ist ein deterministischer Code-/Modellnachweis passend zum Android-Nutzerbefund, keine behauptete tatsächliche Pixelmessung.

Für Live-Stop zeigt der [gepinnt gelesene Kodi21.3-Quellvertrag](KODI_NATIVE_STOP_PROOF_02941.json): Player.stop→SendMsg(wait=true), executebuiltin(wait=false)→PostMsg. Die neue Logik entfernt den synchronen Python-Wartepfad und verlangt eine echte Main-Queue-Rückkehrbarriere. Ein erfolgreiches Posting oder frühzeitiges PlayerStopped-Callback wird nicht als Abschluss ausgegeben. Exakte AudioTrack-/MediaCodec-/Renderer-Deadlockquelle bleibt offen. [Ursachenanalyse mit Codezeilen](URSACHENANALYSE_02941_DE.md).

## Gemessene große Hostfixtures dieses Laufs

| Fixture | Messwerte |
|---|---|
| XMLTV |160.005 gelesen /160.003 gespeichert;95.571.948 XML-Bytes,199.876.608 SQLite-Bytes,12,872 s |
| Filme |200.005 Titel,109.380.521 lokale HTTP-Bytes,309.522.432 SQLite-Bytes,26,308 s |
| Serien |200.005 Titel,109.380.521 HTTP-Bytes,621.727.744 kumulative SQLite-Bytes,27,167 s |
| Katalog Peak-RSS |60.380 KiB Host, kein ARM32-Gerätewert |
| Neuer Widgetbackendtest |20.005 Filme, erste24 Titel, READY,19,611 ms; keine Vollkatalogzählung. Kein Kodi-/BINGIE-End-to-End-Wert |
| Bestehende2.905-Sender/456-Alias-Suche |Kalt erste Namen5,320 ms / Datenabschluss46,825 ms; warm5,308 /16,832 ms, sechs Endtreffer. Keine GUI-/Android-Messung |

Es werden reale temporäre SQLite-Dateien und lokale synthetische HTTP-/SMB-Server verwendet. Keine Provider-/SMB-Nutzerverbindung. Unveränderte Vendor-SMBProtocol-Docstring erzeugt unter Python3.12 eine bekannte SyntaxWarning, Kompilierung/Tests erfolgreich.

## Bestandsschutz

[Schutznachweis](SCHUTZPRUEFUNG_02941.json): **375 unveränderte Add-on-Quelldateien**, alle1435 alten Methoden vorhanden. **163/163** historische UI-Vertragsdateien und Suchmasken-XML/Controls700/701/702/710/720/721 bytegleich zu .40. Original-XCMate-Icon und98 Themegrafiken unverändert. VOD-/Resume-/Autoplay-/Decoder-/Portal-/EPG-Store-/Artwork-Modus-/Remote-/Keymapmodule bytegleich; kein Bibliotheks-/Guide-/Jobschema geändert. .40-ZIP, Produktionsindex und Publish-Bedingung gleich.62 fremde lokale WIP-Dateien unverändert.

Neue Profilzustände ausschließlich eigener Updatehinweis-Marker/Lock und begrenzter Widget-Metadatencache/Lock; atomare temporäre Dateien werden regulär abgeschlossen. Keine vorhandenen Portale, Gruppen, Favoriten, Bilder, EPG-Mappings, Fortschritte oder Caches migriert/gelöscht/überschrieben. Keine Geräteprüfung durch eine erfundene Inventur ersetzen: **Box A komplett unberührt, Box B Dynamisch und nicht automatisch installiert**, keine zusätzlichen USB-/SD-/SMB-/Speicher-/Migrations-/Löschtests auf B. Grünes Testlog auf Credential-/URL-Leaks geprüft; private Rohlogs nicht geöffnet/veröffentlicht.

## Optionaler BINGIE-Review

[Versioniertes Include/Manifest/README](../../integrations/titan-bingie-mod/0.1.29.41/README_DE.md), [separates Review-ZIP](../../integrations/titan-bingie-mod/XCMate_BINGIE_Adapter_REVIEW_0.1.29.41.zip), [Review-SHA](../../integrations/titan-bingie-mod/XCMate_BINGIE_Adapter_REVIEW_0.1.29.41.zip.sha256). **Kein Kodi-Add-on, nicht als normales ZIP installieren.** Keine automatische Kopie/Aktivierung/Shortcutänderung. Die echte BINGIE-Einbindung und externe Skinshortcuts-Reparatur sind BLOCKED bis konkrete Kompatibilitätsprüfung und Freigabe. Kein Downgrade auf einen ungeprüften älteren Python3-Fork vorgeschlagen.

## Reproduktion

Frischer separater PR-Checkout, Python3.12, Pillow und impacket0.13.0:

```sh
python tools/build_repository.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python -m compileall -q src
for f in tests/test_addon.py tests/test_site.py tests/test_providers.py; do
  sed -i "s@'..', 'plugin.video.noodleprivate'@'..', 'src', 'plugin.video.noodleprivate'@g" "$f"
done
python -m unittest discover -s tests -v
python tools/verify_xcmate_02941_protection.py --output /tmp/xcmate41-protection.json
```

Schutztool benötigt das Git-Objekt der dokumentierten Mainbasis. Builder erstellt auch andere Add-on-Pakete/Indizes, deshalb nur separaten Checkout verwenden und keine generierten Produktionsdateien veröffentlichen. Lokal wurde impacket per vorhandenem PYTHONPATH eingebunden, CI installiert es regulär. Loopback-Netzwerkfreigabe für echte lokale HTTP/SMB-Tests nötig.

## Offene Geräteabnahme

[40 deutsche Gates plus1→5→20 Checkboxfolge](ANDROID_ABNAHME_02941_DE.md), [Status jeBox](ANDROID_STATUS_02941.json), [21-Issue-Matrix](ISSUE_MATRIX_02941_DE.md), [sämtliche Dateipfade und Commitzuordnung](AENDERUNGEN_02941_DE.md).

**P0 #203 bleibt zwingendes Android-Freigabegate.** Keine behauptete dauerhaft native Hängerfreiheit, kein echter Skin-/Font-/IR-/Stream-/Updatepopup-PASS. #206/#207 behalten externe/approval-blockierte Teile. Keine Issue-Schließung wegen CI. Kein Merge/Release/Downgrade/Reset/automatisches Geräteupdate.
