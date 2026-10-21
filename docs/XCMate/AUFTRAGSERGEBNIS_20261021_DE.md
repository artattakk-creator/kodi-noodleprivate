# Konsolidierter Entwicklungsauftrag – prüfbarer Bearbeitungsstand

## Empfohlene nächste Geräteprüfung

**Zuerst nur 0.1.29.8 / Draft PR #76 testen.** Der Kandidat enthält Fokus- und
Fensterstart-/Back-Reparatur sowie kompatibles Popup-Routing. Testpaket und
Android-Prüffolge: [Hotfix-Dokument](HOTFIX_0298_NAVIGATION_DE.md).
Die aktuellen Produktivpakete 0.1.29.7 und Rückfall 0.1.29.6 bleiben unverändert.
Keine dieser Arbeiten erteilt einen main-Merge oder Release.

| Auftrag / Issue | Konkretes Ergebnis | Host / native Abnahme |
|---|---|---|
| P0 #73, Regression #67 | Gültige interaktive Fokusziele je Modus; nie Label 501 oder versteckte 120. Native Action-Items behalten Home, Legacy-Routen ankern vor dem Fensterstart; Owner-Sperre über die ganze Lebenszeit, kein Home-Update beim Schließen. Schnelle bewusste Back-Eingaben während des Abschlusses werden abgefangen | 0.1.29.8, 558 Tests, GitHub-Workflow PASS vor reinem Roadmap-Abgleich; Android NOT_RUN |
| Popup-Routing #75 | Eigene Dialog-Aktionen sind nicht als navigierbare Verzeichnisse markiert; gültige alte Directory-Aufrufe enden erfolgreich genau einmal, echte Routenfehler bleiben Fehler | In #76 enthalten, gezielte Routentests |
| Hierarchie #59, Stop/Resume #40 | Back-Ebene, Auswahl-/Staffel-/Episodenposition und Übergänge geprüft; funktionierende Player-/Live-Logik bytegleich | Automatisiert abgedeckt, echte Android-IR-/Stop-/Audio-/Resume-Abnahme offen |
| UI #74 | Fester Kopf, Weiter ansehen → Favoriten → Neu, große 2:3-Poster, mehrzeilige Titel, native vertikale Scrollgruppe | Separater 0.1.29.9 / Draft #77, 564 Tests; Lesbarkeit/IR/Android NOT_RUN |
| Artwork #41 | Bewusste Profile/Auto/Experte >4 GiB, Reserve am Ziel, tatsächliche Bildbytes, persistente Vollinventarisierung aller verfügbaren lokalen Bild-URLs, priorisierte Einzelqueue, getrennte Quota/Disk/Offline-Pausen, geprüfte lokale/USB-Migration mit erhaltenen Originalen | Separater 0.1.29.10 Feature-Draft, 582 Tests; direkte SMB-/VFS-Freiraumfähigkeit noch offen, reale USB/SAF-Abnahme NOT_RUN |
| 0.1.30.1 / PR #50 | Vorhandener Theme-Draft und 98 Originalassets erhalten; konkreter Selektor-/Geometrie-Abgleich für spätere Medienreihen dokumentiert | Keine vorgezogene Integration; erst positive Android-Abnahme |

## Analysegrenzen

Die zwei Home-Plugin-Aufrufe gegen 22:50:04 waren zwei absichtliche Back-Drücke
des Nutzers. Sie werden weder im Test noch in der Dokumentation als interne
Doppelaufrufe ausgegeben. Der historische 15-Sekunden-MODAL_TIMEOUT zeigt eine
blockierte Übergabe, identifiziert aber das damalige aktive Dialogfenster nicht.
Neue reduzierte Traces erfassen numerische Fenster-/Dialog-IDs, Modus, Action,
Monotonic-Zeit und Dispatcher-ID; keine privaten Routenargumente/URLs.
Kein fremder Dialog wird pauschal geschlossen.

514/512 MiB und READY/SPACE_FULL/PENDING waren unterschiedliche Momentaufnahmen;
sie beweisen keine physisch volle Android-Box. Datenbank-OK bedeutet nur die
letzte erfolgreiche Prüfung, keine Garantie aller Bilder. Fehlende Provider-URLs,
HTTP-/Formatfehler, Kapazität und DB-Zustand werden getrennt bewertet.

## Integration nach positiver Android-Abnahme

1. Hotfix-Geräteprotokoll vollständig ausfüllen, insbesondere 10× Filme/Serien/EPG,
   echtes doppeltes Back, keine versteckten Fokusziele, Play/Stop ohne Restton,
   Cursor/Resume und 20 Minuten Stabilität. Fehler blockieren jede Integration.
2. Danach den isolierten UI-Kandidaten prüfen. Der Artwork-Kandidat ist ein
   Geschwister-Branch und wird separat geprüft; seine höhere Testversionsnummer
   ist keine Produktivreihenfolge und kein automatisches Upgradeziel.
3. Auf einem neuen Integrationsbranch von PR #50 die abgenommenen Änderungen
   zusammenführen. Same-file-Konflikte in app_routes, home_menu, media_window,
   media_art und XML semantisch lösen, keine grobe Dateiersetzung.
4. Theme-Decorator auf verschachtelte Layouts erweitern, Titeltext und Postermaß
   bewahren, Such-Icon/Gradient an neue Geometrie anpassen; 98 Originalgrafiken
   samt Prüfsummen erhalten. Alle Hosttests und Paketreproduzierbarkeit erneut
   ausführen, danach echte Android-Kombinationsabnahme.
5. Nur nach ausdrücklicher Freigabe main/Release/Produktivindex aktualisieren.
   Issues bis realer Abnahme offen lassen. Keine Portal-/DB-/Bildlöschung.

Die zwischenzeitlich in main dokumentierte neue Priorität für die horizontale
Programmzeitschrift #57 wurde unverändert erhalten. Ihre Implementierung ist
nicht Bestandteil dieses Navigations-/UI-/Artwork-Auftrags. Die hier vorbereiteten
Feature-Drafts greifen ihrer Geräteabnahme oder Veröffentlichungsreihenfolge nicht vor.

## Schutz des vorhandenen Arbeitsstands

PR #50 bleibt bei 0840f7ccfb99bafb8ade5fb18c79e85b202660cc.
Die 35 bereits vorhandenen privaten Workspace-Änderungen stimmen weiterhin
mit dem vor Arbeitsbeginn erstellten SHA256-Manifest überein. Es wurden keine
privaten Logs/SQLite-Dateien/Portaldaten ins Repository hochgeladen.
