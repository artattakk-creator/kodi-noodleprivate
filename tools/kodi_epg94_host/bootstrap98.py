"""Disposable native-fixture startup only. Never imported by the add-on."""

def settle_fixture_prompt(rpc):
    state=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
    if state['currentwindow']['id']!=10100 or state['currentcontrol']['label']!='No':return False
    labels=rpc('XBMC.GetInfoLabels',dict(labels=['Control.GetLabel('+str(i)+')' for i in range(1,31)]))
    if labels.get('Control.GetLabel(1)')!='Disabled add-ons':return False
    expected='Would you like to enable this add-on? Catalog73 synthetic GUI contract'
    normalized={' '.join(text.replace('[CR]',' ').split()) for text in labels.values()}
    if expected not in normalized:return False
    # Decline only this known disposable fixture's delayed enable prompt.
    # Foreign dialogs and user configuration are never touched.
    rpc('Input.Select')
    return True


def focus_receipt(dialog,owner,control,expected_owner,expected_control):
    if dialog in (0,10100) or owner!=expected_owner or control!=expected_control:return None
    return dict(dialog=dialog,owner=owner,control=control)
