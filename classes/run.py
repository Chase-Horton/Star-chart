from GraphController import GraphController
from pygame.locals import *
from datetime import datetime
import pygame
class pygameController:
    def __init__(self):
        self.currentInput = ""
        self.promptString = ""
        self.capturingInput = False

    def displayInput(self):
        self.G.fastRefresh()
        self.G.updateInfoText()

        font = pygame.font.SysFont("monospace", 32)
        text = font.render(self.promptString + self.currentInput, True, (255, 255, 255))
        self.G.screen.blit(text, (2300, 2128))

    def toggleInput(self, promptString=""):
        self.capturingInput = not self.capturingInput
        self.currentInput = ""
        self.promptString = promptString

    def run_game(self):
        self.G = GraphController()
        start = datetime.now()
        self.G.refresh()
        end = datetime.now()
        print('Time to draw stars: ', end - start)
        while True:
            pygame.display.update()
            self.G.updateInfoText()
            events = pygame.event.get()
            if self.capturingInput:
                for event in events:
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            #return
                            self.G.handleInput(self.currentInput)
                            self.toggleInput()
                        elif event.key == K_BACKSPACE:
                            self.currentInput = self.currentInput[:-1]
                            self.displayInput()
                        else:
                            self.currentInput += event.unicode
                            self.displayInput()
            else:
                start = False
                for event in events:
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            self.toggleInput("Enter an objects name: ")
                            self.displayInput()
                            start = True
                if not start:
                    self.G.handleKeys(events)

P = pygameController()
P.run_game()