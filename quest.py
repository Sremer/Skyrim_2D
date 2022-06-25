import pygame
from settings import *


class Quest:
    def __init__(self, name):
        self.name = name
        self.active = False
        self.finished = False
        self.locked = bool(quest_master_database[self.name]['prereq'])
        self.type = quest_master_database[self.name]['objective']['type']
        self.what = quest_master_database[self.name]['objective']['what']

        # quest details
        self.reqs = self.type + self.what
