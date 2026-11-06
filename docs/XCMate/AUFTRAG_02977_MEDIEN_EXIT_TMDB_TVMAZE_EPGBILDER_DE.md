# XCMate 0.1.29.77 – Verbindlicher Änderungsauftrag
Datum: 06.11.2026 · Status: **AUFTRAG ERFASST / NOCH NICHT IMPLEMENTIERT**

**Masterticket:** [GitHub #380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380)

## Nutzerentscheidung

Die Installationsroutine **GS Media Installer 0.5.26 ist erfolgreich durchgelaufen und wird eingefroren**. Alle Folgearbeiten betreffen ausschließlich `plugin.video.xtreammate` (XCMate), kumulativ auf Source-Version `0.1.29.76`. Kodi-Profile, vorhandene Sender-/EPG-/Widget-Einstellungen, SkinShortcuts, Space Blue und der bestehende TMDB-Read-Access-Token sind vollständig zu schützen.

Der Nutzer meldet am 06.11.2026 erneut einen Freeze beim **Verlassen einer Serie** (neuer Fall; kein zugehöriger Log). Außerdem fehlen weiterhin real sichtbare EPG-Bilder und der vergrößerte BINGIE-Hero ist nicht zufriedenstellend eingebunden. Drei separate Freischaltungen für Bildquellen werden ausdrücklich nicht akzeptiert.

## P0-1 – Serielles/Film-/Live-Playback sicher verlassen

**IST:** In der älteren Android-.74-Logserie [#368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368) ist ein spezifischer Live-TV-Back-Stop dokumentiert: `USER_BACK` → `NATIVE_STOP_POSTED` → `STOP_TIMEOUT` / `NATIVE_QUEUE_UNRETURNED`, native Stop-Barriere ohne ACK. **Der nun gemeldete Serien-Hänger darf nicht ohne Logs mit diesem Live-Fall gleichgesetzt werden.**

**SOLL:** Für `series`, `movie/vod`, `live` ein konsistenter, sessiongebundener Stop- und Rückkehrvertrag mit genau einem Stop pro Player-Eigentümer. Kodi-Playerzustand, Stop-Intent, native Queue/ACK, OnStop/EOF, Autoplay, OSD, Zurück und Ziel-Fenster getrennt prüfen. Keine Endlosschleife oder blockierende GUI-Wartezeit. Return erst nach bestätigtem Stop; bei nicht quittiertem Stop ein sauber diagnostizierbarer Schutzfall, kein erfundener Erfolg. Wiedereinstieg in vorherigen XCMate-Kontext ohne Verlust von Staffel-/Episoden-Fortschritt. Rückwärtskompatibilität zum .42-Exit-Kompatibilitätsmodus.

**Referenzdateien:** `native_stop41.py` (nur Live), `live_exit.py`, `exit_jobs.py`, `playback_exit.py`, Serien-Autoplay-/Navigator-Routinen. Separate Android-Stop-/Decoder-/AudioSink-Diagnose auf RK3528. Tests: mindestens 20 wiederholte Stop-Rückwege je Medientyp, OSD/Back, Folgeepisode, EOF/Netzstörung, Fremdplayer-Schutz. Keine Roh-URLs/Token/Providerdaten im Log.

## P0-2 – Bildquelle automatisch, aber kontrolliert

**Verbindliche Prioritäten:**
1. Verifiziertes, zur aktuellen EPG-Sendung passendes **XMLTV- bzw. Provider-Bild** automatisch übernehmen (kein TMDB-Token erforderlich).
2. **Spielfilm:** bei bereits importiertem gültigen Token eigene **TMDB**-Bildermittlung; eindeutige Titel-/Jahr- oder sicher nachgewiesene Filmidentität.
3. **Serie/Episode:** eigene TMDB-Suche mit vorhandenem Token und **TVMaze standardmäßig als Serien-/Episoden-Fallback** mit verifizierter Titel-/Episodenidentität. TVMaze nicht als verlässlichen Film-Provider behaupten.
4. Weitere freigegebene Kodi-/lokale Quellen nur bei gültiger Identität. Kein willkürliches oder falsches Artwork bei Sport, News, Talk, mehrdeutigen Titeln und fehlender Episodenidentität.

**Freigabe-UX:** Nutzer hat für seine Installation die automatische Aktivierung bereits ausdrücklich beauftragt. Ein *gültiger* TMDB-Import aktiviert zugleich die verknüpften Lookup-Einstellungen `programme_tmdb46` und `tmdb_research43`; die bereits vorhandene, valide Token-Installation wird per einmaliger autorisierter Migration aktiviert, ohne erneuten Import. Für TVMaze `programme_tvmaze67` nach einmaliger verständlicher Information standardmäßig als Fallback an, eigenständiger Opt-out jederzeit möglich. Ein ausdrücklich manuell vorgenommener Opt-out muss Bestand haben; kein ständiges Reaktivieren beim Start. Fremddienst-Abfragen nur nach zulässiger Nutzerfreigabe, mit klarer Quellenanzeige.

**TMDB-Token-Schutz – striktes P0:** vorhandene Token-Datei und ggf. Legacy-Kodi-Einstellung nicht ändern, löschen, überschreiben, umbenennen, zurücksetzen oder erneut hochladen. Read-only Gültigkeits-/Fingerprint-Prüfung vor/nach dem Update. Token niemals in GitHub, in Diagnosen oder in Kodi-Logs ausgeben, keine Token-Bytes aus Box in CI kopieren. Ungültiger Token → eindeutiger Status, keine unberechtigten Anfragen. Kodi-Profile und Geräte-Konfigurationen nicht neu initialisieren.

**Warum heute defekt:** `programme_settings68.py` verwendet Default `False` für beide TMDB-Flags sowie für TVMaze. `tmdb_access61.imported()` aktiviert die TMDB-Lookups bislang nur für Importvariante `choice==6`. `programme_art46.enqueue()` kann ohne TMDB-Freigabe und ohne direkte XMLTV-/Providerbild-URL frühzeitig `NO_IMAGE` für 6 Stunden setzen, auch wenn andere autorisierte Fallbacks existieren. Andere URL-/Renderer-Pfade können unabhängig blockieren: `programme_urls55`, `programme_image69`, `programme_requests68`, `hero_epg63`. Diese Ursachen dürfen nicht durch blindes globales Allowlisting oder falsche Bilder überspielt werden.

## P0-3 – Bilder wirklich anzeigen und BINGIE-Startseite reparieren

- EPG-Quelle → Event-Fakten → Artwork-Matching → sicherer Bildhost/HTTPS/Redirect/Content-Type → lokaler Cache/URL-Lease → Event-ID/Profil/Gültigkeit → **tatsächlich sichtbare Textur** in Mini-EPG, Groß-EPG-Details und BINGIE-Hero nachweisen.
- Ein einziges Event teilt sich dieselbe gültige Bildreferenz. Fehlende Bildquelle transparent mit Sender-Fallback statt falschem Filmbild. Negative Caches nach Änderung einer Bildfreigabe gezielt revalidieren, positives Artwork erhalten.
- **Vergrößerter stabiler Hero**, vollflächiges laufendes Sendungsbild, Senderlogo und feste Jetzt-/Danach-/Fortschritts-Informationen. Darunter genau eine kompakte horizontale aktive Sender-/Coverleiste. Fokusrahmen exakt an der fokussierten Kachel, nie nach unten versetzt oder in andere Zeilen ragend; kein Schrumpfen/Abschneiden beim Scrollen.
- Priorität: lokales EPG + Startgruppe → Logos/Now/Next/Hero/sichtbare fünf Sender → Filme → Serien → restliches Artwork. Kein HTTP oder schweres SQL im Kodi-UI-Thread. Native Home-Bindings und echter Texture-Nachweis auf Kodi 21.3/Android, nicht nur synthetische Hostdaten.
- Ein **einziger verständlicher Bildquellenstatus** in den XCMate-EPG-Einstellungen mit Quelle, Token vorhanden/gültig, aktiviert/deaktiviert, Matching, Fetch, Cache, Skin-Bindings – Statuscodes ohne URL oder Geheimnisse. Keine drei separat zu betätigenden Schalter.

## Test- und Veröffentlichungs-Gates

1. Bei bestehendem gültigem TMDB-Token aus früherem Import: vor/nach Update identischer tokenfreier Fingerprint und Gültigkeitsstatus; TMDB-Bildsuche aktiviert ohne neues Importieren. Alle Importvarianten und expliziter Opt-out getestet.
2. TVMaze bei eindeutiger Serie aktiv und als Fallback funktional; gültiges XMLTV-/Providerbild funktioniert auch ohne TMDB; Film-Suche über TMDB; unklare Episoden/News liefern keine falschen Bilder.
3. Nach vorherigem `NO_IMAGE` kontrollierte neue Suche bei Freigabe, korrekte Event-ID, Quelle und lokale Persistenz; gleiches echtes Bild im EPG und Hero. Hosttests + sichtbarer Android-Screenshotnachweis.
4. Serien-Exit nach Kodi-Stop/ACK zuverlässig zurück (20× auf Android), Filme und Live ebenso. Bei fehlendem ACK genaues, nicht blockierendes Fehlerverhalten belegt.
5. Keine Datenlöschung, kein Zurücksetzen, kein Downgrade; XCMate **0.1.29.77** zunächst nur **GS Media Pilot**, regulärer Kanal erst nach ausdrücklich bestandener Geräteabnahme und Freigabe. **Installer 0.5.26 bleibt eingefroren.**
6. Ohne bestätigte Android-Tests **ANDROID_NOT_TESTED / ANDROID_FAIL**, keine falsche PASS-Meldung. Build/CI/ZIP-SHA/Quellvergleich dokumentieren.

## Codex-Kurzstart

> GitHub-Repository `artattakk-creator/kodi-noodleprivate`, Issue #380 und diese Datei lesen. Die kumulative XCMate-Version 0.1.29.77 auf .76 bauen. Priorität: Serien-Exit-P0, automatische EPG-Bildquellen mit unverändertem TMDB-Token und TVMaze-Fallback, echter BINGIE-Hero-/Fokus-/Artwork-Nachweis. Installer 0.5.26 NICHT ändern. Änderungen samt Regressionen, Privatdatenschutz, CI und Geräteabnahme dokumentieren. Pilot-Paket erst nach Hosttests bereitstellen; regulären Kanal nicht vor Gerätefreigabe verändern.

### Referenzen
- [Master-Issue #380](https://github.com/artattakk-creator/kodi-noodleprivate/issues/380)
- [Event-Bilder #366](https://github.com/artattakk-creator/kodi-noodleprivate/issues/366)
- [Hero/Fokus/EPG #367](https://github.com/artattakk-creator/kodi-noodleprivate/issues/367)
- [Live-TV-Stop/ACK #368](https://github.com/artattakk-creator/kodi-noodleprivate/issues/368)
- [XCMate .76 PR #370](https://github.com/artattakk-creator/kodi-noodleprivate/pull/370)
