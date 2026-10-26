"""Always-visible local programme column for the highlighted mini-list SID."""
import datetime,time
from localization import tr


def programme_rows(events,now=None):
    now=time.time() if now is None else now
    rows=[e for e in events if isinstance(e,dict) and e.get('title') and isinstance(e.get('start'),(int,float)) and isinstance(e.get('stop'),(int,float)) and e['stop']>e['start']]
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
        w,h=owner._width,owner._height;x=int(w*.43);width=w-x-48
        self.heading=xbmcgui.ControlLabel(x,42,width,38,'','font16','0xFFF4F6F9')
        self.hint=xbmcgui.ControlLabel(x,86,width,30,tr(35610),'font12','0xFFBEC4CD')
        self.list=xbmcgui.ControlList(x,126,width,h-210,font='font13',textColor='0xFFF4F6F9',selectedColor='0xFFFFFFFF',buttonTexture=owner._media+'/tv_normal.png',buttonFocusTexture=owner._media+'/tv_focus.png',_itemHeight=58,_space=8)
        owner.addControls([self.heading,self.hint,self.list]);self.list.controlLeft(self.list);self.list.controlRight(self.list)
        self.visible(False)

    def visible(self,value):
        for c in (self.heading,self.hint,self.list):c.setVisible(value)
        if not value:self.focused=False

    def render(self):
        owner=self.owner;index=owner._highlight['channels']
        channel=owner.visible_channels[index] if 0<=index<len(owner.visible_channels) else None
        sid=str(channel.extra.get('stream_id','')) if channel else ''
        info=owner._guide.get(sid);events,current=programme_rows(info.get('programme_events',info.get('events',[])))
        signature=(sid,tuple((e['start'],e['stop'],e['title']) for e in events),current)
        self.heading.setLabel(channel.name if channel else tr(35611))
        if signature!=self.signature:
            changed=sid!=self.sid;self.sid=sid;self.events=events;self.signature=signature
            self.list.reset();labels=[];now=time.time()
            for e in events:
                label=('[B]'+tr(35612)+'[/B]  ' if e['start']<=now<e['stop'] else '')+time_label(e,now)+'  '+e['title']
                labels.append(label)
            self.list.addItems(labels or [tr(35611)])
            self.selected=current if changed or not self.focused else min(self.selected,max(0,len(events)-1));self.list.selectItem(self.selected)
        self.visible(True)

    def focus(self):
        self.render()
        if not self.events:return
        self.focused=True;self.selected=programme_rows(self.events)[1];self.list.selectItem(self.selected);self.owner.setFocus(self.list)

    def command(self,command,native=False):
        if not self.focused:return False
        if command in ('left','back'):
            self.focused=False;self.owner.setFocus(self.owner.control)
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
        return True
