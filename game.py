import pygame
import time
import random
import pyautogui
import unicodedata
from settings import *
from city import City

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
                msg = city.recolectar()
                self.add_message(msg)
            elif action == "money":
                msg = city.comerciar()
                self.add_message(msg)

    def handle_attack_menu_click(self, pos):
        for rect, city in self.attack_menu_rects:
            if rect.collidepoint(pos):
                attacker = self.player_city
                result = attacker.atacar(city)
                self.add_message(result)
                self.close_attack_menu()
                return

    def handle_attack_menu_key(self, key):
        if key >= pygame.K_1 and key <= pygame.K_9:
            idx = key - pygame.K_1
            targets = [c for c in self.cities if c != self.player_city]
            if 0 <= idx < len(targets):
                attacker = self.player_city
                result = attacker.atacar(targets[idx])
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
            name_text = self.font.render(city.name, True, (255,255,255))
            cls_text = self.font.render(city.city_class, True, (200,200,0))
            self.screen.blit(name_text, (rect.x + 10, rect.y + 6))
            self.screen.blit(cls_text, (rect.x + rect.width - cls_text.get_width() - 10, rect.y + 6))

    def update_menu(self):
        w, h = self.screen.get_size()
        title = self.font.render("CONQUISTA DE CHILOE", True, (255,255,255))
        subtitle = self.font.render("Presiona ENTER para comenzar", True, (255,255,255))
        self.screen.blit(title, ((w - title.get_width())//2, h//3))
        self.screen.blit(subtitle, ((w - subtitle.get_width())//2, h//3 + 60))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.game_state = "select_city"

    def update_city_selection(self):
        self.draw_text("Elige tu ciudad:", 300, 50)
        for i, c in enumerate(self.cities):
            self.draw_text(f"{i+1}. {c.name} ({c.city_class})", 200, 100 + i*30)
        keys = pygame.key.get_pressed()
        for i in range(len(self.cities)):
            keyname = f"K_{i+1}"
            if hasattr(pygame, keyname) and keys[getattr(pygame, keyname)]:
                self.player_city = self.cities[i]
                self.game_state = "playing"
                self.map_visible = True
                self.add_message(f"Has elegido {self.player_city.name} ({self.player_city.city_class})")

    def draw_map(self):
        if not self.map_visible:
            return
        sw, sh = self.screen.get_size()
        map_width = 200
        map_height = 500
        start_x = (sw - map_width) // 2
        start_y = (sh - map_height) // 2
        desired = self.map_order
        ordered = []
        for name in desired:
            for c in self.cities:
                if _norm(c.name) == _norm(name):
                    ordered.append(c)
                    break
        if len(ordered) != len(desired):
            ordered = self.cities
        section_h = map_height // len(ordered)
        for i, city in enumerate(ordered):
            rect = pygame.Rect(start_x, start_y + i*section_h, map_width, section_h)
            color = city.owner_color if getattr(city, "conquered", False) and city.owner_color else getattr(city, "color", (150,150,150))
            pygame.draw.rect(self.screen, color, rect)
            name = city.name
            if getattr(city, "conquered", False):
                name = f"{name} (Conquistado)"
            text_surf = self.font.render(name, True, (0,0,0))
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

    def update_gameplay(self):
        c = self.player_city
        if not c:
            return
        self.draw_text(f"Ciudad: {c.name} ({c.city_class})", 50, 20)
        self.draw_text(f"Ataque: {c.attack}", 50, 60)
        self.draw_text(f"Recursos: {c.resources}", 50, 90)
        self.draw_text(f"Monedas: {c.coins}", 50, 120)
        self.draw_text(f"Opciones:", 50, 200)
        self.draw_text(f"1. Atacar - {self.cooldown_remaining('atacar', ACTION_COOLDOWN)}s", 50, 240)
        self.draw_text(f"2. Recolectar - {self.cooldown_remaining('recolectar', ACTION_COOLDOWN)}s", 50, 270)
        self.draw_text(f"3. Comerciar - {self.cooldown_remaining('comerciar', ACTION_COOLDOWN)}s", 50, 300)
        if time.time() - self.last_event_time >= EVENT_INTERVAL:
            self.trigger_global_event()
            self.last_event_time = time.time()

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
                        screenshot = pyautogui.screenshot()
                        screenshot.save("screenshot.png")
                        self.add_message("Screenshot guardada como screenshot.png")
                    elif self.game_state == "select_city":
                        pass
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
                elif event.type == pygame.MOUSEWHEEL:
                    if self.attack_menu_visible:
                        self.attack_menu_scroll += event.y * 20
                        max_scroll = 0
                        total_h = len([c for c in self.cities if c != self.player_city]) * (self.attack_menu_item_h + self.attack_menu_gap)
                        min_scroll = min(0, self.screen.get_height() - 240 - total_h)
                        self.attack_menu_scroll = max(min_scroll, min(max_scroll, self.attack_menu_scroll))
                        self.rebuild_attack_menu_rects()
                    else:
                        self.scroll_offset += event.y * 20
                        max_offset = 0
                        min_offset = -max(0, len(self.messages)*25 - self.notification_area_height)
                        self.scroll_offset = max(min_offset, min(max_offset, self.scroll_offset))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = event.pos
                        if self.attack_menu_visible:
                            self.handle_attack_menu_click(pos)
                        else:
                            if self.game_state == "menu":
                                pass
                            elif self.game_state == "select_city":
                                x, y = pos
                                for i in range(len(self.cities)):
                                    keyname = f"K_{i+1}"
                                sw, sh = self.screen.get_size()
                                sx = 200
                                sy = 100
                                for i, city in enumerate(self.cities):
                                    rect = pygame.Rect(sx, sy + i*30, 400, 28)
                                    if rect.collidepoint(pos):
                                        self.player_city = city
                                        self.game_state = "playing"
                                        self.map_visible = True
                                        self.add_message(f"Has elegido {self.player_city.name} ({self.player_city.city_class})")
                                        break
                            elif self.game_state == "playing":
                                pass
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    pass
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
