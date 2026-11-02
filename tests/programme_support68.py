"""Synthetic tests inject the completed worker read, never GUI disk IO."""
import threading
def completed_read(window):
 values=[];errors=[]
 def read():
  try:
   from programme_art46 import cached
   values.append(cached(window.event))
  except BaseException as error:errors.append(error)
 thread=threading.Thread(target=read);thread.start();thread.join(timeout=2)
 if thread.is_alive():raise AssertionError('SYNTHETIC_PROGRAMME_READ_TIMEOUT')
 if errors:raise errors[0]
 window._art68=values[0]
