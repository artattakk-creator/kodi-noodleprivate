# Pilot-Veröffentlichung XCMate 0.1.29.71 und GS Media Setup 0.5.20 — #354

## Kanal und Umfang

Die Veröffentlichung erfolgt im **bestehenden** `repository.gsmedia.pilot` **1.9.12**.
Repository-ID, Repository-ZIP und Kodi-Kanaladressen bleiben unverändert.
Quellbasis ist der Merge von PR #353, Commit
`f0a1bb40050e89e0220687722273e7cc859b9b5b`.

- [Tatsächlicher Kodi-Index](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/addons.xml)
- [Index-MD5](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/addons.xml.md5)
- [XCMate 0.1.29.71 ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.71.zip)
- [GS Media Setup 0.5.20 ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.20.zip)

| Paket | SHA256 | Bytes |
|---|---|---:|
| XCMate 0.1.29.71 | `ebebf3c9cdb00b8730da436bfb7bd8909a8a5cdfd23ee36b61afa99f775a9a4d` | 3310874 |
| GS Media Setup 0.5.20 | `568a76b67d80d846ea09176d0ea1b9f6b6fed1fd86c2ace79ca865b4a8ccadbd` | 101380 |

Beide Pakete sind bytegleich zu den bereits getesteten PR-#353-Paketen.
Setup wurde aus dem unveränderten, SHA256-gepinnten .5.19-Paket gebaut.
Sein historischer Anzeigename enthält weiterhin „v0.5.19“; maßgeblich ist
die Paketversion **0.5.20** in Kodis Add-on-Informationen. Eine reine kosmetische
Umbenennung wurde zugunsten der geprüften identischen Paketbytes vermieden.

Der Index enthält weiterhin **54** Add-ons. Nur zwei Einträge wechseln die
Version. Die übrigen 52 Einträge und alle bisherigen Paket-ZIPs bleiben
unverändert. Zusätzlich werden die im XCMate-Paket referenzierten Index-Bilder
bereitgestellt. Kein Installerlauf, keine Skinänderung und keine Benutzer- oder
Geräteinstallation sind Teil dieser Veröffentlichung.

## Kodi: beide vorhandenen Add-ons regulär aktualisieren

1. Kodi → **Add-ons → Meine Add-ons → Add-on-Repositories**.
2. Das bereits installierte **xcMate Repository / GS Media Pilot 1.9.12**
   markieren → Kontextmenü → **Auf Aktualisierungen prüfen**. Je nach Oberfläche
   ist dieser Befehl im linken Seitenmenü des Add-on-Browsers erreichbar.
3. **Verfügbare Aktualisierungen** öffnen und gezielt **XCMate 0.1.29.71**
   und **GS Media Setup 0.5.20** aktualisieren. Alternativ die jeweilige
   Add-on-Information → **Aktualisieren / Versionen** öffnen und die Version
   aus dem bestehenden Pilot-Repository auswählen.
4. XCMate befindet sich unter Video-Add-ons, GS Media Setup unter Programm-Add-ons.
   **Setup nicht mit „Öffnen/Ausführen“ starten und keine Installation aller
   Komponenten auswählen.** Die bereits installierten 48 Komponenten bleiben bestehen.
5. In beiden Add-on-Informationen die installierte Version kontrollieren.
   Anschließend Kodi normal beenden und wieder starten. Portale, Startgruppe,
   EPG-/TMDB-Konfiguration und BINGIE-Widgets prüfen.

Erscheint noch die alte Version, die Prüfung im **bestehenden** Repository nach
kurzer Wartezeit wiederholen und Kodi gegebenenfalls normal neu starten.
Kein neues Repository installieren, keine Datenbank und keinen Cache löschen.
Globale Kodi-/Skin-Einstellungen oder Update-Ursprungsregeln nicht verändern.

## Prüfungen und Grenzen

- Produktprüfung PR #353: **2.904 Hosttests bestanden**,
  [CI 41723976215](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41723976215).
- Zusätzliche Release-Tests: **9 bestanden**. Geprüft werden Index/MD5,
  beide ZIPs/CRC/SHA256/Manifeste/Assets, Versionsreihenfolge, alle bisherigen
  Pakete, unveränderte 52 Fremdeinträge und der begrenzte Setup-Delta.
- `python tools/publish_pilot354.py --public` prüft nach dem Push die echten
  URLs ohne Zugangsdaten und ohne abweichende Cache-Busting-URLs.
- `python tools/run_pilot354_native.py --report-dir /tmp/pilot354-native`
  prüft Kodis echte Update-Erkennung mit `UpdateAddonRepos` und der nativen
  Add-on-Browser-Liste `addons://outdated/` (IDs und Versionen) in einem
  isolierten Linux-Kodi-21-Profil. Die alten
  .70/.5.19-Installationen sind reine Metadaten-Fixtures ohne ausführbare
  Produktdienste oder Installer. Dies ist keine Android-Geräteabnahme.
- Workflow: **Verify existing Pilot XCMate 71 and Setup 520 release**.
  Artefakt: `pilot354-release-verification`.
- Veröffentlichung/öffentliche Abrufprüfung/native Erkennung werden erst nach
  tatsächlicher Durchführung mit Commit und Action-Link in Issue #354 bestätigt.
- Beide Android-Updates und Funktionsabnahme auf TX60Pro: **NOT_TESTED**.

Die bestehenden Produktberichte und Android-Schritte aus
`ANDROID_ABNAHME_02971_ISSUE352_DE.md` gelten weiter.
