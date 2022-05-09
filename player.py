import pygame
from settings import *
from support import import_folder
from entity import Entity


class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, attackable_sprites, loot_sprites, create_attack, destroy_attack, create_magic, show_loot, create_smash):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])
        self.sprite_type = 'player'
        self.visible = True

        # armor
        self.armor_type = 'skin'
        self.can_switch_armor = True
        self.armor_switch_time = None

        # graphics setup
        self.import_player_assets()
        self.status = 'down'

        # leveling
        self.exp = 0
        self.level = 1
        self.exp_to_level_up = int(1000 * (.5 * self.level))

        # money
        self.money = 0

        # class
        self.class_type = 'None'

        # movement
        self.attacking = False
        self.attack_cooldown = 300
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.loot_sprites = loot_sprites
        self.speed = 5

        # inventory
        self.weapon_inventory = {
            'sword': {'amount': 1, 'available': 0},
            'axe': {'amount': 1, 'available': 1},
            'rapier': {'amount': 1, 'available': 1},
            'sai': {'amount': 1, 'available': 1}
        }
        self.magic_inventory = {
            'flame': 1,
            'heal': 1
        }
        self.armor_inventory = {
            'skin': {'amount': 1, 'available': 0},
            'steel': {'amount': 1, 'available': 1},
            'thief': {'amount': 1, 'available': 1}
        }
        self.misc_inventory = {}
        self.show_loot = show_loot

        # general attack
        self.attack_type = 'weapon'
        self.can_switch_attack_type = True
        self.attack_type_switch_time = None
        self.switch_duration_cooldown = 200
        self.current_weapon = 'sword'

        # offhand attack
        self.offhand_attack_type = 'fist'
        self.can_switch_offhand_attack = True
        self.offhand_switch_time = None
        self.offhand_magic = None
        self.offhand_weapon = None

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]

        # invisibility
        self.invisible = False
        self.invisibility_time = None
        self.invisibility_duration = 5000

        # defense up
        self.defense_up = False
        self.defense_up_time = None
        self.defense_up_duration = 5000
        self.defense_up_bonus = 0

        # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5, 'stamina': 100}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10, 'stamina': 300}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.stamina = self.stats['stamina']
        self.speed = self.stats['speed']

        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # abilities

        # dash
        self.dashing = False
        self.dash_time = None
        self.dash_cooldown = 100
        self.dash_flickering = False
        self.dash_flicker_time = None
        self.dash_flicker_cooldown = 300

        # ground smash
        self.ground_smashing = False
        self.smash_time = None
        self.smash_cooldown = 500
        self.create_smash = create_smash
        self.previous_attack_type = None

    # general

    def import_player_assets(self):
        character_path = f'graphics/player/{self.armor_type}/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [],
                           'smash': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        if not self.attacking and not self.ground_smashing and not self.dashing:
            keys = pygame.key.get_pressed()

            # abilities input
            if keys[pygame.K_LCTRL]:
                if 'dash' in class_data[self.class_type]['abilities']:
                    self.start_dash_flickering_animation()

                elif 'ground smash' in class_data[self.class_type]['abilities']:
                    self.ground_smash()

            # movement input
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # sprinting
            if keys[pygame.K_LSHIFT] and 'idle' not in self.status:
                armor_effect = 0
                if armor_data[self.armor_type]['type'] == 'heavy':
                    armor_effect = 2
                else:
                    armor_effect = 0

                if self.speed < self.stats['speed'] + (5 - armor_effect) and self.stamina > 0:
                    self.speed += (5 - armor_effect)
                else:
                    self.speed = self.stats['speed']

                self.stamina -= (0.5 + (armor_effect * 0.1))
            else:
                self.speed = self.stats['speed']
                self.stamina_recovery()

            # magic input
            if keys[pygame.K_LALT]:
                if self.offhand_attack_type == 'weapon':
                    self.attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    self.create_attack('Off-Hand')
                    self.current_weapon = self.offhand_weapon
                elif self.offhand_attack_type == 'magic':
                    self.attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    style = self.offhand_magic
                    strength = magic_data[self.offhand_magic]['strength'] + self.stats['magic']
                    cost = magic_data[self.offhand_magic]['cost']
                    self.create_magic(style, strength, cost)
                else:
                    self.attacking = True
                    self.attack_time = pygame.time.get_ticks()

            # attack input
            if keys[pygame.K_SPACE]:
                if self.attack_type == 'weapon':
                    self.attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    self.create_attack('Main-Hand')
                    self.current_weapon = self.weapon
                else:
                    self.attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    style = self.magic
                    strength = magic_data[self.magic]['strength'] + self.stats['magic']
                    cost = magic_data[self.magic]['cost']
                    self.create_magic(style, strength, cost)

            if keys[pygame.K_r]:
                self.exp += 100

    def get_status(self):

        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status and not 'smash' in self.status:
                self.status = self.status + '_idle'

        if self.ground_smashing:
            self.direction.x = 0
            self.direction.y = 0
            self.status = 'smash'

        elif self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')
            elif 'smash' in self.status:
                self.status = 'down'

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.current_weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if self.dashing:
            if current_time - self.dash_time >= self.dash_cooldown:
                self.dashing = False
                self.vulnerable = True

        if self.ground_smashing:
            if current_time - self.smash_time >= self.smash_cooldown:
                self.attack_type = self.previous_attack_type
                self.ground_smashing = False

        if self.dash_flickering:
            if current_time - self.dash_flicker_time >= self.dash_flicker_cooldown:
                self.dash_flickering = False
                self.dash()

        if self.invisible:
            if current_time - self.invisibility_time >= self.invisibility_duration:
                self.invisible = False
                self.visible = True

        if self.defense_up:
            if current_time - self.defense_up_time >= self.defense_up_duration:
                self.defense_up_bonus = 0
                self.defense_up = False

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

        if not self.can_switch_attack_type:
            if current_time - self.attack_type_switch_time >= self.switch_duration_cooldown:
                self.can_switch_attack_type = True

        if not self.can_switch_offhand_attack:
            if current_time - self.offhand_switch_time >= self.switch_duration_cooldown:
                self.can_switch_offhand_attack = True

        if not self.can_switch_armor:
            if current_time - self.armor_switch_time >= self.switch_duration_cooldown:
                self.can_switch_armor = True

    # animation logic

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
            self.image.set_alpha(alpha)
        elif self.invisible:
            self.image.set_alpha(50)
        else:
            self.image.set_alpha(255)

    def dash_animate(self):
        if self.dash_flickering:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(0)

    # attack logic

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.current_weapon]['damage']

        class_damage = 0
        if weapon_data[self.current_weapon]['type'] in list(class_data[self.class_type]['multipliers'].keys()):
            class_damage += int(weapon_data[self.current_weapon]['damage'] * class_data[self.class_type]['multipliers'][weapon_data[self.current_weapon]['type']])

        return base_damage + weapon_damage + class_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        return base_damage + spell_damage

    # movement

    def move_player(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        armor_effect = 0
        if armor_data[self.armor_type]['type'] == 'heavy':
            armor_effect = 1

        self.hitbox.x += self.direction.x * speed
        self.collision_player('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision_player('vertical')
        self.rect.center = self.hitbox.center

    def collision_player(self, direction):
        if direction == 'horizontal':
            for sprite in self.loot_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    self.show_loot(sprite)

            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

            for sprite in self.attackable_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.loot_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    self.show_loot(sprite)

            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

            for sprite in self.attackable_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def start_dash_flickering_animation(self):
        if self.stamina - 20 > 0:
            self.dash_flickering = True
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            self.dash_flicker_time = pygame.time.get_ticks()
            self.stamina -= 20

    # abilities

    def dash(self):
        dash_amount = 300
        self.dashing = True

        if 'left' in self.status:
            self.hitbox.x -= dash_amount
        elif 'right' in self.status:
            self.hitbox.x += dash_amount
        self.collision_player('horizontal')

        if 'up' in self.status:
            self.hitbox.y -= dash_amount
        elif 'down' in self.status:
            self.hitbox.y += dash_amount
        self.collision_player('vertical')

        self.rect.center = self.hitbox.center
        self.dash_time = pygame.time.get_ticks()

    def ground_smash(self):
        if self.stamina >= 20:
            self.stamina -= 20
            self.ground_smashing = True
            self.previous_attack_type = self.attack_type
            self.attack_type = 'smash'

            self.smash_time = pygame.time.get_ticks()
            self.create_smash()

    # stats and recovery

    def stamina_recovery(self):
        if self.stamina < 0:
            self.stamina = 0

        if self.stamina < self.stats['stamina']:
            self.stamina += 0.3
        else:
            self.stamina = self.stats['stamina']

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def level_up(self):
        if self.exp >= self.exp_to_level_up:
            self.level += 1
            self.exp = self.exp - self.exp_to_level_up
            self.exp_to_level_up = int(1000 * (.5 * self.level))

    # updating

    def update(self):
        if not self.can_switch_armor:
            self.import_player_assets()

        if not self.dashing and not self.dash_flickering:
            self.input()

        self.cooldowns()
        self.get_status()

        if not self.dashing and not self.dash_flickering:
            self.animate()
            self.move_player(self.speed)

        if self.dash_flickering:
            self.dash_animate()

        self.energy_recovery()

        # self.level_up()
