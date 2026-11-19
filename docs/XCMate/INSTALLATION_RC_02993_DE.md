# .93 – manuelles kumulatives Testupdate

Draft-PR #455. Noch kein reguläres/Pilot-/NeoDark3-Update, kein Merge und keine produktive Empfehlung.

1. Ausschließlich die vereinbarte Testbox nutzen; Box A unverändert lassen. Bestehendes Profil/Quellen/Token/Widgets außerhalb der Bereinigungsziele sichern. Nicht deinstallieren, keinen Reset oder erneuten Komponenteninstaller starten.
2. `docs/XCMate/test-builds/02993/plugin.video.xtreammate-0.1.29.93.zip` und `.sha256` aus dem PR herunterladen. Aktueller SHA256: `48e0822827c2a8e8a854a812cbac0d0fb3407f6f6b9a5c3c2c2213f20fe77a95`. Frühere .93-Entwicklungsprüfsummen sind überholt.
3. Vor Installation Prüfsumme vergleichen, in Kodi Add-ons → Aus ZIP-Datei installieren wählen. Das aktualisiert die vorhandene Add-on-ID kumulativ; nicht den GS Media Setup Wizard erneut ausführen.
4. Version und Gerätestand notieren. Die Speicherpflege entfernt nur exakt nachgewiesene ältere EPG-Recovery-Sätze und bereits zulässige eigene Altbestände; letzte valide Sicherung, aktive Datenbanken, Quellen und Bilder bleiben. Inventur/Journal und tatsächliche freie Bytes auf demselben Volume vergleichen.
5. [Android-Plan](ANDROID_ABNAHME_02993_DE.md) abarbeiten. Beim ersten Live-Stop-Standbild keine weiteren 120 Zyklen starten; Zeitpunkt und tatsächliche Eingaben (einschließlich Android-HOME) getrennt erfassen. Der native Rockchip-Freeze ist noch kein bestätigter Fix.
6. Keine private Rohlogdatei öffentlich hochladen. PASS/FAIL/NOT_TESTED je Gate mit festen Diagnosecodes und redigierter Zeitkorrelation. Alle Gerätegates zunächst ANDROID_NOT_TESTED.

ZIP ist ein überprüfbarer Kandidat; Host-/Linux-Nativtests ersetzen keine Android-Abnahme. Offene Punkte siehe [Issue-Matrix](ISSUE_MATRIX_02993_DE.md).
