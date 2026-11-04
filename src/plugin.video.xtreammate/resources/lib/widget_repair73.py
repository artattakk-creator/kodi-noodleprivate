"""Repair an existing manual binding without moving slots or touching skin XML."""
from localization import tr


def diagnose(profile,skin,kind,pid):
    from widget_binding50 import context,options
    from widget_hooks45 import probe
    saved=any(r['state']=='ALREADY_LINKED' for r in options(context(profile,skin),kind,pid))
    if not saved:return 'NO_SAVED_BINDING'
    generated=probe()
    matches=[r for r in generated.get('bindings',[]) if r['pid']==str(pid) and r['kind']==kind]
    if not matches:return 'HOME_BUILD_STALE'
    if any(not r.get('hooks') for r in matches):return 'BLOCKED_NO_RELOAD_HOOK'
    from widget_refresh45 import read
    frame=read(pid,kind)
    return 'READY' if frame else 'DATA_PENDING'


def existing(profile,skin,kind,pid,slot):
    import xbmcgui
    from widget_manager50 import runtime,rebuild
    code=diagnose(profile,skin,kind,pid)
    if not xbmcgui.Dialog().yesno('XCMate',tr(38024,slot+1,code)):
        return
    current_profile,current_skin=runtime()
    if (current_profile,current_skin)!=(profile,skin):raise ValueError('PROFILE_CHANGED')
    # Recheck the saved source after confirmation; never create a new binding.
    from widget_binding50 import context,options
    if not any(r['state']=='ALREADY_LINKED' and r['slot']==slot for r in options(context(profile,skin),kind,pid)):
        raise ValueError('PROFILE_CHANGED')
    ctx=context(profile,skin)
    plan=prepare_hook(ctx,kind,pid,slot)
    if plan is not None:apply_hook(plan['id'],profile,skin,confirmed=True)
    rebuild()
    xbmcgui.Dialog().notification('XCMate',tr(36415))


def hook_candidate(ctx,kind,pid,slot):
    """Append one own runtime hook; retain original URL, slot, title and options."""
    import ast
    from widget_binding50 import own
    from widget_hooks45 import HOOK
    suffix='.'+str(slot) if slot else ''
    rows=ctx['rows'];index=next((i for i,r in enumerate(rows) if r[:3]==['mainmenu','10000','widgetPath'+suffix]),None)
    if index is None or not own(rows[index][3],kind,pid):raise ValueError('OCCUPIED_SLOT')
    url=rows[index][3]
    if 'XCMate.Widget45.Reload.'+kind in HOOK.findall(url):return ctx['data']
    if len(url)>8192:raise ValueError('PROFILE_BUDGET')
    updated=url+'&xcmate_reload45=$INFO[Window(Home).Property(XCMate.Widget45.Reload.'+kind+')]'
    raw=ctx['data'];tree=ast.parse(raw.decode('utf-8'),mode='eval');literal=tree.body.elts[index].elts[3]
    lines=raw.splitlines(keepends=True)
    start=sum(map(len,lines[:literal.lineno-1]))+literal.col_offset
    stop=sum(map(len,lines[:literal.end_lineno-1]))+literal.end_col_offset
    result=raw[:start]+repr(updated).encode()+raw[stop:]
    expected=[list(r) for r in rows];expected[index][3]=updated
    if ast.literal_eval(result.decode('utf-8'))!=expected:raise ValueError('CANDIDATE_VERIFY_FAILED')
    return result


def prepare_hook(ctx,kind,pid,slot):
    from widget_transaction50 import prepare,read,sha
    if read(ctx['target'])!=ctx['data'] or sha(read(ctx['menu']))!=ctx['menu_sha']:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
    data=hook_candidate(ctx,kind,pid,slot)
    if data==ctx['data']:return None
    metadata={k:ctx[k] for k in ('profile','skin','menu','menu_sha','meta_sha')}
    metadata.update(repair73=True,kind=kind,pid=str(pid),slot=slot)
    return prepare('binding',[(ctx['target'],data)],metadata)


def apply_hook(token,profile,skin,confirmed=False,restore=False):
    import ast
    from widget_binding50 import context
    from widget_transaction50 import load,apply,folder,read
    plan=load(token,'binding');m=plan['metadata'];ctx=context(profile,skin)
    if not m.get('repair73') or any(ctx[k]!=m[k] for k in ('profile','skin','menu','menu_sha','meta_sha')):raise ValueError('PROFILE_CHANGED')
    before=read(folder()/token/'original.0');after=read(folder()/token/'candidate.0')
    previous=dict(ctx,data=before,rows=ast.literal_eval(before.decode('utf-8')))
    if hook_candidate(previous,m['kind'],m['pid'],m['slot'])!=after:raise ValueError('CANDIDATE_VERIFY_FAILED')
    return apply(token,'binding',[ctx['target']],confirmed=confirmed,restore=restore)
