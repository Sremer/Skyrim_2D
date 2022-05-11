import pygame


class Projectile(pygame.sprite.Sprite):
    def __init__(self, player, groups, sprite_type, obstacle_sprites, attackable_sprites, projectiles_to_remove, range):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.direction = player.status.split('_')[0]
        self.distance = 0
        self.range = int(range * 10)

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
        self.distance += 10
        if self.direction == 'left':
            self.rect.centerx -= 10
        elif self.direction == 'right':
            self.rect.centerx += 10
        elif self.direction == 'up':
            self.rect.centery -= 10
        else:
            self.rect.centery += 10
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
