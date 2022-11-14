import pygame
from settings import *
from support import import_folder, import_csv_layout
from random import choice, randint
from tile import Tile
from Area import Area
from attack_handler import AttackHandler
from magic import MagicPlayer
from particles import AnimationPlayer
from npc import NPC, SpeechBox
from player import Player
from enemy import Enemy
from ui import UI
from menu import Menu
from loot_handler import LootHandler
from quest import QuestChecker
from text import TextGenerator


class GameHandler:

    def __init__(self):

        self.vertical_change = 1
        self.horizontal_change = 1

        self.map = {}
        self.current_areas = []

        self.player = None

        self.create_map()

        self.game_paused = False

        # user interface
        self.ui = UI()
        self.menu = Menu(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        self.attack_handler = AttackHandler(self.map, self.player, self.magic_player, self.animation_player,
                                            self.vertical_change, self.horizontal_change)
        self.loot_handler = LootHandler(self.map, self.player)

        # NPC-Player interactions - need to finish npc handler
        self.talking_paused = False
        self.speech_box_sprites = pygame.sprite.Group()
        self.text_generator = TextGenerator()

        # questing - need to make questing handler
        self.quest_database = {}
        self.active_quests = []
        self.create_quest_database()
        self.quest_checker = QuestChecker(self.quest_database)

        self.player.assign_handlers(self.attack_handler, self.loot_handler)

        for area in self.map.items():
            for sprite in area[1].visible_sprites:
                if sprite.sprite_type == "enemy":
                    sprite.assign_handlers(self.attack_handler, self.loot_handler)

    def create_map(self):
        self.layout = {
            'grass': import_csv_layout('map/test_area/test_area_grass.csv'),
            'trees': import_csv_layout('map/test_area/test_area_trees.csv'),
            'entities': import_csv_layout('map/test_area/test_area_Entities.csv'),
            'buildings': import_csv_layout('map/test_area/test_area_buildings.csv'),
            'doors': import_csv_layout('map/test_area/test_area_doors.csv')
        }
        self.graphics = {
            'grass': import_folder('graphics/grass'),
            'objects': import_folder('graphics/objects'),
            'buildings': import_folder('graphics/buildings')
        }

        for style, layout in self.layout.items():
            num_areas = 5

            area_x_size = len(layout) * TILESIZE / num_areas
            area_y_size = len(layout[0]) * TILESIZE / num_areas

            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE

                    area_num = num_areas * (int(y / area_y_size) + 1) - (num_areas - (int(x / area_x_size) + 1))

                    if area_num not in self.map:
                        self.map[area_num] = Area(area_num, self.vertical_change, self.horizontal_change)

                    if col != '-1':
                        if style == 'grass':
                            random_grass_image = choice(self.graphics['grass'])
                            Tile((x, y), [self.map[area_num].visible_sprites,
                                          self.map[area_num].obstacle_sprites,
                                          self.map[area_num].attackable_sprites],
                                 'grass', random_grass_image)

                        if style == 'trees':
                            surf = self.graphics['objects'][int(col)]
                            Tile((x, y), [self.map[area_num].visible_sprites, self.map[area_num].obstacle_sprites],
                                 'object', surf)

                        if style == 'buildings':
                            surf = self.graphics['buildings'][int(col)]
                            Tile((x, y), [self.map[area_num].visible_sprites, self.map[area_num].obstacle_sprites],
                                 'building', surf)

                        """
                        if style == 'doors':
                            Door((x, y), [self.door_sprites], 'door', col, self.player, self.load_area)
                            saved_data['doors'][col][self.current_area] = (x, y)
                        """

                        if style == 'entities':
                            if col == '0':
                                self.player = Player((x, y),
                                                     [self.map[area_num].visible_sprites, self.map[area_num].friendly_sprites],
                                                     self.map[area_num].obstacle_sprites,
                                                     self.map[area_num].attackable_sprites,
                                                     self.change_camera,
                                                     self.map[area_num].npc_sprites,
                                                     self.create_speech)

                                self.player.curr_area_num = area_num

                            elif col == '2':
                                NPC((x, y), [self.map[area_num].visible_sprites, self.map[area_num].npc_sprites],
                                    'villager', 'npc', self.map[area_num].obstacle_sprites)

                            elif col == '3':
                                NPC((x, y), [self.map[area_num].visible_sprites, self.map[area_num].npc_sprites],
                                    'man-bun', 'npc', self.map[area_num].obstacle_sprites)

                            else:
                                monster_name = 'squid'
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.map[area_num].visible_sprites, self.map[area_num].attackable_sprites],
                                    self.map[area_num].obstacle_sprites,
                                    self.map[area_num].friendly_sprites)

        self.current_areas.append(self.map[self.player.curr_area_num])

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

    # menus

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def level_up(self):
        if self.player.exp >= self.player.exp_to_level_up:
            self.player.level_up()
            self.menu.nr_level_ups += 1
            self.text_generator.add_to_queue('level up')

    def run(self):
        for area in self.current_areas:
            area.draw(self.player)
        self.attack_handler.draw()
        self.ui.display(self.player)
        self.level_up()

        # check quest status
        self.quest_checker.run(self.active_quests, self.player)

        if self.game_paused:
            self.menu.display(self.active_quests)

        elif self.loot_handler.loot_paused:
            self.loot_handler.loot_pause()

        else:
            for area in self.current_areas:
                area.update(self.player)
            self.ui.display(self.player)
            self.attack_handler.update()
            self.text_generator.update()

            # set the menu back
            self.menu.menu_type = 'General'
            self.menu.item_list.clear()
            self.menu.selection_index = 0

