"""One FIFO progress probe after a missing stop receipt. Never repost Stop.

A matching probe on Kodi's main queue proves that the previously enqueued
Stop returned even if the original property was lost. A blocked queue never
gets a fabricated ACK, player query, retry, forced window change or success.
"""
import re,time,uuid
ACK='XCMate.StopQueueProgress93'

def returned(value):
    import xbmcgui
    nonce=value.get('progress_nonce93','')
    return bool(value.get('commands_enqueued93') and value.get('progress_posted93')
                and re.fullmatch('[a-f0-9]{32}',nonce)
                and xbmcgui.Window(10000).getProperty(ACK)==nonce)

def observe(value):
    if (value['token'][0]!='live' or not value.get('native_posted') or value.get('worker_done')
            or not value.get('commands_enqueued93') or value.get('progress_posted93')
            or time.monotonic()-value.get('posted_at75',time.monotonic())<5):return
    import xbmc,xbmcgui
    from exit_jobs import save,trace
    nonce=uuid.uuid4().hex
    value.update(progress_nonce93=nonce,progress_posted93=True)
    xbmcgui.Window(10000).clearProperty(ACK);save(value)
    # Fixed command and generated nonce only, after both original API posts
    # have returned. Shares the exact FIFO of the one existing Stop command.
    xbmc.executebuiltin('SetProperty('+ACK+','+nonce+',home)',wait=False)
    trace('QUEUE_PROGRESS_PROBE_POSTED',tuple(value['token']))
