"""Exact active bank/identity decides the bounded station-logo Hero layer."""
def condition():
 a='String.IsEqual(Window(Home).Property(XCMate.Hero63.Active),A) + String.IsEqual(Window(Home).Property(XCMate.Hero63.A.Identity),ListItem.Property(XCMate.WidgetToken41)) + String.IsEqual(Window(Home).Property(XCMate.Hero63.A.Profile),ListItem.Property(XCMate.EpgProfile63))'
 b=a.replace(',A)',',B)').replace('Hero63.A.','Hero63.B.')
 return 'String.IsEqual(ListItem.Property(XCMate.WidgetKind41),live) + [['+a+' + String.IsEqual(Window(Home).Property(XCMate.Hero63.A.ArtSource),station_logo)] | ['+b+' + String.IsEqual(Window(Home).Property(XCMate.Hero63.B.ArtSource),station_logo)] | [![['+a+'] | ['+b+']] + String.IsEqual(ListItem.Property(XCMate.HeroArtSource63),station_logo)]]'
