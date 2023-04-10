import math
from MessierSelector import MessierSelector
from skyfield.api import load
class CoordinateCalc:
    def __init__(self, width, height, PPI):
        self.PPI = PPI
        self.width = width
        self.height = height

    def convertAltAzToXY(self, obj):
            rad = 9 - (obj.alt / 10.0)
            az = obj.az
            ang = self.calcPointOnCircle(az, self.PPI*rad)
            obj.setLoc(ang)

    def convertRADecToXY(self, obj, time, coords):
        long = coords[1]
        lat = coords[0]
        #convert ra decl
        if isinstance(obj.ra, list):
            ra = obj.ra[0] + obj.ra[1]/60 + obj.ra[2]/3600
        else:
            ra = obj.ra
        if isinstance(obj.dec, list):
            dec = obj.dec[0] + obj.dec[1]/60 + obj.dec[2]/3600
        else:
            dec = obj.dec
        #convert ra decl to alt az
        tai = time.tai_calendar()
        daysSinceJ2000 = (tai[0] - 2000) * 365.25 + (tai[1] - 1) * 30.4375 + tai[2]-0.5 + tai[3]/24 + tai[4]/1440 + tai[5]/86400
        print(f'Days since 2000: {daysSinceJ2000}')
        #get universal time
        UTC = time.utc
        print(f'UTC: {UTC}')
        UTC = UTC[3] + UTC[4]/60 + UTC[5]/3600
        #get local sidereal time
        LST = 100.46 + 0.985647 * daysSinceJ2000 + 15 * UTC + long
        while LST > 360:
            LST -= 360
        while LST < 0:
            LST += 360
        print(f'LST: {LST}')
        #get hour angle
        HA = LST - ra
        while HA > 360:
            HA -= 360
        while HA < 0:
            HA += 360
        print(f'HA: {HA}')
        #calculate altitude
        aAlt = math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(HA)
        alt = math.asin(aAlt)
        print(f'Altitude: {alt}')
        #calculate azimuth
        aAz = (math.sin(dec) - math.sin(alt) * math.sin(lat))
        az = math.acos(aAz / (math.cos(alt) * math.cos(lat)))
        if math.sin(HA) > 0:
            az = 360 - az
        print(f'Azimuth: {az}')

M = MessierSelector()
messier = M.getMessierObj("M25")
ts = load.timescale()
t = ts.now()
print(t)
C = CoordinateCalc(3840, 2160, 91)

C.convertRADecToXY(messier, t, [37.697948, -97.314835])