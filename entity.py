import pygame
from settings import *
from math import sin
from support import import_folder


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'graphics/npcs/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
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

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0


class Undead(Entity):
    def __init__(self, undead_type, pos, groups, obstacle_sprites, attackable_sprites, trigger_death_particles):
        super().__init__(groups)

        # general
        self.sprite_type = 'summoned'
        self.summoned_type = undead_type

        # graphics setup
        self.import_summoned_assets()
        self.status = 'down_idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.trigger_death_particles = trigger_death_particles

        # life
        self.life_duration = 20000
        self.time_alive = pygame.time.get_ticks()

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites
        self.following = False

        # entrance
        self.trigger_death_particles((self.hitbox.centerx, self.hitbox.centery), 'smoke')

        # stats
        self_info = summoned_data[self.summoned_type]
        self.health = self_info['health']
        self.speed = self_info['speed']
        self.attack_damage = self_info['damage']
        self.resistance = self_info['resistance']
        self.attack_radius = self_info['attack_radius']
        self.notice_radius = self_info['notice_radius']
        self.attack_type = self_info['attack_type']
        self.follow_radius = 80

        # enemy interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 300
        # self.trigger_death_particles = trigger_death_particles
        self.attackable_sprites = attackable_sprites

        # attack
        self.attacking = False
        self.attacking_time = None
        self.attacking_duration = 200
        self.attack_active = False

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # death
        self.dead = False
        self.death_time = None
        self.death_duration = 1000

    def import_summoned_assets(self):
        character_path = f'graphics/npcs/{self.summoned_type}/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [], 'dead': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def get_enemy_distance_direction(self):
        self_vec = pygame.math.Vector2(self.rect.center)
        enemy_vec = pygame.math.Vector2()
        distance = 0
        closest_distance = 500

        for sprite in self.attackable_sprites:
            if sprite.sprite_type == 'enemy':
                enemy_vec = pygame.math.Vector2(sprite.rect.center)
                distance = (enemy_vec - self_vec).magnitude()

                if distance < closest_distance:
                    closest_distance = distance

        if closest_distance > 0:
            direction = (enemy_vec - self_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return closest_distance, direction

    def get_closest_enemy(self):
        self_vec = pygame.math.Vector2(self.rect.center)
        enemy_vec = pygame.math.Vector2()
        distance = 0
        closest_distance = 500
        closest_enemy = None

        for sprite in self.attackable_sprites:
            if sprite.sprite_type == 'enemy':
                enemy_vec = pygame.math.Vector2(sprite.rect.center)
                distance = (enemy_vec - self_vec).magnitude()

                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = sprite

        return closest_enemy

    def get_player_distance_direction(self, player):
        summoned_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - summoned_vec).magnitude()

        if distance > 0:
            direction = (player_vec - summoned_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    def get_status(self, player):
        distance = self.get_enemy_distance_direction()[0]
        distance_to_player = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius:

            if self.can_attack:
                self.can_attack = False
                self.attack_time = pygame.time.get_ticks()
                self.attacking = True
                self.attacking_time = pygame.time.get_ticks()
                self.attack_active = True

            elif not self.can_attack and self.attacking:
                if not 'attack' in self.status:
                    if 'idle' in self.status:
                        self.status = self.status.replace('_idle', '_attack')
                    else:
                        self.status = self.status + '_attack'

            else:
                if not 'idle' in self.status:
                    if 'attack' in self.status:
                        self.status = self.status.replace('_attack', '_idle')
                    else:
                        self.status = self.status + '_idle'

            self.following = False

        elif distance <= self.notice_radius:
            if 'idle' in self.status:
                self.status = self.status.replace('_idle', '')
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')
            self.following = False

        elif distance_to_player > self.follow_radius:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')
            if 'idle' in self.status:
                self.status = self.status.replace('_idle', '')
            self.following = True

        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

            if 'idle' in player.status:
                if not 'idle' in self.status and not 'attack' in self.status:
                    self.status = self.status + '_idle'

    def actions(self, player):
        if 'attack' in self.status and self.attack_active:
            self.attack_logic(player)

        elif not 'idle' in self.status and not 'attack' in self.status:
            if not self.following:
                self.direction = self.get_enemy_distance_direction()[1]

            else:
                self.direction = self.get_player_distance_direction(player)[1]

        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
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

        if self.attacking:
            if current_time - self.attacking_time >= self.attacking_duration:
                self.attacking = False

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

        if not self.dead:
            if current_time - self.time_alive >= self.life_duration:
                self.dead = True
                self.death_time = pygame.time.get_ticks()

        if self.dead:
            if current_time - self.death_time >= self.death_duration:
                print('made it')
                self.die()

    def move(self, speed, player):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        if abs(self.direction.x * speed) > abs(self.direction.y * speed):
            if self.direction.x > 0:
                self.status = 'right'
            elif self.direction.x < 0:
                self.status = 'left'
        else:
            if self.direction.y > 0:
                self.status = 'down'
            elif self.direction.y < 0:
                self.status = 'up'

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal', player)
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical', player)
        self.rect.center = self.hitbox.center

    def collision(self, direction, player):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

            if player.hitbox.colliderect(self.hitbox):
                if self.direction.x > 0:  # moving right
                    self.hitbox.right = player.hitbox.left
                if self.direction.x < 0:  # moving left
                    self.hitbox.left = player.hitbox.right

            for sprite in self.attackable_sprites:
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

            if player.hitbox.colliderect(self.hitbox):
                if self.direction.y > 0:  # moving down
                    self.hitbox.bottom = player.hitbox.top
                if self.direction.y < 0:  # moving up
                    self.hitbox.top = player.hitbox.bottom

            for sprite in self.attackable_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def attack_logic(self, player):
        enemy = self.get_closest_enemy()
        enemy.get_damage(player, 'summoned')

        self.attack_active = False

    def get_damage(self, amount):
        if self.vulnerable:
            self.health -= amount
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def check_death(self):
        if self.health <= 0:
            self.dead = True
            self.death_time = pygame.time.get_ticks()

    def die(self):
        self.kill()
        self.trigger_death_particles((self.hitbox.centerx, self.hitbox.centery), 'smoke')

    def update(self):
        # self.hit_reaction()
        self.animate()
        self.cooldowns()
        self.check_death()

    def summoned_update(self, player):
        if not self.dead:
            self.move(self.speed, player)
            self.get_status(player)
            self.actions(player)
        else:
            self.status = 'dead'


