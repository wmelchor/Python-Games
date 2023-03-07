import pygame


class Sprite(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = position)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center = position)

        # float based movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = direction
        self.speed = 500

    def update(self, delta_time):
        self.pos += self.direction * self.speed * delta_time
        self.rect.center = (round(self.pos.x), round(self.pos.y))
