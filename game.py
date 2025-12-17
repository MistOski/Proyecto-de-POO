import pygame
import time
import random
import pyautogui
import os

from mapa import CITY_POLYGONS
from settings import *
from city import City


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Conquista de Chiloé")
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

        #Menu de ataque / extorsion
        self.attack_menu_visible = False
        self.attack_menu_rects = []
        self.attack_menu_width = 400
        self.attack_menu_item_h = 40
        self.attack_menu_gap = 8
        self.extort_mode = False

        #Mapa
        self.map_visible = False
        base_path = os.path.dirname(__file__)
        map_path = os.path.join(base_path, "images", "mapa.png")
        self.map_image = pygame.image.load(map_path).convert_alpha()

    #NOTIFICACIONES
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

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        self.screen.blit(self.font.render(text, True, color), (x, y))

    #COOLDOWN
    def cooldown_remaining(self, action, cooldown):
        if not self.player_city:
            return 0
        last = self.player_city.last_action_time.get(action, 0)
        elapsed = time.time() - last
        return max(0, int(cooldown - elapsed))

    #MENU DE ATAQUE Y EXTORSION
    def open_attack_menu(self, extort=False):
        if not self.player_city:
            return

        self.attack_menu_visible = True
        self.extort_mode = extort
        self.attack_menu_rects = []

        targets = [
            c for c in self.cities
            if c != self.player_city
            and c.owner != self.player_city
        ]

        w = self.attack_menu_width
        h = self.attack_menu_item_h
        gap = self.attack_menu_gap
        sw, _ = self.screen.get_size()
        x = (sw - w) // 2
        y = 120

        for i, city in enumerate(targets):
            rect = pygame.Rect(x, y + i * (h + gap), w, h)
            self.attack_menu_rects.append((rect, city))

        modo = "extorsión" if extort else "ataque"
        self.add_message(f"Menú de {modo} abierto")

    def close_attack_menu(self):
        self.attack_menu_visible = False
        self.extort_mode = False
        self.attack_menu_rects = []

    def handle_attack_menu_click(self, pos):
        for rect, city in self.attack_menu_rects:
            if rect.collidepoint(pos):
                if self.extort_mode:
                    result = self.player_city.extorsionar(city)
                else:
                    result = self.player_city.atacar(city)

                self.add_message(result)
                self.close_attack_menu()
                return

    def draw_attack_menu(self):
        if not self.attack_menu_visible:
            return

        sw, sh = self.screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        titulo = "Selecciona ciudad a extorsionar" if self.extort_mode else "Selecciona ciudad a atacar"
        title = self.font.render(titulo, True, (255, 255, 255))
        self.screen.blit(title, ((sw - title.get_width()) // 2, 60))

        for rect, city in self.attack_menu_rects:
            pygame.draw.rect(self.screen, (80, 80, 80), rect)
            self.screen.blit(self.font.render(city.name, True, (255, 255, 255)),
                             (rect.x + 10, rect.y + 6))

    #EVENTOS DE IA
    def trigger_global_event(self):
        for city in self.cities:
            if city == self.player_city:
                continue

            if (
                city.city_class == "Conquistador"
                and city.can_act("extorsionar", EXTORT_COOLDOWN)
            ):
                if random.random() < 0.4:
                    targets = [
                        c for c in self.cities
                        if c != city and c.owner != city
                    ]
                    if targets:
                        self.add_message(city.extorsionar(random.choice(targets)))
            else:
                action = random.choice(["recolectar", "comerciar"])
                self.add_message(getattr(city, action)())

    #MENU PRINCIPAL
    def update_menu(self):
        w, h = self.screen.get_size()
        self.draw_text("CONQUISTA DE CHILOÉ", (w - 300) // 2, h // 3)
        self.draw_text("Presiona ENTER para comenzar", (w - 400) // 2, h // 3 + 60)

        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.game_state = "select_city"

    #SELECTOR DE CIUDAD INICIAL
    def update_city_selection(self):
        self.draw_text("Elige tu ciudad:", 300, 50)
        for i, c in enumerate(self.cities):
            self.draw_text(f"{i+1}. {c.name} ({c.city_class})", 200, 100 + i * 30)

        keys = pygame.key.get_pressed()
        for i in range(len(self.cities)):
            if keys[getattr(pygame, f"K_{i+1}")]:
                self.player_city = self.cities[i]
                self.map_visible = True
                self.game_state = "playing"
                self.add_message(f"Has elegido {self.player_city.name}")

    #GAMEPLAY
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

        if c.city_class == "Conquistador":
            self.draw_text(
                f"4. Extorsionar - {self.cooldown_remaining('extorsionar', EXTORT_COOLDOWN)}s",
                50, 330
            )

        if time.time() - self.last_event_time >= EVENT_INTERVAL:
            self.trigger_global_event()
            self.last_event_time = time.time()

    #MAPA
    def draw_map(self):
        if not self.map_visible:
            return

        sw, sh = self.screen.get_size()
        mx = 420
        my = 40
        mw = sw - mx - 40
        mh = sh - 80

        self.draw_city_polygons((mx, my, mw, mh))

    def draw_city_polygons(self, map_rect):
        mx, my, mw, mh = map_rect

        def project(px, py):
            return mx + int(px * mw), my + int(py * mh)

        for city in self.cities:
            polys = CITY_POLYGONS.get(city.name)
            if not polys:
                continue

            color = city.owner_color if city.conquered and city.owner_color else city.color
            overlay = pygame.Surface((mw, mh), pygame.SRCALPHA)

            for poly in polys:
                pts = [project(x, y) for x, y in poly]
                pygame.draw.polygon(
                    overlay,
                    (*color, 160),
                    [(x - mx, y - my) for x, y in pts]
                )

            self.screen.blit(overlay, (mx, my))

            # ---------------- NOMBRES ----------------
            # Centro aproximado del primer polígono
            poly0 = polys[0]
            cx = sum(p[0] for p in poly0) / len(poly0)
            cy = sum(p[1] for p in poly0) / len(poly0)
            px, py = project(cx, cy)

            label = city.name
            if city.conquered:
                label += " (CONQUISTADO)"

            text_surf = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(px, py))
            self.screen.blit(text_surf, text_rect)



    def run(self):
        while True:
            self.clock.tick(FPS)
            self.screen.fill((185, 160, 130))

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
                        if event.key == pygame.K_1 and self.player_city.can_act("atacar", ACTION_COOLDOWN):
                            self.open_attack_menu()
                        elif event.key == pygame.K_2 and self.player_city.can_act("recolectar", ACTION_COOLDOWN):
                            self.add_message(self.player_city.recolectar())
                        elif event.key == pygame.K_3 and self.player_city.can_act("comerciar", ACTION_COOLDOWN):
                            self.add_message(self.player_city.comerciar())
                        elif (
                            event.key == pygame.K_4
                            and self.player_city.city_class == "Conquistador"
                            and self.player_city.can_act("extorsionar", EXTORT_COOLDOWN)
                        ):
                            self.open_attack_menu(extort=True)

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
            self.draw_map()
            self.draw_attack_menu()
            pygame.display.flip()
