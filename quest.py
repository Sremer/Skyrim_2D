import pygame
from settings import *


class QuestChecker:
    def __init__(self, quest_database):
        self.quest_database = quest_database

    def get_checker(self, quest, player):
        return bool(quest_master_database[quest]['objective']['what'] in list(player.quest_inventory.keys()))

    def run(self, active_quests, player):
        for quest in active_quests:
            if not self.quest_database[quest]['done']:
                if self.quest_database[quest]['type'] == 'get':
                    finished = self.get_checker(quest, player)
                    if finished:
                        self.quest_database[quest]['done'] = True
