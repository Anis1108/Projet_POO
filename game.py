import pygame
from skill import Pistolet, Grenade, Sniper, Soigner, Teleportation
from unit import Unit
from joueur import Joueur
from obstacle import Obstacle
from objet import Gift, Bombe 


# Taille de la grille et de chaque cellule du jeu
GRID_SIZE = 16  # Taille de la grille (16x16 cases).
CELL_SIZE = 50  # Taille d'une cellule (50x50 px).
INFO_PANEL_WIDTH = 200  # Largeur du panneau d'information.
WIDTH = GRID_SIZE * CELL_SIZE + INFO_PANEL_WIDTH  # Largeur de la fenêtre du jeu.
HEIGHT = GRID_SIZE * CELL_SIZE  # Hauteur de la fenêtre du jeu.
FPS = 30  # Limite d'images par seconde

# Définition des couleurs utilisées dans le jeu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
BUTTON_COLOR = (0, 128, 255)
HOVER_COLOR = (0, 255, 255)
TEXT_COLOR = (255, 255, 255)


# Classe principale du jeu
class Game:
    def __init__(self, screen, difficulty="facile"):
        self.screen = screen  # Fenêtre principale du jeu.
        self.difficulty = difficulty  # Difficulté du jeu.
        self.background = pygame.image.load(r"asset/backr.png")  # Image de fond.
        self.background = pygame.transform.scale(self.background, (GRID_SIZE * CELL_SIZE, HEIGHT))  # Mise à l'échelle de l'image de fond.

        # Initialisation des unités du joueur avec leurs caractéristiques
        self.player_units = [
            Unit(0, 0, 100, 3, 3, 'player', player_images[0], [Soigner()], move_range=6),
            Unit(1, 0, 100, 2, 1, 'player', player_images[1], [Pistolet(), Grenade(), Teleportation()], move_range=4),
            Unit(2, 0, 100, 2, 1, 'player', player_images[2], [Grenade()], move_range=3),
            Unit(3, 0, 100, 2, 1, 'player', player_images[3], [Sniper()], move_range=5),
        ]

        # Initialisation des unités ennemies avec leurs caractéristiques
        self.enemy_units = [
            Unit(6, 6, 100, 1, 1, 'enemy', enemy_images[0], [Pistolet(), Grenade(), Sniper()], move_range=4),
            Unit(7, 6, 100, 1, 1, 'enemy', enemy_images[1], [Pistolet(), Grenade()], move_range=5),
            Unit(6, 7, 100, 1, 1, 'enemy', enemy_images[2], [Grenade(), Teleportation()], move_range=4),
            Unit(7, 7, 100, 1, 1, 'enemy', enemy_images[3], [Sniper()], move_range=4),
        ]

        # Initialisation des joueurs
        self.player = Joueur("Player 1", self.player_units)  # Création du joueur 1 avec ses unités.
        self.enemy = Joueur("Player 2", self.enemy_units)  # Création du joueur 2 avec ses unités.

        self.player_turn = True  # Indicateur pour savoir si c'est le tour du joueur.
        self.winner = None  # Garde le nom du vainqueur à la fin du jeu.
        
        # Variables pour l'interface du jeu
        self.game_started = False  # Indicateur si le jeu a commencé ou non.
        self.obstacle_images = {
            'obstacle_type1': r"asset/bonome.png",  # Image du bonhomme de neige.
            'obstacle_type2': r"asset/mur.png",  # Image du mur.
            'obstacle_type3': r"asset/nuage.png"  # Image du nuage.
        }

        # Positions des cadeaux (objets à récupérer) dans le jeu
        gift_positions = [
            (8, 0), (14, 7), (0, 8), (3, 9), (14, 10), (4, 14), (11, 15),
        ]
        gift_image_path = r"C:asset\gift.png"
        self.gifts = Gift.generate_gifts_from_positions(gift_image_path, positions=gift_positions)  # Création des cadeaux dans le jeu.

        bombe_positions =[(7,2) ,(12,3) ,(1,10),(13,11),(4,13),(10,14),(5,5)]
        bombe_image_path=r"C:asset\bombe.png"
        self.bombes=Bombe.generate_bombes_from_positions(bombe_image_path, positions=bombe_positions)

        # Initialisation des obstacles dans le jeu
        self.obstacles = []
        self.initialize_obstacles()  # Initialisation des obstacles selon la difficulté.

    def initialize_obstacles(self):
        """Initialise les obstacles en fonction de la difficulté."""
        # Positions manuelles des obstacles selon leur type
        manual_positions = {
            'obstacle_type1': [  # Bonhommes de neige
                (0, 5), (2, 6), (13, 6), (15, 6), (3, 7), (6, 9), (8, 9),
                (0, 12), (1, 12), (3, 14), (5, 15), (7, 15), (9, 15), (13, 15),
            ],
            'obstacle_type2': [  # Murs
                (14, 0), (15, 0), (0, 6), (1, 6), (0, 7), (1, 7), (2, 7), (12, 7), (13, 7), (14, 17),
                (15, 7), (2, 8), (3, 8), (13, 8), (14, 8), (15, 8), (7, 8), (7, 9), (13, 9), (14, 9), (15, 9),
                (6, 10), (7, 10), (8, 10), (13, 10), (15, 10), (0, 13), (1, 13), (0, 14), (1, 14), (2, 14),
                (0, 15), (1, 15), (2, 15), (3, 15), (4, 15),
            ],
            'obstacle_type3': [  # Neige (zones plus difficiles à traverser)
                (0, 1), (4, 0), (7, 0), (9, 0), (13, 0), (3, 1), (6, 1), (11, 1), (12, 1),
                (8, 2), (10, 2), (2, 3), (6, 3), (3, 4), (13, 4), (15, 4), (7, 5), (10, 5),
                (5, 6), (9, 6), (0, 9), (4, 9), (11, 9), (10, 11), (5, 12), (11, 13),
            ]
        }

        # Ajustement des obstacles selon la difficulté
        if self.difficulty == "facile":
            # Retrait de certains obstacles pour rendre le jeu plus facile
            manual_positions['obstacle_type1'] = [
                pos for pos in manual_positions['obstacle_type1'] if pos not in [
                    (0, 12), (1, 12), (3, 14), (13, 15), (15, 6)
                ]
            ]
            manual_positions['obstacle_type2'] = [
                pos for pos in manual_positions['obstacle_type2'] if pos not in [
                   (15, 7), (2, 8), (3, 8), (13, 8), (14, 8), (15, 8), (7, 8), (7, 9), (13, 9), (14, 9), (15, 9),
                (6, 10), (7, 10), (8, 10), (13, 10), (15, 10), (0, 13), (1, 13), (0, 14), (1, 14), (2, 14),
                (0, 15), (1, 15), (2, 15), (3, 15), (4, 15),
                ]
            ]
            manual_positions['obstacle_type3'] = [
                pos for pos in manual_positions['obstacle_type3'] if pos not in [
                    (8, 2), (10, 2), (2, 3), (6, 3), (3, 4), (13, 4), (15, 4), (7, 5), (10, 5),
                    (5, 6), (9, 6), (0, 9), (4, 9), (11, 9), (10, 11), (5, 12), (11, 13),
                ]
            ]

        elif self.difficulty == "difficile":
            # Ajout de nouveaux obstacles pour rendre le jeu plus difficile
            manual_positions['obstacle_type1'].extend([
                (15, 11), (13, 11),
            ])

        # Ajouter les obstacles au jeu
        excluded_positions = {(unit.x, unit.y) for unit in self.player_units + self.enemy_units}
        for obstacle_type, positions in manual_positions.items():
            image_path = self.obstacle_images[obstacle_type]  # Récupère le chemin de l'image de l'obstacle.
            obstacles = Obstacle.generate_obstacles_from_positions(0, excluded_positions, image_path, positions)  # Crée les obstacles dans le jeu.
            self.obstacles.extend(obstacles)  # Ajoute les obstacles générés à la liste.

    
    def draw_main_menu(self):
        """Dessiner le menu principal avec les boutons."""
        # Charger et afficher l'image de fond
        background_image = pygame.image.load(r"C:\Users\AS\Desktop\Projet_POO\asset\interface.png")  # Mettez ici le chemin vers votre image
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Ajuster la taille de l'image à la fenêtre
        self.screen.blit(background_image, (0, 0))  # Afficher l'image de fond sur l'écran


        # Bouton 'Démarrer'
        start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, start_button_rect)
        start_text = pygame.font.Font(None, 36).render("Démarrer", True, TEXT_COLOR)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - 20))

        # Bouton 'Quitter'
        quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, quit_button_rect)
        quit_text = pygame.font.Font(None, 36).render("Quitter", True, TEXT_COLOR)
        self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()

    def handle_main_menu_events(self):
        """Gérer les événements du menu principal."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Vérifier si on clique sur le bouton 'Démarrer'
                start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
                if start_button_rect.collidepoint(x, y):
                    self.game_started = True
                    return True

                # Vérifier si on clique sur le bouton 'Quitter'
                quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
                if quit_button_rect.collidepoint(x, y):
                    pygame.quit()
                    exit()

        return False
 
    def draw_difficulty_menu(self):
        """Dessiner le menu de sélection de difficulté."""
        font = pygame.font.Font(None, 72)
        title_text = font.render("Sélectionner la difficulté", True, TEXT_COLOR)
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

        # Bouton "Facile"
        easy_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, easy_button_rect)
        easy_text = pygame.font.Font(None, 36).render("Facile", True, TEXT_COLOR)
        self.screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 20))

        # Bouton "Difficile"
        hard_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, hard_button_rect)
        hard_text = pygame.font.Font(None, 36).render("Difficile", True, TEXT_COLOR)
        self.screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()

    def handle_difficulty_menu_events(self):
        """Gérer les événements du menu de sélection de difficulté."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Vérifier si on clique sur le bouton "Facile"
                easy_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
                if easy_button_rect.collidepoint(x, y):
                    self.difficulty = "facile"
                    return True

                # Vérifier si on clique sur le bouton "Difficile"
                hard_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
                if hard_button_rect.collidepoint(x, y):
                    self.difficulty = "difficile"
                    return True

        return False



    # Gestion des tours
    def handle_player_turn(self):

        # Sélectionne les unités du joueur actuel et les unités adverses.
        active_units = self.player.units if self.player_turn else self.enemy.units
        opposing_units = self.enemy.units if self.player_turn else self.player.units
        
        # Parcourt les unités de l’équipe active et ignore celles qui sont déjà mortes (health <= 0).
        for unit in active_units:
            if unit.health <= 0:
                continue

            # Position initiale
            unit.initial_position = (unit.x, unit.y)
            # Marque l’unité comme sélectionnée pour l’afficher avec un contour.
            unit.is_selected = True
            self.flip_display()

            has_acted = False
            while not has_acted:



                # Liste des cibles disponibles (alliées pour soigner ou ennemies pour attaquer).
                if any(skill.name == "Soigner" for skill in unit.skills):
                    available_targets = [ally for ally in self.player.units if ally.health < 100 and ally != unit]
                else:
                    available_targets = [t for t in opposing_units if t.health > 0 and self.is_target_in_move_range(unit, t)]


                # Vérifie les événements Pygame, comme la fermeture de la fenêtre.
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    
                    # Deplacement
                    if event.type == pygame.KEYDOWN: # Détecte si une touche est pressée.
                        dx, dy = 0, 0
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1

                        new_x = unit.x + dx # Calcule la nouvelle position après le déplacement.
                        new_y = unit.y + dy
                        if self.is_in_move_range(unit, new_x, new_y): # Vérifie si la nouvelle position est dans la portée de déplacement de l’unité.
                            unit.move(dx, dy, self.obstacles) # Met à jour les coordonnées (x, y) de l’unité si le déplacement est valide.
                            self.flip_display() # Met à jour l’affichage pour refléter la nouvelle position.

                            # Vérifie si l'unité est sur une bombe et applique l'effet de la bombe
                            for bombe in self.bombes:
                                if bombe.x == unit.x and bombe.y == unit.y:
                                    unit.health = max(unit.health - 10, 0)  # Applique la réduction de 10 en santé, sans dépasser 0.
                                    self.bombes.remove(bombe)  # Retire la bombe du terrain
                                    
                                    break
                        if event.key == pygame.K_SPACE: # Appuie sur la barre d’espace pour passer à l'action.
                                                        # Vérifier si le joueur est sur un cadeau
                            for gift in self.gifts:
                                if gift.x == unit.x and gift.y == unit.y:
                                    # Activer le pouvoir pour traverser les nuages
                                    unit.has_power = True
                                    print("Pouvoir activé : l'unité peut désormais traverser les nuages !")
                                    self.gifts.remove(gift)  # Supprimer le cadeau après activation
                                    break
                            if not available_targets: # Si aucune cible n’est trouvée, le tour est marqué comme terminé pour cette unité.
                                print("Aucune cible disponible. Tour terminé pour cette unité.")
                                has_acted = True 

                            else:
                                skill = self.handle_skill_selection(unit) # Ouvre un menu pour choisir une compétence parmi celles de l'unité.

                                if skill: 

                                    if skill.name == "Grenade": 
                                        target_positions = self.handle_grenade_target_selection(unit,skill_range=skill.range) # Selectionne la cible
                                        if target_positions: # Si la cible est selectionnée
                                            skill.use(unit, target_positions, opposing_units)  # Applique les dégâts aux cibles situées sur les positions sélectionnées.
                                            self.remove_dead_units() # Elimine les unités avec health <= 0.
                                            if self.check_game_over(): # Vérifie si une équipe a perdu (fin du jeu).
                                                return
                                    elif skill.name == "Teleportation":
                                        print("Sélectionnez une case vide pour vous téléporter.")
                                        target_position = self.handle_target_position_selection(unit)
                                        if target_position:
                                            success = skill.use(unit, target_position)
                                            if success:
                                                has_acted = True

                                    elif skill.name == "Soigner":
                                        target = self.handle_target_selection(unit, is_heal=True, skill_range=skill.range) # Permet de sélectionner une cible valide à soigner.
                                        if target:
                                            print(f"{unit} soigne {target} à la position ({target.x}, {target.y})")
                                            unit.use_skill(skill.name, target) # Applique l'effet de soin sur la cible sélectionnée.
                                    else: # Le reste des competances 
                                        target = self.handle_target_selection(unit, skill_range=skill.range)
                                        if target:
                                            print(f"{unit} attaque {target} à la position ({target.x}, {target.y})")
                                            unit.use_skill(skill.name, target)
                                    
                                    self.remove_dead_units() # Elimine les unités mortes après l'attaque ou le soin.
                                    if self.check_game_over(): # Si une équipe perd toutes ses unités, le jeu s’arrête.
                                        return
                            has_acted = True # Marque l'unité comme ayant agi

            unit.is_selected = False # Retire la sélection visuelle de l’unité après avoir agi.
            self.flip_display()

        self.switch_turn() # Passe le tour à l’autre joueur.


    

    


    """ unit : L’unité en question, qui tente de se déplacer.
        new_x : Nouvelle position en x sur la grille.
        new_y : Nouvelle position en y sur la grille. """
    
    """ La fonction retourne un booléen (True ou False).
    Calcule la distance horizontale entre la nouvelle position new_x et la position de départ de l'unité unit.initial_position[0] (position initiale en x).
    Calcule la distance verticale entre la nouvelle position new_y et la position de départ unit.initial_position[1] (position initiale en y).
    Compare ces distances avec la portée de déplacement de l’unité (unit.move_range).
    Les deux distances (horizontale et verticale) doivent être inférieures ou égales à la portée de déplacement pour que la position soit valide."""

    def is_in_move_range(self, unit, new_x, new_y): 
        return abs(new_x - unit.initial_position[0]) <= unit.move_range and abs(new_y - unit.initial_position[1]) <= unit.move_range



    """unit : L’unité active dont on vérifie la portée.
       target : La cible (une autre unité) avec laquelle on compare la distance."""
    
    """Les deux distances (horizontale et verticale) doivent être inférieures ou égales à la portée pour que la cible soit valide."""

    def is_target_in_move_range(self, unit, target):
        return abs(unit.initial_position[0] - target.x) <= unit.move_range and abs(unit.initial_position[1] - target.y) <= unit.move_range
    


    """Permet à un joueur de sélectionner une compétence pour une unité active pendant son tour
    et gère l'affichage des compétences disponibles, la navigation dans le menu, et donne la possibilité de passer son tour."""

    def handle_skill_selection(self, unit): # unit : L'unité active dont on va sélectionner une compétence.
        
        skill_index = 0 # Initialise un index (skill_index) pour naviguer dans la liste des compétences disponibles.

        # Vérifier les cibles potentielles dans la zone de déplacement
        opposing_units = self.enemy.units if self.player_turn else self.player.units #  Liste des unités adverses.

        allies_in_range = [
            ally for ally in (self.player.units if self.player_turn else self.enemy.units)
            if ally.health < 100 and self.is_target_in_move_range(unit, ally)
        ] # Liste des alliés ayant moins de 100 HP et étant dans la portée de déplacement de l’unité active.

        enemies_in_range = [
            enemy for enemy in opposing_units
            if self.is_target_in_move_range(unit, enemy)
        ] # Liste des ennemis dans la portée de l'unité active.

        
        """ Si la compétence est "Soigner" et qu'il y a des alliés à soigner → Ajouter la compétence.
        Pour toutes les autres compétences, vérifier si des ennemis sont disponibles dans la portée → Ajouter la compétence."""

        # Vérifier si "Soigner" ou des compétences d'attaque sont disponibles
        skills_to_display = []
        for skill in unit.skills:
            if skill.name == "Soigner" and allies_in_range:
                skills_to_display.append(skill)  # Ajouter "Soigner" si des alliés blessés sont à portée
            elif skill.name != "Soigner" and enemies_in_range:
                skills_to_display.append(skill)  # Ajouter les compétences d'attaque si des ennemis sont à portée

        # Ajouter l'option "Passer" seulement si des compétences sont ajoutées
        # Cela garantit que "Passer" ne s'affiche pas seule
        if skills_to_display:  
            skills_to_display.append("Passer")

        # Vérifier si aucune compétence n'est disponible
        if not skills_to_display:
            print("Aucune compétence utilisable. Tour terminé pour cette unité.")
            return None


        # Interface pour sélectionner la compétence
        while True: # Cette boucle tourne indéfiniment jusqu'à ce qu'une action valide (comme valider une compétence) soit effectuée.
            self.flip_display() # Actualise l’affichage de la grille.
            font = pygame.font.SysFont('Arial', 24) # Utilise la police système Arial avec une taille de 24 pixels.


            """skill_index : Indice de la compétence actuellement sélectionnée.
               color :
               Vert (GREEN) : La compétence actuellement sélectionnée.
               Blanc (WHITE) : Les autres compétences non sélectionnées."""
            

            for i, skill in enumerate(skills_to_display):
                color = GREEN if i == skill_index else WHITE
                skill_name = skill if isinstance(skill, str) else skill.name  # "Passer" est une chaîne
                skill_text = font.render(skill_name, True, color) # font.render : Génère une image de texte à partir du nom de la compétence.

                """ self.screen.blit : Dessine l'image de texte (skill_text) sur l'écran.
                    Horizontalement (x) : Aligne le texte avec la position de l'unité active (unit.x * CELL_SIZE).
                    Verticalement (y) :
                                        unit.y * CELL_SIZE + 40 : Décale le texte sous la position de l'unité active.
                                        + i * 30 : Décale chaque compétence de 30 pixels vers le bas pour éviter le chevauchement."""
                self.screen.blit(skill_text, (unit.x * CELL_SIZE, unit.y * CELL_SIZE + 40 + i * 30)) 


            pygame.display.flip() # Met à jour l’écran pour afficher les modifications effectuées par blit

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()  # Arrête proprement le jeu avec pygame.quit() et quitte le programme avec exit().

                if event.type == pygame.KEYDOWN: # Événement déclenché lorsqu'une touche est pressée.
                    """ K_UP : Flèche haut → Décrémente l'index de sélection skill_index.
                        K_DOWN : Flèche bas → Incrémente l'index de sélection skill_index.
                        % len(skills_to_display) :
                         Assure que l'index reste dans les limites de la liste skills_to_display.
                         Si l’index dépasse la fin, il revient au début (et inversement)."""
                    if event.key == pygame.K_UP:
                        skill_index = (skill_index - 1) % len(skills_to_display)
                    elif event.key == pygame.K_DOWN:
                        skill_index = (skill_index + 1) % len(skills_to_display)
                    elif event.key == pygame.K_RETURN:
                        selected_skill = skills_to_display[skill_index]
                        if selected_skill == "Passer":
                            print("Le joueur a choisi de passer son tour.")
                            return None  # Retourner None pour indiquer que le tour est passé
                        return selected_skill # Si l'utilisateur sélectionne une compétence autre que "Passer", celle-ci est retournée.



    def is_valid_position(self, x, y):
        """
        Vérifie si la case à la position (x, y) est valide pour le curseur.
        Une case est considérée comme valide si :
            - Elle ne contient pas d'obstacle.
            - Elle ne contient pas de cadeau.

        Paramètres :
            - x (int) : Coordonnée horizontale de la case.
            - y (int) : Coordonnée verticale de la case.

        Retourne :
            - True si la case est valide (libre d'obstacle et de cadeau).
            - False sinon.
        """
        # Parcourt la liste des obstacles
        for obstacle in self.obstacles:  
            # Vérifie si un obstacle occupe la position (x, y)
            if obstacle.x == x and obstacle.y == y:
                return False  # Retourne False si un obstacle est trouvé

        # Parcourt la liste des cadeaux
        for gift in self.gifts:  
            # Vérifie si un cadeau occupe la position (x, y)
            if gift.x == x and gift.y == y:
                return False  # Retourne False si un cadeau est trouvé

        # Si aucune condition n'empêche le curseur, la case est valide
        return True  # Retourne True si la case est libre


    def handle_target_position_selection(self, unit):
        """
        Permet de sélectionner une case valide sur la carte (sans obstacles ni cadeaux).
        Le curseur peut se déplacer sur des cases avec des unités.

        Retourne :
            - (cursor_x, cursor_y) : Tuple représentant les coordonnées de la case sélectionnée.
        """
        cursor_x, cursor_y = unit.x, unit.y # Position initiale du curseur en haut à gauche de la grille

        while True:  # Boucle principale pour gérer le déplacement et la sélection
            # Actualise l'affichage de la grille et du jeu
            self.flip_display()

            # Dessine un rectangle vert pour représenter le curseur à la position actuelle
            pygame.draw.rect(self.screen, GREEN, 
                            (cursor_x * CELL_SIZE, cursor_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

            # Met à jour l'écran pour afficher les changements
            pygame.display.flip()

            # Gestion des événements Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Gestion de la fermeture de la fenêtre
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:  # Détection d'une touche enfoncée
                    new_x, new_y = cursor_x, cursor_y  # Position temporaire pour vérifier le déplacement

                    # Déplacement du curseur vers le haut
                    if event.key == pygame.K_UP and cursor_y > 0:
                        new_y -= 1
                    # Déplacement du curseur vers le bas
                    elif event.key == pygame.K_DOWN and cursor_y < GRID_SIZE - 1:
                        new_y += 1
                    # Déplacement du curseur vers la gauche
                    elif event.key == pygame.K_LEFT and cursor_x > 0:
                        new_x -= 1
                    # Déplacement du curseur vers la droite
                    elif event.key == pygame.K_RIGHT and cursor_x < GRID_SIZE - 1:
                        new_x += 1

                    # Vérifie si la nouvelle position est valide
                    if self.is_valid_position(new_x, new_y):
                        cursor_x, cursor_y = new_x, new_y  # Met à jour les coordonnées du curseur

                    # Validation de la position avec la touche Entrée
                    if event.key == pygame.K_RETURN:
                        if self.is_valid_position(cursor_x, cursor_y):
                            return cursor_x, cursor_y  # Retourne la position validée
                        else:
                            print("Case invalide. Choisissez une autre position.")




    

    def handle_target_selection(self, unit, is_heal=False, skill_range=0):
        """
        Gère la sélection d'une cible dans la zone de déplacement et la portée de la compétence.
        L'utilisateur peut sélectionner une unité ennemie pour attaquer ou une unité alliée pour soigner.

        Paramètres :
        - unit : L'unité active (celle qui utilise la compétence).
        - is_heal : Indique si la compétence est un soin (True) ou une attaque (False).
        - skill_range : La portée de la compétence utilisée.

        Retourne :
        - Une unité ciblée (alliée ou ennemie) ou None si aucune unité valide n'est sélectionnée.
        """
        # Position initiale du curseur : l'unité commence sur sa propre case
        cursor_x, cursor_y = unit.x, unit.y
        selected = False  # Variable pour savoir si une cible a été validée

        # Calculer les positions valides (zone de déplacement ET portée de la compétence)
        move_range = [
            (unit.initial_position[0] + dx, unit.initial_position[1] + dy)  # Calcul des positions autour de l'unité
            for dx in range(-unit.move_range, unit.move_range + 1)  # Zone de déplacement horizontale
            for dy in range(-unit.move_range, unit.move_range + 1)  # Zone de déplacement verticale
            if 0 <= unit.initial_position[0] + dx < GRID_SIZE  # S'assurer que la case reste dans les limites horizontales
            and 0 <= unit.initial_position[1] + dy < GRID_SIZE  # S'assurer que la case reste dans les limites verticales
            and abs(unit.x - (unit.initial_position[0] + dx)) <= skill_range  # La case doit être dans la portée de la compétence (horizontal)
            and abs(unit.y - (unit.initial_position[1] + dy)) <= skill_range  # La case doit être dans la portée de la compétence (vertical)
        ]

        # Boucle d'affichage pour permettre à l'utilisateur de déplacer le curseur et de choisir une cible
        while not selected:
            self.flip_display()  # Actualiser l'affichage pour montrer les nouvelles positions

            # Dessiner les cases valides dans la zone de déplacement et de portée
            for x, y in move_range:
                pygame.draw.rect(self.screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

            # Dessiner le curseur à la position actuelle
            pygame.draw.rect(self.screen, GREEN, (cursor_x * CELL_SIZE, cursor_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
            pygame.display.flip()  # Rafraîchir l'affichage pour montrer les changements

            # Gestion des événements utilisateur
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Si l'utilisateur ferme la fenêtre
                    pygame.quit()
                    exit()
                
                if event.type == pygame.KEYDOWN:  # Si une touche est pressée
                    # Déplacement du curseur vers le haut
                    if event.key == pygame.K_UP and (cursor_x, cursor_y - 1) in move_range:
                        cursor_y -= 1
                    # Déplacement du curseur vers le bas
                    elif event.key == pygame.K_DOWN and (cursor_x, cursor_y + 1) in move_range:
                        cursor_y += 1
                    # Déplacement du curseur vers la gauche
                    elif event.key == pygame.K_LEFT and (cursor_x - 1, cursor_y) in move_range:
                        cursor_x -= 1
                    # Déplacement du curseur vers la droite
                    elif event.key == pygame.K_RIGHT and (cursor_x + 1, cursor_y) in move_range:
                        cursor_x += 1
                    # Validation de la case avec la touche ENTER
                    elif event.key == pygame.K_RETURN:
                        # Cas pour les soins : vérifier les alliés à la position du curseur
                        if is_heal:
                            for ally in self.player.units if self.player_turn else self.enemy.units:
                                if ally.x == cursor_x and ally.y == cursor_y and ally.health < 100:
                                    return ally  # Retourner l'allié sélectionné
                        # Cas pour les attaques : vérifier les ennemis à la position du curseur
                        else:
                            for enemy in self.enemy.units if self.player_turn else self.player.units:
                                if enemy.x == cursor_x and enemy.y == cursor_y and enemy.health > 0:
                                    return enemy  # Retourner l'ennemi sélectionné
                        return None  # Si aucune unité valide n'est trouvée, retourner None


    def handle_grenade_target_selection(self, unit, skill_range=0):
        """
        Gère la sélection d'une cible pour la compétence Grenade.
        Le carré 2x2 reste dans la zone de déplacement ET dans la portée de la compétence.
        Retourne les positions valides des 4 cases formant ce carré.

        Paramètres :
        - unit : L'unité active qui utilise la compétence Grenade.
        - skill_range : La portée maximale à partir de laquelle l'unité peut lancer la grenade.

        Retourne :
        - Une liste contenant les coordonnées des 4 cases formant le carré 2x2 choisi par le joueur.
        """
        # 1. Calculer les limites possibles pour le coin supérieur gauche du carré 2x2
        # La grenade ne peut être lancée que dans la zone de déplacement ET la portée de la compétence.

        # Limite minimale en x :
        # On part de la position initiale de l'unité (unit.initial_position[0]) et on retire la portée de déplacement.
        # On vérifie également que l'unité ne dépasse pas la portée de la compétence (unit.x - skill_range).
        # Enfin, on empêche de sortir de la grille (valeur minimale = 0).
        min_x = max(unit.initial_position[0] - unit.move_range, unit.x - skill_range, 0)

        # Limite maximale en x :
        # On part de la position initiale et on ajoute la portée de déplacement.
        # On vérifie la portée de la compétence et que l'unité reste dans les limites de la grille.
        # On soustrait 2 à GRID_SIZE pour laisser de la place pour le carré 2x2.
        max_x = min(unit.initial_position[0] + unit.move_range, unit.x + skill_range, GRID_SIZE - 2)

        # Limite minimale en y (même logique que pour x)
        min_y = max(unit.initial_position[1] - unit.move_range, unit.y - skill_range, 0)

        # Limite maximale en y (même logique que pour x)
        max_y = min(unit.initial_position[1] + unit.move_range, unit.y + skill_range, GRID_SIZE - 2)

        # 2. Initialiser la position du curseur
        # Le curseur est initialisé à une position valide proche de l'unité
        cursor_x = min(max(min_x, unit.x), max_x - 1)  # Assurer que cursor_x est dans les limites calculées
        cursor_y = min(max(min_y, unit.y), max_y - 1)  # Assurer que cursor_y est dans les limites calculées

        # Boucle principale pour permettre au joueur de déplacer le curseur et de valider sa cible
        while True:
            self.flip_display()  # Rafraîchir l'affichage pour montrer les changements visuels

            # 3. Dessiner un contour rouge autour des 4 cases du carré 2x2
            # Le rectangle part de la position actuelle du curseur (cursor_x, cursor_y)
            # Sa largeur est de 2 cellules (CELL_SIZE * 2) et sa hauteur est de 2 cellules
            pygame.draw.rect(
                self.screen, (255, 0, 0),  # Couleur rouge pour le contour
                (cursor_x * CELL_SIZE, cursor_y * CELL_SIZE, CELL_SIZE * 2, CELL_SIZE * 2), 3  # Position et dimensions du rectangle
            )
            pygame.display.flip()  # Mettre à jour l'affichage pour montrer le rectangle

            # 4. Gérer les événements clavier pour déplacer le curseur
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Si l'utilisateur ferme la fenêtre, quitter proprement
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:  # Si une touche est pressée
                    # Déplacement vers le haut : vérifier que le curseur reste dans les limites calculées
                    if event.key == pygame.K_UP and cursor_y > min_y:
                        if cursor_y - 1 + 1 <= max_y:  # Vérifie que le coin inférieur droit reste dans les limites
                            cursor_y -= 1
                    # Déplacement vers le bas
                    elif event.key == pygame.K_DOWN and cursor_y < max_y:
                        if cursor_y + 1 + 1 <= max_y:  # Vérifie que le coin inférieur droit reste dans les limites
                            cursor_y += 1
                    # Déplacement vers la gauche
                    elif event.key == pygame.K_LEFT and cursor_x > min_x:
                        if cursor_x - 1 + 1 <= max_x:  # Vérifie que le coin inférieur droit reste dans les limites
                            cursor_x -= 1
                    # Déplacement vers la droite
                    elif event.key == pygame.K_RIGHT and cursor_x < max_x:
                        if cursor_x + 1 + 1 <= max_x:  # Vérifie que le coin inférieur droit reste dans les limites
                            cursor_x += 1

                    # Validation de la position avec la touche ENTER
                    elif event.key == pygame.K_RETURN:
                        # Retourner les positions des 4 cases formant le carré 2x2
                        # Chaque tuple (x, y) correspond à une case
                        return [
                            (cursor_x, cursor_y),         # Coin supérieur gauche
                            (cursor_x + 1, cursor_y),     # Coin supérieur droit
                            (cursor_x, cursor_y + 1),     # Coin inférieur gauche
                            (cursor_x + 1, cursor_y + 1)  # Coin inférieur droit
                        ]








    def remove_dead_units(self):
        """
        Supprime les unités mortes (avec une santé inférieure ou égale à 0) des listes d'unités du joueur et de l'ennemi.

        Cela permet de garder les listes d'unités à jour et d'éviter de traiter les unités qui ne sont plus en jeu.
        """
        # Mettre à jour la liste des unités du joueur en excluant celles qui ont une santé égale ou inférieure à 0
        self.player.units = [u for u in self.player.units if u.health > 0]
        
        # Mettre à jour la liste des unités de l'ennemi en excluant celles qui ont une santé égale ou inférieure à 0
        self.enemy.units = [u for u in self.enemy.units if u.health > 0]




    def check_game_over(self):
        """
        Vérifie si le jeu est terminé en regardant si l'une des deux équipes n'a plus d'unités en jeu.

        - Si le joueur n'a plus d'unités, l'ennemi (Player 2) est déclaré vainqueur.
        - Si l'ennemi n'a plus d'unités, le joueur (Player 1) est déclaré vainqueur.

        Retourne :
        - True si le jeu est terminé (une équipe a perdu toutes ses unités).
        - False sinon.
        """
        # Vérifier si la liste des unités du joueur est vide
        if len(self.player.units) == 0:
            self.winner = "Player 2"  # Déclarer Player 2 comme vainqueur
            self.show_winner_screen()  # Afficher l'écran de victoire pour Player 2
            return True  # Retourner True pour indiquer que le jeu est terminé

        # Vérifier si la liste des unités de l'ennemi est vide
        elif len(self.enemy.units) == 0:
            self.winner = "Player 1"  # Déclarer Player 1 comme vainqueur
            self.show_winner_screen()  # Afficher l'écran de victoire pour Player 1
            return True  # Retourner True pour indiquer que le jeu est terminé

        # Si aucune équipe n'a perdu toutes ses unités, le jeu continue
        return False


    def show_winner_screen(self):
        """
        Affiche l'écran de victoire pour le gagnant de la partie.

        - Remplit l'écran avec une couleur noire.
        - Affiche un message indiquant le gagnant ("Player 1 Wins!" ou "Player 2 Wins!").
        - Attend quelques secondes pour que le joueur puisse voir le message.
        - Ferme le jeu et quitte le programme.
        """
        # Remplir l'écran avec la couleur noire pour effacer l'ancien affichage
        self.screen.fill(BLACK)

        # Définir une police de caractères pour le texte du vainqueur
        font = pygame.font.SysFont('Arial', 48)  # Police Arial, taille 48

        # Créer un texte affichant le nom du vainqueur suivi de "Wins!"
        winner_text = font.render(f"{self.winner} Wins!", True, WHITE)  # Texte blanc

        # Calculer la position pour centrer le texte sur l'écran
        text_x = WIDTH // 2 - winner_text.get_width() // 2  # Centrage horizontal
        text_y = HEIGHT // 2 - winner_text.get_height() // 2  # Centrage vertical

        # Afficher le texte centré à l'écran
        self.screen.blit(winner_text, (text_x, text_y))

        # Mettre à jour l'affichage pour que le texte soit visible
        pygame.display.flip()

        # Attendre 5 secondes (5000 millisecondes) pour que le joueur voie le message
        pygame.time.wait(5000)

        # Quitter proprement Pygame et fermer le programme
        pygame.quit()
        exit()


    def switch_turn(self):
        """
        Change le tour actif entre le joueur et l'ennemi.

        - Si c'est actuellement le tour du joueur, le tour passe à l'ennemi.
        - Si c'est actuellement le tour de l'ennemi, le tour passe au joueur.

        Utilise l'opérateur logique `not` pour inverser la valeur booléenne de `self.player_turn`.
        """
        # Inverser l'état de player_turn
        # Si player_turn est True (tour du joueur), il devient False (tour de l'ennemi), et inversement
        self.player_turn = not self.player_turn


    def bar(self, unit):
        """
        Dessine une barre de santé au-dessus de la tête de chaque unité.
        - Bleu pour les unités du joueur 1.
        - Rouge pour les unités du joueur 2.
        - La taille de la barre dépend du niveau de santé.

        Paramètres :
        - unit : L'unité pour laquelle la barre de santé est affichée.
        """
        # Définir les couleurs des barres selon l'équipe
        bar_color = BLUE if unit.team == 'player' else RED  # Bleu pour joueur 1, Rouge pour joueur 2

        # Taille de la barre de santé
        max_bar_width = CELL_SIZE - 4  # Largeur maximale de la barre
        bar_height = 5  # Hauteur de la barre

        # Calcul de la largeur actuelle de la barre (en fonction de la santé)
        health_ratio = max(0, unit.health / 100)  # Ratio entre 0 et 1
        current_bar_width = int(max_bar_width * health_ratio)

        # Position de la barre : centrée horizontalement et placée au-dessus de la cellule
        bar_x = unit.x * CELL_SIZE + 2
        bar_y = unit.y * CELL_SIZE - 8  # Décalage vers le haut

        # Dessiner l'arrière-plan gris (barre vide)
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, max_bar_width, bar_height))

        # Dessiner la barre de santé actuelle (bleu ou rouge)
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, current_bar_width, bar_height))




    def flip_display(self):
        """
        Affiche la grille de jeu, les unités actives, les unités adverses dans la zone de déplacement
        et les panneaux d'informations. Rafraîchit l'écran pour refléter l'état actuel du jeu.
        
        Cette méthode est appelée pour réactualiser l'affichage à chaque événement important (mouvement, sélection).
        """
        # 1. Dessiner le fond noir pour nettoyer l'affichage
        # Affiche l'image de fond
        self.screen.blit(self.background, (0, 0)) 
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # 2. Déterminer les unités actives et les unités adverses
        # Si c'est le tour du joueur, active_units correspond à ses unités, sinon celles de l'ennemi.
        active_units = self.player.units if self.player_turn else self.enemy.units
        opposing_units = self.enemy.units if self.player_turn else self.player.units

        # 3. Afficher la zone de déplacement des unités actives
        for unit in active_units:  # Parcourir toutes les unités actives
            if unit.is_selected:  # Si une unité est sélectionnée
                # Définir la zone de déplacement en fonction de sa portée
                for dx in range(-unit.move_range, unit.move_range + 1):  # Parcourir les décalages horizontaux
                    for dy in range(-unit.move_range, unit.move_range + 1):  # Parcourir les décalages verticaux
                        zone_x = unit.initial_position[0] + dx  # Position X dans la zone de déplacement
                        zone_y = unit.initial_position[1] + dy  # Position Y dans la zone de déplacement

                        # Vérifier que la position calculée reste dans les limites de la grille
                        if 0 <= zone_x < GRID_SIZE and 0 <= zone_y < GRID_SIZE:
                            # Dessiner un rectangle CYAN autour des cases valides dans la portée de déplacement
                            pygame.draw.rect(
                                self.screen, BLUE,  # Couleur CYAN pour indiquer la zone de déplacement
                                (zone_x * CELL_SIZE, zone_y * CELL_SIZE, CELL_SIZE, CELL_SIZE),  # Position et dimensions
                                width=1  # Épaisseur du contour de 1 pixel
                            )

                            # 4. Dessiner les unités adverses situées dans la zone de déplacement
                            for target in opposing_units:  # Parcourir toutes les unités adverses
                                if target.x == zone_x and target.y == zone_y:  # Si la cible est dans la zone
                                    target.draw(self.screen)  # Dessiner l'unité adverse
                                    self.bar(target)  # Dessiner la barre de l'unité adverse

        # 5. Dessiner toutes les unités actives
        for unit in active_units:
            unit.draw(self.screen)  # Dessiner l'unité active à sa position actuelle
            self.bar(unit)  # Dessiner la barre de l'unité active

        # 6. Afficher le panneau d'informations (santé des unités)
        self.display_health_panel()
        
        # Dessiner tous les obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        # Dessiner les cadeaux
        for gift in self.gifts:
            gift.draw(self.screen)
        for bombe in self.bombes :
            bombe.draw(self.screen)

        # 7. Rafraîchir l'affichage pour prendre en compte tous les dessins précédents
        pygame.display.flip()





    def display_health_panel(self):
        """
        Affiche un panneau d'informations sur le côté droit de l'écran, montrant uniquement la santé des unités.
        - Utilise des barres de santé colorées pour une meilleure lisibilité.
        - Les unités du joueur sont affichées en bleu.
        - Les unités ennemies sont affichées en rouge.
        """
        # Dessiner un fond gris pour le panneau d'informations
        pygame.draw.rect(self.screen, (50, 50, 50), (GRID_SIZE * CELL_SIZE, 0, INFO_PANEL_WIDTH, HEIGHT))  

        # Créer une police pour afficher les informations du texte
        font = pygame.font.SysFont('Arial', 20, bold=True)  # Police Arial, taille 20, en gras

        # Décalage initial pour le texte
        decalage = 20

        # Afficher un titre pour les unités du joueur
        player_title = font.render("Player 1", True, BLUE)
        self.screen.blit(player_title, (GRID_SIZE * CELL_SIZE + 10, decalage))

        # Afficher les barres de santé pour chaque unité du joueur
        for unit in self.player.units:
            decalage += 30  # Espacement entre chaque unité
            self._draw_health_bar(unit.health, decalage, color=BLUE)

        # Ajouter un grand espace avant les unités ennemies
        decalage += 50

        # Afficher un titre pour les unités ennemies
        enemy_title = font.render("Player 2", True, RED)
        self.screen.blit(enemy_title, (GRID_SIZE * CELL_SIZE + 10, decalage))

        # Afficher les barres de santé pour chaque unité ennemie
        for unit in self.enemy.units:
            decalage += 30  # Espacement entre chaque unité
            self._draw_health_bar(unit.health, decalage, color=RED)

    def _draw_health_bar(self, health, y_position, color):
        """
        Dessine une barre de santé pour une unité à une position donnée.
        - health : La valeur de santé de l'unité (entre 0 et 100).
        - y_position : La position verticale où dessiner la barre.
        - color : Couleur principale de la barre.
        """
        bar_width = INFO_PANEL_WIDTH - 40  # Largeur de la barre de santé
        bar_height = 20  # Hauteur de la barre
        x_position = GRID_SIZE * CELL_SIZE + 10  # Position horizontale de départ

        # Calculer la largeur de la barre de santé en fonction de la santé restante
        health_ratio = max(0, min(health / 100, 1))  # Assurez-vous que la santé est entre 0 et 100
        current_bar_width = int(bar_width * health_ratio)

        # Dessiner l'arrière-plan de la barre (barre vide, en gris foncé)
        pygame.draw.rect(self.screen, (100, 100, 100), (x_position, y_position, bar_width, bar_height))

        # Dessiner la barre de santé actuelle (barre remplie)
        pygame.draw.rect(self.screen, color, (x_position, y_position, current_bar_width, bar_height))

        # Afficher la valeur de la santé au centre de la barre
        font = pygame.font.SysFont('Arial', 16)
        health_text = font.render(f"{health} HP", True, WHITE)
        text_x = x_position + (bar_width // 2 - health_text.get_width() // 2)
        text_y = y_position + (bar_height // 2 - health_text.get_height() // 2)
        self.screen.blit(health_text, (text_x, text_y))



    def handle_main_menu_events(self):
        """Gérer les événements du menu principal."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Vérifier si on clique sur le bouton 'Démarrer'
                start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
                if start_button_rect.collidepoint(x, y):
                    self.game_started = True
                    return True

                # Vérifier si on clique sur le bouton 'Quitter'
                quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
                if quit_button_rect.collidepoint(x, y):
                    pygame.quit()
                    exit()

        return False
    def main_menu(self):
        """Affiche le menu principal."""
        while not self.game_started:
            self.handle_main_menu_events()
            self.draw_main_menu()
        # Une fois le jeu démarré, sélectionner la difficulté
        self.difficulty = None
        while self.difficulty is None:
            self.handle_difficulty_menu_events()
            self.draw_difficulty_menu()

        # Réinitialiser les obstacles selon la difficulté choisie
        self.initialize_obstacles()

pygame.init()  # Initialisation de Pygame 
# Contrôle de la vitesse
clock = pygame.time.Clock()  # Initialisation de la clock
FPS = 30  # Limitation à 30 images par seconde

# Charger les images pour les unités du joueur et de l'ennemi
# Les images sont redimensionnées à la taille des cellules de la grille (CELL_SIZE x CELL_SIZE)
player_images = [
    pygame.transform.scale(pygame.image.load(f"pics/{i}.png"), (CELL_SIZE, CELL_SIZE))
    for i in range(1, 5)  # Charge les images pics/1.png, pics/2.png, pics/3.png, pics/4.png
]

enemy_images = [
    pygame.transform.scale(pygame.image.load(f"pics/{i}.png"), (CELL_SIZE, CELL_SIZE))
    for i in range(5, 9)  # Charge les images pics/5.png, pics/6.png, pics/7.png, pics/8.png
]

# Créer une fenêtre pour le jeu avec les dimensions WIDTH x HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Créer une instance de la classe Game, pas game
game_instance = Game(screen) 


# Définir le titre de la fenêtre
pygame.display.set_caption("Jeu de tour par tour 2D")

# Initialiser l'instance du jeu
# L'objet Game gère la logique et les mécaniques du jeu
game = Game(screen)
game.main_menu()  # Affiche le menu principal



# Boucle principale du jeu
while True:
    game.handle_player_turn()  # Appelle la gestion du tour actuel (joueur ou ennemi)
    clock.tick(FPS)  # Contrôle la vitesse de rafraîchissement du jeu en fonction de FPS (30 images/s par défaut)
