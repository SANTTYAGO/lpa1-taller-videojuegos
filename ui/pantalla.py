# ui/pantalla.py
import pygame
from models.personaje import Personaje
from models.enemigo import Enemigo
from core.combate import SistemaCombate # IMPORTANTE: Traemos el cerebro matemático del daño

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 32
VELOCIDAD = 5

# Paleta de colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)
ROJO_ENEMIGO = (220, 20, 60) 
GRIS_PANEL = (50, 50, 50)
AMARILLO = (255, 215, 0) # Para destacar los menús de combate

class MotorGrafico:
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
        
        # Estados Principales
        self.estado = "EXPLORACION" 
        
        # NUEVO: Sub-Estados del Combate JRPG
        self.turno_actual = "JUGADOR" # Puede ser JUGADOR, ENEMIGO, VICTORIA, DERROTA
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        
        self.jugador_x = (ANCHO // 2) - (TAMANO_TILE // 2)
        self.jugador_y = ((ALTO - 60) // 2) - (TAMANO_TILE // 2)
        
        if self.enemigo:
            self.enemigo_rect = pygame.Rect(600, 300, TAMANO_TILE, TAMANO_TILE)

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
                
            # Escuchar teclado solo en modo combate
            if self.estado == "COMBATE" and evento.type == pygame.KEYDOWN:
                self.manejar_teclas_combate(evento)

        # Mover jugador solo en exploración
        if self.estado == "EXPLORACION":
            self.mover_jugador()
            self.verificar_colisiones()

    def manejar_teclas_combate(self, evento):
        """Controlador de la Máquina de Estados de Turnos (R5.1 y R5.2)"""
        
        if self.turno_actual == "JUGADOR":
            if evento.key == pygame.K_a: # Presionar 'A' para Atacar
                dano = SistemaCombate.calcular_dano(self.heroe.ataque, self.enemigo.defensa)
                self.enemigo.recibir_dano(dano)
                self.mensaje_combate = f"¡{self.heroe.nombre} ataca! Causa {dano} puntos de daño."
                
                if not self.enemigo.esta_vivo():
                    self.turno_actual = "VICTORIA"
                else:
                    self.turno_actual = "ENEMIGO"

        elif self.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE: # Presionar 'ESPACIO' para recibir el golpe enemigo
                dano = SistemaCombate.calcular_dano(self.enemigo.ataque, self.heroe.defensa)
                self.heroe.recibir_dano(dano)
                self.mensaje_combate = f"¡{self.enemigo.nombre} contraataca y causa {dano} de daño!"
                
                if not self.heroe.esta_vivo():
                    self.turno_actual = "DERROTA"
                else:
                    self.turno_actual = "JUGADOR"

        elif self.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN: # ENTER para salir del combate
                self.heroe.ganar_experiencia(100) # Recompensa por ganar
                self.estado = "EXPLORACION"
                
        elif self.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN: # ENTER para cerrar el juego tras morir
                self.corriendo = False

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
        if self.enemigo and self.enemigo.esta_vivo():
            jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
            if jugador_rect.colliderect(self.enemigo_rect):
                self.estado = "COMBATE" 
                self.turno_actual = "JUGADOR" # Al chocar, el jugador siempre tiene el primer turno
                self.mensaje_combate = f"¡Emboscada! {self.enemigo.nombre} te ataca."
                self.jugador_x -= 40 # Separación para no chocar infinitamente

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
            
            if self.enemigo and self.enemigo.esta_vivo():
                pygame.draw.rect(self.pantalla, ROJO_ENEMIGO, self.enemigo_rect)

            jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
            pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

            self.dibujar_hud()

        elif self.estado == "COMBATE":
            self.pantalla.fill(NEGRO)
            
            # Dibujar Título del Combate y HP del Enemigo
            titulo = self.fuente_grande.render(f"VS {self.enemigo.nombre}", True, ROJO_ENEMIGO)
            hp_enemigo = self.fuente.render(f"HP Enemigo: {self.enemigo.puntos_vida}", True, BLANCO)
            self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
            self.pantalla.blit(hp_enemigo, (ANCHO // 2 - hp_enemigo.get_width() // 2, 100))
            
            # Dibujar Caja de Mensajes estilo JRPG
            caja_msg_rect = pygame.Rect(100, 200, 600, 150)
            pygame.draw.rect(self.pantalla, GRIS_PANEL, caja_msg_rect)
            pygame.draw.rect(self.pantalla, AMARILLO, caja_msg_rect, 3)
            
            texto_msg = self.fuente.render(self.mensaje_combate, True, BLANCO)
            self.pantalla.blit(texto_msg, (120, 220))
            
            # Dibujar Instrucciones dinámicas según el turno
            if self.turno_actual == "JUGADOR":
                instruccion = self.fuente.render("▶ Presiona 'A' para Atacar", True, AMARILLO)
            elif self.turno_actual == "ENEMIGO":
                instruccion = self.fuente.render("▶ Presiona 'ESPACIO' para continuar", True, AMARILLO)
            elif self.turno_actual == "VICTORIA":
                instruccion = self.fuente.render("▶ ¡Has ganado! Presiona 'ENTER' para salir", True, (100, 255, 100))
            elif self.turno_actual == "DERROTA":
                instruccion = self.fuente.render("▶ Has muerto. Presiona 'ENTER' para salir", True, ROJO_ENEMIGO)
                
            self.pantalla.blit(instruccion, (120, 300))
            
            self.dibujar_hud()

        pygame.display.flip()

    def actualizar(self):
        self.reloj.tick(FPS)

    def salir(self):
        pygame.quit()