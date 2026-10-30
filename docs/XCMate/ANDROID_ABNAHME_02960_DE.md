# .60 – kurze spätere Box-B-Abnahme

Alle Punkte zunächst **NOT_TESTED / ANDROID_NOT_TESTED**. Erst mit geprüftem ZIP beginnen. Ausschließlich Box B; keine Neuinstallation, kein Downgrade, kein Cache-/Profil-/Widgetreset, keine Box-A-Aktion. Eigene TMDB-Daten niemals an GitHub/Chat/Logs weitergeben. Bei einem echten Freeze sofort abbrechen und keine weiteren Wiedergabezyklen ausführen.

Installation und Skin-Rücknahme: INSTALLATION_RESTORE_02960_DE.md. Vorhandene Film-/Serienverknüpfungen und Live-Quelle nicht löschen oder neu anlegen. Die optionale Skin-Anpassung benötigt eine eigene ausdrückliche Bestätigung im Add-on; das Update selbst patcht den Skin nicht.

| Test | Kurzer Ablauf und PASS-Bedingung | Initial | PASS | FAIL | ÜBERSPRINGEN |
|---|---|---|---|---|---|
| HOME60-01 | BINGIE .60-Adapter in der bestehenden Widgetverwaltung prüfen, Diff/Hashes lesen und nur bei eigener Zustimmung übernehmen. Vorhandene Live-Reihe zeigt kleine Logos; keine erneute Verknüpfung von Filmen/Serien. | NOT_TESTED | ☐ | ☐ | ☐ |
| HOME60-02 | Gesamte konfigurierte Startgruppe nach rechts bis zum letzten Sender durchlaufen, Reihenfolge vergleichen. Fokus startet keinen Stream. Jetzt/Danach, Beschreibung, Fortschritt und richtiges Bild wechseln passend. | NOT_TESTED | ☐ | ☐ | ☐ |
| HOME60-03 | Sender ohne EPG bzw. ohne Bild fokussieren: Sender bleibt sichtbar, verständlicher fehlender EPG-/neutraler Bildzustand, keine falsche vorherige Sendung und kein Dauerspinner. Schnelle Fokuswechsel bleiben bedienbar. | NOT_TESTED | ☐ | ☐ | ☐ |
| TMDB60-01 | Eigenen API Read Access Token unter Medien & Wiedergabe lokal eintragen. „TMDB-Verbindung testen“ unter EPG ausführen: TMDB_OK oder konkrete Fehlerklasse, niemals Tokenanzeige. Der Test aktiviert keine globalen Optionen. | NOT_TESTED | ☐ | ☐ | ☐ |
| TMDB60-02 | Falls gewünscht beide bestehenden TMDB-Schalter auf Box B privat aktivieren. Bereits geladenes EPG verwenden und Hintergrundvorbereitung abwarten. Eindeutigen Film bzw. Folge mit Jahr/Staffel/Folge in EPG-Detail und Home vergleichen: dasselbe richtige Bild, Provider-/XMLTV-Bild bleibt vorrangig. Keine erfundenen Treffer. | NOT_TESTED | ☐ | ☐ | ☐ |
| REG60-01 | Je zehn unterschiedliche Filme und Serien mit korrekten Providerpostern durchscrollen und passende Details öffnen. Automatische Aktualisierung und vorhandene Quellen bleiben nutzbar; keine TMDB-Abhängigkeit für diese Reihen. | NOT_TESTED | ☐ | ☐ | ☐ |
| REG60-02 | Genau einmal Live-TV bewusst mit OK starten und mit Zurück nach bestehender Overlay-Regel verlassen. .42-Einstellung beibehalten. Nach bestätigtem Stopp richtige bedienbare Ansicht, kein Doppelstart. Nur bei PASS optional weitere fünf Zyklen sowie Film-/Serien-Back und Resume. | NOT_TESTED | ☐ | ☐ | ☐ |
| REG60-03 | Kodi normal neu starten: Portale, Startgruppe/-sender, vorhandene Widgets, EPG, Cover und lokal bestätigte TMDB-Bilder erhalten. EPG-Aktualisierung aus .59 bleibt erreichbar. | NOT_TESTED | ☐ | ☐ | ☐ |

Je Test genau einen späteren Zustand und eine kurze Beobachtung eintragen. ÜBERSPRINGEN ist kein PASS. Host-Screenshots, erfolgreiche Authentifizierung oder PUBLISHED ersetzen keine tatsächliche Box-B-Darstellung. Ein reales Token-/HTTP-Problem kann ohne Bilderfolge isoliert getestet werden; keine umfangreichen weiteren Tests vor fertigem Paket verlangen.
