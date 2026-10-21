> **Aktueller Einstieg (21.10.2026):** [Zentrale Roadmap](ROADMAP_AKTUELL_2026-10-21_DE.md) und [vollständige Issue-Integrationsmatrix](ISSUE_INTEGRATIONSMATRIX_DE.md). Produktiv **0.1.29.6**, Testkandidaten **0.1.29.7 / 0.1.30.1**, primäres Gerät **Kodi 21.2 / ARM32**. Die folgenden früheren Statusangaben bleiben unverändert als Historie; aktuelle Code-, CI- und Gerätebelege stehen in der zentralen Roadmap. Kein neuer Merge/Release freigegeben.

# XCMate 0.1.23 – verbindliche Codex-Übergabe nach Android-TV-Gerätediagnose

**Erfasst:** 18.10.2026. **Status:** P0 Live-TV-Navigator am echten Android-TV **FEHLGESCHLAGEN**; P1 EPG-Aktualisierung/Anzeige **FEHLGESCHLAGEN bzw. NICHT BESTÄTIGT**. Diese Datei ist ein **Auftrag und Befund**, keine implementierte Fehlerbehebung und keine Freigabe für 0.1.24.

**Bearbeitungsnachtrag 18.10.2026:** Die nachstehende Geräteaufnahme bleibt der Ausgangsbefund. Die umgesetzte P0-Korrektur, 213 bestandene Tests, getrennte EPG-Analyse und der vorbereitete Android-/Repository-Testweg stehen in [KODI21_FIX_024_DE.md](KODI21_FIX_024_DE.md). **0.1.24 ist ein Entwicklungs-/PR-Kandidat; nicht produktiv veröffentlicht und noch nicht am Android-TV abgenommen.**

## Sofortstart für Codex

1. **Zuerst diese Datei vollständig lesen**, anschließend [aktuellen Projektstatus](CODEX_STATUS_CURRENT_DE.md), [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12), [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) und [XCMate Skin #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).
2. Basis ist `main` im Repository `artattakk-creator/kodi-noodleprivate`. Kodi-ID `plugin.video.xtreammate` **beibehalten**; ausgelieferte Version derzeit `0.1.23` über GS-Media-Kodi-Repository. [PR #15](https://github.com/artattakk-creator/kodi-noodleprivate/pull/15) wurde gemergt; 202 GitHub-CI-Tests bestanden, dennoch Android-Fehler.
3. **P0 zuerst:** konkreten `TypeError` im `WindowDialog`-Control-Aufbau anhand Signatur und möglichst Geräte-Traceback beheben. Nur auf einem **neuen separaten Fix-Branch**, mit echten/strikten Kodi-API-Signaturen; nicht bloß in permissiven Python-Mocks grün testen.
4. **P1 separat:** EPG-Protokoll und Quellenstatus so korrigieren, dass fehlgeschlagene Importversuche **nicht** als geladen gelten; EPG-Status & echte Jetzt-/Danach-Vorschau gemäß #13. Nicht unkontrolliert mehrere große XMLTV-Dateien parallel laden.
5. PR, nachvollziehbare Versions-/Dateiliste, reproduzierbare Tests, Risiken und exakt dokumentierte Android-Abnahme liefern. **Keine direkte Veröffentlichung auf `main` ohne ausdrückliche Freigabe.** Andere Kodi-Add-ons/BINGIE MOD nicht ändern.

## 1. Gerätetest – bestätigte Fakten aus fünf TV-Diagnosefotos

Die Bilder wurden vom Nutzer in der Chat-Konversation am 18.10.2026 bereitgestellt; **hier sind die diagnostischen Textwerte dokumentiert**. Die fünf Bilddateien selbst sind nicht in dieses GitHub-Repository hochgeladen. Einige abgeschnittene/unscharfe Bildausschnitte erlauben kein zuverlässiges vollständiges Abschreiben jeder Zeile. Für Details ggf. `kodi.log` erbitten; keine erfundenen Werte ergänzen.

| Feld | Gerätediagnose | Schlussfolgerung |
|---|---|---|
| Installierte Version | **0.1.23** | Version auf dem Fernseher bestätigt. |
| Hintergrunddienst | **LÄUFT**; letzter Heartbeat **0,1 s**; **1497** Schleifen; allgemeiner Dienstfehler **keine gemeldet** | Kodi-Dienst ist aktiv; Fehler betrifft den Dialog-/Navigatorstart, nicht einen grundsätzlich toten Dienst. |
| Live-Beobachtung | `Video JA / XCMate-Sitzung JA` | Wiedergabe und LiveSession sind erkannt. |
| Sitzungswiederherstellung | `XCMate-Live-Stream erkannt` | Recovery-Matching positiv. |
| Ownership-Diagnose | enthält `URL_IDENTITY` | Laufender Stream wurde einer XCMate-Live-Sitzung zugeordnet. |
| Letzte TV-Einblendung | **`TV-Dialog-Fehler: TypeError`** | Python-Konstruktion/Aktivierung des TV-Dialogs schlägt fehl. |
| Auto-TV-Popup | **`Fehler: TypeError`** | Separater sichtbarer Fehlerstatus. |
| Persistierte Dialoghistorie | mehrmals `CANDIDATE_CREATED → SHOW_FAILED → CLOSED`; zuletzt wieder `CANDIDATE_CREATED` | Kandidatenobjekt erfolgreich erstellt, aber Anzeige nicht abgeschlossen; spätere Kandidatenstatusmeldung ist **kein Erfolg**. |
| Katalog | `catalog=True, channels=53664` | **53.664 Live-Sender** im Cache – Skalierungsrisiko, aber nicht alleiniger Fehlernachweis. |
| Kodi-Keymap | `INAKTIV` / globale Keymap ausgeschaltet | Beibehalten; nicht als Workaround global Fernbedienung anderer Add-ons überschreiben. |
| Native Fernbedienungsereignisse | `0` | Ohne offenes XCMate-Overlay erwartbar; kein Nachweis eines Remote-Mappings. |
| Separater XML-Popup-Test | `WindowXMLDialog – Default/720p`, **9 Ereignisse**, Zurück `Action-ID 92`, per Zurück geschlossen, Fokus `Testfeld` | XML-Testfenster empfängt Eingaben; **kein Beleg** für echten TV-`WindowDialog`. |

**Reproduktion am Gerät:** In XCMate `0.1.23` den gespeicherten Startsender manuell starten, OK drücken → Kodi-Videoplayer reagiert, XCMate meldet **„TV-Navigation konnte nicht geöffnet werden“**. Nach Stop im Menü `TV-Fernbedienung: Diagnose` erscheinen die oben genannten Statuswerte. Der Stream war abspielbar; Senderwechsel über Hoch/Runter, Senderliste über Links und eigener OSD-Zugriff funktionieren wegen des nicht gestarteten Overlays noch nicht.

**Wichtig:** `Letzter Dienstfehler: keine gemeldet` ist nicht im Widerspruch zu `TV-Dialog-Fehler: TypeError`: Der Exception-Handler verarbeitet und meldet den UI-Fehler gesondert.

## 2. P0 – präzise technische Hypothese: Kodi-ControlList-Konstruktor

**Quelle in `main`:** `src/plugin.video.xtreammate/resources/lib/live_overlay.py`, Methode `LiveNavigator._build_controls()`, ungefähr Zeilen 284–340; besonders:

```python
self.control = xbmcgui.ControlList(
    32, 135, sidebar-58, height-205,
    font='font13', textColor='0xFFFFFFFF',
    selectedColor='0xFFFFFFFF',
    buttonTexture=normal, buttonFocusTexture=focused,
    itemHeight=46, space=3,
)
```

Die zugrunde liegende native Kodi-Binding-Signatur von `ControlList` verwendet **`_itemHeight`** und **`_space`** als Namen der optionalen Python-Konstruktorargumente, obwohl erläuternde Kodi-Beispieltexte auch `itemHeight`/`space` ohne Unterstrich zeigen können. Die tatsächlich gültige Signatur ist ausschlaggebend, nicht ein veraltetes Beispiel.

**Prüfreferenzen:**
- [Kodi – native ControlList-Klassensignatur](https://xbmc.github.io/docs.kodi.tv/master/kodi-base/d8/de1/class_x_b_m_c_addon_1_1xbmcgui_1_1_control_list.html)
- [Kodistubs – Python-`ControlList.__init__`-Signatur](https://romanvm.github.io/Kodistubs/_modules/xbmcgui.html)

**Starke Hypothese:** Das ungültige Keyword `itemHeight` (oder `space`) wirft auf Kodi 21/Omega `TypeError` bereits in `_build_controls()` aus. Ablauf: `start_if_eligible()` erzeugt `LiveNavigator` → `service.py` ruft `candidate.show()` → `LiveNavigator.show()` führt `_build_controls()` **vor** `trace('dialog','SHOW_REQUESTED')` aus → `ControlList` wirft → `SHOW_FAILED`, `close()`, `TypeError` im Dienst → Nutzerbenachrichtigung. **Das passt genau zu den Gerätewerten**, ist ohne vollständigen Traceback jedoch nicht abschließend bewiesen. Andere Kodi-`xbmcgui`-Kontrollen im selben Aufbau **auch** auf Signaturfehler prüfen; nicht vor dem Test nur eine Ursache als sicher ausgeben.

**Erwartete Minimaländerung zur Überprüfung:**
```python
# Nach Abgleich mit Kodi 21/Omega:
_itemHeight=46, _space=3
```
Alternativ Kodi-kompatiblen Konstruktor plus `setItemHeight(46)` / `setSpace(3)` verwenden, wenn durch echte API abgesichert. Keine pauschalen zusätzlichen `except Exception: pass`, die den Fehler nur verstecken.

**Pflichtprüfungen:**
- Strikter Stub oder echte Kodi-Bindings werfen `TypeError` für `itemHeight`/`space`; korrigierte Argumente bestehen.
- Durchlaufe echte `LiveNavigator.show()`-Konstruktion und alle angelegten Controls (`ControlList`, `ControlButton`, `ControlLabel`, `ControlImage`, `addControl` und Navigation). Permissive `**kwargs`-Mocks sind für diesen Regressionstest **nicht ausreichend**.
- Diagnose unterscheidet `CANDIDATE_CREATED`, `SHOW_REQUESTED`, `SHOW_FAILED`, sichtbaren fokussierten Dialog und Keyevents. Der letzte Status darf einen vorherigen fatalen Fehler nicht als Erfolg verdecken.
- Keine Netzwerkanfragen im `onAction`-/`onControl`-Pfad; kein Blockieren der Videowiedergabe.
- Nach Reparatur am echten Android-TV prüfen: Senderliste sichtbar, Fokus erkennbar, Links öffnet Gruppen/Senderliste wie definiert, Hoch/Runter wählt/zappt entsprechend Ansicht, OK zeigt XCMate-OSD, Zurück/Stop verlässlich. Standard-Kodi-Player bzw. BINGIE MOD und andere Add-ons bleiben unbeeinträchtigt.

**Log zur letzten Absicherung:** Kodi-`kodi.log` (ggf. `kodi.old.log`) nach `XCMate WindowDialog startup failed:` suchen und den vollständigen `TypeError`-Text bzw. Python-Traceback ohne geheime Stream-/Portal-URLs beilegen. Dies ist eine wichtige Bestätigung, aber die signaturbasierte Regression kann Codex bereits unabhängig vom Log untersuchen.

## 3. P1 – eigenständige EPG-Fehlerkette

**Diagnose am 18.10.2026 (etwa 17:19:22, lokale Anzeigezeit):**

| Bereich | Daten |
|---|---|
| Gesamt-EPG | `epg: NO_NEW_GUIDE`, `running=False`; Verlauf `RUNNING → PROVIDER_LIMIT → NO_NEW_GUIDE` |
| Externe XMLTV-Feeds | `epg_source: DOWNLOAD_FAILED`, `source_index=2`, `failed=2`, `bytes=3591764`, `limit_bytes=83886080` |
| Verlauf externe Quellen | `READ → DOWNLOAD_FAILED → READ → DOWNLOAD_FAILED` |
| Nutzerwirkung | In normaler Senderliste keine bestätigten `Jetzt/Danach`-Daten; „Aktualisierung im Hintergrund gestartet“ war nur Anforderung. |

**Interpretation mit Grenzen:**
- Der **anbieterinterne** XMLTV-Guide löst `PROVIDER_LIMIT` aus. Der genaue Grenztyp (HTTP-Bytebudget, entpackte XMLTV-Bytes, Zahl der Programme/Kanäle, zeitliches Budget) muss differenziert werden.
- Mindestens zwei externe Quellen-/Leseversuche haben im Lauf nicht erfolgreich geendet. `source_index=2` bezeichnet die zweite **verarbeitete** Quelle in der aktuellen Reihenfolge, nicht zwingend einen konkret benannten Anbieter.
- **3.591.764 Byte ≠ 83.886.080 Byte**: Externe `DOWNLOAD_FAILED` darf nicht als sichere Dateigrößenüberschreitung gedeutet werden. `bytes` ist die zugeordnete Rohdatenmenge; Parsefehler, GZIP-/Formatproblem oder andere Exceptions prüfen. Ein angefangener `READ` ist **kein erfolgreicher Import**.
- Die öffentliche Deutschland-Kaimandura-DE-MASTER-Quelle kann entpackt über 80 MiB liegen. Das kann *eine* Fehlerquelle sein, wurde aber auf diesem Screenshot **nicht sicher mit `source_index=2` identifiziert**.
- Den eventuell vorhandenen Altcache **nicht löschen**. Kein blindes Hochsetzen von Ressourcenlimits. EPG-Quellen getrennt/seriell testen, kleineren Deutschland-EPGShare01-Feed sowie AT/CH, und genau erfassen, ob Daten importiert und zu Xtream-IDs gematcht werden.
- Nutzer benötigt vor `XCMate Skin` eine vom eigentlichen Player unabhängige **EPG-Status & Vorschau**: Name jeder konfigurierten Quelle (ohne Credentials), Zeit letzter erfolgreicher Import, Resultat/Fehlertyp, Zahl der Sender und Sendungen, Match-Quote gegen echte aktivierte Xtream-Sender sowie einen tatsächlich sichtbaren `Jetzt/Danach`-Eintrag. Dies ist [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13).

**Quellcodepfade:** `resources/lib/epg.py` (Provider-`PROVIDER_LIMIT`/`NO_NEW_GUIDE`), `resources/lib/epg_sources.py` (`READ`, `DOWNLOAD_FAILED`, Quelle, Limits und Fehlerklassifizierung), `resources/lib/epg_io.py` (Streaming/Decompression-Grenzen), `resources/lib/epg_views.py` und `main.py::_live_channels` (Now/Next-Matching und Ansicht).

## 4. Skalierung, Sicherheit und Systemverhalten

- Der laufende Portal-Katalog enthält **53.664 Live-Sender**. Bei einem neu geöffneten Fenster nicht sämtliche Zeilen in `ControlList` rendern, sondern aktuelle Gruppe/Viewport paginieren/virtualisieren; mit wirklich großem synthetischem Katalog benchmarken. **Dies ist ein zweiter Prüfpunkt, nicht der nachgewiesene `TypeError` selbst**.
- Keine globalen Keymaps ohne klare Nutzerentscheidung. Frühere globale Kodi-Hänger dürfen nicht wiederkehren; fremde Filme/Serien müssen sich normal navigieren, stoppen und fortsetzen lassen.
- Vertrauliche Xtream-Zugangsdaten, Anbieter-URLs mit Passwörtern, Tokens, Session-Nonces nicht ins Repository, in Issues oder in Tests aufnehmen.
- Änderungen an `plugin.video.noodleprivate`, anderen Add-ons und dem produktiven Repositoryindex unterlassen, solange nur P0/P1 untersucht wird.
- Bei Kodi-Service-/Dialog-Fehlern gespeicherte Diagnose in `addon_data` erhalten, keine Lösch-/Neuinstallationsanweisungen.

## 5. Empfohlener Ablauf für Codex / Release 0.1.24 (noch NICHT erstellt)

**Phase A – P0 minimal und messbar:** Eigenen Fix-Branch von `main` erstellen, strikte Kodi-21-Control-Konstruktion reproduzieren, `TypeError` beheben, Regressionstest ergänzen, lokal alle Tests und GitHub-CI ausführen, PR öffnen. Dazu knappen Android-Prüfplan liefern. Keine direkt produktive ZIP veröffentlichen.

**Phase B – P1 getrennt:** Fehlerhafte EPG-Feeds und `PROVIDER_LIMIT` mit anonymisierten Fehlerklassen und kontrollierten Ressourcengrenzen diagnostizieren, echte Import-/Matching-Ergebnisse im UI anzeigen, mindestens einen Now/Next-Eintrag vom Cache bis zur Liste testen. Tests unter realistischen Cache- und XMLTV-Budgets.

**Phase C – Android-Abnahme:** Nach ausdrücklicher Merge-Freigabe reguläres GS Media Kodi Update (kein manuelles ZIP) installieren, genaue Version verifizieren, Kodi neu starten, Live-Sender und XCMate-Fenster testen. Diagnose bei jeder reproduzierten Fehlermeldung erneut erfassen. **Der Stand 0.1.23 ist ausdrücklich kein Android-PASS.**

**Phase D – künftiger XCMate Skin:** Eigenständige, separat aktivierbare Skin-Machbarkeitsprüfung nach [Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14). Hierfür die bestehenden TiviMate-/UI-/Design-Referenzen im Repo nutzen, aber den P0-Fix nicht durch einen ungeprüften kompletten BINGIE-MOD-Neubau ersetzen. EPG erst sichtbar machen.

## 6. Nachvollziehbarkeit und Übergabe-Regeln

- Primärlinks: [Issue #12 (P0)](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) · [Issue #13 (P1)](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) · [Issue #14 (XCMate Skin)](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14).
- Für die Version `0.1.23`: [PR #15](https://github.com/artattakk-creator/kodi-noodleprivate/pull/15) und [GitHub-CI mit 202 Tests](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39136334056) – Mock-/Unit-Tests ersetzen keinen Android-TV-Gerätetest.
- Nach Codex-Änderungen stets `CODEX_STATUS_CURRENT_DE.md`, `README.md` und ggf. diese Übergabe mit **getrennten Feldern Implementiert / Tests / GitHub veröffentlicht / Android bestanden / offene Fehler** fortschreiben. Alte Fehlerprotokolle nicht löschen.
- Änderungen/Behauptungen jeweils mit PR, Commit, konkreten Codezeilen, Testergebnissen und gegebenenfalls Geräte-Statuscodes belegen. Keine pauschale Behauptung „Fernbedienung funktioniert“, bevor Fokus und tatsächliche D-Pad-Aktionen am Gerät beobachtet wurden.

## 7. Ein-Satz-Auftrag zum Wiederaufnehmen

> Lies `docs/XCMate/CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md`, bearbeite den auf Android bestätigten `TypeError` beim `LiveNavigator.show()` in Issue #12 (prüfe insbesondere falsche `xbmcgui.ControlList`-Keywords `itemHeight`/`space`), sichere echte Kodi-Omega-Regressionstests und dokumentiere die unabhängigen EPG-Fehler aus Issue #13. Arbeite auf einem neuen Branch mit PR; `main` nur nach Freigabe und Geräteprüfung aktualisieren.
