"""Storage action/target/backend attribution; no paths, hosts, IDs or labels."""
import re


def kind(value):
    if str(value).startswith('smb://'):return 'SMB'
    if str(value).startswith(('/mnt/media_rw/','/media/')):return 'USB'
    if str(value).startswith('/storage/') and not str(value).startswith(('/storage/emulated/','/storage/self/')):return 'USB'
    return 'LOCAL'


def mark(action,stage,target='',backend='',error=None,count=None):
    if action not in ('DOWNLOAD','RECORD'):return
    if stage not in ('PICKER_ACTION','PICKER_ROOT_LISTED','SOURCE_CATEGORY','TARGET_SELECTED','TARGET_PROBE','TARGET_BOUND','PERSIST_OK','STAGING_READY','TARGET_TEST_BEGIN','TARGET_TEST_DONE','FAILED'):return
    if target not in ('LOCAL','USB','SMB','UNKNOWN'):target='UNKNOWN'
    if backend not in ('','NATIVE','USB_STAGE','SMB2','INTERNAL_STAGE','INTERNAL_STAGE_EXCLUSIVE'):backend='OTHER'
    def token(value):return value if isinstance(value,str) and re.fullmatch('[A-Z][A-Z0-9_]{0,63}',value) else ''
    code=token(getattr(error,'code',''));step=token(getattr(error,'step',''));number=getattr(error,'number',getattr(error,'errno',0)) or 0
    try:
        import xbmc
        xbmc.log('[XCMate][STORAGE] PICKER_ACTION={} event={} TARGET_CLASS={} PROBE_BACKEND={} code={} step={} errno={} count={}'.format(action,stage,target,backend,code,step,number if isinstance(number,int) and 0<=number<=4095 else 0,count if isinstance(count,int) and 0<=count<=10000 else 0),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass
