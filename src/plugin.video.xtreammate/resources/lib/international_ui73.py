"""Country/alternative picker; network verification on the existing worker UI."""
from localization import tr

CONTINENTS=('Europe','Asia','Africa','North America','South America','Oceania')


def show(portal):
    import xbmcaddon,xbmcgui
    from menu_icons45 import select
    from international_epg73 import countries,verify,activate,registry
    from setup_window import WorkWindow
    while True:
        continent=select(xbmcgui.Dialog(),tr(38030),[tr(38040+i) for i in range(6)],default='globe')
        if not 0<=continent<6:return
        rows=countries(CONTINENTS[continent])
        choice=select(xbmcgui.Dialog(),tr(38030),[r['label']+' ['+r['code']+'] · '+tr(38031 if r['candidate'] else 38032) for r in rows],default='globe')
        if not 0<=choice<len(rows):continue
        country=rows[choice];sources=country['sources']
        if not sources:xbmcgui.Dialog().ok('XCMate',tr(38032));continue
        choice=select(xbmcgui.Dialog(),country['label'],[s['provider']+' · '+('GZIP' if s['url'].endswith('.gz') else 'XMLTV') for s in sources],default='list')
        if not 0<=choice<len(sources):continue
        source=dict(sources[choice]);terms=registry()['provider_policy'][source['provider']]
        if 'unchecked' in source.get('verification',''):
            xbmcgui.Dialog().ok('XCMate',tr(38033,'EPG_ENDPOINT_PENDING'));continue
        if not terms['personal_player_use']:
            xbmcgui.Dialog().ok('XCMate',tr(38033,'EPG_TERMS_PENDING'));continue
        class Probe(WorkWindow):
            def onInit(self):
                if self._initialized:return
                self._initialized=True
                for cid in (5,6,10,11,12,13,14,15,19,21,100,101,102,16,17):self.getControl(cid).setVisible(False)
                self.getControl(18).setVisible(True);self.getControl(18).setLabel(tr(38013));self.setFocusId(18)
                self.getControl(2).setLabel(tr(38034,country['label']))
                cancelled=self.cancel.is_set
                self.work(lambda:verify(source,cancelled),self.verified)
            def verified(self,proof):
                self.status(None,tr(38035,proof['channels'],proof['programmes']))
                if xbmcgui.Dialog().yesno(tr(38030),tr(38036,proof['channels'],proof['programmes'])):
                    self.work(lambda:activate(portal,country,source,confirmed=True),self.activated)
                else:self.close()
            def activated(self,requested):
                xbmcgui.Dialog().ok('XCMate',tr(38037 if requested else 38038));self.close()
            def failed_work(self,exc):
                from vodsync_api72 import failure
                self.status(None,tr(38033,failure(exc).code))
            def onClick(self,cid):
                if cid==18:self.close()
        w=Probe('XCMateSetup.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
        w.configure_work();w.run()
