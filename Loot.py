import pygame
from settings import *


class Loot(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/map/details/skull.png')
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, HITBOX_OFFSET['loot'])
        self.sprite_type = 'loot'

        # list of loot
        self.loot = [['Take All x1', 'Take All'], ['lance x1', 'weapon'], ['steel x1', 'armor'],
                     ['sword x2', 'weapon'], ['gold x100', 'gold'], ['lunch money x1', 'quest'], ['Exit x1', 'Exit']]
