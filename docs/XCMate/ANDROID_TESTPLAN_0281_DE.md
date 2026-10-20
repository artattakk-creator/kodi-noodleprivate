# Android-Abnahme, Installation und Rollback – 0.1.28.1

**Alle folgenden Hotfix-Gerätefälle sind OFFEN.** Cloud-Modelle ersetzen Kodi 21.3
Omega auf RK3528 / ARM 32-bit nicht. [Analyse und Testergebnisse](HOTFIX_0281_STARTUP_DE.md)
· [Issue #38](https://github.com/artattakk-creator/kodi-noodleprivate/issues/38).

## Testpaket installieren

1. Kodi sauber beenden und das gesamte bestehende XCMate-Profil sichern:
   `special://profile/addon_data/plugin.video.xtreammate/`. SQLite-Dateien einschließlich
   vorhandener WAL-/SHM-Dateien zusammen sichern; nicht im laufenden Schreibbetrieb kopieren.
   Zusätzlich installierte Version und vorhandene Cache-/Medienpfade notieren. Sicherung
   privat halten, da Zugangsdaten enthalten sind. **Nichts löschen.**
2. Geprüftes Kandidaten-ZIP 0.1.28.1 aus dem Hotfix-PR laden und SHA256 mit dessen
   Prüfsumme vergleichen. Bei CI-Download äußeres GitHub-Artefakt entpacken: Nur das
   darin liegende `plugin.video.xtreammate-0.1.28.1.zip` in Kodi installieren.
3. **Add-ons → Aus ZIP-Datei installieren**; Kandidat über bestehende Installation
   installieren. ID bleibt `plugin.video.xtreammate`, Profil bleibt erhalten.
   Installierte Version in Add-on-Informationen kontrollieren. Keine Neuinstallation
   des Repository-Add-ons und keine Cache-Leerung nötig.
4. Kodi neu starten, damit Service und Plugin dieselben aktualisierten Python-Module
   verwenden. Vorheriges problematisches Startverhalten und nötigen Neustart notieren;
   ein Neustart allein hatte bereits einen Einfluss auf den Befund. Nicht als Fix-Beweis werten.

## Auszuführende Gerätefälle

| Fall | Prüfung / Abnahme |
|---|---|
| Kaltstart BINGIE MOD | Bestehende XCMate-Widgets laden lassen und bereits währenddessen XCMate aus Video-Add-ons öffnen. Sechs Menüeinträge innerhalb weniger Sekunden, Fernbedienung bedienbar. Zeit messen. |
| Warmstarts / Zurück | Zehnmal öffnen, Zurück, erneut öffnen; kein dauerhafter Spinner und kein hängenbleibender Invoker. |
| Estuary | Reversibler Skinwechsel; fünf Starts durchführen, danach ursprünglichen Skin wiederherstellen. Keine Skin-Dateien ändern. |
| EPG-Job | Eine bestehende EPG-Aktualisierung manuell anfordern, währenddessen Root und Widgets öffnen. Kein zweiter Import muss vor dem Menü fertig werden. |
| Katalogimport | Bestehende Film-/Serien-/Live-Aktualisierung starten, währenddessen Root mehrfach öffnen; erwartete Daten bleiben sichtbar. Keine Gruppen dafür umkonfigurieren. |
| Provider offline/langsam | Verbindung vorübergehend trennen: Root bleibt lokal erreichbar. Widgets zeigen gespeicherte Daten oder Fehler/Ladehinweis; kein unbegrenzter Verzeichnisaufruf. Danach Verbindung wiederherstellen. |
| Gleichzeitige Widgets | `widget_live_start_group`, `widget_recent_vod`, `widget_recent_series` parallel; EPG/Neuheiten behalten sinnvolle gespeicherte Werte. Bei DB-Zeitlimit kontrollierter Fehler statt Ladekreis. |
| Profilvergleich | Portale aller vorhandenen Typen, Startsender/-gruppen, aktivierte Gruppen, Favoriten, EPG-Quellen/-Mappings, Resume, Remote- und Darstellungseinstellungen unverändert. |
| Neues Profil | Nur separates Wegwerf-Testprofil verwenden: Root zeigt Assistent + ausdrückliche Legacy-Übernahme; kein automatischer Modal-/Migrationslauf. Keine echten Portaldateien beschädigen. |
| Live-Freeze | Startkanal Bild/Ton; erstes OK Info, zweites OK/Runter Bedienleiste, Links Senderliste, zweites Links Gruppen, Hoch/Runter Zappen, Zurück Schließen; Unterfunktionen/Fokus testen. Keine globale Keymap aktivieren. |
| Stop/Neustart | Live stoppen, Root erneut öffnen, Kodi sauber beenden/neustarten; gespeicherte Daten und Programme weiter vorhanden. Service-Abbruchzeit beobachten. |

Die in Issue #38 für **0.1.28** bestätigten vier Live-Fälle sind Ausgangsbefunde;
0.1.28.1 muss dieselben Fälle erneut bestehen. Keine neue Gerätefreigabe aus alten
Tests ableiten. Pro Fall Version, Skin, Kalt-/Warmstart, Laufzeit, Importzustand und
Ergebnis festhalten. Richtwert Root: wenige Sekunden; Überschreitungen dokumentieren.

## Hänger sicher eingrenzen

BOOT-Diagnose liegt auf INFO und benötigt grundsätzlich kein zusätzliches Kodi-Debuglogging.
Nach reproduziertem Start mit Datum/Uhrzeit die XCMate-BOOT-Zeilen aus `kodi.log`
und bei Rotation `kodi.old.log` sichern; Kodi-Invoker-/Thread-Zeitstempel beibehalten.
Kein öffentliches Rohlog hochladen, es kann fremde Add-on-/IPTV-Zugangsdaten enthalten.

Erwartete Folge: ENTRY → MAIN_IMPORT_BEGIN/DONE → ROUTER_INIT_BEGIN/DONE →
DISPATCH_BEGIN → ROUTE → PORTALS_IMPORT_BEGIN/DONE → ROOT_MENU_BEGIN →
PORTALS_LOAD_BEGIN/DONE → HOME_MENU_BEGIN → DIRECTORY_DONE → HOME_MENU_DONE →
ROOT_MENU_DONE → DISPATCH_DONE. DONE enthält `duration_ms`; Fehler enthält
`*_FAILED error=...` und START_FAILED. Letztes BEGIN ohne Abschluss eingrenzen:

- Kein ENTRY: Kodi startet den Python-Einstieg noch nicht oder hängt schon in nativen Grundlagen.
- MAIN_IMPORT_BEGIN ohne DONE: Import-/Addon-Initialisierung vor Router.
- PORTALS_LOAD_BEGIN ohne DONE: lokaler Profil-/Dateizugriff.
- HOME_MENU_BEGIN ohne DIRECTORY_DONE: Kodi-Menü-/Lokalisierungs-/ListItem-Aufbau.
- DIRECTORY_DONE vorhanden: Directory bereits abgeschlossen; weitere Kodi-/Skin-/Autoplay-
  Aktivität untersuchen, nicht vorschnell einen fehlenden Directory-Abschluss behaupten.

Bei einem erneut lange hängenden Start Zurück/Abbrechen benutzen und Marker sichern;
keine weiteren Cache-Resets als Diagnosevoraussetzung. Exception-Meldungen und argv
werden vom neuen Tracer bewusst nicht geschrieben. Der native Ursprung bleibt offen,
wenn nur der BEGIN-Marker bekannt ist.

## Regulärer Repository-Updateweg – erst nach ausdrücklicher Freigabe

Bis zur Abnahme zeigt `main` weiterhin die veröffentlichte 0.1.28. Der PR allein
veröffentlicht nichts. Erst nach erfolgreichem Gerätetest und explizitem Review/Merge
baut der bestehende Main-Push-Workflow den Index und das **neue** ZIP 0.1.28.1;
0.1.28 niemals mit anderem Inhalt ersetzen. Vierstellige Kodi-Version wird bereits
vom Builder akzeptiert (`\d+(?:\.\d+){2,3}`), das Repository-Addon bleibt 1.7.0.
Danach in Kodi: **Meine Add-ons → Add-on-Repository → GS Media → Kontextmenü →
Nach Aktualisierungen suchen**, anschließend XCMate aktualisieren und 0.1.28.1 prüfen.
Kodi neu starten. Profile bleiben erhalten; kein Neu-Einrichten von Konten.

## Rollback ohne Profilverlust

Kodi beenden; aktuelle Profilsicherung behalten. Offizielles unverändertes XCMate-
0.1.28-ZIP aus dem bestehenden Repository lokal installieren bzw. in Kodi die
entsprechende ältere Version wählen. Falls nötig automatische XCMate-Updates für den
Rollback vorübergehend deaktivieren, anschließend bewusst wieder aktivieren. Keine
Deinstallation samt Benutzerdaten, keine DB-/Cache-Löschung. Dieser Hotfix führt keine
Schema-/Profil-Migration durch; die vorhandenen Daten sind weiterhin nutzbar.
0.1.28 kann den ursprünglichen intermittierenden Fehler weiter zeigen. Ein Wechsel
auf 0.1.27 wäre eine separate Entscheidung mit älterem Funktionsumfang, kein Standard-Rollback.
