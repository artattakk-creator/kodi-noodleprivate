""".96 Xtream provider EPG baseline, with lossless legacy intent history.

Only portal configuration changes here. No network, EPG database, guide import,
backup, optional source, credential or artwork-consent changes. Call ensure()
from the existing upgrade/service worker before loading EPG portal snapshots.
"""
from copy import deepcopy

FIELDS=('epg_show','provider_epg_enabled','epg_opt_out94','provider_epg_opt_out94')
_TARGET=dict(epg_show=True,provider_epg_enabled=True,epg_opt_out94=False,provider_epg_opt_out94=False)
MESSAGE='Anbieter-EPG ist die Grundversorgung. Verfügbare Anbieterdaten werden verwendet; zusätzliche XMLTV-Quellen sind optional. Aktiviert bedeutet noch keinen erfolgreichen Import.'


def normalized(portal):
 """Detached configuration; archive original flag values before .96 defaults."""
 result=deepcopy(portal)
 if result.get('type')!='xtream':return result
 if result.get('provider_baseline96') is True and all(type(result.get(k)) is bool and result[k]==v for k,v in _TARGET.items()):return result
 history=result.get('provider_baseline_history96',[])
 if not isinstance(history,list):raise ValueError('PROVIDER_BASELINE_HISTORY_INVALID')
 previous={k:deepcopy(result[k]) for k in FIELDS if k in result}
 if previous:
  history.append(dict(contract='0.1.29.96',reason='provider_epg_baseline',values=previous))
 result.update(_TARGET)
 result.update(provider_baseline96=True,provider_baseline_history96=history)
 return result


def migrate_portal(portal):
 """Existing atomic portal writer plus an independent detached readback.

 Caller snapshots stay untouched even on write/readback failure. Existing
 profile coordination serializes migration with setup and portal editing.
 """
 from portals import get_by_id,update
 from profile_transaction import writing
 with writing():
  current=get_by_id(str(portal['id']))
  if not current:raise ValueError('PROVIDER_PORTAL_UNAVAILABLE')
  expected=normalized(current)
  if expected==current:return current
  if update(current['id'],expected) is False:raise OSError('PROVIDER_BASELINE_SAVE_FAILED')
  saved=get_by_id(current['id'])
  # The existing writer owns its updated timestamp; all other fields,
  # including credentials and every unrelated setting, must read back.
  facts=lambda row:{k:v for k,v in row.items() if k!='updated'}
  if not saved or facts(saved)!=facts(expected):raise OSError('PROVIDER_BASELINE_READBACK_FAILED')
  return saved


def ensure():
 """Idempotent upgrade worker entry point; each migrated portal is verified."""
 from portals import load_all
 for portal in load_all():
  if portal.get('type')=='xtream':migrate_portal(portal)
 return load_all()
