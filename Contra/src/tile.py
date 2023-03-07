import pygame
from settings import *
from pygame.math import Vector2 as vector


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups, z):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = position)
        self.z = z


class CollisionTile(Tile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups, LAYERS['Level'])
        self.old_rect = self.rect.copy()


class MovingObject(CollisionTile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)
        self.direction = vector(0, -1)
        self.speed = 200
        self.position = vector(self.rect.topleft)

    def update(self, delta_time):
        self.old_rect = self.rect.copy()
        self.position.y += self.direction.y * self.speed * delta_time
        self.rect.topleft = (round(self.position.x), round(self.position.y))
