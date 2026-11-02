# -*- coding: utf-8 -*-
"""GS Media Setup 0.2.0 — active, read-only device preflight.

The installation executor is intentionally NOT enabled until repositories,
source hashes, full dependencies and Kodi 21 ARM32 have been verified.
No automatic start; no profile, skin, repository or userdata modifications.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "resources" / "lib"))
from setup_plan import profile_names
from setup_inventory import snapshot
from setup_gate import inspect


def _device_label():
    try:
        import xbmc
        return (xbmc.getInfoLabel("System.BuildVersion") or "Kodi-Version nicht ermittelbar")[:80]
    except (ImportError, AttributeError, RuntimeError):
        return "Kodi-Version nicht ermittelbar"


def _report(key, title, inventory):
    result = inspect(key, inventory)
    lines = [
        "GS MEDIA SETUP 0.2.0 — SYSTEMPRÜFUNG",
        "=" * 46,
        "Kodi: " + _device_label(),
        "Installationsprofil: " + title,
        "Inventar: " + result["inventory"],
        "Bereits installierte Add-ons: " + str(len(inventory.get("addons", {})))
            if inventory.get("code") == "READY" else "Inventar derzeit nicht verfügbar",
        "",
        "INSTALLATION NOCH GESPERRT — REINE VORPRÜFUNG",
        "Installationsquellen und SHA256 müssen zuerst geprüft werden.",
        "Nichts wird installiert, deaktiviert, zurückgesetzt oder gelöscht.",
        "",
        "Abhängigkeiten in vorgesehener Reihenfolge:",
    ]
    for number, row in enumerate(result["rows"], 1):
        lines.append("{:02d}. {} ({})".format(number, row["addon_id"], row["state"]))
        lines.append("    Mindestversion (historisch): {} | Gerät: {}".format(
            row["minimum"] or "offen", row["actual_version"] or "unbekannt"))
        lines.append("    Quelle: " + row["source"])
        if row["install_blocked"] or not row["manifest_known"]:
            lines.append("    PRÜFUNG NÖTIG: " + row["note"])
    lines += [
        "",
        "Noch nicht freigegebene Installationsschritte: " + str(result["blocking"]),
        "Nächste Phase: verifizierte Pakete, Benutzerfreigabe,",
        "Kodi-Installation und Fortsetzen nach einem Neustart.",
        "Diese Funktionen sind in 0.2.0 noch NICHT implementiert.",
        "",
        "Referenz: GitHub issue #317 / GS Media.",
    ]
    return "\n".join(lines)


def run():
    try:
        import xbmcgui
    except ImportError:
        raise RuntimeError("GS Media Setup ist nur innerhalb von Kodi ausführbar")
    dialog = xbmcgui.Dialog()
    profiles = profile_names()
    while True:
        choice = dialog.select("GS Media Setup 0.2.0 – Entwicklung", [
            "Installationsprofil und Abhängigkeiten prüfen",
            "Aktuelle Kodi-Add-ons inventarisieren",
            "Sicherheits- und Entwicklungsstatus",
            "Beenden",
        ])
        if choice in (-1, 3):
            return
        if choice == 2:
            dialog.ok("GS Media Setup 0.2.0", "Aktive Vorprüfung ohne Installation. "
                      "Neue Kodi-Box und bestehende Profile bleiben unverändert. "
                      "Fehlende oder ungeprüfte Paketquellen blockieren spätere Installationsschritte.")
            continue
        inventory = snapshot()
        if choice == 1:
            lines = ["Geräte-Inventur: " + inventory["code"],
                     "Kodi: " + _device_label(),
                     "Installierte Add-ons: " + str(len(inventory.get("addons", {}))), ""]
            if inventory["code"] == "READY":
                for addon_id, item in sorted(inventory["addons"].items()):
                    lines.append("{}  {}  {}".format(addon_id, item["version"],
                                  "aktiv" if item["enabled"] is True else
                                  "deaktiviert" if item["enabled"] is False else "Status unbekannt"))
            else:
                lines.append("Kodi JSON-RPC nicht verfügbar: Keine fehlenden Add-ons unterstellen.")
            dialog.textviewer("GS Media – Lokale Inventur", "\n".join(lines), usemono=True)
            continue
        selected = dialog.select("GS Media – Profil wählen", [title for _key, title in profiles])
        if selected < 0:
            continue
        key, title = profiles[selected]
        dialog.textviewer("GS Media – " + title, _report(key, title, inventory), usemono=True)


if __name__ == "__main__":
    run()
