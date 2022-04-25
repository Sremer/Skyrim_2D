import pygame
from settings import *


class Menu:
    def __init__(self, player):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.menu_type = 'General'
        self.saved_menu_type = None
        self.saved_item_type = None
        self.player = player
        self.num_items_in_row = 6

        # item creation
        self.height = self.display_surface.get_size()[1] * 0.15
        self.width = self.display_surface.get_size()[0] // 7
        self.item_list = []

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        # press timer
        self.can_press = True
        self.press_switch_time = None
        self.press_cooldown = 200

        # title
        self.pause_title = pygame.Rect(WIDTH // 2 - HEALTH_BAR_WIDTH, 80, HEALTH_BAR_WIDTH * 2, BAR_HEIGHT * 2)

        # level up
        self.nr_level_ups = 0
        self.level_up = False

        # menus
        self.menus = None

        # convert weapon dictionary
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

        # convert magic dictionary
        self.magic_graphics = []
        for magic in magic_data.values():
            magic = pygame.image.load(magic['graphic']).convert_alpha()
            self.magic_graphics.append(magic)

    def input(self):
        keys = pygame.key.get_pressed()
        attribute_nr = self.menus[self.menu_type]['attribute_nr']

        if self.can_move:
            if keys[pygame.K_d] and self.selection_index < attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_a] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_w] and self.selection_index - self.num_items_in_row >= 0:
                self.selection_index -= self.num_items_in_row
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_s] and self.selection_index < attribute_nr - self.num_items_in_row:
                self.selection_index += self.num_items_in_row
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.can_press = False
                self.press_switch_time = pygame.time.get_ticks()
                if self.menu_type == 'Level Up':
                    self.nr_level_ups -= 1
                    if self.nr_level_ups < 0:
                        self.nr_level_ups = 0
                self.menu_type, item_type = self.item_list[self.selection_index].trigger(self.player, self.menu_type, self.saved_menu_type, self.saved_item_type)
                if self.menu_type != 'Hand Choice':
                    self.saved_menu_type = self.menu_type
                if item_type != 'Main-Hand' and item_type != 'Off-Hand':
                    self.saved_item_type = item_type
                self.item_list.clear()
                self.selection_index = 0

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 300:
                self.can_move = True

        if not self.can_press:
            current_time = pygame.time.get_ticks()
            if current_time - self.press_switch_time >= self.press_cooldown:
                self.can_press = True

    def display_title(self):
        text_surf = self.font.render('Game Paused', False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.pause_title)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.pause_title, 3)

    def create_items(self):
        # self.item_list.clear()
        attribute_nr = self.menus[self.menu_type]['attribute_nr']

        for item, index in enumerate(range(attribute_nr)):
            # horizontal position
            full_width = self.display_surface.get_size()[0]
            increment = 0
            if attribute_nr <= self.num_items_in_row:
                increment = (full_width // attribute_nr)
            else:
                increment = (full_width // self.num_items_in_row)

            left_offset = item % self.num_items_in_row
            left = (left_offset * increment) + (increment - self.width) // 2

            # vertical position
            top_offset = int(item // self.num_items_in_row) * 75

            offset = int(item // self.num_items_in_row + 1) * 0.3

            top = self.display_surface.get_size()[1] * offset - top_offset

            # create the object
            item = General_Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)

    def reload_menu_items(self, player):
        self.menus = {
            'General': {'attribute_nr': 3, 'attribute_names': ['Magic', 'Items', 'Quit']},
            'Items': {'attribute_nr': 3, 'attribute_names': ['Weapons', 'Armor', 'Back']},
            'Magic': {'attribute_nr': len(player.magic_inventory) + 1, 'attribute_names': player.magic_inventory + ['Back']},
            'Weapons': {'attribute_nr': len(player.weapon_inventory) + 1, 'attribute_names': player.weapon_inventory + ['Back']},
            'Armor': {'attribute_nr': len(player.armor_inventory) + 1, 'attribute_names': player.armor_inventory + ['Back']},
            'Hand Choice': {'attribute_nr': 2, 'attribute_names': ['Main-Hand', 'Off-Hand']},
            'Level Up': {'attribute_nr': 3, 'attribute_names': ['Health', 'magic', 'Stamina']}
        }

    def display(self):
        self.reload_menu_items(self.player)
        if self.nr_level_ups:
            self.menu_type = 'Level Up'
        if not self.item_list:
            self.create_items()
        self.display_title()
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            name = self.menus[self.menu_type]['attribute_names'][index]
            item.display(self.display_surface, self.selection_index, name)


class General_Item:
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font
        self.item_type = None

    def display_names(self, surface, name, selected):
        color = TEXT_COLOR

        if ', ' in name:
            new_name = name.split(' ')
            # title
            title_surf = self.font.render(new_name[0], False, color)
            title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))
            title1_surf = self.font.render(new_name[1], False, color)
            title1_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 50))

            # draw
            surface.blit(title_surf, title_rect)
            surface.blit(title1_surf, title1_rect)

        else:
            # title
            title_surf = self.font.render(name, False, color)
            title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

            # draw
            surface.blit(title_surf, title_rect)

    def trigger(self, player, menu_type, saved_menu_type, saved_item_type):
        if self.item_type == 'General' or self.item_type == 'Magic' or self.item_type == 'Items' or self.item_type == 'Weapons' or self.item_type == 'Armor':
            return self.item_type, None

        elif self.item_type == 'Quit':
            pygame.quit()

        elif self.item_type == 'Back':
            return 'General', None

        elif menu_type == 'Loot':


            return 'General', None

        elif menu_type == 'Level Up':
            print(self.item_type)
            if self.item_type == 'Health':
                if player.stats['health'] <= player.max_stats['health'] - 20:
                    player.stats['health'] += 20
                player.health = player.stats['health']
                print(player.stats['health'])

            elif self.item_type == 'magic':
                if player.stats['energy'] <= player.max_stats['energy'] - 8:
                    player.stats['energy'] += 8
                player.energy = player.stats['energy']

            else:
                if player.stats['stamina'] <= player.max_stats['stamina'] - 20:
                    player.stats['stamina'] += 20
                player.stamina = player.stats['stamina']

            return 'General', None

        elif menu_type == 'Armor':
            player.armor_type = self.item_type
            player.can_switch_armor = False
            player.armor_switch_time = pygame.time.get_ticks()

            return 'General', None

        elif menu_type == 'Hand Choice':
            if self.item_type == 'Main-Hand':
                if saved_menu_type == 'Weapons':
                    player.attack_type = 'weapon'
                    player.weapon = saved_item_type
                elif saved_menu_type == 'Magic':
                    player.attack_type = 'magic'
                    player.magic = saved_item_type
            else:
                if saved_menu_type == 'Weapons':
                    player.offhand_attack_type = 'weapon'
                    player.offhand_weapon = saved_item_type
                elif saved_menu_type == 'Magic':
                    player.offhand_attack_type = 'magic'
                    player.offhand_magic = saved_item_type

            return 'General', None
        else:
            return 'Hand Choice', self.item_type

    def display(self, surface, selection_num, name):
        self.item_type = name

        if self.index == selection_num:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR_ACTIVE, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, self.index == selection_num)



