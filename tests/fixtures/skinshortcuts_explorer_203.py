# Copyright (C) 2013-2021 Skin Shortcuts (script.skinshortcuts)
# SPDX-License-Identifier: GPL-2.0-only
# Unmodified method excerpts from MikeSiLVO/script.skinshortcuts v2.0.3,
# commit 3816843a8069d237d38f13f3d0cbd991677dff28.
# Only host reference: the installed BINGIE 2.2.3 / skinshortcuts fork is NOT tested.
class ReferenceExplorer:
    @staticmethod
    def _detect_plugin_content(item):
        # based on the properties in the listitem we try to detect the content

        if "showtitle" not in item and "artist" not in item:
            # these properties are only returned in the json response
            # if we're looking at actual file content...
            # if it's missing it means this is a main directory listing
            # and no need to scan the underlying listitems.
            return None

        if "showtitle" not in item and "artist" not in item:
            # these properties are only returned in the json response
            # if we're looking at actual file content...
            # if it's missing it means this is a main directory listing
            # and no need to scan the underlying listitems.
            return "files"

        if "showtitle" not in item and "artist" in item:
            # AUDIO ITEMS ####
            if len(item["artist"]) != 0:
                artist = item["artist"][0]
            else:
                artist = item["artist"]

            if item["type"] == "artist" or artist == item["title"]:
                return "artists"

            if item["type"] == "album" or item["album"] == item["title"]:
                return "albums"

            if (item["type"] == "song" and "play_album" not in item["file"]) or \
                    (item["artist"] and item["album"]):
                return "songs"

        else:
            # VIDEO ITEMS ####
            if item["showtitle"] and not item["artist"]:
                # this is a tvshow, episode or season...
                if item["type"] == "season" or (item["season"] > -1 and item["episode"] == -1):
                    return "seasons"

                if item["type"] == "episode" or item["season"] > -1 and item["episode"] > -1:
                    return "episodes"

                return "tvshows"

            if item["artist"]:
                # this is a musicvideo
                return "musicvideos"

            if item["type"] == "movie" or item["imdbnumber"] or item["mpaa"] or \
                    item["trailer"] or item["studio"]:
                return "movies"

        return None

    def explorer(self, history, location, label, thumbnail, item_type, is_widget=False):
        is_library = False
        widget_type = None
        addon_type = None

        dialog_label = label[0].replace("  >", "")
        if len(label) != 1:
            dialog_label = "%s - %s" % (label[0].replace("  >", ""), label[-1].replace("  >", ""))

        listings = []

        tree = self.data_func.get_overrides_skin()

        # Shortcut to go 'up'
        if len(label) == 1:
            # This is the root, create a link to go back to select_shortcut
            listitem = self.create(["::UP::", "..", "", {}])
        else:
            # This isn't the root, create a link to go up the heirachy
            listitem = self.create(["::BACK::", "..", "", {}])

        listings.append(listitem)

        # Default action - create shortcut (do not show when we're looking at
        # the special entries from skinhelper service)
        if "script.skin.helper.service" not in location:
            create_label = "32058"
            if is_widget:
                create_label = "32100"

            listings.append(
                self._get_icon_overrides(tree,
                                         self.create(["::CREATE::", create_label, "", {}]), "")
            )

        log("Getting %s - %s" % (dialog_label, location))

        # Show a waiting dialog, then get the listings for the directory
        dialog = xbmcgui.DialogProgress()
        dialog.create(dialog_label, LANGUAGE(32063))

        # we retrieve a whole bunch of properties, needed to guess the content type properly
        json_response = jsonrpc.files_get_directory(location, ["title", "file", "thumbnail",
                                                               "episode", "showtitle", "season",
                                                               "album", "artist", "imdbnumber",
                                                               "firstaired", "mpaa", "trailer",
                                                               "studio", "art"])

        # Add all directories returned by the json query
        if json_response:
            json_result = json_response['result']['files']

            for item in json_result:
                # Handle numeric labels
                alt_label = item["label"]
                if item["label"].isnumeric():
                    alt_label = "$NUMBER[%s]" % item["label"]

                if location.startswith("library://"):
                    # Process this as a library node
                    is_library = True
                    if widget_type is None:
                        widget_type = self.node_func.get_media_type(location)

                    if item_type == "32014":
                        # Video node
                        window_id = "Videos"
                        if widget_type == "unknown":
                            widget_type = "video"
                        widget_target = "videos"

                    else:
                        # Audio node
                        window_id = "Music"
                        if widget_type == "unknown":
                            widget_type = "audio"
                        widget_target = "music"

                    if item["filetype"] == "directory":
                        thumb = None
                        if item["thumbnail"] != "":
                            thumb = item["thumbnail"]

                        listitem = self.create(
                            ["ActivateWindow(%s,%s,return)" % (window_id, item["file"]), alt_label,
                             "", {
                                 "icon": "DefaultFolder.png",
                                 "thumb": thumb
                             }]
                        )

                        if item["file"].endswith(".xml/") and \
                                self.node_func.is_grouped(item["file"]):
                            listitem = self.create([item["file"], "%s  >" % (item["label"]), "", {
                                "icon": "DefaultFolder.png",
                                "thumb": thumb
                            }])

                        # Add widget properties
                        widget_name = "%s - %s" % (label[0].replace("  >", ""), item["label"])
                        listitem.setProperty("widget", "Library")
                        listitem.setProperty("widgetName", widget_name)
                        listitem.setProperty("widgetType", widget_type)
                        listitem.setProperty("widgetTarget", widget_target)
                        listitem.setProperty("widgetPath", item["file"])

                        listings.append(self._get_icon_overrides(tree, listitem, ""))

                # some special code for smart shortcuts in script.skin.helper.service
                elif item.get("title", None) == "smartshortcut":

                    smart_shortcuts_data = ast.literal_eval(item.get("mpaa"))
                    thumb = smart_shortcuts_data["background"]

                    listitem = self.create([item["file"], alt_label, "", {
                        "icon": item.get("icon"),
                        "thumb": thumb
                    }])
                    # add all passed properties to the gui to set default background, widget etc.
                    properties = []
                    for key, value in list(smart_shortcuts_data.items()):
                        properties.append([key, value])

                    listitem.setProperty("smartShortcutProperties", repr(properties))
                    listitem.setProperty("untranslatedIcon", thumb)
                    listitem.setProperty("widget", smart_shortcuts_data.get("widget", "Addon"))
                    listitem.setProperty("widgetName", item["label"])
                    listitem.setProperty("widgetType", smart_shortcuts_data["type"])

                    if smart_shortcuts_data["type"] == "music" or \
                            smart_shortcuts_data["type"] == "artists" or \
                            smart_shortcuts_data["type"] == "albums" or \
                            smart_shortcuts_data["type"] == "songs":
                        listitem.setProperty("widgetTarget", "music")

                    else:
                        listitem.setProperty("widgetTarget", "videos")

                    listitem.setProperty("widgetPath", smart_shortcuts_data["list"])
                    listings.append(self._get_icon_overrides(tree, listitem, ""))

                else:
                    # Process this as a plugin
                    if item["filetype"] == "directory":
                        thumb = None
                        if item["thumbnail"] != "":
                            thumb = item["thumbnail"]

                        listitem = self.create([item["file"], "%s  >" % item['label'], "", {
                            "icon": "DefaultFolder.png",
                            "thumb": thumb
                        }])
                        listings.append(self._get_icon_overrides(tree, listitem, ""))

                    else:
                        content_type = self._detect_plugin_content(item)
                        if content_type is not None:
                            if addon_type is not None:
                                addon_type = content_type

                            else:
                                if addon_type not in (content_type, 'mixed'):
                                    addon_type = "mixed"

        # Close progress dialog
        dialog.close()

        # Show select dialog
        get_more = self._allow_install_widget_provider(location, is_widget)
        show_dialog = ShowDialog(
            "DialogSelect.xml", CWD, listing=listings, window_title=dialog_label, more=get_more
        )
        show_dialog.doModal()
        selected_item = show_dialog.result
        del show_dialog

        if selected_item == -2:
            # Get more button
            log("Selected get more button")
            return self._explorer_install_widget_provider(history, label, thumbnail,
                                                          item_type, is_widget)

        if selected_item != -1:
            selected_action = listings[selected_item].getProperty("path")
            if selected_action == "::UP::":
                # User wants to go out of explorer, back to select_shortcut
                listitem = xbmcgui.ListItem(label="back", offscreen=True)
                listitem.setProperty("path", "::UP::")

                return listitem

            if selected_action == "::CREATE::":
                # User has chosen the shortcut they want

                # Localize strings
                local_item_type = self.data_func.local(item_type)[2]

                # Create a listitem
                listitem = xbmcgui.ListItem(label=label[len(label) - 1].replace("  >", ""),
                                            label2=local_item_type, offscreen=True)
                listitem.setArt({
                    'icon': "DefaultShortcut.png",
                    'thumb': thumbnail[len(thumbnail) - 1]
                })

                # Build the action
                if item_type in ["32010", "32014", "32069"]:
                    action = 'ActivateWindow(Videos,"%s",return)' % location
                    listitem.setProperty("windowID", "Videos")
                    listitem.setProperty("widgetType", "videos")

                    # Add widget details
                    if is_library:
                        listitem.setProperty("widget", "Library")
                        widget_type = self.node_func.get_media_type(location)
                        if widget_type != "unknown":
                            listitem.setProperty("widgetType", widget_type)

                    else:
                        listitem.setProperty("widget", "Addon")

                    if addon_type is not None:
                        listitem.setProperty("widgetType", addon_type)

                    listitem.setProperty("widgetTarget", "videos")
                    listitem.setProperty("widgetName", dialog_label)
                    listitem.setProperty("widgetPath", location)

                elif item_type in ["32011", "32019", "32073"]:
                    action = 'ActivateWindow(Music,"%s",return)' % location
                    listitem.setProperty("windowID", "Music")

                    # Add widget details
                    listitem.setProperty("widgetType", "audio")
                    if is_library:
                        listitem.setProperty("widget", "Library")
                        widget_type = self.node_func.get_media_type(location)
                        if widget_type != "unknown":
                            listitem.setProperty("widgetType", widget_type)

                    else:
                        listitem.setProperty("widget", "Addon")

                    if addon_type is not None:
                        listitem.setProperty("widgetType", addon_type)

                    listitem.setProperty("widgetTarget", "music")
                    listitem.setProperty("widgetName", dialog_label)
                    listitem.setProperty("widgetPath", location)

                elif item_type in ["32012", "32089"]:
                    action = 'ActivateWindow(Pictures,"%s",return)' % location
                    listitem.setProperty("window_id", "Pictures")

                    # Add widget details
                    listitem.setProperty("widget", "Addon")
                    listitem.setProperty("widgetType", "picture")
                    listitem.setProperty("widgetTarget", "pictures")
                    listitem.setProperty("widgetName", dialog_label)
                    listitem.setProperty("widgetPath", location)

                elif item_type == "32009":
                    action = 'ActivateWindow(Programs,"%s",return)' % location
                    listitem.setProperty("windowID", "Programs")

                    # Add widget details
                    listitem.setProperty("widget", "Addon")
                    listitem.setProperty("widgetType", "program")
                    listitem.setProperty("widgetTarget", "programs")
                    listitem.setProperty("widgetName", dialog_label)
                    listitem.setProperty("widgetPath", location)

                elif item_type == "32123":
                    action = 'ActivateWindow(Games,"%s",return)' % location
                    listitem.setProperty("windowID", "Games")

                    # Add widget details
                    listitem.setProperty("widget", "Addon")
                    listitem.setProperty("widgetType", "game")
                    listitem.setProperty("widgetTarget", "games")
                    listitem.setProperty("widgetName", dialog_label)
                    listitem.setProperty("widgetPath", location)

                else:
                    action = "RunAddon(%s)" % location

                listitem.setProperty("path", action)
                listitem.setProperty("displayPath", action)
                listitem.setProperty("shortcutType", item_type)
                listitem.setProperty("icon", "DefaultShortcut.png")
                if thumbnail[len(thumbnail) - 1] == "":
                    listitem.setProperty("thumbnail", thumbnail[0])
                else:
                    listitem.setProperty("thumbnail", thumbnail[len(thumbnail) - 1])

                listitem.setProperty("location", location)

                return listitem

            if selected_action == "::BACK::":
                # User is going up the heirarchy, remove current level and re-call this function
                history.pop()
                label.pop()
                thumbnail.pop()

                return self.explorer(history, history[len(history) - 1], label, thumbnail,
                                     item_type, is_widget=is_widget)

            if selected_action.startswith("ActivateWindow(") or \
                    selected_action.startswith("$INFO"):
                # The user wants to create a shortcut to a specific shortcut listed
                listitem = listings[selected_item]

                # Add widget details
                if is_library:
                    widget_type = self.node_func.get_media_type(listitem.getProperty("widgetPath"))
                    if widget_type != "unknown":
                        listitem.setProperty("widgetType", widget_type)

                return listitem

            # User has chosen a sub-level to display, add details and re-call this function
            history.append(selected_action)
            label.append(listings[selected_item].getLabel())
            thumbnail.append(listings[selected_item].getProperty("thumbnail"))

            return self.explorer(history, selected_action, label, thumbnail, item_type,
                                 is_widget=is_widget)

        return None
