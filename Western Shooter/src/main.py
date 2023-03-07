import pygame, sys
from pytmx.util_pygame import load_pygame
from pygame.math import Vector2 as vector
from settings import *
from player import Player
from sprite import Sprite, Bullet
from monster import Coffin, Cactus


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load('../graphics/other/bg.png').convert()

    def customize_draw(self, player):
        # change offset vector. Moves the background in accordance to the player
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT /2

        # blit the surface bg. -offset helps move the background in accordance to the player
        self.display_surface.blit(self.bg, -self.offset)

        # sprites inside the group (player)
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            # Moves the background in accordance to the player
            offset_rect = sprite.image.get_rect(center = sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        # Doing this here, so that we only need to load the bullet once
        self.bullet_surface = pygame.image.load('../graphics/other/particle.png').convert_alpha()
        pygame.display.set_caption('Shooter')

        # groups
        self.all_sprites = AllSprites()
        self.obstacles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

        self.setup()
        self.music = pygame.mixer.Sound('../sound/music.mp3')
        self.music.set_volume(0.3)
        self.music.play(loops = -1)

    def create_bullet(self, position, direction):
        Bullet(position, direction, self.bullet_surface, [self.all_sprites, self.bullets])

    def bullet_collision(self):
        # bullet obstacle collision
        for obstacle in self.obstacles.sprites():
            pygame.sprite.spritecollide(obstacle, self.bullets, True)

        # bullet monster collision
        for bullet in self.bullets.sprites():
            sprites = pygame.sprite.spritecollide(bullet, self.monsters, False, pygame.sprite.collide_mask)

            if sprites:
                bullet.kill()
                for sprite in sprites:
                    sprite.damage()

        # Player bullet collision
        # This sprite collide method does return a list, so the if statement returns true if the list has content
        if pygame.sprite.spritecollide(self.player, self.bullets, True, pygame.sprite.collide_mask):
            self.player.damage()

    def setup(self):
        tmx_map = load_pygame('../data/Map.tmx')

        # tiles
        for x, y, surface in tmx_map.get_layer_by_name('Fence').tiles():
            # Each pixel is multiplied by 64 to convert the tiles
            Sprite((x * 64, y * 64), surface, [self.all_sprites, self.obstacles])

        # objects
        for object in tmx_map.get_layer_by_name('Object'):
            Sprite((object.x, object.y), object.image, [self.all_sprites, self.obstacles])

        for object in tmx_map.get_layer_by_name('Entities'):
            if object.name == 'Player':
                # We are giving the player a reference to the obstacles, but they are not a part of that group
                self.player = Player(position = (object.x, object.y),
                                     groups = self.all_sprites,
                                     path = PATHS['player'],
                                     collision_sprites = self.obstacles,
                                     create_bullet = self.create_bullet)
            if object.name == 'Coffin':
                Coffin(position=(object.x, object.y),
                       groups=[self.all_sprites, self.monsters],
                       path=PATHS['coffin'],
                       collision_sprites=self.obstacles,
                       player = self.player)

            if object.name == 'Cactus':
                Cactus(position=(object.x, object.y),
                       groups=[self.all_sprites, self.monsters],
                       path=PATHS['cactus'],
                       collision_sprites=self.obstacles,
                       player = self.player,
                       create_bullet = self.create_bullet)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # dt
            delta_time = self.clock.tick() / 1000

            # update groups
            self.all_sprites.update(delta_time)
            self.bullet_collision()

            # draw groups
            self.display_surface.fill('black')
            self.all_sprites.customize_draw(self.player)

            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()