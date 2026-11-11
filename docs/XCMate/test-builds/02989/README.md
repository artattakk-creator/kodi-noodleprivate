# XCMate 0.1.29.89 – Testpaket

[Installations-ZIP](plugin.video.xtreammate-0.1.29.89.zip) · [SHA256-Datei](plugin.video.xtreammate-0.1.29.89.zip.sha256) · [Draft-PR #426](https://github.com/artattakk-creator/kodi-noodleprivate/pull/426)

Getesteter Quellstand: `0deaafa17bb5e5b5ad69c55cea3750a453a2a9db`.

SHA256: `5e2522ccb45e3a3274257c94ae440a1e5caee127cbeb8cf3f6fb814a1e5a874b`

Das ZIP ist ein kumulatives Testupdate, kein veröffentlichtes Repository-Update. Nach privater Profilsicherung über Kodi → Add-ons → Aus ZIP-Datei installieren über die vorhandene Installation einspielen. Keine Deinstallation und kein Profilreset. Box A bleibt unverändert.

## USB, SD oder Samba für Bilder

In der vorhandenen Artwork-Verwaltung ein externes Ziel auswählen. Verfügbare USB-/SD-Speicher und bestehende Kodi-Samba-Quellen verwenden; Anmeldung und Berechtigungen bleiben bei Kodi. Das Ziel wird nicht automatisch aktiviert.

Zielprobe → Kopieren → SHA256-Prüfung → sichtbare Bildprobe → ausdrückliche Aktivierung. Die Originaldateien bleiben erhalten. Nur Senderlogos, Sendungsbilder und Film-/Seriencover werden ausgelagert. Datenbanken, Token und Profile bleiben intern.

Bei nicht erreichbarem Laufwerk bleibt die Auswahl erhalten; keine stille interne Archivumschaltung. Unbekannter NAS-Freiraum ist keine bestätigte Kapazität. Eigene Grenzen: Logos 16 MiB, Poster 24 MiB, Sendungsbilder 32 MiB; bestehende Speicherreserven bleiben berücksichtigt.

Ein älteres separat ausgelagertes .87-Sendungsbildarchiv mit physischem Mountnachweis kann noch nicht auf ein anderes generisches Ziel konvertiert werden. Dieser Fall wird vor Änderung der Konfiguration kontrolliert blockiert.

## Abnahme

[Vollständiger Testbericht](../../TESTBERICHT_02989_DE.md) · [Android-, Reminder- und Laufwerkstestliste](../../ANDROID_ABNAHME_02989_DE.md)

Physische Android-, USB-/SD- und echte Samba-Tests sind **ANDROID_NOT_TESTED**. Host-/Linux-Kodi-Tests ersetzen diese Abnahme nicht. Kein Merge und keine Veröffentlichung in regulär, Pilot oder NeoDark3 freigegeben.
