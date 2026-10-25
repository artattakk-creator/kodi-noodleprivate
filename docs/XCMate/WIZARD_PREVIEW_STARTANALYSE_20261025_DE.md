# Wizard #43 – unabhängige WIZ-0-Entwicklung, noch kein Testkandidat

Stand 25.10.2026 (Europe/Berlin), Basis main **46b4f9f / .35**. Parallel zu .36-Draft #163, unabhängiger Branch `feat/xcmate-wizard-staging-preview`. **Kein installierbares Preview, kein vollständiger Wizard-PASS, keine Installationsaufforderung.** Keine Versionsänderung oder Veröffentlichung. Nach .36-Merge auf dann aktuelles main portieren; Integration kumulativ .37.

Verbindlicher Vollvertrag: Issue #43 und `CODEX_PARALLELAUFTRAG_WIZARD_NEUBOX_KODI21_22_20261025_DE.md`, aktualisierte Release-Roadmap. Box A unverändert, Box B später frisches Kodi 21.3; 22 RC1 ausschließlich optionaler separater Prerelease-Test.

## Tatsächlicher Bestand und erste Änderung

Der historische Codehinweis „scan_contents lädt vor Checkboxen alle Kataloge“ entspricht nicht mehr dem aktuellen Einstieg: `setup_wizard.setup` öffnet `setup_window.open_setup`, dieser verwendet bereits `setup_draft.Draft`. Vorhandene native Setup-UI zeigt getrennte Gruppen/Checkboxen, Quellenwahl, Scan und explizites Speichern. `Draft.discover` authentifiziert und fragt Kategorien ab, `Draft.scan` arbeitet ausgewählte Gruppen über `adapter.entries`, Staging und spätere Veröffentlichung sind bereits vorhanden. Diese vorhandene Architektur wird weiterverwendet.

Konkrete Lücke: `main.Router._root` zeigt bei fehlenden aktiven Portalen bisher **nur einen Menüpunkt**, keinen automatischen Assistenten. `setup_draft.dispose` entfernt den temporären Stagingordner; sichere Wiederaufnahme nach Prozess-/Stromabbruch und verbliebene neue-ID-Transaktionen müssen gesondert geprüft werden. Der Testdateiname `setup_first_run` allein beweist keinen automatischen Root-Einstieg und kein Android-E2E.

Erste implementierte Grundlage ist `setup_entry_policy.eligibility` mit acht Hosttests: expliziter leerer Root-Kontext darf angeboten werden; vorhandene **auch deaktivierte** Profile, Widgets/RunPlugin, Portal-Hints und Modals verhindern automatische Einrichtung. Nur Entscheidung, **noch keine Aktivierung in root**. Keine Accounts/Quellen/Cachedateien geschrieben und keine bestehende Installation beeinflusst.

## Nächste Implementierungsschritte / echte Blocker

1. Directory-End/Busy10138/Owner-Handoff für Root→native Setup-UI reproduzieren, SingleFlight mit bestehendem `window_navigation.ownership` über Interpretergrenzen; nach Cancel keine Root-Neuöffnungs-Endlosschleife. Fremde Modals weder schließen noch ignorieren. **Integrationsblocker vor Root-Aktivierung.**
2. Bestehende `SetupWindow`/`Draft` wiederverwenden: Account/Name/Typ/Auth, Kategorien vor Streamscan, getrennter Live/VOD/Serie-Opt-in. Erst nach Auswahl und Quellenwahl importieren, keine Default-Alle-Flut. Xtream/M3U-Datei/M3U-URL/Stalker tatsächlich getrennt testen, keine behaupteten fehlenden Adapterfähigkeiten.
3. Alle vorhandenen Profilzeilen schützen; Save-/Rollback-/Readback prüfen, Restart-/Resume-Konzept nur für neuen Stagingaccount. Originaldaten und manuelle EPG-Zuordnungen unverändert. Count-/Progress-/EPG-Mapping-/Coverstatus auf realen Daten prüfen.
4. Erst bei funktionsfähigem Fresh-Install-End-to-End Preview-ZIP+SHA+Head-SHA für **leere Box B** bauen. Preview-Versionsstrategie darf spätere offizielle .36/.37-Updates nicht blockieren; keine .35-Preview auf Box A installieren, keine OTA-Indizes ändern.
5. WIZ-01–12 alle zunächst **NOT_TESTED**; Kodi 21.3- und optionale Kodi22-RC1-Kompatibilität bleiben Gerätegates. Kein Release als „vollständiger Wizard“ aus diesem Grundlagen-Draft.

Konfliktkarte für spätere kumulative Integration: `main.py`, Setup-Module/XML und `library_index.py`/`app_services.py` bei regulären Importen gegen die Genre-Nachindizierung aus .36 prüfen. Dieser WIZ-0-Commit ändert keinen dieser gemeinsamen bestehenden Pfade. Live-/Guide-/Suchmaske/Icon/Autoplay bleiben erhalten. #43 bleibt offen.

Reproduktion der ersten Grundlage: `python -m unittest discover -s tests -p test_xcmate_wizard_entry_preview.py -v`. Vorhandene Setup-Hosttests werden als zusätzliche Ausgangsprüfung ausgeführt; auch sie ersetzen keinen Geräte-PASS.
