# XCMate 0.1.29.86 – Implementierung und Freigabestand

Basis: `c6124922d067361e37db4dd325710ea89a96002e` (`main`, veröffentlichte .85).
Branch: `fix/xcmate-02986-android-live-hero-mapping`. Auftrag #409, Zusammenhänge #401/#406/#407.
**Review-Build. Kein Merge, kein Release, keine Installation auf Box A.**

## Bestätigte Codepfade und Korrekturen

A: `live_items62.basic()` rief pro Sender Artwork-Auflösung auf; darin konnte selbst die Auswahl einer Provider-Bildadresse bereits auf Bilddateien zugreifen. Der neue `live_rail86` erzeugt die vollständige Identitätsleiste mit einem Gruppen-Read und einem gebündelten Logo-Nachweis. EPG kommt aus dem RAM-Snapshot; es blockiert den Verzeichnisaufbau nicht. Beide bestehenden Live-Widget-URLs verwenden dieselbe schnelle Darstellung, die URLs und der Widgets-Ordner bleiben erhalten. Senderklicks behalten `play_live`/`source_play` und den bisherigen Widget-Token.

`logo_manifest86` führt einen eigenständigen, account-/profil-/gruppen-/quellengebundenen Nachweis. Verifizierte lokale Dateien sowie vorhandene Kodi-Textur-Nachweise werden zuerst gelesen. Der bestehende Provider-Worker lädt begrenzt nach und schreibt nach vollständiger Reserveprüfung atomar. RAM-/Kodi-Renderer-Fallback bleibt bei Schreibblockade möglich. Keine automatische Zieländerung, keine Löschung, keine zusätzliche Datenbank. Ungültige Quelle oder geänderter Dateistempel kann keinen fremden Nachweis übernehmen.

B: Der bisherige Resolver konnte ein Feedbild vor der eigenen TMDB-Suche wählen und eine früh zurückgegebene Cache-Referenz endlos erneuern. Im Home-Pfad werden bestätigte breite TMDB-Backdrops, große verifizierte Szenenbilder und offizielle Poster getrennt behandelt. Mindestgrößen: breite Bilder 960×540 mit Seitenverhältnis 1,3–2,5; offizielle Poster 500×700 mit Verhältnis 0,45–0,85. Kleine XMLTV-Bilder, Providerposter und unbestätigte Vorschläge sind keine Hero-Hauptbilder. Offizielle Poster verwenden einen eigenen großen proportionalen Modus.

Die Auswahl und die Quelle sind an dieselbe Sendung und Mapping-Generation gebunden. Die letzte zulässige Darstellung bleibt hinter dem Nachfolger erhalten; ein Kandidat mit geringerer Qualität verdrängt sie nicht. Remote-Kandidaten werden im eigenen Kodi-Bildcontrol vorbereitet; der Worker verlangt danach eine tatsächlich decodierbare Kodi-Textur. Lokale Bilder werden vollständig decodiert und gegebenenfalls gehasht, bevor sie zur Darstellung freigegeben werden. **Diese Receipts sind keine Behauptung sichtbarer Android-Pixel.** Ereigniswechsel, Opt-out, explizite Quellenwiderrufe und Integritätsfehler dürfen nicht an fremden Bildern festhalten.

C/E: Die Skin-Erweiterung verändert ausschließlich den per Digest bekannten eigenen .85-Hero. Alle übrigen Includes, Templates, Overrides, persönlichen SkinShortcuts und Widget-Pfade bleiben byteidentisch. Eigene Controls für Texturvorbereitung und kompakten Status werden ergänzt. Die vorhandenen Film-/Serien-Ladeanzeigen bleiben erhalten. Zwischengespeicherte Medien dürfen nach der Identitätsleiste vorbereitet werden; sie warten nicht mehr auf eine vollständige externe Hero-Suche. Ein identischer Live-Identitäts-/Logo-Datensatz erzeugt keine neue Veröffentlichung allein wegen geänderter EPG-Texte oder Fortschrittswerte.

D: `series_requests85` blockierte die Recherche bislang vor der Suche auf exakt vorhandenen lokalen EPG-Fakten. Der neue Recherchepfad nutzt denselben vorhandenen Worker, verlangt für die reine Suche aber keine EPG-Daten. Freitext, erneute Suche, Quellenwechsel TMDB-TV/TMDB-Movie/TVMaze und begrenzte Folgeseiten bleiben auch bei null Treffern erreichbar. Charmed-Alternativabfragen unterscheiden die Originalserie und den Reboot über unabhängig gelesene Werkdetails. Kandidaten enthalten Werktyp, Titel, Jahr, Land, Beschreibung und geprüfte Posterreferenz. Kein Suchtreffer wird automatisch gespeichert.

Vor einer ausdrücklichen Speicherung werden Werk-ID, Details und der aktuelle Profil-/Portal-/Sender-/Werk-Kontext erneut gelesen. Veraltete/fehlende EPG-Fakten lassen Suche/Vorschau zu, verhindern aber einen falschen Speichererfolg. Film- und Seriendetails bieten denselben Manager sowie den bisherigen Artwork-Picker. Die vorhandene .85-Mappingdatei wird kompatibel um den Werktyp erweitert. Bewusste TV-/Filmwahl übernimmt keine Episodenfakten. Eigene ausdrücklich gewählte Bilder werden begrenzt gelesen, decodiert, kopiert und gehasht; Originale bleiben erhalten. SMB-Zugriff nur auf die ausdrücklich ausgewählte einzelne Datei, kein automatischer Share-Test oder Scan.

## Ehrliche Grenzen

- Ein anderer nutzbarer Android-Speicherpool wurde auf der physischen Box **nicht** nachgewiesen. `EXTERNAL_UNAVAILABLE` ist ein zulässiger negativer Befund, kein behaupteter Speichergewinn. Der neue Logo-Writer nutzt ausschließlich das vorhandene lokale Ziel und seine volle Reserve. VFS-Ziele werden nicht automatisch als neues Logo-Archiv aktiviert.
- Die reale Sichtbarkeit aller persönlichen Reihen, insbesondere „Frisch im Kino“ und „Diese Woche aktuell“, benötigt Box-B-Prüfung. Byteerhalt und synthetische Kodi-Reihen ersetzen diese nicht.
- Android-Warm-/Kaltstart-SLO, P50/P95, 20 Minuten CSI: Vegas, Mount-/Rechteprüfung und die realen Charmed-/Monk-Matches bleiben **ANDROID_NOT_TESTED**.
- Kein neuer Referenz-Screenshot wurde geliefert. Es gibt keine erfundene Designfreigabe.
- Bestehende Player-/Exit-/Portal-/Speicherreserve-Implementierungen und Installer 0.5.26 bleiben unverändert.

## Tests und Paket

Siehe `TESTBERICHT_02986_DE.md`, `ANDROID_ABNAHME_02986_DE.md` und `test-builds/02986/`.
Automatisierte Ergebnisse werden erst nach abgeschlossenen Läufen eingetragen. Regulär, Pilot und NeoDark3 bleiben auf den bestehenden veröffentlichten Bytes.
