# XCMate .55 – Box B, alle Geräteprüfungen zunächst NOT_TESTED

Box B: Android TV 13 / ARM32 / Kodi 21.3 / Titan BINGIE MOD 2.2.3 / Skinshortcuts 2.1.0. Box A unverändert lassen. .54-Daten/Passwörter/Startgruppe/Favoriten/EPG-Mappings/Resume/Autoplay/Artworkmodus bleiben erhalten. Update ausschließlich mit freigegebenem Test-ZIP als bestehendes Add-on; keine Neuinstallation/Deinstallation oder Profil-/Cachebereinigung.

**Zuerst NAV55-01 bis NAV55-04 ohne Skinänderung testen.** Bei erneutem Hänger FAIL markieren; Zeitpunkt, betroffene Menüaktion und feste LIVE_GUIDE-Ereignisse getrennt erfassen. Keine privaten Rohlogs auf GitHub veröffentlichen. Alle Ergebnisse nur als PASS/FAIL/NOT_TESTED eintragen. Host-PASS ersetzt keine Zeile dieser Liste.

## Vorbereitung

ZIP-SHA256 mit der beiliegenden .sha256-Datei vergleichen. Vorherige .42-Kompatibilitätseinstellung und vorhandene Benutzerkonfiguration dokumentieren, nichts umstellen. Nach Update Installations-Popup kontrollieren. Für BINGIE nur den nativen Editor verwenden: Widget auswählen → Video-Add-ons → XCMate → Widgets. Live als erste freie/ausdrücklich selbst gewählte Position, darunter Filme und Serien. Fremde belegte Positionen nicht ersetzen. Speichern vollständig im nativen Editor bestätigen.

**Hero-Skinadapter erst nach gesonderter ausdrücklicher Freigabe und verifizierter privater Sicherung anwenden.** Konkrete vier Dateien, Hashes, Review und Rückrollweg: `integrations/titan-bingie-mod/0.1.29.55/README_DE.md`. Das Add-on-ZIP allein verändert keinen Skin. Filme/Serien und der einfache Quellpicker benötigen keinen Hero-Patch.

Für XMLTV-/Providerbilder sind exakt vertrauenswürdige, zur Nutzung freigegebene HTTPS-Bildhosts in Kodi → XCMate konfigurieren → EPG eintragbar; keine Credentials/URLs mit Query oder Wildcards. Standard ist nur das offizielle TMDb-CDN, dessen Recherche weiter die bereits vorhandene separate Zustimmung und privaten API-Token benötigt. Ohne zulässige eindeutige Referenz muss der neutrale Fallback bleiben. Weder API-Schlüssel noch vollständige private Bild-/Portal-/SMB-Adressen in Testergebnisse kopieren.

| ID | Ausführung und erwartetes Ergebnis | Status |
|---|---|---|
| NAV55-01 | Startsender → vertikale Live-Navigation → jeden Eintrag einzeln aktivieren, insbesondere Einstellungen. Richtige bedienbare Ansicht, kein wirkungsloser Dauerklick und kein Kodi-Neustart nötig. | NOT_TESTED |
| NAV55-02 | Back schließt offene Menüebene; eigene noch wartende Übergabe lässt sich abbrechen. Danach Navigation erneut öffnen. Back aus reinem Live-Vollbild beendet eigenen Stream über erhaltenen .42-Modus. | NOT_TESTED |
| NAV55-03 | Einstellungen/Home/Guide mehrmals öffnen/zurück; schnelle doppelte OK-Eingaben. Genau eine Zielaktion, keine doppelte Wiedergabe und kein eingefrorener Eingabestatus. | NOT_TESTED |
| NAV55-04 | Fremden nativen Dialog abbrechen, anschließend Navigation erneut bedienen. Danach 20 Live-Navigations-/Back-Zyklen; ursprüngliche Kompatibilitätseinstellung erhalten. Fremde Dialoge/Player werden nicht geschlossen. | NOT_TESTED |
| PICK55-01 | Nativer BINGIE-Picker → Video-Add-ons → XCMate → Widgets. Genau Live-TV – Startgruppe, Neueste Filme, Neueste Serien als auswählbare Ordner, keine Hilfe-/Manager-/URL-Ersatzzeilen. | NOT_TESTED |
| PICK55-02 | Live-Ordner als Quelle wählen und native BINGIE-Konfiguration speichern. Keine Portal-/Gruppenabfrage. Nach Kodi-Neustart identische gespeicherte Quelle. | NOT_TESTED |
| PICK55-03 | Film- und Serienordner ebenso verknüpfen/speichern; auch ohne Hero-Patch echte Poster, richtige Details und Neustartpersistenz aller drei Reihen. | NOT_TESTED |
| HOME55-01 | Erst nach separater Skinfreigabe echte BINGIE Home öffnen: Hero Bild links, Logo/Titel/JETZT/DANACH/Plot/Zeiten/Progress rechts, schmale blaue Senderbuttons darunter, Film-/Serienreihen darunter. Mit Chatvorlage visuell vergleichen. | NOT_TESTED |
| HOME55-02 | Ganze Startgruppe mit mindestens 88, möglichst 150 Sendern horizontal durchlaufen. 20+ Fokuswechsel aktualisieren Hero; kein Fokuswechsel startet Wiedergabe. Kein festes 12-/24-Limit. | NOT_TESTED |
| HOME55-03 | OK auf erstem, mittlerem und spätem Sender startet genau den Fokuskanal; Back über erhaltenen .42-Exit, Home/Navigation anschließend bedienbar. | NOT_TESTED |
| EPG55-01 | Bei Sendern mit manueller EPG-Quellenzuweisung Hero, großes EPG und Infobar vergleichen: gleicher Sender/Quelle, Jetzt/Danach, Text, Zeiten und EPG-Fortschritt. Keine Verwechslung gleichnamiger Kanal-IDs. | NOT_TESTED |
| EPG55-02 | Sendungswechsel beobachten, Sender mit Lücke und Tagesgrenze prüfen. Keine alte Sendung/kein fremdes Bild; Zeiten inklusive lokaler Zeitzone stimmen überein. | NOT_TESTED |
| URL55-01 | Vor erneutem Kodi-Start mindestens einen positiven Bild-URL-Beleg im vorhandenen Artworkindex nachweisen (Status, Zeit, Quelle, TTL, Eventbindung; private URL nicht veröffentlichen). Keine lokale Bilddatei erforderlich. | NOT_TESTED |
| URL55-02 | Kodi-Start plus 20+ Fokuswechsel: keine TMDb-/TV-Spielfilm-/EPG-Metadatensuche. Direkte Bild-/CDN-Abrufe durch Kodi sind ausdrücklich zulässig. EPG-Text bleibt sofort bedienbar. | NOT_TESTED |
| URL55-03 | Tatsächlich laufender Film: richtige Filmabbildung für exakt Titel/Jahr im Hero und EPG-Detail, identische gespeicherte URL. Generisches Icon zählt nicht als Bild-PASS. | NOT_TESTED |
| URL55-04 | Konkrete Serienepisode: tatsächliche Staffel/Folge prüfen; richtiges Bild und gleiche URL in Hero/EPG-Detail. Anderes Episodenbild ist FAIL. | NOT_TESTED |
| URL55-05 | Belegtes XMLTV-/Provider-Eventbild: richtige Sendung und gleiche persistente HTTPS-URL in beiden Ansichten. Quelle und Eventbezug prüfen. | NOT_TESTED |
| URL55-06 | Kodi neu starten: vorhandene gültige URLs weiter nutzbar, keine erneute Metadatensuche erforderlich. Sender-/Film-/Serienbindings bleiben gespeichert. | NOT_TESTED |
| URL55-07 | Netz kurz trennen bzw. tatsächlich fehlendes/abgelaufenes Bild prüfen. Neutrales Bild, weiterhin EPG-Text und funktionierende Fernbedienung/Back, kein Freeze. Hintergrundreparatur statt Fokussuche. | NOT_TESTED |
| URL55-08 | Nicht freigegebener Host/fehlendes Nutzungsrecht: ehrlicher Fallback und klarer Status, keine falsche Bildfreigabe. TV Spielfilm ohne belegte Schnittstelle bleibt blockiert. | NOT_TESTED |
| SKIN55-01 | Nur nach eigener Freigabe: konkrete Original-/Kandidatenhashes, private Backup-/Restore-Prüfdateien und tatsächlichen Rückrollweg auf Box B kontrollieren. Unbekannter Skinstand blockiert ohne Überschreiben. | NOT_TESTED |
| REG55-01 | Filme/Serien: Cover, Details, Fernbedienung, Resume und staffelübergreifendes Autoplay; Favoriten, Gruppen und automatische Widgetupdates unverändert. | NOT_TESTED |
| REG55-02 | Vorhandener .54-Wizard und Passwort-/Portalbestand unverändert; ohne Not keinen Neuimport starten. Historische 17 PASS aus #265 erhalten, neue Geräteprüfung nicht daraus ableiten. | NOT_TESTED |
| REG55-03 | „Installation erfolgreich“, installierte Version .55 und konkrete Änderungen sichtbar; einmal bestätigen, nach Kodi-Neustart keine Wiederholung. | NOT_TESTED |

## Rückmeldung

Je ID tatsächliches Ergebnis und kurze Beobachtung, bei Bildtests zusätzlich echte Film-/Episode-/Event-Übereinstimmung bestätigen. Keine privaten URLs, Benutzer, Passwörter, Schlüssel oder Rohlogs. Ein übergebener ListItem-Wert beweist keine sichtbare Textur. Fehlende echte Bildnachweise und eine erneut hängende Navigation verhindern Freigabe. Kein automatisches Schließen von Issues, Merge oder Release.
