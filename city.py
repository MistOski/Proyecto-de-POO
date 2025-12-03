import random
import time
from settings import CITY_CLASSES, CITY_COLORS

class City:
    def __init__(self, name):
        self.name = name
        self.city_class = random.choice(CITY_CLASSES)

        self.attack = 10
        self.resources = 0
        self.coins = 0

        # clase extra
        if self.city_class == "Conquistador":
            self.attack += 5

        # sistema de territorios
        self.color = CITY_COLORS[name]
        self.original_color = CITY_COLORS[name]
        self.conquered = False
        self.owner_color = None

        self.last_action_time = {
            "recolectar": 0,
            "atacar": 0,
            "comerciar": 0
        }

    def can_act(self, action, cooldown):
        return time.time() - self.last_action_time[action] >= cooldown

    def recolectar(self):
        base = 20
        if self.city_class == "Recolector":
            base = int(base * 1.2)
        self.resources += base
        self.last_action_time["recolectar"] = time.time()
        return f"{self.name} recolecto {base} recursos."

    def atacar(self, target):
        self.last_action_time["atacar"] = time.time()

        # evitar guerra del Comerciante
        if target.city_class == "Comerciante":
            if random.random() <= 0.30:
                return f"La ciudad Comerciante {target.name} evito la guerra."

        # conquista
        if self.attack > target.attack:
            gain = 20
            if self.city_class == "Comerciante":
                gain = int(gain * 1.2)

            self.coins += gain

            # actualizar territorio
            target.conquered = True
            target.owner_color = self.color

            return f"{self.name} conquisto {target.name} y gano {gain} monedas."

        else:
            return f"{self.name} fallo al atacar a {target.name}."

    def comerciar(self):
        base = 15
        if self.city_class == "Comerciante":
            base = int(base * 1.2)
        self.coins += base
        self.last_action_time["comerciar"] = time.time()
        return f"{self.name} gano {base} monedas comerciando."
