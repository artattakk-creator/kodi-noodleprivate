# XCMate – TiviMate 5.3.3: vierte Foto-Serie der Einstellungen

**Aufnahme/Erfassung:** 14.10.2026. **Quelle:** 10 vom Nutzer bereitgestellte Fotos der konkreten TiviMate-Konfiguration; Originalbilder im Chat, nicht ins öffentliche Repository übernommen. **Status:** Funktions- und UI-Referenz; keinerlei Aussage über eine bereits funktionierende Kodi-Implementierung. **Veröffentlichtes XCMate:** 0.1.10, Add-on-ID `plugin.video.xtreammate`.

**Verbindliche Regeln:** Gleiche Menüstruktur, Funktionssemantik und einstellbare Felder eigenständig für XCMate spezifizieren. TiviMate-Assets/Programmcode nicht kopieren. Die gespeicherten XCMate-Portale, Zugangsdaten, EPG-Zuordnungen, Fernbedienungsprofile und Startsender bleiben unberührt. Ein Bild enthält sichtbare private Kontoinformationen und einen Gerätebezeichner: **nicht übernehmen** (auch nicht teilweise). Ein anderes zeigt einen lokalen Aufnahmepfad: statt des echten Pfads nur `[lokaler Aufnahmepfad]` dokumentieren.

## 1. Fotoindex

| Referenzfoto | Gezeigtes Untermenü | Befund |
| --- | --- | --- |
| `1000118384.jpg` | **Wiedergabe** | Puffergröße, Audio-/Video-Decoder, AFR, Surround-Spurauswahl, Passthrough, externer Player, Schritte überspringen |
| `1000118387.jpg` | **Sonstiges** | Untermenüs Suchen, Erinnerungen, Aufnahme, VOD |
| `1000118385.jpg` | **Kindersicherung** (oben) | Ein/Aus, PIN ändern, PIN-Eingabemethode, wiederholte PIN-Abfrage, Sender-Ausnahme, Schutzbereiche |
| `1000118386.jpg` | **Kindersicherung** (unten) | Schutzbereiche: Einstellungen, Playlists, EPG, Kanal- und Gruppenoptionen |
| `1000118390.jpg` | **Sonstiges → Aufnahme** | Aufnahmeverzeichnis sowie Vor-/Nachlaufzeiten |
| `1000118389.jpg` | **Sonstiges → Erinnerungen** | Minuten vor Sendungsstart, Popup-Anzeige, Standardaktion, Wake aus Sleep |
| `1000118388.jpg` | **Sonstiges → Suchen** | Sprachsuche, Suchverlauf, Favoriten zuerst, vergangene Sendungen, bei Kanalwechsel auf Suchbildschirm bleiben |
| `1000118391.jpg` | **Sonstiges → VOD** | Nächste Folge automatisch abspielen |
| `1000118392.jpg` | **Über** (oben) | Anonyme Statistiken, Updates, Beta, Update-Suche, Rechtstexte, Konto, Gerätename, Version |
| `1000118393.jpg` | **Über** (unten) | Konto und Gerätename noch einmal sichtbar; Version, allgemeiner Abo-Verwaltungshinweis |

**Achtung zur Schalterauswertung:** Blaue, rechts stehende Markierungen sind als **Ein** erkennbar; helle Markierungen links in grauer Spur als **Aus**. Einige Felder haben dagegen einen *dunklen Schalterknopf rechts* (Sprachsuche bevorzugen, VOD-Nächste-Folge, anonyme Statistiken). Aus der Fotografie allein ist deren tatsächlicher Aktivierungs-/Verfügbarkeitsstatus nicht sicher zu beurteilen: **`unbestimmt`**, nicht voreilig `true` oder `false` setzen. Diese Werte am Gerät durch erneutes Öffnen des Auswahlfeldes bestätigen. Dies gilt nicht als Grund, bestehende Einstellungen zu überschreiben.

## 2. Wiedergabe – sichtbare Einzelwerte

| Funktion | Foto-Wert | Typ | Technischer Hinweis |
| --- | --- | --- | --- |
| Puffergröße | **Klein** | Auswahl | Kodi-Cache/Player-Einstellungen sind nicht identisch mit ExoPlayer-Buffern |
| Audio Decoder | **Hardware** | Auswahl | Plattform-/Kodi-Decoderkonfiguration, nicht durch alle Add-ons erzwingbar |
| Video Decoder | **Hardware** | Auswahl | Kodi-/MediaCodec-Abhängigkeit |
| Automatische Anpassung der Framerate (AFR) | **Aus** | Auswahl | Kodi Display/Refresh-Rate-Schalter können global gelten |
| Standardmäßig Surround-Audiospur auswählen | **Aus** | Schalter | Nur anwenden, wenn mehrere Audiospuren vorliegen |
| Audio-Passthrough | **Aus** | Schalter | Kodi-Systemaudioeinstellung; nicht global ungefragt ändern |
| Externen Player nutzen | **Nein** | Auswahl | Externe Playerintegration separat prüfen |
| Schritte überspringen | Untermenü sichtbar | Navigation | Werte nicht sichtbar, nach weiteren Fotos erfassen |

## 3. Sonstiges – Menübaum

`Einstellungen → Sonstiges → Suchen | Erinnerungen | Aufnahme | VOD`

### Suchen

| Option | Fotozustand |
| --- | --- |
| Sprachsuche bevorzugen | **Unbestimmt** (dunkler Schalter rechts; evtl. gesperrt) |
| Suchverlauf anzeigen | **Ein** |
| Lieblingssender zuerst anzeigen | **Ein** |
| Vergangene Sendungen anzeigen | **Aus** |
| Bleibe auf dem Suchbildschirm, wenn du den Kanal wechselst | **Aus** |

### Erinnerungen

| Option | Sichtbarer Wert |
| --- | --- |
| Vor Programmstart erinnern (Minuten) | **0** |
| Popup-Timeout (Sekunden) | **10** |
| Standardaktion | **Anschauen** |
| Wache aus dem Schlafmodus auf | **Aus** (geräteabhängig) |

### Aufnahme

| Option | Sichtbarer Wert |
| --- | --- |
| Aufnahmeverzeichnis | `[lokaler Aufnahmepfad]` (Wert aus Datenschutz-/Portabilitätsgründen weggelassen) |
| Beginn der Aufnahme vorher (Minuten) | **0** |
| Aufnahme stoppen nach (Minuten) | **0** |

**Implementierungsgrenze:** Geplanter Vorlauf/Nachlauf, der Aufnahmeort und Speicherrechte müssen in Kodi geprüft werden. Ein in TiviMate gezeigter Android-Aufnahmepfad ist kein automatisch gültiger Kodi-Pfad. Keine Aufnahmen löschen oder Speicherort ersetzen.

### VOD

| Option | Sichtbarer Wert |
| --- | --- |
| Nächste Folge automatisch abspielen | **Unbestimmt** (dunkler Schalter rechts) |

Diese Option ist Bestandteil der bereits spezifizierten XCMate-Serienfunktionen. Die künftige XCMate-Einstellung muss separat speicherbar sein und einen klaren Standard besitzen; die Nutzereinstellung aus TiviMate kann aus dem Bild nicht eindeutig als ein/aus ausgelesen werden. Wiedergabeverlauf/Bookmarks und Staffel-/Episodenfortschritt bleiben portalgetrennt.

## 4. Kindersicherung

| Option | Fotozustand |
| --- | --- |
| Kindersicherung aktivieren/deaktivieren | **Aus** |
| PIN ändern | Aktion |
| PIN Eingabemethode | **Sammler** (sichtbare UI-Beschriftung) |
| Nach dem Entsperren ist keine PIN erforderlich | Auswahl zeigt **Immer erforderlich** (Wortlaut wie fotografiert, Semantik später überprüfen) |
| Nur für Sender nicht erforderlich | **Aus** |

**PIN benötigt für**: Einstellungen, Einstellungen / Playlists, Einstellungen / EPG, Kanaloptionen, Gruppenoptionen – alle fünf gezeigten Schalter **Aus**.

**Sicherheitsanforderungen an eine eigene XCMate-Implementierung:** Kindersicherung muss Inhalte und geschützte Aktionen tatsächlich vor Ausführung sperren, nicht bloß visuell. Eigene PIN sicher als abgeleiteten, gesalzenen Prüfwert speichern, nicht im Klartext/GitHub; Rate-Limiting und geschützte Wiederherstellungslogik vorsehen. Keine automatische Kopie einer TiviMate-PIN. Bereits vorhandene Portal-/EPG-Zugangsdaten oder Wizard-PINs nicht als Eltern-PIN wiederverwenden. Kodi erlaubt bei einem Add-on allein keine vollumfängliche systemweite Sperre anderer Add-ons.

## 5. Über

| Eintrag | Sichtbarer Wert / Status |
| --- | --- |
| Anonyme Statistiken senden | **Unbestimmt** (dunkler Schalter rechts) |
| Automatisch aktualisieren | **Ein** |
| Am Beta-Test teilnehmen | **Aus** |
| Nach Updates suchen | Aktion |
| Nutzungsbedingungen | Link |
| Datenschutz-Bestimmungen | Link |
| Account | `[privates Benutzerkonto redigiert]` |
| Gerätename | `[privater Gerätename redigiert]` |
| Version | **TiviMate 5.3.3 (Premium)** |
| Google-Play-Aboverwaltung | Allgemeiner externer Hinweis; **nicht** in XCMate als TiviMate-Abo übernehmen |

**Ziel für XCMate:** eigener `Über`-Dialog mit XCMate-/GS-Media-Marke, echter Versionsnummer, Repository-/Changelog-Verknüpfung und GS-Media-Rechtstexten. **Keine Fremdmarken-AGB, TiviMate-Aboverwaltung oder fremdes Konto** übernehmen. Anonyme Telemetrie falls überhaupt vorgesehen nur per informierter Opt-in-Entscheidung, nicht stillschweigend. Updates ausschließlich über die bestehende kontrollierte GS-Media-Kodi-Repository-Infrastruktur.

## 6. Ergänzung des Zustands-/Menümodells

- `SETTINGS_ROOT → PLAYBACK`: Puffer, Decoder, AFR, Audio, Extern, Skip-Steps
- `SETTINGS_ROOT → MISC → SEARCH_SETTINGS | REMINDERS | RECORDING | VOD_SETTINGS`
- `SETTINGS_ROOT → PARENTAL`: PIN-Status, PIN ändern, Eingabemethode, PIN-Nachfrage, geschützte Unterbereiche
- `SETTINGS_ROOT → ABOUT`: GS-Media-spezifische Informationen, Update-Status, Rechtstexte

**Abnahme:** Kein Wert aus den Fotos wird ungefragt als Default über bestehende Kodi-Profile geschrieben. Hardware-/Android-bezogene Funktionen bei fehlender Kodi-Unterstützung ehrlich deaktiviert oder als systemweite Kodi-Einstellung kenntlich machen. Nie eine nur gezeichnete Kindersicherung oder Aufnahmefunktion als funktionsfähig präsentieren. Nach echter Implementierung: Python-/Kodi-Mock-Tests, GitHub-Build, ZIP/Katalog/Checksumme und Test auf Android-Box mit Titan BINGIE MOD. **P0 Startsender + Remote bleibt vorrangig.**

**Weitere Quellen:** [vorherige Einstellungsserie](TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md), [maschinenlesbarer Foto-Vertrag](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json), [Design](DESIGN_SYSTEM_DE.md), [Serienfortschritt](SERIES_PROGRESS_SPEC_DE.md).
