# Kodi21-Streamfelder in .39

Quelle ist ausschließlich die aktuelle per InfoTag/Nonce bestätigte eigene VideoPlayer-Session. `stream_details.Details` verwirft alte Sessionwerte sofort und liest höchstens alle zwei Sekunden während sichtbarer Info/Details. Kein Provider-HTTP, kein JSON-RPC-Polling und kein Auslesen fremder Player.

| Feld | Kodi21-Kandidat | Verhalten ohne Wert |
|---|---|---|
| Pixelbreite/-höhe | `Player.Process(VideoWidth/VideoHeight)` | unbekannt, keine HD/4K-Schätzung |
| Scanart | `Player.Process(VideoScanType)` | kein p/i ergänzen |
| Bildrate | `Player.Process(VideoFPS)` | unbekannt; NaN/ungültige Werte verwerfen |
| Seitenverhältnis | `Player.Process(VideoDAR)` | unbekannt |
| Videocodec | `VideoPlayer.VideoCodec` | unbekannt |
| Decoder/Pixelformat | `Player.Process(VideoDecoder/PixFormat)` | unbekannt |
| HDR | `VideoPlayer.HdrType` | unbekannt, nicht automatisch SDR |
| Audiocodec/-kanäle/-sprache | `VideoPlayer.AudioCodec/AudioChannels/AudioLanguage` | unbekannt; 6 Kanäle nicht als gesicherte AVR-5.1-Ausgabe ausgeben |
| Abtastrate | `Player.Process(AudioSamplerate)` | unbekannt |
| Untertitel | `VideoPlayer.SubtitlesLanguage`, `VideoPlayer.SubtitlesEnabled` | fehlende Sprache unbekannt; nativen Aktivzustand getrennt lesen |

Dies sind Kodi21-Kandidaten, keine Garantie, dass jeder Decoder/Stream/BINGIE-Build sie liefert. Reale Verfügbarkeit auf Kodi21.3 ARM32: **NOT_TESTED**. Keine v22-Felder `VideoLiveBitrate`, `AudioLiveBitrate` oder `AudioName`; keine nominale Bitrate als gemessene Netzbandbreite ausgeben.

Referenzen: [Kodi InfoLabels](https://kodi.wiki/view/InfoLabel), [Omega WindowIDs.h](https://github.com/xbmc/xbmc/blob/Omega/xbmc/guilib/WindowIDs.h). Standard-VideoOSD 12901 wird nur für eigene bestätigte Sessions freigegeben; andere Modaldialoge bleiben erhalten.
