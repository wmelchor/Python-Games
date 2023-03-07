import pygame, sys
from settings import *

pygame.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Frogger')
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Keyboard input (Temp) Maybe could use for pausing
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                print(a)

    delta_time = clock.tick(60) / 1000

    pygame.display.update()