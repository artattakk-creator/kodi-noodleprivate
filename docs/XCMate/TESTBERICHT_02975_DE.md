# XCMate 0.1.29.75 – Testbericht

Basis: `ad5c337c0ca9ea6f85e458c17383fb32c19e3fc2` (.74). Auftrag #366/#367/#368. Status dieses ersten PR-Standes: **DRAFT, voriger vollständiger Hostlauf PASS; neuer Fokus-Queue-Fix gezielt PASS, vollständige CI und abschließender 60-Minuten-Lauf noch ausstehend**. Keine Android-Abnahme behauptet. Der Bericht wird mit den abschließenden Ergebnissen aktualisiert.

Der vorläufige SHA `0d0cbf290ec489635a3e69faf787643db91a02298eb91bd021878bac4f5e7126` ist nach der letzten Fokus-Queue-Korrektur überholt. Aktuelles ZIP: `83acfaf48b1877dc32fb8879c470bcbc178c90d85a4296dc88c716f560ea1392`. Die früheren vollständigen Hostzahlen gelten für den vorigen Kandidaten; der abschließende 3.097er CI-Lauf muss den neuen Stand bestätigen.

## Bereits geprüft

| Prüfung | Ergebnis |
|---|---|
| Vollständiger lokaler Hostlauf des vorigen Kandidaten | **3.090/3.090 PASS**, 582,170 s; zusätzliche drei neue Skin-Schutzfälle separat im 39er Lauf PASS |
| Neue .75-Funktions- und Bestandsschutztests | **43/43 PASS**, 4,916 s (inklusive fünfter Skin-Datei, Schreibfehler/Rollback/Restore) |
| Vollständiger GitHub-Hostjob des vorigen Kandidaten (Code `0da8f3c`) | **3.093/3.093 PASS**, 657,999 s; Gesamtworkflow wegen separatem Cloud-Zeitgate noch nicht freigegeben |
| Nativer 720p-Neustart und Reload | **PASS**, andere Kodi-PID, sieben Bild-/Fokusfälle, 88/24/24 Einträge, 32 geschützte Dateien bytegleich |
| Bestehende pytest-Brandingtests | **11/11 PASS**, 0,15 s |
| Sprachdateien | **17 Kataloge PASS** |
| Originale Tabler-Icons und Lizenzen | **92 Texturen PASS** |
| Kodi 21.2 Linux, BINGIE 2.2.3, 1280×720 | **PASS**, 29 Fokus-/Bildfälle einschließlich fremder Poster-/Musik-/TV-Quellen, 20 echte Auf-/Ab-Wechsel, Seitenmenü, fehlende Progress-Controls |
| 20 verspätete Live-Stop-ACK-/Fullscreen-Rückkehrzyklen | **Host PASS**, kein zweiter Stop, Rückkehr genau einmal |
| ZIP | **CRC, eindeutige/sichere Pfade, 728 Dateien, Source-Bytevergleich PASS** |
| Pilot-Staging | **lokale Prüfung PASS**, noch nicht öffentlich freigegeben |
| Regulärer Katalog | unverändert `.74`, automatische Veröffentlichung `.75` gesperrt |
| Android Kodi 21.2/21.3 / RK3528 | **ANDROID_NOT_TESTED** |

Der vorherige vollständige 3.090er Hostlauf war **FAIL** (7 Assertions, 1 Error). Eine Assertion betraf zusätzlich geprüfte native Navigationsparameter und ist korrigiert; die Katalog-Sicherungsfehler waren isoliert nicht reproduzierbar und werden im vollständigen Lauf mit Ausnahmeaufzeichnung nachgeprüft. Die Katalogfehler sind im anschließenden vollständigen Lauf mit identischem Standard-Discovery und Ausnahmeaufzeichnung nicht erneut aufgetreten; kein Katalogcode wurde dafür verändert. Ein zusätzlicher parallel gestarteter Diagnoselauf wurde vom Arbeitsumgebungs-OOM beendet (exit 137) und zählt nicht als PASS. Danach wurde die lokale Parallelität reduziert. Merge erst bei grünen automatisierten Gates.

Ein separater historischer 2.000-Schritte-Navigationstest überschritt im isolierten GitHub-Paket die unveränderte 5-s-Grenze (6,131 / 6,155 s). Profiling belegt 70.738 erfolglose `xbmcvfs`-Importsuchen, weil die alte Omega-Testfixture dieses tatsächlich in Kodi vorhandene native Modul nicht bereitstellte. Die Fixture modelliert jetzt `translatePath` ohne Dateisystemsuche. Keine Anwendungskorrektur und keine Lockerung des Grenzwerts: kompletter Einzelfall einschließlich Setup lokal 0,856 s; das genaue 197er CI-Paket besteht anschließend. Der gesamte CI-Lauf wird nochmals geprüft. Die erweiterte Neustart-Harness wartet jetzt auf das tatsächliche Ende des alten Kodi-Prozesses und das Ende der regulären BINGIE-Startmaske; HTTP-Ping allein war noch kein Neustartnachweis.

## Reproduzierbare Befehle

```sh
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0' 'simpleeval==0.9.13' 'pytest>=8,<10'
python -m unittest discover -s tests -v
python -m pytest -q tests/test_xcmate_bingie_branding.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python tools/run_kodi_home75_contract.py --report-dir /tmp/home75-720 --resolution 1280x720
python tools/run_kodi_home75_contract.py --report-dir /tmp/home75-1080 --resolution 1920x1080 --idle-seconds 3600
python tools/package_xcmate71.py /tmp/package75
cmp /tmp/package75/plugin.video.xtreammate-0.1.29.75.zip docs/XCMate/test-builds/02975/plugin.video.xtreammate-0.1.29.75.zip
python tools/publish_xcmate75_pilot.py
python tools/release_channel75.py
```

Netzwerk-/Loopbackberechtigung und Docker werden für die betreffenden Hosttests benötigt. Die nativen Screenshots verwenden ausschließlich synthetische Sender, Titel und Farben. Sie beweisen Kodi-Rendering und Identitätswechsel, keinen privaten TMDB-Match und keine Android-Eigenschaft.

## Native Renderbelege und Messgrenzen

[Live, 720p](test-builds/02975/evidence/720-home75-live-0.png), [Film mit Fanart](test-builds/02975/evidence/720-home75-vod-0.png), [Film mit Hochkantposter](test-builds/02975/evidence/720-home75-vod-1.png), [Serie](test-builds/02975/evidence/720-home75-series-0.png), [Seitenmenü](test-builds/02975/evidence/720-home75-menu.png), [native Messdaten](test-builds/02975/evidence/native720.json), [tatsächliche Phasen](test-builds/02975/evidence/load-order720.json), [Neustart-/Restore-Messdaten](test-builds/02975/evidence/restart720.json).

Die `settled_render_ms` von 2.718–3.044 ms enthalten ausdrücklich 1.500 ms feste Settle-Wartezeit, Screenshoterzeugung und Python-Pixelprüfung. Das ist **keine** gemessene Android-Kaltstartlatenz und kein Nachweis eines `<2 s`-Ziels. Native Phasen wurden in der Reihenfolge `1 → 2 → 3` empfangen; `PREPARED` ist getrennt von tatsächlich sichtbaren Labels/Geometrie. Die echte private EPG-/Bildlatenz wird gemäß Android-Testplan separat gemessen.

## Issue-/Abnahmematrix

| Auftrag | Implementierung | Nachweis / noch offen |
|---|---|---|
| #367 Home-Hero/Einzelrail/Navigationsicons | feste 66,7/33,3-Aufteilung, native Nachbarziele, vorhandene Routen erhalten | 720p/1080p CI-Rendering PASS; Langzeit/Android ausstehend |
| #367 Start-EPG/Ladepriorität | profil-/konfigurationsgebundener lokaler Checkpoint, Fokus + sichtbare fünf, vorhandene Worker gegatet | Hosttests PASS; reale Android-Startreihenfolge offen |
| #366 Bildpfad/296301/296302 | exakter geprüfter Event-Origin, eng begrenzte Alt-Negativ-Neubewertung, Text unabhängig vom Progress-Control | Host PASS; private Provider-/TMDB-/TVmaze-Treffer **ANDROID_NOT_TESTED** |
| #368 Rückkehr nach verspätetem positivem ACK | exakte Session, leeres eigenes Vollbild freigegeben, Rückkehr genau einmal | 20 Hostzyklen PASS; native ARM32-Stop-Blockade **nicht nachweislich behoben** |
| Kodi MyVideos131 | begrenzte read-only Diagnose, keine Schema-/Dateireparatur | Host PASS; reale Bibliothek unverändert, Android offen |
| Datenbestand/Skin/Space Blue | bestehender SHA-/Preview-/Zustimmungs-/Restore-Ablauf, unbekannte Skin-XML blockiert | Host PASS; keine Benutzerbox verändert |

Alle `HERO75-R1..R8`, `H75-01..H75-10`, `PREFETCH75-1..8`, `LOAD75-A..F` und 20× Android-Back bleiben geräteseitig **ANDROID_NOT_TESTED**; ausführbare Schritte: [Android-Abnahme](ANDROID_ABNAHME_02975_DE.md). Unbekannte private Space-Blue-XML wird nicht ungeprüft überschrieben.

## Offene Grenzen

Die sichtbare Ein-Rail-Vorgabe und das automatische Vorbereiten unsichtbarer Medienreihen sind in der Spezifikation nicht eindeutig vereinbart. Ohne Nutzerpräzisierung bleibt das strengere tatsächliche Render-Gate erhalten; Fokuswechsel bleiben sofort möglich. Ein nativer Kodi-Stop ohne FIFO-ACK wird nur begrenzt diagnostiziert, niemals durch einen zweiten Stop oder falsches HOME-Ergebnis maskiert. Ausführlich: [Ursachen und Grenzen](URSACHENANALYSE_02975_DE.md).

## Releasekanäle

Nur nach grüner CI: autorisierter Merge und bestehender **GS Media Pilot**, kein neues Repository, kein Installerlauf. Das reguläre Root-`addons.xml` bleibt `.74`; separate ausdrückliche Android-Freigabe erforderlich. Eine Freigabedatei für den regulären Kanal ist nicht enthalten. Nach Veröffentlichung sind Pilot-Index, MD5, ZIP, SHA256, Manifest und tatsächliche öffentliche Verfügbarkeit erneut zu prüfen.
