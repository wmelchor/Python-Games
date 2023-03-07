import pygame
from os import walk
from random import choice


class Car(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)
        self.name = 'car'
        # This will be a random car from the cars folder
        for folder_name, sub_folder, img_list in walk('../graphics/cars'):
            car_name = choice(img_list)
        self.image = pygame.image.load('../graphics/cars/' + car_name).convert_alpha()
        self.rect = self.image.get_rect(center = position)
        # float based movement
        self.pos = pygame.math.Vector2(self.rect.center)

        if position[0] < 200:
            self.direction = pygame.math.Vector2(1, 0)
        else:
            self.direction = pygame.math.Vector2(-1, 0)
            # This will flip the car on the X axis
            self.image = pygame.transform.flip(self.image, True, False)
        self.speed = 300
        self.hitbox = self.rect.inflate(0, -self.rect.height / 2)

    def update(self, delta_time):
        self.pos += self.direction * self.speed * delta_time
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        self.rect.center = self.hitbox.center
        # Basically if the car is outside the map
        if not -200 < self.rect.x < 3400:
            self.kill()
