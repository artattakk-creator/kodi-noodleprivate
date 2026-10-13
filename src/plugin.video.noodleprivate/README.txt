Noodle Private 0.4.1
====================
Kodi 19+ video plugin for adult users. The installed Cumination add-on is
required for EPorner, xHamster, Pornhub, XNXX, SpankBang and Tnaflix.
NoodleMagazine remains a separate direct site adapter.

GRAPHICS / VISUAL UPDATE 0.4.1
- Kodi metadata icon: resources/icon.png (600x600)
- Kodi background fanart: resources/fanart.png (1920x1080)
- The home menu uses original category images in resources/media/*.png.
- Cinematic dark-magenta GS Media design; portrait is an original illustration
  of an adult woman in a jacket. No third-party photographs or licensed assets.
- Visual-only update; preferences, collections and watched history are preserved.

HOW TO USE
- Choose 'Anbieteruebergreifende Suche' to search the active providers.
- Browse individual sources under 'Videoanbieter'.
- Enable or disable each provider via 'Filter, Qualitaet & Anbieter'.
- On a video, open the context menu -> 'Zu Favoritenliste hinzufuegen'.
- Create and rename as many named favorites lists as needed.
- All favorites, searches, history and settings remain local on the Kodi device.

BINGIE MOD / DIRECT WIDGET URLS
- All source folders: plugin://plugin.video.noodleprivate/?action=providers
- EPorner: plugin://plugin.video.noodleprivate/?action=provider_browse&provider=eporner
- xHamster: plugin://plugin.video.noodleprivate/?action=provider_browse&provider=xhamster
- Pornhub: plugin://plugin.video.noodleprivate/?action=provider_browse&provider=pornhub
- XNXX: plugin://plugin.video.noodleprivate/?action=provider_browse&provider=xnxx
- SpankBang: plugin://plugin.video.noodleprivate/?action=provider_browse&provider=spankbang
- Tnaflix: plugin://plugin.video.noodleprivate/?action=provider_browse&provider=tnaflix
- Named collection: plugin://plugin.video.noodleprivate/?action=collection_view&collection_id=default
- All collections: plugin://plugin.video.noodleprivate/?action=favorites
- Search prompt: plugin://plugin.video.noodleprivate/?action=global_search_prompt
- Fixed search term: plugin://plugin.video.noodleprivate/?action=global_search&query=example

PROVIDER LIMITATIONS
Kodi JSON-RPC Files.GetDirectory must be able to enumerate the corresponding
Cumination plugin directory. Some source sites may fail or time out; failing
sources do not delete other search results or local favorites. Kodi navigates
external provider video links through the original Cumination plugin. Noodle
Private does not copy or bypass Cumination resolvers.

UPGRADE FROM 0.2.0
Install from the same GS Media Kodi repository. Keep the existing add-on ID
plugin.video.noodleprivate, and do not uninstall/clear the add-on profile.
The files state.json and preferences.json are left unchanged by this update.
