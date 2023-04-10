from skyfield.api import Star as SkyStar, load
from skyfield.data import hipparcos
from data.Star import Star
import threading
import queue
from util import normalizeListMagnitudes
class StarSelector:
    def __init__(self, df=None):
        self.df = df
        if isinstance(df, type(None)):
            with load.open(hipparcos.URL) as f:
                self.df = hipparcos.load_dataframe(f)
            self.df = self.df[self.df['ra_degrees'].notnull()] 
        starNames = open('./data/stars', 'r', encoding="utf-8")
        constNames = open('./data/constellations', 'r', encoding="utf-8")
        constStars = open('./data/constellationship', 'r', encoding='utf-8')
        
        self.THREADS  = 500
        self.queue = queue.Queue()

        self.nameDict = {}
        self.constellNameDict = {}
        self.starConstellDict = {}
        #make dict of star ids and names
        for line in starNames.readlines():
            line = line.split('|')
            starId = int(line[0])
            name = self.getBetween('"', line[1])
            self.nameDict[starId] = name
        #make dict of contellation ids and names
        for line in constNames.readlines():
            line = line.split('\t')
            symbol = line[0]
            name = line[1][1:-1]
            self.constellNameDict[symbol] = name
        #make dict of star ids and constellation names
        for line in constStars.readlines():
            line = line.split(' ')
            symbol = line[0]
            line = line[2:]
            for code in line:
                self.starConstellDict[int(code)] = symbol
    # helper func to get string between symbols for const and star tables
    def getBetween(self, symbol, string):
        start = string.index(symbol) + 1
        end = string.index(symbol, start)
        return string[start:end]
    #! NEED TO RETURN NONE IF NONE ARE FOUND
    def selectStarByNameOrId(self, nameOrId, location, time):
        tempStars = self.df
        starDf = []
        if not str(nameOrId).isdigit():
            for code, star in self.nameDict.items():
                if star == nameOrId:
                    starDf = tempStars.loc[code, :]
                    break
        elif str(nameOrId).isdigit():
            starDf = self.df.loc[int(nameOrId), :]
        if len(starDf) > 0:
            starObj = SkyStar.from_dataframe(starDf)
            #calculate apparent alt az and dist at t from loc
            apparent = location.at(time).observe(starObj).apparent()
            alt, az, distance = apparent.altaz()
            
            mag = starDf['magnitude']
            id = int(starDf.name)
            try:
                name = self.nameDict[id]
            except:
                name = "nan"
            try:
                symbol = self.starConstellDict[id]
                constell = self.constellNameDict[symbol]
            except:
                symbol = "nan"
                constell = "nan"
            return Star(id, name, constell, symbol, mag, alt, az, distance, starObj)
        else:
            return None

    def selectStarsByConstellations(self, time, location, constellations, starsToMap=[]):
        tempStars = self.df[self.df["magnitude"] <= 12]
        for index, star in tempStars.iterrows():
            starObj = SkyStar.from_dataframe(tempStars.loc[index])
            id = int(star.name)

            try:
                symbol = self.starConstellDict[id]
                constell = self.constellNameDict[symbol]
            except:
                symbol = "nan"
                constell = "nan"
            if symbol not in constellations:
                continue
            else:
                pass
            #calculate apparent alt az and dist at t from loc
            apparent = location.at(time).observe(starObj).apparent()
            alt, az, distance = apparent.altaz()
            
            mag = star['magnitude']
            try:
                name = self.nameDict[id]
            except:
                name = "nan"
            starsToMap.append(Star(id, name, constell, symbol, mag, alt, az, distance, starObj))
        starsToMap = normalizeListMagnitudes(starsToMap)
        return starsToMap
    #select stars by magnitude and return list of star objects using threading and queue
    def selectStarsByMagnitudeWithBatching(self, filter, time, location):
        tempStars = self.df[self.df["magnitude"] <= filter]
        threads = []
        for batch in self.batch(tempStars):
            threads.append(threading.Thread(target=self.calculateDataForListOfStars, args=(time, location, batch)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        starsToMap = []
        while not self.queue.empty():
            starsToMap.append(self.queue.get())
        starsToMap = normalizeListMagnitudes(starsToMap)
        return starsToMap
    # batch list of stars for multiprocessing
    def batch(self, l):
        if self.THREADS > len(l):
            batches = len(l)
        else:
            batches = self.THREADS
        batchSize = len(l) // batches
        for i in range(0, len(l), batchSize):
            yield l[i:i + batchSize]
    #calculate apparent alt az and dist at t from loc for a list of stars
    def calculateDataForListOfStars(self, time, location, starsToMap):
        for index, star in starsToMap.iterrows():
            starObj = SkyStar.from_dataframe(starsToMap.loc[index])
            apparent = location.at(time).observe(starObj).apparent()
            alt, az, distance = apparent.altaz()
            mag = star['magnitude']
            id = int(star.name)
            try:
                name = self.nameDict[id]
            except:
                name = "nan"
            try:
                symbol = self.starConstellDict[id]
                constell = self.constellNameDict[symbol]
            except:
                symbol = "nan"
                constell = "nan"
            self.queue.put(Star(id, name, constell, symbol, mag, alt, az, distance, starObj))
            

    def selectStarsByMag(self, filter, time, location):
        #select all stars less than magnitude filter
        tempStars = self.df[self.df["magnitude"] <= filter]
        starsToMap = []

        for index, star in tempStars.iterrows():
            starObj = SkyStar.from_dataframe(tempStars.loc[index])
            #calculate apparent alt az and dist at t from loc
            apparent = location.at(time).observe(starObj).apparent()
            alt, az, distance = apparent.altaz()
            
            mag = star['magnitude']
            id = int(star.name)
            try:
                name = self.nameDict[id]
            except:
                name = "nan"
            try:
                symbol = self.starConstellDict[id]
                constell = self.constellNameDict[symbol]
            except:
                symbol = "nan"
                constell = "nan"
            starsToMap.append(Star(id, name, constell, symbol, mag, alt, az, distance, starObj))
        starsToMap.reverse()

        starsToMap = normalizeListMagnitudes(starsToMap)
        return starsToMap
