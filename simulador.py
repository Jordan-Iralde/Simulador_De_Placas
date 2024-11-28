import pygame
import random
import numpy as np
import sys
import time

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

class Plate:
    def __init__(self, plate_id, x, y):
        self.plate_id = plate_id
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))  # Colores aleatorios
        self.blocks = {(x, y)}
        self.direction = np.array([random.choice([-1, 0, 1]), random.choice([-1, 0, 1])])  # Movimiento aleatorio en x y y
        self.speed = PLATE_SPEED

    def move(self):
        # Mover cada bloque de la placa en la dirección elegida
        self.blocks = {(x + self.direction[0] * self.speed, y + self.direction[1] * self.speed) for x, y in self.blocks}

    def handle_collision(self, terrain):
        # Colisiones: Al colisionar con otra placa, se eleva el terreno o se forman montañas
        for x, y in self.blocks:
            if 0 <= x < len(terrain[0]) and 0 <= y < len(terrain):
                terrain[y][x] = self.plate_id + 1  # Asignar el id de la placa al terreno

    def add_block(self, x, y):
        self.blocks.add((x, y))

    def interact_with_plates(self, terrain, plates):
        # Simular interacciones complejas entre placas (colisiones, movimientos)
        for x, y in self.blocks:
            if 0 <= x < len(terrain[0]) and 0 <= y < len(terrain):
                neighbor_plate_id = terrain[y][x] - 1
                if neighbor_plate_id != self.plate_id and neighbor_plate_id >= 0:
                    # Realizar acción al colisionar (por ejemplo, formar montañas)
                    plates[neighbor_plate_id].create_mountains(terrain, x, y)

    def create_mountains(self, terrain, x, y):
        # Crear montañas en el terreno cuando las placas interactúan
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 <= x + dx < len(terrain[0]) and 0 <= y + dy < len(terrain):
                    terrain[y + dy][x + dx] = max(terrain[y + dy][x + dx], 2)  # Elevar el terreno

    def render(self, screen, block_size):
        for x, y in self.blocks:
            pygame.draw.circle(screen, self.color, (int(x * block_size + block_size / 2), int(y * block_size + block_size / 2)), block_size // 2)

def initialize_plates(width, height):
    plates = []
    for i in range(NUM_PLATES):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        plates.append(Plate(i, x, y))
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
    # Renderizamos el mapa
    for y in range(len(terrain)):
        for x in range(len(terrain[y])):
            value = terrain[y][x]
            if value == 0:
                color = WATER_COLOR  # Agua
            else:
                color = plates[value - 1].color  # Color de la placa
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

    # Inicializar el terreno y las placas
    terrain = np.zeros((terrain_height, terrain_width), dtype=int)
    plates = initialize_plates(terrain_width, terrain_height)

    running = True
    while running:
        screen.fill((0, 0, 0))  # Limpiar pantalla

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Mover placas
        for plate in plates:
            plate.move()
            plate.handle_collision(terrain)
            plate.interact_with_plates(terrain, plates)  # Interacción entre placas

        # Generar eventos aleatorios (sismos)
        generate_earthquake(terrain)

        # Renderizar el mapa
        render_map(screen, terrain, plates, BLOCK_SIZE)

        # Dibujar UI
        draw_ui(screen, plates, terrain)

        # Botón para ajustar velocidad
        draw_button(screen, 10, WINDOW_HEIGHT - 60, 200, 50, "Ajustar Velocidad", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        if handle_button_click(10, WINDOW_HEIGHT - 60, 200, 50):
            global PLATE_SPEED
            PLATE_SPEED = random.randint(1, 5)  # Cambiar la velocidad de las placas

        # Botón para ajustar probabilidad de terremoto
        draw_button(screen, 220, WINDOW_HEIGHT - 60, 200, 50, "Ajustar Prob. Sismo", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        if handle_button_click(220, WINDOW_HEIGHT - 60, 200, 50):
            global EVENT_PROBABILITY
            EVENT_PROBABILITY = random.uniform(0.01, 0.1)  # Cambiar probabilidad de terremoto

        # Mostrar estadísticas
        draw_button(screen, 440, WINDOW_HEIGHT - 60, 200, 50, "Mostrar Estadísticas", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        if handle_button_click(440, WINDOW_HEIGHT - 60, 200, 50):
            print(f"Velocidad Placas: {PLATE_SPEED}, Probabilidad de Sismo: {EVENT_PROBABILITY}")

        # Renderizar las placas
        for plate in plates:
            plate.render(screen, BLOCK_SIZE)

        pygame.display.flip()

        # Control de velocidad
        clock.tick(10)  # Ajustar velocidad de la simulación

    pygame.quit()

if __name__ == "__main__":
    main()
