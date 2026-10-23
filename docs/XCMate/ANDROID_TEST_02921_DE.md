# Android-Abnahme XCMate 0.1.29.21 – Autoplay

**Alle folgenden Punkte: NOT_TESTED**, bis der Nutzer den echten Ablauf bestätigt.
Kodi 21.2 Omega, Android 13 ARM32, Titan BINGIE MOD, IR-Fernbedienung; wenn möglich Vergleich mit Estuary. .20 bleibt Rückfallbasis.

1. ZIP und SHA256 aus demselben Draft-PR laden, Prüfsumme vergleichen, über „Aus ZIP-Datei installieren“ installieren und Kodi regulär neu starten. Version .21 prüfen. Keine Neusynchronisierung, Cachebereinigung oder Datenlöschung. Testserie mit verlässlichen Folgenmetadaten wählen; für Fortschritt Testfolgen mindestens 60 Sekunden, sinnvoll 2–3 Minuten. Ein Sprung mit Seek kann Callback-/Resume-Verhalten anders beeinflussen; mindestens einen kompletten natürlichen Ablauf prüfen.
2. Drei tatsächlich aufeinanderfolgende Folgen natürlich auslaufen lassen. Ohne weiteres OK muss die nächste beginnen. Titel, Staffel/Folge und Zeiten der eigenen Leiste mit OK kontrollieren. Nicht nur vorgerückte Detailbeschriftung als laufenden Stream zählen.
3. Letzte Folge einer Staffel natürlich beenden; erste tatsächlich vorhandene Folge der nächsten Staffel muss starten. Falls verfügbar Nummernlücke prüfen. Bewusst später eingestiegene Folge muss bei ihrem Nachfolger weitermachen, nicht bei S1E1. Specials dürfen nicht automatisch starten.
4. OK → **Autoplay: Ein** → umschalten auf **Aus**, natürliches Ende abwarten: keine nächste Folge. Während einer weiteren echten Wiedergabe wieder Ein schalten und Fortsetzung prüfen. Die Option ist nur für die laufende eigene Episode/Kette; keine globale Einstellungsmigration.
5. Mitten in der Episode **Stop** im eigenen Player wählen: Ton endet, keine Folge startet später. Ebenso Hardware-Stop, falls vorhanden (sonst NOT_TESTED). Back bei sichtbarer Leiste darf nur die Leiste ausblenden; anschließend Back bei ausgeblendeter Leiste beendet Wiedergabe und Kette.
6. Stop/Back genau beim Episodenwechsel drücken, mindestens fünf Versuche (vor/kurz nach dem tatsächlichen Ende). Kein späterer Hintergrundton und kein doppelter Start. Bei bereits gestarteter Folge Stop nochmals prüfen. Zur Serien-/Staffelansicht zurückkehren und sofort ohne erneutes Verlassen navigieren.
7. Serienende: letzte gültige Folge natürlich beenden, kein Wrap/Neustart. Fehlende oder nicht abspielbare nächste Quelle darf höchstens einen Startversuch und eine verständliche Abbruchmeldung auslösen; kein Replay-/Request-Sturm. Keine absichtlich defekten produktiven Daten anlegen.
8. Eine Folge bis mindestens Minute 1 ansehen, stoppen und Kodi neu starten. Resume muss erhalten bleiben. Eine andere Folge natürlich abschließen, neu starten: korrekter Gesehen-Status, keine verlorenen Favoriten. Automatisch begonnene nächste Folge muss zum richtigen Portal und zur richtigen Serie gehören.
9. Manuellen **Nächste Folge**-Button, beliebige Episodenauswahl, Staffelwechsel, D-Pad-Fokus, Audio-/Untertitelwahl, Pause und Seek prüfen. Filme, normales Live-TV und EPG → „Jetzt Sender ansehen“ wie bisher: keine Autoplay-Kette und keine zusätzliche Stop-/Back-Regression. Fremde Addon-Wiedergabe darf nicht gestoppt oder fortgesetzt werden.
10. Kodi während Wiedergabe und während Wechsel regulär beenden; nach Neustart kein ungefragter automatischer Episodenstart.

Pro Punkt `PASS / FAIL / NOT_TESTED`, genaue Version und Beobachtung melden. Logs vor Upload redigieren (keine Provider-URLs/Zugangsdaten/Tokens). Bei Problemen .20 aus dem unveränderten ZIP installieren und Kodi neu starten; vorhandene Daten behalten.

Anschließend **vor dem separaten EPG-Test .20 wieder installieren**. .22 stammt unabhängig von .20, enthält also kein .21-Autoplay. Keine Freigabe/Veröffentlichung aus Host-Tests ableiten.
