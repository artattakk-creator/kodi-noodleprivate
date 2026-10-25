"""Normalize only the explicitly reviewed .35 guide/focus hooks for old freezes."""

def without_guide35(source):
    binary=isinstance(source,bytes)
    if binary:source=source.decode()
    replacements=(
        ("if selected_stream else __import__('tv_focus').target(portal,self.index,self.enabled)[0])",
         "if selected_stream else str(portal.get('start_group_id') or '*'))"),
        ("if self._closed or getattr(self,'_exiting',False) or getattr(self,'_guide_handoff',False):",
         "if self._closed or getattr(self,'_exiting',False):"),
        ("        if self.category_id!='*' and self.category_id not in self.enabled:\n            self.category_id=__import__('tv_focus').target(self.portal,self.index,self.enabled)[0]",
         "        if self.category_id!='*' and self.category_id not in self.enabled: self.category_id='*'"),
        ("            if index == 3:\n                from live_guide_navigation import request\n                request(self)\n                return",
         "            if index == 3:\n                self._epg()\n                return"),
        ("                if self.mode in ('hidden','info'):self._focus_playing_channel()\n",''),
        ('''    def suspend_for_guide(self):
        """Service-only close: preserve the immutable running live session."""
        if self._closed:return
        self._closed=True
        if hasattr(self,'_guide'):self._guide.close()
        self._intro_deadline=None
        xbmcgui.Window(10000).clearProperty('XtreamMate.RemoteCommand')
        super().close()

''',''),
        ('''    def _focus_playing_channel(self):
        from tv_focus import target
        from playback_exit import identity
        try:owned=identity(xbmc.Player())
        except (AttributeError,RuntimeError):owned=None
        sid=owned[1]['sid'] if owned and owned[0]=='live' and owned[1]['pid']==str(self.portal['id']) else ''
        self.category_id,position,found=target(self.portal,self.index,self.enabled,sid)
        self._highlight['channels']=position;self._scroll_to_current=False;self._list_key=None
        trace('focus','CURRENT_CHANNEL',count=position,focused=found)

''',''))
    for added,original in replacements:
        assert source.count(added)==1,added
        source=source.replace(added,original)
    return source.encode() if binary else source
