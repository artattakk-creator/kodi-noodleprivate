# .30-C – Jetzt-Sendungen in der lokalen Suche (#140 / A03)

Basis .29 / main 9ce385b. Historisches A03 bleibt FAIL bis zum Android-Retest.
Die neun bestandenen Such-/Live-/IR-/EPG-Regressionen müssen erneut PASS bleiben.

## Reproduzierbare Lücken und Reparatur

Die Suche verwendete nur guide_v1.sqlite. Der große EPG und Now/Next können für
den aktuellen Zeitpunkt zusätzlich bereits gespeichertes Kurzzeit-EPG verwenden.
Bei fehlenden oder nur zukünftigen XMLTV-Daten fand die Suche dessen Jetzt-Titel
nicht. Jetzt gleicher Cache-only-Fallback mit gültigen Start-/Endzeiten, sowohl
alte Vierer- als auch neuere Zwölfer-Caches. Kein Netzwerkabruf/Refresh während
der Suche. Explizite manuelle Zuordnung bleibt maßgeblich und wird niemals durch
einen anderen Provider-/Short-Titel ersetzt. Gültige aktuelle XMLTV-Daten gehen vor.

Die alte Abfrage las alle aktuellen Programme samt Beschreibung. Unbeteiligte
Sender konnten deren globale 50.000-Zeilen-Grenze ausschöpfen. Neue read-only-
Abfragen lösen nur ausgewählte IDs/Aliase auf, lesen nur cid/title/source/start,
in 256er-Blöcken und unter endlichem SQL-Budget. Keine Hydrierung der Langzeit-DB.
Sender-/Gruppenfilter, exakte VOD-/Serienzählung und manuelle Mappings unverändert.
Für sehr große fehlende Short-Guide-Mengen begrenzt ein Zwei-Sekunden-Budget die
Cache-Fallback-Arbeit; EPG_PARTIAL und ein Hinweis statt falscher EPG-Bereitschaft.
NO_EPG / NO_CURRENT_EPG / EPG_UNAVAILABLE unterscheiden fehlende DB, keine aktuelle
Abdeckung und fehlerhafte/gesperrte DB. Sendernamensuche bleibt verfügbar.

Anonymes SEARCH_EPG-Log und Diagnose-Snapshot epg_search: channels, now_count,
xml_now, short_now, manual_count, manual_missing, alias_count, source_count,
name_hits, programme_hits, matched und fester Status. Keine Suchbegriffe,
Programmtitel, Sender-/Portal-/EPG-IDs, URLs oder Zugangsdaten. Diagnose-Menü nutzt
die bestehende feste Stages-/Felder-Allowlist.

## Hostprüfung

```sh
PYTHONPATH=tests:src/plugin.video.xtreammate/resources/lib python -m unittest -v \
  test_xcmate_epg_search_02930 test_xcmate_search_02926 test_xcmate_search_live_02927
```

30 Tests PASS. Fünf neue Reproduktionen: Short-only ohne DB, zukünftiges XMLTV +
aktuelles/abgelaufenes Short-EPG, manuelle Mapping-Priorität, über 50.000 irrelevante
Jetzt-Programme ohne Verlust der relevanten Treffer sowie private Diagnosedaten.
Der Testadapter stellt die neue cache-only Client-Grenze bereit; keine produktive
Such-/Player-Handoff-/Window-Owner-Logik verändert.

## Android (alle neuen Gates NOT_TESTED)

1. Jetzt-Sendung im großen EPG prüfen, denselben echten Titel suchen (A03).
2. Live-Tab zeigt passenden Sender und Titel; Sendername bleibt separat suchbar.
3. Bei null Treffern nur anonymen SEARCH_EPG-Status/Zähler teilen. Besonders
   now_count=0, manual_missing, xml_now/short_now und EPG_PARTIAL unterscheiden.
4. Manuell zugeordneten Sender sowie Programmlücke/Future-only prüfen; keine
   erfundene Jetzt-Sendung oder falsche Quelle.
5. Alle neun bisherigen Regressionen unverändert wiederholen: In-Window-Suche,
   Tabs/Zurück, Film/Serie, Live-Übergabe, IR, großes EPG und Autoplay.

Keine Änderung an Player, Such-Handoff, Keymaps, Portalprofil oder Guide-Daten.
Kein main-Merge/Release/OTA in diesem Draft.
