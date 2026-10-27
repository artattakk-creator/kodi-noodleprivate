"""Existing reader plus explicit choices; IO stays in existing data workers."""
from library_index import Reader as BaseReader


class Reader(BaseReader):
    def page(self,kind,*args,**kwargs):
        rows,total=super().page(kind,*args,**kwargs)
        if kind in ('vod','series'):
            from media_overrides43 import apply_many
            rows=apply_many(self.pid,rows)
        return rows,total

    def get(self,kind,sid):
        row=super().get(kind,sid)
        if row and kind in ('vod','series'):
            from media_overrides43 import apply_many
            row=apply_many(self.pid,[row])[0]
        return row
