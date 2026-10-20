# XCMate Space Premium – Theme-/Core-Build, Abnahme und Release-Gates

**Stand: 20. Oktober 2026. Entwicklungsstand von PR #50. Keine Freigabe zur Veröffentlichung.**

## 1. Verbindliche Referenzen

- Repo: https://github.com/artattakk-creator/kodi-noodleprivate
- Draft-PR: https://github.com/artattakk-creator/kodi-noodleprivate/pull/50
- Branch: `feat/xcmate-space-premium-installer`
- Add-on-ID: `plugin.video.xtreammate`, geplanter Core `0.1.30`
- Produktiv am Gerät: `0.1.29.2`, Kodi 21.3 Omega / Android ARM32 / Titan BINGIE MOD
- Autoritative 98 Grafiken: Nutzerarchiv `XCMate_Space_Premium_98_Grafiken_FUER_CODEX.zip`, gültiges originales Mastertracking (98 SHA-256).
- Drive-Master: https://drive.google.com/drive/folders/1UPA7fLKIq21GkA4NzAPEVfLp2BvSpm3y
- Wiederholbarer GitHub-Build: `.github/workflows/xcmate-space-premium-build.yml`
- Paketformat und Installer: `docs/XCMate/THEME_FORMAT_INSTALLER_030_DE.md` (dort frühere historische Blocker-Texte beachten).

## 2. Nachgewiesene Ergebnisse

| Prüfgegenstand | Beleg / Resultat |
|---|---|
| Ursprungs-ZIP | SHA-256 `d39cc1525c7a57c607242872ecf7e0cecf647f9cb1e5f92fa16be5ba8d163e3f` |
| Originale | 98 eindeutige Bildpfade, 98/98 SHA-256-Übereinstimmungen mit finalem Tracker |
| Bilddateien | 98/98 vollständig mit Pillow erfolgreich dekodiert |
| Theme-Metadaten | `theme.json`, `SHA256SUMS.txt`, `README.md`, `LICENSE.txt` |
| Manifest | 98 `required_files`, 106 deklarative logische Asset-Schlüssel |
| Theme ZIP | `themes/xcmate/space-premium/XCMate-Space-Premium-1.0.0.zip` |
| Theme ZIP Länge | **19.772.084 Bytes** |
| Theme ZIP SHA-256 | `8fc7f312a65fa5ecdbe68d3487939a25d685de29717896a0a1113c8d41176ae2` |
| Unabhängiger Rebuild | Offizieller Builder liefert *denselben SHA-256* wie lokale Rekonstruktion |
| Core Icon | `src/plugin.video.xtreammate/icon.png`, unverändertes freigegebenes 512×512-Original |
| Core Icon SHA-256 | `81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135` |
| Core Testkandidat | `plugin.video.xtreammate/plugin.video.xtreammate-0.1.30.zip` mit inkludiertem Original-Icon; SHA256-Sidecar und CI-Paketprüfung |
| Sicherheit | Bounded ZIP/PNG/JPEG/CRC/Hash, Pfad-/Symlink-/Alias-Checks im bestehenden Core, atomare Theme-Revisionen und Stock-Fallback |

### Wichtig: Archivvollständigkeit ist nicht gleich vollständiges Runtime-Rendering

Das installierbare Theme-Paket enthält **alle freigegebenen Bilder** und wurde technisch geprüft. Ob tatsächlich *alle* Grafiken an *jeder* vorgesehenen Stelle gerendert werden, kann nur mit vollständiger Core-Texture-/View-Mappingprüfung und Android-Abnahme nachgewiesen werden. Weitere Renderer-Arbeit **ist offen**.

Aktuell konkret angebunden:
- Hauptmenü: sechs Theme-Icons + motivbezogene Kachel-Fanarts.
- Einstellungen: Icons und Hintergrundbilder für die üblichen XCMate-Rubriken, bei fehlendem Premium-Theme fallback auf das permanente Core-Icon/Fanart.
- Medien und Guide: bestehende WindowXML-Resolver für Hintergrund/Fokus/Panel/Palette; dynamische Providercover bleiben erhalten.

Nicht als vollständig abgenommen:
- Alle EPG-spezifischen Aktionsicons, Media-Buttons und widget-spezifischen Grafiken.
- Live-TV-Sender-/Gruppenliste, Infobar, untere Playerleiste und weitere reine Texturen.
- Originalgrafik-Ausnutzung in zehn Ansichten und visuelle Focus-/Lesbarkeitsprüfung.
- Rendering/Performance auf Kodi 21.3 Android ARM32 IR.

## 3. Installations-/Aktivierungsvertrag

**Themen-ZIP nicht über „Kodi: Aus ZIP installieren“ installieren!** Erst nach Core-0.1.30-Gerätefreigabe in XCMate: Einstellungen → Darstellung & Sprache → XCMate-Designs → lokale ZIP-Datei auswählen; dann aktivieren. Alternativ HTTPS-GitHub-Katalog aus freigegebenem Main nach Merge; die aktuelle Main-Version liefert die neue Theme-Datei vor dem Merge ausdrücklich **nicht**.

Core `0.1.29.2` besitzt den neuen Theme-Installer nicht. Keine Datenlöschung, keine Neuinstallation mit Reset. Der normale Core-Updatepfad muss Accounts, Portale, Favoriten, EPG, Gruppen, Covers, Resume, Startsender und Datenbanken unverändert übernehmen.

Die Designauswahl wird privat in `themes_v1/` geführt. Nach Prüffehler Standardtheme, bestehende alte Revision nicht vorab löschen; laufende Wiedergabe erhält keine erzwungene Umstellung. Kein globaler Titan-BINGIE-MOD-/Kodi-Skin-/Keymap-Eingriff.

## 4. Entwicklervalidierung

Nach Checkout des **Draft-Branches**, Python 3.12 und `Pillow>=11,<13`:

```bash
python -m unittest discover -s tests
python tools/validate_xcmate_catalog.py --output theme-catalogue-validation.json
```

Den reproduzierbaren Theme-Bau auf frischen Staging-Ordner auszuführen, der **genau** 98 Bilddateien sowie `theme.json`, `SHA256SUMS.txt`, `README.md`, `LICENSE.txt` enthält:

```bash
python -B tools/build_xcmate_theme.py --source <isoliertes-staging> --output <neuer-output>/XCMate-Space-Premium-1.0.0.zip
```

Der GitHub-Workflow übernimmt isoliertes Staging, vollen Builder, erneute Core-ZIP-Erstellung inkl. Icon, Artifact-Upload und einen **Draft-Branch-Commit**. Er führt keinen Merge und kein Release aus. Core- und Theme-ZIP werden nach dem Quellstand aktualisiert; `main` bleibt unberührt.

Der Core-Test muss ausdrücklich prüfen:
- Bei fehlendem Theme keine 98 Dateiscans bei jeder Kachel und kein neues UI-Fenster.
- Vorhandenes Core-Icon in `addon.xml` und `plugin.video.xtreammate/icon.png` des installierbaren ZIP.
- 98/98 Bilder, exakte SHA und ZIP-CRC.
- Core- und Theme-ZIP als zwei getrennte Installationsartefakte.
- Stock-Design-Fallback; Theme-Einbau darf laufenden fremden oder eigenen Stream nicht ohne explizites Benutzerziel beeinflussen.

## 5. Abnahme vor Merge / produktivem Release

1. Kodi-Start, aktive Accounts/Gruppen/Filme/Serien/EPG/Resume persistent.
2. Standarddesign nach Core-Update vollständig nutzbar und Originalicon in Add-on-Kachel sichtbar.
3. Lokaler Theme-Import von USB/SMB und aus lokaler Datei; Aktivierung, Fehlerfall, erneutes Installieren, Entfernen, Rücksetzen auf Core.
4. Kein flackerndes/fehlendes Artwork; Schärfe/Transparenz/Font-/Fokus-Lesbarkeit bei 720p/1080p/4K.
5. Vollbild-Live-OSD: OK → Info, OK/↓ → untere Leiste, Links → Sender/Gruppe, Hoch/Runter → ±1; Back nur vorgesehene Ebene schließen, beim tatsächlichen Stream-Exit kontrolliert stoppen. **Bekannter Live-Back-Ladebildschirm-Hänger ist offen**, Ursache ohne Kodi-Log nicht verifiziert.
6. VOD- und Serien-Folge starten; zurück zum Detail/Staffelmenü muss XCMate-eigene Wiedergabe inklusive Ton beenden und Resume erhalten. Separates Issue #40, Fremdstreams nie stoppen.
7. Gruppe-Senderanzahl aus lokalem Katalog, keine zusätzlichen HTTP-Requests; Performance von Kaltstart (aktuell ca. 17 s) messen.
8. CI und Runtime-Gerätetests müssen grün, Benutzerfreigabe vor Merge und Freigabe vor Release explizit.

**Abnahmestatus: Theme-Archiv/Builder verifiziert; Gesamt-UI/Android NOT_RUN. Draft-PR offen. Keine Produktivfreigabe.**
