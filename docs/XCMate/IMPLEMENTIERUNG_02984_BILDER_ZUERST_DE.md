# XCMate 0.1.29.84 – Implementierung und offene Grenzen

Stand: 09.11.2026. Einziger Branch `fix/xcmate-02984-artwork-visible-first`, bestehender [Draft-PR #405](https://github.com/artattakk-creator/kodi-noodleprivate/pull/405). Kumulativ auf .83 (`ee42712655cb9adcdcb11b09d591a1737d899844`); aktuelle Main-Dokumentation einschließlich Abschnitt E (`81fa0e620130a93d9ff2fac2f0ba16dc6584b914`) übernommen. Kein Merge oder Release.

## Bestätigte Ursachen

Die übergebene Android-Forensik beschreibt vorhandene Providerreferenzen, aber keine sichtbaren Film-/Seriencover bei etwa 27–28 MiB freiem Speicher. `persistent()` sperrte gleichzeitig den Referenzweg, während die unveränderte Archivreserve Schreibvorgänge verhinderte. Weitere optionale Status-/Framewrites benötigen selbst Speicher. RAM_ONLY allein war deshalb kein durchgängiger Anzeigepfad. Private Rohlogs und TV-Fotos wurden für diesen Build nicht erneut heruntergeladen oder veröffentlicht.

Eine zusätzliche Ursache wurde im echten Linux-Kodi 21.2 nachgewiesen: `Textures.GetTextures` akzeptiert gemäß Kodi-21-Schema `properties` und `filter`, aber kein `limits`. Die bisherige Anfrage lieferte `-32602`, obwohl die passende Texturdatei vorhanden war. Beide betroffenen Wiederherstellungswege verwenden jetzt exakte URL-Filter ohne diesen ungültigen Parameter; Antwort-, Datei- und Iterationsgrenzen bleiben bestehen. Kein unbeschränkter Scan des Kodi-Texturecaches.

Bei Serien blockierte der Genreschlüssel die TV-Werksuche schon vor TMDB. Der kurze Titel „The Middle“ scheiterte zusätzlich am bisherigen Movie-Abgrenzungsweg; „King of Queens“ benötigt einen belegten Alternativtitel. Das ist kein globaler Tokenfehler. Bestehende erfolgreiche Film- und XMLTV-Pfade bleiben erhalten.

## Sichere Anzeige bei blockierter Archivierung

- `artwork_display84`: tatsächliches Archiv-/Metadatenziel im vorhandenen Worker messen, kurze profilgebundene Druckmeldung. GUI liest nur. Kapazität, Archivreserve und Metadatenreserve getrennt; keine Reserveabsenkung, Modusänderung oder neue Datenbank.
- `widget_assets69`, `widget_art44`, `widget_cache82`: vorhandene Queue, Read-only-Widgetwege und Gesundheits-/Backoff-Logik weiterverwenden. Quellgebundene Kodi-Texturen zuerst. Bei Reservesperre öffentliche, credentialfreie HTTPS-Anzeigereferenzen mit Konto-/Profil-/Quellenbindung, Public-DNS-Lease höchstens 30 Sekunden und `redirect-limit=0`. Keine pauschale Freigabe privater Providerlinks.
- Optionale Metadaten-/Archivwrites werden bei Reservesperre übersprungen. Vorhandene Dateien und Datenbanken werden weder entfernt noch verschoben. Erste echte Referenzen dürfen einmal je Hook/Kind/Policy die alte 60-Sekunden-Veröffentlichungsbremse passieren; weitere Aktualisierungen bleiben gedrosselt.
- `programme_display84`: Freigabe erst nach vollständiger Dekodierung durch den vorhandenen sicheren Transport. Exaktes Ereignis/Fingerprint, Konto, Profil und Freigaben binden die Lease. DNS-Erneuerung im Worker; spätestens nach fünf Minuten erneute Bildvalidierung. Keine HTTP-/DNS-/SQL-Arbeit im GUI-Leser.
- Neustart: nur die exakt aktuelle XMLTV-/Provider-URL aus Kodis Textureindex wiederverwenden; zulässiger Pfad, keine Symlinks, vollständige Dekodierung, Größen-/SHA256-/Dateistabilitätsprüfung. Keine geratenen TMDB-Zuordnungen.
- Senderlogo bleibt als getrennte Rolle `station_logo` bis zum passenden Eventbild sichtbar. Verifiziertes lokales Kodi-Logo bleibt auch nach Ablauf seiner alten Remote-Lease offline nutzbar. Fremder Sender, Profilwechsel, DNS-Widerruf und EPG-Rollover dürfen kein altes Eventbild übernehmen.
- Bestehende Artwork-/Programme-Worker beachten zusätzlich Kodis Abbruchsignal. Das verhindert, dass deren Schleifen beim echten Kodi-Neustart weiterlaufen. Keine Änderung der Player-Stop-Strategie.

## Reference-first und sichtbare fünf Programme

`programme_store46.Stage.finish` signalisiert erst nach erfolgreichem Import. `programme_reference84` verwendet den vorhandenen Programme-Worker: alle 15 Sekunden höchstens vier Metadatenjobs pro aktivem Portal, maximal vier Portale pro Tick. Keine Bildkörper im Importparser oder Metadatenresolver. Deduplizierung über normalisierte Werksdaten, Quelle/Konto/Profil/Token-/Freigabekontext; positive/negative TTL. Referenzbestand maximal **256 Einträge / 512 KiB**. Optionales atomisches privates Journal nur bei ausreichender Reserve.

Auf BINGIE werden höchstens fünf aktuelle **Sendungsbilder** priorisiert; Senderlogos sind getrennt. Der ausgewählte Sender kommt zuerst. Viewport 1–5 → 2–6 fordert nur 6 neu an; gültige 2–5 bleiben nutzbar, Rücknavigation verwendet Treffer. Keine zusätzliche NEXT-/Achterrotation in diesem Home-Pfad. EPG-Texte bleiben von der Bildsuche unabhängig. Vorbereitete unsichtbare Film-/Serienbereiche dürfen die nächste Hintergrundphase freigeben; als sichtbar gelten sie erst nach tatsächlichem nativem Control-Nachweis.

## Serienerkennung, Filmregression und Diagnose

`programme_tv66` benötigt weder Genre noch Staffel/Folge für einen **Serien-Werk-Fallback**. Erforderlich bleiben vollständige begrenzte TV-Trefferlisten, eindeutiger Treffer, unabhängige TV-ID-/Name-/Produktionsjahr-Bestätigung. Fehlendes Genre bzw. kurze Titel werden zusätzlich gegen einen gleichnamigen Film abgegrenzt. News, Sport, Talk und explizite Filme bleiben ausgeschlossen.

„King of Queens“ darf „The King of Queens“ nur nach unabhängiger offizieller `alternative_titles`-Bestätigung übernehmen. Kein Abschneiden von Artikeln oder unscharfer Namensersatz. DS9-Hinweise sind Klassifikationshilfen, keine fest verdrahteten TMDB-IDs. Mehrdeutige/unvollständige Treffer und Jahres-/ID-Konflikte bleiben ohne Serienbild.

Bei exakt bestätigter Episode ohne Still ist ein unabhängig bestätigter Serien-Backdrop/Poster als **`series_fallback`, kein Episodenbild** zulässig. Falsche Episode/Untertitel oder ein vorhandener ungültiger Stillpfad beenden den Versuch. Die Filmabfrage bleibt für jetzt sowie sechs und zwölf Stunden spätere EPG-Slots abgesichert. Token wird weder neu importiert noch verändert; TVMaze bleibt optional und bewusste Opt-outs gelten. Es wird keine automatische TVMaze-Aktivierung behauptet.

Feste Diagnosegründe unterscheiden Genre unbekannt, kurzer Titel/Beweispflicht, Alias unbestätigt, mehrere Treffer, Jahreskonflikt, Quelle deaktiviert und Artwork fehlt. Keine Titel, IDs, Tokens oder URLs in diesen Logereignissen. `programme_probe84` bietet eine ausdrückliche lokale Prüfung und reicht den einmal bestätigten Kandidaten zur bestehenden Bilddekodierung durch; bei Opt-out erfolgt bereits vor dem Konfigurationstest kein API-Aufruf; normale Detail-/Hero-Texte enthalten keine internen Uppercase-Codes. Kodi-Bibliotheksfehler bleiben ausschließlich read-only diagnostiziert. Ein Probe-TMDB-Treffer beweist nicht dessen Anzeige, wenn der Resolver anschließend ein exaktes XMLTV-Bild bevorzugt.

## BINGIE-Geometrie

Aktuelle **Testgeometrie**: Hero **620 px**, Rail-Oberkante **640 px**, Medienreihen **244 px**. Das ist ein Ausgangswert aus dem verlangten 600–640-Bereich, keine abschließende Box-B-Layoutabnahme. Begrenztes Senderlogo in eigenem Control `296784`, maximal **560 × 280**, `keep/contain`. Event-/Portrait-/Landscape-Bilder proportional; kein Strecken. Rechte Informationstafel 540 × 620 mit **90 % Navy-Deckkraft**, getrennten Text-/Progress-/Quellenbereichen. Film↔Serienabstand verkleinert, Serienreihe normal per Scroll erreichbar.

Änderungen laufen ausschließlich über den vorhandenen gesicherten Adapter: bekannte owned Nodes, exakte Digest-Verträge, Vorschau/Zustimmung, Backup und Rückrollmöglichkeit. Unbekannte persönliche Graphen und Opt-out werden nicht überschrieben. In dieser Sitzung wurden keine Geräte-/persönlichen Skin-Dateien verändert. Hero-Basisgeometrie wird unabhängig vom kleinen sichtbaren Logo gemessen, damit die Ladephasen nicht am Logo-Control hängen bleiben.

## Offen / Blocker, ausdrücklich kein Vollständigkeits-PASS

Der [PR-Nachtrag](https://github.com/artattakk-creator/kodi-noodleprivate/pull/405#issuecomment-6741573753) verlangt, nicht abgeschlossene Schritte offen mit Abnahmeblocker auszuweisen.

| Anforderung | Stand / Grenze |
|---|---|
| Neuer temporärer **Bilddatei**-Cache mit hartem Byte-/Objektlimit, LRU, Pins/Refcounts und Ende+Grace | **OPEN / Abnahmeblocker.** Implementiert sind begrenzte Referenzmetadaten/RAM-Leases und Wiederverwendung vorhandener Kodi-Dateien. Ein neuer Datei-Eviktor ist nicht implementiert. Bestehende Archivdateien besitzen keinen hierfür verifizierten Löschbesitz; sie werden nicht bereinigt. Kein globales Kodi-Cachelimit behaupten. |
| Ausschließlich tatsächlich sichtbare Film-/Serienposter nachladen | **PARTIAL / OPEN.** Bestehender begrenzter Widgetbestand bis 24 Referenzen, Phasenpriorität und Fokus erhalten. Noch kein vollständiger eigener Cover-Viewport-/Pin-Lifecycle für jede BINGIE-Variante. Legacy-Archivmodus bleibt erhalten; keine Zusage, dass außerhalb von Reservesperre ausschließlich sichtbare Bildkörper geladen werden. |
| Persistenter Wiederaufnahmecursor des Metadaten-Imports | **OPEN.** Session-/RAM-Cursor vorhanden, Referenzjournal nur bei ausreichender Reserve. Unter vollständig blockierten Writes kein dauerhaftes Pending-Importjournal. |
| Android-Kapazitätswiderspruch / #401 Migration | **OPEN, nachgelagert.** 3,76 GiB ist die gemessene FUSE-Pool-Gesamtkapazität, kein Artwork-Verbrauch. Kein Speichergewinn erfunden. Caber-Toss-SMB-Schreibnachweis nicht als pauschalen Rechtefehler umdeuten. Keine Migration ausgeführt. |
| Tatsächliche Bilder / endgültige Geometrie auf Box B | **ANDROID_NOT_TESTED.** Insbesondere The Middle, King of Queens, DS9, Blauwal/XMLTV und Providerposter benötigen reale sichtbare Nachweise. |

## Bestandsschutz und Nachweisgrenzen

Provider, Token, EPG-Mappings, Favoriten, Archive, Kodi-Datenbanken, Widgets, SkinShortcuts, Space Blue und Box A bleiben unangetastet. Router, Keymaps, Player-Exit-Implementierung, Moduswahl und Installer **0.5.26** bleiben geschützt. Regulär/Pilot/NeoDark3 bleiben byteidentisch auf dem veröffentlichten .83-Stand. Google Drive/WebDAV sind kein Scope.

URL_APPROVED, IMAGE_DECODED und REFERENCE_HANDED sind unterschiedliche Stufen. Native CI bestätigt zusätzlich echte Kodi-ListItems, Texturdateien und Screenshotpixel bei 1080p/720p und zwei Offline-Neustarts. Das sind synthetische Linux-Kodi-21.2-Nachweise, keine echten TMDB-Account-/Android-Nachweise. Die 27-MiB-Störung betrifft **XCMates Python-Kapazitätsmessung**; Kodis C++-Texturecache schreibt auf real freien Hostspeicher. Kein physischer ENOSPC-PASS.

[Testbericht](TESTBERICHT_02984_DE.md) · [Android-Abnahme](ANDROID_ABNAHME_02984_DE.md)
