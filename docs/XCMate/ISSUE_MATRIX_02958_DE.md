# Issue-Abnahmematrix .58

| Thema | Code-/Hoststand | Geräte-/DoD-Stand |
|---|---|---|
| #277 A / Anbieter-Schalter | Expliziter sichtbarer Toggle, atomarer Re-Read und geprüfter Save implementiert; bestehender Import/Quellenzuweisung durch SQLite-Integration geprüft | Android NOT_TESTED; echte Providerdaten fehlen |
| #277 B / Medien-Quellenvertrag; #274 Abgrenzung | Provider-only in nativem Widget und Worker; gespeicherte manuelle Dateien erhalten; keine Helper-Abfrage in Medienwidgets | Android NOT_TESTED |
| #277 B / tatsächliche unsichtbare Film-/Serienreihen | Read-only aktiver Profil-/generierter Include-/Home-Consumer-Diagnosepfad implementiert | Ursache auf Box B BLOCKED_DEVICE_ACCESS; kein behaupteter Sichtbarkeitsfix |
| #277 C / Live-Back-Freeze | Diagnoseblinden Fleck vor blocked()-Guard geschlossen; native Queue/Prepare/ACK/Strategie getrennt; bestehender Stop unverändert | Nativer Freeze-Fix BLOCKED_DEVICE_ACCESS; Android NOT_TESTED |
| #276 / vollständige Live-Reihe; #252 / Picker | Bestehende Startgruppe ≥88, keine Wiedergabe beim Fokus, URLs/Ordner raw-identisch | Live Home bisher vom Nutzer nicht eingerichtet: NOT_TESTED |
| #266 / großer Hero | Bestehendes separates Opt-in unverändert | Nicht aktiviert; NOT_TESTED |
| #269 / Wizard | Vollständig unverändert; bestehende Regressionen beibehalten | Kein eigener Wizard-Umbau |
| #273/#274 / Live-Sendungsbildresolver | Bestehende .57-Implementierung unverändert; Helper 5.4.16 laut Nutzer bestätigt | Echte Live-Bilder in dieser Sitzung NOT_TESTED |

Historie .57: Providerbedienung FAIL/UNUSABLE, Film-Home FAIL, Serien-Home FAIL, Live-Back FAIL; Live-Home bewusst nicht eingebunden. Diese Befunde bleiben erhalten. Alle neuen .58-Gates sind NOT_TESTED. Kein P0 als vollständig gerätebehoben, kein Issue geschlossen, kein Merge/Release.
