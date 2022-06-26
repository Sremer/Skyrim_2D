import pygame
from settings import *


class TextGenerator():
    def __init__(self):
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # the queue
        self.queue = {}
        self.to_pop = []

    def add_to_queue(self, text):
        self.queue[text] = HEIGTH // 2 - 20

    def show_text(self, text, y):
        text_surf = self.font.render(text, False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y))
        self.display_surface.blit(text_surf, text_rect)

    def update_text_y(self, text):
        self.queue[text] = self.queue[text] - 2
        if self.queue[text] < 200:
            self.to_pop.append(text)

    def update(self):
        if self.queue:
            previous = None
            print(self.queue)

            for text in self.queue:
                if not previous or (self.queue[text] - self.queue[previous]) > 30:
                    self.show_text(text, self.queue[text])
                    self.update_text_y(text)
                    previous = text

            for text in self.to_pop:
                self.queue.pop(text)
            self.to_pop.clear()


