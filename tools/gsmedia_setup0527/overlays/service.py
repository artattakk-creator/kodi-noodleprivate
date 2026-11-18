"""Read back setup after restart and recover Kodi's temporary source policy."""
from pathlib import Path
import sys

import xbmc

sys.path.insert(0, str(Path(__file__).resolve().parent / "resources/lib"))


def main():
    from setup_auto_ui50 import ERRORS, _context, exclusive
    from setup_compat27 import current_platform
    from setup_finish27 import postboot, read_marker
    from setup_inventory import snapshot
    from setup_origin_guard52 import restore

    if not current_platform(xbmc):
        return
    monitor = xbmc.Monitor()
    if monitor.waitForAbort(12):
        return
    profile = _context()
    try:
        # Do not contend with an active or very recently started installer.
        if not Path(profile).is_dir():
            return
        with exclusive(profile):
            restore(profile, xbmc.executeJSONRPC)
            record = read_marker(profile)
            if record:
                postboot(xbmc, monitor, profile, snapshot, record)
    except ERRORS as error:
        xbmc.log("GS Media 0.5.27: postboot " + type(error).__name__, xbmc.LOGWARNING)


if __name__ == "__main__":
    main()
