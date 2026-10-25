"""First-run eligibility foundation; deliberately not activated by root yet.

The integration must provide ALL existing profiles, not only active ones, then
perform the separately reviewed native directory/modal/owner handoff. This pure
policy neither opens a dialog nor writes an account or guesses API capability.
"""


def eligibility(action,handle,all_profiles,modal=False,portal_hint=''):
    if not isinstance(all_profiles,(list,tuple)) or not isinstance(handle,int) or isinstance(handle,bool):
        return False,'INVALID_CONTEXT'
    if all_profiles:return False,'EXISTING_PROFILE'
    if action!='root':return False,'ACTION_CONTEXT'
    if handle<0:return False,'NO_DIRECTORY_OWNER'
    if portal_hint:return False,'PORTAL_HINT'
    if modal:return False,'MODAL_BUSY'
    return True,'ELIGIBLE'
