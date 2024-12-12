import pygame
import random

CELL_SIZE = 50  # Taille d'une case
GRID_WIDTH = 16  # Largeur de la grille en nombre de cases
GRID_HEIGHT = 16  # Hauteur de la grille en nombre de cases


class Obstacle:
    def __init__(self, x, y, obstacle_type, image_path):
        self.x = x
        self.y = y
        self.obstacle_type = obstacle_type
        self.image = pygame.image.load(image_path)  # Chargement de l'image
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # Redimensionner l'image

    def draw(self, screen):
        """Dessiner l'obstacle à sa position."""
        screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
    @staticmethod
    def generate_obstacles_from_positions(num_obstacles, excluded_positions, image_path, manual_positions=None):
        """
        Génère une liste d'obstacles à partir de positions définies manuellement ou aléatoirement.

        Paramètres :
        ------------
        num_obstacles : int
            Nombre d'obstacles à générer (utilisé seulement si `manual_positions` est None).
        excluded_positions : set[tuple[int, int]]
            Positions à éviter (unités déjà placées, départ, etc.).
        image_path : str
            Chemin vers l'image utilisée pour les obstacles.
        manual_positions : list[tuple[int, int]], optionnel
            Liste des positions (x, y) où placer les obstacles. Si None, les positions sont générées aléatoirement.

        Retourne :
        ---------
        list[Obstacle]
            Une liste d'instances d'Obstacle.
        """
        obstacles = []

        if manual_positions:  # Si les positions sont fournies
            for x, y in manual_positions:
                if (x, y) not in excluded_positions:  # Vérifie que la position est libre
                    excluded_positions.add((x, y))
                    obstacles.append(Obstacle(x, y, "Obstacle", image_path))
        else:  # Génération aléatoire
            for _ in range(num_obstacles):
                while True:
                    x = random.randint(0, GRID_WIDTH - 1)
                    y = random.randint(0, GRID_HEIGHT - 1)
                    if (x, y) not in excluded_positions:  # Vérifie que la position est libre
                        excluded_positions.add((x, y))
                        obstacles.append(Obstacle(x, y, "Obstacle", image_path))
                        break

        return obstacles

    """
    @staticmethod
    def generate_random_obstacles(num_obstacles, excluded_positions, image_path):
        ""
        Génère une liste d'obstacles aléatoires.

        Paramètres :
        ------------
        num_obstacles : int
            Nombre d'obstacles à générer.
        excluded_positions : set de tuples (x, y)
            Positions à éviter (unités déjà placées, départ, etc.).
        image_path : str
            Chemin vers l'image utilisée pour les obstacles.

        Retourne :
        ---------
        list[Obstacle]
            Une liste d'instances d'Obstacle.
        "
        obstacles = []
        for _ in range(num_obstacles):
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if (x, y) not in excluded_positions:  # Vérifie si la position est libre
                    excluded_positions.add((x, y))
                    obstacles.append(Obstacle(x, y, "Obstacle", image_path))
                    break
        return obstacles
    """
    
    def can_place_obstacle(self, x, y):
        """
        Vérifie si un obstacle peut être placé à une position donnée.

        Paramètres
        ----------
        x : int
            Position x sur la grille.
        y : int
            Position y sur la grille.

        Retourne
        --------
        bool
            True si aucun obstacle ni unité n'est à cet emplacement, sinon False.
        """
        # Vérifie si une unité est déjà présente
        for unit in self.player_units + self.enemy_units:
            if unit.x == x and unit.y == y:
                return False

        # Vérifie si un obstacle est déjà présent
        for obstacle in self.obstacles:
            if obstacle.x == x and obstacle.y == y:
                return False

        return True

