# XCMate .66 – Issue-/Abnahmematrix

| Referenz | Implementierung / automatisierter Nachweis | Echte Android-Abnahme |
|---|---|---|
| #300 Fokus/Text | Lokale native Framegrenzen für Fremdposter/Musik, unterdrückter paralleler Globalrahmen, Property-Reihenfolge, begrenzter Plot. Neues natives Kontur-/Kollisionsgate entscheidet | OPEN / ANDROID_NOT_TESTED |
| #291 lokale EPG-Abdeckung | Source-spezifischer Neustart/24h-Plan, 88 Sender vor Fokus, gleiche guide_v1.sqlite, echte Empfangsbelege und lokale Diagnose | OPEN / ANDROID_NOT_TESTED |
| #300 TMDB-Artwork | TV-Klassifizierung ohne erfundene Episode, eindeutiger Titel/Jahr-Details-Match, beschrifteter Serienfallback, lokale Bilddatei und gemeinsame Event-ID. API-Erfolg allein genügt nicht | OPEN / ANDROID_NOT_TESTED; früheres TMDB_OK vom Nutzer belegt |
| #298 / #257 Index/Suche | .65-Queue/Lease/Paging unverändert erhalten, neue >1000-/Genre-/Portal-/Kategorie-Suchstrecken | OPEN / ANDROID_NOT_TESTED; aktueller Adult-Zone-Providercount unbekannt |
| #295 / #297 / #293 / #284 Bestandsschutz | Vorhandener Tokenimport, .42-Live-Back, WELT, Provider-VOD-Widgets, 142×72-Buttons, Grafiken, Portale/Passwörter, EPG/Mappings, Resume/Autoplay, Wizard erhalten | A66-01 bis A66-12 ANDROID_NOT_TESTED |
| Allgemeiner Skin-Adapter, Downloads/Aufnahmen, neue Navigationsebenen | DEFERRED; nicht in .66 implementiert | Kein neues Abnahmegate |

HOST/NATIVE_PASS erst nach tatsächlich grünem finalem Lauf; genaue native Kodi-Version im Artefakt. Ein rotes Gate bleibt BLOCKED und verhindert einen als fertig ausgegebenen technischen Freigabestatus. Box A wird nicht verändert. Unbekannte Skin-Hashes bleiben blockiert. Ohne ausdrückliche neue Freigabe weder Merge noch Repository-Veröffentlichung.
