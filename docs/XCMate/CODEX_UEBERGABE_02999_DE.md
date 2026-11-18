# XCMate 0.1.29.99 – Übergabe zu Issue #488

Die Reparatur basiert auf dem kumulativen Kopf von Draft-PR #487, Commit `81bd2ad0c9c5f2d49de47c693d363a686f886111`. Bildreferenz ist .90, Commit `ae8cb65af2e14852e119e95a3712a002b492f5eb`.

## Reparaturablauf

Der zusätzliche Menüpunkt sichert nach expliziter Bestätigung die ursprüngliche `settings.xml` bytegenau im privaten Profil. Er benötigt kein vorheriges LastGood. Im aktiven Kodi-Prozess verbleibt die ursprüngliche Datei. Der nächste Kodi-Prozess prüft die Originalkopie und den bisherigen Dateistand. Vor dem Start der XCMate-Worker schreibt er eine frische Kodi-Konfiguration atomar und liest sie zurück. Der nachfolgende Kodi-Prozess prüft den Dateistand erneut. Ein interner Prüfwert mit leerem Schema-Default zeigt, ob Kodi tatsächlich die Benutzerdatei geladen hat. Erst danach melden Oberfläche und Protokoll `POST_RESTART_OK`.

Die neue Datei aktiviert den Anbieter-EPG. Optionale Bilder aus XMLTV, TMDB, TVMaze, TMDb Helper und dem Katalog bleiben zunächst ausgeschaltet. Separate Portale, Token-Datei, EPG-Bestand, Favoriten, Senderlogos und Zuordnungen liegen außerhalb der Reparatur. Werte, die ausschließlich in der alten `settings.xml` stehen, bleiben in der Originalkopie erhalten und sind nach dem Neuaufbau nicht mehr aktiv. Die Bestätigung erklärt diesen Unterschied. Ein zuvor gewählter Ordner für ältere Kurzzeitcaches muss erneut ausgewählt werden. Die vorhandenen Cache-Dateien bleiben auf dem Datenträger.

## Nachgewiesene Bildregression

Auf .90 konnte XCMate den bereits unabhängig zugeordneten Backdrop direkt verwenden. Auf .98 hatte die optionale TMDB-Galerie Vorrang. Scheiterten ihre Bilder beim Abruf oder bei der Dekodierung, fehlte der zuvor funktionierende Backdrop in der Fallback-Liste. .99 behält vorhandene freigegebene Galeriebilder in ihrer Reihenfolge und berücksichtigt anschließend den direkten Backdrop desselben Werks. Die Korrektur gilt für den URL-Pfad und die ausdrücklich aktivierte lokale Ablage. Die lokale Ablage kann außerdem eine andere Variante der bereits zugeordneten Datei prüfen, wenn die normalisierte URL scheitert. Bei einem Werk, für das nur ein bestätigtes offizielles Poster vorliegt, kann die lokale Ablage dieses Poster wieder verwenden.

Die identischen vier Host-Regressionsfälle bestehen mit .90 und .99 und schlagen mit unverändertem .98 fehl. Sie benutzen synthetische Providerantworten, HTTP-404 und ungültige Bilder sowie Host-Bilddekodierung. Die Android-Bilddarstellung steht zur Abnahme aus.

## Paket und nächste Prüfung

Das Kandidaten-ZIP und die SHA256-Datei liegen unter `test-builds/02999/`. Reproduzierbarer Bau aus der geprüften Quellbasis:

```sh
python3 tools/release_candidate99.py --stage --output docs/XCMate/test-builds/02999
python3 tools/release_candidate99.py --output docs/XCMate/test-builds/02999
```

Die [Android-Abnahme](ANDROID_ABNAHME_02999_DE.md) enthält die Testschritte. Verbleibende Risiken sind die Zugriffsrechte und Persistenz auf Android-Dateisystemen, die tatsächliche Kodi-Neustartfolge, sichtbare BINGIE-Texturen, echtes Provider-Verhalten sowie reale Speicher- und Decodergrenzen.
