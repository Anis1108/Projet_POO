import pygame
from skill import Pistolet, Grenade, Sniper
from unit import Unit
from joueur import Joueur

# Constantes globales
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

# Charger les images
player_images = [pygame.image.load(f"pics/{i}.png") for i in range(1, 5)]
enemy_images = [pygame.image.load(f"pics/{i}.png") for i in range(5, 9)]
player_images = [pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE)) for img in player_images]
enemy_images = [pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE)) for img in enemy_images]


class Game:
    """Classe principale pour gérer le jeu."""

    def __init__(self, screen):
        

        self.screen = screen

        # Initialisation des unités
        self.player_units = [
            Unit(0, 0, 100, 2, 'player', player_images[0], [Pistolet(), Grenade(), Sniper()]),
            Unit(1, 0, 100, 2, 'player', player_images[1], [Pistolet(), Grenade()]),
            Unit(2, 0, 100, 2, 'player', player_images[2], [Grenade()]),
            Unit(3, 0, 100, 2, 'player', player_images[3], [Sniper()]),
        ]

        self.enemy_units = [
            Unit(6, 6, 100, 1, 'enemy', enemy_images[0], [Pistolet(), Grenade(), Sniper()]),
            Unit(7, 6, 100, 1, 'enemy', enemy_images[1], [Pistolet(), Grenade()]),
            Unit(6, 7, 100, 1, 'enemy', enemy_images[2], [Grenade()]),
            Unit(7, 7, 100, 1, 'enemy', enemy_images[3], [Sniper()]),
        ]

        # Joueurs
        self.player = Joueur("Player 1", self.player_units)
        self.enemy = Joueur("Player 2", self.enemy_units)

        # Tour actuel et vainqueur
        self.player_turn = True
        self.winner = None

    def handle_player_turn(self):
        """Gère le tour des unités du joueur actif."""
        active_units = self.player.units if self.player_turn else self.enemy.units
        opposing_units = self.enemy.units if self.player_turn else self.player.units

        for unit in active_units:
            if unit.health <= 0:
                continue

            unit.initial_position = (unit.x, unit.y)
            unit.is_selected = True
            self.flip_display()

            has_acted = False
            while not has_acted:
                available_targets = [t for t in opposing_units if t.health > 0 and self.is_target_in_move_range(unit, t)]

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1

                        new_x = unit.x + dx
                        new_y = unit.y + dy
                        if self.is_in_move_range(unit, new_x, new_y):
                            unit.move(dx, dy)
                            self.flip_display()

                        if event.key == pygame.K_SPACE:
                            if not available_targets:
                                print("Aucune cible à attaquer. Tour terminé pour cette unité.")
                                has_acted = True
                            else:
                                skill = self.handle_skill_selection(unit)
                                if skill:
                                    target = self.handle_target_selection(unit, available_targets)
                                    if target:
                                        unit.use_skill(skill.name, target)
                                        self.remove_dead_units()
                                        if self.check_game_over():
                                            return
                            has_acted = True

            unit.is_selected = False
            self.flip_display()

        self.switch_turn()

    def is_in_move_range(self, unit, new_x, new_y):
        return abs(new_x - unit.initial_position[0]) <= 1 and abs(new_y - unit.initial_position[1]) <= 1

    def is_target_in_move_range(self, unit, target):
        return abs(unit.initial_position[0] - target.x) <= 1 and abs(unit.initial_position[1] - target.y) <= 1

    def handle_skill_selection(self, unit):
        skill_index = 0
        while True:
            self.flip_display()
            font = pygame.font.SysFont('Arial', 24)
            for i, skill in enumerate(unit.skills):
                color = GREEN if i == skill_index else WHITE
                skill_text = font.render(f"{skill.name}", True, color)
                self.screen.blit(skill_text, (unit.x * CELL_SIZE, unit.y * CELL_SIZE + 40 + i * 30))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        skill_index = (skill_index - 1) % len(unit.skills)
                    elif event.key == pygame.K_DOWN:
                        skill_index = (skill_index + 1) % len(unit.skills)
                    elif event.key == pygame.K_RETURN:
                        return unit.skills[skill_index]

    def handle_target_selection(self, unit, targets):
        target_index = 0
        while True:
            self.flip_display()
            for i, target in enumerate(targets):
                if i == target_index:
                    pygame.draw.rect(self.screen, GREEN, (target.x * CELL_SIZE, target.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        target_index = (target_index - 1) % len(targets)
                    elif event.key == pygame.K_RIGHT:
                        target_index = (target_index + 1) % len(targets)
                    elif event.key == pygame.K_RETURN:
                        return targets[target_index]

    def remove_dead_units(self):
        self.player.units = [u for u in self.player.units if u.health > 0]
        self.enemy.units = [u for u in self.enemy.units if u.health > 0]

    def check_game_over(self):
        if len(self.player.units) == 0:
            self.winner = "Player 2"
            self.show_winner_screen()
            return True
        elif len(self.enemy.units) == 0:
            self.winner = "Player 1"
            self.show_winner_screen()
            return True
        return False

    def show_winner_screen(self):
        self.screen.fill(BLACK)
        font = pygame.font.SysFont('Arial', 48)
        winner_text = font.render(f"{self.winner} Wins!", True, WHITE)
        self.screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(5000)
        pygame.quit()
        exit()

    def switch_turn(self):
        self.player_turn = not self.player_turn
    def draw_health_bar(self, unit):
        """Dessine une barre de couleur au-dessus des unités."""
        bar_color = BLUE if unit.team == 'player' else RED  # Couleur de la barre
        bar_width = CELL_SIZE - 4  # Largeur légèrement plus petite que la cellule
        bar_height = 5  # Hauteur de la barre
        bar_x = unit.x * CELL_SIZE + 2  # Position X centrée
        bar_y = unit.y * CELL_SIZE - 8  # Position Y au-dessus de l'unité
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, bar_width, bar_height))


    def flip_display(self):
        """Affiche la grille, les unités actives et les unités adverses dans la zone de déplacement."""
        # Dessiner le background
        self.screen.fill(BLACK)

        # Dessiner la grille
        

        # Afficher la zone de déplacement et les unités adverses dans cette zone
        active_units = self.player.units if self.player_turn else self.enemy.units
        opposing_units = self.enemy.units if self.player_turn else self.player.units

        for unit in active_units:  # Unité active du joueur en cours
            if unit.is_selected:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        zone_x = unit.initial_position[0] + dx
                        zone_y = unit.initial_position[1] + dy
                        if 0 <= zone_x < GRID_SIZE and 0 <= zone_y < GRID_SIZE:
                            # Dessiner la zone de déplacement en cyan
                            pygame.draw.rect(self.screen, CYAN,
                                            (zone_x * CELL_SIZE, zone_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                            
                            # Vérifier et dessiner les unités adverses dans cette zone
                            for target in opposing_units:
                                if target.x == zone_x and target.y == zone_y:
                                    target.draw(self.screen)
                                    self.draw_health_bar(target)

        # Dessiner les unités actives
        for unit in active_units:
            unit.draw(self.screen)
            self.draw_health_bar(unit)

        # Afficher le panneau de santé
        self.display_health_panel()

        # Rafraîchir l'affichage
        pygame.display.flip()







    def display_health_panel(self):
        pygame.draw.rect(self.screen, WHITE, (GRID_SIZE * CELL_SIZE, 0, INFO_PANEL_WIDTH, HEIGHT), 1)
        font = pygame.font.SysFont('Arial', 18)
        y_offset = 10

        self.screen.blit(font.render("Player Units:", True, BLUE), (GRID_SIZE * CELL_SIZE + 10, y_offset))
        for unit in self.player.units:
            y_offset += 20
            self.screen.blit(font.render(f"({unit.x}, {unit.y}): {unit.health} HP", True, WHITE),
                             (GRID_SIZE * CELL_SIZE + 10, y_offset))

        y_offset += 30
        self.screen.blit(font.render("Enemy Units:", True, RED), (GRID_SIZE * CELL_SIZE + 10, y_offset))
        for unit in self.enemy.units:
            y_offset += 20
            self.screen.blit(font.render(f"({unit.x}, {unit.y}): {unit.health} HP", True, WHITE),
                             (GRID_SIZE * CELL_SIZE + 10, y_offset))


# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-based Game")
game = Game(screen)

# Boucle principale
clock = pygame.time.Clock()
while True:
    game.handle_player_turn()
    clock.tick(FPS)
