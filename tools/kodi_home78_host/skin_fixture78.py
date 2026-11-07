"""Existing user layout and a native builder cache-hit, in a disposable profile.

The compiler output was produced by pinned SkinShortcuts Template 2.1.0. The
builder deliberately skips ReloadSkin to reproduce the production handoff gap.
"""
from pathlib import Path
import shutil,hashlib,json
exec(compile(Path('/base_skin78.py').read_text(encoding='utf-8'),'/base_skin78.py','exec'),globals())
root=Path('/root/.kodi');skin=root/'addons/skin.titan.bingie.mod'
# Nontrivial previously compiled rows exist BEFORE the repair transaction.
generated=skin/'xml/script-skinshortcuts-includes.xml'
shutil.copyfile('/candidate/xml/script-skinshortcuts-includes.xml',generated)
folder=root/'userdata/addon_data/script.skinshortcuts';folder.mkdir(parents=True,exist_ok=True)
rows=[]
for i,(kind,path,name) in enumerate((('videos','plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=fixture59&home50=1','Live-TV'),('movies','plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=fixture59','Filme'),('tvshows','plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=fixture59','Serien'),('movies','plugin://plugin.video.xtreammate/?fixture66=poster','Neu im Kino'))):
 suffix='' if i==0 else '.'+str(i)
 for key,value in dict(widget='Addon',widgetName=name,widgetType=kind,widgetTarget='videos',widgetPath=path).items():rows.append(['mainmenu','10000',key+suffix,value])
(folder/'skin.titan.bingie.mod.properties').write_text(repr(rows),encoding='utf-8')
(folder/'skin.titan.bingie.mod-mainmenu.DATA.xml').write_text('<shortcuts><shortcut><label>Startseite</label><action>ActivateWindow(Home)</action><labelID>10000</labelID></shortcut><shortcut><label>Neu im Kino</label><action>ActivateWindow(Videos,&quot;plugin://plugin.video.xtreammate/?fixture66=poster&quot;,return)</action><labelID>cinema78</labelID></shortcut></shortcuts>',encoding='utf-8')
protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}
Path('/root/old-layout78.json').write_text(json.dumps(protected))
(root/'addons/script.skinshortcuts/default.py').write_text("from pathlib import Path\nif 'XCMate78.Contract' not in Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesVariables.xml').read_text(encoding='utf-8'):raise SystemExit\nPath('/root/builder66-called').write_text('native cached build skipped')\nPath('/root/builder66-complete').write_text('done without ReloadSkin')\n")
