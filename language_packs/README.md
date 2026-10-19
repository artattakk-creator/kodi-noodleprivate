# XCMate Language Packs – Katalog-Staging

**Englisch ist die technische Standard-/Fallbacksprache; Deutsch bleibt installiert.**

Diese Wurzel ist für **künftige optionale und nachinstallierbare XCMate-Oberflächen-Übersetzungen** reserviert. Der Sprachpaket-Installer, der Loader und eine Downloadfunktion **sind noch nicht implementiert**.

Aktuelle, bereits im Kodi-Addon mitgelieferte Sprachdateien (in XCMate 0.1.26, nicht verschieben oder löschen):

- `src/plugin.video.xtreammate/resources/language/resource.language.en_gb/strings.po` – English / Standard-Fallback
- `src/plugin.video.xtreammate/resources/language/resource.language.de_de/strings.po` – Deutsch / erhalten

Die aktuelle Kodi-eigene Spracheinstellung eines bestehenden Nutzers wird nicht überschrieben. `settings.xml:lang_priority` steuert IPTV-Inhaltsfilter, **nicht** die XCMate-Oberflächensprache.

Vorgesehen: `language_packs/<locale>/manifest.json` und `strings.po`, installierbarer Userdata-Pfad später unter `special://profile/addon_data/plugin.video.xtreammate/language_packs/<locale>/`. Ein Zusatzordner allein wird von Kodi **nicht automatisch** als neue Runtime-Übersetzung eingelesen; Codex muss einen kompatiblen Loader, sichere Katalogprüfung und Fallbacks implementieren.

Späteres Menü: **Einstellungen → Darstellung & Sprache → XCMate-Sprache → Sprachpakete verwalten**. English und Deutsch dauerhaft verfügbar, optional ergänzte Packs lassen sich herunterladen, auswählen, entfernen. Daten-ZIPs ohne Code, Hash/Symlink/Zip-Slip/Größenprüfungen.

Vollständige Spezifikation: [docs/XCMate/LANGUAGE_PACK_ARCHITECTURE_027_DE.md](../docs/XCMate/LANGUAGE_PACK_ARCHITECTURE_027_DE.md).

**Versionsstand:** 0.1.26 produktiv, neue Sprache-Pack-Funktion nur Zielentwicklung. Kein GitHub-Merge von fremden Sprachpaketen und keine automatischen Installationen.
