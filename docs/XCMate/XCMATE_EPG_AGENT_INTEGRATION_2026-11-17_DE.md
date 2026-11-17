# XCMate EPG Agent – vollständig in XCMate integrierte Bedienung

**Status: Entwurf, nicht implementiert** · 17.11.2026 · Issue #485

## Verbindliche Produktentscheidung

Der Dienst und die sichtbare Funktion heißen **XCMate EPG Agent**. Es ist **kein separat zu installierendes Kodi-Add-on** und kein manuell zu bedienender Cloudservice. Das XCMate-Add-on integriert den Zugang unter `Einstellungen → EPG → XCMate EPG Agent` mit einer zentralen Option:

- **„XCMate EPG Agent aktivieren“** – AUS ab Werk; EIN nach expliziter Nutzerwahl.
- Funktion bei EIN: den automatisch täglich serverseitig zusammengeführten EPG samt vorhandenen Sendungsbildern und Senderlogos als **eine** bevorzugte externe XMLTV-Quelle in XCMate integrieren. **Xtream-/Anbieter-EPG als lokale Basis und Fallback immer aktiv lassen**, auch wenn Agent deaktiviert oder offline ist.
- Wenn die allgemeine Bildsuche aus Datenschutz-/Consent-Gründen ausdrücklich AUS ist, darf der Agent diese Einstellung **nicht still überschreiben**. Die EPG-Sendungen werden dann ohne Artwork dargestellt; im Einstellungsbildschirm klar informieren.
- Bei AUS keine neue Agent-XMLTV laden und keinen serverseitigen Client-spezifischen Job auslösen; lokales EPG, manuelle Zuordnungen, Provider-Einträge, Benutzerprofil, Senderlogos, Tokens und andere eingerichtete Quellen **nicht löschen**.

## Systemaufbau

1. **Zentraler Backend-Agent:** Ein 24h-Scheduler verarbeitet autorisierte EPGShare01-DE/AT, Kaimandura und später weitere zugelassene XMLTV-Feeds. Pro Quelle HTTP-Validatoren `ETag`/`Last-Modified`; bei Bedarf sichere limitierte Hashprüfung. Nur geänderte Programme neu mergen und neu mit Artwork versehen. Persistent gespeicherte letzte gültige Datenbasis; bei Quellenfehler LastGood statt Leerdatei.
2. **TMDB-API serverseitig:** Für `api.themoviedb.org` das bestehende GitHub-Actions-Secret `TMDB_READ_ACCESS_TOKEN` über Bearer-Header nutzen. Der von #449 geplante Installer-Import des persönlichen TMDB-Tokens ist eine **separate** Funktion für optionale lokale Client-Nachschläge, noch **nicht fertig**. **Nie** den Token in XMLTV, Query-URL, Kodi-Logs, ZIP, GitHub-Artifact oder Statusantwort schreiben. Bildlinks als HTTPS zur offiziellen TMDB-Bild-CDN, mit Host-/Pfad- und Lizenzprüfung; sichere XMLTV-`<icon>`-Fallbacks.
3. **Kanäle/IDs:** Private Sicherung vom 16.11.2026 enthielt laut abgeschlossener Inventur 2520 Livestreams, 519 mit `epg_channel_id`; in der vom 12.11. 2862/551. Abgleich nur anhand beweisbarer Kombination aus Provider-Kanal-ID, normalisiertem Namen, Feed-ID und Quelle. Provider-IDs sind **nicht** automatisch identische EPGShare/Kaimandura-IDs. Ambige Treffer: kein stilles Mapping; Review. Private Geräte-/Portal-IDs nicht in öffentliches Gesamt-XMLTV oder GitHub aufnehmen. Je Gerät/Portal unterschiedliche ID-Abbildung lokal im Client oder in einer geschützten individuellen Konfiguration, nicht über einen globalen öffentlichen EPG-Identifier.
4. **XMLTV:** Output `xcmate-epg.xml.gz`, `xcmate-epg.xml.gz.sha256` und eine sichere manifest-/status-Datei mit Datenversion, Zeitfenster, Programmen, Quellenstatus und Aktualisierungszeit; öffentliches Hosting erst nach Lizenz- und Quellenweitergaberechteprüfung. Atomares Publizieren nur nach GZIP/XMLTV/IDs/Zeiten/Artwork-URL/Geheimnis-Prüfungen; ältere gültige Version als Fallback.
5. **Kodi-Integration:** Bei EIN nur einen **stabilen** HTTPS-Endpunkt und dessen Manifest/ETag prüfen; wenn unverändert, keine erneute XMLTV herunterladen, keinen großen XMLTV-Import anstoßen. Bei Änderung herunterladen, ZIP-/GZIP-/Hash-/Größen-/Strukturprüfung, atomare Hintergrundaufnahme in bestehende EPG-Pipeline und per Quelle/Revision korrekte UI-Aktualisierung. Kein synchroner Netz-/SQLite-Call auf GUI-Thread; kein `settings.xml`-Rewrite beim bloßen Öffnen des Menüs; keine erzwungenen 1–6 GiB Artwork-Reserven.
6. **Robuste Fehlerbehandlung:** Offline, EPG-Server 5xx, ungültige XMLTV, unpassende IDs, TMDB 401/403/429/Timeout führen zu verständlichem Status und Provider-/LastGood-Fallback. Keine globale Deaktivierung aller EPG-Quellen, kein Crash, keine Datenlöschung.

## Vorgesehene XCMate-Menüoberfläche

```text
Einstellungen > EPG > XCMate EPG Agent

[ ] XCMate EPG Agent aktivieren
    Automatischer Gesamt-EPG aus EPGShare01, Kaimandura und weiteren Quellen.
    Verfügbare Bilder, Senderlogos und Sendungsdetails werden ergänzt.
    Anbieter-EPG bleibt immer als Rückfallebene aktiv.

Status: Deaktiviert / Aktualisierung läuft / Aktuell / Quelle ausgefallen / Fehler
Letzte erfolgreiche Aktualisierung: [Zeitpunkt]
Nächste Prüfung: [Zeitpunkt]
Quellen: [Zahl], Sender zugeordnet: [Zahl], Sendungen: [Zahl]
Artwork: [Treffer/Fehler/aus durch Bildfreigabe]
[Jetzt auf Aktualisierung prüfen] [Diagnose anzeigen]
```

„Jetzt auf Aktualisierung prüfen“ prüft die zentrale Datenversion, erzwingt keinen teuren globalen TMDB-/XMLTV-Neuaufbau. Die Anzeige muss mit IR-Fernbedienung in BINGIE MOD und Kodi-Standardskin lesbar/fokussierbar sein. Jeder Status muss source-qualified und ohne Portal-/TMDB-Geheimwerte bleiben.

## Test-/Abnahme-Gates

- Einmal EIN → einmalige sichere Erstladung, eindeutige UI-Meldung, Provider-EPG weiterhin da; Neustart behält Wahl, ohne EPG-Vollreimport bei gleichem ETag.
- 24h-Backendlauf bei unveränderten Quellen → gleiche SHA/Version, kein Artwork-API-Requery, keine Kodi-Neuladung.
- Eine Quelle geändert → nur betroffene Programme neu berechnet, finale XMLTV atomar, Kodi übernimmt nach Statusprüfung.
- Eine Quelle ausgefallen → vorhandene Programme/LastGood bleiben, kein leeres Live-EPG und kein `Invalid XMLTV` wegen Teilfehler.
- Bei AUS: kein Agent-Fetch, keine Änderung an manuellem EPG/Portal oder fremden EPG-Quellen.
- Kodi-Einstellungen für explizites Bild-Opt-out respektieren; nach EIN echte Bildtexturen im Hero, Mini- und Groß-EPG sowie Details im Live-Gerätetest, nicht nur erfolgreiche URL-Freigaben.
- Logo-URL-Matching nur für bestätigte passende Kanal-IDs; Quelle und Nachweis für unsichere Aliasse.
- Zwei sichere EPG-Quellen mit identischen Kanal-IDs dürfen keine Quellkollisionen hervorrufen (#474).
- 720p/1080p Kodi-Linux-Tests und **separat** RK3528/Android-21.3-Geräteabnahme. Agent allein behebt nicht die weiterhin offenen Bild-/EPG-/Kodi-Absturzprobleme aus #468/#482/#452.

## Änderungs- und Release-Grenze

Nur Entwurf und isolierte Codex-Folgearbeit. Keine automatische Installation, kein Scheduler-Lauf, keine neue Kodi-Version, kein Merge nach Main, keine Veröffentlichung von XMLTV oder Benutzer-Daten ohne erneute Freigabe. Weiterverarbeitungsrechte der Feeds/Artwork und künftiger Hosting-Endpunkt vor Veröffentlichung prüfen.

**Codex-Hauptmodell:** GPT-6.1 Sol / Hoch für Architektur und sicherheitskritische Aggregator-/Kodi-Integration. Nach Aufteilung der Parser, Feed-Cache und UI-Tests einzelne Arbeitsagenten auf Mittel.
