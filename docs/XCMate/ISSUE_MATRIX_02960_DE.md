# .60 – Issue-/Abnahmematrix

| Bereich | Umsetzung / Hostnachweis | Geräte-/Freigabestand |
|---|---|---|
| #284 Live-Home | Belegter Laufzeit-URL-Vergleich durch native Compilerentscheidung ersetzt; echte 2.2.3-Home-Logoreihe, 88 Sender, zwei Hero-/drei Logo-Pixelnachweise, keine Fokuswiedergabe | Android NOT_TESTED; tatsächliche Box-B-Dateien nicht gelesen |
| #284 TMDB-Test | Private optionale Bearer-Konfiguration, begrenzter Hintergrundtest und konkrete Statuscodes, Rate-Limit/Retry-After | Echte eigene TMDB-Authentifizierung auf Box B NOT_TESTED |
| #284 EPG-Bildpfad | Konservative Titel-/Jahres-/Episodenidentität, Provider/XMLTV zuerst, vorhandener persistenter gemeinsamer Cache, Quelle/Attribution | Reale Sendungsbilder und Quellenabdeckung NOT_TESTED |
| #281 Medienwidgets | Neuer Nutzerbefund: Reihen bereits scrollbar sichtbar. Bestehende Quellen/Providerpfade unverändert; Host je zehn dekodierte synthetische Providerposter und exakte Klickziele | Reale Poster-/Klickziel-/Neustartabnahme weiter offen |
| #283 / .59 Import und Return | Raw unverändert; sämtliche vorhandenen Regressionen erhalten | Bestehende Android-/Decoder-Gates bleiben offen |
| #282 Live-View | Referenz geprüft; kein alter Versionsstand/zusätzlicher Previewdialog blind übernommen | Eigenständiger historischer Draft; kein Merge |
| #280 TVmaze | Nicht integriert | Separates Experiment; keine neue Freigabe |
| Skin / Daten | Explizite Vier-Dateien-Übernahme mit Hashen/Diff/Backup/Restore; keine automatische Anwendung, keine URL-/Bindingänderung | Box A/B unangetastet; Nutzer-Opt-in und reale Abnahme erforderlich |

Kein Host-PASS als Android-PASS, kein Merge/Release und keine Schließung von Issues.
