# XCMate – Zusatzauftrag: Globale Suche optisch und funktional verbessern

Wir ergänzen den laufenden XCMate-Entwicklungsauftrag um eine klare UI-/UX-Anforderung für die **globale Suche**.

Repository:
https://github.com/artattakk-creator/kodi-noodleprivate

Aktueller Hauptstand:
XCMate 0.1.29.32 auf main

WICHTIG:
Dieser Auftrag ergänzt die bereits offenen Arbeiten an der globalen Suche (#140) und an der allgemeinen Roadmap (#143).
Die funktionale Suchreparatur bleibt Priorität 1.
Danach bzw. im selben Folgezyklus soll zusätzlich die **Darstellung der Suchergebnisse** deutlich verbessert werden.

## Ziel

Die globale Suche soll nicht nur technisch funktionieren, sondern die Suchergebnisse sollen auch deutlich besser lesbar, schöner strukturiert und visuell informativer dargestellt werden.

Die aktuelle Darstellung gefällt in dieser Form nicht und ist für praktische Nutzung zu schlicht.

## Verbindliche Anforderungen an die Ergebnisdarstellung

### 1. Sender-Treffer / Live-TV-Treffer
Für Treffer aus dem Live-TV-/Sender-Bereich soll die Ergebnisliste deutlich aufgewertet werden.

Pflicht:
- **Senderlogo / Sender-Icon** gut sichtbar links oder prominent im Treffer anzeigen
- Sendername klar lesbar
- Wenn verfügbar: **aktuell laufende Sendung** zusätzlich direkt im Suchtreffer anzeigen
- Wenn verfügbar: kurzer Zusatz wie
  - „läuft jetzt“
  - Titel der aktuellen Sendung
  - optional Zeitspanne oder kurzer Now/Next-Auszug
- Ergebniszeile soll visuell klar als Sender-/Live-TV-Ergebnis erkennbar sein
- Layout soll nicht wie eine rohe Textliste wirken

Zielbild:
Ein Live-TV-Treffer soll auf den ersten Blick wie ein echter TV-Sender-Treffer aussehen und nicht nur wie ein Textnamen-Eintrag.

### 2. Film-Treffer
Für Filme sollen in der Suchergebnisliste sichtbare Medienkarten bzw. Listenzeilen mit Artwork dargestellt werden.

Pflicht:
- **Cover / Poster / sichtbares Artwork**
- Filmtitel prominent
- Wenn verfügbar: kurzer Zusatz wie Jahr / Kurzinfo / Kategorie
- Ergebnis muss sofort als Film erkennbar sein
- Kein reiner Texttreffer ohne visuelle Medieninformation, wenn Cover vorhanden ist

### 3. Serien-Treffer
Für Serien genauso:

Pflicht:
- **Cover / Poster / Serien-Artwork**
- Serientitel prominent
- Wenn verfügbar: kurze Zusatzinformation, z. B. Staffel-/Serienhinweis oder Kategorie
- Ergebnis muss auf den ersten Blick als Serien-Treffer erkennbar sein

### 4. Suchergebnisse insgesamt schöner strukturieren
Die globale Suche soll insgesamt visuell überarbeitet werden.

Pflicht:
- klarere Trefferdarstellung je Inhaltstyp
- bessere optische Trennung von
  - Live TV / Sender
  - Filme
  - Serien
- bessere Fokusdarstellung für IR-Fernbedienung
- Suchliste soll wie eine echte XCMate-Oberfläche wirken, nicht wie ein technischer Rohdialog
- vorhandene XCMate-Gestaltung / Branding beibehalten
- keine Verschlechterung der Bedienbarkeit auf Android TV und Titan BINGIE MOD

### 5. Performance / technische Grenzen
Wichtig:
- keine blockierenden Remote- oder HTTP-Aufrufe direkt beim D-Pad-Navigieren
- bereits lokal bekannte Logos / Cover / Poster bevorzugt verwenden
- EPG-Infos für Sender nur dort anzeigen, wo lokal/cached verfügbar
- kein UI-Freeze durch Nachladen
- fehlende Bilder dürfen nicht zum Absturz oder zu leeren kaputten Listen führen
- falls kein Bild vorhanden ist, sauberer Fallback verwenden

### 6. Fokus und Bedienung
Pflicht:
- Treffer müssen mit Fernbedienung sauber fokussierbar bleiben
- kein Fokusverlust durch Bilder oder nachträgliches Nachladen
- kein ungewollter Sprung auf andere Controls
- OK startet den erwarteten Treffer
- Back kehrt korrekt zurück

### 7. Bestandsschutz
Nicht verschlechtern:
- bestehende Film-/Seriendetails
- Live-TV-Start
- Autoplay
- vorhandene Originalgrafiken / Original-Icons
- Benutzerprofile, Portale, EPG-Daten
- laufende Arbeiten an Suchfunktion und EPG-Mapping nicht zerstören

## Technische Umsetzung – gewünschte Richtung

Bitte prüfen:
- wo die globale Suche aktuell ihr Ergebnisfenster rendert
- wie Trefferobjekte für Sender, Filme und Serien getrennt typisiert werden
- wie lokale Logos / Cover / Poster zuverlässig in die Suche eingespeist werden können
- ob für Sender ein kompakter „läuft jetzt“-Text aus dem lokalen EPG-/NowNext-Stand eingeblendet werden kann
- wie die Trefferliste als typisierte Medienliste statt als einfache Textliste aufgebaut werden kann

Wenn nötig:
- eigenes Such-Result-Layout / WindowXML / Container verbessern
- Suchtreffer-Typen explizit modellieren
- pro Treffer Bild + Primärtext + Sekundärtext unterstützen

## Akzeptanzkriterien

Die Änderung gilt erst dann als erfüllt, wenn folgende Punkte auf Android-TV plausibel nachgewiesen sind:

### SEARCHUI-01
Suche nach einem Sender:
- Senderlogo sichtbar
- Sendername sichtbar
- wenn möglich aktuell laufende Sendung sichtbar

### SEARCHUI-02
Suche nach einem Film:
- Cover/Poster sichtbar
- Filmtitel sichtbar
- Treffer klar als Film erkennbar

### SEARCHUI-03
Suche nach einer Serie:
- Cover/Poster sichtbar
- Serientitel sichtbar
- Treffer klar als Serie erkennbar

### SEARCHUI-04
Gemischte Trefferliste:
- Live-TV, Filme und Serien optisch sinnvoll getrennt oder klar erkennbar
- Fokus mit IR-Fernbedienung sauber

### SEARCHUI-05
Fehlende Bilder:
- sauberer Fallback statt kaputtem Layout

### SEARCHUI-06
Keine Regression:
- keine Verschlechterung der Suchbedienung
- kein zusätzlicher Freeze
- keine Fokusfehler
- kein Absturz

## Lieferumfang

Erwarte einen neuen Draft-PR auf kumulativer aktueller main-Basis mit:
- verbesserter globaler Suchdarstellung
- Test-ZIP
- SHA256
- kurzer Dokumentation
- Android-Teststrecke für SEARCHUI-01 bis SEARCHUI-06

Kein eigenmächtiger Merge.
Kein Release ohne ausdrückliche Freigabe.