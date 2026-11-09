"""Classification hint only: still require unique API and independent details."""
def known(event):
 from epg_events import title_key
 title=title_key(str(event.get('title') or ''))
 return title in {title_key(v) for v in ('Star Trek: Deep Space Nine','The Middle','King of Queens','The King of Queens')}
