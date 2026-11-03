# -*- coding: utf-8 -*-
"""GS Media Setup Wizard – read-only developer preview for Kodi 21+.

Does NOT install or uninstall add-ons; does NOT alter Kodi userdata, skin,
service enablement, repositories or update settings. No automatic startup.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "resources" / "lib"))
from setup_plan import BUILTINS, plan_for, profile_names  # noqa: E402


def _installed_status(addon_id):
    """Report readable local metadata without mutating add-on state."""
    if addon_id in BUILTINS:
        return "Kodi-Systemkomponente"
    try:
        import xbmcaddon
        addon = xbmcaddon.Addon(addon_id)
        version = addon.getAddonInfo("version") or "Version unbekannt"
        return "Erreichbar: " + version
    except Exception:
        # Kodi Addon(id) cannot distinguish absent from disabled reliably.
        return "Nicht abfragbar (fehlt oder ist deaktiviert)"


def _plan_text(profile_id, profile_label):
    rows = plan_for(profile_id)
    lines = [
        "GS MEDIA SETUP – NUR VORSCHAU",
        "=" * 38,
        "Profil: " + profile_label,
        "",
        "ES WIRD NICHTS INSTALLIERT, GELÖSCHT ODER GEÄNDERT.",
        "Die Mindestversionen stammen aus historischen Kodi-21-Manifesten",
        "des alten Backups, nicht aus einer aktuellen Online-Prüfung.",
        "Unbekannte transitive Abhängigkeiten werden nicht erfunden.",
        "",
    ]
    for index, row in enumerate(rows, 1):
        addon_id = row["addon_id"]
        min_version = row["minimum"] or "nicht festgelegt"
        status = _installed_status(addon_id)
        lines.append("{:02d}. {}".format(index, addon_id))
        lines.append("    Minimum: {} | {}".format(min_version, status))
        if not row["manifest_known"]:
            lines.append("    (!) Weitere Abhängigkeiten noch zu prüfen")
    lines.extend([
        "",
        "Die Kodi-Installationsquelle und Verfügbarkeit wurden nicht geprüft.",
        "Dieses Paket unterstützt noch KEINEN automatischen Installer.",
        "Bestehende Kodi-Profile, EPG- und TMDB-Daten bleiben unangetastet.",
    ])
    return "\n".join(lines)


def run():
    try:
        import xbmcgui
    except ImportError:
        raise RuntimeError("GS Media Setup muss in Kodi gestartet werden")
    dialog = xbmcgui.Dialog()
    profiles = profile_names()
    while True:
        choice = dialog.select(
            "GS Media Setup – sicherer Entwurf",
            ["Installationsprofile ansehen", "Installierte Add-ons prüfen",
             "Sicherheit und Versionsstand", "Beenden"],
        )
        if choice in (-1, 3):
            return
        if choice in (0, 1):
            selected = dialog.select(
                "Gewünschtes Paket", [label for _key, label in profiles],
            )
            if selected < 0:
                continue
            key, title = profiles[selected]
            dialog.textviewer(
                "GS Media – " + title, _plan_text(key, title),
                usemono=True,
            )
        elif choice == 2:
            dialog.ok(
                "GS Media Setup 0.1.0 – Vorschau",
                "Sicherer Test-Entwurf für Kodi 21. "
                "Kein Autostart, keine Installation, keine Löschung, "
                "kein Profilreset. Geplante Installation erst nach "
                "separater Freigabe und Android-Abnahme.",
            )


if __name__ == "__main__":
    run()
