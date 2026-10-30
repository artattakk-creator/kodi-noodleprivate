# .59 – Abnahmematrix zu #281 / #277 / #276

| Bereich | Festgestellte Ursache / Änderung | Host | Android / tatsächlicher Endzustand |
|---|---|---|---|
| BINGIE Filmwidgets | Private aktive Home-Konfiguration nicht verfügbar; tatsächlicher erster defekter Skin-Übergang UNVERIFIED. Gültige native generische widgetType-Werte werden nicht mehr fälschlich abgewiesen; native Entry-/Home-Beobachtung getrennt. Keine Bindung geändert. | 24 native Einträge + zehn tatsächlich dekodierte synthetische Providerposter | NOT_TESTED; sichtbare echte BINGIE-Reihe nicht als repariert behauptet |
| BINGIE Serienwidgets | Wie Filme; gleicher bestehender URL-/Directory-Pfad, Provider-only | 24 native Einträge + zehn tatsächlich dekodierte synthetische Providercover | NOT_TESTED; reale Ursache UNVERIFIED |
| Provider-EPG | Wizard-Resume verdrängte normalen Refresh; Busy-Worker konnte Anfrage still verbrauchen. Getrennte Buttons, wartende Nonce, aktuelle Persistenz, Fortschritt und differenzierte Fehler statt Popup | Automatisiert geprüft; bestehende SQLite-/Mapping-Regressionssuite | NOT_TESTED für echten Download, Senderabdeckung, Speicherung/Neustart auf Box B |
| EPG-Bilder | Fehlende EPG-Fakten zuerst; Bildquelle/fehlendes Bild/Hostblockade verständlich getrennt. Keine neue externe API | Lokale Zustände geprüft; bestehende Ereignis-/URL-Bindung erhalten | NOT_TESTED; echte Bildverfügbarkeit UNVERIFIED |
| Live-TV-Zurück | Abgelaufene Stop-Frist machte nach bestätigtem ACK einen vorübergehenden Modalzustand endgültig failed. Bereitschaft statt Dauerfehler; Session-/Parallelitätsguard bleibt | Reproduktion vor/nach, genau eine Rückkehr, kein zusätzlicher Stop | NOT_TESTED; fehlendes natives ACK/Rockchip-Decoderstopp bleibt eigenständiger offener Fall |
| Bestandsschutz | Wizard, .42-Option/Stop, Provider-only Medien, Mappings, URLs/Ordner/Skin unverändert; keine Geräteaktion | Source-/Testinventar und Regressionen | Box A/B unangetastet; echte Abnahme offen |
| #280 / #279 | Experimenteller TVmaze-/eigener TMDB-Connector getrennt | Nicht im Kandidaten | Keine Integration/Freigabe |

Keine Android-PASS-Meldung aus Hosttests, PUBLISHED oder synthetischen Pixeln. Keine Issues geschlossen; kein Merge/Release. Historische .58-Nutzerfehler bleiben erhalten.
