# XCMate 0.1.29.84 – Bildanzeige vor optionaler Archivspeicherung

Stand: 09.11.2026. Basis `ee42712655cb9adcdcb11b09d591a1737d899844` (.83), Master #403. Ein Branch `fix/xcmate-02984-artwork-visible-first`. Kein Merge und keine Veröffentlichung freigegeben.

## Ursachen und begrenzte Korrektur

Die bereitgestellte Forensik dokumentiert etwa 27–28 MiB verfügbaren Platz, 24 Film-/Serieneinträge mit null anzeigbaren Bildern und vorhandene Quellreferenzen. Die privaten Rohlogs wurden für diesen Build nicht erneut heruntergeladen oder veröffentlicht. Kodi-Systeminfo und Pfadstatistik widersprechen sich weiterhin; daraus wird kein zusätzlicher freier Speicher abgeleitet.

Im Quellcode blockierte `persistent()` die RAM-Referenzversorgung in `widget_assets69`, während die interne Archivierung wegen der unveränderten Reserve keine Dateien schreiben durfte. Auch eine große Widget-Frame-Publikation verlangt 32 MiB Reserve. Damit konnte eine korrekte Providerquelle weder über das Archiv noch über die Veröffentlichung zur Anzeige gelangen. Erfolgreich dekodierte Programme im Zustand RAM_ONLY waren zusätzlich von optionalen Statuswrites und der späteren Consumer-Zulassung abhängig.

Die Korrektur trennt ausschließlich die Anzeige von optionalen Archiv-/Statuswrites:

- `artwork_display84`: vorhandener Worker misst tatsächliches Archiv-/Metadatenziel; kurze profilgebundene Druckmeldung. GUI liest nur die Meldung. Keine neue Datenbank, keine Reserve-/Modusänderung.
- `widget_assets69`: existierende Queue und Gesundheits-/Backoff-Logik bleiben erhalten. Lokale Kodi-Texturen werden in allen Modi wiederverwendet. Im gewählten persistenten Modus sind bei Speicherdruck sichere HTTPS-Anzeigereferenzen möglich, mit Konto-/Profil-/Quellenbindung, Public-DNS-Prüfung, maximal 30 Sekunden und `redirect-limit=0`. Keine pauschale URL-Freigabe. Startsender und die ersten fünf Logos werden vor der übrigen Gruppe geprüft.
- `widget_cache82`, `widget_refs74`, `widget_art44`, `programme_assets47`, `widget_data41`, `widget_diagnostics47`, `programme_index46`, `event_art81`: optionale Persistenzversuche bei Reservesperre aussetzen. Bestehende Dateien und Datenbanken bleiben erhalten. Kein globaler Job-Neustart.
- `widget_live47`/`widget_readonly56`: bestehende Read-only-Veröffentlichung und bestehende Widget-/Reload-Routen verwenden. Quellreferenzrevision invalidiert das alte Unchanged-Gate. Die erste echte Referenzversorgung darf genau einmal pro Hook/Kind/Policy die bisherige 60-Sekunden-Bremse passieren.
- `programme_display84`: erst nach vollständiger Bilddekodierung bestehender sicherer Transporte eine kurze Anzeigefreigabe erzeugen. Exakte Ereignisidentität, Fingerprint, Konto, Profil und Nutzerfreigaben binden die Referenz. DNS im Worker erneuern; maximal fünf Minuten ohne erneute Bildvalidierung. Keine DNS-/HTTP-/SQL-Arbeit im GUI-Leser. Definitiv widerrufene DNS-Freigaben sperren die Anzeige.
- Nach Kodi-Neustart darf der Worker ein vorhandenes Kodi-Texturbild nur zur exakt aktuellen XMLTV-/Provider-URL wiederverwenden: zugelassener Texture-Pfad, vollständige Dekodierung, Größen-/SHA256-/Dateistabilitätsprüfung. Keine geratenen TMDB-Zuordnungen.
- Live-Hero: geprüftes Senderlogo ist ein ausdrücklich getrenntes Fallback `station_logo`; es zählt nicht als bestätigtes Sendungsbild. EPG-Text bleibt von der Bildsuche unabhängig.

## Unverändert / zurückgestellt

Player, Router, Keymaps, Skin-XML und Artwork-Moduswahl sind unverändert. Installer 0.5.26 und veröffentlichte .83-Kanäle sind byteidentisch geschützt. Keine Benutzerbilder, Datenbanken, Zugangsdaten, Tokens, EPG-Mappings, SkinShortcuts oder Cache-Dateien werden gelöscht oder verschoben. #401-Migrationsjournal, Google Drive und WebDAV sind kein Bestandteil dieses Fixes. Der unbestätigte Android-Kapazitätsunterschied bleibt offen.

## Aussagegrenzen

URL_APPROVED bedeutet nur zugelassene Quelle; REFERENCE_HANDED nur ListItem-Übergabe; IMAGE_DECODED nur vollständige Dekodierung. Keine dieser Meldungen behauptet Android-Sichtbarkeit. Bei nicht verfügbarer Quelle, Sicherheitsblockade oder fehlender Kodi-Textur bleibt der Fehler beziehungsweise Fallback ehrlich sichtbar. Native CI verwendet ausschließlich synthetische öffentliche Hostnamen im isolierten TLS-Fixture, keine privaten Providerdaten.

Native .84-CI simuliert 27 MiB **in XCMates Python-Kapazitätsmessung**. Kodis C++-Texturecache schreibt auf tatsächlich freien Linux-Hostspeicher. Das ist kein physischer ENOSPC-Nachweis und kein Android-Rendernachweis. Der allgemeine native Test bleibt zusätzlich mit langen Pausen, Neustarts und Player-ACK-Zyklen erhalten.
