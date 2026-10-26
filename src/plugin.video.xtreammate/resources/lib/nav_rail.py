"""Shared data-driven native rail; no provider/SQLite work or playback here."""
import os
from localization import tr
ENTRIES=(('search','search',35600,'global_search'),('favourites','heart',35601,'favourites'),
         ('live','device-tv',35602,'home_live'),('movies','movie',35603,'movies_home'),
         ('series','playlist',35604,'series_home'),('guide','calendar',35605,'guide_grid'),
         ('settings','settings',35606,'settings_home'),('home','home-2',35607,'xcmate_home'))


def entries(context='home'):
    values=list(ENTRIES)
    if context=='live':values[3:3]=[('groups','list',35608,'groups')];values.insert(-1,('startup','pin',35609,'startup_current'))
    else:values.insert(-1,('startup','pin',35615,'startup_settings'))
    return values


def icon(name,state='normal'):
    import xbmcaddon
    return os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','navigation',name+'-'+state+'.png')


class RailView:
    def __init__(self,owner,context,activate,restore):
        import xbmcgui
        self.owner=owner;self.context=context;self.activate=activate;self.restore=restore
        self.items=entries(context);self.active=False;self.expanded=False;self.position=next((i for i,e in enumerate(self.items) if e[0]==context),0)
        self.height=max(640,owner.getHeight());self.buttons=[];self.icons=[]
        root=os.path.dirname(os.path.dirname(icon('search')))
        self.panel=xbmcgui.ControlImage(24,24,84,self.height-48,os.path.join(root,'tv_panel.png'));owner.addControl(self.panel)
        step=(self.height-64)/len(self.items)
        for i,entry in enumerate(self.items):
            y=int(32+i*step);h=int(step)-4
            b=xbmcgui.ControlButton(30,y,72,h,'',focusTexture=os.path.join(root,'tv_focus.png'),noFocusTexture=os.path.join(root,'remote_clear.png'),font='font13',textOffsetX=62,textColor='0xFFBEC4CD',focusedColor='0xFFFFFFFF')
            image=xbmcgui.ControlImage(48,y+(h-32)//2,32,32,icon(entry[1]))
            owner.addControls([b,image]);b.setNavigation(b,b,b,b);self.buttons.append(b);self.icons.append(image)
        self.hide()

    def show(self,expanded=False,focus=True):
        self.active=True;self.expanded=expanded;self.panel.setWidth(332 if expanded else 84);self.panel.setVisible(True)
        for i,(b,image,entry) in enumerate(zip(self.buttons,self.icons,self.items)):
            b.setWidth(320 if expanded else 72);b.setLabel(tr(entry[2]) if expanded else '')
            b.setVisible(True);b.setEnabled(True);image.setVisible(True);image.setImage(icon(entry[1],'focused' if i==self.position else 'selected' if entry[0]==self.context else 'normal'))
        if focus:self.owner.setFocus(self.buttons[self.position])

    def hide(self):
        if self.active:
            try:
                if self.owner.getFocusId() in [b.getId() for b in self.buttons] and hasattr(self.owner,'capture'):
                    self.owner.setFocus(self.owner.capture)
            except (AttributeError,RuntimeError):pass
        self.active=False;self.expanded=False
        # Kodi can retain the expanded button label in a native render cache.
        # Clear content and focusability as well as visibility on every exit.
        for button in self.buttons:button.setLabel('');button.setWidth(72);button.setEnabled(False)
        for image in self.icons:image.setImage('')
        for c in [self.panel,*self.buttons,*self.icons]:c.setVisible(False)

    def command(self,command):
        if not self.active:return False
        if command in ('up','down'):
            self.position=(self.position+(-1 if command=='up' else 1))%len(self.items);self.show(self.expanded)
        elif command=='left':
            if self.expanded:self.hide();self.restore('full')
            else:self.show(True)
        elif command in ('right','back'):
            if self.expanded:self.show(False)
            else:self.hide();self.restore('previous')
        elif command=='ok':self.activate(self.items[self.position][3])
        else:return False
        return True

    def click(self,cid):
        if not self.active:return False
        for i,b in enumerate(self.buttons):
            if b.getId()==cid:self.position=i;self.command('ok');return True
        return False


def standalone(router,portal):
    import xbmcgui
    from window_navigation import ownership
    class RailDialog(xbmcgui.WindowDialog):
        def __init__(self):
            super().__init__();self.destination=None;self.finished=False
            self.rail=RailView(self,'home',self.choose,self.restore)
        def choose(self,action):self.destination=action;self.finished=True;self.close()
        def restore(self,where):self.finished=True;self.close()
        def onAction(self,action):
            command={1:'left',2:'right',3:'up',4:'down',9:'back',10:'back',92:'back'}.get(action.getId())
            if command:self.rail.command(command)
        def onControl(self,control):self.rail.click(control.getId())
    destination=None
    with ownership() as acquired:
        if not acquired:return
        import xbmc,time
        from window_lifecycle import state
        monitor=xbmc.Monitor();deadline=time.monotonic()+5
        while state()['modal'] or state()['updating']:
            if time.monotonic()>deadline or monitor.waitForAbort(.05):return
        window=RailDialog()
        try:
            import xbmc
            window.show();window.rail.show(False)
            monitor=xbmc.Monitor()
            while not window.finished:
                if monitor.waitForAbort(.05):break
            destination=window.destination
        finally:window.close()
    if destination:
        from navigation_dispatch import dispatch
        dispatch(destination,portal['id'])


def open_in_view(view,context):
    if getattr(view,'_closed',False) or getattr(view,'mode','')=='search':return False
    previous=view.getFocusId()
    def restore(where):
        view._navigation_rail.hide();view.setFocusId(previous)
    def activate(action):
        view._nav_destination=action;view._navigation_rail.hide();view.close()
    rail=getattr(view,'_navigation_rail',None)
    if rail is None:
        view._navigation_rail=rail=RailView(view,('movies' if view.kind=='vod' else 'series') if context=='media' else context,activate,restore)
    else:rail.restore=restore
    rail.show(False);return True


def view_action(view,key):
    rail=getattr(view,'_navigation_rail',None)
    if not rail or not rail.active:return False
    command={1:'left',2:'right',3:'up',4:'down',9:'back',10:'back',92:'back'}.get(key)
    if command:rail.command(command)
    return True  # Native OK is consumed once by onClick.
