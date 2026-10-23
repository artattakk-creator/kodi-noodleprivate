"""Never log packet, credential, challenge or filename details."""
class Quiet:
 def debug(self,*a,**k):pass
 info=warning=warn=error=exception=critical=debug
 def isEnabledFor(self,*a):return False
logger=Quiet()
def tqdm(*args,**kwargs):raise RuntimeError('PROGRESS_UNAVAILABLE')
