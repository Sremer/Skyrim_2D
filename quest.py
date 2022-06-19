import pygame
from settings import *


class Quest:
    def __init__(self, name, can_start=False):
        self.name = name
        self.can_start = can_start
        self.active = False
        self.completed = False

        # full_reqs = quest_data[name][]
