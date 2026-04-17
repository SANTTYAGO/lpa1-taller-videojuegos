# ui/pantalla.py
import pygame

# Constantes de la ventana
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 32 # Tamaño estándar para juegos de 16-bits (32x32 píxeles)

# Paleta de colores temporales
NEGRO = (0, 0, 0)
VERDE_OSCURO = (34, 139, 34) # Representará el pasto
AZUL_HEROE = (30, 144, 255)  # Representará a nuestro personaje

class MotorGrafico:
    def __init__(self):
        # Inicializar todos los módulos de Pygame
        pygame.init()
        
        # Configurar la ventana
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura 16-Bits")
        
        # Reloj para controlar la velocidad del juego
        self.reloj = pygame.time.Clock()
        self.corriendo = True

    def manejar_eventos(self):
        """Escucha las acciones del usuario (teclado, ratón, cerrar ventana)."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False

    def dibujar(self):
        """Se encarga de pintar todo en la pantalla frame por frame."""
        # 1. Limpiar la pantalla con un color de fondo (pasto)
        self.pantalla.fill(VERDE_OSCURO)
        
        # 2. Dibujar al jugador en el centro (temporalmente un cuadrado azul)
        # Más adelante, aquí le diremos a la pantalla que dibuje la imagen (sprite) del personaje
        centro_x = (ANCHO // 2) - (TAMANO_TILE // 2)
        centro_y = (ALTO // 2) - (TAMANO_TILE // 2)
        jugador_rect = pygame.Rect(centro_x, centro_y, TAMANO_TILE, TAMANO_TILE)
        
        pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

        # 3. Actualizar la pantalla para mostrar los cambios
        pygame.display.flip()

    def actualizar(self):
        """Mantiene el juego a la velocidad correcta (60 FPS)."""
        self.reloj.tick(FPS)

    def salir(self):
        """Cierra Pygame de forma segura."""
        pygame.quit()