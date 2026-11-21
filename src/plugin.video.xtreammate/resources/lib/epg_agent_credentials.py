"""Owner-entered Kodi GitHub read token; never log, publish, or embed it."""
import os
from pathlib import Path
import re
import tempfile

from epg_agent_github import DeliveryError, read_token

NAME = "reader-token.txt"
_PATTERN = re.compile(r"(?:github_pat_|ghp_|ghu_|ghs_)[A-Za-z0-9_]*\\Z")


def store_token(directory, token):
    """Atomically store one strictly read-only *intended* PAT in the local profile.

    Permissions on the token itself cannot be verified locally; the owner must
    create a fine-grained token scoped to the private output repository with
    Contents: Read-only and a short expiry in GitHub.
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
            out.write(token.encode("ascii") + b"\\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, root / NAME)
        return read_token(root / NAME) == token
    finally:
        if os.path.exists(name):
            os.unlink(name)


def clear_token(directory):
    """Remove local token only; revoke in GitHub separately."""
    root = Path(directory)
    if root.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    path = root / NAME
    if path.exists() or path.is_symlink():
        path.unlink()
