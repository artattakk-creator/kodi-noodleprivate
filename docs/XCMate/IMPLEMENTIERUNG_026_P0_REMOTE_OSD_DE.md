# XCMate 0.1.26 – P0-Testkandidat: Links und drei TV-Bedienebenen

> **RELEASE-STATUS 19.10.2026 – VERBINDLICH:** **XCMate 0.1.26 ist im regulären GS Media Kodi Repository veröffentlicht.** [PR #22](https://github.com/artattakk-creator/kodi-noodleprivate/pull/22) geprüft/übernommen, Merge `cfbe1207fc344c77fbe2042b07f10a2e21fefc03`. [250/250 PR-CI-Tests](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39230063504) erfolgreich; automatischer [Publish-Workflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39240004268) erfolgreich; `addons.xml` und `addon.xml` bestätigen beide **0.1.26**; produktive ZIP hat **262100 Bytes**, veröffentlichte SHA-256 **`4fc88c80202d4c81c07817bb622ea2072cc6ba0c07c01ac45bc420fb809a752a`**, unabhängig gegen reale ZIP überprüft. **Android-TV-Abnahme der 0.1.26 ausstehend**: LEFT aus Live → Senderliste → Gruppen, dreistufiges OSD, Fokus, Pause/Stop/Seek und Inputdiagnose müssen auf dem Gerät geprüft werden. Erste 0.1.25-Infobar sollte laut Freeze unverändert sein, jedoch noch nicht unter 0.1.26 bestätigt. **Nicht enthalten:** 7–10-Tage-EPG, Auto-Tune oder Aufnahmeplanung. Die darunter stehenden Hinweise `Produktiv 0.1.25`, `0.1.26 nur Testkandidat` beschreiben den historischen Branch-Stand und sind nicht mehr aktuell. Der vorgängig dokumentierte Upstream-Lizenzkonflikt aus [Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19) ist weiterhin **ungeklärt**; dieses Release löst die Rechtsfrage nicht.


Stand: 19.10.2026. Basis `main` / `3f5e898`, veröffentlichtes XCMate **0.1.25**.
Branch `fix/xcmate-026-remote-three-level`. Kodi-ID bleibt `plugin.video.xtreammate`.
**0.1.26 ist ausschließlich ein überprüfter Cloud-Testkandidat. Android-Abnahme offen; kein Merge, kein Produktionsupdate.**

**Review:** [Entwurfs-PR #22](https://github.com/artattakk-creator/kodi-noodleprivate/pull/22),
Code-/Paketcommit `902b3dda823c0498ba9e3aea45944a57b0e5d532`.
[GitHub-CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39229913403):
Build, Syntax, Tests und Upload erfolgreich; Produktions-Publish **übersprungen**.
[CI-Testartefakt xcmate-review-22](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39229913403/artifacts/12176890835),
Upload API-bestätigt (252540 Bytes äußeres Artefakt, Aufbewahrung bis 02.11.2026).
Das neu gepackte CI-ZIP hat eine eigene Sidecar-SHA; der unten genannte Hash gilt für das
bytegenau geprüfte eingecheckte Kandidaten-ZIP. Kein lokaler Downloadabgleich des CI-Containers behauptet.

Gelesene Grundlage: vollständige [Android-Übergabe 0.1.25](ANDROID_025_HANDOFF_REMOTE_3LEVEL_EPG_SCHEDULE_DE.md),
[zentraler Status](CODEX_STATUS_CURRENT_DE.md), [UX-Spezifikation](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md),
[0.1.25-Implementierung](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md) sowie Issues
[#20](https://github.com/artattakk-creator/kodi-noodleprivate/issues/20),
[#21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21),
[#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12),
[#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) und
[#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17).
Der eingefügte Nutzerauftrag für 0.1.26 wurde vollständig berücksichtigt.

## Ursache: belegt im Code und noch offen am Gerät

**Reproduziert:** 0.1.25 reicht LEFT an `mapped_action()` weiter. Ein gespeichertes
Profil `left=88, more=1` ordnet die native Action 1 `more` zu: Extras statt Senderliste.
Bei `left=88` ohne andere Belegung für 1 passiert gar nichts. Die Profildatei wird
im bisherigen Callback erneut gelesen. Defekte JSON-Dateien können den Dispatch abbrechen.
Drei neue Regressionen waren vor dem Fix rot: Profilkollision, Profil-Dateizugriff im
Tastenpfad, fehlender Down-Wechsel von Player zu Einstellungen.

**Geräteursache weiterhin nicht abschließend belegt:** Für den gemeldeten Android-Fehler
fehlen Action-ID und das damals gespeicherte Profil. Ein erfolgreicher Modelltest ist
kein Nachweis, dass das konkrete Gerät Action 1 sendet. Deshalb neue Diagnose und 10×-Test.

**Native Listennavigation:** Kodi `21.0-Omega` ruft in
[`Window.cpp::OnAction`](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Window.cpp#L395)
zuerst die native Control-Verarbeitung auf und stellt anschließend den Python-Callback
zu, auch bei erfolgreicher nativer Verarbeitung. Die Selbstnavigation der Liste allein
belegt also kein Verschlucken von LEFT. `WindowDialogMixin` behandelt Öffnen/Schließen
gesondert und gibt normale Actions an diesen Pfad weiter. Die Tests bilden Selbstnavigation,
nativen Listenschritt und danach Python-Dispatch nach. `onInit()` wird nie künstlich aufgerufen.

## Änderungen

- Native LEFT/RIGHT/UP/DOWN, Back, Menü und OK behalten ihre Funktion innerhalb des eigenen
  Dialogs. LEFT hat jetzt wie RIGHT einen expliziten `onAction`-Zweig. Gelernte zusätzliche
  Codes bleiben als Aliase erhalten. Bestehende JSON-Dateien werden nicht migriert/überschrieben.
- Profil einmal beim Navigatorstart laden; ungültiges/unlesbares Profil verwendet im RAM
  die Standards. Der Lerndialog verhindert neue widersprüchliche Zuordnungen nativer Tasten.
  Geänderte Aliase gelten beim nächsten Navigatorstart; kein Dateilesen pro Tastendruck.
- Drei klar getrennte Ebenen. Left/Right bewegt in den unteren Leisten den Fokus; Up/Down
  wechselt die Ebene. Ein Ebenenwechsel führt niemals eine Playeraktion aus.
- Transportfolge: **-10 s · Play/Pause · +30 s · Live-Ende · Stop · Weitere**. Play/Pause
  verwendet `Player.Paused`, tauscht Beschriftung/PNG und bleibt zur Zustandskontrolle offen.
  Der Servicetick aktualisiert extern geänderten Pausezustand ohne normalen Fokuswechsel.
- Seek/Live-Ende nur bei `Player.SeekEnabled` und endlicher Dauer >5 s. Andernfalls sichtbar
  deaktiviert, grau beschriftet und aus der Fokusfolge entfernt; deutlicher Hinweis im Titel.
  Vor Ausführung nochmals prüfen; ±Seek auf 0…Dauer begrenzen. Live-Ende meint das von Kodi
  gemeldete Ende des verfügbaren Puffers, keine erfundene Provider-Timeshift-Fähigkeit.
  Fällt Seek während des Menüs weg, Fokus nur im eigenen obersten Dialog reparieren.
- **Stop bleibt separat.** OK auf Stop und native Stop beenden Wiedergabe und Navigator.
  Up/Back, Down oder das zweite OK stoppen/pausieren nicht. Native SELECT nach `onControl`
  führt weiterhin keine zweite Aktion aus; schnelle eigenständige OK-Eingaben bleiben erhalten.
- **Erste OK-Infobar unverändert:** Control-Definitionen bytegleich zu `main`,
  `_render_info` AST-identisch. Positionen, Farben, Texte, Assets und EPG-Resolver unverändert;
  zusätzlicher Freeze-Test für die zehn Controls. Nur Ebenen-2/3-Assets/Bedienung erweitert.
- Keine Änderungen an globalen Keymaps, BINGIE MOD, Noodle Private, Konten, Favoriten,
  Gruppen-/EPG-Zuordnungen oder produktivem Repositoryindex.

| Zustand | Eingabe | Ergebnis |
| --- | --- | --- |
| Vollbild | OK | Unveränderte Infobar |
| Infobar | OK / Down | Playerleiste, Fokus Play/Pause, keine Aktion |
| Playerleiste | Down | Einstellungen: Ton/Bild/Untertitel/EPG/Einstellungen/Gruppen |
| Einstellungen | Up / Back | Playerleiste, bisherigen Fokus behalten |
| Playerleiste | Up / Back | Infobar |
| Infobar | Up / Back | Vollbild |
| Vollbild | Up / Down | Bisheriges Zapping |
| Vollbild / Infobar | Left | Senderliste |
| Senderliste | Left | Gruppen |
| Gruppen | Right / Back | Senderliste |
| Senderliste | Back / Right | Vollbild |
| Player / Einstellungen | Left / Right | Genau einen aktiven Button weiter |
| Einstellungen | Down | Unterste Ebene behalten; keine Aktion |

**Layoutmodelle mit synthetischen Daten, kein Kodi-Renderer/Android-Screenshot:**
[Infobar](assets/026/infobar-layout.png), [Senderliste](assets/026/channels-layout.png),
[Player](assets/026/controls-layout.png), [Einstellungen](assets/026/settings-layout.png).
Die historischen 0.1.25-Bilder bleiben erhalten.

## Tastendiagnose nach Stop und Neustart

`TV-Fernbedienung: Diagnose` zeigt den letzten Input und einen begrenzten Verlauf von
**64** Events: Quelle (`native`/`control`/`bridge`), Action-ID, Buttoncode, aufgelöster Befehl,
Modus vorher/nachher, Fokus vorher/nachher und angeklickte Control-ID. Auch unbekannte,
abgewiesene und bereits per Control ausgeführte SELECT-Callbacks sind unterscheidbar.
Das aktive gelernte LEFT-Binding wird numerisch mitgeführt.

Kumulative Zähler pro Navigator: `left_received` für behandelte native Action 1,
`left_channels` für Vollbild/Infobar → Sender und `left_groups` für Sender → Gruppen.
Ein neuer Navigator setzt sie zurück. Die letzten 64 Events sind ein Ringpuffer;
bei langen Tests zwischendurch Diagnose sichern, die Zähler bleiben im neuesten Eintrag.
Fehlt eine native Action vollständig, kann Python keinen nicht empfangenen Tastendruck
protokollieren: dann Fokus-/Dialogstatus und unabhängigen Anlerntest vergleichen.

Input-Callbacks schreiben nur Window-Property und RAM-Ringpuffer. Der Dienst sichert ihn
höchstens einmal pro Sekunde, auch nach Wiedergabestopp; Close/Shutdown/Diagnoseansicht
sichern ebenfalls. Atomarer Replace, bei Schreibfehler begrenzte Queue für erneuten Versuch.
Bei hartem Prozessabbruch können die letzten ca. 1 s fehlen. Unbeschreibbares privates
Profil verhindert Persistenz, darf aber Wiedergabe nicht abbrechen.
Nur feste erlaubte Texte, IDs, Zahlen und Zeitstempel: keine URLs, Konten, Namen oder
Exception-Texte. Die bisherigen übrigen Diagnosestufen behalten ihre Begrenzungen.

## Verifikation und Installationsdatei

- **250/250 Tests bestanden**, vor und nach vollständigem isoliertem Repositorybuild,
  Python 3.12.14; keine Fehler/Skips. Davon **39** strikte Overlay-/Lifecycle-Tests.
  Neue Regressionen: 10 Links-Zyklen mit altem Profil, korrupte Profile, kein Profil-I/O,
  drei Ebenen, dynamisches Pause/Play, Seek/Live-Ende/Stop, Capability-Wechsel, Infobar-Freeze,
  Diagnosepersistenz/Ringpuffer/Schreibfehler sowie Erhalt gespeicherter Aliase.
- Bestehende 53.664-Sender-/Paging-, Shared-EPG-, Cache-, HTTP-/GZIP-, Parser- und
  Fremd-Add-on-Isolationstests liefen mit. Zusätzlich **24 HTTP-/Cache-/EPG-Tests** mit
  System-Python/httpx bestanden; Venv prüft urllib. Keine neue echte Feed-Abnahme behauptet.
- Signaturen mit `21.0-Omega` abgeglichen: `ControlList(_itemHeight,_space)`,
  Button/Label/Image, `setEnabled(bool)`, `setLabel`, `setImage`, `setPosition`, `setWidth`,
  `getFocusId`; direkter GUI-Aufrufvertrag und strikte Konstruktoren laufen in der Suite.
  [`Player.h`](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/interfaces/legacy/Player.h)
  bestätigt `getTime()/getTotalTime()/seekTime(double)`;
  [`GUIInfoManager.cpp`](https://github.com/xbmc/xbmc/blob/21.0-Omega/xbmc/GUIInfoManager.cpp)
  bestätigt `Player.Paused` und `Player.SeekEnabled`. Keine echten Kodi-Bindings in der Cloud.
- Isolierter Build: Syntax, alle drei ZIPs, Installerkopien und Index-MD5 erfolgreich.
  Nur neue XCMate-ZIP/SHA in den Branch übernommen. `addons.xml` bleibt **0.1.25**.
- [Installierbare ZIP 0.1.26](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.26.zip):
  **262100 Bytes**, **77 Dateien** vollständig bytegleich mit den Kandidatenquellen,
  ZIP-CRC und Manifest geprüft. SHA-256:
  **`751f47fc0fddd17ac8f576abc3e13dc6455c143ebd00d419b85acf2d765aaa3a`**
  ([Sidecar](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.26.zip.sha256)).
  CI packt einen eigenen Container mit eigener SHA; diese nicht verwechseln.

Reproduzieren: `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -v`.
Builder nur in wegwerfbarer Kopie verwenden, da er auch andere Repositorypakete erzeugt.

## Android-TV-Abnahme – jeder folgende Fall ist OFFEN

1. **Installation/Daten:** Kandidat als ZIP-Update installieren, keine Deinstallation oder
   Profillöschung. Version **0.1.26** und nach vollständigem Kodi-Neustart **service build=26**
   kontrollieren. Globale Fallback-Keymap AUS. Konten, Favoriten, Gruppen, zwei manuelle
   EPG-Zuordnungen und Einstellungen vor/nach dem Update vergleichen.
2. **Freeze:** Erster OK auf demselben echten Sender wie bei 0.1.25: identische kompakte
   Infobar, Logo/JETZT/DANACH/Zeiten/Progress. Kein Kodi-OSD, kein Pause/Stop. Auto-Ausblendung
   und reale Programmzeiten kontrollieren. Ein Missing-State bleibt ehrlich.
3. **LEFT 10/10:** Jeweils aus freiem TV Left → Sender, Left → Gruppen, Right → Sender,
   Back → TV. Zehnmal, Video spielt durch. Zusätzlich Left aus Infobar. Sichtbaren Fokus
   und die tatsächlich vom Gerät gesendeten IDs erfassen. Nach Stop Diagnose sichern;
   `left_channels=10`, `left_groups=10`, `left_received=20` für die reine Zehnerfolge erwarten,
   sofern Action 1 ankommt. Zusätzliche Testeingaben erhöhen die Zähler entsprechend.
4. **Vorhandenes Profil:** Mit bisherigen gelernten Belegungen testen, ohne Zurücksetzen.
   `learned_left_action` und tatsächliche Action vergleichen. Zusätzlicher gelernter LEFT-Code
   bleibt nutzbar; normale Action 1 muss unabhängig davon funktionieren. Profil nicht löschen.
5. **Drei Ebenen:** OK → Info → OK/Down → Player → Down → Einstellungen → Up/Back → Player
   → Up/Back → Info → Up/Back → TV, jeweils zehnmal. Auch mit Fokus auf Stop vor Down/Back:
   kein ungewolltes Stop/Pause. Unten weiteres Down bleibt sicher auf Einstellungen.
6. **Schnelles OK:** Getrennte schnelle OKs: erstes Info, zweites Player, drittes genau einmal
   Play/Pause. Icon/Beschriftung wechseln passend zum echten Bildzustand; nächstes OK setzt fort.
   Long-OK/Menü als Shortcut prüfen. Keine verlorenen schnellen Eingaben oder Doppelaktionen.
7. **Transport:** Nicht seekbarer Stream: drei Funktionen deaktiviert, Fokus überspringt sie,
   Play/Pause und Stop erreichbar. Seekbarer Stream nur wenn tatsächlich vorhanden:
   -10/+30, Puffergrenzen und Live-Ende ohne Schwarzbild prüfen. Live-Ende nicht als
   providerweites Timeshift verkaufen. Capability-Wechsel und externe Pause prüfen.
8. **Settings:** Alle sechs Buttons per Left/Right/OK erreichbar, Fokus deutlich; Ton/Bild/
   Untertitel öffnen native Kodi-Dialoge und kommen sauber zurück. EPG echte Programme oder
   erklärter Missing-State; Gruppen und XCMate-Einstellungen funktionieren. Safe-Area/Lesbarkeit
   auf tatsächlicher Auflösung prüfen; keine kaputten Glyphen oder abgeschnittenen Controls.
9. **Senderliste/Last:** 2.746 und ggf. 53.664 Sender, 100er-Seiten, Page-Up/Down, erste/letzte
   Sender-ID und einfacher Up/Down-Schritt. Warm Left möglichst <500 ms, Infobar <250 ms,
   native Sichtbarkeit separat messen. Offline weiter navigieren; kein Tastendruck-HTTP.
10. **Stop/Diagnose/Isolation:** Separaten Stop drücken, nach Ende Input-/Fokusverlauf lesen,
    danach Kodi neu starten und denselben Zeitverlauf wiederfinden. Fremdes Add-on/VOD und
    BINGIE MOD normal bedienen, kein XCMate-Fokusrest. Danach XCMate erneut starten.

**Wenn LEFT weiter fehlt:** Nach geprüftem Kandidaten gezielt Action/Fokus/Modus-Spur sichern.
`ACTION_UNMAPPED` mit anderer ID → konkreten Gerätecode analysieren; `COMMAND_HANDLED left`
mit Ziel `channels` ohne sichtbare Liste → Renderer/Fokus prüfen; gar kein Input trotz
aktiver Wiedergabe → obersten Dialog und unabhängigen Anlerndialog prüfen. Keine globale Keymap
auf Verdacht installieren. Issues #12/#20 bleiben bis Geräte-PASS offen.

## P1/P2 und regulärer Updateweg

Gemäß Phasenvertrag zuerst dieses kleine P0-Reviewpaket. Langzeit-EPG und Scheduler nicht
in denselben Navigator-Fix mischen. [Separater Analyse-/Umsetzungsplan](PLAN_EPG_LANGZEIT_TIMER_DE.md)
präzisiert die tatsächlichen 48er-/48h-Grenzen, lokalen Index und Hardwareprüfung.
**0.1.26 enthält noch keinen 7/10-Tage-Browser, Auto-Tune oder EPG-Aufnahmescheduler.**

Nach PR/CI und Android-Abnahme nur mit ausdrücklicher Nutzerfreigabe nach `main` übernehmen.
Dann vorhandenen „Publish GS Media Kodi updates“-Workflow abwarten, Manifest/Indexversion,
neue Paket-SHA und Index-MD5 vergleichen. Erst dann normales automatisches GS-Media-Kodi-Update,
Kodi-Neustart und Buildkontrolle. Kein separater GitHub-Release erforderlich. Der PR-Workflow
stellt vorab ZIP+eigene SHA als `xcmate-review-<PR>` bereit; Produktions-Publish ist bei PRs aus.
