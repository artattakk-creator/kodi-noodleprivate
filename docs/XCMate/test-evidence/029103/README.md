# XCMate 0.1.29.103 · Native Nachweise zu #517

## BINGIE 2.2.3 unter Linux-Kodi 21.2

Die kontrollierten Widget-Quellen liefen im nativen Renderer. Pro Auflösung wurden 18 Fokuszustände über die sechs geforderten und drei persönlichen Reihen gemessen. Geprüft wurden beide Fokuslinien, horizontale und vertikale Navigation, die feste Senderleiste und die Wiedergabe eines kontrollierten Audiostreams. Der 4K-Lauf enthält den nativen Rücksprung aus dem Seitenmenü zum vorher gewählten Sender.

- [Live-TV](bingie-1080-live.png), [Filme](bingie-1080-vod.png), [Serien](bingie-1080-series.png)
- [Kino](bingie-1080-cinema.png), [Trend](bingie-1080-trend.png), [MP3](bingie-1080-mp3.png)
- [720p-Messung](bingie-720.json), [1080p-Messung](bingie-1080.json), [2160p-Messung](bingie-2160.json), [Home-Scheduler bei 2160p](bingie-2160-schedule.json)

## Zuordnung und Agent-Einstellungen

Kodi öffnete die Agent-Quelle. Die vorbefüllte Suche „DE| KiKA AVC“ fand die erwartete XMLTV-ID. Fernbedienungstasten öffneten Vorschau und Save. Die quellgebundene Auswahl und der sichtbare Programmeintrag wurden nach einem Prozessneustart erneut geprüft. Der native Zuordnungslauf verwendete den ZIP-Hash `20efa5c7a80e0db2f2e99116ac51304e472831fac4dd26e3a5392bd0641e4e0c`.

- [Agent in der Quellliste](mapping-720-source.png), [Save-Fokus und Vorschau](mapping-1080-save.png), [Kalt-Readback](mapping-1080-restart.json)
- [Agent-Seite nach Auswahl von ALL](agent-settings-720.png)

## Sendungsdetail und Hero-Installation

Für „Ghosts“ wurden die echten öffentlichen Ereignisfakten und kontrollierte Bildbytes im nativen Detailpfad geprüft. Der sichtbare Header, die getrennte Posterfläche und die weiteren Details wurden tokenfrei dargestellt. Der separate Patchdialog prüfte Abbruch, ausdrückliche Installation und unveränderte gespeicherte Widget-Bindungen.

- [Ghosts mit weiterer Detailseite](ghosts-720.png), [Rendererbeleg und ZIP-Hash](ghosts-720.json)
- [Hero-Zustimmung](hero-720-approval.png), [Prüfsummenanzeige](hero-720-checksums.png)

Physische Android- und LG-Abnahme · `NOT_TESTED`. Die Linux-Fixtures belegen weder CDN-Auslieferung echter Bildbytes noch Wiedergabe auf dem Zielgerät.
