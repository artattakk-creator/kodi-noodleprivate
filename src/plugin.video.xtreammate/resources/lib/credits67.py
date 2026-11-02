"""Native credits: unchanged official logo and exact required attribution."""
import xbmcgui,xbmcaddon
from tmdb_connection60 import ATTRIBUTION
class Credits(xbmcgui.WindowXMLDialog):
 def onInit(self):
  self.getControl(101).setLabel('XCMate · Credits');self.getControl(501).setLabel('Zurück / Back')
  self.getControl(130).setVisible(True)
  self.getControl(103).setText(self.text+'\n\n'+ATTRIBUTION+'\n\nhttps://www.themoviedb.org\nTVmaze-Daten: CC BY-SA; Bildrechte beim Rechteinhaber.')
 def onAction(self,action):
  if action.getId() in (9,10,92):self.close()
 def onClick(self,cid):
  if cid==501:self.close()
def show(text):
 window=Credits('XCMateCredits67.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p');window.text=text;window.doModal()
