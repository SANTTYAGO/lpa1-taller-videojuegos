# ui/pantalla.py
import pygame
from models.personaje import Personaje # Importamos la clase de lógica

# Constantes de la ventana
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 32
VELOCIDAD = 5

# Paleta de colores temporales
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)
GRIS_PANEL = (50, 50, 50)

class MotorGrafico:
    # NUEVO: Ahora el motor recibe al personaje lógico
    def __init__(self, heroe: Personaje):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura 16-Bits")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Enlazamos el personaje lógico con la interfaz
        self.heroe = heroe
        
        # Configuración de fuente para los textos
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        
        # Posición inicial (centro de la pantalla, dejando espacio para el HUD abajo)
        self.jugador_x = (ANCHO // 2) - (TAMANO_TILE // 2)
        self.jugador_y = ((ALTO - 60) // 2) - (TAMANO_TILE // 2)

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False

        teclas = pygame.key.get_pressed()
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador_x -= VELOCIDAD
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador_x += VELOCIDAD
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.jugador_y -= VELOCIDAD
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.jugador_y += VELOCIDAD

        # Colisión: No salir de los bordes, respetando el panel inferior de 60px
        self.jugador_x = max(0, min(self.jugador_x, ANCHO - TAMANO_TILE))
        self.jugador_y = max(0, min(self.jugador_y, ALTO - 60 - TAMANO_TILE))

    def dibujar_hud(self):
        """Dibuja la barra de estado inferior al estilo RPG clásico."""
        # Fondo del panel
        panel_rect = pygame.Rect(0, ALTO - 60, ANCHO, 60)
        pygame.draw.rect(self.pantalla, GRIS_PANEL, panel_rect)
        pygame.draw.rect(self.pantalla, BLANCO, panel_rect, 2) # Borde blanco

        # Textos de estadísticas basados en el objeto lógico
        texto_nombre = self.fuente.render(self.heroe.nombre, True, BLANCO)
        texto_hp = self.fuente.render(f"HP: {self.heroe.puntos_vida}/{self.heroe.puntos_vida_max}", True, (255, 100, 100))
        texto_nivel = self.fuente.render(f"Nivel: {self.heroe.nivel}", True, (100, 255, 100))
        texto_ataque = self.fuente.render(f"ATK: {self.heroe.ataque}", True, BLANCO)
        
        # Posicionar los textos en el panel
        self.pantalla.blit(texto_nombre, (20, ALTO - 40))
        self.pantalla.blit(texto_hp, (200, ALTO - 40))
        self.pantalla.blit(texto_nivel, (350, ALTO - 40))
        self.pantalla.blit(texto_ataque, (500, ALTO - 40))

    def dibujar(self):
        self.pantalla.fill(VERDE_OSCURO)
        
        # Dibujar al jugador
        jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
        pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

        # Dibujar la interfaz por encima de todo
        self.dibujar_hud()

        pygame.display.flip()

    def actualizar(self):
        self.reloj.tick(FPS)

    def salir(self):
        pygame.quit()