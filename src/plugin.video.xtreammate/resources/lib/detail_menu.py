"""Left-side native detail menu; keep media/player actions in their old path."""
import xbmcgui
from localization import tr


class DetailMenuMixin:
    def _detail_menu_hide(self):
        self._detail_menu_open=False
        self.setProperty('XCMate.DetailMenu','')
        self.getControl(810).setVisible(False)

    def _detail_menu_close(self):
        self._detail_menu_hide()
        self.setFocusId(getattr(self,'_detail_menu_focus',300))

    def _detail_menu_action(self,key):
        if getattr(self,'_detail_menu_open',False):
            if key in (1,2,9,10,92):self._detail_menu_close()
            return True
        if key!=1 or self.mode!='detail' or not self.actions or self._playback_waiting:return False
        self._detail_menu_focus=self.getFocusId()
        self._detail_menu_open=True;self.setProperty('XCMate.DetailMenu','true')
        self._fill(810,[dict(name=tr(34200 if self.kind=='vod' else 34201)),
                        dict(name=tr(34202)),dict(name=tr(34203)),
                        dict(name=tr(33703)),dict(name=tr(34204))])
        self.getControl(810).setVisible(True);self.setFocusId(810)
        return True

    def _detail_menu_click(self,cid):
        if not getattr(self,'_detail_menu_open',False):return False
        if cid!=810:return True
        choice=self.getControl(810).getSelectedPosition();self._detail_menu_close()
        if choice==0:
            from downloads_ui import request
            request(self)
        elif choice==1:
            from downloads_ui import manage
            manage()
        elif choice==2:
            item=dict(self.selected)
            def retry():
                from media_art import retry_poster
                return retry_poster(item)
            def ready(code):
                from media_art import diagnostic_label
                xbmcgui.Dialog().notification('XCMate',diagnostic_label(code))
            self._request(retry,ready)
        elif choice==3:self._poster_status()
        return True
