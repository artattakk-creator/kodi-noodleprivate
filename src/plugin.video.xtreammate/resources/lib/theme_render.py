"""Local texture bindings only. No input, focus, playback or network operations."""
import os
import xml.etree.ElementTree as ET

LIVE_TEXTURES = {
    'tv_normal.png':'panel.default', 'tv_focus.png':'focus.rail',
    'tv_pause.png':'icon.player.pause', 'tv_play.png':'icon.player.play',
    'tv_back.png':'icon.player.seek-back', 'tv_forward.png':'icon.player.seek-forward',
    'tv_stop.png':'icon.player.stop', 'tv_more.png':'icon.player.more',
    'tv_live.png':'icon.player.live-edge', 'tv_audio.png':'icon.player.audio',
    'tv_video.png':'icon.player.video-settings', 'tv_subtitle.png':'icon.player.subtitles',
    'tv_epg.png':'icon.epg', 'tv_settings.png':'icon.settings', 'tv_tv.png':'icon.epg.channels',
    'tv.png':'icon.live',
}
MEDIA_ACTIONS = {
    'play':'play', 'restart':'restart', 'resume':'resume', 'seasons':'seasons',
    'continue_episode':'resume', 'next_episode':'episodes', 'trailer':'trailer',
}


def snapshot():
    try:
        from theme_store import current
        return current()
    except (OSError, ValueError, ImportError):
        return None


def live_texture(owner, fallback, key=None):
    from theme_store import asset
    return asset(key or LIVE_TEXTURES.get(os.path.basename(fallback),''),
                 fallback,snapshot=getattr(owner,'_theme',None))


def action_art(action, theme, favourite=False):
    from theme_store import asset
    name = ('favorite-remove' if favourite else 'favorite-add') if action=='favourite' else MEDIA_ACTIONS.get(action,'')
    icon = asset('icon.media.'+name,snapshot=theme) if name else ''
    return {'icon':icon,'thumb':icon}


def choice_items(labels, keys, theme):
    """Native Kodi select supports ListItems; indices/actions stay identical."""
    if not theme: return labels
    import xbmcgui
    from theme_store import asset
    result=[]
    for label,key in zip(labels,keys):
        item=xbmcgui.ListItem(label)
        item.setArt({'icon':asset(key,snapshot=theme),'thumb':asset(key,snapshot=theme)})
        result.append(item)
    return result


def guide_state(window, status=None, detail=False):
    from theme_store import asset
    theme=getattr(window,'_theme',None)
    if not theme: return
    if status is not None: window._theme_guide_status=status
    status=getattr(window,'_theme_guide_status','loading')
    window.setProperty('XCMate.EpgStatusIcon',asset(
        'status.epg.source-error' if status=='error' else 'status.epg.no-data' if status=='empty' else 'icon.epg.clock',snapshot=theme))
    window.setProperty('XCMate.GuideBackground',asset(
        'background.epg.detail' if detail else 'background.epg.guide',snapshot=theme))


def decorate_xml(tree, theme, filename):
    """Decorative images have no IDs, focus or action handlers.

    Existing interactive rectangles and navigation remain exactly as bundled.
    Only action-list text makes room for its newly drawn ListItem icon.
    """
    from theme_store import asset
    root=tree.getroot();controls=root.find('controls')
    def image(parent,key,left,top,width,height,dynamic=False):
        value=key if dynamic else asset(key,snapshot=theme)
        if not value: return
        node=ET.SubElement(parent,'control',{'type':'image','xcmate-decoration':'true'})
        for name,text in dict(left=left,top=top,width=width,height=height,aspectratio='keep',texture=value).items():
            ET.SubElement(node,name).text=str(text)
        return node
    if filename=='XCMateMedia.xml':
        for cid in ('300','330'):
            for layout in root.findall("./controls/control[@id='"+cid+"']/*"):
                if layout.tag not in ('itemlayout','focusedlayout'): continue
                image(layout,'$INFO[ListItem.Art(icon)]',8,6,32,32,True)
                for label in layout.findall("control[@type='label']"):
                    if label.find('left') is not None: label.find('left').text='48'
                    width=label.find('width')
                    if width is not None: width.text=str(max(1,int(width.text)-40))
        for control in root.findall('./controls/control'):
            for layout in control:
                if layout.tag not in ('itemlayout','focusedlayout'): continue
                for node in list(layout.findall("control[@type='image']")):
                    if node.findtext('texture')=='$INFO[ListItem.Art(poster)]':
                        shade=image(layout,'panel.media.poster.shade',node.findtext('left','0'),node.findtext('top','0'),node.findtext('width','100'),node.findtext('height','92'))
                        if shade is not None: layout.remove(shade);layout.insert(list(layout).index(node)+1,shade)
        gradient=image(controls,'panel.media.rail.gradient',44,164,1192,144)
        if gradient is not None: controls.remove(gradient);controls.insert(2,gradient)
        image(controls,'icon.shared.search',1058,38,28,28)
    elif filename=='XCMateGuide.xml':
        texture=root.find("./controls/control[@type='image']/texture")
        if texture is not None: texture.text='$INFO[Window.Property(XCMate.GuideBackground)]'
        for cid,key in (('310','icon.epg.day-prev'),('311','icon.epg.day-next'),('312','icon.shared.info')):
            button=root.find("./controls/control[@id='"+cid+"']")
            image(controls,key,int(button.findtext('left'))+8,140,28,28)
            ET.SubElement(button,'textoffsetx').text='40'
        image(controls,'$INFO[Window.Property(XCMate.EpgStatusIcon)]',8,88,28,28,True)
    # Decorative divider sits between heading and content, never over controls.
    image(controls,'panel.divider',44,119,1192,3)
    image(controls,'icon.shared.back',8,674,28,24)
