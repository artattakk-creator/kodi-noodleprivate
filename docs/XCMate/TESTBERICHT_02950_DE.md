# XCMate .50 – vollständiger Test- und Paketbericht

Stand: 28.10.2026 (Europe/Berlin). Auftrag #252, Referenzen #250 / PR #251 / PR #253. Kumulative Basis `main` .49: `bc278a32a0e9a3bc8763189c09ffa9195d4dddf3`; Quellbuild `7015628534fc7a96afb363480c692cd3df640f38`; Branch `hotfix/xcmate-02950-bingie-home`.

## Gesamtresultat

**2.078 Hosttests PASS in 318.062 s, 0 Fehler, 0 Failures, 0 übersprungene Tests.** Alle **2.035 bisherigen Methoden** erhalten, **43 neue**. Sauberer `git archive`-Checkout mit regulärem Bootstrap/Upgrade/Build, PO-Prüfung (de/en jeweils **1.115 Kontexte**), 92 Navigationstexturen/Lizenzen und Python-Syntaxprüfung. Vollständige Socket-/SMB-/Datenbank-/Großkatalog-/UI-/Playerregressionen auf freigegebenem Host-Testnetz. Keine echte Kodi-/Android-Instanz und keine Nutzerbox wurde damit bedient.

Bekannte unveränderte `SMBProtocol.py`-SyntaxWarning; der allein für Original-Template-Referenztests gepinnte `simpleeval==0.9.13` erzeugt unter Python 3.12 DeprecationWarnings für alte AST-Aliase. Keine neuen Laufzeitfehler, kein Test dafür übersprungen. Diese Testabhängigkeit wird von CI installiert, nicht neu als XCMate-Kodi-Laufzeitabhängigkeit gebündelt.

`TESTLOG_02950.txt` enthält den vollständigen synthetischen Hostlauf; nur abschließende Zeilenleerzeichen normalisiert. Roh-/publizierte Log-SHA in `TESTERGEBNISSE_02950.json`.

## Was konkret geprüft wurde

- Exakt drei direkte native Aktionen Live-TV, Filme und Serien; keine Gruppenlisten als Verknüpfungsersatz. Bestehender .49-Quellbrowser bleibt separat als Kompatibilitätsfunktion getestet.
- Wirkliche bestehende Skinshortcuts-Profildatei: freie Position, gezieltes Aktualisieren ihrer fünf Widgetfelder, Unicode-/Kommentarerhalt, Ablehnung belegter Medien-/Fremdkontopositionen, ausdrückliche Umstellung eigener Legacy-Live-Gruppenlinks. Namen/Reload-Hooks bereits korrekter Medienbindungen bleiben unverändert.
- **Originaler Skinshortcuts-2.1.0-Profilleser** liest nach verifiziertem Save und erneutem frischem Reader die exakte Widgetquelle; Save ist kein JSON-Scheinmodell. Default-/umbenannte/unbekannte/zu große/beschädigte Profile und Einzelwidgetmodus werden nicht geraten.
- Freigabe muss ausdrücklich wahr sein. Abbrechen ändert kein Ziel; private Originale/Kandidaten/SHA256 und echte Rücksicherungs-Prüfdateien existieren vor der Entscheidung. Profilwechsel während der Bestätigung und spätere Fremdänderungen führen zur Sperre.
- **Offizielle BINGIE-2.2.3-Dateien**: echte Home-Region, Senderleiste, Registry und acht Templatepositionen. Originaler Skinshortcuts-2.1.0-Compiler und Widget-Registryloader verarbeiten die Kandidaten. Bisherige Medienparameter bleiben erhalten; bekannte .46-Card-Erweiterung wird nicht entfernt.
- Schreibfehler vor und nach jeder der vier Datei-Ersetzungen sowie Prozessabbrüche zwischen Dateien; exakte Rücksicherung, keine Überschreibung späterer Fremdänderungen. Wiederherstellung kehrt Definitions-/Aufruferreihenfolge um.
- **88 reale synthetische Sender in einer lokalen Startgruppe**, zusätzlicher fremder Gruppenbestand und absichtlich abweichende Startsendergruppe. Nur gewünschte Gruppe, vollständige 88 Einträge, keine Gruppenkacheln, kein Providerfallback. Fehlende Gruppe ergibt leere Quelle mit Diagnose.
- Gemeinsame lokale Now/Next-/Artwork-Events einschließlich richtigem ProgrammeKey, Beschreibung und neutralem ProgrammeImage; Logos als eigene Property. Reale Native-ListItems behalten genaue vorhandene Player-Klickziele. Fokusdarstellung verwendet native InfoLabels, keine Python-Fokus-Netz-/SQL-/Playbackfunktion.
- Kodi-21.3-Headerbeleg für den Abbrechen-Standard, Player-/Editor-/Skinversionguards, explizit bestätigter nativer Editor als Ausweichweg, kein automatisches Umstellen fremder Benutzereinstellungen.

Die frühen gezielten Arbeitsläufe fanden fehlende SKINPATH-/Labelhelfer im Testadapter des Original-Profillesers sowie die nötige Abgrenzung neuer Quellen in alten Freeze-Helfern. Diese Testmodell-/Erwartungspunkte sind im finalen sauberen Lauf korrigiert. Keine Methode entfernt oder neu übersprungen; .49-Medien-/Quellkompatibilität bleibt geprüft, die .50-Direktspeicherung erhält eigene Tests.

## Bestandsschutz

**566 alte Quelldateien erhalten: 560 bytegleich, sechs exakt überprüfte Versions-/Sprach-/Routeänderungen; sieben neue Dateien.** Keine entfernte Quelldatei. Unverändert u.a. native .42-Stopengine, Media-/Player-/Resume-/Autoplaycode, Portale, Favoriten, EPG-/Mappingkern, Artwork-/Covercache, Widget-Reader/Klickziele/Autorefresh und native Setting-IDs. 62 gesicherte fremde WIP-Dateien unverändert.

Die Entwicklung hat keine Geräteinstallation, keine produktive Skin-Datei und kein Benutzerprofil verändert. Tests wenden die Transaktionen ausschließlich auf synthetische Profile und öffentliche Skinreferenzkopien in temporären Hostverzeichnissen an. Das installierte Add-on wendet beim Start/Update nichts an; Skin- und Profilplan benötigen getrennte lokale Nutzerbestätigungen.

## Installationspaket

- `plugin.video.xtreammate-0.1.29.50.zip`: **3,090,209 Bytes**, **573 Dateien**.
- SHA256: `399e5d98bd3cd940cf4073afe899abc40f5b9f5c359c5ac177f17eb70acb59a8`
- CRC, sichere/eindeutige Pfade, keine Symlinks/Profile/DBs/Rohlogs/Bytecode und AST aller Python-Dateien: PASS.
- **Alle 573 Paketdateien bytegleich zum Quellstand.** Eigene deterministische ZIP-Rekonstruktion ergibt exakt dieselben Bytes.
- `PAKETPRUEFUNG_02950.json`, `DATEIKATALOG_02950.json`, `SCHUTZPRUEFUNG_02950.json` und `NEUE_TESTS_02950.json` enthalten die Kataloge.

## Separates Skin-Prüfobjekt

`integrations/titan-bingie-mod/0.1.29.50/`: vollständiger Vier-Dateien-Diff, Kandidaten, Vorher-/Nachher-SHA256, Lizenz und Anleitung. Prüfarchiv-SHA256: `b09e3203c6ae9f613ed62e0148177884c18eaf14ccbf9497dedff9b049c14600`.

Dieses Archiv ist **kein installierbarer Skin und keine private Gerätesicherung**. Vor Ort verifizierter Istzustand und private Backups bleiben maßgebend; unbekannte Hashes blockieren. Die konkrete Aktivierung auf Box A steht aus und benötigt ausdrückliche separate Freigabe. Ein unverändert kopierter Referenzcompiler und XML-Geometrie sind kein Android-Pixel-/IR-/Decodiernachweis.

## CI / Geräteabnahme

Unabhängiger GitHub-PR-Build führt denselben Bestand aus, prüft Paket und Quellbytes und liefert sein Artefakt mit berechnetem ZIP-SHA. Exakter finaler Liefer-HEAD, Run und Ergebnis werden im Draft-PR geführt, damit kein nachträglicher Dokumentationscommit rekursiv die CI-Basis ändert. Der produktive Publish-Schritt muss beim PR **skipped** bleiben; kein automatischer Merge/Release.

**W50-01 bis W50-12: alle NOT_TESTED.** Historische .49-Abnahme bleibt FAIL. Für unbekannte Profile/Skinstände gelten dokumentierte BLOCKED-Voraussetzungen; native assistierte Auswahl ist kein ungeprüftes One-Click-Versprechen. Tatsächliche Home-Reihen, Bilddecodierung, IR/vertikale Navigation, OK/Back, Neustartpersistenz und Autorefresh müssen auf Box A geprüft werden. Anleitung: `ANDROID_ABNAHME_02950_DE.md`; Ursachen und Grenzen: `URSACHENANALYSE_02950_DE.md`; Matrix: `ISSUE_MATRIX_02950_DE.md`.
