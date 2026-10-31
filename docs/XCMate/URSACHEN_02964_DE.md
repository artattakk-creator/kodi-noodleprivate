# XCMate .64 – Codeursachen, Android-Befunde und Grenzen

Basis main 4e89c3a8af29a8796f26c2b3ddb2c1484ef89769 (.63), vollständiger Master #295 samt Nachtrag; vom Nutzer als identisch mit dem Chat-Anhang bestätigt. Ein kumulativer Branch und Draft-PR #296. Kein Merge/Release/Reset.

## Befund und belegbare Reparatur

Die gemeldeten Android-Fotos selbst stehen diesem Ausführungskontext nicht zur Verfügung. Ihre im Master beschriebenen Befunde S64-01 bis S64-04 sind reale FAIL-/Teilbefunde. Codeursachen und reproduzierbare Hostfälle sind davon getrennt. Keine Aussage, dass eine einzelne Hypothese alle Gerätefehler erklärt.

Fokus: Die gepinnte echte BINGIE-2.2.3-Definition Bingie_Screens_Fixed_Focus_Frame_Base verwendet einen absoluten top=611. Die akzeptierte XCMate-LiveRow hat 76 Pixel Höhe, die normalen Posterlayouts 330 Pixel. Der bisherige native Test ließ EnableFixedFrameWidgets/LockHubWidgets aus und prüfte Live-Fokus. .64 blendet den absoluten Fremdrahmen ausschließlich bei eigenen Film-/Serienkacheln aus und zeichnet dort einen lokalen cyanfarbenen Rahmen in den expliziten Maßen des jeweiligen nativen Elterngrupps. Fremde Widgets behalten ihren ursprünglichen Rahmen. LiveRow, 142×72-Layout, Navigation und Quellen bleiben byteidentisch. Tatsächliche Android-Ursache erst durch B64-03 bestätigt/widerlegt.

Serien: widget_refresh45.publish verwendete für live/vod den gemeinsamen Renderer mit asset_refs47, für series nur describe ohne diese Referenzen. Eine fertige Referenz konnte dadurch die veröffentlichte Signatur und damit die Aktualisierung nicht ändern, obwohl die direkte Route die Referenz bereits lesen konnte. .64 verwendet denselben provider-only Renderer für alle drei Typen. Reproduktion: Series-Provider-URL vorhanden, freigegebene lokale Datei nur im gemeinsamen Assetindex, unabhängiger alter widget_art44-Cache leer. Test prüft Signaturwechsel und echte Referenz. Kein TMDB/TVmaze für VOD. Diagnosen unterscheiden fehlende Metadaten, abgewiesene URI, fehlende gültige Referenz, Bindungswiderspruch und explizit bestätigte Dekodierfehler. URI_READY ist KEIN Pixel-PASS.

EPG: hero_epg63 ersetzte bei fehlendem RAM-Eintrag bereits vorbereitete lokale Zeilentexte durch einen leeren Guide. .64 erlaubt den statischen Zeilenfallback ausschließlich mit gültigem Profil, Ereignisschlüssel, aktueller Start/Stop-Zeit, höchstens 300 Sekunden Alter sowie passender Konfigurations- und Guide-Revision. Ungültige/alte/fremde Werte bleiben gesperrt. Der Fokus wird innerhalb der bestehenden Acht-Sender-/24-Job-Queue priorisiert, der Rotationscursor bleibt nicht verhungert. Keine SQL-/Datei-/HTTP-Arbeit im GUI-Callback. guide_v1.sqlite bleibt einzige EPG-Wahrheit.

Hero: eigene .64-Ressource, vollflächiges Bild, transparente Originalverläufe, kurze Titel Bold60 und lange Titel Bold40. Mehr Platz für Beschreibung; No-Art nutzt das unveränderte Original lightweight_splash.jpg, keine fiktive Sendungsabbildung. Positive lokale Ereignis-/Artworkidentität bleibt unverändert.

Token: Der alte UI-Code etikettierte Fehler beim Ziel-Lesen pauschal als TOKEN_WRITE um. Der alte Writer kombinierte rename und Directory-fsync. .64 trennt Auswahl/VFS, Format, Profilanker, Ziel, temp-create/write/file-fsync, atomare Umbenennung, Directory-fsync und abschließende sichere Byte-/Format-/Statusprüfung. Nach schon erfolgtem rename wird ein Syncfehler nur nach erfolgreicher Endprüfung als IMPORTED_SYNC_WARNING gemeldet. Keine Behauptung bestätigter Dauerhaftigkeit. Nicht verifizierte Commit-Ergebnisse heißen TOKEN_COMMIT_UNVERIFIED, mit committed-Flag und Phase. Vor-Commit-Fehler erhalten den alten Zielinhalt. O_NOFOLLOW, private Kinder/0600-Datei, Überwrite-Vergleich, Profilprüfung und Tokenpriorität bleiben erhalten.

## Sicherer Skinwechsel

Nur exakt bekannte .63-Dateihashes oder die bestehende verifizierte Vorgängerkette. Diff, ausdrückliche Zustimmung, verifizierte private Sicherungen, atomare Transaktion und Rebuild. Keine Installation verändert automatisch Skin-Dateien. .64→.63 und anschließende Rücknahme des älteren Plans werden geprüft; unbekannte Anpassungen bleiben BLOCKED. Gespeicherte Widgetbindungsdateien/URLs werden nicht geändert.

## Grenzen

Die verwaltete Arbeitsumgebung ist beim Start gescheitert. Ausführbare Host-/Kodi-Prüfungen erfolgen über GitHub Actions. Native Fixtures verwenden synthetische Provider und isolierte Helfer; der echte gepinnte Skinshortcuts-Templatecompiler erzeugt die Widgetcontrols. Sein Fixture-Builder installiert deren Ausgabe nach Zustimmung. Kein Nachweis einer echten Android-Skinshortcuts-Generierung.

Kein Zugriff auf Box A/B oder private Token/Logs. Realer Android-Fokus, DMAX-Mapping, USB/SMB-Treiber, echte private TMDB-Authentifizierung und warme sichtbare Ein-Sekunden-Grenze bleiben NOT_TESTED. Ein erfolgreicher Linux-Test schließt #295 nicht.
