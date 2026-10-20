# Phase C – aktive Gruppen und durchgehende Senderliste

20.10.2026. Entwicklung 0.1.29.1, auf Phase B / PR #46, Phase A / #45 und #39.
Refs #37/#42. **Keine Veröffentlichung, Android-Abnahme offen.**

## Eng begrenzte, ausdrücklich autorisierte Änderung

Normale Live-TV-Gruppenliste enthält ausschließlich aktive Gruppen und optional
„Alle aktivierten Gruppen“. Kein AN/AUS-Präfix, kein automatisches Aktivieren bei OK.
Bei null aktiven Gruppen bleibt ein eindeutiger Hinweis mit Menü-Zugang bestehen.
Menü öffnet bestehende Checkboxverwaltung mit **allen lokal bekannten Gruppen**;
Zurück verwirft Änderungen, Speichern liest die Auswahl erneut ein und korrigiert
Listen/Fokus ohne Senderwechsel. `known`/`auto_new` bleiben erhalten, neu automatisch
aktivierte Kategorien werden korrekt aus `enabled_ids` abgeleitet.

Die Verwaltung erhält den vorhandenen Kategoriensnapshot. Explizites „neu laden“
fordert Hintergrundarbeit an; kein Providerzugriff im Remote-Callback. Keine globalen
Keymaps und keine Skinänderung. Andere Add-ons unverändert.

Die Senderliste zeigt ausschließlich Sender. Vorherige/Nächste-Seite-Einträge und
Seitenzähler entfallen. Intern bleiben maximal 100 ListItems und acht eigene sichtbare
Zeilen. Absolute Auswahlposition wird über Fenstergrenzen erhalten: 100→101 ohne OK,
auch rückwärts, ohne doppeltes Kodi-/Python-Bewegen. Native Up/Down und Bridge führen
jeweils genau einen Schritt aus. Am Ende/Anfang bleibt die Liste stehen; das bereits
bestehende Wrap beim **Vollbild-Zappen** bleibt unberührt. PageUp/PageDown bleiben
Schnellnavigation (große Liste: 100 Sender; kurze Liste: nativer Kodi-Schritt).
EPG-Vorbereitung bleibt asynchron für aktuelle/sichtbare Sender, kein Netzwerk im D-Pad.

## Freeze-Prüfung statt pauschalem neuem Dateihash

Das originale `xcmate_026_freeze.json` bleibt unverändert. Zusätzlicher AST-Nachweis
speichert alle Originalfunktionen und prüft unveränderte Overlay-Methoden einzeln.
Ausnahme nur für `category_rows`, `_list_content`, `_page_channels`, `_toggle` (jetzt
Verwaltung) und `_select`; neu ist `_move_channels`. Drei exakt bekannte Einfügungen
in Katalogladen/Position/native Action und zwei neue Anzeigetexte werden für den
Vergleich gezielt normalisiert. Sonstige Konstruktion, Controls, Fokus-/Ownership-,
OK-/Back-/Player-/Zap-Methoden bleiben durch den ursprünglichen AST geschützt.
Bestehende strikte Omega-API-/Callbacktests bleiben aktiv, WindowDialog hat weiterhin
keinen künstlich ausgelösten onInit/onClick-Pfad.

Der alte Page-Link-Test wurde entsprechend der ausdrücklich ersetzten Anforderung
geändert: Jede Zeile stimmt jetzt mit einem echten absoluten Sender überein. Keine
Testabschaltung, keine Duplikation der 40 bestehenden Callbacktests als „neue“ Fälle.

## Testergebnisse

425/425 vollständige Tests in 62,315 s bestanden, keine Fehler/übersprungenen Tests.
8 neue Fälle: aktive/keine Gruppen, tatsächliche Checkbox-Persistenz/Reaktivierung
und Cancel/auto_new, native/Bridge-Grenzbewegung, 1001 Sender/10 Gruppen mit 2000
Auf-/Ab-Ereignissen und unveränderter Controlanzahl. 40 bestehende Omega-Callbackfälle
und 31 bestehende UI-/Freeze-Fälle separat bestanden. Modell-Grenze für den 2000er-
Eventlauf: 5 s; keine daraus abgeleitete Android-Latenzbehauptung.

Erster Voll-Lauf war wegen einer veralteten englischen Staffel-Textprüfung aus Phase B
rot. Der dortige Test wurde im zuständigen B-Branch auf den vollständig erwarteten
neuen Status „Season 1 · 0/2 · Unwatched“ korrigiert; B-CI danach erfolgreich. Dieser
Branch übernimmt diesen Testfix. Keine Abschwächung zu bloßem StartsWith.

## Android – alle neuen Abnahmen OFFEN

- Gemischte Aktiv-/Deaktiv-Auswahl: nur aktive Gruppennamen, kein AN/AUS.
- Menü in Gruppenliste: alle Checkboxen sichtbar, Aktivieren/Speichern sofort wirksam;
  Cancel verändert nichts; keine automatische Reaktivierung durch OK.
- Alle deaktivieren: eindeutiger Verwaltungszugang, laufender Sender bleibt unberührt.
- Mindestens 1000 Sender/10 Gruppen: Grenzen 99/100/101, 199/200/201, Ende und Anfang,
  langsame/gedrückte IR-Tasten, PageUp/PageDown, Bridge falls explizit aktiviert.
- OK spielt immer den angezeigten Sender; kein Sprung/Mehrfach-Tune am Fensterwechsel.
- Kein Bild-/Ton-Stop beim bloßen Verwalten oder Overlay-Back. Erst tatsächliches
  Playback-Verlassen gemäß Phase A. Audio-/Video-/Untertiteldialoge weiter funktionsfähig.
- EPG Jetzt/Nächste und Logos ohne Neuöffnen, D-Pad bei langsamen Providern responsiv.
- Nach Kodi-Neustart gespeicherte Kategorien und Favoriten/Resume erhalten.

Rollback: Kodi beenden, Profil sichern und vorheriges offizielles ZIP über bestehende
ID installieren; keine Profil-/Gruppen-/DB-Löschung. Datenformat der Auswahl unverändert.

[Geprüftes ZIP 0.1.29.1](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.1.zip):
109 Dateien / 345227 Bytes, SHA256 `0c1ad79bf58e01d94675d31573cda7e1a42523d7f96151d2bcc09aca3cf69827`.
Syntax/CRC und jedes Quellbyte geprüft. [Maschineller Nachweis](TESTERGEBNISSE_PHASE_C_029.json).
