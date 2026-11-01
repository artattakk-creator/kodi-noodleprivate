# XCMate .65 – Ursachen und kumulative Reparatur

Verbindlich: Master #298 (Chat-Anhang vom Nutzer als identisch bestätigt), #297, #291 und Indexanforderungen #257. Ausgangspunkt main .64, cad966081b9dd6fe75f7ff9cde2a4b286efdcf09. Ein Draft-PR #299. Nutzerfreigabe zum regulären Merge erst nach sämtlichen technischen Gates. Kein Gate erzwingen.

## Token-Zielzugriff

Realer .64-Android-Befund: Quellwahl, VFS und UTF-8-Format erfolgreich; PRIVATE_DESTINATION_READ scheitert vor jedem Schreiben. Der bisherige Leser beginnt mit os.open('/') und läuft jede Pfadkomponente ab. Eine Root-Leseverweigerung ist hostseitig reproduziert und kann trotz zugänglichem Kodi-Profil zum gleichen Vorabbruch führen. Das beweist nicht, dass genau diese eine Ursache auf Box B vorliegt.

.65 öffnet für die exakt aktuelle private Tokenadresse Kodis autoritativen Profilanker und prüft jeden privaten Nachfahren relativ zum Deskriptor. Nur der Kodi-Anker darf bereits normalisierte Android-Mount-Aliasse enthalten; private Unterordner/Datei bleiben O_NOFOLLOW-geschützt. Directory-Flag-/Suchzugriffsvarianten werden ausschließlich mit anschließender fstat-Verzeichnisprüfung verwendet. Kein ungesicherter Kodi-VFS-Schreibersatz für das private Ziel.

Nach ausdrücklich ausgewählter und formal gültiger Eingabe werden fehlende private Kinder sicher initialisiert. Bestehende Dateien bleiben vor Überschreiben vergleichsgeprüft. Nicht sicher lesbarer regulärer Dateieintrag oder Symlink: nur explizite separate Bestätigung kann den einen Eintrag im privaten Profil unverändert unter einem zufälligen Sicherungsnamen bewahren. Ziel des Symlinks wird nie gelesen/geändert. Unsichere private Vorfahren/Verzeichnisse werden nicht automatisch repariert. Kein Löschen von Sicherungen oder anderer Daten.

Feste Phasen, normalisierter Subcode und errno unterscheiden Zugriffsverweigerung, fehlende Eltern, Symlink/kein Verzeichnis, nicht regulären Eintrag, I/O, Read-only und unsupported Directory-Zugriff. Keine Token, Hashfragmente, privaten Pfade oder Rohfehler. Import, Readback, Formatstatus und echter HTTPS-Authentifizierungstest bleiben getrennt. Die maskierte manuelle Eingabe nutzt denselben sicheren Zielcheck.

## Katalog

Belegter Codepfad: catalog_sync löschte den Auftrag vor Arbeit und Lease-Prüfung. .65 hält den dauerhaften Auftrag bis zum verifizierten Abschluss. Aktive Lease blockiert die Entnahme, Rennen beim Lease-Erwerb sind transaktional, gemeinsame Worker serialisiert. Neustart/Abbruch kann keinen verschwundenen Auftrag hinterlassen. Neue/erzwungene Benutzeranforderung während Arbeit wird nicht durch eine alte Abschlusslöschung verdrängt.

Expliziter Kategorie-Nachimport übersprang durch 12h-TTL teilweise einen bereits vorhandenen Head und konnte diesen alten Head als Erfolg melden. .65 fordert die konkrete Kategorie erneut an und verlangt neuen verifizierten Status; eine Lease-Wartephase verbraucht keinen Retry. Source-empty, filtered, cached, failed, cancelled und ready bleiben unterscheidbar.

Gezielte Nachimporte veröffentlichen ausschließlich die angeforderte aktivierte ID. Ein regulärer Gesamtauftrag kann weitere ebenfalls aktivierte Gruppen aus derselben vollständig gelieferten Antwort übernehmen; die Counts bleiben je Kategorie getrennt. Ein ignorierter category_id-Parameter darf keine andere Gruppe als angeblichen Erfolg ersetzen. Leere/ausgefilterte Antworten erhalten den vorherigen Head. Kalter Offline-Fallback importiert nur ausdrücklich erlaubte Kategorien ohne bereits vorhandene brauchbare Generation/Legacy-Daten; Herkunft CACHED bleibt sichtbar, niemals als aktuelle Remote-Verfügbarkeit ausgeben.

Legacy-Refresh aus lokalen Cachedateien kann veröffentlichte heads/items_v2 nicht mehr löschen. Nicht autoritative Teilsnapshots ergänzen Legacy-Zeilen statt gültige übrige Titel zu verdrängen. IDs 0 werden nicht mit fehlenden IDs verwechselt. Keine Filterung nach Kategoriebezeichnungen; Adult Zone ist im Test nur ein fiktiver Kategoriename. Die echte Menge des Anbieterbestands ist unbekannt.

Filme/Serien erhalten einen sichtbaren Gruppen-/Indexstatus im bestehenden Kontextmenü: Auswahl aktiv/deaktiviert, lokaler Count, vorhandene Providerbelege, Generation/Datum, Import-/Verwerfungszahlen und Jobstatus. Gezielter Nachimport und Abbruch pro Gruppe, ohne Portalreset. Statuslesen läuft im vorhandenen Medienarbeiter; GUI zeigt lesbaren Text und paginierte Gruppen.

## EPG

Der Masterguide bleibt guide_v1.sqlite. Der alte Home-Resolver las auch bei gültigem RAM-Handoff erneut SQL. .65 verwendet für diese kurze Darstellung zuerst SID-/Portal-/Mapping-/Profil-/Revisions-geprüfte RAM-Werte und liest nur fehlende Sender nach. Längere Programm-/Archivvorbereitung bleibt auf dem vollständigen gespeicherten Datenpfad.

Beim kalten Lesen werden alle begrenzten autoritativen Sendertexte vor optionaler Sidecar-Anreicherung gelesen. Ein teurer Metadatenschritt darf bereits gelesene Texte anderer Sender nicht verlieren. Gleiche kanonische Referenzen desselben Senders werden innerhalb der gepinnten read-only Transaktion wiederverwendet; keine senderübergreifende Quellenübernahme.

Ein budgetbedingt nicht lesbarer existierender Master löst im Live-Snapshot keinen großen JSON-Kompatibilitätsreload und keine anschließende Serie von Einzelabfragen mehr aus. Gültiger Warm-Handoff bleibt nutzbar; ehrlicher Fehlerstatus bei fehlenden Daten. Kein Provider-/TMDB-HTTP für Text-EPG, kein neuer Guide, keine Datenlöschung.

## Grenzen / Nachweis

Die verwaltete Umgebung ist beim Start gescheitert. Host-/native Kodi-Prüfungen laufen in GitHub Actions, mit synthetischen Daten und isolierten Linux-Profilen. Keine Box A/B, privaten Rohlogs oder realen Zugangsdaten verwendet. Source-/Test-Bestandsschutz .64, vollständige Regression, native Fokus-/Posterstrecken, Vorher/Nachher-JSON, Source-ZIP/CRC/Index/MD5 und SHA bilden die technischen Gates.

Exakte Messwerte, Testanzahl, HEAD und Artefakte stehen im Abschlussbericht von PR #299 und CI. Echte Zielzugriffe, TMDB_OK, Adult-Zone-Providercount und sichtbare Android-EPG-Latenz bleiben ANDROID_NOT_TESTED. Ein grüner technischer Release bedeutet keine vorgetäuschte Geräteabnahme.
