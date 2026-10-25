# XCMate Wizard – isolierte TESTBOX-PREVIEW (NICHT freigegeben)

**Branch:** `feat/xcmate-wizard-second-box-preview-20261025`, aus dem aktuellen `main` `0.1.29.35`. **Kein Produktiv-Release**, keine Änderung an der Hauptbox.

## Was der Preview-Branch tatsächlich ergänzt

- Für einen **komplett leeren Portalbestand** bei erstem echten XCMate-Root-Aufruf: **bestehenden nativen Setup-Wizard automatisch öffnen**. Keine Pop-up-Schleife nach Abbruch, manuelle Wiedereinstiegsmöglichkeit bleibt.
- Gespeicherte bestehende Profile, einschließlich nur deaktivierter Konten, **lösen kein Autostart-Setup aus**. App-Startup/Back/Home/Live-/Medienfunktionen unverändert.
- Nach **Scan ausgewählter Kategorien**, vor finalem `Speichern`: **optional Startgruppe und Startsender aus temporärer Staging-SQLite auswählen**; erst finaler transaktionaler Save übernimmt diese Daten, keine automatische Stream-Wiedergabe.
- Vorhandene Setup-Implementierung (vorhanden auf .35): Xtream/M3U/Stalker-Kontoaufnahme, Gruppen-Checkboxen **vor** Import, Auswahl XMLTV/Provider-EPG, lokaler Scan mit Progress, Staging, Prüf-/Save-Transaktion; dieser Preview-Draft ersetzt sie nicht und behauptet **keine** schon bestandene neuere-Kodi-Android-Abnahme.

## So kommt das ZIP auf die zweite Box

1. Nach Erstellung dieses Branch-Draft-PR unter **Pull Requests** den PR öffnen → **Checks** → `Publish GS Media Kodi updates` (das Workflow-PR-Ereignis baut NICHT produktiv).
2. **Nur wenn der Check erfolgreich grün ist:** Den **`xcmate-review-...`**-Artifact unter dem zugehörigen **Actions-Run** laden. Das GitHub-Actions-Artifact selbst ist ein Transport-ZIP, darin befindet sich das echte installierbare **`plugin.video.xtreammate-0.1.29.35.zip`** und die **`.sha256`**. **Transport-ZIP zuerst entpacken, erst das innere Add-on-ZIP in Kodi installieren.**
3. Das Paket trägt in `addon.xml` bewusst weiterhin die Basisversion **0.1.29.35**, damit eine neuere offizielle kumulative .36/.37-Version weiterhin als reguläres Update erkannt wird. Es ist **kein öffentliches .37-Release**. Die Prüfsumme/Branch-Commit-SHA der konkreten Build-Artifacts für Testnotizen aufschreiben.
4. **Nur** auf der **zweiten Box mit leerem XCMate-Setup**: `Kodi → Einstellungen → Add-ons → Aus ZIP-Datei installieren` (falls Sicherheitsnachfrage erscheint, nur die bewusst selbst gewählte vertrauenswürdige lokale Datei). Kodi 21.x Basistest; Kodi 22 Pre-/RC-Version **nur** ausdrücklich isoliert, Kompatibilität ist **NOT_TESTED**.
5. Die vorhandene Hauptbox bleibt auf dem zugelassenen OTA-/Upgradepfad; **keine Installation dieser Preview darüber**. Test-Zugangsdaten/Portal-URLs nicht ins GitHub-Issue posten.

## 12 Checkpoints – bis echte Geräteabnahme NOT_TESTED

| ID | Erwartung |
| --- | --- |
| WB-01 | Kodi-Neuinstallation auf Testbox: Add-on lässt sich installieren, Versions-/Dependencydialog verständlich |
| WB-02 | Beim allerersten XCMate-Öffnen ohne Portal erscheint Wizard automatisch |
| WB-03 | Anbieterart wählen (Xtream Codes, M3U-URL/Datei, Stalker) – noch keine Falschbehauptung, alle real testen |
| WB-04 | Accountname und Test-Zugangsdaten eingeben; sinnvolle Validierungs-/Netzwerkfehler ohne Klartext-Geheimnisse |
| WB-05 | Vor Komplettimport Kategorien getrennt Live, Filme, Serien mit Checkboxen auswählen, keine ungefragten Vollimporte |
| WB-06 | EPG-Quelle(n) inklusive Provider und DE/AT-Presets gezielt wählen, leere/fehlerhafte Daten neutral |
| WB-07 | Realer Scan zeigt nicht blockierende Fortschritte, Counts und Ergebniszusammenfassung |
| WB-08 | Startsender (optional) aus zuvor selektierter Live-Gruppe auswählen, ohne abzuspielen |
| WB-09 | Erst nach Bestätigung `Speichern` Portal/Group/Start-SID persistent; Home funktioniert |
| WB-10 | Unterbrechen/Abbrechen während Eingabe/Scan/Save: kein halbes aktives Portal, erneuter Setup-Versuch möglich |
| WB-11 | Nach Kodi-Neustart vorhandenes Testkonto: kein Autowizard, Cover/EPG/Startsender persistiert soweit Quelle |
| WB-12 | Erstmalig neuere Kodi-/Android-Basis: Live/Guide/Medien/IR/Back/Resume, Kodi-Logs/Build-SHA erfassen |

## Technische Abgrenzung

Dies ist ein **früher Wizard-PREVIEW-Draft** für zweite Box, nicht die vollständige .37-Abnahme. Hosttests sind keine Android-Bestätigung. Bei `FAILED`-Workflow oder noch nicht erschienenen Artefakten ist **kein verifiziertes Installations-ZIP verfügbar**.

Reguläre Roadmap: `.36` Performance/Genresuche, **`.37` Wizard vollständig inklusive etwaiger Testbox-Korrekturen**, danach `.38` zweispaltiges Mini-EPG und volle Navigation. Wizard-Draft nach .36-Merge **auf neueste main portieren**; niemals ältere Branches direkt zum Release mergen.

[Wizard-Pflichten #43](https://github.com/artattakk-creator/kodi-noodleprivate/issues/43) · [Original-Parallelauftrag](CODEX_PARALLELAUFTRAG_WIZARD_NEUBOX_KODI21_22_20261025_DE.md).
