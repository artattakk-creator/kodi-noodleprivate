"""Owner-local confirmed pages, isolated by query/portal/generation and offset.

Pending/error is not a publication of zero matches. No SQL, network or disk.
A final confirmed empty page still replaces old results. Bounded to 24 pages.
"""
from collections import OrderedDict
KINDS=('live','vod','series')
PENDING=('INDEX_PENDING','INDEX_ERROR','GENRE_PENDING')

class Pages:
    def __init__(self,context):self.context=context;self.pages=OrderedDict();self.preserved={}

    def publish(self,value,view):
        for kind in KINDS:
            incoming=value.get(kind)
            if not isinstance(incoming,dict):continue
            key=(kind,max(0,int(view[1])) if view and view[0]==kind else 0)
            old=self.pages.get(key);new=dict(incoming,rows=list(incoming.get('rows',[])))
            temporary=new.get('code') in PENDING or new.get('partial',False)
            preserve=bool(old and old.get('rows') and temporary)
            if preserve:
                if new.get('rows'):
                    by_id={str(row['sid']):row for row in new['rows']}
                    rows=[by_id.pop(str(row['sid']),row) for row in old['rows']]
                    rows.extend(by_id.values());new['rows']=rows[:48]
                else:new['rows']=old['rows']
                new['total']=max(old.get('total') or 0,new.get('total') or 0,len(new['rows']))
                new['partial']=True
            self.preserved[key]=preserve;self.pages[key]=new;self.pages.move_to_end(key)
            while len(self.pages)>24:
                removed,_=self.pages.popitem(last=False);self.preserved.pop(removed,None)

    def section(self,kind,offset=0):
        return self.pages.get((kind,offset),dict(rows=[],total=None,code='INDEX_PENDING'))
