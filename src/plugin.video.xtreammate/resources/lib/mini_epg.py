"""Always-visible local programme column for the highlighted mini-list SID."""
import datetime,time,textwrap
from localization import tr


def programme_rows(events,now=None):
    now=time.time() if now is None else now
    rows=[e for e in events if isinstance(e,dict) and e.get('title') and isinstance(e.get('start'),(int,float)) and isinstance(e.get('stop'),(int,float)) and e['stop']>e['start'] and e['stop']>now]
    rows=sorted(rows,key=lambda e:(e['start'],e['stop']))[:256]
    current=next((i for i,e in enumerate(rows) if e['start']<=now<e['stop']),None)
    if current is None:current=next((i for i,e in enumerate(rows) if e['start']>now),max(0,len(rows)-1))
    return rows,current


def time_label(event,now=None):
    today=datetime.datetime.fromtimestamp(time.time() if now is None else now).date()
    start=datetime.datetime.fromtimestamp(event['start']);stop=datetime.datetime.fromtimestamp(event['stop'])
    return start.strftime('%H:%M' if start.date()==today else '%d.%m. %H:%M')+'–'+stop.strftime('%H:%M' if stop.date()==start.date() else '%d.%m. %H:%M')


class MiniProgramme:
    def __init__(self,owner):
        import xbmcgui
        self.owner=owner;self.focused=False;self.sid='';self.selected=0;self.events=[];self.signature=None
        self._visible=False;self._native_count=0;self._painted={}
        w,h=owner._width,owner._height;x=int(w*.36);width=int(w*.32)
        self.heading=xbmcgui.ControlLabel(x,48,width,30,'','font13','0xFFF4F6F9')
        self.hint=xbmcgui.ControlLabel(x,86,width,28,tr(35610),'font12','0xFFBEC4CD')
        self.list=xbmcgui.ControlList(x,122,width,min(376,h-190),font='font12',textColor='0x00000000',selectedColor='0x00000000',buttonTexture=owner._media+'/remote_clear.png',buttonFocusTexture=owner._media+'/remote_clear.png',_itemHeight=66,_space=4)
        owner.addControls([self.heading,self.hint,self.list]);self.list.controlLeft(self.list);self.list.controlRight(self.list)
        self.rows=[]
        for row in range(5):
            y=122+row*70
            highlight=xbmcgui.ControlImage(x,y,width,66,owner._media+'/xcmate_focus_neon.png')
            stamp=xbmcgui.ControlLabel(x+8,y+2,width-16,20,'','font12','0xFFBEC4CD')
            title=xbmcgui.ControlTextBox(x+8,y+22,width-16,40,font='font12',textColor='0xFFF4F6F9')
            owner.addControls([highlight,stamp,title]);self.rows.append((highlight,stamp,title))
        self.column_width=width
        self.visible(False)

    def _set(self,control,method,value):
        key=(id(control),method)
        if key not in self._painted or self._painted[key]!=value:
            getattr(control,method)(value);self._painted[key]=value

    def visible(self,value):
        self._visible=bool(value)
        if value:
            # Prepare text/row visibility first. Never bulk-show the highlights.
            self._paint()
            for control in (self.heading,self.hint,self.list):self._set(control,'setVisible',True)
        else:
            self.focused=False
            for control in (self.heading,self.hint,self.list,*[c for row in self.rows for c in row]):
                self._set(control,'setVisible',False)
            self._set(self.heading,'setLabel','')
            for _,stamp,title in self.rows:
                self._set(stamp,'setLabel','');self._set(title,'setText','')

    def render(self):
        owner=self.owner;index=owner._highlight['channels']
        channel=owner.visible_channels[index] if 0<=index<len(owner.visible_channels) else None
        sid=str(channel.extra.get('stream_id','')) if channel else ''
        info=owner._guide.get(sid);events,current=programme_rows(info.get('programme_events',info.get('events',[])))
        identity=lambda event:(event['start'],event['stop'])
        signature=(sid,tuple(identity(e) for e in events))
        self._set(self.heading,'setLabel',channel.name if channel else tr(35611))
        self._set(self.hint,'setLabel',tr(35830) if self.focused else tr(35610))
        previous=identity(self.events[self.selected]) if self.focused and self.selected<len(self.events) else None
        changed=sid!=self.sid
        self.sid=sid;self.events=events
        if changed or not self.focused:self.selected=current
        else:
            self.selected=next((i for i,e in enumerate(events) if identity(e)==previous),min(self.selected,max(0,len(events)-1)))
        if signature!=self.signature:
            self.signature=signature
            # Native rows carry no text/identity. Equal-sized snapshots require
            # no reset at all, including title corrections and NOW rollover.
            count=max(1,len(events))
            if count!=self._native_count:
                self.list.reset();self.list.addItems(['']*count);self._native_count=count
        if self.list.getSelectedPosition()!=self.selected:self.list.selectItem(self.selected)
        self.visible(True)

    def _paint(self):
        if not self._visible:return
        now=time.time();first=self.selected//5*5
        current=next((i for i,e in enumerate(self.events) if e['start']<=now<e['stop']),None)
        desired=[]
        for slot,(highlight,stamp,title) in enumerate(self.rows):
            index=first+slot;event=self.events[index] if index<len(self.events) else None
            focused=bool(event and self.focused and index==self.selected)
            active=bool(event and index==current)
            label=(('● '+tr(35612)+'  ' if active else '')+time_label(event,now)) if event else ''
            label='[COLOR FF55DD99]'+label+'[/COLOR]' if active else label
            text=wrap_title(event['title'],self.column_width) if event else tr(35611) if not self.events and slot==0 else ''
            desired.append((highlight,stamp,title,focused,bool(event),label,text))
        # Disable every old/ineligible focus BEFORE showing the next focus.
        # This invariant holds after each individual Kodi setter, not just at
        # the end of a Python method (there is no atomic GUI batch API).
        for highlight,_,_,focused,_,_,_ in desired:
            if not focused:self._set(highlight,'setVisible',False)
        for highlight,stamp,title,focused,present,label,text in desired:
            self._set(stamp,'setLabel',label);self._set(title,'setText',text)
            self._set(stamp,'setVisible',present);self._set(title,'setVisible',bool(text))
            if focused:self._set(highlight,'setVisible',True)

    def focus(self):
        self.render()
        if not self.events:return
        self.focused=True;self.selected=programme_rows(self.events)[1];self.list.selectItem(self.selected);self.owner.setFocus(self.list)
        self._set(self.hint,'setLabel',tr(35830));self._paint()

    def command(self,command,native=False):
        if not self.focused:return False
        if command in ('left','back'):
            self.focused=False;self.owner.setFocus(self.owner.control)
            self._set(self.hint,'setLabel',tr(35610))
        elif command in ('up','down'):
            pos=self.list.getSelectedPosition()
            target=pos if native and pos!=self.selected else self.selected+(-1 if command=='up' else 1)
            self.selected=min(max(0,target),max(0,len(self.events)-1))
            if self.list.getSelectedPosition()!=self.selected:self.list.selectItem(self.selected)
        elif command=='ok':
            if self.events:
                import xbmcgui
                event=self.events[self.selected]
                from programme_window46 import request
                request(self.owner,self.owner.index.by_sid.get(self.sid),event)
        elif command=='right':pass
        else:return False
        self._paint()
        return True


def wrap_title(title,width):
    """At most two explicit lines in a bounded native TextBox (no scrolling)."""
    value=' '.join(str(title or '').split())[:1024]
    return '\n'.join(textwrap.wrap(value,width=max(16,int((width-16)/8)),max_lines=2,placeholder='…'))
