# Superpowers-Entwicklungsworkflow

Verbindlich ist der Nutzerauftrag vom 17.11.2026: Issues und Projektdokumente → Ursachenanalyse/RED-Test → kleiner Entwicklungsbranch → GREEN/Regression → unabhängiger Review → Verifikation → Draft-PR. Kein automatischer Merge oder Release, keine Secrets oder Android-Scheinabnahme.

## Bestand und Entscheidungen

Main `ec5755e2` enthält .92-Quellen, aber veröffentlicht Pilot-.96 aus dem unge­mergten Source-PR #471. Ein Agent darf daraus keinen Downgrade ableiten. Vor Produktarbeit Versionen, Source-/ZIP-SHA und offene PRs vergleichen; ein explizit dokumentierter gestapelter Source-PR ist zulässig. PR #472/#470 enthalten bereits read-only Entwürfe; deren Branch bleibt unverändert. Neue Struktur separat auf main.

Möglichkeiten: (1) sofortiger API-Runner, braucht Schlüssel/Budget und wirksamen Branch-/Environment-Schutz; derzeit ungeeignet. (2) ungeprüftes @codex-Botkommando, unbestätigter Integrationsvertrag; ungeeignet. (3) freigegebener, schreibgeschützter Auftragsumschlag plus nachvollziehbarer Codex-Ausführung und PR-CI; gewählt als sichere erste Stufe. Dies ist eine Implementierungsentscheidung im ausdrücklich selbstständigen Arbeitsauftrag, keine behauptete separate Produkt-/Releasefreigabe.

## Auftragseingang

Nur offenes Issue im exakten Repository. Ausschließlich Repository-Eigentümer als menschlicher Auslöser; Label `codex:approved` muss im frischen API-Read noch vorhanden sein. Issue und Ereignis-ID müssen übereinstimmen. Kein PR, Bot, Fremdrepo oder frei ausführbarer Text. Bei Änderung seit Labelereignis: BLOCKED, neu freigeben. Ausgabe enthält nur feste Referenzen, Issue-Body-SHA und Entwicklungsbranch, keine Titel/Body/Logs/Zugangsdaten. Label ist keine Merge-/Release-/API-Freigabe.

`issues:labeled` und manueller Dispatch erstellen ausschließlich einen Auftragsumschlag als CI-Artefakt. Erst nach späterem Merge kann das neue Issue-Ereignis auf main aktiv sein; diese Sitzung mergen wir nicht. Kein automatischer kostenpflichtiger Agentenstart. Ein späterer Runner benötigt gesonderte technische Aktivierung, explizites Budget, vertrauenswürdige Skillsinstallation, getrennte read-only-Ausführung und eingeschränkten Publisher sowie unabhängige Reviewgates.

## Prüfung und Review

Read-only PR-CI führt tatsächliche Tooltests und einen Diff-Schutz aus. Veröffentlichungsdateien, Profile, Backups und geheimnistragende Dateien bleiben gesperrt. Regeln sind zusätzliche Kontrollen, kein Ersatz für GitHub-Rulesets/Environments. Vorhandene Publisher werden nicht unbemerkt umgebaut. Fachlicher LLM-Review erfolgt in dieser ersten Runde durch einen unabhängigen lesenden Codex-Subagenten; die CI-Policyprüfung wird nicht als solcher ausgegeben.

## Erste Produktaufgabe

Issue #474 separat: tatsächliche Quelle+Kanal+Sender-Bindung, Preview ohne Schreiben, Save mit unabhängigem Readback und sichtbarem Ergebnis, Fehler mit erhaltener Ansicht/Zuordnung. Das konkrete Android-Ereignis ist ohne zeitlich passendes Log nicht bewiesen. Nachfolgende Settings-/Timeout-Themen zunächst getrennt diagnostizieren und als eigene Aufgaben dokumentieren.
