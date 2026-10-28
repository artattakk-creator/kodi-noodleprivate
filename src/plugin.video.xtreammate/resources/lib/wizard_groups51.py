"""Owner-pumped, lazy group rows; no network or add-on queries per click."""
import time
import os
import xbmcgui

KINDS=('live','vod','series')
BATCH=32
SLICE=.008


class GroupRows:
    def configure_rows(self):
        import xbmcaddon
        from localization import tr
        root=xbmcaddon.Addon().getAddonInfo('path')
        self._row_labels={key:tr(key) for key in (32712,32780,36503,36504)}
        self._state_icons={value:os.path.join(root,'resources','media',
            'setup_checked.png' if value else 'setup_unchecked.png') for value in (False,True)}
        self._rendered={kind:None for kind in KINDS}
        self._bulk={};self._groups_loaded=True;self._focus_trace=0

    def _mark51(self,stage,**fields):
        from setup_trace import mark
        mark(stage,getattr(self.draft,'pid',''),**fields)

    def _item_state(self,item,selected):
        item.setProperty('setup_selected','true' if selected else 'false')
        item.setArt({'icon':self._state_icons[bool(selected)]})

    def _groups(self):
        self._gui()
        if not self._groups_loaded:
            self._rendered={kind:None for kind in KINDS};self._bulk={}
            self._groups_loaded=True
        self._render_slice()

    def _render_slice(self):
        kind=self.kind;number=KINDS.index(kind);control=self.getControl(100+number)
        if self._rendered[kind] is None:
            control.reset();self._rendered[kind]=0
            self._mark51('GROUPS_RENDER_BEGIN',kind=kind,total=len(self._entries))
        start=self._rendered[kind];pos=start;items=[];deadline=time.monotonic()+SLICE
        while pos<len(self._entries) and len(items)<BATCH:
            group=self._entries[pos]
            item=xbmcgui.ListItem(str(group['category_name']))
            self._item_state(item,str(group['category_id']) in self.draft.selected[kind])
            items.append(item);pos+=1
            if time.monotonic()>=deadline:break
        if items:control.addItems(items)
        self._rendered[kind]=pos
        if (pos>start or start==0) and pos==len(self._entries):
            self._mark51('GROUPS_RENDER_END',kind=kind,total=pos)
        self._render_status()

    def _render_status(self):
        pos=self._rendered[self.kind] or 0;total=len(self._entries)
        if pos<total:
            self.status(100*pos/max(1,total),self._row_labels[36503].format(pos,total))
        elif self.kind in self._bulk:
            self.status(100*self._bulk[self.kind]/max(1,pos),self._row_labels[36504])
        else:
            self.status(100,self._row_labels[32712])

    def pump(self):
        super().pump()
        if self._closed or not self._initialized or self.busy or self.stage!='groups':return
        if self._rendered[self.kind] is None or self._rendered[self.kind]<len(self._entries):
            self._render_slice()
        if self.kind in self._bulk:
            kind=self.kind;pos=self._bulk[kind]
            end=min(pos+BATCH,self._rendered[kind] or 0)
            control=self.getControl(100+KINDS.index(kind));selected=self.draft.selected[kind]
            deadline=time.monotonic()+SLICE
            while pos<end:
                group=self.draft.categories[kind][pos]
                self._item_state(control.getListItem(pos),str(group['category_id']) in selected)
                pos+=1
                if time.monotonic()>=deadline:break
            if pos<(self._rendered[kind] or 0):self._bulk[kind]=pos
            else:self._bulk.pop(kind,None)
            self._render_status()

    def bulk_selection(self,select):
        self.draft.selected[self.kind]={str(g['category_id']) for g in self._entries} if select else set()
        self.draft.scanned=False;self._bulk[self.kind]=0
        self._mark51('GROUP_TOGGLE',kind=self.kind,total=len(self.draft.selected[self.kind]))
        self._selection_status()

    def onFocus(self,controlId):
        # Trace only focus/control category, never provider group names/IDs.
        now=time.monotonic()
        if controlId in (100,101,102) and now-self._focus_trace>=.25:
            self._focus_trace=now;self._mark51('GROUP_FOCUS',kind=KINDS[controlId-100])
