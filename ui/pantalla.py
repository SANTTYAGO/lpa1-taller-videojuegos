# ui/pantalla.py
import pygame
import os
from models.personaje import Personaje
from models.enemigo import Enemigo
from core.combate import SistemaCombate

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 64
VELOCIDAD = 5

# Paleta de colores (Fallback)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)
ROJO_ENEMIGO = (220, 20, 60) 
GRIS_PANEL = (50, 50, 50)
AMARILLO = (255, 215, 0)

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
        
        self.estado = "EXPLORACION" 
        self.turno_actual = "JUGADOR"
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        
        self.jugador_x = (ANCHO // 2) - (TAMANO_TILE // 2)
        self.jugador_y = ((ALTO - 60) // 2) - (TAMANO_TILE // 2)
        
        if self.enemigo:
            self.enemigo_rect = pygame.Rect(600, 300, TAMANO_TILE, TAMANO_TILE)

        # NUEVO: Sistema de carga de Sprites
        self.cargar_sprites()

    def cargar_sprites(self):
        """Intenta cargar las imágenes y recorta el primer frame de las hojas de sprites."""
        self.usar_sprites = False
        try:
            escala_mapa = (64, 64) 
            
            # 1. Cargar el Héroe (Hoja de Sprites completa)
            ruta_heroe = os.path.join("assets", "Heroe", "Soldier", "Soldier-Idle.png")
            hoja_heroe = pygame.image.load(ruta_heroe).convert_alpha()
            
            # Detectamos el tamaño de un solo cuadro (asumiendo que es cuadrado, usamos su altura)
            tamano_cuadro_h = hoja_heroe.get_height()
            
            # Recortamos el primer frame: (X inicial, Y inicial, Ancho, Alto)
            rect_primer_frame_h = pygame.Rect(0, 0, tamano_cuadro_h, tamano_cuadro_h)
            frame_heroe = hoja_heroe.subsurface(rect_primer_frame_h)
            
            # Ahora sí escalamos solo ese recorte
            self.img_heroe = pygame.transform.scale(frame_heroe, escala_mapa)

            # 2. Cargar el Enemigo (Hoja de Sprites completa)
            ruta_enemigo = os.path.join("assets", "Enemigo", "Orc", "Orc-Idle.png")
            hoja_enemigo = pygame.image.load(ruta_enemigo).convert_alpha()
            
            tamano_cuadro_e = hoja_enemigo.get_height()
            rect_primer_frame_e = pygame.Rect(0, 0, tamano_cuadro_e, tamano_cuadro_e)
            frame_enemigo = hoja_enemigo.subsurface(rect_primer_frame_e)
            
            self.img_enemigo = pygame.transform.scale(frame_enemigo, escala_mapa)

            # 3. Cargar el Suelo (Este normalmente sí es un solo bloque, no requiere recorte)
            ruta_suelo = os.path.join("assets", "Suelo", "Grass_Middle.png")
            self.img_suelo = pygame.image.load(ruta_suelo).convert()
            self.img_suelo = pygame.transform.scale(self.img_suelo, (TAMANO_TILE, TAMANO_TILE))
            
            self.usar_sprites = True
            print("✅ Sprites recortados y cargados correctamente.")
        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}")
            print("Usando gráficos por defecto (cuadrados).")

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
                
            if self.estado == "COMBATE" and evento.type == pygame.KEYDOWN:
                self.manejar_teclas_combate(evento)

        if self.estado == "EXPLORACION":
            self.mover_jugador()
            self.verificar_colisiones()

    def manejar_teclas_combate(self, evento):
        if self.turno_actual == "JUGADOR":
            if evento.key == pygame.K_a:
                dano = SistemaCombate.calcular_dano(self.heroe.ataque, self.enemigo.defensa)
                self.enemigo.recibir_dano(dano)
                self.mensaje_combate = f"¡{self.heroe.nombre} ataca! Causa {dano} puntos de daño."
                
                if not self.enemigo.esta_vivo():
                    self.turno_actual = "VICTORIA"
                else:
                    self.turno_actual = "ENEMIGO"

        elif self.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                dano = SistemaCombate.calcular_dano(self.enemigo.ataque, self.heroe.defensa)
                self.heroe.recibir_dano(dano)
                self.mensaje_combate = f"¡{self.enemigo.nombre} contraataca y causa {dano} de daño!"
                
                if not self.heroe.esta_vivo():
                    self.turno_actual = "DERROTA"
                else:
                    self.turno_actual = "JUGADOR"

        elif self.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                self.heroe.ganar_experiencia(100)
                self.estado = "EXPLORACION"
                
        elif self.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
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
                self.turno_actual = "JUGADOR"
                self.mensaje_combate = f"¡Emboscada! {self.enemigo.nombre} te ataca."
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
            # NUEVO: Dibujar el mapa y los sprites
            if self.usar_sprites:
                # Llenar todo el fondo con la textura de suelo usando un bucle doble
                for x in range(0, ANCHO, TAMANO_TILE):
                    for y in range(0, ALTO - 60, TAMANO_TILE):
                        self.pantalla.blit(self.img_suelo, (x, y))
            else:
                self.pantalla.fill(VERDE_OSCURO)
            
            # Dibujar enemigo
            if self.enemigo and self.enemigo.esta_vivo():
                if self.usar_sprites:
                    self.pantalla.blit(self.img_enemigo, self.enemigo_rect.topleft)
                else:
                    pygame.draw.rect(self.pantalla, ROJO_ENEMIGO, self.enemigo_rect)

            # Dibujar jugador
            if self.usar_sprites:
                self.pantalla.blit(self.img_heroe, (self.jugador_x, self.jugador_y))
            else:
                jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
                pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

            self.dibujar_hud()

        elif self.estado == "COMBATE":
            self.pantalla.fill(NEGRO)
            
            titulo = self.fuente_grande.render(f"VS {self.enemigo.nombre}", True, ROJO_ENEMIGO)
            hp_enemigo = self.fuente.render(f"HP Enemigo: {self.enemigo.puntos_vida}", True, BLANCO)
            self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
            self.pantalla.blit(hp_enemigo, (ANCHO // 2 - hp_enemigo.get_width() // 2, 100))
            
            # Si tenemos el sprite del enemigo, lo dibujamos grande en el centro al estilo Dragon Quest
            if self.usar_sprites:
                enemigo_grande = pygame.transform.scale(self.img_enemigo, (128, 128))
                self.pantalla.blit(enemigo_grande, (ANCHO // 2 - 64, 150))
            
            caja_msg_rect = pygame.Rect(100, 300, 600, 150)
            pygame.draw.rect(self.pantalla, GRIS_PANEL, caja_msg_rect)
            pygame.draw.rect(self.pantalla, AMARILLO, caja_msg_rect, 3)
            
            texto_msg = self.fuente.render(self.mensaje_combate, True, BLANCO)
            self.pantalla.blit(texto_msg, (120, 320))
            
            if self.turno_actual == "JUGADOR":
                instruccion = self.fuente.render("▶ Presiona 'A' para Atacar", True, AMARILLO)
            elif self.turno_actual == "ENEMIGO":
                instruccion = self.fuente.render("▶ Presiona 'ESPACIO' para continuar", True, AMARILLO)
            elif self.turno_actual == "VICTORIA":
                instruccion = self.fuente.render("▶ ¡Has ganado! Presiona 'ENTER' para salir", True, (100, 255, 100))
            elif self.turno_actual == "DERROTA":
                instruccion = self.fuente.render("▶ Has muerto. Presiona 'ENTER' para salir", True, ROJO_ENEMIGO)
                
            self.pantalla.blit(instruccion, (120, 400))
            
            self.dibujar_hud()

        pygame.display.flip()

    def actualizar(self):
        self.reloj.tick(FPS)

    def salir(self):
        pygame.quit()