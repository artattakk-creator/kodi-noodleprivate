# XCMate .66 – Android-Abnahme für den Testkandidaten

Alle neuen Gates zunächst ANDROID_NOT_TESTED. Aktuelle installierte Version vor Test prüfen; alte Fotos beweisen keine .65-/ .66-Version. Box A nicht aus der Ferne verändern. Keine Deinstallation, kein Downgrade und kein Profil-, Skin-, EPG-, Artwork- oder Widgetreset. Bestehende Startgruppe, WELT, .42-Stopmodus, Portalpasswörter und manuelle Zuordnungen erhalten.

ZIP nur als normales Add-on-Update installieren. Vorher die konkrete Test-ZIP-SHA256 mit dem PR vergleichen. Erst nach Nutzerfreigabe darf .66 nach main und in das reguläre GS-Media-Repository.

| Gate | Ausführung und echte Erwartung | Status |
|---|---|---|
| A66-01 | Version .66/Kodi/Gerät und Datenbestand vor/nach normalem Update protokollieren; Erfolgspopup zeigt Version/Änderungen | ANDROID_NOT_TESTED |
| A66-02 | Vorhandenen Zugang ohne neue Eingabe nach Kodi-Neustart testen; nur echte HTTPS-Antwort zählt als TMDB_OK. Keinen neuen Import-Marathon | ANDROID_NOT_TESTED |
| A66-03 | Nitro/MacGyver-Detail: Text, präziser Bildstatus und echte Bildanzeige bei nachgewiesenem eindeutigem Treffer. Serienbild ausdrücklich als Serienfallback kennzeichnen | ANDROID_NOT_TESTED |
| A66-04 | Home desselben Events: gleiches Now/Next, passende Bilddatei/Attribution oder ehrlicher NO_MATCH_AMBIGUOUS/NO_ARTWORK-Fallback; keine Fremdsenderbilder | ANDROID_NOT_TESTED |
| A66-05 | 88-Sender-Startgruppe kalt öffnen; nie besuchten Sender mit nachgewiesenem XMLTV-Event prüfen, ohne vorheriges Zappen. EPG-Manager → Menütaste: lokale Senderabdeckung | ANDROID_NOT_TESTED |
| A66-06 | Provider-XMLTV, EPGShare und tatsächlich konfigurierte Calamura/Kaimandura-Quelle getrennt: Mapping, Versuch/Erfolg, echte Abdeckung, manuell fälliger Refresh, Ereigniskorrektur und Quellenausfall | ANDROID_NOT_TESTED |
| A66-07 | Offline-Kaltstart: gültiges gespeichertes EPG bleibt nutzbar, kein Leeren/Neuimport am Fokus | ANDROID_NOT_TESTED |
| A66-08 | Home → Live → Detail → Home: konsistente Identität/Revision; kalte und warme DB-/GUI-Zeit separat messen. Warmes Now/Next-Ziel ≤1 s; Playerstart/Zurück unverändert | ANDROID_NOT_TESTED |
| A66-09 | HOPE/Coco/Lupin/Loki, TMDB-Helper/XCMate/Musik: erste, zweite, letzte Kachel; vertikal/horizontal, schneller Wechsel, fehlende Fanart, Langtitel. Genau ein sichtbarer Rahmen um die aktive Kachel | ANDROID_NOT_TESTED |
| A66-10 | 142×72-Live-Button bleibt korrekt; Hero-Text endet vor Überschrift/Poster. 720p/1080p/4K/Overscan/Fontwechsel prüfen. Bekannten Skinpatch nur nach Vorschau und ausdrücklichem Ja anwenden; Nein muss unverändert bleiben; Rücknahme prüfen | ANDROID_NOT_TESTED |
| A66-11 | Aktivierte Film-/Serienkategorien inklusive tatsächlicher Adult-Zone-ID, >100/>1000 Paging, Titel-/Genre-/globale Suche, neue Gruppe, gezielter Retry/Cancel. Quelle 0, deaktiviert, CACHED und INDEX_INCOMPLETE unterscheiden; echte Providercounts nicht erfinden | ANDROID_NOT_TESTED |
| A66-12 | WELT-Start und einmal Zurück, Film/Serie-Back, Staffel-Autoplay/Resume, Portale/Passwörter, Favoriten, EPG/Mappings, Bilder und bestehende Widgetlinks erhalten. Box A unangetastet | ANDROID_NOT_TESTED |

## Belege

Vorher/nachher Screenshot mit sichtbarem Fokus und Hero für die fünf Zustände aus #300. Gerät/Kodi/Add-on-/Skinversion und Test-ID notieren. Native Linux-Bilder sind synthetisch und ersetzen diese Fotos nicht.

TMDB_OK ist kein TMDB_ART_OK. Ohne unabhängigen Identitäts- und Dateinachweis kein Bild-PASS; MacGyver muss nicht zwingend ein eindeutiges Episodenbild besitzen. Ohne Quelle ehrliche Lücke statt erfundener Programme.

Keine Token, privaten Pfade, Provider-/SMB-Adressen, echten Kataloglisten oder Rohlogs öffentlich posten. Feste Stufen/Subcodes, anonymisierte Zuordnung und Zählwerte genügen. Zeitangaben mit Gerätezeitzone dokumentieren.
