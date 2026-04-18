# ui/pantalla.py
import pygame

# Constantes de la ventana
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 32
VELOCIDAD = 5 # La velocidad a la que se moverá el personaje

# Paleta de colores temporales
NEGRO = (0, 0, 0)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)  

class MotorGrafico:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura 16-Bits")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Posición inicial del jugador (en el centro de la pantalla)
        self.jugador_x = (ANCHO // 2) - (TAMANO_TILE // 2)
        self.jugador_y = (ALTO // 2) - (TAMANO_TILE // 2)

    def manejar_eventos(self):
        """Escucha las acciones del usuario y el teclado."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False

        # Capturar el estado de todas las teclas para un movimiento continuo y fluido
        teclas = pygame.key.get_pressed()
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador_x -= VELOCIDAD
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador_x += VELOCIDAD
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.jugador_y -= VELOCIDAD
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.jugador_y += VELOCIDAD

        # Sistema de colisión básico: Evitar que el jugador salga de la pantalla
        self.jugador_x = max(0, min(self.jugador_x, ANCHO - TAMANO_TILE))
        self.jugador_y = max(0, min(self.jugador_y, ALTO - TAMANO_TILE))

    def dibujar(self):
        """Se encarga de pintar todo en la pantalla frame por frame."""
        self.pantalla.fill(VERDE_OSCURO)
        
        # Dibujar al jugador usando sus coordenadas dinámicas
        jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
        pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

        pygame.display.flip()

    def actualizar(self):
        """Mantiene el juego a la velocidad correcta."""
        self.reloj.tick(FPS)

    def salir(self):
        """Cierra Pygame de forma segura."""
        pygame.quit()