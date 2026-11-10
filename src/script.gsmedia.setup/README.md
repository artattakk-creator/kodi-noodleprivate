# GS Media Setup 0.4.0 – Integrationskandidat für ein frisches Kodi 21.3

**Stand: 02.11.2026. Entwicklungsbranch / PR #320, nicht produktiv freigegeben.**
Die Codebasis enthält den von `main` übernommenen XCMate-Stand **0.1.29.70**.
Das separate GS Media Repository 1.8.2 und dieser Wizard liegen weiterhin im
Draft. **Box A und ihre Einstellungen dürfen nicht verändert werden.**

## Verbindliches Zielbild

Auf einer neu installierten Android-/Kodi-21.3-Box soll nach Installation des
GS-Media-Repository-ZIPs ein einzelner geführter Wizard die vollständige
Ersteinrichtung übernehmen. Kodi-eigene Sicherheits-, Fremdquellen- und
Skinwechsel-Dialoge benötigen weiterhin ausdrückliche Benutzerfreigabe.

**Alle elf Pflichtanwendungen** sind im Standardplan enthalten:

1. Titan BINGIE MOD (`skin.titan.bingie.mod`, vorläufig nur 2.2.3)
2. XCMate (`plugin.video.xtreammate`, Mindestversion 0.1.29.70)
3. Cumination (`plugin.video.cumination`)
4. xVAULT (`plugin.video.xvault`)
5. TMDB Helper (`plugin.video.themoviedb.helper`)
6. SlyGuy Trailers (`slyguy.trailers`)
7. YouTube (`plugin.video.youtube`, originale Variante bewusst prüfen)
8. MP3 Streams Echoed (`plugin.audio.m3sr2019`, nicht altes MP3 Streams)
9. SHOUTcast (`plugin.audio.shoutcast`)
10. EZ Maintenance+ (`script.ezmaintenanceplus`; **keine automatische Reinigung**)
11. Caber Toss (`script.cabertoss`)

Rekursive Abhängigkeiten, Original-Repositories, feste Paketversionen,
Lizenzen und SHA256 müssen vor einer Freigabe vollständig geprüft werden.
Eine installierte Add-on-ID allein belegt **keine** freigegebene Herkunft.

## Was der RC tatsächlich implementiert

- Read-only Kodi-JSON-RPC-Inventur, geordneter Abhängigkeitsplan, einzelne
  ausdrücklich bestätigte `InstallAddon`-Aufträge, Status erneut aus Kodi
  auslesen, atomisches lokales Journal, Unterbrechung und manuelle Wiederholung.
- Kein ungeprüfter automatischer Download von Drittanbieter-ZIPs; unbekannte
  Quellen bleiben manuell und der Abschluss bleibt gesperrt.
- BINGIE-2.2.3-Patch für exakt vier per SHA256 verglichene XML-Dateien,
  ursprüngliche BINGIE-Lizenzangaben, privates Backup und Rollback bei Fehler.
  **Vor** dem Skin-Patch prüft der Wizard jetzt auch, ob die vorhandenen
  Skinshortcuts-Dateien konfliktfrei übernommen werden können.
- Hauptmenü Live-TV/XCMate zuerst, darunter in Reihenfolge die drei Widgets
  XCMate Live-TV, XCMate Filme, XCMate Serien; nachfolgend TMDB-, Provider-,
  Musik- und sonstige Menüpunkte aus der historisch belegten Layoutvorlage.
  Konfiguration nur bei frischer Installation, Skinshortcuts-v2-Schema.
- Die Original-xVAULT-Playerdefinition wird für Filme **und** Serien in
  TMDB Helper übernommen, ohne fremde oder vertauschte Player-Einstellungen
  zu überschreiben.
- Einmaliger XCMate-Wizard **erst nach** nachgewiesenem Komplettabschluss,
  Kodi-Neustart und erneut verifizierter Installationsinventur.
  Der Service speichert vor einem eventuellen RunPlugin den One-shot-Marker.
- Journal-Validierung verweigert unzulässige Phasen, Fremd-IDs,
  doppelte Installationsschritte, ungeprüfte Stage-Flags und zusätzliche
  Felder (z. B. Zugangsdaten). Keine privaten Portale/Tokens in GitHub.

## Was ausdrücklich NICHT als fertig gilt

**Blocker A – Paketnachweise:** xVAULT, MP3 Streams Echoed und EZ Maintenance+
sowie weitere externe Pakete brauchen originale, tatsächlich erreichbare
Kodi-kompatible ZIPs, feste SHA256, Lizenz-/Quellfreigabe und einen geprüften
Lieferweg. Das ZIP von GS Media darf nicht unerlaubt Drittanbieter rehosten.
Bekannte Abhängigkeitslisten ersetzen keine vollständige transitive Prüfung.

**Blocker B – BINGIE-Gerätetest:** Original-XML-Hashes des wirklich neu
installierten Titan BINGIE MOD 2.2.3 prüfen; Skinshortcuts 2.x,
Menüstruktur, Navigation, Fokusrahmen, XCMate-Live-Hero und alle drei Widgets
visuell und funktional auf Android testen. BINGIE v3 niemals als v2 behandeln.

**Blocker C – Medien- und Boot-Healthcheck:** Echtes xVAULT-Film- und
Episoden-Playback, Provider/EPG/Artwork, Kodi-Neustart, einmaligen
XCMate-Handoff, unterbrochenen Installationslauf und Wiederaufnahme prüfen.
Dieser Test wurde auf der neuen Android-Box **noch nicht durchgeführt**.

Daher hält `setup_full.py` die Herkunfts-, Abhängigkeits- und
Health-Stufen ausdrücklich auf **unverifiziert**. Die
Abschlussanzeige meldet keine erfolgreiche Vollinstallation, solange die
Quellen- und Gerätetests fehlen. **Kein automatischer XCMate-Wizard.**

## Verbindliche Abnahme auf Testbox B

1. Android-Box mit blankem Kodi 21.3 vorbereiten; Kodi-Profil sichern,
   keine Bestandsdaten und keine alten Skinshortcuts importieren.
2. GS Media Repository 1.8.2 RC und Setup 0.4.0 ausschließlich aus
   dem GitHub-Actions-Testartefakt von PR #320 testweise installieren.
   **Achtung:** Das Repository-Manifest verweist weiterhin auf den
   veröffentlichten `main`-Katalog (der derzeit noch 1.8.1 ist).
   Daher den Setup-Wizard als separate ZIP aus dem RC-Artefakt installieren;
   nicht annehmen, dass Repo 1.8.2 bereits als offizielles Update verfügbar ist.
3. Read-only Inventur und Quellenübersicht zuerst prüfen.
   Jeden Installationsauftrag/Repository-Dialog separat bestätigen.
4. Beim ersten Test nur eindeutig freigegebene Originalquellen verwenden.
   404, Paket-/Lizenz-/Hashabweichung und inkompatible Version müssen
   nachvollziehbar blockieren, nicht übersprungen werden.
5. Kodi-21.3-ARM32-Kernbetrieb, BINGIE-Patch + Sicherung, Live-TV-/Film-/
   Serien-Widgets, xVAULT-Player und konkrete Wiedergabe abnehmen.
6. Kodi-Neustart, Journal-Wiederaufnahme und One-shot-XCMate-Wizard nur
   **nach** erfolgreicher vollständiger Provenienz- und Healthprüfung testen.
7. Fehlgeschlagene Schritte dürfen weder Nutzerdaten zerstören noch
   Installations-Erfolg fingieren. Testbericht mit PASS/FAIL/NOT_TESTED.

## GitHub

- Masteranforderungen: Issue #317
- Vollinstaller-Integrationsbranch: PR #320 (Draft)
- XCMate-EPG/Artwork-Integration: Issue #315, Release .70 über PR #319
- Stand vor Integration: PR #318 (Pilot .3.0)
- Provenienz- und Abhängigkeitsvorarbeiten: PR #312

**Release-Regel:** Kein Merge des GS Media Setup nach `main`, keine
Freigabe für produktive Kodi-Boxen und keine Behauptung einer vollständigen
Ein-Klick-Installation ohne Paket-/Lizenz-/Hash- und reale Android-Abnahme.
