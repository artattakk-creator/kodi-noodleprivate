# .30-E – Kodi-Gettext-Validierung (#142)

Beide DE-/EN-Dateien enthielten im englischen msgid von #34718 ein JSON-Escape
`\u2013`. Kodi/Gettext akzeptiert diese Schreibweise nicht. Durch das tatsächliche
UTF-8-Zeichen „–“ ersetzt. Das sichtbare Passwortfeld bleibt lokal; keine Änderung
an Credentials, SMB-Settings oder Speicherung.

`python tools/validate_kodi_po.py` prüft alle ausgelieferten UTF-8-Kataloge:
Gettext-Strings und Fortsetzungen, erlaubte C-/Oktal-Escapes, Kontextsyntax,
fehlende msgid/msgstr und doppelte IDs. Unbekannte Escapes wie `\u`/`\q` sind Fehler.
Ein echter doppelter Backslash, etwa `DOMAIN\\user`, bleibt gültig.
Keine JSON-Interpretation von PO-Strings.

Vier automatisierte Tests PASS; jeweils 751 Kontexte pro Sprache, gleiche IDs.
Die vollständige CI führt denselben Validator vor Syntax-/Regressionstests aus.
Keine Bild-/Userdateien oder Repository-Indizes verändert.

Android: Sprachwechsel DE/EN, SMB-Passwortdialog öffnen, Übersetzung anzeigen,
keine PO-Parsermeldung. Status **NOT_TESTED** bis zum tatsächlichen Gerätetest.
