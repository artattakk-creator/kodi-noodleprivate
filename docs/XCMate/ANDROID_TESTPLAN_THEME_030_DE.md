# XCMate 0.1.30 – Android-TV-Abnahme, vollständig NOT_RUN

Stand 21.10.2026. Kodi **21.3 Omega / Android ARM32**, zuerst **Titan BINGIE MOD**, danach Estuary. Originale jetzt **98/98 vorhanden und gebaut**; kein Asset-Downloadblocker mehr. [Pakete, Prüfsummen und vollständige Sicherung](INSTALLATION_0292_UND_THEME_030_DE.md), [Prüfbericht](PR50_PRUEFBERICHT_030_20261021_DE.md), [98-Dateien-/106-Key-Matrix](SPACE_PREMIUM_RENDERER_MATRIX_030.json).

Vor jedem Update Kodi sauber beenden, das gesamte tatsächliche XCMate-Profil **einschließlich DB/WAL/SHM**, versteckter Dateien und externer Bild-/Metadatencaches konsistent sichern; Dateianzahl, Größen und möglichst Hashes vergleichen. Keine App-Daten löschen, Konten zurücksetzen oder globale Keymap aktivieren. Profilpfade sind abhängig vom verwendeten Kodi-Profil. Zugangsdaten niemals öffentlich hochladen.

Core-Test-ZIP 0.1.30 über dieselbe Add-on-ID installieren, nicht regulär veröffentlichen. Zuerst ohne Theme testen. Danach Original-Theme-ZIP **innerhalb XCMates** importieren, Version 1.0.0 prüfen und aktivieren; Kodi-Add-on-ZIP-Installer ist dafür ungeeignet. Beides vorab vollständig herunterladen und SHA-256 vergleichen.

| Fall | Ablauf und überprüfbares Soll | Status |
|---|---|---|
| T01 | Konten, Gruppen, EPG-Quellen, manuelle Zuordnungen, Favoriten, Resume, Startsender/-gruppe und IR-Belegung vor/nach Update vergleichen | NOT_RUN |
| T02 | Standarddesign: Hauptmenü, Live-TV, EPG, Filme, Serien, Suche und Settings unverändert bedienbar | NOT_RUN |
| T03 | Designs: mehrere installierte Versionen anzeigen; lokales/USB-/SMB-ZIP wählen; Cancel in Auswahl und Fortschritt ohne halbe Revision | NOT_RUN |
| T04 | Original Space Premium 1.0.0 importieren/aktivieren, nächste Ansicht und Versionsanzeige; Standarddesign und bestätigtes Entfernen, Nein/Back ohne Wirkung | NOT_RUN |
| T05 | Alle real angebundenen Matrixeinträge in passenden Ansichten prüfen: EPG-Zustand/Details, Mediaaktionen inkl. Favorit plus/minus, Widgets ohne/mit echter Provider-Art, Livegruppen/-sender, Infobar, Controls, Extras | NOT_RUN |
| T06 | Bei 720p/1080p/4K: Safe Area, Alpha, Kontrast, Schrift, Icons und Fokus sichtbar; echte Kodi-Screenshots mit Versions-/Auflösungsnachweis erstellen | NOT_RUN |
| T07 | Stock und Theme dieselben IR-Sequenzen je 30-mal: OK → Info; OK/Runter → Controls; Links → Sender; weiteres Links → Gruppen; Hoch/Runter; Menu; Back je Ebene. Kein verlorener/doppelter Schritt, Fokus und Zap-Ziel identisch | NOT_RUN |
| T08 | Video und Audio laufen lassen, Theme/Standard vormerken: keine Unterbrechung; Wechsel erst in neuer Ansicht nach Wiedergabeende. Keine globale Skin-/Keymapänderung | NOT_RUN |
| T09 | Neustart/offline: aktive Bilder lokal nutzbar; Fernbedienungsnavigation ohne Netzwerkzugriffe. Defekte/fehlende Theme-Datei nur in gesicherter Testkopie: neue Ansicht fällt auf Core zurück | NOT_RUN |
| T10 | Neue Version über getrennte Testkopie installieren, identische Revision idempotent, andere Bytes unter gleicher Version abweisen; alte offene Controls behalten gültige Pfade | NOT_RUN |
| T11 | Offline/Timeout/404, falscher SHA, inkompatibler Core, trunkiertes/überdimensioniertes/unsicheres Archiv und Speicherknappheit kontrolliert testen. Verständliche Ablehnung, bisherige Auswahl erhalten, keine Coverlöschung | NOT_RUN |
| T12 | Online vor Merge: verständlicher 404-Hinweis, kein angeblicher Download. Nach später expliziter Freigabe: Katalog **und ZIP** auf untenstehenden main-URLs am Gerät HTTP 200; Bytes/Hash 1.0.0 vergleichen, erst dann installieren | NOT_RUN / REQUIRES_FUTURE_MAIN_AVAILABILITY |
| T13 | RAM, Peak-RAM, Importzeit und je 10 Kalt-/Warmstarts Stock/Theme messen; große Listen/Widgets ohne Tasten-HTTP. Keine unbewiesene Leistungsverbesserung annehmen | NOT_RUN |
| T14 | Noodle Private, BINGIE MOD, andere Add-ons, globale Keymaps und Einstellungen vor/nach Test unverändert | NOT_RUN |

## Issue #40: gezielter Wiedergabe- und Diagnoseplan

Alle folgenden Fälle sind **NOT_RUN**. Live-Spinnerursache bleibt unbewiesen. Der automatisiert bewiesene doppelte asynchrone Stop ist kein Nachweis der Android-Ursache.

1. Live-TV starten, Sender/Quelle anonym kennzeichnen. Uhrzeit, Skin, Fullscreen und sichtbare Overlay-Ebene protokollieren. Back zunächst Gruppen → Sender → versteckt/geschlossen: Stream und Ton müssen weiterlaufen, **kein STOP_SENT** allein durch Schließen einer Ebene.
2. Tatsächlich in die XCMate-Ansicht zurückkehren: nur verifiziert eigene Wiedergabe inkl. Audio stoppt. Back unmittelbar nach Start, beim Puffern und in schnellen Wiederholungen testen; außerdem Senderwechsel und unabhängige fremde Add-on-Wiedergabe. Fremde Streams dürfen niemals gestoppt werden.
3. Echten Film und echte Serienfolge je zehnmal starten/zurückkehren, auch schnell beim Laden. Bild/Ton stoppen genau für das eigene Item; Resume bleibt nach Kodi-Neustart. Neu gestartetes anderes Item darf nicht durch einen alten Pending-Stop blockiert werden.
4. Hängerfall mit genauen Zeiten filmen/protokollieren, keine Profil-/Cachelöschung. Nach Stop/Neustart Diagnoseansicht öffnen und lokale `xcmate_diagnostic_*.json`, besonders `xcmate_diagnostic_exit.json`, aus dem Add-on-Profil sichern. Zusätzlich **kodi.log und kodi.old.log** sichern: `[XCMate][EXIT]` und `BACK_RECEIVED` werden sofort mit erlaubten Zustandsdaten geloggt, selbst wenn der Service die Queue vor dem Hänger noch nicht persistieren konnte.
5. Erwartete Codes: `EXIT_REQUESTED`, `RESUME_CHECKPOINT`, `STOP_SENT`, ggf. `STOP_PENDING` oder `STOP_FAILED`; `FULLSCREEN`/`NAVIGATION` mit window_id/dialog_id/busy. Native Fenster-/Busy-Übergänge und Abstand zum letzten BACK_RECEIVED vergleichen. Fehlender Datensatz ist kein Beweis, dass Kodi das Ereignis nie empfing.
6. Die Exit-Queue ist begrenzt und wird durch den Service gespeichert; der GUI-Close-Checkpoint erzeugt **keine zusätzliche Exit-Dateischreibarbeit**. Bestehende Close-/SQLite-Pfade können weiterhin lokale IO enthalten und müssen am Gerät zeitlich eingegrenzt werden. Keine unbelegte Ursache behaupten.

Logs vor Weitergabe auf Kodi-eigene Provider-URLs/Zugangsdaten prüfen und bereinigen. Neue XCMate-Exitdiagnose schreibt keine URLs, Account-/Streamnamen oder rohen Identitätsmarker. Vollständige Profile/DBs gehören nicht in öffentliche Issues.

## Noch offene Integration und Freigabe

Zwölf Originale sind im Paket, aber ohne Verbraucher: branding.fanart/splash/wordmark, icon.epg.auto-switch/record/today, icon.player.skip-back/skip-forward, icon.shared.filter/sort/warning und panel.loading. Keine neuen Aufnahme-/Skip-Aktionen oder Startup-/Loading-Fenster als Texturtest erfinden. Diese Einträge sind **OPEN_RENDERER**, keine bestandene vollständige Designabnahme.

#37 (lokale Gruppengröße) und #38 (~17 s Start bzw. frühere Startbeobachtung) separat messen und berichten; hier keine Ursachen-/Lösungsbehauptung. Online-URLs nach künftiger Freigabe:

- `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/themes/xcmate/catalog-v1.json`
- `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/themes/xcmate/space-premium/XCMate-Space-Premium-1.0.0.zip`

Je Fall Datum, Gerät/Android/Kodi/Core/Theme/Skin, Hash, Tastenfolge, Soll/Ist, Zeiten/RAM und Diagnosecode festhalten. Cloudtests ersetzen weder IR noch Renderer noch Audio-/Video-Gegenprobe. Rollback: Kodi beenden, unveränderte veröffentlichte 0.1.29.2 über dieselbe ID installieren und bei Bedarf vollständige konsistente Sicherung wiederherstellen. **Kein Merge/Release/Produktivindex-Update ohne Benutzerentscheidung.**
