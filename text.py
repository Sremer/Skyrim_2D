import pygame
from settings import *


class TextGenerator:
    def __init__(self):
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # the queue
        self.queue = {}
        self.to_pop = []

        # timer
        self.can_display = True
        self.delay_time = 500
        self.timer = None

    def add_to_queue(self, text):
        self.queue[text] = [HEIGTH // 2 - 20, 255]
        if self.can_display:
            self.timer = pygame.time.get_ticks()
            self.can_display = False

    def show_text(self, text, y):
        text_surf = self.font.render(text, False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y))
        text_surf.set_alpha(self.queue[text][1])
        self.display_surface.blit(text_surf, text_rect)

    def update_text_y(self, text):
        self.queue[text][0] = self.queue[text][0] - 2
        self.queue[text][1] -= 3
        if self.queue[text][0] < 150:
            self.to_pop.append(text)

    def update(self):
        if self.queue:
            if self.can_display:
                previous = None

                for text in self.queue:
                    if not previous or (self.queue[text][0] - self.queue[previous][0]) > 30:
                        self.show_text(text, self.queue[text][0])
                        self.update_text_y(text)
                        previous = text

                for text in self.to_pop:
                    self.queue.pop(text)
                self.to_pop.clear()

            else:
                current_time = pygame.time.get_ticks()
                if current_time - self.timer >= self.delay_time:
                    self.can_display = True





