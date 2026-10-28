# XCMate .52 – Ursachen, Reparatur und Grenzen

Basis: aktuelles `main` .51, Commit `2a9a47736384e6af8e1384fddd5d719092cea9cb`. Auftrag: neuer vollständiger Nutzerauftrag .52; #257 vollständig mit Kommentaren gelesen, außerdem #242, #231, #232, #58, #98, #183 und #100. Der ältere Dokumentationsvorbehalt in #257 ist durch den ausdrücklichen neuen Implementierungsauftrag überholt. Kein Merge, keine Geräteaktion, keine Skinänderung.

## EPG: tatsächlicher Codebefund

Die frühere Ein-Tages-Löschung ist bereits seit .44 entfernt. Sie wurde in .51 nicht erneut als Ursache gefunden. Der gemeinsame Faktenindex kann bereits sieben lokale Kalendertage Vergangenheit und heute plus 20 zukünftige Tage behalten. **Die beiden Master-Importer `stream_epg.import_source` und `guide_store.import_cache` filterten aber weiterhin bei `now + 10*86400`.** Dadurch waren gespeicherte Fakten und `guide_v1.sqlite` inkonsistent. Ein reiner Fernzukunft-Feed konnte zudem mit falschem Abschlussstatus erscheinen.

Beide Importer verwenden jetzt dieselbe bestehende Kalendergrenze: Beginn des Tages −7 inklusive bis Beginn des Tages +21 exklusiv. Programme, die die linke Grenze überlappen, bleiben lesbar. Keine vorgelagerte Begrenzung auf zehn Tage. Keine automatische Löschung alter Benutzerdateien oder bestehenden EPGs. Nicht gelieferte Tage werden weder erfunden noch als vorhanden ausgewiesen.

Die additive, transaktionale LastGood-Veröffentlichung aus .44 bleibt erhalten: kürzere Quellen löschen weder gültige Vergangenheit noch Zukunft, Parserfehler und Abbruch veröffentlichen keinen halben Master. Nach Lieferung eines ärmeren Eintrags desselben verifizierten Events bleiben bereits gespeicherte Beschreibung und rich Facts erhalten. Andere Titel oder widersprüchliche Episoden werden nicht als Bildspender behandelt. Der bestehende `BACKUP_REQUIRED`-Schutz für gefüllte EPGs bleibt aktiv und wird getestet; bei fehlender verifizierter Sicherung findet kein Download statt. Ein blockierter Refresh ist **kein** erfolgreicher Import.

Ein weiterer bestätigter Codefehler: Eine fehlende Provider-XMLTV-Adresse (`None`) führte vor den externen Quellen zu `.startswith` auf `None`. Jetzt sind leere Provideradressen zulässig; auch ein Fehler beim Auflösen dieser Adresse verhindert nicht die übrigen aktivierten Quellen. Provider- und Quellenfehler bleiben als getrennte feste Codes sichtbar. Bei korrekt gespeichertem Feed ohne Jetzt-Sendung wird `READY_NO_NOW` statt einer fehlgeschlagenen Veröffentlichung gemeldet; der Kurzcache bleibt dann erhalten.

## Quellen und gemeinsame Sendungsdaten

Es bleibt bei `guide_v1.sqlite`, seinem bestehenden qualifizierten Eingangsarchiv und `programme_artwork.sqlite`/`programme_meta46.sqlite`. Kein zweites EPG-System. Die additive Tabelle `source_aliases52` liegt in der bestehenden gemeinsamen Fakten-/Artworkdatenbank. Sie verbindet SID, stabile Quelle und Kanal-ID; unterschiedliche IDs werden nur durch den vorhandenen konservativen, eindeutigen Sendernamenabgleich als automatische Ergänzung zugelassen. Unklare Namen werden nicht geraten. Bereits indexierte ältere M3U-/STB-Profile mit konfiguriertem XMLTV verwenden ebenfalls den bestehenden Streaming-Importer; der bisherige nicht indexierte STB-Bulk-/Short-Fallback bleibt erhalten.

Das bestehende Masterprogramm gewinnt bei widersprüchlichen überlappenden Zeitintervallen. Andere aktivierte, verifizierte Quellen ergänzen wirkliche Lücken; nahezu identische Sendungen ergänzen fehlende Details statt doppelt aufzutreten. Staffel/Episode und normalisierter Titel werden zur Spenderprüfung herangezogen; bloße Titelähnlichkeit genügt nicht. Widersprüchliche nichtleere Beschreibungen sperren ebenfalls die Bildspende; alte unqualifizierte Compatibility-Fakten umgehen nicht den bisherigen Text-/Quellprüfer. Quellenschlüssel sind stabil und nicht die Position im Quellenmenü. `field_sources52` dokumentiert die Herkunft ergänzter Felder; Source-Key, Kanal, Event-Fingerprint und `updated52` bleiben erhalten. Bild-URLs, Genre, Staffel/Episode, Besetzung und Regie werden aus echten XMLTV-Fakten übernommen. Bereits vorhandene lokale Bildreferenzen, Event-Keys und Bildjobs werden weiterverwendet; keine neuen Downloads beim Fokus und keine Cache-Löschung.

Explizite quellqualifizierte manuelle Mappings bleiben strikt. Dieselbe Kanal-ID in zwei Quellen wird dadurch eindeutig aufgelöst. Es gibt **keinen** automatischen Wechsel auf eine andere Quelle, wenn die vom Nutzer fest gebundene Quelle leer ist. Legacy-Zuordnungen behalten ihren Kanalstring und Vorrang; für sie werden keine abweichenden Kanalnamen geraten. Quellenreihenfolge, JSON-Mappings, Gruppen und Portaldateien bleiben unangetastet.

Großer Guide, Mini-EPG, Infobar und Widget verwenden den vorhandenen `local_epg`-/`programme_snapshot47`-/`programme_events46`-Datenpfad mit derselben Ereignisidentität. Die Erweiterung verbindet lokal bereits veröffentlichte Fakten auf diesem Pfad; sie öffnet keinen Netzwerkzugriff. SQL-/Seitengrößen sind begrenzt, UI-Reads read-only. Die bestehende explizite Guide-Diagnose erhält eine Quellen-/Tagesmatrix (28 Kalendertage), reale Intervallunion statt doppelt gezählter Sekunden, echte Tageslängen bei Sommer-/Winterzeit und `last_good`. Kanal-IDs sind in der Matrix gehasht. Auch frühere .46-Fakten der Tage 11–20 zählen ohne Reimport. Bei Sperre/Budgetfehler ist Abdeckung unbekannt, nicht 0 Prozent. Diese Diagnose wird nicht beim Fokuswechsel ausgeführt.

## Serien nach Einrichtung

Gruppenauswahl und dauerhafte Worklist existierten bereits. **`sync_kind(only_categories=…)` verwendete jedoch einen leeren/veralteten Kategoriencache, ohne fehlende angeforderte Kategorien nachzuladen.** So konnte ein bestätigter Auftrag enden, bevor irgendeine neue Serie angefordert wurde. Der nachgewiesene Hostfehler erklärt einen möglichen Pfad; ohne Geräte-Trace wird er nicht als einzige Android-Ursache behauptet.

Die vorhandene Queue wird weiterverwendet: bestätigte neu aktivierte Seriengruppen werden gebündelt eingereiht, fehlende Heads ausgewählter Gruppen nach Neustart erkannt. Nur angeforderte fehlende Kategorienmetadaten werden im Worker aktualisiert, anschließend nur diese Gruppen importiert. Vorhandene Live-/Film-Heads und Serienfortschritte bleiben erhalten. Ganze Worker-Laufzeit durch nicht blockierende OS-Sperre geschützt, unabhängig von Jobdeadline; veraltete Fehlerstatus werden nicht mit einem neuen gültigen Import verwechselt. Keine endlosen automatischen Resets erschöpfter Jobs. Speichern mehrerer Gruppen erzeugt einen atomaren Worklist-Schreibvorgang.

In der Serienansicht wird `gespeichert/empfangen` während des Imports angezeigt. Unter der vorhandenen Serien-Gruppenauswahl gibt es `Serien-Nachimport` mit Status, gezieltem Wiederholen fehlgeschlagener/abgebrochener Aufträge und Abbrechen. Abgewählte Gruppen werden nicht weiter importiert. Abbruch wird kooperativ im Datenstream erkannt und veröffentlicht keinen Teil-Head. Im Service folgt die bestehende Widgetveröffentlichung und native Reload-Brücke; die vorhandene BINGIE-Verknüpfung wird nicht neu geschrieben. Fehlt im fremden Skin die bestehende Reload-Unterstützung, bleibt der vorhandene explizite Blockierstatus bestehen; keine heimliche Skinmodifikation.

## Erste Infobar

Das vorhandene Auflösungsfeld erhält einen kleinen Rahmen mit der vorhandenen neutralen Textur. Breite und Höhe stammen ausschließlich aus `Player.Process(VideoWidth)` und `Player.Process(VideoHeight)` der eigenen aktiven Kodi-Session. Nur vollständige ganzzahlige Paare 1–16384 werden gezeigt. Fehlende Werte werden neutral dargestellt, Rahmen verborgen. Kein Sendername, Provider-Label oder Bildschirmmaß als Ersatz.

Bei Live-Session-/Senderwechsel werden Werte sofort verworfen. Zwei gleiche reguläre Samples sind erforderlich, damit ein spät freigegebener alter Decoderwert nicht sofort neu angezeigt wird. Das bestehende Zwei-Sekunden-Sampling bleibt bestehen; es gibt keine Zusatzabfragen, Threads oder RPC. Damit kann die bestätigte Pixelanzeige beim ersten Öffnen bzw. Umschalten etwa zwei Sekunden später erscheinen. Audio und übrige Infobardaten behalten ihren Datenpfad; Film-/Serien-Metadaten behalten ihre sofortige Abfrage. Kodi kann keine kryptografische Zuordnung einzelner InfoLabels zu einem Decoder garantieren; reale Kanalwechsel und Box-spezifische Labelverfügbarkeit bleiben Gerätegates.

## Reproduzierbarer Vergleich .51 → .52

`REPRODUKTION_02952.json` enthält tatsächliche Messwerte desselben synthetischen Hosts. Ausführbar mit `PYTHONDONTWRITEBYTECODE=1 python tools/probe_xcmate_02952.py /pfad/zum/checkout label` (Checkout muss Tests und Quellen enthalten; keine Kodi-Installation nötig). Für den Vorherlauf wurde ein unverändertes Archiv des oben genannten Main-Commits verwendet.

| Prüfung | .51 | .52 |
|---|---|---|
| Master nach Feed −7/0/+11/+20/+21 | −7 und 0 | −7, 0, +11, +20; +21 korrekt ausgeschlossen |
| Kürzerer Folgefeed nur heute | vorherige 2 erhalten | vorherige 4 erhalten |
| Beschreibung aus qualifizierter zweiter Quelle | leer | `Rich details` |
| Zeitlücke am Folgetag | nicht sichtbar | echte zweite Sendung sichtbar |
| Nachträglich aktivierte Seriengruppe mit leerem Kategoriencache | FAILED, kein Providergruppenaufruf, 0 Serien | READY, exakt Gruppe b geladen, 7 Serien |
| Widgetdaten nach demselben Import | INDEX_MISSING, 0 | READY, dieselben 7 IDs |

Importprobe: 29,187 ms vorher / 29,043 ms nachher für drei winzige synthetische Imports; dies ist **kein Performanceversprechen** und keine Androidmessung. Korrektheit und Datenerhalt stehen hier im Vordergrund. Weitere Hosttests prüfen echte SQLite-Neuverbindung, Parserfehler, DST, manuell/automatisch, Abbruch, 1.201 Serien, doppelte Worker und die bestehende native Widget-Reload-Brücke.

## Offene Freigabebedingungen

Alle echten Gerätefälle auf Box A (21.2) und Box B (21.3) zunächst NOT_TESTED. Keine Aussage über tatsächlich bereitgestellte 20 Tage eines privaten Anbieters ohne Messung. Anbieterzugriff, ARM32-Speicherbudget, Bilddekodierung, Fernbedienung und Kodi-Neustart müssen vor Freigabe am vorgesehenen Gerät geprüft werden. Keine gespeicherten Daten automatisch löschen, kein Profilreset, keine neue Installation. Der vollständige Host-/Paketbericht wird separat mit exakt geprüftem Quellcommit geliefert.
