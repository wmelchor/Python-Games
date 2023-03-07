import pygame
from pygame.math import Vector2 as vector
from settings import *
from os import walk
from entity import Entity


class Enemy(Entity):
    def __init__(self, position, groups, path, collision_sprites, shoot, player):
        super().__init__(position, groups, path, shoot)
        self.player = player
        for sprite in collision_sprites.sprites():
            if sprite.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = sprite.rect.top

        # overwrite
        self.cooldown = 1500

    def get_status(self):
        if self.player.rect.centerx < self.rect.centerx:
            self.status = 'left'
        else:
            self.status = 'right'

    def check_fire(self):
        enemy_pos = vector(self.rect.center)
        player_pos = vector(self.player.rect.center)

        distance = (player_pos - enemy_pos).magnitude()
        # Will only shoot if the player is in the same vertical position as the enemy
        same_y = True if self.rect.top - 20 < player_pos.y < self.rect.bottom + 20 else False

        if distance < 600 and same_y and self.can_shoot:
            bullet_direction = vector(1, 0) if self.status == 'right' else vector(-1, 0)
            y_offset = vector(0, -16)
            position = self.rect.center + bullet_direction * 80
            self.shoot(position + y_offset, bullet_direction, self)

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            self.shoot_sound.play()

    def update(self, delta_time):
        self.get_status()
        self.animate(delta_time)
        self.blink()

        self.shoot_timer()
        self.check_fire()
        self.invul_timer()

        self.check_death()