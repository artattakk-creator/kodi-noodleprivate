"""Invert only reviewed .24 visual hooks before checking the original freezes.

No baseline digests are replaced and no input/playback method is exempted.
"""
import ast


def without_theme(source):
    binary=isinstance(source,bytes)
    if binary:source=source.decode()
    source=source.replace("        self.osd_bg.setImage(__import__('theme_render').texture(self,os.path.join(self._media,'tv_panel.png'),'panel.player.options' if self.mode=='extras' else 'panel.player.controls'))\n",'')
    source=source.replace("        self._theme=__import__('theme_render').snapshot()\n",'')
    for line in ("        __import__('theme_render').guide_status(self,'error')\n", "        __import__('theme_render').guide_status(self,'ready' if value['rows'] else 'empty')\n", "        __import__('theme_render').guide_status(self,'ready' if value[0] else 'empty',True)\n","        __import__('theme_render').guide_status(self,'loading')\n"):
        source=source.replace(line,'')
    source=source.replace("__import__('theme_render').epg_choices(choices,self._theme),useDetails=bool(self._theme)",'choices')
    while True:
        nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='texture' and isinstance(n.func.value,ast.Call) and isinstance(n.func.value.func,ast.Name) and n.func.value.func.id=='__import__' and len(n.func.value.args)==1 and isinstance(n.func.value.args[0],ast.Constant) and n.func.value.args[0].value=='theme_render']
        if not nodes:break
        node=max(nodes,key=lambda n:(n.lineno,n.col_offset));assert len(node.args)==3
        assert isinstance(node.args[0],ast.Name) and node.args[0].id=='self'
        lines=source.splitlines(keepends=True);start=sum(map(len,lines[:node.lineno-1]))+node.col_offset;stop=sum(map(len,lines[:node.end_lineno-1]))+node.end_col_offset
        source=source[:start]+ast.get_source_segment(source,node.args[1])+source[stop:]
    source=source.replace("window_source(xml,'series' if view=='SERIES' else 'vod')","window_source(xml)")
    source=source.replace("def add_action(router,label,url,icon=None,plot='',fanart=None):","def add_action(router,label,url,icon=None,plot=''):")
    source=source.replace("    if fanart:item.setArt({'fanart':fanart})\n",'')
    return source.encode() if binary else source
