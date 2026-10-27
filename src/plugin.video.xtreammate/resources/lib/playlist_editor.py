"""Native, paged editor for the persistent M3U working copy, never the source."""
import os
from urllib.parse import urlsplit
import xbmcgui
from localization import tr
from setup_window import WorkWindow


class PlaylistEditor(WorkWindow):
    def configure(self,portal):
        self.configure_work();self.portal=portal;self.query='';self.offset=0;self.rows=[]
        from m3u_store import path
        self.filename=path(portal['id'])
    def onInit(self):
        self._initialized=True
        self.getControl(2).setLabel(tr(32721))
        for ident,label in ((10,32722),(11,32723),(12,32724),(13,32725),(14,32726),(15,32747),(16,32756),(17,32757),(18,32710)):
            self.getControl(ident).setLabel(tr(label))
        self.load()
    def load(self):
        from m3u_store import entries
        def read(): return list(entries(self.filename,query=self.query,include_disabled=True,offset=self.offset,limit=100))
        self.work(read,self.ready)
    def ready(self,rows):
        self.rows=rows;self.getControl(100).reset()
        from menu_icons45 import decorate
        self.getControl(100).addItems([decorate(xbmcgui.ListItem(('☑ ' if r['enabled'] else '☐ ')+r['name']+' · '+r['group_name']),'list',full=True) for r in rows])
        self.status(0,tr(32754,self.offset+1,self.offset+len(rows),len(rows)));self.setFocusId(100)
    def change(self,operation):
        def job():
            operation()
            from source_sync import sync_kind
            for kind in ('live','vod','series'): sync_kind(self.portal,kind,force=True,local_only=True,cancel=self.cancel.is_set)
            from m3u_store import export_lines
            # Compatibility snapshot is ours; replace only this generated file.
            target=self.portal.get('m3u_url','')
            if target==self.filename+'.m3u':
                # Snapshot is optional. The normalized index/working SQLite are
                # authoritative. Streaming write avoids a full-playlist string.
                temporary=target+'.editor.tmp'
                try:
                    with open(temporary,'w',encoding='utf-8') as stream:
                        for line in export_lines(self.filename,include_disabled=True): stream.write(line)
                        stream.flush();os.fsync(stream.fileno())
                    os.replace(temporary,target)
                finally:
                    if os.path.exists(temporary): os.unlink(temporary)
            from m3u_store import entries
            return list(entries(self.filename,query=self.query,include_disabled=True,offset=self.offset,limit=100))
        self.work(job,self.ready)
    def choose_group(self):
        from m3u_store import categories
        groups=categories(self.filename)
        selected=__import__('menu_icons45').select(xbmcgui.Dialog(),tr(32728),[g['name']+' · '+g['kind'] for g in groups],default='list')
        return groups[selected] if 0<=selected<len(groups) else None
    def edit_row(self):
        from m3u_store import edit,reorder
        pos=self.getControl(100).getSelectedPosition()
        if not 0<=pos<len(self.rows): return
        row=self.rows[pos];dlg=xbmcgui.Dialog()
        choice=__import__('menu_icons45').select(dlg,tr(32746),[tr(n) for n in (32727,32728,32729,32730,32731,32732,32733,32734)],default='list')
        values={}
        if choice in (0,2,3):
            field={0:'name',2:'logo',3:'epg'}[choice];value=dlg.input(tr({0:32727,2:32729,3:32730}[choice]),defaultt=row[field]).strip()
            if value or field!='name': values[field]=value
        elif choice==1:
            group=self.choose_group()
            if group: values['gid']=group['gid']
        elif choice==4: values['enabled']=int(not row['enabled'])
        elif choice in (5,6): self.change(lambda:reorder(self.filename,row['sid'],-1 if choice==5 else 1));return
        elif choice==7 and dlg.yesno('XCMate',tr(32751)): values['deleted']=1
        if values: self.change(lambda:edit(self.filename,row['sid'],**values))
    def groups(self):
        from m3u_store import categories,group
        dlg=xbmcgui.Dialog();groups=categories(self.filename)
        choice=__import__('menu_icons45').select(dlg,tr(32723),[tr(32735)]+[g['name']+' · '+g['kind'] for g in groups],default='list')
        if choice<0: return
        selected=groups[choice-1] if choice else None
        name=dlg.input(tr(32738),defaultt=selected['name'] if selected else '').strip()
        if not name: return
        kind=__import__('menu_icons45').select(dlg,tr(32736),[tr(32701),tr(32702),tr(32703)],default='list')
        if kind<0: return
        self.change(lambda:group(self.filename,name,('live','vod','series')[kind],selected['gid'] if selected else None))
    def export(self):
        from m3u_store import export
        dlg=xbmcgui.Dialog();folder=dlg.browseSingle(0,tr(32739),'files')
        if not folder: return
        name=dlg.input(tr(32740),defaultt='XCMate.m3u8').strip()
        if not name or name!=os.path.basename(name) or any(c in name for c in ('/','\\','\x00')): return
        target=folder.rstrip('/\\')+'/'+name
        def canonical(uri):
            if not uri: return ''
            if '://' not in uri: return os.path.realpath(uri)
            from urllib.parse import urlunsplit
            from posixpath import normpath
            p=urlsplit(uri);return urlunsplit((p.scheme,p.netloc,normpath(p.path),p.query,p.fragment))
        if canonical(target) in {canonical(self.portal.get(k,'')) for k in ('m3u_original','m3u_origin','m3u_url')}:
            self.status(0,tr(32750));return
        import xbmcvfs
        overwrite=xbmcvfs.exists(target)
        if overwrite and not dlg.yesno('XCMate',tr(32741)): return
        self.work(lambda:export(self.filename,target,allow_overwrite=overwrite),lambda _:self.status(100,tr(32742)))
    def onClick(self,controlId):
        if controlId==18: self.close();return
        if self.busy: return
        try:
            if controlId==100: self.edit_row()
            elif controlId==10:
                self.query=xbmcgui.Dialog().input(tr(32722),defaultt=self.query)[:200];self.offset=0;self.load()
            elif controlId==11: self.groups()
            elif controlId==12:
                group=self.choose_group()
                if not group: self.status(0,tr(32749));return
                name=xbmcgui.Dialog().input(tr(32738)).strip();uri=xbmcgui.Dialog().input(tr(32737)).strip()
                if name and uri:
                    from m3u_store import add
                    self.change(lambda:add(self.filename,name,group['gid'],uri))
            elif controlId==13:
                from m3u_store import duplicates
                # URLs may contain credentials; show only names/counts.
                self.work(lambda:duplicates(self.filename),lambda rows:xbmcgui.Dialog().textviewer(tr(32725),tr(32776)+'\n'+'\n'.join(str(r['n'])+' × '+r['name'] for r in rows)))
            elif controlId==14: self.export()
            elif controlId in (16,17):
                self.offset=max(0,self.offset+(-100 if controlId==16 else 100));self.load()
        except (OSError,ValueError) as exc: self.status(0,tr(32743,type(exc).__name__))


def open_editor(portal):
    import xbmcaddon
    window=PlaylistEditor('XCMatePlaylistEditor.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
    window.configure(portal);window.run()
