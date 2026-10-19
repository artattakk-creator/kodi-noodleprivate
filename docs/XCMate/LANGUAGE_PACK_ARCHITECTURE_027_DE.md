# XCMate – Sprachpakete (Language Packs) / Architektur und Entwicklungsauftrag

**Teilstand PR #28:** [en/de-Lokalisierung mit 207 neuen IDs und 25 Sprachtests implementiert](STABILISIERUNG_027_SYNC_LOKALISIERUNG_DE.md).
Native Kodi-Sprachauswahl bleibt unverändert; englischer Fallback pro Text, deutsche
Altinstallation erhalten. **Installer, externe Packs und eigener Sprachwahldialog weiterhin offen.**


**Entscheidung:** 19.10.2026. **Status:** verbindliche Produktspezifikation; **noch keine neue Runtime-Sprachpaket-Installation oder Downloadfunktion implementiert**. Aktuelles produktives XCMate: **0.1.26**; Funktions-FREEZE für Live-TV-/Remote-OSD.

## 1. Verbindliche Sprachenregel

- **Englisch (`en_GB`) ist die Standard- und technische Fallbacksprache.** In der lokalen Quelldatei `resources/language/resource.language.en_gb/strings.po` liegen derzeit die bestehenden String-IDs (Kodi `msgctxt`, z. B. `#32001`).
- **Deutsch (`de_DE`) bleibt vorinstalliert und verfügbar.** Die bestehende Datei `resources/language/resource.language.de_de/strings.po` ist bereits Teil der produktiven 0.1.26-Version und darf nicht gelöscht oder überschrieben werden. Bestehende Nutzer, die Kodi/XCMate deutsch verwenden, dürfen nicht plötzlich auf Englisch zurückgesetzt werden.
- Eine neue Installation ohne explizite Sprachauswahl verwendet **Englisch** als XCMate-Basis; optional kann „Automatisch – Kodi-Sprache“ angeboten werden. Bei Altinstallationen bestehende Kodi-Sprachauswahl/Benutzerpräferenz **nicht überschreiben**. Fällt eine Übersetzung aus, nur die fehlende Einzel-Zeichenkette auf `en_GB` zurückführen, nicht die gesamte UI oder den Senderkatalog unerwartet umstellen.
- Kodi-Oberflächensprache ist **nicht gleich** dem bereits existierenden Einstellungsfeld `lang_priority`, das zur Filterung von IPTV-Sprachen dient. Beide Optionen und Keys **konsequent getrennt** halten; `lang_priority` niemals als UI-Language benutzen.
- Sprachpakete enthalten **nur XCMate-UI-Strings**, keine EPG-Übersetzungen, keine Account- oder Nutzerdaten und keinen Programmcode.

## 2. Bestehende Kodi-Struktur (verifiziert an `main`)

```text
src/plugin.video.xtreammate/
  resources/
    language/
      resource.language.en_gb/strings.po  # EXISTIERT – Basissprache
      resource.language.de_de/strings.po  # EXISTIERT – Deutsch
```

Dies ist die **native Kodi-Addon-Lokalisierungsstruktur**. Ein eigener, frei gewählter Ordner mit `strings.po` wird **nicht automatisch** durch Kodi mit `xbmcaddon.Addon().getLocalizedString` ausgewertet. Deshalb muss für dynamisch nachinstallierbare Packs entweder eine kontrollierte XCMate-Übersetzungsschicht mit Fallback implementiert oder ein Kodi-kompatibles Sprachressourcen-/Addon-Update-Verfahren geprüft werden. Das Verteilen von zusätzlichen `strings.po`-Dateien ohne Einbindung reicht technisch nicht.

## 3. Zwei Speicherbereiche: Repo-Staging und Nutzerinstallation

**A. GitHub-Staging/Katalog (nicht automatisch als installiert gelten lassen):**
```text
language_packs/
  README.md
  manifest.example.json
  catalog.json                # erst bei tatsächlich freigegebenen Paketen
  fr_fr/                      # zukünftiges freigegebenes Übersetzungspaket
    manifest.json
    strings.po
  es_es/                      # später weitere
```
Dieser Ordner liegt **außerhalb** der aktuellen produktiven Add-on-Runtime und kann später einen kuratierten Katalog speisen. **English/German bleiben in `resources/language/` des Add-ons** als Basispakete; sie werden nicht aus Versehen ersetzt.

**B. Geplanter lokaler Installationspfad auf Kodi (noch nicht automatisch angelegt):**
`special://profile/addon_data/plugin.video.xtreammate/language_packs/<locale>/`
mit genau `manifest.json` und `strings.po`, ggf. einem Cacheindex; Userdata übersteht Kodi-Addon-Updates. Nicht in `special://home/addons/.../resources/language` schreiben, da Kodi-Updates diesen Pfad ersetzen und Schreibrechte fehlen können. Keine Nutzeraccountdaten dort ablegen.

## 4. Späterer UI-Workflow

Unter **Einstellungen → Darstellung & Sprache → XCMate-Sprache**:

1. **English (en_GB) – Basis / immer verfügbar / nicht löschbar**.
2. **Deutsch (de_DE) – bereits vorhanden / beibehalten / nicht löschen**.
3. **Weitere Sprachen herunterladen** – zeigt nur einen **kuratierten, tatsächlich erreichbaren und freigegebenen Katalog**, mit Sprache, Versionskompatibilität, Übersetzungsgrad, Downloadgröße und Autorenhinweisen.
4. **Installierte optionale Sprachen verwalten** – Sprache aktivieren, zurück auf Englisch/Deutsch wechseln, optionales Paket löschen (nicht die aktuelle aktive Sprache löschen, bevor auf sichere andere Sprache umgestellt wurde).
5. **Paket installieren** – von sicherer HTTPS-Katalogadresse oder bewusst ausgewähltem ZIP, mit Hash-/Signatur- und Integritätsprüfung, Limit von Dateien/Größen, gültigen Locale-IDs, zulässiger PO- und JSON-Syntax. Offline-Fehler lokal aussagekräftig anzeigen.
6. **Rückgängig / Fallback** – Fehler beim Neustart, beschädigtes Paket oder ungültige String-ID darf weder Kodi noch andere Add-ons blockieren. Automatisch auf internes `en_GB` zurückfallen; aktives Deutsch bei Altinstallationen respektieren.

**Keine ungefragten Sprachdownloads; kein automatischer Wechsel auf Englisch auf bestehenden deutschen Installationen.**

## 5. Manifest-Beispiel und Sicherheit

Jedes optionale Paket hat ein **rein deklaratives JSON**: `schema_version`, `language`/Locale (`fr_FR` etc.), `language_name`, `pack_version`, `min_xcmate_version`, `max_xcmate_version` falls nötig, `string_id_range`, `sha256` und optional `author`/`license`, `source`. Das Repo-Beispiel in `language_packs/manifest.example.json` ist **nur eine Vorlage**, keine aktive Katalogfreigabe.

- ZIP: **nur** `strings.po` und `manifest.json` (ggf. kleine Dokumentation), niemals ausführbaren Code, Skins, Fonts, Skripte oder beliebige Dateipfade.
- Validierung gegen **genau die englische ID-Liste**, PO-Header UTF-8, eindeutige IDs, vorhandene `msgstr`, keine widersprüchlichen Format-Placeholders (`%s`, `{name}`), keine übergroßen Strings, keine mehrdeutigen Locale-Namen. Übersetzungsgrad sichtbar, fehlende Texte per ID Englisch.
- Herunterladen nur explizit nach Nutzeraktion über HTTPS und vertrauenswürdige Quelle, ZIP-Slip/Path-Traversal/Symlinks/ZIP-Bomb-Prüfung, Grenzen für Dateien/Bytes/Kompressionsrate, Hashprüfung und atomare Installation (Tempdatei → Validierung → Rename).
- Kein Ausführen oder dynamisches Importieren von Code aus Übersetzungen, keine Manipulation von Kodi-Global-Sprache oder anderen Add-ons.
- Keine personenbezogenen Daten/Portalkonten im Paket oder in Logs.

## 6. Technische Realisierung / Tests / Nicht-Ziele

**P1 Aufgabe für Codex (nach bereits eingeplanten Menü-/EPG- und Film-/Serienbausteinen):**
- Vorhandene en/de PO-Dateien als Basissprachen inventarisieren, die derzeit verwendeten String-IDs und hartkodierten UI-Texte sammeln; zunächst ausschließlich neue XCMate-Menüs und Dialoge über zentrale `tr(string_id)`- oder Kodi-Lokalisierungsschicht sauber referenzieren. Keine sofortige invasive Umschreibung der bewährten Live-TV-Overlay-State-Machine (Funktions-FREEZE).
- Loader von extern installierten `strings.po`-Paketen nur bei konkreter Implementierung verfügbar machen. **Kodi-native Einstellungslabels** aus `settings.xml` müssen ebenfalls kompatibel bleiben; gegebenenfalls nach Sprachwechsel Reload/Neustart anbieten, nicht behaupten, Kodi werde nachträglich beliebige `user_data` PO-Dateien automatisch lesen.
- Kompatible Sprachen nachinstallieren, auswählen, entfernen; Nutzerpräferenz speichern, Deutsch der Bestandsinstallation nach Kodi-Update erhalten. Strings-Katalog und Fallback ohne Netz während Fernbedienungsevents.
- CI/Tests: Wechsel `en_GB↔de_DE`, Erstinstallation, Altprofil-Upgrade, optional `fr_FR`-Fixture, fehlende/duplizierte ID, ungültiges Format, ungültiger ZIP-Pfad, Offline-Verfügbarkeit, defektes Manifest, partiell übersetzte Pack, active-pack deletion, Schreibfehler, Kodi 21/Android und BINGIE MOD. Direkte Wiedergabe weiterhin unberührt.
- Scope klar abgrenzen: **Nur Englisch/Deutsch sind bereits im produktiven Paket**, weitere Sprache und Download-/Deinstallationsmenü **sind noch nicht gebaut**.
- Kein Merge/Release nach `main` ohne ausdrückliche Freigabe. Codex-PR + Review + Android-Test, später normale Kodi-Repository-Updates.

**Verweise:** [0.1.27-Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md) · [aktueller Status](CODEX_STATUS_CURRENT_DE.md) · [Design 1/Themeverwaltung](DESIGN_FREEZE_SPACE_PREMIUM_THEME_ARCHITECTURE_DE.md).
