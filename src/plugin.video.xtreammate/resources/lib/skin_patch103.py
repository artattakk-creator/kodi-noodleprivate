"""Native approval and non-sensitive diagnostics for BINGIE skin plans."""

import errno
from contextlib import contextmanager
from pathlib import Path
from xml.etree.ElementTree import ParseError

from localization import tr

CODES = {
    'PROFILE_PATH_UNAVAILABLE', 'SKIN_PATH_UNAVAILABLE', 'PATCH_LOCK_UNAVAILABLE',
    'SKIN_MIGRATION_BLOCKED', 'WIDGET_INVENTORY_CHANGED', 'HOME103_GEOMETRY_UNVERIFIED',
    'PATCH_PERMISSION_DENIED', 'PATCH_READ_ONLY', 'PATCH_FILE_MISSING',
    'PATCH_STORAGE_FULL', 'PATCH_IO_FAILED', 'PATCH_INVALID_XML', 'PATCH_VALIDATION_FAILED',
}
STAGES = {'runtime', 'profile', 'layout', 'inventory', 'journal', 'target', 'preview', 'restore', 'reload'}
OUTCOMES = {'ROLLED_BACK', 'INTERRUPTED'}
IO_CODES = {
    errno.EACCES: 'PATCH_PERMISSION_DENIED',
    errno.EPERM: 'PATCH_PERMISSION_DENIED',
    errno.EROFS: 'PATCH_READ_ONLY',
    errno.ENOENT: 'PATCH_FILE_MISSING',
    errno.ENOSPC: 'PATCH_STORAGE_FULL',
}


class PatchError(ValueError):
    pass


class PatchIOError(OSError):
    pass


def code(exc):
    from widget_manager50 import ERRORS

    if str(exc) in CODES | ERRORS:
        return str(exc)
    if isinstance(exc, OSError):
        return IO_CODES.get(exc.errno, 'PATCH_IO_FAILED')
    if isinstance(exc, ParseError):
        return 'PATCH_INVALID_XML'
    return 'PATCH_VALIDATION_FAILED'


@contextmanager
def phase(stage):
    try:
        yield
    except (PatchError, PatchIOError):
        raise
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, ParseError) as exc:
        reason = code(exc)
        failure = (PatchIOError if isinstance(exc, OSError) else PatchError)(reason)
        failure.stage = stage
        raise failure from None


def local_dir(value, failure):
    import xbmcvfs

    if not value:
        raise ValueError(failure)
    path = Path(xbmcvfs.translatePath(value))
    if not path.is_absolute() or not path.is_dir():
        raise ValueError(failure)
    return path.resolve(strict=True)


def active_profile():
    return local_dir('special://profile/', 'PROFILE_PATH_UNAVAILABLE')


def diagnostics(exc, stage):
    reason = code(exc)
    stage = getattr(exc, 'stage', stage)
    journal = getattr(exc, 'journal', '')
    fields = ['code=' + reason, 'stage=' + (stage if stage in STAGES else 'runtime')]
    if journal in OUTCOMES:
        fields.append('journal=' + journal)
    return ' '.join(fields)


def log_error(exc, stage):
    import xbmc

    details = diagnostics(exc, stage)
    try:
        xbmc.log('[XCMate][BINGIE-PATCH] ' + details, getattr(xbmc, 'LOGWARNING', 2))
    except (AttributeError, RuntimeError):
        pass
    return details


def show_error(dialog, exc, stage):
    reason = code(exc)
    message_id = {
        'WIDGET_INVENTORY_CHANGED': 39375,
        'PATCH_PERMISSION_DENIED': 39376,
        'PATCH_READ_ONLY': 39376,
        'PROFILE_PATH_UNAVAILABLE': 39377,
        'SKIN_PATH_UNAVAILABLE': 39377,
    }.get(reason, 39374)
    if getattr(exc, 'stage', stage) == 'reload':
        message_id = 39378
    dialog.ok(tr(36669), tr(message_id) + '\n\n' + log_error(exc, stage))


def confirm(dialog, plan):
    from widget_skin50 import FILES
    from widget_skin78 import FILES as GRAPH

    entries = plan['entries']
    names = GRAPH if len(entries) == len(GRAPH) else FILES + ('xml/IncludesBingie.xml',)
    while True:
        choice = dialog.yesnocustom(
            tr(36669), tr(39370), customlabel=tr(39372), nolabel=tr(36426), yeslabel=tr(39371)
        )
        if choice != 2:
            return choice == 1
        changes = '\n\n'.join(
            name + '\n' + entry['before'] + '\n→ ' + entry['after']
            for name, entry in zip(names, entries) if entry['before'] != entry['after']
        )
        dialog.textviewer(tr(39372), tr(39373, len(entries)) + '\n\n' + changes)
