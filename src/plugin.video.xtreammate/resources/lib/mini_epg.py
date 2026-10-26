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

    def visible(self,value):
        for c in (self.heading,self.hint,self.list,*[c for row in self.rows for c in row]):c.setVisible(value)
        if not value:
            self.focused=False
            for _,stamp,title in self.rows:stamp.setLabel('');title.setText('')

    def render(self):
        owner=self.owner;index=owner._highlight['channels']
        channel=owner.visible_channels[index] if 0<=index<len(owner.visible_channels) else None
        sid=str(channel.extra.get('stream_id','')) if channel else ''
        info=owner._guide.get(sid);events,current=programme_rows(info.get('programme_events',info.get('events',[])))
        signature=(sid,tuple((e['start'],e['stop'],e['title']) for e in events),current)
        self.heading.setLabel(channel.name if channel else tr(35611))
        self.hint.setLabel(tr(35830) if self.focused else tr(35610))
        if signature!=self.signature:
            previous=self.events[self.selected] if self.focused and self.selected<len(self.events) else None
            changed=sid!=self.sid;self.sid=sid;self.events=events;self.signature=signature
            self.list.reset()
            # Visible native control owns keys/scroll/OK, but NEVER a text layer.
            self.list.addItems(['']*len(events) or [''])
            self.selected=current if changed or not self.focused else min(self.selected,max(0,len(events)-1));
            if previous and not changed and self.focused:
                self.selected=next((i for i,e in enumerate(events) if (e['start'],e['stop'],e['title'])==(previous['start'],previous['stop'],previous['title'])),self.selected)
            self.list.selectItem(self.selected)
        self.visible(True);self._paint()

    def _paint(self):
        now=time.time();first=self.selected//5*5
        for slot,(highlight,stamp,title) in enumerate(self.rows):
            index=first+slot;event=self.events[index] if index<len(self.events) else None
            highlight.setVisible(bool(event and self.focused and index==self.selected))
            stamp.setVisible(bool(event));title.setVisible(bool(event))
            if event:
                active=event['start']<=now<event['stop']
                label=('● '+tr(35612)+'  ' if active else '')+time_label(event,now)
                stamp.setLabel('[COLOR FF55DD99]'+label+'[/COLOR]' if active else label)
                title.setText(wrap_title(event['title'],self.column_width))
            else:
                stamp.setLabel('');title.setText(tr(35611) if not self.events and slot==0 else '')
                if not self.events and slot==0:title.setVisible(True)

    def focus(self):
        self.render()
        if not self.events:return
        self.focused=True;self.selected=programme_rows(self.events)[1];self.list.selectItem(self.selected);self.owner.setFocus(self.list)
        self.hint.setLabel(tr(35830));self._paint()

    def command(self,command,native=False):
        if not self.focused:return False
        if command in ('left','back'):
            self.focused=False;self.owner.setFocus(self.owner.control)
            self.hint.setLabel(tr(35610))
        elif command in ('up','down'):
            pos=self.list.getSelectedPosition()
            target=pos if native and pos!=self.selected else self.selected+(-1 if command=='up' else 1)
            self.selected=min(max(0,target),max(0,len(self.events)-1));self.list.selectItem(self.selected)
        elif command=='ok':
            if self.events:
                import xbmcgui
                event=self.events[self.selected];xbmcgui.Dialog().textviewer(event['title'],event.get('description') or tr(35613))
        elif command=='right':pass
        else:return False
        self._paint()
        return True


def wrap_title(title,width):
    """At most two explicit lines in a bounded native TextBox (no scrolling)."""
    value=' '.join(str(title or '').split())[:1024]
    return '\n'.join(textwrap.wrap(value,width=max(16,int((width-16)/8)),max_lines=2,placeholder='…'))
