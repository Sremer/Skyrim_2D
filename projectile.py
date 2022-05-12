import pygame
import math
from settings import *


class Projectile(pygame.sprite.Sprite):
    def __init__(self, player, groups, sprite_type, obstacle_sprites, attackable_sprites, projectiles_to_remove, range):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.direction = player.status.split('_')[0]
        self.distance = 0
        self.range = int(range * 10)
        self.speed = 25

        # sprite groups
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.projectiles_to_remove = projectiles_to_remove

        # graphic
        full_path = f'graphics/weapons/{sprite_type}/{self.direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if self.direction == 'right':
            self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(0, 16))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))
        elif self.direction == 'down':
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
        else:
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))

    def move(self):
        self.distance += self.speed
        if self.direction == 'left':
            self.rect.centerx -= self.speed
        elif self.direction == 'right':
            self.rect.centerx += self.speed
        elif self.direction == 'up':
            self.rect.centery -= self.speed
        else:
            self.rect.centery += self.speed
        self.collision()

        if self.distance >= self.range:
            self.kill()

    def collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.projectiles_to_remove.append(self)
        for sprite in self.attackable_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.projectiles_to_remove.append(self)

    def update(self):
        self.move()


class LongShotArrow(pygame.sprite.Sprite):
    def __init__(self, player, groups, obstacle_sprites, attackable_sprites, target_sprite, projectiles_to_remove, vertical_change, horizontal_change):
        super().__init__(groups)
        self.sprite_type = 'long shot arrow'
        self.direction = player.status.split('_')[0]
        self.speed = 40
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.offset.x = player.rect.centerx - (self.half_width * horizontal_change)
        self.offset.y = player.rect.centery - (self.half_height * vertical_change)
        self.range = 1300
        self.distance = 0

        # sprite groups
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.projectiles_to_remove = projectiles_to_remove
        self.target_sprite = target_sprite

        # target
        # placement
        if self.direction == 'right':
            self.pos = (player.rect.midright + pygame.math.Vector2(0, 16))
        elif self.direction == 'left':
            self.pos = (player.rect.midleft + pygame.math.Vector2(0, 16))
        elif self.direction == 'down':
            self.pos = (player.rect.midbottom + pygame.math.Vector2(-10, 0))
        else:
            self.pos = (player.rect.midtop + pygame.math.Vector2(-10, 0))

        for sprite in self.target_sprite:
            self.target_x = sprite.rect.centerx + self.offset.x + 20
            self.target_y = sprite.rect.centery + self.offset.y + 20

        x, y = self.pos
        mx, my = self.target_x, self.target_y
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0] / length, self.dir[1] / length)
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

        # graphic
        full_path = f'graphics/weapons/arrow/right.png'
        self.image = pygame.image.load(full_path).convert_alpha()
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.pos)

    def move(self):
        self.rect.center = (self.rect.centerx + self.dir[0] * self.speed,
                    self.rect.centery + self.dir[1] * self.speed)
        self.distance += self.speed

        self.collision()

        if self.distance >= self.range:
            self.kill()

    def collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.projectiles_to_remove.append(self)
        for sprite in self.attackable_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.projectiles_to_remove.append(self)
        for sprite in self.target_sprite:
            if sprite.rect.colliderect(self.rect):
                self.projectiles_to_remove.append(self)

    def update(self):
        self.move()


class Target(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.direction = pygame.math.Vector2()
        full_path = f'graphics/weapons/arrow/target.png'
        self.image = pygame.image.load(full_path).convert_alpha()
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGTH//2))
        self.speed = 10

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        offset = 25

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > WIDTH - offset:
            self.rect.x = WIDTH - offset

        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > HEIGTH - offset:
            self.rect.y = HEIGTH - offset

    def update(self):
        self.input()
        self.move()

