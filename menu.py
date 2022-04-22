import pygame
from settings import *


class Menu:
    def __init__(self, player):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        # title
        self.pause_title = pygame.Rect(WIDTH // 2 - HEALTH_BAR_WIDTH, 80, HEALTH_BAR_WIDTH * 2, BAR_HEIGHT * 2)

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                # self.item_list[self.selection_index].trigger(self.player)

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 300:
                self.can_move = True

    def display_title(self):
        text_surf = self.font.render('Game Paused', False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.pause_title)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.pause_title, 3)


    def display(self):
        self.display_title()
        self.input()
        self.selection_cooldown()


#class Item:
    #def __init__(self, l, t, w, h, index, font):

