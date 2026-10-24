# .29-A – begrenzte Provider-/CDN-Redirects (#135)

Basis: main c17cb4f, produktiv .28. Draft/Teststand, kein Merge/Release/OTA.
Der Android-Befund beweist mindestens eine abgelehnte Weiterleitung, keinen
vertrauenswürdigen Zielhost und keinen erfolgreichen vollständigen Download.

## Vertrag

Unbekannte andere Origins bleiben gesperrt. Der Downloadmanager bietet nach
einer Blockade die Prüfung/Freigabe an: nur für genau das Portal, den ursprünglichen
Quell-Origin und den Ziel-Origin (Schema, Host, Port). Die sichtbaren Hostdetails
bleiben im privaten Gerätedialog. Der Nutzer muss den Host unabhängig als
vertrauenswürdig kennen; es gibt keine automatisch als geprüft behauptete CDN-Liste.
Freigaben lassen sich im Manager je Portal widerrufen. Anschließend gezielt Retry
auswählen; Freigabe allein startet keine Übertragung. Laufende Verbindungen vor
Widerruf bei Bedarf pausieren.

Höchstens fünf GET-Redirects, Loop-Erkennung, Schema-/Host-/Port-Prüfung pro Hop.
HTTP bleibt für vorhandene explizite HTTP-Anbieter möglich; HTTPS wird nie auf HTTP
herabgestuft. Quell- und Ziel-DNS werden geprüft und die geprüfte IP direkt
verbunden; HTTPS behält Zertifikatsprüfung und ursprünglichen Hostnamen/SNI.
Kein Cookie-Jar, automatische Authentifizierung oder Übernahme von Proxy-Credentials.
Nach der ersten Origin-Grenze bleiben nur Accept/Accept-Encoding/Range/If-Range
erhalten, auch wenn eine spätere Weiterleitung zum ursprünglichen Host zurückführt.

Private Adressen brauchen zusätzlich eine ausdrückliche LAN-Freigabe. Erlaubbar
sind nur RFC1918 und IPv6-ULA. Loopback, Link-Local/Metadaten, Multicast, reservierte
Adressen und IPv6-Tunnel/NAT64 bleiben gesperrt. Gemischte sichere/unsichere
DNS-Antworten werden vollständig abgelehnt. Auch ein freigegebener Host muss bei
jedem neuen Verbindungsaufbau die aktuelle Adressprüfung bestehen.

Private SQLite-Datei (0600): nur Quell-/Ziel-Origin, Portalbindung und Freigabe;
die kurzlebige offene Freigabe enthält keine Medienpfade, Queries oder Header.
Anonyme DOWNLOAD_REDIRECT-Marker nennen Statusklasse, Hop, Origin-Wechsel, Schema
und festen Reason-Code; niemals Host/URL/Titel/Portal-ID/Token.

Nach Redirect gelten weiter Content-Length, Content-Type, Magic-/DRM-/Container-,
Dateigrenzen, Freiraum, Teilhash, Range/ETag und sichere Dateiveröffentlichung.
Beim Resume muss auch der Hash des endgültigen Ziel-URLs identisch bleiben;
ein Zielwechsel trotz gleichem ETag stoppt mit SOURCE_CHANGED vor dem Anhängen.
Der URL selbst wird nicht persistiert. Fehlender Validator führt zum vollständigen
Neustart, nicht zum unkontrollierten Anhängen.

## Nachweise / Android-Gates

Gezielte Tests: explizite Portal-/Source-Bindung und Widerruf, Header-Leak/Bounce,
unbekannter Host, relative Ketten, Loop/Hop-Limit, Downgrade, private/mixed/mapped/
NAT64-Adressen, DNS-Rebinding, TLS-IP-Pin/SNI, anonyme Logs, Resume-Zielwechsel und
fehlende/ungültige Content-Length. Reales Zwei-Server-Loopback-HTTP überträgt
Film-/Folgen-Fixtures; nur die Test-DNS-Funktion erlaubt dafür absichtlich Loopback.
Produktions-Loopback bleibt gesperrt. Host-PASS ist kein Android-PASS.

RDX01 Film über tatsächlichen, ausdrücklich freigegebenen Provider/CDN: NOT_TESTED.
RDX02 einzelne Folge über denselben Sicherheitsvertrag: NOT_TESTED.
RDX03 unautorisierte Weiterleitung / fehlende Freigabe bleibt gesperrt: NOT_TESTED.
RDX04 Pause/Resume/Retry, lokale Wiedergabe und nach Neustart offline: NOT_TESTED.

Für die gemeinsame Geräteabnahme ausschließlich den späteren kumulativen .29-C-
Kandidaten verwenden; dieser isolierte A-Branch enthält die USB-/SMB-Reparatur noch
nicht. Vollständige Roadmap #43/#127/#120/#122/#123/#98/#115 bleibt offen.
