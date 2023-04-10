import math
import copy
class Telescope:
    def __init__(self, apertureMM, focalLengthMM):
        self.aperture = apertureMM
        self.focalLength = focalLengthMM
        self.focalRatio = self.focalLength / self.aperture
    def calculateMagnification(self, eyepieceFocalLengthMM):
        return self.focalLength / eyepieceFocalLengthMM
    def calculateExitPupil(self, eyepieceFocalLengthMM):
        return self.aperture/self.calculateMagnification(eyepieceFocalLengthMM)
    def calculateFOV(self, eyepieceFocalLengthMM, eyepieceAFOV):
        return eyepieceAFOV / self.calculateMagnification(eyepieceFocalLengthMM)
    def calculateFOVAltAzRanges(self, eyepieceFocalLengthMM, eyepieceAFOV, centerAlt, centerAz):
        halfFOV = self.calculateFOV(eyepieceFocalLengthMM, eyepieceAFOV)/2
        if centerAlt-halfFOV < 0:
            lowerAltFov = 0
        else:
            lowerAltFov = centerAlt-halfFOV
        if centerAlt+halfFOV > 90:
            upperAltFov = 90
        else:
            upperAltFov = centerAlt+halfFOV
        if centerAz - halfFOV < 0:
            lowerAzFov = 360 + (centerAz - halfFOV)
        else:
            lowerAzFov = centerAz - halfFOV
        if centerAz + halfFOV > 360:
            upperAzFov = (centerAz + halfFOV) - 360
        else:
            upperAzFov = centerAz + halfFOV
        return [[lowerAltFov, upperAltFov], [lowerAzFov, upperAzFov]]
    def calcPointOnCircle(self, t, r, h=3840/2, k=2160/2):
        x = r*math.cos(math.radians(-t-90)) + h
        y = r*math.sin(math.radians(-t-90)) + k
        return (x, y)
    def getAngle(self, a, b, c):
        ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
        return 360 + ang if ang < 0 else ang
    def getScaledStarCoords(self, fov, magnification, object, center):
        object = copy.copy(object)
        halfFov = fov/2
        #after subtracting center all should be less than half fov
        newAlt = center.alt - object.alt
        newAlt = abs(newAlt)
        newAlt = newAlt/halfFov
        newAlt = 90 - newAlt * 90
        objectLocation = object.loc
        centerLocation = center.loc
        northLocation = [centerLocation[0], centerLocation[1] - 100]
        newObjectAzimuth = 360 - self.getAngle(northLocation, centerLocation, objectLocation)
        #print(f'center.az: {center.az}, object.az: {object.az}, center.x {center.loc[0]}, center.y {center.loc[1]}, object.x: {object.loc[0]}, object.y: {object.loc[1]}')
        #print(f'newObjectAzimuth: {newObjectAzimuth} | newAlt: {newAlt}')
        object.normMagnitude = object.normMagnitude * magnification/2
        object.alt = newAlt
        object.az = newObjectAzimuth
        return object
    def plotListOfStarsScaled(self, graphState, GridPlotter, listOfStars, fov, magnification, center):
        GridPlotter.screen.fill((0,0,0))
        GridPlotter.plotGraph(graphState)
        GridPlotter.plotGraphLines(graphState)
        GridPlotter.plotLabels(graphState, center)
        for star in listOfStars:
            star = self.getScaledStarCoords(fov, magnification, star, center)
            GridPlotter.plotStar(star, [255,255,255])

        

        
