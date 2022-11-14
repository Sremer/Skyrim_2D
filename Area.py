import pygame
from settings import *


class Area:
    def __init__(self, area_num, vertical_change, horizontal_change):
        self.area_num = area_num

        self.vertical_change = vertical_change
        self.horizontal_change = horizontal_change

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.npc_sprites = pygame.sprite.Group()
        self.friendly_sprites = pygame.sprite.Group()

        # attack sprites
        self.attackable_sprites = pygame.sprite.Group()

    def load_area(self):
        pass

    def unload_area(self):
        pass

    def draw(self, player):
        self.visible_sprites.custom_draw(player, self.vertical_change, self.horizontal_change)

    def update(self, player):
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(player)
        self.visible_sprites.npc_update(player)
        self.visible_sprites.summoned_update(player)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load('graphics/test_area.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def change_floor(self, new_floor):
        self.floor_surf = pygame.image.load(f'graphics/{new_floor}.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player, vertical_change, horizontal_change):
        # getting the offset
        self.offset.x = player.rect.centerx - (self.half_width * horizontal_change)
        self.offset.y = player.rect.centery - (self.half_height * vertical_change)

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)

    def npc_update(self, player):
        npc_sprites = [sprite for sprite in self.sprites() if
                       hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'npc']
        for npc in npc_sprites:
            npc.npc_update(player)

    def summoned_update(self, player):
        summoned_sprites = [sprite for sprite in self.sprites() if
                       hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'summoned']
        for summoned in summoned_sprites:
            summoned.summoned_update(player)
