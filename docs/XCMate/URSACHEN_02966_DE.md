# XCMate .66 – Ursachen und kumulative Reparatur

Basis: main .65, 5dfc989a6cf71cb61f43b5c3645797e4825b28fc. Auftrag #301, vollständige UEBERGABE_CODEX_02966_20261101_DE.md, #300, #291 und offene Geräteabnahme #298. Ein Branch fix/xcmate-02966-epg-artwork-focus, Draft-PR #302. Keine automatische Merge-/Releasefreigabe.

## Befundgrenzen

Der Nutzer hat TMDB_OK am echten Gerät bestätigt. Das belegt Authentifizierung und Antwort, nicht Bildauflösung, Bilddatei, Persistenz oder sichtbare Darstellung. Nitro/MacGyver-Text ist für einen Sender sichtbar; die Vollständigkeit über 88 Sender ist nicht bewiesen. Die Fotos enthalten keine sicher lesbare installierte Version. Kein pauschaler .65-Gerätestatus. Keine privaten Originalfotos, Rohlogs, Zugangsdaten oder Providerkataloge wurden für Hosttests verwendet.

## EPG-Planung und Kaltstart

Der alte Scheduler behandelte WAIT_ACTIVE_CATALOG und IMPORT_BUSY_OR_LOCK_UNAVAILABLE wie eine 24-Stunden-Sperre. Ein beim Start noch fehlender Senderkatalog konnte damit den später möglichen vollständigen XMLTV-Import für den Rest des Tages verhindern. Ein frischer Kurzcache sowie ein beliebiger letzter Quellerfolg wurden außerdem als globale Frische behandelt.

.66 unterscheidet kurze 60-Sekunden-Wartezustände von Benutzerabbruch und Sicherungssperre. Erfolg gilt nur für die betreffende stabile Quelle; unbekannte externe Quellen werden nicht durch Anbietererfolg als aktuell ausgegeben. Bei alten Daten darf der gemeinsame Guide-Zeitstempel nur für genau eine nachgewiesene Quelle als Neustartanker dienen. Mehrere undatierte Quellen sind unbekannt und werden gezielt geprüft. Das bestehende Intervallsetting wird nicht umgeschrieben; die fällige Hintergrundplanung hat entsprechend Master eine Obergrenze von 24 Stunden. Deaktivierte Quellen und epg_auto_refresh werden respektiert.

Alle ausgewählten Live-Kategorien werden weiterhin durch den bestehenden paginierten Katalog gelesen, nicht durch die Liste zuletzt angewählter Sender. Der Hintergrundproduzent wärmt die komplette übergebene Startgruppe aus guide_v1.sqlite, bevor sein begrenzter Artwork-Cursor acht Sender auswählt. Keine HTTP-Abfrage im GUI-/Fokuspfad, keine zweite EPG-Datenbank. Die .65-RAM-Identitäts-/Profil-/Mapping-/Revisionsprüfung bleibt erhalten. Ein nach dem Read geänderter WAL-Dateistatus löst keine sofortige doppelte Aufwärmrunde aus.

## Quellenbelege und Korrekturen

Nach vollständig validiertem XMLTV werden tatsächlich gespeicherte eindeutige Datensätze, Zeitgrenzen, normalisierte Quellrevision sowie Sender-Mappingzahlen ermittelt. Der vorhandene Quellenbericht enthält Versuch/Erfolg und tatsächliche gelieferte Abdeckung; kein ausgedachtes 20-Tage-Versprechen. Quell- und Gesamtbestand bleiben getrennt. Menü im EPG-Manager öffnet eine workerbasierte lokale Senderabdeckung mit READY, UNMAPPED, SOURCE_EMPTY, EVENT_OUT_OF_WINDOW, STALE oder DB_UNAVAILABLE.

Zeitkorrekturen werden nur bei gleicher nachgewiesener Quelle/Priorität, eindeutigem Titel und identischer aussagekräftiger Beschreibung, mindestens 80 Prozent Intervallüberlappung, begrenzter Zeitabweichung und ohne Kollision mit anderen Sendungen übernommen. Primärer Eintrag und dessen Quellintervall werden gemeinsam innerhalb der bestehenden Guide-Transaktion korrigiert. Ein bereits gespeicherter eindeutig veralteter Quellzeitpunkt wird nur in seine bewiesene Korrektur zusammengeführt. Andere Programme bleiben erhalten; Abbruch rollt auch diese Änderungen zurück. Unklare/kurze Beschreibungen und mehrdeutige Folgeintervalle bleiben konservativ geschützt. Wiederholter Serientitel allein ist kein Deduplizierungsbeweis.

## Artwork nach TMDB_OK

Der bisherige eigene Resolver akzeptierte TV nur bei Staffel- und Episodennummer. Eine korrekt als Serie klassifizierte EPG-Sendung ohne diese Angaben konnte trotz gültigem Token keinen eigenen TV-Suchpfad erreichen.

.66 sucht bei solcher Klassifizierung vollständig und konservativ nach der Serie, prüft Original-/lokalisierten Titel und vorhandenes Produktionsjahr und verifiziert den eindeutigen Treffer über unabhängige Details. Mehrdeutige Remakes und abgeschnittene Ergebnislisten ergeben NO_MATCH_AMBIGUOUS. Fehlendes geeignetes Bild ergibt NO_ARTWORK. Staffel-/Episodenbilder behalten ihren bisherigen exakten Pfad; ein allgemeines Serienbild ist ausdrücklich series_fallback und kein erfundenes Episodenstill. Für MacGyver ohne genug Identitätsbelege darf deshalb weiterhin ein ehrlicher Fallback erscheinen.

Die vorhandene URL-/DNS-/TLS-/Credential-Policy bleibt aktiv. Das Bild wird im bestehenden persistenten Event-Bildcache materialisiert und über dieselbe Eventidentität in Home und Detail verwendet. Ein neuer Matching-Fingerprint ersetzt keine Dateien und löscht keine globalen Jobs; nur normal angeforderte negative Eventzustände werden nach der korrigierten Policy neu bewertet. Provider-VOD-Poster und Medienmetadaten behalten ihre Providerquelle. Kein Tokenimport, keine neue Zugangseingabe und kein Einschalten deaktivierter Rechercheoptionen beim Update.

Diagnose trennt fehlende Klassifizierung, Opt-in, Authentifizierung, mehrdeutigen Match, fehlendes Artwork, Netzwerk-/Speicherfehler und angeforderte GUI-Bildausgabe. GUI_IMAGE_REQUESTED bestätigt nur den gesetzten Bildpfad, niemals echte Android-Pixel.

## BINGIE-Fokus und Text

.64/.65 zeichnete bereits lokale Rahmen für XCMate-Film-/Serienitems. Andere Widgets blieben am absoluten BINGIE-Globalrahmen mit Basis-top 611 und verzögerten Widget-Eigenschaften. Unterschiedliche Zeilenhöhen und Scrollzustände wurden von den bisherigen nativen Tests nicht vollständig abgedeckt. Im originalen SetFixedVerticalNavigationProps wurde CurrentWidgetID vor einer davon abhängigen Bedingung zum Setzen von CurrentWidgetPos aktualisiert.

.66 bindet auch die betroffenen nativen Fremdwidget-Rahmen an Control.HasFocus(widgetid) und die Abmessungen ihrer tatsächlichen focusedlayout-Gruppe. Globale Parallelrahmen werden beim tatsächlichen Fokus in der Widgetgruppe unterdrückt; die bekannten Live-Buttons bleiben 142×72. Die bekannte Home-Variante publiziert Position vor Identität. Die originalen nativen Titel-/Metadatenbausteine bleiben erhalten, erhalten aber ein begrenztes relatives Textflussbudget: Titel 140, Metadaten 100, Plot 48 plus Abstände innerhalb eines 310 hohen Ausschnitts. Damit können zusätzliche Metadaten oder lange Titel die zweizeilige Reg22-Vorschau nicht unter eine Widgetüberschrift drücken. Alte bedingte Caption-Verschiebungen aus diesem kompakten Textbereich entfallen; Player, Resume-Daten und übrige Skin-Animationen bleiben unverändert. Der native Mischwidget-Test reproduzierte zunächst korrekt sitzenden Rahmen, aber Plot-Pixel bis in die Überschrift; die Grenze wurde anhand dieses Rendernachweises korrigiert, ohne Framepositionen zu verschieben.

Dies ist ausschließlich eine Erweiterung des vorhandenen BINGIE-2.2.3-Adapters. Vier bekannte Dateien, exakte Hashkette, Diff/Vorschau, gesondertes Ja, Sicherung und Rücknahme. Eine .65-Anpassung benötigt neue Zustimmung; ein Update verändert keine Skin-Dateien automatisch. Unbekannte Anpassungen sind BLOCKED. Keine Verallgemeinerung auf andere Skins, kein neues Routing und keine Keymap-/Playeränderung.

Die endgültigen nativen Kontur-/Textkollisionsbelege entscheiden über diesen Fix. Ohne diese Belege kein Darstellungs-PASS. Android bleibt unabhängig davon offen.

## Bestandsschutz und Grenzen

647 vorhandene Quelldateien und 2665 historische Testmethoden/Skip-Bedingungen werden anhand des unveränderlichen .65-Bestands geprüft. Vollständige explizite Vorher-/Nachher-Deltas werden nur in historischen Quell-Snapshotverträgen normalisiert; Runtime-Tests führen den neuen Code aus. Der bestehende .53-Neustarttest erhält einen wirklich zu seiner ausgewählten externen Quelle gehörenden Fixture-Import statt eines deaktivierten Providerimports; seine Frische-/Folgetag-Assertions bleiben erhalten. Der historische Service-Threadtest erhält ebenfalls einen belegten Anbietererfolg statt des jetzt unzureichenden Kurzcache-Frischeflags; seine Thread-/Aufrufasserts bleiben unverändert.

Die verwaltete Ausführungsumgebung ist ausgefallen. Alle Builds, Host- und nativen Kodi-Prüfungen laufen in GitHub Actions mit isolierten synthetischen Profilen. Tatsächliche Kodi-Version des nativen Renderers steht im CI-JSON. Keine Behauptung eines Android- oder zusätzlichen nativen Versions-PASS ohne ausgeführten Nachweis.

Echte Android-Abnahme A66-01 bis A66-12 bleibt ANDROID_NOT_TESTED; die übernommenen Nutzerbefunde bleiben separat als reale historische PASS/FAIL dokumentiert. Kein Box-A-Zugriff, Profilreset oder produktives Release.
