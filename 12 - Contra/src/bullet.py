import pygame
from pygame.math import Vector2 as vector
from settings import *
from os import walk


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, surface, direction, groups):
        super().__init__(groups)
        self.image = surface
        # flip the bullet if facing left
        if direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center = position)
        self.z = LAYERS['Level']

        # movement
        self.direction = direction
        self.speed = 1200
        self.pos = vector(self.rect.center)
        # Timer for kill
        self.start_time = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time):
        self.pos += self.direction * self.speed * delta_time
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        # Delete the bullet if fired and hasn't hit anything for a long time
        if pygame.time.get_ticks() - self.start_time > 1000:
            self.kill()


class FireAnimation(pygame.sprite.Sprite):
    def __init__(self, enitity, surface_list, direction, groups):
        super().__init__(groups)

        # setup
        self.entity = enitity
        self.frames = surface_list
        # flip the frames
        if direction.x < 0:
            self.frames = [pygame.transform.flip(frame, True, False) for frame in self.frames]

        # image
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # offset
        x_offset = 60 if direction.x > 0 else -60
        y_offset = 10 if enitity.duck else -16
        self.offset = vector(x_offset, y_offset)

        # position
        self.rect = self.image.get_rect(center = self.entity.rect.center + self.offset)
        self.z = LAYERS['Level']

    def animate(self, delta_time):
        self.frame_index += 15 * delta_time
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def move(self):
        # Now the firing animation should follow the player
        self.rect.center = self.entity.rect.center + self.offset

    def update(self, delta_time):
        self.animate(delta_time)
        self.move()
