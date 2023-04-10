class Star:
    def __init__(self, id, name, constellation, symbol, mag, alt, az, dist, starObj):
        self.loc = []
        self.name = name
        self.objType = 'star'
        self.constellation = constellation
        self.symbol = symbol
        self.ID = id
        self.az = az.degrees
        self.alt = alt.degrees
        self.distance = dist
        self.magnitude = mag
        self.starObj = starObj
    def setLoc(self, loc):
        self.loc = loc
""" def info(self):
        dist = 'Distance: {:,.2f} AU '.format(self.distance.au) + '| {:,.2f} ly'.format(self.distance.m/9460730472580800)
        infoLst = [f'HYG ID: {self.ID}', f'Name: {self.name}', f'Magnitude: {self.magnitude}', dist, f'Member of Constellation: {self.constellation} | {self.symbol}']
        offset = 0
        for txt in infoLst:
            label = myfont.render(txt, 1, (255,255,0))
            screen.blit(label, (100, 100 + offset))
            offset += 40
        #print(f'Right Ascension: {self.ra}\nDeclination: {self.declination}') """
