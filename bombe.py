import pygame

CELL_SIZE = 50  # Taille d'une case

class Bombe :
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # Adapter à la taille des cellules
        self.is_used = False  # La bombe n'est pas encore utilisée


    @staticmethod
    def generate_bombes_from_positions(image_path, positions):
        bombes=[]
        for x, y in positions:
            bombes.append(Bombe(x, y, image_path))
        return bombes
    def draw(self, screen):
        # Calculer la position dans la fenêtre
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        screen.blit(self.image, (screen_x, screen_y))


