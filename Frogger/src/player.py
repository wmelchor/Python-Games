import pygame, sys
from os import walk


class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_sprites):
        super().__init__(groups)
        self.import_assets()
        self.frame_index = 0
        self.status = 'up'
        # self.image = self.animation[self.frame_index]
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)

        # float based movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 300

        # Collisions
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate(0, -self.rect.height / 2)

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.collision_sprites.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if hasattr(sprite, 'name') and sprite.name == 'car':
                        pygame.quit()
                        sys.exit()
                    # If we are moving right, then move us left of the object we collide with
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    # If we are moving left, then move us right of the object we collide with
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
        else:
            for sprite in self.collision_sprites.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if hasattr(sprite, 'name') and sprite.name == 'car':
                        pygame.quit()
                        sys.exit()
                    # If we are moving down, then move us above the object we collide with
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                    # If we are moving up, then move us below the object we collide with
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

        # This destroys things I come in contact with
        # for sprite in self.collision_sprites.sprites():
        #    if sprite.rect.colliderect(self.rect):
        #        sprite.kill()

    def import_assets(self):
        # better import
        self.animations = {}
        # Folder[0] gives us the path to the folder, but for some reason has a forward slash[../graphics/player\left]
                                                            # That's something we need to fix with a string method
        # Folder[1] gives us the names of the folders containing the frames of animation
        # Folder[2] gives us the list of string names for the frames of animation [eg 1.png]
        for index, folder in enumerate(walk('../graphics/player')):
            if index == 0:
                for name in folder[1]:
                    # Gives the name of the folder plus an empty list
                    self.animations[name] = []
            else:
                # Now we will have a dictionary for the animations, ex: down: [file1, file2...]
                for file_name in folder[2]:
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

        # self.pos += self.direction * self.speed * delta_time
        # self.rect.center = round(self.pos.x), round(self.pos.y)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

    def animate(self, delta_time):
        current_animation = self.animations[self.status]
        # If there is movement
        if self.direction.magnitude() != 0:
            self.frame_index += 10 * delta_time
            if self.frame_index >= len(current_animation):
                self.frame_index = 0
        else:
            self.frame_index = 0
        self.image = current_animation[int(self.frame_index)]

    def restrict(self):
        if self.rect.left < 640:
            # This will place the player so that the position of the player's center is a bit to the right of 640
            self.pos.x = 640 + self.rect.width / 2
            self.hitbox.left = 640
            self.rect.left = 640
        if self.rect.right > 2560:
            # This will place the player so that the position of the player's center is a bit to the right of 640
            self.pos.x = 2560 - self.rect.width / 2
            self.hitbox.right = 2560
            self.rect.right = 2560
        if self.rect.bottom > 3500:
            # This will place the player so that the position of the player's center is a bit to the right of 640
            self.pos.y = 3500 - self.rect.height / 2
            self.rect.bottom = 3500
            # Hitbox is shorter, so do it slightly differently
            self.hitbox.centery = self.rect.centery

    def update(self, delta_time):
        self.input()
        self.move(delta_time)
        self.animate(delta_time)
        self.restrict()
