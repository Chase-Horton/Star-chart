from skyfield.api import load, wgs84
from data.Planet import Planet
import pandas as pd
from util import normalizeListMagnitudes
class PlanetSelector:
    def __init__(self):
        self.planets = load('de421.bsp')
        self.planetList = {'Mercury':1, 'Venus':2, 'Mars':4, 'Jupiter':5, 'Saturn':6, 'Uranus':7, 'Neptune':8}
        self.planetMagnitudes = {'Mercury':-0.36, 'Venus':-4.40, 'Mars':-1.52, 'Jupiter':-9.40, 'Saturn':-8.88, 'Uranus':-7.19, 'Neptune':-6.87}
        self.planetNameList = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        self.selectedPlanets = [1, 2, 4, 5, 6, 7, 8]
        self.planetCodes = {planetKey:self.planets[self.planetList[planetKey]] for planetKey in self.planetList.keys()}
        self.NASAplanetData = self.loadPlanetData()
    def loadPlanetData(self):
        df = pd.read_csv('data/planets', sep='\t')
        df = df.transpose()
        df = df.rename(columns=df.iloc[0]).iloc[1:]
        return df
    def loadDataForPlanet(self, planetName):
        CAPSplanetName = planetName.upper()
        return self.NASAplanetData.loc[CAPSplanetName]
    #get alt and az of planet by name time and location and store in obj
    def getPlanetObj(self, planetName, time, location):
        apparent = location.at(time).observe(self.planetCodes[planetName]).apparent()
        alt, az, distance = apparent.altaz()
        planetInfo = self.loadDataForPlanet(planetName) 
        planetData = Planet(self.planetList[planetName], planetName, alt, az, distance, self.planetMagnitudes[planetName], self.planetCodes[planetName], planetInfo['Mass (1024kg) '], planetInfo['Diameter (km) ']
        , planetInfo['Density (kg/m3) '], planetInfo['Gravity (m/s2) '], planetInfo['Escape Velocity (km/s) '], planetInfo['Rotation Period (hours) '], planetInfo['Mean Temperature (C) '], planetInfo['Number of Moons '], planetInfo['Ring System? '])
        return planetData
    #toggle planet selection by number
    def togglePlanetSelection(self, number):
        if number in self.selectedPlanets:
            self.selectedPlanets.remove(number)
        else:
            self.selectedPlanets.append(number)
    #get string names of all selected planet numbers
    def getSelectedPlanets(self):
        for number in self.selectedPlanets:
            for planet in self.planetNameList:
                if self.planetList[planet] == number:
                    yield planet
    #get planet objects of all selected planets using string names function
    def getSelectedPlanetsObjs(self, time, location):
        planets = []
        for planet in self.getSelectedPlanets():
            if planet != None:
                planets.append(self.getPlanetObj(planet, time, location))
        return planets
    #get all planet objects of selected planets which are visible at time and location
    def getVisiblePlanets(self, time, location):
        planets = []
        for planet in self.getSelectedPlanets():
            if planet != None:
                planetObj = self.getPlanetObj(planet, time, location)
                if planetObj.alt > 0:
                    planets.append(planetObj)
        planets = normalizeListMagnitudes(planets)
        return planets