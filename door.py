import pygame
from tile import Tile
from settings import *


class Door(Tile):
    def __init__(self, pos, groups, sprite_type, door_num, player, load_area, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(pos, groups, sprite_type, surface)
        self.door_num = door_num

        # general
        self.player = player
        self.load_area = load_area

    def check_collision(self):
        if self.player.hitbox.colliderect(self.hitbox):
            if self.player.hitbox.y < self.hitbox.y:
                offset = -64
            else:
                offset = 64

            self.load_area(self.door_num, (self.hitbox.x, self.hitbox.y))

    def update(self):
        self.check_collision()
