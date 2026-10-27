"""Stable catalogue pages: no mixed generations or positional focus guessing."""
class CatalogueChanged(ValueError):
    pass


class Page(tuple):
    def __new__(cls,rows,total,offset,revision=None,selected=None):
        obj=super().__new__(cls,(rows,total))
        obj.offset=offset;obj.revision=revision;obj.selected=selected
        return obj


def revision(reader,kind):
    state=reader.state(kind) if hasattr(reader,'state') else None
    return (state.get('revision'),state.get('updated')) if state else None


def read(reader,kind,category,offset,limit,*,expected=None,restore=None):
    before=revision(reader,kind)
    if expected is not None and before!=expected:raise CatalogueChanged('CATALOGUE_CHANGED')
    if restore and hasattr(reader,'position'):
        position=reader.position(kind,restore,category)
        if position is not None:offset=position//limit*limit
    rows,total=reader.page(kind,category=category,offset=offset,limit=limit)
    if not isinstance(total,int) or total<0:raise CatalogueChanged('COUNT_UNAVAILABLE')
    if not rows and total and offset>=total:
        # A shortened catalogue can move the previous page beyond its end.
        # One bounded final-page read; never interpret this as an empty group.
        offset=(total-1)//limit*limit
        rows,total=reader.page(kind,category=category,offset=offset,limit=limit)
    if revision(reader,kind)!=before:raise CatalogueChanged('CATALOGUE_CHANGED')
    return Page(rows,total,offset,before,restore)
