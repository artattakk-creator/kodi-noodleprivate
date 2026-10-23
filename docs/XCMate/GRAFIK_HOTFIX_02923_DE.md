# XCMate 0.1.29.23 – Grafik-Testkandidat

Basis: main 283c006ebafc6a237365652edaffcbb3bc2ba990, produktive 0.1.29.22. Separater Draft; kein Merge, Release oder OTA-Update. Android-Abnahme steht aus.

## Befund und Änderung

Das unveränderte Original-Icon hat SHA256 `81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135`. .22 verwendete weiterhin den alten Dateinamen `icon.png`; der Repository-Builder stellte das in Kodi-Metadaten referenzierte Icon bisher nicht außerhalb des ZIP bereit. .23 verwendet in Metadaten, Laufzeit und Home-Starteintrag `icon-81da1003a2753ec6.png` mit exakt denselben Originalbytes und liefert dieses Repository-Asset zusätzlich aus. Das erzeugt einen eigenen Kodi-Bildcache-Schlüssel, ohne Bilddatenbanken anzufassen. Einstellungen → Über XCMate → Original-Icon prüfen zeigt Originalbytes und Art des Kodi-Laufzeitverweises. Das behebt nachgewiesene Paket-/Referenzlücken; die konkrete Ursache auf dem Zielgerät und sichtbare Branding-Abnahme sind noch nicht bestätigt.

Posterfehler waren bisher pauschal NETWORK_ERROR. Jetzt unterscheiden Worker HTTP-Authentifizierung, nicht gefunden, Rate-Limit, Server-/Clientfehler, DNS, TLS, Timeout und Verbindung von ungültigen Quellen/Bildern und Speicherfehlern. Die Hintergrundqueue behält ihre begrenzten drei Versuche. Permanente Fehler verbrauchen keine weiteren automatischen Netzwerkversuche; Retry-After wird begrenzt respektiert. HTTP-interne Wiederholungen sind nur für Artwork deaktiviert.

Filmdetails bieten Posterstatus/erneut versuchen: Quelldatenfeld, Anzahl vorhandener Kandidaten, Status, Versuche und Zeitwerte ohne Provideradresse oder Zugangsdaten. Die Einzelaktion setzt ausschließlich diesen Job zurück, mit dauerhafter 60-Sekunden-Sperre und Rate-Limit-Schutz. READY-Dateien und andere Jobs bleiben erhalten. Nach permanentem oder ausgeschöpftem Fehler kann ein anderer gültiger Bildverweis desselben Metadatensatzes verwendet werden. Es gibt keine Suche nach Titel/Jahr, keinen Vollimport und keinen globalen Queue-Reset.

Für Disney → Aladdin (1992) liegen weder tatsächliche Providerantwort noch aktuelle Jobdetails vor. Deshalb ist eine konkrete Remote-Ursache oder ein repariertes Cover nicht bewiesen. Die neue Diagnose ermöglicht diese Zuordnung am Gerät. Alternative Quellen existieren nur, wenn der aktuelle Eintrag sie tatsächlich mitliefert.

## Erhalt und Grenzen

Guide-Grid, Guide-Fenster/XML, Owner-Pump, Autoplay, Player-OSD, Resume und Wiedergabeübergabe bleiben unverändert. In MediaWindow ist nur eine zusätzliche Detailaktion ergänzt. Bestehende Bilder, Portale, Zuordnungen und Nutzerdaten werden nicht gelöscht. Keine Kodi-Keymap-/Skin-/Cacheänderung. Fehlende Providerbilder können ohne gültige alternative Quelle nicht erfunden werden. Keine Hostprüfung ersetzt Kodi-21.2-/Android-Abnahme.

Offen: #37 sichtbare Geräteabnahme; #111 konkreter Aladdin-Fehler; #41/#90 vollständige Artwork-Abnahme; #69 SQLite-Sonderfälle. #85 B02 bleibt außerhalb aktiver Tests. Theme-Installer, Downloads, Aufnahmen und Timeline folgen in eigenen Entwicklungspaketen.
