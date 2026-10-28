# XCMate .51 – Android-Abnahme Box B

Alle Gates zunächst **NOT_TESTED**. Hosttests ersetzen keine Android-Abnahme. Box A bleibt unberührt. Keine Neuinstallation, Profil-/Cachelöschung oder ungefragte Skinänderung. Eine frische Installation nur auf einer ausdrücklich bereitgestellten Testumgebung prüfen; dafür keine bestehende Box zurücksetzen.

Vorbereitung: Testpaket-SHA gegen die mitgelieferte `.sha256` prüfen. ZIP als kumulatives Add-on-Update installieren. Version .51, Kodi-/Android-Version und Box B dokumentieren. Keine Portalwerte oder Rohlogs in GitHub eintragen. Bestehende Widgetreihen, Gruppen, EPG-Mapping, Favorit, Cover und Resume-Stelle vorab kontrollieren. Der Hotfix aktiviert keinen Skinpatch.

| ID | Ausführbare Prüfung / erwartetes Ergebnis | Ergebnis |
|---|---|---|
| W51-01 | Auf frischer genehmigter Testumgebung ohne Portal/Settings Wizard öffnen. Manuell Xtream wählen. Leere Pflichtfelder abbrechen: keine neue Portalanmeldung und keine Endlosschleife. | NOT_TESTED |
| W51-02 | Unter XCMate → Konfigurieren Typ Xtream, Server/User/Pass eintragen. Wizard öffnen, „Vorhandene Zugangsdaten verwenden“ bestätigen. Kein erneutes Eingeben dieser drei vollständigen Werte; keine Klartextanzeige der Werte im Bestätigungsdialog. Name bestätigen, Anbieter lädt. | NOT_TESTED |
| W51-03 | Nur Server und Benutzer vorbelegen. Übernahme bestätigen. Nur fehlendes Passwort wird verdeckt abgefragt; danach erfolgreiche Discovery. Fehlende Server-/Userwerte entsprechend separat ergänzen. | NOT_TESTED |
| W51-04 | Übernahme ablehnen: manuelle Typ-/Dateneingabe möglich. Wizard abbrechen und wieder öffnen. Die Configure-Werte und bestehende Portale bleiben erhalten. | NOT_TESTED |
| W51-05 | 0/1/1.000+ Gruppen je nach verfügbarem Testanbieter prüfen. Leerer Medientab zeigt klaren Hinweis und bedienbare Weiter-/Abbruchbuttons. Bei großen Listen kommen Zeilen schrittweise, Fortschritt zählt hoch; die ersten Zeilen früh bedienbar. Keine unerwarteten Katalogdownloads während der Gruppenwahl. | NOT_TESTED |
| W51-06 | Lange Live-Liste mit IR auf/ab scrollen, erste/mittlere/letzte Gruppe per OK an-/abwählen. Haken und Zähler stimmen; Cursor bleibt an gleicher Stelle. Keine Poster-/Fanartflächen unter Gruppennamen. | NOT_TESTED |
| W51-07 | Wiederholt Live → Filme → Serien → Live wechseln. Eigene Auswahl und Scrollposition je Tab bleiben erhalten. Tabfokus und aktuelle Auswahl klar sichtbar; keine Fokus-Endlosschleife. | NOT_TESTED |
| W51-08 | Alle/Keine in großer Liste betätigen, während der Markierung Tab wechseln, zurückkehren und einzelne Gruppe umschalten. Oberfläche bedienbar, Zähler/Markierungen anschließend korrekt, andere Tab-Auswahl erhalten. | NOT_TESTED |
| W51-09 | Wenige explizite Gruppen auswählen, Inhalte prüfen/importieren. Echte Fortschrittsmeldungen sichtbar. Zurück aus Zusammenfassung, Auswahl ändern, erneut prüfen: nur aktuelle Auswahl wird gespeichert. | NOT_TESTED |
| W51-10 | Speichern, Kopier-/Prüfstatus beobachten. Portal erst nach erfolgreicher Verifikation nutzbar, ausgewählte Live-/Film-/Serieninhalte indexiert. Bestehendes Portal unverändert. Kodi neu starten: neues Portal und Auswahl weiterhin vorhanden, keine erneute Zwangseinrichtung. | NOT_TESTED |
| W51-11 | Während Discovery abbrechen/Back, sofort erneut öffnen. Entweder normaler Neustart nach abgeschlossenem Abbruch oder klare Meldung, dass vorheriger Auftrag noch endet. Kein zweiter Providerjob und kein verspätetes Wiederöffnen/GUI-Update. Nach Ende erneut starten können. | NOT_TESTED |
| W51-12 | Abbruch während Scan vor Speichern sowie während eines frühen Save-Kopierblocks. Keine Änderung an bestehenden Portalen/EPG/Favoriten/Widgets. Unveröffentlichtes neues Staging aufgeräumt; eventuell bereits vollständig publizierte neue Einrichtung als solche dokumentieren. | NOT_TESTED |
| W51-13 | Absichtlich ungültiger Testzugang: sichere AUTH-Meldung, Erneut versuchen/Abbrechen bedienbar. Keine Zugangsdaten in Markerlogs. Keine echte private Anbieteradresse in Testbericht schreiben. | NOT_TESTED |
| W51-14 | Kontrollierter Netzfehler bei Testanbieter: klare NET-/TIMEOUT-Meldung statt endlosem Busy. Nach Rückkehr des vorherigen Jobs erneut öffnen. Bei blockiertem DNS begrenztes UI-Timeout dokumentieren, keine sofortige Beendigung des OS-Aufrufs behaupten. | NOT_TESTED |
| W51-15 | M3U-URL, lokale M3U-Datei und STB jeweils mit zulässigem Testzugang getrennt: typgerechte Vorbelegung, Discovery, Gruppenwahl, Abbruch bzw. explizites Speichern. Nicht verfügbare Anbieterart bleibt NOT_TESTED. | NOT_TESTED |
| W51-16 | Bestand: Live-TV Start/Back mit bestehendem .42-Modus; großer EPG/Mapping; Film-/Seriencover, Wiedergabe/Resume/Autoplay; drei bestehende BINGIE-Reihen und Aktualisierung. Original-Icon und Skin-Einstellungen erhalten. Kein neuer Skinpatch wird aktiviert. | NOT_TESTED |

Je Gate `PASS / FAIL / NOT_TESTED`, Zeitpunkt, Dauer, Gruppenzahl je Typ und harmlose Beobachtung ergänzen. Bei FAIL ersten abweichenden Schritt nennen. Für Diagnosen nur die oben dokumentierten anonymisierten SETUP-Marker und Fehlercodes verwenden; private Kodi-Rohlogs bleiben privat. Beim ersten Hänger weitere belastende Schritte abbrechen und Zeitpunkt festhalten.

Freigabe: Erst nach echter Box-B-Abnahme und ausdrücklicher Nutzerentscheidung mergen. Keine automatische Veröffentlichung oder Installation auf anderen Geräten.
