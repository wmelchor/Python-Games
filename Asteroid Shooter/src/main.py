import pygame, sys
from random import randint, uniform


class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):
        # 1. We have to init the parent class
        super().__init__(groups)
        # 2. We need a surface -> image
        self.image = pygame.image.load('../graphics/ship.png').convert_alpha()
        # 3. We need a rect
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2))
        # Mask
        self.mask = pygame.mask.from_surface(self.image)
        # timer
        self.can_shoot = True
        self.shoot_time = None

        # Sound
        self.laser_sound = laser_sound = pygame.mixer.Sound('../sounds/laser.ogg')

    def input_position(self):
        self.rect.center = pygame.mouse.get_pos()

    def laser_timer(self, duration=300):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > duration:
                self.can_shoot = True

    def laser_shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            Laser(laser_group, self.rect.midtop)
            self.laser_sound.play()

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, False, pygame.sprite.collide_mask):
            # Maybe implement loss screen + option to restart (Needs to pause all other elements too)
            pygame.quit()
            sys.exit()

    def update(self):
        self.laser_timer()
        self.laser_shoot()
        self.input_position()
        self.meteor_collision()


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, xy_pos):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom= xy_pos)
        self.mask = pygame.mask.from_surface(self.image)

        # float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)  # Like tuple but with float
        self.direction = pygame.math.Vector2(0,-1)
        self.speed = 600
        self.score = 0

        # Sound
        self.explosion_sound = pygame.mixer.Sound('../sounds/explosion.wav')

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            self.kill()
            score.update_score()
            self.explosion_sound.play()

    def update(self):
        # As of right now, this gives us [0,-1] * 600 * 0.001 = [0,-0.6], so we move -0.6 in the y axis per frame
        self.pos += self.direction * self.speed * delta_time
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        if self.rect.bottom < 0:
            self.kill()
        self.meteor_collision()




class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, xy_pos):
        super().__init__(groups)
        # Randomize meteor size
        meteor_surface = pygame.image.load('../graphics/meteor.png').convert_alpha()
        meteor_size = pygame.math.Vector2(meteor_surface.get_size()) * uniform(0.5, 1.5)
        self.scaled_surface = pygame.transform.scale(meteor_surface, meteor_size)
        self.image = self.scaled_surface
        self.rect = self.image.get_rect(center = xy_pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.5,0.5), 1)
        self.speed = randint(300,500)

        # Rotation logic
        self.rotation = 0
        self.rotation_speed = randint(20,50)

    def rotate(self):
        self.rotation += self.rotation_speed * delta_time
        rotated_surface = pygame.transform.rotozoom(self.scaled_surface, self.rotation, 1)
        self.image = rotated_surface
        self.rect = self.image.get_rect(center = self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += self.direction * self.speed * delta_time
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotate()
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class Score:
    def __init__(self):
        self.font = pygame.font.Font('../graphics/subatomic.ttf', 50)
        self.score = 0

    def update_score(self):
        self.score += 1

    def display(self):
        score_text = f'Score: {self.score}'
        text_surface = self.font.render(score_text, True, 'White')
        text_rect = text_surface.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.2))
        display_surface.blit(text_surface, text_rect)
        pygame.draw.rect(display_surface, 'White', text_rect.inflate(30, 30), width=5, border_radius=5)


class Loss:
    def __init__(self):
        self.font = pygame.font.Font('../graphics/subatomic.ttf', 50)

    def display(self):
        score_text = 'You Lose!'
        text_surface = self.font.render(score_text, True, 'White')
        text_rect = text_surface.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        display_surface.blit(text_surface, text_rect)


pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Meteor shooter')
clock = pygame.time.Clock()

# background
bg_surface = pygame.image.load('../graphics/background.png').convert()

# Sprite groups
spaceship_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# Sprite creation
ship = Ship(spaceship_group)

# Timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 400)

# Score
score = Score()

# music
bg_music = pygame.mixer.Sound('../sounds/music.wav')
bg_music.play(loops = -1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == meteor_timer:
            x_pos = randint(-100, (WINDOW_WIDTH + 100))
            y_pos = randint(-150, -50)
            Meteor(meteor_group, (x_pos, y_pos))


    # framerate limit
    delta_time = clock.tick(120) / 1000

    # background
    display_surface.blit(bg_surface, (0,0))

    # update
    spaceship_group.update()
    laser_group.update()
    meteor_group.update()

    # Score display
    score.display()

    # Graphics
    spaceship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    # Final frame
    pygame.display.update()