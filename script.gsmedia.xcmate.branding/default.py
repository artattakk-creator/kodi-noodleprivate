# -*- coding: utf-8 -*-
"""User-initiated BINGIE branding management; NEVER applies at add-on install time."""
import os
import sys
from pathlib import Path

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "resources", "lib"))
from branding_patch import BrandingError, apply, restore, status, supported, preview
from branding_colors import safe_skin_value

ADDON = xbmcaddon.Addon()
DIALOG = xbmcgui.Dialog()
SKIN_ID = "skin.titan.bingie.mod"


def notice(message):
    DIALOG.notification("XCMate Branding", message, xbmcgui.NOTIFICATION_INFO, 6500)


def get_paths():
    try:
        skin = xbmcaddon.Addon(id=SKIN_ID)
        raw = skin.getAddonInfo("path")
    except Exception as exc:
        raise BrandingError("BINGIE MOD ist nicht installiert: {}".format(exc))
    skin_dir = Path(xbmcvfs.translatePath(raw))
    addon_dir = Path(xbmcvfs.translatePath(ADDON.getAddonInfo("path")))
    userdata = Path(xbmcvfs.translatePath(ADDON.getAddonInfo("profile")))
    return skin_dir, addon_dir, userdata


def read_color(key):
    return xbmc.getInfoLabel('Skin.String({})'.format(key)).strip()


def write_color(key, value):
    if not safe_skin_value(value):
        raise BrandingError('Nicht darstellbarer BINGIE-Farbwert für: ' + key)
    if value:
        xbmc.executebuiltin('Skin.SetString({},{})'.format(key, value))
    else:
        xbmc.executebuiltin('Skin.Reset({})'.format(key))


def run():
    try:
        skin_dir, addon_dir, userdata = get_paths()
        if xbmc.getSkinDir() != SKIN_ID:
            raise BrandingError('Bitte zunächst Titan BINGIE MOD als aktiven Skin auswählen.')
        current = status(skin_dir, userdata, read_color)
        mode = xbmc.getInfoLabel("Skin.String(splash_screen)").strip() or "netflix_default"
        opts = ["Status / Vorschau", "Space Blue + Intro installieren", "Originalfarben, Logo & Intro wiederherstellen", "Beenden"]
        chosen = DIALOG.select("XCMate BINGIE Space Blue Manager", opts)
        if chosen in (-1, 3):
            return
        if chosen == 0:
            DIALOG.textviewer("XCMate Branding – Status", preview(skin_dir, addon_dir, userdata, mode, read_color))
            return
        if xbmc.getCondVisibility("Player.HasMedia"):
            raise BrandingError("Bitte zuerst die aktuelle Wiedergabe beenden.")
        if chosen == 1:
            if current.get("state") not in ("not_installed",):
                raise BrandingError("Backup/Patch bereits vorhanden: zuerst Status prüfen oder wiederherstellen.")
            if not supported(skin_dir):
                raise BrandingError("Nur für verifiziertes BINGIE MOD 2.2.3. Keine Skin-Dateien verändert.")
            if mode == "none":
                raise BrandingError("Das Skin-Intro ist deaktiviert. Bitte im Skin ein Intro aktivieren.")
            if mode not in ("netflix_default", "netflix_alternative", "netflix_extended"):
                raise BrandingError("Unbekannter Skin-Intro-Modus: " + mode)
            DIALOG.textviewer("Geplante Änderung (nur Branding)", preview(skin_dir, addon_dir, userdata, mode, read_color))
            if not DIALOG.yesno("XCMate Branding", "Intro, Splash, Logo UND komplettes Space-Blue-Farbschema installieren?\nOriginale und Farbwerte werden vorher gesichert. Widgets und Fokuslogik bleiben unberührt.\nKodi danach neu starten."):
                return
            summary = apply(skin_dir, addon_dir, userdata, mode, read_color, write_color)
            DIALOG.ok("XCMate Space Blue installiert", "Geänderte Dateien: {}\nOriginale unter Add-on-Daten gesichert.\nKodi jetzt vollständig beenden und neu starten.".format(summary["files"]))
        if chosen == 2:
            if current.get("state") == "not_installed":
                notice("Kein Branding-Backup vorhanden.")
                return
            if not DIALOG.yesno("Originalfarben, Logo & Intro wiederherstellen", "Gesicherte Dateien wiederherstellen?\nSpäter geänderte Dateien werden geschützt.\nBei Konflikten wird der Rückbau sicher abgebrochen."):
                return
            result = restore(skin_dir, userdata, read_color, write_color)
            DIALOG.ok("Wiederherstellung", "{} Dateien zurückgesetzt.\nKodi vollständig neu starten.".format(result["files"]))
    except BrandingError as exc:
        DIALOG.ok("XCMate Branding – Schutzabbruch", str(exc))
    except (OSError, ValueError, RuntimeError) as exc:
        xbmc.log("[XCMate Branding] Abbruch: {}".format(type(exc).__name__), xbmc.LOGERROR)
        DIALOG.ok("XCMate Branding", "Sicherheitsabbruch: {}.\nOriginaldateien gegebenenfalls über Wiederherstellen zurücksetzen.".format(type(exc).__name__))


if __name__ == "__main__":
    run()
