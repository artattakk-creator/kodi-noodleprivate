"""Local, immutable texture snapshots. No input, focus, player or network work."""
import os
import xml.etree.ElementTree as ET

LIVE_TEXTURES={'tv_normal.png':'panel.default','tv_focus.png':'focus.rail',
 'tv_pause.png':'icon.player.pause','tv_play.png':'icon.player.play','tv_back.png':'icon.player.seek-back',
 'tv_forward.png':'icon.player.seek-forward','tv_stop.png':'icon.player.stop','tv_more.png':'icon.player.more',
 'tv_live.png':'icon.player.live-edge','tv_audio.png':'icon.player.audio','tv_video.png':'icon.player.video-settings',
 'tv_subtitle.png':'icon.player.subtitles','tv_epg.png':'icon.epg','tv_settings.png':'icon.settings','tv_tv.png':'icon.epg.channels','tv.png':'icon.live'}
MEDIA_ACTIONS={'play':'play','restart':'restart','resume':'resume','seasons':'seasons',
 'continue_episode':'resume','next_episode':'episodes','trailer':'trailer'}


def snapshot():
    try:
        from theme_store import current
        return current()
    except (OSError,ValueError,ImportError,RuntimeError):return None


def lightweight_background():
    import xbmcaddon
    return os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','lightweight_splash.jpg')


def media_background(owner,fanart=''):
    # Landing/search keep one stable original splash while posters refresh.
    if not getattr(owner,'_theme',None):
        if owner.mode in ('landing','search') or not fanart:return lightweight_background()
    return fanart or os.path.join(__import__('xbmcaddon').Addon().getAddonInfo('path'),'resources','media','media_neutral.png')


def texture(owner,fallback,key=''):
    from theme_store import asset
    return asset(key or LIVE_TEXTURES.get(os.path.basename(fallback),''),fallback,snapshot=getattr(owner,'_theme',None))


def action_art(action,theme,favourite=False):
    from theme_store import asset
    name=('favorite-remove' if favourite else 'favorite-add') if action=='favourite' else MEDIA_ACTIONS.get(action,'')
    icon=asset('icon.media.'+name,snapshot=theme) if name else ''
    return dict(icon=icon,thumb=icon)


def choice_items(labels,keys,theme):
    if not theme:return labels
    import xbmcgui
    from theme_store import asset
    result=[]
    for label,key in zip(labels,keys):
        item=xbmcgui.ListItem(label);icon=asset(key,snapshot=theme);item.setArt(dict(icon=icon,thumb=icon));result.append(item)
    return result


def guide_status(owner,status,detail=False):
    from theme_store import asset
    theme=getattr(owner,'_theme',None)
    if theme:
        owner.setProperty('XCMate.ThemeGuideBackground',asset('background.epg.detail' if detail else 'background.epg.guide',asset('background.epg',snapshot=theme),snapshot=theme))
        owner.setProperty('XCMate.ThemeEpgStatus',asset('status.epg.source-error' if status=='error' else 'status.epg.no-data' if status=='empty' else 'icon.epg.clock',snapshot=theme))


def epg_choices(labels,theme):
    from localization import tr
    keys={tr(32549):'icon.shared.info',tr(33112):'icon.shared.info',tr(32550):'icon.player.play',tr(32551):'icon.epg.remind',tr(33118):'icon.epg.channels',tr(33121):'icon.shared.info',tr(33113):'icon.epg'}
    return choice_items(labels,[keys.get(label,'icon.shared.info') for label in labels],theme)


def apply_xml(tree,theme,filename,kind='vod'):
    """Adapt current .22 layouts. Never change focus IDs/links or hit rectangles."""
    from theme_store import asset
    root=tree.getroot();controls=root.find('controls')
    background='background.epg.detail' if filename=='XCMateProgramme.xml' else 'background.epg.guide' if 'Guide' in filename else 'background.series' if kind=='series' else 'background.movies'
    keys={'media_neutral.png':background,'lightweight_splash.jpg':background,'tv_normal.png':'panel.default','media_shade.png':'panel.overlay',
          'tv_focus.png':'focus.default','media_detail_gradient.png':'panel.media.rail.gradient'}
    for node in root.iter():
        if node.tag in ('texture','texturefocus','texturenofocus') and node.text and not node.text.startswith('$'):
            key=keys.get(node.text.rsplit('/',1)[-1])
            # The .22 transparent guide frame remains untouched: text is drawn
            # beneath some native focus layers on Omega/BINGIE.
            if key:node.text=asset(key,asset('background.epg',node.text,snapshot=theme) if key==background and 'Guide' in filename else node.text,snapshot=theme)
    def image(parent,key,x,y,w,h,dynamic=False):
        value=key if dynamic else asset(key,snapshot=theme)
        if not value:return
        n=ET.SubElement(parent,'control',{'type':'image','xcmate-decoration':'true'})
        for tag,text in dict(left=x,top=y,width=w,height=h,texture=value,aspectratio='keep').items():ET.SubElement(n,tag).text=str(text)
    if filename=='XCMateGuide.xml':
        node=root.find("./controls/control[@type='image']/texture")
        if node is not None:
            node.set('fallback',node.text);node.text='$INFO[Window.Property(XCMate.ThemeGuideBackground)]'
    if filename=='XCMateMedia.xml':
        for cid in ('300','330'):
            for layout in root.findall("./controls/control[@id='"+cid+"']/*"):
                if layout.tag not in ('itemlayout','focusedlayout'):continue
                image(layout,'$INFO[ListItem.Art(icon)]',8,6,30,30,True)
                for label in layout.findall("control[@type='label']"):
                    left=label.find('left');width=label.find('width')
                    if left is not None:left.text='46'
                    if width is not None:width.text=str(max(1,int(width.text)-38))
        for layout in root.iter():
            # Focused rows use the proven Core frame and no poster overlay.
            if layout.tag!='itemlayout':continue
            for n in list(layout.findall("control[@type='image']")):
                if n.findtext('texture')=='$INFO[ListItem.Art(poster)]':
                    before=len(layout)
                    image(layout,'panel.media.poster.shade',n.findtext('left','0'),n.findtext('top','0'),n.findtext('width','100'),n.findtext('height','92'))
                    if len(layout)>before:
                        shade=layout[-1];layout.remove(shade)
                        layout.insert(list(layout).index(n)+1,shade)
        image(controls,'icon.shared.search',1058,38,28,28)
    headers=(('310','icon.epg.day-prev'),('311','icon.epg.day-next'),('312','icon.epg.today'),('313','icon.epg.clock'),('314','icon.epg.channels'),('315','icon.shared.search')) if filename=='XCMateGuideGrid.xml' else (('310','icon.epg.day-prev'),('311','icon.epg.day-next'),('312','icon.shared.info')) if filename=='XCMateGuide.xml' else ()
    for cid,key in headers:
        button=root.find("./controls/control[@id='"+cid+"']")
        if button is None:continue
        image(controls,key,int(button.findtext('left','0'))+7,int(button.findtext('top','0'))+8,24,24)
        text=button.find('textoffsetx')
        if text is None:text=ET.SubElement(button,'textoffsetx')
        text.text='34'
    if 'Guide' in filename:image(controls,'$INFO[Window.Property(XCMate.ThemeEpgStatus)]',8,132,28,28,True)
    image(controls,'panel.divider',44,64,1192,3)
    image(controls,'icon.shared.back',8,674,28,24)
