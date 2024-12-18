class Skill:
    """
    Classe de base pour les compétences utilisables par les unités.
    Chaque compétence a un nom, une puissance (dommages ou soins) et une portée.

    - name : Nom de la compétence.
    - power : Puissance de la compétence (dommages positifs ou soins négatifs).
    - range : Portée maximale à laquelle la compétence peut être utilisée.
    """
    def __init__(self, name, power, range):
        self.name = name  # Nom de la compétence
        self.power = power  # Valeur des dommages (positif) ou soins (négatif)
        self.range = range  # Portée maximale en cases (horizontalement et verticalement)

    def use(self, user, target):
        """
        Méthode pour utiliser une compétence sur une cible.
        - user : L'unité qui utilise la compétence.
        - target : L'unité ciblée par la compétence.
        
        Condition : La cible doit être dans la portée de la compétence.
        
        Effet : Réduit les points de santé de la cible par la valeur de "power".
        """
        if abs(user.x - target.x) <= self.range and abs(user.y - target.y) <= self.range:
            damage = user.attack_power * self.power 
            damage = damage/target.defense_power
            target.health -= damage  # Applique les dommages ou soins à la cible


class Pistolet(Skill):
    """
    Compétence Pistolet : Inflige des dommages à une cible dans une portée de 3 cases.
    - Dégâts : 30
    - Portée : 3 cases
    """
    def __init__(self):
        super().__init__("Pistolet", 30, 3)  # Initialise avec le nom "Pistolet", 30 de puissance, et portée 3


class Grenade(Skill):
    """
    Compétence Grenade : Inflige des dommages à plusieurs cibles situées sur des positions adjacentes.
    - Dégâts : 50
    - Portée : 2 cases
    
    La méthode "use" est surchargée pour gérer plusieurs cibles.
    """
    def __init__(self):
        super().__init__("Grenade", 50, 2)  # Initialise avec le nom "Grenade", 50 de puissance, et portée 2

    def use(self, user, target_positions, enemies):
        """
        Applique les dégâts aux unités situées sur les positions adjacentes ciblées.
        
        Paramètres :
        - user : L'unité qui lance la grenade.
        - target_positions : Liste des positions visées [(x1, y1), (x2, y2)].
        - enemies : Liste des unités ennemies à vérifier.
        
        Effet : Réduit les points de santé des unités se trouvant sur les positions ciblées.
        """
        
        for pos in target_positions:  # Parcourir les positions visées par la grenade
            for enemy in enemies:  # Parcourir les unités ennemies
                if (enemy.x, enemy.y) == pos:  # Vérifier si l'ennemi est sur une position ciblée
                    damage = user.attack_power * self.power 
                    damage = damage/enemy.defense_power
                    enemy.health -= self.power  # Appliquer les dégâts de la grenade


class Sniper(Skill):
    """
    Compétence Sniper : Inflige des dommages à une cible unique à longue portée.
    - Dégâts : 80
    - Portée : 5 cases
    """
    def __init__(self):
        super().__init__("Sniper", 80, 5)  # Initialise avec le nom "Sniper", 80 de puissance, et portée 5


class Soigner(Skill):
    """
    Compétence Soigner : Restaure des points de santé à une cible alliée dans une portée de 3 cases.
    - Restaure : 30 HP (valeur négative pour inverser les dommages).
    - Portée : 3 cases

    La méthode "use" est spécialisée pour soigner une unité alliée.
    """
    def __init__(self):
        super().__init__("Soigner", -30, 8)  # Initialise avec le nom "Soigner", -30 (soins), et portée 2

    def use(self, user, target):
        """
        Soigne une unité alliée si elle est dans la portée.
        
        Paramètres :
        - user : L'unité qui utilise la compétence Soigner.
        - target : L'unité alliée ciblée pour recevoir les soins.
        
        Effet : Restaure les points de santé de la cible, sans dépasser 100 HP.
        """
        if abs(user.x - target.x) <= self.range and abs(user.y - target.y) <= self.range:
            # Ajouter les points de santé en s'assurant qu'ils ne dépassent pas 100
            target.health = min(100, target.health - self.power)
class Teleportation(Skill):
    """
    Compétence Téléportation : Permet à une unité de se déplacer vers une case vide sans obstacle.
    - Portée illimitée.
    """
    def __init__(self):
        super().__init__("Teleportation", 0, float('inf'))  # Portée infinie

    def use(self, user, target_position):
        """
        Utilise la compétence Téléportation pour se déplacer vers une position vide.
        - target_position : Tuple (x, y) représentant la position ciblée.
        - obstacles : Liste des obstacles sur la carte.
        - units : Liste de toutes les unités présentes sur la carte.
        """
        target_x, target_y = target_position

        # Met à jour la position de l'unité
        user.x, user.y = target_position
        print(f"{user} s'est téléporté en ({target_x}, {target_y}).")
        return True
