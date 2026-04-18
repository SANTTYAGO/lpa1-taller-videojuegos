# ui/pantalla.py
import pygame
import os
from models.personaje import Personaje
from core.escenario import Escenario
from core.combate import SistemaCombate
from models.objeto import Objeto, Equipamiento # NUEVO: Importamos el Equipamiento

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
NARANJA = (255, 140, 0)
MORADO_MERCADER = (128, 0, 128) # Color para el NPC de la tienda

class MotorGrafico:
    def __init__(self, heroe: Personaje, mundo: Escenario):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura 16-Bits")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        self.heroe = heroe
        self.mundo = mundo
        self.indice_zona = 0 
        
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        
        self.estado = "EXPLORACION" # Puede ser EXPLORACION, COMBATE o TIENDA
        self.turno_actual = "JUGADOR"
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        self.mensaje_tienda = "¡Bienvenido! ¿Qué vas a llevar?"
        
        # Objeto de prueba para vender en la tienda
        self.item_tienda = Equipamiento(nombre="Espada Maestra", aumento_ataque=15, aumento_defensa=5, precio_compra=150, precio_venta=75)
        
        self.jugador_x = 50 
        self.jugador_y = ((ALTO - 60) // 2) - (TAMANO_TILE // 2)

        self.frame_index = 0
        self.tiempo_animacion = 0
        self.VELOCIDAD_ANIMACION = 120 
        self.accion_heroe = "IDLE" 
        self.mirando_izquierda = False 
        
        self.efecto_actual = None 
        self.tiempo_efecto = 0    

        self.cargar_sprites()
        self.cargar_zona() 

    def cargar_zona(self):
        zona_actual = self.mundo.zonas[self.indice_zona]
        self.enemigo = zona_actual.enemigo
        self.objeto = zona_actual.objeto
        self.es_tienda = zona_actual.es_tienda
        self.nombre_zona = zona_actual.nombre
        
        if self.enemigo:
            self.enemigo_rect = pygame.Rect(600, 300, TAMANO_TILE, TAMANO_TILE)
        if self.objeto:
            self.objeto_rect = pygame.Rect(300, 400, TAMANO_TILE, TAMANO_TILE)
        if self.es_tienda:
            self.mercader_rect = pygame.Rect(ANCHO // 2, 200, TAMANO_TILE, TAMANO_TILE)

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
        self.img_objeto = None
        try:
            escala_mapa = (TAMANO_TILE, TAMANO_TILE) 
            
            ruta_idle_h = os.path.join("assets", "Heroe", "Soldier", "Soldier-Idle.png")
            ruta_walk_h = os.path.join("assets", "Heroe", "Soldier", "Soldier-Walk.png")
            ruta_attack_h = os.path.join("assets", "Heroe", "Soldier", "Soldier-Attack01.png")
            
            self.anim_heroe_idle = self.extraer_frames(ruta_idle_h, escala_mapa)
            self.anim_heroe_walk = self.extraer_frames(ruta_walk_h, escala_mapa)
            self.anim_heroe_attack = self.extraer_frames(ruta_attack_h, escala_mapa)

            ruta_idle_e = os.path.join("assets", "Enemigo", "Orc", "Orc-Idle.png")
            ruta_attack_e = os.path.join("assets", "Enemigo", "Orc", "Orc-Attack01.png")
            
            self.anim_enemigo_idle = self.extraer_frames(ruta_idle_e, escala_mapa)
            self.anim_enemigo_attack = self.extraer_frames(ruta_attack_e, escala_mapa)

            ruta_suelo = os.path.join("assets", "Suelo", "Grass_Middle.png")
            self.img_suelo = pygame.image.load(ruta_suelo).convert()
            self.img_suelo = pygame.transform.scale(self.img_suelo, escala_mapa)
            
            try:
                ruta_obj = os.path.join("assets", "Objeto", "item.png")
                self.img_objeto = pygame.image.load(ruta_obj).convert_alpha()
                self.img_objeto = pygame.transform.scale(self.img_objeto, escala_mapa)
            except: pass
            
            self.usar_sprites = True
        except Exception as e:
            pass

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
                
            # Eventos de Combate
            if self.estado == "COMBATE" and evento.type == pygame.KEYDOWN:
                self.manejar_teclas_combate(evento)
                
            # NUEVO: Eventos de Exploración (Entrar a la tienda)
            elif self.estado == "EXPLORACION" and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_t and self.es_tienda:
                    self.estado = "TIENDA"
                    self.mensaje_tienda = "¡Bienvenido! Tengo mercancía de primera."
                    
            # NUEVO: Eventos de la Tienda
            elif self.estado == "TIENDA" and evento.type == pygame.KEYDOWN:
                self.manejar_teclas_tienda(evento)

        if self.estado == "EXPLORACION":
            self.mover_jugador()
            self.verificar_colisiones()

    def manejar_teclas_tienda(self, evento):
        """Lógica para comprar ítems en el mercader"""
        if evento.key == pygame.K_b: # Tecla B para Comprar (Buy)
            if self.heroe.puntaje >= self.item_tienda.precio_compra:
                # Cobramos los puntos
                self.heroe.puntaje -= self.item_tienda.precio_compra
                # Equipamos automáticamente el objeto (esto llama a tu método de la clase Personaje)
                self.heroe.equipar(self.item_tienda)
                self.mensaje_tienda = f"¡Excelente compra! Has equipado {self.item_tienda.nombre}."
                # Generamos un nuevo ítem más caro para la próxima
                self.item_tienda = Equipamiento("Armadura Épica", aumento_ataque=5, aumento_defensa=20, precio_compra=300, precio_venta=150)
            else:
                self.mensaje_tienda = "No tienes suficientes Puntos para comprar esto."
                
        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
            self.estado = "EXPLORACION" # Volver al mapa

    def manejar_teclas_combate(self, evento):
        if self.turno_actual == "JUGADOR":
            if evento.key == pygame.K_a:
                self.efecto_actual = "HEROE_ATACA"
                self.tiempo_efecto = pygame.time.get_ticks()
                self.frame_index = 0 
                
                dano = SistemaCombate.calcular_dano(self.heroe.ataque, self.enemigo.defensa)
                self.enemigo.recibir_dano(dano)
                self.mensaje_combate = f"¡{self.heroe.nombre} ataca! Causa {dano} puntos de daño."
                
                if not self.enemigo.esta_vivo():
                    self.turno_actual = "VICTORIA"
                else:
                    self.turno_actual = "ENEMIGO"

        elif self.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
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

        if moviendo: self.accion_heroe = "WALK"
        else: self.accion_heroe = "IDLE"

        self.jugador_y = max(0, min(self.jugador_y, ALTO - 60 - TAMANO_TILE))
        
        if self.jugador_x > ANCHO - TAMANO_TILE:
            if self.indice_zona < len(self.mundo.zonas) - 1:
                self.indice_zona += 1
                self.cargar_zona()
                self.jugador_x = 0 
                self.heroe.zonas_exploradas += 1 
            else:
                self.jugador_x = ANCHO - TAMANO_TILE 
                
        elif self.jugador_x < 0:
            if self.indice_zona > 0:
                self.indice_zona -= 1
                self.cargar_zona()
                self.jugador_x = ANCHO - TAMANO_TILE 
            else:
                self.jugador_x = 0 

    def verificar_colisiones(self):
        jugador_rect = pygame.Rect(self.jugador_x, self.jugador_y, TAMANO_TILE, TAMANO_TILE)
        
        if self.enemigo and self.enemigo.esta_vivo():
            if jugador_rect.colliderect(self.enemigo_rect):
                self.estado = "COMBATE" 
                self.turno_actual = "JUGADOR"
                self.mensaje_combate = f"¡Emboscada! {self.enemigo.nombre} te ataca."
                self.jugador_x -= 40 
                self.efecto_actual = None 

        if self.objeto:
            if jugador_rect.colliderect(self.objeto_rect):
                if hasattr(self.objeto, 'dano_explosion'):
                    self.heroe.recibir_dano(self.objeto.dano_explosion)
                else:
                    self.heroe.recolectar_objeto(self.objeto)
                    self.heroe.ganar_puntaje(50) 
                
                self.mundo.zonas[self.indice_zona].objeto = None
                self.objeto = None

    def dibujar_hud(self):
        panel_rect = pygame.Rect(0, ALTO - 60, ANCHO, 60)
        pygame.draw.rect(self.pantalla, GRIS_PANEL, panel_rect)
        pygame.draw.rect(self.pantalla, BLANCO, panel_rect, 2)

        texto_hp = self.fuente.render(f"HP: {self.heroe.puntos_vida}/{self.heroe.puntos_vida_max}", True, (255, 100, 100))
        texto_inv = self.fuente.render(f"ATK: {self.heroe.ataque} | DEF: {self.heroe.defensa} | Pts: {self.heroe.puntaje}", True, AMARILLO)
        
        color_zona = (100, 255, 100) if self.es_tienda else BLANCO
        texto_zona = self.fuente.render(f"{self.nombre_zona} ({self.indice_zona+1}/20)", True, color_zona)
        
        self.pantalla.blit(texto_hp, (20, ALTO - 40))
        self.pantalla.blit(texto_inv, (180, ALTO - 40))
        self.pantalla.blit(texto_zona, (500, ALTO - 40))

    def dibujar(self):
        if self.estado == "EXPLORACION":
            if self.usar_sprites:
                for x in range(0, ANCHO, TAMANO_TILE):
                    for y in range(0, ALTO - 60, TAMANO_TILE):
                        self.pantalla.blit(self.img_suelo, (x, y))
            else:
                self.pantalla.fill(VERDE_OSCURO)
            
            # Dibujar el aviso flotante si es una tienda
            if self.es_tienda:
                pygame.draw.rect(self.pantalla, MORADO_MERCADER, self.mercader_rect)
                aviso = self.fuente.render("Presiona 'T' para Comerciar", True, BLANCO)
                self.pantalla.blit(aviso, (ANCHO//2 - aviso.get_width()//2, 160))

            if self.objeto:
                if self.img_objeto:
                    self.pantalla.blit(self.img_objeto, self.objeto_rect.topleft)
                else:
                    color_obj = (139, 0, 0) if hasattr(self.objeto, 'dano_explosion') else NARANJA
                    pygame.draw.rect(self.pantalla, color_obj, self.objeto_rect)

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

        # NUEVA PANTALLA: TIENDA
        elif self.estado == "TIENDA":
            self.pantalla.fill(NEGRO)
            
            titulo = self.fuente_grande.render("Refugio del Mercader", True, MORADO_MERCADER)
            self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
            
            # Panel de oferta
            oferta_rect = pygame.Rect(200, 150, 400, 200)
            pygame.draw.rect(self.pantalla, GRIS_PANEL, oferta_rect)
            pygame.draw.rect(self.pantalla, BLANCO, oferta_rect, 2)
            
            nombre_item = self.fuente_grande.render(self.item_tienda.nombre, True, AMARILLO)
            stats = self.fuente.render(f"+{self.item_tienda.aumento_ataque} ATK / +{self.item_tienda.aumento_defensa} DEF", True, BLANCO)
            precio = self.fuente.render(f"Costo: {self.item_tienda.precio_compra} Puntos", True, (100, 255, 100))
            
            self.pantalla.blit(nombre_item, (ANCHO // 2 - nombre_item.get_width() // 2, 170))
            self.pantalla.blit(stats, (ANCHO // 2 - stats.get_width() // 2, 230))
            self.pantalla.blit(precio, (ANCHO // 2 - precio.get_width() // 2, 280))

            # Panel inferior de diálogos
            caja_msg_rect = pygame.Rect(100, 400, 600, 120)
            pygame.draw.rect(self.pantalla, GRIS_PANEL, caja_msg_rect)
            pygame.draw.rect(self.pantalla, MORADO_MERCADER, caja_msg_rect, 3)
            
            texto_msg = self.fuente.render(self.mensaje_tienda, True, BLANCO)
            instruccion = self.fuente.render("▶ Presiona 'B' para Comprar | 'ENTER' para Salir", True, AMARILLO)
            
            self.pantalla.blit(texto_msg, (120, 420))
            self.pantalla.blit(instruccion, (120, 480))
            
            self.dibujar_hud()

        elif self.estado == "COMBATE":
            self.pantalla.fill(NEGRO)
            
            titulo = self.fuente_grande.render(f"VS {self.enemigo.nombre}", True, ROJO_ENEMIGO)
            hp_enemigo = self.fuente.render(f"HP Enemigo: {self.enemigo.puntos_vida}", True, BLANCO)
            self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))
            self.pantalla.blit(hp_enemigo, (ANCHO // 2 - hp_enemigo.get_width() // 2, 80))
            
            if self.usar_sprites:
                tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_efecto
                if self.efecto_actual == "HEROE_ATACA" and tiempo_transcurrido < 600:
                    idx = min(self.frame_index, len(self.anim_heroe_attack) - 1)
                    sprite_h = self.anim_heroe_attack[idx]
                else:
                    idx = self.frame_index % len(self.anim_heroe_idle)
                    sprite_h = self.anim_heroe_idle[idx]
                    
                if self.efecto_actual == "ENEMIGO_ATACA" and tiempo_transcurrido < 600:
                    idx = min(self.frame_index, len(self.anim_enemigo_attack) - 1)
                    sprite_e = self.anim_enemigo_attack[idx]
                else:
                    idx = self.frame_index % len(self.anim_enemigo_idle)
                    sprite_e = self.anim_enemigo_idle[idx]

                hero_grande = pygame.transform.scale(sprite_h, (192, 192))
                self.pantalla.blit(hero_grande, (150, 120))

                enemigo_grande = pygame.transform.scale(sprite_e, (192, 192))
                enemigo_grande = pygame.transform.flip(enemigo_grande, True, False)
                self.pantalla.blit(enemigo_grande, (450, 120))
            
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