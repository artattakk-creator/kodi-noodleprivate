# Bilddokumentation und Redaktionsprotokoll – GS Media 48/48 + Branding

**Begleitdokument zum [vollständigen Installations-How-to](HOWTO_GS_MEDIA_KODI_213_VOLLINSTALLATION_48_PLUS_BRANDING_NEODARK3_2026-11-09_DE.md)**  
**Stand:** 09.11.2026 · **Testgerät:** ausschließlich Box B · **Zweck:** aus tatsächlich ausgeführten und fotografierten Arbeitsschritten später ein bebildertes, druckfähiges PDF und eine leicht verständliche Schritt-für-Schritt-Anleitung erstellen.

**Regel:** Alle Bilder in diesem Dokument sind derzeit **GEPLANT, NICHT AUFGENOMMEN**. Keine Screenshots/Ergebnisse fingieren; Pakete/Kataloge sind GitHub-seitig verifiziert, nicht als Android-Vollinstallation abgenommen. Fotos und Uhrzeiten werden nur nach tatsächlichem Gerätetest ergänzt. Ein von uns verfasstes How-to ist **kein** Beleg, dass Kodi den Schritt auf der Box erfolgreich absolviert hat.

## A. Verbindliches Dokumentformat

Jeder Arbeitsschritt erhält denselben Aufbau:

1. **Schritt-ID und sprechende Kapitelüberschrift** (z. B. `INST-02` „Pilot-Repository installieren“).
2. **Zweck/Voraussetzung** in einem Satz.
3. **Tastenfolge durch Kodi** in maximal 3–6 kurzen Einzelschritten; Fernbedienung statt Maus voraussetzen.
4. **Screenshot-ID mit Bildlegende und Fokuspunkt**: Was soll auf dem Bild sichtbar sein? Welche Option wird ausgewählt? Bei mehreren Klicks mehrere Bilder mit `a`, `b`.
5. **Soll-/Ist-Ergebnis**: erwartete Kodi-Meldung, tatsächlich beobachtete Meldung, Status `NOT_TESTED`, `PASS`, `FAIL` oder `BLOCKED`.
6. **Fehlerhilfe**: ein reproduzierbarer Fehlercode, exakte Paket-ID und N/48, nächster sicherer Schritt. Auf Bild erkennbare private Angaben im Original erhalten, aber vor Veröffentlichung maskieren.
7. **Standnachweis**: Gerät Box B, Kodi-/Repo-/Installer-Version, Datum, Quelle, Screenshot-Dateiname, Test-/Issue-Link. Keine privaten IPs, Portalnamen, Gerätekennungen oder Zugangsdaten in GitHub/PDF.

## B. Bildplan: alle benötigten Aufnahmen

Die Dateinamen sind **geplante Redaktionsnamen**, **noch keine vorhandenen Dateien**. **Nicht** blind auf GitHub verlinken, bevor redigiertes Bildmaterial zur Veröffentlichung tatsächlich freigegeben und hochgeladen wurde.

| Bild-ID | How-to-/Testschritt | Was fotografiert werden soll | Bildunterschrift im späteren PDF | Aufnahmestatus |
|---|---|---|---|---|
| IMG-01 | BACKUP-01 | Übersicht der Backups auf geprüftem Ziel *ohne* sichtbare Ordnernamen/Zugänge | „Vor dem Zurücksetzen: Sicherung prüfen“ | NOT_CAPTURED |
| IMG-02 | BASE-01 | Frisches Kodi 21.3 mit Estuary-Startseite | „Kodi erstmals ohne Zusatz-Add-ons starten“ | NOT_CAPTURED |
| IMG-03 | INST-01 | Kodi **Einstellungen → Dateimanager** | „Im Dateimanager die Netzwerkquelle hinzufügen“ | NOT_CAPTURED |
| IMG-04 | INST-01 | **Quelle hinzufügen**, Eingabe `https://tinyurl.com/neodark3` | „Die NeoDark3-Adresse exakt eintragen“ | NOT_CAPTURED |
| IMG-05 | INST-01 | Quellenname **NeoDark3** / verfügbare Quelle im Dateimanager | „Die Quelle als NeoDark3 speichern“ | NOT_CAPTURED |
| IMG-06 | INST-01 | Online-Verzeichnis mit Pilot-ZIP und Installer-ZIP | „Die beiden benötigten Installationsdateien sind sichtbar“ | NOT_CAPTURED |
| IMG-06A | INST-02 | Erster Kodi-Aufruf **Add-ons → Paket-Symbol → Aus ZIP-Datei installieren**, darauf Sperrhinweis | „Beim ersten ZIP-Aufruf weist Kodi auf deaktivierte unbekannte Quellen hin“ | NOT_CAPTURED |
| IMG-06B | INST-02 | **Zahnrad → System → Add-ons → Unbekannte Quellen**, Schalter einschalten | „Unbekannte Quellen für die Installation bewusst aktivieren“ | NOT_CAPTURED |
| IMG-06C | INST-02 | Kodi-Sicherheitswarnung, Auswahl „Ja“ – ohne private Inhalte | „Die Sicherheitswarnung lesen und mit Ja bestätigen“ | NOT_CAPTURED |
| IMG-06D | INST-02 | Zurück zu **Add-ons → Paket-Symbol → Aus ZIP-Datei installieren** | „Nach der Freigabe erneut Aus ZIP-Datei installieren öffnen“ | NOT_CAPTURED |
| IMG-07 | INST-02 | **NeoDark3** im nun offenen ZIP-Dateibrowser | „Nun die NeoDark3-Quelle auswählen“ | NOT_CAPTURED |
| IMG-08 | INST-02 | Auswahl `repository.gsmedia.pilot-1.9.12.zip` | „GS Media Pilot Repository 1.9.12 auswählen“ | NOT_CAPTURED |
| IMG-09 | INST-02 | Repo erfolgreich installiert/aktiv, sichtbarer Name/Version | „Das Pilot-Repository ist einsatzbereit“ | NOT_CAPTURED |
| IMG-10 | INST-03 | **Aus Repository installieren → Pilot → Programm-Add-ons** | „Zum XCMate Media Center Installer wechseln“ | NOT_CAPTURED |
| IMG-11 | INST-03 | Detailansicht **XCMate Media Center Installer 0.5.26** | „Die richtige Installer-Version prüfen“ | NOT_CAPTURED |
| IMG-12 | INST-04 | Installer-Startbildschirm und sichere Neuanlage/Fortsetzen-Auswahl | „Den vollständigen Installationslauf starten“ | NOT_CAPTURED |
| IMG-13 | INST-04 | Echtes Fortschrittsfenster, Paketnummer **N/48**, konkrete Paket-ID | „Der Installer prüft und installiert 48 Komponenten“ | NOT_CAPTURED |
| IMG-14 | INST-04 / Fehlerfall | Stoppdialog mit lesbarer **Paketnummer, Code und Add-on-ID** | „Bei einem Fehler genau diesen Zustand dokumentieren und den Lauf fortsetzen“ | NOT_CAPTURED |
| IMG-15 | INST-06 | Tatsächlich bestätigter **Space Blue Manager 0.2.0** / Skin-Abgleich | „Branding und BINGIE MOD werden geprüft“ | NOT_CAPTURED |
| IMG-16 | INST-07 | Finale 48/48 + nachgelagerte Branding-/Neustart-Meldung | „Der Installer meldet Abschluss; Kodi wird danach manuell neu gestartet“ | NOT_CAPTURED |
| IMG-17 | INST-07 | Kodi-Start nach Abschluss mit aktivem BINGIE Space Blue | „So sieht die neue XCMate-Startseite aus“ | NOT_CAPTURED |
| IMG-18 | INST-08/09 | Live-Startsender, reale Senderlogos, Hero/EPG und Ladeanzeigen | „Senderleiste, EPG und Medienzeilen überprüfen“ | NOT_CAPTURED |

| IMG-19 | POSTINSTALL-WIDGETS | XCMate → Einstellungen → Aussehen und Darstellung → Widgets | „Die drei XCMate-Widgetverknüpfungen auswählen“ | NOT_CAPTURED |
| IMG-20 | POSTINSTALL-WIDGETS | BINGIE-Home-Zielauswahl mit Position und „Ja, diese Verknüpfung speichern“ | „Film- und Serienwidgets einer freien Home-Position zuordnen“ | NOT_CAPTURED |
| IMG-21 | POSTINSTALL-WIDGETS | Falls nötig: BINGIE Skin-Einstellungen → Shortcuts → Menü bearbeiten → Home/Widget | „Nach einem Neuaufbau das native BINGIE-Home-Profil anlegen“ | NOT_CAPTURED |
| IMG-22 | POSTINSTALL-WIDGETS | Echte Home-Anzeige mit Filmen-/Serienpostern und Fokus | „Eingebundene Film- und Serienreihen überprüfen“ | NOT_CAPTURED |

**Prinzip bei echten Fehlern:** Jede zusätzliche Fehlermeldung erhält eigene Aufnahme `ERR-NNN`, Gerätelauf-ID, betroffene Add-on-ID und GitHub-Issue-Bezug. Das dokumentiert nicht nur den Endzustand, sondern hilft Codex, einen Fehler reproduzierbar **dauerhaft** im Installer zu beseitigen.

**Neu bestätigt am 09.11.2026:** Der Nutzer hat die **TinyURL-Quelle NeoDark3** tatsächlich eingerichtet. Beim Beginn der ZIP-Installation wurde der Ablauf über „Unknown Sources“ mit anschließendem Zurückgehen und erneutem Aufruf beschrieben; die **Kodi-Warnungsbestätigung und die erfolgreiche Repository-Installation sind noch nicht einzeln als abgeschlossen bestätigt**. Deshalb bleiben alle Bild-IDs `NOT_CAPTURED`; die Screenshotanzahl steigt **von 18 auf 26 geplante Aufnahmen**, nicht auf 22 vorhandene Fotos.

## C. Maschinenlesbare Quellen für eine spätere PDF-Produktion

Der begleitende [Bild-/Schritt-Manifestentwurf](HOWTO_GS_MEDIA_BILDMANIFEST_2026-11-09.json) enthält pro Bild `image_id`, `step_id`, `caption_de`, `expected_view`, `status`, `asset_path` und `evidence`. `asset_path=null` bedeutet: Bildmaterial liegt **nicht** öffentlich vor; erst nach expliziter Prüfung/Freigabe kann ein relativer Pfad in `docs/XCMate/assets/howto-neo-dark3/` eingetragen werden. **Keine privaten Bildschirmfotos, Rohlogs oder echten Credential-Felder automatisiert ins öffentliche Repo committen.**

Beim PDF-Satz kann das Programm je Schritt Titel, Kodi-Klickpfad, Beschreibung, Screenshot (falls vorhanden), Bildunterschrift, Prüfhinweis und Tipps aus Manifest + How-to übernehmen. Fehlt ein Foto, wird die betreffende Abbildung **ausgelassen und intern als TODO** markiert – **keine** generierte Nachbildung als tatsächlicher Test-Screenshot ausgeben.

## D. Datenschutz und Bildqualität

- **Vor dem öffentlichen Upload:** Passwörter/Tokens, Portal-/Xtream-URLs, MAC-/Geräte-IDs, interne IPs/SMB-Freigaben, QR-Codes und private Inhalte abdecken; lieber den relevanten Kodi-Ausschnitt als ganzen Fernseher zeigen.
- Hochformat des Handys ist möglich; für Druck lieber lesbares **16:9-Querformat**, scharf, ohne starken Spiegelreflex; mindestens so, dass Menütext und Versionen klar erkennbar sind.
- Das **unveränderte Original** bleibt ausschließlich privat. Für GitHub/PDF eine **separate redigierte Kopie**. Prüfung des Bildinhalts vor Upload ist erforderlich; geschwärzte Stellen dürfen nicht bloß mit leicht transparenten Markierungen verdeckt sein.
- UI-Bilder aus tatsächlicher Box B von **Konzeptzeichnungen** oder theoretischen Menübeispielen unterscheiden. Keine Behauptung, der Installer hätte schon 48/48 bestanden, solange nur das Design dokumentiert ist.
- Falls ein Bildschirm anders heißt/aufgebaut ist: **Ist-Zustand dokumentieren**, Klickfolge des How-tos anhand echter Beobachtung korrigieren, Abweichung im Installations-Issue erfassen.

## E. Durchlaufprotokoll (bei jeder Nutzer-Rückmeldung aktualisieren)

| Feld | Wert |
|---|---|
| Testlauf-ID | `BOXB-CLEAN-20261109-01` (geplanter Bezeichner, noch keine Ausführung) |
| Gerät | Box B – nicht Box A |
| Ziel | Kodi 21.3, `NeoDark3` → Pilot 1.9.12 → Setup 0.5.26 → 48/48 + Branding |
| Startschritt | `INST-01`: **NeoDark3-Quelle durch Nutzer eingerichtet**; `INST-02`: Sicherheitsfreigabe/ZIP-Auswahl folgt |
| Realer Gerätetest | **IN_PROGRESS – Quelle eingerichtet; ob ZIP-Liste und Freigabe abgeschlossen sind, offen** |
| Aktuelle Screenshots | **0 von 26 geplanten Bildern aufgenommen/freigegeben** |
| Letzter bestätigter Erfolgsstatus | **NeoDark3 als Kodi-Netzwerkquelle angelegt** (Nutzermeldung vom 09.11.2026); Pilotinstallation noch nicht bestätigt |
| Offene Probleme | #407 Installationsabnahme, #401 Python/Storage, #406 Bild-/UI-Abdeckung |
| Nächste Aktualisierung | Tatsächlich sichtbaren Kodi-Bildschirm + PASS/FAIL/Foto nach Nutzerfeedback eintragen |

**Postinstallationsmeldung (09.11., 22:42):** Nutzer meldet 48er-Installer weitgehend erfolgreich, kurzer Hänger beim SlyGuy-Repository, langsames EPG und nach Auswahl nicht sichtbare Filme-/Serienwidgets. Die exakten 48/48-/Branding-Endwerte und neue Kodi-Logs wurden noch nicht bestätigt. Der neue Ablauf für BINGIE-Home-Widgetbindungen ist in Abschnitt 6A des [Voll-How-tos](HOWTO_GS_MEDIA_KODI_213_VOLLINSTALLATION_48_PLUS_BRANDING_NEODARK3_2026-11-09_DE.md) beschrieben; vor GUI-Abnahme keine Bilder als aufgenommen kennzeichnen. Aktuell **26 geplante Motive, 0 Fotoaufnahmen**.

## F. Zielprodukt später

**Bebildertes PDF „GS Media / XCMate – Vollinstallation auf Android Kodi 21.3“**, mit:
- Titelblatt mit Stand/Version und Hinweis „getestet auf Box B“ nur wenn real abgenommen,
- Voraussetzungen / Datensicherung,
- maximal ein bis zwei Schritte pro Druckseite mit nummerierter Menüführung, großem Screenshot, Pfeilen/Markierung, Bildunterschrift,
- 48-Komponenten-Installer-Übersicht und Error/Resume-Beispielen,
- abschließender Checkliste und QR-Code/kurzer URL nur zu **öffentlichen, geprüften** Installationsdateien,
- Anlage „Troubleshooting“ mit echten, behobenen Fehlern und verlinkten GitHub-Issues.

**PDF noch nicht erstellt:** ohne die tatsächlichen Screenshots wäre es nur ein Textdokument mit Platzhaltern. Die Markdown-Anleitung und das strukturierte Manifest liefern die belastbare Basis für eine spätere Erstellung.
