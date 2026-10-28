# Copyright Skin Shortcuts contributors, GPL-2.0 (see skinshortcuts_GPL-2.0-only.txt).
# Unmodified methods from the published BINGIE repository script.skinshortcuts 2.1.0 archive.
import os,ast,copy
import xml.etree.ElementTree as xmltree
from simpleeval import simple_eval

class DataFunctions:
    def _get_additionalproperties( self, profileDir ):
        # Load all saved properties (widgets, backgrounds, custom properties)

        if self.currentProperties is not None:
            return[ self.currentProperties, self.defaultProperties ]

        self.currentProperties = []
        self.defaultProperties = []

        path = os.path.join(profileDir, "addon_data", ADDONID, xbmc.getSkinDir() + ".properties")
        if xbmcvfs.exists( path ):
            # The properties file exists, load from it
            try:
                file = xbmcvfs.File( path ).read()
                listProperties = ast.literal_eval( file )
                self._save_hash( path, file )

                for listProperty in listProperties:
                    # listProperty[0] = groupname
                    # listProperty[1] = labelID
                    # listProperty[2] = property name
                    # listProperty[3] = property value

                    # If listProperty[3] starts with $SKIN, it's from an older version of the script
                    # so quickly run it through the local function to remove the unecessary localisation
                    if listProperty[3].startswith( "$SKIN["):
                        listProperty[3] = self.local( listProperty[3] )[3]
                    self.currentProperties.append( [listProperty[0], listProperty[1], listProperty[2], listProperty[3]] )
            except:
                log( "Failed to load current properties" )
                print_exc()
                self.currentProperties = [ None ]
        else:
            self.currentProperties = [ None ]

        # Load skin defaults (in case we need them...)
        tree = self._get_overrides_skin()
        for elemSearch in [["widget", tree.findall( "widgetdefault" )], ["widget:node", tree.findall( "widgetdefaultnode" )], ["background", tree.findall( "backgrounddefault" )], ["custom", tree.findall( "propertydefault" )] ]:
            for elem in elemSearch[1]:
                # Get labelID and defaultID
                labelID = elem.attrib.get( "labelID" )
                defaultID = labelID
                if "defaultID" in elem.attrib:
                    defaultID = elem.attrib.get( "defaultID" )

                if elemSearch[0] == "custom":
                    # Custom property
                    if "group" not in elem.attrib:
                        self.defaultProperties.append( ["mainmenu", labelID, elem.attrib.get( 'property' ), elem.text, defaultID ] )
                    else:
                        self.defaultProperties.append( [elem.attrib.get( "group" ), labelID, elem.attrib.get( 'property' ), elem.text, defaultID ] )
                else:
                    # Widget or background
                    if "group" not in elem.attrib:
                        self.defaultProperties.append( [ "mainmenu", labelID, elemSearch[ 0 ].split( ":" )[ 0 ], elem.text, defaultID ] )

                        if elemSearch[ 0 ] == "background":
                            # Get and set the background name
                            backgroundName = self._getBackgroundName( elem.text )
                            if backgroundName is not None:
                                self.defaultProperties.append( [ "mainmenu", labelID, "backgroundName", backgroundName, defaultID ] )

                        if elemSearch[0] == "widget":
                            # Get and set widget type and name
                            widgetDetails = self._getWidgetNameAndType( elem.text )
                            if widgetDetails is not None:
                                self.defaultProperties.append( [ "mainmenu", labelID, "widgetName", widgetDetails[ "name" ], defaultID ] )
                                if "type" in widgetDetails:
                                    self.defaultProperties.append( [ "mainmenu", labelID, "widgetType", widgetDetails[ "type" ], defaultID ] )
                                if "path" in widgetDetails:
                                    self.defaultProperties.append( [ "mainmenu", labelID, "widgetPath", widgetDetails[ "path" ], defaultID ] )
                                if "target" in widgetDetails:
                                    self.defaultProperties.append( [ "mainmenu", labelID, "widgetTarget", widgetDetails[ "target" ], defaultID ] )

                        if elemSearch[0] == "widget:node":
                            # Set all widget properties from the default
                            if elem.text:
                                self.defaultProperties.append( [ "mainmenu", labelID, "widget", elem.attrib.get( "label" ), defaultID ] )
                            if "label" in elem.attrib:
                                self.defaultProperties.append( [ "mainmenu", labelID, "widgetName", elem.attrib.get( "label" ), defaultID ] )
                            if "type" in elem.attrib:
                                self.defaultProperties.append( [ "mainmenu", labelID, "widgetType", elem.attrib.get( "type" ), defaultID ] )
                            if "path" in elem.attrib:
                                self.defaultProperties.append( [ "mainmenu", labelID, "widgetPath", elem.attrib.get( "path" ), defaultID ] )
                            if "target" in elem.attrib:
                                self.defaultProperties.append( [ "mainmenu", labelID, "widgetTarget", elem.attrib.get( "target" ), defaultID ] )
                    else:
                        self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, elemSearch[ 0 ].split( ":" )[ 0 ], elem.text, defaultID ] )

                        if elemSearch[ 0 ] == "background":
                            # Get and set the background name
                            backgroundName = self._getBackgroundName( elem.text )
                            if backgroundName is not None:
                                self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "backgroundName", backgroundName, defaultID ] )

                        if elemSearch[0] == "widget":
                            # Get and set widget type and name
                            widgetDetails = self._getWidgetNameAndType( elem.text )
                            if widgetDetails is not None:
                                self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetName", widgetDetails[ "name" ], defaultID ] )
                                if "type" in widgetDetails:
                                    self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetType", widgetDetails[ "type" ], defaultID ] )
                                if "path" in widgetDetails:
                                    self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetPath", widgetDetails[ "path" ], defaultID ] )
                                if "target" in widgetDetails:
                                    self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetTarget", widgetDetails[ "target" ], defaultID ] )

                        if elemSearch[ 0 ] == "widget:node":
                            # Set all widget properties from the default
                            if "label" in elem.attrib:
                                self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetName", elem.attrib.get( "label" ), defaultID ] )
                            if "type" in elem.attrib:
                                self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetType", elem.attrib.get( "type" ), defaultID ] )
                            if "path" in elem.attrib:
                                self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetPath", elem.attrib.get( "path" ), defaultID ] )
                            if "target" in elem.attrib:
                                self.defaultProperties.append( [ elem.attrib.get( "group" ), labelID, "widgetTarget", elem.attrib.get( "target" ), defaultID ] )

        # Load icons out of mainmenu.DATA.xml
        path = os.path.join( SKINPATH , "mainmenu.DATA.xml")
        if xbmcvfs.exists( path ):
            file = xbmcvfs.File( path ).read()
            self._save_hash( path, file )
            tree = xmltree.parse( path )
            for node in tree.getroot().findall( "shortcut" ):
                label = self.local( node.find( "label" ).text )[3].replace( " ", "" ).lower()
                action = node.find( "action.text" )
                labelID = self._get_labelID( label, action, getDefaultID = True )
                self.defaultProperties.append( [ "mainmenu", labelID, "icon", node.find( "icon" ).text ] )

        returnVal = [ self.currentProperties, self.defaultProperties ]
        return returnVal

    def checkAdditionalProperties( self, group, labelID, defaultID, isUserShortcuts, profileDir ):
        # Return any additional properties, including widgets, backgrounds, icons and thumbnails
        allProperties = self._get_additionalproperties( profileDir )
        currentProperties = allProperties[1]

        returnProperties = []

        # This returns two lists...
        #  allProperties[0] = Saved properties
        #  allProperties[1] = Default properties

        if isUserShortcuts and ( len( allProperties[ 0 ] ) == 0 or allProperties[ 0 ][ 0 ] is not None ):
            currentProperties = allProperties[0]

        # Loop through the current properties, looking for the current item
        for currentProperty in currentProperties:
            # currentProperty[0] = Group name
            # currentProperty[1] = labelID
            # currentProperty[2] = Property name
            # currentProperty[3] = Property value
            # currentProperty[4] = defaultID
            if labelID is not None and currentProperty[0] == group and currentProperty[1] == labelID:
                returnProperties.append( self.upgradeAdditionalProperties( currentProperty[2], currentProperty[3] ) )
            elif len( currentProperty ) != 4:
                if defaultID is not None and currentProperty[0] == group and currentProperty[4] == defaultID:
                    returnProperties.append( self.upgradeAdditionalProperties( currentProperty[2], currentProperty[3] ) )

        return returnProperties

    def upgradeAdditionalProperties( self, propertyName, propertyValue ):
        # This function fixes any changes to additional properties between Kodi versions
        if propertyName.startswith( "widgetTarget" ) and propertyValue == "video":
            propertyValue = "videos"

        return [ propertyName, propertyValue ]

    def _get_labelID( self, labelID, action, getDefaultID = False, includeAddOnID = True, noNonLocalized = False ):
        # This gets the unique labelID for the item we've been passed. We'll also store it, to make sure
        # we don't give it to any other item.

        labelID = self.createNiceName( self.slugify( labelID.replace( " ", "" ).lower() ), noNonLocalized )

        if includeAddOnID:
            addon_labelID = self._get_addon_labelID( action )
            if addon_labelID is not None:
                labelID = addon_labelID

        # If we're getting the defaultID, just return this
        if getDefaultID == True:
            return labelID

        # Check if the labelID exists in the list
        if labelID in self.labelIDList:
            # We're going to add an --[int] to the end of this
            count = 0
            while labelID + "--" + str( count ) in self.labelIDList:
                count += 1

            # We can now use this one
            self.labelIDList.append( labelID + "--" + str( count ) )
            return labelID + "--" + str( count )
        else:
            # We can use this one
            self.labelIDList.append( labelID )
            return labelID

    def _get_addon_labelID( self, action ):
        # This will check the action to see if this is a program or the root of a plugin and, if so, return that as the labelID

        if action is None:
            return None

        try:
            if action.startswith( "RunAddOn(" ) and "," not in action:
                return action[9:-1]

            if action.startswith( "RunScript(" ) and "," not in action:
                return action[10:-1]

            if "plugin://" in action and "?" not in action:
                # Return the action
                # - less ActivateWindow(
                # - The second group after being split by comma
                # - Less plugin://
                return action[15:-1].split( "," )[1].replace( '"', '' )[9:]
        except:
            return None

        return None

    def createNiceName ( self, item, noNonLocalized = False ):
        # Translate certain localized strings into non-localized form for labelID
        if noNonLocalized == False:
            if item == "3":
                return "videos"
            if item == "2":
                return "music"
            if item == "342":
                return "movies"
            if item == "20343":
                return "tvshows"
            if item == "32022":
                return "livetv"
            if item == "20389":
                return "musicvideos"
            if item == "10002":
                return "pictures"
            if item == "12600":
                return "weather"
            if item == "10001":
                return "programs"
            if item == "32032":
                return "dvd"
            if item == "10004":
                return "settings"
            if item == "32087":
                return "radio"

        return item.lower( ).replace( " ", "" )

class Template:
    def replaceElements( self, tree, visibilityCondition, profileVisibility, items, properties = {}, customitems = None ):
        if tree is None: return
        for elem in tree:
            # <tag skinshortcuts="visible" /> -> <tag condition="[condition]" />
            if "skinshortcuts" in elem.attrib:
                # Get index of the element
                index = list( tree ).index( elem )

                # Get existing attributes, text and tag
                attribs = []
                for singleAttrib in elem.attrib:
                    if singleAttrib == "skinshortcuts":
                        type = elem.attrib.get( "skinshortcuts" )
                    else:
                        attribs.append( ( singleAttrib, elem.attrib.get( singleAttrib ) ) )
                text = elem.text
                tag = elem.tag

                # Don't continue is type = visibility, and no visibilityCondition
                if type == "visibility" and visibilityCondition is None:
                    continue

                # Remove the existing element
                tree.remove( elem )

                # Make replacement element
                newElement = xmltree.Element( tag )
                if text is not None:
                    newElement.text = text
                for singleAttrib in attribs:
                    newElement.set( singleAttrib[ 0 ], singleAttrib[ 1 ] )

                # Make replacements
                if type == "visibility" and visibilityCondition is not None:
                    newElement.set( "condition", visibilityCondition )

                # Insert it
                tree.insert( index, newElement )

            # <tag>$skinshortcuts[var]</tag> -> <tag>[value]</tag>
            # <tag>$skinshortcuts[var]</tag> -> <tag><include>[includeName]</include></tag> (property = $INCLUDE[includeName])
            if elem.text is not None:
                while "$SKINSHORTCUTS[" in elem.text:
                    # Split the string into its composite parts
                    stringStart = elem.text.split( "$SKINSHORTCUTS[", 1 )
                    stringEnd = stringStart[ 1 ].split( "]", 1 )
                    # stringStart[ 0 ] = Any code before the $SKINSHORTCUTS property
                    # StringEnd[ 0 ] = The name of the $SKINSHORTCUTS property
                    # stringEnd[ 1 ] = Any code after the $SKINSHORTCUTS property

                    if stringEnd[ 0 ] in properties:
                        if properties[ stringEnd[ 0 ] ].startswith( "$INCLUDE[" ):
                            # Remove text property
                            elem.text = ""
                            # Add include element
                            includeElement = xmltree.SubElement( elem, "include" )
                            includeElement.text = properties[ stringEnd [ 0 ] ][ 9:-1 ]
                        else:
                            elem.text = stringStart[ 0 ] + properties[ stringEnd[ 0 ] ] + stringEnd[ 1 ]
                    else:
                        elem.text = stringStart[ 0 ] + stringEnd[ 1 ]

            # <tag attrib="$skinshortcuts[var]" /> -> <tag attrib="[value]" />
            for attrib in elem.attrib:
                value = elem.attrib.get( attrib )
                while "$SKINSHORTCUTS[" in elem.attrib.get( attrib ):
                    # Split the string into its composite parts
                    stringStart = elem.attrib.get( attrib ).split( "$SKINSHORTCUTS[", 1 )
                    stringEnd = stringStart[ 1 ].split( "]", 1 )

                    if stringEnd[ 0 ] in properties:
                        elem.set( attrib, stringStart[ 0 ] + properties[ stringEnd[ 0 ] ] + stringEnd[ 1 ] )
                    else:
                        elem.set( attrib, stringStart[ 0 ] + stringEnd[ 1 ] )

                if value.startswith( "$SKINSHORTCUTS[" ) and value[ 15:-1 ] in properties:
                    newValue = ""
                    if value[ 15:-1 ] in properties:
                        newValue = properties[ value[ 15:-1 ] ]
                    elem.set( attrib, newValue )

            # <tag>$PYTHON[var]</tag> -> <tag>[result]</tag>
            if elem.text is not None:
                while "$PYTHON[" in elem.text:
                    # Split the string into its composite parts
                    stringStart = elem.text.split( "$PYTHON[", 1 )
                    stringEnd = stringStart[ 1 ].split( "]", 1 )
                    # stringStart[ 0 ] = Any code before the $MATHS property
                    # StringEnd[ 0 ] = The maths to be performed
                    # stringEnd[ 1 ] = Any code after the $MATHS property

                    stringEnd[ 0 ] = simple_eval( "%s" %( stringEnd[ 0 ] ), names=properties )

                    elem.text = stringStart[ 0 ] + str( stringEnd[ 0 ] ) + stringEnd[ 1 ]

            # <tag attrib="$PYTHON[var]" /> -> <tag attrib="[value]" />
            for attrib in elem.attrib:
                value = elem.attrib.get( attrib )
                while "$PYTHON[" in elem.attrib.get( attrib ):
                    # Split the string into its composite parts
                    stringStart = elem.attrib.get( attrib ).split( "$PYTHON[", 1 )
                    stringEnd = stringStart[ 1 ].split( "]", 1 )

                    stringEnd[ 0 ] = simple_eval( "%s" %( stringEnd[ 0 ] ), names=properties )

                    elem.set( attrib, stringStart[ 0 ] + str( stringEnd[ 0 ] ) + stringEnd[ 1 ] )

            # <skinshortcuts>visible</skinshortcuts> -> <visible>[condition]</visible>
            # <skinshortcuts>items</skinshortcuts> -> <item/><item/>...
            if elem.tag == "skinshortcuts":
                # Get index of the element
                index = list( tree ).index( elem )

                # Get the type of replacement
                type = elem.text

                # Don't continue is type = visibility, and no visibilityCondition
                if type == "visibility" and visibilityCondition is None:
                    continue

                # Remove the existing element
                tree.remove( elem )

                # Make replacements
                if type == "visibility" and visibilityCondition is not None:
                    # Create a new visible element
                    newelement = xmltree.Element( "visible" )
                    newelement.text = visibilityCondition
                    # Insert it
                    tree.insert( index, newelement )
                elif type == "items" and customitems is not None and elem.attrib.get( "insert" ):
                    for elem in self.buildSubmenuCustomItems( customitems, items.findall( "item" ), elem.attrib.get( "insert" ), properties ):
                        for child in elem:
                            tree.insert( index, child )
                elif type == "items":
                    # Firstly, go through and create an array of all items in reverse order, without
                    # their existing visible element, if it matches our visibilityCondition
                    newelements = []
                    if items == []:
                        break
                    for item in items.findall( "item" ):
                        newitem = self.copy_tree( item )

                        # Remove the existing visible elem from this
                        for visibility in newitem.findall( "visible" ):
                            if visibility.text != profileVisibility:
                                continue
                            newitem.remove( visibility )

                        # Add a copy to the array
                        newelements.insert( 0, newitem )
                    if len( newelements ) != 0:
                        for elem in newelements:
                            # Insert them into the template
                            tree.insert( index, elem )

            else:
                # Iterate through tree
                self.replaceElements( elem, visibilityCondition, profileVisibility, items, properties, customitems = customitems )

    def copy_tree( self, elem ):
        if elem is None: return None
        ret = xmltree.Element(elem.tag, elem.attrib)
        ret.text = elem.text
        ret.tail = elem.tail
        for child in elem:
            ret.append(self.copy_tree(child))
        return ret

class LibraryFunctions:
    def widgets( self ):
        # Get widgets
        listitems = []

        # Load skin overrides
        tree = DATA._get_overrides_skin()
        elems = tree.getroot().findall( "widget" )
        for elem in elems:
            widgetType = None
            widgetPath = None
            widgetTarget = None
            widgetIcon = ""
            widgetName = None
            if "type" in elem.attrib:
                widgetType = elem.attrib.get( "type" )
            if "condition" in elem.attrib:
                if not xbmc.getCondVisibility( elem.attrib.get( "condition" ) ):
                    continue
            if "path" in elem.attrib:
                widgetPath = elem.attrib.get( "path" )
            if "target" in elem.attrib:
                widgetTarget = elem.attrib.get( "target" )
            if "icon" in elem.attrib:
                widgetIcon = elem.attrib.get( "icon" )
            if "name" in elem.attrib:
                widgetName = DATA.local( elem.attrib.get( 'name' ) )[2]

            # Save widget for button 309
            self.dictionaryGroupings[ "widgets-classic" ].append( [elem.text, DATA.local( elem.attrib.get( 'label' ) )[2], widgetType, widgetPath, widgetIcon, widgetTarget ] )

            # Save widgets for button 312
            listitem = self._create( [ elem.text, DATA.local( elem.attrib.get( 'label' ) )[2], "::SCRIPT::32099", {"icon": widgetIcon } ] )
            listitem.setProperty( "widget", elem.text )
            if widgetName is not None:
                listitem.setProperty( "widgetName", widgetName )
            else:
                listitem.setProperty( "widgetName", DATA.local( elem.attrib.get( 'label' ) )[2] )
            if widgetType is not None:
                listitem.setProperty( "widgetType", widgetType )
            if widgetPath is not None:
                listitem.setProperty( "widgetPath", widgetPath )
            if widgetTarget is not None:
                listitem.setProperty( "widgetTarget", widgetTarget )
            listitems.append( listitem )

        self.addToDictionary( "widgets", listitems )

    def addWidgetReload( self, widgetPath ):
        if "plugin://" not in widgetPath or "reload=" in widgetPath.lower() or "script.extendedinfo" in widgetPath.lower():
            # Not a plugin, or already has a reload parameter
            # Also return on Extended Info, as it doesn't like its parameters to be altered
            return widgetPath

        # Depending whether it already has additional components or not, we may need to use a ? or a & to extend the path
        # with the new reload parameter
        reloadSplitter = "?"
        if "?" in widgetPath:
            reloadSplitter = "&"

        # We have seperate reload params for each content type
        # default: refresh at every library change/video playback (widgetreload) + every 10 minutes (widgetreload2)
        reloadParam = "$INFO[Window(Home).Property(widgetreload)]$INFO[Window(Home).Property(widgetreload2)]"
        if "movie" in widgetPath:
            reloadParam = "$INFO[Window(Home).Property(widgetreload-movies)]"
        elif "episode" in widgetPath:
            reloadParam = "$INFO[Window(Home).Property(widgetreload-episodes)]"
        elif "tvshow" in widgetPath:
            reloadParam = "$INFO[Window(Home).Property(widgetreload-episodes)]"
        elif "musicvideo" in widgetPath:
            reloadParam = "$INFO[Window(Home).Property(widgetreload-musicvideos)]"
        elif "music" in widgetPath or "song" in widgetPath:
            reloadParam = "$INFO[Window(Home).Property(widgetreload-music)]"

        # And return it all
        return "%s%sreload=%s" %( widgetPath, reloadSplitter, reloadParam )

