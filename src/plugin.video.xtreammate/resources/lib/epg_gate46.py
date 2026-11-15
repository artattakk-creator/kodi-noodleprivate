"""Worker-only import gate, independent of the last backup GUI status."""
def access(filename):
    from epg_gate95 import inspect
    code=inspect(filename)['code']
    return 'READY' if code=='IMPORT_AUTHORIZED' else code
