# XCMate 0.1.29.70 – EPG-Bilder und verständliche Fehlerdiagnose

Basis: main .69, ebf12b3667df65f865d1e617457551ff9327f303. Draft-PR #319. Kein Merge oder reguläres Repository-Release ohne neue Freigabe.

## Was der Nutzer beobachtet hat

Mini-EPG-Details: HELPER_TIMEOUT und „Ergebnis für diese Sitzung vorgemerkt“.
Großer EPG: HELPER_BACKGROUND_UNAVAILABLE, teilweise NOT_SCHEDULED.
BINGIE Home: weiterhin kein Sendungsbild.

Die beiden privaten Anhänge kodi.log und kodi.old.log sind wegen ausgefallener Arbeitsumgebung **nicht lesbar**. Sie wurden nicht heruntergeladen, ausgewertet oder öffentlich hochgeladen. Zeitpunkte, Zählwerte, tatsächliche Laufzeit, Sender-/Quellenkonfiguration und eigener TMDB-API-Status dieses Geräteversuchs sind deshalb **BLOCKED / nicht belegt**. Ein anonymisierter Textauszug wurde angefragt. Aussagen unten sind reproduzierte Quellcodebefunde; ihre Zuordnung zu diesem konkreten Android-Versuch bleibt offen.

## Nachgewiesene Codefehler

### 1. Fünf-Minuten-Lücke zwischen Anzeige und Hintergrunddienst

programme_requests68.result verwarf jedes Statuspaket nach 300 Sekunden. drain übersprang dagegen ein Ereignis, solange dessen Artwork-/Negativ-TTL noch gültig war; negative Ergebnisse können sechs Stunden, positive URLs bis zu einem Tag gelten.

Reproduktion: Eine geprüfte Bildreferenz wird veröffentlicht, der Statusumschlag ist sechs Minuten alt, die Bildreferenz weiterhin gültig. .69 liefert kein Ergebnis mehr; der Worker akzeptiert denselben Status weiterhin und startet nichts Neues. Entsprechend kann die Oberfläche PENDING/NOT_SCHEDULED melden, obwohl ein Ergebnis existiert. Bei schreibgeschützter DB fällt der alternative persistente Lesepfad weg. Dieser Codepfad passt als Verdacht zum Bericht, ist ohne die neuen Logs kein bestätigter Geräte-Root-Cause.

.70 verwendet dieselbe tatsächliche Gültigkeit: Status älter als fünf Minuten nur bei unexpired TTL, aktueller Quellenrichtlinie, Profil- und Ereignisbindung. HTTPS-Bildnachweise, Ablauf, Host-/Credential-/Quellenprüfungen bleiben zusätzlich aktiv. Zustände ohne Ergebnis-TTL laufen weiterhin nach fünf Minuten ab. Kein SQL oder Netzwerk in der GUI.

### 2. Expliziter Retry blieb im negativen Sitzungscache hängen

resolve und enqueue konnten ein negatives RAM-Ergebnis zurückgeben, bevor der explizite Aktualisierungsauftrag geprüft wurde. Auch der Intake konnte am gültigen Negativstatus vorbeispringen. Der bestehende Refresh-Mechanismus verbraucht seinen Marker; ihn an mehreren Gates nacheinander aufzurufen stiehlt dem Resolver den Auftrag.

.70 liest den bereits vorhandenen profilgebundenen Marker an diesen Gates **nicht konsumierend**. Ein neuer Ergebniszeitstempel beendet den einmaligen Retry. Positive Bilder, CANCELLED und HTTP_RATE_LIMIT werden dadurch nicht invalidiert. Vorhandene betroffene .69-Helper-Negative ohne neue Quellen-Diagnose werden beim nächsten tatsächlichen Zugriff einmal neu geprüft. Keine globale Cache-/DB-/Job-Löschung.

### 3. Angefordert ist nicht gleich „nicht eingeplant“

request konnte erfolgreich ein Intent schreiben, result aber ein leeres Ergebnis zurückgeben, solange noch kein Worker-ACK existierte. Die Diagnose übersetzte PENDING pauschal als NOT_SCHEDULED.

.70 meldet REQUESTED beziehungsweise WAITING_SERVICE. Der erste Anforderungszeitpunkt bleibt bei wiederholtem Fokus erhalten; andernfalls würde jeder GUI-Tick die Wartezeit erneut auf null setzen. Das ist eine wahrheitsgemäße Bestätigung des übergebenen Auftrags und kein behaupteter Bildtreffer.

### 4. Fehlerstatus im RAM ist kein vorgemerkter Bilddownload

RAM_ONLY beschrieb bisher sowohl ein gefundenes Bild als auch einen erfolglosen Lookup. Der Satz „Ergebnis für diese Sitzung vorgemerkt“ erklärt nicht, ob überhaupt ein Bild existiert.

.70 unterscheidet: geprüfte Bildreferenz, erfolglose Bildsuche und Metadaten-Speicherung. HELPER_TIMEOUT heißt, dass der Helper nicht rechtzeitig geantwortet hat; HELPER_BACKGROUND_UNAVAILABLE heißt, dass die Hintergrundabfrage keine verwertbare Antwort liefern konnte. Beide Zustände sind **kein** Render-PASS und bedeuten nicht, dass ein Bild auf den Download wartet.

Zusätzlich werden die Quellen getrennt dokumentiert: eigene TMDB-Suche, lokale Katalogdaten, TVmaze und Helper. Eine eigene API-Abweisung darf nicht allein hinter einem späteren Helper-Fehler verschwinden. Feste ART70-Logereignisse enthalten nur eine pseudonymisierte Ereigniskennung, Quellenklasse und festen Statuscode. Keine Titel, Stream-/Provider-URLs, Tokens, Zugangsdaten oder rohen Exceptions.

## Grenzen und Bestandsschutz

Ein Helper-Timeout beweist weder einen ungültigen eigenen Token noch fehlende EPG-Daten. Der eigene TMDB-Zugang und die Freigabe der Bildsuche sind getrennte Einstellungen; vorhandene Opt-outs werden nicht heimlich eingeschaltet. Nachrichten/Sport bleiben konservativ behandelt, und es werden keine geratenen Bilder oder Stockfotos eingesetzt.

Die neue Version behebt nachgewiesene interne Abruf-/Retry- und Diagnosefehler. Sie kann ohne private Gerätebelege nicht garantieren, dass der externe Helper antwortet oder TMDB für die konkrete Sendung einen eindeutigen Treffer hat. Echter API-Zugriff und Bildanzeige auf Android bleiben NOT_TESTED.

Live-TV-Exit/Kompatibilitätsmodus, Kodi-/Skin-/Widget-Routen, Portale, EPG-Mappings, bestehende Bilder, Token/Passwörter, Resume und Autoplay bleiben erhalten. Keine Neuinstallation, Resets, Datenlöschung oder automatische Änderungen auf Box A.
