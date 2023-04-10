import pandas as pd
from data.MessierObj import Messier
from skyfield.api import Star, load, wgs84
from util import normalizeListMagnitudes
class MessierSelector:
    def __init__(self):
        self.messier = pd.read_csv('data/catalogue-de-messier.csv', sep=';')
        self.messierNames = pd.read_csv('data/messier-names.csv')
        self.messierLocations = pd.read_csv('data/messier-locations.csv')

        self.messierObjects = []
        #create list of Messier objects
        for _, row in self.messier.iterrows():
            Mcode = row['Messier']
            NGC = row['NGC']
            objType = self.messierLocations.loc[self.messierLocations['Name'] == Mcode]['Class'].values[0]
            magnitude = row['Magnitude']
            constellation = row['Constellation (EN)']
            ra = row['RA (Right Ascension)']
            decl = row['Dec (Declinaison)']
            distance = row['Distance (l.y / a. l.)']
            size = row['Size / Dimensions']
            discoverer = row['Discoverer / Découvreur']
            yearDiscovered = row['Year / Année']
            imageUrl = row['Image']
            NGCName = self.messierNames.loc[self.messierNames['M'] == Mcode]['NGC'].values[0]
            if NGCName == NGC:
                NGCName = None
            
            if not isinstance(ra, str):
                ra = self.messierLocations.loc[self.messierLocations['Name'] == Mcode]['Right ascension'].values[0]
                ra = ra.split("h")
                ra[1] = ra[1].replace("m", "")
                ra[1] = ra[1].replace(" ", "")
                ra = [float(ra[0]), float(ra[1])]
                decl = self.messierLocations.loc[self.messierLocations['Name'] == Mcode]['Declination'].values[0]
                decl = decl.split("°")
                decl[1] = decl[1].replace("'", "")
                decl[1] = decl[1].replace(" ", "")
                decl = [float(decl[0]), float(decl[1])]
            
            self.messierObjects.append(Messier(Mcode, NGC, NGCName, ra, decl, magnitude, distance, size, objType, constellation, yearDiscovered, discoverer, imageUrl))
    #get messier object by Mcode
    def getMessierObj(self, MCode):
        for obj in self.messierObjects:
            if obj.MCode == MCode:
                return obj
    #get messier alt az by MCode for time and location
    def getMessierAltAz(self, MCode, time, location):
        messierObj = self.getMessierObj(MCode)
        messierLocation = Star(ra_hours=(messierObj.ra[0], messierObj.ra[1], messierObj.ra[2]), dec_degrees=(messierObj.dec[0], messierObj.dec[1], messierObj.dec[2]))

        apparent = location.at(time).observe(messierLocation)
        alt, az, trash =  apparent.apparent().altaz()
        return alt, az
    
    #get all visible messier objects with alt Az for time and location
    def getVisibleMessierObjects(self, time, location):
        visibleMessier = []
        for obj in self.messierObjects:
            alt, az = self.getMessierAltAz(obj.MCode, time, location)
            if alt.degrees > 0:
                obj.alt = alt.degrees
                obj.az = az.degrees
                visibleMessier.append(obj)
        visibleMessier = normalizeListMagnitudes(visibleMessier)
        return visibleMessier
    #get all messier objects with alt az for time and location
    def getAllMessierObjects(self, time, location):
        allMessier = []
        for obj in self.messierObjects:
            alt, az = self.getMessierAltAz(obj.MCode, time, location)
            obj.alt = alt.degrees
            obj.az = az.degrees
            allMessier.append(obj)
        allMessier = normalizeListMagnitudes(allMessier)
        return allMessier