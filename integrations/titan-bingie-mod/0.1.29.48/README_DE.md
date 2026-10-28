# Live-TV-Senderleiste und Hero – .48 Review

Status: **BLOCKED_SKIN_INTEGRATION / REVIEW_ONLY_NOT_INSTALLED**.

Der Nutzer hat das Design bestätigt, jedoch keinen beliebigen Umbau seiner vorhandenen BINGIE-Dateien freigegeben. `Includes_XCMate48_REVIEW.xml` wird daher weder installiert noch automatisch referenziert. Kein bestehender Widgetpfad, Skin-Shortcut, Reload-Hook oder Film-/Seriencontainer wird überschrieben. Der bisherige optionale .46-Kacheladapter bleibt unverändert, setzt aber **nicht** das neue Senderleistenkonzept um.

Die echte XCMate-eigene Vorschau ist unter Einstellungen → Widgets → **Live-TV: Senderleiste und große Vorschau (.48)** erreichbar. Sie verwendet `XCMateLiveHero48.xml` und dieselben lokalen Event-/Artwork-Daten wie Guide und Livewidget. Erst OK startet den ausgewählten Stream über den vorhandenen Guide-Handoff; Fokus startet keine Wiedergabe. Keine EPG-/Bildsuche auf dem Fokuspfad.

## Was für eine BINGIE-Aktivierung noch fehlt

1. Read-only-Snapshot der **tatsächlich installierten** Titan BINGIE MOD 2.2.3 und der generierten Home-Widgetdefinitionen; Livecontainer-ID, bestehende URL, Reload-Hook und Bild-/Textbereich belegen. Ein öffentliches Skin-Beispiel ersetzt diese Prüfung nicht.
2. Nur die bestehende Live-Reihe als Senderleiste ersetzen und den dazugehörigen Hero anbinden. Die zwei PASS-Posterreihen und ihre automatischen Aktualisierungsauslöser bytegenau erhalten. Parameter `liveid` und `existing_live_url` im Reviewinclude bleiben deshalb bewusst ungebunden. Existierende Refresh-Bindung in der konkreten Skin-Definition erhalten; der Entwurf erfindet keinen Reload-Hook.
3. Vor jeglichem Skin-Schreiben: Originaldateien privat sichern, SHA256/Größen prüfen, konkreten Diff und Zielpfade vorlegen, ausdrückliche Nutzerfreigabe. Kein automatischer globaler Rebind. Installer darf bei abweichender Skinversion/Dateiprüfsumme nichts überschreiben.
4. Rollback muss exakt die gesicherten Originalbytes wiederherstellen und zwischenzeitlich veränderte Dateien erkennen. Anschließend Fokus, 88+ Sender, Now→Next und beide Medienreihen auf Box B abnehmen.

Ohne diese Nachweise bleibt die **bestehende BINGIE-Startseite** blockiert. Die native Vorschau oder gültige ListItem-Properties sind kein behaupteter Android-/BINGIE-PASS. Keine Änderungen auf Box A.
