"""Re-read the current exit latch before committing a return decision.

Two service/interpreter polls may overlap an already committed Home request.
A stale poll must not overwrite that request as RETURN_BLOCKED. No Stop, window
close, forced modal release or native decoder change is performed here.
"""


def guard(value):
    from live_exit import state
    from playback_exit import _same
    current=state()
    if not current or not _same(('live',value['session']),('live',current['session'])):
        return 'STALE_SESSION',None
    if current['phase']=='complete':
        return 'ALREADY_COMMITTED',current
    if current['phase']!='home':
        return 'PHASE_CHANGED',current
    return 'READY',current
