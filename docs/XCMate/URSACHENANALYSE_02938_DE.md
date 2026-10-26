# .38 – Fehlernachweis und technische Grenzen

Basis: main `e25020c80703d440b0606b6d66559428dfc96cca` (.37), ohne Übernahme alter PR-Branches. Nutzerauftrag und vollständige Issues #178–181 sowie #94/#95/#106/#150/#173/#176/#177 gelesen. Suchmasken-Freeze und aktuelle Roadmap berücksichtigt. Die OSDs gehören laut neuem Auftrag bereits zu .38. #182 verlangt ausdrücklich keine neue Widget-Datenarchitektur in diesem Zyklus.

## Bestätigte Codepfade

| Befund | Vorher / reproduzierter Pfad | Korrektur / Nachweis |
|---|---|---|
| #179 Autostart | Historischer Diagnose-Default `true` blockiert die ausdrücklich gesetzte Portaloption. Nur einzelne Root-Aliase erreicht; zeitlicher Cooldown unterscheidet Refresh nicht zuverlässig von App-Einstieg. | `app_entry.py` verwaltet einen verbrauchten Vordergrund-Einstieg. Root/Home/`app_open` teilen einen Token. Widget/Background/Return armiert nicht. Erneuter Start erst nach beobachtetem Verlassen. 20 Refreshs und abgelaufener alter Cooldown erzeugen weiterhin nur einen Start. |
| Diagnoseaktion | Directory-Popup-Route ohne sauberen Abschluss kann `GetDirectory failed` erzeugen. | Directory vor temporärer Pause beenden; sichtbare 15-Minuten-Aktion statt verborgenem Dauerblock. Portalpräferenz bleibt erhalten. |
| Race vor Playerstart | Während Resolver/Preplay kann fremde Wiedergabe beginnen oder Autostart deaktiviert werden. | Session/Portal/Player vor Queue-Verbrauch und erneut nach Vorbereitung/Preplay prüfen. Doppelt konsumierter Token wird verworfen. Bestehender manueller Startpfad bleibt erhalten. |
| #176 Cover-Flackern | 30-s-Freigabe läuft aus → `lookup()` leer → Platzhalter → nächste Freigabe → ursprüngliches Bild. Render-Tick setzt dieselbe Referenz wiederholt. | Revalidierung vor Ablauf; nur bereits angezeigte identische Referenz während ausstehender Prüfung halten. Neue ListItems erhalten keine abgelaufene Freigabe. Endgültiger DNS-Fehler entfernt Referenz. Revision/`setArt`/`setImage` nur bei echter Änderung. Zwei TTL-Runden, DNS-Fehler und Quellenwechsel getestet. |
| #180 SQLite | `OperationalError` benennt weder Lock noch fehlendes Schema oder Query-Abbruch. Eine leere Statusausgabe ist kein Nachweis für leeres Archiv. | BUSY/LOCKED, QUERY_TIMEOUT, SCHEMA, READONLY, FULL und sonstige Fehler getrennt; Statusbudget begrenzt auf 0,5 s. Echte exklusive SQLite-Sperre und fehlendes Schema mit temporären DBs getestet; Query-Unterbrechung über Fehlerklassifikation geprüft. Kein automatisches Rebuild. |
| Fokus 300 | XML-Nachbarziel und reine Python-Sichtbarkeitsprüfung können ein nativ verborgenes Control erreichen. | Nur erlaubte Detailkante 820 abgesichert; native `Control.IsVisible` und `IsEnabled`, sonst sicheres Ziel 400. Such-Tabs/Ergebniscontrols bleiben byteäquivalent. |
| Mini-EPG | Bestehende Jetzt/Danach-Ansicht reicht nicht für reale Historie und fokussierbare rechte Spalte. | Nur markierten Sender zusätzlich read-only aus `guide_v1.sqlite` lesen: bis 6 h Historie/10 Tage Zukunft, maximal 256 echte Events; Titel 512/Plot 8192 Zeichen begrenzt. Kein globaler Cache-/Schemaumbau. |

## Navigation und Player

Gemeinsame lokale Tabler-Rail: Mini → Gruppen → kompakt → erweitert → Vollbild. Rückweg stufenweise; Programme rechts ändern beim Markieren keinen Sender. Native Buttons, kein Text als Attrappe. Owner-/Session-Token und Fensterfreigabe vor Rubrikhandoff, fremde Modals blockieren sicher. Guide-Kontext in 20 Öffnen-/Schließen-Zyklen des Testfensters erhalten; Medienkontext nach Rail-Öffnen, 20 Hoch-/Runter-Bewegungen und Back ebenfalls erhalten. Ein vollständiger Neuaufbau anderer Rubriken kann seine Scrollposition noch verlieren; das ist offen, nicht als PASS versteckt. Home hat die Rail als Kontextaktion, keine permanente Kodi-Verzeichnisleiste.

Live-Info und zweite Control-Ebene nutzen Kodi VideoPlayer. VOD ergänzt dessen Pause/Stop/Seek/Spulen und echte Zeit-/Codecwerte. Capabilities entscheiden über verfügbare Aktionen. Stop läuft über bestehenden asynchronen Exit-Worker; nur ein expliziter erneuter Benutzer-Stop darf nach abgeschlossenem Fehler neu versuchen. Hintergrundpolling wiederholt ihn nicht. VOD-Back blendet nur aus. Back auf sichtbarem Live-OSD schließt Ebenen; bestehender bewusster Live-App-Exit aus bereits geschlossenem Vollbild bleibt erhalten. Kein neuer Decoder, keine globale Keymap, kein fremder Player-Stop. Portale/Resume/Autoplay-Engine bleiben unverändert.

## Diagnose, Inventur und freiwillige Bereinigung

Physische interne Bilddateien, Jobs, aktive externe Ablage und Kodi-Texturecache werden getrennt ausgewiesen. Budget, freier/gesamter Speicher und Reserve sind echte gemessene oder ausdrücklich unbekannte Werte; null Jobs beweisen keinen leeren Kodi-Texturecache. Dynamisch hat kein dauerhaftes XCMate-Bildarchiv. Echte neue Installation bleibt dynamisch, Legacy-Modus-Gate unverändert.

Die optionale Bereinigung verlangt Dynamisch, lesende Inventur und zwei explizite Bestätigungen. Nur geprüfte eigene `64hex.img` unter den zwei festen internen Bildwurzeln sind zulässig. Verzeichnis-FDs/O_NOFOLLOW, Inode/Device/Linkzahl und erneuter SHA schützen vor Austausch, Hardlinks, Symlinks und Traversal. Neue Dateien nach Inventur bleiben erhalten. Aktive Migration blockiert widersprüchliche Löschung. Journal entsteht erst nach Bestätigung; nach Abbruch kein automatisches Fortsetzen. Nur tatsächlich gelöschte READY-Referenzen werden MISSING, andere Jobs/URLs bleiben erhalten. Physisch freigegebener Speicher und nominal gelöschte Bytes werden getrennt gemessen.

Diese Implementierung wurde ausschließlich auf temporären Hostprofilen ausgeführt. **Box B erhält keine weiteren Speicher-/Kopier-/Migrations-/Löschtests. Box A wurde nicht berührt; ihre Version ist UNKNOWN.** Reale Kopie, Aktivierung und spätere Löschung bleiben getrennte Benutzerentscheidungen. Der vorhandene .37-Migrationsmechanismus bleibt kumulativ erhalten, inklusive Hash-/Unterbrechungs-/SMB-Regressionstests.

## Sicherheits- und Beweisgrenzen

DNS-/URL-Freigaben werden nicht verlängert: positives DNS-TTL begrenzt weiterhin URL-Zulassung, negatives DNS-Caching bleibt kurz, neue unfreigegebene Quellen sind gesperrt. Die stabil gehaltene Referenz betrifft nur bereits angezeigte identische Bilder während Revalidierung. Definitiver Fehler entfernt sie. Kodi lädt dynamische Bilder selbst; tatsächliche HTTP/TLS-Aufrufe und DNS-Pinning des nativen Kodi-Transports wurden auf Android nicht beobachtet. Ein vollständiger Schutz dieses Transports gegen DNS-Rebinding wird nicht behauptet.

Der Hardwaredecoder-Hinweis `null size` wurde keinem neuen XCMate-Fehler zugeordnet; er bleibt Gerätebeobachtung. Keine Änderungen an Kodi, Titan BINGIE MOD, Slyguy oder anderen Add-ons. Der ältere All-Media-Hänger #174 hat weiter unbekanntes Gerät/Version und wird nicht mit #169 gleichgesetzt. Box-B-.37-PASS sind historische Nutzerrückmeldung, keine .38-Abnahme. Keine Rohlogs oder Zugangsdaten veröffentlicht.

## Offener Umfang

- #94/#150: Home-Kontextaktion vorhanden; dauerhafte Home-Rail und vollständige rubrikübergreifende Positionserhaltung teilweise offen.
- #181: Technik und drei Varianten geliefert; Android-IR/Fokus und visuelle Auswahl fehlen.
- #106/#173: Hostschutz grün; reale Box-A-Inventur/Sicherung/Migration nicht durchgeführt.
- #171: Physischer externer Metadatenbestand BLOCKED; vorhandener Export ist kein Offload.
- #43/#164: Dauerhaftes Resume ungespeicherter Wizard-Scans nach Prozessabbruch BLOCKED; bestehende Wizard-Funktionen erhalten.
- #98 bleibt eigenständige quellensichere Mapping-Entwicklung, #161 Architekturphase, #182 Widget-Folgearbeit .39.

Jede neue Android-Prüfung bleibt NOT_TESTED; B-Speichertests sind durch den Nutzer gestoppt. Kein Merge, produktiver Release, Profilreset oder Gerätezugriff Bestandteil dieser Lieferung.
