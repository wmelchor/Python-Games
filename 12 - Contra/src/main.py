import pygame, sys
from settings import *
from player import Player
from pytmx.util_pygame import load_pygame
from pygame.math import Vector2 as vector
from tile import Tile, CollisionTile, MovingObject
from bullet import Bullet, FireAnimation
from enemy import Enemy
from overlay import Overlay


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()

        # sky
        self.fg_sky = pygame.image.load('../graphics/sky/fg_sky.png').convert_alpha()
        self.bg_sky = pygame.image.load('../graphics/sky/bg_sky.png').convert_alpha()

        self.padding = WINDOW_WIDTH / 2
        self.sky_width = self.bg_sky.get_width()
        tmx_map = load_pygame('../data/map.tmx')
        # How wide each tile is * amount of tiles in width
        map_width = tmx_map.tilewidth * tmx_map.width + (2 * self.padding)
        self.sky_num = int(map_width // self.sky_width)

    def customize_draw(self, player):
        # change offset vector. Moves the background in accordance to the player
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT /2

        for x in range(self.sky_num):
            x_pos = -self.padding * (x * self.sky_width)
            # Inserting the background/fg with slightly messy code. Moves the bg and fg a bit at diff speeds when player moves
            # thanks to the offset / 2.5 or 2. 800 is kind of arbitrary, just a guestimate.
            self.display_surface.blit(self.bg_sky, (x_pos - self.offset.x / 2.5, 850 - self.offset.y / 2.5))
            self.display_surface.blit(self.fg_sky, (x_pos - self.offset.x / 2, 850 - self.offset.y / 2))

        # blit all sprites
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.z):
            # Moves the background in accordance to the player
            offset_rect = sprite.image.get_rect(center=sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)


class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Contra')
        self.clock = pygame.time.Clock()

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.platform_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.vulnerable_sprites = pygame.sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)

        # bullet images
        self.bullet_surf = pygame.image.load('../graphics/bullet.png').convert_alpha()
        self.fire_surfaces = [pygame.image.load('../graphics/fire/0.png').convert_alpha(), pygame.image.load('../graphics/fire/1.png').convert_alpha()]

        self.music = pygame.mixer.Sound('../audio/music.wav')
        self.music.set_volume(0.2)
        self.music.play(loops = -1)

    def platform_collisions(self):
        for platform in self.platform_sprites.sprites():
            for border in self.platform_border_rects:
                # bounce the platforms
                # If the platform is moving up -> place the top of the plat at the bottom of the border
                # Change the direction of the plat
                if platform.rect.colliderect(border):
                    if platform.direction.y < 0: # up
                        platform.rect.top = border.bottom
                        platform.position.y = platform.rect.y
                        platform.direction.y = 1
                    else: # down
                        platform.rect.bottom = border.top
                        platform.position.y = platform.rect.y
                        platform.direction.y = -1
            # if the platform bottom collides with the top of the player, then move the plat up
            if platform.rect.colliderect(self.player.rect) and self.player.rect.centery > platform.rect.centery:
                platform.rect.bottom = self.player.rect.top
                platform.position.y = platform.rect.y
                platform.direction.y = -1

    def bullet_collision(self):
        # obstacles
        for obstacles in self.collision_sprites.sprites():
            # Kill bullet sprite once it collides with an obstacle
            pygame.sprite.spritecollide(obstacles, self.bullet_sprites, True)

        # entities
        for sprite in self.vulnerable_sprites.sprites():
            if pygame.sprite.spritecollide(sprite, self.bullet_sprites, True, pygame.sprite.collide_mask):
                sprite.damage()

    def shoot(self, position, direction, entity):
        Bullet(position, self.bullet_surf, direction, [self.all_sprites, self.bullet_sprites])
        FireAnimation(entity, self.fire_surfaces, direction, self.all_sprites)

    def setup(self):
        tmx_map = load_pygame('../data/map.tmx')

        # tiles, is separate because it will have collision
        # Returns a tuple
        for x, y, surface in tmx_map.get_layer_by_name('Level').tiles():
            # Right now this doesn't give us anything as the actual level is far below the window
            CollisionTile((x * 64, y * 64), surface, [self.all_sprites, self.collision_sprites])

        # background, background detail, foreground detail bottom, foreground detail top
        for layer in ['BG', 'BG Detail', 'FG Detail Bottom', 'FG Detail Top']:
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                Tile((x * 64, y * 64), surface, self.all_sprites, LAYERS[layer])

        # objects
        for object in tmx_map.get_layer_by_name('Entities'):
            if object.name == 'Player':
                # We are giving the player a reference to the obstacles, but they are not a part of that group
                self.player = Player(position = (object.x, object.y),
                                     groups = [self.all_sprites, self.vulnerable_sprites],
                                     path= '../graphics/player',
                                     collision_sprites = self.collision_sprites,
                                     shoot = self.shoot)
            if object.name == 'Enemy':
                # We are giving the player a reference to the obstacles, but they are not a part of that group
                self.enemy = Enemy(position=(object.x, object.y),
                                    groups= [self.all_sprites, self.vulnerable_sprites],
                                    path='../graphics/enemy',
                                    collision_sprites = self.collision_sprites,
                                    shoot=self.shoot,
                                    player = self.player)

        self.platform_border_rects = []
        for object in tmx_map.get_layer_by_name('Platforms'):
            if object.name == 'Platform':
                MovingObject((object.x, object.y), object.image, [self.all_sprites, self.collision_sprites, self.platform_sprites])
            # border
            else:
                border_rect = pygame.Rect(object.x, object.y, object.width, object.height)
                # Now we have access to the platforms and borders
                self.platform_border_rects.append(border_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            delta_time = self.clock.tick() / 1000
            self.display_surface.fill((249, 131, 103))

            self.platform_collisions()
            self.all_sprites.update(delta_time)
            self.bullet_collision()

            self.all_sprites.customize_draw(self.player)
            self.overlay.display()

            pygame.display.update()


if __name__ == '__main__':
    main = Main()
    main.run()