# ui/pantalla.py
import pygame
import os
from models.personaje import Personaje
from core.escenario import Escenario
from core.combate import SistemaCombate
from models.objeto import Objeto, Equipamiento

# Constantes Globales
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 64 
VELOCIDAD = 5

# Paleta de colores UI/UX
NEGRO_ELEGANTE = (15, 15, 20)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)
ROJO_ENEMIGO = (220, 20, 60) 
GRIS_PANEL = (50, 50, 50)
AMARILLO = (255, 215, 0)
NARANJA = (255, 140, 0)
MORADO_MERCADER = (128, 0, 128)
AMARILLO_GIRASOL = (255, 204, 51) 

# ==========================================
# PATRÓN DE DISEÑO: ESTADOS (STATE PATTERN)
# ==========================================

class EstadoJuego:
    """Clase base (Interfaz) para todos los estados del juego."""
    def __init__(self, motor):
        self.motor = motor 

    def manejar_evento(self, evento): 
        pass
    def actualizar(self): 
        pass
    def dibujar(self): 
        pass


class EstadoMenuPrincipal(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
            if self.motor.usar_sonidos:
                pygame.mixer.music.load(os.path.join("assets", "Sonidos", "mapa.mp3"))
                pygame.mixer.music.play(-1)
            self.motor.estado_actual = self.motor.estado_exploracion

    def dibujar(self):
        self.motor.pantalla.fill(NEGRO_ELEGANTE)
        
        titulo = self.motor.fuente_gigante.render("La Leyenda de los 17 Girasoles", True, AMARILLO_GIRASOL)
        self.motor.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 3))
        
        tiempo = pygame.time.get_ticks()
        parpadeo = abs(tiempo % 2000 - 1000) / 1000.0 
        color_instruccion = (int(255 * parpadeo), int(255 * parpadeo), int(255 * parpadeo))
        
        instruccion = self.motor.fuente.render("Presiona ENTER para adentrarte en las 20 zonas", True, color_instruccion)
        self.motor.pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, ALTO // 2 + 50))


class EstadoFinJuego(EstadoJuego):
    def __init__(self, motor):
        super().__init__(motor)
        self.victoria = False 

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
            self.motor.corriendo = False 

    def dibujar(self):
        self.motor.pantalla.fill(NEGRO_ELEGANTE)
        
        if self.victoria:
            texto = self.motor.fuente_gigante.render("¡VICTORIA SUPREMA!", True, AMARILLO_GIRASOL)
            subtitulo = self.motor.fuente.render("Has superado todas las pruebas de esta aventura.", True, BLANCO)
        else:
            texto = self.motor.fuente_gigante.render("FIN DEL JUEGO", True, ROJO_ENEMIGO)
            subtitulo = self.motor.fuente.render("Tu viaje termina aquí en la oscuridad...", True, BLANCO)
            
        instruccion = self.motor.fuente.render("Presiona ENTER para salir", True, GRIS_PANEL)
        
        self.motor.pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, ALTO // 3))
        self.motor.pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, ALTO // 2))
        self.motor.pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, ALTO - 100))


class EstadoExploracion(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t and self.motor.es_tienda:
                self.motor.estado_actual = self.motor.estado_tienda
                self.motor.mensaje_tienda = "¡Bienvenido! Tengo mercancía de primera."

    def actualizar(self):
        self._mover_jugador()
        self._verificar_colisiones()

    def _mover_jugador(self):
        teclas = pygame.key.get_pressed()
        moviendo = False
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.motor.jugador_x -= VELOCIDAD
            self.motor.mirando_izquierda = True
            moviendo = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.motor.jugador_x += VELOCIDAD
            self.motor.mirando_izquierda = False
            moviendo = True
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.motor.jugador_y -= VELOCIDAD
            moviendo = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.motor.jugador_y += VELOCIDAD
            moviendo = True

        if moviendo:
            self.motor.accion_heroe = "WALK"
        else:
            self.motor.accion_heroe = "IDLE"

        self.motor.jugador_y = max(0, min(self.motor.jugador_y, ALTO - 60 - TAMANO_TILE))
        
        if self.motor.jugador_x > ANCHO - TAMANO_TILE:
            if self.motor.indice_zona < len(self.motor.mundo.zonas) - 1:
                self.motor.indice_zona += 1
                self.motor.cargar_zona()
                self.motor.jugador_x = 0 
                self.motor.heroe.zonas_exploradas += 1 
            else: 
                self.motor.jugador_x = ANCHO - TAMANO_TILE 
        elif self.motor.jugador_x < 0:
            if self.motor.indice_zona > 0:
                self.motor.indice_zona -= 1
                self.motor.cargar_zona()
                self.motor.jugador_x = ANCHO - TAMANO_TILE 
            else: 
                self.motor.jugador_x = 0 

    def _verificar_colisiones(self):
        jugador_rect = pygame.Rect(self.motor.jugador_x, self.motor.jugador_y, TAMANO_TILE, TAMANO_TILE)
        
        if self.motor.enemigo and self.motor.enemigo.esta_vivo():
            if jugador_rect.colliderect(self.motor.enemigo_rect):
                self.motor.estado_actual = self.motor.estado_combate 
                self.motor.turno_actual = "JUGADOR"
                self.motor.mensaje_combate = f"¡Emboscada! {self.motor.enemigo.nombre} te ataca."
                self.motor.jugador_x -= 40 
                self.motor.efecto_actual = None 
                
                if self.motor.usar_sonidos:
                    pygame.mixer.music.load(os.path.join("assets", "Sonidos", "combate.mp3"))
                    pygame.mixer.music.play(-1)
                    
        if self.motor.objeto:
            if jugador_rect.colliderect(self.motor.objeto_rect):
                if hasattr(self.motor.objeto, 'dano_explosion'):
                    self.motor.heroe.recibir_dano(self.motor.objeto.dano_explosion)
                    if not self.motor.heroe.esta_vivo():
                        self.motor.estado_fin.victoria = False
                        self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.heroe.recolectar_objeto(self.motor.objeto)
                    self.motor.heroe.ganar_puntaje(50) 
                    if self.motor.usar_sonidos: 
                        self.motor.sfx_moneda.play()
                        
                self.motor.mundo.zonas[self.motor.indice_zona].objeto = None
                self.motor.objeto = None

    def dibujar(self):
        if self.motor.usar_sprites:
            for x in range(0, ANCHO, TAMANO_TILE):
                for y in range(0, ALTO - 60, TAMANO_TILE):
                    self.motor.pantalla.blit(self.motor.img_suelo, (x, y))
        else: 
            self.motor.pantalla.fill(VERDE_OSCURO)
            
        if self.motor.es_tienda:
            pygame.draw.rect(self.motor.pantalla, MORADO_MERCADER, self.motor.mercader_rect)
            aviso = self.motor.fuente.render("Presiona 'T' para Comerciar", True, BLANCO)
            self.motor.pantalla.blit(aviso, (ANCHO//2 - aviso.get_width()//2, 160))
            
        if self.motor.objeto:
            if self.motor.img_objeto: 
                self.motor.pantalla.blit(self.motor.img_objeto, self.motor.objeto_rect.topleft)
            else:
                color_objeto = (139, 0, 0) if hasattr(self.motor.objeto, 'dano_explosion') else NARANJA
                pygame.draw.rect(self.motor.pantalla, color_objeto, self.motor.objeto_rect)
                
        if self.motor.enemigo and self.motor.enemigo.esta_vivo():
            if self.motor.usar_sprites:
                indice_e = self.motor.frame_index % len(self.motor.anim_enemigo_idle)
                self.motor.pantalla.blit(self.motor.anim_enemigo_idle[indice_e], self.motor.enemigo_rect.topleft)
            else: 
                pygame.draw.rect(self.motor.pantalla, ROJO_ENEMIGO, self.motor.enemigo_rect)
                
        if self.motor.usar_sprites:
            if self.motor.accion_heroe == "WALK":
                lista_activa = self.motor.anim_heroe_walk
            else:
                lista_activa = self.motor.anim_heroe_idle
                
            indice_h = self.motor.frame_index % len(lista_activa)
            imagen_actual = lista_activa[indice_h]
            
            if self.motor.mirando_izquierda: 
                imagen_actual = pygame.transform.flip(imagen_actual, True, False)
                
            self.motor.pantalla.blit(imagen_actual, (self.motor.jugador_x, self.motor.jugador_y))
        else:
            jugador_rect = pygame.Rect(self.motor.jugador_x, self.motor.jugador_y, TAMANO_TILE, TAMANO_TILE)
            pygame.draw.rect(self.motor.pantalla, AZUL_HEROE, jugador_rect)


class EstadoCombate(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: 
            return
            
        if self.motor.turno_actual == "JUGADOR":
            if evento.key == pygame.K_a:
                if self.motor.usar_sonidos: 
                    self.motor.sfx_ataque.play()
                self.motor.efecto_actual = "HEROE_ATACA"
                self.motor.tiempo_efecto = pygame.time.get_ticks()
                self.motor.frame_index = 0 
                
                dano = SistemaCombate.calcular_dano(self.motor.heroe.ataque, self.motor.enemigo.defensa)
                self.motor.enemigo.recibir_dano(dano)
                self.motor.mensaje_combate = f"¡{self.motor.heroe.nombre} ataca! Causa {dano} puntos de daño."
                
                if not self.motor.enemigo.esta_vivo():
                    self.motor.turno_actual = "VICTORIA"
                else:
                    self.motor.turno_actual = "ENEMIGO"
                    
        elif self.motor.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                self.motor.efecto_actual = "ENEMIGO_ATACA"
                self.motor.tiempo_efecto = pygame.time.get_ticks()
                self.motor.frame_index = 0
                
                dano = SistemaCombate.calcular_dano(self.motor.enemigo.ataque, self.motor.heroe.defensa)
                self.motor.heroe.recibir_dano(dano)
                self.motor.mensaje_combate = f"¡{self.motor.enemigo.nombre} contraataca y causa {dano} de daño!"
                
                if not self.motor.heroe.esta_vivo():
                    self.motor.turno_actual = "DERROTA"
                    self.motor.estado_fin.victoria = False
                else: 
                    self.motor.turno_actual = "JUGADOR"
                    
        elif self.motor.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                self.motor.heroe.ganar_experiencia(100)
                self.motor.efecto_actual = None
                
                if self.motor.enemigo.nombre == "Rey Demonio":
                    self.motor.estado_fin.victoria = True
                    self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.estado_actual = self.motor.estado_exploracion
                    if self.motor.usar_sonidos:
                        pygame.mixer.music.load(os.path.join("assets", "Sonidos", "mapa.mp3"))
                        pygame.mixer.music.play(-1)
                        
        elif self.motor.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
                self.motor.estado_actual = self.motor.estado_fin

    def dibujar(self):
        self.motor.pantalla.fill(NEGRO_ELEGANTE)
        
        titulo = self.motor.fuente_grande.render(f"VS {self.motor.enemigo.nombre}", True, ROJO_ENEMIGO)
        texto_hp_enemigo = self.motor.fuente.render(f"HP Enemigo: {self.motor.enemigo.puntos_vida}", True, BLANCO)
        
        self.motor.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))
        self.motor.pantalla.blit(texto_hp_enemigo, (ANCHO // 2 - texto_hp_enemigo.get_width() // 2, 80))
        
        if self.motor.usar_sprites:
            tiempo_transcurrido = pygame.time.get_ticks() - self.motor.tiempo_efecto
            
            if self.motor.efecto_actual == "HEROE_ATACA" and tiempo_transcurrido < 600:
                indice_frame = min(self.motor.frame_index, len(self.motor.anim_heroe_attack) - 1)
                sprite_h = self.motor.anim_heroe_attack[indice_frame]
            else:
                indice_frame = self.motor.frame_index % len(self.motor.anim_heroe_idle)
                sprite_h = self.motor.anim_heroe_idle[indice_frame]
                
            if self.motor.efecto_actual == "ENEMIGO_ATACA" and tiempo_transcurrido < 600:
                indice_frame = min(self.motor.frame_index, len(self.motor.anim_enemigo_attack) - 1)
                sprite_e = self.motor.anim_enemigo_attack[indice_frame]
            else:
                indice_frame = self.motor.frame_index % len(self.motor.anim_enemigo_idle)
                sprite_e = self.motor.anim_enemigo_idle[indice_frame]
                
            heroe_grande = pygame.transform.scale(sprite_h, (192, 192))
            self.motor.pantalla.blit(heroe_grande, (150, 120))
            
            enemigo_grande = pygame.transform.scale(sprite_e, (192, 192))
            enemigo_grande = pygame.transform.flip(enemigo_grande, True, False)
            self.motor.pantalla.blit(enemigo_grande, (450, 120))
            
        caja_msg_rect = pygame.Rect(100, 350, 600, 150)
        pygame.draw.rect(self.motor.pantalla, GRIS_PANEL, caja_msg_rect)
        pygame.draw.rect(self.motor.pantalla, AMARILLO, caja_msg_rect, 3)
        
        texto_mensaje = self.motor.fuente.render(self.motor.mensaje_combate, True, BLANCO)
        self.motor.pantalla.blit(texto_mensaje, (120, 370))
        
        if self.motor.turno_actual == "JUGADOR": 
            texto_instruccion = "▶ Presiona 'A' para Atacar"
            color_instruccion = AMARILLO
        elif self.motor.turno_actual == "ENEMIGO": 
            texto_instruccion = "▶ Presiona 'ESPACIO' para continuar"
            color_instruccion = AMARILLO
        elif self.motor.turno_actual == "VICTORIA": 
            texto_instruccion = "▶ Has ganado. Presiona 'ENTER'"
            color_instruccion = (100, 255, 100)
        elif self.motor.turno_actual == "DERROTA": 
            texto_instruccion = "▶ Has caído... Presiona 'ENTER'"
            color_instruccion = ROJO_ENEMIGO
            
        instruccion = self.motor.fuente.render(texto_instruccion, True, color_instruccion)
        self.motor.pantalla.blit(instruccion, (120, 450))


class EstadoTienda(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: 
            return
            
        if evento.key == pygame.K_b:
            if self.motor.heroe.puntaje >= self.motor.item_tienda.precio_compra:
                self.motor.heroe.puntaje -= self.motor.item_tienda.precio_compra
                self.motor.heroe.equipar(self.motor.item_tienda)
                self.motor.mensaje_tienda = f"¡Equipado: {self.motor.item_tienda.nombre}!"
                self.motor.item_tienda = Equipamiento("Armadura Épica", aumento_ataque=5, aumento_defensa=20, precio_compra=300, precio_venta=150)
            else: 
                self.motor.mensaje_tienda = "Puntos insuficientes."
        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
            self.motor.estado_actual = self.motor.estado_exploracion 

    def dibujar(self):
        self.motor.pantalla.fill(NEGRO_ELEGANTE)
        
        titulo = self.motor.fuente_grande.render("Refugio del Mercader", True, MORADO_MERCADER)
        self.motor.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
        
        oferta_rect = pygame.Rect(200, 150, 400, 200)
        pygame.draw.rect(self.motor.pantalla, GRIS_PANEL, oferta_rect)
        pygame.draw.rect(self.motor.pantalla, AMARILLO_GIRASOL, oferta_rect, 2)
        
        texto_nombre = self.motor.fuente_grande.render(self.motor.item_tienda.nombre, True, AMARILLO)
        texto_stats = self.motor.fuente.render(f"+{self.motor.item_tienda.aumento_ataque} ATK / +{self.motor.item_tienda.aumento_defensa} DEF", True, BLANCO)
        texto_precio = self.motor.fuente.render(f"Costo: {self.motor.item_tienda.precio_compra} Puntos", True, (100, 255, 100))
        
        self.motor.pantalla.blit(texto_nombre, (ANCHO // 2 - 150, 170))
        self.motor.pantalla.blit(texto_stats, (ANCHO // 2 - 100, 230))
        self.motor.pantalla.blit(texto_precio, (ANCHO // 2 - 80, 280))
        
        caja_msg_rect = pygame.Rect(100, 400, 600, 120)
        pygame.draw.rect(self.motor.pantalla, GRIS_PANEL, caja_msg_rect)
        pygame.draw.rect(self.motor.pantalla, MORADO_MERCADER, caja_msg_rect, 3)
        
        mensaje = self.motor.fuente.render(self.motor.mensaje_tienda, True, BLANCO)
        instruccion = self.motor.fuente.render("▶ Presiona 'B' para Comprar | 'ENTER' para Salir", True, AMARILLO)
        
        self.motor.pantalla.blit(mensaje, (120, 420))
        self.motor.pantalla.blit(instruccion, (120, 480))


# ==========================================
# CLASE PRINCIPAL (CONTEXTO)
# ==========================================

class MotorGrafico:
    def __init__(self, heroe: Personaje, mundo: Escenario):
        pygame.init()
        pygame.mixer.init()
        
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("La Leyenda de los 17 Girasoles")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        self.heroe = heroe
        self.mundo = mundo
        self.indice_zona = 0 
        
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_gigante = pygame.font.SysFont("Arial", 50, bold=True)
        
        self.estado_menu = EstadoMenuPrincipal(self)
        self.estado_exploracion = EstadoExploracion(self)
        self.estado_combate = EstadoCombate(self)
        self.estado_tienda = EstadoTienda(self)
        self.estado_fin = EstadoFinJuego(self)
        
        self.estado_actual = self.estado_menu 
        
        self.turno_actual = "JUGADOR"
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        self.mensaje_tienda = "¡Bienvenido! ¿Qué vas a llevar?"
        self.item_tienda = Equipamiento("Espada Maestra", aumento_ataque=15, aumento_defensa=5, precio_compra=150, precio_venta=75)
        
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
        self.cargar_sonidos()
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
            rectangulo = pygame.Rect(i * alto, 0, alto, alto)
            recorte = hoja.subsurface(rectangulo)
            frames.append(pygame.transform.scale(recorte, escala))
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
            self.img_suelo = pygame.transform.scale(pygame.image.load(ruta_suelo).convert(), escala_mapa)
            
            try: 
                ruta_obj = os.path.join("assets", "Objeto", "item.png")
                self.img_objeto = pygame.transform.scale(pygame.image.load(ruta_obj).convert_alpha(), escala_mapa)
            except Exception: 
                pass
                
            self.usar_sprites = True
        except Exception as e: 
            print("No se cargaron sprites gráficos. Modo colores planos activado.")

    def cargar_sonidos(self):
        self.usar_sonidos = False
        try:
            self.sfx_ataque = pygame.mixer.Sound(os.path.join("assets", "Sonidos", "ataque.wav"))
            self.sfx_moneda = pygame.mixer.Sound(os.path.join("assets", "Sonidos", "moneda.wav"))
            self.sfx_ataque.set_volume(0.5) 
            self.sfx_moneda.set_volume(0.6)
            self.usar_sonidos = True
        except Exception: 
            print("No se encontraron sonidos. Modo silencioso activado.")

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: 
                self.corriendo = False
            self.estado_actual.manejar_evento(evento)

    def dibujar_hud(self):
        if self.estado_actual in [self.estado_menu, self.estado_fin]: 
            return
            
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

    def actualizar(self):
        self.estado_actual.actualizar()
        
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_animacion > self.VELOCIDAD_ANIMACION:
            self.tiempo_animacion = tiempo_actual
            self.frame_index += 1
            
        self.reloj.tick(FPS)

    def dibujar(self):
        self.estado_actual.dibujar()
        self.dibujar_hud()
        pygame.display.flip()

    def salir(self): 
        pygame.quit()