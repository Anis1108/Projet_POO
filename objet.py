from abc import ABC, abstractmethod
import pygame

CELL_SIZE = 50  # Taille d'une case

class Objet(ABC):  # Classe abstraite
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # Adapter à la taille des cellules

    @abstractmethod
    def use(self, unit):
        """Méthode abstraite qui doit être implémentée dans les classes dérivées"""
        pass

    def draw(self, screen):
        # Calculer la position dans la fenêtre
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        screen.blit(self.image, (screen_x, screen_y))

class Gift(Objet):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.collected = False

    def use(self, unit):
        """L'unité collecte le cadeau et obtient un pouvoir"""
        if not self.collected:
            self.collected = True
            unit.has_power = True  # Exemple d'effet de cadeau
            print("Cadeau collecté ! Pouvoir activé.")
        
    @staticmethod
    def generate_gifts_from_positions(image_path, positions):
        gifts = []
        for x, y in positions:
            gifts.append(Gift(x, y, image_path))
        return gifts
class Bombe(Objet):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.is_used = False

    def use(self, unit):
        """Effet de la bombe sur l'unité : réduction de la vie"""
        if not self.is_used:
            self.is_used = True
            unit.health -= 10  # Réduction de la vie de 10
            unit.health = max(unit.health, 0)  # S'assurer que la vie ne devienne pas négative
            print(f"Bombe utilisée! Vie réduite à {unit.health}.")
        
    @staticmethod
    def generate_bombes_from_positions(image_path, positions):
        bombes = []
        for x, y in positions:
            bombes.append(Bombe(x, y, image_path))
        return bombes

