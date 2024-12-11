# peut etre modifier par Fadel

class Joueur:
    """
    Classe représentant un joueur dans le jeu.

    Chaque joueur possède :
    - un nom pour l'identifier,
    - une liste d'unités qu'il contrôle.
    
    Attributs :
    - name : str - Nom du joueur.
    - units : list - Liste des unités contrôlées par le joueur.
    """
    def __init__(self, name, units):
        """
        Initialise un joueur avec un nom et une liste d'unités.

        Paramètres :
        - name : str - Nom donné au joueur (ex. "Player 1").
        - units : list - Liste des instances d'unités associées au joueur.
        """
        self.name = name  # Nom du joueur
        self.units = units  # Liste des unités contrôlées par le joueur