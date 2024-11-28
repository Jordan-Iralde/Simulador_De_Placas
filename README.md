import pygame
import random
import numpy as np
import sys
from pygame.locals import *

# Configuración de la ventana y parámetros
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 10
NUM_PLATES = 5
EVENT_PROBABILITY = 0.02  # Probabilidad de un evento aleatorio (terremoto)
PLATE_SPEED = 1  # Velocidad de movimiento de las placas

# Colores
WATER_COLOR = (0, 0, 255)
MOUNTAIN_COLOR = (139, 69, 19)
PLATE_COLOR = (150, 150, 255)
BUTTON_COLOR = (0, 255, 0)
BUTTON_HOVER_COLOR = (0, 200, 0)

# Función para mejorar la forma de los continentes (algoritmo de difusión)
def generate_terrain_map(width, height):
    # Inicializar el mapa (agua y tierra aleatoria)
    terrain_map = np.random.choice([0, 1], size=(height, width), p=[0.7, 0.3])  # 30% tierra, 70% agua
    
    # Mejorar la forma de los continentes con un filtro de difusión
    for _ in range(3):  # Realizar varias iteraciones de suavizado
        new_terrain_map = terrain_map.copy()
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Promediar las celdas vecinas (suavizar)
                neighbors = terrain_map[y-1:y+2, x-1:x+2]
                new_terrain_map[y, x] = np.sum(neighbors) // 9  # Promedio de vecinos
        terrain_map = new_terrain_map
    
    return terrain_map

class Plate:
    def __init__(self, plate_id, x, y, color):
        self.plate_id = plate_id
        self.color = color
        self.blocks = {(x, y)}
        self.direction = np.array([random.choice([-1, 0, 1]), random.choice([-1, 0, 1])])  # Movimiento aleatorio
        self.speed = PLATE_SPEED

    def move(self, terrain_width, terrain_height):
        # Mover los bloques de la placa y realizar la envoltura esférica
        new_blocks = set()
        for x, y in self.blocks:
            new_x = (x + self.direction[0] * self.speed) % terrain_width
            new_y = (y + self.direction[1] * self.speed) % terrain_height
            new_blocks.add((new_x, new_y))
        self.blocks = new_blocks

    def handle_collision(self, terrain):
        # Colisiones: cuando las placas se tocan, se eleva el terreno
        for x, y in self.blocks:
            if 0 <= x < len(terrain[0]) and 0 <= y < len(terrain):
                terrain[y][x] = self.plate_id + 1  # Asignar el id de la placa al terreno

    def add_block(self, x, y):
        self.blocks.add((x, y))

    def interact_with_plates(self, terrain, plates):
        # Simular interacciones entre placas
        for x, y in self.blocks:
            if 0 <= x < len(terrain[0]) and 0 <= y < len(terrain):
                neighbor_plate_id = terrain[y][x] - 1
                if neighbor_plate_id != self.plate_id and neighbor_plate_id >= 0:
                    plates[neighbor_plate_id].create_mountains(terrain, x, y)

    def create_mountains(self, terrain, x, y):
        # Crear montañas al interactuar con otras placas
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 <= x + dx < len(terrain[0]) and 0 <= y + dy < len(terrain):
                    terrain[y + dy][x + dx] = max(terrain[y + dy][x + dx], 2)  # Elevar el terreno

    def render(self, screen, block_size):
        for x, y in self.blocks:
            pygame.draw.circle(screen, self.color, (int(x * block_size + block_size / 2), int(y * block_size + block_size / 2)), block_size // 2)

def initialize_plates(width, height, map_data):
    plates = []
    for i in range(NUM_PLATES):
        # Elegir un lugar donde no haya agua (basado en el mapa de continentes)
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        while map_data[y][x] == 255:  # Si es agua, buscamos otro punto
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        plates.append(Plate(i, x, y, (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))))  # Color aleatorio
    return plates

def generate_earthquake(terrain):
    # Sismos aleatorios con magnitudes y ubicaciones
    if random.random() < EVENT_PROBABILITY:
        x = random.randint(0, len(terrain[0]) - 1)
        y = random.randint(0, len(terrain) - 1)
        magnitude = random.randint(4, 9)  # Magnitud aleatoria entre 4 y 9
        print(f"Sismo generado en ({x}, {y}) con magnitud {magnitude}")
        # Simulamos el daño del terremoto afectando el terreno
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if 0 <= x + dx < len(terrain[0]) and 0 <= y + dy < len(terrain):
                    terrain[y + dy][x + dx] = max(0, terrain[y + dy][x + dx] - magnitude)

def render_map(screen, terrain, plates, block_size):
    # Renderizar el mapa sin rastros
    for y in range(len(terrain)):
        for x in range(len(terrain[y])):
            value = terrain[y][x]
            if value == 0:
                color = WATER_COLOR  # Agua
            else:
                color = plates[int(value) - 1].color  # Convertir a entero antes de acceder a la lista de placas
            pygame.draw.rect(screen, color, (x * block_size, y * block_size, block_size, block_size))

def draw_ui(screen, plates, terrain):
    # Información de las placas y el terreno
    font = pygame.font.Font(None, 36)
    text = font.render(f'Placas: {len(plates)}', True, (255, 255, 255))
    screen.blit(text, (10, 10))

    for i, plate in enumerate(plates):
        plate_info = f"Placa {i}: {len(plate.blocks)} bloques"
        text = font.render(plate_info, True, plate.color)
        screen.blit(text, (10, 40 + i * 30))

def draw_button(screen, x, y, width, height, text, color, hover_color):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))

    font = pygame.font.Font(None, 30)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (x + width // 2 - label.get_width() // 2, y + height // 2 - label.get_height() // 2))

def handle_button_click(x, y, width, height):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
        return True
    return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simulador de Placas Tectónicas")
    clock = pygame.time.Clock()

    # Dimensiones del terreno
    terrain_width = WINDOW_WIDTH // BLOCK_SIZE
    terrain_height = WINDOW_HEIGHT // BLOCK_SIZE

    # Generamos el mapa de terreno
    terrain = generate_terrain_map(terrain_width, terrain_height)

    plates = initialize_plates(terrain_width, terrain_height, terrain)
    
    running = True
    while running:
        screen.fill((0, 0, 0))  # Fondo negro

        # Mover placas
        for plate in plates:
            plate.move(terrain_width, terrain_height)
            plate.handle_collision(terrain)
            plate.interact_with_plates(terrain, plates)

        generate_earthquake(terrain)

        render_map(screen, terrain, plates, BLOCK_SIZE)

        draw_ui(screen, plates, terrain)

        # Dibujo de botones (puedes agregar más interactividad aquí)
        draw_button(screen, 650, 50, 120, 40, "Start Simulation", BUTTON_COLOR, BUTTON_HOVER_COLOR)

        # Detectar eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
