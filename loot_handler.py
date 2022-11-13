import pygame
from loot_menu import LootMenu
from Loot import Loot


class LootHandler:
    def __init__(self, the_map, player):

        self.player = player

        self.map = the_map

        self.loot_paused = False
        self.loot_menu = LootMenu(self.player)

        self.loot_sprites = pygame.sprite.Group()
        self.current_loot_sprite = None

    def create_loot(self, pos):
        Loot(pos, [self.map[self.player.curr_area_num].visible_sprites, self.map[self.player.curr_area_num].obstacle_sprites, self.loot_sprites])

    def show_loot(self, loot_sprite):
        self.loot_paused = True
        self.current_loot_sprite = loot_sprite

    def loot_pause(self):
        self.loot_paused = self.loot_menu.display(self.current_loot_sprite)
        if not self.loot_paused:
            self.current_loot_sprite.kill()

    def loot_player_collision(self):
        for sprite in self.loot_sprites:
            if sprite.hitbox.colliderect(self.player.hitbox):
                self.show_loot(sprite)