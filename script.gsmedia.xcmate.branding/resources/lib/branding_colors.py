# -*- coding: utf-8 -*-
"""Verified Space Blue palette for Titan BINGIE MOD 2.2.3.

Only presentation values. Do not change focus/container geometry, skinshortcuts,
provider data, EPG, widget routes or content-artwork tinting.
"""
import re

DEEP = "FF061322"
NAVY = "FF0A2947"
NAVY_PANEL = "E6061322"
SURFACE = "DD0A2947"
BLUE = "FF159FEA"
CYAN = "FF42D9FF"
ICE = "FFE6F5FF"
MUTED = "FF88A6BE"
LOW = "AA88A6BE"
SOFT = "AA0A2947"
DARK_TEXT = "FF061322"

# Kodi Skin.String keys used by BINGIE's own color settings.
# Status/MPAA/parental classifications are intentionally *not* recolored.
PALETTE = {
    "SpinnerTexture.Color": CYAN,
    "WidgetSpinnerTexture.Color": CYAN,
    "HomeWidgetsBorderColor": CYAN,
    "LineUnderMenuIconsColor": BLUE,
    "HeaderTextColor": ICE,
    "ViewDetailsTextColor": ICE,
    "ViewDetailsHighlightTextColor": CYAN,
    "ViewDetailsListItemTextColor": ICE,
    "ViewDetailsListItemTextFocusColor": ICE,
    "ViewDetailsFocusColor": NAVY,
    "ViewDetailsBorderFocusColor": CYAN,
    "ButtonFocusColor": CYAN,
    "GeneralPanelsColor": NAVY_PANEL,
    "FooterTextColor": ICE,
    "ButtonTextColor": ICE,
    "ButtonFocusTextColor": DARK_TEXT,
    "GeneralTextColor": ICE,
    "GeneralHighlightTextColor": CYAN,
    "BingiePrimaryTextColor": ICE,
    "BingieSecondaryTextColor": MUTED,
    "MainMenuButtonColor": LOW,
    "MainMenuFocusButtonColor": CYAN,
    "BingieDetailsFlagColor": NAVY,
    "BingieDetailsFlagTextColor": ICE,
    "BingieNewEpisodesTagColor": BLUE,
    "BingieTop250IconColor": CYAN,
    "BingieAdditionalInfoIconsColor": CYAN,
    "BingieAdditionalInfoTextColor": ICE,
    "BingieLabelTextColor": ICE,
    "BingieSubLabelTextColor": MUTED,
    "FooterPanelColor": NAVY_PANEL,
    "ViewDetailsPanelColor": DEEP,
    "OSDPanelColor": NAVY_PANEL,
    "ButtonColor": NAVY,
    "OSDPrimaryTextColor": ICE,
    "OSDSecondaryTextColor": MUTED,
    "OSDProgressBarColor": BLUE,
    "OSDProgressBarBackgroundColor": SOFT,
    "OSDProgressBarCacheColor": "80159FEA",
    "OSDProgressBarBorderColor": NAVY,
    "OSDButtonsFocusColor": CYAN,
    "OSDButtonsColor": MUTED,
    "OSDBingieButtonsFocusColor": CYAN,
    "OSDBingieButtonsColor": MUTED,
    "OSDVolumeButtonColor": BLUE,
    "OSDBufferingSpinnerColor": CYAN,
    "BingieOSDProgressBarBackgroundColor": SOFT,
    "BingieOSDProgressBarColor": BLUE,
    "BingieOSDProgressBarCacheColor": "80159FEA",
    "BingieOSDProgressTextColor": ICE,
    "BingieOSDHeaderTextColor": ICE,
    "BingieOSDPlotTextColor": MUTED,
    "BingieOSDSubLabelTextColor": ICE,
    "BingieOSDLabelTextColor": ICE,
    "BingieOSDDeatailsTextColor": MUTED,
    "ScrollbarBackgroundColor": DEEP,
    "ScrollbarUnfocusedColor": MUTED,
    "ScrollbarFocusedColor": CYAN,
    "BingiePlotTextColor": MUTED,
    "BingieDeatailsTextColor": MUTED,
    "BingieHeaderTextColor": ICE,
    "BingieSpotlightPlotTextColor": ICE,
    "BingieDialogAdditionalInfoTextColor": MUTED,
    "BingieDialogAdditionalInfoIconColor": CYAN,
    "BingieButtonFocusTextColor": ICE,
    "BingieButtonTextColor": MUTED,
    "BingieSecondaryButtonFocusTextColor": DARK_TEXT,
    "BingieSecondaryButtonTextColor": ICE,
    "BingieProgressBarColor": BLUE,
    "BingieProgressBarBackgroundColor": NAVY,
    "BingieHomeProgressBarColor": BLUE,
    "BingieHomeProgressBarBackgroundColor": NAVY,
    "BingieHomeProgressBarTextColor": ICE,
    "WatchedIndicator.Watched.Color": BLUE,
    "WatchedIndicator.UnWatched.Color": "AA159FEA",
    "WatchedIndicator.Progress.Color": BLUE,
    "WatchedIndicator.Episodes.Color": BLUE,
    "SideBladePanelColor": NAVY_PANEL,
    "TagOverlaysPanelColor": NAVY_PANEL,
    "TagOverlaysTextColor": ICE,
    "LyricsOverlayColor": NAVY_PANEL,
    "LyricsTextColor": ICE,
    "LyricsFocusTextColor": CYAN,
    "MainMenuTextColor": MUTED,
    "MainMenuFocusTextColor": ICE,
    "HeaderPanelColor": NAVY_PANEL,
    "ActiveSpinControlColor": CYAN,
    "PanelBorderColor": BLUE,
}

DEFAULT_COLORS = {
    "black": DEEP, "blue": BLUE, "darkblue": DEEP,
    "selected": BLUE, "mainblue": BLUE, "ccmainblue": "CC159FEA",
    "list_label_1_fo": "CC42D9FF", "list_label_1_select": "CC42D9FF",
    "list_label_2_first": "77159FEA", "panel_color": NAVY,
    "grey2": MUTED, "grey3": NAVY,
    "grey": MUTED, "lightgrey": MUTED, "midgrey": "FF627F97",
    "bluegrey": ICE, "darkgrey": NAVY, "darkgrey2": "FF214567",
}

def edit_defaults(data):
    """Return bytewise exact reversible operations for the named color entries."""
    from branding_patch import BrandingError
    if len(data) > 128 * 1024:
        raise BrandingError("BINGIE-Farbdatei ungewöhnlich groß.")
    result = data
    changes = []
    for name, color in DEFAULT_COLORS.items():
        expr = re.compile(rb'(<color\s+name="' + name.encode("ascii") +
                          rb'">)([^<]*)(</color>)', re.I)
        matches = list(expr.finditer(result))
        if len(matches) != 1:
            raise BrandingError("BINGIE-Farbwert fehlt oder mehrfach: " + name)
        old = matches[0].group(0)
        new = matches[0].group(1) + color.encode("ascii") + matches[0].group(3)
        if old == new:
            continue
        result = result.replace(old, new, 1)
        changes.append(dict(old=old.decode("ascii"), new=new.decode("ascii"), count=1))
    return result, changes

_ALLOWED = re.compile(r"^[A-Za-z0-9# ._+-]{0,80}$")
def safe_skin_value(value):
    """Prevent Kodi builtin argument injection on restoring user settings."""
    return isinstance(value, str) and bool(_ALLOWED.fullmatch(value))

def names_for_settings():
    """Colorpicker display names are updated too, so the UI has no stale 'Red'."""
    out = {}
    for key, value in PALETTE.items():
        out[key] = value
        out[key + ".name"] = "XCMate Space Blue"
    return out
