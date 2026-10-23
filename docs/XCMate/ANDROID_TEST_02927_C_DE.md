# .27-C – linkes Detailmenü und Downloads

Aufbauend auf .27-A (#125) und .27-B (#126). Interner Testschritt mit Add-on-Version
.27, kein vollständiger Releasekandidat, kein Merge/Repository-Update.
Die neue .26-Geräteabnahme mit 15 PASS / 6 FAIL bleibt historische Baseline.
Alle neuen Android-Prüfungen beginnen mit NOT_TESTED.

## Bedienung und Lieferumfang

Film- oder Seriendetails öffnen → **Links**. Ein natives Seitenmenü erscheint:
Film/Folge herunterladen, Downloads verwalten, Poster erneut herunterladen,
Posterstatus und Schließen. **Rechts oder Zurück** schließt nur dieses Menü und
stellt die Detailposition wieder her. Vorhandene Play-/Resume-/Autoplay-Aktionen
bleiben in ihrem bisherigen Pfad; keine globalen Kodi-Keymaps.

Downloads nutzen exakt **recordings_folder**, also den Aufnahmeordner. Kein
zweiter Downloadordner, keine Migration vorhandener Dateien. Dateien liegen im
gleichen Ordner mit **Download - …** und eigener ID, Episoden mit SxxExx.
Im Menü wird der Typ ausdrücklich als Download angezeigt. Bei Serien wählt der
Nutzer eine tatsächlich vorhandene Folge; es gibt keinen unbeabsichtigten
Serien-/Staffel-Komplettdownload. Flat-Series-Quellen werden als Einzelmedium
behandelt. Der bestehende manuelle Next-/Autoplay-Pfad wird nicht verwendet.

Vor jedem Auftrag wird die zusätzliche Anbieter-Verbindung bestätigt. Ein
Service-Worker übernimmt Transfers, ein Dateilock verhindert parallele Worker.
Die private SQLite-Queue enthält Identität/Status, keine Stream-URLs oder Tokens.
Pro Zugriff eigene SQLite-Verbindung. Zielprobe vor Providerauflösung; nur
geprüfte lokale POSIX-/Hardlink-Ziele wie .27-B. Finalisierung ohne Überschreiben,
partielle Dateien getrennt und nur vollständige Jobs abspielbar. Keine globale
Löschung. Pause/Abbruch behalten Teildaten. Neustart unterbrochener Transfers
pausiert diese; Fortsetzen ist ausdrücklich und nutzt Range nur nach Prüfung von
Validator/Quellfingerprint/Teilhash. Andernfalls sauberer Neuanfang in eigener
Teildatei. Begrenzter Retry/Backoff, kein endloser Neustart.

Unterstützt werden erlaubte direkte HTTP(S)-Medien mit bekannter Content-Length
und erkanntem MP4/MKV/AVI/TS-Container. HLS/DASH, DRM, Redirects zu fremden
Origins und nicht lokale Ziele werden nicht als unterstützte Downloads ausgegeben.
Standardobergrenze 64 GiB auf geprüftem Speicher, mindestens 64 MiB Reserve.
Provider kann Downloads/Zweitverbindungen einschränken. Kodi-Offlinetest offen.

## Android-Abnahme

Zunächst B01–B02 aus der .27-B-Anleitung durchführen und ein kompatibles
Aufnahmeziel bestätigen. Die Menü-Startbestätigung ist noch kein Download-PASS.

- [ ] C01 Film öffnen → Links: Menü, lesbare Labels und sichtbarer D-Pad-Fokus.
- [ ] C02 Hoch/Runter, Rechts, Zurück: Menü schließt, gleiche Film-/Seriendetails,
  gleiche Aktion; kein unerwarteter Playerstart oder Suchaufruf.
- [ ] C03 Poster erneut herunterladen: nur gewähltes Poster, Status sichtbar,
  vorhandene Bilder/Jobs anderer Titel erhalten; Back weiterhin bedienbar.
- [ ] C04 Film-Download wählen und abbrechen: kein Auftrag/Providertransfer.
- [ ] C05 Film-Download bestätigen → Verwaltung: vorgemerkt/laufend, MiB steigen;
  vorhandener Aufnahmeordner wird verwendet; Datei trägt Download-Kennzeichnung.
- [ ] C06 Serien-Download: reale Folge wählen, dann bestätigen; korrekte Serie,
  Staffel und Folge; kein Download anderer Folgen oder Portale.
- [ ] C07 Laufenden Auftrag pausieren/abbrechen, Status erneut öffnen; Teildatei
  bleibt erhalten und kann nicht als fertiger Film gestartet werden.
- [ ] C08 Fortsetzen/Retry: bei stabilem Range-Validator weiterladen, andernfalls
  sicher neu beginnen; kein beschädigtes Anhängen oder Überschreiben.
- [ ] C09 Fertigen Film und eine Folge aus Verwaltung abspielen, Bild/Ton prüfen.
- [ ] C10 Kodi neu starten, Netzwerk trennen: fertige Downloads bleiben auffindbar
  und lokal abspielbar; bestehende Aufnahmen/Poster weiter vorhanden.
- [ ] C11 Volles/fehlendes/inkompatibles Ziel: klare Fehlermeldung, keine falsche
  Fertigmeldung, keine zusätzliche Provider-Verbindung bei früher Zielablehnung.
- [ ] C12 A01–A08 und B03–B08 wiederholen: Such-Live, EPG, Live-IR, Resume,
  Staffelautoplay und Stop, Favoriten und Originalicon erhalten.

## Weitere verbindliche Entwicklung

Diese Lieferung erfüllt die angeforderten ersten P0-Drafts und das neue
Detailmenü/Downloads. Der vollständige Einrichtungsassistent #43, informative
Suchansicht #127 sowie #120/#122/#123/#98/#111 sind weiterhin beauftragt und
noch nicht als fertig enthalten. **Insbesondere #43 und #127 sind verbindliche
Gates der nächsten vollständigen Baureihe**, keine unverbindliche Verschiebung.
Der ergänzte PR-Stack-Plan nennt Reihenfolge, Abhängigkeiten und Abnahmekriterien.
Dieser C-Test darf ohne deren Umsetzung/Abnahme nicht als vollständiger
Releasekandidat veröffentlicht werden.
