"""Owner-only Kodi GitHub read credentials. No upload or secret logging."""
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit

from epg_agent_github import DeliveryError, read_token

NAME = "reader-token.txt"
MAX_TOKEN_FILE_BYTES = 1024
_PATTERN = re.compile(r"(?:github_pat_|ghp_|ghu_|ghs_)[A-Za-z0-9_]*\Z")
_WIN_PATH = re.compile(r"^[A-Za-z]:[\\\\/]")
_ALLOWED_SCHEMES = {"smb", "nfs", "special"}


def store_token(directory, token):
    """Atomically store a user-supplied PAT in the local addon profile.

    The GitHub permissions cannot be verified from a token's syntax. Create a
    fine-grained read-only token scoped to the private EPG repository.
    """
    if not isinstance(token, str) or not 20 <= len(token) <= 400 or not _PATTERN.fullmatch(token):
        raise DeliveryError("AUTH_INVALID")
    root = Path(directory)
    if root.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    os.chmod(root, 0o700)
    fd, name = tempfile.mkstemp(prefix=".reader-token-", dir=str(root))
    try:
        with os.fdopen(fd, "wb") as out:
            os.fchmod(out.fileno(), 0o600)
            out.write(token.encode("ascii") + b"\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, root / NAME)
        return read_token(root / NAME) == token
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _safe_browse_path(value):
    """Only Kodi VFS local files, USB and configured SMB/NFS shares.

    Explicitly refuse web/FTP/plugin locations and embedded network credentials.
    No source path or token may appear in any exception or Kodi notification.
    """
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise DeliveryError("TOKEN_FILE_INVALID_PATH")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise DeliveryError("TOKEN_FILE_INVALID_PATH")
    if value.startswith(("/", "\\\\")) or _WIN_PATH.match(value):
        return value
    try:
        uri = urlsplit(value)
        if (uri.scheme.lower() not in _ALLOWED_SCHEMES or not uri.netloc
                or not uri.path or uri.username or uri.password
                or uri.query or uri.fragment):
            raise DeliveryError("TOKEN_FILE_INVALID_PATH")
    except ValueError:
        raise DeliveryError("TOKEN_FILE_INVALID_PATH") from None
    return value


def _parse_token_bytes(raw):
    """Accept one plain-text PAT or a minimal {"token": "..."} JSON file."""
    if not isinstance(raw, (bytes, bytearray)) or not raw or len(raw) > MAX_TOKEN_FILE_BYTES:
        raise DeliveryError("TOKEN_FILE_INVALID_CONTENT")
    try:
        value = bytes(raw).decode("utf-8-sig").strip()
        if value.startswith("{"):
            payload = json.loads(value)
            if not isinstance(payload, dict) or set(payload) != {"token"}:
                raise DeliveryError("TOKEN_FILE_INVALID_CONTENT")
            value = payload["token"]
    except (UnicodeError, ValueError, TypeError):
        raise DeliveryError("TOKEN_FILE_INVALID_CONTENT") from None
    if not isinstance(value, str) or not 20 <= len(value) <= 400 or not _PATTERN.fullmatch(value):
        raise DeliveryError("AUTH_INVALID")
    return value


def import_token_file(directory, selected_path, vfs_module=None):
    """Read max 1025 bytes through Kodi VFS; persist only validated PAT locally.

    Handles removable/internal storage, SMB and NFS sources selected in Kodi's
    file browser. The original file remains where it is; it is never uploaded,
    renamed, deleted, copied to GitHub or included in diagnostic output.
    """
    location = _safe_browse_path(selected_path)
    if vfs_module is None:
        import xbmcvfs as vfs_module
    source = None
    try:
        source = vfs_module.File(location, "rb")
        raw = source.readBytes(MAX_TOKEN_FILE_BYTES + 1)
    except Exception:
        raise DeliveryError("TOKEN_FILE_READ_FAILED") from None
    finally:
        if source is not None:
            try:
                source.close()
            except Exception:
                pass
    token = _parse_token_bytes(raw)
    return store_token(directory, token)


def clear_token(directory):
    """Remove local token only; revoke separately in GitHub."""
    root = Path(directory)
    if root.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    path = root / NAME
    if path.exists() or path.is_symlink():
        path.unlink()
