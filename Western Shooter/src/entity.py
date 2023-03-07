import pygame
from pygame.math import Vector2 as vector
from os import walk
from math import sin


class Entity(pygame.sprite.Sprite):
    def __init__(self, position, groups, path, collision_sprites):
        super().__init__(groups)
        self.import_assets(path)
        self.frame_index = 0
        self.status = 'down'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = position)

        # float based movement
        self.pos = vector(self.rect.center)
        self.direction = vector()
        self.speed = 400

        # collisions
        self.hitbox = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height / 2)
        self.collision_sprites = collision_sprites
        self.mask = pygame.mask.from_surface(self.image)

        # attack
        self.attacking = False

        # health
        self.health = 3
        self.is_vulnerable = True
        self.hit_time = None

        # sounds
        self.hit_sound = pygame.mixer.Sound('../sound/hit.mp3')
        self.hit_sound.set_volume(0.3)
        self.shoot_sound = pygame.mixer.Sound('../sound/bullet.wav')
        self.shoot_sound.set_volume(0.1)

    def blink(self):
        if not self.is_vulnerable:
            # This if statement will give us the actual blinking
            if self.wave_value():
                # Illustrates well what a mask is. White on the non-transparent part of an image
                # and black on the transparent part
                mask = pygame.mask.from_surface(self.image)
                white_surface = mask.to_surface()
                # We are getting rif of the black pixels
                white_surface.set_colorkey((0, 0, 0))
                self.image = white_surface

    def wave_value(self):
        # This will fluctuate from negative to positive values
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return True
        else:
            return False

    def damage(self):
        if self.is_vulnerable:
            self.health -= 1
            self.is_vulnerable = False
            self.hit_time = pygame.time.get_ticks()
            self.hit_sound.play()

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def vulnerability_timer(self):
        if not self.is_vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time > 400:
                self.is_vulnerable = True

    def import_assets(self, path):
        self.animations = {}    # Will be dictionary {animation status: frame}
        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    # Gives the name of the folder plus an empty list
                    self.animations[name] = []
            else:
                # Now we will have a dictionary for the animations, ex: down: [file1, file2...]
                # This will be in order thanks to the sort method. Split gives us the number before the period
                for file_name in sorted(folder[2], key = lambda string: int(string.split('.')[0])):
                    path = folder[0].replace('\\', '/') + '/' + file_name
                    surface = pygame.image.load(path).convert_alpha()
                    # This will simply give us the folder name of the file
                    key = folder[0].split('\\')[1]
                    self.animations[key].append(surface)

    def move(self, delta_time):
        # normalize the vector -> the length of the vector will be 1.
        # magnitude just gives length. Can't normalize length 0
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # horizontal movement + collision
        self.pos.x += self.direction.x * self.speed * delta_time
        # Use the hitbox for collision!
        self.hitbox.centerx = round(self.pos.x)
        # Use the rect for the drawing!
        self.rect.centerx = self.hitbox.centerx
        # horizontal collisions
        self.collision('horizontal')

        # vertical movement + collision
        self.pos.y += self.direction.y * self.speed * delta_time
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    # If we are moving right, then move us left of the object we collide with
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    # If we are moving left, then move us right of the object we collide with
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else:
                    # If we are moving down, then move us above the object we collide with
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    # If we are moving up, then move us below the object we collide with
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery