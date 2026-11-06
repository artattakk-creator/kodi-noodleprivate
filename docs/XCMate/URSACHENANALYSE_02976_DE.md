# XCMate 0.1.29.76 – verifizierte Vorbereitung ohne künstlichen Sichtbarkeitsnachweis

## Befund und Freigabe

Die veröffentlichte .75 ließ die automatische Serienvorbereitung erst nach realem Öffnen der Filmleiste zu; restliche Hintergrundarbeit wartete zusätzlich auf die Serienleiste. Genau eine sichtbare Leiste war korrekt, blockierte damit aber die automatische Vorbereitung der unsichtbaren Folgezeile. Der Nutzer hat ausdrücklich erlaubt, verifizierte Bild-/Fallback-Vorbereitung als Freigabe der nächsten Phase zu verwenden. Tatsächlich sichtbare Darstellung muss separat belegt bleiben.

## Korrektur

Der bestehende widget_fast69-Worker und seine begrenzten Caches bleiben verantwortlich. Live-TV muss weiterhin zuerst nativ bereit sein. Danach wird die veröffentlichte Filmseite pro aktivem Portal geprüft: Profil-/Provider-Policy, aktuelle Titel-/Quellreferenzen, Signatur, Alter, lokale Bilddatei oder freigegebene externe Referenz. Fehlende Bilder dürfen als ehrlicher neutraler Fallback vorbereitet sein. Ein Queue-Eintrag allein genügt nicht.

Sind alle aktivierten Filmseiten vorbereitet, werden Serien zugelassen; danach die restliche bestehende Hintergrundarbeit. Keine zusätzliche Queue, kein neuer Worker und keine Änderungen an Routing, XML-Layout, Player oder Skinshortcuts. Bestätigte leere Kataloge und deaktivierte Bereiche blockieren die Folgephase nicht; fehlende oder fehlerhafte Indizes gelten weiterhin nicht als leerer Erfolg.

Sichtbarkeitsnachweise stehen separat in `visible` und entstehen ausschließlich in `observe()` anhand nativer Kodi-Controls/Labels. `phase` bezeichnet nur Hintergrundzulassung; `ready76` enthält Bild-/Fallback-Referenzbelege, keine Pixelbehauptung. Kurze synchrone Zustandsänderungen verwenden einen pro Serviceinterpreter gemeinsamen Lock; Dateiprüfungen finden außerhalb statt. Profil-/Kontextwechsel während der Prüfung verwerfen alte Ergebnisse. Ein fehlender/abgelaufener Veröffentlichungsdatensatz wird trotz identischer Quellsignatur erneut publiziert.

## Bestandsschutz und Grenzen

Basis ist main b3024e9620e8924e880a70fc92ca70e4b5a5658b. Alle 728 bestehenden Quelldateien und bisherigen Testmethoden bleiben erhalten; exakt geprüfte Textdeltas werden von zusätzlichen Schutztests kontrolliert. Veröffentlichte Pilot-.75-ZIP und beide Kataloge bleiben bytegleich. Keine Datenbankmigration, Löschung oder Änderung von Benutzereinstellungen. .76 bleibt ein unveröffentlichter Folge-Draft.

Diese Änderung repariert keine nativen Android-Decoderhänger. #368 bleibt für Stop ohne ACK offen. Native Linux-Tests sind kein Android-Nachweis. Sämtliche neue Android-Gates sind ANDROID_NOT_TESTED.
