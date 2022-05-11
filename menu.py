import pygame
from settings import *


class Menu:
    def __init__(self, player):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.menu_type = 'General'
        self.saved_item_type = None
        self.saved_item_name = None
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
        self.gold_title = pygame.Rect(WIDTH // 2 - HEALTH_BAR_WIDTH // 2, 130, HEALTH_BAR_WIDTH, BAR_HEIGHT * 2)

        # level up
        self.nr_level_ups = 0
        self.level_up = False

        # menus
        self.menus = None

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

                # trigger the item event
                self.menu_type, self.saved_item_name = self.item_list[self.selection_index].trigger(self.player, self.saved_item_type, self.saved_item_name)

                if self.menu_type != 'Hand Choice':
                    self.saved_item_type = self.menu_type

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

    def display_money(self):
        text_surf = self.font.render('Gold: ' + str(self.player.money), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 150))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.gold_title)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.gold_title, 3)

    def create_items(self):

        attribute_nr = self.menus[self.menu_type]['attribute_nr']
        names = self.menus[self.menu_type]['attribute_names']

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

            num_items = 0
            if index < attribute_nr - 1:
                if self.menu_type == 'Weapons':
                    num_items = self.player.weapon_inventory[names[index]]['available']
                elif self.menu_type == 'Magic':
                    num_items = self.player.magic_inventory[names[index]]
                elif self.menu_type == 'Armor':
                    num_items = self.player.armor_inventory[names[index]]['available']

            # create the object
            item = Item(left, top, self.width, self.height, index, self.font, names[index], self.menu_type, num_items)
            self.item_list.append(item)

    def reload_menu_items(self, player):
        weapon_list = []
        for weapon in list(player.weapon_inventory.keys()):
            if player.weapon_inventory[weapon]['available'] >= 1:
                weapon_list.append(weapon)

        armor_list = []
        for armor in list(player.armor_inventory.keys()):
            if player.armor_inventory[armor]['available'] >= 1:
                armor_list.append(armor)

        self.menus = {
            'General': {'attribute_nr': 4, 'attribute_names': ['Magic', 'Items', 'Classes', 'Quit Game']},
            'Items': {'attribute_nr': 3, 'attribute_names': ['Weapons', 'Armor', 'Back']},
            'Magic': {'attribute_nr': len(player.magic_inventory.keys()) + 1, 'attribute_names': list(player.magic_inventory.keys()) + ['Back']},
            'Weapons': {'attribute_nr': len(weapon_list) + 1, 'attribute_names': weapon_list + ['Back']},
            'Armor': {'attribute_nr': len(armor_list) + 1, 'attribute_names': armor_list + ['Back']},
            'Hand Choice': {'attribute_nr': 2, 'attribute_names': ['Main-Hand', 'Off-Hand']},
            'Level Up': {'attribute_nr': 3, 'attribute_names': ['Health', 'magic', 'Stamina']},
            'Classes': {'attribute_nr': len(class_data.keys()) + 1, 'attribute_names': list(class_data.keys()) + ['Back']}
        }

    def display(self):
        self.reload_menu_items(self.player)
        if self.nr_level_ups:
            self.menu_type = 'Level Up'
        if not self.item_list:
            self.create_items()
        self.display_title()
        self.display_money()
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            item.display(self.display_surface, self.selection_index)


class Item:
    def __init__(self, l, t, w, h, index, font, name, item_type, num_items):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font
        self.name = name
        self.item_type = item_type
        self.num_items = num_items

    def display_names(self, surface):
        color = TEXT_COLOR

        # title
        title_surf = self.font.render(self.name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        # draw
        surface.blit(title_surf, title_rect)

    def display_num(self, surface):
        color = TEXT_COLOR

        # title
        title_surf = self.font.render('x' + str(self.num_items), False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 55))

        # draw
        surface.blit(title_surf, title_rect)

    def switch(self, player, saved_item_type, saved_item_name):
        if self.name == 'Main-Hand':
            if saved_item_type == 'Weapons':
                player.attack_type = 'weapon'
                if player.weapon:
                    player.weapon_inventory[player.weapon]['available'] += 1
                    if weapon_data[player.weapon]['type'] == 'bow':
                        player.offhand_weapon = None
                        player.offhand_attack_type = 'fist'
                player.weapon = saved_item_name
                player.weapon_inventory[player.weapon]['available'] -= 1
            elif saved_item_type == 'Magic':
                if player.attack_type == 'weapon':
                    player.weapon_inventory[player.weapon]['available'] += 1
                player.attack_type = 'magic'
                player.magic = saved_item_name
        else:
            if saved_item_type == 'Weapons':
                player.offhand_attack_type = 'weapon'
                if player.offhand_weapon:
                    player.weapon_inventory[player.offhand_weapon]['available'] += 1
                    if weapon_data[player.offhand_weapon]['type'] == 'bow':
                        player.weapon = None
                        player.attack_type = 'fist'
                player.offhand_weapon = saved_item_name
                player.weapon_inventory[player.offhand_weapon]['available'] -= 1
            elif saved_item_type == 'Magic':
                if player.offhand_attack_type == 'weapon':
                    player.weapon_inventory[player.offhand_weapon]['available'] += 1
                player.offhand_attack_type = 'magic'
                player.offhand_magic = saved_item_name

    def trigger(self, player, saved_item_type, saved_item_name):
        if self.name == 'Quit Game':
            pygame.quit()

        elif self.name == 'Back':
            return 'General', None

        elif self.item_type == 'General' or self.item_type == 'Items':
            return self.name, None

        elif self.item_type == 'Classes':
            for magic in class_data[player.class_type]['magic']:
                player.magic_inventory.pop(magic)

            player.class_type = self.name

            for magic in class_data[player.class_type]['magic']:
                player.magic_inventory[magic] = 1

            return 'General', None

        elif self.item_type == 'Level Up':
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

        elif self.item_type == 'Armor':
            player.armor_inventory[player.armor_type]['available'] += 1
            player.armor_type = self.name
            player.armor_inventory[player.armor_type]['available'] -= 1
            player.can_switch_armor = False
            player.armor_switch_time = pygame.time.get_ticks()

            return 'General', None

        elif self.name == 'bow':
            if player.weapon:
                player.weapon_inventory[player.weapon]['available'] += 1
            if player.offhand_weapon:
                player.weapon_inventory[player.offhand_weapon]['available'] += 1

            player.attack_type = 'bow'
            player.offhand_attack_type = 'bow'
            player.weapon = self.name
            player.offhand_weapon = self.name
            player.weapon_inventory[player.weapon]['available'] -= 1

            return 'General', None

        elif self.item_type == 'Hand Choice':
            self.switch(player, saved_item_type, saved_item_name)

            return 'General', None

        else:
            return 'Hand Choice', self.name

    def display(self, surface, selection_num):
        if self.index == selection_num:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR_ACTIVE, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface)
        if self.num_items > 1:
            self.display_num(surface)



