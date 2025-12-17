import pygame

class AttackMenu:
    def __init__(self, font):
        self.font = font
        self.visible = False
        self.buttons = []

    def open(self, screen, player_city, cities):
        self.visible = True
        self.buttons.clear()
        sw, _ = screen.get_size()
        x = sw // 2 - 150
        y = 140

        for city in cities:
            if city != player_city:
                rect = pygame.Rect(x, y, 300, 40)
                self.buttons.append((rect, city))
                y += 50

    def close(self):
        self.visible = False
        self.buttons.clear()

    def draw(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.font.render("Selecciona ciudad a atacar", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 80))

        for rect, city in self.buttons:
            pygame.draw.rect(screen, (80, 80, 80), rect)
            text = self.font.render(city.name, True, (255, 255, 255))
            screen.blit(text, (rect.x + 10, rect.y + 8))

    def handle_click(self, pos):
        for rect, city in self.buttons:
            if rect.collidepoint(pos):
                return city
        return None

