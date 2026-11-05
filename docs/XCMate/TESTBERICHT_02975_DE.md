# XCMate 0.1.29.75 – Testbericht

Basis: `ad5c337c0ca9ea6f85e458c17383fb32c19e3fc2` (.74). Auftrag #366/#367/#368. Status dieses ersten PR-Standes: **DRAFT, Gesamtlauf/CI und abschließender 60-Minuten-Lauf noch ausstehend**. Keine Android-Abnahme behauptet. Der Bericht wird mit den abschließenden Ergebnissen aktualisiert.

## Bereits geprüft

| Prüfung | Ergebnis |
|---|---|
| Neue .75-Funktions- und Bestandsschutztests | **39/39 PASS**, 5,063 s (inklusive fünfter Skin-Datei, Schreibfehler/Rollback/Restore) |
| Bestehende pytest-Brandingtests | **11/11 PASS**, 0,15 s |
| Sprachdateien | **17 Kataloge PASS** |
| Originale Tabler-Icons und Lizenzen | **92 Texturen PASS** |
| Kodi 21.2 Linux, BINGIE 2.2.3, 1280×720 | **PASS**, 23 Fokus-/Bildfälle, 20 echte Auf-/Ab-Wechsel, Seitenmenü, fehlende Progress-Controls |
| 20 verspätete Live-Stop-ACK-/Fullscreen-Rückkehrzyklen | **Host PASS**, kein zweiter Stop, Rückkehr genau einmal |
| ZIP | **CRC, eindeutige/sichere Pfade, 728 Dateien, Source-Bytevergleich PASS** |
| Pilot-Staging | **lokale Prüfung PASS**, noch nicht öffentlich freigegeben |
| Regulärer Katalog | unverändert `.74`, automatische Veröffentlichung `.75` gesperrt |
| Android Kodi 21.2/21.3 / RK3528 | **ANDROID_NOT_TESTED** |

Der vorherige vollständige 3.090er Hostlauf war **FAIL** (7 Assertions, 1 Error). Eine Assertion betraf zusätzlich geprüfte native Navigationsparameter und ist korrigiert; die Katalog-Sicherungsfehler waren isoliert nicht reproduzierbar und werden im vollständigen Lauf mit Ausnahmeaufzeichnung nachgeprüft. Sie werden nicht übergangen und nicht als behoben ausgegeben. Merge erst bei grünen automatisierten Gates.

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

[Live, 720p](test-builds/02975/evidence/720-home75-live-0.png), [Film mit Fanart](test-builds/02975/evidence/720-home75-vod-0.png), [Film mit Hochkantposter](test-builds/02975/evidence/720-home75-vod-1.png), [Serie](test-builds/02975/evidence/720-home75-series-0.png), [Seitenmenü](test-builds/02975/evidence/720-home75-menu.png), [native Messdaten](test-builds/02975/evidence/native720.json).

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
