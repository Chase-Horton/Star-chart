import pandas as pd
from StarSelector import StarSelector
from skyfield.api import load, wgs84

class ConstellationLoader:
    def __init__(self):
        self.df = pd.read_csv('data/constellationLines.csv')
        self.StarSelector = StarSelector()

    def addConstellationToDf(self, constellation):
        lines = constellation.lines
        name = constellation.name
        symbol = constellation.symbol
        for i in range(len(lines)):
            line = lines[i]
            for i, row in self.df.iterrows():
                if row['star1ID'] == line.star1Pos.ID and row['star2ID'] == line.star2Pos.ID:
                    self.df.drop(i, inplace=True)
            newRow =  pd.DataFrame([[line.star1Pos.ID, line.star2Pos.ID, name, symbol]], columns=['star1ID', 'star2ID', 'name', 'symbol'])
            self.df = pd.concat([self.df, newRow])
    
    def loadConstellationWithPosFromDf(self, nameOrSymbol, visibleStars):
        #printed loaded lines
        #print(self.df)
        lines = []
        name = None
        symbol = None
        #for row in dataframe, if name or symbol matches constellation name, add linepair to "lines"
        for i, row in self.df.iterrows():
            if row['name'] == nameOrSymbol or row['symbol'] == nameOrSymbol:
                name = row['name']
                symbol = row['symbol']
                lines.append([row['star1ID'], row['star2ID']])
        #if no name or symbol, return None
        if name == None or symbol == None:
            return None
        #for each linepair, add id to "starsToLoad" if not already in list
        starsToLoad = []
        for starPair in lines:
            if starPair[0] not in starsToLoad:
                starsToLoad.append(starPair[0])
            if starPair[1] not in starsToLoad:
                starsToLoad.append(starPair[1])
        #if no stars to load, return None
        if len(starsToLoad) == 0:
            return None
        #for each star in "starsToLoad", find star in "visibleStars" and add starPos to "starPosDict"
        starPosDict = {}
        for starID in starsToLoad:
            for visibleStar in visibleStars:
                if visibleStar.ID == starID:
                    if visibleStar.alt > 0:
                        starPos = visibleStar.loc
                        starPosDict[starID] = starPos
        #if no visible stars, return None
        if len(starPosDict) == 0:
            return None
        #for each linepair, if both stars are in "starPosDict", add line to "lines"
        visibleLines = []
        for starPair in lines:
            star1ID = starPair[0]
            star2ID = starPair[1]
            if star1ID in starPosDict and star2ID in starPosDict:
                star1Pos = starPosDict[starPair[0]]
                star2Pos = starPosDict[starPair[1]]
                line = ConstellationLine([star1Pos, star2Pos])
                visibleLines.append(line)
        #return constellation with name, symbol, and lines
        return Constellation(name, symbol, visibleLines)

    def loadAllVisibleConstellations(self, visibleStars):
        names = []
        for i, row in self.df.iterrows():
            if row['name'] not in names:
                names.append(row['name'])
        constellations = []
        for name in names:
            constellation = self.loadConstellationWithPosFromDf(name, visibleStars)
            if constellation != None:
                constellations.append(constellation)
        if len(constellations) == 0:
            return None
        return constellations

class Constellation:
    def __init__(self, name, symbol, lines):
        self.name = name
        self.symbol = symbol
        self.lines = lines

class ConstellationLine:
    def __init__(self, TwoStars):
        self.pos1 = TwoStars[0]
        self.pos2 = TwoStars[1]
        self.color = (0, 0, 255)
        self.width = 3
class Line:
    def __init__(self, pos1, pos2, color, width):
        self.pos1 = pos1
        self.pos2 = pos2
        self.color = color
        self.width = width

""" S1 = lambda:None
S2 = lambda:None
S1.loc = [0,0]
S1.ID = 1
S2.loc = [1,4]
S2.ID = 4
line1 = ConstellationLine([S1, S2])
UMa = Constellation("Ursa Major", "UMa", [line1])
C.addConstellationToDf(UMa) """