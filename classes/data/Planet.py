class Planet:
    def __init__(self, id, name, alt, az, dist, magnitude, planetObj, mass, diameter, density, gravity, escape, rotation, avgTemp, numMoons, rings):
        self.loc = []
        self.name = name
        self.objType = 'planet'
        self.ID = id
        self.magnitude = magnitude
        self.az = az.degrees
        self.alt = alt.degrees
        self.distance = dist
        self.starObj = planetObj
        #info
        self.mass1024 = float(mass.strip().replace(',', ''))
        self.diameter = float(diameter.strip().replace(',', ''))
        self.density = float(density.strip().replace(',', ''))
        self.gravity = float(gravity.strip().replace(',', ''))
        self.escape = float(escape.strip().replace(',', ''))
        self.rotation = float(rotation.strip().replace(',', ''))
        self.avgTemp = float(avgTemp.strip().replace(',', ''))
        self.numMoons = int(numMoons.strip().replace(',', ''))
        self.rings = bool(rings)
    #set x,y coords on graph
    def setLoc(self, loc):
        self.loc = loc
    #return info string
    def info(self):
        return f'Name: {self.name}\nAltitude: {self.alt}\nAzimuth: {self.az}\nDistance: {self.distance}\nMagnitude: {self.magnitude}'