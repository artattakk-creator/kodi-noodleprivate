"""Host-only isolated authenticated SMB2 server; never packaged in the add-on."""
import json,logging,sys
from impacket.smbserver import SimpleSMBServer,SMBSERVER
from impacket.ntlm import compute_lmhash,compute_nthash

logging.disable(logging.CRITICAL)
SMBSERVER.allow_reuse_address=True
server=SimpleSMBServer(listenAddress='127.0.0.1',listenPort=int(sys.argv[2]) if len(sys.argv)>2 else 0)
server.addShare('MEDIA',sys.argv[1]);server.setSMB2Support(True)
server.addCredential('fixture',0,compute_lmhash('fixture-password'),compute_nthash('fixture-password'))
print(json.dumps(dict(port=server.getServer().server_address[1])),flush=True)
server.start()
