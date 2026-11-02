# XCMate 0.1.29.68 – Ursachen und Änderungen

Basis: main `4d8ba5ef2c7bf997af437e230ef1ec52e1e747e8`, XCMate .67, GS Media Repository 1.8.1 Lite. Auftrag: #313 mit Nachträgen 6574386143, 6575216980 und 6575564481. Die hochgeladene Datei war in der ausgefallenen Arbeitsumgebung nicht lesbar; gearbeitet wird nach dem GitHub-Auftrag, wie im Chat angekündigt.

## Verifizierter Codepfad

- Der bisherige Guide-Seitenworker beantragte Senderlogos, aber keine Sendungsbilder. Der gemeinsame Preview-Reader und die Detailansicht lasen ausschließlich vorhandene Programme-Artwork-Einträge.
- Der bisherige Produzent `programme_prefetch48` bearbeitet Home-Startgruppen, nicht beliebige sichtbar ausgewählte Guide-Sendungen. Ein vorhandener Token / TMDB_OK ersetzt diese fehlende Auftragserzeugung nicht.
- Der neue begrenzte Property-Broker `programme_requests68` verbindet Seiten-, Fokus-, Detail- und Hero-Worker mit der vorhandenen maximal 24 Aufträge großen Warteschlange. Der Service nimmt sichtbare Aufträge unabhängig vom verzögerten Bulk-Import an.
- Acht sichtbare Guide-Zeilen liefern höchstens acht ausgewählte Ereignisse. Der lokale Preview-Worker fordert das tatsächlich fokussierte Ereignis nach. Temporäre manuelle Mapping-Vorschauen erzeugen keine Jobs.
- Vor einer Suche lädt der Service das Ereignis erneut aus der lokalen EPG-Basis. Profil, SID, Canonical, Quelle, Quellrevision und Zeitintervall dürfen nicht auf ein anderes Ereignis wechseln. Veraltete Bindungen melden CACHE_MISMATCH.
- Fokussierte Jobs werden priorisiert; nach drei bevorzugten Jobs kommt ein wartender Hintergrundjob zum Zug. Ein bereits wartender Job wird hochgestuft, kein Duplikat erzeugt. Bei voller Queue darf ein noch nicht gestarteter, nicht priorisierter RAM-Auftrag verdrängt werden; er wird beim regulären Warmup erneut erfasst. Keine persistenten Bilder oder Jobs werden gelöscht.
- Der Detail-GUI-Pump führt keine Cache-/SQLite-/Dateileser mehr aus. Sein initialer Worker lädt den Cache; spätere Zustände und fertige Bildreferenzen kommen über begrenzte Properties. Der gemeinsame Preview-Renderer bleibt lokal und behält das offizielle TMDB-Logo als eigene Ebene.

## Zustände und negative Ergebnisse

QUEUED und RUNNING sind echte Warteschlangen-/Workerzustände. LOCAL_IMAGE_READY bezeichnet eine lokal materialisierte Referenz, nicht bereits bewiesene Android-Pixel. CACHE_MISMATCH, NO_MATCH, NO_ARTWORK, HTTP_AUTH, HTTP_RATE_LIMIT und Download-/Cachefehler bleiben Fehlerzustände. Kodi-Texture-Darstellung wird gesondert nativ und auf Android geprüft.

Ein Negativresultat gilt nur für das exakte Ereignis einschließlich Profil, Quelle, EPG-Revision, Tokenrevision, Quellenfreigaben, Bildhost-Freigaben und Budgets. Unveränderte Ergebnisse halten ihren bisherigen TTL; ein erneuter sichtbarer Request löst keinen unbegrenzten HTTP-Retry aus. Positive Dateien werden weder gelöscht noch global invalidiert.

Eigener freigegebener TMDB-Zugang kommt vor optionalen Helper-Abfragen. TVmaze bleibt opt-in und konservativ. Leere zusätzliche Bildhost-Freigabe ist für image.tmdb.org korrekt; keine Wildcard-Freigaben.

## Zentrale Konfiguration

Unter Einstellungen → EPG → privater TMDB-Zugang befindet sich das zentrale Sendungsbildmenü mit getrenntem Token-/Lookupstatus, bestehendem Import, Verbindungstest, einmaliger expliziter Freigabe, optionalen Quellen, Bildbudget, Speicherdiagnose und Credits. Die beiden Legacy-Schlüssel bleiben erhalten und werden nicht automatisch umgestellt; ihre doppelten Schalter werden ausgeblendet. Der Import-/Tokenbestand und sämtliche Portalwerte bleiben erhalten.

## Speicherbefund: drei unterschiedliche Sachverhalte

Die Logs enthalten sowohl SQLITE_FULL als auch errno 28. Der Code begrenzt die additive Programm-/Artworkdatenbank auf 32768 Seiten bzw. bei 4096 Byte 128 MiB. Das ist kein Nachweis, dass jeder SQLITE_FULL ausschließlich vom internen Limit stammt.

Die neue reine Lesediagnose zeigt page_count, page_size, freelist_count, logische Größe, DB-/WAL-Dateigröße, freien Speicher, das konfigurierte Seitenbudget, die 32-MiB-Importreserve sowie das separat wirksame Bildbudget und die Artwork-Sicherheitsreserve. Die Verbindungseinstellung max_page_count wird separat angegeben; sie darf nicht mit der Writer-Policy verwechselt werden.

Interner DB-Grenzstand, niedriger physischer Freiraum, RESERVE_BLOCKED und BUDGET_FULL sind unterscheidbar. Keine automatische Budgeterhöhung, keine Reserveabschaltung, keine Löschung/VACUUM/Retention. Der vorhandene geprüfte Manifest-Fallback bleibt nutzbar, wenn die additive SQLite-Tabelle nicht schreiben kann. Die tatsächlichen Box-B-Werte sind Android NOT_TESTED.

## Mini-EPG und Startgruppen

- Ein kleiner Service-Worker wärmt lokale Katalogmodelle und acht lokale EPG-Zeilen bereits vor der verzögerten Bulk-Phase. Keine Provider-Abfrage oder Reindexierung pro Links.
- Katalogmodelle sind an Profil, Portalidentität, gespeicherte Gruppe und veröffentlichte Indexpolicy gebunden. Warm verwendbare Modelle bleiben innerhalb derselben Policy sofort verfügbar; die Hintergrundaktualisierung ersetzt sie später.
- Fehlende, noch ladende EPG-Zeilen erhalten einen Ladezustand. Bei fehlendem EPG bleibt der Sendername sichtbar. Ein noch fehlender Katalog wird nicht als endgültig leere Gruppe ausgegeben.
- HTTP 404/410 des Short-EPG gelten für sechs Stunden als nicht unterstützter Endpunkt. Lokales XMLTV/EPG und bestehende Snapshots bleiben unabhängig nutzbar.
- `* ` bedeutet alle aktuell aktivierten Gruppen in Provider-Reihenfolge, mit deduplizierten SIDs. Unbekannte oder deaktivierte Gruppen führen nicht zu fremden/globalen Sendern.
- Der eigene Home-Leser erhält die Provider-Reihenfolge. Die historische gespeicherte Widgetquelle behält ihre einmalige Startsender-Anheftung. Bestehende Routen und Widget-URLs bleiben unverändert.

## Externe Befunde und offene Gates

Die gemeldete Arrow/metadatautils/Skin-Helper-Ausnahme wird als externe Kompatibilitätsdiagnose separat geführt. Die neue Anzeige liest nur installierte Versionsnummern. Es werden weder fremde Module importiert/repariert noch Skin-Dateien oder Repository-Schemata geändert. Eine tatsächliche Reparatur dieser externen Abhängigkeit ist BLOCKED bis zur isolierten Reproduktion; sie ist keine belegte alleinige Ursache des fehlenden TMDB-Bildes.

BLOCKED_NO_RELOAD_HOOK wird nicht durch ungefragte Skinänderungen umgangen. Der Hero kann seine bereits vorhandenen Runtime-Properties nutzen; ein fremdes oder fehlendes Reload-Hook bleibt gesondert zu prüfen.

Keine Übernahme aus #306/#312. Keine Änderung an Player-/Stop-Implementierung, Keymaps, Wizard, Medienwidgets, Originalgrafiken oder Benutzerprofilen. Frühere Live-/Exit-Tickets bleiben offen. Ein .67-Stopnachweis ist keine Gesamtfreigabe für .68.

## Testanpassungen

Alle 2768 bisherigen Testmethoden und Skipbedingungen bleiben erhalten. 663 Quellbestände werden gegen die gepinnte .67 geschützt; historische Snapshotprüfungen normalisieren nur vollständig hinterlegte exakte Änderungen.

Zwei historische Tests injizierten Cacheleseergebnisse direkt in den GUI-Pump. Sie erhalten jetzt denselben synthetischen abgeschlossenen Worker-Read; ihre Bild-/Identitätsassertionen bleiben bestehen. Eine historische .61-Fehlerreproduktion verwendet den passenden historischen Seitenleser, damit die inzwischen reparierte .68-Abhängigkeit den alten Fehler nicht verdeckt.
