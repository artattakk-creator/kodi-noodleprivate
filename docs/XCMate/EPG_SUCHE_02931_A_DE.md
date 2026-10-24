# .31-A – Suchfokus und vollständiger lokaler Jetzt-EPG-Scan (#140)

Basis main 6d3555a / .30. Keine Änderung historischer Gerätewerte; EPG1/3 sind
weiterhin FAIL, EPG2 BLOCKED bis tatsächlicher .31-Abnahme.

Belegte Code-Lücken: _search_ready fokussierte automatisch den ersten Treffer;
der einmalige Zwei-Sekunden-Short-Scan ließ spätere Sender dauerhaft ungeprüft.
Das erklärt mögliche Ausfälle, beweist allein nicht den gesamten Android-Vorfall.

Neu: Worker-eigener Cursor scannt alle erlaubten Sender in Scheiben von höchstens
64 Kanälen bzw. 200 ms zwischen einzelnen Cachezugriffen. Kein HTTP/Refresh.
Teilzählungen erscheinen mit +, bis die Suche vollständig ist. Kein globaler
Timeout, der den Rest als endgültige Null verkauft. Einzelne Dateisystemzugriffe
können länger dauern, laufen aber außerhalb des GUI-Callbacks. Stale Generationen
werden vom bestehenden Owner verworfen; kein neuer Pool/Service/Globalcache.
Explizite Mappings und gültige XML-Daten bleiben maßgeblich. Keine EPG-Schreibzugriffe.

Nach Eingabe bleibt Fokus auf Suchnavigation, erst bewusste Navigation wählt
Resultate. Stale Klicks auf unsichtbare Landing-Controls und unfokussierte
Treffer werden konsumiert. Such-Tab-Fokus wird bei verzögerter Kodi-Sichtbarkeit
aufbewahrt. Re-Init beim Keyboard-/Dialog-Rücksprung ersetzt keinen Suchworker
mehr durch Landing/Playback-Restore. Suchstatus behält vorhandenen Owner.
SEARCH_EPG-Scan und Suchlifecycle teilen eine zufällige reine Hex-Korrelation;
keine Titel/IDs/Portal-/Providerdaten oder Exceptiontexte in öffentlichen Logs.

36 gezielte Hosttests PASS (6 neue). Neue Reproduktionen: später Short-only-Titel
nach >2 s auf mehreren Sendern, inkrementelle Fertigstellung ohne Fokus-Sprung,
Keyboard-Reinit, langsamer/leer bleibender Worker, verzögerte native Sichtbarkeit
sowie ignorierte alte Klicks und explizite Live-Auswahl. Bestehende Such-/Live-
Handoff-Tests bestehen; search_live/Player/Guide-Handoff unverändert.

Android nur Delta: EPG1/3 (echter Jetzt-Titel, auch mehrere Sender), EPG2 nach
Entblockung, Keyboard-OK bleibt Suchansicht, Down+OK wählt bewusst, Back/Fehler/
langsamer Scan bleiben bedienbar. Bestehende S1–S5 und vier Stunden sind Baseline,
keine erneute Vollmatrix oder Langzeitabnahme ohne konkreten Regressionshinweis.
Keine Profil-/DB-Migration, keine Daten-/Keymap-/Icon-/Splashänderung.
Kein main-Merge/Release; installierbare .31 erst im kumulativen Testbranch.
