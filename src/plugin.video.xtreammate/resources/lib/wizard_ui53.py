"""Keep .51 native worker/rendering; add resumable navigation around its steps."""
import functools


def resumable(cls):
    original={name:getattr(cls,name) for name in ('configure','work','working','render','discovered','scanned','failed_work','onClick','onAction')}
    def session(w):return getattr(w.draft,'resume53',None)
    def checkpoint(w,categories=False):
        s=session(w)
        if s:
            ok=s.checkpoint(w.draft,w.stage,categories=categories)
            if not ok and w._initialized and not w._closed:
                w.getControl(18).setLabel('Später (nur Arbeitsspeicher)')
                w.getControl(3).setText('Zwischenstand konnte nicht sicher gespeichert werden. Eingaben bleiben bis zum Schließen im Arbeitsspeicher. Schreibrechte prüfen.')
            return ok
    @functools.wraps(original['configure'])
    def configure(w,draft):
        original['configure'](w,draft);s=session(w)
        w._resume_target53=s.state.get('stage','groups') if s else 'groups'
        if s and getattr(s,'authenticated53',False) and any(draft.categories.values()):
            w.stage='summary' if draft.scanned and w._resume_target53=='summary' else 'groups'
    @functools.wraps(original['work'])
    def work(w,job,apply):
        s=session(w)
        if not s:return super(cls,w).work(job,apply)
        checkpoint(w);draft=w.draft;stage=w.stage
        def guarded():
            succeeded=False
            try:
                value=job();succeeded=True;return value
            finally:s.checkpoint(draft,stage,categories=stage=='discover' and succeeded)
        return super(cls,w).work(guarded,apply)
    @functools.wraps(original['working'])
    def working(w):
        original['working'](w)
        w.getControl(19).setVisible(False)
    @functools.wraps(original['render'])
    def render(w):
        original['render'](w)
        if not session(w):w.getControl(19).setVisible(False)
        if session(w):
            w.getControl(18).setLabel('Einrichtung später fortsetzen');w.getControl(19).setVisible(not w.busy)
            w.getControl(19).setLabel('Entwurf verwerfen')
    @functools.wraps(original['discovered'])
    def discovered(w,result):
        s=session(w)
        if s:
            s.authenticated53=True
            for kind in ('live','vod','series'):
                allowed={str(g['category_id']) for g in w.draft.categories[kind]}
                if w.draft.selected[kind]-allowed:w.draft.scanned=False
                w.draft.selected[kind].intersection_update(allowed)
            if w.draft.scanned and w._resume_target53=='summary':w.stage='summary';w.render();checkpoint(w);return
        original['discovered'](w,result);checkpoint(w)
    @functools.wraps(original['scanned'])
    def scanned(w,result):original['scanned'](w,result);checkpoint(w)
    @functools.wraps(original['failed_work'])
    def failed(w,exc):
        original['failed_work'](w,exc)
        if session(w):
            w.getControl(16).setVisible(True);w.getControl(16).setLabel('Zurück')
            w.getControl(18).setVisible(True);w.getControl(18).setLabel('Einrichtung später fortsetzen')
            w.getControl(19).setVisible(True);w.getControl(19).setLabel('Entwurf verwerfen')
            w.getControl(17).setLabel('Erneut versuchen');checkpoint(w)
    @functools.wraps(original['onClick'])
    def click(w,cid):
        s=session(w)
        if s:
            if cid==19 and not w.busy:
                import xbmcgui
                if xbmcgui.Dialog().yesno('XCMate','Nur diesen Einrichtungsentwurf verwerfen? Bestehende Portale bleiben erhalten.',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0)):
                    s.discard(confirmed=True);s.action='discard';w.close()
                return
            if cid==16 and not w.busy and w.stage in ('groups','failed'):
                checkpoint(w);s.action='back';w.close();return
            if cid==18:checkpoint(w);s.action='later'
            if cid==17 and not w.busy and w.stage=='groups' and w.draft.scanned and w.draft._scan_signature==w.draft._signature():
                w.scanned(w.draft.report);return
        original['onClick'](w,cid)
        if s and not w.busy and not w._closed:checkpoint(w)
    @functools.wraps(original['onAction'])
    def action(w,event):
        if session(w) and event.getId() in (9,10,92):
            if w.busy:w.onClick(18)
            elif w.stage=='summary':w.onClick(16)
            else:w.onClick(16)
            return
        return original['onAction'](w,event)
    for name,method in [('configure',configure),('work',work),('working',working),('render',render),('discovered',discovered),('scanned',scanned),('failed_work',failed),('onClick',click),('onAction',action)]:setattr(cls,name,method)
    return cls
