# ui/pantalla.py
import pygame
from models.personaje import Personaje
from models.enemigo import Enemigo # NUEVO: Importamos al enemigo lógico

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 32
VELOCIDAD = 5

# Paleta
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)
ROJO_ENEMIGO = (220, 20, 60) # NUEVO: Color del enemigo
GRIS_PANEL = (50, 50, 50)

class MotorGrafico:
    # NUEVO: Recibimos también un enemigo_prueba
    def __init__(self, heroe: Personaje, enemigo_prueba: Enemigo = None):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura 16-Bits")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        self.heroe = heroe
        self.enemigo = enemigo_prueba
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Estado del juego
        self.estado = "EXPLORACION" # Puede ser "EXPLORACION" o "COMBATE"
        
        # Coordenadas iniciales
        self.jugador_x = (ANCHO // 2) - (TAMANO_TILE // 2)
        self.jugador_y = ((ALTO - 60) // 2) - (TAMANO_TILE // 2)
        
        # Posicionamos al enemigo a la derecha del mapa si existe
        if self.enemigo:
            self.enemigo_rect = pygame.Rect(600, 300, TAMANO_TILE, TAMANO_TILE)

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
                
            # NUEVO: Controles en combate (Ataque rápido de prueba)
            if self.estado == "COMBATE" and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN: # Presionar ENTER para simular victoria
                    self.enemigo.puntos_vida = 0
                    self.heroe.ganar_experiencia(150) # Dar EXP al jugador
                    self.estado = "EXPLORACION" # Volver al mapa

        if self.estado == "EXPLORACION":
            self.mover_jugador()
            self.verificar_colisiones()

    def mover_jugador(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador_x -= VELOCIDAD
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador_x += VELOCIDAD
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.jugador_y -= VELOCIDAD
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.jugador_y += VELOCIDAD

        self.jugador_x = max(0, min(self.jugador_x, ANCHO - TAMANO_TILE))
        self.jugador_y = max(0, min(self.jugador_y, ALTO - 60 - TAMANO_TILE))

    def verificar_colisiones(self):
        """Detecta si el rectángulo del jugador toca el del enemigo."""
        if self.enemigo and self.enemigo.esta_vivo():
            jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
            if jugador_rect.colliderect(self.enemigo_rect):
                print(f"¡Emboscada! Iniciando combate contra {self.enemigo.nombre}.")
                self.estado = "COMBATE" # Cambiamos de pantalla
                # Empujamos al jugador un poco hacia atrás para que al volver no siga chocando
                self.jugador_x -= 40 

    def dibujar_hud(self):
        panel_rect = pygame.Rect(0, ALTO - 60, ANCHO, 60)
        pygame.draw.rect(self.pantalla, GRIS_PANEL, panel_rect)
        pygame.draw.rect(self.pantalla, BLANCO, panel_rect, 2)

        texto_nombre = self.fuente.render(self.heroe.nombre, True, BLANCO)
        texto_hp = self.fuente.render(f"HP: {self.heroe.puntos_vida}/{self.heroe.puntos_vida_max}", True, (255, 100, 100))
        texto_nivel = self.fuente.render(f"Nivel: {self.heroe.nivel}", True, (100, 255, 100))
        texto_ataque = self.fuente.render(f"ATK: {self.heroe.ataque}", True, BLANCO)
        
        self.pantalla.blit(texto_nombre, (20, ALTO - 40))
        self.pantalla.blit(texto_hp, (200, ALTO - 40))
        self.pantalla.blit(texto_nivel, (350, ALTO - 40))
        self.pantalla.blit(texto_ataque, (500, ALTO - 40))

    def dibujar(self):
        if self.estado == "EXPLORACION":
            self.pantalla.fill(VERDE_OSCURO)
            
            # Dibujar enemigo (solo si sigue vivo)
            if self.enemigo and self.enemigo.esta_vivo():
                pygame.draw.rect(self.pantalla, ROJO_ENEMIGO, self.enemigo_rect)

            # Dibujar jugador
            jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
            pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

            self.dibujar_hud()

        elif self.estado == "COMBATE":
            # Pantalla de batalla JRPG (Fondo negro)
            self.pantalla.fill(NEGRO)
            titulo = self.fuente_grande.render(f"¡{self.enemigo.nombre} ataca!", True, ROJO_ENEMIGO)
            instruccion = self.fuente.render("Presiona ENTER para atacar y ganar (Prueba temporal)", True, BLANCO)
            
            self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 3))
            self.pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, ALTO // 2))
            
            self.dibujar_hud() # Mantenemos la barra de vida abajo

        pygame.display.flip()

    def actualizar(self):
        self.reloj.tick(FPS)

    def salir(self):
        pygame.quit()