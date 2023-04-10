import pygame
import math
import time
black = 0, 0, 0
white = 255, 255, 255
width = 3840
height = 2160
pygame.init()
myfont = pygame.font.SysFont("monospace", 32)
class GridPlotter:
    def __init__(self, screen, PixelsPerInch):
        self.screen = screen
        self.PPI = PixelsPerInch
        self.graphColor = [0, 255, 0]
        self.starColor = white
        self.lines = 2
    def addStarToMap(self, star):
        self.starsToMap.append(star)

    def calcPointOnCircle(self, t, r, h=width/2, k=height/2):
        x = r*math.cos(math.radians(-t-90)) + h
        y = r*math.sin(math.radians(-t-90)) + k
        return (x, y)
    def calcPointOnCircleAndOpp(self, t, r, h=width/2, k=height/2):
        x = r*math.cos(t) + h
        y = r*math.sin(t) + k
        t += math.radians(180)
        x1 = r*math.cos(t) + h
        y1 = r*math.sin(t) + k
        return [(x, y), (x1, y1)]
    def plotGraph(self, state):
        if state > 0:
            pygame.draw.circle(self.screen, self.graphColor, (width/2, height/2), self.PPI*1, 1)
            pygame.draw.circle(self.screen, self.graphColor, (width/2, height/2), self.PPI*3, 1)
            pygame.draw.circle(self.screen, self.graphColor, (width/2, height/2), self.PPI*5, 1)
            pygame.draw.circle(self.screen, self.graphColor, (width/2, height/2), self.PPI*7, 1)
            pygame.draw.circle(self.screen, self.graphColor, (width/2, height/2), self.PPI*9, 1)
    def plotGraphLines(self, state):
        if state > 1:
            ang = self.calcPointOnCircleAndOpp(0, self.PPI*9)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(60), self.PPI*9)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(120), self.PPI*9)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
        if state > 2:
            ang = self.calcPointOnCircleAndOpp(math.radians(30), self.PPI*7)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(90), self.PPI*7)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(150), self.PPI*7)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
        if state > 3:
            ang = self.calcPointOnCircleAndOpp(math.radians(15), self.PPI*5)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(45), self.PPI*5)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(75), self.PPI*5)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(105), self.PPI*5)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(135), self.PPI*5)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
            ang = self.calcPointOnCircleAndOpp(math.radians(165), self.PPI*5)
            pygame.draw.line(self.screen, self.graphColor, ang[0], ang[1])
    def plotLabels(self, state, star=None):
        #AZIMUTH
        #label wide rotations EW
        if star != None:
            if star.name != 'nan':
                northLabel = f'0° N relative to {star.name}'
            elif star.name == 'nan':
                northLabel = f'0° N relative to {star.ID}'
        else:
            northLabel = '0° N'
        if state > 4:
            ang = self.calcPointOnCircleAndOpp(0, self.PPI*9)

            label = myfont.render('270° W', 1, (255,255,0))
            self.screen.blit(label, (ang[0][0] + 7, ang[0][1] - 19))

            label = myfont.render('90° E', 1, (255,255,0))
            self.screen.blit(label, (ang[1][0] - 130, ang[1][1] - 19))
            #NS
            ang = self.calcPointOnCircleAndOpp(math.radians(90), self.PPI*9)

            label = myfont.render('180° S', 1, (255,255,0))
            self.screen.blit(label, (ang[0][0]-8, ang[0][1]))

            label = myfont.render(northLabel, 1, (255,255,0))
            self.screen.blit(label, (ang[1][0], ang[1][1]-40))
        #ALTITUDE
        if state > 5:
            ang = self.calcPointOnCircle(-45, self.PPI*9)
            label = myfont.render('0° Alt', 1, (255,255,0))
            self.screen.blit(label, (ang[0], ang[1]))

            ang = self.calcPointOnCircle(-45, self.PPI*7)
            label = myfont.render('20°', 1, (255,255,0))
            self.screen.blit(label, (ang[0], ang[1]))

            ang = self.calcPointOnCircle(-45, self.PPI*3)
            label = myfont.render('60°', 1, (255,255,0))
            self.screen.blit(label, (ang[0], ang[1]))

            ang = self.calcPointOnCircle(-45, self.PPI*0)
            label = myfont.render('90°', 1, (255,255,0))
            self.screen.blit(label, (ang[0], ang[1]))


    def plotStarList(self, list, symbol="none"):
        for star in list:
            if star.symbol == symbol:
                color = [0,0,255]
            #! COLOR SOMETHING IF TOGGLE?
            elif star.name != "nan":
                color = [225,255,255]
            else:
                color = [255,255,255]
            self.plotStar(star, color)

    def plotStar(self, star, color):
        if star.alt < 0:
            star.setLoc((-99,-99))
            return "Below Horizon"
        else:
            rad = 9 - (star.alt / 10.0)
            az = star.az
            ang = self.calcPointOnCircle(az, self.PPI*rad)
            star.setLoc(ang)
            pygame.draw.circle(self.screen, color, ang, 8*star.normMagnitude + 2)
    
    def plotPlanetList(self, list):
        for planet in list:
            self.plotPlanet(planet)
    def plotMessierList(self, list):
        for messier in list:
            self.plotPlanet(messier, [255,0,255])
    def plotPlanet(self, planet, color=[255,165,0]):
        rad = 9 - (planet.alt / 10.0)
        az = planet.az
        ang = self.calcPointOnCircle(az, self.PPI*rad)
        planet.setLoc(ang)
        pygame.draw.circle(self.screen, color, ang, 12*planet.normMagnitude + 2)
            
    def update(self, state):
        self.screen.fill([0,0,0])
        self.plotGraph(state)
        self.plotGraphLines(state)
        self.plotLabels(state)
    def updateGraphLines(self, decrement=False):
        if decrement:
            self.lines -=1
        if self.lines == -1:
            self.lines = 2
        self.screen.fill(black)
        if self.lines == 2:
            self.plotGraph()
            self.plotGraphLines()
        elif self.lines == 1:
            self.plotGraph()