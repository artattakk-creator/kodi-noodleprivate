# Android-Abnahme .54 – ausschließlich Box B

Alle neuen Geräteprüfungen zunächst NOT_TESTED. Box A bleibt vollständig unangetastet. Nur der Nutzer installiert nach bewusster Entscheidung das geprüfte ZIP über die bestehende Version; keine Deinstallation, Downgrade oder Reset. Laufenden alten Import nicht durch automatische Aktionen unterbrechen. SHA256 vorher vergleichen.

Erste Umgebung: Android TV 13 / ARM32 / Kodi 21.3 Omega / Estuary. Der historische Startcrash ist ungeklärt: ST54-01 ist das erste Gate. Bei erneutem Prozessabbruch abbrechen, übrige Fälle BLOCKED und anonymisierte Diagnose vor weiteren Versuchen sichern. Kein Rohlog mit privaten Daten auf GitHub.

| ID | Erwartetes Ergebnis | Status |
|---|---|---|
| ST54-01 | **Startstabilität:** Box B unter Kodi 21.3 Estuary starten. Bei Kodi-Prozessende/Helperfehler FAIL, weitere Tests BLOCKED; anonymisierte Kodi-/Android-Crashdaten sichern. Keine Ursache ohne Log behaupten. | NOT_TESTED |
| UPD54-01 | **Installations-Popup:** Bewusst .53 → .54 aktualisieren. „Installation erfolgreich“, Version .54 und tatsächliche Änderungen sichtbar; bei neuer Installation ebenfalls. Bestätigen, neu starten: kein zweites Popup. | NOT_TESTED |
| UPD54-02 | **Sichere Anzeige:** Bei Wiedergabe/fremdem Dialog wird der Hinweis zurückgestellt. Kein Player-/Fokusverlust. | NOT_TESTED |
| AUTH54-01 | **Erfolg:** Gültige Xtream-Adresse samt optionalem Port/User/Passwort prüfen. „Verbindung erfolgreich. Zugangsdaten bestätigt.“ und automatisch Kategorien laden; noch kein Vollimport. | NOT_TESTED |
| AUTH54-02 | **Fehlerarten:** Ungültige Zugangsdaten, DNS, TLS, HTTP und einzelne Zeitüberschreitung unterscheiden. Keine Secrets in Fehlermeldung; Eingaben bleiben. | NOT_TESTED |
| AUTH54-03 | **Passwort:** Neu eingegebenes Passwort nach Fehler über Anzeigen/Ausblenden bearbeiten. Gespeichertes Passwort niemals als Klartext-Default. Nach Bestätigung nicht in Übersicht. | NOT_TESTED |
| AUTH54-04 | **Back/Retry/Später:** Zurück/Bearbeiten/Erneut prüfen/Später verwenden. Kein Doppeljob; Server/User und Markierungen erhalten. Neuer Kodi-/Python-Interpreter: nur fehlendes Passwort erneut. | NOT_TESTED |
| CAT54-01 | **45 aus 883:** 45 Gruppen aus großem Angebot markieren, zwischen Live/Filmen/Serien wechseln. Auswahl sofort gesichert; nur aktive Gruppen importieren. | NOT_TESTED |
| CAT54-02 | **Gruppenunterbrechung:** Kontrolliert bei Gruppe 39 abbrechen. Vollständig geprüfte Gruppen 1–38 beim Retry überspringen; unfertige Gruppe eindeutig erneut bearbeiten. | NOT_TESTED |
| CAT54-03 | **Auswahländerung:** Eine Gruppe abwählen/eine neue wählen, erneut prüfen. Nur betroffene Einheiten importieren, keine Titel deaktivierter Gruppen veröffentlichen. | NOT_TESTED |
| CAT54-04 | **.53-Entwurf:** Vorhandenen .53-Entwurf über normales Update fortsetzen. Nur nachweislich eigene/gleiche/aktuelle atomare Heads übernehmen; andere gezielt erneut laden. Alte EPG-Arbeitsdateien bleiben erhalten. | NOT_TESTED |
| CAT54-05 | **Speichern vor EPG:** Katalog prüfen und Portal speichern. Vor EPG müssen Live, Filme, Serien und aktivierte Gruppen bereits in der Portalverwaltung vorhanden sein. | NOT_TESTED |
| CAT54-06 | **Save-Fehler:** Bei tatsächlichem Schreib-/SQLite-Fehler keine ungeprüfte Portalveröffentlichung. Katalog-Checkpoints und bestehende Portale erhalten; gezielter Retry. | NOT_TESTED |
| EPG54-01 | **Zwei große Quellen:** Zwei reale konfigurierte XMLTV-Quellen fortsetzen. Gut lesbar Quelle X/Y, Bytes/gelesen/zugeordnet/gespeichert; keine erfundenen Prozentwerte. | NOT_TESTED |
| EPG54-02 | **5/20-Minuten-Lauf:** Einen tatsächlich aktiven Import über fünf, möglichst zwanzig Minuten laufen lassen. Kein globaler Zeitabbruch; reale Aktivität und letzte Messung sichtbar. Einzel-I/O darf begrenzt fehlschlagen. | NOT_TESTED |
| EPG54-03 | **Quelle 2 fortsetzen:** Quelle 1 fertig, Quelle 2 kontrolliert abbrechen. Portal bleibt nutzbar. Nach ggf. normaler verifizierter Sicherung nur Quelle 2 fortsetzen, Quelle 1 lokal verifizieren. | NOT_TESTED |
| EPG54-04 | **Kodi-Neustart:** Bei offener EPG-Phase Kodi regulär beenden/neustarten. Bestehendes Portal und offene Phase erkennen, keine Login-/Katalogneuanlage. EPG-Manager bietet Fortsetzen. | NOT_TESTED |
| EPG54-05 | **Backup/LastGood:** Bestehende Sicherungs-/Import-/Platzsperren respektieren. Fehlerhafter/verkürzter Feed erhält LastGood, sieben Vergangenheitstage/+20 soweit geliefert, manuelle Quellzuordnung. | NOT_TESTED |
| EPG54-06 | **Parallelität:** Während eines Imports keine zweite konkurrierende Portalaufgabe zulassen. Nach Abbruch bleibt die Worker-Lease bis zur tatsächlichen Bereinigung gesperrt. | NOT_TESTED |
| UI54-01 | **TV-Lesbarkeit:** Gruppenzähler, aktive Reiterlinie, Liste, Fortschritt und Buttons ohne Überschneidung. 720p/1080p, große Zähler, Fernbedienung und Fokus prüfen. | NOT_TESTED |
| UI54-02 | **Fanart:** Add-on in Kodis Übersicht markieren: regulärer Lightweight-Splash, Original-Icon unverändert. Bei alter Kodi-Textur normalen Neustart prüfen, keinen globalen Cache löschen. | NOT_TESTED |
| REG54-01 | **Medien:** Live-Back mit bestehenden Einstellungen, Film-/Serien-Back, Resume, staffelübergreifendes Autoplay, Suche und Infobar-Pixelwerte prüfen. | NOT_TESTED |
| REG54-02 | **EPG/Benutzerdaten:** Großes/kleines EPG, Favoriten, Quellen/Mappings, Portale, Gruppen, Cover und Einstellungen erhalten. Box A nicht testen oder verändern. | NOT_TESTED |
| REG54-03 | **Widgets später:** Vorhandene Film-/Serien-/Live-Widgetdaten unverändert. Reale BINGIE-Abnahme erst nach erfolgreicher Estuary-Stabilitätsprüfung separat; keine Skinänderung in .54. | NOT_TESTED |

**24 NOT_TESTED, 0 Android-PASS.** Nicht erfüllte Voraussetzung mit BLOCKED-Grund protokollieren, nie Hostsimulation als Geräte-PASS ausgeben.

Protokoll: Test-ID, Version/ZIP-SHA, Kodi/Skin/Gerät, Zeitpunkt Europe/Berlin, PASS/FAIL/NOT_TESTED, Dauer, reale Zähler, Beobachtung und BLOCKED-Grund. Keine Passwörter/Provideradressen/SMB-Daten.

Passwortgrenze: laufender Wizard-Interpreter hält das neue Passwort im RAM. Explizites Später oder ein Kodi-Neustart kann diesen Interpreter beenden; anschließend ggf. nur Passwort erneut. Es gibt keine neue ungeschützte Credential-Ablage.

Merge/Release bleiben bis ausdrücklicher Freigabe untersagt. Slideshow nicht Bestandteil der Abnahme, BLOCKED_APPROVED_ASSETS.
