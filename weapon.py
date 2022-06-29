import pygame
from support import import_folder


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups, hand):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        direction = player.status.split('_')[0]
        weapon = None
        if hand == 'bow':
            weapon = 'bow'
        elif hand == 'Main-Hand':
            weapon = player.weapon
        else:
            weapon = player.offhand_weapon

        # graphic
        if not weapon == 'bow':
            full_path = f'graphics/weapons/{weapon}/{direction}.png'
            self.image = pygame.image.load(full_path).convert_alpha()

            # placement
            if direction == 'right':
                self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(0, 16))
            elif direction == 'left':
                self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))
            elif direction == 'down':
                self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
            else:
                self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))


class Bow(Weapon):
    def __init__(self, player, groups, hand):
        super().__init__(player, groups, hand)
        self.status = 0
        self.direction = player.status.split('_')[0]
        self.player = player

        # animation
        self.import_assets()
        self.image = self.animations[self.direction][self.status]
        offset = 12
        if self.direction == 'right':
            self.rect = self.image.get_rect(midleft=self.player.rect.midright + pygame.math.Vector2(0 - offset, 16))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(midright=self.player.rect.midleft + pygame.math.Vector2(0 + offset, 16))
        elif self.direction == 'down':
            self.rect = self.image.get_rect(midtop=self.player.rect.midbottom + pygame.math.Vector2(-10, 0 - offset))
        else:
            self.rect = self.image.get_rect(midbottom=self.player.rect.midtop + pygame.math.Vector2(-10, 0 + offset))

    def import_assets(self):
        character_path = f'graphics/weapons/bow/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate_and_place(self):
        animation = self.animations[self.direction]

        self.image = animation[self.status]

        if self.status == 2:
            offset = 24
        elif self.status == 1:
            offset = 19
        else:
            offset = 12

        if self.direction == 'right':
            self.rect = self.image.get_rect(midleft=self.player.rect.midright + pygame.math.Vector2(0 - offset, 16))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(midright=self.player.rect.midleft + pygame.math.Vector2(0 + offset, 16))
        elif self.direction == 'down':
            self.rect = self.image.get_rect(midtop=self.player.rect.midbottom + pygame.math.Vector2(-10, 0 - offset))
        else:
            self.rect = self.image.get_rect(midbottom=self.player.rect.midtop + pygame.math.Vector2(-10, 0 + offset))

    def update(self):
        self.animate_and_place()
