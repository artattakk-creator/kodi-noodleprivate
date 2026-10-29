# XCMate .56 – Issue-/Abnahmematrix

| Issue | Umfang dieses Kandidaten | Hoststatus / Grenze | Android |
|---|---|---|---|
| #271 Master | Native drei Quellen, RO-Datenübertragung, Live-Grundreihe, gemeinsamer persistierter Event-Bildpfad | Implementiert; kein abschließender Beweis sichtbarer BINGIE-Pixel | NOT_TESTED, W56-* |
| #270 Medien leer | Cache-Lock-/Schreibfehler, Serien-RO-/Primärschlüsselreader, getypte Metadaten, echte Items/Coverreferenzen, bestehende Reload-Hooks | Reproduzierte Codefehler korrigiert; konkrete Box-B-Ursache ohne aktuelle Logs noch nicht gesichert | NOT_TESTED, MEDIA-01/02/03 |
| #266 Live Home | Vollständige gespeicherte Startgruppe, stationseigene Logos/Namen/OK-Ziele auch ohne EPG, 150-Sender-Hostfall | Grundfeed implementiert; Geometrie/Pixel bestimmt unveränderter Skin. Vorhandener optionaler Heroadapter unberührt | LIVE-01 NOT_TESTED; LIVE-02 ohne separate Skinfreigabe BLOCKED |
| #267 Pickerstruktur | XCMate → Widgets, drei bestehende Quellen/URLs | Byte-/AST-Schutz, keine Routingänderung | NOT_TESTED |
| #239 gemeinsames Bild | Gleicher Event-/Quell-/UTC-Beleg, gemeinsame gespeicherte URL; periodische Hintergrundvorbereitung und angekündigte Filme; vorsichtiger eindeutiger Jahreslos-Match | Synthetischer Harry-Potter-/Film-/Event-/Readernachweis; reale Providerbilder und Androiddecodierung offen | IMG-01 bis IMG-04 NOT_TESTED |
| #269 Wizard-Checkpoint | Keine Änderung, keine Geräteursache behauptet; read-only Widgetpfad behebt nicht den Wizard | Weiterhin OFFEN, separater Auftrag erforderlich | Nicht in .56 repariert |
| #265 Wizard-Freeze | .54-Wizard und Import erhalten | Byteidentische Schutzprüfung | SAFE-02 NOT_TESTED |
| #244 historisch | Kein Rückgriff auf alten Branch/Index, vorhandene Regressionen beibehalten | Kumulativ auf .55 | SAFE-01 NOT_TESTED |
| TV Spielfilm | Kein nachgewiesener autorisierter APIzugang | BLOCKED_NO_AUTHORIZED_API | Nicht als funktionierende Bildquelle behauptet |

Keine Issues geschlossen; keine automatischen Merges/Releases, keine Geräte-/Skinänderung. Technische Einzelheiten: `URSACHENANALYSE_02956_DE.md`; Geräteablauf: `ANDROID_ABNAHME_02956_DE.md`; vollständiger Abschlusslauf und Paketbelege im Testbericht und Draft-PR.
