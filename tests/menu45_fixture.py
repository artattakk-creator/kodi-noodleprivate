"""Native ListItem / useDetails additions for pre-.27 thin Kodi models."""
import inspect
class Item:
 def __init__(self,label='',*args,**kwargs):self.label=label;self.art={}
 def getLabel(self):return self.label
 def setArt(self,art):self.art.update(art)
def install(gui):
 gui.ListItem=Item
 original=gui.Dialog
 def dialog(*args,**kwargs):
  value=original(*args,**kwargs)
  for name in ('select','multiselect'):
   method=getattr(value,name,None)
   if method is None:continue
   signature=inspect.signature(method)
   if 'useDetails' not in signature.parameters and not any(p.kind==p.VAR_KEYWORD for p in signature.parameters.values()):
    def call(*args,_method=method,**kwargs):kwargs.pop('useDetails',None);return _method(*args,**kwargs)
    setattr(value,name,call)
  return value
 gui.Dialog=dialog
 return gui
