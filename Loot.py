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
        self.loot = [['Take All', 'Take All'], ['lance', 'weapon'], ['steel', 'armor'], ['sword', 'weapon']]
