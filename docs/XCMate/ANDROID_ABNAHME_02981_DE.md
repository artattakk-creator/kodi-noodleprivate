# Android-Abnahme XCMate 0.1.29.81

Alle Gates: **ANDROID_NOT_TESTED**. Nur echtes Gerät darf PASS/FAIL setzen.
Kodi 21.2 und 21.3 getrennt erfassen: Gerät, Architektur, Version, Uhrzeit und jeweils Ergebnis. Box A nicht verändern. Keine Neuinstallation, kein Profil-/Cache-Reset. .81 nur als manuelles Update aus dem freigegebenen Test-ZIP installieren; noch kein regulärer/Pilot/NeoDark3-Release.

Vorher SHA256 der ZIP gegen die beiliegende Datei prüfen. Kodi → Add-ons → Aus ZIP-Datei installieren → vorhandenes .81-Paket. Danach Version und Update-Hinweise kontrollieren; bestehende Provider-/TMDB-/EPG-/Artwork-Einstellungen unverändert lassen. Keine privaten Logs veröffentlichen.

| Gate | Ausführbarer Ablauf | Erwartung / Ergebnis |
| --- | --- | --- |
| A1 | Startseite mit 24 vorhandenen Filmen öffnen; ohne Down/Fokus drei Hintergrundzyklen einschließlich Katalogaktualisierung abwarten, etwa 15 Minuten. | Bereits sichtbare Providerposter bleiben erhalten, kein Play-Icon-Wechsel; **ANDROID_NOT_TESTED**. |
| A2 | Startgruppe mit 88 Sendern, mehrfach seitwärts, danach Filme/Serien und zurück; während EPG-/Bildsuche und Idle beobachten. | Alle vorhandenen Logos bleiben dem richtigen Sender zugeordnet; 88 Objekte allein sind kein Pixelnachweis; **ANDROID_NOT_TESTED**. |
| A3 | Croods/VOX bei unveränderter Sendung zehn Minuten beobachten, Katalogjob parallel; danach echten Eventwechsel abwarten. | Kein TMDB/XMLTV-Flattern oder Schwarzbild; neue Sendung erhält eigenes Bild, Quelle korrekt; **ANDROID_NOT_TESTED**. |
| A4 | Modern Family, Yuna & Stitch, Mockingjay (1), Harry Potter und der Feuerkelch, Croods aufrufen, Hero und EPG-Details prüfen. | Passender Request/Cachetreffer oder verständlicher Skip. Nur tatsächliche API-/Matching- und sichtbare Texturbelege zählen. Token bleibt unverändert; **ANDROID_NOT_TESTED**. |
| A5 | Live, Film und Serie mit Landscape sowie Film/Serie nur mit Poster öffnen, 720p und 1080p prüfen. | Großer proportionaler Hero, vollständiges Portrait, transparente rechte Infos, beide Medienreihen ohne Fokus sichtbar, enger Abstand, blauer exakt passender Rahmen; **ANDROID_NOT_TESTED**. |
| A6 | Automatischen Scan und „Gesamten Katalog aktualisieren“ ausführen; optional Statuszeile ein-/ausschalten, Abschlussbericht lesen. | Standard still, keine Gruppenpopups; echte neue/geänderte/unveränderte Werte und API-/Vollsync-Zeiten; Cover/Logos unverändert; **ANDROID_NOT_TESTED**. |
| A7 | Erst Live starten/Back, danach Film aus Detailansicht starten/Back, danach Serie mit Autoplay/Resume; große und kleine EPG-Details öffnen/schließen. | Je ein Playerstart, Stop-ACK und bedienbare Rückkehr; Fortschritt, Favoriten und persönliche Widgets einschließlich „Neu im Kino“ erhalten; **ANDROID_NOT_TESTED**. |
| A8 | Kodi regulär neu starten, anschließend kurz offline schalten und bereits geprüfte Bilder ansehen; wieder online, nächstes EPG-Event öffnen. | Lokale Bilder bleiben; keine fremde Edition/Kontoquelle, keine endlosen Retry-Jobs; **ANDROID_NOT_TESTED**. |
| A9 | Paketversion, SHA256, Update-Hinweise, Einstellungen und alle persönlichen Widgets prüfen; anonymisierten Bericht mit Uhrzeiten erstellen. | .81 kumulativ; keine Konfigurationsverluste. CI/Host und Android getrennt ausweisen; **ANDROID_NOT_TESTED**. |

Keine absichtliche Beschädigung privater Bilddateien, Token oder Datenbanken auf der Box. Korruptions-/Konto-/Paralleltests erfolgen ausschließlich mit isolierten Hostfixtures.

## Reproduktion am Host

```sh
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p '*02981.py' -v
python tools/run_kodi_home81_contract.py --report-dir /tmp/native81-720 --resolution 1280x720
python tools/run_kodi_home81_contract.py --report-dir /tmp/native81-1080 --resolution 1920x1080
python tools/run_kodi_media77_contract.py --report-dir /tmp/native81-media
python tools/package_xcmate71.py /tmp/package81
```

Native Fixtures verwenden ein wegwerfbares Linux-Kodi-Profil, künstliche Bilder und synthetische H.264/AAC-Dateien. Sie installieren nichts auf Android und verändern keine Box. Abhängigkeiten und gepinnte Skin-Prüfsumme siehe CI `home75-review.yml`. Die zwei nativen Auflösungen lokal nacheinander ausführen.
