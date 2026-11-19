"""Worker-only import gate, independent of the last backup GUI status."""
def access(filename):
    from epg_gate95 import inspect
    from ui_jobs86 import cancelled
    try:
        import xbmc
        monitor=xbmc.Monitor()
        abort=getattr(monitor,'abortRequested',lambda:False)
    except (ImportError,AttributeError):abort=lambda:False
    code=inspect(filename,cancel=lambda:cancelled() or abort())['code']
    return 'READY' if code=='IMPORT_AUTHORIZED' else code
