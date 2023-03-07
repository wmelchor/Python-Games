import pygame, sys
from settings import *
from player import Player
from car import Car
from sprite import SimpleSprite, LongSprite
from random import choice, randint


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # This offset changes where we are on the map, this can work as a camera
        self.offset = pygame.math.Vector2(0, 0)
        self.bg = pygame.image.load('../graphics/main/map.png').convert()
        self.fg = pygame.image.load('../graphics/main/overlay.png').convert_alpha()

    def customize_draw(self):

        # change the offset vector
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        # blit the bg, offset is negative so that the camera moves in the opposite direction as us
        display_surface.blit(self.bg, -self.offset)

        # Instead of drawing the sprite image, we can draw a green rectangle or something as seen below
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):  # Now the sprites will be ordered by y positions
            # size = sprite.rect.size
            # surface = pygame.Surface(size)
            # surface.fill('green')
            # display_surface.blit(surface, sprite.rect)
            offset_position = sprite.rect.topleft - self.offset
            display_surface.blit(sprite.image, offset_position)

        # blit the foreground
        display_surface.blit(self.fg, -self.offset)


pygame.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Frogger')
clock = pygame.time.Clock()

# groups
all_sprites = AllSprites()
# This will check what can be collided with
obstacle_sprites = pygame.sprite.Group()

# sprites
player = Player((2062, 3274), all_sprites, obstacle_sprites)

# timer
car_timer = pygame.event.custom_type()
pygame.time.set_timer(car_timer, 50)
pos_list = []

# font
font = pygame.font.Font(None, 50)
text_surface = font.render('You win!', True, 'White')
text_rect = text_surface.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

# music
music = pygame.mixer.Sound('../audio/music.mp3')
music.play(loops = -1)

# sprite setup
for file_name, position_list in SIMPLE_OBJECTS.items():
    path = f'../graphics/objects/simple/{file_name}.png'
    surface = pygame.image.load(path).convert_alpha()
    for position in position_list:
        SimpleSprite(surface, position, [all_sprites, obstacle_sprites])

for file_name, position_list in LONG_OBJECTS.items():
    path = f'../graphics/objects/long/{file_name}.png'
    surface = pygame.image.load(path).convert_alpha()
    for position in position_list:
        LongSprite(surface, position, [all_sprites, obstacle_sprites])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == car_timer:
            random_pos = choice(CAR_START_POSITIONS)
            if random_pos not in pos_list:
                pos_list.append(random_pos)
                pos = (random_pos[0], random_pos[1] + randint(-8, 8))
                Car(pos, [all_sprites, obstacle_sprites])
            if len(pos_list) > 5:
                del pos_list[0]

    keys = pygame.key.get_pressed()

    # dt
    delta_time = clock.tick(60) / 1000

    # bg
    display_surface.fill('black')

    if player.pos.y >= 1180:
        # update
        all_sprites.update(delta_time)

        # draw
        # all_sprites.draw(display_surface)
        all_sprites.customize_draw()

    else:
        display_surface.blit(text_surface, text_rect)

    pygame.display.update()