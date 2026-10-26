# .38 – Zustandsvertrag, Scope und Abnahme

Basis e25020c80703d440b0606b6d66559428dfc96cca, main .37. Der neue Nutzerauftrag vom 26.10.2026 und #181 ziehen die beiden Player-OSDs ausdrücklich in .38 vor; ältere .39/.40-Versionsangaben gelten dafür nicht. Keine Übernahme alter Branches. Keine Geräteänderung; Box B dynamisch, keine weiteren Ablage-/Migrationstests auf B. Box A erst read-only Inventur/Sicherung, jede reale Kopie/Aktivierung/Löschung separat freigeben.

## Live-Zustände

| Links ab Vollbild | Zustand | Rechts/Back |
|---|---|---|
| 1 | MINI_EPG: Sender links, echte Vorher/Jetzt/Danach-Spalte rechts | Rechts fokussiert Programm, Back blendet aus |
| 2 | SENDERGRUPPEN, nur aus linker Mini-Spalte | Mini mit gleichem Sender/Scroll |
| 3 | NAV_RAIL_COMPACT | Gruppen |
| 4 | NAV_RAIL_EXPANDED | Kompakt |
| 5 | LIVE_FULL, Video läuft | bisheriger letzter Sender / bestehender kontrollierter Exit |

Rechte Mini-Spalte: Links/Back nur zurück zur Senderliste, ↑↓ reale Events, OK Details ohne Tune. Bloßes Markieren links stimmt nicht um. Rail-Einträge datengetrieben und lokal: Suche, Favoriten, Live, Filme, Serien, großer Guide, Einstellungen, Home; Gruppen/Startsender kontextabhängig. Keine Kontext-Links-Aktion des großen EPG oder der Detailmenüs ersetzen. Globale dreigeteilte Suchmaske strikt optisch unverändert.

## Player und Einstieg

Einmal OK: Live-Info; zweimal OK/Runter: echte fokussierbare Buttons. Back schließt OSD, Stop benutzt vorhandenen asynchronen Exit und beendet nur eigene Session. Kodi bleibt Decoder. Native Audio-/Bilddialoge sind fremde modale Owner und werden nicht geschlossen. Pause/Seek nur bei tatsächlicher Kodi-Fähigkeit. VOD-Autoplay und Resume unverändert; keine Daten-/HTTP-Abfragen im IR-Callback.

Autostart ist eine pro bewusstem App-Einstieg verbrauchte Absicht, keine 30-s-Refresh-Regel. Root und kompatibler app_open-/Home-Shortcut teilen einen Lease; Service beobachtet Verlassen, damit Refresh/Back/Setup/Navigation nicht erneut starten. Diagnosepause ist bewusst temporär, der historische Default blockiert keine gespeicherte Nutzeroption mehr. Race- und Foreign-Player-Test vor Player-Aufruf.

## Host-/Android-Gates

Zuerst P0-Einstieg und TTL-Reproduktion. Dann Rail/Mini, Player-Capabilities/Owner/Fokus, Diagnose/Inventur und optionale doppelt bestätigte eigene Bildbereinigung. Bestehende 1.298 Tests erhalten, neue gezielte Tests, >=20k Bildfixture, reproduzierbares ZIP/SHA, CI und deutsche Abnahme. Echte .38-Android-Tests auf Kodi21.2/21.3 bleiben NOT_TESTED; historische .37-PASS von B sind Regressionserwartung, keine neue .38-Abnahme. Keine OSD-Designabnahme aus Host-CI. Drei Layoutskizzen zur separaten visuellen Auswahl liefern. #161 EPG-Hub bleibt separat; offene physische Metadaten-/Wizard-Scanresume-Blocker werden nicht still als erledigt markiert.
