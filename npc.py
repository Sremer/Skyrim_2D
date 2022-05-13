import pygame
from settings import *
from support import import_folder
from entity import Entity
from random import choice, randint


class NPC(Entity):
    def __init__(self, pos, groups, name, sprite_type, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(f'graphics/npcs/{name}/down_idle/down_idle.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        # general setup
        self.name = name
        self.sprite_type = sprite_type
        self.import_npc_assets()
        self.status = 'down'
        self.change = False
        self.change_time = pygame.time.get_ticks()
        self.change_cooldown = 500

        # movement
        self.origin = pygame.math.Vector2(pos)
        self.max_distance = 200
        self.speed = 3
        self.just_idled = False
        self.talk = False
        self.talk_radius = 75

        # sprite groups
        self.obstacle_sprites = obstacle_sprites

    def import_npc_assets(self):
        character_path = f'graphics/npcs/{self.name}/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def get_player_distance_direction(self, player):
        npc_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - npc_vec).magnitude()

        if distance > 0:
            direction = (player_vec - npc_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    def movement_logic(self):
        walk_or_idle = randint(1, 2)
        if self.just_idled:
            walk_or_idle = 1

        if walk_or_idle == 1: # walk
            origin_vec = pygame.math.Vector2(self.origin)
            direction = None
            possible_x = 0
            possible_y = 0

            while True:
                direction = choice(['up', 'down', 'left', 'right'])
                possible_x = 0
                possible_y = 0
                if direction == 'up':
                    possible_y = -1
                    if self.hitbox.y + (possible_y * self.speed) < self.origin.y - 200:
                        continue
                elif direction == 'down':
                    possible_y = 1
                    if self.hitbox.y + (possible_y * self.speed) > self.origin.y + 200:
                        continue
                elif direction == 'left':
                    possible_x = -1
                    if self.hitbox.x + (possible_x * self.speed) < self.origin.x - 200:
                        continue
                else:
                    possible_x = 1
                    if self.hitbox.x + (possible_x * self.speed) > self.origin.x + 200:
                        continue

                self.just_idled = False
                break

            self.direction = pygame.math.Vector2(possible_x, possible_y)
            self.status = direction

        else: # idle
            self.direction.x = 0
            self.direction.y = 0
            self.just_idled = True

        self.change = False
        self.change_time = pygame.time.get_ticks()

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        # idle status
        if distance <= self.talk_radius:
            self.direction.x = 0
            self.direction.y = 0
            self.talk = True
            player.talk = True
            self.change = False
        elif self.talk and distance > self.talk_radius:
            player.talk = False
        else:
            self.talk = False

        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status:
                self.status = self.status + '_idle'

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.change:
            if current_time - self.change_time >= self.change_cooldown:
                self.change = True

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.movement_logic()

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.movement_logic()

    def update(self):
        if self.change:
            self.movement_logic()
        self.cooldowns()
        self.animate()
        self.move(self.speed)

    def npc_update(self, player):
        self.get_status(player)


class SpeechBox(pygame.sprite.Sprite):
    def __init__(self, groups, sprite_type, words):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.sprite_type = sprite_type
        self.words = words
        self.height = self.display_surface.get_size()[1] * 0.3
        self.width = self.display_surface.get_size()[0] * 0.8

        # timer
        self.can_kill = False
        self.time = pygame.time.get_ticks()
        self.cooldown_time = 300

        self.pos = (WIDTH // 10 + 100, HEIGTH // 2 + 150)
        self.speech_box = pygame.Rect(WIDTH // 10, HEIGTH // 2 + 100, self.width, self.height)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and self.can_kill:
            return False
        else:
            return True

    def cooldown(self):
        current_time = pygame.time.get_ticks()

        if not self.can_kill:
            if current_time - self.time >= self.cooldown_time:
                self.can_kill = True

    def create(self):
        text_surf = self.font.render(self.words, False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.pos)

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.speech_box)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.speech_box, 3)

    def update(self):
        self.create()
        self.cooldown()
        return self.input()

