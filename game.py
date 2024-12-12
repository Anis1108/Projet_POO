import pygame
from skill import Pistolet, Grenade, Sniper, Soigner
from unit import Unit
from joueur import Joueur
from obstacle import Obstacle
from gift import Gift


GRID_SIZE = 16 #Taille de la grille du jeu (16x16 cases).
CELL_SIZE = 50 #Taille en pixels d'une case de la grille (50x50 px).
INFO_PANEL_WIDTH = 200 #Largeur du panneau d'information à droite.
WIDTH = GRID_SIZE * CELL_SIZE + INFO_PANEL_WIDTH #Dimensions totales de la fenêtre du jeu.
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30 #Limite d'images par seconde

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)




"""Classe Game"""
class Game:
    

    def __init__(self, screen):
        

        self.screen = screen #Fenêtre principale où le jeu est dessiné.
        self.background = pygame.image.load(r"C:\Users\AS\Desktop\LydiaKEBLIPhython\asset\backr.png")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        # Chaque unité est créée avec sa position initiale (x, y), sa santé, son équipe, une image, ses compétences, et sa distance de déplacement (move_range).
        self.player_units = [
            Unit(0, 0, 100, 3,3, 'player', player_images[0], [Pistolet(), Grenade(), Sniper()]),
            Unit(1, 0, 100, 2,1, 'player', player_images[1], [Pistolet(), Grenade()]),
            Unit(2, 0, 100, 2,1, 'player', player_images[2], [Grenade()]),
            Unit(3, 0, 100, 2,1, 'player', player_images[3], [Sniper()]),
        ]

        self.enemy_units = [
            Unit(6, 6, 100, 1,1, 'enemy', enemy_images[0], [Pistolet(), Grenade(), Sniper()]),
            Unit(7, 6, 100, 1,1, 'enemy', enemy_images[1], [Pistolet(), Grenade()]),
            Unit(6, 7, 100, 1,1, 'enemy', enemy_images[2], [Grenade()]),
            Unit(7, 7, 100, 1,1, 'enemy', enemy_images[3], [Sniper()]),
        ]


        # Chaque joueur possède un nom et une liste d’unités.
        self.player = Joueur("Player 1", self.player_units)
        self.enemy = Joueur("Player 2", self.enemy_units)

        
        self.player_turn = True # Définit si c'est le tour du joueur.
        self.winner = None #Garde le nom du vainqueur lorsqu'une partie se termine.

        # Positions des obstacles dans un dictionnaire

        manual_positions = {
            'obstacle_type1': [  # Bonhommes de neige
                (0,5),(2,6),(13,6),(15,6),(3,7),(6,9),(8,9),
                (0 ,12),(1,12),(3,14),(5,15),(7,15) ,(9,15),(13,15),
            ],
            'obstacle_type2': [  # Murs
                (14,0),(15,0),(0,6),(1,6),(0,7),(1,7),(2,7),(12,7),(13,7),(14 ,17),
                (15,7),(2,8),(3,8),(13,8),(14,8),(15,8),(7,8),(7,9),(13,9),(14,9),(15,9),
                (6,10),(7,10),(8,10),(13,10),(15,10) ,(0,13),(1,13),(0 ,14),(1,14),(2,14),
                (0,15), (1,15), (2,15), (3,15), (4,15), 

            ],
            'obstacle_type3': [  # Neige (zones plus difficiles à traverser)
                (0, 1),(4,0),(7,0),(9,0),(13,0),(3,1) ,(6,1),(11,1),(12,1) ,
                (8,2),(10,2), (2,3),(6,3),(3,4),(13,4),(15,4),(7,5),(10,5),
                (5,6),(9,6),(0,9),(4,9),(11 ,9),(10,11),(5,12),(11,13),
            ]
        }




        excluded_positions = {(unit.x, unit.y) for unit in self.player_units + self.enemy_units}
        
        # Générer dynamiquement les obstacles
        self.obstacles = []
        self.obstacle_images = {
            'obstacle_type1': r"C:\Users\AS\Desktop\LydiaKEBLIPhython\asset\bonome.png",
            'obstacle_type2': r"C:\Users\AS\Desktop\LydiaKEBLIPhython\asset\mur.png",
            'obstacle_type3': r"C:\Users\AS\Desktop\LydiaKEBLIPhython\asset\nuage.png"
        }

        for obstacle_type, positions in manual_positions.items():
            image_path = self.obstacle_images[obstacle_type]
            obstacles = Obstacle.generate_obstacles_from_positions(10, excluded_positions, image_path, positions)
            self.obstacles.extend(obstacles)
        
        # Positions des cadeaux
        gift_positions = [
            (8,0),(14,7),(0,8),(3,9),(14,10),(4,14),(11,15), # Ajoutez autant de cadeaux que vous voulez
        ]

        gift_image_path = r"C:\Users\AS\Desktop\LydiaKEBLIPhython\asset\gift.png"  # Image du cadeau

        self.gifts = Gift.generate_gifts_from_positions(
            gift_image_path,
            positions=gift_positions
        )

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

                        if event.key == pygame.K_SPACE: # Appuie sur la barre d’espace pour passer à l'action.
                                                        # Vérifier si le joueur est sur un cadeau
                            for gift in self.gifts:
                                if gift.x == unit.x and gift.y == unit.y:
                                    # Réduire la santé de l'unité et retirer le cadeau
                                    unit.health += 1
                                    self.gifts.remove(gift)
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
                pygame.draw.rect(self.screen, CYAN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

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
        Dessine une barre colorée au-dessus des unités pour reconnaitre les unités.

        - La barre est dessinée juste au-dessus de la position de l'unité.

        Paramètres :
        - unit : L'unité dont la barre de vie doit être affichée.
        """
        # Déterminer la couleur de la barre en fonction de l'équipe de l'unité
        # BLEU pour les unités du joueur, ROUGE pour les unités ennemies
        bar_color = BLUE if unit.team == 'player' else RED

        # Définir les dimensions de la barre de vie
        bar_width = CELL_SIZE - 4  # Largeur légèrement inférieure à celle de la cellule
        bar_height = 5  # Hauteur fixe de la barre (5 pixels)

        # Calculer la position X pour centrer la barre horizontalement par rapport à la cellule
        bar_x = unit.x * CELL_SIZE + 2  # Position X centrée avec un petit décalage

        # Calculer la position Y pour placer la barre juste au-dessus de l'unité
        bar_y = unit.y * CELL_SIZE - 8  # Position Y : au-dessus de la cellule

        # Dessiner un rectangle plein pour représenter la barre de vie
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, bar_width, bar_height))



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
                                self.screen, CYAN,  # Couleur CYAN pour indiquer la zone de déplacement
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

        # 7. Rafraîchir l'affichage pour prendre en compte tous les dessins précédents
        pygame.display.flip()





    def display_health_panel(self):
        """
        Affiche un panneau d'informations sur le côté droit de l'écran, montrant la santé des unités.
        - Les unités du joueur sont affichées en bleu.
        - Les unités ennemies sont affichées en rouge.
        
        
        """
        # Dessiner un rectangle blanc pour le panneau d'informations
        # Le panneau couvre toute la hauteur de l'écran à droite de la grille
        pygame.draw.rect(self.screen, WHITE, (GRID_SIZE * CELL_SIZE, 0, INFO_PANEL_WIDTH, HEIGHT), 1)

        # Créer une police pour afficher les informations du texte
        font = pygame.font.SysFont('Arial', 18)  # Police Arial, taille 18 pixels

        # Initialiser un décalage vertical pour placer les lignes de texte successives
        decalage = 10  # Premier texte à 10 pixels du haut

        # Afficher le titre pour les unités du joueur
        self.screen.blit(font.render("Player Units:", True, BLUE), (GRID_SIZE * CELL_SIZE + 10, decalage))

        # Afficher les informations de santé pour chaque unité du joueur
        for unit in self.player.units:
            decalage += 20  # Ajouter un espace vertical de 20 pixels
            # Afficher la position (x, y) et les points de vie de l'unité
            self.screen.blit(font.render(f"({unit.x}, {unit.y}): {unit.health} HP", True, WHITE),
                            (GRID_SIZE * CELL_SIZE + 10, decalage))

        # Ajouter un espace vertical avant d'afficher les unités ennemies
        decalage += 30  # Grand espace pour séparer les deux sections

        # Afficher le titre pour les unités ennemies
        self.screen.blit(font.render("Enemy Units:", True, RED), (GRID_SIZE * CELL_SIZE + 10, decalage))

        # Afficher les informations de santé pour chaque unité ennemie
        for unit in self.enemy.units:
            decalage += 20  # Ajouter un espace vertical de 20 pixels
            # Afficher la position (x, y) et les points de vie de l'unité
            self.screen.blit(font.render(f"({unit.x}, {unit.y}): {unit.health} HP", True, WHITE),
                            (GRID_SIZE * CELL_SIZE + 10, decalage))





pygame.init()  # Initialisation de Pygame 

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

# Définir le titre de la fenêtre
pygame.display.set_caption("Jeu de tour par tour 2D")

# Initialiser l'instance du jeu
# L'objet Game gère la logique et les mécaniques du jeu
game = Game(screen)

# Créer un objet horloge pour contrôler la cadence du jeu
clock = pygame.time.Clock()

# Boucle principale du jeu
while True:
    game.handle_player_turn()  # Appelle la gestion du tour actuel (joueur ou ennemi)
    clock.tick(FPS)  # Contrôle la vitesse de rafraîchissement du jeu en fonction de FPS (30 images/s par défaut)
