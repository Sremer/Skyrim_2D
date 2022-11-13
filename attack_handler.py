import pygame
from settings import *
from weapon import Weapon, Bow
from projectile import Projectile, LongShotArrow, Target
from random import randint


class AttackHandler:
    def __init__(self, the_map, player, magic_player, animation_player, vertical_change, horizontal_change):

        self.display_surface = pygame.display.get_surface()

        self.map = the_map

        self.player = player

        self.magic_player = magic_player

        self.animation_player = animation_player

        self.current_attack = []
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = self.map[self.player.curr_area_num].attackable_sprites

        self.target_sprite = pygame.sprite.Group()
        self.projectiles_to_remove = []
        self.vertical_change = vertical_change
        self.horizontal_change = horizontal_change

    def get_full_weapon_damage(self):
        base_damage = self.player.stats['attack']
        weapon_damage = weapon_data[self.player.current_weapon]['damage']

        class_damage = 0
        if weapon_data[self.player.current_weapon]['type'] in list(class_data[self.player.class_type]['multipliers'].keys()):
            class_damage += int(weapon_data[self.player.current_weapon]['damage'] * class_data[self.player.class_type]['multipliers'][weapon_data[self.player.current_weapon]['type']])

        return base_damage + weapon_damage + class_damage

    def get_full_magic_damage(self):
        base_damage = self.player.stats['magic']
        spell_damage = magic_data[self.player.magic]['strength']
        return base_damage + spell_damage

    def get_full_summoned_damage(self):
        return summoned_data['skeleton']['damage']

    def get_full_bow_damage(self, arrow_type):
        if arrow_type == 'arrow':
            return weapon_data[self.player.weapon]['damage'] + 10
        else:
            return (weapon_data[self.player.weapon]['damage'] + 10) * 2

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.map[self.player.curr_area_num].visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.map[self.player.curr_area_num].visible_sprites, self.attack_sprites])

        if style == 'invisibility':
            self.magic_player.invisibility(self.player, cost, [self.map[self.player.curr_area_num].visible_sprites])

        if style == 'defense up':
            self.magic_player.defense_up(self.player, strength, cost, [self.map[self.player.curr_area_num].visible_sprites])

        if style == 'lightning':
            self.magic_player.lightning(self.player, cost, [self.map[self.player.curr_area_num].visible_sprites, self.attack_sprites])

        if style == 'summon':
            self.magic_player.summon(self.player, cost, [self.map[self.player.curr_area_num].visible_sprites, self.map[self.player.curr_area_num].friendly_sprites], self.map[self.player.curr_area_num].obstacle_sprites, self.attackable_sprites, 'skeleton', self.trigger_death_particles)

    def create_attack(self, hand):
        self.current_attack.append(Weapon(self.player, [self.map[self.player.curr_area_num].visible_sprites, self.attack_sprites], hand))

    def destroy_attack(self):
        if self.current_attack:
            for attack in self.current_attack:
                attack.kill()
        self.current_attack = []

    def create_bow(self):
        self.current_attack.append(Bow(self.player, [self.map[self.player.curr_area_num].visible_sprites], 'bow'))

    def draw_bow(self, new_status):
        self.current_attack[0].status = new_status

    def create_arrow(self, range, type='arrow'):
        if type == 'arrow':
            Projectile(self.player, [self.map[self.player.curr_area_num].visible_sprites, self.attack_sprites], type, self.map[self.player.curr_area_num].obstacle_sprites, self.attackable_sprites, self.projectiles_to_remove, range)
        elif type == 'long shot':
            LongShotArrow(self.player, [self.map[self.player.curr_area_num].visible_sprites, self.attack_sprites], self.map[self.player.curr_area_num].obstacle_sprites,
                          self.attackable_sprites, self.target_sprite, self.projectiles_to_remove, self.vertical_change, self.horizontal_change)

    def create_smash(self):
        self.magic_player.ground_smash(self.player, [self.map[self.player.curr_area_num].visible_sprites, self.attack_sprites])

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.map[self.player.curr_area_num].visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            class_bonus = 0
            if armor_data[self.player.armor_type]['type'] in list(class_data[self.player.class_type]['multipliers'].keys()):
                class_bonus += int(
                    armor_data[self.player.armor_type]['defense'] * class_data[self.player.class_type]['multipliers'][
                        armor_data[self.player.armor_type]['type']])

            self.player.health -= (amount - armor_data[self.player.armor_type]['defense']
                                   - class_bonus - self.player.defense_up_bonus)
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.map[self.player.curr_area_num].visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.map[self.player.curr_area_num].visible_sprites)

    def add_exp(self, amount):
        self.player.exp += amount

    # projectile logic

    def remove_projectiles(self):
        if self.projectiles_to_remove:
            for projectile in self.projectiles_to_remove:
                projectile.kill()

    def create_target(self):
        if not self.target_sprite:
            Target([self.target_sprite])

    def kill_target(self):
        if self.target_sprite:
            for sprite in self.target_sprite:
                sprite.kill()

    def draw(self):
        self.target_sprite.draw(self.display_surface)

    def update(self):
        self.target_sprite.update()
        self.player_attack_logic()
        self.remove_projectiles()
