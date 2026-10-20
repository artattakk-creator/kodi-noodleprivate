# Android-TV-Test: Theme-Installer 0.1.30 – alles NOT_RUN

Ziel Kodi 21.3 Omega, Android-TV ARM32, zuerst Titan BINGIE MOD, danach Estuary.
Der Core-Testkandidat enthält **keine Space-Premium-Originale**. Reale Grafikabnahme
und die nachfolgenden Space-Premium-Fälle bleiben bis Übergabe des geprüften Pakets
blockiert. Keine Installation eines synthetischen Testthemes als Designnachweis.

Vorher den [kompletten Profil-/WAL-/Bildbackupplan](INSTALLATION_0292_UND_THEME_030_DE.md)
befolgen. Zuerst 0.1.29.2 anhand des dortigen Plans separat abnehmen. Dann bewusst
die geprüfte **0.1.30-Core-Test-ZIP aus dem Feature-Branch** über dieselbe ID installieren;
kein produktives Repositoryupdate oder automatisch veröffentlichtes Core-Release.

| Fall | Ablauf / erwartetes Ergebnis | Status |
|---|---|---|
| T01 | Unverändertes Standarddesign öffnen; vorhandene Accounts/EPG/Favoriten/Resume vor/nach Update vergleichen | NOT_RUN |
| T02 | Darstellung & Sprache → XCMate-Designs; alle Einträge per IR/OK/Back erreichbar, Cancel bleibt folgenlos | NOT_RUN |
| T03 | Leerer/noch nicht veröffentlichter Katalog: ehrlicher Leer-/Downloadhinweis, kein angeblich installiertes Space Premium | NOT_RUN |
| T04 | Nach Originalübergabe gültige lokale/USB-/SMB-ZIP auswählen; Fortschrittsdialog bedienen/abbrechen; nur vollständig geprüfte Version erscheint | NOT_RUN / BLOCKED_ASSETS |
| T05 | Installierte Designs zeigt Space Premium 1.0.0; Aktivieren und nächste Ansicht prüfen | NOT_RUN / BLOCKED_ASSETS |
| T06 | Reale Previews Hauptmenü/Live-TV/Gruppen/Sender/EPG/Filme/Serien/Settings/Infobar/Controls mit Originalen erstellen und abnehmen; fehlende Layoutadapter zuerst implementieren | NOT_RUN / BLOCKED_ASSETS |
| T07 | 1080p-/4K-Skalierung, Safe Area, Transparenz, Kontrast, Lesbarkeit und Fokus im Wohnzimmerabstand messen | NOT_RUN / BLOCKED_ASSETS |
| T08 | Freeze: OK Info, zweites OK/Runter Controls, Links Sender, zweites Links Gruppen, Hoch/Runter Zap, Back schließt Ebene; keine doppelten/verlorenen Eingaben | NOT_RUN |
| T09 | Live/Film/Audio laufen lassen, Theme/Standard wählen: Bild/Ton laufen weiter; Wechsel erst neue Ansicht nach Wiedergabeende | NOT_RUN / BLOCKED_ASSETS |
| T10 | Kodi-Neustart mit aktivem Design; offline alle lokalen Themebilder verfügbar; keine Netzwerkabfrage beim Navigieren | NOT_RUN / BLOCKED_ASSETS |
| T11 | Neue gültige Theme-Version installieren: alte Bildpfade bleiben während bestehender Ansicht gültig; Neustart/Wechsel korrekt | NOT_RUN / BLOCKED_ASSETS |
| T12 | Beschädigte/fehlende Datei und Manifest in einer Testkopie: neue Ansicht fällt sicher auf Standard zurück; übriges Profil bleibt identisch | NOT_RUN / BLOCKED_ASSETS |
| T13 | Trunkiertes ZIP, falsche SHA, falsche Core-Kompatibilität, ZIP-Slip/überdimensionierte Testdatei: verständliche Ablehnung; vorheriges Theme bleibt | NOT_RUN |
| T14 | Speicherplatzmangel mit kontrollierter Testumgebung simulieren; keine Cover-/Metadatenlöschung; Abbruchreste bereinigt | NOT_RUN |
| T15 | Standard wiederherstellen; Entfernen nur nach Ja, Nein/Back ohne Wirkung; bei Wiedergabe kein Entfernen/Stop | NOT_RUN / BLOCKED_ASSETS |
| T16 | Globale Skin-/Keymapdateien, Noodle Private und andere Add-ons vor/nach Test vergleichen | NOT_RUN |

Pro Fall Datum/Uhrzeit, Kodi/Core/Theme-Version und Hash, Skin, Eingabefolge, Soll/Ist,
Fehlercode, Start-/Öffnungsdauer und Speicherverbrauch festhalten. Keine Konto-URLs
oder Zugangsdaten in Screenshots/Logs veröffentlichen. Cloud-Mocktests belegen keine
IR-Ereignisse oder tatsächliche Android-Renderleistung. Noch keine Geräteabnahme.

Rollback des Installer-Tests: Kodi beenden, geprüfte veröffentlichte 0.1.29.2 über
dieselbe ID installieren. Optionales `themes_v1` wird vom alten Core ignoriert;
für einen exakt vorherigen Zustand die vollständige zusammengehörige Sicherung
wiederherstellen. Keine Konto-/Appdaten löschen. Kein automatischer Main-Merge.
