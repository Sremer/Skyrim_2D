import pygame
from settings import *
from support import *
from tile import Tile
from player import Player
from random import choice, randint
from weapon import Weapon
from enemy import Enemy
from ui import UI
from particles import AnimationPlayer
from menu import Menu
from magic import MagicPlayer
from Loot import Loot
from loot_menu import LootMenu
from projectile import Projectile, Target, LongShotArrow
from npc import NPC, SpeechBox,Helper
from quest import QuestChecker
from text import TextGenerator


class Level:
    def __init__(self):

        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        self.vertical_change = 1
        self.horizontal_change = 1

        # NPC-Player interactions
        self.talking_paused = False

        # loot system
        self.loot_paused = False
        self.loot_menu = None

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.loot_sprites = pygame.sprite.Group()
        self.current_loot_sprite = None
        self.npc_sprites = pygame.sprite.Group()
        self.speech_box_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = []
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # projectile sprites
        self.projectiles_to_remove = []
        self.target_sprite = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()
        self.menu = Menu(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # quests
        self.quest_database = {}
        self.active_quests = []
        self.create_quest_database()
        self.quest_checker = QuestChecker(self.quest_database)

        # text generation
        self.text_generator = TextGenerator()

    # general

    def create_map(self):
        layout = {
            'grass': import_csv_layout('map/test_area_grass.csv'),
            'trees': import_csv_layout('map/test_area_trees.csv'),
            'entities': import_csv_layout('map/test_area_Entities.csv')
        }
        graphics = {
            'grass': import_folder('graphics/grass'),
            'objects': import_folder('graphics/objects')
        }

        for style, layout in layout.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites,
                                          self.obstacle_sprites,
                                          self.attackable_sprites],
                                 'grass', random_grass_image)

                        if style == 'trees':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)

                        if style == 'entities':
                            if col == '0':
                                self.player = Player((x, y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.attackable_sprites,
                                    self.loot_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic,
                                    self.show_loot,
                                    self.create_smash,
                                    self.create_bow,
                                    self.create_arrow,
                                    self.change_camera,
                                    self.create_target,
                                    self.kill_target,
                                    self.target_sprite,
                                    self.npc_sprites,
                                    self.create_speech)
                            elif col == '2':
                                NPC((x, y), [self.visible_sprites, self.npc_sprites], 'villager', 'npc', self.obstacle_sprites)

                            elif col == '3':
                                NPC((x, y), [self.visible_sprites, self.npc_sprites], 'man-bun', 'npc', self.obstacle_sprites)

                            else:
                                monster_name = 'squid'
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visible_sprites, self.attackable_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp,
                                    self.create_loot)

        # create loot menu
        self.loot_menu = LootMenu(self.player)

    # questing

    def create_quest_database(self):
        for quest in quest_master_database:
            self.quest_database[quest] = {
                'active': False,
                'finished': False,
                'done': False,
                'locked': bool(quest_master_database[quest]['prereq']),
                'type': quest_master_database[quest]['objective']['type'],
                'what': quest_master_database[quest]['objective']['what']
            }

    def start_quest(self, quest_name):
        self.quest_database[quest_name]['active'] = True
        self.active_quests.append(quest_name)
        self.text_generator.add_to_queue(quest_name + ' started')

    def finish_quest(self, quest_name):
        self.quest_database[quest_name]['active'] = False
        self.quest_database[quest_name]['finished'] = True
        self.active_quests.remove(quest_name)
        self.player.exp += quest_master_database[quest_name]['xp']
        self.text_generator.add_to_queue('+50 exp')
        self.player.money += quest_master_database[quest_name]['money']
        self.text_generator.add_to_queue('+100 gold')

        quest_type = self.quest_database[quest_name]['type']
        if quest_type == 'get':
            what = self.quest_database[quest_name]['what']
            self.player.quest_inventory.pop(what)

    # player actions

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

        if style == 'invisibility':
            self.magic_player.invisibility(self.player, cost, [self.visible_sprites])

        if style == 'defense up':
            self.magic_player.defense_up(self.player, strength, cost, [self.visible_sprites])

        if style == 'lightning':
            self.magic_player.lightning(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def create_attack(self, hand):
        self.current_attack.append(Weapon(self.player, [self.visible_sprites, self.attack_sprites], hand))

    def destroy_attack(self):
        if self.current_attack:
            for attack in self.current_attack:
                attack.kill()
        self.current_attack = []

    def create_bow(self):
        self.current_attack.append(Weapon(self.player, [self.visible_sprites], 'bow'))

    def create_arrow(self, range, type='arrow'):
        if type == 'arrow':
            Projectile(self.player, [self.visible_sprites, self.attack_sprites], type, self.obstacle_sprites, self.attackable_sprites, self.projectiles_to_remove, range)
        elif type == 'long shot':
            LongShotArrow(self.player, [self.visible_sprites, self.attack_sprites], self.obstacle_sprites,
                          self.attackable_sprites, self.target_sprite, self.projectiles_to_remove, self.vertical_change, self.horizontal_change)

    def create_smash(self):
        self.magic_player.ground_smash(self.player, [self.visible_sprites, self.attack_sprites])

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
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
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
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])
            print(self.player.health)

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def add_exp(self, amount):
        self.player.exp += amount

    # menus

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def level_up(self):
        if self.player.exp >= self.player.exp_to_level_up:
            self.player.level_up()
            self.menu.nr_level_ups += 1
            self.text_generator.add_to_queue('level up')

    def create_loot(self, pos):
        Loot(pos, [self.visible_sprites, self.obstacle_sprites, self.loot_sprites])

    def show_loot(self, loot_sprite):
        self.loot_paused = True
        self.current_loot_sprite = loot_sprite

    # projectile logic

    def remove_projectiles(self):
        if self.projectiles_to_remove:
            for projectile in self.projectiles_to_remove:
                projectile.kill()

    def change_camera(self, direction):
        rate = 0.025

        if direction:
            if direction == 'up':
                self.vertical_change += rate
                if self.vertical_change >= 2:
                    self.vertical_change = 2
            elif direction == 'down':
                self.vertical_change -= rate
                if self.vertical_change <= 0:
                    self.vertical_change = 0
            elif direction == 'right':
                self.horizontal_change -= rate
                if self.horizontal_change <= 0:
                    self.horizontal_change = 0
            else:
                self.horizontal_change += rate
                if self.horizontal_change >= 2:
                    self.horizontal_change = 2

        else:
            if self.vertical_change < (1 - rate):
                self.vertical_change += rate
            elif self.vertical_change > (1 + rate):
                self.vertical_change -= rate
            else:
                self.vertical_change = 1

            if self.horizontal_change < (1 - rate):
                self.horizontal_change += rate
            elif self.horizontal_change > (1 + rate):
                self.horizontal_change -= rate
            else:
                self.horizontal_change = 1

    def create_target(self):
        if not self.target_sprite:
            Target([self.target_sprite])

    def kill_target(self):
        if self.target_sprite:
            for sprite in self.target_sprite:
                sprite.kill()

    # NPC

    def is_there_unlocked_quest(self, npc_name):
        if npc_data[npc_name]['quests']:
            for quest in npc_data[npc_name]['quests']:
                if not self.quest_database[quest]['locked'] and not self.quest_database[quest]['finished']:
                    return quest
            return None
        else:
            return None

    def create_speech(self, name):
        quest = self.is_there_unlocked_quest(name)

        if quest:
            if self.quest_database[quest]['active'] and self.quest_database[quest]['done']:
                speech = quest_master_database[quest]['dialogue']['finish']
                self.finish_quest(quest)

            elif self.quest_database[quest]['active']:
                speech = quest_master_database[quest]['dialogue']['during']
            else:
                speech = quest_master_database[quest]['dialogue']['start']
                self.start_quest(quest)

        else:
            speech = choice(npc_data[name]['talk'])

        SpeechBox([self.speech_box_sprites], 'speech', speech, name)
        self.talking_paused = True

    def run(self):
        # update and draw the game
        self.visible_sprites.custom_draw(self.player, self.vertical_change, self.horizontal_change)
        self.target_sprite.draw(self.display_surface)
        self.ui.display(self.player)
        self.level_up()

        # check quest status
        self.quest_checker.run(self.active_quests, self.player)

        if self.game_paused:
            self.menu.display(self.active_quests)

        elif self.loot_paused:
            self.loot_paused = self.loot_menu.display(self.current_loot_sprite)
            if not self.loot_paused:
                self.current_loot_sprite.kill()

        elif self.talking_paused:
            update = True
            for sprite in self.speech_box_sprites:
                update = sprite.update()

            if not update:
                for sprite in self.speech_box_sprites:
                    sprite.kill()
                self.talking_paused = False
                self.player.talking = False
                self.player.can_talk = False
                self.player.can_talk_time = pygame.time.get_ticks()

        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.visible_sprites.npc_update(self.player)
            self.target_sprite.update()
            self.player_attack_logic()
            self.remove_projectiles()
            self.text_generator.update()

            # set the menu back
            self.menu.menu_type = 'General'
            self.menu.item_list.clear()
            self.menu.selection_index = 0


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