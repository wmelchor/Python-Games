from re import match
from entity import Entity
import pygame, sys
from pygame.math import Vector2 as vector



class Player(Entity):
    def __init__(self, position, groups, path, collision_sprites, create_bullet):
        super().__init__(position, groups, path, collision_sprites)
        self.create_bullet = create_bullet
        self.bullet_shot = False

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            # Makes sure the string only has a direction and is not adding multiple _idle
            self.status = self.status.split('_')[0] + '_idle'

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.attacking:
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
        # In own time, fix space bar needing to be let go to shoot. (Caused by frame index being stuck at 0),
        # Which means that pressing space bar many times results in canceling animation
        if keys[pygame.K_SPACE]:
            self.attacking = True
            self.direction = vector()
            self.frame_index = 0
            self.bullet_shot = False

            if self.status.split('_')[0] == 'left':
                self.bullet_direction = vector(-1, 0)
            elif self.status.split('_')[0] == 'right':
                self.bullet_direction = vector(1, 0)
            elif self.status.split('_')[0] == 'up':
                self.bullet_direction = vector(0, -1)
            else:
                self.bullet_direction = vector(0, 1)

            # This is a switch statement. Don't know why it's underlined but it works
            #match self.status.split('_')[0]:
             #   case 'left': self.bullet_direction = vector(-1, 0)
              #  case 'right': self.bullet_direction = vector(1, 0)
               # case 'up': self.bullet_direction = vector(0, -1)
                #case 'down': self.bullet_direction = vector(0, 1)

    def animate(self, delta_time):
        current_animation = self.animations[self.status]
        self.frame_index += 7 * delta_time

        if int(self.frame_index) == 3 and self.attacking and not self.bullet_shot:
            bullet_start_pos = self.rect.center + self.bullet_direction * 80
            self.create_bullet(bullet_start_pos, self.bullet_direction)
            self.bullet_shot = True
            self.shoot_sound.play()

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def check_death(self):
        if self.health <= 0:
            pygame.quit()
            sys.exit()

    def update(self, delta_time):
        self.input()
        self.get_status()
        self.move(delta_time)
        self.animate(delta_time)
        self.blink()
        self.check_death()
        self.vulnerability_timer()