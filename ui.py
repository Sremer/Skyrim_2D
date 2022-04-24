import pygame
from settings import *


class UI:
    def __init__(self):
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # bar setup
        self.health_bar_rect = pygame.Rect((WIDTH // 2) - (HEALTH_BAR_WIDTH // 2), HEIGTH - 50, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(50, HEIGTH - 50, ENERGY_BAR_WIDTH, BAR_HEIGHT)
        self.stamina_bar_rect = pygame.Rect((WIDTH - HEALTH_BAR_WIDTH + 10), HEIGTH - 50, ENERGY_BAR_WIDTH, BAR_HEIGHT)

    def show_bar(self, current, max_amount, bg_rect, color):
        # draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # converting stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # draw the bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, player):
        self.exp_bar_rect = pygame.Rect(90, 30, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        text_surf = self.font.render(str(player.level), False, TEXT_COLOR)
        offset = 0
        if player.level >= 100:
            offset = 30
        elif player.level >= 10:
            offset = 15
        x = 60 - offset
        text_rect = text_surf.get_rect(topleft=(x, 30))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

        self.show_bar(player.exp, player.exp_to_level_up, self.exp_bar_rect, EXP_COLOR)

    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        self.show_bar(player.stamina, player.stats['stamina'], self.stamina_bar_rect, STAMINA_COLOR)
        self.show_exp(player)

