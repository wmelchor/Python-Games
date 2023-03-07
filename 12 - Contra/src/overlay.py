import pygame


class Overlay:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.health_surface = pygame.image.load('../graphics/health.png').convert_alpha()

    def display(self):
        for i in range(self.player.health):
            x = 10 + i * (self.health_surface.get_width() + 2)
            y = 10
            self.display_surface.blit(self.health_surface, (x, y))