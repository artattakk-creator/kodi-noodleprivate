"""Host-only isolated authenticated SMB2 server; never packaged in the add-on."""
import json,logging,sys,threading
from impacket import smb3structs as smb2
from impacket.smbserver import SimpleSMBServer,SMBSERVER
from impacket.ntlm import compute_lmhash,compute_nthash

logging.disable(logging.CRITICAL)
SMBSERVER.allow_reuse_address=True
server=SimpleSMBServer(listenAddress='127.0.0.1',listenPort=int(sys.argv[2]) if len(sys.argv)>2 else 0)
server.addShare('MEDIA',sys.argv[1]);server.setSMB2Support(True)
server.addCredential('fixture',0,compute_lmhash('fixture-password'),compute_nthash('fixture-password'))
# Impacket 0.13.0 implements FILE_CREATE with exists() followed by O_CREAT,
# without O_EXCL. Concurrent requests can both succeed, unlike SMB FILE_CREATE.
# Serialize only this host server's CREATE handlers to model atomic server-side
# disposition; the real signed wire/client and collision assertions stay intact.
# This never patches the add-on or the host filesystem functions.
_create_guard=threading.Lock()
def atomic_create(*args):
    with _create_guard:return _original_create(*args)
_original_create=server.getServer().hookSmb2Command(smb2.SMB2_CREATE,atomic_create)
assert _original_create is not None
print(json.dumps(dict(port=server.getServer().server_address[1])),flush=True)
server.start()
