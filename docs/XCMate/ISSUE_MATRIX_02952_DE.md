# XCMate .52 – Issue-/Abnahmematrix

| Issue/Anforderung | Code / Hostbefund | Android |
|---|---|---|
| #257 EPG-Regression / #231 | verbliebene Zehn-Tages-Filter repariert; LastGood bei kürzerem/kaputtem Feed und Metadatenverarmung geschützt; frühere Ein-Tages-Löschung bereits vorher entfernt | EP52-01–05, 09–10 NOT_TESTED |
| #232 sieben Tage / 20 Zukunft | einheitliche lokale Kalendergrenzen, DST und +20-only geprüft; echte Feedmenge bleibt Anbieterabhängigkeit | EP52-03–04 NOT_TESTED |
| #242 gemeinsame EPG-/Artworkbasis | vorhandene Datenbanken, Event-Key und Bildreferenzen weiterverwendet; reiche Source-Facts und lokale gemeinsame Reads | EP52-06, 08–09 NOT_TESTED |
| #58 Quellen/Dubletten | stabile Quelle+CID, echte Lücken, konservative Spenderprüfung, Prioritätskonflikte und Quellenumordnung getestet | EP52-06 NOT_TESTED |
| #98 manuelle Zuordnung | Vorschau-/Mappingcode erhalten, source-qualified Vorrang auch bei gleicher CID getestet; keine neue automatische Mappingänderung | EP52-07 NOT_TESTED |
| #257 Serien-Nachimport | vorhandene Queue repariert/abgesichert, Kategorienrefresh, gezielte SQL-Heads, Progress/Retry/Cancel, native Widget-Reload-Evidenz | SER52-01–06 NOT_TESTED |
| #183 / #100 Auflösung | genaue Kodi-VideoWidth/-Height, eigener Token, Rahmen und neutraler Übergang, bestehende Audioanzeige erhalten | PIX52-01–04 NOT_TESTED |
| .42 Live-Back / .51 Wizard / BINGIE / Medien | Bestandsschutz und vollständige Regressionen PASS, keine neue Player-/Skinarchitektur | REG52-01–04 NOT_TESTED |

**Host gesamt: 2.168 PASS. Gerätefreigabe: offen.** Keine Issues als vollständig auf Android erledigt markieren oder schließen. Fehlende Anbieter-Tage/Bilder/Pixel-InfoLabels sind keine künstlich erzeugten PASS-Daten. Nicht indexierte alte STB-Bulk-/Short-Profile behalten ihren bisherigen Fallback; neue qualifizierte XMLTV-Zusammenführung nutzt den vorhandenen indexierten Pfad. Fehlt ein bestehender BINGIE-Reload-Hook, weiterhin ausdrücklich BLOCKED statt Skinänderung.

Downloads, Aufnahmen, Speicherumzüge, neue Skinadapter oder andere Roadmapblöcke gehören nicht zu .52. Kein Merge/Release ohne ausdrückliche Freigabe.
