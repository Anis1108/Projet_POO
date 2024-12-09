import pygame

# Constantes
GRID_SIZE = 12
CELL_SIZE = 60
INFO_PANEL_WIDTH = 200
WIDTH = GRID_SIZE * CELL_SIZE + INFO_PANEL_WIDTH
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

# Classe représentant une unité
class Unit:
    def __init__(self, x, y, health, attack_power, team, image, skills=None):
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.team = team
        self.image = image
        self.is_selected = False
        self.skills = skills if skills else []
        self.initial_position = (x, y)

    def move(self, dx, dy):
        """Déplace l'unité."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def use_skill(self, skill_name, target=None):
        """Utilise une compétence."""
        for skill in self.skills:
            if skill.name == skill_name:
                skill.use(self, target)

    def draw(self, screen):
        """Dessine l'unité."""
        screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
