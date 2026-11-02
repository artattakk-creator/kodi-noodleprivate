"""Read installed versions only; never patch or import third-party helpers."""
def inspect():
 import xbmcaddon
 result=dict(code='EXTERNAL_DIAGNOSIS_ONLY',reported='Arrow timedelta/tzinfo traceback is external; not proof of XCMate image failure',versions={},skin_files_changed=False)
 for name in ('script.module.arrow','script.module.metadatautils','script.skin.helper.widgets','script.skin.helper.backgrounds','skin.titan.bingie.mod','repository.bingie'):
  try:result['versions'][name]=xbmcaddon.Addon(name).getAddonInfo('version')
  except (RuntimeError,ValueError):result['versions'][name]='NOT_INSTALLED'
 return result
