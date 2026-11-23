"""Install-once private EPG read token for public token-free Kodi updates.

The token may ship in an owner-only pilot ZIP under resources/private.  A
successful initial installation writes it to userdata/addon_data, which Kodi
preserves during regular add-on upgrades. Public catalog ZIPs must NEVER
contain the bundled credential; the normal reader only consumes its local copy.
"""
import os
from pathlib import Path
import tempfile

from epg_agent_github import DeliveryError, read_token

BUNDLED_NAME = "xcmate_epg_read_token.txt"
LOCAL_NAME = "reader-token.txt"


def bundled_path():
    return Path(__file__).resolve().parent.parent / "private" / BUNDLED_NAME


def ensure_local_token(directory, bundled=None):
    """Return the active local token path, never the token content.

    When no local token exists, provision once from the private owner ZIP.
    Existing tokens are preserved across reinstall/update, even when the newer
    ZIP includes a different token. Deleting/revoking is an explicit operation.
    """
    root = Path(directory)
    destination = root / LOCAL_NAME
    if destination.is_symlink():
        raise DeliveryError("AUTH_STORE_UNSAFE")
    if destination.is_file():
        return destination
    source = bundled_path() if bundled is None else Path(bundled)
    if source.is_symlink():
        raise DeliveryError("AUTH_BUNDLE_UNSAFE")
    if not source.is_file():
        return destination  # No bundled token in regular, publicly served ZIPs.

    # Validate the credential without displaying, returning or logging it.
    value = read_token(source)
    if root.is_symlink():
        raise DeliveryError("AUTH_STORE_UNSAFE")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink():
        raise DeliveryError("AUTH_STORE_UNSAFE")
    try:
        os.chmod(root, 0o700)
    except OSError:
        # Some Kodi profiles use a platform-specific filesystem, where chmod
        # is unavailable. The profile is still inside Kodi's app-owned data.
        pass
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink():
            raise DeliveryError("AUTH_STORE_UNSAFE")
        return destination

    fd, tmp = tempfile.mkstemp(prefix=".epg-reader-", dir=str(root))
    try:
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            try:
                os.fchmod(stream.fileno(), 0o600)
            except (AttributeError, OSError):
                pass
            stream.write(value + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if destination.exists() or destination.is_symlink():
            if destination.is_symlink():
                raise DeliveryError("AUTH_STORE_UNSAFE")
        else:
            os.replace(tmp, destination)
        return destination
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
