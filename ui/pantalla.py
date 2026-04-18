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

# Paleta de colores
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

        # Controladores de Animación
        self.frame_index = 0
        self.tiempo_animacion = 0
        self.VELOCIDAD_ANIMACION = 120 
        self.accion_heroe = "IDLE" 
        self.mirando_izquierda = False 
        
        # NUEVO: Controladores visuales de Combate
        self.efecto_actual = None # "HEROE_ATACA" o "ENEMIGO_ATACA"
        self.tiempo_efecto = 0    # Temporizador para saber cuándo detener el ataque

        self.cargar_sprites()

    def extraer_frames(self, ruta, escala):
        hoja = pygame.image.load(ruta).convert_alpha()
        alto = hoja.get_height()
        columnas = hoja.get_width() // alto 
        
        frames = []
        for i in range(columnas):
            rect = pygame.Rect(i * alto, 0, alto, alto)
            frame = hoja.subsurface(rect)
            frames.append(pygame.transform.scale(frame, escala))
        return frames

    def cargar_sprites(self):
        self.usar_sprites = False
        try:
            escala_mapa = (TAMANO_TILE, TAMANO_TILE) 
            
            # Héroe
            ruta_idle_h = os.path.join("assets", "Heroe", "Soldier", "Soldier-Idle.png")
            ruta_walk_h = os.path.join("assets", "Heroe", "Soldier", "Soldier-Walk.png")
            ruta_attack_h = os.path.join("assets", "Heroe", "Soldier", "Soldier-Attack01.png")
            
            self.anim_heroe_idle = self.extraer_frames(ruta_idle_h, escala_mapa)
            self.anim_heroe_walk = self.extraer_frames(ruta_walk_h, escala_mapa)
            self.anim_heroe_attack = self.extraer_frames(ruta_attack_h, escala_mapa)

            # Enemigo
            ruta_idle_e = os.path.join("assets", "Enemigo", "Orc", "Orc-Idle.png")
            ruta_attack_e = os.path.join("assets", "Enemigo", "Orc", "Orc-Attack01.png")
            
            self.anim_enemigo_idle = self.extraer_frames(ruta_idle_e, escala_mapa)
            self.anim_enemigo_attack = self.extraer_frames(ruta_attack_e, escala_mapa)

            # Suelo
            ruta_suelo = os.path.join("assets", "Suelo", "Grass_Middle.png")
            self.img_suelo = pygame.image.load(ruta_suelo).convert()
            self.img_suelo = pygame.transform.scale(self.img_suelo, escala_mapa)
            
            self.usar_sprites = True
            print("✅ Sprites y ataques cargados correctamente.")
        except Exception as e:
            print(f"⚠️ Error cargando animaciones: {e}")

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
                # Disparar animación de ataque
                self.efecto_actual = "HEROE_ATACA"
                self.tiempo_efecto = pygame.time.get_ticks()
                self.frame_index = 0 # Reiniciar cuadro para ataque limpio
                
                dano = SistemaCombate.calcular_dano(self.heroe.ataque, self.enemigo.defensa)
                self.enemigo.recibir_dano(dano)
                self.mensaje_combate = f"¡{self.heroe.nombre} ataca! Causa {dano} puntos de daño."
                
                if not self.enemigo.esta_vivo():
                    self.turno_actual = "VICTORIA"
                else:
                    self.turno_actual = "ENEMIGO"

        elif self.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                # Disparar animación de contraataque
                self.efecto_actual = "ENEMIGO_ATACA"
                self.tiempo_efecto = pygame.time.get_ticks()
                self.frame_index = 0
                
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
                self.efecto_actual = None
                
        elif self.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
                self.corriendo = False

    def mover_jugador(self):
        teclas = pygame.key.get_pressed()
        moviendo = False
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador_x -= VELOCIDAD
            self.mirando_izquierda = True
            moviendo = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador_x += VELOCIDAD
            self.mirando_izquierda = False
            moviendo = True
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.jugador_y -= VELOCIDAD
            moviendo = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.jugador_y += VELOCIDAD
            moviendo = True

        if moviendo:
            self.accion_heroe = "WALK"
        else:
            self.accion_heroe = "IDLE"

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
                self.efecto_actual = None # Limpiar efectos de combates previos

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
            if self.usar_sprites:
                for x in range(0, ANCHO, TAMANO_TILE):
                    for y in range(0, ALTO - 60, TAMANO_TILE):
                        self.pantalla.blit(self.img_suelo, (x, y))
            else:
                self.pantalla.fill(VERDE_OSCURO)
            
            if self.enemigo and self.enemigo.esta_vivo():
                if self.usar_sprites:
                    indice_e = self.frame_index % len(self.anim_enemigo_idle)
                    self.pantalla.blit(self.anim_enemigo_idle[indice_e], self.enemigo_rect.topleft)
                else:
                    pygame.draw.rect(self.pantalla, ROJO_ENEMIGO, self.enemigo_rect)

            if self.usar_sprites:
                lista_activa = self.anim_heroe_walk if self.accion_heroe == "WALK" else self.anim_heroe_idle
                indice_h = self.frame_index % len(lista_activa)
                imagen_actual = lista_activa[indice_h]
                if self.mirando_izquierda:
                    imagen_actual = pygame.transform.flip(imagen_actual, True, False)
                self.pantalla.blit(imagen_actual, (self.jugador_x, self.jugador_y))
            else:
                jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
                pygame.draw.rect(self.pantalla, AZUL_HEROE, jugador_rect)

            self.dibujar_hud()

        elif self.estado == "COMBATE":
            self.pantalla.fill(NEGRO)
            
            titulo = self.fuente_grande.render(f"VS {self.enemigo.nombre}", True, ROJO_ENEMIGO)
            hp_enemigo = self.fuente.render(f"HP Enemigo: {self.enemigo.puntos_vida}", True, BLANCO)
            self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))
            self.pantalla.blit(hp_enemigo, (ANCHO // 2 - hp_enemigo.get_width() // 2, 80))
            
            # NUEVO: Lógica de Batalla JRPG Vista Lateral
            if self.usar_sprites:
                tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_efecto
                
                # 1. Determinar Sprite del Héroe
                if self.efecto_actual == "HEROE_ATACA" and tiempo_transcurrido < 600:
                    # Animación de ataque (topeamos el index para que no se reinicie a la mitad)
                    idx = min(self.frame_index, len(self.anim_heroe_attack) - 1)
                    sprite_h = self.anim_heroe_attack[idx]
                else:
                    idx = self.frame_index % len(self.anim_heroe_idle)
                    sprite_h = self.anim_heroe_idle[idx]
                    
                # 2. Determinar Sprite del Enemigo
                if self.efecto_actual == "ENEMIGO_ATACA" and tiempo_transcurrido < 600:
                    idx = min(self.frame_index, len(self.anim_enemigo_attack) - 1)
                    sprite_e = self.anim_enemigo_attack[idx]
                else:
                    idx = self.frame_index % len(self.anim_enemigo_idle)
                    sprite_e = self.anim_enemigo_idle[idx]

                # Dibujar al Héroe a la izquierda (escalado grande)
                hero_grande = pygame.transform.scale(sprite_h, (192, 192))
                self.pantalla.blit(hero_grande, (150, 120))

                # Dibujar al Enemigo a la derecha (volteado para que mire al héroe)
                enemigo_grande = pygame.transform.scale(sprite_e, (192, 192))
                enemigo_grande = pygame.transform.flip(enemigo_grande, True, False)
                self.pantalla.blit(enemigo_grande, (450, 120))
            
            # Panel inferior de mensajes
            caja_msg_rect = pygame.Rect(100, 350, 600, 150)
            pygame.draw.rect(self.pantalla, GRIS_PANEL, caja_msg_rect)
            pygame.draw.rect(self.pantalla, AMARILLO, caja_msg_rect, 3)
            
            texto_msg = self.fuente.render(self.mensaje_combate, True, BLANCO)
            self.pantalla.blit(texto_msg, (120, 370))
            
            if self.turno_actual == "JUGADOR":
                instruccion = self.fuente.render("▶ Presiona 'A' para Atacar", True, AMARILLO)
            elif self.turno_actual == "ENEMIGO":
                instruccion = self.fuente.render("▶ Presiona 'ESPACIO' para continuar", True, AMARILLO)
            elif self.turno_actual == "VICTORIA":
                instruccion = self.fuente.render("▶ ¡Has ganado! Presiona 'ENTER' para salir", True, (100, 255, 100))
            elif self.turno_actual == "DERROTA":
                instruccion = self.fuente.render("▶ Has muerto. Presiona 'ENTER' para salir", True, ROJO_ENEMIGO)
                
            self.pantalla.blit(instruccion, (120, 450))
            self.dibujar_hud()

        pygame.display.flip()

    def actualizar_animaciones(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_animacion > self.VELOCIDAD_ANIMACION:
            self.tiempo_animacion = tiempo_actual
            self.frame_index += 1

    def actualizar(self):
        self.actualizar_animaciones() 
        self.reloj.tick(FPS)

    def salir(self):
        pygame.quit()