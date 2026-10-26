# .42 – Issue-Abnahme, kein automatisches Schließen

| Issue | Tatsächlicher Stand | Geräteabnahme |
|---|---|---|
| #216 | Optionaler Android21.3-Live-Fullscreen-Lifecycle, Singleflight und zwei getrennte Rückkehrbarrieren implementiert;35neue Hosttests, vollständige Suite grün. Kein belegter nativer Decoderfix. | NOT_TESTED / OPEN |
| #203 | Native CloseFile-Blockade anhand Kodi21.3 genauer eingegrenzt; exakter Lock/Stack unbekannt. | OPEN; erst ein Live-Back, bei Freeze abbrechen |
| #215 | Historische .41-QA unverändert: Startsender-TeilPASS, Live-Back FAIL,5/20BLOCKED, übrigeGatesNOT_TESTED. | Historisch FAIL, nicht hochgestuft |
| #213 | .41-Funktionen kumulativ erhalten; Mini/EPG/Widget/Notice-Codebytegleich. | Vorherige übrige40-Gate-Abnahme nach P0 fortsetzen |

Kein Issue geschlossen, kein Release/Merge, keine Android-Installation. Weitere .41-/Roadmap-Issues nicht in diesen P0-Hotfix gezogen. Per-Item-Softwaredecoder BLOCKED mangels belegter Kodi-Python-API; Fremd-Skin/Keymaps unangetastet. Alle neuen sieben Android-Gates NOT_TESTED.
