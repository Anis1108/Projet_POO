import pygame

# Constantes pour la configuration du jeu
GRID_SIZE = 12  # Taille de la grille du jeu (12x12 cases).
CELL_SIZE = 60  # Taille en pixels d'une case de la grille (60x60 pixels).

# Couleurs
GREEN = (0, 255, 0)  # Couleur verte utilisée pour le contour des unités sélectionnées

class Unit:
    """
    Représente une unité dans le jeu avec des propriétés comme la position, la santé,
    la puissance d'attaque, l'équipe à laquelle elle appartient, son image et ses compétences.

    - x : Position horizontale de l'unité dans la grille.
    - y : Position verticale de l'unité dans la grille.
    - health : Points de vie de l'unité.
    - attack_power : Puissance d'attaque de l'unité.
    - team : Équipe à laquelle appartient l'unité (joueur ou ennemi).
    - image : Image Pygame représentant visuellement l'unité.
    - skills : Liste des compétences utilisables par l'unité.
    - move_range : Portée de déplacement de l'unité en cases.
    """
    def __init__(self, x, y, health, attack_power, defense_power, team, image, skills=None, move_range=1):
        self.x = x  # Position X initiale dans la grille
        self.y = y  # Position Y initiale dans la grille
        self.health = health  # Points de vie de l'unité
        self.attack_power = attack_power
        self.defense_power = defense_power
        self.team = team  # Équipe : 'player' ou 'enemy'
        self.image = image  # Image de l'unité (chargée avec Pygame)
        self.is_selected = False  # Indique si l'unité est actuellement sélectionnée
        self.skills = skills if skills else []  # Liste des compétences, vide par défaut
        self.initial_position = (x, y)  # Position initiale avant tout mouvement
        self.move_range = move_range  # Portée maximale de déplacement (en nombre de cases)

    def move(self, dx, dy):
        """
        Déplace l'unité dans la grille si la position cible est valide.
        - dx : Variation horizontale (gauche ou droite).
        - dy : Variation verticale (haut ou bas).
        
        Condition : L'unité ne doit pas sortir des limites de la grille.
        """
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx  # Mettre à jour la position X
            self.y += dy  # Mettre à jour la position Y

    def use_skill(self, skill_name, target=None):
        """
        Utilise une compétence de l'unité sur une cible.
        - skill_name : Nom de la compétence à utiliser.
        - target : Cible sur laquelle appliquer la compétence (peut être None).
        
        Effet : Applique l'effet de la compétence si celle-ci existe.
        """
        for skill in self.skills:  # Parcourir les compétences disponibles
            if skill.name == skill_name:  # Rechercher la compétence par nom
                skill.use(self, target)  # Utiliser la compétence avec la méthode "use"

    def draw(self, screen):
        """
        Dessine l'unité à sa position actuelle dans la grille.
        - screen : Surface Pygame sur laquelle dessiner.
        
        Si l'unité est sélectionnée, un contour vert est ajouté autour de son image.
        """
        # Dessiner l'image de l'unité à la position actuelle (convertie en pixels)
        screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        
        # Dessiner un contour vert si l'unité est sélectionnée
        if self.is_selected:
            pygame.draw.rect(
                screen,  # Surface de dessin
                GREEN,  # Couleur du contour
                (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE),  # Rectangle autour de l'unité
                3  # Épaisseur du contour (3 pixels)
            )
