import pygame


class NPCHandler:
    def __init__(self, the_map, player):

        self.map = the_map

        self.player = player

        self.npc_sprites = self.map[self.player.curr_area_num].npc_sprites

