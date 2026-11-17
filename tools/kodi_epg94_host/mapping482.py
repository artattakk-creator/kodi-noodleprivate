"""Native mapping journey; runs inside the existing isolated Kodi owner."""
import menu_icons45
import guide_mapping48
from guide_grid_window import GuideGridWindow
from library_index import replace_catalog

phase94('mapping482_native_journeys')
# A real catalogue, not a provider request, supplies the native Grid entry.
replace_catalog(portal['id'],'live',[dict(stream_id='1',name='Native station',category_id='a',epg_channel_id='xml')],
                [dict(category_id='a',category_name='Native group')])
cases482=[]
for kind482 in ('mini','grid'):
 grid482=None
 if kind482=='grid':
  router482=SimpleNamespace(_xc=lambda p:None,url_for=lambda action,**kw:'plugin://plugin.video.xtreammate/?action='+str(action))
  grid482=GuideGridWindow('XCMateGuideGrid.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
  grid482.configure(router482,portal);grid482.show()
  def grid_ready482():grid482.pump();return grid482._ready and not grid482._loading and bool(grid482.rows)
  wait(grid_ready482,'GRID482_NOT_READY')
  from mapping_context96 import GridAdapter
  adapter482=GridAdapter(grid482)
 else:adapter482=MiniAdapter(parent,channel)
 child482=MappingWindow48('XCMateMapping48.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
 child482.configure(adapter482.parent,adapter482)
 original_select482=menu_icons45.select
 def actual_source_picker482(dialog,heading,labels,*args,**kwargs):
  assert labels and any('lokal' in s for s in labels)
  Path('/root/epg482-source-'+kind482+'.json').write_text(json.dumps(dict(kind=kind482,labels=labels)))
  return original_select482(dialog,heading,labels,*args,**kwargs)
 menu_icons45.select=actual_source_picker482
 try:
  child482._shown=True;child482.show();wait(lambda:child482._ready,'MAPPING482_NOT_READY')
  assert child482.query=='Native station'
  def channels482():child482.pump();return child482.source is not None and bool(child482.rows) and child482.future is None
  wait(channels482,'MAPPING482_SOURCE_OR_NAMES_FAILED',45)
  assert child482.rows[0]['id']=='xml'
  assert child482.getControl(103).getText().find('CHANNELS_READY')>=0
  child482.getControl(200).selectItem(0);child482.setFocusId(200)
  xbmc.executebuiltin('Action(Select)',wait=False)
  def preview482():child482.pump();return child482.previewed
  wait(preview482,'MAPPING482_PREVIEW_FAILED')
  assert child482.getControl(301).getText().find('Native programme')>=0
  xbmc.sleep(200);preview_shot482=shot('epg482-preview-'+kind482)
  assert 'PREVIEW_READY' in child482.getControl(103).getText()
  source_before482=Path(epg_sources._file_path()).read_bytes()
  # A global capacity rejection must be visible and never fake a running job.
  guide_mapping48._slots.acquire()
  try:
   child482._preview()
   assert child482.future is None and not child482.previewed
   assert 'MAPPING_BUSY' in child482.getControl(103).getText()
   assert not child482.getControl(104).isVisible()
   xbmc.sleep(200);busy_shot482=shot('epg482-busy-'+kind482)
  finally:guide_mapping48._slots.release()
  assert Path(epg_sources._file_path()).read_bytes()==source_before482
  child482._preview();wait(preview482,'MAPPING482_RETRY_FAILED')
  child482.setFocusId(405);xbmc.executebuiltin('Action(Select)',wait=False)
  def saved482():child482.pump();return child482.saved
  wait(saved482,'MAPPING482_SAVE_FAILED')
  binding482=epg_sources.configuration(portal['id'])['source_mappings48']['1']
  assert binding482==dict(channel='xml',source='provider')
  if kind482=='grid':
   assert grid482.rows[grid482.row]['mapping']=='MANUAL'
   assert 'Native programme' in grid482.rows[grid482.row]['events'][0]['title']
  else:assert snapshot.get('1',time.time())['mapping']=='MANUAL'
  cases482.append(dict(kind=kind482,parent='NATIVE_GRID' if grid482 else 'SYNTHETIC_MINI_OWNER',
      prefilled_query=True,source_picker='NATIVE_DIALOG_SELECTED_BY_RPC',preview=preview_shot482,
      busy=busy_shot482,source_qualified_readback=True,actual_adapter_apply=True))
 finally:
  menu_icons45.select=original_select482;child482.close();adapter482.finish(child482.saved)
  if grid482:grid482.close()
report['mapping482']=dict(status='PASS',cases=cases482,android='ANDROID_NOT_TESTED',source_picker_pixel_review='REQUIRED')
