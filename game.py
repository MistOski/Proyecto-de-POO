import pygame
import time
import random
import pyautogui
import unicodedata
import os
from settings import *
from city import City

CITY_POLYGONS = {
    "Ancud": [
        [  # Poligono 1
            (0.18, 0.05), (0.78, 0.05),
            (0.85, 0.18), (0.60, 0.26),
            (0.25, 0.26)
        ],
        [  # Poligono 2 (extensión norte)
            (0.30, 0.00), (0.55, 0.00),
            (0.60, 0.05), (0.30, 0.05)
        ]
    ],

    "Dalcahue": [
        [
            (0.25, 0.26), (0.60, 0.26),
            (0.65, 0.38), (0.30, 0.38)
        ]
    ],

    "Castro": [
        [
            (0.30, 0.38), (0.65, 0.38),
            (0.62, 0.45), (0.30, 0.45)
        ],
        [
            (0.55, 0.40), (0.75, 0.42),
            (0.78, 0.48), (0.60, 0.48)
        ]
    ],

    "Chonchi": [
        [
            (0.28, 0.45), (0.62, 0.45),
            (0.60, 0.65), (0.28, 0.65)
        ]
    ],

    "Quellón": [
        [
            (0.22, 0.65), (0.70, 0.65),
            (0.82, 0.95), (0.15, 0.95)
        ],
        [
            (0.55, 0.70), (0.85, 0.78),
            (0.80, 0.95), (0.65, 0.90)
        ]
    ]
}

def _norm(s):
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode().lower()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Conquista de Chiloe")
        self.clock = pygame.time.Clock()

        self.cities = [City(name) for name in CITY_NAMES]
        self.player_city = None

        self.font = pygame.font.SysFont("Arial", 24)

        self.game_state = "menu"
        self.last_event_time = time.time()

        self.messages = []
        self.message_duration = 5
        self.scroll_offset = 0
        self.notification_area_height = 200

        self.attack_menu_visible = False
        self.attack_menu_rects = []
        self.attack_menu_scroll = 0
        self.attack_menu_width = 400
        self.attack_menu_item_h = 40
        self.attack_menu_gap = 8

        self.map_visible = False
        self.map_order = ["Ancud", "Dalcahue", "Castro", "Chonchi", "Quellon"]

        # ===== MAPA REAL =====
        base_path = os.path.dirname(__file__)
        map_path = os.path.join(base_path, "images", "mapa.png")
        self.map_image = pygame.image.load(map_path).convert_alpha()

    def point_in_polygon(self, point, polygon):
        x, y = point
        inside = False
        j = len(polygon) - 1

        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i

        return inside

    def add_message(self, text):
        self.messages.append((text, time.time()))
        if len(self.messages) > 200:
            self.messages.pop(0)

    def draw_messages(self):
        area_width = 400
        area_height = self.notification_area_height
        x = 10
        y_start = self.screen.get_height() - area_height - 10
        s = pygame.Surface((area_width, area_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (x, y_start))
        clip_rect = pygame.Rect(x, y_start, area_width, area_height)
        self.screen.set_clip(clip_rect)
        y = y_start + area_height - 25 + self.scroll_offset
        for text, _ in reversed(self.messages):
            rendered = self.font.render(text, True, (255, 255, 0))
            self.screen.blit(rendered, (x + 5, y))
            y -= 25
        self.screen.set_clip(None)

    def draw_text(self, text, x, y, color=(255,255,255)):
        t = self.font.render(text, True, color)
        self.screen.blit(t, (x, y))

    def cooldown_remaining(self, action, cooldown):
        if not self.player_city:
            return 0
        elapsed = time.time() - self.player_city.last_action_time[action]
        remaining = cooldown - elapsed
        return max(0, int(remaining))

    def open_attack_menu(self):
        if not self.player_city:
            return
        self.attack_menu_visible = True
        self.attack_menu_scroll = 0
        targets = [c for c in self.cities if c != self.player_city]
        w = self.attack_menu_width
        h_item = self.attack_menu_item_h
        gap = self.attack_menu_gap
        sw, sh = self.screen.get_size()
        x = (sw - w) // 2
        y = 120
        self.attack_menu_rects = []
        for i, city in enumerate(targets):
            rect = pygame.Rect(x, y + i*(h_item + gap) + self.attack_menu_scroll, w, h_item)
            self.attack_menu_rects.append((rect, city))
        self.add_message("Menu de ataque abierto")

    def rebuild_attack_menu_rects(self):
        targets = [c for c in self.cities if c != self.player_city]
        w = self.attack_menu_width
        h_item = self.attack_menu_item_h
        gap = self.attack_menu_gap
        sw, sh = self.screen.get_size()
        x = (sw - w) // 2
        y = 120
        self.attack_menu_rects = []
        for i, city in enumerate(targets):
            rect = pygame.Rect(x, y + i*(h_item + gap) + self.attack_menu_scroll, w, h_item)
            self.attack_menu_rects.append((rect, city))

    def close_attack_menu(self):
        self.attack_menu_visible = False
        self.attack_menu_rects = []
        self.attack_menu_scroll = 0
        self.add_message("Menu de ataque cerrado")

    def trigger_global_event(self):
        for city in self.cities:
            action = random.choice(["attack", "collect", "money"])
            if action == "attack":
                targets = [c for c in self.cities if c != city]
                if targets:
                    target = random.choice(targets)
                    result = city.atacar(target)
                    self.add_message(f"{city.name} atacó a {target.name}: {result}")
            elif action == "collect":
                self.add_message(city.recolectar())
            else:
                self.add_message(city.comerciar())

    def handle_attack_menu_click(self, pos):
        for rect, city in self.attack_menu_rects:
            if rect.collidepoint(pos):
                result = self.player_city.atacar(city)
                self.add_message(result)
                self.close_attack_menu()
                return

    def handle_attack_menu_key(self, key):
        if pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
            targets = [c for c in self.cities if c != self.player_city]
            if 0 <= idx < len(targets):
                result = self.player_city.atacar(targets[idx])
                self.add_message(result)
                self.close_attack_menu()

    def draw_attack_menu(self):
        if not self.attack_menu_visible:
            return
        sw, sh = self.screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        title = self.font.render("Selecciona ciudad a atacar", True, (255,255,255))
        self.screen.blit(title, ((sw - title.get_width())//2, 60))
        for rect, city in self.attack_menu_rects:
            pygame.draw.rect(self.screen, (80,80,80), rect)
            self.screen.blit(self.font.render(city.name, True, (255,255,255)), (rect.x + 10, rect.y + 6))

    def update_menu(self):
        w, h = self.screen.get_size()
        self.screen.blit(self.font.render("CONQUISTA DE CHILOE", True, (255,255,255)),
                         ((w - 300)//2, h//3))
        self.screen.blit(self.font.render("Presiona ENTER para comenzar", True, (255,255,255)),
                         ((w - 400)//2, h//3 + 60))
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.game_state = "select_city"

    def update_city_selection(self):
        self.draw_text("Elige tu ciudad:", 300, 50)
        for i, c in enumerate(self.cities):
            self.draw_text(f"{i+1}. {c.name} ({c.city_class})", 200, 100 + i*30)
        keys = pygame.key.get_pressed()
        for i in range(len(self.cities)):
            if keys[getattr(pygame, f"K_{i+1}")]:
                self.player_city = self.cities[i]
                self.game_state = "playing"
                self.map_visible = True
                self.add_message(f"Has elegido {self.player_city.name}")

    def draw_map(self):
        if not self.map_visible:
            return

        sw, sh = self.screen.get_size()

        # Tamaño original
        mw, mh = self.map_image.get_size()

        # Margen izquierdo para no chocar con el HUD
        left_margin = 420
        max_w = sw - left_margin - 20
        max_h = sh - 40

        # Escala proporcional máxima
        scale = min(max_w / mw, max_h / mh)

        map_scaled = pygame.transform.smoothscale(
            self.map_image,
            (int(mw * scale), int(mh * scale))
        )

        x = left_margin + (max_w - map_scaled.get_width()) // 2
        y = (sh - map_scaled.get_height()) // 2

        self.screen.blit(map_scaled, (x, y))

        self.draw_city_polygons((x, y, map_scaled.get_width(), map_scaled.get_height()))



    def update_gameplay(self):
        c = self.player_city
        if not c:
            return

        self.draw_text(f"Ciudad: {c.name} ({c.city_class})", 50, 20)
        self.draw_text(f"Ataque: {c.attack}", 50, 60)
        self.draw_text(f"Recursos: {c.resources}", 50, 90)
        self.draw_text(f"Monedas: {c.coins}", 50, 120)
        self.draw_text("Opciones:", 50, 200)
        self.draw_text(f"1. Atacar - {self.cooldown_remaining('atacar', ACTION_COOLDOWN)}s", 50, 240)
        self.draw_text(f"2. Recolectar - {self.cooldown_remaining('recolectar', ACTION_COOLDOWN)}s", 50, 270)
        self.draw_text(f"3. Comerciar - {self.cooldown_remaining('comerciar', ACTION_COOLDOWN)}s", 50, 300)

        if time.time() - self.last_event_time >= EVENT_INTERVAL:
            self.trigger_global_event()
            self.last_event_time = time.time()

    def draw_city_polygons(self, map_rect):
        mx, my, mw, mh = map_rect

        def project(px, py):
            return (mx + int(px * mw), my + int(py * mh))

        for city in self.cities:
            city_polys = CITY_POLYGONS.get(city.name)
            if not city_polys:
                continue

            color = city.owner_color if city.conquered and city.owner_color else city.color

            overlay = pygame.Surface((mw, mh), pygame.SRCALPHA)

            for poly_norm in city_polys:
                polygon = [project(x, y) for x, y in poly_norm]
                pygame.draw.polygon(
                    overlay,
                    (*color, 130),
                    [(x - mx, y - my) for x, y in polygon]
                )

            self.screen.blit(overlay, (mx, my))

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.screen.fill((0,0,50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.key == pygame.K_F12:
                        pyautogui.screenshot().save("screenshot.png")
                        self.add_message("Screenshot guardada como screenshot.png")
                    elif self.game_state == "playing":
                        if self.attack_menu_visible:
                            self.handle_attack_menu_key(event.key)
                        else:
                            if event.key == pygame.K_1 and self.player_city.can_act("atacar", ACTION_COOLDOWN):
                                self.open_attack_menu()
                            elif event.key == pygame.K_2 and self.player_city.can_act("recolectar", ACTION_COOLDOWN):
                                self.add_message(self.player_city.recolectar())
                            elif event.key == pygame.K_3 and self.player_city.can_act("comerciar", ACTION_COOLDOWN):
                                self.add_message(self.player_city.comerciar())

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.attack_menu_visible:
                        self.handle_attack_menu_click(event.pos)

            if self.game_state == "menu":
                self.update_menu()
            elif self.game_state == "select_city":
                self.update_city_selection()
            elif self.game_state == "playing":
                self.update_gameplay()

            self.draw_messages()
            if self.map_visible:
                self.draw_map()
            if self.attack_menu_visible:
                self.draw_attack_menu()

            pygame.display.flip()