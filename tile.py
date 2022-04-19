import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.sprite_type = 'grass'
        y_offset = HITBOX_OFFSET[self.sprite_type]
        self.image = pygame.image.load('graphics/test/rock.png').convert_alpha()
        if self.sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, y_offset)
