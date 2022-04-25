import pygame
from settings import *


class LootMenu:
    def __init__(self, player):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
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

    def input(self, loot_sprite):
        keys = pygame.key.get_pressed()
        attribute_nr = len(self.item_list)

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
                still_pause = self.item_list[self.selection_index].trigger(self.player, self.item_list)
                self.item_list.remove(self.item_list[self.selection_index])
                loot_sprite.loot.remove(loot_sprite.loot[self.selection_index])
                self.selection_index = 0

                if len(self.item_list) <= 1 or not still_pause:
                    return False
                else:
                    return True

        return True

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
        text_surf = self.font.render('Loot', False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.pause_title)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.pause_title, 3)

    def create_items(self, loot_sprite):
        # self.item_list.clear()
        attribute_nr = len(loot_sprite.loot)

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
            item = Item(left, top, self.width, self.height, index, self.font, loot_sprite.loot[index][0], loot_sprite.loot[index][1])
            self.item_list.append(item)

    def display(self, loot_sprite):
        # if not self.loot_item_list:
        self.create_items(loot_sprite)
        self.display_title()
        paused = self.input(loot_sprite)
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            item.display(self.display_surface, self.selection_index)

        self.item_list.clear()
        return paused


class Item:
    def __init__(self, l, t, w, h, index, font, name, item_type):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font
        full_name = name.split(' x')
        self.name = full_name[0]
        self.item_type = item_type
        self.num_items = int(full_name[1])

    def display_names(self, surface, selected):
        color = TEXT_COLOR

        title_surf = self.font.render(self.name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        # draw
        surface.blit(title_surf, title_rect)

        if self.num_items > 1:
            # title
            title_surf = self.font.render('x' + str(self.num_items), False, color)
            title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 55))

            # draw
            surface.blit(title_surf, title_rect)

    def trigger(self, player, item_list):
        if self.item_type == 'Exit':
            return False

        elif self.item_type == 'Take All':
            for item in item_list:
                item.add_to_player(player)
            return False
        else:
            self.add_to_player(player)
            return True

    def add_to_player(self, player):
        if self.item_type == 'gold':
            player.money += self.num_items

        elif self.item_type == 'weapon':
            for i in range(self.num_items):
                if self.name in list(player.weapon_inventory.keys()):
                    player.weapon_inventory[self.name] += 1
                else:
                    player.weapon_inventory[self.name] = 1

        elif self.item_type == 'armor':
            for i in range(self.num_items):
                if self.name in list(player.armor_inventory.keys()):
                    player.armor_inventory[self.name] += 1
                else:
                    player.armor_inventory[self.name] = 1

        elif self.item_type == 'magic':
            for i in range(self.num_items):
                if self.name in list(player.magic_inventory.keys()):
                    player.magic_inventory[self.name] += 1
                else:
                    player.magic_inventory[self.name] = 1

        elif self.item_type == 'Take All':
            pass

        else:
            for i in range(self.num_items):
                if self.name in list(player.misc_inventory.keys()):
                    player.misc_inventory[self.name] += 1
                else:
                    player.misc_inventory[self.name] = 1

    def display(self, surface, selection_num):

        if self.index == selection_num:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR_ACTIVE, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, self.index == selection_num)



