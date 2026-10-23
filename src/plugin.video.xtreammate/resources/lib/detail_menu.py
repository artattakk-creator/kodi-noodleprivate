"""Left-side native detail menu; keep media/player actions in their old path."""
import xbmc,xbmcgui
from localization import tr


def mark(event,reason='',ready=False,waiting=False):
    events=('DETAIL_LEFT_RECEIVED','DETAIL_ACTIONS_BUTTON','DETAIL_MENU_ELIGIBILITY',
            'MENU_VISIBLE','FOCUS_810','MENU_CLOSED','ACTION_SELECTED')
    reasons=('', 'OPEN','CLOSED','WRONG_MODE','NO_ITEM','NOT_READY','DEFERRED')
    if event not in events:return
    try:xbmc.log('[XCMate][DETAIL_MENU] event={} reason={} actions_ready={} playback_waiting={}'.format(
        event,reason if reason in reasons else 'OTHER',int(bool(ready)),int(bool(waiting))),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


class DetailMenuMixin:
    def _detail_menu_hide(self):
        was_open=getattr(self,'_detail_menu_open',False)
        self._detail_menu_open=False
        self.setProperty('XCMate.DetailMenu','')
        self.getControl(810).setVisible(False)
        self.getControl(800).setVisible(False)
        if was_open:mark('MENU_CLOSED')

    def _detail_menu_prepare(self,mode):
        self.getControl(820).setLabel(tr(34300))
        self.getControl(820).setVisible(mode=='detail')
        context=str((self.selected or {}).get('sid',''))
        if mode!='detail' or context!=getattr(self,'_detail_menu_context',None):
            self._detail_menu_hide()
        elif not getattr(self,'_detail_menu_open',False):self._detail_menu_hide()

    def _detail_menu_close(self):
        self._detail_menu_hide()
        self.getControl(300).selectItem(getattr(self,'_detail_menu_row',0))
        self.setFocusId(getattr(self,'_detail_menu_focus',300))

    def _detail_menu_show(self,button=False):
        ready=bool(self.actions);waiting=bool(self._playback_waiting)
        reason='WRONG_MODE' if self.mode!='detail' else 'NO_ITEM' if not self.selected or not self.selected.get('sid') else 'OPEN'
        mark('DETAIL_MENU_ELIGIBILITY',reason,ready,waiting)
        if reason!='OPEN':return False
        self._detail_menu_focus=self.getFocusId() if button else getattr(self,'_action_focus',self.getFocusId())
        if self._detail_menu_focus not in (300,400,820):self._detail_menu_focus=300
        self._detail_menu_row=self.getControl(300).getSelectedPosition()
        self._detail_menu_context=str(self.selected['sid'])
        self._detail_menu_open=True;self.setProperty('XCMate.DetailMenu','true')
        self.getControl(802).setLabel('XCMate')
        self._fill(810,[dict(name=tr(34200 if self.kind=='vod' else 34201)),
                        dict(name=tr(34202)),dict(name=tr(34203)),
                        dict(name=tr(33703)),dict(name=tr(34204))])
        # Explicit parent visibility, independent of an info-label used as an
        # XML boolean condition. Both entry methods use this same native panel.
        self.getControl(800).setVisible(True);self.getControl(810).setVisible(True)
        mark('MENU_VISIBLE')
        self.setFocusId(810)
        mark('FOCUS_810','OPEN' if self.getFocusId()==810 else 'DEFERRED')
        return True

    def _detail_menu_action(self,key):
        if getattr(self,'_detail_menu_open',False):
            if key in (1,2,9,10,92):self._detail_menu_close()
            return True
        if key==1:
            mark('DETAIL_LEFT_RECEIVED')
            return self._detail_menu_show()
        if self.mode=='detail' and key==2 and getattr(self,'_action_focus',self.getFocusId())==300:
            self.setFocusId(820);return True
        return False

    def _detail_menu_click(self,cid):
        if cid==820 and self.mode=='detail':
            mark('DETAIL_ACTIONS_BUTTON');self._detail_menu_show(button=True);return True
        if not getattr(self,'_detail_menu_open',False):return False
        if cid!=810:return True
        choice=self.getControl(810).getSelectedPosition();mark('ACTION_SELECTED');self._detail_menu_close()
        if choice==0:
            from downloads_ui import request
            request(self)
        elif choice==1:
            from downloads_ui import manage
            manage()
        elif choice==2:
            item=dict(self.selected)
            def retry():
                from media_art import retry_poster,poster_report
                code=retry_poster(item)
                return code,poster_report(item)
            def ready(value):
                from media_art import diagnostic_label
                code,report=value
                text=diagnostic_label(code)+' · '+str(report['source_field'])
                if report['candidate_count']<2:text+=' · '+tr(34500)
                xbmcgui.Dialog().notification('XCMate',text)
            self._request(retry,ready)
        elif choice==3:self._poster_status()
        return True
