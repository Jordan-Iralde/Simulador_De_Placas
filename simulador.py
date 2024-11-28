import pygame
import random
import sys

# Tamaño de la ventana
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200

# Tamaño de los "bloques" de terreno
BLOCK_SIZE = 10

# Función para generar ruido de Perlin (implementación simple)
def perlin_noise(x, y):
    # Función pseudoaleatoria simple
    return random.uniform(0.0, 1.0)

# Función para generar el mapa de alturas utilizando el ruido de Perlin
def generate_terrain(width, height, scale):
    terrain = [[0.0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            island_left = perlin_noise((x - width / 3) / scale, y / scale)
            island_right = perlin_noise((x - 2 * width / 3) / scale, y / scale)
            terrain_height = max(island_left, island_right)
            terrain[y][x] = terrain_height
    return terrain

# Función para renderizar el mapa con bloques más grandes
def render_map(screen, terrain, block_size):
    for y in range(len(terrain)):
        for x in range(len(terrain[y])):
            height = terrain[y][x]
            normalized_height = min(1.0, max(0.0, height))
            
            red, green, blue = 0, 0, 255
            if normalized_height > 0.5:
                green = min(255, int((normalized_height - 0.5) * 2 * 255))
                blue = max(0, 255 - int((normalized_height - 0.5) * 2 * 255))
            if normalized_height > 0.8:
                red = min(255, int((normalized_height - 0.8) * 5 * 255))
                green = max(0, 255 - int((normalized_height - 0.8) * 5 * 255))

            pygame.draw.rect(screen, (red, green, blue), 
                             (x * block_size, y * block_size, block_size, block_size))

def main(scale=50.0):
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Generador de Islas con Ruido de Perlin")
    clock = pygame.time.Clock()

    # Generar terreno
    terrain_width = WINDOW_WIDTH // BLOCK_SIZE
    terrain_height = WINDOW_HEIGHT // BLOCK_SIZE
    terrain = generate_terrain(terrain_width, terrain_height, scale)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill((0, 0, 0))  # Limpiar la pantalla
        render_map(screen, terrain, BLOCK_SIZE)
        pygame.display.flip()
        clock.tick(60)  # Simular 60 FPS

    pygame.quit()

if __name__ == "__main__":
    scale = 50.0
    if len(sys.argv) > 1:
        scale = float(sys.argv[1])
        print(f"Usando escala: {scale}")
    main(scale)
