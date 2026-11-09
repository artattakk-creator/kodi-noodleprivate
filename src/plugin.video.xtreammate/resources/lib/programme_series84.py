"""Classification hint only: still require unique API and independent details."""
def known(event):
 from epg_events import title_key
 title=title_key(str(event.get('title') or ''))
 return title==title_key('Star Trek: Deep Space Nine')
