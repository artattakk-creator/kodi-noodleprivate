# XCMate .62 – Abnahmematrix

| Anforderung | Host-/Codebeleg | Box B |
|---|---|---|
| #289 gezielter Live-Reader, 803 Gruppen/88 Sender | neue SQL-/WAL-/Fehler- und native Pixeltests PASS | ANDROID_NOT_TESTED |
| #289 unabhängig von EPG/Artwork | injizierte Dekorationsfehler, alle Identitäten/Klickziele erhalten PASS | ANDROID_NOT_TESTED |
| #289 LastGood nur gleiche aktive Gruppe/Policy | Fremdgruppe/Policywechsel/gesperrte Gruppe abgewiesen PASS | ANDROID_NOT_TESTED |
| #289 Skinshortcuts getiterator | zwei Originalfehler reproduziert, exakter bestätigbarer Fix + Restore PASS | ANDROID_NOT_TESTED |
| #288 sichtbares Zurück, separates Deaktivieren | keine Abfrage/Schreiboperation für Zurück; Abschalten bestätigt PASS | ANDROID_NOT_TESTED |
| TMDB lokaler Dateiimport/Persistenz/Sicherheit | vorhandene + neue Datei-/URI-/Neustarttests PASS | ANDROID_NOT_TESTED |
| echte TMDB_OK mit privatem Token und Sendungsbild | vom Nutzer auf Box B auszuführen; keine simulierte Auth als Gerätetest | ANDROID_NOT_TESTED |
| Filme/Serien | Nutzer-PASS aus .61 erhalten; produktive Daten-/Renderpfade roh unverändert, Gesamttests PASS | Regression B-62-09 offen |

Keine Schließung von #289/#288 vor Nutzerbefund. Android B-62-01 bis B-62-10 jeweils PASS / FAIL / ÜBERSPRINGEN erfassen. Main-Merge ist im aktuellen Chat autorisiert, Gerätezugriff oder automatische Fremd-Addon-Patches sind es nicht.
