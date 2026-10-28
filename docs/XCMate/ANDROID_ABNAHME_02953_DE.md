# Android-Abnahme XCMate 0.1.29.53

Version .53 als kumulativer Testkandidat, kein automatisches Update/Installation durch Codex. Nur der Nutzer installiert das geprüfte ZIP bewusst über Kodi „Aus ZIP-Datei installieren“ über die bestehende Installation. Keine Deinstallation, kein Reset, keine Änderung bestehender Cover-Speicherorte. SHA256 zuerst mit der gelieferten Datei vergleichen. Normale Sicherung vor eigener Abnahme verwenden; vorhandene EPG-Schutzbarrieren respektieren.

Box A: Kodi 21.2, bestehender interner Artwork-/Portalbestand. Box B: Kodi 21.3, bestehender dynamischer Artwork-Modus und .42-Live-Kompatibilitätsmodus. Jeden Test getrennt dokumentieren. Daten/Logausschnitte vor Weitergabe anonymisieren; keine Rohlogs oder Zugangsdaten hochladen.

Ergebnis je Zelle ausschließlich PASS / FAIL / NOT_TESTED; bei nicht erfüllter Voraussetzung NOT_TESTED mit BLOCKED-Grund. Ein Host-PASS ersetzt keine Geräteabnahme. Besonders die realen Feedprogramme wurden in dieser Arbeitsumgebung durch die Netzwerkpolicy blockiert.

| ID | Prüfung / erwartetes Ergebnis | Box A | Box B |
|---|---|---|---|
| EP53-01 | **Quellenmanager:** Alle konfigurierten Anbieter-/XMLTV-Quellen öffnen; Aktivierung, Priorität, letzten Erfolg/Fehler, reale Sender/Sendungen und Zeitraum prüfen. Kein JSON/SQL sichtbar. | NOT_TESTED | NOT_TESTED |
| EP53-02 | **Manuelle Aktualisierung:** Jetzt aktualisieren anfordern; Anforderung darf noch keinen Erfolg behaupten. Abschließenden Bericht öffnen. Bestehende Backup-/Import-Sperre bei Bedarf als BLOCKED dokumentieren, niemals zurücksetzen. | NOT_TESTED | NOT_TESTED |
| EP53-03 | **Sieben/20 Tage:** Bereits empfangene Sendungen von Tag −7 sowie tatsächlich gelieferte Zukunft bis +20 ansehen. Nicht gelieferte Tage als Quellenlücke dokumentieren, keine künstlichen Programme erwarten. | NOT_TESTED | NOT_TESTED |
| EP53-04 | **LastGood:** Eine verkürzte/fehlgeschlagene konfigurierte Quelle kontrolliert prüfen; vorhandene jüngere/ältere Programme und reiche Informationen bleiben. Keine Datenbank löschen. | NOT_TESTED | NOT_TESTED |
| EP53-05 | **WELT-Vergleich:** WELT TV markieren → OK kurz → EPG zuweisen. EPGShare01/Kaimandura/Provider nacheinander vergleichen; exakte Quell-ID/CID und reale Uhrzeiten/Texte festhalten. Originalraster ändert sich bei offenem bedienbarem Dialog. | NOT_TESTED | NOT_TESTED |
| EP53-06 | **Comedy-Varianten:** Comedy Central Deutschland ebenso vergleichen; SD/HD, DE/AT/CH und +1 nicht automatisch vermischen. Fehlende Quelle/Sendung offen dokumentieren. | NOT_TESTED | NOT_TESTED |
| EP53-07 | **Abbruch:** Nach mehreren Vorschauen Zurück/Abbrechen. Ursprüngliche Blöcke, Quelle/CID, Senderfokus, Gruppe und Zeitposition müssen exakt zurückkehren; keine Wiedergabe starten. | NOT_TESTED | NOT_TESTED |
| EP53-08 | **Speichern/Neustart:** Genau einen echten Kandidaten ausdrücklich speichern. Anderen Sender unverändert prüfen. Raster, Mini, Infobar und vorhandenes Home zeigen dieselbe Sendung; nach Kodi-Neustart und offline erhalten. | NOT_TESTED | NOT_TESTED |
| EP53-09 | **Großer Katalog:** Quelle mit über 1.000 Kanälen: Namen/IDs suchen, vorige/weitere Seite, Fernbedienung und Beschreibungs-/Zeitraumscroll prüfen. | NOT_TESTED | NOT_TESTED |
| EP53-10 | **Kalter Kandidat:** Bisher nicht importierten Kanal ausdrücklich wählen: sichtbare Ladeanzeige, RAM-Vorschau, jederzeit Abbruch. Netzwerk-/Ressourcenlimit darf keinen Erfolg vortäuschen oder Mapping ändern. Erst Save persistiert. | NOT_TESTED | NOT_TESTED |
| EP53-11 | **Bericht:** Aktualisierungsbericht: Beginn/Dauer/Quellenergebnis, geladen vs gespeichert, echte Zeitspanne, vorher/nachher sowie Neu/Aktualisiert/Konflikte plausibel; lesbar und scrollbar. | NOT_TESTED | NOT_TESTED |
| EP53-12 | **Intervall/Retry:** 24 h bei unverändertem neuen Standard; zuvor bewusst andere Einstellung bleibt. Mindestens 24-h-Beobachtung getrennt protokollieren; fehlgeschlagene Quelle begrenzt, erfolgreiche nicht alle 60 s neu laden. | NOT_TESTED | NOT_TESTED |
| WIZ53-01 | **Vorbefüllung:** Wizard bei bestehendem Profil bewusst öffnen, vorhandene Portale nicht ersetzen. Neueinstellungen mit Server/Benutzer/Passwort werden übernommen; kein vorhandenes Passwort sichtbar. | NOT_TESTED | NOT_TESTED |
| WIZ53-02 | **Neues Passwort:** Nur neu manuell eingegebenes Passwort standardmäßig während Eingabe sichtbar; optionale Verdeckung prüfen. Nach Bestätigung nicht in Übersicht/Fehlertext anzeigen. | NOT_TESTED | NOT_TESTED |
| WIZ53-03 | **Gespeichertes Passwort:** Regulär gespeichertes Passwort nie unmaskiert vorbefüllen; nach Kodi-Neustart vorhandenes Portal weiterhin funktionsfähig. | NOT_TESTED | NOT_TESTED |
| WIZ53-04 | **Große Gruppen:** Große Live-/Film-/Seriengruppenlisten laden, einzelne an/abwählen; flüssiger Fokus und sichtbarer Fortschritt. | NOT_TESTED | NOT_TESTED |
| WIZ53-05 | **Back:** Zwischen Tabs, Gruppen und Zusammenfassung zurück und erneut vor; bisherige Gruppen und RAM-Passwort bleiben. | NOT_TESTED | NOT_TESTED |
| WIZ53-06 | **Fehler/Retry:** Kontrollierten Verbindungs-/Scanfehler auslösen, gültige Angaben wiederherstellen und Retry. Keine zweite Arbeitsschleife, bestätigte Eingaben/Auswahl bleiben. | NOT_TESTED | NOT_TESTED |
| WIZ53-07 | **Später:** Einrichtung später fortsetzen, Wizard erneut öffnen. Nicht abgeschlossene Portale nicht als fertig melden; Auswahl und geeigneter Arbeitsstand erhalten. | NOT_TESTED | NOT_TESTED |
| WIZ53-08 | **Kodi-Neustart:** Mit unvollständiger Einrichtung Kodi regulär beenden/neustarten. Nichtgeheime Eingaben/Gruppen fortsetzen; ausschließlich fehlendes ungespeichertes Passwort erneut, bei geheimer M3U-URL diese erneut eingeben. | NOT_TESTED | NOT_TESTED |
| WIZ53-09 | **Anbieterwechsel:** Im Entwurf bewusst anderen Anbieter wählen; alten Scan nicht unter fremden Zugangsdaten übernehmen. Vorhandene Portale bleiben erhalten. | NOT_TESTED | NOT_TESTED |
| WIZ53-10 | **Speicherfehler:** Bei real auftretendem Speicher-/Berechtigungsfehler offen protokollieren; kein falscher Save-/Restart-Erfolg. Retry/Back/Später erreichbar, keine Sicherheitsreserve umgehen. | NOT_TESTED | NOT_TESTED |
| WIZ53-11 | **Verwerfen:** Verwerfen zunächst verneinen → Entwurf bleibt. Nur für ausdrücklich entbehrlichen neuen Entwurf bestätigen; alte Portale/EPG/Cover unberührt. | NOT_TESTED | NOT_TESTED |
| WIZ53-12 | **Abbruch/Worker:** Während Laden abbrechen und erneut öffnen. Kein zweiter blockierender Job; gegebenenfalls verständlich auf Cleanup warten, später erfolgreich fortsetzen. | NOT_TESTED | NOT_TESTED |
| WID53-01 | **Drei Quellen:** Aussehen/Darstellung/Widgets: Live-TV, Filme, Serien direkt erreichbar. Vorhandene BINGIE-Verknüpfungen bleiben nach Restart. | NOT_TESTED | NOT_TESTED |
| WID53-02 | **Startgruppe:** Vorhandenes Live-Widget zeigt vollständige Startgruppe mit mindestens 88 kleinen Logos in stabiler Reihenfolge; kein Sender aus anderer Gruppe. | NOT_TESTED | NOT_TESTED |
| WID53-03 | **Hero-Fokus:** Nur mit bereits freigegebener/installierter BINGIE-Hero-Integration: Fokuswechsel aktualisiert Bild, Titel, Text, Jetzt/Nächste/Fortschritt ohne Start. Andernfalls BLOCKED_SKIN_APPROVAL; keine automatische Skinänderung. | NOT_TESTED | NOT_TESTED |
| WID53-04 | **Live-OK/Back:** OK startet gewählten Sender einmal; Overlay-Back und Live-Back mit bestehendem .42-Modus unverändert. Bei Stop-Hänger weitere Zyklen anhalten. | NOT_TESTED | NOT_TESTED |
| WID53-05 | **Filme:** Vorhandene Filmcoverreihe samt Navigation, persistenten/dynamischen Bildern und automatischer Aktualisierung prüfen. | NOT_TESTED | NOT_TESTED |
| WID53-06 | **Serien:** Nachträglich bewusst aktivierte Seriengruppe importieren: neue Serien im lokalen Katalog und bestehenden Widget nach Aktualisierung, keine Neubindung nötig. | NOT_TESTED | NOT_TESTED |
| REG53-01 | **Live/Start:** Startsender, große EPG-Navigation, funktionierender .42-Kompatibilitätsmodus und gespeicherte Optionen unverändert. Auf Box A keine fremden Einstellungen übernehmen. | NOT_TESTED | NOT_TESTED |
| REG53-02 | **Medien:** Film/Serie starten und beenden, Resume und staffelübergreifendes Autoplay einschließlich bewusstem Stop prüfen. | NOT_TESTED | NOT_TESTED |
| REG53-03 | **Info-Bar:** Originale .52-Infobar/Pixelskalierung: reale VideoWidth × VideoHeight in 720/1080/UHD soweit vorhandene Streams; Audio/UT und Fokus unverändert. | NOT_TESTED | NOT_TESTED |
| REG53-04 | **Suche:** Freigegebene Suchmaske, Film-/Serien-/Live-/Programmtitelsuche, Cover und Back-Rückkehr prüfen. | NOT_TESTED | NOT_TESTED |
| UPD53-01 | **Änderungen im Popup:** Nach bewusstem Update auf .53: Popup nennt EPG-Änderungen, Wizard-Eingaben und korrektes Passwortverhalten; lesbar. Bestätigen, Kodi neu starten: keine zweite Anzeige für dieselbe Version. | NOT_TESTED | NOT_TESTED |
| UPD53-02 | **Popup verschieben:** Updatehinweis bei laufender Wiedergabe/fremdem Dialog bleibt zurückgestellt, erscheint erst danach und stört weder Player noch Fokus. | NOT_TESTED | NOT_TESTED |

**36 Tests je Box, 72 NOT_TESTED, 0 Android-PASS.**

Abnahmeblock zum Kopieren:

```text
Box / Kodi / Version / Zeitpunkt:
ZIP-SHA256:
Test-ID: PASS / FAIL / NOT_TESTED
Beobachtung / Dauer / tatsächliche Quell-ID und Kanal-ID (keine URLs):
Offenes Gate / BLOCKED-Grund:
```

Freigabegates: Box-A-Datenschutz, stabiler Live-Back, echte Vorschau/Cancel/Save, sichere Wizard-Wiederaufnahme und erhaltene Widgets. Neue reale Skinintegration bleibt bis zur gesonderten ausdrücklichen Freigabe BLOCKED_SKIN_APPROVAL. Download-/Aufnahmereparaturen und Speicherumzüge sind nicht Bestandteil. Kein Merge, Release oder Issue-Abschluss durch diese Checkliste.
