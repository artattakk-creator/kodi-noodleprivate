# XCMate .62 – belegte Ursachen, konkrete Reparatur und Grenzen

Basis main `dfe59e98305aa73cfcf3e0c7c7e49dcfb0dbf9ca`, .61. #289 einschließlich Nachtrag und #288 vollständig berücksichtigt. Bestehender Androidbefund .61: Filme/Serien PASS, Live-Home FAIL. Das bleibt historisch erhalten.

## Live-Reader

Der alte Home-Pfad validierte zunächst alle Gruppen mit MovieReader.groups; widget_group46.pages baute einen zweiten Reader auf, lud erneut alle Gruppen und suchte sogar bei absichtlich geleerter Startsender-ID nach sid=''. Dafür wurden ausgewählte Kategorien temporär in SQLite geschrieben. Derselbe enge Reader-Budgetpfad wie bei Medien konnte abbrechen. Anschließend konnte optionale EPG-/Artwork-Dekoration die gesamte Senderliste verwerfen. render verschluckte die Ausnahme als LOCAL_UNAVAILABLE und schloss ein erfolgreiches leeres Directory ab.

Reproduzierter Fehlerpfad: kontrollierter SQLITE_INTERRUPT bei der unnötigen Leer-ID-Abfrage → alter .61-Reader liefert null Items; neuer .62-Reader liefert unter identischer Fehlerbedingung 88. Echter WAL-Writer kann während des Read den Gruppen-Head austauschen, dennoch werden alle 88 Identitäten aus genau einer konsistenten Generation gelesen. 803-Gruppen-Test prüft gezielte SQL-Point-Queries ohne Gruppen-Scan, leere SID-Suche, TEMP-Tabellen oder HTTP. **Welcher dieser bisher verschluckten Ausnahmecodes auf der realen Android-Box konkret vorlag, ist aus den vorhandenen Logs nicht eindeutig bestimmbar.** Dies wird nicht als bewiesene einzelne Android-Ursache ausgegeben.

Neue Live-only-Module ändern weder MovieReader/WidgetQuery noch Film-/Serienpfade: genau konfigurierte und aktivierte Gruppe, eine RO-Transaktion, gepinnter Head, begrenzte Keyset-Seiten, keine COUNT-/OFFSET-/Import-/Netzwerkoperation. Defekte Zusatz-Payloads werden durch sichere Senderidentität aus derselben Katalogzeile ersetzt. Klickziel kommt ausschließlich aus Portaltyp/pid und der SID dieser Zeile. Optionaler EPG-/Artwork-Fehler lässt die Basis-ListItems bestehen. Alle Bilder/Programme bleiben in der vorhandenen gemeinsamen Pipeline, keine Home-TMDB-Sonderlogik.

Bei transientem Budget/Lock/IO kann ausschließlich der bereits vorhandene policygebundene Raw-LastGood-Snapshot derselben Startgruppe verwendet werden. Portal, aktivierte Gruppe, jede Kategorie und Policy vor/nach Read werden geprüft. Fremde Gruppen, geänderte Auswahl und permanente Fehler fallen geschlossen aus. Keine neue Snapshot-Publikation im Home-Read. Leeres Fehler-Directory wird nicht als erfolgreicher Cache veröffentlicht. HOME62 meldet feste Stufe/Fehler/Anzahl, niemals Portal-/Gruppenwerte, Provideradressen oder SQL-Fehlertexte.

## Skinshortcuts getrennt

Originaldatei aus offiziellem 2.1.0-Paket: SHA256 `43d51ee82cac216e62ed4fe6defa1c08eadf20f8b18264ab1e4a6e345680a128`. Zwei tatsächliche xmldata.getiterator-Aufrufe (Zeilen 971/1055) sind unter aktuellem ElementTree inkompatibel; beide Original-Ausdrücke reproduzieren AttributeError, beide gepatchten iter-Ausdrücke liefern dieselben XML-Elemente. Die Stellen betreffen Playlist-/Shortcut-Aufbereitung. Aus diesen Tracebacks allein ist kein kausaler Nachweis für den bereits vorher mit 0 Items antwortenden DirectoryProvider möglich; Fehler und Consumer-Generierung bleiben getrennte Gates.

Upstream-Prüfung: BigNoids alter Master meldet 1.0.18/Python2; der aktuelle MikeSiLVO-Hauptzweig meldet 3.0.6~beta1, verlangt xbmc.python3.0.2 und dokumentiert eine eigene Warnung für v2-Skins. Deshalb kein ungeprüftes Hauptversionsupdate für BINGIE2.2.3. Stattdessen optionaler, exakt hashgebundener Zwei-Aufruf-Fix für das nachgewiesene 2.1.0-Paket. Keine automatische Anwendung, kein ZIP-/Addon-Installer. Vorschau, private Original-/Kandidatensicherung, ausdrückliche Zustimmung, atomarer Austausch und verifizierbare Wiederherstellung. Fremde Änderungen/Versionen werden blockiert. Kodi-Neustart lädt den Code; keine Pycache-Löschung. Originalquelle und Lizenz in tests/fixtures dokumentiert. Benutzereinstellungen, Shortcuts-Bindings und alle Skin-Dateien werden dabei nicht geändert.

## TMDB

Bestehende .61-Implementierung bleibt zentral. Zurück ist jetzt ausdrücklich Position4 ohne Dialog oder Einstellungsänderung; Deaktivieren ist Position5 mit Bestätigung. Sichere Übersetzung lokaler file:- und ausgewählter special:-URIs endet weiterhin im O_NOFOLLOW-Descriptor-Walk. Kein realpath auf beliebige Symlinks, keine Netzwerk-/SAF-/SMB-Umgehung. Bestehende Datei-/Legacy-Priorität, atomare Speicherung, versteckte nicht geheime Neustartrevision und beide Opt-ins bleiben erhalten.

FILE_VALID ist ausschließlich eine Formatprüfung. Echter GET /3/configuration mit privatem Token und TMDB_OK wird auf Box B geprüft. Die Cloud hat weder private Zugangsdaten noch Gerätezugang; kein behaupteter realer TMDB- oder Android-PASS. Normale Filme/Serien behalten Provider-Metadaten/-Cover.

## Merge

Die ausdrückliche aktuelle Chat-Anweisung autorisiert den Merge dieser .62 nach Code-, Paket- und Testprüfung. Frühere Nicht-Merge-/Android-Gates in angehängten Texten sind hierdurch ersetzt. Fremde Skin-/Skinshortcuts-Dateien werden trotzdem ausschließlich nach separater Bestätigung auf dem Gerät verändert. Box A bleibt unangetastet.
