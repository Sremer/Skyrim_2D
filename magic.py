import pygame
from settings import *
from random import randint


class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def defense_up(self, player, strength, cost, groups):
        if player.energy >= cost and not player.defense_up:
            player.defense_up = True
            player.defense_up_time = pygame.time.get_ticks()
            player.energy -= cost
            player.defense_up_bonus = int((strength - player.stats['magic']) * armor_data[player.armor_type]['defense'])
            print(player.defense_up_bonus)
            self.animation_player.create_particles('defense up', player.rect.center, groups)

    def invisibility(self, player, cost, groups):
        if player.energy >= cost and not player.invisible:
            player.visible = False
            player.invisible = True
            player.invisibility_time = pygame.time.get_ticks()
            player.energy -= cost
            player.image.set_alpha(200)
            self.animation_player.create_particles('smoke', player.rect.center, groups)

    def heal(self, player, strength, cost, groups):
        if player.energy >= cost:
            # self.sounds['heal'].play()
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats['health']:
                player.health = player.stats['health']
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0, -60), groups)

    def flame(self, player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
            # self.sounds['flame'].play()

            if player.status.split('_')[0] == 'right':
                direction = pygame.math.Vector2(1, 0)
            elif player.status.split('_')[0] == 'left':
                direction = pygame.math.Vector2(-1, 0)
            elif player.status.split('_')[0] == 'up':
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x: # horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), groups)
                else: # vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), groups)

    # abilities

    def ground_smash(self, player, groups):
        self.animation_player.create_particles('ground smash', player.rect.center + pygame.math.Vector2(0, 32), groups, 'smash')
