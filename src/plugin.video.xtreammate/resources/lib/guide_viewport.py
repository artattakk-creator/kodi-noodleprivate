"""Worker viewport over the shared published local guide, never network."""
def cache(pid,channels,mappings,now,focus_sid=''):
    from local_epg import window
    return window(pid,channels,mappings,now,now+2*86400,focus_sid=focus_sid,history=True,budget=.5)
