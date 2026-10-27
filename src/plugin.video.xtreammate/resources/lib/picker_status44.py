"""Fixed source/status classes; never query text, file paths or API secrets."""
from localization import tr
CODES={'TMDB_DISABLED':35971,'TMDB_TOKEN_MISSING':35972,'HTTP_AUTH':35973,'HTTP_RATE_LIMIT':35974,
       'TIMEOUT':35975,'DNS_ERROR':35975,'TLS_ERROR':35975,'IMAGE_DECODER_MISSING':35935,
       'INVALID_IMAGE':35976,'NO_RESULTS':35977,'FOREIGN_MODAL':35978,'WRONG_MODE':35979,
       'NO_METADATA':35970,'SAVE_FAILED':35980,'PROVIDER_REFRESH_UNAVAILABLE':35981}


def mark(stage,source='',code='',rows=None):
    if stage not in ('REQUEST','OPEN','OPEN_REJECTED','SOURCE','RESULTS','PREVIEW','SAVE','ERROR','CLOSED'):return
    source=source if source in ('provider','tmdb','commons','local','metadata','art') else 'other'
    allowed=set(CODES)|{'OK','BUSY','CANCELLED','INVALID_JSON','UNSAFE_SOURCE','HTTP_NOT_FOUND','HTTP_SERVER','HTTP_CLIENT','CONTENT_TYPE','CONTENT_ENCODING','RESPONSE_LIMIT','IMAGE_LIMIT','RESEARCH_BUSY','INVALID_TOKEN','WORKER_UNAVAILABLE','LOCAL_FILE_REQUIRED','UNAVAILABLE','BUDGET_FULL','DISK_FULL','WRONG_ITEM','PLAYBACK_BUSY','WINDOW_CLOSED'}
    code=code.partition(':')[0] if isinstance(code,str) else ''
    code=code if code in allowed else 'OTHER'
    try:
        import xbmc
        xbmc.log('[XCMate][PICKER44] stage='+stage+' source='+source+' code='+code+((' rows='+str(max(0,min(24,rows)))) if isinstance(rows,int) else ''),xbmc.LOGINFO)
    except Exception:pass


def message(code,source=''):
    label={'provider':35900,'tmdb':35901,'commons':35902,'local':35903}.get(source)
    text=tr(CODES[code]) if code in CODES else tr(35906,code)
    return (tr(label)+' · ' if label else '')+text+' ['+code+']'
