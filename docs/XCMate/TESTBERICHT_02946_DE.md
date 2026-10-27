# XCMate .46 – Testumfang und Prüfbarkeit

Entwicklungsbasis: veröffentlichte .45/main a2f83c49. Code-Build: 7bb7a07 (spätere reine Dokument-/Paketcommits verändern den Add-on-Quellinhalt nicht). Alle1.725 früheren Methoden laufen weiter,152 neue .46-Methoden werden ausgeführt. Kein Skip, keine neue Gerätefreigabe.

**Abschließender Hostlauf:1.877 Tests PASS in283,679s;0 Fehler/0 Failures.1.725 frühere Methoden und152 neue.** ZIP-Inhalt, CRC, sichere Pfade, byteweiser Quellvergleich, Python-AST und unabhängiger reproduzierbarer ZIP-Nachbau PASS.

## Aussagekraft

Kodi21-Hostmodelle und echte lokale SQLite/WAL-, HTTP-, SMB- und Dateisystemtests. Synthetische Provider-/Bilddaten. Keine Android-Box kontaktiert oder installiert. Source-/Commit-/Threadmodelle beweisen Add-on-Zustandsverträge; sie reproduzieren keinen nativen MediaCodec-Deadlock auf RK3528.

Ein vorheriger vollständiger1877er-Lauf hatte genau einen Fehler in der historischen Dateierstellungs-Allowlist: SQLite erzeugte zusätzlich die zulässigen WAL/SHM-Koordinationsdateien der neuen Datenbank. Alle bereits vorhandenen Payloadbytes blieben im selben Test identisch. Die Allowlist wurde ausschließlich um `programme_artwork.sqlite-wal` und `programme_artwork.sqlite-shm` erweitert; die Payload-/Read-only-Prüfung blieb vollständig aktiv. Der abschließende Gesamtbericht enthält den neuen vollständigen Lauf.

Beibehaltene Methodennamen mit ausdrücklich geänderter Produktspezifikation: Der alte12er-Widgetfall erwartet gemäß #241 jetzt alle1001 lokalen Sender; neue137er-Tests prüfen Seiten, Pin, letztes Element und genaue Klick-IDs. Source-Freeze-Tests invertieren ausschließlich die exakt katalogisierten37 reviewbaren Änderungen; native Stop-/Kompatibilitätsimplementierung, Medien-Autoplay/Resume, Referenzinfobar, Icon und freigegebene Suchmaske werden weiterhin geschützt. Keine generischen Ausschlüsse unbekannter Änderungen.

## Paketprüfung

CRC, eindeutige Einträge, sichere relative Pfade, keine Symlinks, keine Python-Bytecodes, keine Datenbanken/Profil-/Rohlogdateien. Vollständiger byteweiser Vergleich jedes Add-on-Dateieintrags mit `src/plugin.video.xtreammate`, Python-AST aller Module und unabhängiger deterministischer ZIP-Nachbau. SHA256 in TESTERGEBNISSE_02946.json und neben der ZIP. Die bestehenden .45-ZIPs und der produktive addons.xml-Index bleiben unverändert.

## Messungen und Geräteabnahme

PERFORMANCE_02946.json enthält25 synthetische Hostmessungen mit frischem Reader/Verbindungen und warmem OS-Cache; keine angeblichen Android-Kaltstartwerte. FLOW46 liefert nur feste Phasen/monotone Zeiten und anonyme Korrelation. `tools/analyse_xcmate_flow46.py` exportiert ausschließlich p50/p95-Aggregate, keine privaten Rohlogzeilen. Getrennte reale Kalt-/Warmmessungen für Playerbild, Gruppen/Mini-EPG und Medienstart stehen im Androidplan.

Native Queue ohne bestätigte Rückkehr: BLOCKED_NATIVE_QUEUE_STALLED. Fehlender BINGIE-Hook/Renderer: BLOCKED_NO_RELOAD_HOOK / BLOCKED_NO_OVERLAY_FOCUS_BINDING. Fehlender20-Tage-Feed: BLOCKED_DATA_NOT_AVAILABLE. Fehlender Decoder, echte Diskreserve, DB-/Artworkbudget und Netzwerkfehler sind keine erfolgreichen Bildtests. Alle neuen Androidfälle NOT_TESTED; .45-Serienbefüllung bleibt ein historischer PASS.

Reproduzierbare Hostvorschauen: PROGRAMME46_HOST_720.png/1080.png und COVER46_HOST_720.png, erzeugt aus der tatsächlichen eigenen XML-Geometrie mit neutralen Testbildern/Hostfonts. Keine Android-Screenshots oder echten Providerbilder.
