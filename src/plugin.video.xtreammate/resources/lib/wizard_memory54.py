"""RAM-only lifetime of the currently executing wizard interpreter.

No window property, file, service message, URL or log contains the secret.
A new Kodi/Python interpreter must request the missing password again.
"""
_session=None
_profile=None

def remember(session):
    global _session,_profile
    from wizard_resume53 import root
    _session=session;_profile=root()

def current():
    from wizard_resume53 import root
    if _profile==root() and _session is not None and _session.state.get('status')=='ACTIVE':return _session
    return None
