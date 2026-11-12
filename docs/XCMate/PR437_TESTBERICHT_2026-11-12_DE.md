# PR #437 – Uhrparameter und Medien-Consumer

Stand: 12.11.2026. Basis: `4336dd56a707f80b3784fa11f179d2a427cd5727`, veröffentlichte .90. Keine neue Version, kein Merge, kein Release. Das separate Review-Paket besitzt weiterhin Add-on-Version .90 und ist **kein reguläres Update**. Vor einer Geräteinstallation Versions-/Installationsfreigabe einholen; keine Deinstallation oder Rückinstallation.

## Ursache und Änderung

Der Kodi-Directory-Parameter `clock50=$INFO[System.Time(hh:mm)]` wurde vom strikten URI-Validator verworfen. `candidate(layout80=True)` übersprang dadurch gültige Film-/Serien-Consumer. Der Patch normalisiert ausschließlich diesen vollständigen Queryparameter für die Prüfung. Der gespeicherte und generierte Pfad bleibt bytegleich. Unbekannte InfoLabels, doppelte Uhr-Token, andere Parameterpositionen und ausführbare Kodi-Builtins bleiben gesperrt. Genau zwei eigene `widget_base`-Includes werden zu `XCMate80.MediaRow`; Live-TV und Fremdwidgets bleiben unverändert.

Ein eigener nativer CI-Vertrag verwendet die originale SkinShortcuts-2.1.0-Auswahl und deren vorhandene XCMate-Uhr-Presets. Nur in einem frischen synthetischen Profil steht Home zuerst. Dadurch müssen die tatsächlich kompilierten Container **1510/1520/1530** entstehen. Er fordert 88/24/24 native Einträge, fokussierbare Reihen, gemessene Logo-/Coverpixel und drei vollständige Kodi-Prozessneustarts. Keine privaten Backup-Dateien und keine erfundenen gespeicherten Widgetpfade.

## Schutzprüfungen nach veröffentlichter .90

Die vorherige CI hatte 34 Hostfehler: alte Kanal-Guards erwarteten weiterhin .89, Quellhash-Prüfungen kannten die neue Uhränderung nicht, historische ZIP-Prüfungen verglichen alte ZIPs gegen neuen Quellcode. Jetzt pinnen die Kanalprüfungen den bereits autorisierten Release-Commit #432. Historische ZIPs werden vollständig gegen ihre historischen Quellen geprüft. Ein zusätzlicher Vollbyte-Guard akzeptiert ausschließlich die dokumentierte Änderung an `widget_reload78.py`; beliebige weitere Edits normalisieren nicht. Der neue Review-ZIP-Test prüft sämtliche aktuellen Quelldateien und CRC/SHA256. Alte Testmethoden und Skip-Bedingungen bleiben erhalten. Keine Veröffentlichung wird durch diese Anpassung erlaubt.

## Aktuell ausgeführt

| Prüfung | Ergebnis |
| --- | --- |
| Uhrparameter, Sicherheit, zwei Konversionen, Idempotenz, Pfad-/ID-Erhalt | PASS – 9 Tests |
| Kumulative Scope-/Historien-/Bestandsschutztests | PASS – 169 Tests, 80,277 s |
| Zusätzlicher Review-/Release-/Negativschutz | PASS – 4 Tests |
| Aktuelles Review-ZIP: 855 Dateien, CRC und jede Quelldatei | PASS |
| Vollständige Hosttestsuite | RUNNING – Abschluss folgt im PR |
| Neue native Kodi-Containerprüfung 720p/1080p | NOT_TESTED – CI wird mit diesem Commit gestartet |
| Physische Android-Prüfung | NOT_TESTED |

Die bisherigen nativen Gesamtprüfungen sind **nicht vollständig grün**: `NATIVE_ONE_RAIL` im geerbten .75-Vertrag und `GROUP90_NATIVE_VIDEO_NOT_OWNED` im .90-Gruppen-Playback-Vertrag. Diese Fehler werden nicht als Android-Erfolg oder Clock-Fix-Erfolg umgedeutet. Der separate originale Picker war vor dieser Ergänzung erfolgreich; seine Prüfung bleibt bestehen.

## Review-Paket

`docs/XCMate/test-builds/pr437/plugin.video.xtreammate-0.1.29.90.zip`

SHA256: `64582723e2661d8710e903e3a3dcf4b4ff44cacf967459ef2141b1c4ffe8f6f1`.

Die drei veröffentlichten .90-Pakete bleiben unverändert: SHA256 `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`. Installer .5.26 ebenfalls unverändert.

## Android-Abnahme – zunächst vollständig NOT_TESTED

1. Bestehendes Profil, Shortcuts und Einstellungen sichern; nur nach Testinstallationsfreigabe aktualisieren. Kein Reset.
2. Kaltstart: Home mit Live-Hero und Logo-Leiste; Filme und Serien mit Überschriften und echten Covern; native Container 1510/1520/1530 mit tatsächlichen Items protokollieren.
3. Filme und Serien per Down/Up/Left/Right betreten; Fokusrahmen, horizontales Scrollen und OK prüfen.
4. Kodi dreimal regulär neu starten und Skin einmal über die vorhandene bestätigte Aktualisierung neu laden. Reihen und gespeicherte Pfade müssen erhalten bleiben.
5. Fremde Widgets, insbesondere Kino/Trend/Disney-Helper-Verknüpfungen, auf unveränderte Namen, Reihenfolge und Pfade prüfen.
6. Offline/EPG-BUSY: letzte gültige Cover und EPG-Daten erhalten; keine leeren Reihen durch Cachefehler.
7. Sender-/Gruppenwechsel sowie Player-Rückkehr getrennt protokollieren. Bekannter Exit-ACK-Fehler #174 bleibt offen.

## Getrennte Folgearbeiten

Gemäß Übergabe: echter BINGIE-Multiimage-Spinner in eigener kleiner Skin-PR; Zusatzwidget-Diagnose/-Routen separat; EPG-/Artwork-Hub und referenzsichere Bereinigung nach Widget-/Android-P0-Abnahme. Kein automatisches Überschreiben gespeicherter Shortcuts, keine Daten-/Cachelöschung und kein Player-Rewrite im Uhr-Hotfix.
