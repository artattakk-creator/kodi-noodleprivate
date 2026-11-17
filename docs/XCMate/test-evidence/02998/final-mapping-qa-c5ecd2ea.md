# Unabhängige EPG-Mapping-QA – XCMate 0.1.29.98

Prüfstand: `c5ecd2ea69bb84e648cae9433d250613dceff46e`.
ZIP: `plugin.video.xtreammate-0.1.29.98.zip`, SHA256 `d37d34fbb5be5e46154b912d3ce960f6e248431fcf7d0a9651fa9785b20a12c3`.
Modus: unabhängiger unterstützter Read-only-Reviewer gemäß projektlokalem epg_mapping_qa-Checklist; keine Produkt-/GitHub-/Profiländerungen oder Providerzugriffe.

## Ergebnis und geprüfte Identität

Kein verbleibender bestätigter Mapping-Produktblocker im geprüften Host-/Linux-Dialog-/Gridumfang. Keine uneingeschränkte Mini-/Android- oder Veröffentlichungsfreigabe.

HEAD wurde direkt bestätigt. Die XCMate-Produktquellen und das .98-ZIP sind gegenüber `2f434987eb397011295a4039e8a6bba7ffffa42b` bytegleich. Die .98-Produktquellen unterscheiden sich von `eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a` ausschließlich durch addon.xml-Version/News. Der Hauptagent muss die Identität des virtuellen GitHub-Merge-Checkouts mit diesen Produkt-/Test-/Harnessbäumen zusätzlich abschließend belegen.

## Unabhängige Hostnachweise

- 69 fokussierte Mappingtests bestanden; auf dem bytegleichen .98-Produktstand ausgeführt.
- 12 Paket-/Versions-/Inspector-Tests bestanden. Reproduzierbarkeit, CRC, exakte Quelldateien, alte .96/.97-Paketbytes sowie Manipulations-/Veröffentlichungssperren geprüft.
- 7 Fixture-/Wrappertests einschließlich fehlender/veränderter Fokusreceipts bestanden; committeter Harness entspricht dem zuvor geprüften Diff.
- Eigene bestehende-Fixture-Repros mit echtem asynchronem Worker: Quellenwechsel, reversible Vorschau, leere Vorschau ohne Save, Busy/Timeout/DB_BUSY/Retry, Abbrechen, Late-Result-Abweisung, Save, quellqualifizierter Cold-Readback und neuer Reader erfolgreich. Keine Player-Aktionen.
- 20.000 lokale Sender: Treffer 35,7 ms, Nichttreffer 35,5 ms, unverändertes 150-ms-Lesebudget.
- Historische .96-Delegation gelesen: unveränderte ursprüngliche Testkörper am gepinnten .96-Commit, Paket-/Sidecarprüfung vor separatem Originaltestprozess. Die beiden historischen Unterprozessläufe wurden vom Reviewer nicht erneut gestartet; tatsächliche vollständige Suite muss CI belegen.

Repros: `/tmp/epg98-independent-qa/{repro.py,large_local.py,final_review_extra.py,pagination_stale.py,run_focused.py}`.

## Frische native .98-Bildprüfung

Alle zwölf PNGs aus Run `44117233113`, Jobs `134158531492` (720p) und `134158530592` (1080p), unabhängig visuell angesehen:

- `/tmp/release98-final-evidence/mapping-720/epg482-{source,preview,busy}-{mini,grid}.png`
- `/tmp/release98-final-evidence/mapping-1080/epg482-{source,preview,busy}-{mini,grid}.png`

In beiden Auflösungen sind echte Quellenpicker mit Provider und lokalem Zähler sichtbar. PREVIEW_READY und MAPPING_BUSY sind vollständig lesbar. Quelle/Sender/EPG-ID/Programmzeiten sind sichtbar; keine Status-Clipping- oder Toastüberdeckungsregression. Busy zeigt Save grau und Retry grün fokussiert. Der echte Grid-Elternbereich zeigt Programme und die quellqualifizierte VORSCHAU-Kennzeichnung. Keine vorherigen .97-Pixel als .98-Beleg verwendet.

Wichtige Einschränkung: Beide `epg482-preview-mini.png` zeigen hinter/links vom Mappingpanel zusätzlich einen Yes/No-Dialog „Disabled add-ons – Would you like to enable this add-on? XCMate“. Dieser unterliegende Erstinstallationsprompt gehört zum wegwerfbaren synthetischen Native-Fixture. Er ist nicht der Catalog73-Fixtureprompt und wurde vom engen Guard nicht quittiert; kein unbekannter Dialog wurde zwangsweise geschlossen. `fixture_prompts98_declined=0` bedeutet daher nicht, dass kein Prompt erschien. Das Mappingpanel bleibt vollständig lesbar. Die vom Hauptagenten berichteten strikten Receipts belegen als obersten Dialog Mini 13002/owner mini/control 200 bzw. Busy 404, Grid 13004/owner grid/control 200 bzw. 404. Die bewiesene obere Mapping-Dialogidentität und der erwartete Fokus sind von diesem unterliegenden Fixtureprompt zu trennen. Keine neue bestätigte Falsch-PASS-Codeursache und kein bestätigter verbleibender Host-/Native-Releaseblocker im genannten Mappingumfang; die Bilder dürfen trotzdem nicht als insgesamt promptfrei beschrieben werden.

Der Mini-Elternbereich ist synthetisch und zeigt Kodi Home, keine echte Mini-Now/Next-Spalte. Reale Mini-Elternpixel bleiben unbewiesen.

## Gate-Tabelle

| Gate | Ergebnis und Grenze |
|---|---|
| E1 Einstieg | PASS im Host-/nativen Fixtureumfang; 0/1/viele konfigurierte Quellen und Namensvarianten im Host, nativer Picker mit Provider |
| E2 Vorschau | PASS für Dialog und echten nativen Grid; echte Mini-Elternspalte UNKNOWN |
| E3 Buttons/Status | PASS für geprüfte Lesbarkeit, Zustände und berichtete strikte Fokusreceipts; sichtbarer unterliegender XCMate-Prompt in beiden Mini-Vorschauframes ausdrücklich dokumentiert |
| E4 Persistenz | PASS im geprüften Hostumfang; native CI meldet zusätzlich tatsächliches Adapter-Apply und quellqualifizierten Readback |
| E5 Praxis | Linux-Kodi 21.2 bei 720p/1080p im ausgewiesenen Umfang geprüft; physisches Android ANDROID_NOT_TESTED |

## Noch offene Abnahme

Echte RK3528/Kodi-21.3/BINGIE-Prüfung: tatsächliche konfigurierte Quellen, Sendernamen/Varianten, sichtbare echte Mini-Elternspalte, IR/Back/Cancel während Coldload, Save mit Rückkehr und Kodi-Neustart/EPG-Refresh, Providerbasis ohne optionale XMLTV/Bilder. Keine Nutzerprofile zurücksetzen.

Vollständige finale Unit-/Pytest-CI war bei dieser Übergabe noch in Arbeit. Dieser Bericht allein begründet weder PILOT_READY noch Merge-/Veröffentlichungserlaubnis.
