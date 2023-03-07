import pygame


class SimpleSprite(pygame.sprite.Sprite):
    def __init__(self, surface, position, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = position)
        # We want to vertically shrink the box used for the hitbox
        self.hitbox = self.rect.inflate(0, -self.rect.height / 2)


class LongSprite(pygame.sprite.Sprite):
    def __init__(self, surface, position, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = position)
        # For tall objects we want to do it slightly differently
        self.hitbox = self.rect.inflate(-self.rect.width * 0.8, -self.rect.height / 2)
        self.hitbox.bottom = self.rect.bottom - 10  # Shift the bottom of the hitbox by 10 pixels