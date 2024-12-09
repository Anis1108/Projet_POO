# Classe représentant une compétence spéciale
class Skill:
    def __init__(self, name, power, range):
        self.name = name
        self.power = power
        self.range = range

    def use(self, user, target):
        """Applique l'effet de la compétence sur une cible."""
        if abs(user.x - target.x) <= self.range and abs(user.y - target.y) <= self.range:
            target.health -= self.power

class Pistolet(Skill):
    def __init__(self):
        super().__init__("Pistolet", 30, 3)

class Grenade(Skill):
    def __init__(self):
        super().__init__("Grenade", 50, 2)

class Sniper(Skill):
    def __init__(self):
        super().__init__("Sniper", 80, 5)

class Teleporte(Skill):
    def __init__(self):
        super().__init__("Téléporte", 0, float('inf'))  # Portée infinie, pas de dégâts
    
    def use(self, user, new_x, new_y):
        """
        Téléporte l'utilisateur à une nouvelle position spécifiée.
        """
        user.x = new_x
        user.y = new_y
        print(f"{user.name} s'est téléporté à la position ({new_x}, {new_y})")

