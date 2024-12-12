import pygame

CELL_SIZE = 50  # Taille d'une case

class Gift:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # Adapter à la taille des cellules

    def draw(self, screen):
        # Calculer la position dans la fenêtre
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        screen.blit(self.image, (screen_x, screen_y))

    @staticmethod
    def generate_gifts_from_positions(image_path, positions):
        gifts = []
        for x, y in positions:
            gifts.append(Gift(x, y, image_path))
        return gifts

