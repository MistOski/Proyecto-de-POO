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

        #Bonus inicial por clase
        if self.city_class == "Conquistador":
            self.attack += 5

        #Territorio
        self.color = CITY_COLORS[name]
        self.original_color = CITY_COLORS[name]
        self.conquered = False
        self.owner = None
        self.owner_color = None

        #Cooldowns
        self.last_action_time = {
            "recolectar": 0,
            "atacar": 0,
            "comerciar": 0,
            "extorsionar": 0
        }

    #LIMITE DE DISTANCIA
    def distancia(self, ciudad_nombre):
        match ciudad_nombre:
            case "Ancud":
                return 0
            case "Dalcahue":
                return 1
            case "Castro":
                return 2
            case "Chonchi":
                return 3
            case "Quellón":
                return 4

    #CONTROL DEL COOLDOWN
    def can_act(self, action, cooldown):
        return time.time() - self.last_action_time[action] >= cooldown

    #RECOLECTAR
    def recolectar(self):
        base = 20
        if self.city_class == "Recolector":
            base = int(base * 1.2)

        self.resources += base
        self.last_action_time["recolectar"] = time.time()
        return f"{self.name} recolecto {base} recursos."

    #COMERCIO
    def comerciar(self):
        base = 15
        if self.city_class == "Comerciante":
            base = int(base * 1.2)

        self.coins += base
        self.last_action_time["comerciar"] = time.time()
        return f"{self.name} gano {base} monedas comerciando."

    #ATAQUE
    def atacar(self, target):
        self.last_action_time["atacar"] = time.time()

        # No atacar ciudades propias
        if target.conquered and target.owner == self:
            return f"{target.name} ya pertenece a {self.name}."

        # Distancia valida
        if abs(self.distancia(self.name) - self.distancia(target.name)) != 1:
            return "La ciudad esta fuera del alcance."

        # Comerciante puede evitar guerra (30%)
        if target.city_class == "Comerciante":
            if random.random() <= 0.30:
                return f"La ciudad Comerciante {target.name} evito la guerra."

        # Combate con variacion
        attack_power = self.attack + random.randint(-3, 3)
        defense_power = target.attack + random.randint(-3, 3)

        if attack_power > defense_power:
            # Marcar conquista
            target.conquered = True
            target.owner = self
            target.owner_color = self.color

            # Recompensas base
            monedas = 50
            recursos = 30
            ataque = 5

            # Bonificaciones por clase
            if self.city_class == "Comerciante":
                monedas = int(monedas * 1.2)

            if self.city_class == "Recolector":
                recursos = int(recursos * 1.2)

            # Aplicar recompensas
            self.coins += monedas
            self.resources += recursos
            self.attack += ataque

            return (
                f"{self.name} conquisto {target.name} "
                f"(+{monedas} monedas, +{recursos} recursos, +{ataque} ataque)"
            )

        return f"{self.name} fallo al atacar {target.name}."

   
    def extorsionar(self, target):
        if self.city_class != "Conquistador":
            return "Solo los Conquistadores pueden extorsionar."

       
        if target.conquered and target.owner == self:
            return f"{target.name} ya esta bajo tu control."

   
        if abs(self.distancia(self.name) - self.distancia(target.name)) != 1: #Sistema de extorsion, limites y todo respecto a distancia y ciudades propias
            return "La ciudad esta fuera del alcance."

        self.last_action_time["extorsionar"] = time.time()

        monto = random.randint(20, 40) #Monto de 20-40 monedas

        # Comerciantes pierden menos
        if target.city_class == "Comerciante":
            monto = int(monto * 0.8)

        target.coins = max(0, target.coins - monto)
        self.coins += monto

        return f"{self.name} extorsiono a {target.name} y obtuvo {monto} monedas."
