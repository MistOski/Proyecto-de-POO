import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from pygame import Rect

class AttackMenu:
    def __init__(self, player_city, city_list, font):
        self.font = font
        self.player_city = player_city

        self.cities = [c for c in city_list if c.name != player_city.name]

        self.visible = False
        self.buttons = []

        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        x = SCREEN_WIDTH // 2 - 150
        y = 150
        w = 300
        h = 45
        gap = 10

        for city in self.cities:
            rect = Rect(x, y, w, h)
            self.buttons.append((rect, city))
            y += h + gap

    def draw(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 30, 30))
        screen.blit(overlay, (0, 0))

        title = self.font.render("Selecciona una ciudad para atacar", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        for rect, city in self.buttons:
            pygame.draw.rect(screen, (70, 70, 70), rect)
            text = self.font.render(city.name, True, (255, 255, 255))
            screen.blit(text, (rect.x + 10, rect.y + 10))

    def handle_click(self, pos):
        if not self.visible:
            return None

        for rect, city in self.buttons:
            if rect.collidepoint(pos):
                return city

        return None

    def open(self):
        self.visible = True

    def close(self):
        self.visible = False
