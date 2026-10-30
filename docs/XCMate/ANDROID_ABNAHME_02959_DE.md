# .59 – kurze Box-B-Abnahme nach Fertigstellung des Testpakets

Aktueller Stand sämtlicher Geräteprüfungen: NOT_TESTED. Kein autorisierter Gerätezugang in dieser Sitzung. Diese Anleitung wird mit dem fertigen Paket bereitgestellt; vorab wird keine neue umfangreiche Abnahme angefordert. Box A bleibt ausgeschlossen. Keine Neuinstallation, kein Downgrade, keine Profil-/Skinshortcuts-/Cache-Rücksetzung.

Zunächst ZIP/SHA256 aus dem Draft-PR vergleichen und .59 nur nach eigener Testentscheidung auf Box B regulär aktualisieren. Bestehenden .42-Kompatibilitätswert beibehalten; keine automatische Umstellung. Installationspopup soll .59 und konkrete Änderungen zeigen. Bereits vorhandene Widgetbindungen NICHT löschen oder neu speichern.

| Schritt | Kurzer Ablauf / PASS-Bedingung | Neuer Kandidat |
|---|---|---|
| W59 – Filme und Serien | Vorhandenes BINGIE Home öffnen, ohne Wiedergabe zu starten. Je mindestens zehn unterschiedliche Titel mit richtigen Providerpostern sichtbar, Fernbedienungsfokus und Detailklick korrekt. Nach normalem Kodi-Neustart weiter vorhanden. Bei Unsichtbarkeit lediglich festhalten; kein Reset/Neubinden. PUBLISHED allein ist kein PASS. | NOT_TESTED |
| E59 – Anbieter-EPG | EPG-Manager: Anbieter aktiviert lassen. „Jetzt aktualisieren“ muss auch bei offenem Einrichtungscheckpoint erreichbar bleiben; „EPG-Einrichtung fortsetzen“ ist separat. Fortschritt und Abschlussbericht abwarten: echte gespeicherte Sender-/Sendungszahlen und Zeitraum, oder konkrete Fehlerstufe. Drei reale Sender in großem/kleinem EPG vergleichen. Bestehende externe Quellen und Mappings erhalten. | NOT_TESTED |
| B59 – Sendungsbild | Ein tatsächlich vorhandenes Ereignis mit Provider-/XMLTV-Bild im großen EPG-Detail öffnen. Richtiges Bild bzw. verständlicher fehlender/blockierter Bildstatus; Logo/Text/Zeiten und Fernbedienung bleiben bedienbar. Keine willkürlichen Ersatzbilder. Quellenzuweisung bei Bedarf nur mit RAM-Vorschau vergleichen; Abbrechen bewahrt die alte Zuordnung. | NOT_TESTED |
| R59 – Live-TV-Zurück | Erst einen einzigen Startsender→Back-Vorgang. Overlays schließen nur ihre Ebene. Nach bestätigtem Stop muss die richtige Oberfläche bedienbar zurückkommen, ohne zweiten Stop oder Replay. Bei einem Freeze sofort alle weiteren Wiedergabe-/Lasttests abbrechen; tatsächliche Uhrzeit und anonymisierte ACK-/Return-Codes festhalten. Nur nach PASS optional weitere fünf Zyklen und Film-/Serien-Back/Resume prüfen. | NOT_TESTED |

Für die spätere Benutzerabnahme je Schritt PASS / FAIL / ÜBERSPRINGEN und kurze Beobachtung eintragen. ÜBERSPRINGEN gilt nicht als PASS. Ein Diagnosecode oder Host-Pixelnachweis ersetzt keine reale Geräteprüfung.

Nach erfolgreichem Import optional die bestehende manuelle EPG-Zuweisung mit Provider und einer externen Quelle vergleichen; Rastervorschau vor Speichern, Abbrechen ohne Änderung und Persistenz nach Neustart kontrollieren. Kein zusätzlicher EPG-Datenspeicher oder neue Widgetverwaltung.

Keine Rohlogs, Provider-URLs, Zugangsdaten, Portal-UUIDs, privaten Netzadressen oder absoluten Benutzerprofilpfade veröffentlichen. Die neue Home-Diagnose protokolliert feste Codes und Zahlen; Entry-/DIRECTORY-Nachweis und tatsächliche Home-Container getrennt bewerten. Bei einem legitimen fremden Dialog wartet die Rückkehr, ohne ihn zu schließen. Fehlendes natives ACK bleibt ein anderer, offener Fehlerfall.
