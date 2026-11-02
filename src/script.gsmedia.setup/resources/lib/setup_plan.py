"""Read-only GS Media setup plan, based on archived Kodi addon.xml manifests.

No Kodi APIs, filesystem mutations or network calls here. This is a *preview*
of direct and partially verified transitive dependencies, not an installer.
"""
from collections import OrderedDict

# Direct imports are taken from the 2026-10-21 Kodi backup manifests.
# Unknown manifests have deliberately NOT been filled in with guesses.
DEPENDENCIES = {
    "plugin.video.xtreammate": (("xbmc.python", "3.0.0"), ("script.module.pil", "5.1.0")),
    "skin.titan.bingie.mod": (
        ("xbmc.gui", "5.17.0"),
        ("script.bingie.helper", "1.1.2"),
        ("script.skinshortcuts", "2.1.0"),
        ("script.skin.helper.service", "1.30.0"),
        ("script.skin.helper.widgets", "1.30.0"),
        ("script.skin.helper.backgrounds", "1.0.36"),
        ("resource.images.skinbackgrounds.titanium", "1.0.0"),
        ("resource.images.skinicons.wide", "1.0.5"),
        ("resource.images.backgroundoverlays.basic", "1.0.0"),
        ("resource.images.studios.coloured", "0.0.23"),
        ("plugin.video.themoviedb.helper", "5.4.16"),
        ("plugin.program.autocompletion", "2.1.2"),
        ("plugin.video.youtube", "7.0.2.2"),
    ),
    "script.bingie.helper": (
        ("xbmc.python", "3.0.0"),
        ("script.module.simplejson", "3.17.0"),
    ),
    "script.skinshortcuts": (
        ("xbmc.python", "3.0.0"),
        ("script.module.unidecode", "0.4.14"),
        ("script.module.simpleeval", "0.9.10"),
    ),
    "plugin.video.themoviedb.helper": (
        ("xbmc.python", "3.0.1"),
        ("script.module.requests", "2.9.1"),
        ("script.module.pil", "1.1.7"),
        ("script.module.addon.signals", "0.0.6"),
        ("script.module.jurialmunkey", "0.2.2"),
        ("script.module.infotagger", "0.0.5"),
        ("script.module.beautifulsoup4", "4.9.3"),
    ),
    "script.module.jurialmunkey": (
        ("xbmc.python", "3.0.1"),
        ("script.module.requests", "2.9.1"),
        ("script.module.infotagger", "0.0.5"),
    ),
    "script.module.slyguy": (
        ("slyguy.dependencies", "0.0.30"),
        ("repository.slyguy", "0.0.9"),
    ),
    "slyguy.dependencies": (("repository.slyguy", ""),),
    "plugin.audio.shoutcast": (("xbmc.python", "3.0.0"), ("script.module.xbmcswift2", "19.0.0"), ("script.module.xmltodict", "0.12.0")),
    "plugin.audio.m3sr2019": (("xbmc.python", "3.0.0"), ("script.module.beautifulsoup4", "4.9.3"), ("script.module.requests", "2.9.1"), ("script.module.routing", "0.2.0")),
}
# The Kodi built-in requirements are verified by Kodi itself, not downloaded.
BUILTINS = frozenset(("xbmc.python", "xbmc.gui"))

# These are previews of intended modules. Membership does not imply the
# corresponding addon exists on every device or in GS Media 1.8 already.
PROFILES = (
    ("core", "Basis: XCMate + BINGIE", (
        "skin.titan.bingie.mod", "plugin.video.xtreammate",
    )),
    ("media", "Medien: Basis + xVAULT + Cumination", (
        "skin.titan.bingie.mod", "plugin.video.xtreammate",
        "plugin.video.xvault", "plugin.video.cumination",
    )),
    ("music", "Musik: Basis + MP3 Streams + SHOUTcast", (
        "skin.titan.bingie.mod", "plugin.video.xtreammate",
        "plugin.audio.m3sr2019", "plugin.audio.shoutcast",
    )),
    ("all", "Medien und Musik kombiniert", (
        "skin.titan.bingie.mod", "plugin.video.xtreammate",
        "plugin.video.xvault", "plugin.video.cumination",
        "plugin.audio.m3sr2019", "plugin.audio.shoutcast",
    )),
)


def profile_names():
    return tuple((key, title) for key, title, _ in PROFILES)


def _version_tuple(value):
    # Historic XML imports contain numeric minimum versions. This helper
    # never compares current installed versions; it only merges source minima.
    if not value:
        return ()
    return tuple(int(part) for part in value.split("."))


def plan_for(profile_id):
    """Return deduplicated preview rows (id, minimum, builtin, manifest_known).

    Unknown transitive dependencies are explicitly noted via manifest_known,
    rather than silently asserted to be absent.
    """
    matches = [roots for key, _title, roots in PROFILES if key == profile_id]
    if len(matches) != 1:
        raise ValueError("Unknown setup profile")
    result = OrderedDict()
    active = set()
    installed_order = []

    def include(addon_id, minimum=""):
        if not addon_id or "/" in addon_id or "\\" in addon_id:
            raise ValueError("Unexpected addon identifier")
        if addon_id not in result:
            result[addon_id] = minimum
        elif _version_tuple(minimum) > _version_tuple(result[addon_id]):
            result[addon_id] = minimum
        if addon_id in active:
            raise ValueError("Cyclic source dependency")
        if addon_id in expanded:
            return
        active.add(addon_id)
        for child, child_version in DEPENDENCIES.get(addon_id, ()):
            include(child, child_version)
        active.remove(addon_id)
        expanded.add(addon_id)
        installed_order.append(addon_id)

    expanded = set()
    for root in matches[0]:
        include(root)
    return tuple(
        {
            "addon_id": addon_id,
            "minimum": minimum,
            "builtin": addon_id in BUILTINS,
            "manifest_known": addon_id in DEPENDENCIES or addon_id in BUILTINS,
        }
        for addon_id in installed_order
        for minimum in (result[addon_id],)
    )
