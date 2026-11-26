"""Provision the packaged read credential in Kodi userdata and recover stale copies."""
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

    Preserve an existing local copy until an authenticated read verifies its
    replacement. An older installation may have no packaged credential.
    """
    root = Path(directory)
    destination = root / LOCAL_NAME
    if root.is_symlink() or destination.is_symlink():
        raise DeliveryError("AUTH_STORE_UNSAFE")
    if destination.is_file():
        return destination
    source = bundled_path() if bundled is None else Path(bundled)
    if source.is_symlink():
        raise DeliveryError("AUTH_BUNDLE_UNSAFE")
    if not source.is_file():
        return destination

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

    return _install(destination, value)


def _install(destination, value, *, replace=False):
    root = destination.parent
    if root.is_symlink() or destination.is_symlink():
        raise DeliveryError("AUTH_STORE_UNSAFE")
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
        if replace or not destination.exists():
            os.replace(tmp, destination)
        return destination
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def fetch_with_recovery(fetch, directory, local, **options):
    """Retry a rejected local credential once with a distinct packaged token."""
    recoverable = {"PRIVATE_ENDPOINT_ACCESS_DENIED", "AUTH_INVALID", "AUTH_NOT_PROVISIONED"}
    try:
        return fetch(directory, local, **options)
    except DeliveryError as failure:
        if failure.code not in recoverable:
            raise
        bundle = bundled_path()
        try:
            replacement = read_token(bundle)
        except DeliveryError:
            raise failure from None
        try:
            original = read_token(local)
        except DeliveryError:
            original = None
        if replacement == original:
            raise
        options["etag"] = ""
        result = fetch(directory, bundle, **options)
        if result.get("status") in {"STAGED_FULL_CANDIDATE", "UNCHANGED", "PRIVATE_PENDING"}:
            destination = Path(local)
            from profile_transaction import writing
            with writing(timeout=.2):
                try:
                    current = read_token(destination)
                except DeliveryError:
                    current = None
                if current == original:
                    _install(destination, replacement, replace=True)
        return result
