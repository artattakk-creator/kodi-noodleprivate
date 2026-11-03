# GS Media native BINGIE-Shortcuts dependency bridge (Test only)

This very small first-party Kodi script is intentionally nonfunctional at
runtime. Its `addon.xml` declares `script.skinshortcuts` >= 2.1.0, which
the original BINGIE MOD 2.2.3 requires. Kodi Omega's AddonInstaller
can install an *out-of-date dependency* from the same repository as its
parent add-on. The bridge is installed from `repository.gsmedia.pilot`
instead of incorrectly calling `InstallAddon(script.skinshortcuts)`,
which does not upgrade an already installed add-on.

The upstream GPL-2.0-only Skin Shortcuts 2.1.0 package remains byte-identical
to AchillesPunks and is separately distributed in the pilot catalog with
full attribution. The bridge itself is MIT-licensed GS Media source.

Kodi Omega first prefers the official 2.0.3 even when our pilot is the parent.
The wizard therefore temporarily and explicitly switches official add-on
updates to ANY_REPOSITORY **during this one native dependency transaction**, then
restores original values using an atomic recovery journal. No permanent
Kodi settings changes, Addons.db modifications, direct ZIP
extraction into the Kodi add-ons folder, or silent modification of user data.
Kodi prompts for installation. If the native dependency resolution fails,
the setup must stop with a useful error and preserve all prior installations.
