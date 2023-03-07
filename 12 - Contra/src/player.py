import pygame, sys
from pygame.math import Vector2 as vector
from pygame._sdl2 import controller
from entity import Entity


class Player(Entity):
    def __init__(self, position, groups, path, collision_sprites, shoot):
        super().__init__(position, groups, path, shoot)

        # collision
        self.collision_sprites = collision_sprites

        # vertical movement
        self.gravity = 15
        self.jump_speed = 1000
        self.on_floor = False
        self.moving_floor = None

        self.health = 10

        self.gamepad = None


    def get_status(self):
        if self.direction.x == 0 and self.on_floor:
            # Makes sure the string only has a direction and is not adding multiple _idle
            self.status = self.status.split('_')[0] + '_idle'
        if self.duck and self.on_floor:
            self.status = self.status.split('_')[0] + '_duck'
        if self.direction.y != 0 and not self.on_floor:
            self.status = self.status.split('_')[0] + '_jump'

    def check_contact(self):
        bottom_rect = pygame.Rect(0, 0, self.rect.width, 5)
        bottom_rect.midtop = self.rect.midbottom
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(bottom_rect):
                if self.direction.y > 0:
                    self.on_floor = True
                # If the sprite has the attribute of direction (Like a moving plat!)
                if hasattr(sprite, 'direction'):
                    self.moving_floor = sprite

    def controller_input(self):
        pygame._sdl2.controller.init()
        if pygame._sdl2.controller.get_count() > 0:
            self.gamepad = pygame._sdl2.controller.Controller(0)
            self.gamepad.init()
            if self.gamepad.get_button(pygame.CONTROLLER_BUTTON_DPAD_LEFT):
                self.direction.x = -1
                self.status = 'left'
            elif self.gamepad.get_button(pygame.CONTROLLER_BUTTON_DPAD_RIGHT):
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
            if (self.gamepad.get_button(pygame.CONTROLLER_BUTTON_A) or self.gamepad.get_button(pygame.CONTROLLER_BUTTON_B)) and self.on_floor:
                self.direction.y = -self.jump_speed
            if self.gamepad.get_button(pygame.CONTROLLER_BUTTON_DPAD_DOWN):
                self.duck = True
            else:
                self.duck = False

            if (self.gamepad.get_button(pygame.CONTROLLER_BUTTON_Y) or self.gamepad.get_button(pygame.CONTROLLER_BUTTON_X)) and self.can_shoot:
                # direction of bullet = direction of player
                direction = vector(1, 0) if self.status.split('_')[0] == 'right' else vector(-1, 0)
                # starting point of bullet = edge of player
                position = self.rect.center + direction * 70
                y_offset = vector(0, -16) if not self.duck else vector(0, 10)
                self.shoot(position + y_offset, direction, self)
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()
                self.shoot_sound.play()
        else:
            pass

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
        if keys[pygame.K_UP] and self.on_floor:
            self.direction.y = -self.jump_speed
        if keys[pygame.K_DOWN]:
            self.duck = True
        else:
            self.duck = False

        if keys[pygame.K_SPACE] and self.can_shoot:
            # direction of bullet = direction of player
            direction = vector(1, 0) if self.status.split('_')[0] == 'right' else vector(-1, 0)
            # starting point of bullet = edge of player
            position = self.rect.center + direction * 70
            y_offset = vector(0, -16) if not self.duck else vector(0, 10)
            self.shoot(position + y_offset, direction, self)
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            self.shoot_sound.play()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    # If the current left side of the player is inside the right side of the sprite, then
                    # there was collision. Also checks if the old rect in the previous frame was coming from
                    # the right side in order to be sure of where to place the player. This will apply the same
                    # way to the other directions
                    # For left collision
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                    # For right collision
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                    self.pos.x = self.rect.x
                else:
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    # For right collision
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        # If the player is on top of a sprite then we are grounded
                        self.on_floor = True
                    self.pos.y = self.rect.y
                    # Vertical collision means our fall speed is 0
                    self.direction.y = 0
            if self.on_floor and self.direction.y != 0:
                self.on_floor = False

    def move(self, delta_time):
        # normalize the vector -> the length of the vector will be 1.
        # magnitude just gives length. Can't normalize length 0
        # if self.direction.magnitude() != 0:
        #   self.direction = self.direction.normalize()

        if self.duck and self.on_floor:
            self.direction.x = 0

        # horizontal movement + collision
        self.pos.x += self.direction.x * self.speed * delta_time
        # Use the hitbox for collision!
        #self.hitbox.centerx = round(self.pos.x)
        # Use the rect for the drawing!
        self.rect.x = round(self.pos.x)#self.hitbox.centerx
        # horizontal collisions
        self.collision('horizontal')

        # vertical movement + collision
        # gravity
        self.direction.y += self.gravity
        # Here self.speed was removed from the equation because it would cause us to fall too fast
        self.pos.y += self.direction.y * delta_time

        # If there is a moving floor and the moving floor is moving down and we are not jumping
        # then we glue the player to the moving floor
        if self.moving_floor and self.moving_floor.direction.y > 0 and self.direction.y > 0:
            self.direction.y = 0
            self.rect.bottom = self.moving_floor.rect.top
            self.pos.y = self.rect.y
            self.on_floor = True

        self.rect.y = round(self.pos.y)
        self.collision('vertical')
        self.moving_floor = None

    def check_death(self):
        if self.health <= 0:
            pygame._sdl2.controller.Controller.quit
            pygame.quit()
            sys.exit()

    def restrict(self):
        if self.rect.left < 250:
            # This will place the player so that the position of the player's center is a bit to the right of 250
            self.rect.left = 250
            self.pos.x = self.rect.x
        # This one doesn't matter
        if self.rect.right > 10060:
            # This will place the player so that the position of the player's center is a bit to the right of 10060
            self.rect.right = 10060
            self.pos.x = self.rect.width
        if self.rect.bottom > 8400:
            self.health = 0

    def update(self, delta_time):
        self.old_rect = self.rect.copy()
        self.input()
        self.controller_input()
        self.restrict()
        self.get_status()
        self.move(delta_time)
        self.check_contact()
        self.animate(delta_time)
        self.blink()
        self.shoot_timer()
        self.invul_timer()

        self.check_death()