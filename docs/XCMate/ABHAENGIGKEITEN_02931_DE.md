# .31 – priorisierte Abhängigkeiten vor Codearbeit

Basis main 6d3555a / XCMate .30; Versionsnummer .31 vor Beginn frei.
Bestehende .30-Abnahme 12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED unverändert.
Vier Stunden und Service-Neustart sind PASS; kein neuer pauschaler Langzeittest.

| Priorität / Issue | Ist-Code / Beobachtung | Belegte Lücke und Root-Cause-Grenze | Konkrete Änderung | Hosttests | Android-Delta |
|---|---|---|---|---|---|
| A #140 | Suchergebnis fokussiert automatisch 710; Kurzcache scannt nur 2 s. Gerät: EPG_PARTIAL, programme_hits=0, unerwünschter Player-Handoff | Zeitlimit überspringt verbleibende Sender; Fokus springt nach Eingabe auf Treffer. Endgültige Geräteursache noch unbewiesen | Inkrementell alle Cache-Sender bearbeiten; Fokus nach Eingabe auf Tabs behalten; Re-Init/verspätete Clicks sicher behandeln; keine HTTP-Suche | später Short-only Treffer, mehrere Sender, langsame/fehlerhafte Worker, Root/Keyboard-Reinit, explizite Auswahl | EPG1/3; EPG2 nach Entblockung |
| B #135/#63 | Grant/Retry existiert nur in Managerunterfunktion; untrusted Redirect stoppt vor Bytes | Security-Deny ist korrekt, Bedienablauf nicht ausreichend verständlich. Vertrauenswürdigkeit nicht aus Fehlermeldung ableitbar | Sichtbare statusabhängige Freigabe-/Widerruf-/Retry-Aktion mit enger Bindung; anonyme Source/Stage/Target-Diagnose | deny/grant/revoke, falsches Portal/Quelle, kein Downgrade/SSRF/Headerleak; Film/Folge realer Hosttransfer | DL1/2/3/4/5 |
| B #136 | USB_STAGE/SMB2 samt Persistenz erreicht; noch keine fertige Datei | Keine belegte Write-Ursache aus Redirect-Deny | Kleine lokale Backend-Testdatei auf ausdrücklich gewähltem Ziel, Größe/Hash/Readback, eigene Datei sicher entfernen; kein interner Ersatz | ausgewähltes Ziel, NoReplace, Fehlerphase, keine Fremdlöschung | ST1, ST3/4 nach Source-Freigabe; ST2/5 schützen |
| C #126 | Native Capture-Publish separat; keine Gerätedatei | Ohne Stream-/Probegrund kein gesicherter einzelner Bug | Separat beobachten; keine Download-Stage als Capture-Freigabe verkaufen | bestehende TS-/Ziel-/Abbruchtests | REC1–4 nach kompatiblem Ziel |
| D #111 | Provider-Timeout, einmal DB-BUSY | DB-BUSY beweist keine Timeoutursache | Getrennte Folgeentwicklung; READY und Queue bewahren | vorhandener selektiver Retry | ART1/2 nach Fix |
| Später #151/#94/#150/#98/#99/#123/#43 | Neue eigenständige Funktionen | Noch nicht implementiert | Nicht in P0-Such-/Downloadpatch mischen | eigene spätere Tests | nur nach Umsetzung |

Lieferumfang .31: A und B als getrennte Drafts, kumulatives Test-ZIP/Changelog/SHA.
Keine Behauptung, Recorder/Poster oder neue Roadmap-Features seien damit erledigt.
Keine Profil-/EPG-/Resume-Löschung, keine Keymaps, kein Merge/Release/Issue-Abschluss.
