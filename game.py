import pygame
import time
import random
import pyautogui
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

    
    def add_message(self, text):
        self.messages.append((text, time.time())) #Mensajes 
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

    def draw_text(self, text, x, y):
        t = self.font.render(text, True, (255,255,255))
        self.screen.blit(t, (x, y))

    def cooldown_remaining(self, action, cooldown):
        elapsed = time.time() - self.player_city.last_action_time[action]
        remaining = cooldown - elapsed
        return max(0, int(remaining))

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
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_offset += event.y * 20
                    max_offset = 0
                    min_offset = -max(0, len(self.messages)*25 - self.notification_area_height)
                    self.scroll_offset = max(min_offset, min(max_offset, self.scroll_offset))

            if self.game_state == "menu":
                self.update_menu()
            elif self.game_state == "select_city":
                self.update_city_selection()
            elif self.game_state == "playing":
                self.update_gameplay()

            self.draw_messages()
            pygame.display.flip()

    def update_menu(self):
  
        w, h = self.screen.get_size()
        title = self.font.render("CONQUISTA DE CHILOÉ", True, (255,255,255))
        subtitle = self.font.render("Presiona ENTER para comenzar", True, (255,255,255)) #Menu de inicio
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
            if keys[getattr(pygame, f"K_{i+1}")]:    #Selector de ciudad inicial
                self.player_city = self.cities[i]
                self.game_state = "playing"
                self.add_message(f"Has elegido {self.player_city.name} ({self.player_city.city_class})")
                time.sleep(0.2)

 
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
                city.recolectar()             
                self.add_message(f"{city.name} recolectó recursos.")        #Eventos realizados por las otras ciudades
            elif action == "money":
                city.comerciar()
                self.add_message(f"{city.name} comerció y obtuvo monedas.")

    
    def update_gameplay(self):
        c = self.player_city

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

        keys = pygame.key.get_pressed()

        if keys[pygame.K_1] and c.can_act("atacar", ACTION_COOLDOWN):
            target = random.choice([x for x in self.cities if x != c])            #Acciones del jugador
            result = c.atacar(target)
            self.add_message(result)
            time.sleep(0.2)

        if keys[pygame.K_2] and c.can_act("recolectar", ACTION_COOLDOWN):
            self.add_message(c.recolectar())
            time.sleep(0.2)

        if keys[pygame.K_3] and c.can_act("comerciar", ACTION_COOLDOWN):
            self.add_message(c.comerciar())
            time.sleep(0.2)