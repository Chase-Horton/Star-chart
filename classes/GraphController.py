from skyfield.api import load, wgs84
from skyfield.data import hipparcos
from StarSelector import StarSelector
from PlanetSelector import PlanetSelector
from MessierSelector import MessierSelector
from GridPlotter import GridPlotter
from Models import ConstellationLoader

from Telescope import Telescope
from pytz import timezone
import pygame, sys
from pygame.locals import *
import math

#temp
import pyperclip
#temp
pygame.init()
myfont = pygame.font.SysFont("monospace", 32)
class GraphController:
    def __init__(self):
        #STATEFUL
        self.TELESCOPE_MODE = False
        self.CURRENT_TELESCOPE = None
        self.CURRENT_ZOOM_OBJ = None
        self.CURRENT_EYEPIECE = None

        self.selectedSearchObject = None
        self.selectedMousePlanet = None
        self.currPlanets = []
        self.currStars = []
        self.currMessier = []
        self.currConstellationIndex = 0
        self.planetPlotterEnabled = False
        self.messierPlotterEnabled = False
        self.graphStateIndex = 6
        self.constellationCatalog = ['none', 'Ori', 'UMa', 'UMi', 'Dra', 'Cas', 'Cam', 'Cep', 'Gem', 'Aqr', 'Leo', 'Sco', 'CMa',
         'And', 'Peg', 'Aur', 'Cyg', 'Cnc', 'Lyr', 'Vir', 'Boo']
        self.constellationCatalogIndex = 0
        self.filter = 3
        #CONST
        self.CENTRALTIME = timezone('US/Central')
        size = 3840, 2160
        self.screen = pygame.display.set_mode(size, display=1)
        self.ts = load.timescale()
        #set time for angle calc
        self.time = self.ts.now()

        planets = load('de421.bsp')
        self.earth = planets['earth']
        #set location to wichita on earth for apparent location of stars
        self.location = self.earth + wgs84.latlon(37.697948, -97.314835)

        #load hipparcos db of stars
        with load.open(hipparcos.URL) as f:
            self.df = hipparcos.load_dataframe(f)

        #remove missing pos
        self.df = self.df[self.df['ra_degrees'].notnull()]
        #create star, planet, and messier selector object
        self.Selector = StarSelector(self.df)
        self.PlanetSelector = PlanetSelector()
        self.MessierSelector = MessierSelector()
        #obj to load constellations
        self.ConstellationLoader = ConstellationLoader()
        #create grid controller
        self.GridPlotter = GridPlotter(self.screen, 115)
    #select stars filtering by selected magnitude
    def selectStarsByMag(self):
        return self.Selector.selectStarsByMag(self.filter, self.time, self.location)
    #select stars by list of constellation symbols
    def selectStarsByConst(self, consts):
        return self.Selector.selectStarsByConstellations(self.time, self.location, consts)
    #add stars by list of constellation symbols to list of stars
    def addStarsByConst(self, consts, starList):
        return self.Selector.selectStarsByConstellations(self.time, self.location, consts, starList)
    #update selected constellation index
    def updateConstellationIndex(self, i):
        self.constellationCatalogIndex += i
        if self.constellationCatalogIndex < 0:
            self.constellationCatalogIndex = len(self.constellationCatalog) - 1
        elif self.constellationCatalogIndex >= len(self.constellationCatalog):
            self.constellationCatalogIndex = 0
        self.fastRefresh()
    #update GraphStateIndex
    def updateGraphStateIndex(self, i):
        self.graphStateIndex += i
        if self.graphStateIndex < 0:
            self.graphStateIndex = 6
        elif self.graphStateIndex > 6:
            self.graphStateIndex = 0
        self.fastRefresh()
    def emulateTelescopeAtActiveStar(self, telescopeAperature=150, telescopeFocalLength=750, eyepieceFocalLength=25, eyepieceAFOV=60):
        T = Telescope(telescopeAperature, telescopeFocalLength)
        altOfObj = self.selectedMousePlanet.alt
        azOfObj = self.selectedMousePlanet.az
        altAzRangeOfEyepiece = T.calculateFOVAltAzRanges(eyepieceFocalLength, eyepieceAFOV, altOfObj, azOfObj)
        r = (altAzRangeOfEyepiece[0][1]-altAzRangeOfEyepiece[0][0])*math.sqrt(self.GridPlotter.PPI)/2
        pygame.draw.circle(self.screen, [255,0,0], self.selectedMousePlanet.loc, r, 1)
        telescopeVisibleStarList = self.selectAllActiveObjectsFromRange(altAzRangeOfEyepiece)[0]
        for obj in telescopeVisibleStarList:
            self.GridPlotter.plotStar(obj, [255,0,0])
    def zoomTelescopeAtActiveStar(self, telescopeAperature=150, telescopeFocalLength=750, eyepieceFocalLength=25, eyepieceAFOV=60):
        if not self.TELESCOPE_MODE:
            self.TELESCOPE_MODE = True
            self.CURRENT_TELESCOPE = Telescope(telescopeAperature, telescopeFocalLength)
            self.CURRENT_ZOOM_OBJ = self.selectedMousePlanet
            self.CURRENT_EYEPIECE = [eyepieceFocalLength, eyepieceAFOV]
            self.refreshTelescope()
        else:
            self.TELESCOPE_MODE = False
            self.CURRENT_TELESCOPE = None
            self.CURRENT_ZOOM_OBJ = None
            self.CURRENT_EYEPIECE = None
            self.fastRefresh()

    def refreshTelescope(self):
        altOfObj = self.CURRENT_ZOOM_OBJ.alt
        azOfObj = self.CURRENT_ZOOM_OBJ.az
        altAzRangeOfEyepiece = self.CURRENT_TELESCOPE.calculateFOVAltAzRanges(self.CURRENT_EYEPIECE[0], self.CURRENT_EYEPIECE[1], altOfObj, azOfObj)
        telescopeVisibleStarList = self.selectAllActiveObjectsFromRange(altAzRangeOfEyepiece)[0]
        magnification = self.CURRENT_TELESCOPE.calculateMagnification(self.CURRENT_EYEPIECE[0])
        fov = self.CURRENT_TELESCOPE.calculateFOV(self.CURRENT_EYEPIECE[0], self.CURRENT_EYEPIECE[1])
        self.CURRENT_TELESCOPE.plotListOfStarsScaled(self.graphStateIndex, self.GridPlotter, telescopeVisibleStarList, fov, magnification, self.selectedMousePlanet)

    #select all stars, planets, or messier objects in alt az range
    def selectAllActiveObjectsFromRange(self, altAzRanges):
        altRange = altAzRanges[0]
        azRange = altAzRanges[1]
        visibleStars = []
        visiblePlanets = []
        visibleMessierObjects = []
        for star in self.currStars:
            if star.alt >= altRange[0] and star.alt <= altRange[1] and star.az >= azRange[0] and star.az <= azRange[1]:
                visibleStars.append(star)
        for planet in self.currPlanets:
            if planet.alt >= altRange[0] and planet.alt <= altRange[1] and planet.az >= azRange[0] and planet.az <= azRange[1]:
                visiblePlanets.append(planet)
        for messierObject in self.currMessier:
            if messierObject.alt >= altRange[0] and messierObject.alt <= altRange[1] and messierObject.az >= azRange[0] and messierObject.az <= azRange[1]:
                visibleMessierObjects.append(messierObject)
        return visibleStars, visiblePlanets, visibleMessierObjects
        
    #redraw graph then stars based on state values
    def drawStars(self):
        #!selection magnitude add more options later
        if "mag" == "mag":
            self.GridPlotter.plotStarList(self.currStars, self.constellationCatalog[self.constellationCatalogIndex])
        #selection constellation
        elif "byConst" == "TBA":
            pass
    #draw planets 
    def drawPlanets(self):
        self.GridPlotter.plotPlanetList(self.currPlanets)
    #draw messier objects
    def drawMessier(self):
        self.GridPlotter.plotMessierList(self.currMessier)  
    #draw stars with threading
    def drawStarsWithThread(self):
        #!selection magnitude add more options later
        if "mag" == "mag":
            self.currStars = self.Selector.selectStarsByMagnitudeWithBatching(self.filter, self.time, self.location)
            self.GridPlotter.plotStarList(self.currStars, self.constellationCatalog[self.constellationCatalogIndex])
        #selection constellation
        elif "byConst" == "TBA":
            pass
    def fastDrawStars(self):
        self.GridPlotter.plotStarList(self.currStars, self.constellationCatalog[self.constellationCatalogIndex])
    def findStarOrPlanet(self, loc):
        for star in self.currStars:
            dist = math.sqrt((loc[0] - star.loc[0]) ** 2 + (loc[1] - star.loc[1]) ** 2)
            if dist < star.normMagnitude*8 + 2:
                return star
        for planet in self.currPlanets:
            dist = math.sqrt((loc[0] - planet.loc[0]) ** 2 + (loc[1] - planet.loc[1]) ** 2)
            if dist < planet.normMagnitude*12 + 2:
                return planet
        for messierObject in self.currMessier:
            dist = math.sqrt((loc[0] - messierObject.loc[0]) ** 2 + (loc[1] - messierObject.loc[1]) ** 2)
            if dist < messierObject.normMagnitude*12 + 2:
                return messierObject
        return None
    #!TODO:save infolst and offsets for between refreshes
    def selectStarOrPlanet(self, starOrPlanet, color=[255, 255, 0], position = [100, 100]):
        if starOrPlanet == None:
            label = myfont.render('No Star Found', 1, color)
            self.screen.blit(label, position)
            return
        elif starOrPlanet.objType == 'star':
            #! REMOVE THIS
            """currClip = pyperclip.paste()
            newClip = currClip + ',' + str(starOrPlanet.ID)
            if len(newClip.split(',')) > 2:
                newClip = newClip.split(',')[2]
                print('new clip: ' + newClip)
            elif len(newClip.split(',')) == 2:
                print('ready to paste\n')
            pyperclip.copy(newClip) """
            star = starOrPlanet
            #recolor star
            self.GridPlotter.plotStar(star, color)
            #print info
            dist = 'Distance: {:,.2f} AU '.format(star.distance.au) + '| {:,.2f} ly'.format(star.distance.m/9460730472580800)
            infoLst = [f'HYG ID: {star.ID}', f'Name: {star.name}', f'Magnitude: {star.magnitude}', dist, f'Member of Constellation: {star.constellation} | {star.symbol}',
            'Azimuth: {:.2f}°'.format(star.az), 'Altitude: {:.2f}°'.format(star.alt)]
            offset = 0
            for txt in infoLst:
                label = myfont.render(txt, 1, color)
                self.screen.blit(label, (position[0], position[1] + offset))
                offset += 40
            return
        elif starOrPlanet.objType == 'planet':
            planet = starOrPlanet
            #recolor planet
            if planet.alt > 0:
                self.GridPlotter.plotPlanet(planet, color)
            #print info
            dist = 'Distance: {:,.2f} km '.format(planet.distance.km) + '| {:,.2f} ly'.format(planet.distance.m/9460730472580800)
            infoLst = [f'Name: {planet.name}', f'Magnitude: {planet.magnitude}', dist,'Azimuth: {:.2f}°'.format(planet.az),
                'Altitude: {:.2f}°'.format(planet.alt), 'Mass: {:,.2f} kg'.format(planet.mass1024*1024), 'Diameter: {:,.2f} km'.format(planet.diameter),
                 'Density: {:,.2f} kg/m^3'.format(planet.density), 'Gravity: {:,.2f} m/s^2'.format(planet.gravity),
                  'Average Temperature: {:,.2f} C'.format(planet.avgTemp), 'Number of Moons {}'.format(planet.numMoons)]
            offset = 0
            for txt in infoLst:
                label = myfont.render(txt, 1, color)
                self.screen.blit(label, (position[0], position[1] + offset))
                offset += 40
            return
        else:
            messier = starOrPlanet
            if messier.alt > 0:
                #recolor messier
                self.GridPlotter.plotPlanet(messier, color)
            #print info
            designation = f'Messier #: {messier.MCode}'
            NGC = f'Designation: {messier.NGC}'
            if messier.NGCNames == None:
                name = 'Other Names: N/A'
            else:
                name = f'Other Names: {messier.NGCNames}'
            constellation = f'Constellation: {messier.constellation}'
            mType = f'Type: {messier.type}'
            yearDiscovered = 'Year Discovered: {:.0f}'.format(messier.yearDiscovered)

            magnitude = 'Magnitude: {:.2f}'.format(messier.magnitude)
            alt = 'Altitude: {:.2f}°'.format(messier.alt)
            az = 'Azimuth: {:.2f}°'.format(messier.az)
            distance = 'Distance: {:,.2f} ly'.format(messier.distance)
            infoLst = [designation, NGC, name, constellation, mType, yearDiscovered, magnitude, alt, az, distance]
            offset = 0
            for txt in infoLst:
                label = myfont.render(txt, 1, color)
                self.screen.blit(label, (position[0], position[1] + offset))
                offset += 40
            return
    #if self.currConstellationObj != None, then load constellation from name or symbol, else remove constellation
    def toggleConstellationLines(self):
        if self.currConstellationIndex == 0:
            self.currConstellationIndex = 1
        elif self.currConstellationIndex == 1:
            self.currConstellationIndex = 2
        else:
            self.currConstellationIndex = 0
        self.fastRefresh()
    #draw lines on screen for constellation from self.currConstellationObj
    def drawConstellationLines(self):
        if self.currConstellationIndex == 2:
            currConstellationsListObj = self.ConstellationLoader.loadAllVisibleConstellations(self.currStars)
            if currConstellationsListObj != None:
                for constellation in currConstellationsListObj:
                    for line in constellation.lines:
                        pygame.draw.line(self.screen, line.color, line.pos1, line.pos2, line.width)
        elif self.currConstellationIndex == 1:
            currConstellationObj = self.ConstellationLoader.loadConstellationWithPosFromDf(self.constellationCatalog[self.constellationCatalogIndex], self.currStars)
            if currConstellationObj != None:
                for line in currConstellationObj.lines:
                    pygame.draw.line(self.screen, line.color, line.pos1, line.pos2, line.width)
    # update location with new lat long
    def updateLocation(self, lat, long ,elev=0):
        self.location = self.earth + wgs84.latlon(lat, long, elev)
        self.refresh()
    #update filter value and redraw stars
    def updateFilter(self, i):
        self.filter += i
        self.refresh()
    #update time and redraw stars
    def updateTime(self, i):
        self.time += i
        self.refresh()
    #generate an objects orbit at time interval
    def generateOrbit(self, object, i, timeInterval):
        x = 0
        time = self.time
        while x < i:
            #here
            pass
    #update info text
    def updateInfoText(self):
        label = myfont.render('Showing Stars brighter than Magnitude: {:.1f}'.format(self.filter), 1, (0,0,255))
        self.screen.blit(label, (2700, 100))
        if self.constellationCatalog[self.constellationCatalogIndex] != 'none':
            constell = self.Selector.constellNameDict[self.constellationCatalog[self.constellationCatalogIndex]]
        else:
            constell = 'None'
        label = myfont.render(f'Selected Constellation: {constell}', 1, (0,0,255))
        self.screen.blit(label, (2800, 140))
        time = str(str(self.time.astimezone(self.CENTRALTIME)))
        time = time.split(':')
        time = time[:2]
        time = ':'.join(time)
        label = myfont.render(f'Selected Time CST: {time}', 1, (0,0,255))
        self.screen.blit(label, (2900, 180))
    #toggle planet plotter
    def togglePlanetPlotter(self):
        self.planetPlotterEnabled = not self.planetPlotterEnabled
        self.refresh()
    def toggleMessierPlotter(self):
        self.messierPlotterEnabled = not self.messierPlotterEnabled
        self.refresh()
    #!TODO: ADD METHOD THAT UPDATES SAVED SEARCH OBJECTS POSITION INSTEAD OF RERUNNING THIS FUNCTION
    def searchObject(self, name):
        # first check if it is a planet we are displaying
        for planet in self.currPlanets:
            if planet.name == name:
                return planet
        # then check if it is a planet we are not displaying
        if name in self.PlanetSelector.planetList:
            return self.PlanetSelector.getPlanetObj(name, self.time, self.location)
        # then check if it is a messier object we are displaying
        for messier in self.currMessier:
            if messier.NGCNames != None:
                if name in messier.NGCNames and 'M' not in name:
                    return messier
            if name == messier.MCode:
                return messier
            if name == messier.NGC:
                return messier
        # then check if it is a messier object we are not displaying
        messierObjects = self.MessierSelector.getAllMessierObjects(self.time, self.location)
        for messier in messierObjects:
            if messier.NGCNames != None:
                if name in messier.NGCNames and 'M' not in name:
                    return messier
            if name == messier.MCode:
                return messier
            if name == messier.NGC:
                return messier
        # now check if the object is a star we are displaying
        foundStar = None
        for star in self.currStars:
            if star.name == name:
                foundStar = star
            if star.ID == name:
                foundStar = star
                return star
        if foundStar != None:
            return foundStar
        else:
            #resolution too low
            return self.Selector.selectStarByNameOrId(name, self.location, self.time)
    def refreshSearchObjectAndData(self):
        if self.selectedSearchObject != None:
            #update info on search object in bottom right
            newObj = self.searchObject(self.selectedSearchObject.name)
            self.selectedSearchObject = newObj
            self.selectStarOrPlanet(newObj, [255, 0, 0], [2950, 1500])
    def refreshSelectedMousePlanet(self):
        if self.selectedMousePlanet != None:
            newObj = self.searchObject(self.selectedMousePlanet.name)
            self.selectedMousePlanet = newObj
            self.selectStarOrPlanet(self.selectedMousePlanet)
    def refresh(self):
        #refresh star locations
        self.currStars = self.selectStarsByMag()
        if not self.TELESCOPE_MODE:
            #draw graph and lines and labels
            self.GridPlotter.update(self.graphStateIndex)
            if self.messierPlotterEnabled:
                self.currMessier = self.MessierSelector.getVisibleMessierObjects(self.time, self.location)
                self.drawMessier()
            #draw stars over messier
            self.drawStars()
            #draw constellation lines over stars if there is a constellation obj selected
            self.drawConstellationLines()
            #draw planets over stars
            if self.planetPlotterEnabled:
                self.currPlanets = self.PlanetSelector.getVisiblePlanets(self.time, self.location)
                self.drawPlanets()
            #draw search object over planets
            self.refreshSearchObjectAndData()
            #draw selected mouse planet over search objects
            self.refreshSelectedMousePlanet()
        else:
            #if telescope mode
            if self.planetPlotterEnabled:
                self.currPlanets = self.PlanetSelector.getVisiblePlanets(self.time, self.location)
            if self.messierPlotterEnabled:
                self.currMessier = self.MessierSelector.getVisibleMessierObjects(self.time, self.location)
            self.refreshTelescope()
    def fastRefresh(self):
        if not self.TELESCOPE_MODE:
            #draw graph and lines and labels
            self.GridPlotter.update(self.graphStateIndex)
            if self.messierPlotterEnabled:
                self.currMessier = self.MessierSelector.getVisibleMessierObjects(self.time, self.location)
                self.drawMessier()
            self.fastDrawStars()
            self.drawConstellationLines()
            if self.planetPlotterEnabled:
                self.currPlanets = self.PlanetSelector.getVisiblePlanets(self.time, self.location)
                self.drawPlanets()
            self.refreshSearchObjectAndData()
            self.refreshSelectedMousePlanet()
        else:
            #if telescope mode DEFINITELY BROKEN AS FUCK
            if self.planetPlotterEnabled:
                self.currPlanets = self.PlanetSelector.getVisiblePlanets(self.time, self.location)
            if self.messierPlotterEnabled:
                self.currMessier = self.MessierSelector.getVisibleMessierObjects(self.time, self.location)
            self.refreshTelescope()
    def handleInput(self, input):
        #for now only handle search
        if 'search' == 'search':
            if input != '':
                self.selectedSearchObject = self.searchObject(input)
                self.fastRefresh()
            else:
                self.selectedSearchObject = None
                self.fastRefresh()
            

    def handleKeys(self, events):
        for event in events:
            if(event.type == KEYDOWN):
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_w:
                    self.updateFilter(.1)
                elif event.key == K_s:
                    self.updateFilter(-.1)
                elif event.key == K_d:
                    self.updateConstellationIndex(1)
                elif event.key == K_a:
                    self.updateConstellationIndex(-1)
                elif event.key == K_TAB:
                    self.updateGraphStateIndex(-1)
                elif event.key == K_e:
                    self.updateTime(0.0006944444444444444*180)
                elif event.key == K_q:
                    self.updateTime(-0.0006944444444444444)
                elif event.key == K_p:
                    self.togglePlanetPlotter()
                elif event.key == K_m:
                    self.toggleMessierPlotter()
                elif event.key == K_c:
                    self.toggleConstellationLines()
                elif event.key == K_t:
                    self.emulateTelescopeAtActiveStar()
                elif event.key == K_z:
                    self.zoomTelescopeAtActiveStar()
                elif event.key == ord('`'):
                    self.fastRefresh()
            elif event.type == MOUSEBUTTONDOWN:
                self.selectedMousePlanet = None
                self.fastRefresh()
                self.selectedMousePlanet = self.findStarOrPlanet(pygame.mouse.get_pos())
                self.selectStarOrPlanet(self.selectedMousePlanet)
                

            