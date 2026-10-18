# XCMate 0.1.24 – P0-Korrektur, getrennte EPG-Analyse und Android-Testplan

Stand: 18.10.2026. Entwicklungsbranch `fix/kodi21-strict-gui-epg-diagnostics`, Basis `c789a45` von `origin/main`. Kandidat **0.1.24 / service build=24**, nicht produktiv veröffentlicht. Android-Abnahme ausstehend. Ausgangsbefund vollständig gelesen: [Übergabe 0.1.23](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md), [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13); Skin #14 bleibt eine spätere Aufgabe.

**Review:** [Entwurfs-PR #16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16), Code-/Paketcommit `1dc780f`. **GitHub-CI erfolgreich:** [Run 39143315938](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143315938), einschließlich Tests, Paketaufbereitung und Artefakt-Upload; Produktions-Publish-Schritt übersprungen. [CI-Artefakt xcmate-review-16](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143315938/artifacts/12142272132), 14 Tage verfügbar. Der Download von CI-Logs/-Artefakt ist in dieser Cloud-Umgebung serverseitig gesperrt; CI-Erfolg und Artefaktbestand wurden über die GitHub-API geprüft. Die unten dokumentierte ZIP-/Quellprüfung betrifft das unabhängig lokal gebaute und im Branch eingecheckte Paket.

## P0: nachgewiesener Aufruffehler

`LiveNavigator.show()` baut vor `WindowDialog.show()` seine Controls auf. Dabei wurde `ControlList(..., itemHeight=46, space=3)` aufgerufen. Die tatsächliche Omega-Deklaration verwendet **`_itemHeight` und `_space`**. Mit ausdrücklich benannten Parametern statt `*args, **kwargs` reproduzieren die zuvor 18 Dialogtests unmittelbar `TypeError: unexpected keyword argument 'itemHeight'`. Beide alten Keywordnamen werden nun zusätzlich einzeln abgewiesen. Nach Korrektur startet der gesamte modellierte Dialogpfad erfolgreich, ohne `onInit()` aufzurufen.

Das ist ein nachgewiesener Quellcodefehler und passt zum Geräteverlauf `CANDIDATE_CREATED → SHOW_FAILED → CLOSED`. Ein vollständiger nativer Geräte-Traceback lag nicht vor; weitere Fehler auf dem Android-TV sind durch diese Tests nicht ausgeschlossen. Die permissiven bisherigen GUI-Mocks hatten diesen Fehler verdeckt.

API-Referenz ist der tatsächliche Kodi-Tag **21.0-Omega**, Tag-Objekt `60c450005472e6d38929bb28c07d00589102818d`, insbesondere [Control.h](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Control.h), [Control.cpp](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Control.cpp), [Window.h](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Window.h), [Dialog.h](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Dialog.h), [ListItem.h](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/ListItem.h) und [WindowXML.h](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/WindowXML.h). Die wirkungslosen nativen Setter `setItemHeight()` / `setSpace()` sind kein Ersatz für korrekte Konstruktorargumente.

| Geprüfter API-Bereich | Ergebnis und Absicherung |
| --- | --- |
| `ControlList` | Zwei falsche Keywordnamen korrigiert; explizite vollständige Konstruktorsignatur im Laufzeittest. |
| `ControlLabel`, `ControlButton`, `ControlImage` | Positionale Argumentreihenfolge und verwendete Keywords entsprechen Omega; ebenfalls explizite Testkonstruktoren. |
| `addControl(s)`, `setFocus`, `setNavigation`, `controlLeft/Right`, Listenmethoden | Anzahl/Art der verwendeten Argumente geprüft; Navigation wird nach Hinzufügen der Controls eingerichtet. Sichtbarkeit und Fokus laufen durch das Dialogmodell. |
| `Window`, Properties, native Dialoge und `ListItem` | Repositoryweiter AST-Vertragstest bindet über 200 direkte GUI-Aufrufe bzw. erkannte lokale GUI-Aliase gegen feste Signaturen. Kein Netzwerk oder Kodi für diesen Test nötig. |
| `WindowDialog` vs. `WindowXMLDialog` | Programmatische Fenster erhalten kein `onInit`/`onClick`. Beim zusätzlichen Audit derselbe Fehler in `remote_profiles._capture()` gefunden: Aufbau jetzt im Konstruktor vor `doModal()`, Lernen durch `onAction`, einschließlich rohem Buttoncode. Der XML-Popup-Test behält seine passenden XML-Callbacks. |

Es laufen keine echten Kodi-Bindings in der Cloud. Die Vertrags- und Callbacktests prüfen Argumente und Kontrollfluss, nicht den nativen Renderer oder Androids Fokusvergabe.

### 53.664 Sender und Fehlerdiagnose

- Höchstens **100 Sender pro GUI-Seite** werden mit EPG-Text aufbereitet, ergänzt um höchstens zwei fokussierbare Seitenlinks. OK auf einem Seitenlink blättert, ohne zu tunen. Native Page-Up/Down blättern ebenfalls; die letzte Seite und kurze Listen behalten korrekte absolute Auswahlpositionen.
- Der synthetische Test mit 53.664 Senderobjekten prüft letzten Sender, absolutes Tune-Ziel, Vor-/Zurückblättern und Page-Callbacks. Messwert des lokalen Render-/Callbacktests einschließlich Fixture: **0,108 s**. Kein Android-Laufzeitversprechen und kein Benchmark des gesamten Dateikatalogimports. Der komplette Metadatenkatalog bleibt im Arbeitsspeicher; dieses bestehende Verhalten wurde nicht virtualisiert.
- `SHOW_FAILED` speichert eine erlaubnisgefilterte `failure_stage` (`CONTROL_LIST`, `BUILD_CONTROLS`, `WINDOW_SHOW`, `RENDER`, `FOCUS`) und sichere `exception_class`. Nach `CLOSED` und Neustart zeigt der Diagnosebericht den letzten gespeicherten Fehler mit Zeitpunkt. Keine Exception-Texte, Stream-Adressen oder Zugangsdaten werden dafür gespeichert.
- Zulassungsprüfung, Stream-Identität und globale Keymaps wurden nicht gelockert. Keine Änderung an Noodle Private, anderen Add-ons oder BINGIE MOD.

## P1: getrennte Analyse von EPG-Fehlern

| Reales Signal aus 0.1.23 | Belegte Aussage | Verbesserung im Kandidaten |
| --- | --- | --- |
| `PROVIDER_LIMIT` | Eine Schutzgrenze wurde ausgelöst. Aus dem alten Code allein ist nicht erkennbar, ob HTTP-Eingang, entpackte Daten, 150.000 Sendungen oder 10.000 Kanäle betroffen waren. | Erhält `failure_stage`, `exception_class`, `failure_code`, `limit_kind` und `limit_value`. `limit_bytes` erscheint nur bei einer Bytegrenze. HTTP- und XMLTV-Eingangs-/Entpackgrenzen sind getrennt. |
| `NO_NEW_GUIDE` | Abschluss ohne neue speicherbare Programme; keine eigenständige Fehlerursache und kein Nachweis gelungener Datenübernahme. | Der Bericht zeigt die vorausgehende gespeicherte Provider-Ausnahme auch nach dem Abschluss. Guter vorhandener Cache bleibt erhalten. |
| `READ → DOWNLOAD_FAILED`, 3.591.764 Bytes | Lesen hatte bereits geklappt; der alte Catch-all schloss auch Entpack-/Parserfehler ein. **Kein Beleg einer 80-MiB-Überschreitung.** | `DOWNLOAD`, `PARSE`, `MERGE` getrennt; `GZIP_INVALID`, `HTTP_COMPRESSION_FAILED`, `INVALID_XMLTV`, `EMPTY_GUIDE`, Zeitlimits und konkrete Größen-/Mengengrenzen. HTTP-Status wird, falls vorhanden, nur numerisch gespeichert. |

Externe Quellen werden weiterhin seriell im Hintergrund verarbeitet. `source_index` bezeichnet jetzt den festen Platz in der konfigurierten Quellenliste, einschließlich deaktivierter Einträge; die EPG-Verwaltung zeigt `[1]`, `[2]` usw. an. So ist die Quelle lokal zuzuordnen, ohne private URLs in den Diagnoseverlauf zu kopieren. Verändert man die Quellenreihenfolge, gilt eine alte Nummer für die damalige Reihenfolge. Dieser begrenzte Verlauf ersetzt keinen dauerhaften Status pro Quelle/Portal.

Ungültiges XML propagiert jetzt `ElementTree.ParseError` bis zum jeweiligen abgesicherten Importversuch. Dadurch wird es nicht mehr zu einem scheinbar erfolgreichen, leeren Parsergebnis. Beide produktiven Parser-Aufrufer fangen Fehler pro Quelle ab. Einzelne ungültige Programmzeitstempel werden weiterhin isoliert übersprungen. Leeres gültiges XMLTV wird als `EMPTY_GUIDE` klassifiziert. Die 80-MiB-, Kanal- und Sendungslimits wurden nicht angehoben.

**Nicht behaupten:** Die tatsächliche externe Fehlerklasse der Android-Fotos ist noch unbekannt. Kleine DE-/AT-/CH-Feeds wurden in dieser Cloud-Aufgabe nicht live auf Verfügbarkeit oder Senderabdeckung geprüft. Kein belegter frischer Geräteimport und kein nachgewiesenes Jetzt/Danach am Fernseher.

**Issue #13 bleibt offen:** Ein eigener Menüpunkt „EPG-Status & Vorschau“, dauerhaft getrennte Quell-/Portalstatus, gültige Zeitfenster, Matching-Quote und auswählbare echte Titelvorschau sind noch nicht vollständig implementiert. Der aktuelle Kandidat liefert die vorausgehende Fehlerklassifikation; Cache-/Mapping-Prioritäten und bestehende Senderlistenanzeige bleiben bestehen. Skin #14 folgt später.

## Tests und Paketprüfung

- **213/213 Tests bestanden**, sowohl im Checkout als auch nach Build in einer wegwerfbaren Repositorykopie mit Python **3.12.14**. Build-Bootstrap und bestehende Upgrade-Schritte erfolgreich, vollständiger Syntaxcheck bestanden.
- **23 strikte Overlay-/Callbacktests**; dazu der repositoryweite GUI-Vertragstest. Kodi `WindowDialog.show()` ruft im Modell ausdrücklich kein `onInit()` auf. Native Listenbewegung / `onControl` vor `onAction` vermeiden einen vorgetäuschten Erfolg und doppelte OK-Ausführung.
- **19 EPG-/Cache-/HTTP-Tests** zusätzlich mit System-Python und verfügbarem **httpx 0.28.1** bestanden; im Build-Venv ohne httpx auch urllib geprüft. Enthalten: HTTP-/GZIP-Limits, Transportkompression, kaputtes XMLTV-GZIP, ungültiges XML, leere Guides, fester Quellenindex und Cache-/Konfigurationserhalt.
- Persistenztests lesen Fehlerstufe/-klasse nach Close/Neustart wieder ein und prüfen, dass private Exception-Texte nicht erscheinen. Bestehende Tests prüfen Zeitstempelfehler, manuelle Zuordnung, Providerpriorität, unbeschreibbaren Cache und asynchrone GUI-Pfade.
- Installierbare ZIP gegen **alle 56 Quelldateien bytegenau** verglichen, Manifest-Version geprüft, CRC-Test bestanden. Der vollständige Repositorybuild prüfte drei Pakete, Installerkopien und Index-MD5 ausschließlich in der Kopie. Produktionsindex im Branch unverändert.

Testpaket: [`plugin.video.xtreammate-0.1.24.zip`](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.24.zip), **242152 Bytes**. [SHA-256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.24.zip.sha256):

```text
1100ea73a974dfe92d731d4384826a15c20c0be9cac5dc5d205f8ca03f267286
```

Die PR-CI baut erneut und stellt ausschließlich XCMate-ZIP und eigene SHA-256 als `xcmate-review-<PR-Nummer>` bereit, Aufbewahrung 14 Tage. CI-ZIP-Zeitstempel und damit SHA können vom hier eingecheckten lokalen Paket abweichen; immer die zum jeweiligen Artefakt gehörende Prüfsumme benutzen. Kein automatisches Release durch den PR.

Reproduzierbar: `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -v`. Den bestehenden `tools/build_repository.py` **nur in einer wegwerfbaren Kopie** ausführen: Er erzeugt alle Repositorypakete und Artwork. Dieselben Bootstrap-/Upgrade-/Build-/Compile-/Testschritte stehen in `.github/workflows/publish.yml`; die neue Artefaktbereitstellung ist auf `pull_request` beschränkt.

## Nächster Android-Test und regulärer Updateweg

1. **Zunächst PR und Tests prüfen; kein ungeprüfter Merge.** Das geprüfte ZIP ist als Review-Artefakt vorbereitet. Für den bevorzugten regulären GS-Media-Updateweg ist eine gesonderte Freigabe zum Merge erforderlich. Dieser Branch aktualisiert weder `addons.xml` noch das produktive Repository.
2. **Erst nach Freigabe:** PR nach `main` übernehmen; bestehenden Workflow „Publish GS Media Kodi updates“ abwarten. Auf `main` Manifest und `addons.xml` auf 0.1.24, ZIP-Pfad und `addons.xml.md5` kontrollieren. Kein gesonderter GitHub-Release nötig.
3. Auf Android-TV über **Add-ons → Meine Add-ons → Add-on-Repositorys → GS Media → Nach Aktualisierungen suchen**, dann **XCMate → Aktualisieren**. Nicht deinstallieren, keine Profile/Quellen/Zuordnungen löschen. Kodi vollständig beenden/neustarten. **Version 0.1.24 und `service build=24`** bestätigen. Globale Fallback-Keymap ausgeschaltet lassen.
4. **ANDROID OFFEN – Dialog/Fokus:** gespeicherten Live-Sender starten, automatische sichtbare Liste und Fokus prüfen. Diagnose muss `SHOW_REQUESTED`, passenden Fokus/aktiven Dialog und tatsächliche `NATIVE_ACTION`-Zählung zeigen. Kandidat oder XML-Popup allein gilt nicht als Erfolg.
5. **ANDROID OFFEN – Navigation:** Links, Rechts, Hoch, Runter, kurzes OK, Menü, Zurück, OSD-Ton/Bild/EPG/Einstellungen prüfen. Kein doppeltes OK; lange OK-Taste nur entsprechend tatsächlich gemeldeter/angelernter Action bewerten. Bei großen Gruppen Seitenlinks und letzten Sender testen. Tastenanlernen gesondert prüfen.
6. **ANDROID OFFEN – Isolation:** Stop und Wiedergabe in fremdem Add-on; XCMate darf keine Tasten/Fokus behalten. BINGIE MOD und normale Kodi-Bedienung prüfen.
7. **ANDROID OFFEN – EPG:** zuerst eine kleine DE-, danach bei Bedarf AT-/CH-Quelle einzeln aktivieren und Hintergrundaktualisierung anfordern. GUI währenddessen bedienen. Diagnose nach Wiedergabeende lesen: Quelle `[n]`, Stufe, Klasse, Grenzgrund/HTTP-Status, Zeitpunkt und Erfolg. Dann reguläre Senderliste mit Jetzt/Danach und zwei manuelle Zuordnungen nach Neustart prüfen. Große Masterquelle getrennt testen; Limit nicht hochsetzen.
8. **ANDROID OFFEN – Fehlerpersistenz:** Bei erneutem `SHOW_FAILED` oder EPG-Fehler nach Stop Diagnose sichern; anschließend Kodi neu starten und gespeicherten Fehler vergleichen. Keine privaten URLs oder unbereinigten Logs veröffentlichen.

Issue #12 bis zum bestätigten Android-Navigationstest offen lassen; Issue #13 bis zum vollständigen EPG-Status-/Vorschautest ebenfalls offen lassen. Der Bericht dokumentiert Cloud-Prüfungen und einen Testkandidaten, keinen Geräte-Abnahmeerfolg.
