import pygame, sys
from settings import *
from level import Level
from GameHandler import GameHandler


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('Skyrim 2D')
        self.clock = pygame.time.Clock()

        # self.level = Level()
        self.gameHandler = GameHandler()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        #self.level.toggle_menu()
                        self.gameHandler.toggle_menu()

            self.screen.fill('black')
            self.gameHandler.run()
            #self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()