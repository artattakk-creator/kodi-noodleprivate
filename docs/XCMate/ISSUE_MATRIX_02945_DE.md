# XCMate .45 – Issue- und Abnahmematrix

Alle .45-Androidfälle NOT_TESTED. HOST_PASS nur nach tatsächlichem vollständigen grünen Lauf im separaten Testbericht. Historische .44-Beobachtungen aus #235: >20 Alltags-Live-Backs, subjektiv schneller, mindestens ein Suchtrefferstart, positive Mini/Gruppen/Rail-Beobachtungen. Kein pauschales vollständiges PASS, alte .43-FAIL nicht ungeprüft fortschreiben.

| Issues | Umsetzung / Status | Verbleibendes Gate |
|---|---|---|
| #236/#235 | Kumulativer .45-Draft auf bestehendem historischen freeze-Branch, .44-Referenz unverändert | Vollständige Box-B-Abnahme und ausdrückliche Freigabe |
| #229/#230 | Gemeinsamer konkreter Widget-ListItem-Vertrag,12/24, reale Art/Metadaten, lokale Veröffentlichung, verifizierte native Reload-Hooks | W45-01–10; ohne bestehenden Hook automatische Sichtaktualisierung BLOCKED_NO_RELOAD_HOOK |
| #206/#207/#182 | Lokales Jetzt/Danach/Progress und echte Logos, vorhandene Quellen; optionaler versiongeprüfter reversibler BINGIE-Adapter | Native Layout-/Fokus-/Logoabmessungen auf2.2.3 offen; kein automatischer Fremdskinpatch, Adapter nicht auf Gerät angewandt |
| #195 | Sieben Bereiche, alte IDs/Werte/Aktionen erhalten, PIN6666 ohne Persistenz, direkter Routenschutz | S45-01–05, Neustart; PIN ist UX-Sperre |
| #200 | Zentrale35lokale Glyphen in eigenen nativen und XML-Menüs/Untermenüs ohne neue Fokusziele | M45-01–02, komplette Menümatrix; native nicht anpassbare Kodi-Dialoge ausgenommen |
| #100/#183 | Referenz-Infobar mit echten bestehenden Streamdaten, Vorher/Jetzt/Danach, Datum/Uhr und6Technikfeldern | I45-01–05, Hostvorschau kein Androidpixelbeweis; Bildmuster hat Vorrang vor älterem Schlankheitswunsch |
| #231/#232/#161 | .44-EPG-Publisher/Backup/Zuordnungen geschützt, begrenzter read-only Vorher-Leser | P45-01; Refresh ohne verifizierte konsistente Sicherung BLOCKED; vollständiger #98/#161-Quellchooser FOLLOW_UP |
| #227/#201/#140/#127 | Funktionierende Suche/Genre/Klickpfade geschützt, keine neue Suchmaske | P45-02 + D1–D8; Film und Episode getrennt |
| #223/#224/#220 | Funktionierende Mini-/Gruppen-/Railsteuerung unverändert, zentrale Menüdekorationen | NAV/I45/M45 + A/B; echtes Frameflackern erneut beobachten |
| #225/#226 | Kategorie-/Fokus-/Back-Regeln aus .44 erhalten | C1–C3 und lange Film-/Serienlisten |
| #228/#111/#151 | Bestehende gezielte Cover-/Metadatensuche und Speicherung erhalten | P45-03 + E1–E11; kein neuer globaler Retry/Reset |
| #216/#203/#202 | Kritische .42-Stop-/Exitdateien bytegleich, Modus EIN erhalten, keine Engine-/Keymapänderung | Einzelback→Filmback→5→20, H1–H8; echte Androidstabilität nicht durch Host ersetzt |
| #221/#194 | Bisherige vollständige A–H-Strecke als neue .45-Abnahme übernommen | Historie unverändert, keine automatischen Issue-Closes |

Downloads/Aufnahmen/USB/SMB/Migrationen bleiben nachrangig und werden in .45 nicht neu entwickelt oder am Gerät getestet. Nur Menüzuordnung und Schutz geändert. Box A bleibt unangetastet. Kein Main-Merge, Produktivrelease oder automatische Installation.
