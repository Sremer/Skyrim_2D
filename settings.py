# game setup
WIDTH = 1280
HEIGTH = 720
FPS = 60
TILESIZE = 64
HITBOX_OFFSET = {
    'player': -26,
    'object': -40,
    'grass': -10,
    'loot': -40,
    'invisible': 0}

# ui
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = 'graphics/font/joystix.ttf'
UI_FONT_SIZE = 18

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'dark red'
ENERGY_COLOR = 'dark blue'
STAMINA_COLOR = 'dark green'
EXP_COLOR = 'light blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# weapons
weapon_data = {
    'sword': {'cooldown': 0, 'damage': 15, 'type': 'sword', 'graphic': 'graphics/weapons/sword/full.png'},
    'lance': {'cooldown': 400, 'damage': 30, 'type': 'spear', 'graphic': 'graphics/weapons/lance/full.png'},
    'axe': {'cooldown': 300, 'damage': 20, 'type': 'axe', 'graphic': 'graphics/weapons/axe/full.png'},
    'rapier': {'cooldown': 50, 'damage': 8, 'type': 'sword', 'graphic': 'graphics/weapons/rapier/full.png'},
    'sai': {'cooldown': 80, 'damage': 10, 'type': 'special', 'graphic': 'graphics/weapons/sai/full.png'},
    'bow': {'cooldown': 80, 'damage': 10, 'type': 'bow', 'graphic': 'graphics/weapons/bow/down.png'}
}

# armor
armor_data = {
    'skin': {'defense': 0, 'type': 'none'},
    'steel': {'defense': 5, 'type': 'heavy'},
    'thief': {'defense': 3, 'type': 'light'}
}

# magic
magic_data = {
    'flame': {'strength': 5, 'cost': 20, 'graphic': 'graphics/particles/flame/fire.png'},
    'heal': {'strength': 20, 'cost': 10, 'graphic': 'graphics/particles/heal/heal.png'},
    'invisibility': {'strength': 5, 'cost': 20, 'graphic': 'graphics/particles/'},
    'defense up': {'strength': 0.5, 'cost': 20, 'graphic': 'graphics/particles/'}
}

# enemy
monster_data = {
    'squid': {'health': 100, 'exp': 100, 'damage': 20, 'attack_type': 'slash',
              'attack_sound': 'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80,
              'notice_radius': 360},
    'raccoon': {'health': 300, 'exp': 250, 'damage': 40, 'attack_type': 'claw',
                'attack_sound': 'audio/attack/claw.wav', 'speed': 2, 'resistance': 3, 'attack_radius': 120,
                'notice_radius': 400},
    'spirit': {'health': 100, 'exp': 110, 'damage': 8, 'attack_type': 'thunder',
               'attack_sound': 'audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60,
               'notice_radius': 350},
    'bamboo': {'health': 70, 'exp': 120, 'damage': 6, 'attack_type': 'leaf_attack',
               'attack_sound': 'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 50,
               'notice_radius': 300}}

# classes

class_data = {
    'None': {'multipliers': {}, 'abilities': [], 'magic': []},
    'knight': {'multipliers': {'sword': 0.5, 'spear': 0.3, 'heavy': 0.5}, 'abilities': ['ground smash'], 'magic': ['defense up']},
    'rogue': {'multipliers': {'knife': 0.5, 'light': 0.3}, 'abilities': ['dash'], 'magic': ['invisibility']},
    'archer': {'multipliers': {'bow': 0.5, 'light': 0.3}, 'abilities': ['long shot'], 'magic': ['']}
}

# NPC

npc_data = {
    'villager': {'talk': ['Nice Day!', 'Here let me tell you my story... I was 3 when I first realized that I wanted to bake. Baking became my passion; my obsession. I would stay up for long days and nights creating the most beautiful cakes...then one day I said nah.'],
                 'quests': ['lunch money']}
}

# Quests

quest_data = {
    'lunch money': {'start': 'I have a very important request...that squid over there has stolen all of my lunch money. Would you get it back for me?',
                    'reqs': ['kill_squid_1'],
                    'during': 'I am just so hungry',
                    'finish': 'Thank you! Now I wont go hungry',
                    'available': True,
                    'started': False,
                    'completed': False}

}
