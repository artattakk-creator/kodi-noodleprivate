"""IR category focus is distinct from confirmed category and gallery layout."""
def handle(view,key,previous_focus):
    if view.mode not in ('grid','groups'):return False
    if previous_focus==200 and key in (3,4):
        view._mode_focus[view.mode]=200
        view.setFocusId(200)  # Native list moved; do not request another category.
        return True
    if previous_focus==200 and key==2:
        if not view.rows:return True
        view._category_focus44=False;view.mode='grid';view._cols=4
        view._mode_focus['grid']=210;view._show('grid')
        view.getControl(210).selectItem(0);view._focus_item(0);view.setFocusId(210)
        return True
    if previous_focus==210 and key==2 and view._cols==4:
        position=view.getControl(210).getSelectedPosition()
        view._cols=6;view._mode_focus['grid']=210;view._show('grid')
        view.getControl(210).selectItem(position);view._focus_item(position);view.setFocusId(210)
        return True
    if previous_focus==210 and key==1 and view._last_position%view._cols==0:
        position=view._last_position
        view._cols=4;view.mode='groups';view._category_focus44=True
        view._mode_focus['groups']=200;view._show('groups')
        view.getControl(210).selectItem(position)
        view.setFocusId(200)
        return True
    return False
