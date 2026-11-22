# XCMate 0.1.29.101 – integrierter EPG-Agent / GS Media Hub Schema 4

**Stand:** Entwicklungsbranch, **kein** produktives Release / kein Merge nach main.
**Verbindlicher Auftrag:** #509, #508, #505, #506.

## Gewünschter Regelbetrieb
- Die Synology DS414 veröffentlicht das überprüfte EPG in das PRIVATE Repo
  \`artattakk-creator/xcmate-epg-private\` als private GitHub Release-Assets.
- \`manifest.json\` vom 22.11.2026 ist \`schema_version=4\`, \`PRIVATE_READY\`;
  Profile \`all\`, \`de\`, \`at\` sind vorhanden. Der alte Reader kann nur Schema 3.
- Kodi erhält seinen **eng begrenzten privaten GitHub-Read-Token** entweder als
  lokale Datei \`special://userdata/addon_data/plugin.video.xtreammate/epg-agent/reader-token.txt\`
  oder **nur im privaten Build** als
  \`resources/private/xcmate_epg_read_token.txt\`. Keine Token im Public Repo.
- EPG-Agent ist ein fester, optional abwählbarer Teil des Add-ons. Auf
  Neuinstallationen ist der Agent standardmäßig aktiviert; DE und AT sind
  initial ausgewählt. Vorhandene Nutzer-Opt-outs werden nicht überschrieben.
- UI \`Einstellungen > EPG > EPG-Agent\`: Ein/Aus, DE, AT, alle Länder,
  Aktualisieren, Status. Backend importiert \`de\`, \`at\`, echte Kombination
  \`de+at\` (und nicht implizit das größere \`all\`), bzw. \`all\` explizit.
  Andere Länder erst nach Veröffentlichung eigener verifizierter Profile.
- Bestehender Provider-EPG bleibt als lokale unabhängige Fallbackquelle.
  Beim defekten GitHub-Download wird kein bestehender Guide gelöscht.

## Implementation im isolierten Branch
- \`epg_agent_hub4.py\`: strenge Prüfung von Repository/Manifest/Filenames/
  GitHub-Asset-IDs, HTTPS-API-URL und SHA-256. Autorisierung nur an das fest
  vorgegebene GitHub-API-Asset; alle HTTP-Redirects sind ausschließlich durch
  den bestehenden \`_LimitedGitHubRedirect\` erlaubt, der Bearer entfernt.
- Streamende GZIP-Downloads auf lokale temporäre Datei, Hash und Bytezahl
  vor Aufnahme; XMLTV-Streaming-Prüfung gegen Manifestanzahlen.
- Bei DE+AT: XMLTV-Union mit erhaltenen Originalfeldern und Artwork-Elementen;
  doppelte Kanal-IDs nur bei identischem Sendernamen; DE-Priorität bei
  identischem Kanal+Start+Ende, zusätzliche AT-Events bleiben erhalten.
- Ausgabe an den bisherigen \`epg_agent100_import.install\`-Stagingpfad als
  verifiziertes \`candidate-<sha>/xcmate-epg.xml.gz\`. Manifest und Daten
  werden nur als gemeinsam vollständige lokale Kandidaten übernommen.
- Der bestehende Schema-3-Reader bleibt kompatibel.
- Hostregressionen in \`tests/test_epg_agent_hub4.py\`.

## Pflichtaufgaben vor Freigabe
1. GitHub Action / Unit-Tests auf dem PR-Branch ausführen und eventuelle Fehler
   beheben. Synthetische Tests **ersetzen keine Geräteabnahme**.
2. Private Read-Credential **ausschließlich beim privaten Paketbau** injizieren;
   Quelltext, Build-Logs, öffentliches ZIP und PR müssen tokenfrei bleiben.
   Es gibt derzeit **keinen bestätigten eingebundenen echten Reader-Token**.
3. Mit realem privaten GitHub-Schema-4-Asset End-to-End prüfen:
   Manifest-GET, 302→CDN, GZIP und SHA, Receiver, Senderzuordnung, XMLTV-
   Artworkrollen und 460.454 Events im \`all\`-Profil. Noch **nicht geprüft**.
4. Vor Kodi-Import: tatsächliche Ressourcenlimits und noch verfügbare
   Speicherkapazität Android TV 13, ARM32, Kodi 21.3 und LG webOS Kodi 22
   kontrollieren. Auf beiden Geräten echte Back-/Player-/EPG-Tests.
5. Partner-Integration mit bestehendem PR #505 (optionaler manueller
   Credential-Import) und #506 (universelle Detailansicht) rebasen/testen,
   keine unkontrollierten gegenseitigen Überschreibungen.
6. Vor Merge: Länderwechsel DE/AT/DE+AT/all, Netz-Ausfall, abgelaufener PAT,
   403, SHA-Mismatch, 0-Mapping, LastGood, Kodi-Neustart, mehrere Portale,
   Backups, EPG-Bilder / Senderlogos.
7. Release nur nach bestandener realer QA und gesonderter Nutzerfreigabe.

**Statusunterscheidung:** Das private GitHub-Manifest ist bereits real
\`PRIVATE_READY\`. Das bedeutet nicht, dass dieser neue Kodi-Reader bereits
installiert, authentifiziert oder auf Endgeräten freigegeben ist.
