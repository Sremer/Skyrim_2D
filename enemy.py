import pygame
from settings import *
from entity import Entity
from support import *


class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player,
                 trigger_death_particles, add_exp, create_loot, friendly_sprites):

        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites
        self.friendly_sprites = friendly_sprites

        # stun
        self.stunned = False
        self.stun_time = None
        self.stun_cooldown = 1200

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp
        self.create_loot = create_loot
        self.target = 'player'

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        """
        # sound
        self.death_sound = pygame.mixer.Sound('audio/death.wav')
        self.hit_sound = pygame.mixer.Sound('audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.death_sound.set_volume(0.2)
        self.hit_sound.set_volume(0.2)
        self.attack_sound.set_volume(0.3)
        """

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    def get_friendly_sprite_direction(self):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        friendly_vec = pygame.math.Vector2()
        distance = 0
        closest_distance = 500

        for sprite in self.friendly_sprites:
            if sprite.sprite_type != 'player':
                friendly_vec = pygame.math.Vector2(sprite.rect.center)
                distance = (friendly_vec - enemy_vec).magnitude()

                if distance < closest_distance:
                    closest_distance = distance

        if closest_distance > 0:
            direction = (friendly_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return closest_distance, direction

    def get_closest_sprite(self):
        closest_sprite = None
        enemy_vec = pygame.math.Vector2(self.rect.center)
        friendly_vec = pygame.math.Vector2()
        closest_distance = 500

        for sprite in self.friendly_sprites:
            if sprite.sprite_type != 'player':
                friendly_vec = pygame.math.Vector2(sprite.rect.center)
                distance = (friendly_vec - enemy_vec).magnitude()

                if distance < closest_distance:
                    closest_distance = distance
                    closest_sprite = sprite

        return closest_sprite

    def get_closest_target(self, player):
        player_vec = self.get_player_distance_direction(player)
        other_vec = self.get_friendly_sprite_direction()

        if player_vec[0] < other_vec[0]:
            self.target = 'player'
            return player_vec
        else:
            self.target = 'other'
            return other_vec

    def get_status(self, player):
        distance = self.get_closest_target(player)[0]

        if distance <= self.attack_radius and self.can_attack and player.visible:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius and player.visible:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack' and self.target == 'player':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)

        elif self.status == 'attack' and self.target == 'other':
            self.attack_time = pygame.time.get_ticks()
            closest_target = self.get_closest_sprite()
            closest_target.get_damage(monster_data[self.monster_name]['damage'])

        elif self.status == 'move':
            if self.target == 'player':
                self.direction = self.get_player_distance_direction(player)[1]
            else:
                self.direction = self.get_friendly_sprite_direction()[1]

        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

        if self.stunned:
            if current_time - self.stun_time >= self.stun_cooldown:
                self.stunned = False

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            elif attack_type == 'magic':
                self.health -= player.get_full_magic_damage()
            elif attack_type == 'arrow' or attack_type == 'long shot arrow':
                self.health -= player.get_full_bow_damage(attack_type)
            elif attack_type == 'summoned':
                self.health -= player.get_full_summoned_damage()
            else:
                self.health -= 10
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

            if attack_type == 'smash':
                self.stunned = True
                self.stun_time = pygame.time.get_ticks()

    def check_death(self):
        if self.health <= 0:
            pos = self.hitbox.center
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.create_loot(pos)

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def move_enemy(self, speed, player):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision_enemy('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision_enemy('vertical')
        self.rect.center = self.hitbox.center

    def collision_enemy(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

            for sprite in self.friendly_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

            for sprite in self.friendly_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.hit_reaction()
        # self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self, player):
        if not self.stunned:
            self.move_enemy(self.speed, player)
            self.get_status(player)
            self.actions(player)
