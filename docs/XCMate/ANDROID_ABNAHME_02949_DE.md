# XCMate .49 – Widget-Hotfix: kurze Android-Abnahme

Stand: 28.10.2026 (Europe/Berlin). Issue #252. Basis: main .48. Alle Tests zunächst **NOT_TESTED**; Host-/CI-PASS ersetzt keinen Gerätetest. Keine automatische Geräteaktion, Deinstallation, kein Downgrade und kein Reset. Bestehende produktive Konfiguration, insbesondere Box A, erhalten.

## Installation

ZIP und gleichnamige SHA256-Datei aus dem Draft-PR herunterladen, Prüfsumme vergleichen. Über Kodi → Add-ons → Aus ZIP-Datei installieren **als Update über .48** installieren. Kein neues Profil und keine Daten-/Cachelöschung. Solange der PR nicht ausdrücklich freigegeben und gemergt ist, ist .49 kein regulär veröffentlichtes Repository-Update.

Vorher Gerätename, Kodi-Version, Titan-BINGIE-MOD-Version, installierte XCMate-Version und bestehende drei Widgetbindungen notieren. Keine funktionierende Reihe für den Test löschen; für eine neue Auswahl eine freie/gezielt gewählte Reihe verwenden.

## Drei Schritte

| Test | Durchführung und Erwartung | Status |
|---|---|---|
| W49-01 – Menü und Quellen | XCMate → Einstellungen → **Aussehen und Darstellung → Widgets**. Direkt **Live-TV – Startgruppe**, **Filme – Neueste Filme**, **Serien – Neueste Serien** sichtbar. Jeden Ordner öffnen: echte Sender bzw. Titel bei vorhandenem lokalen Bestand; kein URL-Textviewer und kein Wiedergabestart beim bloßen Öffnen. Zurück funktioniert. Die Anleitung erklärt das Speichern durch BINGIE. | NOT_TESTED |
| W49-02 – BINGIE auswählen und speichern | In der BINGIE-Widget-Konfiguration eine freie/gezielt gewählte Startseitenreihe konfigurieren. **Video-Add-ons → XCMate → Einstellungen → Aussehen und Darstellung → Widgets → gewünschte Quelle** durchstöbern. Innerhalb des Quellordners **Als Widget verwenden / Use as widget** wählen und BINGIE-Konfiguration bestätigen/verlassen. Für alle drei Quellen wiederholen. Kodi Home zeigt echte Sender/Filme/Serien; jeweils einen Eintrag bedienen. XCMate selbst meldet beim Durchstöbern ausdrücklich noch keinen Speichererfolg. | NOT_TESTED |
| W49-03 – Neustart und Bestand | Kodi regulär beenden und erneut öffnen: gespeicherte Reihen weiterhin vorhanden. Alte Widget-URLs bleiben gültig; vorhandene Film-/Seriencover und automatische Aktualisierung bei einer regulären Katalogänderung erhalten. Live-TV-Start und Back, Portale, Gruppen, EPG-Zuordnungen, Favoriten, Resume und .42-Kompatibilitätsmodus unverändert. Keine neue Skinbindung/Reset für bestehende funktionierende Reihen nötig. | NOT_TESTED |

Ergebnis je Zeile PASS/FAIL/NOT_TESTED mit Gerätezeit und Beobachtung notieren. Gibt es keinen tatsächlichen neuen Katalogstand, Autorefresh in W49-03 ausdrücklich **NOT_TESTED** lassen statt ihn durch Datenlöschung oder erzwungenen Vollimport zu simulieren. Bei FAIL genauen Menüschritt/Wortlaut und privat gesicherten Kodi-Logzeitpunkt erfassen; keine privaten Rohlogs/Provider- oder SMB-Daten veröffentlichen.

Die Live-Hero-Integration wird durch diesen Hotfix nicht in BINGIE eingebaut. Die bereits vorhandene eigene .48-Vorschau bleibt unter „Status vorhandener Widgets und weitere Funktionen“ separat erreichbar. Keine neuen Skinadapter-, USB-, SMB-, Aufnahme- oder Downloadtests für diesen Hotfix.
