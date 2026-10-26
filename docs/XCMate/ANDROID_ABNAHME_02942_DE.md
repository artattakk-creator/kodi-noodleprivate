# Android-Abnahme – XCMate 0.1.29.42 P0 Live

Stand26.10.2026. **Alle neuen Gates NOT_TESTED.** Ausschließlich Box B: Android RK3528 ARM32, Kodi21.3. Box A nicht installieren oder prüfen. Keine Deinstallation, kein Downgrade/Reset, keine Daten-/Cache-/Speicher-/USB-/SMB-/SD-/Migrationsprüfung. Dynamisches Artwork, Portale, Gruppen, Favoriten, Resume und EPG-Mappings erhalten. Der optionale BINGIE-Adapter wird nicht installiert.

**Wichtig: Dies ist ein opt-in Lifecycle-Kompatibilitätskandidat, kein nachgewiesener Decoderfix.** Bei Freeze sofort aufhören; keine Wiederholungsschleife und kein Test aller weiteren Gates. Eine sichtbare Startseite mit weiterlaufendem Ton ist FAIL.

## Vorbereitung ohne Wiedergabe

1. ZIP/SHA aus dem Draft-PR prüfen. Als reguläres Update aus ZIP über die vorhandene Installation installieren. Keine automatische Geräteinstallation durch Codex.
2. Installierte Add-on-Version0.1.29.42 kontrollieren. Box-B-Konfiguration/Artwork bleibt bestehen.
3. **Vor dem Startsender:** Kodi → Add-ons → XCMate → Konfigurieren → **Wiedergabe** → **„Live-TV: Vollbild vor Stop freigeben (Android21.3-Kompatibilitätstest)“ EIN**. Falls im XCMate-Einstellungsmenü: Wiedergabe → Add-on-Einstellungen öffnen. Nur diese neue eigene Option bewusst ändern. Keine Kodi-Hardwarebeschleunigungs-, Audio-, Skin- oder IR-Einstellung ändern.
4. Mit OK speichern und den Einstellungsdialog vollständig verlassen. Die Option ist standardmäßig AUS; ohne Einschalten verwendet .42 den auf Box B bereits gescheiterten .41-Stop. Den ausgeschalteten Vergleichspfad deshalb nicht erneut absichtlich als Freeze-Test ausführen.
5. Keine fremden Player/Add-ons parallel starten. Fremde Modaldialoge vorher regulär schließen, nicht mit einem erzwungenen Close-Befehl.

## Strikte erste Reihenfolge

| Gate | Durchführung und echte PASS-Bedingung | Status |
|---|---|---|
| PREP42-01 | .42 auf Box B, neue Option bewusst EIN; vorhandene Daten und dynamischer Artwork-Modus vorhanden. | NOT_TESTED |
| START42-01 | Konfigurierten Startsender einmal starten. Bild und Ton stabil, normaler Live-Vollbildzustand. | NOT_TESTED |
| LIVE42-01 **P0** | Ohne offenes Overlay **einmal Zurück**. Stream endet einschließlich Ton; native Freigabe kehrt zurück; Home/Videos bedienbar; IR reagiert. Kein STOP_TIMEOUT, kein Dauerstandbild. Erst nach diesem PASS weiter. | NOT_TESTED |
| VOD42-01 | Erst nach LIVE42-01 PASS einen Film starten, Vollbild mit Zurück verlassen. Eigener Filmstream endet, vorherige Medienansicht und Fernbedienung funktionieren. | NOT_TESTED |
| REG42-01 | Mini-EPG, großer EPG und bestehende Ansichten kurz öffnen; .41-Textebene/Zukunft, Auswahl und Back-Ebenen erhalten. Offene Live-Overlays schließen mit Back nur ihre Ebene. Erst danach Hidden-/Vollbild-Back zum Beenden. | NOT_TESTED |
| LIVE42-05 | Erst nach obigen PASS **fünf weitere** reguläre Startsender-/Live-Back-Zyklen; alle fünf mit Bild/Ton-Ende und bedienbarer Rückkehr. Bei einem FAIL abbrechen. | NOT_TESTED |
| LIVE42-20 | Erst nach LIVE42-05 PASS **zwanzig weitere** reguläre Zyklen. Keine automatisierte Stressschleife; bei einem FAIL abbrechen. | NOT_TESTED |

Die fünf und zwanzig Zyklen sind zusätzliche Zyklen zum ersten Einzeltest. Keine Hostzahlen als Geräte-PASS übernehmen. STOP_DONE/Native-ACK aus Logs ist nur eine zusätzliche technische Bestätigung; allein reicht sie ohne Ton-Ende und bedienbare Oberfläche nicht.

## Bei FAIL: genau das Fehlersignal festhalten

- Letzte sichtbare Ansicht und letzter Bedienvorgang, Bild/Ton/IR-Reaktion, Uhrzeit Europe/Berlin, Version und Option EIN/AUS.
- In einem privaten Logauszug nur feste XCMate-Phasen: STRATEGY_FULLSCREEN42, FULLSCREEN_EXIT_POSTED/RETURN/READY, PLAYER_STOP_START, NATIVE_STOP_POSTED, PLAYER_STOP_DONE, STOP_TIMEOUT, STOP_REJECTED, LATE_*.
- **PREP-Timeout** ohne FULLSCREEN_READY und **nativer Close-Hänger** nach FULLSCREEN_READY unterscheiden. Keine zweite Stop-Anforderung senden, um die Quarantäne „wegzudrücken“.
- Kein Neustart, Abwarten oder beendeter Pythonworker als PASS werten. Codex installiert/steuert/restartet die Box nicht. Weitere Diagnose einschließlich ADB/ANR/Stacks nur nach separater Freigabe; keine privaten Rohlogs öffentlich hochladen.

## Reversibilität und Fortsetzung

Die neue Option kann bei beendeter Wiedergabe über denselben Schalter wieder AUS geschaltet werden; keine Dateien oder Kodi-Decoder-Einstellungen zurückzusetzen. **Das repariert keinen bereits hängenden nativen Prozess** und ist keine Aufforderung zum erneuten Test des bekannten .41-Fehlers. Für die Abnahme muss der geprüfte Modus zusammen mit dem Ergebnis dokumentiert bleiben.

Issue#215 bleibt historisch unverändert: .41 Startsender-Teilfunktion PASS, LIVE41-01 FAIL, 5er/20er BLOCKED, übrige .41-Gates NOT_TESTED. Nach bestandenen P0-Gates die ursprüngliche [40-Gate-.41-Liste](ANDROID_ABNAHME_02941_DE.md) auf .42 fortsetzen; frühere FAILs bleiben am damaligen Versionsstand erhalten. Kein pauschaler Gesamt-PASS, Issue-Close, Merge oder Release ohne echte Abnahme und ausdrückliche Freigabe.
