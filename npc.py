import pygame
from settings import *
from entity import Entity

class NPC(Entity):
    def __init__(self, groups, name, sprite_type, obstacle_sprites):
        super().__init__(groups)
        self.name = name
        self.sprite_type = sprite_type

        # sprite groups
        self.obstacle_sprites = obstacle_sprites
