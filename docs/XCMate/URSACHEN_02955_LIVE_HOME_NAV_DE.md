# XCMate .55 – Live-Navigation, native Widgets und gemeinsame Sendungsbilder

Basis: main .54 `2d08ff1e650505aa4d78a1128640d8baacb929c5`. Ein kumulativer Branch `feat/xcmate-02955-live-home`, #266/#267 sowie #239/#252/#254/#265/#263. Kein Merge, produktives Release oder Gerätezugriff. Wizard ab .54 eingefroren.

## Neuer P0-Befund: vertikale Live-Navigation reagiert nicht

Der Nutzer meldet wirkungslose Menüeinträge, unerreichbare Einstellungen und fehlenden Rückweg. Es liegen für diesen neuen Gerätefall keine privaten Rohlogs vor. Deshalb wird keine vollständige Android-Ursache als bewiesen ausgegeben.

Ein konkreter Hostfehler ist reproduzierbar: `live_guide_navigation.request()` setzt nach erfolgreicher Veröffentlichung einer Fensterübergabe `navigator._guide_handoff=True`. Wird die zugehörige Kodi-Window-Property danach entfernt, zu lang oder unlesbar, liefert `_state()` None. Der bisherige Owner-Poll beendet sich dann, ohne die lokale Bool-Sperre zurückzunehmen. `LiveNavigator._accept_input()` lehnt mit dieser Sperre sämtliche Controls und Back ab. Eine neue Settings-Anforderung wird ebenfalls abgelehnt. Der Zustand kann unbegrenzt bestehen bleiben. Dies ist ein ausreichender Add-on-Fehlerpfad für die gemeldete Symptomklasse; der Auslöser auf der konkreten Box ist weiterhin NOT_TESTED.

Die Korrektur gleicht die lokale Sperre vor Eingaben und im Service mit dem echten Auftrag und dessen Owner/Token ab. Ein verwaister lokaler Zustand wird gelöst, ohne fremde Aufträge/Modaldialoge zu löschen oder den Player anzufassen. Eine gültige eigene Übergabe unterdrückt weiterhin doppelte native OK-/Control-Callbacks. Back kann nur die eigene QUEUED-Anforderung abbrechen, solange exakt das eigene Dialogfenster sichtbar ist. Bereits suspendierte/aktive Fenster behalten ihren bisherigen Lifecycle. Keine neue Stop-Strategie, kein Python-Thread als Ersatz für .42.

Neue feste Diagnoseereignisse: `INPUT_RECOVERED`, `CANCELLED`, `REQUEST_REJECTED` mit begrenzten Gründen DESTINATION/PENDING/CLOSED/LOCAL_GATE/OWNERSHIP/NATIVE_OWNER/SESSION/API. Keine Portalnamen, Sendernamen, URLs oder Exceptiontexte. Hosttests reproduzieren Propertyverlust, beschädigte Properties, fremde Owner/Dialoge, erneutes Settings-Queuing, Back und die echte `_accept_input()`-Methode.

## Widgetauswahl statt Verwaltung

Der normale lokale XCMate-Root enthält zusätzlich den passiven Ordner Widgets. Er ist ein natives Kodi-Verzeichnis, kein Einrichtungsbutton. `widget_sources49` liefert genau drei Ordner: Live-TV – Startgruppe, Neueste Filme, Neueste Serien; IsPlayable=false, isFolder=true, ein erfolgreiches nicht gecachtes endOfDirectory. Der neue Auswahlpfad ist ausschließlich BINGIE → Widget auswählen → Video-Add-ons → XCMate → Widgets.

Die Appearance-Liste enthält keinen Widget-Manager mehr. Alte gespeicherte `widget_setup`-/Manager-Aktions-URLs bleiben kompatibel, werden aber nicht im neuen Quellordner angeboten. Der eingefrorene Erstinstallations-/Wizard-Root wird nicht umgebaut. Die Quellen setzen ein bereits konfiguriertes Portal voraus; keine neue Portal-/Gruppenauswahl.

Neue Quellen-URLs verwenden die bestehenden nativen Reload-Properties. Live enthält `home50=1` und verwendet `widget_home50`: ausschließlich explizite gespeicherte Startgruppe, Startsender nur dann zuerst, wenn er zu dieser Gruppe gehört. Alle 88/150+ Sender bleiben vorhanden. Die Route endet direkt bei den Sendern und öffnet keinen Gruppenbrowser. Alte Live-URLs ohne home50 bleiben lesbar. Film-/Serienquellen bleiben die bisherigen recent-Routen samt richtigen Detailzielen. BINGIE speichert die vom Nutzer gewählten Positionen; XCMate überschreibt keine belegten Slots.

## Eine EPG-Quelle und eine Bildreferenz

`guide_v1.sqlite` bleibt führend. Sender/Logos stammen aus dem vorhandenen lokalen Katalog; Now/Next, UTC-Intervalle, Beschreibung und Sendungsfortschritt aus `local_epg` und der bisherigen quellensicheren Mapping-/Merge-Kette. Import, Retention, LastGood und Backup-Gates bleiben unverändert. Keine zweite Widget-EPG-Datenbank.

`programme_urls55` veröffentlicht in der vorhandenen artwork-Tabelle von `programme_artwork.sqlite`. Gespeichert werden bestehender Eventkey und zusätzlicher strenger Bindingbeleg aus Portal, SID, kanonischem Kanal, konkreter EPG-Quelle, Start/Ende und Titelhash, außerdem vollständige HTTPS-URL, Herkunft, Matchingbeleg, Attribution, Auflösungszeit, TTL, Profil- und Hostpolicybeleg und Status. Die bestehende gemeinsame Event-ID wird nicht umdefiniert. Manuelle Quellenwechsel oder gleichnamige Kanal-IDs dürfen kein altes Bild übernehmen.

Ein begrenzter einzelner Bildreferenz-Worker nutzt die vorhandenen Producer. Die unabhängig von Repaints rotierende Startgruppen-Vorbereitung priorisiert acht Sender pro Durchgang und auch deren folgende Sendung; maximal 24 wartende Events. Gültige positive/negative Belege verhindern wiederholte Netzarbeit. Exakte XMLTV-/Provider-Eventreferenzen und bereits vorher verifizierte Referenzen werden wiederverwendet. Nach einer neu beobachteten EPG-Revision ist optional die bestehende strenge TMDb-Suche zugelassen. Die erste Beobachtung ist nur Bootbaseline, niemals TMDb-Suchtrigger; eine fehlende erste Revision gilt nicht als Suchfreigabe. Kein Download des gesamten Programmarchivs.

Der Worker prüft URL/Host/DNS/TLS und begrenzt die Antwortvorprüfung auf 64 KiB Headerdaten/Dimensionen. Er legt keine neue lokale Bilddatei an. Größere fertige Bildbytes lädt Kodi später direkt. Im vorhandenen lokalen Bildarchiv wird nichts entfernt; bereits gültige lokale Bilder bleiben als Legacy-Rückfall lesbar.

Home/ListItem-Aufbau und Sendungsdetails lesen ausschließlich lokale Event-/Artworkdaten. Die frühere Detail-Enqueue-/Publikationsarbeit ist entfernt; der historische Fokusjob wird nur noch geleert, ohne SQLite-/Provider-/TMDb-Recherche. Hero und EPG-Detail lesen denselben Cache-Einstieg. Kodi erhält dieselbe gespeicherte URL mit festen Transportoptionen `redirect-limit=0`, `connection-timeout=3`, `failonerror=true`. Ein Textur-Fallback schützt das Hero; bei Ablauf wird lokal ein neutraler Zustand ausgegeben. Reparatur erfolgt ausschließlich durch die Hintergrundlane. Kein SHA-Nachweis einer lokalen Bilddatei ist Voraussetzung für eine Online-Referenz. Die produktiven Event-Publisher übernehmen keine älteren RAM-Artwork-Manifeste mehr in dieselbe Tabelle: Nur der Referenz-Worker schreibt die neuen URL-Belege. Ein konkurrierender Event-Commit kann damit keine neuere Bild-URL durch einen alten Fallback überschreiben; die bisherige direkte Publikations-API bleibt für Legacy-Aufrufer kompatibel.

## Quellenfreigabe, Fehler und Grenzen

Nur HTTPS/Port443, keine URL-Credentials, Querytokens, Fragmente, privaten Literal-IP-/lokalen Hosts, Headeranhänge oder unsicheren Pfade. Standardmäßig ist ausschließlich der offizielle `image.tmdb.org`-Bildpfad freigegeben. Weitere tatsächlich erlaubte XMLTV-/Anbieter-Bildhosts können unter Kodi → XCMate konfigurieren → EPG als **exakte Hostnamen, Komma getrennt** eingetragen werden. Keine Wildcards oder pauschale Provider-CDN-Freigabe. Eine Änderung hebt gezielt die eigene negative Hostbewertung auf. Unbekannte Hosts liefern `BLOCKED_IMAGE_HOST_OR_URL`, keine falsche Erfolgsmeldung. Bekannte eigene Zugangsdaten im Bildpfad werden vor dem Netzaufruf abgewiesen. Bei nicht freigegebenem Host ist damit ein bewusst ehrlicher neutraler Fallback zu erwarten.

Der Vorprüfer verwendet den bestehenden geprüften Public-DNS-/Pinned-IP-/TLS-Transport ohne Cookies/Authorization und ohne Redirects. Kodi lädt später selbst: hierfür wird keine IP-Pinnung des Kodi-Core behauptet. Zugelassen werden deshalb nur ausdrücklich vertrauenswürdige Hosts; seine Redirects bleiben abgeschaltet. Signierte Bildadressen mit Query werden bewusst nicht an den Skin weitergegeben. Diese Sicherheitsgrenzen können die Zahl nutzbarer Providerbilder begrenzen.

TMDb bleibt optional: bestehende Einstellungen `programme_tmdb46`, `tmdb_research43` und privater Read-Token. Film nur exakt Titel/Jahr/eindeutige Identität; Serie exakt Staffel/Folge und vorhandener Episodentitel. Fertige offizielle CDN-URL und Attribution werden vor der Anzeige gespeichert. API-Token gelangt nie in die Render-URL. Nutzungsrechte bleiben Voraussetzung. TV Spielfilm: **BLOCKED_NO_AUTHORIZED_API / Rechte nicht belegt**, keine Extraktion/Hotlinks. Keine Behauptung, ein technischer URL-Check erteile Bildrechte.

Positive URL-TTL maximal 24h, sendungsbezogen begrenzt. Negative Netzwerkbewertungen 5min; kein unbeschränkter Retry. 404/Redirect/Netzfehler und Host-/Credential-Sperre sind getrennte feste Zustände. Ein späterer Kodi-Texturfehler ist nicht als Bild-PASS messbar; der sichtbare Gerätefehler muss in der Abnahme erfasst werden. Eine sofortige Rückmeldung aus Kodis Textureloader oder ein garantierter sofortiger Netzabbruch wird nicht erfunden.

## BINGIE-Layout und Bestandsschutz

Die freigegebene Chatvorlage ist Layoutreferenz, keine Quelle für hartcodierte Inhalte. Die echte Home-Erweiterung nutzt den vorhandenen Vier-Dateien-Adapter: links 16:9-Programmbild, rechts Logo/Name/Titel/JETZT/Zeiten/EPG-Fortschritt/Plot/DANACH, darunter 76px-Senderreihe mit proportionalen Logos und blauem Rahmen. Nur native OK-Ziele starten Playback. Physische Reihenfolge im BINGIE-Editor: Live, Filme, Serien. Native Sidebar, Uhr, originale Grafiken, fremde Layouts und Film-/Serienreihen bleiben bestehen. Keine Behauptung pixelgenauer Android-Darstellung vor dem Gerätetest.

Review-Diff, exakte Referenzhashes, GPL-Lizenz, Backup-/Restore-Verfahren: `integrations/titan-bingie-mod/0.1.29.55/`. Unbekannte installierte Skindateien blockieren sicher. Die exakt bekannte eigene .50-Erweiterung kann kontrolliert aktualisiert und auf ihren genauen bisherigen Zustand zurückgesetzt werden. Ein alter .50-Anwendungsplan wird nicht mit dem neuen Layout verwechselt.

Der Wizard-/EPG-Import-Freeze und die .42-Stop-Dateien werden zusätzlich zu den historischen Vertragsprüfungen **ohne Normalisierung raw-byte-exakt** geprüft. Alle 2.294 alten Testmethoden bleiben erhalten. Alte Erwartungen „sechs Homeeinträge“ werden gezielt um den ausdrücklich gewünschten passiven Widgets-Ordner ergänzt; historische Methodenbezeichnungen bleiben zur Nachvollziehbarkeit erhalten. Alte Producer-Testdoubles zeigen auf die neue Referenzqueue, ohne die Batch-/Pagingprüfungen abzuschwächen. Es gibt keine neuen Skips.

Das Installations-Popup meldet „Installation erfolgreich“, die installierte .55-Version und die fünf tatsächlichen Changelog-Punkte einschließlich EPG/Bildreferenzen, Navigation und erhaltener Passwörter/Wizard .54. Es wartet weiter auf einen sicheren nativen Zustand und wird pro Version einmal bestätigt.

## Echte Bild-Verifikationsmatrix

| Fall | Hostnachweis | Reales Androidbild in Hero und EPG-Detail |
|---|---|---|
| Film mit exaktem Titel/Jahr | strenger bestehender Matchingtest + persistente URL-Kette | NOT_TESTED |
| konkrete Serienepisode | Staffel/Folge/Titeltest + URL-Record | NOT_TESTED |
| echtes XMLTV-Event | synthetisches SQLite-EPG → Home/Detail identischer Key und URL | NOT_TESTED |
| neutrales Bild/fehlendes Recht | sauberer lokaler Fallback, kein PROGRAMME_IMAGE-Erfolg | NOT_TESTED |

Keine privaten Portale, Kodi-Rohlogs, tatsächlichen Nutzertokens oder Gerätebilder wurden in dieser Umgebung verarbeitet. Hier gibt es keine Android-Box und keine privaten Providerkonten. Echte Provider-/TMDb-Bildabnahme ist deshalb offen; die beschränkte Workspace-Netzpolicy wird nicht umgangen. **Ein echtes Bild-PASS benötigt den sichtbaren richtigen Inhalt am Gerät.**
